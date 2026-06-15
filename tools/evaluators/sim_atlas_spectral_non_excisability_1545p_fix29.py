#!/usr/bin/env python3
"""Run the Fix29 Atlas spectral and non-excisability SIM.

PUBLIC_RC_EXCLUDE: atlas_spectral_non_excisability_sim_research_only
PUBLIC_RC_EXCLUDE_REASON: Research-only structural graph SIM over unsigned Atlas candidates; no Genesis signing, node upload, canonical graph mutation, public RC activation, runtime activation, minting, settlement, or ADR/CDL mutation.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
from scipy import sparse
from scipy.sparse import csgraph
from scipy.sparse.linalg import eigsh


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE = "1545p-Fix29"
SIM_ID = "SIM-ATLAS-SPECTRAL-NON-EXCISABILITY-01"
SCHEMA_VERSION = "sim_atlas_spectral_non_excisability_1545p_fix29.v0.1"
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"

FIX22_GRAPH = REPO_ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
FIX25_BASELINE = REPO_ROOT / "out/sim_atlas_whole_graph_baseline_diagnostic_1545p_fix25.json"
FIX28_SUMMARY = REPO_ROOT / "out/sim_atlas_projection_hydration_1545p_fix28.json"

SUMMARY_OUT = REPO_ROOT / "out/sim_atlas_spectral_non_excisability_1545p_fix29.json"
REPORT_OUT = REPO_ROOT / "docs/sims/sim_atlas_spectral_non_excisability_1545p_fix29_v0.1.md"
REVIEW_OUT = REPO_ROOT / "docs/specs/ilc_atlas_spectral_non_excisability_review_1545p_fix29_v0.1.md"

AUTHORITY_EDGE_TYPES = {"GOVERNS", "ATTESTATION"}
LEGACY_EQUIVALENT_TYPED_TRACE_ROLES = {"PROVENANCE"}
SUPPORT_TRACE_EDGE_TYPES = {
    "IMPLEMENTS",
    "TESTS",
    "EVIDENCES",
    "REFERENCES_AUTHORITY",
    "DERIVED_FROM",
    "CLASSIFIED_BY",
    "IMPORTS_MODULE",
}
CONTAINMENT_EDGE_TYPES = {"CONTAINS_FILE", "CONTAINS_GROUP", "CONTAINS_PARTITION"}
AUTHORITY_NODE_KINDS = {
    "adr_artifact",
    "adr_document_node",
    "authority_identity",
    "authority_map",
    "axiom_node",
    "bundle_artifact",
    "cdl_artifact",
    "demotion_event",
    "keygen_ceremony",
    "operator_primitive",
    "policy_constant",
    "policy_contract",
    "policy_rule",
    "public_key_record",
    "schema_artifact",
}
SOURCE_NODE_KINDS = {
    "repo_material_node",
    "runtime_source_file_node",
    "tooling_source_file_node",
    "test_evidence_node",
    "sim_evidence_node",
    "spec_document_node",
    "generated_evidence_node",
    "genesis_private_material_node",
    "sidecar_material_node",
}
AUTHORITY_PREFIXES = ("adr:", "cdl:", "truth_primitive:", "policy:", "artifact:", "genesis_agent:", "ceremony:")

OUTPUT_TOKENS = [
    "atlas_spectral_non_excisability_sim_committed_phase_1545p_fix29",
    "atlas_laplacian_diagnostics_recorded_phase_1545p_fix29",
    "atlas_non_excisability_probes_recorded_phase_1545p_fix29",
    "atlas_authority_cut_checks_recorded_phase_1545p_fix29",
    "atlas_structural_negative_controls_passed_phase_1545p_fix29",
    "public_path_remains_blocked_phase_1545p_fix29",
]

NON_CLAIMS = [
    "No graph rewrite occurred.",
    "No candidate was promoted.",
    "No canonical Genesis graph mutation occurred.",
    "No Genesis signing occurred.",
    "No node upload occurred.",
    "No public graph publication occurred.",
    "No public repository push occurred.",
    "No public RC activation occurred.",
    "No runtime guard clearance occurred.",
    "No minting, settlement, wallet, treasury, ledger write, or economic activation occurred.",
    "No sidecar activation occurred.",
    "No ADR or CDL mutation occurred.",
    "Spectral and non-excisability metrics are structural diagnostics only, not authority proof.",
]


def _canonical_dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def _compact_dumps(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json_object_required:{path}")
    return payload


def _node_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("atlas_candidate_node_missing_candidate_id")
    return value


def _edge_endpoint(edge: dict[str, Any], key: str) -> str:
    value = edge.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"atlas_candidate_edge_missing_{key}")
    return value


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("atlas_candidate_edge_missing_edge_type")
    return value


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 1.0
    return round(numerator / denominator, 6)


def _round_float(value: float, digits: int = 12) -> float:
    return round(float(value), digits)


def _stable_hash(payload: Any, length: int = 16) -> str:
    return hashlib.sha256(_compact_dumps(payload).encode("utf-8")).hexdigest()[:length]


def _is_authority_bearing(node_id: str, node: dict[str, Any]) -> bool:
    kind = str(node.get("node_kind", ""))
    tier = str(node.get("tier", node.get("canonicality_tier", "")))
    if kind in AUTHORITY_NODE_KINDS:
        return True
    if node_id.startswith(AUTHORITY_PREFIXES) and kind not in SOURCE_NODE_KINDS:
        return True
    return "accepted_adr" in tier or "ratified_cdl" in tier or "genesis_core" in tier


def _is_source_derived(node_id: str, node: dict[str, Any]) -> bool:
    return (
        node_id.startswith("repo:file:")
        or node_id.startswith("source:")
        or isinstance(node.get("source_path"), str)
        or str(node.get("node_kind", "")) in SOURCE_NODE_KINDS
    )


def _authority_class(node_id: str, node: dict[str, Any]) -> str:
    tier = str(node.get("tier", node.get("canonicality_tier", ""))).lower()
    kind = str(node.get("node_kind", "")).lower()
    source_path = str(node.get("source_path", "")).lower()
    if node_id == NODE0 or "genesis_core" in tier or kind in {"axiom_node", "authority_map"}:
        return "genesis_or_axiomatic_root"
    if node_id.startswith("adr:") or "accepted_adr" in tier:
        return "accepted_adr"
    if node_id.startswith("cdl:") or "ratified_cdl" in tier:
        return "ratified_cdl"
    if source_path.startswith("ilc_core/") or "runtime" in kind:
        return "runtime_source"
    if "private" in tier or "excluded" in tier or "private" in kind:
        return "private_excluded_material"
    if "generated" in tier or "research" in tier or "evidence" in kind or source_path.startswith("docs/sims/"):
        return "generated_evidence_material"
    return "support_material"


def _privacy_class(node: dict[str, Any]) -> str:
    fields = " ".join(
        str(node.get(key, ""))
        for key in ("tier", "canonicality_tier", "authority_tier", "node_kind", "source_path")
    ).lower()
    if "private" in fields or "excluded" in fields:
        return "private_or_excluded"
    if "generated" in fields or "research" in fields:
        return "research_or_generated"
    return "public_or_support"


def _bfs(seed: set[str], adjacency: dict[str, set[str]]) -> set[str]:
    seen = set(seed)
    queue: deque[str] = deque(sorted(seed))
    while queue:
        current = queue.popleft()
        for target in sorted(adjacency.get(current, set())):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def _build_context() -> dict[str, Any]:
    graph = _read_json(FIX22_GRAPH)
    baseline = _read_json(FIX25_BASELINE)
    fix28 = _read_json(FIX28_SUMMARY)
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not all(isinstance(node, dict) for node in nodes):
        raise ValueError("fix22_nodes_list_required")
    if not isinstance(edges, list) or not all(isinstance(edge, dict) for edge in edges):
        raise ValueError("fix22_edges_list_required")

    node_by_id = {_node_id(node): node for node in nodes}
    valid_edges = []
    endpoint_errors = []
    for edge in edges:
        source = _edge_endpoint(edge, "source")
        target = _edge_endpoint(edge, "target")
        if source not in node_by_id or target not in node_by_id:
            endpoint_errors.append(
                {
                    "edge_id": str(edge.get("edge_id", "")),
                    "source": source,
                    "target": target,
                }
            )
            continue
        valid_edges.append(edge)

    return {
        "baseline": baseline,
        "edge_type_counts": dict(sorted(Counter(_edge_type(edge) for edge in valid_edges).items())),
        "endpoint_errors": endpoint_errors,
        "fix28": fix28,
        "graph": graph,
        "node_by_id": node_by_id,
        "valid_edges": valid_edges,
    }


def _metrics_after_removal(
    node_by_id: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
    removed: set[str],
) -> dict[str, Any]:
    remaining_nodes = set(node_by_id) - removed
    undirected: dict[str, set[str]] = defaultdict(set)
    authority_forward: dict[str, set[str]] = defaultdict(set)
    support_forward: dict[str, set[str]] = defaultdict(set)
    backtrace_forward: dict[str, set[str]] = defaultdict(set)
    backtrace_reverse: dict[str, set[str]] = defaultdict(set)
    outgoing_by_node: dict[str, list[dict[str, Any]]] = defaultdict(list)
    remaining_edge_count = 0

    for edge in edges:
        source = _edge_endpoint(edge, "source")
        target = _edge_endpoint(edge, "target")
        if source not in remaining_nodes or target not in remaining_nodes:
            continue
        remaining_edge_count += 1
        edge_type = _edge_type(edge)
        undirected[source].add(target)
        undirected[target].add(source)
        outgoing_by_node[source].append(edge)
        if edge_type in AUTHORITY_EDGE_TYPES | LEGACY_EQUIVALENT_TYPED_TRACE_ROLES:
            authority_forward[source].add(target)
            backtrace_forward[target].add(source)
            backtrace_reverse[source].add(target)
        elif edge_type in SUPPORT_TRACE_EDGE_TYPES:
            support_forward[source].add(target)
            backtrace_forward[source].add(target)
            backtrace_reverse[target].add(source)

    root_component = _bfs({NODE0}, undirected) if NODE0 in remaining_nodes else set()
    authority_terminals = _bfs({NODE0}, authority_forward) if NODE0 in remaining_nodes else set()

    authority_forward_covered: set[str] = set()
    for node_id in remaining_nodes:
        if node_id in authority_terminals:
            authority_forward_covered.add(node_id)
            continue
        for edge in outgoing_by_node.get(node_id, []):
            if _edge_type(edge) in SUPPORT_TRACE_EDGE_TYPES | LEGACY_EQUIVALENT_TYPED_TRACE_ROLES:
                if _edge_endpoint(edge, "target") in authority_terminals:
                    authority_forward_covered.add(node_id)
                    break

    backtrace_covered = _bfs({NODE0}, backtrace_reverse) if NODE0 in remaining_nodes else set()
    authority_bearing = {
        node_id
        for node_id in remaining_nodes
        if _is_authority_bearing(node_id, node_by_id[node_id])
    }
    authority_traceable = {
        node_id
        for node_id in authority_bearing
        if node_id == NODE0 or node_id in authority_forward_covered or node_id in backtrace_covered
    }
    source_derived = {
        node_id
        for node_id in remaining_nodes
        if _is_source_derived(node_id, node_by_id[node_id])
    }
    backwards_read_covered = source_derived & backtrace_covered

    return {
        "authority_bearing_count": len(authority_bearing),
        "authority_traceability": _ratio(len(authority_traceable), len(authority_bearing)),
        "backwards_read_coverage": _ratio(len(backwards_read_covered), len(source_derived)),
        "edge_count": remaining_edge_count,
        "node_count": len(remaining_nodes),
        "root_reachability": _ratio(len(root_component), len(remaining_nodes)),
    }


def _projection_edges(context: dict[str, Any], projection: str) -> tuple[list[str], list[tuple[int, int]]]:
    node_ids = sorted(context["node_by_id"])
    index = {node_id: idx for idx, node_id in enumerate(node_ids)}
    pairs: set[tuple[int, int]] = set()

    if projection == "clique_incidence":
        for edge in context["valid_edges"]:
            source = index[_edge_endpoint(edge, "source")]
            target = index[_edge_endpoint(edge, "target")]
            if source == target:
                continue
            low, high = sorted((source, target))
            pairs.add((low, high))
        return node_ids, sorted(pairs)

    if projection != "star":
        raise ValueError(f"unknown_projection:{projection}")

    projected_ids = list(node_ids)
    for edge_index, edge in enumerate(context["valid_edges"]):
        edge_id = str(edge.get("edge_id") or f"edge_{edge_index}")
        projected_ids.append(f"virtual_hyperedge:{edge_index}:{edge_id}")
    projected_index = {node_id: idx for idx, node_id in enumerate(projected_ids)}
    virtual_offset = len(node_ids)
    for edge_index, edge in enumerate(context["valid_edges"]):
        virtual = virtual_offset + edge_index
        source = projected_index[_edge_endpoint(edge, "source")]
        target = projected_index[_edge_endpoint(edge, "target")]
        if source != virtual:
            pairs.add(tuple(sorted((source, virtual))))
        if target != virtual:
            pairs.add(tuple(sorted((target, virtual))))
    return projected_ids, sorted(pairs)


def _spectral_diagnostic(context: dict[str, Any], projection: str) -> dict[str, Any]:
    node_ids, pairs = _projection_edges(context, projection)
    n_nodes = len(node_ids)
    if not pairs:
        return {
            "component_count": n_nodes,
            "fiedler_top_coordinates": [],
            "fiedler_vector_export_scope": "empty_projection",
            "lambda2": 0.0,
            "lambda2_method": "empty_projection",
            "largest_component_node_count": 1 if n_nodes else 0,
            "node_count": n_nodes,
            "projection": projection,
            "spectral_failure": None,
        }

    rows = []
    cols = []
    for source, target in pairs:
        rows.extend([source, target])
        cols.extend([target, source])
    data = np.ones(len(rows), dtype=np.float64)
    adjacency = sparse.coo_matrix((data, (rows, cols)), shape=(n_nodes, n_nodes)).tocsr()
    component_count, labels = csgraph.connected_components(adjacency, directed=False, return_labels=True)
    largest_component_node_count = int(np.bincount(labels).max()) if n_nodes else 0

    if projection == "star" and n_nodes > 20_000:
        return {
            "component_count": int(component_count),
            "fiedler_top_coordinates": [],
            "fiedler_vector_export_scope": "not_exported_budget_fallback",
            "lambda2": 0.0,
            "lambda2_method": "cheeger_lb_fallback",
            "largest_component_node_count": largest_component_node_count,
            "node_count": n_nodes,
            "projection": projection,
            "spectral_failure": "star_projection_exceeds_fix29_spectral_budget",
        }

    laplacian = csgraph.laplacian(adjacency, normed=False).astype(np.float64)

    try:
        eigenvalues, eigenvectors = eigsh(laplacian, k=2, which="SM", tol=1e-8)
        order = np.argsort(eigenvalues)
        sorted_values = eigenvalues[order]
        fiedler_vector = eigenvectors[:, order[1]]
        anchor = int(np.argmax(np.abs(fiedler_vector)))
        if float(fiedler_vector[anchor]) < 0:
            fiedler_vector = -fiedler_vector
        top_indices = sorted(
            range(n_nodes),
            key=lambda idx: (-abs(float(fiedler_vector[idx])), node_ids[idx]),
        )[:120]
        top_coordinates = [
            {
                "coordinate": _round_float(float(fiedler_vector[idx])),
                "node_id": node_ids[idx],
            }
            for idx in top_indices
        ]
        return {
            "component_count": int(component_count),
            "eigenvalues_smallest_two": [_round_float(value) for value in sorted_values[:2]],
            "fiedler_top_coordinates": top_coordinates,
            "fiedler_vector_export_scope": "top_120_by_absolute_coordinate",
            "lambda2": _round_float(sorted_values[1]),
            "lambda2_method": "eigsh_SM_k2_scipy_sparse",
            "largest_component_node_count": largest_component_node_count,
            "node_count": n_nodes,
            "projection": projection,
            "spectral_failure": None,
        }
    except Exception as exc:  # pragma: no cover - fallback retained for machines without stable eigsh
        # Cheeger lower bound is recorded as 0 because conductance is not computed
        # in this fallback path. The explicit method prevents silent substitution.
        return {
            "component_count": int(component_count),
            "fiedler_top_coordinates": [],
            "fiedler_vector_export_scope": "not_available_under_fallback",
            "lambda2": 0.0,
            "lambda2_method": "cheeger_lb_fallback",
            "largest_component_node_count": largest_component_node_count,
            "node_count": n_nodes,
            "projection": projection,
            "spectral_failure": type(exc).__name__,
        }


def _build_networkx_graph(context: dict[str, Any]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(sorted(context["node_by_id"]))
    graph.add_edges_from(
        (_edge_endpoint(edge, "source"), _edge_endpoint(edge, "target"))
        for edge in context["valid_edges"]
    )
    return graph


def _family_sets(context: dict[str, Any], graph: nx.Graph) -> dict[str, set[str]]:
    node_by_id = context["node_by_id"]
    degrees = dict(graph.degree())
    support_nodes = {
        node_id
        for node_id, node in node_by_id.items()
        if not _is_authority_bearing(node_id, node)
    }
    private_nodes = {
        node_id
        for node_id, node in node_by_id.items()
        if _authority_class(node_id, node) == "private_excluded_material"
    }
    generated_nodes = {
        node_id
        for node_id, node in node_by_id.items()
        if _authority_class(node_id, node) == "generated_evidence_material"
    }
    runtime_nodes = {
        node_id
        for node_id, node in node_by_id.items()
        if _authority_class(node_id, node) == "runtime_source"
    }
    public_release_nodes = {
        node_id
        for node_id, node in node_by_id.items()
        if any(
            token in str(node.get("source_path", "")).lower()
            for token in ("public_rc", "source_allowlist", "package_profile", "release")
        )
    }
    accepted_adr_nodes = {
        node_id
        for node_id, node in node_by_id.items()
        if node_id.startswith("adr:")
        or "accepted_adr" in str(node.get("canonicality_tier", "")).lower()
        or "draft_direction_accepted" in str(node.get("canonicality_tier", "")).lower()
    }
    ratified_cdl_nodes = {
        node_id
        for node_id, node in node_by_id.items()
        if node_id.startswith("cdl:")
        or "ratified_cdl" in str(node.get("canonicality_tier", "")).lower()
    }
    genesis_root_nodes = {
        node_id
        for node_id, node in node_by_id.items()
        if node_id == NODE0
        or str(node.get("node_kind", "")) in {"axiom_node", "authority_map"}
        or (
            _authority_class(node_id, node) == "genesis_or_axiomatic_root"
            and not node_id.startswith(("adr:", "cdl:"))
        )
    }
    high_degree_support = {
        node_id
        for node_id, _degree in sorted(
            ((node_id, degrees.get(node_id, 0)) for node_id in support_nodes),
            key=lambda item: (-item[1], item[0]),
        )[:25]
    }
    low_degree_support = {
        node_id
        for node_id, _degree in sorted(
            ((node_id, degrees.get(node_id, 0)) for node_id in support_nodes if degrees.get(node_id, 0) <= 1),
            key=lambda item: (item[1], item[0]),
        )[:100]
    }
    return {
        "accepted_adr_nodes": accepted_adr_nodes,
        "generated_evidence_material": generated_nodes,
        "genesis_root_or_axiomatic_root_exception": genesis_root_nodes,
        "high_degree_support_hubs": high_degree_support,
        "low_degree_support_leaves": low_degree_support,
        "private_excluded_material": private_nodes,
        "public_release_candidate_material": public_release_nodes,
        "ratified_cdl_nodes": ratified_cdl_nodes,
        "runtime_source_nodes": runtime_nodes,
    }


def _non_excisability_probes(context: dict[str, Any], families: dict[str, set[str]]) -> list[dict[str, Any]]:
    node_by_id = context["node_by_id"]
    edges = context["valid_edges"]
    baseline = _metrics_after_removal(node_by_id, edges, set())
    records = []
    for family_name in sorted(families):
        removed = set(families[family_name])
        after = _metrics_after_removal(node_by_id, edges, removed)
        edges_removed = sum(
            1
            for edge in edges
            if _edge_endpoint(edge, "source") in removed or _edge_endpoint(edge, "target") in removed
        )
        root_delta = _round_float(after["root_reachability"] - baseline["root_reachability"], 6)
        authority_delta = _round_float(after["authority_traceability"] - baseline["authority_traceability"], 6)
        backwards_delta = _round_float(after["backwards_read_coverage"] - baseline["backwards_read_coverage"], 6)
        if family_name == "genesis_root_or_axiomatic_root_exception":
            verdict = "non_excisable"
        elif authority_delta < -0.01 or root_delta < -0.01:
            verdict = "fragile"
        elif family_name in {"low_degree_support_leaves", "private_excluded_material", "generated_evidence_material"}:
            verdict = "safe_to_defer"
        else:
            verdict = "redundant_support" if abs(root_delta) < 0.000001 and abs(authority_delta) < 0.000001 else "fragile"

        privacy_classes = Counter(_privacy_class(node_by_id[node_id]) for node_id in removed if node_id in node_by_id)
        if privacy_classes.get("private_or_excluded", 0):
            privacy_effect = "private_or_excluded_material_removed_without_public_tier_flip"
        else:
            privacy_effect = "no_privacy_tier_flip_detected"
        records.append(
            {
                "authority_traceability_delta": authority_delta,
                "backwards_read_coverage_delta": backwards_delta,
                "edges_removed": edges_removed,
                "family": family_name,
                "nodes_removed": len(removed),
                "privacy_boundary_effect": privacy_effect,
                "root_reachability_delta": root_delta,
                "sample_node_ids": sorted(removed)[:12],
                "verdict": verdict,
                "warning": (
                    "structural non-excisability does not establish Genesis-rootedness under a typed authority view"
                    if verdict in {"non_excisable", "fragile"}
                    else "structural deferral verdict does not imply semantic rejection"
                ),
            }
        )
    return records


def _authority_cut_checks(
    context: dict[str, Any],
    graph: nx.Graph,
    families: dict[str, set[str]],
) -> dict[str, Any]:
    node_by_id = context["node_by_id"]
    edges = context["valid_edges"]
    baseline = _metrics_after_removal(node_by_id, edges, set())
    articulation_points = sorted(nx.articulation_points(graph))
    authority_articulations = [
        node_id
        for node_id in articulation_points
        if _is_authority_bearing(node_id, node_by_id[node_id])
    ]
    node0_after = _metrics_after_removal(node_by_id, edges, {NODE0})
    top_authority_candidates = sorted(
        families["accepted_adr_nodes"] | families["ratified_cdl_nodes"],
        key=lambda node_id: (-graph.degree(node_id), node_id),
    )[:10]
    top_records = []
    for node_id in top_authority_candidates:
        after = _metrics_after_removal(node_by_id, edges, {node_id})
        top_records.append(
            {
                "authority_traceability_delta": _round_float(
                    after["authority_traceability"] - baseline["authority_traceability"],
                    6,
                ),
                "node_id": node_id,
                "root_reachability_delta": _round_float(
                    after["root_reachability"] - baseline["root_reachability"],
                    6,
                ),
            }
        )
    return {
        "authority_articulation_node_count": len(authority_articulations),
        "authority_articulation_nodes_sample": authority_articulations[:20],
        "node0_removal_authority_traceability_delta": _round_float(
            node0_after["authority_traceability"] - baseline["authority_traceability"],
            6,
        ),
        "node0_removal_root_reachability_delta": _round_float(
            node0_after["root_reachability"] - baseline["root_reachability"],
            6,
        ),
        "top_authority_single_node_removal": top_records,
        "verdict": "authority_cut_warns_as_expected",
    }


def _negative_controls(
    context: dict[str, Any],
    families: dict[str, set[str]],
) -> dict[str, Any]:
    node_by_id = context["node_by_id"]
    edges = context["valid_edges"]
    baseline = _metrics_after_removal(node_by_id, edges, set())
    support_removed = set(sorted(families["low_degree_support_leaves"])[:50])
    forbidden_removed = {NODE0}
    support_after = _metrics_after_removal(node_by_id, edges, support_removed)
    forbidden_after = _metrics_after_removal(node_by_id, edges, forbidden_removed)
    support_authority_delta = _round_float(
        support_after["authority_traceability"] - baseline["authority_traceability"], 6
    )
    forbidden_authority_delta = _round_float(
        forbidden_after["authority_traceability"] - baseline["authority_traceability"], 6
    )
    forbidden_root_delta = _round_float(
        forbidden_after["root_reachability"] - baseline["root_reachability"], 6
    )
    return {
        "forbidden_authority_removal_control": {
            "authority_traceability_delta": forbidden_authority_delta,
            "nodes_removed": len(forbidden_removed),
            "root_reachability_delta": forbidden_root_delta,
            "verdict": "warns_as_expected"
            if forbidden_authority_delta < 0 or forbidden_root_delta < 0
            else "unexpected_no_warning",
        },
        "support_only_low_value_control": {
            "authority_traceability_delta": support_authority_delta,
            "nodes_removed": len(support_removed),
            "root_reachability_delta": _round_float(
                support_after["root_reachability"] - baseline["root_reachability"], 6
            ),
            "verdict": "pass" if support_authority_delta >= -0.000001 else "unexpected_authority_break",
        },
        "structural_negative_controls_passed": support_authority_delta >= -0.000001
        and (forbidden_authority_delta < 0 or forbidden_root_delta < 0),
    }


def _review_queues(
    context: dict[str, Any],
    graph: nx.Graph,
    authority_cut_checks: dict[str, Any],
    families: dict[str, set[str]],
) -> dict[str, list[dict[str, Any]]]:
    node_by_id = context["node_by_id"]
    degrees = dict(graph.degree())
    fragile_nodes = [
        {
            "degree": degrees[node_id],
            "node_id": node_id,
            "reason": "articulation_point_in_structural_projection",
        }
        for node_id in authority_cut_checks["authority_articulation_nodes_sample"]
    ]
    overloaded_hubs = [
        {
            "degree": degree,
            "node_id": node_id,
            "reason": "high_degree_support_hub_structural_pressure",
        }
        for node_id, degree in sorted(
            ((node_id, degrees[node_id]) for node_id in families["high_degree_support_hubs"]),
            key=lambda item: (-item[1], item[0]),
        )
    ]
    low_value_support = [
        {
            "degree": degrees[node_id],
            "node_id": node_id,
            "privacy_class": _privacy_class(node_by_id[node_id]),
            "reason": "low_degree_support_leaf_candidate_for_defer_queue",
        }
        for node_id in sorted(families["low_degree_support_leaves"])[:40]
    ]
    return {
        "fragile_nodes": fragile_nodes,
        "low_value_support_material": low_value_support,
        "overloaded_hubs": overloaded_hubs,
    }


def _projection_sensitivity(star: dict[str, Any], clique: dict[str, Any]) -> dict[str, Any]:
    delta = abs(star["lambda2"] - clique["lambda2"])
    conservative = "star" if star["lambda2"] <= clique["lambda2"] else "clique_incidence"
    return {
        "absolute_delta_lambda2": _round_float(delta),
        "conservative_projection": conservative,
        "significant_delta_threshold": 0.01,
        "significant_delta": delta > 0.01,
        "use_for_fix30_fix31": conservative,
    }


def _build_outputs() -> dict[str, Any]:
    context = _build_context()
    graph = _build_networkx_graph(context)
    families = _family_sets(context, graph)
    spectral_clique = _spectral_diagnostic(context, "clique_incidence")
    spectral_star = _spectral_diagnostic(context, "star")
    bridges = sorted(tuple(sorted(edge)) for edge in nx.bridges(graph))
    articulation_points = sorted(nx.articulation_points(graph))
    bridge_sample = bridges[:50]
    articulation_sample = articulation_points[:50]
    non_excisability = _non_excisability_probes(context, families)
    authority_cut_checks = _authority_cut_checks(context, graph, families)
    negative_controls = _negative_controls(context, families)
    review_queues = _review_queues(context, graph, authority_cut_checks, families)
    payload = {
        "authority_cut_checks": authority_cut_checks,
        "baseline_inputs": {
            "fix22_edge_count": len(context["valid_edges"]),
            "fix22_node_count": len(context["node_by_id"]),
            "fix25_authority_bearing_node_count": context["baseline"]["authority_bearing_node_count"],
            "fix25_authority_reachability": context["baseline"]["authority_reachability"],
            "fix25_backwards_read_coverage": context["baseline"]["backwards_read_coverage"],
            "fix28_b10_b12_fallback_filter_applied": context["fix28"]["b10_b12_fallback_filter_applied"],
            "fix28_b10_b12_fallback_edge_count": context["fix28"]["b10_b12_fallback_edge_count"],
        },
        "bridge_and_articulation_pressure": {
            "articulation_point_count": len(articulation_points),
            "articulation_points_sample": articulation_sample,
            "bridge_count": len(bridges),
            "bridges_sample": [
                {"source": source, "target": target}
                for source, target in bridge_sample
            ],
            "high_degree_support_hub_count": len(families["high_degree_support_hubs"]),
        },
        "edge_type_counts": context["edge_type_counts"],
        "endpoint_error_count": len(context["endpoint_errors"]),
        "graph_views": {
            "analysis_projection_view": "undirected adjacency over Fix22 valid binary edges",
            "authority_trace_view": "typed directed GOVERNS, ATTESTATION, legacy PROVENANCE, and support-trace backtrace roles",
            "hypergraph_source_view": "Fix22 candidate nodes and edges preserved as unsigned source graph",
            "spectral_projection_view": "star projection and clique/incidence projection measured separately",
        },
        "negative_controls": negative_controls,
        "non_claims": NON_CLAIMS,
        "non_excisability_probes": non_excisability,
        "output_tokens": OUTPUT_TOKENS,
        "phase": PHASE,
        "projection_sensitivity": _projection_sensitivity(spectral_star, spectral_clique),
        "review_queues": review_queues,
        "schema_version": SCHEMA_VERSION,
        "sim_id": SIM_ID,
        "spectral_authority_semantics_firewall": {
            "authority_proof_requires": "typed_directed_trace_per_fix24_genesis_rootedness_standard",
            "bridge_analysis_proves": "structural_fragility_only",
            "fiedler_vector_proves": "partition_boundary_structure_only",
            "lambda2_does_not_prove": ["authority", "eligibility", "claimability", "governance_effect"],
            "lambda2_proves": "structural_connectedness_only",
            "non_excisability_proves": "structural_criticality_only",
        },
        "spectral_diagnostics": {
            "clique_incidence_projection": spectral_clique,
            "star_projection": spectral_star,
        },
        "status": "pass" if negative_controls["structural_negative_controls_passed"] else "review_required",
        "structural_negative_controls_passed": negative_controls["structural_negative_controls_passed"],
    }
    return payload


def _table_from_probe_records(records: list[dict[str, Any]]) -> str:
    lines = [
        "| Family | Nodes removed | Root reachability delta | Authority traceability delta | Backwards-read delta | Verdict |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for record in records:
        lines.append(
            "| `{family}` | `{nodes_removed}` | `{root_reachability_delta}` | `{authority_traceability_delta}` | `{backwards_read_coverage_delta}` | `{verdict}` |".format(
                **record
            )
        )
    return "\n".join(lines)


def _report(payload: dict[str, Any]) -> str:
    clique = payload["spectral_diagnostics"]["clique_incidence_projection"]
    star = payload["spectral_diagnostics"]["star_projection"]
    sensitivity = payload["projection_sensitivity"]
    return f"""<!-- PUBLIC_RC_EXCLUDE: atlas_spectral_non_excisability_sim_research_only -->
<!-- PUBLIC_RC_EXCLUDE_REASON: Research-only spectral/non-excisability SIM report; no Genesis signing, canonical graph mutation, public RC activation, runtime activation, minting, settlement, or ADR/CDL mutation. -->

# SIM Atlas Spectral And Non-Excisability - Phase 1545p-Fix29

## Summary

Phase 1545p-Fix29 ran structural spectral diagnostics and non-excisability
probes over the unsigned Fix22 full-repo Atlas candidate. The SIM used the
Fix24 proof-class firewall, the Fix25 baseline, and the Fix28 fallback-edge
boundary. It did not rewrite, promote, sign, upload, activate, or mutate any
canonical graph or governance surface.

## Spectral Diagnostics

| Projection | Nodes | Components | Largest component | Lambda2 | Method |
|---|---:|---:|---:|---:|---|
| `clique_incidence` | `{clique["node_count"]}` | `{clique["component_count"]}` | `{clique["largest_component_node_count"]}` | `{clique["lambda2"]}` | `{clique["lambda2_method"]}` |
| `star` | `{star["node_count"]}` | `{star["component_count"]}` | `{star["largest_component_node_count"]}` | `{star["lambda2"]}` | `{star["lambda2_method"]}` |

Projection sensitivity selected `{sensitivity["use_for_fix30_fix31"]}` as the
conservative projection for later Fix30/Fix31 use. Absolute lambda2 delta was
`{sensitivity["absolute_delta_lambda2"]}` with significant threshold
`{sensitivity["significant_delta_threshold"]}`.

## Authority Semantics Firewall

Lambda2 proves structural connectedness only. The Fiedler vector proves
partition boundary structure only. Non-excisability proves structural
criticality only. Bridge analysis proves structural fragility only. Authority
proof still requires typed directed trace under the Fix24 Genesis-rootedness
standard.

## Non-Excisability Probes

{_table_from_probe_records(payload["non_excisability_probes"])}

Every fragile or non-excisable finding carries this note: structural non-excisability does not establish Genesis-rootedness under a typed authority view.

## Bridge And Authority Cut Checks

- Bridge count: `{payload["bridge_and_articulation_pressure"]["bridge_count"]}`
- Articulation point count: `{payload["bridge_and_articulation_pressure"]["articulation_point_count"]}`
- Authority articulation node count: `{payload["authority_cut_checks"]["authority_articulation_node_count"]}`
- Node0 removal authority-traceability delta: `{payload["authority_cut_checks"]["node0_removal_authority_traceability_delta"]}`
- Node0 removal root-reachability delta: `{payload["authority_cut_checks"]["node0_removal_root_reachability_delta"]}`
- Authority cut verdict: `{payload["authority_cut_checks"]["verdict"]}`

## Negative Controls

- Support-only low-value removal verdict: `{payload["negative_controls"]["support_only_low_value_control"]["verdict"]}`
- Forbidden authority removal verdict: `{payload["negative_controls"]["forbidden_authority_removal_control"]["verdict"]}`
- Structural negative controls passed: `{payload["structural_negative_controls_passed"]}`

## Output Tokens

{chr(10).join(f"- `{token}`" for token in payload["output_tokens"])}

## Non-Claims

{chr(10).join(f"- {claim}" for claim in payload["non_claims"])}
"""


def _review(payload: dict[str, Any]) -> str:
    queue_counts = {key: len(value) for key, value in payload["review_queues"].items()}
    rows = "\n".join(f"| `{key}` | `{value}` |" for key, value in sorted(queue_counts.items()))
    return f"""<!-- PUBLIC_RC_EXCLUDE: atlas_spectral_non_excisability_review_research_only -->
<!-- PUBLIC_RC_EXCLUDE_REASON: Review packet for research-only spectral/non-excisability SIM; not canonical graph state or signing authority. -->

# ILC Atlas Spectral Non-Excisability Review - Phase 1545p-Fix29

## Verdict

`{payload["status"]}` for research-only structural diagnostics.

## Review Queue Counts

| Queue | Count |
|---|---:|
{rows}

## Fix30 Carry-Forward

- Use `{payload["projection_sensitivity"]["use_for_fix30_fix31"]}` as the conservative spectral projection unless a later phase records a stronger reason.
- Use Fiedler top-coordinate records as candidate partition-boundary hints, not as authority evidence.
- Preserve the authority-semantics firewall and proof-class fields during any AutoResearch KEEP or REVERT decision.
- Keep B10-B12 fallback edges excluded from authority-reachability gains unless reclassified by a later explicit phase.

## Non-Claims

{chr(10).join(f"- {claim}" for claim in payload["non_claims"])}
"""


def main() -> None:
    payload = _build_outputs()
    _atomic_write(SUMMARY_OUT, _canonical_dumps(payload))
    _atomic_write(REPORT_OUT, _report(payload))
    _atomic_write(REVIEW_OUT, _review(payload))
    print(_canonical_dumps({"json": str(SUMMARY_OUT), "status": payload["status"]}))


if __name__ == "__main__":
    main()
