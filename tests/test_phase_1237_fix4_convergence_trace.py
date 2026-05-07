from __future__ import annotations

import pytest

from ilc_core.graph.agent_graph_projection_runtime import project_graph
from ilc_core.graph.sidecar_query_runtime import (
    SidecarQueryBounds,
    compute_convergence_trace,
    execute_sidecar_query,
)


def _projection(
    *,
    nodes: tuple[str, ...],
    edges: tuple[tuple[str, str], ...] = (),
) -> dict[str, object]:
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
        "nodes": [{"canonical_id": node_id} for node_id in nodes],
    }


def test_phase_1237_fix4_two_nodes_sharing_hub_have_common_ancestor() -> None:
    result = compute_convergence_trace(
        _projection(nodes=("hub", "a", "b"), edges=(("hub", "a"), ("hub", "b"))),
        node_ids=("a", "b"),
    )

    assert result == {
        "common_ancestors": ["hub"],
        "input_node_ids": ["a", "b"],
        "merge_depth": 1,
        "query_type": "convergence_trace",
    }


def test_phase_1237_fix4_disconnected_nodes_have_no_common_ancestors() -> None:
    result = compute_convergence_trace(
        _projection(
            nodes=("x", "y", "p", "q"),
            edges=(("x", "y"), ("p", "q")),
        ),
        node_ids=("y", "q"),
    )

    assert result["common_ancestors"] == []
    assert result["merge_depth"] is None


def test_phase_1237_fix4_genesis_only_input_has_no_ancestors() -> None:
    result = compute_convergence_trace(
        _projection(nodes=("genesis:root",)),
        node_ids=("genesis:root",),
    )

    assert result["common_ancestors"] == []
    assert result["merge_depth"] is None


def test_phase_1237_fix4_three_nodes_share_ancestor() -> None:
    result = compute_convergence_trace(
        _projection(
            nodes=("root", "a", "b", "c", "d"),
            edges=(("root", "a"), ("root", "b"), ("root", "c"), ("a", "d")),
        ),
        node_ids=("b", "c", "d"),
    )

    assert result["common_ancestors"] == ["root"]


def test_phase_1237_fix4_duplicate_node_ids_deduplicated_and_sorted() -> None:
    result = compute_convergence_trace(
        _projection(nodes=("hub", "a", "b"), edges=(("hub", "a"), ("hub", "b"))),
        node_ids=("b", "a", "a"),
    )

    assert result["input_node_ids"] == ["a", "b"]


@pytest.mark.parametrize("node_ids", (None, [], ()))
def test_phase_1237_fix4_empty_input_rejected(node_ids: object) -> None:
    with pytest.raises(ValueError, match="sidecar_convergence_trace_node_ids_empty"):
        compute_convergence_trace(_projection(nodes=("a",)), node_ids=node_ids)


@pytest.mark.parametrize("node_ids", ("abc", b"abc", ("a", ""), ("a", 1)))
def test_phase_1237_fix4_invalid_node_ids_rejected(node_ids: object) -> None:
    with pytest.raises(ValueError, match="sidecar_convergence_trace_node_ids_invalid"):
        compute_convergence_trace(_projection(nodes=("a",)), node_ids=node_ids)


def test_phase_1237_fix4_unknown_node_rejected() -> None:
    with pytest.raises(ValueError, match="sidecar_convergence_trace_node_id_not_found"):
        compute_convergence_trace(_projection(nodes=("a",)), node_ids=("missing",))


def test_phase_1237_fix4_bounds_max_hops_limits_ancestor_traversal() -> None:
    projection = _projection(
        nodes=("root", "a", "b", "c"),
        edges=(("root", "a"), ("a", "b"), ("root", "c")),
    )

    result = compute_convergence_trace(
        projection,
        node_ids=("b", "c"),
        bounds=SidecarQueryBounds(max_hops=1),
    )

    assert result["common_ancestors"] == []
    assert result["merge_depth"] is None


def test_phase_1237_fix4_cycle_protection_terminates() -> None:
    projection = _projection(
        nodes=("hub", "a", "b"),
        edges=(("hub", "a"), ("hub", "b"), ("a", "hub")),
    )

    result = compute_convergence_trace(projection, node_ids=("a", "b"))

    assert result["common_ancestors"] == ["hub"]
    assert result["merge_depth"] == 1


def test_phase_1237_fix4_merge_depth_is_minimum_predecessor_hops() -> None:
    result = compute_convergence_trace(
        _projection(nodes=("hub", "a", "b"), edges=(("hub", "a"), ("hub", "b"))),
        node_ids=("a", "b"),
    )

    assert result["merge_depth"] == 1


def test_phase_1237_fix4_dispatcher_returns_convergence_trace() -> None:
    result = execute_sidecar_query(
        query_type="convergence_trace",
        projection=_projection(nodes=("hub", "a", "b"), edges=(("hub", "a"), ("hub", "b"))),
        node_ids=("a", "b"),
    )

    assert result["query_type"] == "convergence_trace"


def test_phase_1237_fix4_works_with_phase_1229_project_graph_output() -> None:
    projection = project_graph(
        projection_type="repo_hypergraph",
        nodes=[
            {"canonical_id": "root"},
            {"canonical_id": "a"},
            {"canonical_id": "b"},
        ],
        edges=[
            {"source": "root", "target": "a", "edge_type": "derives_from"},
            {"source": "root", "target": "b", "edge_type": "derives_from"},
        ],
    )

    result = compute_convergence_trace(projection, node_ids=("a", "b"))

    assert result["common_ancestors"] == ["root"]
    assert result["input_node_ids"] == ["a", "b"]
    assert result["merge_depth"] == 1
