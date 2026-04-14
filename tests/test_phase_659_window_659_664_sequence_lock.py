from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


SEQ_LOCK_PATH = Path("docs/specs/ilc_phase_659_664_sequence_lock_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_659_window_659_664_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_659_g8_window_659_664_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_659_SUBJECT_TOKEN = "phase 659 window 659-664 sequence lock"
PHASE_659_BACKFILL_SUBJECT_TOKEN = "phase 659 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQ_LOCK_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Window identity and authorization basis",
    "## 2. Practical row-6 closure target",
    "## 3. Vehicle map and admissibility split",
    "## 4. Per-phase artifact map",
    "## 5. Preserved non-goals and later-row discipline",
    "## 6. Routing and exclusions",
)
REQUIRED_TOKENS = (
    "window_659_664_sequence_lock_primary_gate",
    "cdl_065_is_row_6_coupling_invariants_vehicle",
    "row_6_is_only_checklist_closure_target_in_659_664",
    "cdl_062_opening_admissibility_is_not_option_b_selection",
    "backend_means_later_sovereign_settlement_substrate_family",
    "protocol_legitimacy_surfaces_remain_upstream_of_backend_choice",
    "agent_suitability_gates_required_for_cdl_062_admissibility",
    "legal_memo_not_formal_cdl_062_admissibility_gate",
    "rows_5_and_7_through_9_sharpened_not_closed_in_659_664",
    "option_d_posture_active_after_659",
    "no_cdl_062_opening_in_659_664",
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


def _resolve_commit_ref(*, subject_token: str, expected_paths: set[str]) -> str:
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
        if subject_token not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_token}")


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def test_sequence_lock_exists_and_contains_all_required_headings() -> None:
    text = _read(SEQ_LOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_contains_all_required_tokens() -> None:
    text = _read(SEQ_LOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_explains_upstream_downstream_backend_in_practical_terms() -> None:
    text = _read(SEQ_LOCK_PATH)
    assert "upstream means the source of canonical legitimacy or authority" in text
    assert "downstream means a later backend may record, order, anchor, finalize, or" in text
    assert "backend means a later sovereign settlement substrate family" in text
    assert "public admission and identity activation" in text
    assert "public reputation continuity" in text


def test_lock_names_cdl_065_and_forbids_cdl_062_opening_in_this_window() -> None:
    text = _read(SEQ_LOCK_PATH)
    assert "`CDL-065` is the only constitutional vehicle in Window 659-664." in text
    assert "`CDL-062` is not opened in this window." in text
    assert "no `CDL-062` opening in Window 659-664" in text


def test_lock_states_row_6_is_the_only_closure_target() -> None:
    text = _read(SEQ_LOCK_PATH)
    assert "row 6 remains the only closure target inside Window 659-664" in text
    assert "row-6 governance lock" in text


def test_lock_preserves_later_row_discipline_for_rows_5_and_7_through_9() -> None:
    text = _read(SEQ_LOCK_PATH)
    assert "row 5 remains open" in text
    assert "rows 7-9 remain open" in text
    assert "sharpening is not closure" in text


def test_decision_log_and_ilc_core_remain_out_of_scope_for_main_commit() -> None:
    _require_commit_or_skip(PHASE_659_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_659_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_659_main_and_backfill_commit_path_sets_obey_phase_scope() -> None:
    _require_commit_or_skip(PHASE_659_SUBJECT_TOKEN)
    main_commit_ref = _resolve_commit_ref(
        subject_token=PHASE_659_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(main_commit_ref) == EXACT_REQUIRED_MAIN_PATHS

    if _find_commit_ref(subject_token=PHASE_659_BACKFILL_SUBJECT_TOKEN) is None:
        pytest.skip(f"commit_not_yet_present:{PHASE_659_BACKFILL_SUBJECT_TOKEN}")
    backfill_commit_ref = _resolve_commit_ref(
        subject_token=PHASE_659_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(backfill_commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
