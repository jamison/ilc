# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 1346 default-off CDL-028 fee-burn split quote runtime."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Any

from .epoch_emission_runtime import (
    EPOCH_EMISSION_RUNTIME_VERSION,
    ILC_QUANTUM,
    ISSUANCE_EPOCH_DURATION,
    VALIDATION_EPOCH_SECONDS,
)


FEE_BURN_SPLIT_RUNTIME_VERSION = "fee_burn_split_runtime_1346.v0.1"
CDL_028_DEPENDENCY = "cdl_028_fee_burn_split_ratified_phase_274.v0.1"
PHASE_1345_EMISSION_RUNTIME_DEPENDENCY = EPOCH_EMISSION_RUNTIME_VERSION
CDL_028_FEE_BURN_SPLIT_RUNTIME_TOKEN = "cdl_028_fee_burn_split_runtime_phase_1346.v0.1"
FEE_BURN_10_PERCENT_GENESIS_POOL_TOKEN = "fee_burn_10_percent_genesis_pool_phase_1346"
PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN = "fee_burn_not_activated_phase_1346"
NO_DIRECT_FEE_BURN_STUB_FOUND_TOKEN = "no_direct_fee_burn_stub_found_phase_1346"
PRODUCTION_FEE_BURN_ACTIVATION_TOKEN = (
    "phase_1366_soft_rc_eligible_true_value_path_activation_required"
)

FEE_BURN_RATIO = Decimal("0.10")
GENESIS_BURN_POOL_LABEL = "genesis_burn_pool"
POST_CDL_028_REMAINING_FEE_POOL_LABEL = "post_cdl_028_remaining_fee_pool"
MAX_ILC_QUANTIZE_ADJUSTED_EXPONENT = 18
INVALID_AMOUNT_MAGNITUDE_TOKEN = "invalid_amount_magnitude"


@dataclass(frozen=True)
class EpochFeeBurnSplitQuote:
    runtime_version: str
    cdl_028_dependency: str
    issuance_epoch: int
    issuance_epoch_duration: str
    validation_epoch_seconds: int
    total_epoch_fees_ilc: Decimal
    fee_burn_ratio: Decimal
    genesis_burn_pool_ilc: Decimal
    remaining_fee_pool_ilc: Decimal
    genesis_burn_pool_label: str
    remaining_fee_pool_label: str
    production_fee_burn_activated: bool
    decision_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "cdl_028_dependency": self.cdl_028_dependency,
            "decision_token": self.decision_token,
            "fee_burn_ratio": _decimal_to_string(self.fee_burn_ratio),
            "genesis_burn_pool_ilc": _decimal_to_string(self.genesis_burn_pool_ilc),
            "genesis_burn_pool_label": self.genesis_burn_pool_label,
            "issuance_epoch": self.issuance_epoch,
            "issuance_epoch_duration": self.issuance_epoch_duration,
            "production_fee_burn_activated": self.production_fee_burn_activated,
            "remaining_fee_pool_ilc": _decimal_to_string(self.remaining_fee_pool_ilc),
            "remaining_fee_pool_label": self.remaining_fee_pool_label,
            "runtime_version": self.runtime_version,
            "total_epoch_fees_ilc": _decimal_to_string(self.total_epoch_fees_ilc),
            "validation_epoch_seconds": self.validation_epoch_seconds,
        }


def _require_epoch_sequence(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("fee_issuance_epoch_must_be_non_negative_int")
    return value


def _require_decimal_amount(value: Decimal | int | str, field_name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field_name}_must_be_exact_decimal")
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name}_must_be_exact_decimal") from exc
    if not amount.is_finite():
        raise ValueError(f"{field_name}_must_be_finite")
    if amount < Decimal("0"):
        raise ValueError(f"{field_name}_must_be_non_negative")
    if amount.adjusted() > MAX_ILC_QUANTIZE_ADJUSTED_EXPONENT:
        raise ValueError(INVALID_AMOUNT_MAGNITUDE_TOKEN)
    return amount


def _quantize_ilc(value: Decimal) -> Decimal:
    if value.adjusted() > MAX_ILC_QUANTIZE_ADJUSTED_EXPONENT:
        raise ValueError(INVALID_AMOUNT_MAGNITUDE_TOKEN)
    return value.quantize(ILC_QUANTUM, rounding=ROUND_DOWN)


def _decimal_to_string(value: Decimal) -> str:
    return format(value.normalize(), "f")


def require_cdl_028_fee_burn_ratio(value: Decimal | int | str = FEE_BURN_RATIO) -> Decimal:
    ratio = _require_decimal_amount(value, "fee_burn_ratio")
    if ratio != FEE_BURN_RATIO:
        raise ValueError("fee_burn_ratio_must_equal_cdl_028")
    return ratio


def build_fee_burn_split_quote(
    issuance_epoch: int,
    total_epoch_fees_ilc: Decimal | int | str,
    *,
    fee_burn_ratio: Decimal | int | str = FEE_BURN_RATIO,
) -> EpochFeeBurnSplitQuote:
    epoch = _require_epoch_sequence(issuance_epoch)
    fees = _quantize_ilc(_require_decimal_amount(total_epoch_fees_ilc, "total_epoch_fees_ilc"))
    ratio = require_cdl_028_fee_burn_ratio(fee_burn_ratio)
    genesis_burn_pool = _quantize_ilc(fees * ratio)
    remaining_fee_pool = fees - genesis_burn_pool

    return EpochFeeBurnSplitQuote(
        runtime_version=FEE_BURN_SPLIT_RUNTIME_VERSION,
        cdl_028_dependency=CDL_028_DEPENDENCY,
        issuance_epoch=epoch,
        issuance_epoch_duration=ISSUANCE_EPOCH_DURATION,
        validation_epoch_seconds=VALIDATION_EPOCH_SECONDS,
        total_epoch_fees_ilc=fees,
        fee_burn_ratio=ratio,
        genesis_burn_pool_ilc=genesis_burn_pool,
        remaining_fee_pool_ilc=remaining_fee_pool,
        genesis_burn_pool_label=GENESIS_BURN_POOL_LABEL,
        remaining_fee_pool_label=POST_CDL_028_REMAINING_FEE_POOL_LABEL,
        production_fee_burn_activated=False,
        decision_token=PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN,
    )


def require_production_fee_burn_activation(activation_token: str | None = None) -> None:
    if activation_token != PRODUCTION_FEE_BURN_ACTIVATION_TOKEN:
        raise ValueError(PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN)
    raise ValueError("production_fee_burn_activation_not_implemented_phase_1346")


__all__ = [
    "CDL_028_DEPENDENCY",
    "CDL_028_FEE_BURN_SPLIT_RUNTIME_TOKEN",
    "FEE_BURN_10_PERCENT_GENESIS_POOL_TOKEN",
    "FEE_BURN_RATIO",
    "FEE_BURN_SPLIT_RUNTIME_VERSION",
    "GENESIS_BURN_POOL_LABEL",
    "NO_DIRECT_FEE_BURN_STUB_FOUND_TOKEN",
    "POST_CDL_028_REMAINING_FEE_POOL_LABEL",
    "PHASE_1345_EMISSION_RUNTIME_DEPENDENCY",
    "PRODUCTION_FEE_BURN_ACTIVATION_TOKEN",
    "PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN",
    "EpochFeeBurnSplitQuote",
    "build_fee_burn_split_quote",
    "require_cdl_028_fee_burn_ratio",
    "require_production_fee_burn_activation",
]
