from decimal import Decimal

import pytest

from ilc_core.analysis.governance_weight import compute_governance_weights
from ilc_core.exceptions import GovernanceWeightError


def test_non_genesis_inactivity_decay_reduces_weight() -> None:
    rows = [
        {
            "agent_id": "agent-fast",
            "base_weight": Decimal("2"),
            "quality_score": Decimal("1"),
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": Decimal("0"),
        },
        {
            "agent_id": "agent-stale",
            "base_weight": Decimal("2"),
            "quality_score": Decimal("1"),
            "inactivity_epochs": 10,
            "is_genesis": False,
            "contribution_bonus": Decimal("0"),
        },
    ]

    output = compute_governance_weights(rows)
    fast = next(row for row in output if row["agent_id"] == "agent-fast")
    stale = next(row for row in output if row["agent_id"] == "agent-stale")

    assert isinstance(fast["governance_weight"], Decimal)
    assert fast["governance_weight"] > stale["governance_weight"]


def test_genesis_baseline_and_bonus_policy_switch() -> None:
    rows = [
        {
            "agent_id": "genesis",
            "base_weight": Decimal("0"),
            "quality_score": Decimal("0"),
            "inactivity_epochs": 99,
            "is_genesis": True,
            "contribution_bonus": Decimal("2.5"),
        }
    ]

    with_bonus = compute_governance_weights(rows)
    assert with_bonus[0]["governance_weight"] == Decimal("3.5")

    without_bonus = compute_governance_weights(
        rows,
        policy={
            "inactivity_decay_lambda": Decimal("0.05"),
            "genesis_baseline_weight": Decimal("1"),
            "allow_genesis_bonus": False,
        },
    )
    assert without_bonus[0]["governance_weight"] == Decimal("1")


def test_vote_share_normalization_and_zero_total_behavior() -> None:
    rows = [
        {
            "agent_id": "a",
            "base_weight": Decimal("1"),
            "quality_score": Decimal("1"),
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": Decimal("0"),
        },
        {
            "agent_id": "b",
            "base_weight": Decimal("1"),
            "quality_score": Decimal("1"),
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": Decimal("0"),
        },
    ]
    output = compute_governance_weights(rows)
    assert sum((row["vote_share"] for row in output), Decimal("0")) == Decimal("1")

    zero_total_output = compute_governance_weights(
        [
            {
                "agent_id": "a",
                "base_weight": Decimal("0"),
                "quality_score": Decimal("0"),
                "inactivity_epochs": 0,
                "is_genesis": False,
                "contribution_bonus": Decimal("0"),
            }
        ],
        policy={
            "inactivity_decay_lambda": Decimal("0.05"),
            "genesis_baseline_weight": Decimal("0"),
            "allow_genesis_bonus": False,
        },
    )
    assert zero_total_output[0]["vote_share"] == Decimal("0")


def test_equal_three_agent_vote_shares_close_phase_1356_precision_gap() -> None:
    rows = [
        {
            "agent_id": agent_id,
            "base_weight": Decimal("1"),
            "quality_score": Decimal("1"),
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": Decimal("0"),
        }
        for agent_id in ("a", "b", "c")
    ]

    output = compute_governance_weights(rows)
    assert [row["agent_id"] for row in output] == ["a", "b", "c"]
    assert sum((row["vote_share"] for row in output), Decimal("0")) == Decimal("1")
    assert output[0]["vote_share"] == Decimal("0.3333333333333333333333333333")
    assert output[1]["vote_share"] == Decimal("0.3333333333333333333333333333")
    assert output[2]["vote_share"] == Decimal("0.3333333333333333333333333334")


def test_finite_float_input_rejected_after_phase_1357() -> None:
    with pytest.raises(GovernanceWeightError) as exc_info:
        compute_governance_weights(
            [
                {
                    "agent_id": "floaty",
                    "base_weight": 1.0,
                    "quality_score": Decimal("1"),
                    "inactivity_epochs": 0,
                    "is_genesis": False,
                    "contribution_bonus": Decimal("0"),
                }
            ]
        )
    assert str(exc_info.value) == "governance_weight_invalid_base_weight"


def test_duplicate_agent_id_rejected() -> None:
    rows = [
        {
            "agent_id": "dup",
            "base_weight": Decimal("1"),
            "quality_score": Decimal("1"),
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": Decimal("0"),
        },
        {
            "agent_id": "dup",
            "base_weight": Decimal("1"),
            "quality_score": Decimal("1"),
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": Decimal("0"),
        },
    ]

    with pytest.raises(GovernanceWeightError) as exc_info:
        compute_governance_weights(rows)
    assert str(exc_info.value) == "governance_weight_duplicate_agent_id"
