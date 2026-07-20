from __future__ import annotations

from decimal import Decimal, localcontext

import pytest

from ilc_core.analysis.genesis_accrual_governor import (
    DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY,
    THETA_HARD,
    THETA_SOFT,
    compute_genesis_share_ratio,
    compute_taper_multiplier,
    evaluate_genesis_accrual_governor,
    simulate_genesis_accrual_governor_trajectory,
    validate_genesis_accrual_governor_policy,
)
from ilc_core.exceptions import GenesisAccrualGovernorError


def test_phase_218_constants_are_locked_to_constitutional_targets() -> None:
    with localcontext() as ctx:
        ctx.prec = 50
        theta_soft_expected = (-Decimal("3")).exp()
    assert THETA_HARD == Decimal("0.05")
    assert THETA_SOFT == theta_soft_expected
    assert DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY["theta_hard"] == THETA_HARD
    assert DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY["theta_soft"] == THETA_SOFT


def test_phase_218_hard_cap_sets_taper_to_zero_at_and_above_cap() -> None:
    at_cap = compute_taper_multiplier(THETA_HARD)
    above_cap = compute_taper_multiplier(THETA_HARD + Decimal("0.01"))
    assert at_cap == Decimal("0E-12")
    assert above_cap == Decimal("0E-12")


def test_phase_218_below_cap_taper_is_bounded_and_positive() -> None:
    ratios = [
        Decimal("0"),
        Decimal("0.01"),
        Decimal("0.02"),
        Decimal("0.04"),
        THETA_HARD - Decimal("0.000001"),
    ]
    values = [compute_taper_multiplier(ratio) for ratio in ratios]

    assert values[0] == Decimal("1.000000000000")
    assert all(Decimal("0") < value <= Decimal("1") for value in values[1:])


def test_phase_218_taper_is_monotonic_non_increasing_by_ratio() -> None:
    ratios = [
        Decimal("0"),
        Decimal("0.01"),
        Decimal("0.02"),
        Decimal("0.03"),
        Decimal("0.04"),
        THETA_SOFT,
        THETA_HARD - Decimal("0.000001"),
    ]
    values = [compute_taper_multiplier(ratio) for ratio in ratios]
    assert all(values[idx] >= values[idx + 1] for idx in range(len(values) - 1))


def test_phase_218_zero_issuance_edge_behavior() -> None:
    ratio = compute_genesis_share_ratio(
        {
            "genesis_cumulative_accrual": Decimal("0"),
            "total_cumulative_issuance": Decimal("0"),
        }
    )
    assert ratio == Decimal("0E-12")

    with pytest.raises(GenesisAccrualGovernorError) as exc_info:
        compute_genesis_share_ratio(
            {
                "genesis_cumulative_accrual": Decimal("1"),
                "total_cumulative_issuance": Decimal("0"),
            }
        )
    assert str(exc_info.value) == "genesis_accrual_governor_inconsistent_zero_issuance"


def test_phase_218_invalid_policy_and_input_values_fail_closed() -> None:
    with pytest.raises(GenesisAccrualGovernorError) as exc_policy:
        validate_genesis_accrual_governor_policy(
            {
                "theta_hard": THETA_HARD,
                "theta_soft": Decimal("0.0498"),
                "taper_steepness": Decimal("40"),
            }
        )
    assert str(exc_policy.value) == "genesis_accrual_governor_theta_soft_constant_mismatch"

    with pytest.raises(GenesisAccrualGovernorError) as exc_non_finite:
        compute_taper_multiplier(float("inf"))
    assert str(exc_non_finite.value) == "genesis_accrual_governor_invalid_genesis_share_ratio"

    with pytest.raises(GenesisAccrualGovernorError) as exc_negative:
        evaluate_genesis_accrual_governor(
            {
                "genesis_cumulative_accrual": Decimal("-1"),
                "total_cumulative_issuance": Decimal("10"),
            }
        )
    assert str(exc_negative.value) == "genesis_accrual_governor_invalid_genesis_cumulative_accrual"


def test_phase_218_trajectory_simulation_is_deterministic() -> None:
    rows = [
        {"genesis_cumulative_accrual": Decimal("0"), "total_cumulative_issuance": Decimal("0")},
        {
            "genesis_cumulative_accrual": Decimal("1"),
            "total_cumulative_issuance": Decimal("100"),
        },
        {
            "genesis_cumulative_accrual": Decimal("2"),
            "total_cumulative_issuance": Decimal("120"),
        },
        {
            "genesis_cumulative_accrual": Decimal("4"),
            "total_cumulative_issuance": Decimal("180"),
        },
        {
            "genesis_cumulative_accrual": Decimal("8"),
            "total_cumulative_issuance": Decimal("220"),
        },
    ]
    first = simulate_genesis_accrual_governor_trajectory(rows)
    second = simulate_genesis_accrual_governor_trajectory(rows)

    assert first == second
    assert [row["step_index"] for row in first] == [0, 1, 2, 3, 4]
    assert all(Decimal("0") <= row["taper_multiplier"] <= Decimal("1") for row in first)


def test_phase_218_default_steepness_has_meaningful_taper_delta() -> None:
    low_ratio = compute_taper_multiplier(Decimal("0.01"))
    near_soft_ratio = compute_taper_multiplier(Decimal("0.04"))
    assert low_ratio > near_soft_ratio
    assert (low_ratio - near_soft_ratio) > Decimal("0.1")
