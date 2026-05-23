# SPDX-License-Identifier: AGPL-3.0-or-later
from typing import Optional
import logging
from decimal import Decimal, InvalidOperation
from .types import Node
from .graph import EpistemicGraph
from .exceptions import InsufficientStakeError
from .consensus.engine import ConsensusEngine
from .mining.benchmark import PoWBenchmark
from .economics.onboarding import OnboardingVault
from .identity.log_redaction_runtime import redact_agent_id_for_log
import time

logger = logging.getLogger(__name__)

DRAFT_SIGNATURE = "draft_unsigned_mvp"

class EveAgent:
    def __init__(self, agent_id: str, graph: EpistemicGraph, consensus: ConsensusEngine, vault: Optional[OnboardingVault] = None):
        self.id = agent_id
        self.graph = graph
        self.consensus = consensus
        self.vault = vault
        
        self.wallet_balance = Decimal("0")
        self.credit_balance = Decimal("0")
        
        # Onboarding: Request Credit if Vault exists
        if self.vault:
            credit = self.vault.request_starter_credit(self.id)
            self.credit_balance += credit
            self.wallet_balance += credit # Credit is liquid for staking

        self.benchmark_engine = PoWBenchmark(matrix_size=1000)
        self.trust_vector = {
            "accuracy": 0.5,
            "precision": 0.5,
            "potential": 0.0,
            "tier": "unknown"
        }

    def decide_stake_for_claim(self, requested_stake: Decimal) -> Decimal:
        """
        Decide how much to stake for a claim.submit task.

        MVP behavior (backwards-compatible):
        - Query the current ECU fee for "claim.submit" from Governance.
        - Ensure the chosen stake is at least the ECU fee.
        - Never exceed the agent's wallet_balance.
        - If requested_stake >= required_fee and <= wallet_balance, keep it unchanged.
          (This preserves existing tests that pass explicit stakes like 5.0 or 10.0.)
        - If requested_stake < required_fee but wallet can afford required_fee, bump up
          to exactly required_fee.
        - If wallet_balance < required_fee, return 0.0 to signal "cannot stake".
        """
        self._normalize_balances()
        stake_amount = _agent_coerce_decimal(requested_stake, "agent_requested_stake_invalid")
        if stake_amount < Decimal("0"):
            raise InsufficientStakeError(
                self.id,
                stake=stake_amount,
                required=Decimal("0"),
                message="requested_stake cannot be negative",
            )

        # Ask consensus governance for current ECU fee.
        required_fee = self.consensus.governance.get_task_fee_ecu("claim.submit")
        min_required = required_fee

        # Wallet cannot afford even the minimum fee → no staking.
        if self.wallet_balance < min_required:
            return Decimal("0")

        # Preserve explicit stakes from callers if they are sane.
        if stake_amount >= min_required and stake_amount <= self.wallet_balance:
            return stake_amount

        # If requested stake is below the required fee, bump up to exactly the fee
        # as long as the wallet can pay.
        if stake_amount < min_required and self.wallet_balance >= min_required:
            return min_required

        # If requested stake is more than wallet_balance, cap at wallet_balance.
        if stake_amount > self.wallet_balance:
            return self.wallet_balance

        # Fallback: refuse to stake in any weird edge case.
        return Decimal("0")

    def perform_pow_benchmark(self) -> float:
        """
        Run a hardware / PoW-style benchmark and update this agent's
        trust_vector["potential"].

        The resulting score ∈ [0, 1] is used as a proxy for hardware capability
        (and, in future phases, can inform how aggressively the agent chooses
        to spend stake on ILC tasks).
        """
        # Preserving Phase H Logic
        result = self.benchmark_engine.run(self.id)
        self.trust_vector["potential"] = result["score"]
        self.trust_vector["tier"] = result["tier"]
        logger.info(
            "agent_hardware_verified agent=%s device=%s tier=%s",
            redact_agent_id_for_log(self.id),
            result["device"],
            result["tier"],
        )
        return result["score"]

    def mine_thought(self, content: str, parent_id: str, stake: Decimal) -> Optional[Node]:
        """
        Mine a new claim node linked to parent_id, staking some amount of
        the agent's wallet balance.

        This MVP version now routes the requested stake through
        decide_stake_for_claim(...) to ensure we at least pay the ECU fee
        and never exceed wallet_balance.
        """
        # Decide how much we can/should actually stake given ECU fees + wallet.
        chosen_stake = self.decide_stake_for_claim(stake)

        # If we cannot stake anything meaningful, abort with the existing message.
        if chosen_stake <= Decimal("0") or self.wallet_balance < chosen_stake:
            logger.warning(
                "agent_stake_insufficient_funds agent=%s wallet=%s chosen=%s",
                redact_agent_id_for_log(self.id),
                self.wallet_balance,
                chosen_stake,
            )
            return None

        # Construct the node exactly as before.
        node = Node(
            id="",
            type="claim",
            content=content,
            agent_id=self.id,
            signature=DRAFT_SIGNATURE,
        )
        node.id = node.compute_id()
        self.graph.add_node(node)
        self.graph.add_edge_by_ids(node.id, parent_id, "derives_from")

        # Deduct the chosen stake and register it with the consensus engine.
        self.wallet_balance -= chosen_stake
        success = self.consensus.register_stake(node.id, chosen_stake)
        if not success:
            # In case governance rejects the stake (e.g., ECU fee changed mid-flight),
            # revert the wallet deduction and abort.
            self.wallet_balance += chosen_stake
            logger.warning(
                "agent_stake_rejected_by_consensus agent=%s chosen=%s",
                redact_agent_id_for_log(self.id),
                chosen_stake,
            )
            return None

        logger.info(
            "agent_claim_minted agent=%s node=%s",
            redact_agent_id_for_log(self.id),
            node.id[:8],
        )
        return node

    def auto_mine_claim(self, content: str, parent_id: str) -> Optional[Node]:
        """
        Strategy helper: automatically choose a stake for a claim.submit task
        based on:
        - current wallet_balance,
        - the ECU fee for "claim.submit" (via Governance),
        - this agent's hardware potential (trust_vector["potential"]).

        This is primarily intended for simulations and does not change the
        behavior of mine_thought(...) when called directly with an explicit
        stake.

        MVP strategy:
        - Ensure we have a hardware potential score (run perform_pow_benchmark()
          if needed).
        - Map potential ∈ [0, 1] to a stake fraction ∈ [f_min, f_max] of the
          current wallet_balance.
        - Compute candidate_stake = fraction * wallet_balance.
        - Route candidate_stake through decide_stake_for_claim(...) to enforce
          ECU fees and wallet caps.
        - If the resulting stake is valid, call mine_thought(...) with that
          chosen stake.
        """
        # Ensure we have a potential measurement.
        self._normalize_balances()
        if self.trust_vector.get("potential", 0.0) <= 0.0:
            self.perform_pow_benchmark()

        potential = self.trust_vector.get("potential", 0.0)

        # Low potential → more cautious; high potential → more aggressive.
        # Allow external config (e.g., hardware archetypes) to override.
        f_min = getattr(self, "strategy_stake_fraction_min", 0.05)
        f_max = getattr(self, "strategy_stake_fraction_max", 0.25)
        frac = f_min + (f_max - f_min) * potential

        # Derive a candidate stake from current wallet.
        candidate_stake = Decimal(str(frac)) * self.wallet_balance

        # Let the ECU-aware helper adjust or reject.
        chosen = self.decide_stake_for_claim(candidate_stake)

        if chosen <= Decimal("0") or self.wallet_balance < chosen:
            logger.warning(
                "agent_auto_mine_aborted agent=%s wallet=%s chosen=%s",
                redact_agent_id_for_log(self.id),
                self.wallet_balance,
                chosen,
            )
            return None

        # Delegate actual minting to the existing mine_thought path.
        return self.mine_thought(content, parent_id, chosen)

    def receive_reward(self, amount: Decimal):
        """Handle earnings and auto-repayment."""
        self._normalize_balances()
        reward_amount = _agent_coerce_decimal(amount, "agent_reward_invalid")
        if self.vault:
            repayment, net = self.vault.process_repayment(self.id, reward_amount)
            self.wallet_balance += net
            # Credit balance is technically liability, but simplistic tracking here:
            if repayment > Decimal("0"):
                logger.info(
                    "agent_reward_repayment agent=%s repaid=%s net=%s",
                    redact_agent_id_for_log(self.id),
                    repayment,
                    net,
                )
        else:
            self.wallet_balance += reward_amount

    def refute_node(self, target_id: str, stake: Decimal):
        self._normalize_balances()
        stake_amount = _agent_coerce_decimal(stake, "agent_refutation_stake_invalid")
        if self.wallet_balance < stake_amount:
            logger.warning(
                "agent_refute_insufficient_balance agent=%s target=%s wallet=%s stake=%s",
                redact_agent_id_for_log(self.id),
                target_id,
                self.wallet_balance,
                stake_amount,
            )
            return False
        self.wallet_balance -= stake_amount
        self.consensus.process_contradiction(target_id, stake_amount)
        return True

    def _normalize_balances(self) -> None:
        self.wallet_balance = _agent_coerce_decimal(
            self.wallet_balance, "agent_wallet_balance_invalid"
        )
        self.credit_balance = _agent_coerce_decimal(
            self.credit_balance, "agent_credit_balance_invalid"
        )


def _agent_coerce_decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(token)
    if not isinstance(value, (Decimal, int, float, str)):
        raise ValueError(token)
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(token) from exc
    if not amount.is_finite():
        raise ValueError(f"{token}_non_finite")
    return amount
