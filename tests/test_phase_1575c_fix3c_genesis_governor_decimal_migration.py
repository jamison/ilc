from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.analysis.genesis_accrual_governor import (
    C_MAX_ILC,
    GENESIS_ACCRUAL_GOVERNOR_DECIMAL_MIGRATION_TOKEN,
    GENESIS_ACCRUAL_GOVERNOR_RUNTIME_VERSION,
    evaluate_genesis_accrual_governor,
)
from ilc_core.exceptions import GenesisAccrualGovernorError


def test_fix3c_cmax_is_decimal_not_float() -> None:
    assert isinstance(C_MAX_ILC, Decimal)
    assert C_MAX_ILC == Decimal("25920000")


def test_fix3c_decimal_migration_token_pinned() -> None:
    assert GENESIS_ACCRUAL_GOVERNOR_DECIMAL_MIGRATION_TOKEN == (
        "genesis_accrual_governor_decimal_migration_1575c_fix3c.v0.1"
    )


def test_fix3c_runtime_version_updated() -> None:
    assert GENESIS_ACCRUAL_GOVERNOR_RUNTIME_VERSION == (
        "genesis_accrual_governor_runtime_1575c_fix3c.v0.1"
    )


def test_fix3c_float_monetary_input_rejected() -> None:
    with pytest.raises(GenesisAccrualGovernorError) as exc_info:
        evaluate_genesis_accrual_governor(
            {
                "genesis_cumulative_accrual": 648000.0,
                "total_cumulative_issuance": Decimal("5000000"),
            }
        )

    assert str(exc_info.value) == "genesis_accrual_governor_invalid_genesis_cumulative_accrual"


def test_fix3c_decimal_monetary_input_accepted() -> None:
    report = evaluate_genesis_accrual_governor(
        {
            "genesis_cumulative_accrual": Decimal("648000"),
            "total_cumulative_issuance": Decimal("5000000"),
        }
    )

    assert report["cap_blocked"] is False
    assert report["genesis_share_ratio"] == pytest.approx(648000.0 / 25920000.0)


def test_fix3c_accrual_cannot_exceed_issuance_by_subquantum_amount() -> None:
    with pytest.raises(GenesisAccrualGovernorError) as exc_info:
        evaluate_genesis_accrual_governor(
            {
                "genesis_cumulative_accrual": Decimal("100.0000000005"),
                "total_cumulative_issuance": Decimal("100"),
            }
        )

    assert str(exc_info.value) == "genesis_accrual_governor_accrual_exceeds_issuance"


@pytest.mark.parametrize("bad_value", [Decimal("NaN"), Decimal("Infinity")])
def test_fix3c_non_finite_decimal_rejected(bad_value: Decimal) -> None:
    with pytest.raises(GenesisAccrualGovernorError):
        evaluate_genesis_accrual_governor(
            {
                "genesis_cumulative_accrual": bad_value,
                "total_cumulative_issuance": Decimal("5000000"),
            }
        )


def test_fix3c_int_monetary_input_accepted() -> None:
    report = evaluate_genesis_accrual_governor(
        {
            "genesis_cumulative_accrual": 648000,
            "total_cumulative_issuance": 5000000,
        }
    )

    assert report["cap_blocked"] is False
    assert report["genesis_share_ratio"] == pytest.approx(648000.0 / 25920000.0)
