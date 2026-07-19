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
    build_canonical_economic_event_payloads,
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
        "scheduled_emission_pool",
        "performer_pool",
        "auditor_pool",
        "genesis_overhead_pool",
        "genesis_burn_pool",
    ]


def test_phase_1534p_events_reflect_cleared_emission_guard_without_writes() -> None:
    # Guard cleared by Phase 1575g.
    assert PRODUCTION_EMISSION_NOT_ACTIVATED is False
    for event in _events():
        assert event.production_emission_activated is True


def test_phase_1534p_amounts_parse_without_precision_loss() -> None:
    result, root = _result_and_root()
    events = emit_canonical_economic_event_records(result, root)
    by_role = {event.role: Decimal(event.amount_ilc_str) for event in events}

    assert by_role["scheduled_emission_pool"] == result.emission_quote.capped_epoch_budget_ilc
    assert by_role["performer_pool"] == result.allocation_quote.performer_reward_pool_ilc
    assert by_role["auditor_pool"] == result.allocation_quote.auditor_reward_pool_ilc
    assert (
        by_role["genesis_overhead_pool"]
        == result.allocation_quote.genesis_overhead_pool_ilc
    )
    assert by_role["genesis_burn_pool"] == result.fee_burn_quote.genesis_burn_pool_ilc


def test_phase_1537p_fix1_events_are_additively_conservative_with_residual() -> None:
    result = compute_epoch_emission_production_path(
        9,
        Decimal("1000.000000001"),
        Decimal("250.000000009"),
    )
    root = compute_settlement_root(result)
    events = emit_canonical_economic_event_records(result, root)

    event_sum = sum((Decimal(event.amount_ilc_str) for event in events), Decimal("0"))
    assert event_sum == (
        result.emission_quote.capped_epoch_budget_ilc
        + result.fee_burn_quote.total_epoch_fees_ilc
    )
    assert "rounding_residual" not in {event.role for event in events}


def test_phase_1534p_rejects_float_pool_amount() -> None:
    result, root = _result_and_root()
    bad_allocation = replace(result.allocation_quote, performer_reward_pool_ilc=1.0)
    bad_result = replace(result, allocation_quote=bad_allocation)

    with pytest.raises(ValueError, match="float_in_canonical_economic_event_rejected"):
        emit_canonical_economic_event_records(bad_result, root)


def test_phase_1537p_fix1_event_payload_helper_validates_result_boundary() -> None:
    result, _root = _result_and_root()

    with pytest.raises(ValueError, match="issuance_epoch_must_be_non_negative_int"):
        build_canonical_economic_event_payloads(replace(result, issuance_epoch=True))
    with pytest.raises(
        ValueError,
        match="canonical_economic_event_activation_flag_invalid",
    ):
        build_canonical_economic_event_payloads(
            replace(result, production_emission_activated="false")
        )


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


def test_phase_1537p_fix1_settlement_root_commits_to_event_batch() -> None:
    result, root = _result_and_root()
    events = emit_canonical_economic_event_records(result, root)
    root_payload = json.loads(root.canonical_record_json)
    event_payloads_without_root = [
        {
            key: value
            for key, value in event.to_canonical_record().items()
            if key != "settlement_root_hex"
        }
        for event in events
    ]

    assert root_payload["economic_event_payloads"] == event_payloads_without_root


def test_phase_1537p_fix1_rejects_stale_settlement_root_for_result() -> None:
    result = compute_epoch_emission_production_path(
        9,
        Decimal("1000.000000001"),
        Decimal("250.000000009"),
    )
    stale_result = compute_epoch_emission_production_path(
        9,
        Decimal("1000.000000001"),
        Decimal("250.000000008"),
    )
    stale_root = compute_settlement_root(stale_result)

    with pytest.raises(ValueError, match="settlement_root_event_payload_mismatch"):
        emit_canonical_economic_event_records(result, stale_root)


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
        "cdl_026_cmax_lock_ratified_phase_273.v0.1",
        "cdl_027_decay_formulation_ratified_phase_276.v0.1",
        "cdl_028_fee_burn_split_ratified_phase_274.v0.1",
        "cdl_029_allocation_split_ratified_phase_272.v0.1",
    ]
    for event in _events():
        assert event.schema_version == CANONICAL_ECONOMIC_EVENT_RECORD_SCHEMA_VERSION
        assert event.cdl_authority
        assert all("ratified_phase" in token for token in event.cdl_authority)
