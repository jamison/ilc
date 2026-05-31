import pytest
from decimal import Decimal

from ilc_core.analysis.node_value_kernel import (
    DEFAULT_EW_WEIGHTS,
    build_node_evidence_vectors,
    compute_node_scores,
    compute_utility_flow,
    validate_ew_weights,
)
from ilc_core.exceptions import NodeValueKernelError


def _sample_events() -> list[dict[str, object]]:
    return [
        {
            "kind": "claim",
            "payload": {
                "id": "node-a",
                "agent_id": "agent-1",
                "timestamp": "2026-02-16T00:00:00Z",
                "net_stake": 10.0,
                "parent_ids": ["root"],
                "target_id": "genesis-node",
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "node-b",
                "agent_id": "agent-2",
                "timestamp": "2026-02-16T00:01:00Z",
                "net_stake": 6.0,
                "parent_ids": ["node-a"],
                "target_id": "node-a",
            },
        },
        {
            "kind": "refutation",
            "payload": {
                "id": "refute-1",
                "agent_id": "agent-3",
                "timestamp": "2026-02-16T00:02:00Z",
                "target_id": "node-a",
                "net_stake": 2.0,
            },
        },
    ]


def test_compute_node_scores_is_deterministic_and_sorted() -> None:
    scores_first = compute_node_scores(_sample_events())
    scores_second = compute_node_scores(_sample_events())

    assert scores_first == scores_second
    assert [row["node_id"] for row in scores_first] == sorted(
        row["node_id"] for row in scores_first
    )
    assert any(row["node_id"] == "node-a" for row in scores_first)
    node_a = next(row for row in scores_first if row["node_id"] == "node-a")
    assert isinstance(node_a["epistemic_weight"], Decimal)
    assert node_a["epistemic_weight"] >= Decimal("0")
    assert node_a["utility_flow"] >= Decimal("0")
    assert Decimal("0") <= node_a["reuse_diversity_multiplier"] <= Decimal("1")


def test_validate_weights_requires_expected_keys_and_sum_one() -> None:
    validate_ew_weights(DEFAULT_EW_WEIGHTS)

    with pytest.raises(NodeValueKernelError) as exc_keys:
        validate_ew_weights({"reuse": 1.0})
    assert str(exc_keys.value) == "node_value_kernel_invalid_weight_keys"

    with pytest.raises(NodeValueKernelError) as exc_sum:
        validate_ew_weights(
            {
                "reuse": 0.4,
                "contradiction_resilience": 0.3,
                "validation_integrity": 0.2,
                "path_uplift": 0.2,
            }
        )
    assert str(exc_sum.value) == "node_value_kernel_weight_sum_not_one"


def test_utility_flow_gate_contracts() -> None:
    assert compute_utility_flow(Decimal("0.5"), Decimal("2.0"), Decimal("1.0")) == Decimal("1.000")

    with pytest.raises(NodeValueKernelError) as exc_usage:
        compute_utility_flow(0.5, -1.0, 1.0)
    assert str(exc_usage.value) == "node_value_kernel_negative_usage_window"

    with pytest.raises(NodeValueKernelError) as exc_freshness:
        compute_utility_flow(0.5, 1.0, 1.5)
    assert str(exc_freshness.value) == "node_value_kernel_invalid_freshness_gate"


def test_compute_node_scores_consumes_path_lift_witnesses_when_provided() -> None:
    path_witnesses = [
        {
            "witness_id": "w1",
            "source_id": "root",
            "target_id": "node-b",
            "nodes": [
                {"node_id": "genesis-node", "agent_id": "agent-0"},
                {"node_id": "node-a", "agent_id": "agent-1"},
                {"node_id": "node-b", "agent_id": "agent-2"},
            ],
            "path_weight": 1.0,
            "path_cost": 3.0,
        },
        {
            "witness_id": "w2",
            "source_id": "root",
            "target_id": "node-a",
            "nodes": [
                {"node_id": "genesis-node", "agent_id": "agent-0"},
                {"node_id": "node-a", "agent_id": "agent-1"},
            ],
            "path_weight": 1.0,
            "path_cost": 2.0,
        },
    ]

    baseline_rows = {
        row["node_id"]: row for row in compute_node_scores(_sample_events())
    }
    lifted_rows = {
        row["node_id"]: row
        for row in compute_node_scores(_sample_events(), path_witnesses=path_witnesses)
    }

    assert lifted_rows["node-a"]["path_component"] == Decimal("1")
    assert lifted_rows["node-b"]["path_component"] == Decimal("0.4")
    assert lifted_rows["node-a"]["path_component"] > baseline_rows["node-a"]["path_component"]


def test_compute_node_scores_penalizes_low_diversity_reuse() -> None:
    low_diversity_events = [
        {
            "kind": "claim",
            "payload": {
                "id": "claim-low-1",
                "agent_id": "agent-1",
                "timestamp": "2026-02-16T00:00:00Z",
                "net_stake": 4.0,
                "parent_ids": ["root"],
                "target_id": "target-low",
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "claim-low-2",
                "agent_id": "agent-1",
                "timestamp": "2026-02-16T00:01:00Z",
                "net_stake": 4.0,
                "parent_ids": ["root"],
                "target_id": "target-low",
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "claim-high-1",
                "agent_id": "agent-2",
                "timestamp": "2026-02-16T00:02:00Z",
                "net_stake": 4.0,
                "parent_ids": ["root"],
                "target_id": "target-high",
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "claim-high-2",
                "agent_id": "agent-3",
                "timestamp": "2026-02-16T00:03:00Z",
                "net_stake": 4.0,
                "parent_ids": ["root"],
                "target_id": "target-high",
            },
        },
    ]

    rows = {row["node_id"]: row for row in compute_node_scores(low_diversity_events)}
    low = rows["target-low"]
    high = rows["target-high"]

    assert low["reuse_diversity_multiplier"] < high["reuse_diversity_multiplier"]
    assert low["reuse_component"] < high["reuse_component"]


def test_refutors_do_not_inflate_unique_agents_using() -> None:
    events = [
        {
            "kind": "claim",
            "payload": {
                "id": "claim-1",
                "agent_id": "claim-agent",
                "timestamp": "2026-02-16T00:00:00Z",
                "net_stake": 4.0,
                "parent_ids": ["root"],
                "target_id": "target-node",
            },
        },
        {
            "kind": "refutation",
            "payload": {
                "id": "refute-1",
                "agent_id": "refuting-agent-1",
                "timestamp": "2026-02-16T00:01:00Z",
                "target_id": "target-node",
                "net_stake": 1.0,
            },
        },
        {
            "kind": "refutation",
            "payload": {
                "id": "refute-2",
                "agent_id": "refuting-agent-2",
                "timestamp": "2026-02-16T00:02:00Z",
                "target_id": "target-node",
                "net_stake": 1.0,
            },
        },
    ]

    evidence = {row["node_id"]: row for row in build_node_evidence_vectors(events)}

    assert evidence["target-node"]["unique_agents_using"] == Decimal("1")
    assert evidence["target-node"]["reuse_count"] == Decimal("1")
    assert evidence["target-node"]["refutation_stake_against"] == Decimal("2")
