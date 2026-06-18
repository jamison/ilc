#!/usr/bin/env python3
"""Run the Fix52 authority graph SIM battery."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import tempfile
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse
from scipy.sparse import csgraph
from scipy.sparse.linalg import eigsh


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix48.json"
INPUT = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix51.json"
OUTPUT = ROOT / "out" / "genesis_authority_sim_battery_fix52_v0.1.json"
SIM_DOC = ROOT / "docs" / "sims" / "sim_authority_01" / "genesis_authority_sim_battery_fix52_v0.1.md"
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"


import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_authority_graph_invariants import validate_authority  # noqa: E402


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _node_id(node: dict[str, Any]) -> str:
    return str(node.get("candidate_id") or node.get("node_id") or node.get("id"))


def _node_ids(candidate: dict[str, Any]) -> set[str]:
    return {_node_id(node) for node in candidate.get("nodes", []) if isinstance(node, dict)}


def _gap_ids(candidate: dict[str, Any]) -> set[str]:
    return {
        _node_id(node)
        for node in candidate.get("nodes", [])
        if isinstance(node, dict) and node.get("node_kind") == "epistemic_gap"
    }


def _governs_edges(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        edge
        for edge in candidate.get("edges", [])
        if isinstance(edge, dict) and edge.get("edge_type") == "GOVERNS"
    ]


def _edge_id(source: str, edge_type: str, target: str) -> str:
    return "edge:" + hashlib.sha256(f"{source}|{edge_type}|{target}".encode("utf-8")).hexdigest()[:16]


def _governs_graph(candidate: dict[str, Any]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    for edge in _governs_edges(candidate):
        graph[str(edge["source"])].add(str(edge["target"]))
    return graph


def _reachable(graph: dict[str, set[str]], start: str) -> dict[str, int]:
    depths = {start: 0}
    queue: deque[str] = deque([start])
    while queue:
        node = queue.popleft()
        for target in graph.get(node, ()):
            if target not in depths:
                depths[target] = depths[node] + 1
                queue.append(target)
    return depths


def _authority_exclusion(candidate: dict[str, Any]) -> dict[str, Any]:
    gaps = _gap_ids(candidate)
    graph = _governs_graph(candidate)
    reachable = _reachable(graph, NODE0)
    gap_nodes_in_trace = sorted(gaps.intersection(reachable))
    gap_edge_types = {"EXPECTS_RESOLUTION", "RESOLVED_BY", "EXPIRED_UNRESOLVED"}
    gap_edges_in_authority = [
        edge
        for edge in candidate.get("edges", [])
        if edge.get("edge_type") in gap_edge_types
        and edge.get("source") in reachable
        and edge.get("target") in reachable
    ]
    return {
        "open_gap_node_count": len(gaps),
        "gap_nodes_in_authority_trace_count": len(gap_nodes_in_trace),
        "gap_nodes_in_authority_trace": gap_nodes_in_trace,
        "gap_edges_in_authority_trace_count": len(gap_edges_in_authority),
        "status": "pass"
        if not gap_nodes_in_trace and not gap_edges_in_authority
        else "fail",
    }


def _cycle_count(graph: dict[str, set[str]]) -> int:
    count = 0
    for start in graph:
        queue: deque[str] = deque(graph[start])
        seen: set[str] = set()
        while queue:
            node = queue.popleft()
            if node == start:
                count += 1
                break
            if node in seen:
                continue
            seen.add(node)
            queue.extend(graph.get(node, ()))
    return count


def _fake_bridge(candidate: dict[str, Any]) -> dict[str, Any]:
    graph = _governs_graph(candidate)
    depths = _reachable(graph, NODE0)
    fix50_governs = [
        edge
        for edge in _governs_edges(candidate)
        if edge.get("annotation_phase") == "phase_1545p_fix50"
    ]
    path_length_violations = []
    for edge in fix50_governs:
        target = str(edge["target"])
        depth = depths.get(target)
        if target.startswith(("policy:", "invariant:")) and (depth is None or depth > 4):
            path_length_violations.append({"target": target, "depth": depth})
        if target.startswith(("cdl:", "adr:")) and (depth is None or depth > 2):
            path_length_violations.append({"target": target, "depth": depth})

    reverse_paths = [
        node
        for node, targets in graph.items()
        if node.startswith(("policy:", "invariant:")) and NODE0 in _reachable(graph, node)
    ]
    cycle_count = _cycle_count(graph)
    return {
        "fix50_governs_edge_count": len(fix50_governs),
        "cycle_count": cycle_count,
        "reverse_path_count": len(reverse_paths),
        "reverse_path_sources": sorted(reverse_paths)[:20],
        "path_length_violation_count": len(path_length_violations),
        "path_length_violations": path_length_violations[:20],
        "status": "pass"
        if cycle_count == 0 and not reverse_paths and not path_length_violations
        else "fail",
    }


def _pagerank(candidate: dict[str, Any], iterations: int = 35, damping: float = 0.85) -> dict[str, float]:
    ids = sorted(_node_ids(candidate))
    out: dict[str, list[str]] = {node_id: [] for node_id in ids}
    for edge in candidate.get("edges", []):
        source = str(edge.get("source"))
        target = str(edge.get("target"))
        if source in out and target in out:
            out[source].append(target)

    n = len(ids)
    if n == 0:
        return {}
    rank = {node_id: 1.0 / n for node_id in ids}
    base = (1.0 - damping) / n
    for _ in range(iterations):
        nxt = {node_id: base for node_id in ids}
        dangling_mass = sum(rank[node_id] for node_id, targets in out.items() if not targets)
        dangling_share = damping * dangling_mass / n
        for node_id in ids:
            nxt[node_id] += dangling_share
        for source, targets in out.items():
            if not targets:
                continue
            share = damping * rank[source] / len(targets)
            for target in targets:
                nxt[target] += share
        rank = nxt
    return rank


def _quantiles(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "p25": None, "median": None, "p75": None, "max": None}
    arr = sorted(values)
    return {
        "min": float(arr[0]),
        "p25": float(arr[int((len(arr) - 1) * 0.25)]),
        "median": float(arr[int((len(arr) - 1) * 0.50)]),
        "p75": float(arr[int((len(arr) - 1) * 0.75)]),
        "max": float(arr[-1]),
    }


def _lambda2(candidate: dict[str, Any]) -> dict[str, Any]:
    ids = sorted(_node_ids(candidate))
    index = {node_id: i for i, node_id in enumerate(ids)}
    rows: list[int] = []
    cols: list[int] = []
    for edge in candidate.get("edges", []):
        source = str(edge.get("source"))
        target = str(edge.get("target"))
        if source in index and target in index and source != target:
            rows.extend([index[source], index[target]])
            cols.extend([index[target], index[source]])
    data = np.ones(len(rows), dtype=np.float64)
    matrix = sparse.coo_matrix((data, (rows, cols)), shape=(len(ids), len(ids))).tocsr()
    matrix.data[:] = 1.0
    laplacian = csgraph.laplacian(matrix, normed=True)
    try:
        values = eigsh(laplacian, k=2, which="SM", return_eigenvectors=False, tol=1e-4, maxiter=5000)
        values = sorted(float(v) for v in values)
        return {"lambda2": max(values[1], 0.0), "status": "computed_sparse_normalized_laplacian"}
    except Exception as exc:
        return {"lambda2": None, "status": f"not_computed:{type(exc).__name__}:{exc}"}


def _coverage(candidate: dict[str, Any]) -> dict[str, Any]:
    nodes = sorted(_node_ids(candidate))
    policy_nodes = [node for node in nodes if node.startswith("policy:")]
    invariant_nodes = [node for node in nodes if node.startswith("invariant:")]
    reachable = _reachable(_governs_graph(candidate), NODE0)
    policy_reachable = [node for node in policy_nodes if node in reachable]
    invariant_reachable = [node for node in invariant_nodes if node in reachable]
    return {
        "policy_total": len(policy_nodes),
        "policy_reachable": len(policy_reachable),
        "policy_coverage": float(len(policy_reachable) / len(policy_nodes)) if policy_nodes else 0.0,
        "invariant_total": len(invariant_nodes),
        "invariant_reachable": len(invariant_reachable),
        "invariant_coverage": float(len(invariant_reachable) / len(invariant_nodes))
        if invariant_nodes
        else 0.0,
    }


def _spectral(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    baseline_pr = _pagerank(baseline)
    candidate_pr = _pagerank(candidate)
    top20 = sorted(candidate_pr.items(), key=lambda item: item[1], reverse=True)[:20]
    top20_payload = [{"node_id": node, "pagerank": float(score)} for node, score in top20]
    node0_rank = next((i + 1 for i, (node, _) in enumerate(sorted(candidate_pr.items(), key=lambda item: item[1], reverse=True)) if node == NODE0), None)
    authority_scores = [
        score
        for node, score in candidate_pr.items()
        if node.startswith(("cdl:", "adr:", "policy:", "invariant:"))
    ]
    baseline_l2 = _lambda2(baseline)
    candidate_l2 = _lambda2(candidate)
    depths = _reachable(_governs_graph(candidate), NODE0)
    depth_histogram = Counter(
        depth
        for node, depth in depths.items()
        if node.startswith(("policy:", "invariant:"))
    )
    max_non_node0 = max((score for node, score in candidate_pr.items() if node != NODE0), default=0.0)
    advisory_warnings = []
    if baseline_l2["lambda2"] is not None and candidate_l2["lambda2"] is not None:
        if candidate_l2["lambda2"] < baseline_l2["lambda2"]:
            advisory_warnings.append("lambda2_decreased")
    if node0_rank is None or node0_rank > 10:
        advisory_warnings.append("node0_not_top10_pagerank")
    if max_non_node0 > 0.05:
        advisory_warnings.append("non_node0_hub_dominance_gt_5pct")
    if depth_histogram and max(depth_histogram) > 4:
        advisory_warnings.append("authority_trace_depth_gt_4")
    return {
        "baseline_lambda2": baseline_l2,
        "candidate_lambda2": candidate_l2,
        "lambda2_delta": (
            float(candidate_l2["lambda2"] - baseline_l2["lambda2"])
            if baseline_l2["lambda2"] is not None and candidate_l2["lambda2"] is not None
            else None
        ),
        "top20_pagerank": top20_payload,
        "top5_pagerank": top20_payload[:5],
        "node0_pagerank_rank": node0_rank,
        "node0_pagerank": float(candidate_pr.get(NODE0, 0.0)),
        "authority_pagerank_quintiles": _quantiles(authority_scores),
        "authority_trace_depth_histogram": {str(k): v for k, v in sorted(depth_histogram.items())},
        "advisory_warnings": advisory_warnings,
        "status": "spectral_advisory_pass" if not advisory_warnings else "spectral_advisory_warn",
    }


def _gap_closure(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    base_cov = _coverage(baseline)
    fix51_cov = _coverage(candidate)
    simulated = copy.deepcopy(candidate)
    gaps = [node for node in simulated["nodes"] if node.get("node_kind") == "epistemic_gap"]
    simulated_edges_added = 0
    for gap in gaps:
        if not gap.get("candidate_targets"):
            continue
        target = gap["candidate_targets"][0]["candidate_id"]
        source = gap["source_node_id"]
        edge_type = gap["expected_edge_type"]
        simulated["edges"].append(
            {
                "edge_id": _edge_id(source, edge_type, target),
                "edge_type": edge_type,
                "source": source,
                "target": target,
                "annotation_phase": "phase_1545p_fix52_simulated_gap_resolution",
            }
        )
        simulated_edges_added += 1
    sim_cov = _coverage(simulated)
    return {
        "baseline_fix48": base_cov,
        "post_repair_fix51": fix51_cov,
        "simulated_full_resolution": sim_cov,
        "simulated_edges_added": simulated_edges_added,
        "advisory_warnings": [
            warning
            for warning, condition in (
                ("policy_coverage_not_improved", fix51_cov["policy_coverage"] <= base_cov["policy_coverage"]),
                ("invariant_coverage_not_improved", fix51_cov["invariant_coverage"] <= base_cov["invariant_coverage"]),
                ("simulated_policy_coverage_below_95pct", sim_cov["policy_coverage"] < 0.95),
                ("simulated_invariant_coverage_below_80pct", sim_cov["invariant_coverage"] < 0.80),
            )
            if condition
        ],
    }


def _negative_controls(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    gap = next(node for node in candidate["nodes"] if node.get("node_kind") == "epistemic_gap")
    gap_id = gap["candidate_id"]
    policy = next(node for node in _node_ids(candidate) if node.startswith("policy:"))
    cdl = next(node for node in _node_ids(candidate) if node.startswith("cdl:"))
    reachable = _reachable(_governs_graph(candidate), NODE0)
    cycle_source = next(
        (
            node
            for node, depth in sorted(reachable.items(), key=lambda item: (item[1], item[0]))
            if depth > 0 and node.startswith(("policy:", "invariant:", "cdl:", "adr:"))
        ),
        policy,
    )

    def mutated_with_edge(source: str, edge_type: str, target: str) -> dict[str, Any]:
        copy_candidate = copy.deepcopy(candidate)
        copy_candidate["edges"].append(
            {
                "edge_id": _edge_id(source, edge_type, target),
                "edge_type": edge_type,
                "source": source,
                "target": target,
                "annotation_phase": "negative_control",
                "fix52_negative_control": True,
            }
        )
        return copy_candidate

    controls: list[tuple[str, dict[str, Any], str]] = [
        ("E1_gap_governs_source", mutated_with_edge(gap_id, "GOVERNS", policy), "gap node cannot be GOVERNS source"),
        ("E2_gap_governs_target", mutated_with_edge(NODE0, "GOVERNS", gap_id), "gap node cannot be GOVERNS target"),
        ("E3_test_node_governs_policy", mutated_with_edge("test:negative_control", "GOVERNS", policy), "forbidden GOVERNS source prefix"),
        ("E4_policy_governs_cdl", mutated_with_edge(policy, "GOVERNS", cdl), "GOVERNS must flow authority downward"),
        ("E5_governs_cycle", mutated_with_edge(cycle_source, "GOVERNS", NODE0), "GOVERNS cycle detected"),
    ]

    bad_gap_authority = copy.deepcopy(candidate)
    for node in bad_gap_authority["nodes"]:
        if node.get("candidate_id") == gap_id:
            node["authority_effect"] = "full"
            break
    controls.append(("E6_gap_authority_effect_full", bad_gap_authority, "authority_effect must be"))

    bad_gap_projection = copy.deepcopy(candidate)
    for node in bad_gap_projection["nodes"]:
        if node.get("candidate_id") == gap_id:
            node["projection_policy"]["authority_projection"] = "included"
            break
    controls.append(("E7_gap_in_authority_projection", bad_gap_projection, "invalid projection_policy"))

    results = []
    for name, mutated, expected_fragment in controls:
        errors = validate_authority(mutated)
        matched = any(expected_fragment in error for error in errors)
        results.append(
            {
                "control_id": name,
                "expected_error_fragment": expected_fragment,
                "actual_error_count": len(errors),
                "matched_expected_error": matched,
                "status": "pass" if matched else "fail",
                "sample_errors": errors[:5],
            }
        )
    return results


def _write_sim_doc(result: dict[str, Any]) -> None:
    spectral = result["spectral_result"]
    gap = result["gap_closure_rate_result"]
    neg_rows = "\n".join(
        f"| {entry['control_id']} | {entry['status']} | {entry['expected_error_fragment']} |"
        for entry in result["negative_control_results"]
    )
    top_rows = "\n".join(
        f"| {entry['node_id']} | `{entry['pagerank']:.12g}` |"
        for entry in spectral["top5_pagerank"]
    )
    text = f"""# Genesis Authority SIM Battery Fix52 v0.1

## Executive Summary

Overall verdict: `{result['overall_verdict']}`.

Fix52 is evidence-gathering only. It verifies that the Fix50/Fix51 candidate
keeps epistemic gaps outside authority traces, avoids fake GOVERNS bridges,
measures spectral/PageRank health, simulates gap-closure upper bounds, and
checks negative controls.

## Suite A - Authority Exclusion

- Gap nodes in authority trace: `{result['authority_exclusion_result']['gap_nodes_in_authority_trace_count']}`
- Gap lifecycle edges in authority trace: `{result['authority_exclusion_result']['gap_edges_in_authority_trace_count']}`
- Status: `{result['authority_exclusion_result']['status']}`

## Suite B - No Fake Bridges

- Fix50 GOVERNS edges checked: `{result['fake_bridge_result']['fix50_governs_edge_count']}`
- Cycle count: `{result['fake_bridge_result']['cycle_count']}`
- Reverse path count: `{result['fake_bridge_result']['reverse_path_count']}`
- Path-length violation count: `{result['fake_bridge_result']['path_length_violation_count']}`
- Status: `{result['fake_bridge_result']['status']}`

## Suite C - Spectral Metrics

| Metric | Fix48 baseline | Fix51 candidate |
|---|---:|---:|
| λ₂ | `{spectral['baseline_lambda2']['lambda2']}` | `{spectral['candidate_lambda2']['lambda2']}` |

- λ₂ delta: `{spectral['lambda2_delta']}`
- NODE0 PageRank rank: `{spectral['node0_pagerank_rank']}`
- NODE0 PageRank: `{spectral['node0_pagerank']:.12g}`
- Spectral status: `{spectral['status']}`
- Advisory warnings: `{spectral['advisory_warnings']}`

### Top-5 PageRank

| Node | PageRank |
|---|---:|
{top_rows}

### Authority Trace Depth Histogram

```json
{json.dumps(spectral['authority_trace_depth_histogram'], sort_keys=True)}
```

## Suite D - Gap Closure Rate

| Coverage | Fix48 baseline | Fix51 post-repair | Simulated full-resolution |
|---|---:|---:|---:|
| Policy | `{gap['baseline_fix48']['policy_coverage']:.6f}` | `{gap['post_repair_fix51']['policy_coverage']:.6f}` | `{gap['simulated_full_resolution']['policy_coverage']:.6f}` |
| Invariant | `{gap['baseline_fix48']['invariant_coverage']:.6f}` | `{gap['post_repair_fix51']['invariant_coverage']:.6f}` | `{gap['simulated_full_resolution']['invariant_coverage']:.6f}` |

Simulated edges added: `{gap['simulated_edges_added']}`.
Advisory warnings: `{gap['advisory_warnings']}`.

## Suite E - Negative Controls

| Control | Status | Expected error fragment |
|---|---|---|
{neg_rows}

## Non-Claims

- Fix52 is evidence-gathering only.
- SIM evidence does not grant authority, activation, eligibility, or signing readiness.
- Spectral metrics are research diagnostics, not authority traces.
- No graph mutation, Genesis signing, public graph publication, public RC activation, runtime activation, economic activation, network activation, ADR mutation, or CDL mutation occurred.
"""
    _write_text(SIM_DOC, text)


def main() -> int:
    baseline = _load(BASELINE)
    candidate = _load(INPUT)
    authority_exclusion = _authority_exclusion(candidate)
    fake_bridge = _fake_bridge(candidate)
    spectral = _spectral(baseline, candidate)
    gap_closure = _gap_closure(baseline, candidate)
    negative_controls = _negative_controls(candidate)

    hard_fail = (
        authority_exclusion["status"] != "pass"
        or fake_bridge["status"] != "pass"
        or any(entry["status"] != "pass" for entry in negative_controls)
        or validate_authority(candidate)
    )
    advisory_warn = (
        spectral["status"] != "spectral_advisory_pass"
        or bool(gap_closure["advisory_warnings"])
    )
    verdict = "fail" if hard_fail else "warn" if advisory_warn else "pass"
    result = {
        "sim_battery_id": "genesis_authority_sim_battery_fix52_v0.1",
        "input_candidate_path": str(INPUT.relative_to(ROOT)),
        "input_candidate_sha256": _sha256(INPUT),
        "baseline_candidate_path": str(BASELINE.relative_to(ROOT)),
        "baseline_candidate_sha256": _sha256(BASELINE),
        "authority_exclusion_result": authority_exclusion,
        "fake_bridge_result": fake_bridge,
        "spectral_result": spectral,
        "gap_closure_rate_result": gap_closure,
        "negative_control_results": negative_controls,
        "overall_verdict": verdict,
        "non_claims": [
            "Fix52 is evidence-gathering only.",
            "SIM evidence does not grant authority, activation, eligibility, or signing readiness.",
            "Spectral metrics are research diagnostics, not authority traces.",
            "No graph mutation occurred.",
            "No Genesis signing occurred.",
            "No public graph publication or public RC activation occurred.",
            "No runtime, economic, network, ADR, or CDL activation occurred.",
        ],
    }
    _dump(OUTPUT, result)
    _write_sim_doc(result)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
