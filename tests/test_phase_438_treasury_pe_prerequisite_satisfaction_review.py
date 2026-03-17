"""Phase 438 Treasury P_e prerequisite-satisfaction review tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

REVIEW_PATH = Path("docs/specs/ilc_treasury_pe_prerequisite_satisfaction_review_438_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_438_COMMIT_SUBJECT = "docs(g8): phase 438 treasury pe prerequisite-satisfaction review"


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_438_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    required_paths = {
        str(REVIEW_PATH),
        "tests/test_phase_438_treasury_pe_prerequisite_satisfaction_review.py",
    }
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_438_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if changed_paths == required_paths:
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_438_commit_subject_present_but_no_qualifying_review_commit")
    raise AssertionError("phase_438_commit_not_present_in_local_history")


def _assert_phase_438_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    required_paths = {
        str(REVIEW_PATH),
        "tests/test_phase_438_treasury_pe_prerequisite_satisfaction_review.py",
    }
    assert changed_paths == required_paths, f"phase_438_scope_mismatch:{sorted(changed_paths)}"
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
    assert "tools/runtime_baseline.py" not in changed_paths


def test_review_artifact_has_required_headings() -> None:
    text = REVIEW_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Review question and inherited evidence base",
        "## 2. Phase-431 prerequisite check",
        "## 3. Current readiness verdict for future CDL-050 opening",
        "## 4. Carry-forward controls and non-goals",
        "## 5. Phase 439 pointer",
    ):
        assert heading in text


def test_review_artifact_contains_required_prerequisite_and_verdict_tokens() -> None:
    text = REVIEW_PATH.read_text(encoding="utf-8")
    for token in (
        "Phase 438 reviews whether any Phase-431 prerequisite is satisfied strongly enough to justify a future CDL-050 opening.",
        "Prerequisite 1 (decoupled recovery criterion): NOT SATISFIED.",
        "Prerequisite 2 (explicit treasury-risk tolerance judgment): NOT SATISFIED.",
        "Prerequisite 3 (additional discriminating simulation evidence): NOT SATISFIED.",
        "The trigger-coupled recovery criterion identified in Phase 430 remains unresolved.",
        "The intervention-limit sub-choice remains underdetermined within the trigger=0.20 cluster.",
        "The SIM-009 pair 0.2 / 0.02 remains a provisional planning anchor only and is not constitutional lock-ready.",
        "CDL-050 opening is still not justified at the close of Phase 438.",
        "No decision-log mutation occurred in Phase 438.",
        "No runtime mutation occurred in Phase 438.",
        "Phase 439 is the next authorized coherence and capsule v1.8 phase.",
    ):
        assert token in text


def test_review_artifact_records_all_prerequisites_unsatisfied() -> None:
    text = REVIEW_PATH.read_text(encoding="utf-8")
    assert text.count("NOT SATISFIED") == 3


def test_review_artifact_records_provisional_anchor_and_non_readiness() -> None:
    text = REVIEW_PATH.read_text(encoding="utf-8")
    assert "0.2 / 0.02" in text
    assert "not constitutional lock-ready" in text


def test_review_artifact_records_non_goals_and_next_phase() -> None:
    text = REVIEW_PATH.read_text(encoding="utf-8")
    for token in (
        "- no `CDL-050` opening,",
        "- no Treasury `P_e` ratification work,",
        "- no new simulation commissioning,",
        "- no release-engineering packaging/bootstrap merge.",
        "Phase 439 is the next authorized coherence and capsule v1.8 phase.",
    ):
        assert token in text


def test_phase_438_commit_did_not_mutate_decision_log() -> None:
    commit_ref = _resolve_phase_438_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_phase_438_scope_is_exact() -> None:
    commit_ref = _resolve_phase_438_commit_ref()
    _assert_phase_438_scope(commit_ref)
