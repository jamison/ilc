from __future__ import annotations

import pytest

from ilc_core.analysis.path_lift_counterfactual import (
    compute_path_lift_counterfactual,
    rank_path_lift_rows,
)
from ilc_core.exceptions import NodeValueKernelError


def _sample_path_witnesses() -> list[dict[str, object]]:
    return [
        {
            "witness_id": "witness-b",
            "source_id": "s2",
            "target_id": "t2",
            "nodes": [
                {"node_id": "node-a", "agent_id": "agent-1"},
                {"node_id": "node-d", "agent_id": "agent-2"},
            ],
            "path_weight": 1.0,
            "path_cost": 2.0,
        },
        {
            "witness_id": "witness-a",
            "source_id": "s1",
            "target_id": "t1",
            "nodes": [
                {"node_id": "node-a", "agent_id": "agent-1"},
                {"node_id": "node-b", "agent_id": "agent-2"},
                {"node_id": "node-c", "agent_id": "agent-3"},
            ],
            "path_weight": 1.0,
            "path_cost": 3.0,
        },
    ]


def test_path_lift_counterfactual_is_deterministic_and_non_negative() -> None:
    report_a = compute_path_lift_counterfactual(_sample_path_witnesses())
    report_b = compute_path_lift_counterfactual(_sample_path_witnesses())

    assert report_a == report_b
    assert report_a["witness_count"] == 2
    assert [row["node_id"] for row in report_a["rows"]] == ["node-a", "node-b", "node-c", "node-d"]
    assert all(row["raw_path_lift"] >= 0.0 for row in report_a["rows"])
    assert all(row["normalized_path_lift"] >= 0.0 for row in report_a["rows"])

    rows_by_node = {row["node_id"]: row for row in report_a["rows"]}
    assert rows_by_node["node-a"]["normalized_path_lift"] == pytest.approx(1.0)
    assert rows_by_node["node-b"]["normalized_path_lift"] == pytest.approx(0.4)
    assert rows_by_node["node-c"]["normalized_path_lift"] == pytest.approx(0.4)
    assert rows_by_node["node-d"]["normalized_path_lift"] == pytest.approx(0.6)


def test_rank_path_lift_rows_uses_deterministic_tie_breaks() -> None:
    report = compute_path_lift_counterfactual(_sample_path_witnesses())
    ranked = rank_path_lift_rows(report["rows"])

    # node-b and node-c have equal score; node_id lexical tie break keeps node-b first.
    assert [row["node_id"] for row in ranked] == ["node-a", "node-d", "node-b", "node-c"]


def test_path_lift_rejects_invalid_node_provenance_shape() -> None:
    bad_witnesses = _sample_path_witnesses()
    first = bad_witnesses[0]
    first_nodes = first["nodes"]
    assert isinstance(first_nodes, list)
    first_nodes[0] = {"node_id": "node-a"}

    with pytest.raises(NodeValueKernelError) as exc_info:
        compute_path_lift_counterfactual(bad_witnesses)
    assert str(exc_info.value) == "path_lift_invalid_node_keys"


def test_path_lift_preserves_provenance_for_self_referential_topology_detection() -> None:
    witnesses = [
        {
            "witness_id": "hub-1",
            "source_id": "root",
            "target_id": "leaf-1",
            "nodes": [
                {"node_id": "hub", "agent_id": "agent-solo"},
                {"node_id": "leaf-1", "agent_id": "agent-solo"},
            ],
            "path_weight": 1.0,
            "path_cost": 2.0,
        },
        {
            "witness_id": "hub-2",
            "source_id": "root",
            "target_id": "leaf-2",
            "nodes": [
                {"node_id": "hub", "agent_id": "agent-solo"},
                {"node_id": "leaf-2", "agent_id": "agent-solo"},
            ],
            "path_weight": 1.0,
            "path_cost": 2.0,
        },
    ]

    report = compute_path_lift_counterfactual(witnesses)
    rows_by_node = {row["node_id"]: row for row in report["rows"]}

    hub_row = rows_by_node["hub"]
    assert hub_row["supporting_agents"] == ["agent-solo"]
    assert hub_row["unique_agent_count"] == 1
