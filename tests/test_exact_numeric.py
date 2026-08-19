from decimal import Decimal

import pytest

from ilc_core.ledger.exact_numeric import (
    exact_to_canonical_string,
    normalize_json_scalars,
    parse_non_negative_decimal,
    to_decimal,
)


@pytest.mark.parametrize("value", ["NaN", "sNaN", "Infinity", "-Infinity", float("inf"), float("-inf"), float("nan")])
def test_to_decimal_rejects_non_finite_values(value: object) -> None:
    with pytest.raises(ValueError, match="invalid_exact_numeric_value"):
        to_decimal(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0.0, 0.1, 1.0])
def test_to_decimal_rejects_finite_float_values(value: float) -> None:
    with pytest.raises(ValueError, match="invalid_exact_numeric_value"):
        to_decimal(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["NaN", "Infinity"])
def test_parse_non_negative_decimal_rejects_non_finite_strings(value: str) -> None:
    with pytest.raises(ValueError, match="invalid_exact_numeric_value"):
        parse_non_negative_decimal(value)


def test_exact_to_canonical_string_preserves_finite_values() -> None:
    assert exact_to_canonical_string(Decimal("001.2300")) == "1.23"


def test_normalize_json_scalars_recurses_into_tuples() -> None:
    payload = {
        "tuple_values": (Decimal("10.5000"), {"nested": (Decimal("0"), Decimal("20.0"))}),
    }

    assert normalize_json_scalars(payload) == {
        "tuple_values": ["10.5", {"nested": ["0", "20"]}],
    }
