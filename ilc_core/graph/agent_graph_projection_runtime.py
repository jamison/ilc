# SPDX-License-Identifier: AGPL-3.0-or-later
"""Deterministic graph projection runtime for digital agents.

Phase 1229 implements a read-only projection surface. Callers provide already
available graph records; this module performs no filesystem or network I/O.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable, Mapping, Sequence

from ilc_core.sidecars.public_path_activation import (
    PUBLIC_PATH_SURFACE_SIDECAR_PROJECTION,
    validate_public_path_activation_decision,
)

AGENT_GRAPH_PROJECTION_RUNTIME_VERSION = "agent_graph_projection_runtime_1229.v0.1"

FETCH_INCENTIVE_PROJECTION_TOKEN = (
    "fetch_incentive_hypergraph_slice_projection_required_phase_1229"
)

DEFAULT_MAX_NODES = 500
DEFAULT_MAX_EDGES = 1500
DEFAULT_MAX_HYPEREDGES = 500
DEFAULT_MAX_DEPTH = 4
DEFAULT_MAX_PATHS = 100
DEFAULT_MAX_BYTES = 10_000_000

PROJECTION_TYPES = frozenset(
    {
        "authority_graph",
        "claim_composition_graph",
        "provenance_graph",
        "runtime_binding_graph",
        "economic_flow_graph",
        "branchial_convergence_graph",
        "repo_hypergraph",
        "fetch_incentive_hypergraph_slice",
    }
)


@dataclass(frozen=True)
class ProjectionBounds:
    max_nodes: int = DEFAULT_MAX_NODES
    max_edges: int = DEFAULT_MAX_EDGES
    max_hyperedges: int = DEFAULT_MAX_HYPEREDGES
    max_depth: int = DEFAULT_MAX_DEPTH
    max_paths: int = DEFAULT_MAX_PATHS
    max_bytes: int = DEFAULT_MAX_BYTES

    def validate(self) -> None:
        for field_name in (
            "max_nodes",
            "max_edges",
            "max_hyperedges",
            "max_depth",
            "max_paths",
            "max_bytes",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, int):
                raise ValueError(f"{field_name}_must_be_int")
            if value < 0:
                raise ValueError(f"{field_name}_must_be_non_negative")


def project_graph(
    *,
    projection_type: str,
    nodes: Sequence[Mapping[str, Any]],
    edges: Sequence[Mapping[str, Any]] | None = None,
    hyperedges: Sequence[Mapping[str, Any]] | None = None,
    filters: Mapping[str, Any] | None = None,
    bounds: ProjectionBounds | None = None,
) -> dict[str, Any]:
    """Build a bounded deterministic graph projection.

    Records are ordinary mappings. Required node key: ``canonical_id`` or ``id``.
    Required edge keys: ``source``, ``target``, and ``edge_type``.
    Required hyperedge key: ``canonical_id`` or ``id``.
    """

    if projection_type not in PROJECTION_TYPES:
        raise ValueError("projection_type_unsupported")

    active_bounds = bounds or ProjectionBounds()
    active_bounds.validate()

    raw_edges = tuple(edges or ())
    raw_hyperedges = tuple(hyperedges or ())
    _enforce_count_bounds(nodes, raw_edges, raw_hyperedges, active_bounds)

    selected_nodes = _filter_nodes(nodes, filters)
    selected_ids = {node["canonical_id"] for node in selected_nodes}
    selected_edges = _filter_edges(raw_edges, selected_ids, filters)
    selected_hyperedges = _filter_hyperedges(raw_hyperedges, selected_ids, filters)
    _enforce_count_bounds(selected_nodes, selected_edges, selected_hyperedges, active_bounds)

    projection = {
        "bounds": _canonicalize(active_bounds.__dict__),
        "edges": selected_edges,
        "filters": _canonicalize(dict(filters or {})),
        "hyperedges": selected_hyperedges,
        "metadata": {
            "projection_type": projection_type,
            "runtime_version": AGENT_GRAPH_PROJECTION_RUNTIME_VERSION,
            "wall_clock_time_included": False,
        },
        "metrics": _projection_metrics(selected_nodes, selected_edges, selected_hyperedges),
        "nodes": selected_nodes,
    }
    _enforce_json_size(projection, active_bounds.max_bytes)
    return projection


def export_projection_json(
    projection: Mapping[str, Any],
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> str:
    """Export canonical JSON with stable key ordering and no NaN payloads."""

    if not isinstance(max_bytes, int):
        raise ValueError("max_bytes_must_be_int")
    if max_bytes < 0:
        raise ValueError("max_bytes_must_be_non_negative")
    payload = json.dumps(
        _canonicalize(projection),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    if len(payload.encode("utf-8")) > max_bytes:
        raise ValueError("graph_projection_export_size_exceeded")
    return payload


def export_projection_json_for_public_path(
    projection: Mapping[str, Any],
    *,
    activation_decision: Mapping[str, Any],
    current_epoch: int,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> str:
    """Export a projection only after Phase 1436 public-path authorization."""

    validate_public_path_activation_decision(
        activation_decision,
        current_epoch=current_epoch,
        surface=PUBLIC_PATH_SURFACE_SIDECAR_PROJECTION,
    )
    return export_projection_json(projection, max_bytes=max_bytes)


def export_projection_ndjson(
    projection: Mapping[str, Any],
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> str:
    """Export deterministic NDJSON ordered by section and canonical ID."""

    lines: list[str] = []
    metadata = {
        "kind": "metadata",
        "value": projection.get("metadata", {}),
    }
    metrics = {
        "kind": "metrics",
        "value": projection.get("metrics", {}),
    }
    lines.append(export_projection_json(metadata, max_bytes=max_bytes))
    lines.append(export_projection_json(metrics, max_bytes=max_bytes))
    for section in ("nodes", "edges", "hyperedges"):
        for item in projection.get(section, ()):
            lines.append(
                export_projection_json(
                    {"kind": section[:-1], "value": item},
                    max_bytes=max_bytes,
                )
            )
    payload = "\n".join(lines)
    if len(payload.encode("utf-8")) > max_bytes:
        raise ValueError("graph_projection_export_size_exceeded")
    return payload


def path_to_genesis(
    projection: Mapping[str, Any],
    start_id: str,
    *,
    genesis_id: str = "genesis:root",
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> list[str]:
    """Return a deterministic predecessor path from ``start_id`` to Genesis."""

    if type(max_depth) is not int:
        raise ValueError("max_depth_must_be_int")
    if max_depth < 0:
        raise ValueError("max_depth_must_be_non_negative")

    predecessors: dict[str, list[str]] = {}
    for edge in projection.get("edges", ()):
        source = str(edge["source"])
        target = str(edge["target"])
        predecessors.setdefault(target, []).append(source)
    for values in predecessors.values():
        values.sort()

    frontier: list[tuple[str, list[str]]] = [(start_id, [start_id])]
    visited = {start_id}
    while frontier:
        current, path = frontier.pop(0)
        if len(path) > max_depth + 1:
            continue
        if current == genesis_id:
            return path
        for predecessor in predecessors.get(current, ()):
            if predecessor not in visited:
                visited.add(predecessor)
                frontier.append((predecessor, path + [predecessor]))
    raise ValueError("graph_projection_genesis_path_not_found")


def build_fetch_incentive_hypergraph_slice(
    *,
    bounds: ProjectionBounds | None = None,
) -> dict[str, Any]:
    """Expose the CDL-087 fetch/incentive slice required by Phase 1228."""

    nodes = (
        _node(
            "cdl:060",
            node_class="constitutional_cdl",
            artifact_type="centrality_delta_gossip",
            source_ref="docs/specs/ilc_cdl_060_gossip_centrality_extension_opening_stub_539_v0.1.md",
        ),
        _node(
            "cdl:077",
            node_class="constitutional_cdl",
            artifact_type="want_have_want_block_fetch",
            source_ref="docs/specs/ilc_cdl_077_truth_primitive_fetch_opening_900_v0.1.md",
        ),
        _node(
            "cdl:078",
            node_class="constitutional_cdl",
            artifact_type="relay_incentive",
            source_ref="docs/specs/ilc_cdl_078_relay_incentive_constitutional_lock_opening_907_v0.1.md",
        ),
        _node(
            "cdl:079",
            node_class="constitutional_cdl",
            artifact_type="bootstrap_bundle_fetch",
            source_ref="docs/specs/ilc_cdl_079_hb002_bootstrap_opening_913_v0.1.md",
        ),
        _node(
            "cdl:081",
            node_class="constitutional_cdl",
            artifact_type="hyperedge_ecu_attribution",
            source_ref="docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_opening_929_v0.1.md",
        ),
        _node(
            "cdl:083",
            node_class="constitutional_cdl",
            artifact_type="panel_quorum_refutation",
            source_ref="docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md",
        ),
        _node(
            "cdl:084",
            node_class="constitutional_cdl",
            artifact_type="provenance_chain_attribution",
            source_ref="docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md",
        ),
        _node(
            "cdl:087",
            node_class="constitutional_cdl",
            artifact_type="canonical_fetch_distribution_policy",
            source_ref="docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md",
        ),
        _node(
            "reputation:adjunct_contract_phase_345",
            node_class="reputation_contract",
            artifact_type="lifecycle_graph_history_reputation",
            source_ref="docs/specs",
        ),
        _node(
            "decay:cdl_v1_temporal",
            node_class="decay_contract",
            artifact_type="temporal_decay",
            source_ref="docs/specs",
        ),
        _node(
            "edge:serving_peer_identity",
            node_class="projection_edge_semantics",
            artifact_type="serving_peer_delivered_artifact",
            source_ref="docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md#section-7",
        ),
        _node(
            "edge:served_graph_node_centrality",
            node_class="projection_edge_semantics",
            artifact_type="served_graph_node_is_central",
            source_ref="docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md#section-7",
        ),
    )
    edges = (
        _edge("cdl:077", "cdl:078", "fetch_feeds_relay_incentive"),
        _edge("cdl:078", "cdl:060", "serve_event_feeds_centrality_delta"),
        _edge("cdl:087", "cdl:077", "supplements_without_amendment"),
        _edge("cdl:087", "cdl:078", "depends_on_organic_incentive_path"),
        _edge("cdl:087", "edge:serving_peer_identity", "requires_distinct_edge"),
        _edge("cdl:087", "edge:served_graph_node_centrality", "requires_distinct_edge"),
        _edge("cdl:081", "cdl:084", "provenance_attribution_dependency"),
        _edge("decay:cdl_v1_temporal", "cdl:078", "damps_unused_reputation"),
    )
    hyperedges = (
        {
            "canonical_id": "hyperedge:fetch_incentive_cdl_077_078_060_087",
            "hyperedge_type": "constitutional_incentive_slice",
            "members": ("cdl:077", "cdl:078", "cdl:060", "cdl:087"),
            "projection_local_id": "hyperedge:000001",
            "source_ref": "docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md#section-7",
        },
        {
            "canonical_id": "hyperedge:serving_peer_vs_graph_node_distinction",
            "hyperedge_type": "edge_semantics_distinction",
            "members": (
                "edge:serving_peer_identity",
                "edge:served_graph_node_centrality",
                "cdl:087",
            ),
            "projection_local_id": "hyperedge:000002",
            "source_ref": "docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md#section-7",
        },
    )
    projection = project_graph(
        projection_type="fetch_incentive_hypergraph_slice",
        nodes=nodes,
        edges=edges,
        hyperedges=hyperedges,
        bounds=bounds,
    )
    projection["metadata"]["phase_1228_token_resolved"] = FETCH_INCENTIVE_PROJECTION_TOKEN
    projection["metadata"]["serving_peer_vs_served_graph_node_distinguished"] = True
    _enforce_json_size(projection, (bounds or ProjectionBounds()).max_bytes)
    return projection


def _node(
    canonical_id: str,
    *,
    node_class: str,
    artifact_type: str,
    source_ref: str,
) -> dict[str, str]:
    return {
        "artifact_type": artifact_type,
        "canonical_id": canonical_id,
        "lineage_domain": "genesis",
        "node_class": node_class,
        "projection_local_id": canonical_id.replace(":", "_"),
        "source_ref": source_ref,
    }


def _edge(source: str, target: str, edge_type: str) -> dict[str, str]:
    return {
        "canonical_id": f"edge:{source}->{target}:{edge_type}",
        "edge_type": edge_type,
        "projection_local_id": f"edge:{source.replace(':', '_')}__{target.replace(':', '_')}",
        "source": source,
        "target": target,
    }


def _filter_nodes(
    nodes: Sequence[Mapping[str, Any]],
    filters: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    selected = []
    for index, node in enumerate(nodes, start=1):
        normalized = _normalize_node(node, index)
        if _matches_applicable_filters(normalized, filters):
            selected.append(normalized)
    return sorted(selected, key=lambda item: item["canonical_id"])


def _filter_edges(
    edges: Sequence[Mapping[str, Any]],
    selected_ids: set[str],
    filters: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    selected = []
    for index, edge in enumerate(edges, start=1):
        normalized = _normalize_edge(edge, index)
        if normalized["source"] not in selected_ids or normalized["target"] not in selected_ids:
            continue
        if _matches_applicable_filters(normalized, filters):
            selected.append(normalized)
    return sorted(
        selected,
        key=lambda item: (
            item["source"],
            item["target"],
            item["edge_type"],
            item["canonical_id"],
        ),
    )


def _filter_hyperedges(
    hyperedges: Sequence[Mapping[str, Any]],
    selected_ids: set[str],
    filters: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    selected = []
    for index, hyperedge in enumerate(hyperedges, start=1):
        normalized = _normalize_hyperedge(hyperedge, index)
        members = set(normalized["members"])
        if members and not members.issubset(selected_ids):
            continue
        if _matches_filters(normalized, filters):
            selected.append(normalized)
    return sorted(selected, key=lambda item: item["canonical_id"])


def _normalize_node(node: Mapping[str, Any], index: int) -> dict[str, Any]:
    item = _canonicalize(dict(node))
    canonical_id = item.get("canonical_id") or item.get("id")
    if not isinstance(canonical_id, str) or not canonical_id:
        raise ValueError("graph_projection_node_canonical_id_required")
    item["canonical_id"] = canonical_id
    item.setdefault("projection_local_id", f"node:{index:06d}")
    item.setdefault("source_ref", None)
    return item


def _normalize_edge(edge: Mapping[str, Any], index: int) -> dict[str, Any]:
    item = _canonicalize(dict(edge))
    source = item.get("source")
    target = item.get("target")
    edge_type = item.get("edge_type")
    if not isinstance(source, str) or not source:
        raise ValueError("graph_projection_edge_source_required")
    if not isinstance(target, str) or not target:
        raise ValueError("graph_projection_edge_target_required")
    if not isinstance(edge_type, str) or not edge_type:
        raise ValueError("graph_projection_edge_type_required")
    item["source"] = source
    item["target"] = target
    item["edge_type"] = edge_type
    item.setdefault("canonical_id", f"edge:{source}->{target}:{edge_type}:{index:06d}")
    item.setdefault("projection_local_id", f"edge:{index:06d}")
    item.setdefault("source_ref", None)
    return item


def _normalize_hyperedge(hyperedge: Mapping[str, Any], index: int) -> dict[str, Any]:
    item = _canonicalize(dict(hyperedge))
    canonical_id = item.get("canonical_id") or item.get("id")
    if not isinstance(canonical_id, str) or not canonical_id:
        raise ValueError("graph_projection_hyperedge_canonical_id_required")
    members = item.get("members")
    if members is None:
        members = item.get("member_ids", ())
    if isinstance(members, str) or not isinstance(members, Iterable):
        raise ValueError("graph_projection_hyperedge_members_required")
    item["canonical_id"] = canonical_id
    item["members"] = tuple(sorted(str(member) for member in members))
    item.setdefault("projection_local_id", f"hyperedge:{index:06d}")
    item.setdefault("source_ref", None)
    return item


def _matches_filters(item: Mapping[str, Any], filters: Mapping[str, Any] | None) -> bool:
    if not filters:
        return True
    for key, expected in filters.items():
        if key not in item:
            return False
        actual = item[key]
        if isinstance(expected, (list, tuple, set, frozenset)):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def _matches_applicable_filters(
    item: Mapping[str, Any],
    filters: Mapping[str, Any] | None,
) -> bool:
    if not filters:
        return True
    return _matches_filters(
        item,
        {key: value for key, value in filters.items() if key in item},
    )


def _projection_metrics(
    nodes: Sequence[Mapping[str, Any]],
    edges: Sequence[Mapping[str, Any]],
    hyperedges: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    degree_by_node = {str(node["canonical_id"]): 0 for node in nodes}
    for edge in edges:
        degree_by_node[edge["source"]] = degree_by_node.get(edge["source"], 0) + 1
        degree_by_node[edge["target"]] = degree_by_node.get(edge["target"], 0) + 1
    hyperedge_order_by_id = {
        str(hyperedge["canonical_id"]): len(hyperedge["members"])
        for hyperedge in hyperedges
    }
    return {
        "degree_by_node": dict(sorted(degree_by_node.items())),
        "edge_count": len(edges),
        "hyperedge_count": len(hyperedges),
        "hyperedge_order_by_id": dict(sorted(hyperedge_order_by_id.items())),
        "node_count": len(nodes),
    }


def _enforce_count_bounds(
    nodes: Sequence[Mapping[str, Any]],
    edges: Sequence[Mapping[str, Any]],
    hyperedges: Sequence[Mapping[str, Any]],
    bounds: ProjectionBounds,
) -> None:
    if len(nodes) > bounds.max_nodes:
        raise ValueError("graph_projection_node_count_exceeded")
    if len(edges) > bounds.max_edges:
        raise ValueError("graph_projection_edge_count_exceeded")
    if len(hyperedges) > bounds.max_hyperedges:
        raise ValueError("graph_projection_hyperedge_count_exceeded")


def _enforce_json_size(projection: Mapping[str, Any], max_bytes: int) -> None:
    payload = export_projection_json(projection, max_bytes=max_bytes)
    if len(payload.encode("utf-8")) > max_bytes:
        raise ValueError("graph_projection_export_size_exceeded")


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("graph_projection_decimal_must_be_finite")
        return str(value)
    if isinstance(value, float):
        raise ValueError("graph_projection_float_values_forbidden")
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, tuple):
        return tuple(_canonicalize(item) for item in value)
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    if isinstance(value, set):
        return tuple(_canonicalize(item) for item in sorted(value))
    return value
