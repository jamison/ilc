"""Phase 946 — H-012 EpochAttributionBatch.settle() runtime.

Implements CDL-081 §§4.1–4.6 attribution settlement logic. Delegates from
EpochAttributionBatch.settle() in ilc_core.types.

CDL-081 ratified Phase 943. Partial: ejected stake treasury sub-path
(CDL-081 §4.5) is stubbed pending H-CON-02 ratification.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from ilc_core.types import EdgeType, REUSE_ATTRIBUTION_RATE

if TYPE_CHECKING:
    from ilc_core.types import EpochAttributionBatch

EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_946.v0.1"
CDL_081_DEPENDENCY = "cdl_081_hyperedge_ecu_attribution_ratified_943.v0.1"
CDL_HCON_02_DEPENDENCY = "h_con_02_cdl_required_before_ejected_stake_treasury_executes"

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


@dataclass(frozen=True)
class AttributionEvent:
    """A single traversal clearance record for attribution settlement.

    Defined in the settle runtime so that callers constructing batches
    do not need to import from types.py (avoids circular import risk).

    CDL-081 §4.1: each event is processed with a fresh visited_set.
    """
    edge_type: EdgeType          # REUSE or CO_AUTHORSHIP (others silently ignored — §4.3)
    target_creator_id: str       # REUSE: creator of target node receives REUSE_ATTRIBUTION_RATE
    star_node_id: Optional[str]  # CO_AUTHORSHIP: star node identifier for stake_map lookup
    epoch: int                   # Epoch at which traversal was cleared


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
        NotImplementedError: For EdgeType.REFUTATION (ejected stake treasury
            path requires H-CON-02 — CDL_HCON_02_DEPENDENCY).
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
            # §4.5 Ejected stake / refutation treasury path — H-CON-02 required.
            raise NotImplementedError(CDL_HCON_02_DEPENDENCY)

        else:
            # §4.3 ATTESTATION, PROVENANCE, EPOCH_BOUNDARY — silently ignored.
            continue

    return payouts
