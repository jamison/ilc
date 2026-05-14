"""Phase 1349 default-off CDL-054 validator reward-pool routing runtime."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Any

from .epoch_emission_runtime import ILC_QUANTUM, ISSUANCE_EPOCH_DURATION, VALIDATION_EPOCH_SECONDS
from .treasury_governance_runtime import (
    BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET,
    BURN_FLOOR_FRACTION,
    CDL_047_TREASURY_GOVERNANCE_RUNTIME_TOKEN,
    PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN,
    TREASURY_GOVERNANCE_RUNTIME_VERSION,
    VELOCITY_ALERT_FLOOR,
    build_treasury_governance_quote,
)


VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_VERSION = (
    "validator_reward_pool_routing_runtime_1349.v0.1"
)
CDL_054_DEPENDENCY = (
    "cdl_054_validator_economic_incentive_framework_ratified_phase_491.v0.1"
)
CDL_054_VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_TOKEN = (
    "cdl_054_validator_reward_pool_routing_runtime_phase_1349.v0.1"
)
CDL_047_TREASURY_DEPENDENCY_TOKEN = "cdl_047_treasury_dependency_phase_1349"
VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN = (
    "validator_reward_distribution_not_activated_phase_1349"
)
PRODUCTION_VALIDATOR_REWARD_DISTRIBUTION_ACTIVATION_TOKEN = (
    "phase_1366_soft_rc_eligible_true_value_path_activation_required"
)
NO_DIRECT_VALIDATOR_REWARD_STUB_FOUND_TOKEN = (
    "no_direct_validator_reward_stub_found_phase_1349"
)

EXPECTED_CDL_047_TREASURY_RUNTIME_TOKEN = (
    "cdl_047_treasury_governance_runtime_phase_1348.v0.1"
)
VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN = Decimal("0.02")
VALIDATOR_REWARD_POOL_LABEL = "validator_reward_pool"
WRITE_FEE_BURN_POOL_LABEL = "write_fee_burn_pool"


@dataclass(frozen=True)
class EpochValidatorRewardPoolRoutingQuote:
    runtime_version: str
    cdl_054_dependency: str
    cdl_047_treasury_dependency_token: str
    cdl_047_treasury_runtime_token: str
    cdl_047_treasury_runtime_version: str
    issuance_epoch: int
    issuance_epoch_duration: str
    validation_epoch_seconds: int
    write_fee_burn_pool_ilc: Decimal
    validator_reward_fraction_of_write_fee_burn: Decimal
    validator_reward_pool_ilc: Decimal
    validator_reward_pool_label: str
    write_fee_burn_pool_label: str
    treasury_epoch_budget_ilc: Decimal
    treasury_bounty_cap_fraction: Decimal
    treasury_bounty_cap_ilc: Decimal
    treasury_burn_floor_fraction: Decimal
    treasury_burn_floor_ilc: Decimal
    treasury_planned_burn_ilc: Decimal
    treasury_velocity_alert_floor: Decimal
    observed_velocity: Decimal
    treasury_velocity_alert_triggered: bool
    treasury_remaining_budget_ilc: Decimal
    treasury_decision_token: str
    production_validator_reward_distribution_activated: bool
    decision_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "cdl_047_treasury_dependency_token": self.cdl_047_treasury_dependency_token,
            "cdl_047_treasury_runtime_token": self.cdl_047_treasury_runtime_token,
            "cdl_047_treasury_runtime_version": self.cdl_047_treasury_runtime_version,
            "cdl_054_dependency": self.cdl_054_dependency,
            "decision_token": self.decision_token,
            "issuance_epoch": self.issuance_epoch,
            "issuance_epoch_duration": self.issuance_epoch_duration,
            "observed_velocity": _decimal_to_string(self.observed_velocity),
            "production_validator_reward_distribution_activated": (
                self.production_validator_reward_distribution_activated
            ),
            "runtime_version": self.runtime_version,
            "treasury_bounty_cap_fraction": _decimal_to_string(
                self.treasury_bounty_cap_fraction
            ),
            "treasury_bounty_cap_ilc": _decimal_to_string(self.treasury_bounty_cap_ilc),
            "treasury_burn_floor_fraction": _decimal_to_string(
                self.treasury_burn_floor_fraction
            ),
            "treasury_burn_floor_ilc": _decimal_to_string(self.treasury_burn_floor_ilc),
            "treasury_decision_token": self.treasury_decision_token,
            "treasury_epoch_budget_ilc": _decimal_to_string(self.treasury_epoch_budget_ilc),
            "treasury_planned_burn_ilc": _decimal_to_string(self.treasury_planned_burn_ilc),
            "treasury_remaining_budget_ilc": _decimal_to_string(
                self.treasury_remaining_budget_ilc
            ),
            "treasury_velocity_alert_floor": _decimal_to_string(
                self.treasury_velocity_alert_floor
            ),
            "treasury_velocity_alert_triggered": self.treasury_velocity_alert_triggered,
            "validation_epoch_seconds": self.validation_epoch_seconds,
            "validator_reward_fraction_of_write_fee_burn": _decimal_to_string(
                self.validator_reward_fraction_of_write_fee_burn
            ),
            "validator_reward_pool_ilc": _decimal_to_string(self.validator_reward_pool_ilc),
            "validator_reward_pool_label": self.validator_reward_pool_label,
            "write_fee_burn_pool_ilc": _decimal_to_string(self.write_fee_burn_pool_ilc),
            "write_fee_burn_pool_label": self.write_fee_burn_pool_label,
        }


def require_cdl_047_treasury_dependency() -> None:
    if CDL_047_TREASURY_GOVERNANCE_RUNTIME_TOKEN != EXPECTED_CDL_047_TREASURY_RUNTIME_TOKEN:
        raise ValueError("cdl_047_treasury_dependency_token_mismatch_phase_1349")


def _require_epoch_sequence(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("validator_reward_issuance_epoch_must_be_non_negative_int")
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


def require_cdl_054_validator_reward_fraction(
    validator_reward_fraction: Decimal | int | str = VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN,
) -> Decimal:
    fraction = _require_decimal_amount(
        validator_reward_fraction,
        "validator_reward_fraction",
    )
    if fraction > Decimal("1"):
        raise ValueError("validator_reward_fraction_must_be_unit_interval")
    if fraction != VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN:
        raise ValueError("validator_reward_fraction_must_equal_cdl_054_sim_010_0_02")
    return fraction


def build_validator_reward_pool_routing_quote(
    issuance_epoch: int,
    write_fee_burn_pool_ilc: Decimal | int | str,
    treasury_epoch_budget_ilc: Decimal | int | str,
    treasury_planned_burn_ilc: Decimal | int | str,
    observed_velocity: Decimal | int | str,
    *,
    validator_reward_fraction: Decimal | int | str = VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN,
) -> EpochValidatorRewardPoolRoutingQuote:
    require_cdl_047_treasury_dependency()
    epoch = _require_epoch_sequence(issuance_epoch)
    write_fee_burn_pool = _quantize_ilc(
        _require_decimal_amount(write_fee_burn_pool_ilc, "write_fee_burn_pool_ilc")
    )
    treasury_epoch_budget = _quantize_ilc(
        _require_decimal_amount(treasury_epoch_budget_ilc, "treasury_epoch_budget_ilc")
    )
    treasury_planned_burn = _quantize_ilc(
        _require_decimal_amount(treasury_planned_burn_ilc, "treasury_planned_burn_ilc")
    )
    fraction = require_cdl_054_validator_reward_fraction(validator_reward_fraction)
    validator_reward_pool = _quantize_ilc(write_fee_burn_pool * fraction)

    treasury_quote = build_treasury_governance_quote(
        issuance_epoch=epoch,
        epoch_budget_ilc=treasury_epoch_budget,
        requested_bounty_ilc=validator_reward_pool,
        planned_burn_ilc=treasury_planned_burn,
        observed_velocity=observed_velocity,
    )

    return EpochValidatorRewardPoolRoutingQuote(
        runtime_version=VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_VERSION,
        cdl_054_dependency=CDL_054_DEPENDENCY,
        cdl_047_treasury_dependency_token=CDL_047_TREASURY_DEPENDENCY_TOKEN,
        cdl_047_treasury_runtime_token=CDL_047_TREASURY_GOVERNANCE_RUNTIME_TOKEN,
        cdl_047_treasury_runtime_version=TREASURY_GOVERNANCE_RUNTIME_VERSION,
        issuance_epoch=epoch,
        issuance_epoch_duration=ISSUANCE_EPOCH_DURATION,
        validation_epoch_seconds=VALIDATION_EPOCH_SECONDS,
        write_fee_burn_pool_ilc=write_fee_burn_pool,
        validator_reward_fraction_of_write_fee_burn=fraction,
        validator_reward_pool_ilc=validator_reward_pool,
        validator_reward_pool_label=VALIDATOR_REWARD_POOL_LABEL,
        write_fee_burn_pool_label=WRITE_FEE_BURN_POOL_LABEL,
        treasury_epoch_budget_ilc=treasury_quote.epoch_budget_ilc,
        treasury_bounty_cap_fraction=BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET,
        treasury_bounty_cap_ilc=treasury_quote.bounty_cap_ilc,
        treasury_burn_floor_fraction=BURN_FLOOR_FRACTION,
        treasury_burn_floor_ilc=treasury_quote.burn_floor_ilc,
        treasury_planned_burn_ilc=treasury_quote.planned_burn_ilc,
        treasury_velocity_alert_floor=VELOCITY_ALERT_FLOOR,
        observed_velocity=treasury_quote.observed_velocity,
        treasury_velocity_alert_triggered=treasury_quote.velocity_alert_triggered,
        treasury_remaining_budget_ilc=treasury_quote.treasury_remaining_budget_ilc,
        treasury_decision_token=treasury_quote.decision_token,
        production_validator_reward_distribution_activated=False,
        decision_token=VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    )


def require_production_validator_reward_distribution_activation(
    activation_token: str | None = None,
) -> None:
    if activation_token != PRODUCTION_VALIDATOR_REWARD_DISTRIBUTION_ACTIVATION_TOKEN:
        raise ValueError(VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN)
    raise ValueError("production_validator_reward_distribution_activation_not_implemented_phase_1349")


require_cdl_047_treasury_dependency()


__all__ = [
    "CDL_047_TREASURY_DEPENDENCY_TOKEN",
    "CDL_054_DEPENDENCY",
    "CDL_054_VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_TOKEN",
    "EXPECTED_CDL_047_TREASURY_RUNTIME_TOKEN",
    "NO_DIRECT_VALIDATOR_REWARD_STUB_FOUND_TOKEN",
    "PRODUCTION_VALIDATOR_REWARD_DISTRIBUTION_ACTIVATION_TOKEN",
    "VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN",
    "VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN",
    "VALIDATOR_REWARD_POOL_LABEL",
    "VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_VERSION",
    "WRITE_FEE_BURN_POOL_LABEL",
    "EpochValidatorRewardPoolRoutingQuote",
    "build_validator_reward_pool_routing_quote",
    "require_cdl_047_treasury_dependency",
    "require_cdl_054_validator_reward_fraction",
    "require_production_validator_reward_distribution_activation",
]
