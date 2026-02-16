from __future__ import annotations

from typing import Iterable, Mapping, TypedDict

from ilc_core.exceptions import RewardGovernorError


class UtilityFlowRewardInput(TypedDict):
    node_id: str
    utility_flow: float
    is_genesis: bool


class RewardGovernorPolicy(TypedDict):
    epoch_reward_budget: float
    max_genesis_share: float
    min_flow_threshold: float


class UtilityFlowRewardAllocation(TypedDict):
    node_id: str
    is_genesis: bool
    utility_flow: float
    reward_share: float
    reward_amount: float


class RewardGovernorCheck(TypedDict):
    ok: bool
    errors: list[str]
    total_distributed: float
    budget: float
    genesis_share: float


class UtilityFlowRewardReport(TypedDict):
    allocations: list[UtilityFlowRewardAllocation]
    governor: RewardGovernorCheck


DEFAULT_REWARD_GOVERNOR_POLICY: RewardGovernorPolicy = {
    "epoch_reward_budget": 100.0,
    "max_genesis_share": 0.50,
    "min_flow_threshold": 0.0,
}


def validate_reward_governor_policy(policy: Mapping[str, object]) -> RewardGovernorPolicy:
    required_keys = {"epoch_reward_budget", "max_genesis_share", "min_flow_threshold"}
    if set(policy.keys()) != required_keys:
        raise RewardGovernorError("reward_governor_invalid_policy_keys")

    budget = policy["epoch_reward_budget"]
    max_genesis_share = policy["max_genesis_share"]
    min_flow_threshold = policy["min_flow_threshold"]

    if not isinstance(budget, (int, float)) or budget < 0.0:
        raise RewardGovernorError("reward_governor_invalid_budget")
    if not isinstance(max_genesis_share, (int, float)) or max_genesis_share < 0.0 or max_genesis_share > 1.0:
        raise RewardGovernorError("reward_governor_invalid_max_genesis_share")
    if not isinstance(min_flow_threshold, (int, float)) or min_flow_threshold < 0.0:
        raise RewardGovernorError("reward_governor_invalid_min_flow_threshold")

    return {
        "epoch_reward_budget": float(budget),
        "max_genesis_share": float(max_genesis_share),
        "min_flow_threshold": float(min_flow_threshold),
    }


def _validate_input_row(row: Mapping[str, object]) -> UtilityFlowRewardInput:
    node_id = row.get("node_id")
    utility_flow = row.get("utility_flow")
    is_genesis = row.get("is_genesis")

    if not isinstance(node_id, str) or node_id == "":
        raise RewardGovernorError("reward_governor_invalid_node_id")
    if not isinstance(utility_flow, (int, float)) or utility_flow < 0.0:
        raise RewardGovernorError("reward_governor_invalid_utility_flow")
    if not isinstance(is_genesis, bool):
        raise RewardGovernorError("reward_governor_invalid_is_genesis")

    return {
        "node_id": node_id,
        "utility_flow": float(utility_flow),
        "is_genesis": is_genesis,
    }


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
    eligible_rows = [row for row in normalized_rows if row["utility_flow"] >= threshold and row["utility_flow"] > 0.0]
    total_flow = sum(row["utility_flow"] for row in eligible_rows)

    budget = resolved_policy["epoch_reward_budget"]
    allocations: list[UtilityFlowRewardAllocation] = []
    for row in sorted(eligible_rows, key=lambda item: item["node_id"]):
        reward_share = (row["utility_flow"] / total_flow) if total_flow > 0.0 else 0.0
        allocations.append(
            {
                "node_id": row["node_id"],
                "is_genesis": row["is_genesis"],
                "utility_flow": row["utility_flow"],
                "reward_share": reward_share,
                "reward_amount": budget * reward_share,
            }
        )
    return allocations


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
    return {
        "allocations": allocations,
        "governor": governor,
    }
