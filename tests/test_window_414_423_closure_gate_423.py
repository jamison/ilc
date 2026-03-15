"""Phase 423 closure gate contract tests for window 414-423."""

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


GATE_PATH = Path("tools/check_window_414_423_closure_gate_phase_423.sh")
GATE_CMD = ["bash", str(GATE_PATH)]
HANDOFF_PATH = Path("docs/specs/ilc_window_414_423_handoff_423_v0.1.md")
SNAPSHOT_PATH = Path("out/monitoring/infrastructure_risk_snapshot_phase_316.json")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.6.md")
COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_422_v0.1.md")
ADM_PATH = Path("docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md")
AGENT_CLI_PATH = Path("ilc_core/cli/d2e_agent_cli.py")
NODE_CLI_PATH = Path("ilc_core/cli/d2e_lifecycle_cli.py")
MAIN_CLI_PATH = Path("ilc_core/cli/main.py")
PHASE_423_COMMIT_SUBJECT = "docs(g8): phase 423 window 414-423 closure gate and 424-plus handoff"


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(GATE_CMD + args, capture_output=True, text=True, env=env, check=False)


def _clean_full_run_env() -> dict[str, str]:
    blocked = {
        "ILC_PHASE_423_SNAPSHOT_PATH",
        "ILC_PHASE_413_SNAPSHOT_PATH",
        "ILC_PHASE_401_SNAPSHOT_PATH",
        "ILC_PHASE_337_SNAPSHOT_PATH",
        "ILC_PHASE_327_SNAPSHOT_PATH",
        "ILC_PHASE_316_SNAPSHOT_PATH",
        "ILC_PHASE_316_FORCE_VERDICT",
        "ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE",
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
    env["ILC_PHASE_423_SNAPSHOT_PATH"] = str(snapshot_copy)
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


def _resolve_phase_423_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    required_paths = {
        str(GATE_PATH),
        "tests/test_window_414_423_closure_gate_423.py",
        str(HANDOFF_PATH),
    }
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_423_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if changed_paths == required_paths:
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_423_commit_subject_present_but_no_qualifying_closure_commit")
    raise AssertionError("phase_423_commit_not_present_in_local_history")


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
        "python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_423_g8_window_414_423_closure_gate_and_424_plus_handoff.md",
        "[2/6] lane_contract_tests",
        "python3 -m pytest tests/test_phase_414_cdl_047_and_cdl_048_opening.py tests/test_phase_415_cdl_047_treasury_governance_prelock_hardening.py tests/test_phase_416_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening.py tests/test_phase_417_popperian_bounded_existential_claim_form_governance_review.py tests/test_phase_418_cdl_047_treasury_governance_ratification.py tests/test_phase_419_cdl_048_ecu_mandatory_conversion_deadline_ratification.py tests/test_phase_420_d2e_agent_cli.py tests/test_phase_421_d2e_lifecycle_cli.py tests/test_phase_422_coherence_and_capsule_v1_6.py -q",
        "[3/6] cross_phase_regression",
        "python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_d2_schema_baseline_runtime_310.py tests/test_genesis_state_bundle_runtime_312.py tests/test_epoch_snapshot_runtime_314.py tests/test_infrastructure_economic_risk_monitoring_update_315.py tests/test_infrastructure_composed_preflight_316.py tests/test_wire_transport_runtime_323.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_392_401_closure_gate_401.py tests/test_window_402_413_closure_gate_413.py -q",
        "[4/6] mutation_canary",
        "python3 tools/run_mutation_canary_phase_297.py",
        "[5/6] closure_gate_cli_contract",
        "python3 -m pytest tests/test_window_414_423_closure_gate_423.py -q",
        "[6/6] walkthrough_hygiene",
        "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q",
    ]

    unknown = _run_gate(["--unknown-arg"])
    assert unknown.returncode == 2


def test_gate_full_run_exits_zero_on_pass_snapshot_and_preserves_canonical_snapshot() -> None:
    if os.environ.get("ILC_PHASE_423_GATE_SELFTEST") == "1":
        pytest.skip("phase_423_selftest_context_skip_full_gate")
    canonical_before = SNAPSHOT_PATH.read_bytes()
    canonical_mtime_before = SNAPSHOT_PATH.stat().st_mtime_ns
    canonical_sha_before = hashlib.sha256(canonical_before).hexdigest()
    env = os.environ.copy()
    env["ILC_PHASE_413_SNAPSHOT_PATH"] = "/tmp/phase_413_should_be_sanitized.json"
    env["ILC_PHASE_401_SNAPSHOT_PATH"] = "/tmp/phase_401_should_be_sanitized.json"
    env["ILC_PHASE_337_SNAPSHOT_PATH"] = "/tmp/phase_337_should_be_sanitized.json"
    env["ILC_PHASE_327_SNAPSHOT_PATH"] = "/tmp/phase_327_should_be_sanitized.json"
    env["ILC_PHASE_316_FORCE_VERDICT"] = "conditional"
    env["ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE"] = "1"
    env["ILC_PHASE_423_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_413_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_401_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_337_GATE_SELFTEST"] = "1"
    env["ILC_PHASE_327_GATE_SELFTEST"] = "1"
    result = _run_gate([], env=env)
    assert result.returncode == 0
    assert "phase_423_snapshot_gate=passed" in result.stdout
    assert "phase_423_verdict=pass" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical_before
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime_before
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha_before


def test_gate_full_run_enforces_conditional_exit_and_snapshot_isolation(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_423_GATE_SELFTEST") == "1":
        pytest.skip("phase_423_selftest_context_skip_verdict_simulation")
    env, canonical, canonical_mtime, canonical_sha = _snapshot_override_env(tmp_path, "conditional")
    result = _run_gate([], env=env)
    assert result.returncode == 3
    assert "phase_423_override_required=human" in result.stdout
    assert "phase_423_snapshot_gate=failed" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha


def test_gate_full_run_enforces_blocked_exit_and_snapshot_isolation(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_423_GATE_SELFTEST") == "1":
        pytest.skip("phase_423_selftest_context_skip_verdict_simulation")
    env, canonical, canonical_mtime, canonical_sha = _snapshot_override_env(tmp_path, "blocked")
    result = _run_gate([], env=env)
    assert result.returncode == 1
    assert "phase_423_snapshot_gate=failed" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha


def test_gate_assertions_and_handoff_contract_tokens() -> None:
    decision_log_text = DECISION_LOG_PATH.read_text(encoding="utf-8")
    rows = parse_decision_register_rows(decision_log_text)
    for cdl_id in ("CDL-047", "CDL-048"):
        row = rows[cdl_id]
        assert row.get("status") == "ratified"
        for token in ("ratified_phase", "ratified_date", "evidence_document"):
            assert token in row, f"phase_423_missing_{token}:{cdl_id}"

    agent_cli_text = AGENT_CLI_PATH.read_text(encoding="utf-8")
    assert 'D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"' in agent_cli_text

    node_cli_text = NODE_CLI_PATH.read_text(encoding="utf-8")
    assert 'D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"' in node_cli_text

    from ilc_core.cli.main import OPERATIONAL_COMMANDS

    assert "agent" in OPERATIONAL_COMMANDS
    assert "node" in OPERATIONAL_COMMANDS

    capsule_text = CAPSULE_PATH.read_text(encoding="utf-8")
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.5.md" in capsule_text
    assert "This capsule is self-contained." in capsule_text
    assert "Window 423 is the closure-gate lane for Window 414-423." in capsule_text

    popperian_text = Path("docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md").read_text(encoding="utf-8")
    coherence_text = COHERENCE_PATH.read_text(encoding="utf-8")
    token = (
        "Phase 417 recorded no CDL-047-specific or CDL-048-specific CRITICAL findings; "
        "CDL-049 remains a Window-424+ planning boundary for bounded-existential alignment."
    )
    assert token in popperian_text or token in coherence_text

    adm_text = ADM_PATH.read_text(encoding="utf-8")
    assert "sign_digest(kid: str, payload_hash: bytes, context: dict) -> signature_bytes" in adm_text

    handoff_text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Window summary (414-423 completion state)",
        "## 2. Deliverable matrix for phases 414-422",
        "## 3. Closure-gate category evidence",
        "## 4. Constitutional and runtime closure summary",
        "## 5. Window-424+ strategic boundary",
        "## 6. Monitoring snapshot isolation controls",
        "## 7. Carry-forward risks and controls",
        "## 8. Canonical anchors and next-window pointer",
    ):
        assert heading in handoff_text

    for handoff_token in (
        "Window 414-423 closed the Treasury Governance and ECU mandatory conversion deadline constitutional lanes (CDL-047 and CDL-048) and completed the D2e Agent SDK CLI integration.",
        "CDL-047 is ratified with bounty cap 0.15 x B_e, burn floor 0.05, and velocity alert floor 0.91.",
        "CDL-048 is ratified with ecu_conversion_deadline = 4 issuance epochs.",
        'D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"',
        'D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"',
        token,
        "Window 424+ carry-forward includes CDL-049 bounded-existential alignment, follow-on D2e CLI expansion if needed, Treasury P_e stabilization follow-on governance if warranted, and SIM-009 commissioning only if new coherence gaps warrant it.",
        "No decision-log mutation occurred in Phase 423.",
        "No new ilc_core runtime feature implementation occurred in Phase 423.",
    ):
        assert handoff_token in handoff_text


def test_no_decision_log_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_423_GATE_SELFTEST") == "1":
        pytest.skip("phase_423_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_423_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed


def test_no_ilc_core_runtime_feature_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_423_GATE_SELFTEST") == "1":
        pytest.skip("phase_423_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_423_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
