#!/usr/bin/env python3
"""Hydrate a bounded test workspace and emit canonical evidence envelopes.

PUBLIC_RC_EXCLUDE: homoiconic_test_graph_hydrated_workspace_research_runner
PUBLIC_RC_EXCLUDE_REASON: Research-only local graph/source-tree hydration
rehearsal. Executes only default-local pytest commands selected by Fix35 after
copying and verifying a bounded source slice; does not mutate graph state, sign
nodes, upload nodes, serve graph content, or activate runtime/public RC paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_PLAN = Path("out/test_registry_sidecar_plan_1545p_fix35.json")
DEFAULT_JSON_OUT = Path("out/test_registry_hydrated_workspace_1545p_fix37.json")
DEFAULT_REPORT = Path(
    "docs/specs/ilc_test_registry_hydrated_workspace_report_1545p_fix37_v0.1.md"
)
DEFAULT_PROFILE = "default_local_pytest"
DEFAULT_LIMIT = 8

OUTPUT_TOKENS = [
    "pytest_sidecar_graph_hydrated_workspace_committed_phase_1545p_fix37",
    "hydrated_workspace_digest_verification_recorded_phase_1545p_fix37",
    "graph_hydrated_pytest_execution_bounded_phase_1545p_fix37",
    "pytest_sidecar_hydration_limits_recorded_phase_1545p_fix37",
    "graph_hydrated_evidence_no_authority_overclaim_phase_1545p_fix37",
    "public_path_remains_blocked_phase_1545p_fix37",
]

NON_CLAIMS = [
    "test_evidence_is_not_authority",
    "test_evidence_does_not_grant_activation",
    "test_evidence_does_not_grant_eligibility",
    "test_evidence_does_not_grant_claimability",
    "test_evidence_does_not_grant_governance_effect",
    "test_evidence_does_not_grant_economic_effect",
    "no_graph_mutation",
    "no_edge_promotion",
    "no_canonical_atlas_mutation",
    "no_genesis_signing",
    "no_node_upload",
    "no_public_graph_serving",
    "no_public_rc_activation",
    "no_runtime_activation",
    "no_sidecar_activation",
    "no_adr_cdl_mutation",
]

PATH_LITERAL_RE = re.compile(r"Path\([\"']([^\"']+)[\"']\)")
GIT_HISTORY_NODEID_FRAGMENTS = (
    "::test_no_decision_log_mutation_in_phase_354_commit",
    "::test_no_ilc_core_runtime_mutation_in_phase_354_commit",
)


class HydrationError(ValueError):
    pass


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def atomic_canonical_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(canonical_bytes(payload))
            handle.write(b"\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_value(args: list[str], repo_root: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def validate_command(item: dict[str, Any], repo_root: Path) -> None:
    command = item.get("command")
    if not isinstance(command, list) or len(command) != 5:
        raise HydrationError("invalid_command_shape")
    if command[0:3] != ["python", "-m", "pytest"] or command[-1] != "-q":
        raise HydrationError("invalid_command_shape")
    pytest_nodeid = item.get("pytest_nodeid")
    if command[3] != pytest_nodeid:
        raise HydrationError("command_pytest_nodeid_mismatch")
    if not isinstance(pytest_nodeid, str) or not pytest_nodeid.startswith("tests/") or "::" not in pytest_nodeid:
        raise HydrationError("invalid_pytest_nodeid")
    if item.get("executor_profile") != DEFAULT_PROFILE:
        raise HydrationError("non_default_profile_execution_forbidden")
    if item.get("environment_gates") not in ([], None):
        raise HydrationError("environment_gated_execution_forbidden")
    repo_path = item.get("repo_path")
    if not isinstance(repo_path, str) or not repo_path.startswith("tests/"):
        raise HydrationError("invalid_repo_path")
    if not (repo_root / repo_path).is_file():
        raise HydrationError(f"source_file_missing:{repo_path}")


def requires_git_history(item: dict[str, Any]) -> bool:
    nodeid = str(item.get("pytest_nodeid", ""))
    return any(fragment in nodeid for fragment in GIT_HISTORY_NODEID_FRAGMENTS)


def split_commands(
    commands: list[dict[str, Any]],
    repo_root: Path,
    limit: int,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    selected: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    for item in commands[:limit]:
        validate_command(item, repo_root)
        if requires_git_history(item):
            excluded.append(
                {
                    "pytest_nodeid": str(item["pytest_nodeid"]),
                    "reason": "requires_git_history_not_hydrated",
                }
            )
            continue
        selected.append(item)
    if not selected:
        raise HydrationError("no_hydratable_default_local_commands")
    return selected, excluded


def discover_path_literals(source_text: str, repo_root: Path) -> set[str]:
    paths: set[str] = set()
    for match in PATH_LITERAL_RE.finditer(source_text):
        candidate = match.group(1)
        if candidate.startswith(("/", "../", "./.git", ".git")):
            continue
        candidate_path = repo_root / candidate
        if candidate_path.is_file():
            paths.add(candidate)
    return paths


def build_source_manifest(
    selected: list[dict[str, Any]],
    repo_root: Path,
) -> tuple[list[dict[str, Any]], str]:
    paths: set[str] = {"pyproject.toml", "conftest.py", "tests/conftest.py"}
    for item in selected:
        repo_path = str(item["repo_path"])
        paths.add(repo_path)
        source_text = (repo_root / repo_path).read_text(encoding="utf-8")
        paths.update(discover_path_literals(source_text, repo_root))

    manifest: list[dict[str, Any]] = []
    for repo_path in sorted(paths):
        path = repo_root / repo_path
        if not path.is_file():
            raise HydrationError(f"manifest_source_missing:{repo_path}")
        manifest.append(
            {
                "repo_path": repo_path,
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return manifest, sha256_bytes(canonical_bytes(manifest))


def hydrate_workspace(
    manifest: list[dict[str, Any]],
    repo_root: Path,
    workspace_root: Path,
) -> list[dict[str, Any]]:
    verified: list[dict[str, Any]] = []
    for entry in manifest:
        repo_path = str(entry["repo_path"])
        source = repo_root / repo_path
        target = workspace_root / repo_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        source_digest = str(entry["sha256"])
        hydrated_digest = sha256_file(target)
        if hydrated_digest != source_digest:
            raise HydrationError(f"hydrated_digest_mismatch:{repo_path}")
        verified.append(
            {
                "repo_path": repo_path,
                "sha256": hydrated_digest,
                "verified": True,
            }
        )
    return verified


def environment_profile_digest() -> tuple[dict[str, Any], str]:
    profile = {
        "duration_policy": "bounded_timeout_per_command",
        "executor_family": "pytest",
        "executor_profile": "graph_hydrated_workspace_local",
        "hydration_mode": "bounded_plan_derived_source_tree_slice",
        "pytest_invocation": ["python", "-m", "pytest", "<nodeid>", "-q"],
        "python_version": sys.version.split()[0],
        "wall_clock_protocol_semantics": False,
    }
    return profile, sha256_bytes(canonical_bytes(profile))


def result_status(returncode: int) -> str:
    if returncode == 0:
        return "passed"
    if returncode == 1:
        return "failed"
    if returncode == 5:
        return "no_tests_collected"
    return "error"


def run_one(
    item: dict[str, Any],
    workspace_root: Path,
    source_manifest_digest: str,
    plan_sha256: str,
    env_digest: str,
    timeout: int,
) -> dict[str, Any]:
    repo_path = str(item["repo_path"])
    workspace_source_path = workspace_root / repo_path
    command = list(item["command"])
    exec_command = [sys.executable, "-m", "pytest", command[3], "-q"]
    completed = subprocess.run(
        exec_command,
        cwd=workspace_root,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    stdout = completed.stdout or b""
    stderr = completed.stderr or b""
    envelope_body = {
        "command": command,
        "duration_bucket": "bounded_under_timeout",
        "environment_profile_digest": env_digest,
        "evidence_kind": "test_evidence_run",
        "executor_profile": "graph_hydrated_workspace_local",
        "exit_code": completed.returncode,
        "graph_input_digest": plan_sha256,
        "hydration_mode": "bounded_plan_derived_source_tree_slice",
        "node_id": item["node_id"],
        "non_claim_boundaries": NON_CLAIMS,
        "produced_edges": ["PRODUCES_EVIDENCE", "EVIDENCES"],
        "pytest_nodeid": item["pytest_nodeid"],
        "repo_path": repo_path,
        "result_status": result_status(completed.returncode),
        "source_digest_sha256": sha256_file(workspace_source_path),
        "source_tree_manifest_digest": source_manifest_digest,
        "stderr_digest_sha256": sha256_bytes(stderr),
        "stderr_size_bytes": len(stderr),
        "stdout_digest_sha256": sha256_bytes(stdout),
        "stdout_size_bytes": len(stdout),
        "timeout_seconds": timeout,
        "wall_clock_protocol_semantics": False,
    }
    envelope_id = "test_evidence_run:" + sha256_bytes(canonical_bytes(envelope_body))[:32]
    return {
        "evidence_run_id": envelope_id,
        **envelope_body,
    }


def build_batch(
    plan_path: Path,
    repo_root: Path,
    limit: int,
    timeout: int,
    keep_workspace: bool,
) -> dict[str, Any]:
    plan = load_json(plan_path)
    if plan.get("phase") != "1545p-Fix35" or plan.get("status") != "pass":
        raise HydrationError("fix35_plan_not_pass")
    if plan.get("execution_policy") != "execution_deferred_to_fix36_evidence_envelope":
        raise HydrationError("fix35_plan_wrong_execution_policy")
    commands = plan.get("commands")
    if not isinstance(commands, list) or not commands:
        raise HydrationError("fix35_plan_missing_commands")
    if limit < 1:
        raise HydrationError("limit_must_be_positive")

    selected, excluded = split_commands(commands, repo_root=repo_root, limit=limit)
    manifest, manifest_digest = build_source_manifest(selected, repo_root=repo_root)
    plan_sha = sha256_file(plan_path)
    env_profile, env_digest = environment_profile_digest()

    temp_dir: tempfile.TemporaryDirectory | None = None
    if keep_workspace:
        workspace_path = Path(tempfile.mkdtemp(prefix="ilc_fix37_hydrated_workspace_"))
        workspace_persistence = "retained_for_operator_inspection"
    else:
        temp_dir = tempfile.TemporaryDirectory(prefix="ilc_fix37_hydrated_workspace_")
        workspace_path = Path(temp_dir.name)
        workspace_persistence = "deleted_after_run"
    try:
        verified_files = hydrate_workspace(manifest, repo_root=repo_root, workspace_root=workspace_path)
        evidence_runs = [
            run_one(
                item,
                workspace_root=workspace_path,
                source_manifest_digest=manifest_digest,
                plan_sha256=plan_sha,
                env_digest=env_digest,
                timeout=timeout,
            )
            for item in selected
        ]
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()

    status_counts: dict[str, int] = {}
    for run in evidence_runs:
        status = str(run["result_status"])
        status_counts[status] = status_counts.get(status, 0) + 1

    batch_body = {
        "environment_profile": env_profile,
        "evidence_runs": evidence_runs,
        "excluded_commands": excluded,
        "excluded_count": len(excluded),
        "execution_scope": "bounded_graph_hydrated_workspace_from_fix35_plan",
        "fix35_plan_path": plan_path.as_posix(),
        "fix35_plan_sha256": plan_sha,
        "git_head": git_value(["rev-parse", "HEAD"], repo_root),
        "hydrated_file_count": len(verified_files),
        "hydrated_files": verified_files,
        "hydration_limitations": [
            "git_history_not_hydrated",
            "compiled_dependencies_not_hydrated",
            "private_material_not_hydrated",
            "live_network_not_hydrated",
        ],
        "non_claims": NON_CLAIMS,
        "phase": "1545p-Fix37",
        "result_status_counts": dict(sorted(status_counts.items())),
        "selected_count": len(evidence_runs),
        "source_manifest": manifest,
        "source_tree_manifest_digest": manifest_digest,
        "status": "pass" if status_counts == {"passed": len(evidence_runs)} else "fail",
        "timeout_seconds": timeout,
        "workspace_path": str(workspace_path) if keep_workspace else None,
        "workspace_persistence": workspace_persistence,
    }
    batch_id = "test_hydrated_workspace_batch:" + sha256_bytes(canonical_bytes(batch_body))[:32]
    return {
        "batch_id": batch_id,
        **batch_body,
        "output_tokens": OUTPUT_TOKENS if batch_body["status"] == "pass" else [],
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "<!-- PUBLIC_RC_EXCLUDE: homoiconic_test_hydrated_workspace_report_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Phase 1545p-Fix37 local graph-hydrated workspace rehearsal; no graph mutation, signing, public RC activation, runtime activation, or governance mutation. -->",
        "",
        "# ILC Test Registry Graph-Hydrated Workspace Report 1545p-Fix37 v0.1",
        "",
        "Phase: 1545p-Fix37",
        f"Status: {payload['status']}",
        "Sensitivity: NON-SENSITIVE",
        "",
        "## Summary",
        "",
        f"- Batch id: `{payload['batch_id']}`",
        f"- Execution scope: `{payload['execution_scope']}`",
        f"- Selected hydrated commands: `{payload['selected_count']}`",
        f"- Excluded commands: `{payload['excluded_count']}`",
        f"- Hydrated file count: `{payload['hydrated_file_count']}`",
        f"- Result status counts: `{json.dumps(payload['result_status_counts'], sort_keys=True, separators=(',', ':'))}`",
        f"- Source-tree manifest digest: `{payload['source_tree_manifest_digest']}`",
        f"- Workspace persistence: `{payload['workspace_persistence']}`",
        "",
        "## Excluded Commands",
        "",
    ]
    if payload["excluded_commands"]:
        for item in payload["excluded_commands"]:
            lines.append(f"- `{item['pytest_nodeid']}` reason=`{item['reason']}`")
    else:
        lines.append("- None")
    lines.extend(["", "## Evidence Runs", ""])
    for item in payload["evidence_runs"]:
        lines.append(
            f"- `{item['evidence_run_id']}` `{item['result_status']}` "
            f"`{item['pytest_nodeid']}` stdout=`{item['stdout_digest_sha256']}` "
            f"stderr=`{item['stderr_digest_sha256']}`"
        )
    lines.extend(
        [
            "",
            "## Hydration Limits",
            "",
            "- Git history was not hydrated; git-history-dependent tests were excluded.",
            "- Compiled dependencies, private material, and live-network material were not hydrated.",
            "- The source slice was plan-derived and bounded; this was not a full graph workspace.",
            "",
            "## Boundary",
            "",
            "- Evidence is support evidence only.",
            "- Evidence does not grant authority, activation, eligibility, claimability, governance effect, or economic effect.",
            "- Only graph-hydrated local workspace commands derived from `default_local_pytest` plan entries were executed.",
            "- No graph mutation, edge promotion, signing, upload, publication, runtime activation, sidecar activation, ADR mutation, or CDL mutation occurred.",
            "",
            "## Output Tokens",
            "",
        ]
    )
    for token in payload.get("output_tokens", []):
        lines.append(f"- `{token}`")
    lines.append("")
    lines.append(
        "graph_delta=support_only:docs/specs/ilc_test_registry_hydrated_workspace_report_1545p_fix37_v0.1.md -> testing/homoiconic-test-hydrated-workspace"
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--keep-workspace", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = build_batch(
            plan_path=args.plan,
            repo_root=args.repo_root.resolve(),
            limit=args.limit,
            timeout=args.timeout,
            keep_workspace=args.keep_workspace,
        )
    except (HydrationError, subprocess.TimeoutExpired) as exc:
        failure = {
            "error": str(exc),
            "non_claims": NON_CLAIMS,
            "output_tokens": [],
            "phase": "1545p-Fix37",
            "status": "fail_closed",
        }
        atomic_canonical_write(args.json_out, failure)
        return 2
    atomic_canonical_write(args.json_out, payload)
    write_report(args.report, payload)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
