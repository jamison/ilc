"""Phase 1532p OBL-020 emission production path tests."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch.allocation_distributor_runtime import (
    MAX_UPHELD_REFUTATION_RECIPIENTS,
)
from ilc_core.epoch.epoch_emission_production_path import (
    CDL_EMISSION_AUTHORITY_TOKENS,
    PRODUCTION_EMISSION_NOT_ACTIVATED,
    EpochEmissionProductionResult,
    compute_epoch_emission_production_path,
)
from ilc_core.epoch.issuance_economics_integration_gate import (
    ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS,
)


ROOT = Path(__file__).resolve().parents[1]


def _result() -> EpochEmissionProductionResult:
    return compute_epoch_emission_production_path(
        3,
        Decimal("1000.000000001"),
        Decimal("250.000000009"),
    )


def test_phase_1532p_guard_is_true_and_authority_tokens_are_bound() -> None:
    assert PRODUCTION_EMISSION_NOT_ACTIVATED is True
    assert CDL_EMISSION_AUTHORITY_TOKENS == [
        "cdl_025_emission_schedule_runtime_phase_1345.v0.1",
        "cdl_026_cmax_cap_runtime_phase_1345.v0.1",
        "cdl_027_epoch_length_runtime_phase_1345.v0.1",
        "cdl_028_fee_burn_split_ratified_phase_274.v0.1",
        "cdl_029_allocation_split_ratified_phase_272.v0.1",
    ]


def test_phase_1532p_returns_default_off_production_result() -> None:
    result = _result()

    assert isinstance(result, EpochEmissionProductionResult)
    assert result.production_emission_activated is False
    assert result.guard_token == "PRODUCTION_EMISSION_NOT_ACTIVATED"
    assert result.gate_report.verdict == ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS
    assert result.emission_quote.issuance_epoch == 3
    assert result.fee_burn_quote.issuance_epoch == 3
    assert result.allocation_quote.issuance_epoch == 3
    assert (
        result.allocation_quote.total_epoch_allocation_ilc
        == result.fee_burn_quote.remaining_fee_pool_ilc
    )


def test_phase_1532p_same_inputs_are_deterministic() -> None:
    first = _result().to_canonical_record()
    second = _result().to_canonical_record()

    assert first == second


@pytest.mark.parametrize(
    ("cumulative", "fees", "expected"),
    [
        (1.25, Decimal("10"), "float_input_rejected"),
        (Decimal("1"), 10.5, "float_input_rejected"),
        (Decimal("NaN"), Decimal("10"), "invalid_amount_non_finite"),
        (Decimal("1"), Decimal("Infinity"), "invalid_amount_non_finite"),
    ],
)
def test_phase_1532p_rejects_float_and_non_finite_inputs(
    cumulative: object,
    fees: object,
    expected: str,
) -> None:
    with pytest.raises(ValueError, match=expected):
        compute_epoch_emission_production_path(0, cumulative, fees)  # type: ignore[arg-type]


def test_phase_1532p_gate_constant_remains_present_and_unchanged() -> None:
    gate_source = (
        ROOT / "ilc_core/epoch/issuance_economics_integration_gate.py"
    ).read_text(encoding="utf-8")

    assert (
        'ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS = "issuance_economics_integration_gate_pass"'
        in gate_source
    )


def test_phase_1532p_canonical_record_contains_no_wallet_ledger_or_treasury_write() -> None:
    record = _result().to_canonical_record()
    rendered = str(record).lower()

    assert "ledger_write" not in rendered
    assert "wallet_write" not in rendered
    assert "treasury_write" not in rendered


def test_phase_1537p_fix1_bounds_upheld_refutation_recipients() -> None:
    too_many_recipients = [
        f"agent:refuter:{index}"
        for index in range(MAX_UPHELD_REFUTATION_RECIPIENTS + 1)
    ]
    with pytest.raises(ValueError, match="upheld_refutation_recipients_exceeds_max_count"):
        compute_epoch_emission_production_path(
            0,
            Decimal("0"),
            Decimal("0.000000001"),
            genesis_overhead_cap_blocked=True,
            upheld_refutation_recipients=too_many_recipients,
        )

    too_long_recipient = "agent:" + ("x" * 260)
    with pytest.raises(ValueError, match="upheld_refutation_recipient_id_exceeds_max_bytes"):
        compute_epoch_emission_production_path(
            0,
            Decimal("0"),
            Decimal("0.000000001"),
            genesis_overhead_cap_blocked=True,
            upheld_refutation_recipients=[too_long_recipient],
        )
