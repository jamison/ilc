"""Phase 946 — H-012 EpochAttributionBatch.settle() runtime.

Implements CDL-081 §§4.1–4.6 attribution settlement logic. Delegates from
EpochAttributionBatch.settle() in ilc_core.types.

CDL-083 ratified Phase 1105: ejected stake treasury quorum rules and REFUTATION
attribution implemented. Phase 1106 adds the ejected-stake vote evaluation helper.
CDL-084 ratified Phase 1113: PROVENANCE chain attribution; float kill for
PROVENANCE_DECAY_ALPHA; AttributionEvent.provenance_chain field added.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from ilc_core.types import (
    EdgeType,
    PROVENANCE_DECAY_ALPHA,
    PROVENANCE_MAX_DEPTH,
    REUSE_ATTRIBUTION_RATE,
)

if TYPE_CHECKING:
    from ilc_core.types import EpochAttributionBatch

EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1106.v0.2"
CDL_081_DEPENDENCY = "cdl_081_hyperedge_ecu_attribution_ratified_943.v0.1"
CDL_HCON_02_DEPENDENCY = "h_con_02_cdl_required_before_ejected_stake_treasury_executes"
CDL_083_DEPENDENCY = "cdl_083_h_con_02_ratified_1105.v0.1"
CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"

HCON02_QUORUM_FLOOR = Decimal("0.50")       # Q1: >=50% of remaining members must vote
HCON02_QUORUM_MINIMUM_VOTERS = 2            # Q1: hard minimum regardless of group size
HCON02_VOTE_THRESHOLD_NUMERATOR = 2         # Q2: exact 2/3 — integer arithmetic only
HCON02_VOTE_THRESHOLD_DENOMINATOR = 3       # Q2: exact 2/3 — integer arithmetic only

_ZERO = Decimal("0")


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

    members = _normalize_member_stakes(remaining_member_stakes)

    if type(approve_votes) is not int or approve_votes < 0:
        raise ValueError("approve_votes_must_be_non_negative_integer")
    if type(participating_voters) is not int or participating_voters < 0:
        raise ValueError("participating_voters_must_be_non_negative_integer")
    if approve_votes > participating_voters:
        raise ValueError("approve_votes_must_not_exceed_participating_voters")

    total_members = len(members)
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

    payouts: list[tuple[str, Decimal]] = []
    for agent_id, stake in members.items():
        share = ejected_stake * (stake / total_stake)
        payouts.append((agent_id, share))
    return (True, payouts)


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

    Returns:
        List of (agent_id, ecu_amount) Decimal payout quotes. May contain multiple
        entries for the same agent_id — callers aggregate and apply at most once.

    Raises:
        ValueError: If a REFUTATION event lacks an explicit refuting_agent_id.
    """
    payouts: list[tuple[str, Decimal]] = []

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
            for member_id, member_stake in members.items():
                fraction = member_stake / total_stake
                payout = REUSE_ATTRIBUTION_RATE * fraction
                payouts.append((member_id, payout))

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

        else:
            # §4.3 ATTESTATION, PROVENANCE, EPOCH_BOUNDARY — silently ignored.
            continue

    return payouts
