from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch import (
    CDL_028_DEPENDENCY,
    CDL_028_FEE_BURN_SPLIT_RUNTIME_TOKEN,
    FEE_BURN_10_PERCENT_GENESIS_POOL_TOKEN,
    FEE_BURN_RATIO,
    FEE_BURN_SPLIT_RUNTIME_VERSION,
    GENESIS_BURN_POOL_LABEL,
    NO_DIRECT_FEE_BURN_STUB_FOUND_TOKEN,
    POST_CDL_028_REMAINING_FEE_POOL_LABEL,
    PRODUCTION_FEE_BURN_ACTIVATION_TOKEN,
    PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN,
    build_fee_burn_split_quote,
    require_cdl_028_fee_burn_ratio,
    require_production_fee_burn_activation,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/epoch/fee_burn_split_runtime.py"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1346_g8_cdl_028_fee_burn_split_runtime.md"
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
WALKTHROUGH = ROOT / "docs/phases/phase_1346_cdl_028_fee_burn_split_runtime_walkthrough.md"
CDL_028_EVIDENCE = ROOT / "docs/specs/ilc_cdl_028_fee_burn_split_ratification_evidence_274_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1346_constants_bind_cdl_028_and_default_off_state() -> None:
    assert FEE_BURN_SPLIT_RUNTIME_VERSION == "fee_burn_split_runtime_1346.v0.1"
    assert CDL_028_DEPENDENCY == "cdl_028_fee_burn_split_ratified_phase_274.v0.1"
    assert CDL_028_FEE_BURN_SPLIT_RUNTIME_TOKEN == "cdl_028_fee_burn_split_runtime_phase_1346.v0.1"
    assert FEE_BURN_10_PERCENT_GENESIS_POOL_TOKEN == "fee_burn_10_percent_genesis_pool_phase_1346"
    assert PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN == "fee_burn_not_activated_phase_1346"
    assert PRODUCTION_FEE_BURN_ACTIVATION_TOKEN == (
        "phase_1366_soft_rc_eligible_true_value_path_activation_required"
    )
    assert NO_DIRECT_FEE_BURN_STUB_FOUND_TOKEN == "no_direct_fee_burn_stub_found_phase_1346"
    assert FEE_BURN_RATIO == Decimal("0.10")
    assert GENESIS_BURN_POOL_LABEL == "genesis_burn_pool"
    assert POST_CDL_028_REMAINING_FEE_POOL_LABEL == "post_cdl_028_remaining_fee_pool"


def test_fee_burn_split_routes_10_percent_to_genesis_burn_pool() -> None:
    quote = build_fee_burn_split_quote(issuance_epoch=7, total_epoch_fees_ilc=Decimal("123.45"))

    assert quote.issuance_epoch == 7
    assert quote.total_epoch_fees_ilc == Decimal("123.450000000")
    assert quote.fee_burn_ratio == Decimal("0.10")
    assert quote.genesis_burn_pool_ilc == Decimal("12.345000000")
    assert quote.remaining_fee_pool_ilc == Decimal("111.105000000")
    assert quote.genesis_burn_pool_ilc + quote.remaining_fee_pool_ilc == quote.total_epoch_fees_ilc
    assert quote.genesis_burn_pool_label == GENESIS_BURN_POOL_LABEL
    assert quote.production_fee_burn_activated is False
    assert quote.decision_token == PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN


def test_fee_burn_split_quantizes_down_without_losing_total_balance() -> None:
    quote = build_fee_burn_split_quote(0, "1.2345678999")

    assert quote.total_epoch_fees_ilc == Decimal("1.234567899")
    assert quote.genesis_burn_pool_ilc == Decimal("0.123456789")
    assert quote.remaining_fee_pool_ilc == Decimal("1.111111110")
    assert quote.genesis_burn_pool_ilc + quote.remaining_fee_pool_ilc == quote.total_epoch_fees_ilc


def test_fee_burn_ratio_enforces_cdl_028_10_percent_only() -> None:
    assert require_cdl_028_fee_burn_ratio() == Decimal("0.10")
    assert require_cdl_028_fee_burn_ratio("0.10") == Decimal("0.10")

    with pytest.raises(ValueError, match="fee_burn_ratio_must_equal_cdl_028"):
        require_cdl_028_fee_burn_ratio("0.30")
    with pytest.raises(ValueError, match="fee_burn_ratio_must_equal_cdl_028"):
        build_fee_burn_split_quote(0, "10", fee_burn_ratio="0.05")


def test_exact_numeric_guards_reject_float_bool_negative_and_non_finite() -> None:
    with pytest.raises(ValueError, match="fee_issuance_epoch_must_be_non_negative_int"):
        build_fee_burn_split_quote(True, Decimal("0"))
    with pytest.raises(ValueError, match="fee_issuance_epoch_must_be_non_negative_int"):
        build_fee_burn_split_quote(-1, Decimal("0"))
    with pytest.raises(ValueError, match="total_epoch_fees_ilc_must_be_exact_decimal"):
        build_fee_burn_split_quote(0, 0.1)
    with pytest.raises(ValueError, match="total_epoch_fees_ilc_must_be_finite"):
        build_fee_burn_split_quote(0, Decimal("NaN"))
    with pytest.raises(ValueError, match="total_epoch_fees_ilc_must_be_non_negative"):
        build_fee_burn_split_quote(0, Decimal("-0.000000001"))


def test_production_fee_burn_guard_remains_closed() -> None:
    with pytest.raises(ValueError, match=PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN):
        require_production_fee_burn_activation(None)
    with pytest.raises(ValueError, match="production_fee_burn_activation_not_implemented_phase_1346"):
        require_production_fee_burn_activation(PRODUCTION_FEE_BURN_ACTIVATION_TOKEN)


def test_canonical_record_uses_strings_for_decimal_amounts() -> None:
    record = build_fee_burn_split_quote(3, "100").to_canonical_record()

    assert record["runtime_version"] == FEE_BURN_SPLIT_RUNTIME_VERSION
    assert record["fee_burn_ratio"] == "0.1"
    assert record["total_epoch_fees_ilc"] == "100"
    assert record["genesis_burn_pool_ilc"] == "10"
    assert record["remaining_fee_pool_ilc"] == "90"
    assert record["production_fee_burn_activated"] is False
    assert record["decision_token"] == PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN


def test_evidence_prompt_frontier_and_walkthrough_record_tokens() -> None:
    evidence = _read(CDL_028_EVIDENCE)
    prompt = _read(PROMPT)
    status = _read(STATUS)
    index = _read(INDEX)
    forward_plan = _read(FORWARD_PLAN)
    walkthrough = _read(WALKTHROUGH)
    runtime = _read(RUNTIME)

    assert "fee-burn ratio = `10%`" in evidence
    assert 'FEE_BURN_RATIO = Decimal("0.10")' in runtime
    for token in (
        "cdl_028_fee_burn_split_runtime_phase_1346.v0.1",
        "fee_burn_10_percent_genesis_pool_phase_1346",
        "fee_burn_not_activated_phase_1346",
        "phase_1366_soft_rc_eligible_true_value_path_activation_required",
        "no_direct_fee_burn_stub_found_phase_1346",
    ):
        assert token in prompt
        assert token in status
        assert token in index
        assert token in forward_plan
        assert token in walkthrough
