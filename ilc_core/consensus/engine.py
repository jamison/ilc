from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Callable, Dict, Optional, List, Protocol
import math
import logging

from ..types import Node
from ..graph import EpistemicGraph
from ..exceptions import InsufficientStakeError
from .clustering import SponsorGraph
from .governance import Governance, BacklogMetrics

logger = logging.getLogger(__name__)


class EdgeEventLike(Protocol):
    source_id: str
    target_id: str
    type: str


def _engine_update_epoch_metrics(
    governance: Governance,
    backlog_len: int,
    finalized_last_epoch: int,
    agent_potentials: Optional[List[float]],
    epoch_index: int
) -> None:
    """Helper to update governance metrics at epoch end."""
    # Update hardware potential if measurements are provided.
    if agent_potentials:
        governance.update_hardware_potential(agent_potentials)

    # Update congestion from backlog metrics.
    metrics = BacklogMetrics(
        backlog_len=backlog_len,
        finalized_last_epoch=finalized_last_epoch,
    )
    governance.update_congestion(metrics)

    # Debug/logging (safe to keep for now; can be swapped for proper logger).
    logger.info(
        "consensus_epoch_metrics epoch=%s backlog=%s finalized=%s hardware_scale=%.4f congestion_mult=%.4f",
        epoch_index + 1,
        backlog_len,
        finalized_last_epoch,
        governance.hardware_scale,
        governance.congestion_multiplier,
    )

def _engine_compute_tax_rate(
    age: float,
    net_stake: Decimal
) -> float:
    """Helper to compute maintenance tax rate based on age and reuse."""
    # Reuse count simulated by net_stake for now.
    reuse_factor = max(1.0, float(net_stake))

    base_tax = 0.01  # 1% per epoch (or per time unit)
    # Decay tax as age and reuse increase.
    product = max(1.0, age * reuse_factor)
    tax_rate = base_tax / (1 + math.log(product))
    return tax_rate

def _engine_compute_bounty_amount(
    base_stake: Decimal,
    age: float,
    node_id: str
) -> Decimal:
    """Helper to compute refutation bounty with paradigm shift bonus."""
    # Tuned exponent to ensure EV < 0 for looting attacks at a 1% error rate
    # (as per earlier design discussions).
    paradigm_bonus = Decimal(str(0.001 * math.pow(age, 1.4)))

    total_bounty = base_stake + paradigm_bonus
    logger.info(
        "consensus_bounty_computed node=%s age_seconds=%.1f bounty=%.4f paradigm_bonus=%.4f",
        node_id[:8],
        age,
        total_bounty,
        paradigm_bonus,
    )
    return total_bounty

def _engine_apply_slash(
    node_stakes: Dict[str, Decimal],
    target_id: str,
    stake_amount: Decimal,
    bounty: Decimal
) -> None:
    """Helper to apply slashing and log jackpot."""
    # The Slash (very simple MVP form).
    current = _engine_coerce_decimal(
        node_stakes.get(target_id, Decimal("0")),
        "consensus_stake_balance_invalid",
    )
    new_balance = current - stake_amount
    node_stakes[target_id] = new_balance

    logger.info(
        "consensus_paradigm_shift_jackpot target=%s bounty=%.4f",
        target_id[:8],
        bounty,
    )
    # Post-MVP: bounty transfer moved to project deferred items file (Consensus section).


def _engine_resolve_age_reference_seconds(
    node: "Node",
    graph: "EpistemicGraph",
    age_reference_clock: "Optional[Callable[[], float]]",
) -> float:
    ts = node.timestamp
    if ts.tzinfo is None:
        raise ValueError("node_timestamp_naive_not_allowed")
    if age_reference_clock is not None:
        return max(ts.timestamp(), float(age_reference_clock()))
    graph_timestamps = [
        candidate.timestamp.timestamp()
        for candidate in graph.nodes.values()
        if candidate.timestamp.tzinfo is not None
    ]
    if not graph_timestamps:
        return ts.timestamp()
    return max(ts.timestamp(), max(graph_timestamps))


class ConsensusEngine:
    """
    ConsensusEngine

    Responsibilities
    ----------------
    - Track node-level staking and simple economic signals.
    - Enforce a minimum stake/fee for supporting a node, priced in ECU via Governance.
    - Compute refutation bounties and handle contradictions/supersedes links.
    - Validate independence of validator sets via SponsorGraph.
    - Surface a simple epoch hook to update congestion and hardware potential in Governance.

    Notes on Units
    --------------
    - All costs are conceptually in ECU (epistemic contribution units), not bare ILC.
      For the MVP, we treat the numeric "amount" here as generic units; the monetary
      layer later interprets them as ILC, with conversion ECU -> ILC done in the
      reward engine.
    """

    def __init__(
        self,
        graph: EpistemicGraph,
        governance_config: Optional[Dict] = None,
        *,
        age_reference_clock: Optional[Callable[[], float]] = None,
    ):
        self.graph = graph

        # Ledger: Node ID -> Staked Amount (Decimal units, interpreted later as ECU/ILC)
        self.node_stakes: Dict[str, Decimal] = {}

        # Capital / sponsorship relationships (for independence checks).
        self.sponsor_graph = SponsorGraph()

        # ECU-anchored, congestion-aware governance surface.
        if governance_config is None:
            from ..config import load_governance_config
            governance_config = load_governance_config()
        
        self.governance = Governance(governance_config)

        # Simple epoch bookkeeping (optional, but useful for logging/debugging).
        self.epoch_index: int = 0
        self.last_epoch_finalized: int = 0
        self._age_reference_clock = age_reference_clock

    # ------------------------------------------------------------------
    # Epoch-level hooks
    # ------------------------------------------------------------------
    def end_epoch_update(
        self,
        backlog_len: int,
        finalized_last_epoch: int,
        agent_potentials: Optional[List[float]] = None,
    ) -> None:
        """
        Called at the end of an epoch to update congestion and hardware
        potential inside Governance.

        Parameters
        ----------
        backlog_len : int
            Number of pending tasks/claims that remain un-finalized at epoch end.
        finalized_last_epoch : int
            Number of tasks finalized during this epoch.
        agent_potentials : Optional[List[float]]
            Optional list of benchmark scores (hardware/intelligence potential)
            for agents participating this epoch.

        Behavior
        --------
        - Updates the global median hardware potential, which *reduces* ECU base
          costs as the network becomes faster (more intelligence per watt).
        - Updates congestion based on backlog and finalized work, which *increases*
          ECU cost when queues are long.
        """
        _engine_update_epoch_metrics(
            self.governance,
            backlog_len,
            finalized_last_epoch,
            agent_potentials,
            self.epoch_index
        )
        
        # Bookkeeping.
        self.epoch_index += 1
        self.last_epoch_finalized = finalized_last_epoch

    # ------------------------------------------------------------------
    # Staking and fee enforcement
    # ------------------------------------------------------------------
    def register_stake(self, node_id: str, amount: Decimal) -> bool:
        """
        Called when an agent supports a node by staking on it.

        For the MVP, we:
        - Enforce a minimum stake/fee based on Governance ECU pricing for
          "claim.submit".
        - Treat 'amount' as denomination-compatible with the ECU fee,
          leaving the monetary layer to convert ECU <-> ILC externally.
        """
        stake_amount = _engine_coerce_decimal(amount, "consensus_stake_invalid")
        if stake_amount < Decimal("0"):
            raise InsufficientStakeError(
                node_id,
                stake=stake_amount,
                required=Decimal("0"),
                message="Cannot stake negative amount",
            )

        # Minimum ECU-based fee for submitting/supporting a claim.
        required_fee = self.governance.get_task_fee_ecu("claim.submit")

        if stake_amount < required_fee:
            logger.warning(
                "consensus_stake_rejected node=%s stake=%s min_fee=%s",
                node_id[:8],
                stake_amount,
                required_fee,
            )
            return False

        current = _engine_coerce_decimal(
            self.node_stakes.get(node_id, Decimal("0")),
            "consensus_stake_balance_invalid",
        )
        self.node_stakes[node_id] = current + stake_amount

        logger.info(
            "consensus_stake_accepted node=%s stake=%s min_fee=%s",
            node_id[:8],
            stake_amount,
            required_fee,
        )
        logger.info(
            "consensus_stake_total node=%s net=%s",
            node_id[:8],
            self.node_stakes[node_id],
        )
        return True

    # ------------------------------------------------------------------
    # Sponsorship and independence
    # ------------------------------------------------------------------
    def register_sponsorship(self, sponsor_id: str, agent_id: str) -> None:
        """Records that a Sponsor funds an Agent, for independence checks."""
        self.sponsor_graph.union(sponsor_id, agent_id)

    def validate_independence(self, validators: list[str]) -> bool:
        """
        Sybil / capital-independence check:

        Returns True only if we have >= 3 distinct sponsor clusters among the
        given validator IDs.

        This matches the high-level principle that K-independent capital roots
        are required for critical panels.
        """
        unique_roots = self.sponsor_graph.get_cluster_count(validators)
        logger.info(
            "consensus_independence_check validators=%s clusters=%s",
            len(validators),
            unique_roots,
        )
        return unique_roots >= 3

    # ------------------------------------------------------------------
    # Node age and maintenance tax
    # ------------------------------------------------------------------
    def get_node_age(self, node: Node) -> float:
        """
        Return deterministic age in seconds for a node.

        Age is computed relative to an explicit injected reference clock when
        provided, otherwise relative to the newest aware timestamp already
        present in the local graph. This avoids wall-clock divergence across
        validators processing the same graph state.
        """
        ts = node.timestamp
        if ts.tzinfo is None:
            raise ValueError("node_timestamp_naive_not_allowed")
        reference_seconds = _engine_resolve_age_reference_seconds(
            node, self.graph, self._age_reference_clock
        )
        return max(1.0, reference_seconds - ts.timestamp())

    def calculate_maintenance_tax(self, node: Node) -> float:
        """
        The Shield: Older, reused nodes pay less tax.

        Implementation
        --------------
        - Age reduces effective tax.
        - Reuse is approximated by node.net_stake for now.

        Returns a fractional rate (e.g. 0.01 = 1%).
        """
        age = self.get_node_age(node)
        return _engine_compute_tax_rate(age, node.net_stake)

    # ------------------------------------------------------------------
    # Refutation bounties and contradictions
    # ------------------------------------------------------------------
    def calculate_refutation_bounty(self, node: Node) -> float:
        """
        The Sword: Older nodes are worth more to destroy.

        Paradigm Shift Bonus = age^1.4 (tuned for safety).

        Returns
        -------
        float
            Total bounty amount in generic units (to be interpreted by the
            monetary layer as ILC denominated reward later).
        """
        base_stake = _engine_coerce_decimal(
            self.node_stakes.get(node.id, Decimal("0")),
            "consensus_stake_balance_invalid",
        )
        age = self.get_node_age(node)
        return _engine_compute_bounty_amount(base_stake, age, node.id)

    def process_edge(self, edge: EdgeEventLike, stake_amount: Decimal = Decimal("0")) -> None:
        """Dispatch edge processing based on type."""
        if edge.type == "refutes":
            self.process_contradiction(edge.target_id, stake_amount)
        elif edge.type == "supersedes":
            self.process_update(edge)

    def process_contradiction(self, target_id: str, stake_amount: Decimal) -> None:
        """
        Handle a contradiction/refutation attempt against a target node.

        For the MVP:
        - Compute a refutation bounty for the target.
        - Slash the target's stake by `stake_amount`.
        - Log the "jackpot" value; in a full system, this would transfer to
          the refuter's account and integrate with vesting/clawback logic.
        """
        if target_id not in self.graph.nodes:
            return

        node = self.graph.nodes[target_id]

        bounty = self.calculate_refutation_bounty(node)
        
        _engine_apply_slash(
            self.node_stakes,
            target_id,
            _engine_coerce_decimal(stake_amount, "consensus_refutation_stake_invalid"),
            bounty,
        )

    # ------------------------------------------------------------------
    # Supersedes / evolution handling
    # ------------------------------------------------------------------
    def process_update(self, edge: EdgeEventLike) -> None:
        """
        Handles 'supersedes' links.

        Unlike refutation, this does not slash; it deprecates older nodes in
        favor of newer ones. For the MVP, we simply log the evolution.
        """
        if edge.type != "supersedes":
            return

        old_id = edge.target_id
        new_id = edge.source_id

        if old_id in self.node_stakes:
            logger.info(
                "consensus_supersedes_applied new=%s old=%s",
                new_id[:8],
                old_id[:8],
            )
            logger.info(
                "consensus_supersedes_preserved old=%s stake=%s",
                old_id[:8],
                self.node_stakes[old_id],
            )
        else:
            logger.warning(
                "consensus_supersedes_missing_old old=%s",
                old_id[:8],
            )

    # ------------------------------------------------------------------
    # Canonicality checks
    # ------------------------------------------------------------------
    def is_canonical(self, node_id: str) -> bool:
        """
        The Truth Test (MVP version).

        - Genesis nodes are always treated as canonical.
        - Other nodes must have positive stake to be considered canonical.

        In later versions, this will be replaced by:
        - auditor-panel seals,
        - vesting-based economic confirmation,
        - contradiction windows,
        - and explicit link semantics.
        """
        if node_id not in self.graph.nodes:
            return False

        node = self.graph.nodes[node_id]
        if node.type == "genesis":
            return True

        return self.node_stakes.get(node_id, Decimal("0")) > Decimal("0")


def _engine_coerce_decimal(value: object, token: str) -> Decimal:
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
