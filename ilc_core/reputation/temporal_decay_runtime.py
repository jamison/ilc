"""CDL-V1 temporal decay runtime.

The runtime enforces issuance-epoch-scoped decay helpers using deterministic
math and tokenized validation failures.
"""

from __future__ import annotations

import math

CDL_V1_RUNTIME_VERSION = "cdl_v1_temporal_decay_runtime_388.v0.1"
CDL_V1_DEPENDENCY = "cdl_v1_temporal_decay_388.v0.1"


class TemporalDecayValidationError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def _require_numeric(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_invalid_numeric",
            f"{name} must be a numeric value",
        )
    number = float(value)
    if not math.isfinite(number):
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_invalid_numeric",
            f"{name} must be a finite numeric value",
        )
    return number


def compute_decay_multiplier(
    *,
    elapsed_issuance_epochs: float,
    half_life_epochs: float,
    floor_multiplier: float,
) -> float:
    """Compute exponential temporal-decay multiplier with floor enforcement."""

    elapsed = _require_numeric("elapsed_issuance_epochs", elapsed_issuance_epochs)
    half_life = _require_numeric("half_life_epochs", half_life_epochs)
    floor = _require_numeric("floor_multiplier", floor_multiplier)

    if elapsed < 0.0:
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_negative_elapsed",
            "elapsed_issuance_epochs must be >= 0",
        )
    if half_life <= 0.0:
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_half_life_non_positive",
            "half_life_epochs must be > 0",
        )
    if floor < 0.0 or floor > 1.0:
        raise TemporalDecayValidationError(
            "cdl_v1_temporal_decay_floor_out_of_range",
            "floor_multiplier must be in [0, 1]",
        )

    raw = math.exp(-math.log(2.0) * (elapsed / half_life))
    multiplier = max(floor, min(1.0, raw))
    return round(multiplier, 12)


def apply_temporal_decay(
    *,
    base_ecu_score: float,
    elapsed_issuance_epochs: float,
    half_life_epochs: float,
    floor_multiplier: float,
    epoch_type: str = "issuance_epoch",
) -> float:
    """Apply temporal decay to base score under issuance-epoch scope."""

    base = _require_numeric("base_ecu_score", base_ecu_score)

    if base < 0.0:
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
    return round(base * multiplier, 12)
