#!/usr/bin/env python3
"""Build Phase 1545p-Fix40 post-Fix38 integrity and coverage outputs.

PUBLIC_RC_EXCLUDE: fix40_post_fix38_integrity_runner
PUBLIC_RC_EXCLUDE_REASON: Internal research-only Atlas candidate merge and
coverage diagnostic runner. It does not mutate canonical graph state, sign
nodes, upload nodes, execute tests, activate runtime, or authorize public RC.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PHASE = "1545p-Fix40"
DEFAULT_BASE_GRAPH = Path(
    "out/atlas_research/genesis_atlas_test_frontier_unified_candidate_1545p_fix38.json"
)
DEFAULT_LEDGER = Path("docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json")
DEFAULT_CANDIDATE_OUT = Path("out/atlas_research/genesis_atlas_enriched_candidate_fix40.json")
DEFAULT_COVERAGE_JSON = Path("out/test_graph_coverage_1545p_fix40.json")
DEFAULT_COVERAGE_REPORT = Path("docs/specs/ilc_test_graph_coverage_report_1545p_fix40_v0.1.md")
DEFAULT_GAP_ANALYSIS = Path("out/genesis_core_star_map_gap_analysis_v0.2.json")
DEFAULT_COMPILE_DIAGNOSTIC = Path("out/genesis_compile_coverage_diagnostic_v0.2.json")
DEFAULT_DELTA_REPORT = Path("docs/sims/sim_spectral_02/genesis_coverage_delta_fix38_v0.1.md")
FIX33_COVERAGE_BASELINE = Path("out/test_graph_coverage_1545p_fix33.json")

OUTPUT_TOKENS = [
    "fix40_integrity_checks_passed",
    "fix40_coverage_rerun_complete",
    "fix40_enriched_candidate_produced",
    "fix40_complete",
    "public_path_remains_blocked_phase_1545p_fix40",
]

TERMINAL_PREFIXES = (
    "adr:",
    "api_route:",
    "cdl:",
    "claim:",
    "command:",
    "executor_profile:",
    "graph_node:",
    "invariant:",
    "phase:",
    "phase_window:",
    "policy:",
    "repo_dir:",
    "sim:",
)


class Fix40Error(RuntimeError):
    """Stable phase-runner error."""


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )


def canonical_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_bytes(payload).decode("utf-8") + "\n", encoding="utf-8")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_suffix(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")[:160] or "unknown"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def node_id(node: dict[str, Any]) -> str | None:
    for key in ("candidate_id", "node_id", "id", "vertex_id"):
        value = node.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def edge_source(edge: dict[str, Any]) -> str | None:
    value = edge.get("source") or edge.get("from") or edge.get("source_id")
    return value if isinstance(value, str) and value else None


def edge_target(edge: dict[str, Any]) -> str | None:
    value = edge.get("target") or edge.get("to") or edge.get("target_id")
    return value if isinstance(value, str) and value else None


def edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type") or edge.get("relation") or "UNKNOWN"
    return str(value)


def build_path_index(nodes: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for node in nodes:
        nid = node_id(node)
        if not nid:
            continue
        for key in ("source_path", "repo_path", "path", "label"):
            value = node.get(key)
            if isinstance(value, str) and value:
                index[value].append(nid)
    return {key: sorted(set(value)) for key, value in index.items()}


def prefer_node(candidates: list[str]) -> str:
    def score(value: str) -> tuple[int, str]:
        if value.startswith("repo:file:"):
            return (0, value)
        if value.startswith("repo:file_ref:"):
            return (1, value)
        return (2, value)

    return sorted(candidates, key=score)[0]


def ensure_node(
    nodes: list[dict[str, Any]],
    node_ids: set[str],
    nid: str,
    label: str,
    category: str,
    provenance: str,
) -> None:
    if nid in node_ids:
        return
    nodes.append(
        {
            "authority_status": "candidate_review_required",
            "candidate_id": nid,
            "canonicality_tier": "fix40_candidate_terminal",
            "category": category,
            "confidence": "0.650",
            "genesis_attested": False,
            "inclusion_status": "candidate_overlay",
            "label": label,
            "promotion_status": "candidate_only_not_canonical",
            "provenance": provenance,
            "source_phase": PHASE,
        }
    )
    node_ids.add(nid)


def target_category(target: str) -> str:
    if target.startswith("adr:"):
        return "authority_terminal_adr"
    if target.startswith("cdl:"):
        return "authority_terminal_cdl"
    if target.startswith("policy:"):
        return "authority_terminal_policy"
    if target.startswith("phase:") or target.startswith("phase_window:"):
        return "phase_terminal"
    if target.startswith("invariant:"):
        return "invariant_terminal"
    if target.startswith("executor_profile:"):
        return "executor_profile_terminal"
    if target.startswith("repo_dir:"):
        return "repo_directory_terminal"
    if target.startswith("sim:"):
        return "sim_terminal"
    return "support_artifact"


def resolve_target(
    target: str,
    nodes: list[dict[str, Any]],
    node_ids: set[str],
    path_index: dict[str, list[str]],
    repo_root: Path,
) -> str:
    if target.startswith("graph_node:"):
        stripped = target.removeprefix("graph_node:")
        if stripped not in node_ids:
            ensure_node(nodes, node_ids, stripped, stripped, "graph_node_reference", "fix40_target_resolution")
        return stripped
    if target in node_ids:
        return target
    if target in path_index:
        return prefer_node(path_index[target])
    if target.startswith(TERMINAL_PREFIXES):
        ensure_node(nodes, node_ids, target, target, target_category(target), "fix40_target_resolution")
        return target
    if (repo_root / target).exists():
        nid = f"repo:file_ref:{safe_suffix(target)}"
        ensure_node(nodes, node_ids, nid, target, "support_artifact", "fix40_target_resolution")
        return nid
    nid = f"target:{safe_suffix(target)}"
    ensure_node(nodes, node_ids, nid, target, "unresolved_candidate_terminal", "fix40_target_resolution")
    return nid


def fix40_edge_id(
    source: str,
    etype: str,
    target: str,
    repo_path: str,
    list_name: str,
    index: int,
) -> str:
    payload = {
        "annotation_phase": "fix38",
        "index": index,
        "list_name": list_name,
        "repo_path": repo_path,
        "source": source,
        "target": target,
        "type": etype,
    }
    return "edge:fix40:" + hashlib.sha256(canonical_bytes(payload)).hexdigest()[:32]


def merge_fix38_edges(
    base_graph: dict[str, Any],
    ledger: dict[str, Any],
    repo_root: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    nodes = [dict(node) for node in base_graph.get("nodes", []) if isinstance(node, dict)]
    edges = [dict(edge) for edge in base_graph.get("edges", []) if isinstance(edge, dict)]
    node_ids = {nid for node in nodes if (nid := node_id(node))}
    path_index = build_path_index(nodes)
    existing_edge_ids = {
        edge.get("edge_id") for edge in edges if isinstance(edge.get("edge_id"), str)
    }
    seen_fix40_signatures: set[tuple[str, str, str, str, str]] = set()

    annotations = ledger.get("annotations")
    if not isinstance(annotations, list):
        raise Fix40Error("fix38_ledger_annotations_not_list")

    added_edges = 0
    considered_edges = 0
    created_source_nodes = 0
    created_target_nodes_before = len(node_ids)
    list_counts: Counter[str] = Counter()

    for row in annotations:
        if not isinstance(row, dict):
            continue
        repo_path = row.get("repo_path")
        if not isinstance(repo_path, str) or not repo_path:
            raise Fix40Error("fix38_ledger_row_missing_repo_path")
        source_candidates = path_index.get(repo_path, [])
        if source_candidates:
            source = prefer_node(source_candidates)
        else:
            source = f"repo:file_ref:{safe_suffix(repo_path)}"
            ensure_node(nodes, node_ids, source, repo_path, "test_evidence_node", "fix40_source_resolution")
            path_index.setdefault(repo_path, []).append(source)
            created_source_nodes += 1

        for list_name in ("proposed_semantic_edges", "proposed_authority_trace_edges"):
            proposed = row.get(list_name, [])
            if not isinstance(proposed, list):
                raise Fix40Error(f"fix38_ledger_{list_name}_not_list:{repo_path}")
            for index, item in enumerate(proposed):
                if not isinstance(item, dict):
                    continue
                raw_type = item.get("edge_type")
                raw_target = item.get("target")
                if not isinstance(raw_type, str) or not raw_type:
                    raise Fix40Error(f"fix38_ledger_edge_missing_type:{repo_path}")
                if not isinstance(raw_target, str) or not raw_target:
                    raise Fix40Error(f"fix38_ledger_edge_missing_target:{repo_path}")
                target = resolve_target(raw_target, nodes, node_ids, path_index, repo_root)
                signature = (source, raw_type, target, repo_path, list_name)
                considered_edges += 1
                if signature in seen_fix40_signatures:
                    continue
                seen_fix40_signatures.add(signature)
                edge_id = fix40_edge_id(source, raw_type, target, repo_path, list_name, index)
                if edge_id in existing_edge_ids:
                    continue
                edges.append(
                    {
                        "annotation_method": "manual_reviewed",
                        "annotation_phase": "fix38",
                        "annotation_reviewer": "codex",
                        "candidate_status": "fix38_proposed",
                        "confidence": "0.780"
                        if raw_type == "REFERENCES_AUTHORITY"
                        else "0.860",
                        "edge_id": edge_id,
                        "edge_type": raw_type,
                        "origin_edge_index": index,
                        "origin_edge_list": list_name,
                        "origin_phase": "1545p-Fix38",
                        "origin_repo_path": repo_path,
                        "promotion_status": "candidate_only_not_canonical",
                        "provenance": "fix38_manual_edge_annotation_ledger",
                        "rationale": row.get("manual_read_summary", "Fix38 manual annotation."),
                        "relation": raw_type.lower(),
                        "review_status": item.get("review_status", "candidate_review_required"),
                        "source": source,
                        "source_phase": PHASE,
                        "target": target,
                        "target_original": raw_target,
                    }
                )
                existing_edge_ids.add(edge_id)
                added_edges += 1
                list_counts[list_name] += 1

    result = {
        **base_graph,
        "candidate_status": "unsigned_support_only_not_canonical_fix40_post_fix38_integrity_candidate",
        "edges": edges,
        "fix40_merge_summary": {
            "added_candidate_edges": added_edges,
            "annotations_processed": len(annotations),
            "base_edge_count": len(base_graph.get("edges", [])),
            "base_node_count": len(base_graph.get("nodes", [])),
            "considered_ledger_edges": considered_edges,
            "created_source_nodes": created_source_nodes,
            "created_target_nodes": len(node_ids) - created_target_nodes_before,
            "edge_counts_by_ledger_list": dict(sorted(list_counts.items())),
            "input_base_graph": str(DEFAULT_BASE_GRAPH),
            "input_ledger": str(DEFAULT_LEDGER),
            "phase": PHASE,
        },
        "nodes": nodes,
        "phase": PHASE,
    }
    result["candidate_digest"] = "fix40_candidate:" + hashlib.sha256(
        canonical_bytes(
            {
                "edges": result["edges"],
                "nodes": result["nodes"],
                "phase": result["phase"],
                "status": result["candidate_status"],
            }
        )
    ).hexdigest()[:32]
    return result, result["fix40_merge_summary"]


def integrity_checks(candidate: dict[str, Any]) -> dict[str, Any]:
    nodes = [node for node in candidate.get("nodes", []) if isinstance(node, dict)]
    edges = [edge for edge in candidate.get("edges", []) if isinstance(edge, dict)]
    ids: list[str] = []
    for node in nodes:
        nid = node_id(node)
        if nid:
            ids.append(nid)
    id_counts = Counter(ids)
    node_id_set = set(ids)
    duplicates = sorted(nid for nid, count in id_counts.items() if count > 1)
    dangling = []
    for edge in edges:
        source = edge_source(edge)
        target = edge_target(edge)
        if source not in node_id_set or target not in node_id_set:
            dangling.append(
                {
                    "edge_id": str(edge.get("edge_id", "")),
                    "source": source,
                    "source_present": source in node_id_set,
                    "target": target,
                    "target_present": target in node_id_set,
                }
            )
    references_edges = [edge for edge in edges if edge_type(edge) == "REFERENCES_AUTHORITY"]
    legacy_missing_annotation = [
        str(edge.get("edge_id", ""))
        for edge in references_edges
        if edge.get("source_phase") != PHASE and not edge.get("annotation_method")
    ]
    fix40_missing_annotation = [
        str(edge.get("edge_id", ""))
        for edge in references_edges
        if edge.get("source_phase") == PHASE and not edge.get("annotation_method")
    ]
    proof_class_missing_phase = [
        str(edge.get("edge_id", ""))
        for edge in edges
        if edge.get("annotation_method") == "manual_reviewed" and not edge.get("annotation_phase")
    ]
    hard_stop = bool(dangling or duplicates)
    return {
        "duplicate_node_id_count": len(duplicates),
        "duplicate_node_ids_sample": duplicates[:50],
        "endpoint_dangling_edge_count": len(dangling),
        "endpoint_dangling_edges_sample": dangling[:50],
        "fix40_references_authority_missing_annotation_method_count": len(
            fix40_missing_annotation
        ),
        "fix40_references_authority_missing_annotation_method_sample": fix40_missing_annotation[:50],
        "hard_stop": hard_stop,
        "legacy_references_authority_missing_annotation_method_count": len(
            legacy_missing_annotation
        ),
        "legacy_references_authority_missing_annotation_method_sample": legacy_missing_annotation[
            :10
        ],
        "manual_reviewed_edges_missing_annotation_phase_count": len(proof_class_missing_phase),
        "manual_reviewed_edges_missing_annotation_phase_sample": proof_class_missing_phase[:50],
        "status": "failed_hard_stop" if hard_stop else "pass",
        "typed_trace_scope_note": (
            "Fix40 enforces annotation_method on Fix40-added REFERENCES_AUTHORITY edges. "
            "Legacy missing annotation_method counts are recorded as pre-existing debt "
            "because Fix40 is append-only and must not mutate existing edges."
        ),
    }


def run_coverage_checker(
    repo_root: Path,
    graph_path: Path,
    json_out: Path,
    report: Path,
) -> dict[str, Any]:
    command = [
        sys.executable,
        "tools/check_test_graph_coverage.py",
        "--graph",
        str(graph_path),
        "--json-out",
        str(json_out),
        "--report",
        str(report),
    ]
    result = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise Fix40Error(
            "coverage_checker_failed:"
            + result.stdout.strip()
            + result.stderr.strip()
        )
    payload = load_json(json_out)
    summary = payload["summary"]
    summary["coverage_checker_origin_phase"] = summary.get("phase", "1545p-Fix33")
    summary["phase"] = PHASE
    summary["graph_path"] = display_path(graph_path, repo_root)
    summary["output_tokens"] = OUTPUT_TOKENS
    summary["non_claims"] = sorted(
        set(summary.get("non_claims", []))
        | {
            "no_fix33_baseline_overwrite",
            "no_graph_promotion",
            "no_canonical_atlas_mutation",
            "no_genesis_signing",
            "no_node_upload",
            "no_public_graph_publication",
        }
    )
    canonical_write(json_out, payload)
    write_fix40_coverage_report(report, payload)
    return payload


def write_fix40_coverage_report(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    records = payload["file_records"]
    gap_counts = summary["gap_class_counts"]
    examples = {
        gap: [record["repo_path"] for record in records if gap in record["gap_classes"]][:10]
        for gap in sorted(gap_counts)
    }
    lines = [
        "<!-- PUBLIC_RC_EXCLUDE: fix40_homoiconic_test_graph_coverage_report -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Phase 1545p-Fix40 diagnostic report; no graph mutation, test execution, signing, public RC activation, or runtime activation. -->",
        "",
        "# ILC Test Graph Coverage Report 1545p-Fix40 v0.1",
        "",
        "Phase: 1545p-Fix40",
        "Status: report-first diagnostic rerun over Fix40 candidate",
        "Sensitivity: NON-SENSITIVE",
        "",
        "## Summary",
        "",
        f"- Coverage checker origin phase: `{summary['coverage_checker_origin_phase']}`",
        f"- Coverage input scope: `{summary['coverage_input_scope']}`",
        f"- Graph input: `{summary['graph_path']}`",
        f"- Graph nodes: `{summary['graph_node_count']}`",
        f"- Graph edges: `{summary['graph_edge_count']}`",
        f"- Graph TESTS edges: `{summary['graph_tests_edge_count']}`",
        f"- Local test/support Python files: `{summary['local_test_python_file_count']}`",
        f"- Mapped files: `{summary['mapped_test_file_count']}`",
        f"- Files with valid TESTS edge: `{summary['files_with_tests_edge_count']}`",
        f"- Missing candidate nodes: `{summary['missing_candidate_node_count']}`",
        f"- Missing TESTS edges: `{summary['missing_tests_edge_count']}`",
        f"- Dangling TESTS targets: `{summary['dangling_tests_target_count']}`",
        "",
        "## Gap Class Counts",
        "",
        "| Gap class | Count |",
        "|---|---:|",
    ]
    for gap, count in gap_counts.items():
        lines.append(f"| `{gap}` | `{count}` |")
    lines.extend(["", "## Gap Examples", ""])
    for gap, paths in examples.items():
        lines.append(f"### `{gap}`")
        if paths:
            lines.extend(f"- `{item}`" for item in paths)
        else:
            lines.append("None recorded.")
        lines.append("")
    lines.extend(
        [
            "## Non-Claims",
            "",
            "- No graph-selected tests were executed.",
            "- No function-level pytest collection was performed.",
            "- No canonical Atlas mutation occurred.",
            "- No edge promotion occurred.",
            "- No Genesis signing occurred.",
            "- No node upload occurred.",
            "- No public graph publication occurred.",
            "- No public RC activation occurred.",
            "- No runtime, economic, sidecar, ADR, or CDL mutation occurred.",
            "",
            "## Output Tokens",
            "",
        ]
    )
    lines.extend(f"- `{token}`" for token in OUTPUT_TOKENS)
    lines.extend(
        [
            "",
            "graph_delta=support_only:docs/specs/ilc_test_graph_coverage_report_1545p_fix40_v0.1.md -> testing/homoiconic-test-graph-coverage",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def coverage_delta(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    b = baseline["summary"]
    c = current["summary"]
    return {
        "authority_trace_satisfied_file_count": {
            "baseline": b["authority_trace_satisfied_file_count"],
            "current": c["authority_trace_satisfied_file_count"],
            "delta": c["authority_trace_satisfied_file_count"]
            - b["authority_trace_satisfied_file_count"],
        },
        "files_with_tests_edge_count": {
            "baseline": b["files_with_tests_edge_count"],
            "current": c["files_with_tests_edge_count"],
            "delta": c["files_with_tests_edge_count"] - b["files_with_tests_edge_count"],
        },
        "graph_edge_count": {
            "baseline": b["graph_edge_count"],
            "current": c["graph_edge_count"],
            "delta": c["graph_edge_count"] - b["graph_edge_count"],
        },
        "graph_node_count": {
            "baseline": b["graph_node_count"],
            "current": c["graph_node_count"],
            "delta": c["graph_node_count"] - b["graph_node_count"],
        },
        "missing_expected_authority_trace_count": {
            "baseline": b["gap_class_counts"].get("missing_expected_authority_trace", 0),
            "current": c["gap_class_counts"].get("missing_expected_authority_trace", 0),
            "delta": c["gap_class_counts"].get("missing_expected_authority_trace", 0)
            - b["gap_class_counts"].get("missing_expected_authority_trace", 0),
        },
        "missing_tests_edge_count": {
            "baseline": b["missing_tests_edge_count"],
            "current": c["missing_tests_edge_count"],
            "delta": c["missing_tests_edge_count"] - b["missing_tests_edge_count"],
        },
    }


def write_gap_analysis(
    path: Path,
    candidate_path: Path,
    coverage: dict[str, Any],
    baseline: dict[str, Any],
    integrity: dict[str, Any],
    merge_summary: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "coverage_delta_from_fix33": coverage_delta(baseline, coverage),
        "integrity": integrity,
        "metadata": {
            "candidate_path": str(candidate_path),
            "phase": PHASE,
            "source_baseline": str(FIX33_COVERAGE_BASELINE),
            "status": "research_only_not_canonical",
        },
        "merge_summary": merge_summary,
        "summary": coverage["summary"],
    }
    canonical_write(path, payload)
    return payload


def write_compile_diagnostic(
    path: Path,
    candidate_path: Path,
    coverage: dict[str, Any],
    integrity: dict[str, Any],
    merge_summary: dict[str, Any],
) -> dict[str, Any]:
    summary = coverage["summary"]
    payload = {
        "authority_traceability": {
            "authority_trace_expected_file_count": summary[
                "authority_trace_expected_file_count"
            ],
            "authority_trace_satisfied_file_count": summary[
                "authority_trace_satisfied_file_count"
            ],
            "missing_expected_authority_trace_count": summary["gap_class_counts"].get(
                "missing_expected_authority_trace", 0
            ),
            "role_specific_authority_trace_policy": summary["authority_trace_policy"],
        },
        "compile_coverage": {
            "files_with_tests_edge_count": summary["files_with_tests_edge_count"],
            "graph_edge_count": summary["graph_edge_count"],
            "graph_node_count": summary["graph_node_count"],
            "graph_tests_edge_count": summary["graph_tests_edge_count"],
            "local_test_python_file_count": summary["local_test_python_file_count"],
            "mapped_test_file_count": summary["mapped_test_file_count"],
            "missing_tests_edge_count": summary["missing_tests_edge_count"],
        },
        "edge_recipe_analysis": {
            "fix40_added_candidate_edges": merge_summary["added_candidate_edges"],
            "fix40_considered_ledger_edges": merge_summary["considered_ledger_edges"],
            "fix40_edge_counts_by_ledger_list": merge_summary[
                "edge_counts_by_ledger_list"
            ],
        },
        "gaps": summary["gap_class_counts"],
        "integrity": integrity,
        "metadata": {
            "candidate_path": str(candidate_path),
            "phase": PHASE,
            "status": "research_only_not_canonical",
        },
        "verdict": "FIX40_INTEGRITY_PASS_COVERAGE_RERUN_COMPLETE"
        if integrity["status"] == "pass"
        else "FIX40_INTEGRITY_FAILED_STOP",
    }
    canonical_write(path, payload)
    return payload


def write_delta_report(
    path: Path,
    gap_analysis: dict[str, Any],
    fix38_node_count: int,
    fix38_edge_count: int,
) -> None:
    delta = gap_analysis["coverage_delta_from_fix33"]
    current = gap_analysis["summary"]
    integrity = gap_analysis["integrity"]
    merge = gap_analysis["merge_summary"]
    lines = [
        "<!-- PUBLIC_RC_EXCLUDE: fix40_coverage_delta_report -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Internal research-only post-Fix38 coverage delta; no graph promotion, signing, upload, public RC activation, or runtime activation. -->",
        "",
        "# SIM-SPECTRAL-02 Fix40 Post-Fix38 Coverage Delta",
        "",
        "Phase: 1545p-Fix40",
        "Status: research-only diagnostic complete",
        "Sensitivity: NON-SENSITIVE",
        "",
        "## Boundary",
        "",
        "This report compares Fix33 coverage against the Fix40 candidate graph. It does not promote candidate edges, mutate canonical Atlas state, sign graph artifacts, upload nodes, activate public RC, activate runtime, or mutate ADR/CDL state.",
        "",
        "## Integrity",
        "",
        f"- Endpoint dangling edge count: `{integrity['endpoint_dangling_edge_count']}`",
        f"- Duplicate node ID count: `{integrity['duplicate_node_id_count']}`",
        f"- Fix40 REFERENCES_AUTHORITY edges missing annotation_method: `{integrity['fix40_references_authority_missing_annotation_method_count']}`",
        f"- Manual-reviewed edges missing annotation_phase: `{integrity['manual_reviewed_edges_missing_annotation_phase_count']}`",
        f"- Legacy REFERENCES_AUTHORITY edges missing annotation_method: `{integrity['legacy_references_authority_missing_annotation_method_count']}`",
        "",
        "## Merge Summary",
        "",
        f"- Fix38 annotations processed: `{merge['annotations_processed']}`",
        f"- Ledger edges considered: `{merge['considered_ledger_edges']}`",
        f"- Candidate edges added: `{merge['added_candidate_edges']}`",
        f"- Created source nodes: `{merge['created_source_nodes']}`",
        f"- Created target nodes: `{merge['created_target_nodes']}`",
        "",
        "## Coverage Delta",
        "",
        "| Metric | Fix33 baseline | Fix40 result | Delta |",
        "|---|---:|---:|---:|",
        f"| Files with TESTS edge | {delta['files_with_tests_edge_count']['baseline']} | {delta['files_with_tests_edge_count']['current']} | {delta['files_with_tests_edge_count']['delta']:+d} |",
        f"| Missing TESTS edges | {delta['missing_tests_edge_count']['baseline']} | {delta['missing_tests_edge_count']['current']} | {delta['missing_tests_edge_count']['delta']:+d} |",
        f"| Files with authority trace | {delta['authority_trace_satisfied_file_count']['baseline']} | {delta['authority_trace_satisfied_file_count']['current']} | {delta['authority_trace_satisfied_file_count']['delta']:+d} |",
        f"| Missing authority traces | {delta['missing_expected_authority_trace_count']['baseline']} | {delta['missing_expected_authority_trace_count']['current']} | {delta['missing_expected_authority_trace_count']['delta']:+d} |",
        f"| Total nodes | {delta['graph_node_count']['baseline']} | {delta['graph_node_count']['current']} | {delta['graph_node_count']['delta']:+d} |",
        f"| Total edges | {delta['graph_edge_count']['baseline']} | {delta['graph_edge_count']['current']} | {delta['graph_edge_count']['delta']:+d} |",
        "",
        "## Graph Input Baseline Note",
        "",
        f"The Fix33 coverage baseline used graph counts `{delta['graph_node_count']['baseline']}` nodes and `{delta['graph_edge_count']['baseline']}` edges. The immediate Fix38 unified candidate input to Fix40 contained `{fix38_node_count}` nodes and `{fix38_edge_count}` edges. Fix40 appends manual-ledger candidate edges to that Fix38 graph, so graph-count deltas above are relative to Fix33 coverage, while merge-count deltas above are relative to Fix38 input.",
        "",
        "## Current Gap Counts",
        "",
        f"- Missing candidate nodes: `{current['missing_candidate_node_count']}`",
        f"- Missing TESTS edges: `{current['missing_tests_edge_count']}`",
        f"- Missing expected authority traces: `{current['gap_class_counts'].get('missing_expected_authority_trace', 0)}`",
        f"- Dangling TESTS targets: `{current['dangling_tests_target_count']}`",
        "",
        "## Output Tokens",
        "",
    ]
    lines.extend(f"- `{token}`" for token in OUTPUT_TOKENS)
    lines.extend(
        [
            "",
            "graph_delta=support_only:docs/sims/sim_spectral_02/genesis_coverage_delta_fix38_v0.1.md -> testing/homoiconic-test-registry",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-graph", type=Path, default=DEFAULT_BASE_GRAPH)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--candidate-out", type=Path, default=DEFAULT_CANDIDATE_OUT)
    parser.add_argument("--coverage-json", type=Path, default=DEFAULT_COVERAGE_JSON)
    parser.add_argument("--coverage-report", type=Path, default=DEFAULT_COVERAGE_REPORT)
    parser.add_argument("--gap-analysis", type=Path, default=DEFAULT_GAP_ANALYSIS)
    parser.add_argument("--compile-diagnostic", type=Path, default=DEFAULT_COMPILE_DIAGNOSTIC)
    parser.add_argument("--delta-report", type=Path, default=DEFAULT_DELTA_REPORT)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    base_graph_path = args.base_graph if args.base_graph.is_absolute() else repo_root / args.base_graph
    ledger_path = args.ledger if args.ledger.is_absolute() else repo_root / args.ledger
    candidate_out = args.candidate_out if args.candidate_out.is_absolute() else repo_root / args.candidate_out
    coverage_json = args.coverage_json if args.coverage_json.is_absolute() else repo_root / args.coverage_json
    coverage_report = args.coverage_report if args.coverage_report.is_absolute() else repo_root / args.coverage_report
    gap_analysis = args.gap_analysis if args.gap_analysis.is_absolute() else repo_root / args.gap_analysis
    compile_diagnostic = (
        args.compile_diagnostic
        if args.compile_diagnostic.is_absolute()
        else repo_root / args.compile_diagnostic
    )
    delta_report = args.delta_report if args.delta_report.is_absolute() else repo_root / args.delta_report

    base_graph = load_json(base_graph_path)
    ledger = load_json(ledger_path)
    baseline = load_json(repo_root / FIX33_COVERAGE_BASELINE)
    fix38_node_count = len(base_graph.get("nodes", []))
    fix38_edge_count = len(base_graph.get("edges", []))

    candidate, merge_summary = merge_fix38_edges(base_graph, ledger, repo_root)
    integrity = integrity_checks(candidate)
    canonical_write(candidate_out, candidate)

    if integrity["hard_stop"]:
        canonical_write(
            gap_analysis,
            {
                "integrity": integrity,
                "metadata": {
                    "candidate_path": display_path(candidate_out, repo_root),
                    "phase": PHASE,
                    "status": "integrity_failed_stop",
                },
                "merge_summary": merge_summary,
                "output_tokens": ["fix40_integrity_check_failed_stop"],
            },
        )
        print("fix40_integrity_check_failed_stop", file=sys.stderr)
        return 1

    coverage = run_coverage_checker(repo_root, candidate_out, coverage_json, coverage_report)
    gap_payload = write_gap_analysis(
        gap_analysis,
        Path(display_path(candidate_out, repo_root)),
        coverage,
        baseline,
        integrity,
        merge_summary,
    )
    write_compile_diagnostic(
        compile_diagnostic,
        Path(display_path(candidate_out, repo_root)),
        coverage,
        integrity,
        merge_summary,
    )
    write_delta_report(delta_report, gap_payload, fix38_node_count, fix38_edge_count)
    print(
        json.dumps(
            {
                "added_candidate_edges": merge_summary["added_candidate_edges"],
                "candidate": display_path(candidate_out, repo_root),
                "coverage": display_path(coverage_json, repo_root),
                "integrity": integrity["status"],
                "missing_tests_edge_count": coverage["summary"]["missing_tests_edge_count"],
                "phase": PHASE,
            },
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
