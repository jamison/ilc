"""Phase 1535p OBL-020 emission-only economic round-trip integration test."""

from __future__ import annotations

import json
from decimal import Decimal

from ilc_core.epoch.canonical_economic_event import (
    emit_canonical_economic_event_records,
)
from ilc_core.epoch.epoch_emission_production_path import (
    PRODUCTION_EMISSION_NOT_ACTIVATED,
    compute_epoch_emission_production_path,
    compute_settlement_root,
)


CANONICAL_EPOCH = 1
CANONICAL_CUMULATIVE = Decimal("0")
CANONICAL_FEES = Decimal("100.000000000")
_LOWER_HEX = frozenset("0123456789abcdef")


def _round_trip():
    result = compute_epoch_emission_production_path(
        issuance_epoch=CANONICAL_EPOCH,
        cumulative_issued_before_epoch_ilc=CANONICAL_CUMULATIVE,
        total_epoch_fees_ilc=CANONICAL_FEES,
    )
    root = compute_settlement_root(result)
    events = emit_canonical_economic_event_records(result, root)
    event_dicts = [json.loads(event.to_canonical_json()) for event in events]
    return result, root, events, event_dicts


def test_phase_1535p_emission_round_trip_replays_byte_identically() -> None:
    result, root, events, event_dicts = _round_trip()
    result2, root2, events2, event_dicts2 = _round_trip()

    assert root.root_hex == root2.root_hex
    assert root.canonical_record_json == root2.canonical_record_json
    assert len(events) == len(events2)
    assert event_dicts == event_dicts2

    for event, event2 in zip(events, events2, strict=True):
        assert event.amount_ilc_str == event2.amount_ilc_str
        assert event.settlement_root_hex == event2.settlement_root_hex
        assert event.role == event2.role
        assert event.to_canonical_json() == event2.to_canonical_json()

    # Guard cleared by Phase 1575g.
    assert PRODUCTION_EMISSION_NOT_ACTIVATED is False
    assert result.production_emission_activated is True
    assert result2.production_emission_activated is True
    assert all(event.production_emission_activated is True for event in events)
    assert all(event.production_emission_activated is True for event in events2)
    assert all(Decimal(event.amount_ilc_str).is_finite() for event in events)
    assert [event.role for event in events] == [
        "scheduled_emission_pool",
        "performer_pool",
        "auditor_pool",
        "genesis_overhead_pool",
        "genesis_burn_pool",
    ]
    event_sum = sum((Decimal(event.amount_ilc_str) for event in events), Decimal("0"))
    assert event_sum == (
        result.emission_quote.capped_epoch_budget_ilc
        + result.fee_burn_quote.total_epoch_fees_ilc
    )
    assert len(root.root_hex) == 64
    assert all(char in _LOWER_HEX for char in root.root_hex)
