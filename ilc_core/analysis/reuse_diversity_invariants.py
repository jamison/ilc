# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import math
from typing import Mapping, TypedDict

from ilc_core.exceptions import NodeValueKernelError


class ReuseDiversityPolicy(TypedDict):
    min_distinct_agents: int
    max_single_agent_share: float
    penalty_floor: float


class ReuseDiversityMetrics(TypedDict):
    reuse_count: float
    distinct_agent_count: float
    max_agent_reuse_share: float


_REFUTATION_MULTIPLIER = 1.2
_MIN_REFUTATION_SAFE_FLOOR = (1.0 / _REFUTATION_MULTIPLIER) + 1e-9


DEFAULT_REUSE_DIVERSITY_POLICY: ReuseDiversityPolicy = {
    "min_distinct_agents": 2,
    "max_single_agent_share": 0.75,
    "penalty_floor": 0.85,
}


def validate_reuse_diversity_policy(policy: Mapping[str, object]) -> ReuseDiversityPolicy:
    required_keys = {
        "min_distinct_agents",
        "max_single_agent_share",
        "penalty_floor",
    }
    if set(policy.keys()) != required_keys:
        raise NodeValueKernelError("reuse_diversity_invalid_policy_keys")

    min_distinct_agents = policy["min_distinct_agents"]
    max_single_agent_share = policy["max_single_agent_share"]
    penalty_floor = policy["penalty_floor"]

    if (
        isinstance(min_distinct_agents, bool)
        or not isinstance(min_distinct_agents, int)
        or min_distinct_agents < 1
    ):
        raise NodeValueKernelError("reuse_diversity_invalid_min_distinct_agents")
    if (
        isinstance(max_single_agent_share, bool)
        or not isinstance(max_single_agent_share, (int, float))
        or not math.isfinite(float(max_single_agent_share))
        or float(max_single_agent_share) <= 0.0
        or float(max_single_agent_share) > 1.0
    ):
        raise NodeValueKernelError("reuse_diversity_invalid_max_single_agent_share")
    if (
        isinstance(penalty_floor, bool)
        or not isinstance(penalty_floor, (int, float))
        or not math.isfinite(float(penalty_floor))
        or float(penalty_floor) < 0.0
        or float(penalty_floor) > 1.0
    ):
        raise NodeValueKernelError("reuse_diversity_invalid_penalty_floor")

    normalized_floor = float(penalty_floor)
    if normalized_floor < _MIN_REFUTATION_SAFE_FLOOR:
        raise NodeValueKernelError("reuse_diversity_penalty_floor_below_refutation_safety")

    return {
        "min_distinct_agents": min_distinct_agents,
        "max_single_agent_share": float(max_single_agent_share),
        "penalty_floor": normalized_floor,
    }


def validate_reuse_diversity_metrics(metrics: Mapping[str, object]) -> ReuseDiversityMetrics:
    reuse_count = metrics.get("reuse_count")
    distinct_agent_count = metrics.get("distinct_agent_count")
    max_agent_reuse_share = metrics.get("max_agent_reuse_share")

    if (
        isinstance(reuse_count, bool)
        or not isinstance(reuse_count, (int, float))
        or not math.isfinite(float(reuse_count))
        or float(reuse_count) < 0.0
    ):
        raise NodeValueKernelError("reuse_diversity_invalid_reuse_count")
    if (
        isinstance(distinct_agent_count, bool)
        or not isinstance(distinct_agent_count, (int, float))
        or not math.isfinite(float(distinct_agent_count))
        or float(distinct_agent_count) < 0.0
    ):
        raise NodeValueKernelError("reuse_diversity_invalid_distinct_agent_count")
    if (
        isinstance(max_agent_reuse_share, bool)
        or not isinstance(max_agent_reuse_share, (int, float))
        or not math.isfinite(float(max_agent_reuse_share))
        or float(max_agent_reuse_share) < 0.0
        or float(max_agent_reuse_share) > 1.0
    ):
        raise NodeValueKernelError("reuse_diversity_invalid_max_agent_reuse_share")

    reuse_count_f = float(reuse_count)
    distinct_agent_count_f = float(distinct_agent_count)
    max_agent_reuse_share_f = float(max_agent_reuse_share)

    if reuse_count_f > 0.0 and distinct_agent_count_f <= 0.0:
        raise NodeValueKernelError("reuse_diversity_missing_provenance")
    if reuse_count_f > 0.0 and distinct_agent_count_f > reuse_count_f + 1e-9:
        raise NodeValueKernelError("reuse_diversity_inconsistent_distinct_and_reuse")
    if reuse_count_f <= 0.0 and distinct_agent_count_f > 0.0:
        raise NodeValueKernelError("reuse_diversity_inconsistent_distinct_and_reuse")
    if reuse_count_f <= 0.0 and max_agent_reuse_share_f > 0.0:
        raise NodeValueKernelError("reuse_diversity_inconsistent_distinct_and_reuse")

    return {
        "reuse_count": reuse_count_f,
        "distinct_agent_count": distinct_agent_count_f,
        "max_agent_reuse_share": max_agent_reuse_share_f,
    }


def compute_reuse_diversity_multiplier(
    metrics: Mapping[str, object],
    *,
    policy: Mapping[str, object] = DEFAULT_REUSE_DIVERSITY_POLICY,
) -> float:
    resolved_policy = validate_reuse_diversity_policy(policy)
    resolved_metrics = validate_reuse_diversity_metrics(metrics)

    reuse_count = resolved_metrics["reuse_count"]
    distinct_agent_count = resolved_metrics["distinct_agent_count"]
    max_agent_reuse_share = resolved_metrics["max_agent_reuse_share"]

    if reuse_count <= 1.0:
        return 1.0

    distinct_ratio = min(
        1.0,
        distinct_agent_count / float(resolved_policy["min_distinct_agents"]),
    )

    max_share = resolved_policy["max_single_agent_share"]
    if max_agent_reuse_share <= max_share:
        concentration_factor = 1.0
    else:
        overflow = (max_agent_reuse_share - max_share) / max(1e-9, (1.0 - max_share))
        concentration_factor = max(0.0, 1.0 - overflow)

    raw_multiplier = distinct_ratio * concentration_factor
    bounded_multiplier = max(resolved_policy["penalty_floor"], min(1.0, raw_multiplier))
    return float(bounded_multiplier)
