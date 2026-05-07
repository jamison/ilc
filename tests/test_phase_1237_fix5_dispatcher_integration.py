from __future__ import annotations

import pytest

from ilc_core.graph.sidecar_query_runtime import (
    QUERY_TYPES,
    SidecarQuery,
    SidecarQueryBounds,
    execute_sidecar_query,
)


def _sample_projection() -> dict[str, object]:
    return {
        "nodes": [
            {"canonical_id": "a"},
            {"canonical_id": "b"},
            {"canonical_id": "c"},
        ],
        "edges": [
            {
                "canonical_id": "e:a-b",
                "edge_type": "t",
                "source": "a",
                "target": "b",
            },
            {
                "canonical_id": "e:a-c",
                "edge_type": "t",
                "source": "a",
                "target": "c",
            },
        ],
        "hyperedges": [],
        "metrics": {
            "degree_by_node": {"a": 2, "b": 1, "c": 1},
            "edge_count": 2,
            "hyperedge_count": 0,
            "hyperedge_order_by_id": {},
            "node_count": 3,
        },
    }


def test_phase_1237_fix5_dispatcher_runs_all_query_types() -> None:
    projection = _sample_projection()

    ego = execute_sidecar_query(
        query_type="ego_graph",
        projection=projection,
        root_id="a",
    )
    centrality = execute_sidecar_query(
        query_type="centrality_metrics",
        projection=projection,
    )
    convergence = execute_sidecar_query(
        query_type="convergence_trace",
        projection=projection,
        node_ids=("b", "c"),
    )

    assert ego["query_type"] == "ego_graph"
    assert centrality["query_type"] == "centrality_metrics"
    assert convergence["query_type"] == "convergence_trace"
    assert convergence["common_ancestors"] == ["a"]


def test_phase_1237_fix5_sidecar_query_dispatches_ego_graph() -> None:
    result = execute_sidecar_query(
        projection=_sample_projection(),
        query=SidecarQuery(query_type="ego_graph", root_id="a", hops=1),
    )

    assert result["query_type"] == "ego_graph"
    assert [node["canonical_id"] for node in result["nodes"]] == ["a", "b", "c"]


def test_phase_1237_fix5_sidecar_query_dispatches_centrality_metrics() -> None:
    result = execute_sidecar_query(
        projection=_sample_projection(),
        query=SidecarQuery(query_type="centrality_metrics", top_k=1),
    )

    assert result["query_type"] == "centrality_metrics"
    assert result["top_k_applied"] == 1
    assert result["top_nodes_by_degree"][0]["node_id"] == "a"


def test_phase_1237_fix5_sidecar_query_dispatches_convergence_trace() -> None:
    result = execute_sidecar_query(
        projection=_sample_projection(),
        query=SidecarQuery(query_type="convergence_trace", node_ids=("b", "c")),
    )

    assert result["query_type"] == "convergence_trace"
    assert result["input_node_ids"] == ["b", "c"]
    assert result["common_ancestors"] == ["a"]
    assert result["merge_depth"] == 1


def test_phase_1237_fix5_query_dataclass_bounds_override_dispatch_bounds() -> None:
    with pytest.raises(ValueError, match="sidecar_ego_graph_hops_limit_exceeded"):
        execute_sidecar_query(
            projection=_sample_projection(),
            bounds=SidecarQueryBounds(max_hops=4),
            query=SidecarQuery(
                query_type="ego_graph",
                root_id="b",
                hops=2,
                bounds=SidecarQueryBounds(max_hops=1),
            ),
        )


def test_phase_1237_fix5_query_dataclass_unsupported_type_rejected() -> None:
    with pytest.raises(ValueError, match="sidecar_query_type_unsupported"):
        execute_sidecar_query(
            projection=_sample_projection(),
            query=SidecarQuery(query_type="unsupported"),
        )


def test_phase_1237_fix5_no_supported_query_type_raises_not_implemented() -> None:
    projection = _sample_projection()
    calls = {
        "ego_graph": {"root_id": "a"},
        "centrality_metrics": {},
        "convergence_trace": {"node_ids": ("a",)},
    }

    assert QUERY_TYPES == frozenset(calls)
    for query_type, kwargs in calls.items():
        try:
            execute_sidecar_query(
                query_type=query_type,
                projection=projection,
                **kwargs,
            )
        except NotImplementedError as exc:
            pytest.fail(f"unexpected NotImplementedError for {query_type}: {exc}")


def test_phase_1237_fix5_keyword_query_type_still_required_without_query_object() -> None:
    with pytest.raises(ValueError, match="sidecar_query_type_unsupported"):
        execute_sidecar_query(projection=_sample_projection())
