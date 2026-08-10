from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.ledger.exact_numeric import decimal_to_canonical_string


def test_decimal_to_canonical_string_protocol_contract_vectors() -> None:
    cases = [
        (Decimal("0"), "0"),
        (Decimal("1"), "1"),
        (Decimal("1.5"), "1.5"),
        (Decimal("1.50"), "1.5"),
        (Decimal("0.000000000001"), "0.000000000001"),
        (Decimal("0.45"), "0.45"),
        (Decimal("0.050000000000"), "0.05"),
        (Decimal("1E+2"), "100"),
        (Decimal("1.23456789012345678901234567890"), "1.2345678901234567890123456789"),
        (Decimal("-0"), "0"),
    ]
    for value, expected in cases:
        assert decimal_to_canonical_string(value) == expected


def test_decimal_to_canonical_string_rejects_non_finite_values() -> None:
    for value in [Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")]:
        with pytest.raises(ValueError, match="invalid_exact_numeric_value"):
            decimal_to_canonical_string(value)


def test_decimal_to_canonical_string_docstring_marks_protocol_invariant() -> None:
    doc = decimal_to_canonical_string.__doc__ or ""
    assert "PROTOCOL INVARIANT" in doc
    assert "Changing this function's output" in doc
