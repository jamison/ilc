"""Phase 1534p canonical economic event emitter tests."""

from __future__ import annotations

import json
from dataclasses import replace
from decimal import Decimal

import pytest

from ilc_core.epoch.canonical_economic_event import (
    CANONICAL_ECONOMIC_EVENT_RECORD_SCHEMA_VERSION,
    CDL_AUTHORITY_TOKENS,
    CanonicalEconomicEventRecord,
    emit_canonical_economic_event_records,
)
from ilc_core.epoch.epoch_emission_production_path import (
    PRODUCTION_EMISSION_NOT_ACTIVATED,
    compute_epoch_emission_production_path,
    compute_settlement_root,
)


def _result_and_root():
    result = compute_epoch_emission_production_path(
        9,
        Decimal("1000.000000001"),
        Decimal("250.000000009"),
    )
    return result, compute_settlement_root(result)


def _events() -> list[CanonicalEconomicEventRecord]:
    result, root = _result_and_root()
    return emit_canonical_economic_event_records(result, root)


def test_phase_1534p_emits_expected_standard_roles() -> None:
    events = _events()

    assert [event.role for event in events] == [
        "performer_pool",
        "auditor_pool",
        "genesis_overhead_pool",
        "genesis_burn_pool",
        "rounding_residual",
    ]


def test_phase_1534p_events_remain_default_off() -> None:
    assert PRODUCTION_EMISSION_NOT_ACTIVATED is True
    for event in _events():
        assert event.production_emission_activated is False


def test_phase_1534p_amounts_parse_without_precision_loss() -> None:
    result, root = _result_and_root()
    events = emit_canonical_economic_event_records(result, root)
    by_role = {event.role: Decimal(event.amount_ilc_str) for event in events}

    assert by_role["performer_pool"] == result.allocation_quote.performer_reward_pool_ilc
    assert by_role["auditor_pool"] == result.allocation_quote.auditor_reward_pool_ilc
    assert (
        by_role["genesis_overhead_pool"]
        == result.allocation_quote.genesis_overhead_pool_ilc
    )
    assert by_role["genesis_burn_pool"] == result.fee_burn_quote.genesis_burn_pool_ilc
    assert by_role["rounding_residual"] == (
        result.allocation_quote.rounding_residual_to_genesis_overhead_ilc
        + result.allocation_quote.rounding_residual_to_upheld_refutation_recipients_ilc
        + result.allocation_quote.rounding_residual_to_performer_pool_ilc
    )


def test_phase_1534p_rejects_float_pool_amount() -> None:
    result, root = _result_and_root()
    bad_allocation = replace(result.allocation_quote, performer_reward_pool_ilc=1.0)
    bad_result = replace(result, allocation_quote=bad_allocation)

    with pytest.raises(ValueError, match="float_in_canonical_economic_event_rejected"):
        emit_canonical_economic_event_records(bad_result, root)


@pytest.mark.parametrize("bad_amount", [Decimal("NaN"), Decimal("Infinity")])
def test_phase_1534p_rejects_non_finite_pool_amount(bad_amount: Decimal) -> None:
    result, root = _result_and_root()
    bad_allocation = replace(result.allocation_quote, auditor_reward_pool_ilc=bad_amount)
    bad_result = replace(result, allocation_quote=bad_allocation)

    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        emit_canonical_economic_event_records(bad_result, root)


def test_phase_1534p_settlement_root_hex_is_injected() -> None:
    result, root = _result_and_root()
    events = emit_canonical_economic_event_records(result, root)

    for event in events:
        assert event.settlement_root_hex == root.root_hex


def test_phase_1534p_canonical_json_is_reproducible() -> None:
    event = _events()[0]

    first = event.to_canonical_json()
    second = event.to_canonical_json()

    assert first == second
    parsed = json.loads(first)
    assert parsed["role"] == event.role
    assert parsed["amount_ilc_str"] == event.amount_ilc_str


def test_phase_1534p_cdl_authority_and_schema_version_are_bound() -> None:
    assert CDL_AUTHORITY_TOKENS == [
        "cdl_025_terminal_issuance_model_ratified_phase_267.v0.1",
        "cdl_027_decay_formulation_ratified_phase_276.v0.1",
        "cdl_028_fee_burn_split_ratified_phase_274.v0.1",
        "cdl_029_allocation_split_ratified_phase_272.v0.1",
    ]
    for event in _events():
        assert event.schema_version == CANONICAL_ECONOMIC_EVENT_RECORD_SCHEMA_VERSION
        assert event.cdl_authority
        assert all("ratified_phase" in token for token in event.cdl_authority)
