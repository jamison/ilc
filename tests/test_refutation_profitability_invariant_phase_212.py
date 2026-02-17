from __future__ import annotations

import pytest

from ilc_core.analysis.utility_flow_rewards import (
    allocate_rewards_with_governor,
    assert_refutation_profitability_invariant,
    evaluate_refutation_profitability_invariant,
)
from ilc_core.exceptions import RewardGovernorError


def test_phase_212_refuter_net_reward_exceeds_validator_for_equal_effort_and_stake() -> None:
    report = allocate_rewards_with_governor(
        [
            {
                "node_id": "validator-node",
                "utility_flow": 10.0,
                "is_genesis": False,
                "action_kind": "validation",
                "stake_spent": 1.0,
                "effort_units": 5.0,
                "pairing_key": "claim-42",
            },
            {
                "node_id": "refuter-node",
                "utility_flow": 10.0,
                "is_genesis": False,
                "action_kind": "refutation",
                "stake_spent": 1.0,
                "effort_units": 5.0,
                "pairing_key": "claim-42",
            },
        ],
        policy={
            "epoch_reward_budget": 120.0,
            "max_genesis_share": 1.0,
            "min_flow_threshold": 0.0,
        },
    )

    allocations = {row["node_id"]: row for row in report["allocations"]}
    validator = allocations["validator-node"]
    refuter = allocations["refuter-node"]

    assert refuter["reward_amount"] > validator["reward_amount"]
    assert refuter["net_reward"] > validator["net_reward"]
    assert report["refutation_profitability"]["ok"] is True
    assert report["refutation_profitability"]["compared_groups"] == 1


def test_phase_212_invariant_check_rejects_epoch_rows_that_violate_constraint() -> None:
    violating_rows = [
        {
            "node_id": "validator-node",
            "is_genesis": False,
            "utility_flow": 10.0,
            "weighted_utility_flow": 10.0,
            "action_kind": "validation",
            "stake_spent": 2.0,
            "effort_units": 3.0,
            "pairing_key": "claim-x",
            "reward_share": 0.5,
            "reward_amount": 10.0,
            "net_reward": 8.0,
        },
        {
            "node_id": "refuter-node",
            "is_genesis": False,
            "utility_flow": 10.0,
            "weighted_utility_flow": 10.0,
            "action_kind": "refutation",
            "stake_spent": 2.0,
            "effort_units": 3.0,
            "pairing_key": "claim-x",
            "reward_share": 0.5,
            "reward_amount": 10.0,
            "net_reward": 8.0,
        },
    ]

    check = evaluate_refutation_profitability_invariant(violating_rows)
    assert check["ok"] is False
    assert "reward_invariant_refutation_not_more_profitable:claim-x" in check["errors"]

    with pytest.raises(RewardGovernorError) as exc_info:
        assert_refutation_profitability_invariant(violating_rows)
    assert str(exc_info.value) == "reward_invariant_refutation_not_more_profitable"

