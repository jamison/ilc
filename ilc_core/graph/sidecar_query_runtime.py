# SPDX-License-Identifier: AGPL-3.0-or-later
"""Read-only sidecar query runtime for graph projections.

Phase 1237 implements deterministic sidecar queries and canonical exports over
Phase 1229 graph projection dictionaries.
"""

from __future__ import annotations

import json
from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from ilc_core.graph.agent_graph_projection_runtime import (
    AGENT_GRAPH_PROJECTION_RUNTIME_VERSION,
    path_to_genesis,
)
from ilc_core.sidecars.public_path_activation import (
    PUBLIC_PATH_SURFACE_SIDECAR_PROJECTION,
    validate_public_path_activation_decision,
)


SIDECAR_QUERY_RUNTIME_VERSION = "sidecar_query_runtime_1237.v0.1"
SIDECAR_QUERY_COMPLETENESS_TOKEN = "adr_0031_sidecar_query_runtime_completeness_phase_1379"
SIDECAR_PROJECTION_DEPENDENCY = AGENT_GRAPH_PROJECTION_RUNTIME_VERSION
DEFAULT_SIDECAR_EXPORT_MAX_BYTES = 10_000_000
DEFAULT_SIDECAR_EXPORT_MAX_RESULTS = 1_000

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


@dataclass(frozen=True)
class SidecarQuery:
    query_type: str
    root_id: str | None = None
    hops: int = 1
    node_ids: tuple[str, ...] = ()
    genesis_id: str = "genesis:root"
    top_k: int | None = None
    bounds: SidecarQueryBounds | None = None


def execute_sidecar_query(
    *,
    query_type: str = "",
    projection: Mapping[str, Any],
    bounds: SidecarQueryBounds | None = None,
    query: SidecarQuery | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    if query is not None:
        query_type = query.query_type
        if query.bounds is not None:
            bounds = query.bounds
        kwargs = {
            "genesis_id": query.genesis_id,
            "hops": query.hops,
            "node_ids": query.node_ids if query.node_ids else None,
            "root_id": query.root_id,
            "top_k": query.top_k,
        }

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

    if query_type == "centrality_metrics":
        return compute_centrality_metrics(
            projection,
            genesis_id=kwargs.get("genesis_id", "genesis:root"),
            top_k=kwargs.get("top_k"),
            bounds=active_bounds,
        )

    if query_type == "convergence_trace":
        return compute_convergence_trace(
            projection,
            node_ids=kwargs.get("node_ids"),
            bounds=active_bounds,
        )

    raise ValueError("sidecar_query_dispatch_incomplete")


def export_sidecar_query_json(
    result: Mapping[str, Any],
    *,
    max_bytes: int = DEFAULT_SIDECAR_EXPORT_MAX_BYTES,
) -> str:
    _validate_export_max_bytes(max_bytes)
    serializable = _prepare_for_export(result)
    payload = json.dumps(
        serializable,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    if len(payload.encode("utf-8")) > max_bytes:
        raise ValueError("sidecar_export_size_exceeded")
    return payload


def export_sidecar_query_json_for_public_path(
    result: Mapping[str, Any],
    *,
    activation_decision: Mapping[str, Any],
    current_epoch: int,
    max_bytes: int = DEFAULT_SIDECAR_EXPORT_MAX_BYTES,
) -> str:
    """Export a sidecar query only after Phase 1436 public-path authorization."""

    validate_public_path_activation_decision(
        activation_decision,
        current_epoch=current_epoch,
        surface=PUBLIC_PATH_SURFACE_SIDECAR_PROJECTION,
    )
    return export_sidecar_query_json(result, max_bytes=max_bytes)


def export_sidecar_query_ndjson(
    results: Sequence[Mapping[str, Any]],
    *,
    max_bytes: int = DEFAULT_SIDECAR_EXPORT_MAX_BYTES,
    max_results: int = DEFAULT_SIDECAR_EXPORT_MAX_RESULTS,
) -> str:
    _validate_export_max_bytes(max_bytes)
    _validate_export_max_results(max_results)
    if not isinstance(results, Sequence):
        raise ValueError("sidecar_export_results_must_be_sequence")
    if len(results) > max_results:
        raise ValueError("sidecar_export_ndjson_result_count_exceeded")

    lines: list[str] = []
    total_bytes = 0
    for result in results:
        line = export_sidecar_query_json(result, max_bytes=max_bytes)
        line_bytes = len(line.encode("utf-8"))
        total_bytes += line_bytes + (1 if lines else 0)
        if total_bytes > max_bytes:
            raise ValueError("sidecar_export_size_exceeded")
        lines.append(line)
    payload = "\n".join(lines)
    if len(payload.encode("utf-8")) > max_bytes:
        raise ValueError("sidecar_export_size_exceeded")
    return payload


def build_sidecar_query_bundle(
    *,
    projection: Mapping[str, Any],
    query_results: Sequence[Mapping[str, Any]],
    max_results: int = DEFAULT_SIDECAR_EXPORT_MAX_RESULTS,
) -> dict[str, Any]:
    _validate_export_max_results(max_results)
    metadata = projection.get("metadata", {})
    if not isinstance(metadata, Mapping):
        raise ValueError("sidecar_bundle_projection_metadata_must_be_mapping")
    if not isinstance(query_results, Sequence):
        raise ValueError("sidecar_export_results_must_be_sequence")
    if len(query_results) > max_results:
        raise ValueError("sidecar_export_bundle_result_count_exceeded")

    return {
        "bundle_version": SIDECAR_QUERY_RUNTIME_VERSION,
        "projection_dependency": SIDECAR_PROJECTION_DEPENDENCY,
        "projection_metadata": dict(metadata),
        "query_count": len(query_results),
        "query_results": list(query_results),
        "wall_clock_time_included": False,
    }


def _validate_export_max_bytes(max_bytes: int) -> None:
    if type(max_bytes) is not int:
        raise ValueError("sidecar_export_max_bytes_must_be_int")
    if max_bytes < 0:
        raise ValueError("sidecar_export_max_bytes_must_be_non_negative")


def _validate_export_max_results(max_results: int) -> None:
    if type(max_results) is not int:
        raise ValueError("sidecar_export_max_results_must_be_positive_int")
    if max_results <= 0:
        raise ValueError("sidecar_export_max_results_must_be_positive_int")


def _prepare_for_export(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        raise ValueError("sidecar_export_float_values_forbidden")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("sidecar_export_decimal_must_be_finite")
        return str(value)
    if isinstance(value, Mapping):
        return {
            str(key): _prepare_for_export(item)
            for key, item in sorted(
                value.items(),
                key=lambda entry: str(entry[0]),
            )
        }
    if isinstance(value, (list, tuple)):
        return [_prepare_for_export(item) for item in value]
    return value


def compute_convergence_trace(
    projection: Mapping[str, Any],
    node_ids: Sequence[str],
    *,
    bounds: SidecarQueryBounds | None = None,
) -> dict[str, Any]:
    active_bounds = bounds or SidecarQueryBounds()
    active_bounds.validate()

    input_node_ids = _normalize_convergence_node_ids(
        node_ids,
        max_results=active_bounds.max_results,
    )
    all_node_ids = {
        str(node["canonical_id"])
        for node in projection.get("nodes", ())
    }
    for node_id in input_node_ids:
        if node_id not in all_node_ids:
            raise ValueError("sidecar_convergence_trace_node_id_not_found")

    predecessors = _predecessors_by_target(projection)
    ancestor_depths = {
        node_id: _ancestor_depths(
            node_id,
            predecessors=predecessors,
            max_hops=active_bounds.max_hops,
        )
        for node_id in input_node_ids
    }

    common = set(ancestor_depths[input_node_ids[0]])
    for node_id in input_node_ids[1:]:
        common &= set(ancestor_depths[node_id])
    common_ancestors = sorted(common)

    merge_depth = None
    if common_ancestors:
        merge_depth = min(
            depths[ancestor]
            for depths in ancestor_depths.values()
            for ancestor in common_ancestors
        )

    return {
        "common_ancestors": common_ancestors,
        "input_node_ids": input_node_ids,
        "merge_depth": merge_depth,
        "query_type": "convergence_trace",
    }


def _normalize_convergence_node_ids(
    node_ids: Sequence[str] | None,
    *,
    max_results: int,
) -> list[str]:
    if node_ids is None:
        raise ValueError("sidecar_convergence_trace_node_ids_empty")
    if isinstance(node_ids, (str, bytes)):
        raise ValueError("sidecar_convergence_trace_node_ids_invalid")
    if not isinstance(node_ids, Sequence):
        raise ValueError("sidecar_convergence_trace_node_ids_invalid")
    if len(node_ids) == 0:
        raise ValueError("sidecar_convergence_trace_node_ids_empty")
    if len(node_ids) > max_results:
        raise ValueError("sidecar_convergence_trace_node_ids_limit_exceeded")
    for node_id in node_ids:
        if type(node_id) is not str or not node_id:
            raise ValueError("sidecar_convergence_trace_node_ids_invalid")
    return sorted(set(node_ids))


def _predecessors_by_target(projection: Mapping[str, Any]) -> dict[str, list[str]]:
    predecessors: dict[str, list[str]] = {}
    for edge in projection.get("edges", ()):
        source = str(edge["source"])
        target = str(edge["target"])
        predecessors.setdefault(target, []).append(source)
    for values in predecessors.values():
        values.sort()
    return predecessors


def _ancestor_depths(
    start_id: str,
    *,
    predecessors: Mapping[str, Sequence[str]],
    max_hops: int,
) -> dict[str, int]:
    ancestors: dict[str, int] = {}
    seen = {start_id}
    frontier: deque[tuple[str, int]] = deque([(start_id, 0)])

    while frontier:
        current, depth = frontier.popleft()
        if depth >= max_hops:
            continue
        for predecessor in predecessors.get(current, ()):
            if predecessor in seen:
                continue
            seen.add(predecessor)
            ancestor_depth = depth + 1
            ancestors[predecessor] = ancestor_depth
            frontier.append((predecessor, ancestor_depth))

    return ancestors


def compute_centrality_metrics(
    projection: Mapping[str, Any],
    *,
    genesis_id: str = "genesis:root",
    top_k: int | None = None,
    bounds: SidecarQueryBounds | None = None,
) -> dict[str, Any]:
    """Compute centrality metrics.

    The result intentionally contains ``Decimal`` score objects for in-process
    precision. Use ``export_sidecar_query_json`` for canonical JSON export.
    """

    active_bounds = bounds or SidecarQueryBounds()
    active_bounds.validate()

    if top_k is not None:
        if type(top_k) is not int:
            raise ValueError("sidecar_centrality_top_k_out_of_bounds")
        if top_k <= 0 or top_k > active_bounds.max_results:
            raise ValueError("sidecar_centrality_top_k_out_of_bounds")

    metrics = projection.get("metrics", {})
    if not isinstance(metrics, Mapping):
        raise ValueError("sidecar_centrality_metrics_must_be_mapping")

    degree_by_node = _degree_by_node(projection, metrics)
    node_count_value = metrics.get("node_count")
    if node_count_value is None:
        node_count = len(degree_by_node)
    else:
        node_count = _require_int_metric(node_count_value)

    hyperedge_order = _hyperedge_order(metrics)
    denominator = Decimal(max(node_count - 1, 1))
    degree_centrality = {
        node_id: Decimal(degree) / denominator
        for node_id, degree in sorted(degree_by_node.items())
    }

    provenance_depth: dict[str, int | None] = {}
    for node_id in sorted(degree_by_node):
        try:
            path = path_to_genesis(
                projection,
                node_id,
                genesis_id=genesis_id,
                max_depth=active_bounds.max_hops,
            )
            provenance_depth[node_id] = len(path) - 1
        except ValueError:
            provenance_depth[node_id] = None

    limit = top_k if top_k is not None else active_bounds.max_results
    ranked = sorted(
        degree_centrality.items(),
        key=lambda item: (-item[1], item[0]),
    )[:limit]

    return {
        "degree_centrality": degree_centrality,
        "hyperedge_order_by_id": hyperedge_order,
        "node_count": node_count,
        "provenance_depth_by_node": provenance_depth,
        "query_type": "centrality_metrics",
        "top_k_applied": limit,
        "top_nodes_by_degree": [
            {"degree_centrality": score, "node_id": node_id}
            for node_id, score in ranked
        ],
    }


def _degree_by_node(
    projection: Mapping[str, Any],
    metrics: Mapping[str, Any],
) -> dict[str, int]:
    raw_degree = metrics.get("degree_by_node")
    if raw_degree is None:
        degree = {
            str(node["canonical_id"]): 0
            for node in projection.get("nodes", ())
        }
        for edge in projection.get("edges", ()):
            source = str(edge["source"])
            target = str(edge["target"])
            degree[source] = degree.get(source, 0) + 1
            degree[target] = degree.get(target, 0) + 1
        return dict(sorted(degree.items()))

    if not isinstance(raw_degree, Mapping):
        raise ValueError("sidecar_centrality_degree_metric_invalid")
    return {
        str(node_id): _require_int_metric(degree)
        for node_id, degree in sorted(raw_degree.items())
    }


def _hyperedge_order(metrics: Mapping[str, Any]) -> dict[str, int]:
    raw_order = metrics.get("hyperedge_order_by_id", {})
    if not isinstance(raw_order, Mapping):
        raise ValueError("sidecar_centrality_hyperedge_order_invalid")
    return {
        str(hyperedge_id): _require_int_metric(order)
        for hyperedge_id, order in sorted(raw_order.items())
    }


def _require_int_metric(value: Any) -> int:
    if type(value) is not int:
        raise ValueError("sidecar_centrality_metric_must_be_int")
    return value


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
        frontier = sorted(next_frontier)
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
