#!/usr/bin/env python3
"""Classify graph_projection for all nodes in the unified Atlas LMDB.

PUBLIC_RC_EXCLUDE: fix55_lmdb_graph_projection_classification_evaluator
PUBLIC_RC_EXCLUDE_REASON: Local research LMDB metadata patch; not public graph activation, Genesis signing, canonical graph mutation, or public RC publication.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import eigsh


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (  # noqa: E402
    GenesisAtlasCandidateStore,
)


PHASE = "1545p-Fix55"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix55_projection_classification_report_v0.1.json"
FIEDLER_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix55_fiedler_projection_analysis_v0.1.json"
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"
EXPECTED_NODE_COUNT = 15677
EXPECTED_PRIVATE_NODE_COUNT = 475
EXPECTED_LEGACY_CORE_STAR_MAP_COUNT = 54

PROJECTION_VALUES = (
    "genesis_core_star_map",
    "public_protocol_graph",
    "support_candidate_graph",
    "excluded_private_material",
    "review_required",
)

GENESIS_ARTIFACT_ALLOWLIST = frozenset(
    {
        "artifact:genesis_agent1_pubkey_record_838a",
        "artifact:genesis_intent_attestation_init_authority_map",
        "artifact:genesis_state_bundle",
    }
)

GENESIS_CORE_CANONICALITY = frozenset(
    {
        "binding_config",
        "ratified_cdl",
        "retrospective_genesis_attestation",
    }
)

PUBLIC_PROTOCOL_CANONICALITY = frozenset(
    {
        "accepted_adr",
        "draft_direction_accepted",
        "fix41a_candidate_terminal",
        "implemented_runtime",
        "locked_spec",
        "ratified_or_evidence",
    }
)

SUPPORT_CANONICALITY = frozenset(
    {
        "fix38_candidate_overlay",
        "fix40_candidate_terminal",
    }
)


def _canonical_text(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _sha256_payload(payload: Any) -> str:
    return hashlib.sha256(_canonical_text(payload).encode("utf-8")).hexdigest()


def _atomic_write(path: Path, payload: Any) -> None:
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
            handle.write(_canonical_text(payload))
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix55_node_missing_candidate_id")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    value = edge.get("source", edge.get("source_candidate_id", edge.get("from", "")))
    return value if isinstance(value, str) else ""


def _edge_target(edge: dict[str, Any]) -> str:
    value = edge.get("target", edge.get("target_candidate_id", edge.get("to", "")))
    return value if isinstance(value, str) else ""


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type", edge.get("type", ""))
    return value if isinstance(value, str) else ""


def _decode_repo_file_path(candidate_id: str) -> str:
    if not candidate_id.startswith("repo:file:"):
        return ""
    parts = candidate_id.split(":", 2)
    if len(parts) != 3:
        return ""
    raw = parts[2]
    separator = raw.find(":")
    if separator < 0:
        return raw.replace("_", "/")
    return raw[separator + 1 :].replace("_", "/")


def _path_for_node(node: dict[str, Any]) -> str:
    for key in ("source_path", "path"):
        value = node.get(key)
        if isinstance(value, str) and value:
            return value
    return _decode_repo_file_path(_candidate_id(node))


def _path_contains_private_material(node: dict[str, Any]) -> bool:
    candidate_id = _candidate_id(node)
    path = _path_for_node(node)
    haystack = f"{candidate_id}\n{path}"
    return "z_past_chats" in haystack or "Z_Past_Chats" in haystack


def _classify_node(node: dict[str, Any]) -> tuple[str, str]:
    candidate_id = _candidate_id(node)
    node_kind = str(node.get("node_kind", ""))
    canonicality_tier = str(node.get("canonicality_tier", ""))
    graph_projection = node.get("graph_projection")
    path = _path_for_node(node)

    if node_kind == "genesis_private_material_node":
        return "excluded_private_material", "rule_01_private_node_kind"
    if _path_contains_private_material(node):
        return "excluded_private_material", "rule_02_private_path"
    if isinstance(graph_projection, str) and graph_projection and graph_projection != "core_star_map":
        return graph_projection, "rule_03_preserve_non_legacy"
    if graph_projection == "core_star_map":
        return "genesis_core_star_map", "rule_04_migrate_legacy_core_star_map"
    if node_kind == "cdl_artifact":
        return "genesis_core_star_map", "rule_05_cdl_artifact"
    if node_kind == "operator_primitive":
        return "genesis_core_star_map", "rule_06_operator_primitive"
    if node_kind == "epistemic_gap":
        return "support_candidate_graph", "rule_07_epistemic_gap_support"
    if candidate_id.startswith("invariant:"):
        return "genesis_core_star_map", "rule_08_invariant_prefix"
    if candidate_id.startswith("policy:"):
        return "genesis_core_star_map", "rule_09_policy_prefix"
    if candidate_id.startswith("cdl:"):
        return "genesis_core_star_map", "rule_10_cdl_prefix"
    if candidate_id.startswith("adr:"):
        return "genesis_core_star_map", "rule_11_adr_prefix"
    if candidate_id in GENESIS_ARTIFACT_ALLOWLIST:
        return "genesis_core_star_map", "rule_12_genesis_artifact_allowlist"
    if candidate_id.startswith("gap:"):
        return "support_candidate_graph", "rule_13_gap_prefix_support"
    if canonicality_tier in GENESIS_CORE_CANONICALITY:
        return "genesis_core_star_map", "rule_14_genesis_core_canonicality"
    if canonicality_tier in PUBLIC_PROTOCOL_CANONICALITY:
        return "public_protocol_graph", "rule_15_public_protocol_canonicality"
    if canonicality_tier in SUPPORT_CANONICALITY:
        return "support_candidate_graph", "rule_16_support_canonicality"
    if node_kind == "adr_artifact":
        return "genesis_core_star_map", "rule_17_adr_artifact"
    if node_kind == "adr_document_node":
        return "public_protocol_graph", "rule_18_adr_document_node"
    if node_kind == "sidecar_material_node":
        return "public_protocol_graph", "rule_19_sidecar_material_node"
    if node_kind == "runtime_source_file_node" and path.startswith("ilc_core/"):
        return "public_protocol_graph", "rule_20_runtime_source_ilc_core"
    if node_kind == "runtime_source_file_node":
        return "support_candidate_graph", "rule_21_runtime_source_other"
    if node_kind in {"test_evidence_node", "generated_evidence_node", "sim_evidence_node"}:
        return "support_candidate_graph", "rule_22_evidence_node"
    if node_kind == "tooling_source_file_node":
        return "support_candidate_graph", "rule_23_tooling_source_file_node"
    if node_kind in {"repo_group_node", "repo_material_root", "repo_manifest_root"}:
        return "support_candidate_graph", "rule_24_repo_group_or_root"
    if node_kind == "spec_document_node" and path.startswith("docs/adr/"):
        return "public_protocol_graph", "rule_25_spec_docs_adr"
    if node_kind == "spec_document_node" and path.startswith("docs/architecture/"):
        return "public_protocol_graph", "rule_26_spec_docs_architecture"
    if node_kind == "spec_document_node" and path.startswith("docs/whitepaper/"):
        return "public_protocol_graph", "rule_27_spec_docs_whitepaper"
    if node_kind == "spec_document_node":
        return "support_candidate_graph", "rule_28_spec_document_support"
    if candidate_id.startswith("phase:"):
        return "support_candidate_graph", "rule_29_phase_prefix_support"
    if node_kind == "repo_material_node" and path.startswith("ilc_core/"):
        return "public_protocol_graph", "rule_30_repo_material_ilc_core"
    if node_kind == "repo_material_node" and path.startswith("docs/adr/"):
        return "public_protocol_graph", "rule_31_repo_material_docs_adr"
    if node_kind == "repo_material_node" and path.startswith("docs/architecture/"):
        return "public_protocol_graph", "rule_32_repo_material_docs_architecture"
    if node_kind == "repo_material_node" and path.startswith("docs/whitepaper/"):
        return "public_protocol_graph", "rule_33_repo_material_docs_whitepaper"
    if node_kind == "repo_material_node":
        return "support_candidate_graph", "rule_34_repo_material_support"
    return "review_required", "rule_fallback_review_required"


def _strip_graph_projection(node: dict[str, Any]) -> dict[str, Any]:
    clone = dict(node)
    clone.pop("graph_projection", None)
    return clone


def _only_graph_projection_changed(
    before_nodes: list[dict[str, Any]],
    after_nodes: list[dict[str, Any]],
) -> bool:
    before_by_id = {_candidate_id(node): _strip_graph_projection(node) for node in before_nodes}
    after_by_id = {_candidate_id(node): _strip_graph_projection(node) for node in after_nodes}
    return before_by_id == after_by_id


def _normalized_laplacian(node_ids: list[str], edges: list[dict[str, Any]]) -> tuple[sp.csr_matrix, dict[str, int], Counter[int]]:
    node_index = {node_id: index for index, node_id in enumerate(node_ids)}
    undirected: set[tuple[int, int]] = set()
    degree: Counter[int] = Counter()
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        if source not in node_index or target not in node_index:
            continue
        u = node_index[source]
        v = node_index[target]
        if u == v:
            continue
        pair = (u, v) if u < v else (v, u)
        if pair not in undirected:
            undirected.add(pair)
            degree[u] += 1
            degree[v] += 1

    row: list[int] = []
    col: list[int] = []
    values: list[float] = []
    for u, v in sorted(undirected):
        du = degree[u]
        dv = degree[v]
        if du <= 0 or dv <= 0:
            continue
        weight = -1.0 / math.sqrt(float(du * dv))
        row.extend([u, v])
        col.extend([v, u])
        values.extend([weight, weight])
    for index in range(len(node_ids)):
        if degree[index] > 0:
            row.append(index)
            col.append(index)
            values.append(1.0)
        else:
            row.append(index)
            col.append(index)
            values.append(0.0)
    matrix = sp.csr_matrix((values, (row, col)), shape=(len(node_ids), len(node_ids)), dtype=float)
    return matrix, node_index, degree


def _adjacency(node_ids: list[str], edges: list[dict[str, Any]]) -> sp.csr_matrix:
    node_index = {node_id: index for index, node_id in enumerate(node_ids)}
    undirected: set[tuple[int, int]] = set()
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        if source not in node_index or target not in node_index:
            continue
        u = node_index[source]
        v = node_index[target]
        if u == v:
            continue
        pair = (u, v) if u < v else (v, u)
        undirected.add(pair)
    row: list[int] = []
    col: list[int] = []
    values: list[int] = []
    for u, v in sorted(undirected):
        row.extend([u, v])
        col.extend([v, u])
        values.extend([1, 1])
    return sp.csr_matrix((values, (row, col)), shape=(len(node_ids), len(node_ids)), dtype=int)


def _fiedler_metrics(
    *,
    projection_name: str,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, Any]:
    node_ids = [_candidate_id(node) for node in nodes]
    node_set = set(node_ids)
    projected_edges = [
        edge
        for edge in edges
        if _edge_source(edge) in node_set and _edge_target(edge) in node_set
    ]
    authority_counts = _authority_coverage(nodes=nodes, edges=projected_edges)

    result: dict[str, Any] = {
        "authority_coverage": authority_counts,
        "edge_count": len(projected_edges),
        "fiedler_value_lambda2": None,
        "minority_cluster_sample": [],
        "minority_cluster_size": 0,
        "node_count": len(nodes),
        "projection": projection_name,
        "spectral_caveat": (
            "Fiedler vector gives a spectral relaxation of the minimum sparse-cut problem, "
            "not a proof of the exact minimum cut."
        ),
    }
    if len(nodes) < 3:
        result["status"] = "SKIP_TOO_FEW_NODES"
        return result

    adjacency = _adjacency(node_ids, projected_edges)
    component_count, labels = connected_components(adjacency, directed=False, return_labels=True)
    result["connected_component_count"] = int(component_count)
    if component_count > 1:
        label_counts = Counter(int(label) for label in labels)
        result["component_size_counts"] = dict(sorted(label_counts.items()))
        result["fiedler_value_lambda2"] = 0.0
        result["smallest_eigenvalues"] = []
        if NODE0 in node_ids:
            node0_label = int(labels[node_ids.index(NODE0)])
            minority = [
                (node_id, 0.0)
                for node_id, index in {node_id: i for i, node_id in enumerate(node_ids)}.items()
                if int(labels[index]) != node0_label
            ]
            result["minority_reference_node"] = NODE0
            result["node0_component_size"] = int(label_counts[node0_label])
        else:
            smallest_label = min(label_counts, key=lambda label: (label_counts[label], label))
            minority = [
                (node_id, 0.0)
                for node_id, index in {node_id: i for i, node_id in enumerate(node_ids)}.items()
                if int(labels[index]) == smallest_label
            ]
            result["minority_reference_node"] = "smallest_connected_component"
        result["minority_cluster_size"] = len(minority)
        result["minority_cluster_sample"] = [
            {"fiedler_coordinate": "0", "node_id": node_id}
            for node_id, _coordinate in sorted(minority, key=lambda row: row[0])[:25]
        ]
        result["status"] = "PASS_DISCONNECTED_PROJECTION"
        result["spectral_note"] = (
            "Projection is disconnected; algebraic connectivity lambda2 is exactly 0. "
            "No Fiedler vector partition is treated as authoritative for this projection."
        )
        return result

    laplacian, node_index, _degree = _normalized_laplacian(node_ids, projected_edges)
    k = min(3, len(nodes) - 1)
    try:
        values, vectors = eigsh(laplacian, k=k, which="SM", tol=1e-6, maxiter=10000)
    except Exception as exc:  # pragma: no cover - defensive report path
        result["status"] = "EIGSH_FAILED"
        result["error"] = str(exc)
        return result
    order = np.argsort(values)
    sorted_values = [float(values[index]) for index in order]
    result["smallest_eigenvalues"] = sorted_values
    if len(order) < 2:
        result["status"] = "SKIP_NO_FIEDLER_VECTOR"
        return result

    fiedler_value = max(0.0, float(values[order[1]]))
    result["fiedler_value_lambda2"] = fiedler_value
    fiedler_vector = vectors[:, order[1]]
    if NODE0 in node_index:
        reference_positive = bool(fiedler_vector[node_index[NODE0]] >= 0)
        minority = [
            (node_id, float(fiedler_vector[index]))
            for node_id, index in node_index.items()
            if bool(fiedler_vector[index] >= 0) != reference_positive
        ]
        result["minority_reference_node"] = NODE0
    else:
        label_counts = Counter(int(label) for label in labels)
        smallest_label = min(label_counts, key=lambda label: (label_counts[label], label))
        minority = [
            (node_id, 0.0)
            for node_id, index in node_index.items()
            if int(labels[index]) == smallest_label
        ]
        result["minority_reference_node"] = "smallest_connected_component"
    minority_sorted = sorted(minority, key=lambda row: (abs(row[1]), row[0]), reverse=True)
    result["minority_cluster_size"] = len(minority)
    result["minority_cluster_sample"] = [
        {"fiedler_coordinate": f"{coordinate:.12g}", "node_id": node_id}
        for node_id, coordinate in minority_sorted[:25]
    ]
    result["status"] = "PASS"
    return result


def _authority_coverage(*, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    node_ids = {_candidate_id(node) for node in nodes}
    invariant_ids = sorted(node_id for node_id in node_ids if node_id.startswith("invariant:"))
    policy_ids = sorted(node_id for node_id in node_ids if node_id.startswith("policy:"))
    governs_targets = {
        _edge_target(edge)
        for edge in edges
        if _edge_type(edge) == "GOVERNS" and _edge_target(edge) in node_ids
    }
    invariant_governed = [node_id for node_id in invariant_ids if node_id in governs_targets]
    policy_governed = [node_id for node_id in policy_ids if node_id in governs_targets]
    return {
        "invariant_governed_count": len(invariant_governed),
        "invariant_total": len(invariant_ids),
        "policy_governed_count": len(policy_governed),
        "policy_total": len(policy_ids),
    }


def _projection_nodes(nodes: list[dict[str, Any]], projection_name: str) -> list[dict[str, Any]]:
    if projection_name == "all_local":
        return nodes
    if projection_name == "public_eligible":
        return [
            node
            for node in nodes
            if node.get("graph_projection")
            in {"genesis_core_star_map", "public_protocol_graph", "support_candidate_graph"}
        ]
    if projection_name == "authority_only":
        return [node for node in nodes if node.get("graph_projection") == "genesis_core_star_map"]
    raise ValueError(f"fix55_unknown_projection:{projection_name}")


def _run_fiedler_analysis(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    projections = {}
    for projection_name in ("all_local", "public_eligible", "authority_only"):
        projections[projection_name] = _fiedler_metrics(
            projection_name=projection_name,
            nodes=_projection_nodes(nodes, projection_name),
            edges=edges,
        )
    return {
        "phase": PHASE,
        "projections": projections,
        "spectral_caveat": (
            "Fiedler vector gives a spectral relaxation of the minimum sparse-cut problem, "
            "not a proof of the exact minimum cut."
        ),
        "status": "PASS",
    }


def classify_lmdb(
    *,
    lmdb_root: Path = LMDB_ROOT,
    report_path: Path = REPORT_PATH,
    fiedler_report_path: Path = FIEDLER_REPORT_PATH,
) -> dict[str, Any]:
    store = GenesisAtlasCandidateStore(lmdb_root, allow_synthetic_edge_keys=True)
    try:
        pre_payload = store.get_graph_payload()
        if not isinstance(pre_payload, dict):
            raise ValueError("fix55_graph_payload_missing")
        pre_nodes = pre_payload.get("nodes")
        pre_edges = pre_payload.get("edges")
        if not isinstance(pre_nodes, list) or not all(isinstance(node, dict) for node in pre_nodes):
            raise ValueError("fix55_graph_payload_nodes_invalid")
        if not isinstance(pre_edges, list) or not all(isinstance(edge, dict) for edge in pre_edges):
            raise ValueError("fix55_graph_payload_edges_invalid")
        if len(pre_nodes) != EXPECTED_NODE_COUNT:
            raise ValueError(f"fix55_unexpected_pre_node_count:{len(pre_nodes)}")

        pre_mutation_digest = _sha256_payload(pre_payload)
        nodes_with_projection_before = sum(1 for node in pre_nodes if node.get("graph_projection"))
        private_node_count = sum(
            1 for node in pre_nodes if node.get("node_kind") == "genesis_private_material_node"
        )
        legacy_core_count = sum(1 for node in pre_nodes if node.get("graph_projection") == "core_star_map")
        all_projection_values = {
            node.get("graph_projection")
            for node in pre_nodes
            if isinstance(node.get("graph_projection"), str) and node.get("graph_projection")
        }
        if (
            nodes_with_projection_before == EXPECTED_NODE_COUNT
            and legacy_core_count == 0
            and all_projection_values.issubset(set(PROJECTION_VALUES))
            and report_path.exists()
        ):
            fiedler_report = _run_fiedler_analysis(pre_nodes, pre_edges)
            _atomic_write(fiedler_report_path, fiedler_report)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if not isinstance(report, dict) or report.get("status") != "PASS":
                raise ValueError("fix55_existing_report_invalid_for_idempotent_rerun")
            store.put_meta("fix55_graph_projection_classification", report)
            return report

        if private_node_count != EXPECTED_PRIVATE_NODE_COUNT:
            raise ValueError(f"fix55_unexpected_private_node_count:{private_node_count}")
        if legacy_core_count != EXPECTED_LEGACY_CORE_STAR_MAP_COUNT:
            raise ValueError(f"fix55_unexpected_legacy_core_star_map_count:{legacy_core_count}")

        updated_nodes: list[dict[str, Any]] = []
        rule_counts: Counter[str] = Counter()
        value_counts: Counter[str] = Counter()
        review_required_ids: list[str] = []
        for node in pre_nodes:
            updated = copy.deepcopy(node)
            value, rule = _classify_node(updated)
            if value not in PROJECTION_VALUES:
                raise ValueError(f"fix55_invalid_projection_value:{value}")
            updated["graph_projection"] = value
            updated_nodes.append(updated)
            rule_counts[rule] += 1
            value_counts[value] += 1
            if value == "review_required":
                review_required_ids.append(_candidate_id(updated))

        nodes_with_projection_after = sum(1 for node in updated_nodes if node.get("graph_projection"))
        if nodes_with_projection_after != EXPECTED_NODE_COUNT:
            raise ValueError("fix55_nodes_missing_graph_projection_after_classification")
        if value_counts["excluded_private_material"] < EXPECTED_PRIVATE_NODE_COUNT:
            raise ValueError("fix55_private_material_not_excluded")
        if any(node.get("graph_projection") == "core_star_map" for node in updated_nodes):
            raise ValueError("fix55_legacy_core_star_map_value_remaining")

        updated_payload = copy.deepcopy(pre_payload)
        updated_payload["nodes"] = updated_nodes
        post_mutation_digest = _sha256_payload(updated_payload)
        digest_proof = {
            "edge_count_unchanged": len(pre_edges) == len(updated_payload.get("edges", [])),
            "node_count_unchanged": len(pre_nodes) == len(updated_nodes),
            "only_graph_projection_field_changed": _only_graph_projection_changed(pre_nodes, updated_nodes),
            "pre_post_differ": pre_mutation_digest != post_mutation_digest,
        }
        if not all(digest_proof.values()):
            raise ValueError(f"fix55_digest_proof_failed:{digest_proof}")

        store.put_nodes(updated_nodes)
        store.put_graph_payload(updated_payload)

        persisted_payload = store.get_graph_payload()
        if not isinstance(persisted_payload, dict):
            raise ValueError("fix55_persisted_graph_payload_missing")
        persisted_nodes = persisted_payload.get("nodes")
        if not isinstance(persisted_nodes, list) or len(persisted_nodes) != EXPECTED_NODE_COUNT:
            raise ValueError("fix55_persisted_graph_payload_nodes_invalid")
        if any(not node.get("graph_projection") for node in persisted_nodes if isinstance(node, dict)):
            raise ValueError("fix55_persisted_nodes_missing_graph_projection")

        fiedler_report = _run_fiedler_analysis(updated_nodes, pre_edges)
        report = {
            "digest_proof": digest_proof,
            "lmdb_path": str(lmdb_root.relative_to(REPO_ROOT) if lmdb_root.is_absolute() else lmdb_root),
            "nodes_with_projection_after": nodes_with_projection_after,
            "nodes_with_projection_before": nodes_with_projection_before,
            "phase": PHASE,
            "post_mutation_digest": post_mutation_digest,
            "pre_mutation_digest": pre_mutation_digest,
            "private_node_count": private_node_count,
            "projection_vocabulary_note": (
                "genesis_core_star_map is a projection bucket only - not a signing class or authority grant"
            ),
            "review_required_ids": sorted(review_required_ids),
            "rule_hit_counts": dict(sorted(rule_counts.items())),
            "status": "PASS",
            "total_nodes_classified": EXPECTED_NODE_COUNT,
            "value_counts": {key: int(value_counts.get(key, 0)) for key in PROJECTION_VALUES},
        }
        store.put_meta("fix55_graph_projection_classification", report)
    finally:
        store.close()

    _atomic_write(report_path, report)
    _atomic_write(fiedler_report_path, fiedler_report)
    return report


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lmdb-root", type=Path, default=LMDB_ROOT)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--fiedler-report", type=Path, default=FIEDLER_REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = classify_lmdb(
        lmdb_root=args.lmdb_root,
        report_path=args.report,
        fiedler_report_path=args.fiedler_report,
    )
    counts = report["value_counts"]
    print(
        "Done. status=PASS, "
        f"classified={report['total_nodes_classified']}, "
        f"genesis_core_star_map={counts['genesis_core_star_map']}, "
        f"public_protocol={counts['public_protocol_graph']}, "
        f"support={counts['support_candidate_graph']}, "
        f"excluded={counts['excluded_private_material']}, "
        f"review_required={counts['review_required']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
