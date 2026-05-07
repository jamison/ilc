"""Read-only sidecar query runtime skeleton for graph projections.

Phase 1237 Fix1 establishes the sidecar query contract without implementing
query behavior. Later Fix phases fill the dispatcher arms.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ilc_core.graph.agent_graph_projection_runtime import (
    AGENT_GRAPH_PROJECTION_RUNTIME_VERSION,
)


SIDECAR_QUERY_RUNTIME_VERSION = "sidecar_query_runtime_1237.v0.1"
SIDECAR_PROJECTION_DEPENDENCY = AGENT_GRAPH_PROJECTION_RUNTIME_VERSION

QUERY_TYPES = frozenset(
    {
        "ego_graph",
        "centrality_metrics",
        "convergence_trace",
    }
)


@dataclass(frozen=True)
class SidecarQueryBounds:
    max_hops: int = 4
    max_nodes: int = 200
    max_results: int = 100

    def validate(self) -> None:
        for field_name in ("max_hops", "max_nodes", "max_results"):
            value = getattr(self, field_name)
            if type(value) is not int:
                raise ValueError(f"{field_name}_must_be_positive_int")
            if value <= 0:
                raise ValueError(f"{field_name}_must_be_positive_int")


def execute_sidecar_query(
    *,
    query_type: str,
    projection: Mapping[str, Any],
    bounds: SidecarQueryBounds | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    if query_type not in QUERY_TYPES:
        raise ValueError("sidecar_query_type_unsupported")

    active_bounds = bounds or SidecarQueryBounds()
    active_bounds.validate()

    if query_type == "ego_graph":
        root_id = kwargs.get("root_id")
        if root_id is None:
            raise ValueError("sidecar_ego_graph_root_id_required")
        hops = kwargs.get("hops", 1)
        return _ego_graph_query(
            projection,
            root_id=root_id,
            hops=hops,
            bounds=active_bounds,
        )

    raise NotImplementedError(f"sidecar_query_{query_type}_not_yet_implemented")


def _ego_graph_query(
    projection: Mapping[str, Any],
    *,
    root_id: str,
    hops: int,
    bounds: SidecarQueryBounds,
) -> dict[str, Any]:
    if type(hops) is not int:
        raise ValueError("sidecar_ego_graph_hops_invalid")
    if hops < 0:
        raise ValueError("sidecar_ego_graph_hops_invalid")
    if hops > bounds.max_hops:
        raise ValueError("sidecar_ego_graph_hops_limit_exceeded")

    nodes_by_id = {
        str(node["canonical_id"]): node
        for node in projection.get("nodes", ())
    }
    if root_id not in nodes_by_id:
        raise ValueError("sidecar_ego_graph_root_id_not_found")

    neighbors: dict[str, list[str]] = {}
    for edge in projection.get("edges", ()):
        source = str(edge["source"])
        target = str(edge["target"])
        neighbors.setdefault(source, []).append(target)
        neighbors.setdefault(target, []).append(source)
    for node_neighbors in neighbors.values():
        node_neighbors.sort()

    visited: set[str] = {root_id}
    frontier: list[str] = [root_id]
    for _ in range(hops):
        next_frontier: list[str] = []
        for node_id in frontier:
            for neighbor in neighbors.get(node_id, ()):
                if neighbor in visited or neighbor not in nodes_by_id:
                    continue
                if len(visited) + 1 > bounds.max_nodes:
                    raise ValueError("sidecar_ego_graph_node_limit_exceeded")
                visited.add(neighbor)
                next_frontier.append(neighbor)
        frontier = sorted(set(next_frontier))
        if not frontier:
            break

    selected_nodes = [
        nodes_by_id[node_id]
        for node_id in sorted(visited)
    ]
    selected_edges = sorted(
        (
            edge
            for edge in projection.get("edges", ())
            if str(edge["source"]) in visited and str(edge["target"]) in visited
        ),
        key=lambda edge: (
            str(edge["source"]),
            str(edge["target"]),
            str(edge["edge_type"]),
            str(edge["canonical_id"]),
        ),
    )
    selected_hyperedges = sorted(
        (
            hyperedge
            for hyperedge in projection.get("hyperedges", ())
            if all(str(member) in visited for member in hyperedge["members"])
        ),
        key=lambda hyperedge: str(hyperedge["canonical_id"]),
    )

    return {
        "edge_count": len(selected_edges),
        "edges": selected_edges,
        "hops": hops,
        "hyperedge_count": len(selected_hyperedges),
        "hyperedges": selected_hyperedges,
        "node_count": len(selected_nodes),
        "nodes": selected_nodes,
        "query_type": "ego_graph",
        "root_id": root_id,
    }
