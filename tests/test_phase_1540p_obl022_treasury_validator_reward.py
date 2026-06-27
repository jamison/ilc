"""Phase 1540p OBL-022 treasury + validator reward production-path tests."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from decimal import Decimal

import pytest

import ilc_core.epoch.treasury_validator_reward_production_path as path
from ilc_core.epoch.issuance_economics_integration_gate import (
    build_issuance_economics_integration_gate_report,
)
from ilc_core.epoch.treasury_validator_reward_production_path import (
    CANONICAL_TREASURY_DISTRIBUTION_EVENT_SCHEMA_VERSION,
    CDL_047_DEPENDENCY,
    CDL_054_DEPENDENCY,
    SETTLEMENT_ROOT_SCHEMA_VERSION,
    TREASURY_DISTRIBUTION_NOT_ACTIVATED,
    TREASURY_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    TREASURY_VALIDATOR_REWARD_PRODUCTION_PATH_VERSION,
    TreasuryDistributionSettlementRoot,
    TreasuryValidatorRewardProductionResult,
    build_canonical_treasury_validator_reward_event_payloads,
    build_treasury_validator_reward_result,
    compute_treasury_distribution_settlement_root,
    emit_canonical_treasury_distribution_events,
    require_treasury_distribution_production_activation,
)


def _inputs(epoch: int = 3, requested_bounty: Decimal = Decimal("1000")) -> dict[str, object]:
    return {
        "issuance_epoch": epoch,
        "epoch_budget_ilc": Decimal("356202.705201831"),
        "requested_bounty_ilc": requested_bounty,
        "planned_burn_ilc": Decimal("20000"),
        "treasury_planned_burn_ilc": Decimal("20000"),
        "observed_velocity": Decimal("0.95"),
        "write_fee_burn_pool_ilc": Decimal("50000"),
        "cumulative_issued_before_epoch_ilc": Decimal("1000"),
    }


def _result() -> TreasuryValidatorRewardProductionResult:
    return build_treasury_validator_reward_result(_inputs())


def test_phase_1540p_guard_and_activation_boundary() -> None:
    assert TREASURY_DISTRIBUTION_NOT_ACTIVATED is True
    assert TREASURY_DISTRIBUTION_NOT_ACTIVATED_TOKEN == (
        "production_treasury_distribution_not_activated_phase_1540p"
    )

    with pytest.raises(
        NotImplementedError,
        match="production_treasury_distribution_not_activated_phase_1540p",
    ):
        require_treasury_distribution_production_activation()


def test_phase_1540p_builds_guarded_result_with_dependency_tokens() -> None:
    result = _result()

    assert result.runtime_version == TREASURY_VALIDATOR_REWARD_PRODUCTION_PATH_VERSION
    assert result.cdl_047_dependency == CDL_047_DEPENDENCY
    assert result.cdl_054_dependency == CDL_054_DEPENDENCY
    assert result.production_treasury_distribution_activated is False
    assert result.guard_token == TREASURY_DISTRIBUTION_NOT_ACTIVATED_TOKEN
    assert result.integration_gate_result == "issuance_economics_integration_gate_pass"
    assert result.treasury_quote.requested_bounty_ilc == Decimal("1000")
    assert result.reward_routing_quote.validator_reward_pool_ilc == Decimal("1000")


def test_phase_1540p_integration_gate_fail_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    real_report = build_issuance_economics_integration_gate_report()
    failed_report = replace(
        real_report,
        verdict="forced_gate_fail_for_phase_1540p_test",
        blocking_reason="test_only",
    )
    monkeypatch.setattr(
        path,
        "verify_issuance_economics_integration_gate",
        lambda: (_ for _ in ()).throw(ValueError(failed_report.verdict)),
    )

    with pytest.raises(ValueError, match="forced_gate_fail_for_phase_1540p_test"):
        build_treasury_validator_reward_result(_inputs())


def test_phase_1540p_same_result_replays_same_root() -> None:
    first = compute_treasury_distribution_settlement_root(_result())
    second = compute_treasury_distribution_settlement_root(_result())

    assert isinstance(first, TreasuryDistributionSettlementRoot)
    assert first.root_hex == second.root_hex
    assert first.canonical_record_json == second.canonical_record_json


def test_phase_1540p_digest_matches_canonical_record_json() -> None:
    root = compute_treasury_distribution_settlement_root(_result())

    digest = hashlib.sha256(root.canonical_record_json.encode("utf-8")).hexdigest()
    assert digest == root.root_hex
    assert len(root.root_hex) == 64


def test_phase_1540p_root_changes_when_amount_changes() -> None:
    first = compute_treasury_distribution_settlement_root(_result())
    changed = build_treasury_validator_reward_result(_inputs(requested_bounty=Decimal("900")))
    second = compute_treasury_distribution_settlement_root(changed)

    assert first.root_hex != second.root_hex


def test_phase_1540p_root_payload_excludes_settlement_root_hex() -> None:
    root = compute_treasury_distribution_settlement_root(_result())
    payload = json.loads(root.canonical_record_json)

    assert payload["schema_version"] == SETTLEMENT_ROOT_SCHEMA_VERSION
    assert "settlement_root_hex" not in payload
    assert "settlement_root_hex" not in root.canonical_record_json


def test_phase_1540p_emits_canonical_events_with_decimal_amounts() -> None:
    result = _result()
    root = compute_treasury_distribution_settlement_root(result)
    events = emit_canonical_treasury_distribution_events(result, root)

    assert [event.amount_role for event in events] == [
        "treasury_bounty_cap",
        "treasury_planned_burn",
        "treasury_remaining_budget",
        "validator_reward_pool",
    ]
    assert {event.settlement_root_hex for event in events} == {root.root_hex}
    assert all(event.production_treasury_distribution_activated is False for event in events)
    assert all(
        event.schema_version == CANONICAL_TREASURY_DISTRIBUTION_EVENT_SCHEMA_VERSION
        for event in events
    )
    assert [Decimal(event.amount_ilc_str) for event in events]


def test_phase_1540p_root_commits_to_event_payload_batch() -> None:
    result = _result()
    root = compute_treasury_distribution_settlement_root(result)
    events = emit_canonical_treasury_distribution_events(result, root)
    root_payload = json.loads(root.canonical_record_json)
    event_payloads_without_root = [
        {
            key: value
            for key, value in event.to_canonical_record().items()
            if key != "settlement_root_hex"
        }
        for event in events
    ]

    assert root_payload["event_payloads"] == event_payloads_without_root
    assert event_payloads_without_root == build_canonical_treasury_validator_reward_event_payloads(
        result
    )


def test_phase_1540p_rejects_stale_settlement_root_for_result() -> None:
    result = _result()
    stale_result = build_treasury_validator_reward_result(
        _inputs(requested_bounty=Decimal("900"))
    )
    stale_root = compute_treasury_distribution_settlement_root(stale_result)

    with pytest.raises(ValueError, match="settlement_root_event_payload_mismatch"):
        emit_canonical_treasury_distribution_events(result, stale_root)


def test_phase_1540p_rejects_float_before_root() -> None:
    result = _result()
    bad_treasury_quote = replace(result.treasury_quote, bounty_cap_ilc=1.0)
    bad_result = replace(result, treasury_quote=bad_treasury_quote)

    with pytest.raises(ValueError, match="float_in_treasury_distribution_record_rejected"):
        compute_treasury_distribution_settlement_root(bad_result)
