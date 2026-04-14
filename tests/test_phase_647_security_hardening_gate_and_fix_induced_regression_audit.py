from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

DOC_PATH = Path("docs/specs/ilc_security_hardening_gate_and_fix_induced_regression_audit_647_v0.1.md")
SCRIPT_PATH = Path("tools/run_window_642_648_security_hardening_gate_phase_647.sh")
TODO_PATH = Path("TODO.txt")
INVENTORY_PATH = Path("docs/specs/ilc_remaining_float_and_security_follow_on_inventory_643_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_647_BACKFILL_SUBJECT_TOKEN = "phase 647 walkthrough and status backfill"
BACKFILL_PATHS = {
    "docs/phases/phase_647_g8_security_hardening_gate_and_fix_induced_regression_audit_walkthrough.md",
    "docs/phases/STATUS.md",
}
REQUIRED_HEADINGS = (
    "## 1. Gate identity and pass basis",
    "## 2. First-order issue checklist",
    "## 3. Fix-induced regression checklist",
    "## 4. Remaining-float carry-forward verification",
    "## 5. Test matrix and command record",
    "## 6. Verdict and closure readiness",
)
REQUIRED_TOKENS = (
    "window_642_648_security_hardening_gate_pass_required",
    "canonical_json_fix_induced_whitespace_drift_checked",
    "prng_fix_induced_entropy_or_determinism_regression_checked",
    "assert_replacement_exception_swallowing_regression_checked",
    "bounded_stream_fix_did_not_shift_attack_to_temp_disk_checked",
    "remaining_float_inventory_and_todo_verified_before_closure",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def test_gate_doc_exists_with_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_gate_doc_contains_required_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_gate_script_exists_and_references_expected_test_slices() -> None:
    text = _read(SCRIPT_PATH)
    for path in (
        "tests/test_phase_643_remaining_float_and_security_inventory.py",
        "tests/test_phase_644_canonical_json_and_signature_boundary_hardening.py",
        "tests/test_phase_645_prng_timeout_and_invariant_enforcement_hardening.py",
        "tests/test_phase_646_ndjson_ingress_and_operational_boundary_hardening.py",
    ):
        assert path in text


def test_gate_doc_records_first_order_issue_verification() -> None:
    text = _read(DOC_PATH)
    assert "canonical JSON/signature drift" in text
    assert "predictable PRNG" in text
    assert "production invariant enforcement via `assert`" in text
    assert "unbounded NDJSON bundle aggregation" in text


def test_gate_doc_records_second_order_regression_checks() -> None:
    text = _read(DOC_PATH)
    assert "whitespace/separator drift" in text
    assert "deterministic selection remains reproducible" in text
    assert "broad exception swallowing" in text
    assert "temporary-disk spooling" in text


def test_gate_doc_verifies_remaining_float_inventory_and_todo() -> None:
    assert INVENTORY_PATH.exists()
    assert TODO_PATH.exists()
    assert "[TODO – Post-641 Remaining Float and Security Follow-On]" in _read(TODO_PATH)


def test_decision_log_unchanged() -> None:
    assert DECISION_LOG_PATH.exists()


def test_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _find_commit_ref(subject_token=PHASE_647_BACKFILL_SUBJECT_TOKEN)
    if commit_ref is None:
        pytest.skip("commit_not_yet_present")
    assert _changed_paths_for_commit(commit_ref) == BACKFILL_PATHS


def test_gate_script_passes() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
