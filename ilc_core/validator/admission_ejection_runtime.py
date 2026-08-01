# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-017 validator admission/ejection runtime.

This module builds deterministic admission/ejection decisions for the
validator-governance lane. Phase 1589 adds an activation surface for
agent-bound validator role records. It still does not write stake state or
mutate Rust consensus state directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import re
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
from .validator_eligibility_certificate import (
    CANDIDATE,
    OFFICIAL,
    PROVISIONAL,
    ValidatorEligibilityCertificate,
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
FIRST_NON_GENESIS_VALIDATOR_DEPLOYMENT_HUMAN_GATE_TOKEN = (
    "first_non_genesis_validator_deployment_requires_later_human_gate"
)
PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN = (
    "production_validator_admission_activated_phase_1589"
)
VALIDATOR_ROLE_RECORD_VERSION = "validator_role_record_phase_1589.v0.1"
VALIDATOR_ADMISSION_CDL055_BOND_SURFACE_TOKEN = (
    "cdl055_validator_bond_surface_preserved_not_silent_stake_rewrite_phase_1589"
)

MAX_VALIDATOR_ID = 2**32 - 1
ZERO = Decimal("0")
ROLE_STATUSES = (CANDIDATE, PROVISIONAL, OFFICIAL, "ejected")
_LOWER_HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")
_LOWER_HEX_96_RE = re.compile(r"^[0-9a-f]{96}$")
_NETWORK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,62}$")


@dataclass(frozen=True)
class ValidatorRoleRecord:
    schema_version: str
    agent_id: str
    validator_id: int
    validator_key: str
    validator_endpoint: str
    role_status: str
    quorum_weight: int
    effective_from_epoch: int
    effective_to_epoch: int | None
    reputation_evidence_root: str | None
    earned_ecu_work_score_root: str | None
    liveness_state_root: str | None
    admission_authority_token: str
    network_id: str
    eligibility_certificate_sha256: str | None
    eligibility_verdict: str | None
    rust_validator_set_eligible: bool
    cdl055_bond_surface_token: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_version", _require_token(self.schema_version))
        object.__setattr__(self, "agent_id", _require_agent_id(self.agent_id))
        object.__setattr__(
            self,
            "validator_id",
            _require_validator_id(self.validator_id),
        )
        object.__setattr__(
            self,
            "validator_key",
            _require_lower_hex_96(self.validator_key, "validator_key"),
        )
        object.__setattr__(
            self,
            "validator_endpoint",
            _require_endpoint(self.validator_endpoint),
        )
        role_status = _require_role_status(self.role_status)
        object.__setattr__(self, "role_status", role_status)
        object.__setattr__(
            self,
            "quorum_weight",
            _require_quorum_weight(self.quorum_weight, role_status),
        )
        effective_from = _require_epoch(
            self.effective_from_epoch,
            "effective_from_epoch",
        )
        object.__setattr__(self, "effective_from_epoch", effective_from)
        object.__setattr__(
            self,
            "effective_to_epoch",
            _require_effective_to_epoch(self.effective_to_epoch, effective_from),
        )
        object.__setattr__(
            self,
            "reputation_evidence_root",
            _require_optional_root(self.reputation_evidence_root, "reputation_evidence_root"),
        )
        object.__setattr__(
            self,
            "earned_ecu_work_score_root",
            _require_optional_root(
                self.earned_ecu_work_score_root,
                "earned_ecu_work_score_root",
            ),
        )
        object.__setattr__(
            self,
            "liveness_state_root",
            _require_optional_root(self.liveness_state_root, "liveness_state_root"),
        )
        object.__setattr__(
            self,
            "admission_authority_token",
            _require_token(self.admission_authority_token),
        )
        object.__setattr__(self, "network_id", _require_network_id(self.network_id))
        object.__setattr__(
            self,
            "eligibility_certificate_sha256",
            _require_optional_root(
                self.eligibility_certificate_sha256,
                "eligibility_certificate_sha256",
            ),
        )
        if self.eligibility_verdict is not None:
            object.__setattr__(
                self,
                "eligibility_verdict",
                _require_role_status(self.eligibility_verdict),
            )
        if not isinstance(self.rust_validator_set_eligible, bool):
            raise ValueError("rust_validator_set_eligible_must_be_bool_phase_1589")
        if self.rust_validator_set_eligible != (
            role_status == OFFICIAL and self.quorum_weight > 0
        ):
            raise ValueError("rust_validator_set_eligibility_mismatch_phase_1589")
        object.__setattr__(
            self,
            "cdl055_bond_surface_token",
            _require_token(self.cdl055_bond_surface_token),
        )

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "admission_authority_token": self.admission_authority_token,
            "agent_id": self.agent_id,
            "cdl055_bond_surface_token": self.cdl055_bond_surface_token,
            "earned_ecu_work_score_root": self.earned_ecu_work_score_root,
            "effective_from_epoch": self.effective_from_epoch,
            "effective_to_epoch": self.effective_to_epoch,
            "eligibility_certificate_sha256": self.eligibility_certificate_sha256,
            "eligibility_verdict": self.eligibility_verdict,
            "liveness_state_root": self.liveness_state_root,
            "network_id": self.network_id,
            "quorum_weight": self.quorum_weight,
            "reputation_evidence_root": self.reputation_evidence_root,
            "role_status": self.role_status,
            "rust_validator_set_eligible": self.rust_validator_set_eligible,
            "schema_version": self.schema_version,
            "validator_endpoint": self.validator_endpoint,
            "validator_id": self.validator_id,
            "validator_key": self.validator_key,
        }


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
    trust_tier_consecutive_missed_epochs: int
    trust_tier_equivocation_state: bool
    current_agent_ids: tuple[str, ...]
    next_agent_ids: tuple[str, ...]
    current_validator_ids: tuple[int, ...]
    next_validator_ids: tuple[int, ...]
    validator_role_record: ValidatorRoleRecord | None
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
            "trust_tier_consecutive_missed_epochs": (
                self.trust_tier_consecutive_missed_epochs
            ),
            "trust_tier_equivocation_state": self.trust_tier_equivocation_state,
            "trust_tier_eligible": self.trust_tier_eligible,
            "trust_tier_requested": self.trust_tier_requested,
            "current_agent_ids": self.current_agent_ids,
            "next_agent_ids": self.next_agent_ids,
            "validator_role_record": (
                None
                if self.validator_role_record is None
                else self.validator_role_record.to_canonical_record()
            ),
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


def _require_token(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("validator_admission_token_invalid_phase_1589")
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


def _require_network_id(value: object) -> str:
    if not isinstance(value, str) or not _NETWORK_ID_RE.fullmatch(value):
        raise ValueError("validator_network_id_invalid_phase_1589")
    return value


def _require_lower_hex_96(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not _LOWER_HEX_96_RE.fullmatch(value):
        raise ValueError(f"{field_name}_must_be_96_lower_hex_phase_1589")
    return value


def _require_optional_root(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not _LOWER_HEX_64_RE.fullmatch(value):
        raise ValueError(f"{field_name}_must_be_sha256_hex_or_none_phase_1589")
    return value


def _require_endpoint(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("validator_endpoint_must_be_non_empty_phase_1589")
    if any(char.isspace() for char in value):
        raise ValueError("validator_endpoint_must_not_contain_whitespace_phase_1589")
    return value


def _require_role_status(value: object) -> str:
    if not isinstance(value, str) or value not in ROLE_STATUSES:
        raise ValueError("validator_role_status_invalid_phase_1589")
    return value


def _require_quorum_weight(value: object, role_status: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("validator_quorum_weight_must_be_non_negative_int_phase_1589")
    if role_status in {CANDIDATE, PROVISIONAL, "ejected"} and value != 0:
        raise ValueError("non_official_validator_quorum_weight_must_be_zero_phase_1589")
    if role_status == OFFICIAL and value <= 0:
        raise ValueError("official_validator_quorum_weight_must_be_positive_phase_1589")
    return value


def _require_effective_to_epoch(value: object, effective_from_epoch: int) -> int | None:
    if value is None:
        return None
    effective_to = _require_epoch(value, "effective_to_epoch")  # type: ignore[arg-type]
    if effective_to < effective_from_epoch:
        raise ValueError("validator_effective_to_precedes_effective_from_phase_1589")
    return effective_to


def _role_record_is_epoch_active(record: ValidatorRoleRecord, epoch: int) -> bool:
    checked_epoch = _require_epoch(epoch, "current_epoch")
    if checked_epoch < record.effective_from_epoch:
        return False
    if record.effective_to_epoch is not None and checked_epoch > record.effective_to_epoch:
        return False
    return True


def _normalize_agent_ids(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    if not isinstance(values, (tuple, list)):
        raise ValueError("current_agent_ids_must_be_sequence")
    normalized = tuple(_require_agent_id(value) for value in values)
    if len(set(normalized)) != len(normalized):
        raise ValueError("current_agent_ids_must_be_unique")
    return tuple(sorted(normalized))


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


def _parse_admission_options(
    admission_options: dict[str, object],
) -> tuple[tuple[str, ...], int, bool, dict[str, object]]:
    allowed = {
        "admission_authority_token",
        "current_agent_ids",
        "effective_to_epoch",
        "eligibility_certificate",
        "network_id",
        "quorum_weight",
        "role_status",
        "trust_tier_consecutive_missed_epochs",
        "trust_tier_equivocation_state",
        "validator_endpoint",
        "validator_key",
    }
    unknown = sorted(set(admission_options) - allowed)
    if unknown:
        raise ValueError("unknown_validator_admission_option_phase_1353")

    current_agent_ids = admission_options.get("current_agent_ids", [])
    if current_agent_ids is None:
        current_agent_ids = []
    if not isinstance(current_agent_ids, (tuple, list)):
        raise ValueError("current_agent_ids_must_be_sequence")
    normalized_agent_ids = _normalize_agent_ids(current_agent_ids)
    trust_missed_epochs = _require_epoch(
        admission_options.get("trust_tier_consecutive_missed_epochs", 0),
        "trust_tier_consecutive_missed_epochs",
    )
    trust_equivocation = _require_bool(
        admission_options.get("trust_tier_equivocation_state", False),
        "trust_tier_equivocation_state",
    )
    role_options = {
        key: admission_options[key]
        for key in (
            "admission_authority_token",
            "effective_to_epoch",
            "eligibility_certificate",
            "network_id",
            "quorum_weight",
            "role_status",
            "validator_endpoint",
            "validator_key",
        )
        if key in admission_options
    }
    return normalized_agent_ids, trust_missed_epochs, trust_equivocation, role_options


def build_validator_role_record(
    *,
    agent_id: str,
    validator_id: int,
    validator_key: str,
    validator_endpoint: str,
    effective_from_epoch: int,
    network_id: str,
    eligibility_certificate: ValidatorEligibilityCertificate | None = None,
    role_status: str | None = None,
    quorum_weight: int | None = None,
    effective_to_epoch: int | None = None,
    admission_authority_token: str = PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN,
) -> ValidatorRoleRecord:
    """Build the Phase 1589 agent-bound validator-role record.

    Bootstrap authority may substitute only for the certificate's
    reputation-evidence root. The certificate runtime itself enforces that
    earned-ECU work and liveness roots remain required for official status.
    """

    validated_agent_id = _require_agent_id(agent_id)
    checked_epoch = _require_epoch(effective_from_epoch, "effective_from_epoch")
    cert_hash: str | None = None
    cert_verdict: str | None = None
    reputation_root: str | None = None
    work_score_root: str | None = None
    liveness_root: str | None = None
    if eligibility_certificate is not None:
        if not isinstance(eligibility_certificate, ValidatorEligibilityCertificate):
            raise ValueError("eligibility_certificate_must_be_validator_certificate_phase_1589")
        if eligibility_certificate.agent_id != validated_agent_id:
            raise ValueError("eligibility_certificate_agent_mismatch_phase_1589")
        if eligibility_certificate.network_id != _require_network_id(network_id):
            raise ValueError("eligibility_certificate_network_mismatch_phase_1589")
        if eligibility_certificate.epoch != checked_epoch:
            raise ValueError("eligibility_certificate_epoch_mismatch_phase_1589")
        cert_hash = eligibility_certificate.certificate_sha256()
        cert_verdict = eligibility_certificate.eligibility_verdict
        reputation_root = eligibility_certificate.reputation_evidence_root
        work_score_root = eligibility_certificate.earned_ecu_work_score_root
        liveness_root = eligibility_certificate.liveness_root

    resolved_status = _require_role_status(role_status or cert_verdict or CANDIDATE)
    if eligibility_certificate is not None and resolved_status != cert_verdict:
        raise ValueError("validator_role_status_certificate_verdict_mismatch_phase_1589")
    resolved_weight = 1 if quorum_weight is None and resolved_status == OFFICIAL else quorum_weight
    if resolved_weight is None:
        resolved_weight = 0

    return ValidatorRoleRecord(
        schema_version=VALIDATOR_ROLE_RECORD_VERSION,
        agent_id=validated_agent_id,
        validator_id=_require_validator_id(validator_id),
        validator_key=_require_lower_hex_96(validator_key, "validator_key"),
        validator_endpoint=_require_endpoint(validator_endpoint),
        role_status=resolved_status,
        quorum_weight=resolved_weight,
        effective_from_epoch=checked_epoch,
        effective_to_epoch=effective_to_epoch,
        reputation_evidence_root=reputation_root,
        earned_ecu_work_score_root=work_score_root,
        liveness_state_root=liveness_root,
        admission_authority_token=admission_authority_token,
        network_id=network_id,
        eligibility_certificate_sha256=cert_hash,
        eligibility_verdict=cert_verdict,
        rust_validator_set_eligible=resolved_status == OFFICIAL and resolved_weight > 0,
        cdl055_bond_surface_token=VALIDATOR_ADMISSION_CDL055_BOND_SURFACE_TOKEN,
    )


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
    activation_token: str | None = None,
    **admission_options: object,
) -> ValidatorAdmissionDecision:
    """Build a CDL-017 admission decision.

    Calls without `activation_token` preserve the historical default-off quote
    behavior. Calls with the Phase 1589 production token must provide an
    official, epoch-active `ValidatorRoleRecord` through the eligibility
    certificate inputs.
    """

    active_epoch = _require_future_epoch(active_from_epoch, current_epoch)
    normalized_ids = _normalize_validator_ids(current_validator_ids)
    validated_validator_id = _require_validator_id(validator_id)
    if validated_validator_id in normalized_ids:
        raise ValueError("validator_already_active_phase_1353")

    validated_agent_id = _require_agent_id(agent_id)
    (
        normalized_agent_ids,
        trust_missed_epochs,
        trust_equivocation,
        role_options,
    ) = _parse_admission_options(admission_options)
    if validated_agent_id in normalized_agent_ids:
        raise ValueError("validator_agent_already_active_phase_1353")
    stake = _require_stake(stake_ecu)
    requested_trust_tier = _require_bool(trust_tier_requested, "trust_tier_requested")
    trust_tier_eligible = is_trust_tier_eligible(
        consecutive_missed_epochs=trust_missed_epochs,
        liveness_miss_threshold=LIVENESS_MISS_THRESHOLD,
        equivocation_state=trust_equivocation,
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

    production_active = activation_token is not None
    if production_active and activation_token != PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN:
        raise ValueError(PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN)

    validator_role_record = None
    if role_options:
        required = {"network_id", "validator_key", "validator_endpoint"}
        if not required.issubset(role_options):
            raise ValueError("validator_role_record_missing_required_fields_phase_1589")
        default_role_authority_token = (
            PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN
            if production_active
            else PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN
        )
        validator_role_record = build_validator_role_record(
            agent_id=validated_agent_id,
            validator_id=validated_validator_id,
            validator_key=role_options["validator_key"],  # type: ignore[arg-type]
            validator_endpoint=role_options["validator_endpoint"],  # type: ignore[arg-type]
            effective_from_epoch=active_epoch,
            network_id=role_options["network_id"],  # type: ignore[arg-type]
            eligibility_certificate=role_options.get("eligibility_certificate"),  # type: ignore[arg-type]
            role_status=role_options.get("role_status"),  # type: ignore[arg-type]
            quorum_weight=role_options.get("quorum_weight"),  # type: ignore[arg-type]
            effective_to_epoch=role_options.get("effective_to_epoch"),  # type: ignore[arg-type]
            admission_authority_token=role_options.get(
                "admission_authority_token",
                default_role_authority_token,
            ),  # type: ignore[arg-type]
        )

    if production_active:
        if validator_role_record is None:
            raise ValueError("validator_role_record_required_for_activation_phase_1589")
        if not _role_record_is_epoch_active(validator_role_record, active_epoch):
            raise ValueError("validator_role_record_not_epoch_active_phase_1589")
        if validator_role_record.role_status != OFFICIAL:
            raise ValueError("validator_activation_requires_official_role_phase_1589")
        if not validator_role_record.rust_validator_set_eligible:
            raise ValueError("validator_activation_requires_rust_eligible_role_phase_1589")
        if (
            validator_role_record.admission_authority_token
            != PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN
        ):
            raise ValueError("validator_role_record_authority_token_mismatch_phase_1589")

    next_ids = tuple(sorted((*normalized_ids, validated_validator_id)))
    next_agent_ids = tuple(sorted((*normalized_agent_ids, validated_agent_id)))
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
        trust_tier_consecutive_missed_epochs=trust_missed_epochs,
        trust_tier_equivocation_state=trust_equivocation,
        current_agent_ids=normalized_agent_ids,
        next_agent_ids=next_agent_ids,
        current_validator_ids=normalized_ids,
        next_validator_ids=next_ids,
        validator_role_record=validator_role_record,
        production_validator_admission_activated=production_active,
        decision_token=(
            PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN
            if production_active
            else PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN
        ),
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
    "FIRST_NON_GENESIS_VALIDATOR_DEPLOYMENT_HUMAN_GATE_TOKEN",
    "MAX_VALIDATOR_ID",
    "PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN",
    "PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN",
    "RE_ADMISSION_RUNTIME_VERSION",
    "SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_TOKEN",
    "STAKING_LIVENESS_RUNTIME_VERSION",
    "TIMED_OUT_LIFECYCLE_RUNTIME_VERSION",
    "TRUST_TIER_RUNTIME_VERSION",
    "VALIDATOR_ADMISSION_EJECTION_RUNTIME_VERSION",
    "VALIDATOR_ADMISSION_CDL055_BOND_SURFACE_TOKEN",
    "VALIDATOR_ROLE_RECORD_VERSION",
    "VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN",
    "ValidatorAdmissionDecision",
    "ValidatorEjectionDecision",
    "ValidatorRoleRecord",
    "admit_validator",
    "build_validator_role_record",
    "eject_validator",
    "require_production_validator_admission_activation",
]
