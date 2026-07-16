from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.analysis.genesis_accrual_governor import (
    C_MAX_ILC,
    CDL_029_AMENDMENT_2_DEPENDENCY,
    GENESIS_ACCRUAL_GOVERNOR_DECIMAL_MIGRATION_TOKEN,
    GENESIS_ACCRUAL_GOVERNOR_RUNTIME_VERSION,
    THETA_HARD,
    compute_genesis_share_ratio,
    evaluate_genesis_accrual_governor,
    simulate_genesis_accrual_governor_trajectory,
)
from ilc_core.exceptions import GenesisAccrualGovernorError


def test_phase_1573ab_runtime_version_and_dependency_tokens_are_pinned() -> None:
    assert GENESIS_ACCRUAL_GOVERNOR_RUNTIME_VERSION == (
        "genesis_accrual_governor_runtime_1575c_fix3c.v0.1"
    )
    assert GENESIS_ACCRUAL_GOVERNOR_DECIMAL_MIGRATION_TOKEN == (
        "genesis_accrual_governor_decimal_migration_1575c_fix3c.v0.1"
    )
    assert CDL_029_AMENDMENT_2_DEPENDENCY == (
        "cdl_029_amendment_2_cmax_denominator_phase_1573aa"
    )
    assert C_MAX_ILC == Decimal("25920000")


def test_phase_1573ab_share_ratio_uses_cmax_not_total_issued() -> None:
    ratio = compute_genesis_share_ratio(
        {
            "genesis_cumulative_accrual": Decimal("648000"),
            "total_cumulative_issuance": Decimal("5000000"),
        }
    )

    assert ratio == pytest.approx(648_000.0 / 25_920_000.0)
    assert ratio != pytest.approx(648_000.0 / 5_000_000.0)


def test_phase_1573ab_hard_cap_boundary_is_cmax_based() -> None:
    below_cap = evaluate_genesis_accrual_governor(
        {
            "genesis_cumulative_accrual": Decimal("648000"),
            "total_cumulative_issuance": Decimal("5000000"),
        }
    )
    at_cap = evaluate_genesis_accrual_governor(
        {
            "genesis_cumulative_accrual": Decimal(str(THETA_HARD)) * C_MAX_ILC,
            "total_cumulative_issuance": Decimal("5000000"),
        }
    )

    assert below_cap["genesis_share_ratio"] == pytest.approx(0.025)
    assert below_cap["cap_blocked"] is False
    assert below_cap["taper_multiplier"] > 0.0
    assert at_cap["genesis_share_ratio"] == pytest.approx(THETA_HARD)
    assert at_cap["cap_blocked"] is True
    assert at_cap["taper_multiplier"] == pytest.approx(0.0)


def test_phase_1573ab_total_issuance_remains_validation_signal_not_denominator() -> None:
    low_issuance_ratio = compute_genesis_share_ratio(
        {
            "genesis_cumulative_accrual": Decimal("10"),
            "total_cumulative_issuance": Decimal("100"),
        }
    )
    high_issuance_ratio = compute_genesis_share_ratio(
        {
            "genesis_cumulative_accrual": Decimal("10"),
            "total_cumulative_issuance": Decimal("1000000"),
        }
    )

    assert low_issuance_ratio == high_issuance_ratio

    with pytest.raises(GenesisAccrualGovernorError) as exc_info:
        compute_genesis_share_ratio(
            {
                "genesis_cumulative_accrual": Decimal("101"),
                "total_cumulative_issuance": Decimal("100"),
            }
        )
    assert str(exc_info.value) == "genesis_accrual_governor_accrual_exceeds_issuance"


def test_phase_1573ab_trajectory_uses_cmax_ratio_monotonically() -> None:
    trajectory = simulate_genesis_accrual_governor_trajectory(
        [
            {"genesis_cumulative_accrual": Decimal("0"), "total_cumulative_issuance": Decimal("0")},
            {
                "genesis_cumulative_accrual": Decimal("10"),
                "total_cumulative_issuance": Decimal("20"),
            },
            {
                "genesis_cumulative_accrual": Decimal("20"),
                "total_cumulative_issuance": Decimal("200"),
            },
        ]
    )

    assert [row["genesis_share_ratio"] for row in trajectory] == [
        pytest.approx(0.0),
        pytest.approx(10.0 / 25_920_000.0),
        pytest.approx(20.0 / 25_920_000.0),
    ]
