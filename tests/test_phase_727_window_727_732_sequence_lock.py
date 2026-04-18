from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_phase_727_732_sequence_lock_v0.1.md")
TEST_PATH = Path("tests/test_phase_727_window_727_732_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_727_g8_window_727_732_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Inherited gates and constraints",
    "## 3. Window meaning",
    "## 4. Phase table and sequencing",
    "## 5. Explicit separation obligations",
    "## 6. Non-goals",
    "## 7. Source inputs",
)
REQUIRED_TOKENS = (
    "window_727_732_sequence_lock_active",
    "adjacent_gated_economy_hardening_window_active",
    "no_pre_window_conversation_required_for_727_732",
    "no_financial_shard_activation_in_window_727_732",
    "no_cdl_ratification_planned_in_window_727_732",
    "cdl_017_text_review_permitted_but_not_ratifiable_in_window_727_732",
    "track_b_m016_complete_m017_next",
)
PHASE_MAIN_SUBJECT = ("phase 727", "window 727-732 sequence lock")
PHASE_BACKFILL_SUBJECT = ("phase 727", "walkthrough", "backfill")
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
    raise AssertionError("phase_727_commit_not_present_in_local_history")


def _try_resolve_commit_ref(
    subject_tokens: tuple[str, ...], expected_paths: set[str]
) -> str | None:
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


def test_artifact_records_window_identity_and_track_b_baseline() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Window `723-726` is closed. Capsule `v4.9` is the live main-lane frontier" in text
    assert "`CDL-062` remains open as the bounded\nsovereign-substrate research lane" in text
    assert "the live tail shows `M-016` complete and the next\nplanned M-phase as `M-017`" in text


def test_artifact_records_phase_table_and_closure_phase() -> None:
    text = _read(ARTIFACT_PATH)
    assert "| 1 | 727 | sequence lock |" in text
    assert "| 6 | 732 | capsule v5.0 and closure gate |" in text
    assert "Phase `728` selects the adjacent carry-forward lane without opening a new CDL." in text
    assert "Closure phase is Phase `732`." in text


def test_artifact_records_non_ratification_and_separation_boundaries() -> None:
    text = _read(ARTIFACT_PATH)
    assert "This is a hardening and boundary window, not an activation, ratification, or\nruntime-implementation window." in text
    assert "`CDL-062` remains the sovereign-substrate research lane and is not merged" in text
    assert "ADR-0022 remains the architectural boundary anchor" in text
    assert "does not claim that `M-016` solved the stronger public-substrate\nreplayability question" in text


def test_decision_log_and_runtime_surfaces_remain_unmutated_in_this_phase() -> None:
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
        ["git", "diff", "--cached", "--name-only", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert not result_decision.stdout.strip()


def test_phase_727_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_727_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
