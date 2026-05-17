"""Phase 1355 default-off Genesis intervention guardrail runtime.

CDL-V6 ratifies documented Genesis extraordinary intervention with sunset,
audit trail, and mandatory post hoc CDL-V4 review. Phase 597 narrows the
retained bootstrap suspensive constitutional guardrail into concrete runtime
bounds: one invocation per proposal identifier, one-epoch suspension, maximum
three lifetime invocations, and epoch 60 as the outer sunset.

This module records and audits guardrail-invocation decisions only. It does not
fire the Genesis intervention brake, execute Genesis authority, mutate CDL
state, create new law, or activate ordinary governance weight.
"""

from __future__ import annotations

import json
import os
import tempfile
import fcntl
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping


GENESIS_INTERVENTION_RUNTIME_VERSION = "genesis_intervention_runtime_1355.v0.1"
CDL_V6_DEPENDENCY = (
    "cdl_v6_genesis_intervention_protocol_ratified_phase_334.v0.1"
)
PHASE_597_DEPENDENCY = (
    "genesis_governance_dilution_and_brake_semantics_closure_597.v0.1"
)

CDL_V6_GENESIS_INTERVENTION_RUNTIME_TOKEN = (
    "cdl_v6_genesis_intervention_runtime_phase_1355.v0.1"
)
GENESIS_INTERVENTION_INVOCATION_COUNTER_MAX_3_TOKEN = (
    "genesis_intervention_invocation_counter_max_3_phase_1355"
)
APPEND_ONLY_INVOCATION_LOG_TOKEN = "append_only_invocation_log_phase_1355"
EPOCH_CEILING_ENFORCER_TOKEN = "epoch_ceiling_enforcer_phase_1355"
CDL_V6_GOV_B_TO_GOV_A_TOKEN = "cdl_v6_gov_b_to_gov_a_phase_1355"
GENESIS_INTERVENTION_NOT_FIRED_IN_TESTS_TOKEN = (
    "genesis_intervention_not_fired_in_tests_phase_1355"
)
PHASE_597_BOOTSTRAP_SUSPENSIVE_GUARDRAIL_BOUNDS_TOKEN = (
    "phase_597_bootstrap_suspensive_guardrail_bounds_phase_1355"
)
CDL_V6_EXTRAORDINARY_PATH_NOT_ORDINARY_GOVERNANCE_TOKEN = (
    "cdl_v6_extraordinary_path_not_ordinary_governance_phase_1355"
)
GENESIS_INTERVENTION_EXECUTION_NOT_AUTHORIZED_TOKEN = (
    "genesis_intervention_execution_not_authorized_phase_1355"
)
SIGNED_AUDIT_RECORD_REQUIRED_TOKEN = (
    "signed_audit_record_required_for_real_invocation_phase_1355"
)

GENESIS_INTERVENTION_MAX_INVOCATIONS_EXCEEDED_TOKEN = (
    "genesis_intervention_max_invocations_exceeded"
)
GENESIS_INTERVENTION_EPOCH_CEILING_EXCEEDED_TOKEN = (
    "genesis_intervention_epoch_ceiling_exceeded"
)
GENESIS_INTERVENTION_PROPOSAL_INVOCATION_LIMIT_EXCEEDED_TOKEN = (
    "genesis_intervention_proposal_invocation_limit_exceeded"
)
GENESIS_INTERVENTION_SUNSET_MUST_BE_ONE_EPOCH_TOKEN = (
    "genesis_intervention_sunset_must_be_one_epoch_phase_1355"
)
GENESIS_INTERVENTION_TRIGGER_OUT_OF_SCOPE_TOKEN = (
    "genesis_intervention_trigger_out_of_scope_phase_1355"
)
GENESIS_INTERVENTION_ACCEPTED_AUDIT_ONLY_TOKEN = (
    "genesis_intervention_accepted_audit_only_phase_1355"
)

MAX_LIFETIME_INVOCATIONS = 3
MAX_SUSPENSION_EPOCHS = 1
EPOCH_CEILING = 60

ALLOWED_PHASE_597_TRIGGER_TYPES = (
    "canonical_genesis_lineage_severance",
    "ratified_constitutional_contradiction",
)
CDL_V6_EXTRAORDINARY_TRIGGER_TYPES = (
    "capture",
    "constitutional_violation",
    "time_critical_emergency",
)

INTERVENTION_BRAKE_FIRE_COUNT = 0
GENESIS_INTERVENTION_GUARDRAIL_LOCK_FILENAME = ".genesis_intervention_guardrail.lock"
GENESIS_INTERVENTION_GUARDRAIL_THREAD_LOCK = threading.Lock()


@dataclass(frozen=True)
class GenesisInterventionRequest:
    proposal_id: str
    trigger_type: str
    invocation_epoch: int
    expected_sunset_epoch: int
    ratified_artifact_or_lineage_boundary: str
    cdl_v4_review_pointer: str
    requested_by: str
    justification: str
    signed_audit_record_ref: str
    proposal_content_hash: str = ""


@dataclass(frozen=True)
class GenesisInterventionCounterState:
    lifetime_invocations: int
    proposal_invocations: Mapping[str, int]

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "counter_token": GENESIS_INTERVENTION_INVOCATION_COUNTER_MAX_3_TOKEN,
            "lifetime_invocations": self.lifetime_invocations,
            "proposal_invocations": {
                key: self.proposal_invocations[key]
                for key in sorted(self.proposal_invocations)
            },
            "runtime_version": GENESIS_INTERVENTION_RUNTIME_VERSION,
        }


@dataclass(frozen=True)
class GenesisInterventionAuditRecord:
    runtime_version: str
    cdl_v6_dependency: str
    phase_597_dependency: str
    proposal_id: str
    proposal_content_hash: str
    trigger_type: str
    invocation_epoch: int
    expected_sunset_epoch: int
    counter_before: int
    counter_after: int
    proposal_invocations_before: int
    proposal_invocations_after: int
    outcome: str
    outcome_token: str
    accepted: bool
    execution_authorized: bool
    brake_fired: bool
    diagnostic_timestamp: str
    ratified_artifact_or_lineage_boundary: str
    cdl_v4_review_pointer: str
    requested_by: str
    justification: str
    signed_audit_record_ref: str
    counter_token: str
    append_only_log_token: str
    epoch_ceiling_token: str
    hardening_token: str
    phase_597_bounds_token: str
    cdl_v6_extraordinary_boundary_token: str
    execution_not_authorized_token: str
    signed_audit_record_required_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "append_only_log_token": self.append_only_log_token,
            "brake_fired": self.brake_fired,
            "cdl_v4_review_pointer": self.cdl_v4_review_pointer,
            "cdl_v6_dependency": self.cdl_v6_dependency,
            "cdl_v6_extraordinary_boundary_token": (
                self.cdl_v6_extraordinary_boundary_token
            ),
            "counter_after": self.counter_after,
            "counter_before": self.counter_before,
            "counter_token": self.counter_token,
            "diagnostic_timestamp": self.diagnostic_timestamp,
            "epoch_ceiling_token": self.epoch_ceiling_token,
            "execution_authorized": self.execution_authorized,
            "execution_not_authorized_token": self.execution_not_authorized_token,
            "expected_sunset_epoch": self.expected_sunset_epoch,
            "hardening_token": self.hardening_token,
            "invocation_epoch": self.invocation_epoch,
            "justification": self.justification,
            "outcome": self.outcome,
            "outcome_token": self.outcome_token,
            "phase_597_bounds_token": self.phase_597_bounds_token,
            "phase_597_dependency": self.phase_597_dependency,
            "proposal_content_hash": self.proposal_content_hash,
            "proposal_id": self.proposal_id,
            "proposal_invocations_after": self.proposal_invocations_after,
            "proposal_invocations_before": self.proposal_invocations_before,
            "ratified_artifact_or_lineage_boundary": (
                self.ratified_artifact_or_lineage_boundary
            ),
            "requested_by": self.requested_by,
            "runtime_version": self.runtime_version,
            "signed_audit_record_required_token": self.signed_audit_record_required_token,
            "signed_audit_record_ref": self.signed_audit_record_ref,
            "trigger_type": self.trigger_type,
        }

    def to_canonical_json(self) -> str:
        return _canonical_json(self.to_canonical_record())


def _canonical_json(record: Mapping[str, Any]) -> str:
    return json.dumps(
        record,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _require_non_negative_int(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name}_must_be_non_negative_int")
    return value


def _require_non_empty_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name}_must_be_non_empty_string")
    return value


def _require_optional_string(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name}_must_be_string")
    return value


def _require_request(request: GenesisInterventionRequest) -> GenesisInterventionRequest:
    if not isinstance(request, GenesisInterventionRequest):
        raise ValueError("genesis_intervention_request_required")
    _require_non_empty_string(request.proposal_id, "proposal_id")
    _require_optional_string(request.proposal_content_hash, "proposal_content_hash")
    _require_non_empty_string(request.trigger_type, "trigger_type")
    _require_non_negative_int(request.invocation_epoch, "invocation_epoch")
    _require_non_negative_int(request.expected_sunset_epoch, "expected_sunset_epoch")
    _require_non_empty_string(
        request.ratified_artifact_or_lineage_boundary,
        "ratified_artifact_or_lineage_boundary",
    )
    _require_non_empty_string(request.cdl_v4_review_pointer, "cdl_v4_review_pointer")
    _require_non_empty_string(request.requested_by, "requested_by")
    _require_non_empty_string(request.justification, "justification")
    _require_non_empty_string(request.signed_audit_record_ref, "signed_audit_record_ref")
    return request


def _normalize_counter_state(record: Mapping[str, Any] | None) -> GenesisInterventionCounterState:
    if record is None:
        return GenesisInterventionCounterState(
            lifetime_invocations=0,
            proposal_invocations={},
        )
    if not isinstance(record, Mapping):
        raise ValueError("genesis_intervention_counter_record_must_be_object")
    lifetime = _require_non_negative_int(
        record.get("lifetime_invocations"),
        "lifetime_invocations",
    )
    proposal_record = record.get("proposal_invocations", {})
    if not isinstance(proposal_record, Mapping):
        raise ValueError("proposal_invocations_must_be_object")
    proposals: dict[str, int] = {}
    for proposal_id, count in proposal_record.items():
        proposals[_require_non_empty_string(proposal_id, "proposal_id")] = (
            _require_non_negative_int(count, "proposal_invocation_count")
        )
    return GenesisInterventionCounterState(
        lifetime_invocations=lifetime,
        proposal_invocations=proposals,
    )


def read_genesis_intervention_counter(
    counter_path: str | Path,
) -> GenesisInterventionCounterState:
    path = Path(counter_path)
    if not path.exists():
        return _normalize_counter_state(None)
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("genesis_intervention_counter_json_invalid") from exc
    return _normalize_counter_state(record)


def write_genesis_intervention_counter_atomic(
    counter_path: str | Path,
    state: GenesisInterventionCounterState,
) -> None:
    path = Path(counter_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _canonical_json(state.to_canonical_record()) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _append_invocation_audit_record(
    log_path: str | Path,
    audit_record: GenesisInterventionAuditRecord,
) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(audit_record.to_canonical_json())
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


@contextmanager
def _genesis_intervention_guardrail_lock(counter_path: str | Path) -> Iterator[None]:
    path = Path(counter_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.parent / GENESIS_INTERVENTION_GUARDRAIL_LOCK_FILENAME
    with GENESIS_INTERVENTION_GUARDRAIL_THREAD_LOCK:
        with lock_path.open("a", encoding="utf-8") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def _diagnostic_timestamp(value: str | None) -> str:
    if value is not None:
        return _require_non_empty_string(value, "diagnostic_timestamp")
    return datetime.now(timezone.utc).isoformat()


def _build_counter_state_after_acceptance(
    state: GenesisInterventionCounterState,
    request: GenesisInterventionRequest,
) -> GenesisInterventionCounterState:
    proposal_invocations = dict(state.proposal_invocations)
    proposal_invocations[request.proposal_id] = (
        proposal_invocations.get(request.proposal_id, 0) + 1
    )
    return GenesisInterventionCounterState(
        lifetime_invocations=state.lifetime_invocations + 1,
        proposal_invocations=proposal_invocations,
    )


def build_genesis_intervention_audit_record(
    *,
    request: GenesisInterventionRequest,
    state: GenesisInterventionCounterState,
    diagnostic_timestamp: str | None = None,
) -> GenesisInterventionAuditRecord:
    request = _require_request(request)
    state = _normalize_counter_state(state.to_canonical_record())

    proposal_invocations_before = state.proposal_invocations.get(request.proposal_id, 0)
    counter_after = state.lifetime_invocations
    proposal_invocations_after = proposal_invocations_before
    accepted = False
    outcome = "rejected"
    outcome_token = ""

    if request.trigger_type not in ALLOWED_PHASE_597_TRIGGER_TYPES:
        outcome_token = GENESIS_INTERVENTION_TRIGGER_OUT_OF_SCOPE_TOKEN
    elif request.invocation_epoch > EPOCH_CEILING:
        outcome_token = GENESIS_INTERVENTION_EPOCH_CEILING_EXCEEDED_TOKEN
    elif request.expected_sunset_epoch != request.invocation_epoch + MAX_SUSPENSION_EPOCHS:
        outcome_token = GENESIS_INTERVENTION_SUNSET_MUST_BE_ONE_EPOCH_TOKEN
    elif state.lifetime_invocations >= MAX_LIFETIME_INVOCATIONS:
        outcome_token = GENESIS_INTERVENTION_MAX_INVOCATIONS_EXCEEDED_TOKEN
    elif proposal_invocations_before >= 1:
        outcome_token = GENESIS_INTERVENTION_PROPOSAL_INVOCATION_LIMIT_EXCEEDED_TOKEN
    else:
        accepted = True
        outcome = "accepted_audit_only"
        outcome_token = GENESIS_INTERVENTION_ACCEPTED_AUDIT_ONLY_TOKEN
        counter_after = state.lifetime_invocations + 1
        proposal_invocations_after = proposal_invocations_before + 1

    return GenesisInterventionAuditRecord(
        runtime_version=GENESIS_INTERVENTION_RUNTIME_VERSION,
        cdl_v6_dependency=CDL_V6_DEPENDENCY,
        phase_597_dependency=PHASE_597_DEPENDENCY,
        proposal_id=request.proposal_id,
        proposal_content_hash=request.proposal_content_hash,
        trigger_type=request.trigger_type,
        invocation_epoch=request.invocation_epoch,
        expected_sunset_epoch=request.expected_sunset_epoch,
        counter_before=state.lifetime_invocations,
        counter_after=counter_after,
        proposal_invocations_before=proposal_invocations_before,
        proposal_invocations_after=proposal_invocations_after,
        outcome=outcome,
        outcome_token=outcome_token,
        accepted=accepted,
        execution_authorized=False,
        brake_fired=False,
        diagnostic_timestamp=_diagnostic_timestamp(diagnostic_timestamp),
        ratified_artifact_or_lineage_boundary=(
            request.ratified_artifact_or_lineage_boundary
        ),
        cdl_v4_review_pointer=request.cdl_v4_review_pointer,
        requested_by=request.requested_by,
        justification=request.justification,
        signed_audit_record_ref=request.signed_audit_record_ref,
        counter_token=GENESIS_INTERVENTION_INVOCATION_COUNTER_MAX_3_TOKEN,
        append_only_log_token=APPEND_ONLY_INVOCATION_LOG_TOKEN,
        epoch_ceiling_token=EPOCH_CEILING_ENFORCER_TOKEN,
        hardening_token=CDL_V6_GOV_B_TO_GOV_A_TOKEN,
        phase_597_bounds_token=PHASE_597_BOOTSTRAP_SUSPENSIVE_GUARDRAIL_BOUNDS_TOKEN,
        cdl_v6_extraordinary_boundary_token=(
            CDL_V6_EXTRAORDINARY_PATH_NOT_ORDINARY_GOVERNANCE_TOKEN
        ),
        execution_not_authorized_token=(
            GENESIS_INTERVENTION_EXECUTION_NOT_AUTHORIZED_TOKEN
        ),
        signed_audit_record_required_token=SIGNED_AUDIT_RECORD_REQUIRED_TOKEN,
    )


def record_genesis_intervention_guardrail_invocation(
    *,
    request: GenesisInterventionRequest,
    counter_path: str | Path,
    audit_log_path: str | Path,
    diagnostic_timestamp: str | None = None,
) -> GenesisInterventionAuditRecord:
    with _genesis_intervention_guardrail_lock(counter_path):
        state = read_genesis_intervention_counter(counter_path)
        audit_record = build_genesis_intervention_audit_record(
            request=request,
            state=state,
            diagnostic_timestamp=diagnostic_timestamp,
        )
        if audit_record.accepted:
            next_state = _build_counter_state_after_acceptance(state, request)
            write_genesis_intervention_counter_atomic(counter_path, next_state)
            _append_invocation_audit_record(audit_log_path, audit_record)
            return audit_record

        _append_invocation_audit_record(audit_log_path, audit_record)
    raise ValueError(audit_record.outcome_token)


def require_genesis_intervention_execution_authorization() -> None:
    raise ValueError(GENESIS_INTERVENTION_EXECUTION_NOT_AUTHORIZED_TOKEN)
