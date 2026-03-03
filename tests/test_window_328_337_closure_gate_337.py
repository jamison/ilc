"""Phase 337 closure gate contract tests for window 328-337."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest


GATE_PATH = Path("tools/check_window_328_337_closure_gate_phase_337.sh")
GATE_CMD = ["bash", str(GATE_PATH)]
HANDOFF_PATH = Path("docs/specs/ilc_window_328_337_handoff_337_v0.1.md")
SNAPSHOT_PATH = Path("out/monitoring/infrastructure_risk_snapshot_phase_316.json")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_337_COMMIT_SUBJECT = "docs(g8): phase 337 window 328-337 closure verification gate and 338+ handoff"


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(GATE_CMD + args, capture_output=True, text=True, env=env, check=False)


def _clean_full_run_env() -> dict[str, str]:
    blocked = {
        "ILC_PHASE_337_SNAPSHOT_PATH",
        "ILC_PHASE_316_SNAPSHOT_PATH",
        "ILC_PHASE_316_FORCE_VERDICT",
        "ILC_PHASE_337_GATE_SELFTEST",
        "ILC_PHASE_327_SNAPSHOT_PATH",
        "ILC_PHASE_327_GATE_SELFTEST",
        "ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE",
    }
    return {key: value for key, value in os.environ.items() if key not in blocked}


def _snapshot_override_env(tmp_path: Path, verdict: str) -> tuple[dict[str, str], bytes, int]:
    payload = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    severity = payload.get("severity_summary")
    assert isinstance(severity, dict), "snapshot_missing_severity_summary"
    for key in ("s2_indicators", "s3_indicators", "verdict"):
        assert key in severity, f"snapshot_missing_severity_key:{key}"
    severity["verdict"] = verdict

    snapshot_copy = tmp_path / f"snapshot_{verdict}.json"
    snapshot_copy.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    env = _clean_full_run_env()
    env["ILC_PHASE_337_SNAPSHOT_PATH"] = str(snapshot_copy)
    canonical_bytes = SNAPSHOT_PATH.read_bytes()
    canonical_mtime = SNAPSHOT_PATH.stat().st_mtime_ns
    return env, canonical_bytes, canonical_mtime


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_337_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_337_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(GATE_PATH),
        "tests/test_window_328_337_closure_gate_337.py",
        str(HANDOFF_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_337_commit_subject_present_but_no_qualifying_closure_commit")
    raise AssertionError("phase_337_commit_not_present_in_local_history")


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
        "python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_337_g8_constitution_cluster_a_window_328_337_closure_verification_gate_and_338_plus_handoff.md",
        "[2/6] lane_contract_tests",
        "python3 -m pytest tests/test_phase_328_sequence_lock.py tests/test_cdl_024_ratification_329.py tests/test_cdl_v1_ratification_330.py tests/test_cdl_v2_ratification_331.py tests/test_cdl_v3_ratification_332.py tests/test_cdl_v5_ratification_333.py tests/test_cdl_v4_v6_dual_ratification_334.py tests/test_cdl_v7_ratification_335.py tests/test_integration_coherence_336.py -q",
        "[3/6] cross_phase_regression",
        "python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_mutation_canary_phase_297.py tests/test_d2_schema_baseline_runtime_310.py tests/test_genesis_state_bundle_runtime_312.py tests/test_epoch_snapshot_runtime_314.py tests/test_infrastructure_economic_risk_monitoring_update_315.py tests/test_infrastructure_composed_preflight_316.py tests/test_wire_transport_runtime_323.py tests/test_window_318_327_closure_gate_327.py -q",
        "[4/6] mutation_canary",
        "python3 tools/run_mutation_canary_phase_297.py",
        "[5/6] closure_gate_cli_contract",
        "python3 -m pytest tests/test_window_328_337_closure_gate_337.py -q",
        "[6/6] walkthrough_hygiene",
        "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q",
    ]

    unknown = _run_gate(["--unknown-arg"])
    assert unknown.returncode == 2


def test_gate_full_run_exits_zero_on_pass_snapshot_and_preserves_canonical_snapshot() -> None:
    if os.environ.get("ILC_PHASE_337_GATE_SELFTEST") == "1":
        pytest.skip("phase_337_selftest_context_skip_full_gate")
    canonical_before = SNAPSHOT_PATH.read_bytes()
    canonical_mtime_before = SNAPSHOT_PATH.stat().st_mtime_ns
    env = _clean_full_run_env()
    env["ILC_PHASE_316_FORCE_VERDICT"] = "conditional"
    result = _run_gate([], env=env)
    assert result.returncode == 0
    assert "phase_337_snapshot_gate=passed" in result.stdout
    assert "phase_337_verdict=pass" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical_before
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime_before


def test_gate_full_run_enforces_conditional_exit_and_override_token(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_337_GATE_SELFTEST") == "1":
        pytest.skip("phase_337_selftest_context_skip_verdict_simulation")
    env, canonical, canonical_mtime = _snapshot_override_env(tmp_path, "conditional")
    result = _run_gate([], env=env)
    assert result.returncode == 3
    assert "phase_337_override_required=human" in result.stdout
    assert "phase_337_snapshot_gate=failed" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime


def test_gate_full_run_enforces_blocked_exit_and_snapshot_isolation(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_337_GATE_SELFTEST") == "1":
        pytest.skip("phase_337_selftest_context_skip_verdict_simulation")
    env, canonical, canonical_mtime = _snapshot_override_env(tmp_path, "blocked")
    result = _run_gate([], env=env)
    assert result.returncode == 1
    assert "phase_337_snapshot_gate=failed" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime


def test_handoff_exists_and_contains_required_sections_and_tokens() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")

    for heading in (
        "## 1. Window summary (328-337 completion state)",
        "## 2. Deliverable matrix for phases 329-336",
        "## 3. Closure-gate category evidence",
        "## 4. Phase-316 snapshot carry-forward summary",
        "## 5. Constitutional closure summary",
        "## 6. Evaluation-panel and governance carry-forward summary",
        "## 7. Carry-forward risks and controls",
        "## 8. Hard prerequisites for phase 338+ opening",
        "## 9. Non-goals and boundary statement",
        "## 10. Canonical anchors and next-sequence pointer",
    ):
        assert heading in text

    for token in (
        "phase_316_snapshot",
        "release verdict: pass",
        "CDL-024 and CDL-V1 through CDL-V7 are ratified",
        "CDL-021 remains open and milestone-triggered/deferred.",
        "only CDL-021 remains open",
        "panel_size=8",
        "independence_k=3",
        "outsider_seat=true",
        "Quorum: k=5 of m=7 reviewers with VRF-selected outsider seat",
        "trust-tier quorum ladder: L0=3, L1=5, L2=7, L3=9, appeals escalate by +2",
        "The quorum ladder L-tiers correspond to graph epistemic tiers, not protocol/genesis-layer authority tiers and not agent reputation tiers.",
        "L0=3 is architecturally safe because CDL-V7's Popperian gate ensures L0 basic statements are independently and directly verifiable.",
        "task outputs, decomposition validity, and ILC attribution",
        "This gap must be resolved before Window 338+ implementation begins.",
        "tests/test_infrastructure_composed_preflight_316.py",
        "any direct execution path requires immediate snapshot restore or override isolation",
        "git restore out/monitoring/infrastructure_risk_snapshot_phase_316.json",
        "docs/specs/ilc_antigravity_context_capsule_v0.8.md",
        "docs/specs/ilc_integration_coherence_report_336_v0.1.md",
        "no decision-log mutation",
        "no new `ilc_core/` runtime feature implementation",
    ):
        assert token in text


def test_no_decision_log_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_337_GATE_SELFTEST") == "1":
        pytest.skip("phase_337_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_337_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_no_ilc_core_runtime_feature_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_337_GATE_SELFTEST") == "1":
        pytest.skip("phase_337_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_337_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_337_runtime_feature_mutations:{forbidden}"
