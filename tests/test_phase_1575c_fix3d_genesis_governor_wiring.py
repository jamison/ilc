from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.analysis.genesis_accrual_governor import C_MAX_ILC, THETA_HARD
from ilc_core.epoch.allocation_distributor_runtime import (
    CDL_029_POST_THETA_HARD_ROUTING_GOVERNOR_WIRED_TOKEN,
)
from ilc_core.epoch.epoch_emission_runtime import ILC_QUANTUM
from ilc_core.epoch.epoch_emission_production_path import (
    GENESIS_GOVERNOR_WIRING_DEPENDENCY,
    GENESIS_GOVERNOR_WIRING_TOKEN,
    compute_epoch_emission_production_path,
)


def test_fix3d_wiring_tokens_are_pinned() -> None:
    assert GENESIS_GOVERNOR_WIRING_TOKEN == (
        "genesis_governor_wired_into_production_path_1575c_fix3d.v0.1"
    )
    assert GENESIS_GOVERNOR_WIRING_DEPENDENCY == (
        "genesis_accrual_governor_decimal_migration_1575c_fix3c.v0.1"
    )
    assert CDL_029_POST_THETA_HARD_ROUTING_GOVERNOR_WIRED_TOKEN == (
        "cdl_029_post_theta_hard_routing_governor_wired_phase_1575c_fix3d"
    )


def test_fix3d_governor_not_called_without_accrual_signal() -> None:
    result = compute_epoch_emission_production_path(
        3,
        Decimal("1000.000000001"),
        Decimal("250.000000009"),
    )

    assert result.governor_report is None
    assert result.allocation_quote.genesis_overhead_cap_blocked is False


def test_fix3d_governor_called_when_accrual_signal_supplied() -> None:
    result = compute_epoch_emission_production_path(
        3,
        Decimal("1000.000000001"),
        Decimal("250.000000009"),
        genesis_cumulative_accrual_ilc=Decimal("500"),
    )

    assert result.governor_report is not None
    assert result.governor_report["cap_blocked"] is False
    assert "genesis_share_ratio" in result.governor_report
    assert "taper_multiplier" in result.governor_report


def test_fix3d_cap_blocked_true_at_theta_hard_boundary_for_residual_only_quote() -> None:
    result = compute_epoch_emission_production_path(
        3,
        Decimal("20000000"),
        Decimal("0.000000001"),
        genesis_cumulative_accrual_ilc=Decimal(str(THETA_HARD)) * C_MAX_ILC,
    )

    assert result.governor_report is not None
    assert result.governor_report["cap_blocked"] is True
    assert result.allocation_quote.genesis_overhead_cap_blocked is True
    assert result.allocation_quote.genesis_overhead_pool_ilc == Decimal("0")


def test_fix3d_one_quantum_below_cap_is_not_blocked() -> None:
    result = compute_epoch_emission_production_path(
        3,
        Decimal("20000000"),
        Decimal("0.000000001"),
        genesis_cumulative_accrual_ilc=(Decimal(str(THETA_HARD)) * C_MAX_ILC) - ILC_QUANTUM,
    )

    assert result.governor_report is not None
    assert result.governor_report["cap_blocked"] is False
    assert result.allocation_quote.genesis_overhead_cap_blocked is False


def test_fix3d_cap_blocked_false_below_theta_hard() -> None:
    result = compute_epoch_emission_production_path(
        3,
        Decimal("1000.000000001"),
        Decimal("250.000000009"),
        genesis_cumulative_accrual_ilc=Decimal("500"),
    )

    assert result.governor_report is not None
    assert result.governor_report["cap_blocked"] is False
    assert result.allocation_quote.genesis_overhead_cap_blocked is False


def test_fix3d_epoch0_nonzero_accrual_is_rejected() -> None:
    with pytest.raises(ValueError, match="genesis_accrual_governor_inconsistent_zero_issuance"):
        compute_epoch_emission_production_path(
            0,
            Decimal("0"),
            Decimal("0.000000001"),
            genesis_cumulative_accrual_ilc=ILC_QUANTUM,
        )


def test_fix3d_test_only_override_is_explicit_and_type_checked() -> None:
    result = compute_epoch_emission_production_path(
        3,
        Decimal("0"),
        Decimal("0.000000001"),
        _test_only_genesis_cap_blocked_override=True,
    )

    assert result.governor_report is None
    assert result.allocation_quote.genesis_overhead_cap_blocked is True

    with pytest.raises(ValueError, match="_test_only_genesis_cap_blocked_override_must_be_bool"):
        compute_epoch_emission_production_path(
            3,
            Decimal("0"),
            Decimal("0.000000001"),
            _test_only_genesis_cap_blocked_override=1,  # type: ignore[arg-type]
        )
