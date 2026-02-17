from __future__ import annotations

import pytest

from ilc_core.analysis.reuse_diversity_invariants import (
    DEFAULT_REUSE_DIVERSITY_POLICY,
    compute_reuse_diversity_multiplier,
    validate_reuse_diversity_policy,
)
from ilc_core.analysis.utility_flow_rewards import allocate_rewards_with_governor
from ilc_core.exceptions import NodeValueKernelError


def test_phase_216_policy_validation_requires_refutation_safe_floor() -> None:
    validate_reuse_diversity_policy(DEFAULT_REUSE_DIVERSITY_POLICY)

    with pytest.raises(NodeValueKernelError) as exc_info:
        validate_reuse_diversity_policy(
            {
                "min_distinct_agents": 2,
                "max_single_agent_share": 0.75,
                "penalty_floor": 0.8,
            }
        )
    assert str(exc_info.value) == "reuse_diversity_penalty_floor_below_refutation_safety"


def test_phase_216_missing_provenance_fails_closed_for_scoring_metrics() -> None:
    with pytest.raises(NodeValueKernelError) as exc_info:
        compute_reuse_diversity_multiplier(
            {
                "reuse_count": 2.0,
                "distinct_agent_count": 0.0,
                "max_agent_reuse_share": 1.0,
            }
        )
    assert str(exc_info.value) == "reuse_diversity_missing_provenance"


def test_phase_216_multiplier_is_deterministic_and_monotonic_by_diversity() -> None:
    concentrated = {
        "reuse_count": 4.0,
        "distinct_agent_count": 1.0,
        "max_agent_reuse_share": 1.0,
    }
    diversified = {
        "reuse_count": 4.0,
        "distinct_agent_count": 3.0,
        "max_agent_reuse_share": 0.5,
    }

    concentrated_a = compute_reuse_diversity_multiplier(concentrated)
    concentrated_b = compute_reuse_diversity_multiplier(concentrated)
    diversified_out = compute_reuse_diversity_multiplier(diversified)

    assert concentrated_a == pytest.approx(concentrated_b)
    assert DEFAULT_REUSE_DIVERSITY_POLICY["penalty_floor"] <= concentrated_a <= 1.0
    assert DEFAULT_REUSE_DIVERSITY_POLICY["penalty_floor"] <= diversified_out <= 1.0
    assert diversified_out > concentrated_a


def test_phase_216_refuter_still_wins_with_lower_diversity_same_pairing() -> None:
    report = allocate_rewards_with_governor(
        [
            {
                "node_id": "validator-node",
                "utility_flow": 10.0,
                "is_genesis": False,
                "action_kind": "validation",
                "pairing_key": "claim-216",
                "stake_spent": 1.0,
                "effort_units": 3.0,
                "reuse_diversity_multiplier": 1.0,
            },
            {
                "node_id": "refuter-node",
                "utility_flow": 10.0,
                "is_genesis": False,
                "action_kind": "refutation",
                "pairing_key": "claim-216",
                "stake_spent": 1.0,
                "effort_units": 3.0,
                "reuse_diversity_multiplier": 0.85,
            },
        ],
        policy={
            "epoch_reward_budget": 120.0,
            "max_genesis_share": 1.0,
            "min_flow_threshold": 0.0,
        },
    )

    rows = {row["node_id"]: row for row in report["allocations"]}
    validator = rows["validator-node"]
    refuter = rows["refuter-node"]

    assert refuter["effective_diversity_multiplier"] < validator["effective_diversity_multiplier"]
    assert refuter["reward_amount"] > validator["reward_amount"]
    assert report["refutation_profitability"]["ok"] is True
