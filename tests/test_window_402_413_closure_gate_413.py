"""Phase 413 closure gate contract tests for window 402-413."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


GATE_PATH = Path("tools/check_window_402_413_closure_gate_phase_413.sh")
GATE_CMD = ["bash", str(GATE_PATH)]
HANDOFF_PATH = Path("docs/specs/ilc_window_402_413_handoff_413_v0.1.md")
SNAPSHOT_PATH = Path("out/monitoring/infrastructure_risk_snapshot_phase_316.json")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.5.md")
COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_412_v0.1.md")
ADM_PATH = Path("docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md")
AGENT_RUNTIME_PATH = Path("ilc_core/identity/agent_id_runtime.py")
TIMED_OUT_RUNTIME_PATH = Path("ilc_core/node/timed_out_lifecycle_runtime_411.py")
PHASE_413_COMMIT_SUBJECT = "docs(g8): phase 413 window 402-413 closure gate and 414-plus handoff"


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(GATE_CMD + args, capture_output=True, text=True, env=env, check=False)


def _clean_full_run_env() -> dict[str, str]:
    blocked = {
        "ILC_PHASE_413_SNAPSHOT_PATH",
        "ILC_PHASE_401_SNAPSHOT_PATH",
        "ILC_PHASE_316_SNAPSHOT_PATH",
        "ILC_PHASE_316_FORCE_VERDICT",
        "ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE",
        "ILC_PHASE_413_GATE_SELFTEST",
        "ILC_PHASE_401_GATE_SELFTEST",
        "ILC_PHASE_391_GATE_SELFTEST",
        "ILC_PHASE_377_GATE_SELFTEST",
        "ILC_PHASE_367_GATE_SELFTEST",
        "ILC_PHASE_357_GATE_SELFTEST",
        "ILC_PHASE_347_GATE_SELFTEST",
    }
    return {key: value for key, value in os.environ.items() if key not in blocked}


def _snapshot_override_env(tmp_path: Path, verdict: str) -> tuple[dict[str, str], bytes, int, str]:
    payload = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    severity = payload.get("severity_summary")
    assert isinstance(severity, dict), "snapshot_missing_severity_summary"
    for key in ("s2_indicators", "s3_indicators", "verdict"):
        assert key in severity, f"snapshot_missing_severity_key:{key}"
    severity["verdict"] = verdict

    snapshot_copy = tmp_path / f"snapshot_{verdict}.json"
    snapshot_copy.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    env = _clean_full_run_env()
    env["ILC_PHASE_413_SNAPSHOT_PATH"] = str(snapshot_copy)
    canonical_bytes = SNAPSHOT_PATH.read_bytes()
    canonical_mtime = SNAPSHOT_PATH.stat().st_mtime_ns
    canonical_sha = hashlib.sha256(canonical_bytes).hexdigest()
    return env, canonical_bytes, canonical_mtime, canonical_sha


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_413_commit_ref() -> str:
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
        if subject.strip() == PHASE_413_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(GATE_PATH),
        "tests/test_window_402_413_closure_gate_413.py",
        str(HANDOFF_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_413_commit_subject_present_but_no_qualifying_closure_commit")
    raise AssertionError("phase_413_commit_not_present_in_local_history")


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
        "python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_413_g8_d2e_window_402_413_closure_gate_and_414_plus_handoff.md",
        "[2/6] lane_contract_tests",
        "python3 -m pytest tests/test_phase_402_cdl_042_and_cdl_045_opening.py tests/test_phase_403_cdl_042_prelock_hardening.py tests/test_phase_404_cdl_045_prelock_hardening.py tests/test_phase_405_cdl_046_timed_out_amendment_open_prelock.py tests/test_phase_406_sim_008_commissioning.py tests/test_phase_407_cdl_042_ratification.py tests/test_phase_408_cdl_045_ratification.py tests/test_phase_409_cdl_046_ratification.py tests/test_phase_410_d2e_agent_identity_runtime.py tests/test_phase_411_d2e_timed_out_lifecycle_runtime.py tests/test_phase_412_coherence_and_capsule_v1_5.py -q",
        "[3/6] cross_phase_regression",
        "python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_d2_schema_baseline_runtime_310.py tests/test_genesis_state_bundle_runtime_312.py tests/test_epoch_snapshot_runtime_314.py tests/test_infrastructure_economic_risk_monitoring_update_315.py tests/test_infrastructure_composed_preflight_316.py tests/test_wire_transport_runtime_323.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_392_401_closure_gate_401.py -q",
        "[4/6] mutation_canary",
        "python3 tools/run_mutation_canary_phase_297.py",
        "[5/6] closure_gate_cli_contract",
        "python3 -m pytest tests/test_window_402_413_closure_gate_413.py -q",
        "[6/6] walkthrough_hygiene",
        "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q",
    ]

    unknown = _run_gate(["--unknown-arg"])
    assert unknown.returncode == 2


def test_gate_full_run_exits_zero_on_pass_snapshot_and_preserves_canonical_snapshot() -> None:
    if os.environ.get("ILC_PHASE_413_GATE_SELFTEST") == "1":
        pytest.skip("phase_413_selftest_context_skip_full_gate")
    canonical_before = SNAPSHOT_PATH.read_bytes()
    canonical_mtime_before = SNAPSHOT_PATH.stat().st_mtime_ns
    canonical_sha_before = hashlib.sha256(canonical_before).hexdigest()
    env = os.environ.copy()
    env["ILC_PHASE_316_FORCE_VERDICT"] = "conditional"
    env["ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE"] = "1"
    env["ILC_PHASE_401_GATE_SELFTEST"] = "1"
    result = _run_gate([], env=env)
    assert result.returncode == 0
    assert "phase_413_snapshot_gate=passed" in result.stdout
    assert "phase_413_verdict=pass" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical_before
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime_before
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha_before


def test_gate_full_run_enforces_conditional_exit_and_snapshot_isolation(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_413_GATE_SELFTEST") == "1":
        pytest.skip("phase_413_selftest_context_skip_verdict_simulation")
    env, canonical, canonical_mtime, canonical_sha = _snapshot_override_env(tmp_path, "conditional")
    result = _run_gate([], env=env)
    assert result.returncode == 3
    assert "phase_413_override_required=human" in result.stdout
    assert "phase_413_snapshot_gate=failed" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha


def test_gate_full_run_enforces_blocked_exit_and_snapshot_isolation(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_413_GATE_SELFTEST") == "1":
        pytest.skip("phase_413_selftest_context_skip_verdict_simulation")
    env, canonical, canonical_mtime, canonical_sha = _snapshot_override_env(tmp_path, "blocked")
    result = _run_gate([], env=env)
    assert result.returncode == 1
    assert "phase_413_snapshot_gate=failed" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha


def test_gate_assertions_and_handoff_contract_tokens() -> None:
    decision_log_text = DECISION_LOG_PATH.read_text(encoding="utf-8")
    rows = parse_decision_register_rows(decision_log_text)
    for cdl_id in ("CDL-042", "CDL-045", "CDL-046"):
        row = rows[cdl_id]
        assert row.get("status") == "ratified"
        for token in ("ratified_phase", "ratified_date", "evidence_document"):
            assert token in row, f"phase_413_missing_{token}:{cdl_id}"

    agent_text = AGENT_RUNTIME_PATH.read_text(encoding="utf-8")
    assert 'AGENT_ID_RUNTIME_VERSION = "agent_id_runtime_410.v0.1"' in agent_text

    timed_out_text = TIMED_OUT_RUNTIME_PATH.read_text(encoding="utf-8")
    assert 'ORPHAN_TIMEOUT_EPOCHS: int = 4' in timed_out_text
    assert 'RECOVERY_POLICY: str = "stake_full_release"' in timed_out_text

    capsule_text = CAPSULE_PATH.read_text(encoding="utf-8")
    assert (
        "SIM-008 post-issuance transition modeling results are available as evidence for Window-414+ Treasury Governance and ECU mandatory conversion deadline CDL planning."
        in capsule_text
    )
    assert (
        "Runtime-integrity note: V-series validators reject non-finite numeric inputs (NaN/Inf)."
        in capsule_text
    )

    coherence_text = COHERENCE_PATH.read_text(encoding="utf-8")
    assert (
        "CDL-042 ratification closes the agent identity namespace gate for D2e Agent SDK implementation."
        in coherence_text
    )

    adm_text = ADM_PATH.read_text(encoding="utf-8")
    assert "sign_digest(kid: str, payload_hash: bytes, context: dict) -> signature_bytes" in adm_text

    handoff_text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Window summary (402-413 completion state)",
        "## 2. Deliverable matrix for phases 402-412",
        "## 3. Closure-gate category evidence",
        "## 4. Constitutional and runtime closure summary",
        "## 5. Window-414+ strategic boundary",
        "## 6. Monitoring snapshot isolation controls",
        "## 7. Carry-forward risks and controls",
        "## 8. Canonical anchors and next-window pointer",
    ):
        assert heading in handoff_text

    for token in (
        "Window 402-413 closed the constitutional expansion lane for agent identity, operational emergency response, and CDL-035 timed_out amendment (CDL-042, CDL-045, and CDL-046).",
        "CDL-042, CDL-045, and CDL-046 are ratified at Window 402-413 close.",
        "D2e Agent SDK runtime block is implemented: agent identity derivation (Phase 410) and timed-out lifecycle constants (Phase 411).",
        "SIM-008 post-issuance transition modeling evidence is available for Window-414+ Treasury Governance and ECU mandatory conversion deadline CDL planning.",
        "Window 414+ strategic carry-forward includes Treasury Governance CDL planning, ECU mandatory conversion deadline CDL planning, and strict Popperian bounded-existential claim-form review.",
        "No decision-log mutation occurred in Phase 413.",
        "No new ilc_core runtime feature implementation occurred in Phase 413.",
        "docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md",
        "docs/specs/ilc_integration_coherence_report_412_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v1.5.md",
        "docs/specs/ilc_cdl_042_agent_identity_namespace_ratification_evidence_407_v0.1.md",
        "docs/specs/ilc_cdl_045_operational_emergency_response_ratification_evidence_408_v0.1.md",
        "docs/specs/ilc_cdl_046_timed_out_amendment_ratification_evidence_409_v0.1.md",
        "git restore out/monitoring/infrastructure_risk_snapshot_phase_316.json",
    ):
        assert token in handoff_text


def test_no_decision_log_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_413_GATE_SELFTEST") == "1":
        pytest.skip("phase_413_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_413_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed


def test_no_ilc_core_runtime_feature_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_413_GATE_SELFTEST") == "1":
        pytest.skip("phase_413_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_413_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
