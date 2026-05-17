"""Phase 946 — H-012 EpochAttributionBatch.settle() runtime.

Implements CDL-081 §§4.1–4.6 attribution settlement logic. Delegates from
EpochAttributionBatch.settle() in ilc_core.types.

CDL-083 ratified Phase 1105: ejected stake treasury quorum rules and REFUTATION
attribution implemented. Phase 1106 adds the ejected-stake vote evaluation helper.
CDL-084 ratified Phase 1113: PROVENANCE chain attribution; float kill for
PROVENANCE_DECAY_ALPHA; AttributionEvent.provenance_chain field added.
CDL-084 PROVENANCE settlement path activated Phase 1114: silent-ignore stub replaced
with geometric decay ECU payout.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import TYPE_CHECKING, Any, Optional

from ilc_core.types import (
    EDGE_MINT_PHI_BOUND,
    EdgeType,
    PROVENANCE_DECAY_ALPHA,
    PROVENANCE_MAX_DEPTH,
    REUSE_ATTRIBUTION_RATE,
)

if TYPE_CHECKING:
    from ilc_core.types import EpochAttributionBatch

EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1210.v0.7"
CDL_081_DEPENDENCY = "cdl_081_hyperedge_ecu_attribution_ratified_943.v0.1"
CDL_HCON_02_DEPENDENCY = "h_con_02_cdl_required_before_ejected_stake_treasury_executes"
CDL_083_DEPENDENCY = "cdl_083_h_con_02_ratified_1105.v0.1"
CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"
CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"
CDL_083_EJECTED_STAKE_TREASURY_DISTRIBUTION_TOKEN = (
    "cdl_083_ejected_stake_treasury_distribution_phase_1350.v0.1"
)
H_CON_02_QUORUM_GUARD_PHASE_1350_TOKEN = "h_con_02_quorum_guard_phase_1350"
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_NOT_IMPLEMENTED_CLOSED_PHASE_1350_TOKEN = (
    "epoch_attribution_settle_runtime_not_implemented_closed_phase_1350"
)
EJECTED_STAKE_DISTRIBUTION_NOT_ACTIVATED_TOKEN = (
    "ejected_stake_distribution_not_activated_phase_1350"
)
PRODUCTION_EJECTED_STAKE_DISTRIBUTION_ACTIVATION_TOKEN = (
    "phase_1366_soft_rc_eligible_true_value_path_activation_required"
)
MAX_PROVENANCE_CHAIN_INPUT_LENGTH = 64

HCON02_QUORUM_FLOOR = Decimal("0.50")       # Q1: >=50% of remaining members must vote
HCON02_QUORUM_MINIMUM_VOTERS = 2            # Q1: hard minimum regardless of group size
HCON02_VOTE_THRESHOLD_NUMERATOR = 2         # Q2: exact 2/3 — integer arithmetic only
HCON02_VOTE_THRESHOLD_DENOMINATOR = 3       # Q2: exact 2/3 — integer arithmetic only

_ZERO = Decimal("0")
_PAYOUT_QUANTUM = Decimal("0.000000001")
MAX_PAYOUT_QUANTIZE_ADJUSTED_EXPONENT = 18
INVALID_AMOUNT_MAGNITUDE_TOKEN = "invalid_amount_magnitude"


def _quantize_payout(amount: Decimal) -> Decimal:
    if amount.adjusted() > MAX_PAYOUT_QUANTIZE_ADJUSTED_EXPONENT:
        raise ValueError(INVALID_AMOUNT_MAGNITUDE_TOKEN)
    return amount.quantize(_PAYOUT_QUANTUM, rounding=ROUND_DOWN)


def _stake_proportional_payouts(
    total_amount: Decimal,
    members: dict[str, Decimal],
    total_stake: Decimal,
) -> list[tuple[str, Decimal]]:
    """Allocate a proportional Decimal amount with deterministic residual handling."""
    if not members or total_stake == _ZERO:
        return []
    running_total = _ZERO
    ordered_members = sorted(members.items(), key=lambda item: item[0])
    payouts: list[tuple[str, Decimal]] = []
    for index, (agent_id, stake) in enumerate(ordered_members):
        if index == len(ordered_members) - 1:
            share = total_amount - running_total
        else:
            share = _quantize_payout(total_amount * (stake / total_stake))
            running_total += share
        payouts.append((agent_id, share))
    return payouts


@dataclass(frozen=True)
class EjectedStakeTreasuryDistributionQuote:
    """Default-off Phase 1350 quote for CDL-083 ejected-stake release."""

    runtime_version: str
    cdl_083_dependency: str
    distribution_token: str
    h_con_02_guard_token: str
    historical_not_implemented_closed_token: str
    distribution_epoch: int
    ejected_stake_ilc: Decimal
    remaining_member_stake_total_ilc: Decimal
    remaining_member_count: int
    participating_voters: int
    approve_votes: int
    quorum_floor: Decimal
    quorum_minimum_voters: int
    vote_threshold_numerator: int
    vote_threshold_denominator: int
    payouts: tuple[tuple[str, Decimal], ...]
    production_ejected_stake_distribution_activated: bool
    decision_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "approve_votes": self.approve_votes,
            "cdl_083_dependency": self.cdl_083_dependency,
            "decision_token": self.decision_token,
            "distribution_epoch": self.distribution_epoch,
            "distribution_token": self.distribution_token,
            "ejected_stake_ilc": _decimal_to_string(self.ejected_stake_ilc),
            "h_con_02_guard_token": self.h_con_02_guard_token,
            "historical_not_implemented_closed_token": (
                self.historical_not_implemented_closed_token
            ),
            "participating_voters": self.participating_voters,
            "payouts": tuple(
                {
                    "agent_id": agent_id,
                    "amount_ilc": _decimal_to_string(amount),
                }
                for agent_id, amount in self.payouts
            ),
            "production_ejected_stake_distribution_activated": (
                self.production_ejected_stake_distribution_activated
            ),
            "quorum_floor": _decimal_to_string(self.quorum_floor),
            "quorum_minimum_voters": self.quorum_minimum_voters,
            "remaining_member_count": self.remaining_member_count,
            "remaining_member_stake_total_ilc": _decimal_to_string(
                self.remaining_member_stake_total_ilc
            ),
            "runtime_version": self.runtime_version,
            "vote_threshold_denominator": self.vote_threshold_denominator,
            "vote_threshold_numerator": self.vote_threshold_numerator,
        }


def _decimal_to_string(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _require_non_negative_int(value: object, error_token: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(error_token)
    return value


def _require_decimal_amount(
    value: object,
    field_name: str,
    *,
    positive: bool = False,
) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field_name}_must_be_exact_decimal")
    if not isinstance(value, (Decimal, int, str)):
        raise ValueError(f"{field_name}_must_be_exact_decimal")
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name}_must_be_exact_decimal") from exc
    if not amount.is_finite():
        raise ValueError("invalid_amount_non_finite")
    if positive and amount <= _ZERO:
        raise ValueError(f"{field_name}_must_be_positive")
    if not positive and amount < _ZERO:
        raise ValueError(f"{field_name}_must_be_non_negative")
    if amount.adjusted() > MAX_PAYOUT_QUANTIZE_ADJUSTED_EXPONENT:
        raise ValueError(INVALID_AMOUNT_MAGNITUDE_TOKEN)
    return amount


def _normalize_distribution_member_stakes(members: object) -> dict[str, Decimal]:
    if not isinstance(members, dict):
        raise ValueError("ejected_stake_remaining_members_must_be_dict")
    normalized: dict[str, Decimal] = {}
    for member_id, stake in members.items():
        if not isinstance(member_id, str) or member_id == "":
            raise ValueError("ejected_stake_member_id_must_be_non_empty_string")
        normalized[member_id] = _require_decimal_amount(
            stake,
            "ejected_stake_member_stake",
        )
    return normalized


def require_h_con_02_quorum_guard(
    remaining_member_stakes: object,
    approve_votes: object,
    participating_voters: object,
) -> dict[str, Decimal]:
    """Fail closed unless the CDL-083 H-CON-02 quorum and threshold pass."""

    members = _normalize_distribution_member_stakes(remaining_member_stakes)
    approvals = _require_non_negative_int(
        approve_votes,
        "approve_votes_must_be_non_negative_integer",
    )
    voters = _require_non_negative_int(
        participating_voters,
        "participating_voters_must_be_non_negative_integer",
    )
    if approvals > voters:
        raise ValueError("approve_votes_must_not_exceed_participating_voters")

    total_members = len(members)
    if total_members == 0:
        raise ValueError("h_con_02_quorum_guard_no_remaining_members_phase_1350")
    if voters > total_members:
        raise ValueError("participating_voters_must_not_exceed_total_members")
    if voters < HCON02_QUORUM_MINIMUM_VOTERS:
        raise ValueError("h_con_02_quorum_guard_minimum_voters_not_met_phase_1350")
    if Decimal(voters) / Decimal(total_members) < HCON02_QUORUM_FLOOR:
        raise ValueError("h_con_02_quorum_guard_floor_not_met_phase_1350")
    if (
        approvals * HCON02_VOTE_THRESHOLD_DENOMINATOR
        < voters * HCON02_VOTE_THRESHOLD_NUMERATOR
    ):
        raise ValueError("h_con_02_quorum_guard_threshold_not_met_phase_1350")
    return members


def build_ejected_stake_treasury_distribution_quote(
    distribution_epoch: int,
    ejected_stake_ilc: object,
    remaining_member_stakes: object,
    approve_votes: int,
    participating_voters: int,
) -> EjectedStakeTreasuryDistributionQuote:
    """Build a non-activating CDL-083 ejected-stake distribution quote."""

    epoch = _require_non_negative_int(
        distribution_epoch,
        "ejected_stake_distribution_epoch_must_be_non_negative_integer",
    )
    ejected_stake = _quantize_payout(
        _require_decimal_amount(ejected_stake_ilc, "ejected_stake_ilc", positive=True)
    )
    members = require_h_con_02_quorum_guard(
        remaining_member_stakes,
        approve_votes,
        participating_voters,
    )
    total_stake = sum(members.values(), _ZERO)
    if total_stake == _ZERO:
        raise ValueError("ejected_stake_distribution_requires_positive_remaining_stake_phase_1350")

    approved, payouts = evaluate_ejected_stake_vote(
        ejected_stake,
        members,
        approve_votes,
        participating_voters,
    )
    if not approved:
        raise ValueError("h_con_02_quorum_guard_phase_1350_failed")

    return EjectedStakeTreasuryDistributionQuote(
        runtime_version=EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
        cdl_083_dependency=CDL_083_DEPENDENCY,
        distribution_token=CDL_083_EJECTED_STAKE_TREASURY_DISTRIBUTION_TOKEN,
        h_con_02_guard_token=H_CON_02_QUORUM_GUARD_PHASE_1350_TOKEN,
        historical_not_implemented_closed_token=(
            EPOCH_ATTRIBUTION_SETTLE_RUNTIME_NOT_IMPLEMENTED_CLOSED_PHASE_1350_TOKEN
        ),
        distribution_epoch=epoch,
        ejected_stake_ilc=ejected_stake,
        remaining_member_stake_total_ilc=total_stake,
        remaining_member_count=len(members),
        participating_voters=participating_voters,
        approve_votes=approve_votes,
        quorum_floor=HCON02_QUORUM_FLOOR,
        quorum_minimum_voters=HCON02_QUORUM_MINIMUM_VOTERS,
        vote_threshold_numerator=HCON02_VOTE_THRESHOLD_NUMERATOR,
        vote_threshold_denominator=HCON02_VOTE_THRESHOLD_DENOMINATOR,
        payouts=tuple(payouts),
        production_ejected_stake_distribution_activated=False,
        decision_token=EJECTED_STAKE_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    )


def require_production_ejected_stake_distribution_activation(
    activation_token: str | None = None,
) -> None:
    if activation_token != PRODUCTION_EJECTED_STAKE_DISTRIBUTION_ACTIVATION_TOKEN:
        raise ValueError(EJECTED_STAKE_DISTRIBUTION_NOT_ACTIVATED_TOKEN)
    raise ValueError("production_ejected_stake_distribution_activation_not_implemented_phase_1350")


def _require_non_empty_string(value: object, error_token: str) -> str:
    if not isinstance(value, str) or value == "":
        raise ValueError(error_token)
    return value


def _validate_provenance_chain(chain: object) -> tuple[tuple[str, str], ...]:
    """Validate caller-supplied PROVENANCE payload before payout arithmetic."""
    if chain is None:
        raise ValueError("provenance_event_missing_chain")
    if not isinstance(chain, tuple):
        raise ValueError("provenance_chain_must_be_tuple")
    if len(chain) == 0:
        raise ValueError("provenance_event_empty_chain")
    if len(chain) > MAX_PROVENANCE_CHAIN_INPUT_LENGTH:
        raise ValueError("provenance_chain_exceeds_input_bound")

    seen_node_ids: set[str] = set()
    normalized: list[tuple[str, str]] = []
    for entry in chain:
        if not isinstance(entry, tuple) or len(entry) != 2:
            raise ValueError("provenance_chain_entry_must_be_node_creator_pair")
        node_id = _require_non_empty_string(
            entry[0],
            "provenance_chain_node_id_must_be_non_empty_string",
        )
        creator_id = _require_non_empty_string(
            entry[1],
            "provenance_chain_creator_id_must_be_non_empty_string",
        )
        if node_id in seen_node_ids:
            raise ValueError("provenance_chain_contains_duplicate_node_id")
        seen_node_ids.add(node_id)
        normalized.append((node_id, creator_id))
    return tuple(normalized)


def _normalize_member_stakes(members: object) -> dict[str, Decimal]:
    """Validate stake_map member stakes before proportional settlement."""
    if not isinstance(members, dict):
        raise ValueError("stake_map_members_must_be_dict")
    normalized: dict[str, Decimal] = {}
    for member_id, stake in members.items():
        if not isinstance(member_id, str):
            raise ValueError("stake_map_member_id_must_be_string")
        if not isinstance(stake, Decimal):
            raise ValueError("stake_map_member_stake_must_be_decimal")
        if not stake.is_finite() or stake < _ZERO:
            raise ValueError("stake_map_member_stake_must_be_non_negative_finite_decimal")
        normalized[member_id] = stake
    return normalized


def evaluate_ejected_stake_vote(
    ejected_stake: Decimal,
    remaining_member_stakes: dict[str, Decimal],
    approve_votes: int,
    participating_voters: int,
) -> tuple[bool, list[tuple[str, Decimal]]]:
    """Evaluate CDL-083 H-CON-02 ejected stake treasury distribution.

    Implements CDL-083 §§5.1-5.3 only: quorum floor, exact 2/3 approval
    threshold, and stake-proportional distribution among all remaining
    members. CDL-083 §5.5 irrevocability is enforced by the caller.
    """
    if (
        not isinstance(ejected_stake, Decimal)
        or not ejected_stake.is_finite()
        or ejected_stake <= _ZERO
    ):
        raise ValueError("ejected_stake_must_be_positive_finite_decimal")
    if ejected_stake.adjusted() > MAX_PAYOUT_QUANTIZE_ADJUSTED_EXPONENT:
        raise ValueError(INVALID_AMOUNT_MAGNITUDE_TOKEN)

    members = _normalize_member_stakes(remaining_member_stakes)

    if type(approve_votes) is not int or approve_votes < 0:
        raise ValueError("approve_votes_must_be_non_negative_integer")
    if type(participating_voters) is not int or participating_voters < 0:
        raise ValueError("participating_voters_must_be_non_negative_integer")
    if approve_votes > participating_voters:
        raise ValueError("approve_votes_must_not_exceed_participating_voters")

    total_members = len(members)
    # No remaining active members means there is no valid voting population for CDL-083 Q1.
    if total_members == 0:
        return (False, [])
    # CDL-083 Q1: participating_voters counts votes from remaining members — the same
    # population as remaining_member_stakes. Voters cannot exceed that pool.
    if participating_voters > total_members:
        raise ValueError("participating_voters_must_not_exceed_total_members")
    quorum_met = (
        participating_voters >= HCON02_QUORUM_MINIMUM_VOTERS
        and (
            total_members == 0
            or Decimal(participating_voters) / Decimal(total_members) >= HCON02_QUORUM_FLOOR
        )
    )
    if not quorum_met:
        return (False, [])

    threshold_met = (
        approve_votes * HCON02_VOTE_THRESHOLD_DENOMINATOR
        >= participating_voters * HCON02_VOTE_THRESHOLD_NUMERATOR
    )
    if not threshold_met:
        return (False, [])

    total_stake = sum(members.values(), _ZERO)
    if total_stake == _ZERO:
        return (True, [])

    return (True, _stake_proportional_payouts(ejected_stake, members, total_stake))


@dataclass(frozen=True)
class AttributionEvent:
    """A single traversal clearance record for attribution settlement.

    Defined in the settle runtime so that callers constructing batches
    do not need to import from types.py (avoids circular import risk).

    CDL-081 §4.1: each event is processed with a fresh visited_set.
    """
    edge_type: EdgeType
    target_creator_id: str        # REUSE / CO_AUTHORSHIP recipient; do not use for REFUTATION
    star_node_id: Optional[str]
    epoch: int
    refuting_agent_id: Optional[str] = None  # REFUTATION only — explicit payout recipient
    provenance_chain: Optional[tuple[tuple[str, str], ...]] = None
    # Q6: ((node_id, creator_id), ...) ordered nearest-ancestor-first.
    # None is valid for non-PROVENANCE events; Phase 1114 validates PROVENANCE events.


def settle_attribution_batch(
    batch: "EpochAttributionBatch",
    stake_map: dict[str, dict[str, Decimal]],
    emitted_tokens: Optional[list[str]] = None,
    epoch_node_mint_count: int = 0,
) -> list[tuple[str, Decimal]]:
    """Process a batch of attribution events and return ECU payout quotes.

    CDL-081 §§4.1–4.6. All amounts returned are Decimal. No float arithmetic.

    Args:
        batch: The sealed EpochAttributionBatch containing AttributionEvent objects.
        stake_map: {star_node_id: {member_agent_id: stake_amount (Decimal)}}.
            For REUSE events, stake_map is not accessed.
            Empty inner dict → zero-member commons path (CDL-081 §4.6).
        emitted_tokens: Optional mutable list. If provided, protocol event tokens
            (e.g. cdl_081_zero_member_commons_transition) are appended here.
        epoch_node_mint_count: Count of node-mint events in the epoch. Used by
            CDL-085 φ-bound enforcement for PROVENANCE payout suppression.

    Returns:
        List of (agent_id, ecu_amount) Decimal payout quotes. May contain multiple
        entries for the same agent_id — callers aggregate and apply at most once.

    Raises:
        ValueError: If a REFUTATION event lacks an explicit refuting_agent_id.
    """
    if type(epoch_node_mint_count) is not int or epoch_node_mint_count < 0:
        raise ValueError("epoch_node_mint_count_must_be_non_negative")

    payouts: list[tuple[str, Decimal]] = []
    provenance_events_processed = 0
    zero_count_skip_token_emitted = False

    for event in batch.events:
        # CDL-081 §4.1: fresh visited_set per event — no cross-event contamination.
        visited_set: set[str] = set()

        # Cast to AttributionEvent — callers are responsible for event construction.
        attr_event: AttributionEvent = event  # type: ignore[assignment]

        if attr_event.edge_type == EdgeType.REUSE:
            # §4.1 REUSE attribution — creator of target node receives REUSE_ATTRIBUTION_RATE.
            # visited_set deduplication: same creator cannot receive twice per event.
            if attr_event.target_creator_id in visited_set:
                continue
            visited_set.add(attr_event.target_creator_id)
            payouts.append((attr_event.target_creator_id, REUSE_ATTRIBUTION_RATE))

        elif attr_event.edge_type == EdgeType.CO_AUTHORSHIP:
            # §4.2 CO_AUTHORSHIP proportional split among star node members.
            members = _normalize_member_stakes(stake_map.get(attr_event.star_node_id or "", {}))
            if not members:
                # §4.6 Zero-member commons: attribution suspended.
                if emitted_tokens is not None:
                    emitted_tokens.append("cdl_081_zero_member_commons_transition")
                continue
            total_stake = sum(members.values(), _ZERO)
            if total_stake == _ZERO:
                # Pathological: members present but all zero stakes — safe skip.
                continue
            payouts.extend(
                _stake_proportional_payouts(
                    REUSE_ATTRIBUTION_RATE,
                    members,
                    total_stake,
                )
            )

        elif attr_event.edge_type == EdgeType.REFUTATION:
            # §5.4 CDL-083: caller-filter guarantees only upheld REFUTATION
            # events enter the batch. Pay the refuting agent, not the refuted
            # target creator.
            recipient_id = attr_event.refuting_agent_id
            if recipient_id is None:
                raise ValueError("refutation_event_missing_refuting_agent_id")
            if recipient_id in visited_set:
                continue
            visited_set.add(recipient_id)
            payouts.append((recipient_id, REUSE_ATTRIBUTION_RATE))

        elif attr_event.edge_type == EdgeType.PROVENANCE:
            # CDL-084 §3.4: PROVENANCE chain attribution.
            # Q10: malformed chains fail closed with stable error tokens before payout.
            chain = _validate_provenance_chain(attr_event.provenance_chain)
            phi_bound_exceeded = False
            if epoch_node_mint_count == 0:
                if emitted_tokens is not None and not zero_count_skip_token_emitted:
                    emitted_tokens.append("edge_mint_phi_bound_enforcement_skipped_no_node_mints")
                    zero_count_skip_token_emitted = True
            else:
                provenance_ratio = (
                    Decimal(provenance_events_processed) / Decimal(epoch_node_mint_count)
                )
                phi_bound_exceeded = provenance_ratio >= EDGE_MINT_PHI_BOUND
                if phi_bound_exceeded and emitted_tokens is not None:
                    emitted_tokens.append("edge_mint_phi_bound_exceeded")

            # Q5/Q7: pay each creator at most once per event; nearest hop wins.
            visited_creators: set[str] = set()
            for hop_index, (node_id, creator_id) in enumerate(chain):
                if hop_index >= PROVENANCE_MAX_DEPTH:
                    break  # Q3: max depth enforced — hops beyond depth 3 are ignored.
                if creator_id in visited_creators:
                    continue  # Q7: nearest hop wins; skip duplicate creators.
                visited_creators.add(creator_id)
                if phi_bound_exceeded:
                    payouts.append((creator_id, _ZERO))
                    continue
                # Q2: geometric decay — alpha^(hop+1), where hop_index 0 = hop 1.
                decay = PROVENANCE_DECAY_ALPHA ** (hop_index + 1)
                payout = _quantize_payout(REUSE_ATTRIBUTION_RATE * decay)
                payouts.append((creator_id, payout))
            provenance_events_processed += 1

        else:
            # §4.3 ATTESTATION, EPOCH_BOUNDARY — silently ignored.
            continue

    return payouts
