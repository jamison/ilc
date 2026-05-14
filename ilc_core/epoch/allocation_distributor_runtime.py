"""Phase 1347 default-off CDL-029 allocation distributor quote runtime."""

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
from .fee_burn_split_runtime import FEE_BURN_SPLIT_RUNTIME_VERSION


ALLOCATION_DISTRIBUTOR_RUNTIME_VERSION = "allocation_distributor_runtime_1347.v0.1"
CDL_029_DEPENDENCY = "cdl_029_allocation_split_ratified_phase_272.v0.1"
PHASE_1345_EMISSION_RUNTIME_DEPENDENCY = EPOCH_EMISSION_RUNTIME_VERSION
PHASE_1346_FEE_BURN_RUNTIME_DEPENDENCY = FEE_BURN_SPLIT_RUNTIME_VERSION
CDL_029_ALLOCATION_DISTRIBUTOR_RUNTIME_TOKEN = (
    "cdl_029_allocation_distributor_runtime_phase_1347.v0.1"
)
ALLOCATION_80_15_5_ROUTING_TOKEN = "allocation_80_15_5_routing_phase_1347"
PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_TOKEN = (
    "production_distribution_not_activated_phase_1347"
)
PRODUCTION_ALLOCATION_DISTRIBUTION_ACTIVATION_TOKEN = (
    "phase_1366_soft_rc_eligible_true_value_path_activation_required"
)
NO_DIRECT_ALLOCATION_STUB_FOUND_TOKEN = "no_direct_allocation_stub_found_phase_1347"

PERFORMER_ALLOCATION_FRACTION = Decimal("0.80")
AUDITOR_ALLOCATION_FRACTION = Decimal("0.15")
GENESIS_OVERHEAD_ALLOCATION_FRACTION = Decimal("0.05")
THETA_HARD_CONTINUITY_FRACTION = Decimal("0.05")
ALLOCATION_FRACTION_TOTAL = Decimal("1.00")

PERFORMER_REWARD_POOL_LABEL = "performer_reward_pool"
AUDITOR_REWARD_POOL_LABEL = "auditor_reward_pool"
GENESIS_OVERHEAD_POOL_LABEL = "genesis_overhead_pool"


@dataclass(frozen=True)
class EpochAllocationDistributionQuote:
    runtime_version: str
    cdl_029_dependency: str
    issuance_epoch: int
    issuance_epoch_duration: str
    validation_epoch_seconds: int
    total_epoch_allocation_ilc: Decimal
    performer_fraction: Decimal
    auditor_fraction: Decimal
    genesis_overhead_fraction: Decimal
    theta_hard_continuity_fraction: Decimal
    performer_reward_pool_ilc: Decimal
    auditor_reward_pool_ilc: Decimal
    genesis_overhead_pool_ilc: Decimal
    rounding_residual_to_genesis_overhead_ilc: Decimal
    performer_reward_pool_label: str
    auditor_reward_pool_label: str
    genesis_overhead_pool_label: str
    production_allocation_distribution_activated: bool
    decision_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "auditor_fraction": _decimal_to_string(self.auditor_fraction),
            "auditor_reward_pool_ilc": _decimal_to_string(self.auditor_reward_pool_ilc),
            "auditor_reward_pool_label": self.auditor_reward_pool_label,
            "cdl_029_dependency": self.cdl_029_dependency,
            "decision_token": self.decision_token,
            "genesis_overhead_fraction": _decimal_to_string(self.genesis_overhead_fraction),
            "genesis_overhead_pool_ilc": _decimal_to_string(self.genesis_overhead_pool_ilc),
            "genesis_overhead_pool_label": self.genesis_overhead_pool_label,
            "issuance_epoch": self.issuance_epoch,
            "issuance_epoch_duration": self.issuance_epoch_duration,
            "performer_fraction": _decimal_to_string(self.performer_fraction),
            "performer_reward_pool_ilc": _decimal_to_string(self.performer_reward_pool_ilc),
            "performer_reward_pool_label": self.performer_reward_pool_label,
            "production_allocation_distribution_activated": (
                self.production_allocation_distribution_activated
            ),
            "rounding_residual_to_genesis_overhead_ilc": _decimal_to_string(
                self.rounding_residual_to_genesis_overhead_ilc
            ),
            "runtime_version": self.runtime_version,
            "theta_hard_continuity_fraction": _decimal_to_string(
                self.theta_hard_continuity_fraction
            ),
            "total_epoch_allocation_ilc": _decimal_to_string(self.total_epoch_allocation_ilc),
            "validation_epoch_seconds": self.validation_epoch_seconds,
        }


def _require_epoch_sequence(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("allocation_issuance_epoch_must_be_non_negative_int")
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
    return amount


def _quantize_ilc(value: Decimal) -> Decimal:
    return value.quantize(ILC_QUANTUM, rounding=ROUND_DOWN)


def _decimal_to_string(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return format(normalized, "f")
    return format(normalized, "f")


def require_cdl_029_allocation_fractions(
    performer_fraction: Decimal | int | str = PERFORMER_ALLOCATION_FRACTION,
    auditor_fraction: Decimal | int | str = AUDITOR_ALLOCATION_FRACTION,
    genesis_overhead_fraction: Decimal | int | str = GENESIS_OVERHEAD_ALLOCATION_FRACTION,
) -> tuple[Decimal, Decimal, Decimal]:
    performer = _require_decimal_amount(performer_fraction, "performer_fraction")
    auditor = _require_decimal_amount(auditor_fraction, "auditor_fraction")
    genesis_overhead = _require_decimal_amount(
        genesis_overhead_fraction,
        "genesis_overhead_fraction",
    )
    if performer + auditor + genesis_overhead != ALLOCATION_FRACTION_TOTAL:
        raise ValueError("allocation_fractions_must_sum_to_one")
    if (
        performer != PERFORMER_ALLOCATION_FRACTION
        or auditor != AUDITOR_ALLOCATION_FRACTION
        or genesis_overhead != GENESIS_OVERHEAD_ALLOCATION_FRACTION
    ):
        raise ValueError("allocation_fractions_must_equal_cdl_029_80_15_5")
    return performer, auditor, genesis_overhead


def build_allocation_distribution_quote(
    issuance_epoch: int,
    total_epoch_allocation_ilc: Decimal | int | str,
    *,
    performer_fraction: Decimal | int | str = PERFORMER_ALLOCATION_FRACTION,
    auditor_fraction: Decimal | int | str = AUDITOR_ALLOCATION_FRACTION,
    genesis_overhead_fraction: Decimal | int | str = GENESIS_OVERHEAD_ALLOCATION_FRACTION,
) -> EpochAllocationDistributionQuote:
    epoch = _require_epoch_sequence(issuance_epoch)
    total_allocation = _quantize_ilc(
        _require_decimal_amount(total_epoch_allocation_ilc, "total_epoch_allocation_ilc")
    )
    performer, auditor, genesis_overhead = require_cdl_029_allocation_fractions(
        performer_fraction,
        auditor_fraction,
        genesis_overhead_fraction,
    )

    performer_pool = _quantize_ilc(total_allocation * performer)
    auditor_pool = _quantize_ilc(total_allocation * auditor)
    genesis_overhead_base = _quantize_ilc(total_allocation * genesis_overhead)
    rounding_residual = total_allocation - performer_pool - auditor_pool - genesis_overhead_base
    genesis_overhead_pool = genesis_overhead_base + rounding_residual

    return EpochAllocationDistributionQuote(
        runtime_version=ALLOCATION_DISTRIBUTOR_RUNTIME_VERSION,
        cdl_029_dependency=CDL_029_DEPENDENCY,
        issuance_epoch=epoch,
        issuance_epoch_duration=ISSUANCE_EPOCH_DURATION,
        validation_epoch_seconds=VALIDATION_EPOCH_SECONDS,
        total_epoch_allocation_ilc=total_allocation,
        performer_fraction=performer,
        auditor_fraction=auditor,
        genesis_overhead_fraction=genesis_overhead,
        theta_hard_continuity_fraction=THETA_HARD_CONTINUITY_FRACTION,
        performer_reward_pool_ilc=performer_pool,
        auditor_reward_pool_ilc=auditor_pool,
        genesis_overhead_pool_ilc=genesis_overhead_pool,
        rounding_residual_to_genesis_overhead_ilc=rounding_residual,
        performer_reward_pool_label=PERFORMER_REWARD_POOL_LABEL,
        auditor_reward_pool_label=AUDITOR_REWARD_POOL_LABEL,
        genesis_overhead_pool_label=GENESIS_OVERHEAD_POOL_LABEL,
        production_allocation_distribution_activated=False,
        decision_token=PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    )


def require_production_allocation_distribution_activation(
    activation_token: str | None = None,
) -> None:
    if activation_token != PRODUCTION_ALLOCATION_DISTRIBUTION_ACTIVATION_TOKEN:
        raise ValueError(PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_TOKEN)
    raise ValueError("production_allocation_distribution_activation_not_implemented_phase_1347")


__all__ = [
    "ALLOCATION_80_15_5_ROUTING_TOKEN",
    "ALLOCATION_DISTRIBUTOR_RUNTIME_VERSION",
    "ALLOCATION_FRACTION_TOTAL",
    "AUDITOR_ALLOCATION_FRACTION",
    "AUDITOR_REWARD_POOL_LABEL",
    "CDL_029_ALLOCATION_DISTRIBUTOR_RUNTIME_TOKEN",
    "CDL_029_DEPENDENCY",
    "GENESIS_OVERHEAD_ALLOCATION_FRACTION",
    "GENESIS_OVERHEAD_POOL_LABEL",
    "NO_DIRECT_ALLOCATION_STUB_FOUND_TOKEN",
    "PERFORMER_ALLOCATION_FRACTION",
    "PERFORMER_REWARD_POOL_LABEL",
    "PHASE_1345_EMISSION_RUNTIME_DEPENDENCY",
    "PHASE_1346_FEE_BURN_RUNTIME_DEPENDENCY",
    "PRODUCTION_ALLOCATION_DISTRIBUTION_ACTIVATION_TOKEN",
    "PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_TOKEN",
    "THETA_HARD_CONTINUITY_FRACTION",
    "EpochAllocationDistributionQuote",
    "build_allocation_distribution_quote",
    "require_cdl_029_allocation_fractions",
    "require_production_allocation_distribution_activation",
]
