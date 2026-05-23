from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.epistemic.maintenance_lottery_runtime import (
    WERNER_DIAGNOSTIC_PHASE_1442_TOKENS,
    WERNER_DIAGNOSTIC_REVIEW_LANE_ONLY,
    WERNER_DIAGNOSTIC_SETTLEMENT_GRADE,
    WERNER_DIAGNOSTIC_TRANSFERABLE,
    WERNER_DIAGNOSTIC_WALLET_VISIBLE,
    WERNER_DIAGNOSTIC_WIRED_PHASE_1442_TOKEN,
    WERNER_DIASTOLIC_METRIC_DEFINED_PHASE_1442_TOKEN,
    WERNER_LOCAL_CREDIT_IS_SETTLEMENT_GRADE,
    WERNER_LOCAL_CREDIT_IS_TRANSFERABLE,
    WERNER_LOCAL_CREDIT_IS_WALLET_VISIBLE,
    WERNER_NO_ECU_DISTRIBUTION_PHASE_1442_TOKEN,
    WERNER_NO_FLOW_GOVERNOR_CDL_PHASE_1442_TOKEN,
    WERNER_PULSE_PRESSURE_METRIC_DEFINED_PHASE_1442_TOKEN,
    WERNER_REVIEW_LANE_ONLY_PHASE_1442_TOKEN,
    WERNER_SYSTOLIC_METRIC_DEFINED_PHASE_1442_TOKEN,
    build_werner_diagnostic_quote,
)


def test_phase_1442_werner_diagnostic_happy_path_pressure_metrics() -> None:
    quote = build_werner_diagnostic_quote(
        agent_id="agent:werner-diagnostic",
        epoch_id=1442,
        credit_samples=(Decimal("0"), Decimal("3.25"), Decimal("1.5"), Decimal("2")),
    )

    assert quote.agent_id == "agent:werner-diagnostic"
    assert quote.epoch_id == 1442
    assert quote.systolic_local_credit == Decimal("3.25")
    assert quote.diastolic_local_credit == Decimal("0")
    assert quote.pulse_pressure_local_credit == Decimal("3.25")


def test_phase_1442_werner_diagnostic_boundaries_remain_default_off() -> None:
    quote = build_werner_diagnostic_quote(
        agent_id="agent:werner-boundary",
        epoch_id=1442,
        credit_samples=(Decimal("1"),),
    )

    assert WERNER_LOCAL_CREDIT_IS_SETTLEMENT_GRADE is False
    assert WERNER_LOCAL_CREDIT_IS_WALLET_VISIBLE is False
    assert WERNER_LOCAL_CREDIT_IS_TRANSFERABLE is False
    assert quote.review_lane_only is True
    assert quote.settlement_grade is False
    assert quote.wallet_visible is False
    assert quote.transferable is False
    assert WERNER_DIAGNOSTIC_REVIEW_LANE_ONLY is True
    assert WERNER_DIAGNOSTIC_SETTLEMENT_GRADE is False
    assert WERNER_DIAGNOSTIC_WALLET_VISIBLE is False
    assert WERNER_DIAGNOSTIC_TRANSFERABLE is False


def test_phase_1442_werner_diagnostic_rejects_empty_samples() -> None:
    with pytest.raises(ValueError, match="invalid_werner_diagnostic_credit_samples_phase_1442"):
        build_werner_diagnostic_quote(
            agent_id="agent:empty",
            epoch_id=1442,
            credit_samples=(),
        )


def test_phase_1442_werner_diagnostic_rejects_negative_nonfinite_and_float_samples() -> None:
    for bad_sample in (Decimal("-0.1"), Decimal("NaN"), Decimal("Infinity"), 1.0):
        with pytest.raises(ValueError, match="invalid_werner_diagnostic_credit_sample_phase_1442"):
            build_werner_diagnostic_quote(
                agent_id="agent:bad-sample",
                epoch_id=1442,
                credit_samples=(bad_sample,),  # type: ignore[arg-type]
            )


def test_phase_1442_werner_diagnostic_rejects_invalid_agent_or_epoch() -> None:
    with pytest.raises(ValueError, match="invalid_werner_diagnostic_agent_id_phase_1442"):
        build_werner_diagnostic_quote(agent_id="", epoch_id=1442, credit_samples=(Decimal("1"),))
    with pytest.raises(ValueError, match="invalid_epoch_id"):
        build_werner_diagnostic_quote(
            agent_id="agent:bad-epoch",
            epoch_id=-1,
            credit_samples=(Decimal("1"),),
        )


def test_phase_1442_werner_diagnostic_tokens_are_recorded() -> None:
    quote = build_werner_diagnostic_quote(
        agent_id="agent:tokens",
        epoch_id=1442,
        credit_samples=(Decimal("0"), Decimal("1")),
    )

    for token in (
        WERNER_DIAGNOSTIC_WIRED_PHASE_1442_TOKEN,
        WERNER_SYSTOLIC_METRIC_DEFINED_PHASE_1442_TOKEN,
        WERNER_DIASTOLIC_METRIC_DEFINED_PHASE_1442_TOKEN,
        WERNER_PULSE_PRESSURE_METRIC_DEFINED_PHASE_1442_TOKEN,
        WERNER_NO_ECU_DISTRIBUTION_PHASE_1442_TOKEN,
        WERNER_NO_FLOW_GOVERNOR_CDL_PHASE_1442_TOKEN,
        WERNER_REVIEW_LANE_ONLY_PHASE_1442_TOKEN,
    ):
        assert token in WERNER_DIAGNOSTIC_PHASE_1442_TOKENS
        assert token in quote.diagnostic_tokens
