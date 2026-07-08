"""Phase 306 tests for composed query/verify/bundle preflight runner."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import hashlib
from pathlib import Path
from typing import Any


GATE_CMD = ["bash", "tools/check_d2e_composed_preflight_phase_306.sh"]
CLI_CMD = [sys.executable, "-m", "ilc_core.cli.main"]
SNAPSHOT_PATH = Path("out/monitoring/d2e_risk_snapshot_phase_306.json")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_306_COMMIT_SUBJECT = "feat(g8): phase 306 d2e composed query-verify-bundle integration preflight"


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    gate_env = os.environ.copy()
    if env is not None:
        gate_env.update(env)
    gate_env["PYTHON"] = sys.executable
    return subprocess.run(
        GATE_CMD + args,
        capture_output=True,
        text=True,
        env=gate_env,
        check=False,
        timeout=120,
    )


def _run_cli(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(CLI_CMD + args, capture_output=True, text=True, env=env, check=False)


def _payload(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    blob = result.stdout.strip() or result.stderr.strip()
    assert blob, "expected_json_payload"
    return json.loads(blob)


def _write_graph_state(path: Path) -> None:
    state = {
        "schema_version": "d2e03.v0.1",
        "nodes": [{"id": "node-1", "claim_id": "claim-a", "payload": {"text": "alpha"}}],
        "edges": [],
        "epochs": [{"epoch": 9}],
    }
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _manifest_hash(manifest: dict[str, Any]) -> str:
    stable = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def _write_bundle_state(path: Path) -> None:
    manifest = {
        "bundle_version": "v1",
        "entries": [{"cid": "node-1", "kind": "knowledge_node"}],
        "name": "demo-bundle",
    }
    state = {
        "schema_version": "d2e07.v0.1",
        "bundles": [
            {
                "bundle_cid": "bafy-bundle-1",
                "provider": "local",
                "manifest": manifest,
                "integrity": {"manifest_sha256": _manifest_hash(manifest)},
                "graph_refs": {"node_ids": ["node-1"], "claim_ids": ["claim-a"]},
            }
        ],
    }
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_identity_state(path: Path) -> None:
    state = {
        "lineage_id": "lineage-a",
        "status": "active",
        "key_ref": "key-a",
        "rotation_count": 0,
        "updated_at": "2026-02-25T00:00:00Z",
    }
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_gate_cli_contract_dry_run_help_unknown_arg() -> None:
    help_result = _run_gate(["--help"])
    assert help_result.returncode == 0
    assert "Usage:" in help_result.stdout

    dry_run = _run_gate(["--dry-run"])
    assert dry_run.returncode == 0
    lines = [line.strip() for line in dry_run.stdout.splitlines() if line.strip()]
    assert lines == [
        "[1/5] query_lane_scenarios",
        "[2/5] verify_lane_scenarios",
        "[3/5] bundle_lane_scenarios",
        "[4/5] cross_lane_envelope_regression",
        "[5/5] kpi_snapshot",
    ]

    unknown = _run_gate(["--unknown-arg"])
    assert unknown.returncode == 2


def test_gate_full_run_emits_snapshot_and_allowed_verdict() -> None:
    result = _run_gate([])
    assert result.returncode == 0
    assert SNAPSHOT_PATH.exists()

    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    assert snapshot["phase"] == "306"
    assert snapshot["preflight_scope"] is True
    assert snapshot["generated_at"].endswith("Z")
    counts = snapshot["lane_request_counts"]
    assert set(counts.keys()) == {"query", "verify", "bundle"}
    for lane in ("query", "verify", "bundle"):
        assert isinstance(counts[lane], int)
        assert counts[lane] > 0
    assert counts["query"] >= 25
    assert counts["verify"] >= 25
    assert counts["bundle"] >= 120

    kpis = snapshot["kpis"]
    expected_kpi_keys = {
        "kpi_query_invalid_input_rate",
        "kpi_query_not_found_rate",
        "kpi_query_backend_unavailable_rate",
        "kpi_query_p95_latency_ms",
        "kpi_verify_invalid_input_rate",
        "kpi_verify_not_found_rate",
        "kpi_verify_backend_unavailable_rate",
        "kpi_verify_check_failure_ratio",
        "kpi_bundle_invalid_input_rate",
        "kpi_bundle_not_found_rate",
        "kpi_bundle_manifest_invalid_rate",
        "kpi_bundle_provider_blocked_rate",
        "kpi_bundle_backend_unavailable_rate",
        "kpi_bundle_validate_local_ref_missing_rate",
        "kpi_d2e_success_ratio",
        "kpi_d2e_median_latency_ms",
        "kpi_out_of_scope_file_mutation_count",
        "kpi_missing_evidence_anchor_count",
        "kpi_non_target_guardrail_failure_count",
        "kpi_local_state_path_failure_rate",
        "kpi_provider_blocked_recovery_ratio",
        "kpi_runbook_recency_days",
        "kpi_utility_framing_coverage",
        "kpi_macro_hedge_claim_incidents",
        "kpi_vendor_lock_language_incidents",
    }
    assert set(kpis.keys()) == expected_kpi_keys
    assert kpis["kpi_bundle_validate_local_ref_missing_rate"] > 0.0
    assert kpis["kpi_provider_blocked_recovery_ratio"] == 0.0

    severity = snapshot["severity_summary"]
    assert severity["verdict"] in {"pass", "conditional", "blocked"}
    assert set(severity.keys()) == {"s1_indicators", "s2_indicators", "s3_indicators", "verdict"}
    if severity["s3_indicators"]:
        assert severity["verdict"] == "blocked"
    elif severity["s2_indicators"]:
        assert severity["verdict"] == "conditional"
    else:
        assert severity["verdict"] == "pass"


def test_subprocess_regression_query_verify_bundle_identity_envelopes(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    bundle_path = tmp_path / "bundle.json"
    identity_path = tmp_path / "identity.json"
    _write_graph_state(graph_path)
    _write_bundle_state(bundle_path)
    _write_identity_state(identity_path)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_BUNDLE_STATE_PATH"] = str(bundle_path)
    env["ILC_IDENTITY_STATE_PATH"] = str(identity_path)

    query = _run_cli(["query", "node", "--node-id", "node-1"], env)
    assert query.returncode == 0
    query_payload = _payload(query)
    assert query_payload["meta"]["schema_version"] == "299.v0.1"

    verify = _run_cli(["verify", "claim", "--claim-id", "claim-a"], env)
    assert verify.returncode == 0
    verify_payload = _payload(verify)
    assert verify_payload["meta"]["schema_version"] == "301.v0.1"

    bundle = _run_cli(["bundle", "inspect", "--bundle-cid", "bafy-bundle-1"], env)
    assert bundle.returncode == 0
    bundle_payload = _payload(bundle)
    assert bundle_payload["meta"]["schema_version"] == "303.v0.1"

    identity = _run_cli(["identity", "show"], env)
    assert identity.returncode == 0
    identity_payload = _payload(identity)
    assert identity_payload["schema_version"] == "254.v0.1"
    assert "meta" not in identity_payload


def _resolve_phase_306_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_306_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_306_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_306_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_consensus_or_security_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_306_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    forbidden = [
        path
        for path in changed
        if path.startswith("ilc_core/consensus/") or path.startswith("ilc_core/security/")
    ]
    assert not forbidden, f"phase_306_forbidden_runtime_mutations:{forbidden}"
