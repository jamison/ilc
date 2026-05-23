# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 1345 non-activating epoch emission quote runtime."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN, localcontext
from typing import Any


EPOCH_EMISSION_RUNTIME_VERSION = "epoch_emission_runtime_1345.v0.1"
CDL_025_EMISSION_SCHEDULE_RUNTIME_TOKEN = "cdl_025_emission_schedule_runtime_phase_1345.v0.1"
CDL_026_CMAX_CAP_RUNTIME_TOKEN = "cdl_026_cmax_cap_runtime_phase_1345.v0.1"
CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN = "cdl_027_epoch_length_runtime_phase_1345.v0.1"
C_MAX_ENFORCEMENT_RUNTIME_TOKEN = "c_max_enforcement_runtime_phase_1345"
CDL_025_DEPENDENCY = "cdl_025_terminal_issuance_model_ratified_phase_267.v0.1"
CDL_026_DEPENDENCY = "cdl_026_cmax_lock_ratified_phase_273.v0.1"
CDL_027_DEPENDENCY = "cdl_027_decay_formulation_ratified_phase_276.v0.1"

TERMINAL_ISSUANCE_MODEL = "fee_funded_tail_model_b"
C_MAX_ILC = Decimal("25920000")
HALVING_INTERVAL_ISSUANCE_EPOCHS = 48
ISSUANCE_EPOCH_DURATION = "1_month"
VALIDATION_EPOCH_SECONDS = 60
ISSUANCE_SCHEDULE_HORIZON_EPOCHS = 480
ILC_QUANTUM = Decimal("0.000000001")
DECIMAL_PRECISION = 80

PRODUCTION_MINTING_NOT_ACTIVATED_TOKEN = "production_minting_not_activated_phase_1345"
DEVNET_PRODUCTION_TRANSITION_GATE_TOKEN = "devnet_production_transition_gate_recorded_phase_1345"
PRODUCTION_EMISSION_ACTIVATION_TOKEN = "phase_1366_soft_rc_eligible_true_value_path_activation_required"


@dataclass(frozen=True)
class EpochEmissionQuote:
    runtime_version: str
    terminal_issuance_model: str
    issuance_epoch: int
    issuance_epoch_duration: str
    validation_epoch_seconds: int
    halving_interval_issuance_epochs: int
    schedule_horizon_epochs: int
    c_max_ilc: Decimal
    cumulative_issued_before_epoch_ilc: Decimal
    raw_epoch_budget_ilc: Decimal
    capped_epoch_budget_ilc: Decimal
    remaining_cap_before_epoch_ilc: Decimal
    cap_enforced: bool
    production_minting_activated: bool
    decision_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "c_max_ilc": _decimal_to_string(self.c_max_ilc),
            "cap_enforced": self.cap_enforced,
            "capped_epoch_budget_ilc": _decimal_to_string(self.capped_epoch_budget_ilc),
            "cumulative_issued_before_epoch_ilc": _decimal_to_string(
                self.cumulative_issued_before_epoch_ilc
            ),
            "decision_token": self.decision_token,
            "halving_interval_issuance_epochs": self.halving_interval_issuance_epochs,
            "issuance_epoch": self.issuance_epoch,
            "issuance_epoch_duration": self.issuance_epoch_duration,
            "production_minting_activated": self.production_minting_activated,
            "raw_epoch_budget_ilc": _decimal_to_string(self.raw_epoch_budget_ilc),
            "remaining_cap_before_epoch_ilc": _decimal_to_string(
                self.remaining_cap_before_epoch_ilc
            ),
            "runtime_version": self.runtime_version,
            "schedule_horizon_epochs": self.schedule_horizon_epochs,
            "terminal_issuance_model": self.terminal_issuance_model,
            "validation_epoch_seconds": self.validation_epoch_seconds,
        }


def _require_epoch_sequence(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("issuance_epoch_must_be_non_negative_int")
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
    return format(value.normalize(), "f")


def halving_decay_ratio() -> Decimal:
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        return (-Decimal(2).ln() / Decimal(HALVING_INTERVAL_ISSUANCE_EPOCHS)).exp()


def epoch_zero_emission_budget() -> Decimal:
    ratio = halving_decay_ratio()
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        geometric_sum = (Decimal(1) - (ratio ** ISSUANCE_SCHEDULE_HORIZON_EPOCHS)) / (
            Decimal(1) - ratio
        )
        return _quantize_ilc(C_MAX_ILC / geometric_sum)


def raw_epoch_emission_budget(issuance_epoch: int) -> Decimal:
    epoch = _require_epoch_sequence(issuance_epoch)
    ratio = halving_decay_ratio()
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        return _quantize_ilc(epoch_zero_emission_budget() * (ratio**epoch))


def build_epoch_emission_quote(
    issuance_epoch: int,
    cumulative_issued_before_epoch_ilc: Decimal | int | str,
) -> EpochEmissionQuote:
    epoch = _require_epoch_sequence(issuance_epoch)
    cumulative = _require_decimal_amount(
        cumulative_issued_before_epoch_ilc,
        "cumulative_issued_before_epoch_ilc",
    )
    if cumulative > C_MAX_ILC:
        raise ValueError("cumulative_issued_exceeds_c_max")

    raw_budget = raw_epoch_emission_budget(epoch)
    remaining_cap = C_MAX_ILC - cumulative
    capped_budget = raw_budget if raw_budget <= remaining_cap else remaining_cap
    capped_budget = _quantize_ilc(capped_budget)

    return EpochEmissionQuote(
        runtime_version=EPOCH_EMISSION_RUNTIME_VERSION,
        terminal_issuance_model=TERMINAL_ISSUANCE_MODEL,
        issuance_epoch=epoch,
        issuance_epoch_duration=ISSUANCE_EPOCH_DURATION,
        validation_epoch_seconds=VALIDATION_EPOCH_SECONDS,
        halving_interval_issuance_epochs=HALVING_INTERVAL_ISSUANCE_EPOCHS,
        schedule_horizon_epochs=ISSUANCE_SCHEDULE_HORIZON_EPOCHS,
        c_max_ilc=C_MAX_ILC,
        cumulative_issued_before_epoch_ilc=_quantize_ilc(cumulative),
        raw_epoch_budget_ilc=raw_budget,
        capped_epoch_budget_ilc=capped_budget,
        remaining_cap_before_epoch_ilc=_quantize_ilc(remaining_cap),
        cap_enforced=capped_budget != raw_budget,
        production_minting_activated=False,
        decision_token=PRODUCTION_MINTING_NOT_ACTIVATED_TOKEN,
    )


def require_production_minting_activation(activation_token: str | None = None) -> None:
    if activation_token != PRODUCTION_EMISSION_ACTIVATION_TOKEN:
        raise ValueError(PRODUCTION_MINTING_NOT_ACTIVATED_TOKEN)
    raise ValueError("production_minting_activation_not_implemented_phase_1345")


__all__ = [
    "CDL_025_DEPENDENCY",
    "CDL_025_EMISSION_SCHEDULE_RUNTIME_TOKEN",
    "CDL_026_DEPENDENCY",
    "CDL_026_CMAX_CAP_RUNTIME_TOKEN",
    "CDL_027_DEPENDENCY",
    "CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN",
    "C_MAX_ILC",
    "C_MAX_ENFORCEMENT_RUNTIME_TOKEN",
    "DEVNET_PRODUCTION_TRANSITION_GATE_TOKEN",
    "EPOCH_EMISSION_RUNTIME_VERSION",
    "EpochEmissionQuote",
    "HALVING_INTERVAL_ISSUANCE_EPOCHS",
    "ILC_QUANTUM",
    "ISSUANCE_EPOCH_DURATION",
    "ISSUANCE_SCHEDULE_HORIZON_EPOCHS",
    "PRODUCTION_EMISSION_ACTIVATION_TOKEN",
    "PRODUCTION_MINTING_NOT_ACTIVATED_TOKEN",
    "TERMINAL_ISSUANCE_MODEL",
    "VALIDATION_EPOCH_SECONDS",
    "build_epoch_emission_quote",
    "epoch_zero_emission_budget",
    "halving_decay_ratio",
    "raw_epoch_emission_budget",
    "require_production_minting_activation",
]
