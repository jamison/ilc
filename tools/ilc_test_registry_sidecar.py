#!/usr/bin/env python3
"""Local registry-mode pytest sidecar scaffold for Phase 1545p-Fix35.

PUBLIC_RC_EXCLUDE: homoiconic_test_registry_sidecar_research_scaffold
PUBLIC_RC_EXCLUDE_REASON: Research-only local sidecar scaffold. It resolves
candidate test_function nodes to pytest command plans, defaults to dry-run, and
does not execute tests, mutate graph state, sign nodes, or activate
runtime/public RC paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_FUNCTION_ARTIFACT = Path("out/test_function_nodes_1545p_fix34.json")
DEFAULT_DIGEST = Path(
    "docs/specs/ilc_pytest_function_node_collection_digest_1545p_fix34_v0.1.json"
)
DEFAULT_JSON_OUT = Path("out/test_registry_sidecar_plan_1545p_fix35.json")
DEFAULT_REPORT = Path(
    "docs/specs/ilc_test_registry_sidecar_scaffold_report_1545p_fix35_v0.1.md"
)

DEFAULT_PROFILE = "default_local_pytest"
KNOWN_PROFILES = {
    "default_local_pytest",
    "historical_phase_snapshot",
    "expensive_release_artifact",
    "sensitive_phase_selftest",
    "private_local_only",
    "live_network_vps_gated",
    "graph_hydrated_workspace",
}

OUTPUT_TOKENS = [
    "pytest_sidecar_registry_mode_scaffold_committed_phase_1545p_fix35",
    "graph_resolved_pytest_commands_recorded_phase_1545p_fix35",
    "pytest_sidecar_gate_enforcement_recorded_phase_1545p_fix35",
    "pytest_sidecar_default_dry_run_phase_1545p_fix35",
    "pytest_sidecar_execution_deferred_to_evidence_phase_1545p_fix35",
    "public_path_remains_blocked_phase_1545p_fix35",
]


class SidecarError(ValueError):
    pass


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


def load_function_nodes(function_artifact: Path, digest_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if function_artifact.exists():
        data = json.loads(function_artifact.read_text(encoding="utf-8"))
        nodes = data.get("test_function_nodes")
        if not isinstance(nodes, list):
            raise SidecarError("function_artifact_missing_test_function_nodes")
        return nodes, {
            "function_input_scope": "full_function_artifact",
            "function_input_path": function_artifact.as_posix(),
            "function_input_sha256": sha256_file(function_artifact),
            "function_input_size_bytes": function_artifact.stat().st_size,
            "fix34_summary": data.get("summary", {}),
        }

    if digest_path.exists():
        data = json.loads(digest_path.read_text(encoding="utf-8"))
        nodes = data.get("sample_test_function_nodes")
        if not isinstance(nodes, list):
            raise SidecarError("digest_missing_sample_test_function_nodes")
        return nodes, {
            "function_input_scope": "digest_sample_fallback",
            "function_input_path": digest_path.as_posix(),
            "function_input_sha256": sha256_file(digest_path),
            "function_input_size_bytes": digest_path.stat().st_size,
            "fix34_summary": data.get("summary", {}),
        }

    raise SidecarError("no_function_artifact_or_digest_available")


def select_candidates(
    nodes: list[dict[str, Any]],
    repo_root: Path,
    profile: str,
    target: str | None,
    repo_path: str | None,
    limit: int,
    allow_gated_profile: bool,
    allow_env_gates: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if profile not in KNOWN_PROFILES:
        raise SidecarError(f"unknown_executor_profile:{profile}")
    if profile != DEFAULT_PROFILE and not allow_gated_profile:
        raise SidecarError(f"gated_profile_requires_explicit_allow:{profile}")
    if limit < 1:
        raise SidecarError("limit_must_be_positive")

    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    sorted_nodes = sorted(nodes, key=lambda n: (str(n.get("pytest_nodeid", "")), str(n.get("node_id", ""))))

    for node in sorted_nodes:
        node_id = str(node.get("node_id", ""))
        node_pytest_id = str(node.get("pytest_nodeid", ""))
        node_repo_path = str(node.get("repo_path", ""))
        if target and node_id != target:
            continue
        if repo_path and node_repo_path != repo_path:
            continue
        profiles = set(str(item) for item in node.get("executor_profiles", []))
        env_gates = [str(item) for item in node.get("environment_gates", [])]
        if profile not in profiles:
            rejected.append(rejection(node, "profile_not_present_on_node"))
            continue
        if env_gates and not allow_env_gates:
            rejected.append(rejection(node, "environment_gate_requires_explicit_allow"))
            continue
        if not node_pytest_id.startswith("tests/") or "::" not in node_pytest_id:
            rejected.append(rejection(node, "invalid_pytest_nodeid"))
            continue
        local_path = repo_root / node_repo_path
        if not local_path.exists():
            rejected.append(rejection(node, "local_source_file_missing"))
            continue
        selected.append(node)
        if len(selected) >= limit:
            break

    if target and not selected:
        target_seen = any(str(node.get("node_id", "")) == target for node in nodes)
        reason = "target_rejected_by_gates" if target_seen else "target_not_found"
        raise SidecarError(f"{reason}:{target}")
    if not selected:
        raise SidecarError("no_nodes_selected_under_requested_profile")
    return selected, rejected


def rejection(node: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "node_id": node.get("node_id"),
        "pytest_nodeid": node.get("pytest_nodeid"),
        "repo_path": node.get("repo_path"),
        "reason": reason,
    }


def build_plan(
    repo_root: Path,
    function_artifact: Path,
    digest_path: Path,
    profile: str,
    target: str | None,
    repo_path: str | None,
    limit: int,
    dry_run: bool,
    execute: bool,
    allow_gated_profile: bool,
    allow_env_gates: bool,
) -> dict[str, Any]:
    if execute:
        raise SidecarError("execution_deferred_to_fix36_evidence_envelope")
    if not dry_run:
        raise SidecarError("dry_run_required_in_phase_1545p_fix35")

    nodes, input_meta = load_function_nodes(function_artifact, digest_path)
    selected, rejected = select_candidates(
        nodes=nodes,
        repo_root=repo_root,
        profile=profile,
        target=target,
        repo_path=repo_path,
        limit=limit,
        allow_gated_profile=allow_gated_profile,
        allow_env_gates=allow_env_gates,
    )
    commands = []
    profile_counts: Counter[str] = Counter()
    gate_counts: Counter[str] = Counter()
    for node in selected:
        for node_profile in node.get("executor_profiles", []):
            profile_counts[str(node_profile)] += 1
        for gate in node.get("environment_gates", []):
            gate_counts[str(gate)] += 1
        commands.append(
            {
                "node_id": node["node_id"],
                "pytest_nodeid": node["pytest_nodeid"],
                "repo_path": node["repo_path"],
                "command": ["python", "-m", "pytest", node["pytest_nodeid"], "-q"],
                "executor_profile": profile,
                "dry_run": True,
                "environment_gates": node.get("environment_gates", []),
                "source_file_exists": True,
            }
        )

    return {
        "phase": "1545p-Fix35",
        "status": "pass",
        "sidecar_mode": "registry_mode_pytest_dry_run",
        "default_dry_run": True,
        "execute_requested": False,
        "execution_policy": "execution_deferred_to_fix36_evidence_envelope",
        "selection": {
            "profile": profile,
            "target": target,
            "repo_path": repo_path,
            "limit": limit,
            "allow_gated_profile": allow_gated_profile,
            "allow_env_gates": allow_env_gates,
        },
        "input": input_meta,
        "selected_count": len(selected),
        "rejected_count_before_limit": len(rejected),
        "selected_profile_counts": dict(sorted(profile_counts.items())),
        "selected_environment_gate_counts": dict(sorted(gate_counts.items())),
        "commands": commands,
        "rejections_sample": rejected[:25],
        "output_tokens": OUTPUT_TOKENS,
        "non_claims": [
            "no_test_execution",
            "no_evidence_envelope_generation",
            "no_graph_mutation",
            "no_edge_promotion",
            "no_canonical_atlas_mutation",
            "no_genesis_signing",
            "no_node_upload",
            "no_public_rc_activation",
            "no_runtime_activation",
            "no_adr_cdl_mutation",
        ],
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "<!-- PUBLIC_RC_EXCLUDE: homoiconic_test_registry_sidecar_report_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Phase 1545p-Fix35 dry-run sidecar report; no test execution, evidence envelope, graph mutation, signing, public RC activation, or runtime activation. -->",
        "",
        "# ILC Test Registry Sidecar Scaffold Report 1545p-Fix35 v0.1",
        "",
        "Phase: 1545p-Fix35",
        "Status: committed dry-run scaffold",
        "Sensitivity: NON-SENSITIVE",
        "",
        "## Summary",
        "",
        f"- Sidecar mode: `{payload['sidecar_mode']}`",
        f"- Function input scope: `{payload['input']['function_input_scope']}`",
        f"- Function input path: `{payload['input']['function_input_path']}`",
        f"- Executor profile: `{payload['selection']['profile']}`",
        f"- Selected commands: `{payload['selected_count']}`",
        f"- Rejected before limit: `{payload['rejected_count_before_limit']}`",
        f"- Execution policy: `{payload['execution_policy']}`",
        "",
        "## Dry-Run Commands",
        "",
    ]
    for item in payload["commands"]:
        lines.append(f"- `{item['node_id']}` -> `{' '.join(item['command'])}`")
    lines.extend(
        [
            "",
            "## Gate Policy",
            "",
            "- Default profile is `default_local_pytest`.",
            "- Non-default profiles require explicit gated-profile acknowledgement.",
            "- Environment-gated nodes require explicit environment-gate acknowledgement.",
            "- `--execute` fails closed in Fix35 and is routed to Fix36 evidence-envelope work.",
            "",
            "## Non-Claims",
            "",
            "- No tests were executed.",
            "- No evidence envelope was generated.",
            "- No canonical Atlas mutation occurred.",
            "- No edge promotion occurred.",
            "- No Genesis signing occurred.",
            "- No node upload occurred.",
            "- No public graph publication occurred.",
            "- No public repository push occurred.",
            "- No public RC activation occurred.",
            "- No runtime, economic, sidecar activation, ADR, or CDL mutation occurred.",
            "",
            "## Output Tokens",
            "",
        ]
    )
    for token in OUTPUT_TOKENS:
        lines.append(f"- `{token}`")
    lines.append("")
    lines.append(
        "graph_delta=support_only:docs/specs/ilc_test_registry_sidecar_scaffold_report_1545p_fix35_v0.1.md -> testing/homoiconic-test-registry-sidecar"
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="Resolve test_function candidates to pytest commands")
    run.add_argument("--function-artifact", type=Path, default=DEFAULT_FUNCTION_ARTIFACT)
    run.add_argument("--digest", type=Path, default=DEFAULT_DIGEST)
    run.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    run.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    run.add_argument("--repo-root", type=Path, default=Path("."))
    run.add_argument("--profile", default=DEFAULT_PROFILE)
    run.add_argument("--target", default=None)
    run.add_argument("--repo-path", default=None)
    run.add_argument("--limit", type=int, default=8)
    run.add_argument("--dry-run", action="store_true", default=True)
    run.add_argument("--execute", action="store_true")
    run.add_argument("--allow-gated-profile", action="store_true")
    run.add_argument("--allow-env-gates", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = build_plan(
            repo_root=args.repo_root.resolve(),
            function_artifact=args.function_artifact,
            digest_path=args.digest,
            profile=args.profile,
            target=args.target,
            repo_path=args.repo_path,
            limit=args.limit,
            dry_run=args.dry_run,
            execute=args.execute,
            allow_gated_profile=args.allow_gated_profile,
            allow_env_gates=args.allow_env_gates,
        )
    except SidecarError as exc:
        failure = {
            "phase": "1545p-Fix35",
            "status": "fail_closed",
            "error": str(exc),
            "output_tokens": [],
            "non_claims": ["no_test_execution", "no_evidence_envelope_generation"],
        }
        canonical_dump(args.json_out, failure)
        return 2
    canonical_dump(args.json_out, payload)
    write_report(args.report, payload)
    for item in payload["commands"]:
        print(" ".join(item["command"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
