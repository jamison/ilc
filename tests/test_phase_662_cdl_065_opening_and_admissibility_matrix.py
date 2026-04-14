from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


OPENING_PATH = Path("docs/specs/ilc_cdl_065_coupling_invariants_governance_lock_opening_662_v0.1.md")
ADMISSIBILITY_PATH = Path("docs/specs/ilc_cdl_062_opening_admissibility_matrix_662_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_662_cdl_065_opening_and_admissibility_matrix.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_662_g8_cdl_065_opening_and_cdl_062_admissibility_matrix_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_662_SUBJECT_TOKEN = "phase 662 cdl 065 opening and admissibility split"
PHASE_662_BACKFILL_SUBJECT_TOKEN = "phase 662 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(OPENING_PATH),
    str(ADMISSIBILITY_PATH),
    str(DECISION_LOG_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_OPENING_HEADINGS = (
    "## 1. Decision target and why a constitutional vehicle is needed",
    "## 2. Practical row-6 lock scope",
    "## 3. Inherited boundaries and exclusions",
    "## 4. Candidate lock rule set",
    "## 5. Relationship to CDL-062 and Option B",
)
REQUIRED_OPENING_TOKENS = (
    "cdl_065_opened_for_coupling_invariants_governance_lock",
    "row_6_governance_lock_requires_constitutional_vehicle",
    "protocol_truth_and_public_legitimacy_remain_upstream_of_backend_choice",
    "cdl_062_not_opened_in_phase_662",
    "option_b_not_selected_in_phase_662",
)
REQUIRED_ADMISSIBILITY_HEADINGS = (
    "## 1. Purpose and boundary",
    "## 2. Formal opening-side gates",
    "## 3. Non-gates and still-later requirements",
    "## 4. Human authorization boundary",
    "## 5. Distinction from final Option-B selection",
)
REQUIRED_ADMISSIBILITY_TOKENS = (
    "cdl_062_opening_admissibility_precedes_not_equals_option_b_selection",
    "row_6_closed_required_before_cdl_062_admissible",
    "rows_7_and_8_must_be_locked_as_selection_criteria_before_cdl_062_admissible",
    "row_9_material_evidence_required_before_cdl_062_admissible",
    "row_5_must_be_narrowed_before_cdl_062_admissible",
    "agent_suitability_gates_required_before_cdl_062_admissible",
    "machine_legible_participation_gate_required_before_cdl_062_admissible",
    "harness_agnostic_access_gate_required_before_cdl_062_admissible",
    "agent_participant_parity_gate_required_before_cdl_062_admissible",
    "human_auditability_copreservation_gate_required_before_cdl_062_admissible",
    "bounded_agent_economic_participation_non_prohibition_gate_required_before_cdl_062_admissible",
    "legal_memo_not_formal_cdl_062_admissibility_gate",
    "explicit_human_go_required_for_any_future_cdl_062_opening",
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


def test_opening_document_exists_and_contains_all_required_headings() -> None:
    text = _read(OPENING_PATH)
    for heading in REQUIRED_OPENING_HEADINGS:
        assert heading in text


def test_opening_document_contains_all_required_opening_tokens() -> None:
    text = _read(OPENING_PATH)
    for token in REQUIRED_OPENING_TOKENS:
        assert token in text


def test_admissibility_matrix_exists_and_contains_all_required_headings() -> None:
    text = _read(ADMISSIBILITY_PATH)
    for heading in REQUIRED_ADMISSIBILITY_HEADINGS:
        assert heading in text


def test_admissibility_matrix_contains_all_required_tokens() -> None:
    text = _read(ADMISSIBILITY_PATH)
    for token in REQUIRED_ADMISSIBILITY_TOKENS:
        assert token in text


def test_decision_log_contains_an_open_row_for_cdl_065() -> None:
    text = _read(DECISION_LOG_PATH)
    assert "| CDL-065 |" in text
    assert "| open |" in next(line for line in text.splitlines() if line.startswith("| CDL-065 |"))


def test_decision_log_does_not_mutate_cdl_062() -> None:
    text = _read(DECISION_LOG_PATH)
    assert "| CDL-062 |" not in text


def test_admissibility_matrix_distinguishes_opening_from_final_option_b_selection() -> None:
    text = _read(ADMISSIBILITY_PATH)
    assert "It is not final `Option B` authorization." in text
    assert "the sovereign substrate lane may begin" in text
    assert "final `Option B` selection" in text


def test_admissibility_matrix_records_legal_memo_as_non_gate_carry_forward() -> None:
    text = _read(ADMISSIBILITY_PATH)
    assert "The legal memo remains real carry-forward" in text
    assert "It is not used here as a formal admissibility gate." in text


def test_admissibility_matrix_defines_all_five_derived_gates_and_does_not_promote_full_ag_set() -> None:
    text = _read(ADMISSIBILITY_PATH)
    assert "machine-legible participation:" in text
    assert "harness-agnostic access:" in text
    assert "agent-participant parity:" in text
    assert "human-auditability co-preservation:" in text
    assert "bounded agent economic participation non-prohibition:" in text
    assert "This phase does not promote the full AG gate set" in text


def test_ilc_core_remains_unchanged_and_main_backfill_paths_obey_scope() -> None:
    _require_commit_or_skip(PHASE_662_SUBJECT_TOKEN)
    main_commit_ref = _resolve_commit_ref(
        subject_token=PHASE_662_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(main_commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith("ilc_core/") for path in changed_paths)

    if _find_commit_ref(subject_token=PHASE_662_BACKFILL_SUBJECT_TOKEN) is None:
        pytest.skip(f"commit_not_yet_present:{PHASE_662_BACKFILL_SUBJECT_TOKEN}")
    backfill_commit_ref = _resolve_commit_ref(
        subject_token=PHASE_662_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    backfill_paths = _changed_paths_for_commit(backfill_commit_ref)
    assert backfill_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in backfill_paths
    assert not any(path.startswith("ilc_core/") for path in backfill_paths)
