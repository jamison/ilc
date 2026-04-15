from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_671_676_sequence_lock_v0.1.md")
INVENTORY_PATH = Path(
    "docs/research/ilc_rows_7_8_canon_inventory_and_issue_register_671_v0.1.md"
)
TEST_PATH = Path("tests/test_phase_671_window_671_676_sequence_lock.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_671_SUBJECT_TOKENS = ("phase 671", "window 671-676 sequence lock")
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQUENCE_LOCK_PATH),
    str(INVENTORY_PATH),
    str(TEST_PATH),
}
REQUIRED_SEQUENCE_HEADINGS = (
    "## 1. Window identity and rows-7-and-8 target",
    "## 2. Inherited canon and non-goals",
    "## 3. Censorship and external-center boundary",
    "## 4. Genesis bootstrap exception and sunset discipline",
    "## 5. Exitability, replayability, and closure posture",
    "## 6. What this window may and may not close",
)
REQUIRED_SEQUENCE_TOKENS = (
    "rows_7_8_lane_locked_to_selection_criteria_not_substrate_code",
    "row_7_target_hard_censorship_and_exitability_threshold",
    "row_8_target_independence_from_external_constitutional_centers",
    "cdl_062_opening_deferred_beyond_671_676",
    "broad_censorship_model_locked_for_row_7",
    "external_constitutional_center_medium_to_broad_definition_locked",
    "genesis_bounded_bootstrap_exception_only",
    "strong_exitability_and_replayability_bar_locked",
    "row_7_closure_allowed_if_proof_obligations_are_explicit",
    "row_8_closure_allowed_on_criteria_lock_alone",
    "rows_7_8_decision_window_not_substrate_execution_window",
)
REQUIRED_INVENTORY_HEADINGS = (
    "## 1. Purpose and authority order",
    "## 2. Questions already settled by canon",
    "## 3. Questions directionally settled but not yet operationalized",
    "## 4. Questions that require human decision",
    "## 5. Immediate carry-forward obligations for later phases",
    "## 6. Immediate easy wins for later phases",
)
REQUIRED_INVENTORY_TOKENS = (
    "rows_7_8_open_questions_classified_by_authority_not_by_memory",
    "Genesis is a bounded bootstrap necessity, not informal founder discretion",
    "Genesis intervention is extraordinary, documented, sunset-bound, and not a",
    "row 9 is already closed and is not reopened in this lane",
    "Phase 672 must produce the row-7 public-legitimacy-surface threat model",
    "row 8 is the more natural candidate for full closure in this window",
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


def _subject_matches(subject: str, tokens: tuple[str, ...]) -> bool:
    lowered = subject.lower()
    return all(token in lowered for token in tokens)


def _find_commit_ref(*, subject_tokens: tuple[str, ...]) -> str | None:
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
        if _subject_matches(subject, subject_tokens):
            return commit_hash
    return None


def _resolve_commit_ref(*, subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
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
        if _subject_matches(subject, subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_tokens}")


def _require_commit_or_skip(subject_tokens: tuple[str, ...]) -> None:
    if _find_commit_ref(subject_tokens=subject_tokens) is None:
        pytest.skip(f"commit_not_yet_present:{subject_tokens}")


def test_sequence_lock_artifact_exists_and_contains_all_required_headings() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for heading in REQUIRED_SEQUENCE_HEADINGS:
        assert heading in text


def test_sequence_lock_artifact_contains_all_required_tokens() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for token in REQUIRED_SEQUENCE_TOKENS:
        assert token in text


def test_inventory_artifact_exists_and_contains_all_required_headings() -> None:
    text = _read(INVENTORY_PATH)
    for heading in REQUIRED_INVENTORY_HEADINGS:
        assert heading in text


def test_inventory_artifact_contains_all_required_tokens() -> None:
    text = _read(INVENTORY_PATH)
    for token in REQUIRED_INVENTORY_TOKENS:
        assert token in text


def test_sequence_lock_keeps_cdl_062_deferred_and_option_d_active() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "`CDL-062` remains unopened" in text
    assert "Option D remains active." in text
    assert "This phase does not authorize:" in text


def test_sequence_lock_locks_broad_censorship_and_strong_exitability() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "The locked row-7 censorship model is broad:" in text
    assert "The locked minimum bar is strong:" in text
    assert "migrate without privileged original-operator" in text


def test_inventory_records_genesis_as_bounded_exception_and_row_7_row_8_routing() -> None:
    text = _read(INVENTORY_PATH)
    assert "Genesis-rooted lineage remains canonical" in text
    assert "Genesis-operated bottlenecks" in text
    assert "Phase 673 must produce the row-8 exclusion matrix" in text
    assert "Phase 674 must produce the exitability and replayability threshold contract" in text


def test_decision_log_and_ilc_core_remain_unchanged() -> None:
    _require_commit_or_skip(PHASE_671_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_671_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
