import pytest

from ilc_core.analysis.governance_weight import compute_governance_weights
from ilc_core.exceptions import GovernanceWeightError


def test_non_genesis_inactivity_decay_reduces_weight() -> None:
    rows = [
        {
            "agent_id": "agent-fast",
            "base_weight": 2.0,
            "quality_score": 1.0,
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": 0.0,
        },
        {
            "agent_id": "agent-stale",
            "base_weight": 2.0,
            "quality_score": 1.0,
            "inactivity_epochs": 10,
            "is_genesis": False,
            "contribution_bonus": 0.0,
        },
    ]

    output = compute_governance_weights(rows)
    fast = next(row for row in output if row["agent_id"] == "agent-fast")
    stale = next(row for row in output if row["agent_id"] == "agent-stale")

    assert fast["governance_weight"] > stale["governance_weight"]


def test_genesis_baseline_and_bonus_policy_switch() -> None:
    rows = [
        {
            "agent_id": "genesis",
            "base_weight": 0.0,
            "quality_score": 0.0,
            "inactivity_epochs": 99,
            "is_genesis": True,
            "contribution_bonus": 2.5,
        }
    ]

    with_bonus = compute_governance_weights(rows)
    assert with_bonus[0]["governance_weight"] == pytest.approx(3.5)

    without_bonus = compute_governance_weights(
        rows,
        policy={
            "inactivity_decay_lambda": 0.05,
            "genesis_baseline_weight": 1.0,
            "allow_genesis_bonus": False,
        },
    )
    assert without_bonus[0]["governance_weight"] == pytest.approx(1.0)


def test_vote_share_normalization_and_zero_total_behavior() -> None:
    rows = [
        {
            "agent_id": "a",
            "base_weight": 1.0,
            "quality_score": 1.0,
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": 0.0,
        },
        {
            "agent_id": "b",
            "base_weight": 1.0,
            "quality_score": 1.0,
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": 0.0,
        },
    ]
    output = compute_governance_weights(rows)
    assert sum(row["vote_share"] for row in output) == pytest.approx(1.0)

    zero_total_output = compute_governance_weights(
        [
            {
                "agent_id": "a",
                "base_weight": 0.0,
                "quality_score": 0.0,
                "inactivity_epochs": 0,
                "is_genesis": False,
                "contribution_bonus": 0.0,
            }
        ],
        policy={
            "inactivity_decay_lambda": 0.05,
            "genesis_baseline_weight": 0.0,
            "allow_genesis_bonus": False,
        },
    )
    assert zero_total_output[0]["vote_share"] == 0.0


def test_duplicate_agent_id_rejected() -> None:
    rows = [
        {
            "agent_id": "dup",
            "base_weight": 1.0,
            "quality_score": 1.0,
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": 0.0,
        },
        {
            "agent_id": "dup",
            "base_weight": 1.0,
            "quality_score": 1.0,
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": 0.0,
        },
    ]

    with pytest.raises(GovernanceWeightError) as exc_info:
        compute_governance_weights(rows)
    assert str(exc_info.value) == "governance_weight_duplicate_agent_id"
