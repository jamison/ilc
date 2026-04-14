from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


LOCK_PATH = Path("docs/specs/ilc_coupling_invariants_governance_lock_663_v0.1.md")
EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_065_coupling_invariants_governance_lock_ratification_evidence_663_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_663_cdl_065_ratification_and_row6_closure_candidate.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_663_g8_cdl_065_ratification_and_row6_closure_candidate_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_662_SUBJECT_TOKEN = "phase 662 cdl 065 opening and admissibility split"
PHASE_663_SUBJECT_TOKEN = "phase 663 cdl 065 ratification and row 6 closure candidate"
PHASE_663_BACKFILL_SUBJECT_TOKEN = "phase 663 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(LOCK_PATH),
    str(EVIDENCE_PATH),
    str(DECISION_LOG_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_LOCK_HEADINGS = (
    "## 1. Decision target and locked rule",
    "## 2. In-scope legitimacy surfaces",
    "## 3. Allowed downstream backend actions",
    "## 4. Forbidden backend actions",
    "## 5. Lineage and receipt implications",
    "## 6. What this ratification does not decide",
)
REQUIRED_LOCK_TOKENS = (
    "cdl_065_ratified_coupling_invariants_governance_lock",
    "backend_may_carry_legitimacy_not_author_it",
    "protocol_truth_and_public_legitimacy_remain_upstream_of_backend_choice",
    "namespace_quorum_settlement_and_reputation_require_protocol_lineage",
    "rows_5_and_7_through_9_not_closed_by_cdl_065",
    "cdl_062_remains_unopened_after_cdl_065_ratification",
)
REQUIRED_EVIDENCE_HEADINGS = (
    "## 1. Evidence basis",
    "## 2. Surface-matrix coverage",
    "## 3. Counterexample coverage",
    "## 4. Relationship to admissibility split",
    "## 5. Residual blockers outside row 6",
)
REQUIRED_EVIDENCE_TOKENS = (
    "phase_660_matrix_supports_cdl_065",
    "phase_661_counterexample_sweep_supports_cdl_065",
    "phase_662_opening_and_admissibility_split_supports_cdl_065",
    "row_6_closure_candidate_ready_for_window_664_gate_only_if_cdl_065_ratified",
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


def _decision_log_at(commit_ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_ref}:{DECISION_LOG_PATH.as_posix()}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def test_governance_lock_document_exists_and_contains_all_required_headings() -> None:
    text = _read(LOCK_PATH)
    for heading in REQUIRED_LOCK_HEADINGS:
        assert heading in text


def test_governance_lock_document_contains_all_required_tokens() -> None:
    text = _read(LOCK_PATH)
    for token in REQUIRED_LOCK_TOKENS:
        assert token in text


def test_ratification_evidence_document_exists_and_contains_all_required_headings() -> None:
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_EVIDENCE_HEADINGS:
        assert heading in text


def test_ratification_evidence_document_contains_all_required_tokens() -> None:
    text = _read(EVIDENCE_PATH)
    for token in REQUIRED_EVIDENCE_TOKENS:
        assert token in text


def test_decision_log_marks_cdl_065_as_ratified() -> None:
    text = _read(DECISION_LOG_PATH)
    line = next(line for line in text.splitlines() if line.startswith("| CDL-065 |"))
    assert "| ratified |" in line
    assert "ratified_phase: 663" in line
    assert "evidence_document: docs/specs/ilc_cdl_065_coupling_invariants_governance_lock_ratification_evidence_663_v0.1.md" in line


def test_decision_log_still_does_not_mutate_cdl_062() -> None:
    text = _read(DECISION_LOG_PATH)
    assert "| CDL-062 |" not in text


def test_governance_lock_text_clearly_separates_allowed_from_forbidden_backend_actions() -> None:
    text = _read(LOCK_PATH)
    assert "## 3. Allowed downstream backend actions" in text
    assert "## 4. Forbidden backend actions" in text
    assert "record already-legitimate protocol state" in text
    assert "create admission legitimacy without protocol authorization" in text


def test_governance_lock_text_explicitly_preserves_rows_5_and_7_through_9_as_open() -> None:
    text = _read(LOCK_PATH)
    assert "row 5 privacy mechanism closure" in text
    assert "row 7 censorship-resistance closure" in text
    assert "row 8 independence closure" in text
    assert "row 9 maturity closure" in text


def test_historical_opening_boundary_shows_cdl_065_was_open_before_ratification() -> None:
    opening_commit_ref = _find_commit_ref(subject_token=PHASE_662_SUBJECT_TOKEN)
    assert opening_commit_ref is not None
    opening_log = _decision_log_at(opening_commit_ref)
    line = next(line for line in opening_log.splitlines() if line.startswith("| CDL-065 |"))
    assert "| open |" in line
    assert "ratified_phase: 663" not in line


def test_ilc_core_remains_unchanged_and_main_backfill_paths_obey_phase_scope() -> None:
    _require_commit_or_skip(PHASE_663_SUBJECT_TOKEN)
    main_commit_ref = _resolve_commit_ref(
        subject_token=PHASE_663_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(main_commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith("ilc_core/") for path in changed_paths)

    if _find_commit_ref(subject_token=PHASE_663_BACKFILL_SUBJECT_TOKEN) is None:
        pytest.skip(f"commit_not_yet_present:{PHASE_663_BACKFILL_SUBJECT_TOKEN}")
    backfill_commit_ref = _resolve_commit_ref(
        subject_token=PHASE_663_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    backfill_paths = _changed_paths_for_commit(backfill_commit_ref)
    assert backfill_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in backfill_paths
    assert not any(path.startswith("ilc_core/") for path in backfill_paths)
