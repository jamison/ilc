#!/usr/bin/env python3
"""Research-only pytest collection to test_function candidate emitter.

PUBLIC_RC_EXCLUDE: homoiconic_test_function_node_research_collector
PUBLIC_RC_EXCLUDE_REASON: Research-only diagnostic collector. It runs bounded
pytest collection, writes deterministic candidate reports, and does not execute
graph-selected tests, mutate graph state, sign nodes, or activate runtime/public
RC paths.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import check_test_graph_coverage as fix33


DEFAULT_FIX33_JSON = Path("out/test_graph_coverage_1545p_fix33.json")
DEFAULT_JSON_OUT = Path("out/test_function_nodes_1545p_fix34.json")
DEFAULT_REPORT = Path(
    "docs/specs/ilc_pytest_function_node_collection_report_1545p_fix34_v0.1.md"
)
DEFAULT_DIGEST_OUT = Path(
    "docs/specs/ilc_pytest_function_node_collection_digest_1545p_fix34_v0.1.json"
)

OUTPUT_TOKENS = [
    "pytest_function_node_candidates_committed_phase_1545p_fix34",
    "pytest_nodeid_identity_grounded_phase_1545p_fix34",
    "ast_only_identity_rejected_phase_1545p_fix34",
    "pytest_function_edges_deferred_where_uncertain_phase_1545p_fix34",
    "pytest_collection_no_test_execution_phase_1545p_fix34",
    "public_path_remains_blocked_phase_1545p_fix34",
]


def canonical_dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def stable_digest(value: str, length: int = 24) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sanitize_node_token(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.:-]+", "_", value).strip("_") or "unknown"


def run_pytest_collect(repo_root: Path, collect_target: str, timeout: int) -> dict[str, Any]:
    invocation_command = [
        sys.executable,
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        "--disable-warnings",
        "--continue-on-collection-errors",
        collect_target,
    ]
    env = dict(os.environ)
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    proc = subprocess.run(
        invocation_command,
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    nodeids = []
    for line in stdout.splitlines():
        candidate = line.strip()
        if not candidate.startswith("tests/") or "::" not in candidate:
            continue
        nodeids.append(candidate)
    unique_nodeids = sorted(dict.fromkeys(nodeids))
    stable_command = [
        "python",
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        "--disable-warnings",
        "--continue-on-collection-errors",
        collect_target,
    ]
    return {
        "command": stable_command,
        "exit_code": proc.returncode,
        "nodeid_list_sha256": hashlib.sha256(
            ("\n".join(unique_nodeids) + "\n").encode("utf-8")
        ).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
        "stderr_excerpt": stderr[:2000],
        "raw_nodeid_count": len(nodeids),
        "nodeids": unique_nodeids,
    }


def parse_pytest_nodeid(pytest_nodeid: str) -> dict[str, Any]:
    path_part, *parts = pytest_nodeid.split("::")
    function_segment = parts[-1] if parts else ""
    parametrization_id = None
    function_name = function_segment
    match = re.match(r"(?P<name>[^\[]+)(?P<param>\[.*\])$", function_segment)
    if match:
        function_name = match.group("name")
        parametrization_id = match.group("param")
    class_name = "::".join(parts[:-1]) if len(parts) > 1 else None
    return {
        "repo_path": path_part,
        "class_name": class_name,
        "function_name": function_name,
        "parametrization_id": parametrization_id,
    }


def ast_unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return node.__class__.__name__


def ast_metadata_for_file(path: Path) -> dict[tuple[str | None, str], dict[str, Any]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return {}

    records: dict[tuple[str | None, str], dict[str, Any]] = {}

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            records[(None, node.name)] = metadata_for_function(node)
        elif isinstance(node, ast.ClassDef):
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    records[(node.name, member.name)] = metadata_for_function(member)
    return records


def metadata_for_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    decorators = [ast_unparse(deco) for deco in node.decorator_list]
    marks = []
    for deco in decorators:
        match = re.search(r"(?:pytest\.)?mark\.([A-Za-z0-9_]+)", deco)
        if match:
            marks.append(match.group(1))
    args = []
    all_args = list(node.args.posonlyargs) + list(node.args.args) + list(node.args.kwonlyargs)
    for arg in all_args:
        if arg.arg not in {"self", "cls"}:
            args.append(arg.arg)
    return {
        "decorators": sorted(decorators),
        "fixtures": sorted(dict.fromkeys(args)),
        "marks": sorted(dict.fromkeys(marks)),
        "lineno": getattr(node, "lineno", None),
        "is_async": isinstance(node, ast.AsyncFunctionDef),
    }


def load_fix33_records(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    records = {
        record["repo_path"]: record
        for record in data.get("file_records", [])
        if isinstance(record, dict) and isinstance(record.get("repo_path"), str)
    }
    return data, records


def graph_tests_targets_for_file(graph: fix33.GraphIndex, file_record: dict[str, Any]) -> list[str]:
    targets: set[str] = set()
    for nid in file_record.get("candidate_node_ids", []):
        for edge in graph.outgoing_tests.get(nid, []):
            if edge.get("target_resolves"):
                targets.add(str(edge["target"]))
    return sorted(targets)


def build_candidate_payload(
    repo_root: Path,
    collect_target: str,
    collect_timeout: int,
    fix33_json: Path,
    graph_path: Path | None,
    preferred_graph: Path,
    fallback_graph: Path,
) -> dict[str, Any]:
    fix33_payload, fix33_records = load_fix33_records(fix33_json)
    selected_graph, coverage_scope = fix33.select_graph(preferred_graph, fallback_graph, graph_path)
    graph = fix33.load_graph_index(selected_graph, coverage_scope)
    policy = fix33.load_pytest_policy(repo_root / "tests/conftest.py", repo_root / "pyproject.toml")
    collection = run_pytest_collect(repo_root, collect_target, collect_timeout)

    ast_cache: dict[str, dict[tuple[str | None, str], dict[str, Any]]] = {}
    function_nodes: list[dict[str, Any]] = []
    candidate_edges: list[dict[str, Any]] = []
    deferred_records: list[dict[str, Any]] = []
    profile_counts: Counter[str] = Counter()
    gate_counts: Counter[str] = Counter()
    edge_type_counts: Counter[str] = Counter()
    source_file_counts: Counter[str] = Counter()
    nodes_with_fixtures = 0
    nodes_with_marks = 0

    for pytest_nodeid in collection["nodeids"]:
        parsed = parse_pytest_nodeid(pytest_nodeid)
        repo_path = parsed["repo_path"]
        source_path = repo_root / repo_path
        if repo_path not in ast_cache:
            ast_cache[repo_path] = ast_metadata_for_file(source_path)
        ast_map = ast_cache[repo_path]
        ast_meta = ast_map.get(
            (parsed["class_name"], parsed["function_name"])
        ) or ast_map.get((None, parsed["function_name"])) or {
            "decorators": [],
            "fixtures": [],
            "marks": [],
            "lineno": None,
            "is_async": False,
        }
        file_record = fix33_records.get(repo_path, {})
        if file_record:
            classification = {
                "executor_profiles": file_record.get("executor_profiles", []),
                "environment_gates": file_record.get("environment_gates", []),
                "candidate_node_ids": file_record.get("candidate_node_ids", []),
                "candidate_node_status": file_record.get("candidate_node_status"),
            }
        else:
            classification = fix33.classify_test_file(source_path, repo_path, policy)
            classification["candidate_node_ids"] = []
            classification["candidate_node_status"] = "missing_candidate_node"

        source_file_node_ids = sorted(set(classification.get("candidate_node_ids", [])))
        inherited_targets = graph_tests_targets_for_file(graph, file_record) if file_record else []
        node_id = f"test_function:{stable_digest(pytest_nodeid)}"
        profiles = sorted(set(classification.get("executor_profiles", [])))
        gates = sorted(set(classification.get("environment_gates", [])))
        fixtures = sorted(set(ast_meta.get("fixtures", [])))
        marks = sorted(set(ast_meta.get("marks", [])))
        if fixtures:
            nodes_with_fixtures += 1
        if marks:
            nodes_with_marks += 1
        for profile in profiles:
            profile_counts[profile] += 1
        for gate in gates:
            gate_counts[gate] += 1
        source_file_counts[repo_path] += 1

        function_nodes.append(
            {
                "node_kind": "test_function",
                "node_id": node_id,
                "pytest_nodeid": pytest_nodeid,
                "pytest_nodeid_sha256": hashlib.sha256(pytest_nodeid.encode("utf-8")).hexdigest(),
                "identity_source": "pytest_collect_only",
                "repo_path": repo_path,
                "source_file_node_ids": source_file_node_ids,
                "source_file_node_status": classification.get("candidate_node_status", "unknown"),
                "class_name": parsed["class_name"],
                "function_name": parsed["function_name"],
                "parametrization_id": parsed["parametrization_id"],
                "lineno": ast_meta.get("lineno"),
                "is_async": bool(ast_meta.get("is_async", False)),
                "marks": marks,
                "fixtures": fixtures,
                "decorators": ast_meta.get("decorators", []),
                "executor_profiles": profiles,
                "environment_gates": gates,
                "inherited_tests_target_count": len(inherited_targets),
                "inherited_tests_targets": inherited_targets[:25],
                "covers_symbol_status": "deferred_no_strong_function_specific_evidence",
                "promotion_status": "candidate_only",
                "non_claim_boundary": "no_test_execution_no_evidence_envelope_no_edge_promotion",
            }
        )

        for source_file_node_id in source_file_node_ids:
            edge = make_edge(
                "DERIVED_FROM",
                node_id,
                source_file_node_id,
                "pytest_nodeid_source_file",
                "high",
            )
            candidate_edges.append(edge)
            edge_type_counts[edge["edge_type"]] += 1
        for fixture in fixtures:
            edge = make_edge(
                "USES_FIXTURE",
                node_id,
                f"pytest_fixture:{sanitize_node_token(fixture)}",
                "ast_function_argument_enrichment",
                "candidate",
            )
            candidate_edges.append(edge)
            edge_type_counts[edge["edge_type"]] += 1
        for profile in profiles:
            edge = make_edge(
                "REQUIRES_PROFILE",
                node_id,
                f"executor_profile:{profile}",
                "fix33_file_level_executor_classification",
                "candidate",
            )
            candidate_edges.append(edge)
            edge_type_counts[edge["edge_type"]] += 1
        for gate in gates:
            edge = make_edge(
                "SKIPPED_BY_DEFAULT_UNLESS",
                node_id,
                f"env_gate:{sanitize_node_token(gate)}",
                "fix33_file_level_gate_classification",
                "candidate",
            )
            candidate_edges.append(edge)
            edge_type_counts[edge["edge_type"]] += 1
        for target in inherited_targets:
            edge = make_edge(
                "TESTS",
                node_id,
                target,
                "file_level_tests_edge_inherited_for_review",
                "deferred_function_specific_confirmation_required",
            )
            candidate_edges.append(edge)
            edge_type_counts[edge["edge_type"]] += 1

        if not inherited_targets:
            deferred_records.append(
                {
                    "node_id": node_id,
                    "pytest_nodeid": pytest_nodeid,
                    "deferred_reason": "no_file_level_tests_target_available",
                    "repo_path": repo_path,
                }
            )
        else:
            deferred_records.append(
                {
                    "node_id": node_id,
                    "pytest_nodeid": pytest_nodeid,
                    "deferred_reason": "function_specific_coverage_not_proven_by_file_level_inheritance",
                    "repo_path": repo_path,
                    "inherited_tests_target_count": len(inherited_targets),
                }
            )

    summary = {
        "phase": "1545p-Fix34",
        "status": "pass" if function_nodes else "blocked_no_pytest_items_collected",
        "coverage_input_scope": coverage_scope,
        "graph_path": str(selected_graph),
        "fix33_json": str(fix33_json),
        "collect_target": collect_target,
        "collection_command": collection["command"],
        "collection_exit_code": collection["exit_code"],
        "collection_nodeid_list_sha256": collection["nodeid_list_sha256"],
        "collection_stderr_sha256": collection["stderr_sha256"],
        "collection_stderr_excerpt": collection["stderr_excerpt"],
        "collected_test_function_count": len(function_nodes),
        "source_test_file_count": len(source_file_counts),
        "function_nodes_with_source_file_node_count": sum(
            1 for node in function_nodes if node["source_file_node_ids"]
        ),
        "function_nodes_with_inherited_tests_targets_count": sum(
            1 for node in function_nodes if node["inherited_tests_target_count"] > 0
        ),
        "function_nodes_with_fixture_metadata_count": nodes_with_fixtures,
        "function_nodes_with_mark_metadata_count": nodes_with_marks,
        "candidate_edge_count": len(candidate_edges),
        "candidate_edge_type_counts": dict(sorted(edge_type_counts.items())),
        "executor_profile_counts": dict(sorted(profile_counts.items())),
        "environment_gate_counts": dict(sorted(gate_counts.items())),
        "deferred_record_count": len(deferred_records),
        "fix33_missing_candidate_nodes_carried_forward": fix33_payload["summary"].get(
            "missing_candidate_node_count"
        ),
        "identity_policy": {
            "pytest_nodeid_identity_source_required": True,
            "ast_only_identity_rejected": True,
            "parametrized_nodeids_remain_distinct": True,
        },
        "edge_policy": {
            "file_level_tests_inheritance_is_provisional": True,
            "covers_symbol_emitted_only_with_strong_evidence": True,
            "covers_symbol_candidate_count": edge_type_counts.get("COVERS_SYMBOL", 0),
        },
        "output_tokens": OUTPUT_TOKENS,
        "non_claims": [
            "no_test_execution",
            "no_graph_mutation",
            "no_edge_promotion",
            "no_canonical_atlas_mutation",
            "no_evidence_envelope_generation",
            "no_genesis_signing",
            "no_node_upload",
            "no_public_rc_activation",
            "no_runtime_activation",
            "no_adr_cdl_mutation",
        ],
    }
    return {
        "summary": summary,
        "test_function_nodes": function_nodes,
        "candidate_edges": sorted(
            candidate_edges,
            key=lambda edge: (edge["edge_type"], edge["source"], edge["target"]),
        ),
        "deferred_records": deferred_records,
    }


def make_edge(
    edge_type: str,
    source: str,
    target: str,
    evidence_basis: str,
    confidence: str,
) -> dict[str, str]:
    return {
        "edge_type": edge_type,
        "source": source,
        "target": target,
        "evidence_basis": evidence_basis,
        "confidence": confidence,
        "promotion_status": "candidate_only",
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = payload["summary"]
    examples = payload["test_function_nodes"][:10]
    lines = [
        "<!-- PUBLIC_RC_EXCLUDE: homoiconic_test_function_node_report_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Phase 1545p-Fix34 diagnostic report; no test execution, evidence envelope, graph mutation, signing, public RC activation, or runtime activation. -->",
        "",
        "# ILC Pytest Function-Node Collection Report 1545p-Fix34 v0.1",
        "",
        "Phase: 1545p-Fix34",
        "Status: committed research-only candidate collection",
        "Sensitivity: NON-SENSITIVE",
        "",
        "## Summary",
        "",
        f"- Coverage input scope: `{summary['coverage_input_scope']}`",
        f"- Graph input: `{summary['graph_path']}`",
        f"- Fix33 JSON input: `{summary['fix33_json']}`",
        f"- Collect target: `{summary['collect_target']}`",
        f"- Collection exit code: `{summary['collection_exit_code']}`",
        f"- Collected test function candidates: `{summary['collected_test_function_count']}`",
        f"- Source test files represented: `{summary['source_test_file_count']}`",
        f"- Function nodes with mapped source file node: `{summary['function_nodes_with_source_file_node_count']}`",
        f"- Function nodes with inherited file-level TESTS targets: `{summary['function_nodes_with_inherited_tests_targets_count']}`",
        f"- Function nodes with fixture metadata: `{summary['function_nodes_with_fixture_metadata_count']}`",
        f"- Function nodes with mark metadata: `{summary['function_nodes_with_mark_metadata_count']}`",
        f"- Candidate edges: `{summary['candidate_edge_count']}`",
        f"- Deferred records: `{summary['deferred_record_count']}`",
        "",
        "## Candidate Edge Type Counts",
        "",
        "| Edge type | Count |",
        "|---|---:|",
    ]
    for edge_type, count in summary["candidate_edge_type_counts"].items():
        lines.append(f"| `{edge_type}` | `{count}` |")
    lines.extend(["", "## Executor Profile Counts", "", "| Profile | Count |", "|---|---:|"])
    for profile, count in summary["executor_profile_counts"].items():
        lines.append(f"| `{profile}` | `{count}` |")
    lines.extend(["", "## Example Function Nodes", ""])
    for node in examples:
        lines.append(
            f"- `{node['pytest_nodeid']}` -> `{node['node_id']}` "
            f"(profiles: `{','.join(node['executor_profiles'])}`; "
            f"inherited targets: `{node['inherited_tests_target_count']}`)"
        )
    lines.extend(
        [
            "",
            "## Identity And Edge Policy",
            "",
            "- `pytest_nodeid` identity is grounded in bounded `pytest --collect-only` output.",
            "- AST data is enrichment only and cannot create a candidate identity by itself.",
            "- Parametrized pytest node IDs remain distinct candidate nodes.",
            "- File-level `TESTS` inheritance is provisional and requires later function-specific confirmation.",
            "- `COVERS_SYMBOL` remains deferred unless strong function-specific evidence exists.",
            "",
            "## Non-Claims",
            "",
            "- No tests were executed.",
            "- No graph-selected test runner was implemented.",
            "- No evidence envelope was generated.",
            "- No canonical Atlas mutation occurred.",
            "- No edge promotion occurred.",
            "- No Genesis signing occurred.",
            "- No node upload occurred.",
            "- No public graph publication occurred.",
            "- No public repository push occurred.",
            "- No public RC activation occurred.",
            "- No runtime, economic, sidecar, ADR, or CDL mutation occurred.",
            "",
            "## Output Tokens",
            "",
        ]
    )
    for token in OUTPUT_TOKENS:
        lines.append(f"- `{token}`")
    lines.append("")
    lines.append(
        "graph_delta=support_only:docs/specs/ilc_pytest_function_node_collection_report_1545p_fix34_v0.1.md -> testing/homoiconic-test-function-node-candidates"
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_digest(path: Path, payload: dict[str, Any], artifact_path: Path) -> None:
    summary = payload["summary"]
    digest = {
        "phase": "1545p-Fix34",
        "status": summary["status"],
        "full_artifact_path": artifact_path.as_posix(),
        "full_artifact_sha256": sha256_file(artifact_path),
        "full_artifact_size_bytes": artifact_path.stat().st_size,
        "full_artifact_git_policy": "local_reproducible_not_committed_large_artifact",
        "regeneration_command": [
            ".venv/bin/python",
            "tools/collect_pytest_function_nodes.py",
            "--json-out",
            artifact_path.as_posix(),
            "--report",
            DEFAULT_REPORT.as_posix(),
            "--digest-out",
            path.as_posix(),
        ],
        "summary": summary,
        "sample_test_function_nodes": payload["test_function_nodes"][:25],
        "sample_candidate_edges": payload["candidate_edges"][:25],
        "sample_deferred_records": payload["deferred_records"][:25],
        "non_claims": summary["non_claims"],
    }
    canonical_dump(path, digest)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=None)
    parser.add_argument("--preferred-graph", type=Path, default=fix33.DEFAULT_PREFERRED_GRAPH)
    parser.add_argument("--fallback-graph", type=Path, default=fix33.DEFAULT_FALLBACK_GRAPH)
    parser.add_argument("--fix33-json", type=Path, default=DEFAULT_FIX33_JSON)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--digest-out", type=Path, default=DEFAULT_DIGEST_OUT)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--collect-target", default="tests")
    parser.add_argument("--collect-timeout", type=int, default=180)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    payload = build_candidate_payload(
        repo_root=repo_root,
        collect_target=args.collect_target,
        collect_timeout=args.collect_timeout,
        fix33_json=args.fix33_json,
        graph_path=args.graph,
        preferred_graph=args.preferred_graph,
        fallback_graph=args.fallback_graph,
    )
    canonical_dump(args.json_out, payload)
    write_report(args.report, payload)
    write_digest(args.digest_out, payload, args.json_out)
    return 0 if payload["summary"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
