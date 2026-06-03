# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1348 default-off CDL-047 treasury governance quote runtime."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Any

from .allocation_distributor_runtime import ALLOCATION_DISTRIBUTOR_RUNTIME_VERSION
from .epoch_emission_runtime import (
    ILC_QUANTUM,
    ISSUANCE_EPOCH_DURATION,
    VALIDATION_EPOCH_SECONDS,
)


TREASURY_GOVERNANCE_RUNTIME_VERSION = "treasury_governance_runtime_1348.v0.1"
CDL_047_DEPENDENCY = "cdl_047_treasury_governance_ratified_phase_418.v0.1"
PHASE_1347_ALLOCATION_RUNTIME_DEPENDENCY = ALLOCATION_DISTRIBUTOR_RUNTIME_VERSION
CDL_047_TREASURY_GOVERNANCE_RUNTIME_TOKEN = (
    "cdl_047_treasury_governance_runtime_phase_1348.v0.1"
)
BOUNTY_CAP_0_15_B_E_RUNTIME_TOKEN = "bounty_cap_0_15_b_e_runtime_phase_1348"
BURN_FLOOR_0_05_RUNTIME_TOKEN = "burn_floor_0_05_runtime_phase_1348"
VELOCITY_ALERT_TRIGGER_RUNTIME_TOKEN = "velocity_alert_trigger_runtime_phase_1348"
VELOCITY_ALERT_FLOOR_0_91_RUNTIME_TOKEN = "velocity_alert_floor_0_91_runtime_phase_1348"
PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN = "treasury_not_activated_phase_1348"
PRODUCTION_TREASURY_ACTIVATION_TOKEN = (
    "phase_1366_soft_rc_eligible_true_value_path_activation_required"
)
NO_DIRECT_TREASURY_STUB_FOUND_TOKEN = "no_direct_treasury_stub_found_phase_1348"

BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET = Decimal("0.15")
BURN_FLOOR_FRACTION = Decimal("0.05")
VELOCITY_ALERT_FLOOR = Decimal("0.91")
TREASURY_FRACTION_TOTAL_LIMIT = Decimal("1.00")
MAX_ILC_QUANTIZE_ADJUSTED_EXPONENT = 18
INVALID_AMOUNT_MAGNITUDE_TOKEN = "invalid_amount_magnitude"


@dataclass(frozen=True)
class EpochTreasuryGovernanceQuote:
    runtime_version: str
    cdl_047_dependency: str
    issuance_epoch: int
    issuance_epoch_duration: str
    validation_epoch_seconds: int
    epoch_budget_ilc: Decimal
    bounty_cap_fraction_of_epoch_budget: Decimal
    bounty_cap_ilc: Decimal
    requested_bounty_ilc: Decimal
    burn_floor_fraction: Decimal
    burn_floor_ilc: Decimal
    planned_burn_ilc: Decimal
    velocity_alert_floor: Decimal
    observed_velocity: Decimal
    velocity_alert_triggered: bool
    treasury_remaining_budget_ilc: Decimal
    production_treasury_activated: bool
    decision_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "bounty_cap_fraction_of_epoch_budget": _decimal_to_string(
                self.bounty_cap_fraction_of_epoch_budget
            ),
            "bounty_cap_ilc": _decimal_to_string(self.bounty_cap_ilc),
            "burn_floor_fraction": _decimal_to_string(self.burn_floor_fraction),
            "burn_floor_ilc": _decimal_to_string(self.burn_floor_ilc),
            "cdl_047_dependency": self.cdl_047_dependency,
            "decision_token": self.decision_token,
            "epoch_budget_ilc": _decimal_to_string(self.epoch_budget_ilc),
            "issuance_epoch": self.issuance_epoch,
            "issuance_epoch_duration": self.issuance_epoch_duration,
            "observed_velocity": _decimal_to_string(self.observed_velocity),
            "planned_burn_ilc": _decimal_to_string(self.planned_burn_ilc),
            "production_treasury_activated": self.production_treasury_activated,
            "requested_bounty_ilc": _decimal_to_string(self.requested_bounty_ilc),
            "runtime_version": self.runtime_version,
            "treasury_remaining_budget_ilc": _decimal_to_string(
                self.treasury_remaining_budget_ilc
            ),
            "validation_epoch_seconds": self.validation_epoch_seconds,
            "velocity_alert_floor": _decimal_to_string(self.velocity_alert_floor),
            "velocity_alert_triggered": self.velocity_alert_triggered,
        }


def _require_epoch_sequence(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("treasury_issuance_epoch_must_be_non_negative_int")
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


def require_cdl_047_treasury_fractions(
    bounty_cap_fraction: Decimal | int | str = BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET,
    burn_floor_fraction: Decimal | int | str = BURN_FLOOR_FRACTION,
    velocity_alert_floor: Decimal | int | str = VELOCITY_ALERT_FLOOR,
) -> tuple[Decimal, Decimal, Decimal]:
    bounty_fraction = _require_decimal_amount(bounty_cap_fraction, "bounty_cap_fraction")
    burn_fraction = _require_decimal_amount(burn_floor_fraction, "burn_floor_fraction")
    velocity_floor = _require_decimal_amount(velocity_alert_floor, "velocity_alert_floor")
    if bounty_fraction != BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET:
        raise ValueError("bounty_cap_fraction_must_equal_cdl_047_0_15")
    if burn_fraction != BURN_FLOOR_FRACTION:
        raise ValueError("burn_floor_fraction_must_equal_cdl_047_0_05")
    if velocity_floor != VELOCITY_ALERT_FLOOR:
        raise ValueError("velocity_alert_floor_must_equal_cdl_047_0_91")
    if bounty_fraction + burn_fraction > TREASURY_FRACTION_TOTAL_LIMIT:
        raise ValueError("treasury_fractions_must_not_exceed_one")
    return bounty_fraction, burn_fraction, velocity_floor


def build_treasury_governance_quote(
    issuance_epoch: int,
    epoch_budget_ilc: Decimal | int | str,
    requested_bounty_ilc: Decimal | int | str,
    planned_burn_ilc: Decimal | int | str,
    observed_velocity: Decimal | int | str,
    *,
    bounty_cap_fraction: Decimal | int | str = BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET,
    burn_floor_fraction: Decimal | int | str = BURN_FLOOR_FRACTION,
    velocity_alert_floor: Decimal | int | str = VELOCITY_ALERT_FLOOR,
) -> EpochTreasuryGovernanceQuote:
    epoch = _require_epoch_sequence(issuance_epoch)
    epoch_budget = _quantize_ilc(_require_decimal_amount(epoch_budget_ilc, "epoch_budget_ilc"))
    requested_bounty = _quantize_ilc(
        _require_decimal_amount(requested_bounty_ilc, "requested_bounty_ilc")
    )
    planned_burn = _quantize_ilc(_require_decimal_amount(planned_burn_ilc, "planned_burn_ilc"))
    observed = _require_decimal_amount(observed_velocity, "observed_velocity")
    if observed > Decimal("1"):
        raise ValueError("observed_velocity_must_be_unit_interval")
    bounty_fraction, burn_fraction, velocity_floor = require_cdl_047_treasury_fractions(
        bounty_cap_fraction,
        burn_floor_fraction,
        velocity_alert_floor,
    )

    bounty_cap = _quantize_ilc(epoch_budget * bounty_fraction)
    burn_floor = _quantize_ilc(epoch_budget * burn_fraction)
    if requested_bounty > bounty_cap:
        raise ValueError("requested_bounty_exceeds_cdl_047_cap")
    if planned_burn < burn_floor:
        raise ValueError("planned_burn_below_cdl_047_floor")
    if requested_bounty + planned_burn > epoch_budget:
        raise ValueError("treasury_request_exceeds_epoch_budget")

    return EpochTreasuryGovernanceQuote(
        runtime_version=TREASURY_GOVERNANCE_RUNTIME_VERSION,
        cdl_047_dependency=CDL_047_DEPENDENCY,
        issuance_epoch=epoch,
        issuance_epoch_duration=ISSUANCE_EPOCH_DURATION,
        validation_epoch_seconds=VALIDATION_EPOCH_SECONDS,
        epoch_budget_ilc=epoch_budget,
        bounty_cap_fraction_of_epoch_budget=bounty_fraction,
        bounty_cap_ilc=bounty_cap,
        requested_bounty_ilc=requested_bounty,
        burn_floor_fraction=burn_fraction,
        burn_floor_ilc=burn_floor,
        planned_burn_ilc=planned_burn,
        velocity_alert_floor=velocity_floor,
        observed_velocity=observed,
        velocity_alert_triggered=observed < velocity_floor,
        treasury_remaining_budget_ilc=_quantize_ilc(
            epoch_budget - requested_bounty - planned_burn
        ),
        production_treasury_activated=False,
        decision_token=PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN,
    )


def require_production_treasury_activation(activation_token: str | None = None) -> None:
    if activation_token != PRODUCTION_TREASURY_ACTIVATION_TOKEN:
        raise ValueError(PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN)
    raise ValueError("production_treasury_activation_not_implemented_phase_1348")


__all__ = [
    "BOUNTY_CAP_0_15_B_E_RUNTIME_TOKEN",
    "BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET",
    "BURN_FLOOR_0_05_RUNTIME_TOKEN",
    "BURN_FLOOR_FRACTION",
    "CDL_047_DEPENDENCY",
    "CDL_047_TREASURY_GOVERNANCE_RUNTIME_TOKEN",
    "NO_DIRECT_TREASURY_STUB_FOUND_TOKEN",
    "PHASE_1347_ALLOCATION_RUNTIME_DEPENDENCY",
    "PRODUCTION_TREASURY_ACTIVATION_TOKEN",
    "PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN",
    "TREASURY_FRACTION_TOTAL_LIMIT",
    "TREASURY_GOVERNANCE_RUNTIME_VERSION",
    "VELOCITY_ALERT_FLOOR",
    "VELOCITY_ALERT_FLOOR_0_91_RUNTIME_TOKEN",
    "VELOCITY_ALERT_TRIGGER_RUNTIME_TOKEN",
    "EpochTreasuryGovernanceQuote",
    "build_treasury_governance_quote",
    "require_cdl_047_treasury_fractions",
    "require_production_treasury_activation",
]
