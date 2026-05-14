from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch import (
    BOUNTY_CAP_0_15_B_E_RUNTIME_TOKEN,
    BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET,
    BURN_FLOOR_0_05_RUNTIME_TOKEN,
    BURN_FLOOR_FRACTION,
    CDL_047_DEPENDENCY,
    CDL_047_TREASURY_GOVERNANCE_RUNTIME_TOKEN,
    NO_DIRECT_TREASURY_STUB_FOUND_TOKEN,
    PHASE_1347_ALLOCATION_RUNTIME_DEPENDENCY,
    PRODUCTION_TREASURY_ACTIVATION_TOKEN,
    PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN,
    TREASURY_GOVERNANCE_RUNTIME_VERSION,
    VELOCITY_ALERT_FLOOR,
    VELOCITY_ALERT_FLOOR_0_91_RUNTIME_TOKEN,
    VELOCITY_ALERT_TRIGGER_RUNTIME_TOKEN,
    build_treasury_governance_quote,
    require_cdl_047_treasury_fractions,
    require_production_treasury_activation,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/epoch/treasury_governance_runtime.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1348_g8_cdl_047_treasury_governance_runtime.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
WALKTHROUGH = ROOT / "docs/phases/phase_1348_cdl_047_treasury_governance_runtime_walkthrough.md"
CDL_047_EVIDENCE = (
    ROOT / "docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md"
)
SIM_008_EVIDENCE = ROOT / "docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md"
SIM_009_EVIDENCE = ROOT / "docs/specs/ilc_sim_009_pe_stabilization_commissioning_429_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1348_constants_bind_cdl_047_and_default_off_state() -> None:
    assert TREASURY_GOVERNANCE_RUNTIME_VERSION == "treasury_governance_runtime_1348.v0.1"
    assert CDL_047_DEPENDENCY == "cdl_047_treasury_governance_ratified_phase_418.v0.1"
    assert PHASE_1347_ALLOCATION_RUNTIME_DEPENDENCY == "allocation_distributor_runtime_1347.v0.1"
    assert CDL_047_TREASURY_GOVERNANCE_RUNTIME_TOKEN == (
        "cdl_047_treasury_governance_runtime_phase_1348.v0.1"
    )
    assert BOUNTY_CAP_0_15_B_E_RUNTIME_TOKEN == "bounty_cap_0_15_b_e_runtime_phase_1348"
    assert BURN_FLOOR_0_05_RUNTIME_TOKEN == "burn_floor_0_05_runtime_phase_1348"
    assert VELOCITY_ALERT_TRIGGER_RUNTIME_TOKEN == "velocity_alert_trigger_runtime_phase_1348"
    assert VELOCITY_ALERT_FLOOR_0_91_RUNTIME_TOKEN == (
        "velocity_alert_floor_0_91_runtime_phase_1348"
    )
    assert PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN == "treasury_not_activated_phase_1348"
    assert PRODUCTION_TREASURY_ACTIVATION_TOKEN == (
        "phase_1366_soft_rc_eligible_true_value_path_activation_required"
    )
    assert NO_DIRECT_TREASURY_STUB_FOUND_TOKEN == "no_direct_treasury_stub_found_phase_1348"
    assert BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET == Decimal("0.15")
    assert BURN_FLOOR_FRACTION == Decimal("0.05")
    assert VELOCITY_ALERT_FLOOR == Decimal("0.91")


def test_treasury_governance_quote_enforces_cap_floor_and_velocity_alert() -> None:
    quote = build_treasury_governance_quote(
        issuance_epoch=12,
        epoch_budget_ilc="100",
        requested_bounty_ilc="12",
        planned_burn_ilc="5",
        observed_velocity="0.90",
    )

    assert quote.issuance_epoch == 12
    assert quote.epoch_budget_ilc == Decimal("100.000000000")
    assert quote.bounty_cap_fraction_of_epoch_budget == Decimal("0.15")
    assert quote.bounty_cap_ilc == Decimal("15.000000000")
    assert quote.requested_bounty_ilc == Decimal("12.000000000")
    assert quote.burn_floor_fraction == Decimal("0.05")
    assert quote.burn_floor_ilc == Decimal("5.000000000")
    assert quote.planned_burn_ilc == Decimal("5.000000000")
    assert quote.velocity_alert_floor == Decimal("0.91")
    assert quote.observed_velocity == Decimal("0.90")
    assert quote.velocity_alert_triggered is True
    assert quote.treasury_remaining_budget_ilc == Decimal("83.000000000")
    assert quote.production_treasury_activated is False
    assert quote.decision_token == PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN


def test_velocity_alert_floor_is_monitoring_boundary_not_automatic_action() -> None:
    at_floor = build_treasury_governance_quote(1, "100", "10", "5", "0.91")
    above_floor = build_treasury_governance_quote(1, "100", "10", "5", "0.92")

    assert at_floor.velocity_alert_triggered is False
    assert above_floor.velocity_alert_triggered is False
    assert at_floor.production_treasury_activated is False
    assert above_floor.production_treasury_activated is False


def test_treasury_governance_quote_quantizes_down() -> None:
    quote = build_treasury_governance_quote(
        issuance_epoch=0,
        epoch_budget_ilc="1.2345678999",
        requested_bounty_ilc="0.1851851849",
        planned_burn_ilc="0.0617283949",
        observed_velocity="0.50",
    )

    assert quote.epoch_budget_ilc == Decimal("1.234567899")
    assert quote.bounty_cap_ilc == Decimal("0.185185184")
    assert quote.burn_floor_ilc == Decimal("0.061728394")
    assert quote.requested_bounty_ilc == Decimal("0.185185184")
    assert quote.planned_burn_ilc == Decimal("0.061728394")
    assert quote.treasury_remaining_budget_ilc == Decimal("0.987654321")


def test_treasury_fraction_guards_enforce_exact_cdl_047_values() -> None:
    assert require_cdl_047_treasury_fractions() == (
        Decimal("0.15"),
        Decimal("0.05"),
        Decimal("0.91"),
    )
    with pytest.raises(ValueError, match="bounty_cap_fraction_must_equal_cdl_047_0_15"):
        require_cdl_047_treasury_fractions("0.14", "0.05", "0.91")
    with pytest.raises(ValueError, match="burn_floor_fraction_must_equal_cdl_047_0_05"):
        require_cdl_047_treasury_fractions("0.15", "0.04", "0.91")
    with pytest.raises(ValueError, match="velocity_alert_floor_must_equal_cdl_047_0_91"):
        require_cdl_047_treasury_fractions("0.15", "0.05", "0.90")


def test_cap_floor_budget_and_exact_numeric_guards() -> None:
    with pytest.raises(ValueError, match="requested_bounty_exceeds_cdl_047_cap"):
        build_treasury_governance_quote(0, "100", "15.000000001", "5", "0.90")
    with pytest.raises(ValueError, match="planned_burn_below_cdl_047_floor"):
        build_treasury_governance_quote(0, "100", "10", "4.999999999", "0.90")
    with pytest.raises(ValueError, match="treasury_request_exceeds_epoch_budget"):
        build_treasury_governance_quote(0, "100", "15", "90", "0.90")
    with pytest.raises(ValueError, match="treasury_issuance_epoch_must_be_non_negative_int"):
        build_treasury_governance_quote(True, "100", "10", "5", "0.90")
    with pytest.raises(ValueError, match="treasury_issuance_epoch_must_be_non_negative_int"):
        build_treasury_governance_quote(-1, "100", "10", "5", "0.90")
    with pytest.raises(ValueError, match="epoch_budget_ilc_must_be_exact_decimal"):
        build_treasury_governance_quote(0, 0.1, "10", "5", "0.90")
    with pytest.raises(ValueError, match="epoch_budget_ilc_must_be_finite"):
        build_treasury_governance_quote(0, Decimal("NaN"), "10", "5", "0.90")
    with pytest.raises(ValueError, match="requested_bounty_ilc_must_be_non_negative"):
        build_treasury_governance_quote(0, "100", "-1", "5", "0.90")
    with pytest.raises(ValueError, match="observed_velocity_must_be_unit_interval"):
        build_treasury_governance_quote(0, "100", "10", "5", "1.01")
    with pytest.raises(ValueError, match="observed_velocity_must_be_exact_decimal"):
        build_treasury_governance_quote(0, "100", "10", "5", 0.90)


def test_production_treasury_guard_remains_closed() -> None:
    with pytest.raises(ValueError, match=PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN):
        require_production_treasury_activation(None)
    with pytest.raises(ValueError, match="production_treasury_activation_not_implemented_phase_1348"):
        require_production_treasury_activation(PRODUCTION_TREASURY_ACTIVATION_TOKEN)


def test_canonical_record_uses_strings_for_decimal_amounts() -> None:
    record = build_treasury_governance_quote(5, "100", "12", "5", "0.90").to_canonical_record()

    assert record["runtime_version"] == TREASURY_GOVERNANCE_RUNTIME_VERSION
    assert record["bounty_cap_fraction_of_epoch_budget"] == "0.15"
    assert record["bounty_cap_ilc"] == "15"
    assert record["burn_floor_fraction"] == "0.05"
    assert record["burn_floor_ilc"] == "5"
    assert record["velocity_alert_floor"] == "0.91"
    assert record["observed_velocity"] == "0.9"
    assert record["velocity_alert_triggered"] is True
    assert record["production_treasury_activated"] is False
    assert record["decision_token"] == PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN


def test_evidence_prompt_frontier_and_walkthrough_record_tokens() -> None:
    evidence = _read(CDL_047_EVIDENCE)
    sim_008 = _read(SIM_008_EVIDENCE)
    sim_009 = _read(SIM_009_EVIDENCE)
    prompt = _read(PROMPT)
    status = _read(STATUS)
    index = _read(INDEX)
    forward_plan = _read(FORWARD_PLAN)
    walkthrough = _read(WALKTHROUGH)
    runtime = _read(RUNTIME)

    assert "per-epoch bounty issuance cap of 0.15 × B_e" in evidence
    assert "late-economy fee-burn floor of 0.05" in evidence
    assert "ILC velocity monitoring alert floor of 0.91" in evidence
    assert "velocity alert floor candidate of 0.91" in sim_008
    assert "SIM-009 does not open, amend, or ratify any CDL row" in sim_009
    assert 'BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET = Decimal("0.15")' in runtime
    assert 'BURN_FLOOR_FRACTION = Decimal("0.05")' in runtime
    assert 'VELOCITY_ALERT_FLOOR = Decimal("0.91")' in runtime
    for token in (
        "cdl_047_treasury_governance_runtime_phase_1348.v0.1",
        "bounty_cap_0_15_b_e_runtime_phase_1348",
        "burn_floor_0_05_runtime_phase_1348",
        "velocity_alert_trigger_runtime_phase_1348",
        "velocity_alert_floor_0_91_runtime_phase_1348",
        "treasury_not_activated_phase_1348",
        "phase_1366_soft_rc_eligible_true_value_path_activation_required",
        "no_direct_treasury_stub_found_phase_1348",
    ):
        assert token in prompt
        assert token in status
        assert token in index
        assert token in forward_plan
        assert token in walkthrough
