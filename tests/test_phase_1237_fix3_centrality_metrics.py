from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from ilc_core.graph.agent_graph_projection_runtime import project_graph
from ilc_core.graph.sidecar_query_runtime import (
    SidecarQueryBounds,
    compute_centrality_metrics,
    execute_sidecar_query,
)


def _projection(
    *,
    nodes: tuple[str, ...],
    edges: tuple[tuple[str, str], ...] = (),
    hyperedges: tuple[tuple[str, ...], ...] = (),
    include_degree_metrics: bool = True,
) -> dict[str, Any]:
    degree = {node_id: 0 for node_id in nodes}
    for source, target in edges:
        degree[source] = degree.get(source, 0) + 1
        degree[target] = degree.get(target, 0) + 1
    metrics: dict[str, Any] = {
        "edge_count": len(edges),
        "hyperedge_count": len(hyperedges),
        "hyperedge_order_by_id": {
            f"hyperedge:{index:06d}": len(members)
            for index, members in enumerate(hyperedges, start=1)
        },
        "node_count": len(nodes),
    }
    if include_degree_metrics:
        metrics["degree_by_node"] = degree
    return {
        "edges": [
            {
                "canonical_id": f"edge:{source}->{target}:{index:06d}",
                "edge_type": "test",
                "source": source,
                "target": target,
            }
            for index, (source, target) in enumerate(edges, start=1)
        ],
        "hyperedges": [
            {
                "canonical_id": f"hyperedge:{index:06d}",
                "members": tuple(sorted(members)),
            }
            for index, members in enumerate(hyperedges, start=1)
        ],
        "metrics": metrics,
        "nodes": [{"canonical_id": node_id} for node_id in nodes],
    }


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_float(item) for item in value)
    return False


def test_phase_1237_fix3_empty_projection_returns_empty_metrics() -> None:
    result = compute_centrality_metrics({"nodes": [], "edges": [], "metrics": {}})

    assert result["query_type"] == "centrality_metrics"
    assert result["node_count"] == 0
    assert result["degree_centrality"] == {}
    assert result["hyperedge_order_by_id"] == {}
    assert result["provenance_depth_by_node"] == {}
    assert result["top_nodes_by_degree"] == []


def test_phase_1237_fix3_single_node_degree_centrality_is_decimal_zero() -> None:
    result = compute_centrality_metrics(_projection(nodes=("solo",)))

    assert result["degree_centrality"] == {"solo": Decimal("0")}
    assert isinstance(result["degree_centrality"]["solo"], Decimal)


def test_phase_1237_fix3_hub_graph_ranks_hub_highest() -> None:
    result = compute_centrality_metrics(
        _projection(
            nodes=("hub", "a", "b", "c"),
            edges=(("hub", "a"), ("hub", "b"), ("hub", "c")),
        )
    )

    assert result["top_nodes_by_degree"][0] == {
        "degree_centrality": Decimal("1"),
        "node_id": "hub",
    }


def test_phase_1237_fix3_genesis_provenance_depth_is_zero() -> None:
    result = compute_centrality_metrics(_projection(nodes=("genesis:root",)))

    assert result["provenance_depth_by_node"]["genesis:root"] == 0


def test_phase_1237_fix3_two_hop_node_provenance_depth_is_two() -> None:
    result = compute_centrality_metrics(
        _projection(
            nodes=("genesis:root", "a", "b"),
            edges=(("genesis:root", "a"), ("a", "b")),
        )
    )

    assert result["provenance_depth_by_node"] == {
        "a": 1,
        "b": 2,
        "genesis:root": 0,
    }


def test_phase_1237_fix3_unreachable_node_depth_is_none() -> None:
    result = compute_centrality_metrics(
        _projection(
            nodes=("genesis:root", "a", "orphan"),
            edges=(("genesis:root", "a"),),
        )
    )

    assert result["provenance_depth_by_node"]["orphan"] is None


def test_phase_1237_fix3_top_k_truncates_to_explicit_value() -> None:
    result = compute_centrality_metrics(
        _projection(
            nodes=("hub", "a", "b", "c"),
            edges=(("hub", "a"), ("hub", "b"), ("hub", "c")),
        ),
        top_k=2,
    )

    assert result["top_k_applied"] == 2
    assert len(result["top_nodes_by_degree"]) == 2


def test_phase_1237_fix3_top_k_defaults_to_bounds_max_results() -> None:
    result = compute_centrality_metrics(
        _projection(
            nodes=("hub", "a", "b", "c"),
            edges=(("hub", "a"), ("hub", "b"), ("hub", "c")),
        ),
        bounds=SidecarQueryBounds(max_results=1),
    )

    assert result["top_k_applied"] == 1
    assert len(result["top_nodes_by_degree"]) == 1


def test_phase_1237_fix3_top_k_tie_breaking_is_deterministic() -> None:
    result = compute_centrality_metrics(
        _projection(
            nodes=("b", "a", "c"),
            edges=(("a", "c"), ("b", "c")),
        )
    )

    assert result["top_nodes_by_degree"][:2] == [
        {"degree_centrality": Decimal("1"), "node_id": "c"},
        {"degree_centrality": Decimal("0.5"), "node_id": "a"},
    ]


@pytest.mark.parametrize("top_k", (True, "1", 0, -1, 3))
def test_phase_1237_fix3_invalid_top_k_rejected(top_k: object) -> None:
    with pytest.raises(ValueError, match="sidecar_centrality_top_k_out_of_bounds"):
        compute_centrality_metrics(
            _projection(nodes=("a",)),
            top_k=top_k,
            bounds=SidecarQueryBounds(max_results=2),
        )


@pytest.mark.parametrize(
    "bad_metrics",
    (
        {"degree_by_node": {"a": "1"}, "node_count": 1},
        {"degree_by_node": {"a": True}, "node_count": 1},
        {"degree_by_node": {"a": 0}, "node_count": "1"},
        {
            "degree_by_node": {"a": 0},
            "hyperedge_order_by_id": {"h": False},
            "node_count": 1,
        },
    ),
)
def test_phase_1237_fix3_malformed_metric_values_rejected(
    bad_metrics: dict[str, Any],
) -> None:
    projection = {
        "edges": [],
        "hyperedges": [],
        "metrics": bad_metrics,
        "nodes": [{"canonical_id": "a"}],
    }

    with pytest.raises(ValueError, match="sidecar_centrality_metric_must_be_int"):
        compute_centrality_metrics(projection)


def test_phase_1237_fix3_missing_degree_metrics_recomputed_from_projection() -> None:
    result = compute_centrality_metrics(
        _projection(
            nodes=("a", "b", "c"),
            edges=(("a", "b"), ("b", "c")),
            include_degree_metrics=False,
        )
    )

    assert result["degree_centrality"] == {
        "a": Decimal("0.5"),
        "b": Decimal("1"),
        "c": Decimal("0.5"),
    }


def test_phase_1237_fix3_scores_are_decimal_objects_not_strings_or_floats() -> None:
    result = compute_centrality_metrics(
        _projection(nodes=("a", "b"), edges=(("a", "b"),))
    )

    score = result["degree_centrality"]["a"]
    ranked_score = result["top_nodes_by_degree"][0]["degree_centrality"]
    assert isinstance(score, Decimal)
    assert isinstance(ranked_score, Decimal)
    assert not isinstance(score, str)
    assert not isinstance(ranked_score, str)


def test_phase_1237_fix3_no_float_appears_in_result() -> None:
    result = compute_centrality_metrics(
        _projection(nodes=("a", "b"), edges=(("a", "b"),))
    )

    assert not _contains_float(result)


def test_phase_1237_fix3_dispatcher_returns_centrality_metrics() -> None:
    result = execute_sidecar_query(
        query_type="centrality_metrics",
        projection=_projection(nodes=("a",)),
    )

    assert result["query_type"] == "centrality_metrics"


def test_phase_1237_fix3_works_with_phase_1229_project_graph_output() -> None:
    projection = project_graph(
        projection_type="repo_hypergraph",
        nodes=[
            {"canonical_id": "genesis:root"},
            {"canonical_id": "a"},
            {"canonical_id": "b"},
        ],
        edges=[
            {"source": "genesis:root", "target": "a", "edge_type": "derives_from"},
            {"source": "a", "target": "b", "edge_type": "derives_from"},
        ],
        hyperedges=[
            {
                "canonical_id": "hyperedge:ab",
                "members": ["a", "b"],
            }
        ],
    )

    result = execute_sidecar_query(
        query_type="centrality_metrics",
        projection=projection,
        top_k=1,
    )

    assert result["node_count"] == 3
    assert result["top_nodes_by_degree"] == [
        {"degree_centrality": Decimal("1"), "node_id": "a"}
    ]
    assert result["hyperedge_order_by_id"] == {"hyperedge:ab": 2}
    assert result["provenance_depth_by_node"]["b"] == 2
