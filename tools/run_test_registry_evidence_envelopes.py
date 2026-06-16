#!/usr/bin/env python3
"""Run bounded pytest commands and emit canonical test evidence envelopes.

PUBLIC_RC_EXCLUDE: homoiconic_test_evidence_envelope_research_runner
PUBLIC_RC_EXCLUDE_REASON: Research-only local evidence rehearsal. Executes only
default-local pytest commands selected by Fix35, writes support evidence, and
does not mutate graph state, sign nodes, upload nodes, or activate runtime/public
RC paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_PLAN = Path("out/test_registry_sidecar_plan_1545p_fix35.json")
DEFAULT_JSON_OUT = Path("out/test_registry_evidence_envelopes_1545p_fix36.json")
DEFAULT_REPORT = Path(
    "docs/specs/ilc_test_registry_evidence_envelope_report_1545p_fix36_v0.1.md"
)
DEFAULT_PROFILE = "default_local_pytest"

OUTPUT_TOKENS = [
    "canonical_test_evidence_envelopes_committed_phase_1545p_fix36",
    "graph_resolved_pytest_execution_bounded_phase_1545p_fix36",
    "test_evidence_canonical_serialization_confirmed_phase_1545p_fix36",
    "test_evidence_no_authority_overclaim_phase_1545p_fix36",
    "pytest_execution_profiles_remained_default_local_phase_1545p_fix36",
    "public_path_remains_blocked_phase_1545p_fix36",
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
    "no_public_rc_activation",
    "no_runtime_activation",
    "no_adr_cdl_mutation",
]


class EvidenceError(ValueError):
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
        raise EvidenceError("invalid_command_shape")
    if command[0:3] != ["python", "-m", "pytest"] or command[-1] != "-q":
        raise EvidenceError("invalid_command_shape")
    pytest_nodeid = item.get("pytest_nodeid")
    if command[3] != pytest_nodeid:
        raise EvidenceError("command_pytest_nodeid_mismatch")
    if not isinstance(pytest_nodeid, str) or not pytest_nodeid.startswith("tests/") or "::" not in pytest_nodeid:
        raise EvidenceError("invalid_pytest_nodeid")
    if item.get("executor_profile") != DEFAULT_PROFILE:
        raise EvidenceError("non_default_profile_execution_forbidden")
    if item.get("environment_gates") not in ([], None):
        raise EvidenceError("environment_gated_execution_forbidden")
    repo_path = item.get("repo_path")
    if not isinstance(repo_path, str) or not repo_path.startswith("tests/"):
        raise EvidenceError("invalid_repo_path")
    if not (repo_root / repo_path).exists():
        raise EvidenceError(f"source_file_missing:{repo_path}")


def environment_profile_digest() -> tuple[dict[str, Any], str]:
    profile = {
        "duration_policy": "bounded_timeout_per_command",
        "executor_family": "pytest",
        "executor_profile": DEFAULT_PROFILE,
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
    repo_root: Path,
    plan_sha256: str,
    env_digest: str,
    timeout: int,
) -> dict[str, Any]:
    validate_command(item, repo_root)
    repo_path = str(item["repo_path"])
    source_path = repo_root / repo_path
    command = list(item["command"])
    exec_command = [sys.executable, "-m", "pytest", command[3], "-q"]
    completed = subprocess.run(
        exec_command,
        cwd=repo_root,
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
        "executor_profile": DEFAULT_PROFILE,
        "exit_code": completed.returncode,
        "graph_input_digest": plan_sha256,
        "node_id": item["node_id"],
        "non_claim_boundaries": NON_CLAIMS,
        "produced_edges": ["PRODUCES_EVIDENCE", "EVIDENCES"],
        "pytest_nodeid": item["pytest_nodeid"],
        "repo_path": repo_path,
        "result_status": result_status(completed.returncode),
        "source_digest_sha256": sha256_file(source_path),
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


def build_batch(plan_path: Path, repo_root: Path, limit: int, timeout: int) -> dict[str, Any]:
    plan = load_json(plan_path)
    if plan.get("phase") != "1545p-Fix35" or plan.get("status") != "pass":
        raise EvidenceError("fix35_plan_not_pass")
    if plan.get("execution_policy") != "execution_deferred_to_fix36_evidence_envelope":
        raise EvidenceError("fix35_plan_wrong_execution_policy")
    commands = plan.get("commands")
    if not isinstance(commands, list) or not commands:
        raise EvidenceError("fix35_plan_missing_commands")
    if limit < 1:
        raise EvidenceError("limit_must_be_positive")
    selected = commands[:limit]
    plan_sha = sha256_file(plan_path)
    env_profile, env_digest = environment_profile_digest()
    evidence_runs = [
        run_one(item, repo_root=repo_root, plan_sha256=plan_sha, env_digest=env_digest, timeout=timeout)
        for item in selected
    ]
    status_counts: dict[str, int] = {}
    for run in evidence_runs:
        status = str(run["result_status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    batch_body = {
        "environment_profile": env_profile,
        "evidence_runs": evidence_runs,
        "execution_scope": "bounded_default_local_pytest_from_fix35_plan",
        "fix35_plan_path": plan_path.as_posix(),
        "fix35_plan_sha256": plan_sha,
        "git_head": git_value(["rev-parse", "HEAD"], repo_root),
        "git_tree": git_value(["rev-parse", "HEAD^{tree}"], repo_root),
        "non_claims": NON_CLAIMS,
        "phase": "1545p-Fix36",
        "result_status_counts": dict(sorted(status_counts.items())),
        "selected_count": len(evidence_runs),
        "status": "pass" if status_counts == {"passed": len(evidence_runs)} else "fail",
        "timeout_seconds": timeout,
    }
    batch_id = "test_evidence_batch:" + sha256_bytes(canonical_bytes(batch_body))[:32]
    return {
        "batch_id": batch_id,
        **batch_body,
        "output_tokens": OUTPUT_TOKENS if batch_body["status"] == "pass" else [],
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "<!-- PUBLIC_RC_EXCLUDE: homoiconic_test_evidence_envelope_report_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Phase 1545p-Fix36 local evidence-envelope rehearsal; no graph mutation, signing, public RC activation, runtime activation, or governance mutation. -->",
        "",
        "# ILC Test Registry Evidence Envelope Report 1545p-Fix36 v0.1",
        "",
        "Phase: 1545p-Fix36",
        f"Status: {payload['status']}",
        "Sensitivity: NON-SENSITIVE",
        "",
        "## Summary",
        "",
        f"- Batch id: `{payload['batch_id']}`",
        f"- Execution scope: `{payload['execution_scope']}`",
        f"- Selected test commands: `{payload['selected_count']}`",
        f"- Result status counts: `{json.dumps(payload['result_status_counts'], sort_keys=True, separators=(',', ':'))}`",
        f"- Fix35 plan digest: `{payload['fix35_plan_sha256']}`",
        f"- Timeout seconds per command: `{payload['timeout_seconds']}`",
        "",
        "## Evidence Runs",
        "",
    ]
    for item in payload["evidence_runs"]:
        lines.append(
            f"- `{item['evidence_run_id']}` `{item['result_status']}` "
            f"`{item['pytest_nodeid']}` stdout=`{item['stdout_digest_sha256']}` "
            f"stderr=`{item['stderr_digest_sha256']}`"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Evidence is support evidence only.",
            "- Evidence does not grant authority, activation, eligibility, claimability, governance effect, or economic effect.",
            "- Only `default_local_pytest` commands without environment gates were executed.",
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
        "graph_delta=support_only:docs/specs/ilc_test_registry_evidence_envelope_report_1545p_fix36_v0.1.md -> testing/homoiconic-test-evidence"
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=60)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = build_batch(
            plan_path=args.plan,
            repo_root=args.repo_root.resolve(),
            limit=args.limit,
            timeout=args.timeout,
        )
    except (EvidenceError, subprocess.TimeoutExpired) as exc:
        failure = {
            "error": str(exc),
            "non_claims": NON_CLAIMS,
            "output_tokens": [],
            "phase": "1545p-Fix36",
            "status": "fail_closed",
        }
        atomic_canonical_write(args.json_out, failure)
        return 2
    atomic_canonical_write(args.json_out, payload)
    write_report(args.report, payload)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
