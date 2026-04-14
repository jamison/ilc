from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


COUNTEREXAMPLE_PATH = Path("docs/specs/ilc_coupling_counterexample_sweep_661_v0.1.md")
CRITERIA_PATH = Path("docs/specs/ilc_option_b_remaining_rows_closure_criteria_661_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_661_coupling_counterexample_and_row_sharpening.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_661_g8_counterexample_sweep_and_remaining_row_sharpening_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_661_SUBJECT_TOKEN = "phase 661 counterexample sweep and row sharpening"
PHASE_661_BACKFILL_SUBJECT_TOKEN = "phase 661 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(COUNTEREXAMPLE_PATH),
    str(CRITERIA_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_COUNTEREXAMPLE_HEADINGS = (
    "## 1. Purpose and threat model",
    "## 2. Counterexample cases",
    "## 3. Why each case fails the row-6 lock",
    "## 4. Residual ambiguity and future-lane routing",
)
REQUIRED_COUNTEREXAMPLE_TOKENS = (
    "backend_cannot_author_legitimacy_counterexample",
    "backend_cannot_override_protocol_truth_counterexample",
    "backend_cannot_inherit_namespace_without_lineage_counterexample",
    "backend_cannot_inherit_reputation_without_lineage_counterexample",
    "external_constitutional_center_veto_risk_counterexample",
)
REQUIRED_CRITERIA_HEADINGS = (
    "## 1. Purpose and status discipline",
    "## 2. Row 5 closure criteria",
    "## 3. Row 7 closure criteria",
    "## 4. Row 8 closure criteria",
    "## 5. Row 9 closure criteria",
    "## 6. Row 9 evidence starter pack",
    "## 7. Threshold work deferred to Window 665-670",
    "## 8. What this phase does not claim",
)
REQUIRED_CRITERIA_TOKENS = (
    "rows_5_7_8_9_sharpened_not_closed_in_661",
    "row_5_remains_not_started_after_661",
    "rows_7_8_9_remain_open_after_661",
    "agent_suitability_and_machine_use_matter_for_opening_not_selection_only",
    "row_9_evidence_families_locked_before_thresholds",
    "row_9_thresholds_deferred_to_window_665_670",
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


def test_counterexample_sweep_exists_and_contains_all_required_headings() -> None:
    text = _read(COUNTEREXAMPLE_PATH)
    for heading in REQUIRED_COUNTEREXAMPLE_HEADINGS:
        assert heading in text


def test_counterexample_sweep_contains_all_required_tokens() -> None:
    text = _read(COUNTEREXAMPLE_PATH)
    for token in REQUIRED_COUNTEREXAMPLE_TOKENS:
        assert token in text


def test_remaining_row_criteria_exists_and_contains_all_required_headings() -> None:
    text = _read(CRITERIA_PATH)
    for heading in REQUIRED_CRITERIA_HEADINGS:
        assert heading in text


def test_remaining_row_criteria_contains_all_required_tokens() -> None:
    text = _read(CRITERIA_PATH)
    for token in REQUIRED_CRITERIA_TOKENS:
        assert token in text


def test_row_5_is_explicitly_preserved_as_not_closed() -> None:
    text = _read(CRITERIA_PATH)
    assert "row 5 remains `not_started`" in text
    assert "Window 677-682" in text


def test_rows_7_through_9_are_explicitly_preserved_as_not_closed() -> None:
    text = _read(CRITERIA_PATH)
    assert "rows 7-9 remain open" in text
    assert "This phase does not claim:" in text
    assert "- row 7 is closed" in text
    assert "- row 8 is closed" in text
    assert "- row 9 is closed" in text


def test_criteria_artifact_names_evidence_expectations_and_future_lane_ownership() -> None:
    text = _read(CRITERIA_PATH)
    assert "Window 665-670" in text
    assert "Window 671-676" in text
    assert "Window 677-682" in text
    assert "correlation minimization and unlinkability" in text
    assert "selection-criteria document" in text
    assert "external constitutional center" in text


def test_row_9_starter_pack_names_required_evidence_families_and_defers_thresholds() -> None:
    text = _read(CRITERIA_PATH)
    assert "multi-machine canary package" in text
    assert "churn drill" in text
    assert "partition/recovery drill" in text
    assert "HTTP/2 fallback activation scenario" in text
    assert "static-peer bootstrap and operator playbook evidence" in text
    assert "metrics-table template" in text
    assert "topology size" in text
    assert "run count" in text
    assert "success thresholds" in text
    assert "recovery budgets" in text


def test_decision_log_and_ilc_core_remain_unchanged() -> None:
    _require_commit_or_skip(PHASE_661_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_661_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_661_main_and_backfill_commit_path_sets_obey_phase_scope() -> None:
    _require_commit_or_skip(PHASE_661_SUBJECT_TOKEN)
    main_commit_ref = _resolve_commit_ref(
        subject_token=PHASE_661_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(main_commit_ref) == EXACT_REQUIRED_MAIN_PATHS

    if _find_commit_ref(subject_token=PHASE_661_BACKFILL_SUBJECT_TOKEN) is None:
        pytest.skip(f"commit_not_yet_present:{PHASE_661_BACKFILL_SUBJECT_TOKEN}")
    backfill_commit_ref = _resolve_commit_ref(
        subject_token=PHASE_661_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(backfill_commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
