# SPDX-License-Identifier: AGPL-3.0-or-later
"""CDL-V1 temporal decay runtime.

The runtime enforces issuance-epoch-scoped decay helpers using deterministic
Decimal arithmetic and tokenized validation failures.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, localcontext
from typing import TypeAlias

CDL_V1_RUNTIME_VERSION = "cdl_v1_temporal_decay_runtime_388.v0.1"
CDL_V1_DEPENDENCY = "cdl_v1_temporal_decay_388.v0.1"
CDL_V1_DECIMAL_REWRITE_TOKEN = "temporal_decay_no_float_arithmetic_phase_1357"

ExactNumberish: TypeAlias = Decimal | int | str
ZERO = Decimal("0")
ONE = Decimal("1")
TWELVE_PLACES = Decimal("0.000000000001")


class TemporalDecayValidationError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def _require_numeric(name: str, value: object) -> Decimal:
    if isinstance(value, bool):
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_invalid_numeric",
            f"{name} must be an exact finite numeric value",
        )
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, str):
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise TemporalDecayValidationError(
                "cdl_v1_temporal_decay_invalid_numeric",
                f"{name} must be an exact finite numeric value",
            ) from exc
    else:
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_invalid_numeric",
            f"{name} must be an exact finite numeric value",
        )
    if not number.is_finite():
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_invalid_numeric",
            f"{name} must be a finite numeric value",
        )
    return ZERO if number.is_signed() and number == ZERO else number


def _quantize_twelve_places(value: Decimal) -> Decimal:
    return value.quantize(TWELVE_PLACES)


def compute_decay_multiplier(
    *,
    elapsed_issuance_epochs: ExactNumberish,
    half_life_epochs: ExactNumberish,
    floor_multiplier: ExactNumberish,
) -> Decimal:
    """Compute exponential temporal-decay multiplier with floor enforcement."""

    elapsed = _require_numeric("elapsed_issuance_epochs", elapsed_issuance_epochs)
    half_life = _require_numeric("half_life_epochs", half_life_epochs)
    floor = _require_numeric("floor_multiplier", floor_multiplier)

    if elapsed < ZERO:
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_negative_elapsed",
            "elapsed_issuance_epochs must be >= 0",
        )
    if half_life <= ZERO:
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_half_life_non_positive",
            "half_life_epochs must be > 0",
        )
    if floor < ZERO or floor > ONE:
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_floor_out_of_range",
            "floor_multiplier must be in [0, 1]",
        )

    with localcontext() as ctx:
        ctx.prec = 50
        raw = (-(Decimal("2").ln() * (elapsed / half_life))).exp()
    multiplier = max(floor, min(ONE, raw))
    return _quantize_twelve_places(multiplier)


def apply_temporal_decay(
    *,
    base_ecu_score: ExactNumberish,
    elapsed_issuance_epochs: ExactNumberish,
    half_life_epochs: ExactNumberish,
    floor_multiplier: ExactNumberish,
    epoch_type: str = "issuance_epoch",
) -> Decimal:
    """Apply temporal decay to base score under issuance-epoch scope."""

    base = _require_numeric("base_ecu_score", base_ecu_score)

    if base < ZERO:
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_negative_base_score",
            "base_ecu_score must be >= 0",
        )
    if epoch_type != "issuance_epoch":
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_epoch_context_invalid",
            "temporal decay is issuance-epoch scoped",
        )

    multiplier = compute_decay_multiplier(
        elapsed_issuance_epochs=elapsed_issuance_epochs,
        half_life_epochs=half_life_epochs,
        floor_multiplier=floor_multiplier,
    )
    return _quantize_twelve_places(base * multiplier)
