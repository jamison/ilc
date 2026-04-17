from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_phase_707_712_sequence_lock_v0.1.md")
TEST_PATH = Path("tests/test_phase_707_window_707_712_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_707_g8_window_707_712_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Inherited gates and constraints",
    "## 3. Window meaning",
    "## 4. Phase table and sequencing",
    "## 5. Phase-specific prerequisites",
    "## 6. Non-goals",
    "## 7. Source inputs",
)
REQUIRED_TOKENS = (
    "window_707_712_sequence_lock_active",
    "cdl_066_and_cdl_067_ratification_routed_in_window_707_712",
    "cdl_017_prelock_only_not_ratified_in_window_707_712",
    "q1_q6_answers_required_before_phase_710_execution",
    "cdl_062_option_b_selection_not_in_scope_707_712",
    "track_b_status_must_be_verified_from_status_tail",
)
PHASE_MAIN_SUBJECT = ("phase 707", "window 707-712 sequence lock")
PHASE_BACKFILL_SUBJECT = ("phase 707", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}


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


def _resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
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
        lowered = subject.lower()
        if all(token in lowered for token in subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError("phase_707_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_artifact_exists_and_contains_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_artifact_locks_ratification_boundary_and_non_goals() -> None:
    text = _read(ARTIFACT_PATH)
    assert "only `CDL-066` and `CDL-067` are in-window ratification targets" in text
    assert "`CDL-017` remains prelock-only" in text
    assert "no ratification of `CDL-017`" in text
    assert "no opening of `CDL-062`" in text
    assert "no final Option B production selection" in text


def test_artifact_records_phase_table_and_decision_log_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert "| 1 | 707 | sequence lock |" in text
    assert "| 6 | 712 | closure |" in text
    assert "only Phases `708-709` may mutate the constitutional decision log" in text
    assert "Phase `712` may summarize only what Phases `708-711` actually establish" in text


def test_artifact_records_q1_q6_prerequisite_and_track_b_rule() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Q1-Q6 answers must already exist from conversation with the local reviewer" in text
    assert "docs/research/ilc_validator_agent_q1_q6_prewindow_resolution_v0.1.md" in text
    assert "Track B status must be rechecked from `STATUS.md` tail" in text


def test_decision_log_remains_unmutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
    )
    if main_commit and backfill_commit:
        for commit_ref in (main_commit, backfill_commit):
            changed_paths = _changed_paths_for_commit(commit_ref)
            assert str(DECISION_LOG_PATH) not in changed_paths
            assert not any(
                path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths
            )
            assert not any(
                path == "ilc_consensus" or path.startswith("ilc_consensus/")
                for path in changed_paths
            )
        return

    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_707_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_707_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
