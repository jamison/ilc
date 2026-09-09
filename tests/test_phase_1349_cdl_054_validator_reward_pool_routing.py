from __future__ import annotations

import inspect
from decimal import Decimal, ROUND_DOWN
from pathlib import Path

import pytest

from ilc_core.epoch import (
    BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET,
    BURN_FLOOR_FRACTION,
    C_MAX_ILC,
    CDL_047_TREASURY_DEPENDENCY_TOKEN,
    CDL_054_DEPENDENCY,
    CDL_054_VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_TOKEN,
    EXPECTED_CDL_047_TREASURY_RUNTIME_TOKEN,
    NO_DIRECT_VALIDATOR_REWARD_STUB_FOUND_TOKEN,
    PRODUCTION_VALIDATOR_REWARD_DISTRIBUTION_ACTIVATION_TOKEN,
    TREASURY_EPOCH_BUDGET_BINDING_VERIFIED_TOKEN,
    TREASURY_EPOCH_BUDGET_SOURCE_LABEL,
    VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN,
    VALIDATOR_REWARD_POOL_EXCEEDS_CDL047_CAP_TOKEN,
    VALIDATOR_REWARD_POOL_LABEL,
    VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_VERSION,
    VELOCITY_ALERT_FLOOR,
    WRITE_FEE_BURN_POOL_LABEL,
    build_validator_reward_pool_routing_quote,
    require_cdl_047_treasury_dependency,
    require_cdl_054_validator_reward_fraction,
    require_production_validator_reward_distribution_activation,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/epoch/validator_reward_pool_routing_runtime.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1349_g8_cdl_054_validator_reward_pool_routing.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
WALKTHROUGH = ROOT / "docs/phases/phase_1349_cdl_054_validator_reward_pool_routing_walkthrough.md"
CDL_054_EVIDENCE = (
    ROOT
    / "docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md"
)
CDL_054_PRELOCK = (
    ROOT
    / "docs/specs/ilc_cdl_054_validator_economic_incentive_framework_prelock_hardening_490_v0.1.md"
)
SIM_010_SYNTHESIS = (
    ROOT / "docs/specs/ilc_sim_010_validator_incentive_economics_synthesis_487_v0.1.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cumulative_for_remaining_budget(budget: str) -> str:
    quantized_budget = Decimal(budget).quantize(Decimal("0.000000001"), rounding=ROUND_DOWN)
    return format(C_MAX_ILC - quantized_budget, "f")


def test_phase_1349_constants_bind_cdl_054_cdl_047_and_default_off_state() -> None:
    assert (
        VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_VERSION
        == "validator_reward_pool_routing_runtime_1367.v0.2"
    )
    assert CDL_054_DEPENDENCY == (
        "cdl_054_validator_economic_incentive_framework_ratified_phase_491.v0.1"
    )
    assert CDL_054_VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_TOKEN == (
        "cdl_054_validator_reward_pool_routing_runtime_phase_1349.v0.1"
    )
    assert CDL_047_TREASURY_DEPENDENCY_TOKEN == "cdl_047_treasury_dependency_phase_1349"
    assert EXPECTED_CDL_047_TREASURY_RUNTIME_TOKEN == (
        "cdl_047_treasury_governance_runtime_phase_1348.v0.1"
    )
    assert VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN == (
        "validator_reward_distribution_not_activated_phase_1349"
    )
    assert PRODUCTION_VALIDATOR_REWARD_DISTRIBUTION_ACTIVATION_TOKEN == (
        "phase_1366_soft_rc_eligible_true_value_path_activation_required"
    )
    assert NO_DIRECT_VALIDATOR_REWARD_STUB_FOUND_TOKEN == (
        "no_direct_validator_reward_stub_found_phase_1349"
    )
    assert VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN == Decimal("0.02")
    assert VALIDATOR_REWARD_POOL_LABEL == "validator_reward_pool"
    assert WRITE_FEE_BURN_POOL_LABEL == "write_fee_burn_pool"
    assert TREASURY_EPOCH_BUDGET_BINDING_VERIFIED_TOKEN == (
        "phase_1366_treasury_epoch_budget_binding_verified"
    )
    assert TREASURY_EPOCH_BUDGET_SOURCE_LABEL == "phase_1345_capped_epoch_emission_budget_ilc"
    assert BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET == Decimal("0.15")
    assert BURN_FLOOR_FRACTION == Decimal("0.05")
    assert VELOCITY_ALERT_FLOOR == Decimal("0.91")


def test_validator_reward_pool_quote_routes_through_cdl_047_treasury_framework() -> None:
    quote = build_validator_reward_pool_routing_quote(
        issuance_epoch=13,
        write_fee_burn_pool_ilc="100",
        cumulative_issued_before_epoch_ilc=_cumulative_for_remaining_budget("100"),
        treasury_planned_burn_ilc="5",
        observed_velocity="0.90",
    )

    assert quote.issuance_epoch == 13
    assert quote.write_fee_burn_pool_ilc == Decimal("100.000000000")
    assert quote.validator_reward_fraction_of_write_fee_burn == Decimal("0.02")
    assert quote.validator_reward_pool_ilc == Decimal("2.000000000")
    assert quote.validator_reward_pool_label == VALIDATOR_REWARD_POOL_LABEL
    assert quote.write_fee_burn_pool_label == WRITE_FEE_BURN_POOL_LABEL
    assert quote.cumulative_issued_before_epoch_ilc == Decimal("25919900.000000000")
    assert quote.treasury_epoch_budget_binding_token == TREASURY_EPOCH_BUDGET_BINDING_VERIFIED_TOKEN
    assert quote.treasury_epoch_budget_source_label == TREASURY_EPOCH_BUDGET_SOURCE_LABEL
    assert quote.treasury_epoch_budget_ilc == Decimal("100.000000000")
    assert quote.treasury_bounty_cap_fraction == Decimal("0.15")
    assert quote.treasury_bounty_cap_ilc == Decimal("15.000000000")
    assert quote.treasury_burn_floor_fraction == Decimal("0.05")
    assert quote.treasury_burn_floor_ilc == Decimal("5.000000000")
    assert quote.treasury_planned_burn_ilc == Decimal("5.000000000")
    assert quote.treasury_velocity_alert_floor == Decimal("0.91")
    assert quote.observed_velocity == Decimal("0.90")
    assert quote.treasury_velocity_alert_triggered is True
    assert quote.treasury_remaining_budget_ilc == Decimal("93.000000000")
    assert quote.production_validator_reward_distribution_activated is False
    assert quote.decision_token == VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN


def test_validator_reward_pool_quote_quantizes_down() -> None:
    quote = build_validator_reward_pool_routing_quote(
        issuance_epoch=0,
        write_fee_burn_pool_ilc="1.2345678999",
        cumulative_issued_before_epoch_ilc=_cumulative_for_remaining_budget("1.2345678999"),
        treasury_planned_burn_ilc="0.0617283949",
        observed_velocity="0.50",
    )

    assert quote.write_fee_burn_pool_ilc == Decimal("1.234567899")
    assert quote.validator_reward_pool_ilc == Decimal("0.024691357")
    assert quote.treasury_epoch_budget_ilc == Decimal("1.234567899")
    assert quote.treasury_bounty_cap_ilc == Decimal("0.185185184")
    assert quote.treasury_burn_floor_ilc == Decimal("0.061728394")
    assert quote.treasury_planned_burn_ilc == Decimal("0.061728394")
    assert quote.treasury_remaining_budget_ilc == Decimal("1.148148148")


def test_validator_reward_fraction_guard_enforces_sim_010_value() -> None:
    assert require_cdl_054_validator_reward_fraction() == Decimal("0.02")
    assert require_cdl_054_validator_reward_fraction("0.02") == Decimal("0.02")
    with pytest.raises(
        ValueError,
        match="validator_reward_fraction_must_equal_cdl_054_sim_010_0_02",
    ):
        require_cdl_054_validator_reward_fraction("0.01")
    with pytest.raises(ValueError, match="validator_reward_fraction_must_be_unit_interval"):
        require_cdl_054_validator_reward_fraction("1.01")
    with pytest.raises(ValueError, match="validator_reward_fraction_must_be_exact_decimal"):
        require_cdl_054_validator_reward_fraction(0.02)


def test_dependency_and_guard_failures_remain_default_off() -> None:
    require_cdl_047_treasury_dependency()

    with pytest.raises(ValueError, match=VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN):
        require_production_validator_reward_distribution_activation(None)
    with pytest.raises(
        ValueError,
        match="production_validator_reward_distribution_activation_not_implemented_phase_1349",
    ):
        require_production_validator_reward_distribution_activation(
            PRODUCTION_VALIDATOR_REWARD_DISTRIBUTION_ACTIVATION_TOKEN
        )


def test_treasury_framework_rejects_reward_request_above_cdl_047_cap() -> None:
    with pytest.raises(ValueError, match=VALIDATOR_REWARD_POOL_EXCEEDS_CDL047_CAP_TOKEN):
        build_validator_reward_pool_routing_quote(
            issuance_epoch=0,
            write_fee_burn_pool_ilc="1000",
            cumulative_issued_before_epoch_ilc=_cumulative_for_remaining_budget("100"),
            treasury_planned_burn_ilc="5",
            observed_velocity="0.90",
        )


def test_exact_numeric_guards_reject_float_bool_nonfinite_and_negative_values() -> None:
    with pytest.raises(
        ValueError,
        match="validator_reward_issuance_epoch_must_be_non_negative_int",
    ):
        build_validator_reward_pool_routing_quote(True, "100", "25919900", "5", "0.90")
    with pytest.raises(
        ValueError,
        match="validator_reward_issuance_epoch_must_be_non_negative_int",
    ):
        build_validator_reward_pool_routing_quote(-1, "100", "25919900", "5", "0.90")
    with pytest.raises(ValueError, match="write_fee_burn_pool_ilc_must_be_exact_decimal"):
        build_validator_reward_pool_routing_quote(0, 0.1, "25919900", "5", "0.90")
    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        build_validator_reward_pool_routing_quote(0, Decimal("NaN"), "25919900", "5", "0.90")
    with pytest.raises(ValueError, match="write_fee_burn_pool_ilc_must_be_non_negative"):
        build_validator_reward_pool_routing_quote(0, "-1", "25919900", "5", "0.90")
    with pytest.raises(ValueError, match="cumulative_issued_before_epoch_ilc_must_be_exact_decimal"):
        build_validator_reward_pool_routing_quote(0, "100", 0.1, "5", "0.90")
    with pytest.raises(ValueError, match="cumulative_issued_before_epoch_ilc_must_be_finite"):
        build_validator_reward_pool_routing_quote(0, "100", Decimal("Infinity"), "5", "0.90")
    with pytest.raises(ValueError, match="cumulative_issued_before_epoch_ilc_must_be_non_negative"):
        build_validator_reward_pool_routing_quote(0, "100", "-1", "5", "0.90")
    with pytest.raises(ValueError, match="observed_velocity_must_be_exact_decimal"):
        build_validator_reward_pool_routing_quote(0, "100", "25919900", "5", 0.90)


def test_phase_1367_treasury_budget_binding_removes_caller_supplied_budget_input() -> None:
    signature = inspect.signature(build_validator_reward_pool_routing_quote)

    assert "treasury_epoch_budget_ilc" not in signature.parameters
    assert "cumulative_issued_before_epoch_ilc" in signature.parameters

    quote = build_validator_reward_pool_routing_quote(
        issuance_epoch=0,
        write_fee_burn_pool_ilc="100",
        cumulative_issued_before_epoch_ilc="0",
        treasury_planned_burn_ilc="18598.657313599",
        observed_velocity="0.95",
    )

    assert quote.treasury_epoch_budget_ilc == Decimal("371609.891246338")
    assert quote.treasury_epoch_budget_binding_token == (
        "phase_1366_treasury_epoch_budget_binding_verified"
    )


def test_canonical_record_uses_strings_for_decimal_amounts() -> None:
    record = build_validator_reward_pool_routing_quote(
        issuance_epoch=5,
        write_fee_burn_pool_ilc="100",
        cumulative_issued_before_epoch_ilc=_cumulative_for_remaining_budget("100"),
        treasury_planned_burn_ilc="5",
        observed_velocity="0.90",
    ).to_canonical_record()

    assert record["runtime_version"] == VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_VERSION
    assert record["cdl_054_dependency"] == CDL_054_DEPENDENCY
    assert record["cdl_047_treasury_dependency_token"] == CDL_047_TREASURY_DEPENDENCY_TOKEN
    assert record["cdl_047_treasury_runtime_token"] == (
        "cdl_047_treasury_governance_runtime_phase_1348.v0.1"
    )
    assert record["write_fee_burn_pool_ilc"] == "100"
    assert record["cumulative_issued_before_epoch_ilc"] == "25919900"
    assert record["validator_reward_fraction_of_write_fee_burn"] == "0.02"
    assert record["validator_reward_pool_ilc"] == "2"
    assert record["treasury_epoch_budget_binding_token"] == (
        "phase_1366_treasury_epoch_budget_binding_verified"
    )
    assert record["treasury_epoch_budget_source_label"] == (
        "phase_1345_capped_epoch_emission_budget_ilc"
    )
    assert record["treasury_bounty_cap_ilc"] == "15"
    assert record["treasury_burn_floor_ilc"] == "5"
    assert record["treasury_remaining_budget_ilc"] == "93"
    assert record["production_validator_reward_distribution_activated"] is False
    assert record["decision_token"] == VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN


def test_evidence_prompt_frontier_and_walkthrough_record_tokens() -> None:
    evidence = _read(CDL_054_EVIDENCE)
    prelock = _read(CDL_054_PRELOCK)
    sim_010 = _read(SIM_010_SYNTHESIS)
    prompt = _read(PROMPT)
    status = _read(STATUS)
    index = _read(INDEX)
    forward_plan = _read(FORWARD_PLAN)
    walkthrough = _read(WALKTHROUGH)
    runtime = _read(RUNTIME)

    assert "CDL-054 is ratified in Phase 491" in evidence
    assert "CDL-054 governs reward-pool routing through the existing CDL-047 treasury framework only" in prelock
    assert "recommended_validator_reward_fraction: 0.02" in sim_010
    assert 'VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN = Decimal("0.02")' in runtime
    for token in (
        "cdl_054_validator_reward_pool_routing_runtime_phase_1349.v0.1",
        "cdl_047_treasury_dependency_phase_1349",
        "validator_reward_distribution_not_activated_phase_1349",
        "no_direct_validator_reward_stub_found_phase_1349",
        "phase_1366_soft_rc_eligible_true_value_path_activation_required",
    ):
        assert token in prompt
        assert token in status
        assert token in index
        assert token in forward_plan
        assert token in walkthrough
