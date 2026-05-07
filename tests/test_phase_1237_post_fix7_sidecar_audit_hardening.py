from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.graph.agent_graph_projection_runtime import path_to_genesis, project_graph
from ilc_core.graph.sidecar_query_runtime import (
    SidecarQuery,
    SidecarQueryBounds,
    build_sidecar_query_bundle,
    compute_centrality_metrics,
    compute_convergence_trace,
    execute_sidecar_query,
    export_sidecar_query_ndjson,
)


def _projection(
    *,
    nodes: tuple[str, ...],
    edges: tuple[tuple[str, str], ...] = (),
) -> dict[str, object]:
    degree = {node_id: 0 for node_id in nodes}
    for source, target in edges:
        degree[source] = degree.get(source, 0) + 1
        degree[target] = degree.get(target, 0) + 1
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
        "hyperedges": [],
        "metrics": {
            "degree_by_node": degree,
            "edge_count": len(edges),
            "hyperedge_count": 0,
            "hyperedge_order_by_id": {},
            "node_count": len(nodes),
        },
        "nodes": [{"canonical_id": node_id} for node_id in nodes],
    }


def test_audit_hardening_path_to_genesis_respects_max_depth_exactly() -> None:
    projection = project_graph(
        projection_type="repo_hypergraph",
        nodes=[
            {"canonical_id": "genesis:root"},
            {"canonical_id": "a"},
            {"canonical_id": "b"},
            {"canonical_id": "c"},
        ],
        edges=[
            {"edge_type": "derives_from", "source": "genesis:root", "target": "a"},
            {"edge_type": "derives_from", "source": "a", "target": "b"},
            {"edge_type": "derives_from", "source": "b", "target": "c"},
        ],
    )

    with pytest.raises(ValueError, match="graph_projection_genesis_path_not_found"):
        path_to_genesis(projection, "c", max_depth=2)

    assert path_to_genesis(projection, "c", max_depth=3) == [
        "c",
        "b",
        "a",
        "genesis:root",
    ]


def test_audit_hardening_path_to_genesis_rejects_bool_depth() -> None:
    with pytest.raises(ValueError, match="max_depth_must_be_int"):
        path_to_genesis({"edges": []}, "genesis:root", max_depth=True)


def test_audit_hardening_provenance_depth_respects_sidecar_max_hops() -> None:
    projection = _projection(
        nodes=("genesis:root", "a", "b", "c"),
        edges=(("genesis:root", "a"), ("a", "b"), ("b", "c")),
    )

    result = compute_centrality_metrics(
        projection,
        bounds=SidecarQueryBounds(max_hops=2),
    )

    assert result["provenance_depth_by_node"]["b"] == 2
    assert result["provenance_depth_by_node"]["c"] is None


def test_audit_hardening_single_node_convergence_returns_its_ancestors() -> None:
    result = compute_convergence_trace(
        _projection(nodes=("root", "a"), edges=(("root", "a"),)),
        node_ids=("a",),
    )

    assert result == {
        "common_ancestors": ["root"],
        "input_node_ids": ["a"],
        "merge_depth": 1,
        "query_type": "convergence_trace",
    }


def test_audit_hardening_convergence_node_ids_count_is_bounded() -> None:
    with pytest.raises(
        ValueError,
        match="sidecar_convergence_trace_node_ids_limit_exceeded",
    ):
        compute_convergence_trace(
            _projection(nodes=("a", "b", "c")),
            node_ids=("a", "b", "c"),
            bounds=SidecarQueryBounds(max_results=2),
        )


def test_audit_hardening_ndjson_result_count_is_bounded_before_join() -> None:
    with pytest.raises(
        ValueError,
        match="sidecar_export_ndjson_result_count_exceeded",
    ):
        export_sidecar_query_ndjson(
            [
                {"query_type": "ego_graph", "index": 1},
                {"query_type": "ego_graph", "index": 2},
                {"query_type": "ego_graph", "index": 3},
            ],
            max_results=2,
        )


def test_audit_hardening_bundle_result_count_is_bounded() -> None:
    with pytest.raises(
        ValueError,
        match="sidecar_export_bundle_result_count_exceeded",
    ):
        build_sidecar_query_bundle(
            projection={"metadata": {}},
            query_results=[
                {"query_type": "ego_graph", "index": 1},
                {"query_type": "ego_graph", "index": 2},
                {"query_type": "ego_graph", "index": 3},
            ],
            max_results=2,
        )


@pytest.mark.parametrize("max_results", (True, 0, -1, "2"))
def test_audit_hardening_export_max_results_rejects_invalid_values(
    max_results: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="sidecar_export_max_results_must_be_positive_int",
    ):
        export_sidecar_query_ndjson([], max_results=max_results)


def test_audit_hardening_ego_graph_max_nodes_one_allows_isolated_root() -> None:
    result = execute_sidecar_query(
        query_type="ego_graph",
        projection=_projection(nodes=("root",)),
        root_id="root",
        bounds=SidecarQueryBounds(max_nodes=1),
    )

    assert result["node_count"] == 1
    assert result["edges"] == []


def test_audit_hardening_ego_graph_max_nodes_one_rejects_neighbor() -> None:
    with pytest.raises(ValueError, match="sidecar_ego_graph_node_limit_exceeded"):
        execute_sidecar_query(
            query_type="ego_graph",
            projection=_projection(nodes=("root", "a"), edges=(("root", "a"),)),
            root_id="root",
            bounds=SidecarQueryBounds(max_nodes=1),
        )


def test_audit_hardening_top_k_equal_to_max_results_is_allowed() -> None:
    result = compute_centrality_metrics(
        _projection(nodes=("a", "b", "c"), edges=(("a", "b"), ("b", "c"))),
        top_k=2,
        bounds=SidecarQueryBounds(max_results=2),
    )

    assert result["top_k_applied"] == 2
    assert len(result["top_nodes_by_degree"]) == 2


def test_audit_hardening_sidecar_query_rejects_bool_hops() -> None:
    with pytest.raises(ValueError, match="sidecar_ego_graph_hops_invalid"):
        execute_sidecar_query(
            projection=_projection(nodes=("root",)),
            query=SidecarQuery(query_type="ego_graph", root_id="root", hops=True),
        )


def test_audit_hardening_centrality_scores_remain_decimal_before_export() -> None:
    result = compute_centrality_metrics(
        _projection(nodes=("a", "b"), edges=(("a", "b"),)),
    )

    assert isinstance(result["degree_centrality"]["a"], Decimal)
