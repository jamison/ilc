from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

ARTIFACT_PATH = Path("docs/specs/ilc_cdl_058_re_admission_boundary_scoping_512_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_512_re_admission_boundary_cdl_scoping.py")
PHASE_512_SUBJECT_TOKEN = "phase 512 re_admission_boundary cdl scoping"
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Scope description",
    "## 2. Candidate design options",
    "## 3. Dependency interactions",
    "## 4. Simulation disposition",
    "## 5. Window 515+ opening prerequisites",
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


def _resolve_phase_512_commit_ref() -> str:
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
        if PHASE_512_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError("phase_512_commit_subject_present_but_no_qualifying_scoping_commit")
    raise AssertionError("phase_512_commit_not_present_in_local_history")


def test_scoping_document_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_scoping_document_contains_required_tokens_and_exactly_one_sim_token() -> None:
    text = _read(ARTIFACT_PATH)
    assert "cdl_058_governs_re_admission_boundary" in text
    assert "cdl_058_opening_deferred_to_window_515_plus" in text
    sim_tokens = ("sim_010_sufficient", "sim_011_required")
    assert sum(token in text for token in sim_tokens) == 1


def test_scoping_document_enumerates_at_least_three_candidate_options() -> None:
    text = _read(ARTIFACT_PATH)
    candidate_lines = [
        line
        for line in text.splitlines()
        if line.startswith("- ") and ("re-entry" in line or "re-admission" in line)
    ]
    assert len(candidate_lines) >= 3


def test_live_decision_log_preserves_required_statuses_and_absences() -> None:
    commit_ref = _resolve_phase_512_commit_ref()
    # The Phase-512 CDL-058 absent check is a historical prelock reference.
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows["CDL-057"]["status"] == "ratified"
    assert rows["CDL-055"]["status"] == "ratified"
    assert rows["CDL-056"]["status"] == "ratified"
    assert "CDL-053" not in rows
    assert "CDL-058" not in rows


def test_head_commit_touches_no_runtime_files() -> None:
    assert_head_commit_touched_no_runtime_files(commit_ref="HEAD")


def test_phase_512_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_512_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_512_main_commit_does_not_touch_cdl_log_and_cdl_058_remains_absent() -> None:
    commit_ref = _resolve_phase_512_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    # The Phase-512 CDL-058 absent check is a historical prelock reference.
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert "CDL-058" not in rows
