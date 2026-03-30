from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_no_non_target_rows_marked_with_phase,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)

ARTIFACT_PATH = Path("docs/specs/ilc_cdl_058_re_admission_boundary_ratification_evidence_520_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_519_TEST_PATH = Path("tests/test_phase_519_cdl_058_prelock_hardening.py")
TEST_PATH = Path("tests/test_phase_520_cdl_058_ratification_evidence.py")
PHASE_520_SUBJECT_TOKEN = "phase 520 cdl-058 re_admission boundary ratification"
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(DECISION_LOG_PATH),
    str(PHASE_519_TEST_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Ratified lane identity",
    "## 2. Evidence anchors",
    "## 3. Rejected alternatives",
    "## 4. Constitutional boundary after ratification",
    "## 5. Governance tokens",
    "## 6. Section-5 ratification readiness evidence checklist satisfaction",
)
REQUIRED_TOKENS = (
    "cdl_058_governs_re_admission_boundary",
    "cdl_046_timed_out_orthogonal",
    "cdl_053_reserved",
    "sim_011_calibrated_cooldown_constants",
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


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_ref}:{path}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_520_commit_ref() -> str:
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
        if PHASE_520_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError("phase_520_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_520_commit_not_present_in_local_history")


def _baseline_decision_log_text() -> str:
    try:
        commit_ref = _resolve_phase_520_commit_ref()
    except AssertionError:
        return _read(DECISION_LOG_PATH)
    return _commit_text(str(DECISION_LOG_PATH), f"{commit_ref}^")


def test_ratification_evidence_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_ratification_evidence_contains_required_governance_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "No ilc_core/ mutation occurs in Phase 520." in text


def test_ratification_evidence_records_all_required_anchors() -> None:
    text = _read(ARTIFACT_PATH)
    assert "docs/specs/ilc_cdl_058_re_admission_boundary_scoping_512_v0.1.md" in text
    assert "docs/specs/ilc_sim_011_re_admission_boundary_calibration_517_v0.1.md" in text
    assert "docs/specs/ilc_cdl_058_re_admission_boundary_opening_stub_518_v0.1.md" in text
    assert "docs/specs/ilc_cdl_058_re_admission_boundary_prelock_hardening_519_v0.1.md" in text


def test_live_decision_log_marks_cdl_058_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-055"]["status"] == "ratified"
    assert rows["CDL-056"]["status"] == "ratified"
    assert rows["CDL-057"]["status"] == "ratified"
    assert rows["CDL-058"]["status"] == "ratified"
    assert rows["CDL-058"]["ratified_phase"] == "520"
    assert "CDL-053" not in rows


def test_live_decision_log_preserves_cdl_055_cdl_056_and_cdl_057_rows() -> None:
    baseline_rows = parse_decision_register_rows(_baseline_decision_log_text())
    live_rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert live_rows["CDL-055"] == baseline_rows["CDL-055"]
    assert live_rows["CDL-056"] == baseline_rows["CDL-056"]
    assert live_rows["CDL-057"] == baseline_rows["CDL-057"]


def test_phase_520_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_520_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_520_main_commit_ratifies_cdl_058_without_non_target_row_drift() -> None:
    commit_ref = _resolve_phase_520_commit_ref()
    old_text = _commit_text(str(DECISION_LOG_PATH), f"{commit_ref}^")
    new_text = _commit_text(str(DECISION_LOG_PATH), commit_ref)
    rows = parse_decision_register_rows(new_text)
    assert rows["CDL-058"]["status"] == "ratified"
    assert rows["CDL-058"]["ratified_phase"] == "520"
    assert rows["CDL-055"]["status"] == "ratified"
    assert rows["CDL-056"]["status"] == "ratified"
    assert rows["CDL-057"]["status"] == "ratified"
    assert "CDL-053" not in rows
    assert_only_allowed_row_mutations(old_text, new_text, "CDL-058")
    assert_no_non_target_rows_marked_with_phase(rows, phase="520", target_cdls={"CDL-058"})
