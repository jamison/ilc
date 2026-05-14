from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch import (
    CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN,
    CDL_030_DEPENDENCY,
    CDL_030_ECU_PRICE_CLAMP_RUNTIME_TOKEN,
    ECU_PRICE_CLAMP_RUNTIME_VERSION,
    EXPECTED_CDL_027_HALVING_INTERVAL_ISSUANCE_EPOCHS,
    EXPECTED_CDL_027_ISSUANCE_EPOCH_DURATION,
    EXPECTED_CDL_027_RUNTIME_TOKEN,
    HALVING_INTERVAL_ISSUANCE_EPOCHS,
    ISSUANCE_EPOCH_DURATION,
    LIVE_PRICE_ADJUSTMENT_NOT_ACTIVATED_TOKEN,
    NO_DIRECT_PRICE_CLAMP_STUB_FOUND_TOKEN,
    P_MAX,
    P_MIN,
    PRICE_CLAMP_WIDTH,
    PRODUCTION_ECU_PRICE_CLAMP_ACTIVATION_TOKEN,
    P_MIN_P_MAX_BOUNDS_CDL_027_DERIVED_TOKEN,
    build_ecu_price_clamp_quote,
    derive_cdl_030_price_bounds_from_cdl_027_schedule,
    require_cdl_027_schedule_dependency,
    require_cdl_030_price_bounds,
    require_live_price_adjustment_activation,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/epoch/ecu_price_clamp_runtime.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1351_g8_cdl_030_ecu_price_clamp_runtime.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
WALKTHROUGH = ROOT / "docs/phases/phase_1351_cdl_030_ecu_price_clamp_runtime_walkthrough.md"
CDL_030_EVIDENCE = (
    ROOT / "docs/specs/ilc_cdl_030_ecu_price_clamp_ratification_evidence_277_v0.1.md"
)
CDL_030_PRELOCK = (
    ROOT / "docs/specs/ilc_cdl_030_ecu_price_clamp_candidate_lock_277_pre1_v0.1.md"
)
CDL_027_EVIDENCE = (
    ROOT / "docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md"
)
SCOPING = ROOT / "docs/specs/ilc_issuance_stack_scoping_window_1343_1368_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1351_constants_bind_cdl_030_cdl_027_and_default_off_state() -> None:
    assert ECU_PRICE_CLAMP_RUNTIME_VERSION == "ecu_price_clamp_runtime_1351.v0.1"
    assert CDL_030_DEPENDENCY == "cdl_030_ecu_price_clamp_ratified_phase_277.v0.1"
    assert CDL_030_ECU_PRICE_CLAMP_RUNTIME_TOKEN == (
        "cdl_030_ecu_price_clamp_runtime_phase_1351.v0.1"
    )
    assert P_MIN_P_MAX_BOUNDS_CDL_027_DERIVED_TOKEN == (
        "p_min_p_max_bounds_cdl_027_derived_phase_1351"
    )
    assert LIVE_PRICE_ADJUSTMENT_NOT_ACTIVATED_TOKEN == (
        "live_price_adjustment_not_activated_phase_1351"
    )
    assert PRODUCTION_ECU_PRICE_CLAMP_ACTIVATION_TOKEN == (
        "phase_1366_soft_rc_eligible_true_value_path_activation_required"
    )
    assert NO_DIRECT_PRICE_CLAMP_STUB_FOUND_TOKEN == (
        "no_direct_price_clamp_stub_found_phase_1351"
    )
    assert EXPECTED_CDL_027_RUNTIME_TOKEN == "cdl_027_epoch_length_runtime_phase_1345.v0.1"
    assert CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN == EXPECTED_CDL_027_RUNTIME_TOKEN
    assert EXPECTED_CDL_027_HALVING_INTERVAL_ISSUANCE_EPOCHS == 48
    assert HALVING_INTERVAL_ISSUANCE_EPOCHS == 48
    assert EXPECTED_CDL_027_ISSUANCE_EPOCH_DURATION == "1_month"
    assert ISSUANCE_EPOCH_DURATION == "1_month"
    assert P_MIN == Decimal("0.75")
    assert P_MAX == Decimal("1.30")
    assert PRICE_CLAMP_WIDTH == Decimal("0.55")


def test_cdl_030_bounds_derive_from_cdl_027_schedule_anchor() -> None:
    require_cdl_027_schedule_dependency()
    assert derive_cdl_030_price_bounds_from_cdl_027_schedule() == (
        Decimal("0.75"),
        Decimal("1.30"),
    )


def test_cdl_027_dependency_guard_fails_closed_on_schedule_mismatch() -> None:
    with pytest.raises(ValueError, match="cdl_027_runtime_token_mismatch_phase_1351"):
        require_cdl_027_schedule_dependency(cdl_027_runtime_token="wrong")
    with pytest.raises(ValueError, match="cdl_027_halving_interval_mismatch_phase_1351"):
        require_cdl_027_schedule_dependency(halving_interval_issuance_epochs=49)
    with pytest.raises(ValueError, match="cdl_027_halving_interval_mismatch_phase_1351"):
        require_cdl_027_schedule_dependency(halving_interval_issuance_epochs=True)
    with pytest.raises(ValueError, match="cdl_027_epoch_duration_mismatch_phase_1351"):
        require_cdl_027_schedule_dependency(issuance_epoch_duration="1_week")


def test_price_clamp_quote_keeps_in_band_price_default_off() -> None:
    quote = build_ecu_price_clamp_quote(issuance_epoch=7, proposed_price="1.05")

    assert quote.runtime_version == ECU_PRICE_CLAMP_RUNTIME_VERSION
    assert quote.cdl_030_dependency == CDL_030_DEPENDENCY
    assert quote.cdl_027_runtime_token == CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN
    assert quote.derivation_token == P_MIN_P_MAX_BOUNDS_CDL_027_DERIVED_TOKEN
    assert quote.issuance_epoch == 7
    assert quote.issuance_epoch_duration == "1_month"
    assert quote.halving_interval_issuance_epochs == 48
    assert quote.proposed_price == Decimal("1.050000000")
    assert quote.p_min == Decimal("0.75")
    assert quote.p_max == Decimal("1.30")
    assert quote.clamp_width == Decimal("0.55")
    assert quote.clamped_price == Decimal("1.050000000")
    assert quote.clamp_applied is False
    assert quote.clamp_direction == "none"
    assert quote.live_price_adjustment_activated is False
    assert quote.decision_token == LIVE_PRICE_ADJUSTMENT_NOT_ACTIVATED_TOKEN


def test_price_clamp_quote_applies_floor_and_ceiling_bounds() -> None:
    floor_quote = build_ecu_price_clamp_quote(0, "0.50")
    ceiling_quote = build_ecu_price_clamp_quote(0, "1.50")

    assert floor_quote.clamped_price == Decimal("0.75")
    assert floor_quote.clamp_applied is True
    assert floor_quote.clamp_direction == "floor"
    assert ceiling_quote.clamped_price == Decimal("1.30")
    assert ceiling_quote.clamp_applied is True
    assert ceiling_quote.clamp_direction == "ceiling"


def test_price_clamp_quote_quantizes_down_before_boundary_check() -> None:
    quote = build_ecu_price_clamp_quote(0, "1.2345678999")
    edge_quote = build_ecu_price_clamp_quote(0, "1.3000000009")

    assert quote.proposed_price == Decimal("1.234567899")
    assert quote.clamped_price == Decimal("1.234567899")
    assert edge_quote.proposed_price == Decimal("1.300000000")
    assert edge_quote.clamped_price == Decimal("1.300000000")
    assert edge_quote.clamp_direction == "none"


def test_price_bounds_guard_enforces_invariant_and_ratified_values() -> None:
    assert require_cdl_030_price_bounds() == (Decimal("0.75"), Decimal("1.30"))
    assert require_cdl_030_price_bounds("0.75", "1.30") == (
        Decimal("0.75"),
        Decimal("1.30"),
    )
    with pytest.raises(ValueError, match="p_min_must_be_less_than_p_max_phase_1351"):
        require_cdl_030_price_bounds("1.30", "0.75")
    with pytest.raises(ValueError, match="p_min_must_equal_cdl_030_0_75"):
        require_cdl_030_price_bounds("0.70", "1.30")
    with pytest.raises(ValueError, match="p_max_must_equal_cdl_030_1_30"):
        require_cdl_030_price_bounds("0.75", "1.31")


def test_exact_numeric_guards_reject_float_bool_nonfinite_and_nonpositive_values() -> None:
    with pytest.raises(
        ValueError,
        match="ecu_price_clamp_issuance_epoch_must_be_non_negative_int",
    ):
        build_ecu_price_clamp_quote(True, "1.00")
    with pytest.raises(
        ValueError,
        match="ecu_price_clamp_issuance_epoch_must_be_non_negative_int",
    ):
        build_ecu_price_clamp_quote(-1, "1.00")
    with pytest.raises(ValueError, match="proposed_price_must_be_exact_decimal"):
        build_ecu_price_clamp_quote(0, 1.00)
    with pytest.raises(ValueError, match="proposed_price_must_be_exact_decimal"):
        build_ecu_price_clamp_quote(0, True)
    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        build_ecu_price_clamp_quote(0, Decimal("NaN"))
    with pytest.raises(ValueError, match="proposed_price_must_be_positive"):
        build_ecu_price_clamp_quote(0, "0")
    with pytest.raises(ValueError, match="proposed_price_must_be_positive"):
        build_ecu_price_clamp_quote(0, "-0.01")


def test_live_price_adjustment_activation_guard_remains_default_off() -> None:
    with pytest.raises(ValueError, match=LIVE_PRICE_ADJUSTMENT_NOT_ACTIVATED_TOKEN):
        require_live_price_adjustment_activation(None)
    with pytest.raises(
        ValueError,
        match="live_price_adjustment_activation_not_implemented_phase_1351",
    ):
        require_live_price_adjustment_activation(PRODUCTION_ECU_PRICE_CLAMP_ACTIVATION_TOKEN)


def test_canonical_record_uses_strings_for_decimal_values() -> None:
    record = build_ecu_price_clamp_quote(issuance_epoch=5, proposed_price="1.50").to_canonical_record()

    assert record["runtime_version"] == ECU_PRICE_CLAMP_RUNTIME_VERSION
    assert record["cdl_030_dependency"] == CDL_030_DEPENDENCY
    assert record["cdl_027_runtime_token"] == CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN
    assert record["proposed_price"] == "1.5"
    assert record["p_min"] == "0.75"
    assert record["p_max"] == "1.3"
    assert record["clamp_width"] == "0.55"
    assert record["clamped_price"] == "1.3"
    assert record["clamp_applied"] is True
    assert record["clamp_direction"] == "ceiling"
    assert record["live_price_adjustment_activated"] is False
    assert record["decision_token"] == LIVE_PRICE_ADJUSTMENT_NOT_ACTIVATED_TOKEN


def test_evidence_prompt_frontier_and_walkthrough_record_tokens() -> None:
    evidence = _read(CDL_030_EVIDENCE)
    prelock = _read(CDL_030_PRELOCK)
    cdl_027_evidence = _read(CDL_027_EVIDENCE)
    scoping = _read(SCOPING)
    prompt = _read(PROMPT)
    status = _read(STATUS)
    index = _read(INDEX)
    forward_plan = _read(FORWARD_PLAN)
    walkthrough = _read(WALKTHROUGH)
    runtime = _read(RUNTIME)

    assert "Formal declaration:" in evidence
    assert "`CDL-030` is ratified in Phase 277" in evidence
    assert "selected `P_min = 0.75`" in evidence
    assert "selected `P_max = 1.30`" in evidence
    assert "formulation: `halving`" in prelock
    assert "constant: `H=48`" in prelock
    assert "epoch duration: `1 month`" in prelock
    assert "`CDL-027` is ratified in Phase 276 as `halving`" in cdl_027_evidence
    assert "No `NotImplementedError` stubs exist" in scoping
    assert 'P_MIN = Decimal("0.75")' in runtime
    assert 'P_MAX = Decimal("1.30")' in runtime
    assert "assert " not in runtime
    for token in (
        "cdl_030_ecu_price_clamp_runtime_phase_1351.v0.1",
        "p_min_p_max_bounds_cdl_027_derived_phase_1351",
        "live_price_adjustment_not_activated_phase_1351",
        "phase_1366_soft_rc_eligible_true_value_path_activation_required",
        "no_direct_price_clamp_stub_found_phase_1351",
    ):
        assert token in prompt
        assert token in status
        assert token in index
        assert token in forward_plan
        assert token in walkthrough
