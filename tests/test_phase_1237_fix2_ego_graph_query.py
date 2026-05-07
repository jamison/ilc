from __future__ import annotations

import pytest

from ilc_core.graph.agent_graph_projection_runtime import project_graph
from ilc_core.graph.sidecar_query_runtime import (
    SidecarQueryBounds,
    execute_sidecar_query,
)


def _projection(
    *,
    nodes: tuple[str, ...],
    edges: tuple[tuple[str, str], ...] = (),
    hyperedges: tuple[tuple[str, ...], ...] = (),
) -> dict[str, object]:
    return {
        "nodes": [{"canonical_id": node_id} for node_id in nodes],
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
    }


def _node_ids(result: dict[str, object]) -> list[str]:
    return [node["canonical_id"] for node in result["nodes"]]


def _edge_pairs(result: dict[str, object]) -> list[tuple[str, str]]:
    return [(edge["source"], edge["target"]) for edge in result["edges"]]


def test_phase_1237_fix2_hops_zero_returns_root_only() -> None:
    projection = _projection(nodes=("root", "leaf"), edges=(("root", "leaf"),))
    result = execute_sidecar_query(
        query_type="ego_graph",
        projection=projection,
        root_id="root",
        hops=0,
    )

    assert result["query_type"] == "ego_graph"
    assert result["root_id"] == "root"
    assert result["hops"] == 0
    assert _node_ids(result) == ["root"]
    assert result["edge_count"] == 0
    assert result["edges"] == []


def test_phase_1237_fix2_hops_one_on_hub_returns_direct_neighbors() -> None:
    projection = _projection(
        nodes=("hub", "a", "b", "c", "far"),
        edges=(("hub", "a"), ("hub", "b"), ("hub", "c"), ("c", "far")),
    )

    result = execute_sidecar_query(
        query_type="ego_graph",
        projection=projection,
        root_id="hub",
        hops=1,
    )

    assert _node_ids(result) == ["a", "b", "c", "hub"]
    assert _edge_pairs(result) == [("hub", "a"), ("hub", "b"), ("hub", "c")]


def test_phase_1237_fix2_hops_two_on_chain_expands_without_third_hop() -> None:
    projection = _projection(
        nodes=("a", "b", "c", "d"),
        edges=(("a", "b"), ("b", "c"), ("c", "d")),
    )

    result = execute_sidecar_query(
        query_type="ego_graph",
        projection=projection,
        root_id="a",
        hops=2,
    )

    assert _node_ids(result) == ["a", "b", "c"]
    assert _edge_pairs(result) == [("a", "b"), ("b", "c")]


def test_phase_1237_fix2_missing_root_id_rejected_by_dispatcher() -> None:
    with pytest.raises(ValueError, match="sidecar_ego_graph_root_id_required"):
        execute_sidecar_query(query_type="ego_graph", projection=_projection(nodes=("a",)))


def test_phase_1237_fix2_unknown_root_rejected() -> None:
    with pytest.raises(ValueError, match="sidecar_ego_graph_root_id_not_found"):
        execute_sidecar_query(
            query_type="ego_graph",
            projection=_projection(nodes=("a",)),
            root_id="missing",
        )


def test_phase_1237_fix2_hops_limit_exceeded_rejected() -> None:
    with pytest.raises(ValueError, match="sidecar_ego_graph_hops_limit_exceeded"):
        execute_sidecar_query(
            query_type="ego_graph",
            projection=_projection(nodes=("a",)),
            root_id="a",
            hops=2,
            bounds=SidecarQueryBounds(max_hops=1),
        )


@pytest.mark.parametrize("hops", (True, "1", -1))
def test_phase_1237_fix2_invalid_hops_rejected(hops: object) -> None:
    with pytest.raises(ValueError, match="sidecar_ego_graph_hops_invalid"):
        execute_sidecar_query(
            query_type="ego_graph",
            projection=_projection(nodes=("a",)),
            root_id="a",
            hops=hops,
        )


def test_phase_1237_fix2_node_limit_exceeded_rejected_before_overflow() -> None:
    projection = _projection(
        nodes=("hub", "a", "b"),
        edges=(("hub", "a"), ("hub", "b")),
    )

    with pytest.raises(ValueError, match="sidecar_ego_graph_node_limit_exceeded"):
        execute_sidecar_query(
            query_type="ego_graph",
            projection=projection,
            root_id="hub",
            hops=1,
            bounds=SidecarQueryBounds(max_nodes=2),
        )


def test_phase_1237_fix2_isolated_node_returns_itself() -> None:
    result = execute_sidecar_query(
        query_type="ego_graph",
        projection=_projection(nodes=("solo",)),
        root_id="solo",
        hops=1,
    )

    assert _node_ids(result) == ["solo"]
    assert result["edge_count"] == 0
    assert result["hyperedge_count"] == 0


def test_phase_1237_fix2_hyperedge_included_only_when_all_members_selected() -> None:
    projection = _projection(
        nodes=("hub", "a", "b", "far"),
        edges=(("hub", "a"), ("hub", "b")),
        hyperedges=(("hub", "a"), ("hub", "far")),
    )

    result = execute_sidecar_query(
        query_type="ego_graph",
        projection=projection,
        root_id="hub",
        hops=1,
    )

    assert [hyperedge["members"] for hyperedge in result["hyperedges"]] == [
        ("a", "hub")
    ]


def test_phase_1237_fix2_output_order_is_deterministic() -> None:
    projection = _projection(
        nodes=("hub", "c", "a", "b"),
        edges=(("hub", "c"), ("hub", "a"), ("hub", "b")),
    )

    first = execute_sidecar_query(
        query_type="ego_graph",
        projection=projection,
        root_id="hub",
        hops=1,
    )
    second = execute_sidecar_query(
        query_type="ego_graph",
        projection=projection,
        root_id="hub",
        hops=1,
    )

    assert first == second
    assert _node_ids(first) == ["a", "b", "c", "hub"]
    assert _edge_pairs(first) == [("hub", "a"), ("hub", "b"), ("hub", "c")]


def test_phase_1237_fix2_dispatcher_returns_ego_graph() -> None:
    result = execute_sidecar_query(
        query_type="ego_graph",
        projection=_projection(nodes=("root",)),
        root_id="root",
    )

    assert result["query_type"] == "ego_graph"


def test_phase_1237_fix2_works_with_phase_1229_project_graph_output() -> None:
    projection = project_graph(
        projection_type="repo_hypergraph",
        nodes=[
            {"canonical_id": "genesis:root"},
            {"canonical_id": "node:a"},
            {"canonical_id": "node:b"},
            {"canonical_id": "node:c"},
        ],
        edges=[
            {
                "source": "genesis:root",
                "target": "node:a",
                "edge_type": "derives_from",
            },
            {"source": "node:a", "target": "node:b", "edge_type": "derives_from"},
            {"source": "node:b", "target": "node:c", "edge_type": "derives_from"},
        ],
        hyperedges=[
            {
                "canonical_id": "hyperedge:ab",
                "members": ["node:b", "node:a"],
            }
        ],
    )

    result = execute_sidecar_query(
        query_type="ego_graph",
        projection=projection,
        root_id="node:a",
        hops=1,
    )

    assert _node_ids(result) == ["genesis:root", "node:a", "node:b"]
    assert _edge_pairs(result) == [
        ("genesis:root", "node:a"),
        ("node:a", "node:b"),
    ]
    assert [hyperedge["canonical_id"] for hyperedge in result["hyperedges"]] == [
        "hyperedge:ab"
    ]
