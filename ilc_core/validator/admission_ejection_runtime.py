# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1353 default-off CDL-017 validator admission/ejection runtime.

This module builds deterministic admission/ejection decisions for the
validator-governance lane. It does not deploy validators, mutate a live
ValidatorSet, write stake state, or activate production admission.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ilc_core.identity.agent_id_runtime import (
    AGENT_ID_RUNTIME_VERSION,
    CDL_042_DEPENDENCY,
    CDL_069_AMENDMENT,
    is_legacy_agent_id,
    is_v2_agent_id,
)
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string, to_decimal
from ilc_core.node.timed_out_lifecycle_runtime_411 import (
    CDL_046_DEPENDENCY,
    TIMED_OUT_LIFECYCLE_RUNTIME_VERSION,
)

from .re_admission_runtime import (
    CDL_058_DEPENDENCY,
    COOLDOWN_EPOCHS_EQUIVOCATION,
    COOLDOWN_EPOCHS_LIVENESS_MISS,
    COOLDOWN_EPOCHS_VOLUNTARY_EXIT,
    EXIT_REASONS,
    RE_ADMISSION_RUNTIME_VERSION,
    evaluate_re_admission_eligibility,
)
from .staking_liveness_runtime import (
    CDL_055_DEPENDENCY,
    EQUIVOCATION_FULL_SLASH,
    GENESIS_STAKE_AMOUNT,
    LIVENESS_MISS_THRESHOLD,
    LIVENESS_PENALTY_FRACTION,
    STAKING_LIVENESS_RUNTIME_VERSION,
)
from .trust_tier_runtime import (
    CDL_056_DEPENDENCY,
    TRUST_TIER_RUNTIME_VERSION,
    is_trust_tier_eligible,
)


VALIDATOR_ADMISSION_EJECTION_RUNTIME_VERSION = (
    "validator_admission_ejection_runtime_1353.v0.1"
)
CDL_017_DEPENDENCY = (
    "cdl_017_validator_governance_framework_ratified_phase_765.v0.1"
)
CDL_017_VALIDATOR_ADMISSION_EJECTION_RUNTIME_TOKEN = (
    "cdl_017_validator_admission_ejection_runtime_phase_1353.v0.1"
)
ADMIT_VALIDATOR_PRODUCTION_IMPL_TOKEN = "admit_validator_production_impl_phase_1353"
EJECT_VALIDATOR_PRODUCTION_IMPL_TOKEN = "eject_validator_production_impl_phase_1353"
SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_TOKEN = (
    "sec_004_transfer_certificate_epoch_binding_phase_1353"
)
VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN = (
    "validator_set_rotation_wired_fast_path_phase_1353"
)
PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN = (
    "production_validator_admission_not_activated_phase_1353"
)
PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN = (
    "first_non_genesis_validator_deployment_requires_later_human_gate"
)

MAX_VALIDATOR_ID = 2**32 - 1
ZERO = Decimal("0")


@dataclass(frozen=True)
class ValidatorAdmissionDecision:
    runtime_version: str
    cdl_017_dependency: str
    agent_id_runtime_version: str
    cdl_042_dependency: str
    cdl_069_amendment: str
    validator_id: int
    agent_id: str
    stake_ecu: Decimal
    minimum_stake_ecu: Decimal
    active_from_epoch: int
    prior_exit_reason: str | None
    epochs_since_exit: int | None
    re_admission_cooldown_remaining: int
    trust_tier_requested: bool
    trust_tier_eligible: bool
    current_validator_ids: tuple[int, ...]
    next_validator_ids: tuple[int, ...]
    production_validator_admission_activated: bool
    decision_token: str
    admission_token: str
    sec_004_epoch_binding_token: str
    rotation_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "active_from_epoch": self.active_from_epoch,
            "admission_token": self.admission_token,
            "agent_id": self.agent_id,
            "agent_id_runtime_version": self.agent_id_runtime_version,
            "cdl_017_dependency": self.cdl_017_dependency,
            "cdl_042_dependency": self.cdl_042_dependency,
            "cdl_069_amendment": self.cdl_069_amendment,
            "current_validator_ids": self.current_validator_ids,
            "decision_token": self.decision_token,
            "epochs_since_exit": self.epochs_since_exit,
            "minimum_stake_ecu": decimal_to_canonical_string(self.minimum_stake_ecu),
            "next_validator_ids": self.next_validator_ids,
            "prior_exit_reason": self.prior_exit_reason,
            "production_validator_admission_activated": (
                self.production_validator_admission_activated
            ),
            "re_admission_cooldown_remaining": self.re_admission_cooldown_remaining,
            "rotation_token": self.rotation_token,
            "runtime_version": self.runtime_version,
            "sec_004_epoch_binding_token": self.sec_004_epoch_binding_token,
            "stake_ecu": decimal_to_canonical_string(self.stake_ecu),
            "trust_tier_eligible": self.trust_tier_eligible,
            "trust_tier_requested": self.trust_tier_requested,
            "validator_id": self.validator_id,
        }


@dataclass(frozen=True)
class ValidatorEjectionDecision:
    runtime_version: str
    cdl_017_dependency: str
    cdl_046_dependency: str
    cdl_055_dependency: str
    cdl_056_dependency: str
    cdl_058_dependency: str
    validator_id: int
    exit_reason: str
    active_from_epoch: int
    consecutive_missed_epochs: int
    equivocation_state: bool
    penalty_fraction: Decimal
    re_admission_cooldown_epochs: int
    re_admission_not_before_epoch: int
    current_validator_ids: tuple[int, ...]
    next_validator_ids: tuple[int, ...]
    production_validator_admission_activated: bool
    decision_token: str
    ejection_token: str
    sec_004_epoch_binding_token: str
    rotation_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "active_from_epoch": self.active_from_epoch,
            "cdl_017_dependency": self.cdl_017_dependency,
            "cdl_046_dependency": self.cdl_046_dependency,
            "cdl_055_dependency": self.cdl_055_dependency,
            "cdl_056_dependency": self.cdl_056_dependency,
            "cdl_058_dependency": self.cdl_058_dependency,
            "consecutive_missed_epochs": self.consecutive_missed_epochs,
            "current_validator_ids": self.current_validator_ids,
            "decision_token": self.decision_token,
            "ejection_token": self.ejection_token,
            "equivocation_state": self.equivocation_state,
            "exit_reason": self.exit_reason,
            "next_validator_ids": self.next_validator_ids,
            "penalty_fraction": decimal_to_canonical_string(self.penalty_fraction),
            "production_validator_admission_activated": (
                self.production_validator_admission_activated
            ),
            "re_admission_cooldown_epochs": self.re_admission_cooldown_epochs,
            "re_admission_not_before_epoch": self.re_admission_not_before_epoch,
            "rotation_token": self.rotation_token,
            "runtime_version": self.runtime_version,
            "sec_004_epoch_binding_token": self.sec_004_epoch_binding_token,
            "validator_id": self.validator_id,
        }


def _require_epoch(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name}_must_be_non_negative_int")
    return value


def _require_future_epoch(active_from_epoch: int, current_epoch: int) -> int:
    active_epoch = _require_epoch(active_from_epoch, "active_from_epoch")
    current = _require_epoch(current_epoch, "current_epoch")
    if active_epoch <= current:
        raise ValueError("validator_activation_epoch_must_be_future_phase_1353")
    return active_epoch


def _require_validator_id(value: int, field_name: str = "validator_id") -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
        or value > MAX_VALIDATOR_ID
    ):
        raise ValueError(f"{field_name}_must_be_positive_u32")
    return value


def _normalize_validator_ids(values: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    if not isinstance(values, (tuple, list)):
        raise ValueError("current_validator_ids_must_be_sequence")
    normalized = tuple(_require_validator_id(value, "validator_id") for value in values)
    if len(set(normalized)) != len(normalized):
        raise ValueError("current_validator_ids_must_be_unique")
    return tuple(sorted(normalized))


def _require_agent_id(agent_id: str) -> str:
    if not (is_v2_agent_id(agent_id) or is_legacy_agent_id(agent_id)):
        raise ValueError("validator_agent_id_invalid_phase_1353")
    return agent_id


def _require_stake(value: Decimal | int | str) -> Decimal:
    if isinstance(value, float):
        raise ValueError("validator_stake_ecu_must_be_exact_decimal")
    amount = to_decimal(value, token="validator_stake_ecu_must_be_exact_decimal")
    if amount < GENESIS_STAKE_AMOUNT:
        raise ValueError("validator_participation_stake_below_minimum_phase_1353")
    return amount


def _require_bool(value: bool, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name}_must_be_bool")
    return value


def _cooldown_epochs(exit_reason: str) -> int:
    if exit_reason == "liveness_miss":
        return COOLDOWN_EPOCHS_LIVENESS_MISS
    if exit_reason == "equivocation":
        return COOLDOWN_EPOCHS_EQUIVOCATION
    if exit_reason == "voluntary_exit":
        return COOLDOWN_EPOCHS_VOLUNTARY_EXIT
    raise ValueError("unrecognized_exit_reason")


def _penalty_fraction_for_exit_reason(
    exit_reason: str,
    consecutive_missed_epochs: int,
    equivocation_state: bool,
) -> Decimal:
    if exit_reason not in EXIT_REASONS:
        raise ValueError("unrecognized_exit_reason")
    if exit_reason == "equivocation":
        if not equivocation_state:
            raise ValueError("equivocation_exit_requires_equivocation_state_phase_1353")
        return EQUIVOCATION_FULL_SLASH
    if exit_reason == "liveness_miss":
        if consecutive_missed_epochs < LIVENESS_MISS_THRESHOLD:
            raise ValueError("liveness_ejection_requires_threshold_phase_1353")
        return LIVENESS_PENALTY_FRACTION
    return ZERO


def admit_validator(
    *,
    current_epoch: int,
    active_from_epoch: int,
    current_validator_ids: tuple[int, ...] | list[int],
    validator_id: int,
    agent_id: str,
    stake_ecu: Decimal | int | str,
    prior_exit_reason: str | None = None,
    epochs_since_exit: int | None = None,
    trust_tier_requested: bool = False,
) -> ValidatorAdmissionDecision:
    """Build a default-off CDL-017 admission decision.

    The returned decision is a deterministic quote/handoff object. It does not
    mutate any live validator set and always records production activation as
    false.
    """

    active_epoch = _require_future_epoch(active_from_epoch, current_epoch)
    normalized_ids = _normalize_validator_ids(current_validator_ids)
    validated_validator_id = _require_validator_id(validator_id)
    if validated_validator_id in normalized_ids:
        raise ValueError("validator_already_active_phase_1353")

    validated_agent_id = _require_agent_id(agent_id)
    stake = _require_stake(stake_ecu)
    requested_trust_tier = _require_bool(trust_tier_requested, "trust_tier_requested")
    trust_tier_eligible = is_trust_tier_eligible(
        consecutive_missed_epochs=0,
        liveness_miss_threshold=LIVENESS_MISS_THRESHOLD,
        equivocation_state=False,
    )

    cooldown_remaining = 0
    if prior_exit_reason is not None:
        if prior_exit_reason not in EXIT_REASONS:
            raise ValueError("unrecognized_exit_reason")
        if epochs_since_exit is None:
            raise ValueError("epochs_since_exit_required_for_re_admission_phase_1353")
        elapsed = _require_epoch(epochs_since_exit, "epochs_since_exit")
        eligibility = evaluate_re_admission_eligibility(prior_exit_reason, elapsed)
        cooldown_remaining = int(eligibility["cooldown_remaining"])
        if not eligibility["eligible"]:
            raise ValueError("validator_re_admission_cooldown_active_phase_1353")
    elif epochs_since_exit is not None:
        raise ValueError("prior_exit_reason_required_for_epochs_since_exit_phase_1353")

    next_ids = tuple(sorted((*normalized_ids, validated_validator_id)))
    return ValidatorAdmissionDecision(
        runtime_version=VALIDATOR_ADMISSION_EJECTION_RUNTIME_VERSION,
        cdl_017_dependency=CDL_017_DEPENDENCY,
        agent_id_runtime_version=AGENT_ID_RUNTIME_VERSION,
        cdl_042_dependency=CDL_042_DEPENDENCY,
        cdl_069_amendment=CDL_069_AMENDMENT,
        validator_id=validated_validator_id,
        agent_id=validated_agent_id,
        stake_ecu=stake,
        minimum_stake_ecu=GENESIS_STAKE_AMOUNT,
        active_from_epoch=active_epoch,
        prior_exit_reason=prior_exit_reason,
        epochs_since_exit=epochs_since_exit,
        re_admission_cooldown_remaining=cooldown_remaining,
        trust_tier_requested=requested_trust_tier,
        trust_tier_eligible=trust_tier_eligible,
        current_validator_ids=normalized_ids,
        next_validator_ids=next_ids,
        production_validator_admission_activated=False,
        decision_token=PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN,
        admission_token=ADMIT_VALIDATOR_PRODUCTION_IMPL_TOKEN,
        sec_004_epoch_binding_token=SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_TOKEN,
        rotation_token=VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN,
    )


def eject_validator(
    *,
    current_epoch: int,
    active_from_epoch: int,
    current_validator_ids: tuple[int, ...] | list[int],
    validator_id: int,
    exit_reason: str,
    consecutive_missed_epochs: int = 0,
    equivocation_state: bool = False,
) -> ValidatorEjectionDecision:
    """Build a default-off CDL-017 ejection decision."""

    active_epoch = _require_future_epoch(active_from_epoch, current_epoch)
    normalized_ids = _normalize_validator_ids(current_validator_ids)
    validated_validator_id = _require_validator_id(validator_id)
    if validated_validator_id not in normalized_ids:
        raise ValueError("validator_not_active_phase_1353")

    missed_epochs = _require_epoch(consecutive_missed_epochs, "consecutive_missed_epochs")
    equivocation = _require_bool(equivocation_state, "equivocation_state")
    penalty_fraction = _penalty_fraction_for_exit_reason(
        exit_reason,
        missed_epochs,
        equivocation,
    )
    cooldown = _cooldown_epochs(exit_reason)
    next_ids = tuple(id_value for id_value in normalized_ids if id_value != validated_validator_id)

    return ValidatorEjectionDecision(
        runtime_version=VALIDATOR_ADMISSION_EJECTION_RUNTIME_VERSION,
        cdl_017_dependency=CDL_017_DEPENDENCY,
        cdl_046_dependency=CDL_046_DEPENDENCY,
        cdl_055_dependency=CDL_055_DEPENDENCY,
        cdl_056_dependency=CDL_056_DEPENDENCY,
        cdl_058_dependency=CDL_058_DEPENDENCY,
        validator_id=validated_validator_id,
        exit_reason=exit_reason,
        active_from_epoch=active_epoch,
        consecutive_missed_epochs=missed_epochs,
        equivocation_state=equivocation,
        penalty_fraction=penalty_fraction,
        re_admission_cooldown_epochs=cooldown,
        re_admission_not_before_epoch=active_epoch + cooldown,
        current_validator_ids=normalized_ids,
        next_validator_ids=next_ids,
        production_validator_admission_activated=False,
        decision_token=PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN,
        ejection_token=EJECT_VALIDATOR_PRODUCTION_IMPL_TOKEN,
        sec_004_epoch_binding_token=SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_TOKEN,
        rotation_token=VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN,
    )


def require_production_validator_admission_activation(
    activation_token: str | None = None,
) -> None:
    if activation_token != PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN:
        raise ValueError(PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN)
    raise ValueError("production_validator_admission_activation_not_implemented_phase_1353")


__all__ = [
    "ADMIT_VALIDATOR_PRODUCTION_IMPL_TOKEN",
    "AGENT_ID_RUNTIME_VERSION",
    "CDL_017_DEPENDENCY",
    "CDL_017_VALIDATOR_ADMISSION_EJECTION_RUNTIME_TOKEN",
    "CDL_042_DEPENDENCY",
    "CDL_046_DEPENDENCY",
    "CDL_055_DEPENDENCY",
    "CDL_056_DEPENDENCY",
    "CDL_058_DEPENDENCY",
    "CDL_069_AMENDMENT",
    "EJECT_VALIDATOR_PRODUCTION_IMPL_TOKEN",
    "MAX_VALIDATOR_ID",
    "PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN",
    "PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN",
    "RE_ADMISSION_RUNTIME_VERSION",
    "SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_TOKEN",
    "STAKING_LIVENESS_RUNTIME_VERSION",
    "TIMED_OUT_LIFECYCLE_RUNTIME_VERSION",
    "TRUST_TIER_RUNTIME_VERSION",
    "VALIDATOR_ADMISSION_EJECTION_RUNTIME_VERSION",
    "VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN",
    "ValidatorAdmissionDecision",
    "ValidatorEjectionDecision",
    "admit_validator",
    "eject_validator",
    "require_production_validator_admission_activation",
]
