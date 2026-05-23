# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import math
from typing import Mapping, TypedDict

from ilc_core.analysis.utility_flow_rewards import get_refutation_utility_multiplier
from ilc_core.exceptions import NodeValueKernelError


class FreshnessGatePolicy(TypedDict):
    decay_lambda: float
    freshness_floor: float
    genesis_exempt: bool


class FreshnessGateInput(TypedDict):
    age_epochs: float
    is_genesis: bool


_FRESHNESS_POLICY_REQUIRED_KEYS = {
    "decay_lambda",
    "freshness_floor",
    "genesis_exempt",
}

_MIN_REFUTATION_SAFE_FRESHNESS_FLOOR = (1.0 / get_refutation_utility_multiplier()) + 1e-9


DEFAULT_FRESHNESS_GATE_POLICY: FreshnessGatePolicy = {
    "decay_lambda": 0.25,
    "freshness_floor": 0.85,
    "genesis_exempt": True,
}


def validate_freshness_gate_policy(policy: Mapping[str, object]) -> FreshnessGatePolicy:
    if set(policy.keys()) != _FRESHNESS_POLICY_REQUIRED_KEYS:
        raise NodeValueKernelError("freshness_gate_invalid_policy_keys")

    decay_lambda = policy.get("decay_lambda")
    freshness_floor = policy.get("freshness_floor")
    genesis_exempt = policy.get("genesis_exempt")

    if (
        isinstance(decay_lambda, bool)
        or not isinstance(decay_lambda, (int, float))
        or not math.isfinite(float(decay_lambda))
        or float(decay_lambda) < 0.0
    ):
        raise NodeValueKernelError("freshness_gate_invalid_decay_lambda")
    if (
        isinstance(freshness_floor, bool)
        or not isinstance(freshness_floor, (int, float))
        or not math.isfinite(float(freshness_floor))
        or float(freshness_floor) <= 0.0
        or float(freshness_floor) > 1.0
    ):
        raise NodeValueKernelError("freshness_gate_invalid_freshness_floor")
    if not isinstance(genesis_exempt, bool):
        raise NodeValueKernelError("freshness_gate_invalid_genesis_exempt")

    normalized_floor = float(freshness_floor)
    if normalized_floor < _MIN_REFUTATION_SAFE_FRESHNESS_FLOOR:
        raise NodeValueKernelError("freshness_gate_floor_below_refutation_safety")

    return {
        "decay_lambda": float(decay_lambda),
        "freshness_floor": normalized_floor,
        "genesis_exempt": genesis_exempt,
    }


def validate_freshness_gate_input(payload: Mapping[str, object]) -> FreshnessGateInput:
    age_epochs = payload.get("age_epochs")
    is_genesis = payload.get("is_genesis")

    if (
        isinstance(age_epochs, bool)
        or not isinstance(age_epochs, (int, float))
        or not math.isfinite(float(age_epochs))
        or float(age_epochs) < 0.0
    ):
        raise NodeValueKernelError("freshness_gate_invalid_age_epochs")
    if not isinstance(is_genesis, bool):
        raise NodeValueKernelError("freshness_gate_invalid_is_genesis")

    return {
        "age_epochs": float(age_epochs),
        "is_genesis": is_genesis,
    }


def compute_freshness_gate(
    payload: Mapping[str, object],
    *,
    policy: Mapping[str, object] = DEFAULT_FRESHNESS_GATE_POLICY,
) -> float:
    resolved_policy = validate_freshness_gate_policy(policy)
    resolved_input = validate_freshness_gate_input(payload)

    if resolved_policy["genesis_exempt"] and resolved_input["is_genesis"]:
        return 1.0

    raw_decay = math.exp(-resolved_policy["decay_lambda"] * resolved_input["age_epochs"])
    bounded_gate = max(resolved_policy["freshness_floor"], min(1.0, raw_decay))
    return float(bounded_gate)
