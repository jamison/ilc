from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

REPORT_PATH = Path("docs/specs/ilc_ecu_active_layer_runtime_hardening_gate_629_v0.1.md")
PHASE_TEST_PATH = Path("tests/test_phase_629_ecu_active_layer_runtime_hardening_gate.py")
HARDENING_TEST_PATH = Path("tests/test_ecu_active_layer_runtime_hardening.py")
GATE_SCRIPT_PATH = Path("tools/run_window_624_630_runtime_hardening_gate_phase_629.sh")
RUNTIME_PATH = Path("ilc_core/ledger/ecu_active_layer_runtime.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_629_g8_ecu_active_layer_runtime_hardening_gate_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_629_SUBJECT = "phase 629 ecu active layer runtime hardening gate"
PHASE_629_BACKFILL_SUBJECT = "phase 629 walkthrough and status backfill"
EXPECTED_MAIN_PATHS = {
    str(REPORT_PATH),
    str(PHASE_TEST_PATH),
    str(HARDENING_TEST_PATH),
    str(GATE_SCRIPT_PATH),
}
EXPECTED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Gate identity and authority",
    "## 2. Runtime surface under test",
    "## 3. Hardening suite executed",
    "## 4. Findings and fix-loop disposition",
    "## 5. Gate verdict",
    "## 6. Carry-forward constraints",
)
REQUIRED_TOKENS = (
    "ecu_active_layer_runtime_hardening_gate_629_locked",
    "runtime_hardening_gate_phase_629_executed",
    "fix_loop_completed_within_phase_629",
    "bounded_ecu_runtime_no_wallet_widening_confirmed",
    "ecu_debit_not_ilc_payment_629",
    "runtime_hardening_gate_verdict_pass",
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


def _find_commit_ref(*, subject_token: str) -> str | None:
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
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def _resolve_commit_ref(*, subject_token: str) -> str:
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
    raise AssertionError(f"commit_not_present_in_local_history:{subject_token}")


def test_hardening_report_contains_required_headings() -> None:
    text = _read(REPORT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_hardening_report_contains_required_tokens() -> None:
    text = _read(REPORT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_three_lists_full_hardening_suite() -> None:
    text = _read(REPORT_PATH)
    for phrase in (
        "oversubscription prevention across `proposed`, `accepted`, and `delivered`",
        "delivered earmarks remain reserved until `debited`",
        "epoch-commit debit only",
        "expiry release without rollover",
        "idempotent commit processing for previously debited and expired earmarks",
        "stable `earmark_status` and `earmark_history` output",
        "no wallet widening and no ILC transfer path",
        "Decimal-based exact internal accounting",
    ):
        assert phrase in text


def test_section_four_records_fix_loop_disposition() -> None:
    text = _read(REPORT_PATH)
    assert "Fix-1 required" in text
    assert "Fix-1 landed in Phase 629" in text
    assert "No additional fix loop was required" in text


def test_section_five_states_pass_and_bounded_constraints_preserved() -> None:
    text = _read(REPORT_PATH)
    assert "Verdict: PASS." in text
    assert "no wallet widening" in text
    assert "no ILC transferability" in text


def test_gate_script_exists_executable_and_wires_expected_suite() -> None:
    text = _read(GATE_SCRIPT_PATH)
    assert "tests/test_phase_628_ecu_active_layer_runtime_and_accounting_spec.py" in text
    assert "tests/test_ecu_active_layer_runtime.py" in text
    assert "tests/test_ecu_active_layer_runtime_hardening.py" in text
    assert "tests/test_phase_629_ecu_active_layer_runtime_hardening_gate.py" in text
    mode = GATE_SCRIPT_PATH.stat().st_mode
    assert bool(mode & stat.S_IXUSR)


def test_hardening_test_file_runs_and_proves_required_protections() -> None:
    result = subprocess.run(
        [
            "bash",
            "-lc",
            "PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_ecu_active_layer_runtime_hardening.py -q",
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    assert "passed" in result.stdout


def test_main_commit_touches_expected_paths_plus_runtime_if_fix_required() -> None:
    _require_commit_or_skip(PHASE_629_SUBJECT)
    commit_ref = _resolve_commit_ref(subject_token=PHASE_629_SUBJECT)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths in (
        EXPECTED_MAIN_PATHS,
        EXPECTED_MAIN_PATHS | {str(RUNTIME_PATH)},
    )
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_629_BACKFILL_SUBJECT)
    commit_ref = _resolve_commit_ref(subject_token=PHASE_629_BACKFILL_SUBJECT)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXPECTED_BACKFILL_PATHS
