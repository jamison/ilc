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

from decimal import Decimal
from typing import Dict

MAINTENANCE_LOTTERY_RUNTIME_VERSION = "maintenance_lottery_runtime_phase_1409.v0.1"
MAINTENANCE_LOTTERY_CDL_RATIFIED_TOKEN = "cdl_093_ratified_phase_1408"
MAINTENANCE_LOTTERY_RUNTIME_STUB_TOKEN = (
    "maintenance_lottery_runtime_stub_committed_phase_1409"
)

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

PHASE_TOKENS: frozenset[str] = frozenset(
    {
        MAINTENANCE_LOTTERY_RUNTIME_STUB_TOKEN,
        MAINTENANCE_LOTTERY_CDL_RATIFIED_TOKEN,
        MAINTENANCE_LOTTERY_NOT_ACTIVATED_TOKEN,
    }
)


def _validate_non_empty_string(value: str, token: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(token)


def _validate_epoch_id(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("invalid_epoch_id")
    if value < 0:
        raise ValueError("invalid_epoch_id")


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
