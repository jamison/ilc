#!/usr/bin/env python3
"""Read-only test graph coverage checker for Phase 1545p-Fix33.

PUBLIC_RC_EXCLUDE: homoiconic_test_graph_coverage_research_checker
PUBLIC_RC_EXCLUDE_REASON: Research-only diagnostic checker. It reads candidate
Atlas artifacts and local test files, writes deterministic reports, and does
not execute graph-selected tests, mutate graph state, sign nodes, or activate
runtime/public RC paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_PREFERRED_GRAPH = Path(
    "out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json"
)
DEFAULT_FALLBACK_GRAPH = Path("out/genesis_atlas_full_repo_candidate_1545p_fix22.json")
DEFAULT_QUEUES = (
    Path("out/atlas_research/genesis_atlas_atom_candidates_1545p_fix26.jsonl"),
    Path("out/atlas_research/genesis_atlas_semantic_prepass_fix27.jsonl"),
)
DEFAULT_JSON_OUT = Path("out/test_graph_coverage_1545p_fix33.json")
DEFAULT_REPORT = Path("docs/specs/ilc_test_graph_coverage_report_1545p_fix33_v0.1.md")

OUTPUT_TOKENS = [
    "homoiconic_test_graph_coverage_checker_committed_phase_1545p_fix33",
    "homoiconic_test_file_node_mapping_audited_phase_1545p_fix33",
    "homoiconic_test_executor_gate_classification_recorded_phase_1545p_fix33",
    "homoiconic_test_missing_tests_edges_routed_phase_1545p_fix33",
    "homoiconic_test_graph_checker_report_only_phase_1545p_fix33",
    "public_path_remains_blocked_phase_1545p_fix33",
]

AUTHORITY_EXPECTATION_TERMS = (
    "adr",
    "cdl",
    "phase",
    "window",
    "closure",
    "governance",
    "obligation",
    "public_rc",
    "release",
    "genesis",
    "patent",
)

AUTHORITY_TRACE_EDGE_TYPES = frozenset(
    {
        "CLASSIFIED_BY",
        "DERIVED_FROM",
        "EVIDENCES",
        "IMPLEMENTS",
        "REFERENCES_AUTHORITY",
        "REGRESSES",
        "TESTS",
    }
)

AUTHORITY_TRACE_TARGET_PREFIXES = (
    "adr:",
    "cdl:",
    "phase:",
    "phase_window:",
    "policy:",
)

PRIVATE_LIVE_TERMS = (
    "tailscale",
    "vps",
    "ssh",
    "live network",
    "live_network",
    "private testbed",
    "node-2",
    "node-3",
    "node-6",
)


@dataclass(frozen=True)
class GraphIndex:
    path: Path
    coverage_input_scope: str
    node_count: int
    edge_count: int
    node_ids: frozenset[str]
    path_to_node_ids: dict[str, list[str]]
    outgoing_tests: dict[str, list[dict[str, Any]]]
    outgoing_role_traces: dict[str, list[dict[str, Any]]]
    edge_type_counts: Counter[str]


def canonical_dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def graph_paths_for_node(node: dict[str, Any]) -> Iterable[str]:
    for key in ("source_path", "repo_path", "label", "path"):
        value = node.get(key)
        if isinstance(value, str) and value.startswith("tests/"):
            yield value


def select_graph(preferred: Path, fallback: Path, explicit_graph: Path | None) -> tuple[Path, str]:
    if explicit_graph is not None:
        if not explicit_graph.exists():
            raise FileNotFoundError(f"graph_not_found:{explicit_graph}")
        explicit_resolved = explicit_graph.resolve()
        if explicit_resolved == preferred.resolve():
            return explicit_graph, "enriched_graph"
        if explicit_resolved == fallback.resolve():
            return explicit_graph, "lower_information_fallback"
        return explicit_graph, "explicit_graph"
    if preferred.exists():
        return preferred, "enriched_graph"
    if fallback.exists():
        return fallback, "lower_information_fallback"
    raise FileNotFoundError(
        f"no_graph_available:preferred={preferred}:fallback={fallback}"
    )


def load_graph_index(graph_path: Path, coverage_input_scope: str) -> GraphIndex:
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("graph_must_have_nodes_and_edges_lists")

    path_to_node_ids: dict[str, list[str]] = defaultdict(list)
    node_ids: set[str] = set()
    for n in nodes:
        if not isinstance(n, dict):
            continue
        nid = node_id(n)
        if not nid:
            continue
        node_ids.add(nid)
        for graph_path_value in graph_paths_for_node(n):
            path_to_node_ids[graph_path_value].append(nid)

    outgoing_tests: dict[str, list[dict[str, Any]]] = defaultdict(list)
    outgoing_role_traces: dict[str, list[dict[str, Any]]] = defaultdict(list)
    edge_type_counts: Counter[str] = Counter()
    for e in edges:
        if not isinstance(e, dict):
            continue
        etype = edge_type(e)
        edge_type_counts[etype] += 1
        src = edge_source(e)
        tgt = edge_target(e)
        if not src or not tgt:
            continue
        edge_record = {
            "source": src,
            "target": tgt,
            "edge_type": etype,
            "provenance": e.get("provenance", "graph"),
            "target_resolves": tgt in node_ids,
        }
        if etype == "TESTS":
            outgoing_tests[src].append(edge_record)
        if etype in AUTHORITY_TRACE_EDGE_TYPES:
            outgoing_role_traces[src].append(edge_record)

    return GraphIndex(
        path=graph_path,
        coverage_input_scope=coverage_input_scope,
        node_count=len(nodes),
        edge_count=len(edges),
        node_ids=frozenset(node_ids),
        path_to_node_ids={k: sorted(set(v)) for k, v in path_to_node_ids.items()},
        outgoing_tests={k: sorted(v, key=lambda item: item["target"]) for k, v in outgoing_tests.items()},
        outgoing_role_traces={
            k: sorted(v, key=lambda item: (item["edge_type"], item["target"]))
            for k, v in outgoing_role_traces.items()
        },
        edge_type_counts=edge_type_counts,
    )


def extract_constant_file_names(conftest_text: str, constant_name: str) -> set[str]:
    lines = conftest_text.splitlines()
    collecting = False
    names: set[str] = set()
    for line in lines:
        if line.startswith(f"{constant_name} = frozenset("):
            collecting = True
            continue
        if collecting and line == ")":
            break
        if collecting:
            names.update(re.findall(r'"([^"]+\.py)"', line))
    return names


def load_pytest_policy(conftest_path: Path, pyproject_path: Path) -> dict[str, Any]:
    conftest_text = conftest_path.read_text(encoding="utf-8")
    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    historical = extract_constant_file_names(
        conftest_text, "HISTORICAL_PHASE_SNAPSHOT_TEST_FILES"
    )
    expensive = extract_constant_file_names(
        conftest_text, "EXPENSIVE_RELEASE_ARTIFACT_TEST_FILES"
    )
    marker_names = sorted(set(re.findall(r'"([a-zA-Z0-9_]+):', pyproject_text)))
    return {
        "conftest_path": str(conftest_path),
        "pyproject_path": str(pyproject_path),
        "historical_phase_snapshot_file_count": len(historical),
        "expensive_release_artifact_file_count": len(expensive),
        "historical_phase_snapshot_files": sorted(historical),
        "expensive_release_artifact_files": sorted(expensive),
        "pyproject_marker_names": marker_names,
    }


def test_python_files(tests_root: Path) -> list[Path]:
    return sorted(
        path
        for path in tests_root.rglob("*.py")
        if "__pycache__" not in path.parts and path.is_file()
    )


def classify_test_file(path: Path, rel_path: str, policy: dict[str, Any]) -> dict[str, Any]:
    name = path.name
    text = path.read_text(encoding="utf-8", errors="replace")
    profiles: list[str] = []
    gates: list[str] = []
    gap_overrides: list[str] = []

    if name in set(policy["historical_phase_snapshot_files"]):
        profiles.append("historical_phase_snapshot")
        gates.append("ILC_RUN_HISTORICAL_PHASE_SNAPSHOT_TESTS=1")
    if name in set(policy["expensive_release_artifact_files"]):
        profiles.append("expensive_release_artifact")
        gates.append("ILC_RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS=1")
    if "GATE_SELFTEST" in text or re.search(r"ILC_PHASE_[A-Z0-9_]+SELFTEST", text):
        profiles.append("sensitive_phase_selftest")
        gates.append("phase_specific_selftest_env")
    lowered = text.lower()
    if any(term in lowered for term in PRIVATE_LIVE_TERMS):
        profiles.append("live_network_vps_gated")
        gates.append("explicit_live_or_private_operator_gate")
    if "PUBLIC_RC_EXCLUDE" in text:
        profiles.append("private_local_only")
        gates.append("public_rc_exclude_marker")
    if not name.startswith("test"):
        profiles.append("pytest_support_file")
        gap_overrides.append("support_file_not_default_test")

    if not profiles:
        profiles.append("default_local_pytest")

    default_visible = profiles == ["default_local_pytest"]
    requires_authority_trace = any(
        term in rel_path.lower() for term in AUTHORITY_EXPECTATION_TERMS
    )
    return {
        "executor_profiles": sorted(set(profiles)),
        "environment_gates": sorted(set(gates)),
        "default_query_visibility": "included" if default_visible else "excluded_by_gate",
        "requires_role_specific_authority_trace": requires_authority_trace,
        "gap_overrides": sorted(set(gap_overrides)),
        "sha256": sha256_file(path),
    }


def load_supplemental_test_edges(
    queue_paths: list[Path], path_to_node_ids: dict[str, list[str]], node_ids: frozenset[str]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    queue_stats: dict[str, Any] = {}
    for queue_path in queue_paths:
        if not queue_path.exists():
            queue_stats[str(queue_path)] = {"status": "missing", "records": 0, "usable_tests_edges": 0}
            continue
        records = 0
        usable = 0
        with queue_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records += 1
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("edge_type") != "TESTS":
                    continue
                source_path = rec.get("source_path")
                target_path = rec.get("target_path")
                if not isinstance(source_path, str) or not isinstance(target_path, str):
                    continue
                source_ids = path_to_node_ids.get(source_path, [])
                target_ids = path_to_node_ids.get(target_path, [])
                for source_id in source_ids:
                    for target_id in target_ids:
                        usable += 1
                        edges.append(
                            {
                                "source": source_id,
                                "target": target_id,
                                "edge_type": "TESTS",
                                "provenance": f"supplemental_queue:{queue_path.name}",
                                "target_resolves": target_id in node_ids,
                            }
                        )
        queue_stats[str(queue_path)] = {
            "status": "loaded",
            "records": records,
            "usable_tests_edges": usable,
        }
    return edges, queue_stats


def authority_trace_satisfied(
    tests_edges: list[dict[str, Any]],
    role_trace_edges: list[dict[str, Any]],
) -> bool:
    for edge in [*tests_edges, *role_trace_edges]:
        if not edge.get("target_resolves", False):
            continue
        target = edge["target"].lower()
        if (
            target.startswith(AUTHORITY_TRACE_TARGET_PREFIXES)
            or "docs_adr_" in target
            or "docs_specs_" in target
            or "docs_phases_" in target
        ):
            return True
    return False


def build_coverage(
    repo_root: Path,
    graph: GraphIndex,
    policy: dict[str, Any],
    queue_paths: list[Path],
) -> dict[str, Any]:
    supplemental_edges, queue_stats = load_supplemental_test_edges(
        queue_paths, graph.path_to_node_ids, graph.node_ids
    )
    outgoing_tests = defaultdict(list, {k: list(v) for k, v in graph.outgoing_tests.items()})
    for edge in supplemental_edges:
        outgoing_tests[edge["source"]].append(edge)

    records: list[dict[str, Any]] = []
    gap_counts: Counter[str] = Counter()
    profile_counts: Counter[str] = Counter()
    dangling_targets: list[dict[str, str]] = []
    tests_with_edges = 0
    mapped_files = 0
    authority_expected = 0
    authority_satisfied = 0

    for path in test_python_files(repo_root / "tests"):
        rel_path = path.relative_to(repo_root).as_posix()
        classification = classify_test_file(path, rel_path, policy)
        for profile in classification["executor_profiles"]:
            profile_counts[profile] += 1

        node_ids = graph.path_to_node_ids.get(rel_path, [])
        if node_ids:
            mapped_files += 1

        file_tests_edges: list[dict[str, Any]] = []
        file_role_trace_edges: list[dict[str, Any]] = []
        for nid in node_ids:
            file_tests_edges.extend(outgoing_tests.get(nid, []))
            file_role_trace_edges.extend(graph.outgoing_role_traces.get(nid, []))
        file_tests_edges = sorted(
            file_tests_edges,
            key=lambda item: (item["source"], item["target"], item["provenance"]),
        )
        file_role_trace_edges = sorted(
            file_role_trace_edges,
            key=lambda item: (
                item["source"],
                item["edge_type"],
                item["target"],
                item["provenance"],
            ),
        )
        valid_edges = [edge for edge in file_tests_edges if edge["target_resolves"]]
        valid_role_trace_edges = [
            edge for edge in file_role_trace_edges if edge["target_resolves"]
        ]
        if valid_edges:
            tests_with_edges += 1
        for edge in file_tests_edges:
            if not edge["target_resolves"]:
                dangling_targets.append(
                    {"source": edge["source"], "target": edge["target"], "file": rel_path}
                )

        gap_classes: list[str] = []
        if not node_ids:
            gap_classes.append("missing_candidate_node")
        if classification["gap_overrides"]:
            gap_classes.extend(classification["gap_overrides"])
        if node_ids and not valid_edges and "support_file_not_default_test" not in gap_classes:
            gap_classes.append("missing_tests_edge")
        if any(not edge["target_resolves"] for edge in file_tests_edges):
            gap_classes.append("dangling_tests_target")
        if classification["requires_role_specific_authority_trace"]:
            authority_expected += 1
            if authority_trace_satisfied(valid_edges, valid_role_trace_edges):
                authority_satisfied += 1
            elif node_ids:
                gap_classes.append("missing_expected_authority_trace")
        if not gap_classes and valid_edges:
            gap_classes.append("ready_for_function_collection")

        for gap in sorted(set(gap_classes)):
            gap_counts[gap] += 1

        records.append(
            {
                "repo_path": rel_path,
                "source_sha256": classification["sha256"],
                "candidate_node_ids": node_ids,
                "candidate_node_status": "mapped" if node_ids else "missing_candidate_node",
                "executor_profiles": classification["executor_profiles"],
                "environment_gates": classification["environment_gates"],
                "default_query_visibility": classification["default_query_visibility"],
                "requires_role_specific_authority_trace": classification[
                    "requires_role_specific_authority_trace"
                ],
                "tests_edge_count": len(valid_edges),
                "tests_targets": sorted({edge["target"] for edge in valid_edges})[:25],
                "role_trace_edge_count": len(valid_role_trace_edges),
                "role_trace_targets": sorted(
                    {
                        f"{edge['edge_type']}:{edge['target']}"
                        for edge in valid_role_trace_edges
                    }
                )[:25],
                "gap_classes": sorted(set(gap_classes)),
            }
        )

    total = len(records)
    summary = {
        "phase": "1545p-Fix33",
        "status": "pass",
        "coverage_input_scope": graph.coverage_input_scope,
        "graph_path": str(graph.path),
        "graph_node_count": graph.node_count,
        "graph_edge_count": graph.edge_count,
        "graph_tests_edge_count": graph.edge_type_counts.get("TESTS", 0),
        "supplemental_queue_stats": queue_stats,
        "supplemental_tests_edge_count": len(supplemental_edges),
        "local_test_python_file_count": total,
        "mapped_test_file_count": mapped_files,
        "missing_candidate_node_count": gap_counts.get("missing_candidate_node", 0),
        "files_with_tests_edge_count": tests_with_edges,
        "missing_tests_edge_count": gap_counts.get("missing_tests_edge", 0),
        "dangling_tests_target_count": len(dangling_targets),
        "authority_trace_expected_file_count": authority_expected,
        "authority_trace_satisfied_file_count": authority_satisfied,
        "gap_class_counts": dict(sorted(gap_counts.items())),
        "executor_profile_counts": dict(sorted(profile_counts.items())),
        "authority_trace_policy": {
            "ordinary_runtime_tests_do_not_require_references_authority": True,
            "role_specific_authority_trace_checked_only_when_expected": True,
            "role_specific_trace_edges_are_evaluated_directly": True,
        },
        "report_first_mode": True,
        "enforce_threshold_default": False,
        "output_tokens": OUTPUT_TOKENS,
        "non_claims": [
            "no_test_execution",
            "no_graph_mutation",
            "no_edge_promotion",
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
        "file_records": records,
        "dangling_tests_targets": dangling_targets[:100],
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = payload["summary"]
    records = payload["file_records"]
    gap_counts = summary["gap_class_counts"]

    examples = {
        gap: [record["repo_path"] for record in records if gap in record["gap_classes"]][:10]
        for gap in sorted(gap_counts)
    }

    lines = [
        "<!-- PUBLIC_RC_EXCLUDE: homoiconic_test_graph_coverage_report_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Phase 1545p-Fix33 diagnostic report; no graph mutation, test execution, signing, public RC activation, or runtime activation. -->",
        "",
        "# ILC Test Graph Coverage Report 1545p-Fix33 v0.1",
        "",
        "Phase: 1545p-Fix33",
        "Status: committed report-first diagnostic",
        "Sensitivity: NON-SENSITIVE",
        "",
        "## Summary",
        "",
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
        "## Executor Profile Counts",
        "",
        "| Profile | Count |",
        "|---|---:|",
    ]
    for profile, count in summary["executor_profile_counts"].items():
        lines.append(f"| `{profile}` | `{count}` |")
    lines.extend(["", "## Gap Class Counts", "", "| Gap class | Count |", "|---|---:|"])
    for gap, count in gap_counts.items():
        lines.append(f"| `{gap}` | `{count}` |")
    lines.extend(["", "## Gap Examples", ""])
    for gap, paths in examples.items():
        lines.append(f"### `{gap}`")
        if not paths:
            lines.append("")
            lines.append("None recorded.")
        else:
            for item in paths:
                lines.append(f"- `{item}`")
        lines.append("")
    lines.extend(
        [
            "## Authority Trace Policy",
            "",
            "- Ordinary runtime unit tests do not require `REFERENCES_AUTHORITY`.",
            "- Role-specific authority traces are checked only for governance, ADR/CDL, phase/window, release, public-RC, Genesis, patent, or obligation-oriented tests.",
            "- Missing authority traces are report gaps only in this phase.",
            "",
            "## Non-Claims",
            "",
            "- No graph-selected tests were executed.",
            "- No function-level pytest collection was performed.",
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
        "graph_delta=support_only:docs/specs/ilc_test_graph_coverage_report_1545p_fix33_v0.1.md -> testing/homoiconic-test-graph-coverage"
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=None)
    parser.add_argument("--preferred-graph", type=Path, default=DEFAULT_PREFERRED_GRAPH)
    parser.add_argument("--fallback-graph", type=Path, default=DEFAULT_FALLBACK_GRAPH)
    parser.add_argument("--queue", action="append", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--enforce-threshold",
        action="store_true",
        help="Reserved opt-in gate. Not used by default in Phase 1545p-Fix33.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    graph_path, scope = select_graph(args.preferred_graph, args.fallback_graph, args.graph)
    graph = load_graph_index(graph_path, scope)
    policy = load_pytest_policy(repo_root / "tests/conftest.py", repo_root / "pyproject.toml")
    queue_paths = args.queue if args.queue is not None else list(DEFAULT_QUEUES)
    payload = build_coverage(repo_root, graph, policy, queue_paths)
    if args.enforce_threshold:
        payload["summary"]["enforce_threshold_requested"] = True
        payload["summary"]["enforce_threshold_effect"] = "no_threshold_ratified_report_only"
    else:
        payload["summary"]["enforce_threshold_requested"] = False
    canonical_dump(args.json_out, payload)
    write_report(args.report, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
