import pytest

from ilc_core.analysis.utility_flow_rewards import (
    allocate_rewards_with_governor,
    compute_reward_allocations,
    evaluate_reward_governor,
)
from ilc_core.exceptions import RewardGovernorError


def test_reward_allocations_are_deterministic_and_budget_bounded() -> None:
    rows = [
        {"node_id": "node-b", "utility_flow": 1.0, "is_genesis": False},
        {"node_id": "node-a", "utility_flow": 3.0, "is_genesis": False},
    ]

    allocations_a = compute_reward_allocations(rows)
    allocations_b = compute_reward_allocations(rows)

    assert allocations_a == allocations_b
    assert [row["node_id"] for row in allocations_a] == ["node-a", "node-b"]
    assert sum(row["reward_amount"] for row in allocations_a) == pytest.approx(100.0)


def test_governor_detects_genesis_share_cap_breach() -> None:
    rows = [
        {"node_id": "genesis", "utility_flow": 9.0, "is_genesis": True},
        {"node_id": "node-a", "utility_flow": 1.0, "is_genesis": False},
    ]
    policy = {
        "epoch_reward_budget": 100.0,
        "max_genesis_share": 0.2,
        "min_flow_threshold": 0.0,
    }

    allocations = compute_reward_allocations(rows, policy=policy)
    governor = evaluate_reward_governor(allocations, policy=policy)

    assert governor["ok"] is False
    assert "reward_governor_genesis_share_exceeded" in governor["errors"]


def test_min_threshold_filters_low_flows() -> None:
    rows = [
        {"node_id": "node-a", "utility_flow": 0.01, "is_genesis": False},
        {"node_id": "node-b", "utility_flow": 1.0, "is_genesis": False},
    ]
    report = allocate_rewards_with_governor(
        rows,
        policy={
            "epoch_reward_budget": 50.0,
            "max_genesis_share": 1.0,
            "min_flow_threshold": 0.1,
        },
    )

    assert len(report["allocations"]) == 1
    assert report["allocations"][0]["node_id"] == "node-b"
    assert report["governor"]["ok"] is True


def test_duplicate_node_id_rejected() -> None:
    rows = [
        {"node_id": "dup", "utility_flow": 1.0, "is_genesis": False},
        {"node_id": "dup", "utility_flow": 2.0, "is_genesis": False},
    ]

    with pytest.raises(RewardGovernorError) as exc_info:
        compute_reward_allocations(rows)
    assert str(exc_info.value) == "reward_governor_duplicate_node_id"
