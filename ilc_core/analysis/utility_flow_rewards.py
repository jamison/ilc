# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import logging
import math
from decimal import Decimal
from typing import Iterable, Literal, Mapping, TypedDict

from ilc_core.exceptions import RewardGovernorError

logger = logging.getLogger(__name__)


UtilityFlowActionKind = Literal["validation", "refutation", "other"]

_ACTION_UTILITY_MULTIPLIERS: dict[UtilityFlowActionKind, float] = {
    "validation": 1.0,
    "refutation": 1.2,
    "other": 1.0,
}


class UtilityFlowRewardInputRequired(TypedDict):
    node_id: str
    utility_flow: float
    is_genesis: bool


class UtilityFlowRewardInput(UtilityFlowRewardInputRequired, total=False):
    action_kind: UtilityFlowActionKind
    stake_spent: float
    effort_units: float
    pairing_key: str
    reuse_diversity_multiplier: float | None
    diversity_applied_in_scoring: bool
    freshness_gate: float | None
    freshness_applied_in_scoring: bool


class RewardGovernorPolicy(TypedDict):
    epoch_reward_budget: float
    max_genesis_share: float
    min_flow_threshold: float


class UtilityFlowRewardAllocation(TypedDict):
    node_id: str
    is_genesis: bool
    utility_flow: float
    weighted_utility_flow: float
    action_kind: UtilityFlowActionKind
    stake_spent: float
    effort_units: float
    pairing_key: str
    reuse_diversity_multiplier: float
    effective_diversity_multiplier: float
    diversity_applied_in_scoring: bool
    freshness_gate: float
    effective_freshness_multiplier: float
    freshness_applied_in_scoring: bool
    reward_share: float
    reward_amount: float
    net_reward: float


class RewardGovernorCheck(TypedDict):
    ok: bool
    errors: list[str]
    total_distributed: float
    budget: float
    genesis_share: float


class RefutationProfitabilityCheck(TypedDict):
    ok: bool
    errors: list[str]
    compared_groups: int
    skipped_rows: int


class UtilityFlowRewardReport(TypedDict):
    allocations: list[UtilityFlowRewardAllocation]
    governor: RewardGovernorCheck
    refutation_profitability: RefutationProfitabilityCheck
    unallocated_budget: float
    unallocated_budget_reason: str | None


DEFAULT_REWARD_GOVERNOR_POLICY: RewardGovernorPolicy = {
    "epoch_reward_budget": 100.0,
    "max_genesis_share": 0.50,
    "min_flow_threshold": 0.0,
}


def _non_negative_float(value: object, token: str) -> float:
    if isinstance(value, bool):
        raise RewardGovernorError(token)
    if isinstance(value, Decimal):
        if not value.is_finite() or value < Decimal("0"):
            raise RewardGovernorError(token)
        return float(value)
    if isinstance(value, (int, float)):
        normalized = float(value)
        if not math.isfinite(normalized) or normalized < 0.0:
            raise RewardGovernorError(token)
        return normalized
    raise RewardGovernorError(token)


def _unit_interval_float(value: object, token: str) -> float:
    normalized = _non_negative_float(value, token)
    if normalized > 1.0:
        raise RewardGovernorError(token)
    return normalized


def get_action_utility_multiplier(action_kind: UtilityFlowActionKind) -> float:
    return float(_ACTION_UTILITY_MULTIPLIERS[action_kind])


def get_refutation_utility_multiplier() -> float:
    return get_action_utility_multiplier("refutation")


def validate_reward_governor_policy(policy: Mapping[str, object]) -> RewardGovernorPolicy:
    required_keys = {"epoch_reward_budget", "max_genesis_share", "min_flow_threshold"}
    if set(policy.keys()) != required_keys:
        raise RewardGovernorError("reward_governor_invalid_policy_keys")

    budget = policy["epoch_reward_budget"]
    max_genesis_share = policy["max_genesis_share"]
    min_flow_threshold = policy["min_flow_threshold"]

    return {
        "epoch_reward_budget": _non_negative_float(
            budget,
            "reward_governor_invalid_budget",
        ),
        "max_genesis_share": _unit_interval_float(
            max_genesis_share,
            "reward_governor_invalid_max_genesis_share",
        ),
        "min_flow_threshold": _non_negative_float(
            min_flow_threshold,
            "reward_governor_invalid_min_flow_threshold",
        ),
    }


def _validate_input_row(row: Mapping[str, object]) -> UtilityFlowRewardInput:
    node_id = row.get("node_id")
    utility_flow = row.get("utility_flow")
    is_genesis = row.get("is_genesis")
    action_kind = row.get("action_kind", "validation")
    stake_spent = row.get("stake_spent", 0.0)
    effort_units = row.get("effort_units", utility_flow)
    pairing_key = row.get("pairing_key", "")
    reuse_diversity_multiplier = row.get("reuse_diversity_multiplier")
    diversity_applied_in_scoring = row.get("diversity_applied_in_scoring", False)
    freshness_gate = row.get("freshness_gate")
    freshness_applied_in_scoring = row.get("freshness_applied_in_scoring", False)

    if not isinstance(node_id, str) or node_id == "":
        raise RewardGovernorError("reward_governor_invalid_node_id")
    if not isinstance(is_genesis, bool):
        raise RewardGovernorError("reward_governor_invalid_is_genesis")
    if action_kind not in _ACTION_UTILITY_MULTIPLIERS:
        raise RewardGovernorError("reward_governor_invalid_action_kind")
    if not isinstance(pairing_key, str):
        raise RewardGovernorError("reward_governor_invalid_pairing_key")
    normalized_utility_flow = _non_negative_float(
        utility_flow,
        "reward_governor_invalid_utility_flow",
    )
    normalized_stake_spent = _non_negative_float(
        stake_spent,
        "reward_governor_invalid_stake_spent",
    )
    normalized_effort_units = _non_negative_float(
        effort_units,
        "reward_governor_invalid_effort_units",
    )
    if reuse_diversity_multiplier is not None:
        normalized_reuse_diversity_multiplier = _unit_interval_float(
            reuse_diversity_multiplier,
            "reward_governor_invalid_reuse_diversity_multiplier",
        )
    else:
        normalized_reuse_diversity_multiplier = None
    if not isinstance(diversity_applied_in_scoring, bool):
        raise RewardGovernorError("reward_governor_invalid_diversity_applied_in_scoring")
    if freshness_gate is not None:
        normalized_freshness_gate = _unit_interval_float(
            freshness_gate,
            "reward_governor_invalid_freshness_gate",
        )
    else:
        normalized_freshness_gate = None
    if not isinstance(freshness_applied_in_scoring, bool):
        raise RewardGovernorError("reward_governor_invalid_freshness_applied_in_scoring")

    return {
        "node_id": node_id,
        "utility_flow": normalized_utility_flow,
        "is_genesis": is_genesis,
        "action_kind": action_kind,
        "stake_spent": normalized_stake_spent,
        "effort_units": normalized_effort_units,
        "pairing_key": pairing_key,
        "reuse_diversity_multiplier": normalized_reuse_diversity_multiplier,
        "diversity_applied_in_scoring": diversity_applied_in_scoring,
        "freshness_gate": normalized_freshness_gate,
        "freshness_applied_in_scoring": freshness_applied_in_scoring,
    }


def _resolve_effective_diversity_multiplier(row: UtilityFlowRewardInput) -> float:
    if row["diversity_applied_in_scoring"]:
        return 1.0

    provided_multiplier = row["reuse_diversity_multiplier"]
    if provided_multiplier is None:
        logger.warning(
            "reward_governor_missing_reuse_diversity_multiplier_fallback:%s",
            row["node_id"],
        )
        return 1.0
    return float(provided_multiplier)


def _resolve_effective_freshness_multiplier(row: UtilityFlowRewardInput) -> float:
    if row["freshness_applied_in_scoring"]:
        return 1.0

    provided_gate = row["freshness_gate"]
    if provided_gate is None:
        logger.warning(
            "reward_governor_missing_freshness_gate_fallback:%s",
            row["node_id"],
        )
        return 1.0
    return float(provided_gate)


def compute_reward_allocations(
    rows: Iterable[Mapping[str, object]],
    *,
    policy: Mapping[str, object] = DEFAULT_REWARD_GOVERNOR_POLICY,
) -> list[UtilityFlowRewardAllocation]:
    resolved_policy = validate_reward_governor_policy(policy)

    normalized_rows: list[UtilityFlowRewardInput] = []
    seen_ids: set[str] = set()
    for raw_row in rows:
        row = _validate_input_row(raw_row)
        if row["node_id"] in seen_ids:
            raise RewardGovernorError("reward_governor_duplicate_node_id")
        seen_ids.add(row["node_id"])
        normalized_rows.append(row)

    threshold = resolved_policy["min_flow_threshold"]
    eligible_rows = [
        row for row in normalized_rows if row["utility_flow"] >= threshold and row["utility_flow"] > 0.0
    ]
    effective_diversity_multiplier_by_node: dict[str, float] = {
        row["node_id"]: _resolve_effective_diversity_multiplier(row)
        for row in eligible_rows
    }
    effective_freshness_multiplier_by_node: dict[str, float] = {
        row["node_id"]: _resolve_effective_freshness_multiplier(row)
        for row in eligible_rows
    }
    total_flow = sum(
        row["utility_flow"]
        * _ACTION_UTILITY_MULTIPLIERS[row["action_kind"]]
        * effective_diversity_multiplier_by_node[row["node_id"]]
        * effective_freshness_multiplier_by_node[row["node_id"]]
        for row in eligible_rows
    )

    budget = resolved_policy["epoch_reward_budget"]
    allocations: list[UtilityFlowRewardAllocation] = []
    for row in sorted(eligible_rows, key=lambda item: item["node_id"]):
        effective_diversity_multiplier = effective_diversity_multiplier_by_node[row["node_id"]]
        effective_freshness_multiplier = effective_freshness_multiplier_by_node[row["node_id"]]

        weighted_flow = (
            row["utility_flow"]
            * _ACTION_UTILITY_MULTIPLIERS[row["action_kind"]]
            * effective_diversity_multiplier
            * effective_freshness_multiplier
        )
        reward_share = (weighted_flow / total_flow) if total_flow > 0.0 else 0.0
        reward_amount = budget * reward_share
        allocations.append(
            {
                "node_id": row["node_id"],
                "is_genesis": row["is_genesis"],
                "utility_flow": row["utility_flow"],
                "weighted_utility_flow": weighted_flow,
                "action_kind": row["action_kind"],
                "stake_spent": row["stake_spent"],
                "effort_units": row["effort_units"],
                "pairing_key": row["pairing_key"],
                "reuse_diversity_multiplier": (
                    float(row["reuse_diversity_multiplier"])
                    if row["reuse_diversity_multiplier"] is not None
                    else 1.0
                ),
                "effective_diversity_multiplier": effective_diversity_multiplier,
                "diversity_applied_in_scoring": row["diversity_applied_in_scoring"],
                "freshness_gate": (
                    float(row["freshness_gate"])
                    if row["freshness_gate"] is not None
                    else 1.0
                ),
                "effective_freshness_multiplier": effective_freshness_multiplier,
                "freshness_applied_in_scoring": row["freshness_applied_in_scoring"],
                "reward_share": reward_share,
                "reward_amount": reward_amount,
                "net_reward": reward_amount - row["stake_spent"],
            }
        )
    return allocations


def evaluate_refutation_profitability_invariant(
    allocations: Iterable[UtilityFlowRewardAllocation],
    *,
    tolerance: float = 1e-9,
) -> RefutationProfitabilityCheck:
    grouped_rewards: dict[tuple[str, float, float], dict[str, list[float]]] = {}
    skipped_rows = 0

    for row in allocations:
        action_kind = row["action_kind"]
        if action_kind not in ("validation", "refutation"):
            skipped_rows += 1
            continue

        grouping_key = (
            row["pairing_key"],
            row["stake_spent"],
            row["effort_units"],
        )
        group = grouped_rewards.setdefault(
            grouping_key,
            {"validation": [], "refutation": []},
        )
        group[action_kind].append(float(row["net_reward"]))

    errors: list[str] = []
    compared_groups = 0
    for key in sorted(grouped_rewards.keys()):
        group = grouped_rewards[key]
        validator_rewards = group["validation"]
        refuter_rewards = group["refutation"]
        if not validator_rewards or not refuter_rewards:
            continue
        compared_groups += 1
        if min(refuter_rewards) <= max(validator_rewards) + tolerance:
            pairing = key[0] if key[0] else "_global"
            errors.append(f"reward_invariant_refutation_not_more_profitable:{pairing}")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "compared_groups": compared_groups,
        "skipped_rows": skipped_rows,
    }


def assert_refutation_profitability_invariant(
    allocations: Iterable[UtilityFlowRewardAllocation],
    *,
    tolerance: float = 1e-9,
) -> RefutationProfitabilityCheck:
    check = evaluate_refutation_profitability_invariant(
        allocations,
        tolerance=tolerance,
    )
    if not check["ok"]:
        raise RewardGovernorError("reward_invariant_refutation_not_more_profitable")
    return check


def evaluate_reward_governor(
    allocations: Iterable[UtilityFlowRewardAllocation],
    *,
    policy: Mapping[str, object] = DEFAULT_REWARD_GOVERNOR_POLICY,
) -> RewardGovernorCheck:
    resolved_policy = validate_reward_governor_policy(policy)
    rows = list(allocations)

    total_distributed = sum(float(row["reward_amount"]) for row in rows)
    budget = resolved_policy["epoch_reward_budget"]
    genesis_total = sum(float(row["reward_amount"]) for row in rows if bool(row["is_genesis"]))
    genesis_share = (genesis_total / total_distributed) if total_distributed > 0.0 else 0.0

    errors: list[str] = []
    if total_distributed > budget + 1e-9:
        errors.append("reward_governor_budget_exceeded")
    if genesis_share > resolved_policy["max_genesis_share"] + 1e-9:
        errors.append("reward_governor_genesis_share_exceeded")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "total_distributed": total_distributed,
        "budget": budget,
        "genesis_share": genesis_share,
    }


def allocate_rewards_with_governor(
    rows: Iterable[Mapping[str, object]],
    *,
    policy: Mapping[str, object] = DEFAULT_REWARD_GOVERNOR_POLICY,
) -> UtilityFlowRewardReport:
    allocations = compute_reward_allocations(rows, policy=policy)
    governor = evaluate_reward_governor(allocations, policy=policy)
    invariant = assert_refutation_profitability_invariant(allocations)
    unallocated_budget = max(0.0, governor["budget"] - governor["total_distributed"])
    return {
        "allocations": allocations,
        "governor": governor,
        "refutation_profitability": invariant,
        "unallocated_budget": unallocated_budget,
        "unallocated_budget_reason": "zero_eligible_utility_flow" if not allocations else None,
    }
