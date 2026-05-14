from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch import (
    CDL_025_DEPENDENCY,
    CDL_026_DEPENDENCY,
    CDL_027_DEPENDENCY,
    C_MAX_ILC,
    DEVNET_PRODUCTION_TRANSITION_GATE_TOKEN,
    EPOCH_EMISSION_RUNTIME_VERSION,
    HALVING_INTERVAL_ISSUANCE_EPOCHS,
    ISSUANCE_EPOCH_DURATION,
    ISSUANCE_SCHEDULE_HORIZON_EPOCHS,
    PRODUCTION_EMISSION_ACTIVATION_TOKEN,
    PRODUCTION_MINTING_NOT_ACTIVATED_TOKEN,
    TERMINAL_ISSUANCE_MODEL,
    VALIDATION_EPOCH_SECONDS,
    build_epoch_emission_quote,
    epoch_zero_emission_budget,
    raw_epoch_emission_budget,
    require_production_minting_activation,
)


RUNTIME_PATH = Path("ilc_core/epoch/epoch_emission_runtime.py")
PROMPT = Path("docs/antigravity_tasks/antigravity_prompt__phase_1345_g8_production_epoch_emission_engine.md")
STATUS = Path("docs/phases/STATUS.md")
INDEX = Path("docs/PLANNING_INDEX.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1345_constants_are_cdl_bound_and_default_off() -> None:
    assert EPOCH_EMISSION_RUNTIME_VERSION == "epoch_emission_runtime_1345.v0.1"
    assert CDL_025_DEPENDENCY == "cdl_025_terminal_issuance_model_ratified_phase_267.v0.1"
    assert CDL_026_DEPENDENCY == "cdl_026_cmax_lock_ratified_phase_273.v0.1"
    assert CDL_027_DEPENDENCY == "cdl_027_decay_formulation_ratified_phase_276.v0.1"
    assert TERMINAL_ISSUANCE_MODEL == "fee_funded_tail_model_b"
    assert C_MAX_ILC == Decimal("25920000")
    assert HALVING_INTERVAL_ISSUANCE_EPOCHS == 48
    assert ISSUANCE_EPOCH_DURATION == "1_month"
    assert VALIDATION_EPOCH_SECONDS == 60
    assert ISSUANCE_SCHEDULE_HORIZON_EPOCHS == 480
    assert PRODUCTION_MINTING_NOT_ACTIVATED_TOKEN == "production_minting_not_activated_phase_1345"
    assert DEVNET_PRODUCTION_TRANSITION_GATE_TOKEN == "devnet_production_transition_gate_recorded_phase_1345"


def test_halving_schedule_uses_decimal_budget_and_halves_at_h48() -> None:
    epoch_zero = epoch_zero_emission_budget()
    epoch_48 = raw_epoch_emission_budget(48)
    epoch_96 = raw_epoch_emission_budget(96)
    assert epoch_zero == Decimal("371973.146271994")
    assert epoch_48 == Decimal("185986.573135996")
    assert epoch_96 == Decimal("92993.286567998")
    assert abs((epoch_48 / epoch_zero) - Decimal("0.5")) < Decimal("0.000000001")
    assert abs((epoch_96 / epoch_48) - Decimal("0.5")) < Decimal("0.000000001")


def test_quote_enforces_cmax_without_activating_minting() -> None:
    quote = build_epoch_emission_quote(0, Decimal("25919999"))
    assert quote.raw_epoch_budget_ilc == Decimal("371973.146271994")
    assert quote.remaining_cap_before_epoch_ilc == Decimal("1.000000000")
    assert quote.capped_epoch_budget_ilc == Decimal("1.000000000")
    assert quote.cap_enforced is True
    assert quote.production_minting_activated is False
    assert quote.decision_token == PRODUCTION_MINTING_NOT_ACTIVATED_TOKEN


def test_quote_zeroes_budget_at_cmax_and_rejects_over_cap() -> None:
    at_cap = build_epoch_emission_quote(10, C_MAX_ILC)
    assert at_cap.remaining_cap_before_epoch_ilc == Decimal("0E-9")
    assert at_cap.capped_epoch_budget_ilc == Decimal("0E-9")
    assert at_cap.cap_enforced is True
    with pytest.raises(ValueError, match="cumulative_issued_exceeds_c_max"):
        build_epoch_emission_quote(10, C_MAX_ILC + Decimal("0.000000001"))


def test_exact_numeric_guards_reject_float_bool_negative_and_non_finite() -> None:
    with pytest.raises(ValueError, match="issuance_epoch_must_be_non_negative_int"):
        build_epoch_emission_quote(True, Decimal("0"))
    with pytest.raises(ValueError, match="issuance_epoch_must_be_non_negative_int"):
        build_epoch_emission_quote(-1, Decimal("0"))
    with pytest.raises(ValueError, match="cumulative_issued_before_epoch_ilc_must_be_exact_decimal"):
        build_epoch_emission_quote(0, 0.1)
    with pytest.raises(ValueError, match="cumulative_issued_before_epoch_ilc_must_be_finite"):
        build_epoch_emission_quote(0, Decimal("NaN"))
    with pytest.raises(ValueError, match="cumulative_issued_before_epoch_ilc_must_be_non_negative"):
        build_epoch_emission_quote(0, Decimal("-1"))


def test_devnet_production_transition_gate_remains_closed() -> None:
    with pytest.raises(ValueError, match=PRODUCTION_MINTING_NOT_ACTIVATED_TOKEN):
        require_production_minting_activation(None)
    with pytest.raises(ValueError, match="production_minting_activation_not_implemented_phase_1345"):
        require_production_minting_activation(PRODUCTION_EMISSION_ACTIVATION_TOKEN)


def test_canonical_record_serializes_decimals_as_strings() -> None:
    record = build_epoch_emission_quote(48, "0").to_canonical_record()
    assert record["runtime_version"] == EPOCH_EMISSION_RUNTIME_VERSION
    assert record["c_max_ilc"] == "25920000"
    assert record["raw_epoch_budget_ilc"] == "185986.573135996"
    assert record["production_minting_activated"] is False
    assert record["decision_token"] == PRODUCTION_MINTING_NOT_ACTIVATED_TOKEN


def test_phase_1345_prompt_status_and_index_tokens_are_recorded() -> None:
    prompt = _read(PROMPT)
    status = _read(STATUS)
    index = _read(INDEX)
    runtime = _read(RUNTIME_PATH)
    for token in (
        "cdl_025_emission_schedule_runtime_phase_1345.v0.1",
        "cdl_026_cmax_cap_runtime_phase_1345.v0.1",
        "cdl_027_epoch_length_runtime_phase_1345.v0.1",
        "c_max_enforcement_runtime_phase_1345",
        "devnet_production_transition_gate_recorded_phase_1345",
        "production_minting_not_activated_phase_1345",
    ):
        assert token in prompt or token in runtime
        assert token in status
        assert token in index
