# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 1351 default-off CDL-030 ECU price clamp quote runtime."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Any

from .epoch_emission_runtime import (
    CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN,
    HALVING_INTERVAL_ISSUANCE_EPOCHS,
    ILC_QUANTUM,
    ISSUANCE_EPOCH_DURATION,
    VALIDATION_EPOCH_SECONDS,
)


ECU_PRICE_CLAMP_RUNTIME_VERSION = "ecu_price_clamp_runtime_1351.v0.1"
CDL_030_DEPENDENCY = "cdl_030_ecu_price_clamp_ratified_phase_277.v0.1"
CDL_030_ECU_PRICE_CLAMP_RUNTIME_TOKEN = (
    "cdl_030_ecu_price_clamp_runtime_phase_1351.v0.1"
)
P_MIN_P_MAX_BOUNDS_CDL_027_DERIVED_TOKEN = (
    "p_min_p_max_bounds_cdl_027_derived_phase_1351"
)
LIVE_PRICE_ADJUSTMENT_NOT_ACTIVATED_TOKEN = (
    "live_price_adjustment_not_activated_phase_1351"
)
PRODUCTION_ECU_PRICE_CLAMP_ACTIVATION_TOKEN = (
    "phase_1366_soft_rc_eligible_true_value_path_activation_required"
)
NO_DIRECT_PRICE_CLAMP_STUB_FOUND_TOKEN = "no_direct_price_clamp_stub_found_phase_1351"

EXPECTED_CDL_027_RUNTIME_TOKEN = "cdl_027_epoch_length_runtime_phase_1345.v0.1"
EXPECTED_CDL_027_HALVING_INTERVAL_ISSUANCE_EPOCHS = 48
EXPECTED_CDL_027_ISSUANCE_EPOCH_DURATION = "1_month"

P_MIN = Decimal("0.75")
P_MAX = Decimal("1.30")
PRICE_CLAMP_WIDTH = P_MAX - P_MIN
if PRICE_CLAMP_WIDTH != Decimal("0.55"):
    raise RuntimeError("price_clamp_width_policy_mismatch_phase_1440")
FINDING_3_PRICE_CLAMP_WIDTH_DERIVED_RESOLVED_TOKEN = (
    "finding_3_price_clamp_width_derived_resolved_phase_1440"
)
MAX_ILC_QUANTIZE_ADJUSTED_EXPONENT = 18
INVALID_AMOUNT_MAGNITUDE_TOKEN = "invalid_amount_magnitude"


@dataclass(frozen=True)
class EcuPriceClampQuote:
    runtime_version: str
    cdl_030_dependency: str
    cdl_027_runtime_token: str
    derivation_token: str
    issuance_epoch: int
    issuance_epoch_duration: str
    validation_epoch_seconds: int
    halving_interval_issuance_epochs: int
    proposed_price: Decimal
    p_min: Decimal
    p_max: Decimal
    clamp_width: Decimal
    clamped_price: Decimal
    clamp_applied: bool
    clamp_direction: str
    live_price_adjustment_activated: bool
    decision_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "cdl_027_runtime_token": self.cdl_027_runtime_token,
            "cdl_030_dependency": self.cdl_030_dependency,
            "clamp_applied": self.clamp_applied,
            "clamp_direction": self.clamp_direction,
            "clamp_width": _decimal_to_string(self.clamp_width),
            "clamped_price": _decimal_to_string(self.clamped_price),
            "decision_token": self.decision_token,
            "derivation_token": self.derivation_token,
            "halving_interval_issuance_epochs": self.halving_interval_issuance_epochs,
            "issuance_epoch": self.issuance_epoch,
            "issuance_epoch_duration": self.issuance_epoch_duration,
            "live_price_adjustment_activated": self.live_price_adjustment_activated,
            "p_max": _decimal_to_string(self.p_max),
            "p_min": _decimal_to_string(self.p_min),
            "proposed_price": _decimal_to_string(self.proposed_price),
            "runtime_version": self.runtime_version,
            "validation_epoch_seconds": self.validation_epoch_seconds,
        }


def _require_epoch_sequence(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("ecu_price_clamp_issuance_epoch_must_be_non_negative_int")
    return value


def _require_decimal_amount(value: Decimal | int | str, field_name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field_name}_must_be_exact_decimal")
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name}_must_be_exact_decimal") from exc
    if not amount.is_finite():
        raise ValueError("invalid_amount_non_finite")
    if amount <= Decimal("0"):
        raise ValueError(f"{field_name}_must_be_positive")
    if amount.adjusted() > MAX_ILC_QUANTIZE_ADJUSTED_EXPONENT:
        raise ValueError(INVALID_AMOUNT_MAGNITUDE_TOKEN)
    return amount


def _quantize_price(value: Decimal) -> Decimal:
    if value.adjusted() > MAX_ILC_QUANTIZE_ADJUSTED_EXPONENT:
        raise ValueError(INVALID_AMOUNT_MAGNITUDE_TOKEN)
    return value.quantize(ILC_QUANTUM, rounding=ROUND_DOWN)


def _decimal_to_string(value: Decimal) -> str:
    return format(value.normalize(), "f")


def require_cdl_027_schedule_dependency(
    cdl_027_runtime_token: str = CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN,
    halving_interval_issuance_epochs: int = HALVING_INTERVAL_ISSUANCE_EPOCHS,
    issuance_epoch_duration: str = ISSUANCE_EPOCH_DURATION,
) -> None:
    if cdl_027_runtime_token != EXPECTED_CDL_027_RUNTIME_TOKEN:
        raise ValueError("cdl_027_runtime_token_mismatch_phase_1351")
    if (
        type(halving_interval_issuance_epochs) is not int
        or halving_interval_issuance_epochs
        != EXPECTED_CDL_027_HALVING_INTERVAL_ISSUANCE_EPOCHS
    ):
        raise ValueError("cdl_027_halving_interval_mismatch_phase_1351")
    if issuance_epoch_duration != EXPECTED_CDL_027_ISSUANCE_EPOCH_DURATION:
        raise ValueError("cdl_027_epoch_duration_mismatch_phase_1351")


def require_cdl_030_price_bounds(
    p_min: Decimal | int | str = P_MIN,
    p_max: Decimal | int | str = P_MAX,
) -> tuple[Decimal, Decimal]:
    minimum = _require_decimal_amount(p_min, "p_min")
    maximum = _require_decimal_amount(p_max, "p_max")
    if minimum >= maximum:
        raise ValueError("p_min_must_be_less_than_p_max_phase_1351")
    if minimum != P_MIN:
        raise ValueError("p_min_must_equal_cdl_030_0_75")
    if maximum != P_MAX:
        raise ValueError("p_max_must_equal_cdl_030_1_30")
    return minimum, maximum


def derive_cdl_030_price_bounds_from_cdl_027_schedule() -> tuple[Decimal, Decimal]:
    """Return Phase-277 CDL-030 bounds after checking the CDL-027 schedule anchor."""

    require_cdl_027_schedule_dependency()
    return require_cdl_030_price_bounds()


def build_ecu_price_clamp_quote(
    issuance_epoch: int,
    proposed_price: Decimal | int | str,
    *,
    p_min: Decimal | int | str = P_MIN,
    p_max: Decimal | int | str = P_MAX,
) -> EcuPriceClampQuote:
    require_cdl_027_schedule_dependency()
    epoch = _require_epoch_sequence(issuance_epoch)
    minimum, maximum = require_cdl_030_price_bounds(p_min, p_max)
    proposed = _quantize_price(_require_decimal_amount(proposed_price, "proposed_price"))

    if proposed < minimum:
        clamped = minimum
        direction = "floor"
    elif proposed > maximum:
        clamped = maximum
        direction = "ceiling"
    else:
        clamped = proposed
        direction = "none"

    return EcuPriceClampQuote(
        runtime_version=ECU_PRICE_CLAMP_RUNTIME_VERSION,
        cdl_030_dependency=CDL_030_DEPENDENCY,
        cdl_027_runtime_token=CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN,
        derivation_token=P_MIN_P_MAX_BOUNDS_CDL_027_DERIVED_TOKEN,
        issuance_epoch=epoch,
        issuance_epoch_duration=ISSUANCE_EPOCH_DURATION,
        validation_epoch_seconds=VALIDATION_EPOCH_SECONDS,
        halving_interval_issuance_epochs=HALVING_INTERVAL_ISSUANCE_EPOCHS,
        proposed_price=proposed,
        p_min=minimum,
        p_max=maximum,
        clamp_width=PRICE_CLAMP_WIDTH,
        clamped_price=clamped,
        clamp_applied=direction != "none",
        clamp_direction=direction,
        live_price_adjustment_activated=False,
        decision_token=LIVE_PRICE_ADJUSTMENT_NOT_ACTIVATED_TOKEN,
    )


def require_live_price_adjustment_activation(activation_token: str | None = None) -> None:
    if activation_token != PRODUCTION_ECU_PRICE_CLAMP_ACTIVATION_TOKEN:
        raise ValueError(LIVE_PRICE_ADJUSTMENT_NOT_ACTIVATED_TOKEN)
    raise ValueError("live_price_adjustment_activation_not_implemented_phase_1351")


require_cdl_027_schedule_dependency()


__all__ = [
    "CDL_030_DEPENDENCY",
    "CDL_030_ECU_PRICE_CLAMP_RUNTIME_TOKEN",
    "ECU_PRICE_CLAMP_RUNTIME_VERSION",
    "EXPECTED_CDL_027_HALVING_INTERVAL_ISSUANCE_EPOCHS",
    "EXPECTED_CDL_027_ISSUANCE_EPOCH_DURATION",
    "EXPECTED_CDL_027_RUNTIME_TOKEN",
    "EcuPriceClampQuote",
    "FINDING_3_PRICE_CLAMP_WIDTH_DERIVED_RESOLVED_TOKEN",
    "LIVE_PRICE_ADJUSTMENT_NOT_ACTIVATED_TOKEN",
    "NO_DIRECT_PRICE_CLAMP_STUB_FOUND_TOKEN",
    "P_MAX",
    "P_MIN",
    "PRICE_CLAMP_WIDTH",
    "PRODUCTION_ECU_PRICE_CLAMP_ACTIVATION_TOKEN",
    "P_MIN_P_MAX_BOUNDS_CDL_027_DERIVED_TOKEN",
    "build_ecu_price_clamp_quote",
    "derive_cdl_030_price_bounds_from_cdl_027_schedule",
    "require_cdl_027_schedule_dependency",
    "require_cdl_030_price_bounds",
    "require_live_price_adjustment_activation",
]
