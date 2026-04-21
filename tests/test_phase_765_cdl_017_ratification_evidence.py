from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path(
    "docs/specs/ilc_cdl_017_validator_governance_framework_ratification_evidence_765_v0.1.md"
)
TEST_PATH = Path("tests/test_phase_765_cdl_017_ratification_evidence.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_765_g8_cdl_017_ratification_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_764_PATH = Path(
    "docs/specs/ilc_cdl_017_interaction_synthesis_and_activation_boundary_record_764_v0.1.md"
)

REQUIRED_HEADINGS = (
    "## 1. Phase 764 carry-forward verdicts re-read verbatim",
    "## 2. SEC-004 post-ratification implementation scope re-read",
    "## 3. Ratified constitutional decision",
    "## 4. Preserved activation boundary at ratification",
    "## 5. Preserved non-conflation obligations",
    "## 6. Two-commit mutation discipline and decision-log consequence",
    "## 7. Preserved exclusions and non-goals",
)
REQUIRED_TOKENS = (
    "cdl_017_ratification_evidence_765_complete",
    "cdl_017_ratified_validator_governance_framework_lane",
    "phase_764_carry_forward_verdicts_reread_verbatim_in_phase_765",
    "cdl_068_adjacent_lane_reaffirmed_unchanged_in_phase_765",
    "sec_004_post_ratification_scope_reread_with_named_acceptance_test",
    "ratification_opens_validator_governance_lane_only_in_phase_765",
    "first_non_genesis_validator_deployment_human_gate_preserved_after_cdl_017_ratification",
    "m007_hooks_remain_unimplemented_after_cdl_017_ratification",
    "phase_765_commit_1_does_not_mutate_decision_log",
    "phase_765_commit_2_mutates_only_cdl_017_row",
)
COMMIT1_SUBJECT = ("phase 765", "cdl-017 ratification evidence")
COMMIT2_SUBJECT = ("phase 765", "cdl-017 decision log ratification")
COMMIT1_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
    str(PLANNING_INDEX_PATH),
}
COMMIT2_PATHS = {str(DECISION_LOG_PATH)}
VERBATIM_PHASE_764_STRINGS = (
    "`CDL-017` does not alter validator participation stake, liveness penalties,\n> equivocation slash boundary, or the separate re-admission boundary. These\n> remain governed by ratified `CDL-055`.",
    "`CDL-017` does not alter the non-inheritable trust-tier flag, its\n> liveness-threshold tie to `CDL-055`, or the bounded consensus-dispute\n> tiebreaker. These remain governed by ratified `CDL-056`.",
    "`CDL-068` continues to govern topology-shuffle authorization, diversity\n> thresholds, and randomness-source boundary. `CDL-017` consumes this as an\n> adjacent constitutional neighbor rather than amending it.",
)


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
    raise AssertionError("phase_765_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def _current_phase_paths_in_worktree(expected_paths: set[str]) -> set[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", *sorted(expected_paths)],
        capture_output=True,
        check=True,
        text=True,
    )
    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        paths.add(line[3:].strip())
    return paths


def _git_show_text(commit_ref: str, path: Path) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_ref}:{path}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _line_for_cdl(text: str, cdl_id: str) -> str:
    return next(line for line in text.splitlines() if line.startswith(f"| {cdl_id} |"))


def _decision_rows(text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("| CDL-"):
            decision_id = line.split("|", 2)[1].strip()
            rows[decision_id] = line
    return rows


def test_artifact_exists_with_required_headings_and_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_764_carry_forward_verdicts_are_reread_verbatim() -> None:
    text = _read(ARTIFACT_PATH)
    assert str(PHASE_764_PATH) in text
    for exact_string in VERBATIM_PHASE_764_STRINGS:
        assert exact_string in text


def test_sec_004_boundary_and_named_acceptance_test_are_present() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "`TransferCertificate` must gain `epoch: EpochSeq`" in text
    assert "certificate verification must resolve the historically active `ValidatorSet` for that epoch" in text
    assert "`test_ejected_validator_sig_rejected_after_epoch_boundary`" in text
    assert "post-ratification implementation work" in text


def test_ratification_opens_lane_only_and_preserves_human_gate_and_disabled_hooks() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "This is the constitutional opening of the validator-governance lane only." in text
    assert "Genesis-only validator authority remains operative for the near-term testnet at ratification time" in text
    assert "`admit_validator` is still `unimplemented!`" in text
    assert "`eject_validator` is still `unimplemented!`" in text
    assert "The first non-Genesis validator therefore remains a later operator decision after ratification and after the required post-ratification activation work is ready." in text


def test_all_seven_non_conflation_obligations_are_locked() -> None:
    text = _read(ARTIFACT_PATH)
    normalized = _normalized(text)
    for idx in range(1, 8):
        assert f"{idx}. " in text
    assert "`CDL-017` ratification is not runtime hook activation." in text
    assert "`CDL-017` ratification is not first non-Genesis validator deployment." in text
    assert "SEC-004 activation scope is not proof that SEC-004 is already implemented." in text
    assert "`CDL-017` activation law is not silent supersession of `CDL-055`." in text
    assert "`CDL-017` activation law is not silent supersession of `CDL-056`." in text
    assert "row `7` runtime closure is inherited evidence, not a new ratification" in text
    assert "row `5` honest fail record remains true and is not erased by validator-law ratification." in normalized


def test_status_and_planning_index_record_phase_765_artifact_and_phase_766_next() -> None:
    status_text = _normalized(_read(STATUS_PATH))
    planning_text = _normalized(_read(PLANNING_INDEX_PATH))

    assert "## Phase 765" in status_text
    assert "CDL-017 ratification and single-row decision-log mutation" in status_text
    assert str(ARTIFACT_PATH) in status_text
    assert str(WALKTHROUGH_PATH) in status_text
    assert "two-commit phase record" in status_text
    assert "Phase 766 — coherence report, capsule v5.5, and closure gate" in status_text

    assert "Current frontier:" in planning_text
    assert (
        "ACTIVE through Phase `765`" in planning_text
        or "Window `763-766` CLOSED via Phase `766` closure gate" in planning_text
    )
    assert str(ARTIFACT_PATH) in planning_text
    assert (
        "commit-2 single-row `CDL-017` mutation reserved by the phase contract" in planning_text
        or "`CDL-017` is ratified" in planning_text
    )


def test_commit_1_touches_exact_expected_paths_and_no_runtime_paths() -> None:
    commit_ref = _try_resolve_commit_ref(COMMIT1_SUBJECT, COMMIT1_PATHS)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
        assert changed_paths == COMMIT1_PATHS
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path.startswith("ilc_core/") for path in changed_paths)
        assert not any(path.startswith("ilc_consensus/") for path in changed_paths)
        return

    assert _current_phase_paths_in_worktree(COMMIT1_PATHS) == COMMIT1_PATHS


def test_commit_2_touches_only_decision_log_and_no_runtime_paths() -> None:
    commit_ref = _try_resolve_commit_ref(COMMIT2_SUBJECT, COMMIT2_PATHS)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
        assert changed_paths == COMMIT2_PATHS
        assert not any(path.startswith("ilc_core/") for path in changed_paths)
        assert not any(path.startswith("ilc_consensus/") for path in changed_paths)
        return

    result = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_commit_2_ratifies_only_cdl_017_row_and_keeps_cdl_068_unchanged() -> None:
    commit_ref = _resolve_commit_ref(COMMIT2_SUBJECT, COMMIT2_PATHS)
    current_log = _git_show_text(commit_ref, DECISION_LOG_PATH)
    parent_log = _git_show_text(f"{commit_ref}^", DECISION_LOG_PATH)

    current_cdl_017 = _line_for_cdl(current_log, "CDL-017")
    parent_cdl_017 = _line_for_cdl(parent_log, "CDL-017")
    current_rows = _decision_rows(current_log)
    parent_rows = _decision_rows(parent_log)

    assert "| ratified |" in current_cdl_017
    assert "ratified_phase: 765" in current_cdl_017
    assert "ratified_date: 2026-04-21" in current_cdl_017
    assert (
        "evidence_document: docs/specs/ilc_cdl_017_validator_governance_framework_ratification_evidence_765_v0.1.md"
        in current_cdl_017
    )
    assert "| open |" in parent_cdl_017
    assert "ratified_phase: 765" not in parent_cdl_017

    current_rows.pop("CDL-017")
    parent_rows.pop("CDL-017")
    assert current_rows == parent_rows
