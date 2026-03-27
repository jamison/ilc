from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    diff_row_fields,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
RATIFICATION_PATH = Path("docs/specs/ilc_cdl_050_treasury_ecu_governor_ratification_evidence_459_v0.1.md")
HANDOFF_PATH = Path("docs/specs/ilc_window_450_459_handoff_459_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v2.0.md")
PHASE_458_TEST_PATH = Path("tests/test_phase_458_cdl_050_prelock_hardening.py")
PHASE_449_TEST_PATH = Path("tests/test_window_441_449_closure_gate_449.py")
GATE_PATH = Path("tools/check_window_450_459_closure_gate_phase_459.sh")
SNAPSHOT_PATH = Path("out/monitoring/infrastructure_risk_snapshot_phase_316.json")
PHASE_459_SUBJECT_TOKEN = "phase 459 cdl-050 ratification and window 450-459 closure"
FORBIDDEN_TREASURY_TOKEN = "ILC_CDL_MUTATION_" + "AUTHORIZED"
EXACT_REQUIRED_MAIN_PATHS = {
    str(DECISION_LOG_PATH),
    str(RATIFICATION_PATH),
    str(HANDOFF_PATH),
    str(CAPSULE_PATH),
    str(GATE_PATH),
    str(Path("tests/test_window_450_459_closure_gate_459.py")),
    str(PHASE_458_TEST_PATH),
    str(PHASE_449_TEST_PATH),
}
REQUIRED_RATIFICATION_HEADINGS = (
    "## 1. Ratification declaration",
    "## 2. Evidence chain",
    "## 3. Ratified constitutional contract",
    "## 4. Independence and boundary assertions",
)
REQUIRED_RATIFICATION_TOKENS = (
    "CDL-050 is ratified in Phase 459.",
    "CDL-050 ratification remains authorized by phase_456_fix_14_overall_verdict=pass.",
    "The controlling Blocker-1 evidence basis remains the oscillator-cleared rerun chain.",
    "CDL-051 is ratified and remains unaffected by CDL-050 ratification.",
    "CDL-050 implementation in simulations/ or ilc_core/ does not occur in Phase 459.",
    "The Phase 458 prelock artifact remains the direct pre-ratification hardening anchor.",
)
REQUIRED_HANDOFF_HEADINGS = (
    "## 1. Window summary (450-459 completion state)",
    "## 2. Deliverable matrix for phases 450-459",
    "## 3. CDL-050 ratification summary",
    "## 4. Treasury ECU-governor authorization state",
    "## 5. Next-window controls and non-authorizations",
    "## 6. Canonical anchors and next-window pointer",
)
REQUIRED_HANDOFF_TOKENS = (
    "Window 450-459 is closed.",
    "CDL-050 is ratified.",
    "CDL-051 is ratified.",
    "The controlling Blocker-1 evidence basis was the oscillator-cleared rerun chain.",
    "No decision-log mutation occurred in Phase 459 beyond CDL-050 ratification.",
    "No new simulations or ilc_core runtime feature implementation occurred in Phase 459.",
    "Phase 460 is the next numbered phase.",
    "Phase 459 does not authorize Phase 460+ by itself; any move beyond Window 450-459 requires a new sequence lock or amendment.",
)
REQUIRED_CAPSULE_TOKENS = (
    "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.9.md",
    "This capsule is self-contained.",
    "Window 450-459 is closed.",
    "CDL-050 is ratified. CDL-051 is ratified.",
    "Phase 460 is the next authorized phase.",
)
EXPECTED_DRY_RUN_LINES = [
    "[1/6] prompt_contract_validation",
    "python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_459_g8_cdl_050_ratification_and_window_closure.md",
    "[2/6] lane_contract_tests",
    "python3 -m pytest tests/test_phase_457_cdl_050_opening_rerun_path.py tests/test_phase_458_cdl_050_prelock_hardening.py -q",
    "[3/6] cross_phase_regression",
    "python3 -m pytest tests/test_window_441_449_closure_gate_449.py -q",
    "[4/6] mutation_canary",
    "python3 tools/run_mutation_canary_phase_297.py",
    "[5/6] closure_gate_cli_contract",
    "python3 -m pytest tests/test_window_450_459_closure_gate_459.py -q",
    "[6/6] walkthrough_hygiene",
    "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(GATE_PATH)] + args, capture_output=True, text=True, env=env, check=False)


def _clean_gate_env() -> dict[str, str]:
    blocked = {"ILC_PHASE_459_GATE_SELFTEST", "ILC_PHASE_449_GATE_SELFTEST", "ILC_PHASE_459_SNAPSHOT_PATH"}
    return {key: value for key, value in os.environ.items() if key not in blocked}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_459_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if PHASE_459_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)

    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref

    if matching:
        raise AssertionError("phase_459_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_459_commit_not_present_in_local_history")


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


def test_ratification_evidence_artifact_exists_and_contains_required_headings_and_tokens() -> None:
    text = _read(RATIFICATION_PATH)
    for heading in REQUIRED_RATIFICATION_HEADINGS:
        assert heading in text
    for token in REQUIRED_RATIFICATION_TOKENS:
        assert token in text
    assert FORBIDDEN_TREASURY_TOKEN not in text


def test_handoff_artifact_exists_and_contains_required_headings_and_tokens() -> None:
    text = _read(HANDOFF_PATH)
    for heading in REQUIRED_HANDOFF_HEADINGS:
        assert heading in text
    for token in REQUIRED_HANDOFF_TOKENS:
        assert token in text


def test_capsule_v2_0_exists_and_contains_required_tokens() -> None:
    text = _read(CAPSULE_PATH)
    for token in REQUIRED_CAPSULE_TOKENS:
        assert token in text


def test_phase_458_suite_is_historicalized_for_cdl_050_prelock_assertions() -> None:
    phase_458_text = _read(PHASE_458_TEST_PATH)
    assert "historical_text = _decision_log_text_at_ref(_resolve_phase_458_commit_ref())" in phase_458_text
    assert "rows = parse_decision_register_rows(historical_text)" in phase_458_text
    assert "assert EXPECTED_PRELOCK_ROW in historical_text" in phase_458_text
    assert "rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))" in phase_458_text
    assert 'assert rows["CDL-051"]["status"] == "ratified"' in phase_458_text

    phase_449_text = _read(PHASE_449_TEST_PATH)
    assert "def _decision_log_text_at_ref(ref: str) -> str:" in phase_449_text
    assert "historical_rows = parse_decision_register_rows(_decision_log_text_at_ref(_resolve_phase_449_commit_ref()))" in phase_449_text
    assert 'assert "CDL-050" not in historical_rows' in phase_449_text
    assert 'assert live_rows["CDL-051"].get("status") == "ratified"' in phase_449_text


def test_gate_script_exists_and_honors_cli_contract() -> None:
    assert GATE_PATH.exists()

    help_result = _run_gate(["--help"])
    assert help_result.returncode == 0
    assert "Usage:" in help_result.stdout

    help_alias = _run_gate(["-h"])
    assert help_alias.returncode == 0
    assert "Usage:" in help_alias.stdout

    dry_run = _run_gate(["--dry-run"])
    assert dry_run.returncode == 0
    lines = [line.strip() for line in dry_run.stdout.splitlines() if line.strip()]
    assert lines == EXPECTED_DRY_RUN_LINES

    unknown = _run_gate(["--unknown-arg"])
    assert unknown.returncode == 2


def test_gate_full_run_passes_preserves_snapshot_and_live_decision_log_is_ratified() -> None:
    if os.environ.get("ILC_PHASE_459_GATE_SELFTEST") == "1":
        pytest.skip("phase_459_selftest_context_skip_full_gate")

    before = SNAPSHOT_PATH.read_bytes()
    before_mtime = SNAPSHOT_PATH.stat().st_mtime_ns
    before_sha = hashlib.sha256(before).hexdigest()
    result = _run_gate([], env=_clean_gate_env())
    assert result.returncode == 0
    assert "phase_459_verdict=pass" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == before
    assert SNAPSHOT_PATH.stat().st_mtime_ns == before_mtime
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == before_sha
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-050"]["status"] == "ratified"
    assert rows["CDL-051"]["status"] == "ratified"


def test_phase_459_commit_touches_exact_required_paths_and_no_runtime() -> None:
    if os.environ.get("ILC_PHASE_459_GATE_SELFTEST") == "1":
        pytest.skip("phase_459_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_459_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith("simulations/") for path in changed_paths)
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_459_commit_mutates_only_cdl_050_and_leaves_non_target_rows_unchanged() -> None:
    if os.environ.get("ILC_PHASE_459_GATE_SELFTEST") == "1":
        pytest.skip("phase_459_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_459_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    assert set(old_rows.keys()) == set(new_rows.keys())
    assert diff_row_fields(old_rows["CDL-050"], new_rows["CDL-050"]) == {
        "status",
        "current_candidate",
        "ratified_phase",
        "ratified_date",
        "evidence_document",
    }
    assert old_rows["CDL-050"]["status"] == "prelock"
    assert new_rows["CDL-050"]["status"] == "ratified"
    assert old_rows["CDL-050"]["current_candidate"].endswith("(proposed)")
    assert new_rows["CDL-050"]["current_candidate"] == (
        "bounded Treasury ECU-governor lane with decoupled recovery criterion and explicit ECU-side lever ceilings"
    )
    assert new_rows["CDL-050"]["ratified_phase"] == "459"
    assert new_rows["CDL-050"]["ratified_date"]
    assert new_rows["CDL-050"]["evidence_document"] == str(RATIFICATION_PATH)
    for cdl_id in old_rows:
        if cdl_id == "CDL-050":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_459"
