#!/usr/bin/env python3
"""Run the Fix56 projection-aware Fiedler rebaseline.

PUBLIC_RC_EXCLUDE: fix56_projection_aware_fiedler_rebaseline_evaluator
PUBLIC_RC_EXCLUDE_REASON: Local research-only spectral diagnostic over an unsigned Atlas LMDB; not public graph activation, Genesis signing, canonical graph mutation, or public RC publication.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import tempfile
from collections import Counter
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


PHASE = "1545p-Fix56"
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"
EXPECTED_NODE_COUNT = 15677
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
FIX55_FIEDLER_REPORT = REPO_ROOT / "out/genesis_atlas_fix55_fiedler_projection_analysis_v0.1.json"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix56_fiedler_rebaseline_report_v0.1.json"
MINORITY_PATHS = {
    "all_local": REPO_ROOT / "out/genesis_atlas_fix56_fiedler_all_local_minority_cluster_v0.1.json",
    "public_eligible": REPO_ROOT / "out/genesis_atlas_fix56_fiedler_public_eligible_minority_cluster_v0.1.json",
    "authority_only": REPO_ROOT / "out/genesis_atlas_fix56_fiedler_authority_only_minority_cluster_v0.1.json",
}
FIX57_LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix57_public_eligible_minority_audit_ledger_v0.1.md"

PUBLIC_ELIGIBLE_PROJECTIONS = frozenset(
    {"genesis_core_star_map", "public_protocol_graph", "support_candidate_graph"}
)
SPECTRAL_CAVEAT = (
    "Fiedler vector gives spectral relaxation of the minimum sparse-cut problem "
    "— not a proof of the exact minimum cut."
)


def _canonical_text(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _atomic_write_json(path: Path, payload: Any) -> None:
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


def _atomic_write_text(path: Path, text: str) -> None:
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


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix56_node_missing_candidate_id")
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


def _node_description(node: dict[str, Any]) -> str:
    for key in ("source_path", "path", "label", "title", "description"):
        value = node.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _projection_nodes(nodes: list[dict[str, Any]], projection: str) -> list[dict[str, Any]]:
    if projection == "all_local":
        return nodes
    if projection == "public_eligible":
        return [node for node in nodes if node.get("graph_projection") in PUBLIC_ELIGIBLE_PROJECTIONS]
    if projection == "authority_only":
        return [node for node in nodes if node.get("graph_projection") == "genesis_core_star_map"]
    raise ValueError(f"fix56_unknown_projection:{projection}")


def _project_edges(node_ids: set[str], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        edge
        for edge in edges
        if _edge_source(edge) in node_ids and _edge_target(edge) in node_ids
    ]


def _directed_degree_counts(node_ids: set[str], edges: list[dict[str, Any]]) -> tuple[Counter[str], Counter[str]]:
    inbound: Counter[str] = Counter()
    outbound: Counter[str] = Counter()
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        if source in node_ids and target in node_ids:
            outbound[source] += 1
            inbound[target] += 1
    return inbound, outbound


def _normalized_laplacian(
    node_ids: list[str],
    edges: list[dict[str, Any]],
) -> tuple[sp.csr_matrix, dict[str, int], Counter[int], sp.csr_matrix]:
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
    adjacency_values: list[int] = []
    adjacency_row: list[int] = []
    adjacency_col: list[int] = []
    for u, v in sorted(undirected):
        du = degree[u]
        dv = degree[v]
        if du <= 0 or dv <= 0:
            continue
        weight = -1.0 / math.sqrt(float(du * dv))
        row.extend([u, v])
        col.extend([v, u])
        values.extend([weight, weight])
        adjacency_row.extend([u, v])
        adjacency_col.extend([v, u])
        adjacency_values.extend([1, 1])
    for index in range(len(node_ids)):
        row.append(index)
        col.append(index)
        values.append(1.0 if degree[index] > 0 else 0.0)
    laplacian = sp.csr_matrix((values, (row, col)), shape=(len(node_ids), len(node_ids)), dtype=float)
    adjacency = sp.csr_matrix(
        (adjacency_values, (adjacency_row, adjacency_col)),
        shape=(len(node_ids), len(node_ids)),
        dtype=int,
    )
    return laplacian, node_index, degree, adjacency


def _authority_coverage(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, int]:
    node_ids = {_candidate_id(node) for node in nodes}
    invariant_ids = {node_id for node_id in node_ids if node_id.startswith("invariant:")}
    policy_ids = {node_id for node_id in node_ids if node_id.startswith("policy:")}
    governs_targets = {
        _edge_target(edge)
        for edge in edges
        if _edge_type(edge) == "GOVERNS" and _edge_target(edge) in node_ids
    }
    return {
        "invariant_nodes_total": len(invariant_ids),
        "invariant_nodes_with_governs_inbound": len(invariant_ids & governs_targets),
        "policy_nodes_total": len(policy_ids),
        "policy_nodes_with_governs_inbound": len(policy_ids & governs_targets),
    }


def _minority_records(
    *,
    minority: list[tuple[str, float]],
    node_by_id: dict[str, dict[str, Any]],
    inbound: Counter[str],
    outbound: Counter[str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for node_id, coordinate in sorted(minority, key=lambda row: (row[1], row[0])):
        node = node_by_id[node_id]
        records.append(
            {
                "candidate_id": node_id,
                "fiedler_component": float(coordinate),
                "graph_projection": str(node.get("graph_projection", "")),
                "inbound_edge_count": int(inbound[node_id]),
                "outbound_edge_count": int(outbound[node_id]),
                "path_or_description": _node_description(node),
            }
        )
    return records


def _fiedler_projection(
    *,
    projection: str,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    node_by_id = {_candidate_id(node): node for node in nodes}
    node_ids = sorted(node_by_id)
    node_set = set(node_ids)
    projected_edges = _project_edges(node_set, edges)
    inbound, outbound = _directed_degree_counts(node_set, projected_edges)
    coverage = _authority_coverage(nodes, projected_edges)
    base_result: dict[str, Any] = {
        "authority_coverage": coverage,
        "edge_count": len(projected_edges),
        "lambda2": 0.0,
        "minority_cluster_size": 0,
        "node_count": len(nodes),
        "projection": projection,
        "spectral_caveat": SPECTRAL_CAVEAT,
    }
    if len(node_ids) < 3:
        base_result["status"] = "SKIP_TOO_FEW_NODES"
        cluster = _cluster_payload(projection, base_result, [])
        return base_result, cluster

    laplacian, node_index, degree, adjacency = _normalized_laplacian(node_ids, projected_edges)
    component_count, labels = connected_components(adjacency, directed=False, return_labels=True)
    base_result["connected_component_count"] = int(component_count)
    base_result["isolated_node_count"] = int(sum(1 for index in range(len(node_ids)) if degree[index] == 0))

    if component_count > 1:
        label_counts = Counter(int(label) for label in labels)
        base_result["component_size_counts"] = {str(key): int(value) for key, value in sorted(label_counts.items())}
        if NODE0 in node_index:
            reference_label = int(labels[node_index[NODE0]])
            minority = [
                (node_id, 0.0)
                for node_id, index in node_index.items()
                if int(labels[index]) != reference_label
            ]
            base_result["minority_reference_node"] = NODE0
            base_result["node0_component_size"] = int(label_counts[reference_label])
        else:
            anchor = max(node_ids, key=lambda node_id: (int(inbound[node_id] + outbound[node_id]), node_id))
            reference_label = int(labels[node_index[anchor]])
            minority = [
                (node_id, 0.0)
                for node_id, index in node_index.items()
                if int(labels[index]) != reference_label
            ]
            base_result["minority_reference_node"] = anchor
            base_result["reference_selection"] = "highest_degree_node"
        base_result["lambda2"] = 0.0
        base_result["minority_cluster_size"] = len(minority)
        base_result["smallest_eigenvalues"] = []
        base_result["status"] = "PASS_DISCONNECTED_PROJECTION"
        base_result["spectral_note"] = "Projection is disconnected; algebraic connectivity is 0."
        records = _minority_records(
            minority=minority,
            node_by_id=node_by_id,
            inbound=inbound,
            outbound=outbound,
        )
        return base_result, _cluster_payload(projection, base_result, records)

    k = min(3, len(node_ids) - 1)
    values, vectors = eigsh(laplacian, k=k, which="SM", return_eigenvectors=True, tol=1e-6, maxiter=10000)
    order = np.argsort(values)
    sorted_values = [float(values[index]) for index in order]
    base_result["smallest_eigenvalues"] = sorted_values
    if len(order) < 2:
        base_result["status"] = "SKIP_NO_FIEDLER_VECTOR"
        return base_result, _cluster_payload(projection, base_result, [])

    fiedler_value = max(0.0, float(values[order[1]]))
    fiedler_vector = vectors[:, order[1]]
    if NODE0 in node_index:
        if fiedler_vector[node_index[NODE0]] < 0:
            fiedler_vector = -fiedler_vector
        minority = [
            (node_id, float(fiedler_vector[index]))
            for node_id, index in node_index.items()
            if float(fiedler_vector[index]) < 0
        ]
        base_result["minority_reference_node"] = NODE0
    else:
        anchor = max(node_ids, key=lambda node_id: (int(inbound[node_id] + outbound[node_id]), node_id))
        if fiedler_vector[node_index[anchor]] < 0:
            fiedler_vector = -fiedler_vector
        minority = [
            (node_id, float(fiedler_vector[index]))
            for node_id, index in node_index.items()
            if float(fiedler_vector[index]) < 0
        ]
        base_result["minority_reference_node"] = anchor
        base_result["reference_selection"] = "highest_degree_node"

    records = _minority_records(
        minority=minority,
        node_by_id=node_by_id,
        inbound=inbound,
        outbound=outbound,
    )
    base_result["lambda2"] = fiedler_value
    base_result["minority_cluster_size"] = len(records)
    base_result["minority_cluster_sample"] = records[:25]
    base_result["status"] = "PASS"
    return base_result, _cluster_payload(projection, base_result, records)


def _cluster_payload(projection: str, result: dict[str, Any], nodes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "lambda2": float(result["lambda2"]),
        "minority_cluster_size": int(result["minority_cluster_size"]),
        "nodes": nodes,
        "phase": PHASE,
        "projection": projection,
        "spectral_caveat": SPECTRAL_CAVEAT,
        "status": result.get("status", "PASS"),
    }


def _write_fix57_ledger(cluster: dict[str, Any]) -> None:
    rows = cluster["nodes"]
    header = [
        "# Fix57 Public-Eligible Minority Audit Ledger v0.1",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: local Atlas spectral minority-cluster audit ledger; not public RC material -->",
        "",
        f"- Source phase: {PHASE}",
        f"- Projection: {cluster['projection']}",
        f"- Public-eligible minority cluster size: {cluster['minority_cluster_size']}",
        f"- Fix56 lambda2: {cluster['lambda2']}",
        "- Instruction: Fix57 fills in recommended_edge_type, recommended_target, disposition, and notes in batches of 10.",
        "",
        "| # | node_id | path/description | current_edges | graph_projection | recommended_edge_type | recommended_target | disposition | notes |",
        "|---|---------|------------------|---------------|------------------|-----------------------|--------------------|-------------|-------|",
    ]
    table_rows = []
    for index, row in enumerate(rows, start=1):
        current_edges = int(row["inbound_edge_count"]) + int(row["outbound_edge_count"])
        table_rows.append(
            "| {index} | `{node_id}` | {description} | {current_edges} | `{projection}` |  |  |  |  |".format(
                index=index,
                node_id=_escape_md(str(row["candidate_id"])),
                description=_escape_md(str(row.get("path_or_description", ""))),
                current_edges=current_edges,
                projection=_escape_md(str(row.get("graph_projection", ""))),
            )
        )
    _atomic_write_text(FIX57_LEDGER_PATH, "\n".join(header + table_rows) + "\n")


def _escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _load_fix55_baseline() -> dict[str, Any]:
    return json.loads(FIX55_FIEDLER_REPORT.read_text(encoding="utf-8"))


def _fix55_lambda2(baseline: dict[str, Any], projection: str) -> float:
    projection_payload = baseline["projections"][projection]
    value = projection_payload.get("lambda2", projection_payload.get("fiedler_value_lambda2"))
    return float(value)


def _run() -> dict[str, Any]:
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError("fix56_lmdb_missing")
    fix55_baseline = _load_fix55_baseline()
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        nodes = store.iter_nodes()
        edges = store.iter_edges()
    finally:
        store.close()

    if len(nodes) != EXPECTED_NODE_COUNT:
        raise ValueError(f"fix56_unexpected_node_count:{len(nodes)}")
    missing_projection = [_candidate_id(node) for node in nodes if not node.get("graph_projection")]
    if missing_projection:
        raise ValueError(f"fix56_nodes_missing_graph_projection:{len(missing_projection)}")
    if NODE0 not in {_candidate_id(node) for node in nodes}:
        raise ValueError("fix56_node0_missing")

    projections: dict[str, dict[str, Any]] = {}
    cluster_payloads: dict[str, dict[str, Any]] = {}
    for projection in ("all_local", "public_eligible", "authority_only"):
        projection_nodes = _projection_nodes(nodes, projection)
        metrics, cluster = _fiedler_projection(
            projection=projection,
            nodes=projection_nodes,
            edges=edges,
        )
        projections[projection] = metrics
        cluster_payloads[projection] = cluster

    for projection, path in MINORITY_PATHS.items():
        _atomic_write_json(path, cluster_payloads[projection])
    _write_fix57_ledger(cluster_payloads["public_eligible"])

    all_local_fix55 = _fix55_lambda2(fix55_baseline, "all_local")
    public_eligible_fix55 = _fix55_lambda2(fix55_baseline, "public_eligible")
    authority_only_fix55 = _fix55_lambda2(fix55_baseline, "authority_only")
    report = {
        "fix55_baseline_comparison": {
            "all_local_delta": float(projections["all_local"]["lambda2"] - all_local_fix55),
            "all_local_lambda2_fix55": all_local_fix55,
            "all_local_lambda2_fix56": float(projections["all_local"]["lambda2"]),
            "authority_only_delta": float(projections["authority_only"]["lambda2"] - authority_only_fix55),
            "authority_only_lambda2_fix55": authority_only_fix55,
            "authority_only_lambda2_fix56": float(projections["authority_only"]["lambda2"]),
            "public_eligible_delta": float(projections["public_eligible"]["lambda2"] - public_eligible_fix55),
            "public_eligible_lambda2_fix55": public_eligible_fix55,
            "public_eligible_lambda2_fix56": float(projections["public_eligible"]["lambda2"]),
        },
        "fix57_input_ledger": str(FIX57_LEDGER_PATH.relative_to(REPO_ROOT)),
        "input_digest": _input_digest(nodes=nodes, edges=edges),
        "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
        "phase": PHASE,
        "projections": projections,
        "spectral_caveat": SPECTRAL_CAVEAT,
        "status": "PASS",
    }
    _atomic_write_json(REPORT_PATH, report)
    print(
        "Done. status=PASS, "
        f"all_local_lambda2={projections['all_local']['lambda2']}, "
        f"public_eligible_lambda2={projections['public_eligible']['lambda2']}, "
        f"authority_only_lambda2={projections['authority_only']['lambda2']}, "
        f"public_eligible_minority={projections['public_eligible']['minority_cluster_size']}"
    )
    return report


def _input_digest(*, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> str:
    node_ids = [_candidate_id(node) for node in nodes]
    edge_refs = [f"{_edge_source(edge)}|{_edge_type(edge)}|{_edge_target(edge)}" for edge in edges]
    payload = {"edge_refs": sorted(edge_refs), "node_ids": sorted(node_ids)}
    return hashlib.sha256(_canonical_text(payload).encode("utf-8")).hexdigest()


def main() -> int:
    _run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
