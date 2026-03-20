from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
)

SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_450_459_sequence_lock_v0.1.md")
LANE_FREEZE_PATH = Path("docs/specs/ilc_cdl_050_lane_identity_freeze_450_v0.1.md")
TEST_PATH = Path("tests/test_phase_450_window_sequence_lock_and_lane_identity_freeze.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_450_SUBJECT = "docs(g8): phase 450 window 450-459 sequence lock and cdl-050 lane identity freeze"
FORBIDDEN_TREASURY_TOKEN = "ILC_CDL_MUTATION_" + "AUTHORIZED"
OPTION_A = "CDL-050 is reframed in place as the Treasury ECU-governor lane."
OPTION_B = "CDL-050 remains narrow and a new CDL carries the broader ECU-governor model."
MAIN_COMMIT_PATHS = {
    str(SEQUENCE_LOCK_PATH),
    str(LANE_FREEZE_PATH),
    str(TEST_PATH),
}
RELEASE_ENGINEERING_PREFIXES = (
    "release/",
    "bootstrap/",
    "packaging/",
    "docs/release",
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


def _resolve_phase_450_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_450_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == MAIN_COMMIT_PATHS:
            return commit_ref

    if matches:
        raise AssertionError("phase_450_commit_subject_present_but_no_qualifying_sequence_lock_commit")
    raise AssertionError("phase_450_commit_not_present_in_local_history")


def test_sequence_lock_exists_and_contains_required_headings() -> None:
    assert SEQUENCE_LOCK_PATH.exists()
    text = _read(SEQUENCE_LOCK_PATH)
    for heading in (
        "## 1. Window identity",
        "## 2. Entry conditions",
        "## 3. Phase sequence",
        "## 4. CDL-050 opening gates",
        "## 5. Non-goals",
        "## 6. Failure path",
    ):
        assert heading in text


def test_sequence_lock_contains_required_tokens_and_final_row() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for token in (
        "Window 441-449 is closed.",
        "CDL-051 is ratified at Phase 450 entry.",
        "CDL-050 remains unopened at Phase 450 entry.",
        "Window 450-459 is the Treasury ECU-Governor and CDL-050 Closure Block.",
        "Phase 450 opens the Window 450-459 constitutional block.",
        "CDL-050 does not open unless Gates 1 through 7 are satisfied.",
        "Phase 456 is the blocker-clearance gate; if it does not publish a clean pass on all required gates, Phases 457-459 must not proceed.",
        "Phase 459 is the final ratification gate for Window 450-459.",
        "Phase 450 does not authorize Phase 460+ by itself; any move beyond Window 450-459 requires a new sequence lock or amendment.",
        "| 10 | 459 | CDL-050 ratification | Constitutional | SENSITIVE |",
    ):
        assert token in text


def test_lane_identity_freeze_doc_exists_and_contains_required_headings() -> None:
    assert LANE_FREEZE_PATH.exists()
    text = _read(LANE_FREEZE_PATH)
    for heading in (
        "## 1. Decision",
        "## 2. Rationale",
        "## 3. Non-goals frozen for Window 450-459",
        "## 4. Gate-condition summary",
        "## 5. Non-authorization statement",
    ):
        assert heading in text


def test_lane_identity_freeze_doc_contains_exactly_one_binary_decision_token() -> None:
    text = _read(LANE_FREEZE_PATH)
    present = [token for token in (OPTION_A, OPTION_B) if token in text]
    assert present == [OPTION_A]


def test_lane_identity_freeze_doc_contains_required_non_decision_tokens() -> None:
    text = _read(LANE_FREEZE_PATH)
    for token in (
        "CDL-050 lane identity is frozen as of Phase 450.",
        "This decision cannot be changed within Window 450-459 without a new sequence lock amendment.",
        "No CDL-050 opening or ratification occurs in Phase 450.",
        "No Treasury P_e constants are authorized in Phase 450.",
        "Jubilee",
        "node-rent lifecycle",
        "release-engineering",
    ):
        assert token in text


def test_no_forbidden_treasury_mutation_token_in_deliverables_or_test() -> None:
    for path in (SEQUENCE_LOCK_PATH, LANE_FREEZE_PATH, TEST_PATH):
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)


def test_phase_450_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_450_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == MAIN_COMMIT_PATHS


def test_phase_450_commit_respects_non_mutation_boundaries() -> None:
    commit_ref = _resolve_phase_450_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
    assert not any(
        path.startswith(prefix)
        for path in changed
        for prefix in RELEASE_ENGINEERING_PREFIXES
    )
