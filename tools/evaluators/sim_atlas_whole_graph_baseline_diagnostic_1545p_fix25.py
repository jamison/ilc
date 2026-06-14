#!/usr/bin/env python3
"""Whole-graph Genesis Atlas baseline diagnostic for Phase 1545p-Fix25.

PUBLIC_RC_EXCLUDE: genesis_atlas_baseline_diagnostic_research_only
PUBLIC_RC_EXCLUDE_REASON: Research-only diagnostic over unsigned Atlas candidates; no Genesis signing, node upload, public RC activation, or canonical graph mutation.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE = "1545p-Fix25"
SIM_ID = "SIM-ATLAS-WHOLE-GRAPH-BASELINE-DIAGNOSTIC-01"
SCHEMA_VERSION = "sim_atlas_whole_graph_baseline_diagnostic_1545p_fix25.v0.1"

NODE0 = "artifact:genesis_intent_attestation_init_authority_map"

FIX24_JSON = REPO_ROOT / "out/atlas_research/whole_graph_atlas_objective_contract_1545p_fix24.json"
FIX22_GRAPH = REPO_ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
FIX22_PREIMAGES = REPO_ROOT / "out/genesis_atlas_full_repo_node_preimages_1545p_fix22.jsonl"
FIX23_JSON = REPO_ROOT / "out/sim_genesis_atlas_lmdb_materialization_1545p_fix23.json"

JSON_OUT = REPO_ROOT / "out/sim_atlas_whole_graph_baseline_diagnostic_1545p_fix25.json"
REPORT_OUT = REPO_ROOT / "docs/sims/sim_atlas_whole_graph_baseline_diagnostic_1545p_fix25_v0.1.md"
REVIEW_OUT = REPO_ROOT / "docs/specs/ilc_atlas_whole_graph_baseline_diagnostic_review_1545p_fix25_v0.1.md"

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
PROMPT_PREFIXES = (
    "source",
    "repo",
    "atlas",
    "cdl",
    "adr",
    "truth_primitive",
    "policy",
    "artifact",
    "genesis_agent",
)

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
AUTHORITY_PREFIXES = ("adr:", "cdl:", "truth_primitive:", "policy:", "artifact:", "genesis_agent:", "ceremony:")
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
CLASSIFICATION_RELEVANT_KINDS = {
    "generated_evidence_node",
    "genesis_private_material_node",
    "sidecar_material_node",
}
CLASSIFICATION_RELEVANT_TIER_TOKENS = (
    "private",
    "excluded",
    "generated",
    "research",
    "binary",
    "harness",
)


def _canonical_dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


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


def _read_preimage_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"preimage_json_object_required:{path}:{line_no}")
        node_id = row.get("node_id")
        if not isinstance(node_id, str) or not node_id:
            raise ValueError(f"preimage_node_id_required:{path}:{line_no}")
        ids.add(node_id)
    return ids


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


def _prefix(node_id: str) -> str:
    prefix = node_id.split(":", 1)[0]
    return prefix if prefix in PROMPT_PREFIXES else "other"


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


def _is_classification_relevant(node: dict[str, Any]) -> bool:
    fields = " ".join(
        str(node.get(key, ""))
        for key in (
            "tier",
            "canonicality_tier",
            "authority_tier",
            "node_kind",
            "signature_status",
            "text_analysis_status",
        )
    ).lower()
    return str(node.get("node_kind", "")) in CLASSIFICATION_RELEVANT_KINDS or any(
        token in fields for token in CLASSIFICATION_RELEVANT_TIER_TOKENS
    )


def _normalize_label(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


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


def _component_count(node_ids: set[str], undirected: dict[str, set[str]]) -> tuple[int, int]:
    seen: set[str] = set()
    components = 0
    largest = 0
    for node_id in sorted(node_ids):
        if node_id in seen:
            continue
        components += 1
        size = 0
        queue: deque[str] = deque([node_id])
        seen.add(node_id)
        while queue:
            current = queue.popleft()
            size += 1
            for target in sorted(undirected.get(current, set())):
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        largest = max(largest, size)
    return components, largest


def _review_id(issue_class: str, node_id: str, evidence: list[str]) -> str:
    seed = _canonical_dumps({"evidence": evidence, "issue_class": issue_class, "node_id": node_id})
    return "atlas-review:" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def _review_record(
    issue_class: str,
    node_id: str,
    severity: str,
    evidence: list[str],
    recommended_next_fix: str,
) -> dict[str, Any]:
    return {
        "evidence": sorted(evidence),
        "issue_class": issue_class,
        "recommended_next_fix": recommended_next_fix,
        "review_id": _review_id(issue_class, node_id, evidence),
        "severity": severity,
        "source_node_id": node_id,
    }


def _build_diagnostic() -> dict[str, Any]:
    contract = _read_json(FIX24_JSON)
    graph = _read_json(FIX22_GRAPH)
    lmdb_report = _read_json(FIX23_JSON)
    preimage_ids = _read_preimage_ids(FIX22_PREIMAGES)

    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not all(isinstance(node, dict) for node in nodes):
        raise ValueError("fix22_nodes_list_required")
    if not isinstance(edges, list) or not all(isinstance(edge, dict) for edge in edges):
        raise ValueError("fix22_edges_list_required")

    node_by_id = {_node_id(node): node for node in nodes}
    node_ids = set(node_by_id)
    endpoint_errors: list[dict[str, Any]] = []
    undirected: dict[str, set[str]] = defaultdict(set)
    authority_forward_adjacency: dict[str, set[str]] = defaultdict(set)
    support_forward_adjacency: dict[str, set[str]] = defaultdict(set)
    backtrace_adjacency: dict[str, set[str]] = defaultdict(set)
    incoming_by_node: dict[str, list[dict[str, Any]]] = defaultdict(list)
    outgoing_by_node: dict[str, list[dict[str, Any]]] = defaultdict(list)
    edge_type_counts: Counter[str] = Counter()
    missing_decomposition_edges: list[dict[str, Any]] = []

    for edge in edges:
        source = _edge_endpoint(edge, "source")
        target = _edge_endpoint(edge, "target")
        edge_type = _edge_type(edge)
        edge_type_counts[edge_type] += 1
        if source not in node_ids or target not in node_ids:
            endpoint_errors.append(
                {
                    "edge_id": edge.get("edge_id"),
                    "edge_type": edge_type,
                    "source_missing": source not in node_ids,
                    "target_missing": target not in node_ids,
                }
            )
            continue
        undirected[source].add(target)
        undirected[target].add(source)
        outgoing_by_node[source].append(edge)
        incoming_by_node[target].append(edge)

        if edge_type in AUTHORITY_EDGE_TYPES:
            authority_forward_adjacency[source].add(target)
            backtrace_adjacency[target].add(source)
        elif edge_type in LEGACY_EQUIVALENT_TYPED_TRACE_ROLES:
            authority_forward_adjacency[source].add(target)
            backtrace_adjacency[target].add(source)
        elif edge_type in SUPPORT_TRACE_EDGE_TYPES:
            support_forward_adjacency[source].add(target)
            backtrace_adjacency[source].add(target)

        if edge_type not in CONTAINMENT_EDGE_TYPES and edge_type != "IMPORTS_MODULE":
            recipe = edge.get("decomposition_recipe")
            if not isinstance(recipe, dict) or not recipe:
                missing_decomposition_edges.append(
                    {
                        "edge_id": str(edge.get("edge_id", "")),
                        "edge_type": edge_type,
                        "source": source,
                        "target": target,
                    }
                )

    authority_terminals = _bfs({NODE0}, authority_forward_adjacency)

    authority_forward_covered: set[str] = set()
    for node_id in sorted(node_ids):
        if node_id in authority_terminals:
            authority_forward_covered.add(node_id)
            continue
        for edge in outgoing_by_node.get(node_id, []):
            if _edge_type(edge) in SUPPORT_TRACE_EDGE_TYPES | LEGACY_EQUIVALENT_TYPED_TRACE_ROLES:
                if _edge_endpoint(edge, "target") in authority_terminals:
                    authority_forward_covered.add(node_id)
                    break

    backtrace_covered = {node_id for node_id in node_ids if NODE0 in _bfs({node_id}, backtrace_adjacency)}

    classification_relevant = {
        node_id for node_id, node in node_by_id.items() if _is_classification_relevant(node)
    }
    classification_covered: set[str] = set()
    for node_id in sorted(classification_relevant):
        for edge in outgoing_by_node.get(node_id, []):
            if _edge_type(edge) == "CLASSIFIED_BY":
                target = _edge_endpoint(edge, "target")
                if target in authority_terminals or target in backtrace_covered:
                    classification_covered.add(node_id)
                    break

    authority_bearing = {node_id for node_id, node in node_by_id.items() if _is_authority_bearing(node_id, node)}
    authority_traceable = {
        node_id
        for node_id in authority_bearing
        if node_id == NODE0 or node_id in authority_forward_covered or node_id in backtrace_covered
    }
    source_derived = {node_id for node_id, node in node_by_id.items() if _is_source_derived(node_id, node)}
    backwards_read_covered = source_derived & backtrace_covered

    directed_gap = sorted(node_ids - authority_forward_covered - backtrace_covered - classification_covered)
    directed_gap_by_prefix = Counter(_prefix(node_id) for node_id in directed_gap)
    for prefix in (*PROMPT_PREFIXES, "other"):
        directed_gap_by_prefix.setdefault(prefix, 0)

    n_components, largest_component = _component_count(node_ids, undirected)
    orphan_nodes = sorted(node_id for node_id in node_ids if not undirected.get(node_id))

    file_nodes_with_preimages = {node_id for node_id in node_ids if node_id in preimage_ids}
    non_file_nodes = node_ids - source_derived
    merkle_membership_count = len(file_nodes_with_preimages) + len(non_file_nodes)

    label_clusters: dict[str, list[str]] = defaultdict(list)
    path_clusters: dict[str, list[str]] = defaultdict(list)
    for node_id, node in node_by_id.items():
        label = node.get("label")
        if isinstance(label, str) and label:
            label_clusters[_normalize_label(label)].append(node_id)
        source_path = node.get("source_path")
        if isinstance(source_path, str) and source_path:
            path_clusters[source_path].append(node_id)
    duplicate_clusters = [
        {"cluster_key": key, "node_ids": sorted(ids)}
        for key, ids in sorted(label_clusters.items())
        if len(ids) > 1
    ]
    duplicate_source_path_clusters = [
        {"cluster_key": key, "node_ids": sorted(ids)}
        for key, ids in sorted(path_clusters.items())
        if len(ids) > 1
    ]

    tier_counts = Counter(str(node.get("tier", "missing")) for node in nodes)
    kind_counts = Counter(str(node.get("node_kind", "missing")) for node in nodes)

    review_queue: list[dict[str, Any]] = []
    for node_id in sorted(authority_bearing - authority_traceable)[:50]:
        review_queue.append(
            _review_record(
                "authority_trace_gap",
                node_id,
                "high",
                [node_id, str(node_by_id[node_id].get("node_kind", ""))],
                "fix26",
            )
        )
    for node_id in sorted(backwards_read_covered ^ source_derived)[:40]:
        review_queue.append(
            _review_record(
                "backwards_read_gap",
                node_id,
                "medium",
                [node_id, str(node_by_id[node_id].get("source_path", ""))],
                "fix26",
            )
        )
    for node_id in sorted(classification_relevant - classification_covered)[:40]:
        review_queue.append(
            _review_record(
                "privacy_tier_gap",
                node_id,
                "medium",
                [node_id, str(node_by_id[node_id].get("tier", "")), str(node_by_id[node_id].get("node_kind", ""))],
                "fix28",
            )
        )
    for node_id in orphan_nodes[:20]:
        review_queue.append(
            _review_record(
                "orphan_support_leaf",
                node_id,
                "low",
                [node_id],
                "fix27",
            )
        )
    for cluster in duplicate_clusters[:20]:
        review_queue.append(
            _review_record(
                "duplicate_pressure",
                cluster["node_ids"][0],
                "low",
                cluster["node_ids"][:6],
                "fix27",
            )
        )
    for missing in missing_decomposition_edges[:40]:
        review_queue.append(
            _review_record(
                "decomposition_gap",
                str(missing["source"]),
                "medium",
                [str(missing["edge_id"]), str(missing["edge_type"])],
                "fix26",
            )
        )

    node_count = len(node_ids)
    classification_relevant_count = len(classification_relevant)
    non_containment_edge_count = sum(
        count for edge_type, count in edge_type_counts.items() if edge_type not in CONTAINMENT_EDGE_TYPES and edge_type != "IMPORTS_MODULE"
    )

    lmdb_counts = lmdb_report.get("materialization", {}).get("counts", {})
    lmdb_round_trip = lmdb_report.get("materialization", {}).get("round_trip", {})
    fix24_standard = contract.get("genesis_rootedness_standard", {})

    return {
        "authority_bearing_node_count": len(authority_bearing),
        "authority_forward_terminal_count": len(authority_terminals),
        "authority_forward_trace_coverage": _ratio(len(authority_forward_covered), node_count),
        "authority_forward_trace_covered_count": len(authority_forward_covered),
        "authority_reachability": _ratio(len(authority_traceable), len(authority_bearing)),
        "authority_traceable_node_count": len(authority_traceable),
        "backwards_read_coverage": _ratio(len(backwards_read_covered), len(source_derived)),
        "backwards_read_covered_source_node_count": len(backwards_read_covered),
        "classification_relevant_node_count": classification_relevant_count,
        "classification_rule_trace_coverage": _ratio(len(classification_covered), classification_relevant_count),
        "classification_rule_trace_covered_count": len(classification_covered),
        "coverage": _ratio(largest_component, node_count),
        "decomposition_coverage": _ratio(non_containment_edge_count - len(missing_decomposition_edges), non_containment_edge_count),
        "decomposition_required_edge_count": non_containment_edge_count,
        "directed_view_not_yet_contractualized_by_prefix": dict(sorted(directed_gap_by_prefix.items())),
        "directed_view_not_yet_contractualized_count": len(directed_gap),
        "edge_count": len(edges),
        "edge_type_counts": dict(sorted(edge_type_counts.items())),
        "endpoint_error_count": len(endpoint_errors),
        "endpoint_errors_sample": endpoint_errors[:20],
        "fix23_lmdb_cross_check": {
            "edge_count_match": lmdb_counts.get("source_edge_count") == len(edges) == lmdb_counts.get("lmdb_edge_count"),
            "node_count_match": lmdb_counts.get("source_node_count") == node_count == lmdb_counts.get("lmdb_node_count"),
            "preimage_count_match": lmdb_counts.get("source_preimage_count") == len(preimage_ids) == lmdb_counts.get("lmdb_preimage_count"),
            "round_trip": lmdb_round_trip,
        },
        "genesis_bound_transition_envelope_view_status": "not_yet_implemented_not_measured",
        "genesis_rootedness_standard": {
            "accepted_typed_trace_roles": fix24_standard.get("accepted_typed_trace_roles", []),
            "authority_root_node": NODE0,
            "legacy_equivalent_typed_trace_roles_used_for_baseline": sorted(LEGACY_EQUIVALENT_TYPED_TRACE_ROLES),
            "merkle_and_lambda2_authority_scope": "not_sufficient_for_authority_eligibility_claimability_or_governance_effect",
        },
        "graph_projection_used": "full_hypergraph|undirected_adjacency|directed_typed_trace_projection",
        "largest_component_node_count": largest_component,
        "merkle_source_tree_membership_coverage": _ratio(merkle_membership_count, node_count),
        "merkle_source_tree_membership_count": merkle_membership_count,
        "missing_decomposition_edge_count": len(missing_decomposition_edges),
        "missing_decomposition_edges_sample": missing_decomposition_edges[:20],
        "n_components": n_components,
        "negative_controls": {
            "private_or_excluded_nodes_remain_non_authority_count": len(
                classification_relevant - authority_bearing
            ),
            "support_only_nodes_remain_non_authority_count": len(
                source_derived - authority_bearing
            ),
        },
        "node_count": node_count,
        "node_kind_counts": dict(sorted(kind_counts.items())),
        "non_claims": [
            "No graph rewrite occurred.",
            "No Genesis signing occurred.",
            "No node upload occurred.",
            "No public RC activation occurred.",
            "No canonical Genesis graph mutation occurred.",
            "No ADR or CDL mutation occurred.",
            "Merkle inclusion and undirected connectedness are not treated as authority proof.",
        ],
        "orphan_count": len(orphan_nodes),
        "orphan_nodes_sample": orphan_nodes[:20],
        "phase": PHASE,
        "privacy_tier_consistency": {
            "classification_gap_count": len(classification_relevant - classification_covered),
            "classification_relevant_node_count": classification_relevant_count,
            "tier_counts": dict(sorted(tier_counts.items())),
        },
        "review_queue": review_queue[:200],
        "schema_version": SCHEMA_VERSION,
        "sim_id": SIM_ID,
        "source_derived_node_count": len(source_derived),
        "source_git_commit": graph.get("source_git_commit"),
        "status": "committed_research_only_baseline_diagnostic",
        "tokens": [
            "whole_graph_atlas_baseline_diagnostic_committed_phase_1545p_fix25",
            "atlas_authority_trace_baseline_recorded_phase_1545p_fix25",
            "atlas_backwards_read_baseline_recorded_phase_1545p_fix25",
            "atlas_duplicate_merge_pressure_baseline_recorded_phase_1545p_fix25",
            "atlas_privacy_tier_baseline_recorded_phase_1545p_fix25",
            "public_path_remains_blocked_phase_1545p_fix25",
        ],
        "top_duplicate_label_clusters": duplicate_clusters[:20],
        "top_duplicate_source_path_clusters": duplicate_source_path_clusters[:20],
        "undirected_laplacian_connectedness": _ratio(largest_component, node_count),
        "verification_backtrace_coverage": _ratio(len(backtrace_covered), node_count),
        "verification_backtrace_covered_count": len(backtrace_covered),
    }


def _table_from_counts(counts: dict[str, Any]) -> list[str]:
    lines = ["| Key | Count |", "|---|---:|"]
    for key, value in sorted(counts.items()):
        lines.append(f"| `{key}` | `{value}` |")
    return lines


def _report(payload: dict[str, Any]) -> str:
    lines = [
        "# SIM-ATLAS-WHOLE-GRAPH-BASELINE-DIAGNOSTIC-01",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: genesis_atlas_baseline_diagnostic_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: research-only whole-graph Atlas baseline diagnostic; no Genesis signing, node upload, public RC activation, or canonical graph mutation -->",
        "",
        f"**Phase:** {PHASE}",
        f"**Status:** {payload['status']}",
        "**Sensitivity:** NON-SENSITIVE",
        "",
        "## Scope",
        "",
        "This SIM measures the unsigned Fix22/Fix23 whole-repo Atlas candidate against",
        "the Fix24 proof-class contract. It is evidence-only and does not rewrite,",
        "promote, sign, upload, or activate any graph surface.",
        "",
        "## Mandatory Coverage Dimensions",
        "",
        "| Metric | Projection | Value | Count |",
        "|---|---|---:|---:|",
        f"| Merkle/source-tree membership | source-tree/preimage membership | `{payload['merkle_source_tree_membership_coverage']}` | `{payload['merkle_source_tree_membership_count']}/{payload['node_count']}` |",
        f"| Undirected/Laplacian connectedness | undirected adjacency | `{payload['undirected_laplacian_connectedness']}` | `{payload['largest_component_node_count']}/{payload['node_count']}` |",
        f"| Authority-forward trace coverage | directed typed-trace | `{payload['authority_forward_trace_coverage']}` | `{payload['authority_forward_trace_covered_count']}/{payload['node_count']}` |",
        f"| Verification/backtrace coverage | directed typed-trace | `{payload['verification_backtrace_coverage']}` | `{payload['verification_backtrace_covered_count']}/{payload['node_count']}` |",
        f"| Classification-rule trace coverage | directed typed-trace | `{payload['classification_rule_trace_coverage']}` | `{payload['classification_rule_trace_covered_count']}/{payload['classification_relevant_node_count']}` |",
        "",
        "The Genesis-bound transition envelope view is `not_yet_implemented_not_measured`",
        "and is not counted as a failed coverage denominator.",
        "",
        "## Baseline Metrics",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Node count | `{payload['node_count']}` |",
        f"| Edge count | `{payload['edge_count']}` |",
        f"| Components | `{payload['n_components']}` |",
        f"| Orphan nodes | `{payload['orphan_count']}` |",
        f"| Authority reachability over authority-bearing nodes | `{payload['authority_reachability']}` |",
        f"| Backwards-read coverage over source-derived nodes | `{payload['backwards_read_coverage']}` |",
        f"| Decomposition coverage over required edges | `{payload['decomposition_coverage']}` |",
        f"| Missing decomposition edges | `{payload['missing_decomposition_edge_count']}` |",
        f"| directed_view_not_yet_contractualized | `{payload['directed_view_not_yet_contractualized_count']}` |",
        "",
        "## Directed View Gap By Prefix",
        "",
    ]
    lines.extend(_table_from_counts(payload["directed_view_not_yet_contractualized_by_prefix"]))
    lines.extend(["", "## Edge Type Counts", ""])
    lines.extend(_table_from_counts(payload["edge_type_counts"]))
    lines.extend(["", "## Review Queue Summary", ""])
    issue_counts = Counter(row["issue_class"] for row in payload["review_queue"])
    lines.extend(_table_from_counts(dict(issue_counts)))
    lines.extend(["", "## Output Tokens", ""])
    for token in payload["tokens"]:
        lines.append(f"- `{token}`")
    lines.extend(["", "## Non-Claims", ""])
    for claim in payload["non_claims"]:
        lines.append(f"- {claim}")
    lines.append("")
    return "\n".join(lines)


def _review(payload: dict[str, Any]) -> str:
    lines = [
        "# ILC Atlas Whole-Graph Baseline Diagnostic Review 1545p-Fix25 v0.1",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: genesis_atlas_baseline_diagnostic_review_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: review packet for unsigned Atlas baseline diagnostic; not canonical graph state or signing authority -->",
        "",
        "## Finding",
        "",
        "The Fix25 diagnostic establishes the measurement floor for Fix26-Fix31.",
        "The whole-repo candidate is structurally connected, but typed directed",
        "Genesis-rootedness remains a separate proof class and is not inferred from",
        "Merkle membership or undirected connectivity.",
        "",
        "## Required Follow-On Boundaries",
        "",
        "- Fix26 must use the review queue as input for extraction replay and must not mutate the canonical graph.",
        "- Fix27 and Fix30 must not erase proof-class fields while improving spectral or structural scores.",
        "- Fix31 must not mark a node Atlas signing-batch-ready without a declared typed trace role and traversal direction.",
        "- The transition-envelope view remains `not_yet_implemented_not_measured` until separately specified.",
        "",
        "## Review Queue Samples",
        "",
        "| Issue | Severity | Node | Next Fix |",
        "|---|---|---|---|",
    ]
    for row in payload["review_queue"][:25]:
        lines.append(
            f"| `{row['issue_class']}` | `{row['severity']}` | `{row['source_node_id']}` | `{row['recommended_next_fix']}` |"
        )
    lines.extend(["", "## Non-Claims", ""])
    for claim in payload["non_claims"]:
        lines.append(f"- {claim}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    payload = _build_diagnostic()
    _atomic_write(JSON_OUT, _canonical_dumps(payload))
    _atomic_write(REPORT_OUT, _report(payload))
    _atomic_write(REVIEW_OUT, _review(payload))
    print(_canonical_dumps({"json": str(JSON_OUT), "status": payload["status"]}))


if __name__ == "__main__":
    main()
