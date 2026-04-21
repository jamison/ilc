from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import TypeAlias


ExactNumberish: TypeAlias = Decimal | int | float | str
ZERO = Decimal("0")


def _str_to_decimal(value: str, token: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(token) from exc


def to_decimal(value: ExactNumberish, *, token: str = "invalid_exact_numeric_value") -> Decimal:
    if isinstance(value, bool):
        raise ValueError(token)
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, float):
        number = Decimal(str(value))
    elif isinstance(value, str):
        number = _str_to_decimal(value, token)
    else:
        raise ValueError(token)

    if not number.is_finite():
        raise ValueError(token)
    return number


def decimal_to_canonical_string(value: Decimal) -> str:
    if value == ZERO:
        return "0"

    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")

    if rendered.startswith("-"):
        sign = "-"
        body = rendered[1:]
    else:
        sign = ""
        body = rendered

    if "." in body:
        whole, fractional = body.split(".", 1)
        whole = whole.lstrip("0") or "0"
        body = f"{whole}.{fractional}"
    else:
        body = body.lstrip("0") or "0"

    normalized = f"{sign}{body}"
    if normalized in {"-0", "-0.0", ""}:
        return "0"
    return normalized


def exact_to_canonical_string(
    value: ExactNumberish,
    *,
    token: str = "invalid_exact_numeric_value",
) -> str:
    return decimal_to_canonical_string(to_decimal(value, token=token))


def parse_non_negative_decimal(
    value: ExactNumberish,
    *,
    token: str = "invalid_exact_numeric_value",
) -> Decimal:
    number = to_decimal(value, token=token)
    if number < ZERO:
        raise ValueError(token)
    return number


def normalize_json_scalars(value: object) -> object:
    if isinstance(value, Decimal):
        return decimal_to_canonical_string(value)
    if isinstance(value, dict):
        return {
            str(key): normalize_json_scalars(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [normalize_json_scalars(item) for item in value]
    return value


def exact_sum(values: list[Decimal]) -> Decimal:
    return sum(values, ZERO)
