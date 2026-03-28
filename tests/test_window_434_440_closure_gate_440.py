"""Phase 440 closure gate contract tests for window 434-440."""

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


GATE_PATH = Path("tools/check_window_434_440_closure_gate_phase_440.sh")
GATE_CMD = ["bash", str(GATE_PATH)]
HANDOFF_PATH = Path("docs/specs/ilc_window_434_440_handoff_440_v0.1.md")
SNAPSHOT_PATH = Path("out/monitoring/infrastructure_risk_snapshot_phase_316.json")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_434_440_sequence_lock_v0.1.md")
INTAKE_PATH = Path("docs/specs/ilc_window_434_runtime_tranche_intake_434_v0.1.md")
PEER_PATH = Path("ilc_core/network/peer.py")
PHASE_435_HANDOFF_PATH = Path("docs/specs/ilc_runtime_tranche_peer_fanout_handoff_435_v0.1.md")
RUNTIME_BASELINE_PATH = Path("tools/runtime_baseline.py")
PHASE_436_HANDOFF_PATH = Path("docs/specs/ilc_runtime_tranche_benchmark_handoff_436_v0.1.md")
PHASE_437_MEMO_PATH = Path("docs/specs/ilc_runtime_tranche_findings_memo_437_v0.1.md")
PHASE_438_REVIEW_PATH = Path("docs/specs/ilc_treasury_pe_prerequisite_satisfaction_review_438_v0.1.md")
PHASE_439_COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_439_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.8.md")
PHASE_440_COMMIT_SUBJECT = "docs(g8): phase 440 window 434-440 closure gate and 441-plus handoff"


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(GATE_CMD + args, capture_output=True, text=True, env=env, check=False)


def _clean_full_run_env() -> dict[str, str]:
    blocked = {
        "ILC_PHASE_440_GATE_SELFTEST",
        "ILC_PHASE_433_GATE_SELFTEST",
        "ILC_PHASE_423_GATE_SELFTEST",
        "ILC_PHASE_413_GATE_SELFTEST",
        "ILC_PHASE_401_GATE_SELFTEST",
        "ILC_PHASE_391_GATE_SELFTEST",
        "ILC_PHASE_377_GATE_SELFTEST",
        "ILC_PHASE_367_GATE_SELFTEST",
        "ILC_PHASE_357_GATE_SELFTEST",
        "ILC_PHASE_347_GATE_SELFTEST",
        "ILC_PHASE_337_GATE_SELFTEST",
        "ILC_PHASE_327_GATE_SELFTEST",
        "ILC_PHASE_440_SNAPSHOT_PATH",
        "ILC_PHASE_433_SNAPSHOT_PATH",
        "ILC_PHASE_423_SNAPSHOT_PATH",
        "ILC_PHASE_413_SNAPSHOT_PATH",
        "ILC_PHASE_401_SNAPSHOT_PATH",
        "ILC_PHASE_391_SNAPSHOT_PATH",
        "ILC_PHASE_377_SNAPSHOT_PATH",
        "ILC_PHASE_367_SNAPSHOT_PATH",
        "ILC_PHASE_357_SNAPSHOT_PATH",
        "ILC_PHASE_347_SNAPSHOT_PATH",
        "ILC_PHASE_337_SNAPSHOT_PATH",
        "ILC_PHASE_327_SNAPSHOT_PATH",
        "ILC_PHASE_316_SNAPSHOT_PATH",
        "ILC_PHASE_316_FORCE_VERDICT",
        "ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE",
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
    env["ILC_PHASE_440_SNAPSHOT_PATH"] = str(snapshot_copy)
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


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}:{result.stderr.strip()}")
    return result.stdout


def _resolve_phase_440_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    required_paths = {
        str(GATE_PATH),
        str(Path("tests/test_window_434_440_closure_gate_440.py")),
        str(HANDOFF_PATH),
    }
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_440_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if changed_paths == required_paths:
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_440_commit_subject_present_but_no_qualifying_closure_commit")
    raise AssertionError("phase_440_commit_not_present_in_local_history")


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
        "python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_440_g8_window_434_440_closure_gate_and_441_plus_handoff.md",
        "[2/6] lane_contract_tests",
        "python3 -m pytest tests/test_phase_434_window_434_440_sequence_lock_and_runtime_tranche_intake.py tests/test_phase_435_runtime_tranche_peer_fanout_integration.py tests/test_phase_436_runtime_tranche_benchmark_harness_and_tranche_completion.py tests/test_phase_437_runtime_tranche_findings_memo_and_regression_hardening.py tests/test_phase_438_treasury_pe_prerequisite_satisfaction_review.py tests/test_phase_439_coherence_and_capsule_v1_8.py -q",
        "[3/6] cross_phase_regression",
        "python3 -m pytest tests/test_network.py tests/test_network_gossip.py tests/test_node_dissemination_runtime_362.py tests/test_code_health.py tests/test_phase_commit_manifest_296.py tests/test_d2_schema_baseline_runtime_310.py tests/test_genesis_state_bundle_runtime_312.py tests/test_epoch_snapshot_runtime_314.py tests/test_infrastructure_economic_risk_monitoring_update_315.py tests/test_infrastructure_composed_preflight_316.py tests/test_wire_transport_runtime_323.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_392_401_closure_gate_401.py tests/test_window_402_413_closure_gate_413.py tests/test_window_414_423_closure_gate_423.py tests/test_window_424_433_closure_gate_433.py -q",
        "[4/6] mutation_canary",
        "python3 tools/run_mutation_canary_phase_297.py",
        "[5/6] closure_gate_cli_contract",
        "python3 -m pytest tests/test_window_434_440_closure_gate_440.py -q",
        "[6/6] walkthrough_hygiene",
        "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q",
    ]

    unknown = _run_gate(["--unknown-arg"])
    assert unknown.returncode == 2


def test_gate_full_run_exits_zero_on_pass_snapshot_and_preserves_canonical_snapshot() -> None:
    if os.environ.get("ILC_PHASE_440_GATE_SELFTEST") == "1":
        pytest.skip("phase_440_selftest_context_skip_full_gate")
    canonical_before = SNAPSHOT_PATH.read_bytes()
    canonical_mtime_before = SNAPSHOT_PATH.stat().st_mtime_ns
    canonical_sha_before = hashlib.sha256(canonical_before).hexdigest()
    env = _clean_full_run_env()
    env["ILC_PHASE_433_SNAPSHOT_PATH"] = "/tmp/phase_433_should_be_sanitized.json"
    env["ILC_PHASE_423_SNAPSHOT_PATH"] = "/tmp/phase_423_should_be_sanitized.json"
    env["ILC_PHASE_413_SNAPSHOT_PATH"] = "/tmp/phase_413_should_be_sanitized.json"
    env["ILC_PHASE_401_SNAPSHOT_PATH"] = "/tmp/phase_401_should_be_sanitized.json"
    env["ILC_PHASE_391_SNAPSHOT_PATH"] = "/tmp/phase_391_should_be_sanitized.json"
    env["ILC_PHASE_377_SNAPSHOT_PATH"] = "/tmp/phase_377_should_be_sanitized.json"
    env["ILC_PHASE_367_SNAPSHOT_PATH"] = "/tmp/phase_367_should_be_sanitized.json"
    env["ILC_PHASE_357_SNAPSHOT_PATH"] = "/tmp/phase_357_should_be_sanitized.json"
    env["ILC_PHASE_347_SNAPSHOT_PATH"] = "/tmp/phase_347_should_be_sanitized.json"
    env["ILC_PHASE_337_SNAPSHOT_PATH"] = "/tmp/phase_337_should_be_sanitized.json"
    env["ILC_PHASE_327_SNAPSHOT_PATH"] = "/tmp/phase_327_should_be_sanitized.json"
    env["ILC_PHASE_316_FORCE_VERDICT"] = "conditional"
    env["ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE"] = "1"
    env["ILC_PHASE_440_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_433_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_423_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_413_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_401_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_391_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_377_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_367_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_357_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_347_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_337_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_327_GATE_SELFTEST"] = "1"
    result = _run_gate([], env=env)
    assert result.returncode == 0
    assert "phase_440_snapshot_gate=passed" in result.stdout
    assert "phase_440_verdict=pass" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical_before
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime_before
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha_before


def test_gate_full_run_enforces_conditional_exit_and_snapshot_isolation(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_440_GATE_SELFTEST") == "1":
        pytest.skip("phase_440_selftest_context_skip_verdict_simulation")
    env, canonical, canonical_mtime, canonical_sha = _snapshot_override_env(tmp_path, "conditional")
    result = _run_gate([], env=env)
    assert result.returncode == 3
    assert "phase_440_override_required=human" in result.stdout
    assert "phase_440_snapshot_gate=failed" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha


def test_gate_full_run_enforces_blocked_exit_and_snapshot_isolation(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_440_GATE_SELFTEST") == "1":
        pytest.skip("phase_440_selftest_context_skip_verdict_simulation")
    env, canonical, canonical_mtime, canonical_sha = _snapshot_override_env(tmp_path, "blocked")
    result = _run_gate([], env=env)
    assert result.returncode == 1
    assert "phase_440_snapshot_gate=failed" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha


def test_gate_assertions_and_handoff_contract_tokens() -> None:
    # The Phase-440 CDL inventory state is a historical reference.
    decision_log_text = _decision_log_text_at_ref(_resolve_phase_440_commit_ref())
    rows = parse_decision_register_rows(decision_log_text)
    assert rows["CDL-049"].get("status") == "ratified"
    assert "CDL-050" not in rows

    sequence_lock_text = SEQUENCE_LOCK_PATH.read_text(encoding="utf-8")
    for token in (
        "Window 434+ is the Runtime Tranche and Treasury P_e Prerequisite Review Block.",
        "CDL-050 is not pre-authorized at Phase 434 entry.",
        "| 7 | 440 | Closure gate + next-window handoff | Gate | SENSITIVE |",
    ):
        assert token in sequence_lock_text

    intake_text = INTAKE_PATH.read_text(encoding="utf-8")
    for token in (
        "Frozen Phase-434-authorized runtime-tranche import set:",
        "tools/runtime_baseline.py",
        "Window 434+ must cherry-pick the release-track runtime tranche before any public repo packaging commits are merged.",
    ):
        assert token in intake_text

    peer_text = PEER_PATH.read_text(encoding="utf-8")
    for token in (
        "network_gossip_delivery_succeeded",
        "network_gossip_delivery_failed",
    ):
        assert token in peer_text

    phase_435_text = PHASE_435_HANDOFF_PATH.read_text(encoding="utf-8")
    for token in (
        "Real HTTP peer fanout attempts are now performed by ilc_core/network/peer.py.",
        "Delivery success and failure outcomes are observable in runtime logs.",
        "Public packaging/bootstrap work remains outside the numbered window.",
    ):
        assert token in phase_435_text

    runtime_baseline_text = RUNTIME_BASELINE_PATH.read_text(encoding="utf-8")
    for token in (
        "DEFAULT_BUDGETS_MS",
        "build_runtime_baseline_report",
        "out/runtime_baseline/report.json",
    ):
        assert token in runtime_baseline_text

    phase_436_text = PHASE_436_HANDOFF_PATH.read_text(encoding="utf-8")
    for token in (
        "Runtime baseline harness import was byte-aligned to the frozen release-track source.",
        "The numbered runtime tranche authorized by Phase 434 is complete after Phase 436.",
    ):
        assert token in phase_436_text

    phase_437_text = PHASE_437_MEMO_PATH.read_text(encoding="utf-8")
    for token in (
        "No additional regression hardening was required beyond the exact path-set and source-hash guards already published in Phases 435 and 436.",
        "No multi-process or native-P2P measurement exists yet; that remains future work outside Phase 437.",
    ):
        assert token in phase_437_text

    phase_438_text = PHASE_438_REVIEW_PATH.read_text(encoding="utf-8")
    for token in (
        "Prerequisite 1 (decoupled recovery criterion): NOT SATISFIED.",
        "Prerequisite 2 (explicit treasury-risk tolerance judgment): NOT SATISFIED.",
        "Prerequisite 3 (additional discriminating simulation evidence): NOT SATISFIED.",
        "CDL-050 opening is still not justified at the close of Phase 438.",
    ):
        assert token in phase_438_text

    phase_439_text = PHASE_439_COHERENCE_PATH.read_text(encoding="utf-8")
    for token in (
        "The numbered runtime tranche authorized by Phase 434 completed in Phases 435 and 436.",
        "CDL-050 remains unopened and unjustified at the close of Phase 439.",
    ):
        assert token in phase_439_text

    capsule_text = CAPSULE_PATH.read_text(encoding="utf-8")
    for token in (
        "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.7.md",
        "This capsule is self-contained.",
        "Window 440 is the closure-gate lane for Window 434-440.",
        "Treasury P_e prerequisites remain unsatisfied after Phase 438, so CDL-050 remains unopened.",
        "Public packaging/bootstrap work remains on the parallel release-engineering track.",
    ):
        assert token in capsule_text

    handoff_text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Window summary (434-440 completion state)",
        "## 2. Deliverable matrix for phases 434-439",
        "## 3. Closure-gate category evidence",
        "## 4. Runtime tranche closure summary",
        "## 5. Treasury P_e carry-forward state",
        "## 6. Release-engineering boundary and merge state",
        "## 7. Next-window controls and non-authorizations",
        "## 8. Canonical anchors and next-window pointer",
    ):
        assert heading in handoff_text

    for token in (
        "Window 434-440 closed the numbered runtime tranche and left the Treasury P_e lane as a future carry-forward item with CDL-050 unopened.",
        "CDL-049 remained ratified and unaffected at Window 434-440 closure.",
        "The numbered runtime tranche authorized by Phase 434 completed in Phases 435 and 436.",
        "Phase 438 concluded that all three Phase-431 prerequisites remain unsatisfied.",
        "CDL-050 was not opened in Window 434-440.",
        "Public packaging/bootstrap work remained outside the numbered window.",
        "Release-track source anchor remained ../ILC_release_track/docs/handoffs/main_track_handoff_window_434_runtime_tranche_v0.1.md for the imported runtime tranche.",
        "The release-track runtime tranche landed on main before any public repo packaging merge.",
        "Phase 440 does not authorize Phases 441+ by itself; any move beyond Window 434-440 requires a new sequence lock or amendment.",
        "Any future CDL-050 opening remains contingent and not pre-authorized at Window 434-440 closure.",
        "No decision-log mutation occurred in Phase 440.",
        "No new ilc_core runtime feature implementation occurred in Phase 440.",
    ):
        assert token in handoff_text


def test_no_decision_log_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_440_GATE_SELFTEST") == "1":
        pytest.skip("phase_440_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_440_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed


def test_no_ilc_core_runtime_feature_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_440_GATE_SELFTEST") == "1":
        pytest.skip("phase_440_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_440_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
