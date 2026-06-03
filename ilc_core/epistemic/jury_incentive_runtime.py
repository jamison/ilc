# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1401 / CDL-091 jury incentive runtime stub.

This module exposes the CDL-091 ratification evidence to runtime-facing code
while preserving the hard default-off boundary for reviewer payments.

Required phase tokens:
  jury_incentive_runtime_stub_committed_phase_1401
  jury_incentive_runtime_phase_1401.v0.1
  reviewer_payment_not_activated_phase_1401
  cdl_091_ratified_phase_1400
"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

JURY_INCENTIVE_RUNTIME_VERSION = "jury_incentive_runtime_phase_1401.v0.1"
JURY_INCENTIVE_CDL_RATIFIED_TOKEN = "cdl_091_ratified_phase_1400"
JURY_INCENTIVE_RUNTIME_STUB_TOKEN = "jury_incentive_runtime_stub_committed_phase_1401"

REVIEWER_PAYMENT_NOT_ACTIVATED: bool = True
REVIEWER_PAYMENT_NOT_ACTIVATED_TOKEN = "reviewer_payment_not_activated_phase_1401"
APPROVAL_ONLY_PAYMENT_REJECTED: bool = True

PRIMARY_REVIEW_FUNDING_SOURCE = "fixed_pooled_review_budget"
SECONDARY_CONTESTED_FUNDING_SOURCE = "petition_bond_for_contested_or_escalated_cases"
PANEL_PAYMENT_MODEL = "per_reviewer_flat_plus_delayed_accuracy_bonus"

BASE_REVIEW_FEE = Decimal("0.05")
ACCURACY_BONUS_MAX_MULTIPLIER = Decimal("1.00")
APPEAL_SURVIVAL_WEIGHT = Decimal("0.35")
REFUTATION_SURVIVAL_WEIGHT = Decimal("0.35")
INDEPENDENT_REVIEWER_CONSENSUS_WEIGHT = Decimal("0.20")
LONG_RUN_GRAPH_SURVIVAL_WEIGHT = Decimal("0.10")
APPROVAL_BIAS_Z_THRESHOLD = Decimal("2.50")
OUTLIER_BONUS_ATTENUATION = Decimal("0.50")

REGULAR_PANEL_SIZE = 7
OUTSIDER_SEATS = 1
MAX_COMPENSATED_REVIEWERS = 8
REVIEWER_QUORUM_K = 5
ACCURACY_BONUS_VESTING_EPOCHS = 4
APPROVAL_BIAS_MIN_REVIEWS = 20

ACCURACY_BONUS_PARAMETERS: Dict[str, object] = {
    "max_multiplier": ACCURACY_BONUS_MAX_MULTIPLIER,
    "vesting_epochs": ACCURACY_BONUS_VESTING_EPOCHS,
    "appeal_survival_weight": APPEAL_SURVIVAL_WEIGHT,
    "refutation_survival_weight": REFUTATION_SURVIVAL_WEIGHT,
    "independent_reviewer_consensus_weight": INDEPENDENT_REVIEWER_CONSENSUS_WEIGHT,
    "long_run_graph_survival_weight": LONG_RUN_GRAPH_SURVIVAL_WEIGHT,
    "approval_bias_min_reviews": APPROVAL_BIAS_MIN_REVIEWS,
    "approval_bias_z_threshold": APPROVAL_BIAS_Z_THRESHOLD,
    "outlier_bonus_attenuation": OUTLIER_BONUS_ATTENUATION,
}

PHASE_TOKENS: List[str] = [
    JURY_INCENTIVE_RUNTIME_STUB_TOKEN,
    JURY_INCENTIVE_CDL_RATIFIED_TOKEN,
    REVIEWER_PAYMENT_NOT_ACTIVATED_TOKEN,
]


def _validate_non_empty_string(value: str, token: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(token)


def _validate_decimal(value: Decimal, token: str) -> None:
    if not isinstance(value, Decimal):
        raise ValueError(token)
    if not value.is_finite():
        raise ValueError(token)
    if value < Decimal("0"):
        raise ValueError(token)


def queue_reviewer_payment_stub(
    *,
    reviewer_id: str,
    task_id: str,
    base_fee: Decimal = BASE_REVIEW_FEE,
) -> Dict[str, object]:
    """Return a default-off reviewer-payment result without side effects."""
    _validate_non_empty_string(reviewer_id, "invalid_reviewer_id")
    _validate_non_empty_string(task_id, "invalid_task_id")
    _validate_decimal(base_fee, "invalid_base_fee_decimal")

    return {
        "status": "not_activated",
        "reason": REVIEWER_PAYMENT_NOT_ACTIVATED_TOKEN,
        "runtime_version": JURY_INCENTIVE_RUNTIME_VERSION,
        "reviewer_id": reviewer_id,
        "task_id": task_id,
        "base_fee_ecu": str(base_fee),
        "payment_enqueued": False,
        "ledger_write_authorized": False,
        "treasury_write_authorized": False,
        "ecu_distribution_authorized": False,
        "phase_tokens": list(PHASE_TOKENS),
    }
