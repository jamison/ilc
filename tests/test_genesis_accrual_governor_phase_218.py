from __future__ import annotations

import math
from decimal import Decimal

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
    assert THETA_HARD == pytest.approx(1.0 / 20.0, rel=0.0, abs=1e-15)
    assert THETA_SOFT == pytest.approx(math.exp(-3.0), rel=0.0, abs=1e-15)
    assert DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY["theta_hard"] == pytest.approx(THETA_HARD)
    assert DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY["theta_soft"] == pytest.approx(THETA_SOFT)


def test_phase_218_hard_cap_sets_taper_to_zero_at_and_above_cap() -> None:
    at_cap = compute_taper_multiplier(THETA_HARD)
    above_cap = compute_taper_multiplier(THETA_HARD + 0.01)
    assert at_cap == pytest.approx(0.0)
    assert above_cap == pytest.approx(0.0)


def test_phase_218_below_cap_taper_is_bounded_and_positive() -> None:
    ratios = [0.0, 0.01, 0.02, 0.04, THETA_HARD - 1e-6]
    values = [compute_taper_multiplier(ratio) for ratio in ratios]

    assert values[0] == pytest.approx(1.0)
    assert all(0.0 < value <= 1.0 for value in values[1:])


def test_phase_218_taper_is_monotonic_non_increasing_by_ratio() -> None:
    ratios = [0.0, 0.01, 0.02, 0.03, 0.04, THETA_SOFT, THETA_HARD - 1e-6]
    values = [compute_taper_multiplier(ratio) for ratio in ratios]
    assert all(values[idx] >= values[idx + 1] for idx in range(len(values) - 1))


def test_phase_218_zero_issuance_edge_behavior() -> None:
    ratio = compute_genesis_share_ratio(
        {
            "genesis_cumulative_accrual": Decimal("0"),
            "total_cumulative_issuance": Decimal("0"),
        }
    )
    assert ratio == pytest.approx(0.0)

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
                "theta_soft": 0.0498,
                "taper_steepness": 40.0,
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
    assert all(0.0 <= row["taper_multiplier"] <= 1.0 for row in first)


def test_phase_218_default_steepness_has_meaningful_taper_delta() -> None:
    low_ratio = compute_taper_multiplier(0.01)
    near_soft_ratio = compute_taper_multiplier(0.04)
    assert low_ratio > near_soft_ratio
    assert (low_ratio - near_soft_ratio) > 0.1
