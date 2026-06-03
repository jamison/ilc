# SPDX-License-Identifier: AGPL-3.0-only
# ilc_core/economics/entropy.py
"""
Entropy-based helpers for shaping rewards in the ILC economics sandbox.

These functions provide a simple "learning signal" over empirical success rates,
and a corresponding entropy_weight(...) that upweights mid-entropy domains and
downweights tasks that are either trivial (almost always succeed) or hopeless
(almost always fail).

For how this is used in the economics sandbox and how it might map to future
genesis primitives, see docs/protocol_econ_surfaces_mvp.md.
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation

_ZERO = Decimal("0")
_ONE = Decimal("1")
_MAX_SIGNAL = Decimal("0.25")


def _decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(token)
    if not isinstance(value, (Decimal, int, str)):
        raise ValueError(token)
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(token) from exc
    if not amount.is_finite():
        raise ValueError(token)
    return amount


def _entropy_decimal(value: object, token: str) -> Decimal:
    amount = _decimal(value, token)
    if amount < _ZERO or amount > _ONE:
        raise ValueError(token)
    return amount


def learning_signal(success_rate: object) -> Decimal:
    """
    Map a success_rate in [0, 1] to a "learning signal" scalar.

    The shape is intentionally peaked around medium success probabilities, so that
    tasks which are neither trivial nor impossible produce the strongest signal.
    This is a toy model used only in the economics sandbox, not a fixed part of
    the ILC protocol.
    """
    p = _entropy_decimal(success_rate, "entropy_success_rate_invalid")
    return p * (_ONE - p)


def entropy_weight(
    success_rate: object,
    min_floor: object = Decimal("0.5"),
    max_cap: object = Decimal("2.0"),
) -> Decimal:
    """
    Compute an entropy-like weight for a given success_rate in [0, 1].

    The weight is larger for mid-range success rates (where entropy is high) and
    smaller near 0.0 or 1.0. Reward helpers such as simple_claim_reward can use
    this to reward work on "interesting" domains more than on trivial or solved
    ones. This is purely exploratory and parameterized for future tuning.
    """
    floor = _decimal(min_floor, "entropy_min_floor_invalid")
    cap = _decimal(max_cap, "entropy_max_cap_invalid")
    if floor < _ZERO or cap < _ZERO:
        raise ValueError("entropy_weight_bounds_must_be_non_negative")
    if cap < floor:
        raise ValueError("entropy_cap_must_not_be_less_than_floor")

    base_signal = learning_signal(success_rate)  # in [0, 0.25]
    # Normalize to [0, 1]
    normalized = base_signal / _MAX_SIGNAL if base_signal > _ZERO else _ZERO

    span = cap - floor
    return floor + span * normalized
