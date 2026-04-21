from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_phase_763_766_sequence_lock_v0.1.md")
TEST_PATH = Path("tests/test_phase_763_window_763_766_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_763_g8_cdl_017_ratification_window_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline and authority order",
    "## 2. Inherited ratification constraints",
    "## 3. Window meaning",
    "## 4. Constitutional interaction boundaries at open",
    "## 5. Phase table and sequencing",
    "## 6. Explicit non-conflation obligations",
    "## 7. Non-goals",
    "## 8. Source inputs",
)
REQUIRED_TOKENS = (
    "window_763_766_sequence_lock_active",
    "cdl_017_ratification_window_active",
    "cdl_017_ratification_window_open_approved_by_reviewer",
    "track_b_m022_complete_convergence_closed_cdl_017_window_open",
    "row_5_spec_closed_runtime_pending_at_window_open",
    "row_7_runtime_closed_at_window_open",
    "row_8_inherited_candidate_evaluation_pending_at_window_open",
    "sec_004_activation_scope_post_ratification_only",
    "first_non_genesis_validator_deployment_requires_separate_human_gate",
    "no_m007_hook_activation_in_window_763_766",
)
PHASE_MAIN_SUBJECT = ("phase 763", "cdl-017 ratification window sequence lock")
PHASE_BACKFILL_SUBJECT = ("phase 763", "walkthrough", "planning backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
    str(PLANNING_INDEX_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


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
    raise AssertionError("phase_763_commit_not_present_in_local_history")


def test_artifact_exists_and_contains_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_artifact_records_live_frontier_and_reviewer_approval_transition() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Capsule `v5.4` is the latest published main-lane capsule at sequence-lock time." in text
    assert "`CDL-017` remains open and unratified." in text
    assert "Row `5` remains `spec_closed_runtime_pending` with an honest fail record." in text
    assert "Row `7` is `runtime_closed`." in text
    assert "Row `8` remains inherited as a criteria-locked surface with no candidate evaluation." in text
    assert "`M-022 complete; convergence window closed; later CDL-017 ratification window pending reviewer approval`" in text
    assert "Reviewer approval has now been supplied explicitly, so this phase opens the later `CDL-017` ratification window" in text


def test_artifact_records_sec_004_activation_scope_and_acceptance_condition() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "`TransferCertificate` must gain `epoch: EpochSeq`" in text
    assert "certificate verification must resolve the historically active `ValidatorSet` for that epoch" in text
    assert "`test_ejected_validator_sig_rejected_after_epoch_boundary`" in text
    assert "this implementation work begins only after `CDL-017` ratifies" in text
    assert "may imply that SEC-004 is already implemented" in text


def test_artifact_preserves_genesis_only_human_gate_and_no_hook_activation_boundary() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Genesis-only authority remains operative for the near-term testnet" in text
    assert "ratification is not deployment" in text
    assert "ratification is not hook activation" in text
    assert "The first non-Genesis validator remains a later operator decision after ratification" in text
    assert "`admit_validator` is still `unimplemented!`" in text
    assert "`eject_validator` is still `unimplemented!`" in text
    assert "that disabled state remains correct throughout this window" in text


def test_artifact_requires_explicit_cdl_055_and_cdl_056_carry_forward_or_amendment_matrix() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "`CDL-055` and `CDL-056` may not be silently superseded; carry-forward versus amendment must be explicit" in text
    assert "Phase `764` must publish an explicit carry-forward / amendment matrix for `CDL-055` and `CDL-056`" in text
    assert "validator participation stake, liveness penalties, equivocation slash, and re-admission separation remain anchored to `CDL-055`" in text
    assert "validator trust-tier elevation remains non-inheritable and tied to the ratified `CDL-055` liveness threshold per `CDL-056`" in text


def test_artifact_records_phase_table_and_single_row_mutation_discipline() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "| 1 | 763 | sequence lock | gate / constitutional planning |" in text
    assert "| 2 | 764 | CDL-017 interaction synthesis and activation-boundary record | constitutional evidence synthesis |" in text
    assert "| 3 | 765 | CDL-017 ratification and decision-log mutation | constitutional ratification |" in text
    assert "| 4 | 766 | coherence report + capsule v5.5 + closure gate | gate / handoff |" in text
    assert "Phase `765` must follow the two-commit ratification discipline" in text
    assert "commit 2 mutates exactly the `CDL-017` row" in text
    assert "The Phase `765` second commit may touch only the `CDL-017` row and no other file." in text


def test_decision_log_and_runtime_surfaces_are_untouched_in_phase_763() -> None:
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_763_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
    assert not any(
        path == "ilc_consensus" or path.startswith("ilc_consensus/")
        for path in changed_paths
    )


def test_phase_763_backfill_commit_touches_walkthrough_status_and_planning_index_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
    assert not any(
        path == "ilc_consensus" or path.startswith("ilc_consensus/")
        for path in changed_paths
    )


def test_backfill_surfaces_record_active_window_state() -> None:
    status_text = _normalized(_read(STATUS_PATH))
    planning_text = _normalized(_read(PLANNING_INDEX_PATH))
    walkthrough_text = _normalized(_read(WALKTHROUGH_PATH))
    assert "## Phase 763" in status_text
    assert "CDL-017 ratification window sequence lock" in status_text
    assert "**Next planned phase:** Phase 764" in status_text
    assert "CDL-017 ratification window ACTIVE through Phase 763" in planning_text
    assert "Active CDL-017 Ratification Sequence Lock" in planning_text
    assert "reviewer-approved transition from the closed convergence frontier into the later CDL-017 ratification window" in walkthrough_text
