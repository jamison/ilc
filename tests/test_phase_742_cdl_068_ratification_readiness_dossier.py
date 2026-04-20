from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_cdl_068_ratification_readiness_dossier_742_v0.1.md")
TEST_PATH = Path("tests/test_phase_742_cdl_068_ratification_readiness_dossier.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Purpose and scope",
    "## 2. CDL-068 opening checklist re-read",
    "## 3. Checklist item satisfaction record",
    "## 4. Phase 736 prelock criteria satisfaction record",
    "## 5. Ratification-readiness verdict",
    "## 6. Non-ratification and mutation boundary",
)
REQUIRED_EVIDENCE_SOURCES = (
    "docs/research/ilc_sim_validator_01_results_v0.1.md",
    "docs/research/ilc_sim_topology_01_results_v0.1.md",
    "docs/research/ilc_validator_agent_design_evidence_v0.1.md",
    "docs/specs/ilc_cdl_039_topology_shuffling_authorization_scope_note_711_v0.1.md",
)
REQUIRED_TOKENS = (
    "cdl_068_ratification_readiness_dossier_742_complete",
    "all_cdl_068_opening_checklist_items_satisfied_phase_742",
    "all_phase_736_prelock_criteria_checked_phase_742",
    "cdl_068_ratification_readiness_verdict=ready_for_phase_743",
    "cdl_068_not_ratified_in_phase_742",
    "cdl_068_ratification_ready_for_phase_743",
)
PRELOCK_CRITERIA_HEADINGS = (
    "### 4.1 Criterion 1",
    "### 4.2 Criterion 2",
    "### 4.3 Criterion 3",
    "### 4.4 Criterion 4",
    "### 4.5 Criterion 5",
    "### 4.6 Criterion 6",
)
PHASE_MAIN_SUBJECT = (
    "phase 742",
    "cdl-068 ratification-readiness dossier",
)
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(STATUS_PATH),
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
    raise AssertionError("phase_742_commit_not_present_in_local_history")


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


def test_dossier_exists_with_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_each_required_evidence_source_document_is_explicitly_referenced() -> None:
    text = _read(ARTIFACT_PATH)
    for source in REQUIRED_EVIDENCE_SOURCES:
        assert source in text


def test_opening_checklist_is_re_read_from_the_opening_artifact() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "SIM-TOPOLOGY-01 full results:" in text
    assert "SIM-VALIDATOR-01 VRF threshold:" in text
    assert "CDL-017 prelock evidence artifact:" in text
    assert "CDL-039 boundary satisfaction:" in text


def test_all_six_phase_736_prelock_criteria_are_checked_individually() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in PRELOCK_CRITERIA_HEADINGS:
        assert heading in text
    assert text.count("Status: satisfied.") >= 10


def test_explicit_ratification_readiness_verdict_tokens_are_present() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "all checklist items satisfied - `CDL-068` is ready for ratification in" in text


def test_dossier_does_not_ratify_cdl_068_in_phase_742() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Status: ratification-readiness dossier" in text
    assert "Phase `742` remains dossier-only." in text
    assert "no ratification date is created in this dossier" in text
    assert "`CDL-068` is still open at the end of this phase" in text
    assert "Status: ratified" not in text
    assert "ratified_date" not in text


def test_status_backfill_mentions_phase_742_dossier_and_next_phase_743() -> None:
    text = _normalized(_read(STATUS_PATH))
    assert "## Phase 742" in text
    assert "CDL-068 ratification-readiness dossier" in text
    assert "docs/specs/ilc_cdl_068_ratification_readiness_dossier_742_v0.1.md" in text
    assert "Phase 743 — CDL-068 ratification" in text


def test_decision_log_and_ilc_core_and_ilc_consensus_are_untouched_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    if main_commit:
        changed_paths = _changed_paths_for_commit(main_commit)
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
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


def test_phase_742_single_commit_touches_expected_paths_only() -> None:
    commit_ref = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    if commit_ref:
        assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS
        return

    assert _current_phase_paths_in_worktree(EXACT_REQUIRED_MAIN_PATHS) == EXACT_REQUIRED_MAIN_PATHS
