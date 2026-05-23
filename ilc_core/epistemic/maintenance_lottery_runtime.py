# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 1409 / CDL-093 maintenance lottery runtime stub.

This module exposes the CDL-093 ratification evidence to runtime-facing code
while preserving the hard default-off boundary for maintenance lottery draws
and ECU distribution.

Required phase tokens:
  maintenance_lottery_runtime_stub_committed_phase_1409
  maintenance_lottery_runtime_phase_1409.v0.1
  maintenance_lottery_not_activated_phase_1409
  cdl_093_ratified_phase_1408
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Dict

from .review_lane_admission_runtime import ReviewLaneAdmissionDecision

MAINTENANCE_LOTTERY_RUNTIME_VERSION = "maintenance_lottery_runtime_phase_1409.v0.1"
MAINTENANCE_LOTTERY_CDL_RATIFIED_TOKEN = "cdl_093_ratified_phase_1408"
MAINTENANCE_LOTTERY_RUNTIME_STUB_TOKEN = (
    "maintenance_lottery_runtime_stub_committed_phase_1409"
)
CDL_053_LOCAL_CREDIT_WIRED_TOKEN = (
    "cdl_053_local_credit_wired_maintenance_lottery_phase_1430"
)
MAINTENANCE_LOTTERY_NOT_ACTIVATED_PHASE_1430_TOKEN = (
    "maintenance_lottery_not_activated_phase_1430"
)
NO_ECU_DISTRIBUTION_PHASE_1430_TOKEN = "no_ecu_distribution_phase_1430"

MAINTENANCE_LOTTERY_NOT_ACTIVATED: bool = True
MAINTENANCE_LOTTERY_NOT_ACTIVATED_TOKEN = "maintenance_lottery_not_activated_phase_1409"

MAINTENANCE_LOTTERY_DRAW_MECHANISM = "production_vrf_or_later_ratified_randomness_required"
MAINTENANCE_LOTTERY_SHADOW_DRAW_MECHANISM = "epoch_hash_shadow_quote_only"
MAINTENANCE_LOTTERY_POOL_FUNDING_SOURCE = "cdl_053_werner_local_productive_credit"
MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION = Decimal("0.10")
MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM: bool = False
MAINTENANCE_LOTTERY_NONZERO_FUNDING_REQUIRES_SIM: bool = True

MAINTENANCE_LOTTERY_TASK_ELIGIBILITY_MODE = "review_lane_passed_maintenance_tasks_only"
MAINTENANCE_LOTTERY_MIN_CONTRIBUTION_THRESHOLD = (
    "one_review_lane_passed_maintenance_task_per_epoch"
)
MAINTENANCE_LOTTERY_ELIGIBLE_TASK_CLASSES = (
    "star.map.embedding",
    "contradiction.sweep",
    "graph.compression",
    "stability.simulation",
    "custom_review_lane_assigned",
)
MAINTENANCE_LOTTERY_ENTRY_UNIT = "one_entry_per_review_lane_passed_task"
MAINTENANCE_LOTTERY_ENTRY_CAP_PER_AGENT_PER_EPOCH = "one"
MAINTENANCE_LOTTERY_ANTI_GAMING_CONTROLS = (
    "review_lane_pass_required",
    "content_addressed_task_id_required",
    "duplicate_task_id_rejected",
    "duplicate_output_hash_collapsed",
    "difficulty_factor_not_reward_input",
    "one_entry_per_agent_per_epoch",
    "author_reviewer_conflict_checks_required",
    "same_operator_domain_diversity_check_required_before_production",
    "no_unreviewed_task_reward",
    "no_live_distribution_before_j008_pass_and_production_go",
)

MAINTENANCE_LOTTERY_ECU_DISTRIBUTION_PATH = (
    "cdl_053_werner_local_credit_to_phase_1409_default_off_runtime_stub"
)
MAINTENANCE_LOTTERY_SETTLEMENT_BOUNDARY = (
    "epoch_boundary_batch_quote_only_until_j008_pass_and_production_go"
)
MAINTENANCE_LOTTERY_DIRECT_ILC_REWARD_ALLOWED: bool = False
MAINTENANCE_LOTTERY_ACTIVATION_DEFAULT = "not_activated"
MAINTENANCE_LOTTERY_LIVE_DRAWS_ALLOWED: bool = False
MAINTENANCE_LOTTERY_ECU_SETTLEMENT_ALLOWED: bool = False
MAINTENANCE_LOTTERY_RUNTIME_PHASE = "phase_1409_default_off_stub_only"
MAINTENANCE_LOTTERY_GATE_FLIP_PHASE = "phase_1427_after_phase_1425_verification"

WERNER_LOCAL_CREDIT_UNIT_DESIGNATION = "local_productive_credit"
WERNER_LOCAL_CREDIT_IS_SETTLEMENT_GRADE: bool = False
WERNER_LOCAL_CREDIT_IS_WALLET_VISIBLE: bool = False
WERNER_LOCAL_CREDIT_IS_TRANSFERABLE: bool = False
WERNER_LOCAL_CREDIT_UNIT = Decimal("1")
_ZERO_LOCAL_CREDIT = Decimal("0")

WERNER_DIAGNOSTIC_WIRED_PHASE_1442_TOKEN = "werner_diagnostic_wired_phase_1442"
WERNER_SYSTOLIC_METRIC_DEFINED_PHASE_1442_TOKEN = (
    "werner_systolic_metric_defined_phase_1442"
)
WERNER_DIASTOLIC_METRIC_DEFINED_PHASE_1442_TOKEN = (
    "werner_diastolic_metric_defined_phase_1442"
)
WERNER_PULSE_PRESSURE_METRIC_DEFINED_PHASE_1442_TOKEN = (
    "werner_pulse_pressure_metric_defined_phase_1442"
)
WERNER_NO_ECU_DISTRIBUTION_PHASE_1442_TOKEN = "werner_no_ecu_distribution_phase_1442"
WERNER_NO_FLOW_GOVERNOR_CDL_PHASE_1442_TOKEN = (
    "werner_no_flow_governor_cdl_phase_1442"
)
WERNER_REVIEW_LANE_ONLY_PHASE_1442_TOKEN = "werner_review_lane_only_phase_1442"

WERNER_DIAGNOSTIC_REVIEW_LANE_ONLY: bool = True
WERNER_DIAGNOSTIC_SETTLEMENT_GRADE: bool = False
WERNER_DIAGNOSTIC_WALLET_VISIBLE: bool = False
WERNER_DIAGNOSTIC_TRANSFERABLE: bool = False

WERNER_DIAGNOSTIC_PHASE_1442_TOKENS: tuple[str, ...] = (
    WERNER_DIAGNOSTIC_WIRED_PHASE_1442_TOKEN,
    WERNER_SYSTOLIC_METRIC_DEFINED_PHASE_1442_TOKEN,
    WERNER_DIASTOLIC_METRIC_DEFINED_PHASE_1442_TOKEN,
    WERNER_PULSE_PRESSURE_METRIC_DEFINED_PHASE_1442_TOKEN,
    WERNER_NO_ECU_DISTRIBUTION_PHASE_1442_TOKEN,
    WERNER_NO_FLOW_GOVERNOR_CDL_PHASE_1442_TOKEN,
    WERNER_REVIEW_LANE_ONLY_PHASE_1442_TOKEN,
)

PHASE_TOKENS: frozenset[str] = frozenset(
    {
        MAINTENANCE_LOTTERY_RUNTIME_STUB_TOKEN,
        MAINTENANCE_LOTTERY_CDL_RATIFIED_TOKEN,
        MAINTENANCE_LOTTERY_NOT_ACTIVATED_TOKEN,
        CDL_053_LOCAL_CREDIT_WIRED_TOKEN,
        MAINTENANCE_LOTTERY_NOT_ACTIVATED_PHASE_1430_TOKEN,
        NO_ECU_DISTRIBUTION_PHASE_1430_TOKEN,
    }
)


@dataclass(frozen=True)
class MaintenanceLocalCreditTaskRecord:
    agent_id: str
    task_id: str
    epoch_id: int
    task_class: str
    review_lane_decision: ReviewLaneAdmissionDecision


@dataclass(frozen=True)
class MaintenanceLocalCreditQuote:
    eligible: bool
    status: str
    failure_reasons: tuple[str, ...]
    agent_id: str
    task_id: str
    epoch_id: int
    task_class: str
    local_credit_unit: str
    local_credit_delta: Decimal
    accumulated_local_credit: Decimal
    settlement_grade_ecu: bool
    wallet_visible: bool
    transferable: bool
    maintenance_lottery_activated: bool
    lottery_entry_enqueued: bool
    draw_authorized: bool
    ecu_distribution_authorized: bool
    wallet_write_authorized: bool
    ledger_write_authorized: bool
    treasury_write_authorized: bool
    phase_tokens: tuple[str, ...]


@dataclass(frozen=True)
class WernerDiagnosticQuote:
    systolic_local_credit: Decimal
    diastolic_local_credit: Decimal
    pulse_pressure_local_credit: Decimal
    epoch_id: int
    agent_id: str
    review_lane_only: bool = WERNER_DIAGNOSTIC_REVIEW_LANE_ONLY
    settlement_grade: bool = WERNER_DIAGNOSTIC_SETTLEMENT_GRADE
    wallet_visible: bool = WERNER_DIAGNOSTIC_WALLET_VISIBLE
    transferable: bool = WERNER_DIAGNOSTIC_TRANSFERABLE
    diagnostic_tokens: tuple[str, ...] = WERNER_DIAGNOSTIC_PHASE_1442_TOKENS


def _validate_non_empty_string(value: str, token: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(token)


def _validate_epoch_id(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("invalid_epoch_id")
    if value < 0:
        raise ValueError("invalid_epoch_id")


def _validate_non_negative_decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(token)
    try:
        decimal_value = Decimal(value)  # type: ignore[arg-type]
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(token) from exc
    if not decimal_value.is_finite() or decimal_value < _ZERO_LOCAL_CREDIT:
        raise ValueError(token)
    return decimal_value


def _validate_credit_samples(credit_samples: tuple[object, ...]) -> tuple[Decimal, ...]:
    if not isinstance(credit_samples, tuple) or not credit_samples:
        raise ValueError("invalid_werner_diagnostic_credit_samples_phase_1442")
    return tuple(
        _validate_non_negative_decimal(
            sample,
            "invalid_werner_diagnostic_credit_sample_phase_1442",
        )
        for sample in credit_samples
    )


def _validate_local_credit_task_record(
    task_record: MaintenanceLocalCreditTaskRecord,
) -> None:
    if not isinstance(task_record, MaintenanceLocalCreditTaskRecord):
        raise ValueError("invalid_local_credit_task_record")
    _validate_non_empty_string(task_record.agent_id, "invalid_agent_id")
    _validate_non_empty_string(task_record.task_id, "invalid_task_id")
    _validate_epoch_id(task_record.epoch_id)
    _validate_non_empty_string(task_record.task_class, "invalid_task_class")
    if not isinstance(task_record.review_lane_decision, ReviewLaneAdmissionDecision):
        raise ValueError("invalid_review_lane_decision")


def _local_credit_failure_reasons(
    task_record: MaintenanceLocalCreditTaskRecord,
) -> tuple[str, ...]:
    decision = task_record.review_lane_decision
    failure_reasons: list[str] = []

    if task_record.task_class not in MAINTENANCE_LOTTERY_ELIGIBLE_TASK_CLASSES:
        failure_reasons.append("cdl_053_task_class_not_maintenance_equivalent")
    if not decision.admitted or decision.failure_reasons:
        failure_reasons.append("cdl_053_review_lane_not_passed")
    if decision.submission_id != task_record.task_id:
        failure_reasons.append("cdl_053_review_lane_task_id_mismatch")
    if decision.review_epoch != task_record.epoch_id:
        failure_reasons.append("cdl_053_review_lane_epoch_mismatch")
    if decision.review_lane != task_record.task_class:
        failure_reasons.append("cdl_053_review_lane_task_class_mismatch")

    return tuple(failure_reasons)


def request_maintenance_lottery_entry_stub(
    *,
    agent_id: str,
    task_id: str,
    epoch_id: int,
) -> Dict[str, object]:
    """Return a default-off maintenance-lottery result without side effects."""
    _validate_non_empty_string(agent_id, "invalid_agent_id")
    _validate_non_empty_string(task_id, "invalid_task_id")
    _validate_epoch_id(epoch_id)

    return {
        "status": "not_activated",
        "reason": MAINTENANCE_LOTTERY_NOT_ACTIVATED_TOKEN,
        "runtime_version": MAINTENANCE_LOTTERY_RUNTIME_VERSION,
        "lottery_entry_enqueued": False,
        "draw_authorized": False,
        "ecu_distribution_authorized": False,
        "ledger_write_authorized": False,
        "treasury_write_authorized": False,
        "phase_tokens": sorted(PHASE_TOKENS),
    }


def wire_cdl_053_local_credit_eligibility(
    task_record: MaintenanceLocalCreditTaskRecord,
    *,
    existing_local_credit: Decimal | int | str = _ZERO_LOCAL_CREDIT,
) -> MaintenanceLocalCreditQuote:
    """Quote CDL-053 local-credit eligibility without settlement side effects."""

    _validate_local_credit_task_record(task_record)
    existing_credit = _validate_non_negative_decimal(
        existing_local_credit,
        "invalid_existing_local_credit",
    )
    failure_reasons = _local_credit_failure_reasons(task_record)
    eligible = not failure_reasons
    delta = WERNER_LOCAL_CREDIT_UNIT if eligible else _ZERO_LOCAL_CREDIT

    return MaintenanceLocalCreditQuote(
        eligible=eligible,
        status="local_credit_eligible" if eligible else "local_credit_not_eligible",
        failure_reasons=failure_reasons,
        agent_id=task_record.agent_id,
        task_id=task_record.task_id,
        epoch_id=task_record.epoch_id,
        task_class=task_record.task_class,
        local_credit_unit=WERNER_LOCAL_CREDIT_UNIT_DESIGNATION,
        local_credit_delta=delta,
        accumulated_local_credit=existing_credit + delta,
        settlement_grade_ecu=WERNER_LOCAL_CREDIT_IS_SETTLEMENT_GRADE,
        wallet_visible=WERNER_LOCAL_CREDIT_IS_WALLET_VISIBLE,
        transferable=WERNER_LOCAL_CREDIT_IS_TRANSFERABLE,
        maintenance_lottery_activated=not MAINTENANCE_LOTTERY_NOT_ACTIVATED,
        lottery_entry_enqueued=False,
        draw_authorized=False,
        ecu_distribution_authorized=False,
        wallet_write_authorized=False,
        ledger_write_authorized=False,
        treasury_write_authorized=False,
        phase_tokens=tuple(sorted(PHASE_TOKENS)),
    )


def build_werner_diagnostic_quote(
    *,
    agent_id: str,
    epoch_id: int,
    credit_samples: tuple[Decimal, ...],
) -> WernerDiagnosticQuote:
    """Build read-only Werner pressure diagnostics for review-lane inspection."""

    _validate_non_empty_string(agent_id, "invalid_werner_diagnostic_agent_id_phase_1442")
    _validate_epoch_id(epoch_id)
    samples = _validate_credit_samples(credit_samples)
    systolic = max(samples)
    diastolic = min(samples)
    return WernerDiagnosticQuote(
        systolic_local_credit=systolic,
        diastolic_local_credit=diastolic,
        pulse_pressure_local_credit=systolic - diastolic,
        epoch_id=epoch_id,
        agent_id=agent_id,
        review_lane_only=WERNER_DIAGNOSTIC_REVIEW_LANE_ONLY,
        settlement_grade=WERNER_DIAGNOSTIC_SETTLEMENT_GRADE,
        wallet_visible=WERNER_DIAGNOSTIC_WALLET_VISIBLE,
        transferable=WERNER_DIAGNOSTIC_TRANSFERABLE,
        diagnostic_tokens=WERNER_DIAGNOSTIC_PHASE_1442_TOKENS,
    )
