from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


HARDENING_DOC_PATH = Path("docs/specs/ilc_tier0_numeric_hardening_and_window_631_636_closure_636_v0.1.md")
PHASE_TEST_PATH = Path("tests/test_phase_636_tier0_numeric_hardening_and_closure.py")
HARDENING_TEST_PATH = Path("tests/test_tier0_numeric_hardening.py")
GATE_SCRIPT_PATH = Path("tools/run_window_631_636_numeric_determinism_gate_phase_636.sh")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v3.5.md")
HANDOFF_PATH = Path("docs/specs/ilc_window_631_636_handoff_636_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_636_g8_tier0_numeric_hardening_and_closure_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")

PHASE_636_SUBJECT = "phase 636 tier0 numeric hardening gate and closure"
PHASE_636_BACKFILL_SUBJECT = "phase 636 walkthrough and status backfill"

REQUIRED_MAIN_PATHS = {
    str(HARDENING_DOC_PATH),
    str(PHASE_TEST_PATH),
    str(HARDENING_TEST_PATH),
    str(GATE_SCRIPT_PATH),
    str(CAPSULE_PATH),
    str(HANDOFF_PATH),
}
EXACT_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Gate identity and authority",
    "## 2. Tier-0 runtime surface under test",
    "## 3. Hardening suite executed",
    "## 4. Findings and fix-loop disposition",
    "## 5. Closure verdict and carry-forward",
    "## 6. Capsule and handoff updates",
)
REQUIRED_TOKENS = (
    "tier0_numeric_hardening_gate_636_locked",
    "runtime_numeric_hardening_gate_phase_636_executed",
    "tier0_exact_arithmetic_hardening_pass",
    "tier0_no_float_runtime_accounting_confirmed",
    "tier0_no_tolerance_settlement_logic_confirmed",
    "window_631_636_closure_verdict_pass",
    "window_623_plus_may_resume_on_exact_numeric_tier0_foundation",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _find_commit_ref(subject_token: str) -> str | None:
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
        if subject_token in subject.lower():
            return commit_hash
    return None


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def test_hardening_doc_exists_and_contains_required_headings() -> None:
    text = _read(HARDENING_DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_hardening_doc_contains_required_tokens() -> None:
    text = _read(HARDENING_DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_hardening_test_file_exists_and_exercises_required_runtime_classes() -> None:
    text = _read(HARDENING_TEST_PATH)
    for symbol in (
        "InMemoryLedgerBackend",
        "make_commit_epoch_event",
        "to_decimal",
        "parse_non_negative_decimal",
        "EcuActiveLayerRuntime",
    ):
        assert symbol in text


def test_gate_script_exists_is_executable_and_wires_expected_suite() -> None:
    text = _read(GATE_SCRIPT_PATH)
    assert os.access(GATE_SCRIPT_PATH, os.X_OK)
    assert "tests/test_tier0_numeric_hardening.py" in text
    assert "tests/test_phase_636_tier0_numeric_hardening_and_closure.py" in text


def test_capsule_v3_5_exists_and_records_numeric_strike_force_outcome() -> None:
    text = _read(CAPSULE_PATH)
    assert "Capsule v3.5 supersedes v3.4." in text
    assert "Window 631-636 is closed as the Tier-0 exact-numeric constitutional," in text
    assert "Window 623+ may resume on the exact numeric Tier-0 foundation." in text


def test_handoff_636_exists_and_records_carry_forward_and_runtime_routing() -> None:
    text = _read(HANDOFF_PATH)
    assert "window_631_636_handoff_636_v0_1_closed" in text
    assert "window_623_plus_may_resume_on_exact_numeric_tier0_foundation" in text
    assert "Window 623+ may resume on the exact numeric Tier-0 foundation." in text


def test_main_commit_touches_required_deliverables_and_does_not_touch_decision_log() -> None:
    _require_commit_or_skip(PHASE_636_SUBJECT)
    commit_ref = _find_commit_ref(PHASE_636_SUBJECT)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert REQUIRED_MAIN_PATHS.issubset(changed_paths)
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_636_BACKFILL_SUBJECT)
    commit_ref = _find_commit_ref(PHASE_636_BACKFILL_SUBJECT)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_BACKFILL_PATHS
