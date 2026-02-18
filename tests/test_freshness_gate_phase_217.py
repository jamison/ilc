from __future__ import annotations

import pytest

from ilc_core.analysis.freshness_gate import (
    DEFAULT_FRESHNESS_GATE_POLICY,
    compute_freshness_gate,
    validate_freshness_gate_policy,
)
from ilc_core.analysis.node_value_kernel import compute_node_scores
from ilc_core.exceptions import NodeValueKernelError


def test_phase_217_genesis_exemption_stays_at_one_for_old_nodes() -> None:
    gate = compute_freshness_gate(
        {"age_epochs": 10_000.0, "is_genesis": True},
    )
    assert gate == pytest.approx(1.0)

    events: list[dict[str, object]] = [
        {
            "kind": "claim",
            "payload": {
                "id": "claim-1",
                "agent_id": "agent-1",
                "timestamp": "2026-02-18T00:00:00Z",
                "net_stake": 5.0,
                "parent_ids": ["root"],
                "target_id": "axiom:math:01",
                "target_age_epochs": 10_000.0,
                "target_is_genesis": True,
            },
        }
    ]
    rows = {row["node_id"]: row for row in compute_node_scores(events)}
    assert rows["axiom:math:01"]["freshness_gate"] == pytest.approx(1.0)


def test_phase_217_freshness_monotonic_and_bounded() -> None:
    policy = {
        "decay_lambda": 0.3,
        "freshness_floor": 0.85,
        "genesis_exempt": True,
    }
    ages = [0.0, 1.0, 2.0, 5.0, 10.0]
    gates = [
        compute_freshness_gate({"age_epochs": age, "is_genesis": False}, policy=policy)
        for age in ages
    ]

    assert gates[0] == pytest.approx(1.0)
    assert all(gates[idx] >= gates[idx + 1] for idx in range(len(gates) - 1))
    assert all(policy["freshness_floor"] <= gate <= 1.0 for gate in gates)
    assert gates[-1] >= policy["freshness_floor"]


def test_phase_217_invalid_inputs_fail_closed() -> None:
    with pytest.raises(NodeValueKernelError) as exc_age:
        compute_freshness_gate({"age_epochs": -1.0, "is_genesis": False})
    assert str(exc_age.value) == "freshness_gate_invalid_age_epochs"

    with pytest.raises(NodeValueKernelError) as exc_floor:
        validate_freshness_gate_policy(
            {
                "decay_lambda": 0.3,
                "freshness_floor": 0.8,
                "genesis_exempt": True,
            }
        )
    assert str(exc_floor.value) == "freshness_gate_floor_below_refutation_safety"

    with pytest.raises(NodeValueKernelError) as exc_lambda:
        validate_freshness_gate_policy(
            {
                "decay_lambda": float("inf"),
                "freshness_floor": 0.85,
                "genesis_exempt": True,
            }
        )
    assert str(exc_lambda.value) == "freshness_gate_invalid_decay_lambda"


def test_phase_217_governance_override_is_deterministic() -> None:
    policy = {
        "decay_lambda": 0.4,
        "freshness_floor": 0.9,
        "genesis_exempt": True,
    }
    events: list[dict[str, object]] = [
        {
            "kind": "claim",
            "payload": {
                "id": "claim-override",
                "agent_id": "agent-1",
                "timestamp": "2026-02-18T00:00:00Z",
                "net_stake": 4.0,
                "parent_ids": ["root"],
                "target_id": "old-node",
                "target_age_epochs": 9.0,
            },
        }
    ]

    rows_a = compute_node_scores(events, freshness_policy=policy)
    rows_b = compute_node_scores(events, freshness_policy=policy)

    assert rows_a == rows_b
    assert rows_a[0]["freshness_gate"] >= policy["freshness_floor"]


def test_phase_217_old_diverse_nodes_remain_sensible_with_freshness_and_diversity() -> None:
    events: list[dict[str, object]] = [
        {
            "kind": "claim",
            "payload": {
                "id": "old-diverse-1",
                "agent_id": "agent-1",
                "timestamp": "2026-02-18T00:00:00Z",
                "net_stake": 2.0,
                "parent_ids": ["root"],
                "target_id": "old-diverse",
                "target_age_epochs": 12.0,
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "old-diverse-2",
                "agent_id": "agent-2",
                "timestamp": "2026-02-18T00:01:00Z",
                "net_stake": 2.0,
                "parent_ids": ["root"],
                "target_id": "old-diverse",
                "target_age_epochs": 12.0,
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "old-diverse-3",
                "agent_id": "agent-3",
                "timestamp": "2026-02-18T00:02:00Z",
                "net_stake": 2.0,
                "parent_ids": ["root"],
                "target_id": "old-diverse",
                "target_age_epochs": 12.0,
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "old-concentrated-1",
                "agent_id": "agent-9",
                "timestamp": "2026-02-18T00:03:00Z",
                "net_stake": 2.0,
                "parent_ids": ["root"],
                "target_id": "old-concentrated",
                "target_age_epochs": 12.0,
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "old-concentrated-2",
                "agent_id": "agent-9",
                "timestamp": "2026-02-18T00:04:00Z",
                "net_stake": 2.0,
                "parent_ids": ["root"],
                "target_id": "old-concentrated",
                "target_age_epochs": 12.0,
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "old-concentrated-3",
                "agent_id": "agent-9",
                "timestamp": "2026-02-18T00:05:00Z",
                "net_stake": 2.0,
                "parent_ids": ["root"],
                "target_id": "old-concentrated",
                "target_age_epochs": 12.0,
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "fresh-diverse-1",
                "agent_id": "agent-1",
                "timestamp": "2026-02-18T00:06:00Z",
                "net_stake": 2.0,
                "parent_ids": ["root"],
                "target_id": "fresh-diverse",
                "target_age_epochs": 0.0,
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "fresh-diverse-2",
                "agent_id": "agent-2",
                "timestamp": "2026-02-18T00:07:00Z",
                "net_stake": 2.0,
                "parent_ids": ["root"],
                "target_id": "fresh-diverse",
                "target_age_epochs": 0.0,
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "fresh-diverse-3",
                "agent_id": "agent-3",
                "timestamp": "2026-02-18T00:08:00Z",
                "net_stake": 2.0,
                "parent_ids": ["root"],
                "target_id": "fresh-diverse",
                "target_age_epochs": 0.0,
            },
        },
    ]

    rows = {row["node_id"]: row for row in compute_node_scores(events)}
    old_diverse = rows["old-diverse"]
    old_concentrated = rows["old-concentrated"]
    fresh_diverse = rows["fresh-diverse"]

    assert old_diverse["freshness_gate"] == pytest.approx(old_concentrated["freshness_gate"])
    assert old_diverse["reuse_diversity_multiplier"] > old_concentrated["reuse_diversity_multiplier"]
    assert old_diverse["utility_flow"] > old_concentrated["utility_flow"]
    assert old_diverse["utility_flow"] < fresh_diverse["utility_flow"]
    assert DEFAULT_FRESHNESS_GATE_POLICY["freshness_floor"] <= old_diverse["freshness_gate"] <= 1.0
