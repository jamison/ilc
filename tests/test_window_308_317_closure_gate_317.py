"""Phase 317 closure gate contract tests for window 308-317."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


GATE_PATH = Path("tools/check_window_308_317_closure_gate_phase_317.sh")
GATE_CMD = ["bash", str(GATE_PATH)]
HANDOFF_PATH = Path("docs/specs/ilc_window_308_317_handoff_317_v0.1.md")
SNAPSHOT_PATH = Path("out/monitoring/infrastructure_risk_snapshot_phase_316.json")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_317_COMMIT_SUBJECT = "docs(g8): phase 317 window 308-317 closure verification gate and 318+ handoff"


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
        timeout=300,
    )


def _snapshot_override_env(tmp_path: Path, verdict: str) -> tuple[dict[str, str], bytes | None]:
    payload = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    severity = payload.get("severity_summary")
    assert isinstance(severity, dict), "snapshot_missing_severity_summary"
    for key in ("s2_indicators", "s3_indicators", "verdict"):
        assert key in severity, f"snapshot_missing_severity_key:{key}"
    severity["verdict"] = verdict

    snapshot_copy = tmp_path / "snapshot_override.json"
    snapshot_copy.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    env = os.environ.copy()
    env["ILC_PHASE_317_SNAPSHOT_PATH"] = str(snapshot_copy)
    canonical = SNAPSHOT_PATH.read_bytes() if SNAPSHOT_PATH.exists() else None
    return env, canonical


def test_gate_script_exists() -> None:
    assert GATE_PATH.exists()


def test_gate_cli_contract_dry_run_help_alias_unknown_arg_and_exact_lines() -> None:
    help_result = _run_gate(["--help"])
    assert help_result.returncode == 0
    assert "Usage:" in help_result.stdout

    help_alias = _run_gate(["-h"])
    assert help_alias.returncode == 0
    assert "Usage:" in help_alias.stdout

    dry_run = _run_gate(["--dry-run"])
    assert dry_run.returncode == 0
    lines = [line.strip() for line in dry_run.stdout.splitlines() if line.strip()]
    assert lines == [
        "[1/6] prompt_contract_validation",
        "python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_317_g8_constitution_cluster_a_window_308_317_closure_verification_gate_and_318_plus_handoff.md",
        "[2/6] lane_contract_tests",
        "python3 -m pytest tests/test_phase_308_sequence_lock.py tests/test_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309.py tests/test_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311.py tests/test_epoch_snapshot_contract_and_cdl_023_evidence_prelock_313.py tests/test_infrastructure_economic_risk_monitoring_update_315.py -q",
        "[3/6] cross_phase_regression",
        "python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_mutation_canary_phase_297.py tests/test_d2_schema_baseline_runtime_310.py tests/test_genesis_state_bundle_runtime_312.py tests/test_epoch_snapshot_runtime_314.py tests/test_infrastructure_composed_preflight_316.py -q",
        "[4/6] mutation_canary",
        "python3 tools/run_mutation_canary_phase_297.py",
        "[5/6] closure_gate_cli_contract",
        "python3 -m pytest tests/test_window_308_317_closure_gate_317.py -q",
        "[6/6] walkthrough_hygiene",
        "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q",
    ]

    unknown = _run_gate(["--unknown-arg"])
    assert unknown.returncode == 2


def test_gate_full_run_exits_zero_on_pass_snapshot() -> None:
    if os.environ.get("ILC_PHASE_317_GATE_SELFTEST") == "1":
        pytest.skip("phase_317_selftest_context_skip_full_gate")
    result = _run_gate([])
    assert result.returncode == 0
    assert "phase_317_snapshot_gate=passed" in result.stdout
    assert "phase_317_verdict=pass" in result.stdout


def test_gate_full_run_enforces_conditional_exit_and_override_token(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_317_GATE_SELFTEST") == "1":
        pytest.skip("phase_317_selftest_context_skip_verdict_simulation")
    env, canonical = _snapshot_override_env(tmp_path, "conditional")
    result = _run_gate([], env=env)
    assert result.returncode == 3
    assert "phase_317_override_required=human" in result.stdout
    assert "phase_317_snapshot_gate=failed" in result.stdout
    if canonical is not None:
        assert SNAPSHOT_PATH.read_bytes() == canonical


def test_gate_full_run_enforces_blocked_exit_and_snapshot_isolation(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_317_GATE_SELFTEST") == "1":
        pytest.skip("phase_317_selftest_context_skip_verdict_simulation")
    env, canonical = _snapshot_override_env(tmp_path, "blocked")
    result = _run_gate([], env=env)
    assert result.returncode == 1
    assert "phase_317_snapshot_gate=failed" in result.stdout
    if canonical is not None:
        assert SNAPSHOT_PATH.read_bytes() == canonical


def test_handoff_exists_and_contains_required_sections_and_pointers() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")

    for heading in (
        "## 1. Window summary (308-317 completion state)",
        "## 2. Deliverable matrix for phases 309-316",
        "## 3. Closure-gate category evidence",
        "## 4. Phase-316 KPI snapshot carry-forward summary",
        "## 5. KPI provenance policy for closure interpretation",
        "## 6. Carry-forward risks and controls",
        "## 7. Hard prerequisites for phase 318+ opening",
        "## 8. Non-goals and boundary statement",
        "## 9. Canonical anchors and next-sequence pointer",
    ):
        assert heading in text

    for token in (
        "phase_316_snapshot",
        "release verdict",
        "no decision-log mutation",
        "no new `ilc_core/` runtime feature implementation",
        "measured",
        "derived",
        "not_applicable_in_preflight",
    ):
        assert token in text


def _resolve_phase_317_commit_ref() -> str:
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
        if subject.strip() == PHASE_317_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_317_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_317_GATE_SELFTEST") == "1":
        pytest.skip("phase_317_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_317_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_ilc_core_runtime_feature_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_317_GATE_SELFTEST") == "1":
        pytest.skip("phase_317_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_317_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_317_runtime_feature_mutations:{forbidden}"
