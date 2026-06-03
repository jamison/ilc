# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-V2 sybil-resistance runtime.

Deterministic heuristic scoring helpers with bounded risk-to-penalty mapping
and tokenized validation failures.
"""

from __future__ import annotations

import math

from ilc_core.reputation.temporal_decay_runtime import CDL_V1_DEPENDENCY

CDL_V2_RUNTIME_VERSION = "cdl_v2_sybil_resistance_runtime_389.v0.1"
CDL_V2_DEPENDENCY = "cdl_v2_sybil_resistance_389.v0.1"


class SybilResistanceValidationError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def _require_numeric(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_invalid_numeric",
            f"{name} must be a numeric value",
        )
    number = float(value)
    if not math.isfinite(number):
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_invalid_numeric",
            f"{name} must be a finite numeric value",
        )
    return number


def _require_unit_interval(name: str, value: float) -> float:
    number = _require_numeric(name, value)
    if number < 0.0 or number > 1.0:
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_out_of_range",
            f"{name} must be in [0, 1]",
        )
    return number


def _require_validation_epoch(epoch_type: str) -> None:
    if epoch_type != "validation_epoch":
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_epoch_context_invalid",
            "sybil-resistance heuristics are validation-epoch scoped",
        )


def compute_identity_cluster_risk(
    *,
    shared_operator_fraction: float,
    shared_infrastructure_fraction: float,
    key_rotation_overlap_fraction: float,
) -> float:
    """Compute bounded cluster-risk signal from overlap indicators."""

    operator = _require_unit_interval("shared_operator_fraction", shared_operator_fraction)
    infrastructure = _require_unit_interval(
        "shared_infrastructure_fraction", shared_infrastructure_fraction
    )
    key_overlap = _require_unit_interval(
        "key_rotation_overlap_fraction", key_rotation_overlap_fraction
    )

    risk = (0.50 * operator) + (0.30 * infrastructure) + (0.20 * key_overlap)
    return round(max(0.0, min(1.0, risk)), 12)


def compute_burst_write_penalty(
    *,
    writes_per_validation_epoch: float,
    baseline_writes_per_validation_epoch: float,
    burst_sensitivity: float = 0.35,
    epoch_type: str = "validation_epoch",
) -> float:
    """Compute bounded penalty for burst-write anomalies."""

    writes = _require_numeric("writes_per_validation_epoch", writes_per_validation_epoch)
    baseline = _require_numeric(
        "baseline_writes_per_validation_epoch", baseline_writes_per_validation_epoch
    )
    sensitivity = _require_numeric("burst_sensitivity", burst_sensitivity)
    _require_validation_epoch(epoch_type)

    if writes < 0.0 or baseline <= 0.0:
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_rate_non_positive",
            "writes must be >= 0 and baseline must be > 0",
        )
    if sensitivity <= 0.0 or sensitivity > 1.0:
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_burst_sensitivity_out_of_range",
            "burst_sensitivity must be in (0, 1]",
        )

    ratio = writes / baseline
    if ratio <= 1.0:
        return 0.0

    penalty = min(1.0, (ratio - 1.0) * sensitivity)
    return round(penalty, 12)


def compute_diversity_floor_contribution(
    *,
    distinct_cluster_refs: float,
    expected_diversity_floor: float,
) -> float:
    """Compute contribution signal for diversity-floor satisfaction."""

    distinct_refs = _require_numeric("distinct_cluster_refs", distinct_cluster_refs)
    expected_floor = _require_numeric("expected_diversity_floor", expected_diversity_floor)

    if distinct_refs < 0.0 or expected_floor <= 0.0:
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_diversity_floor_invalid",
            "distinct refs must be >= 0 and expected floor must be > 0",
        )

    contribution = min(1.0, distinct_refs / expected_floor)
    return round(contribution, 12)


def compute_sybil_penalty(
    *,
    cluster_risk: float,
    burst_write_penalty: float,
    diversity_floor_contribution: float,
) -> float:
    """Map risk signals to bounded sybil penalty score in [0, 1]."""

    risk = _require_unit_interval("cluster_risk", cluster_risk)
    burst = _require_unit_interval("burst_write_penalty", burst_write_penalty)
    diversity = _require_unit_interval(
        "diversity_floor_contribution", diversity_floor_contribution
    )

    raw_penalty = (0.55 * risk) + (0.35 * burst) - (0.25 * diversity)
    bounded = max(0.0, min(1.0, raw_penalty))
    return round(bounded, 12)
