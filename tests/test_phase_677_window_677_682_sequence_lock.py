from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_677_682_sequence_lock_v0.1.md")
INVENTORY_PATH = Path("docs/research/ilc_row_5_canon_inventory_and_issue_register_677_v0.1.md")
GROUPING_PATH = Path("docs/specs/ilc_window_677_682_candidate_phase_grouping_v0.1.md")
FRAME_PATH = Path(
    "docs/research/ilc_window_677_682_privacy_public_legitimacy_conversation_frame_2026_04_15_v0.1.md"
)
TEST_PATH = Path("tests/test_phase_677_window_677_682_sequence_lock.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_677_SUBJECT_TOKENS = ("phase 677", "row 5 privacy lane")
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQUENCE_LOCK_PATH),
    str(INVENTORY_PATH),
    str(GROUPING_PATH),
    str(FRAME_PATH),
    str(TEST_PATH),
}
REQUIRED_SEQUENCE_HEADINGS = (
    "## 1. Window identity and row-5 target",
    "## 2. Inherited canon and non-goals",
    "## 3. Protected thing and adversary boundary",
    "## 4. Observability floor and inadmissibility boundary",
    "## 5. Mechanism-family posture and sequencing risk",
    "## 6. Window outcome posture and remaining gap discipline",
)
REQUIRED_SEQUENCE_TOKENS = (
    "row_5_lane_locked_to_pre_substrate_privacy_narrowing_not_final_mechanism_closure",
    "row_5_problem_locked_to_public_submission_correlation_minimization_not_hide_all_private_work",
    "row_5_partial_not_closure_target_locked_for_677_682",
    "cdl_062_opening_and_final_substrate_selection_deferred_beyond_677_682",
    "identity_cross_submission_and_receipt_linkage_protection_locked_as_minimum_target",
    "hosted_query_surface_adversary_explicitly_in_scope",
    "operator_path_and_indexer_adversaries_locked_as_minimum_scope",
    "strong_row_5_observability_floor_locked",
    "specialized_tooling_required_for_default_public_legitimacy_verification_is_inadmissible",
    "receipt_lineage_machine_legibility_challengeability_and_bounded_human_auditability_nonnegotiable",
    "three_bucket_mechanism_family_posture_locked_for_680",
    "later_stage_bucket_reserved_for_nullifier_and_heavier_zk_families",
    "phase_681_scopes_to_phase_680_survivor_set_and_may_iterate_back_if_matrix_too_wide",
    "materially_harder_requires_metric_not_narrative_only",
    "phase_682_must_state_remaining_row_5_gap_explicitly",
    "row_5_advancement_requires_bounded_partial_with_carry_forward_packet",
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
    "row_5_open_questions_classified_by_authority_not_by_memory",
    "Phase 611 classifies row 5 as a real Option-B graduation blocker",
    "the tractable privacy problem is correlation minimization and unlinkability",
    "Phase 678 must treat hosted-query surfaces as a named surveillance vector",
    "Phase 679 must lock the observability budget as a hard constraint artifact",
    "Phase 682 must state the remaining row-5 gap explicitly if the row advances",
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


def test_sequence_lock_keeps_cdl_062_closed_and_row_5_partial_only() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "`CDL-062` remains unopened" in text
    assert "Option D remains active" in text
    assert "row 5 does not close in Window 677-682" in text


def test_grouping_records_hosted_query_scope_and_phase_681_iterate_back_risk() -> None:
    text = _read(GROUPING_PATH)
    assert "hosted-query-surface aggregation as its own practical surveillance class" in text
    assert "phase sequencing note: this phase scopes to the surviving shortlist from" in text
    assert "may force a controlled iterate-back if the Phase 680 matrix is" in text


def test_frame_records_three_bucket_posture_and_partial_only_result() -> None:
    text = _read(FRAME_PATH)
    assert "`E`, operationalized as `C` plus an explicit later-stage bucket" in text
    assert "hosted-query-surface aggregation deserves explicit treatment" in text
    assert "the eventual 682 decision record should explicitly state the remaining gap" in text
    assert "Minimum acceptable result:" in text


def test_decision_log_and_ilc_core_remain_unchanged() -> None:
    _require_commit_or_skip(PHASE_677_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_677_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
