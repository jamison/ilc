from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

ARTIFACT_PATH = Path("docs/specs/ilc_epoch_boundary_cdl_vehicle_selection_508_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_508_epoch_boundary_cdl_vehicle_selection.py")
PHASE_508_SUBJECT_TOKEN = "phase 508 epoch boundary cdl vehicle selection"
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Candidate vehicle set",
    "## 2. Selected vehicle",
    "## 3. Rejected alternatives",
    "## 4. Scope disposition",
    "## 5. Constitutional protections",
)
VEHICLE_TOKENS = (
    "epoch_boundary_vehicle_selected = cdl_030_extension",
    "epoch_boundary_vehicle_selected = cdl_051_extension",
    "epoch_boundary_vehicle_selected = new_cdl_057",
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


def _resolve_phase_508_commit_ref() -> str:
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
        if PHASE_508_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError("phase_508_commit_subject_present_but_no_qualifying_vehicle_commit")
    raise AssertionError("phase_508_commit_not_present_in_local_history")


def test_vehicle_selection_document_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_vehicle_selection_document_contains_exactly_one_vehicle_and_blocking_scope_token() -> None:
    text = _read(ARTIFACT_PATH)
    assert sum(token in text for token in VEHICLE_TOKENS) == 1
    assert "blocking_authority_scope = deferred" in text or "blocking_authority_scope = in_scope" in text


def test_vehicle_selection_document_contains_protection_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    assert "cdl_053_unaffected" in text
    assert "cdl_030_p_e_clamp_unchanged" in text
    assert "No decision-log mutation occurs in Phase 508." in text


def test_live_decision_log_preserves_required_rows_and_absences() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-030"]["status"] == "ratified"
    assert rows["CDL-051"]["status"] == "ratified"
    assert rows["CDL-055"]["status"] == "ratified"
    assert rows["CDL-056"]["status"] == "ratified"
    assert "CDL-053" not in rows
    assert rows.get("CDL-057", {}).get("status") in {None, "open", "ratified"}


def test_head_commit_touches_no_runtime_files() -> None:
    assert_head_commit_touched_no_runtime_files(commit_ref=_resolve_phase_508_commit_ref())


def test_phase_508_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_508_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_508_main_commit_does_not_touch_cdl_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_508_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
