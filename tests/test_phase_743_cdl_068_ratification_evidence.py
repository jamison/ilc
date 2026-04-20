from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path(
    "docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md"
)
TEST_PATH = Path("tests/test_phase_743_cdl_068_ratification_evidence.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
DOSSIER_PATH = Path("docs/specs/ilc_cdl_068_ratification_readiness_dossier_742_v0.1.md")

REQUIRED_HEADINGS = (
    "## 1. Phase 742 dossier verdict re-read",
    "## 2. Ratified constitutional decision",
    "## 3. Ratified topology floors, ceilings, cadence, and VRF threshold",
    "## 4. Phase 736 prelock criteria re-read as satisfied",
    "## 5. Two-commit mutation discipline and decision-log consequence",
    "## 6. Preserved exclusions and non-goals",
)
REQUIRED_TOKENS = (
    "cdl_068_ratification_evidence_complete",
    "cdl_068_ratified_topology_shuffle_authorization_lane",
    "cdl_068_topology_parameters_ratified_as_floors_and_ceilings",
    "cdl_068_vrf_upgrade_threshold_fixed_at_10_active_validators",
    "cdl_068_commit_1_does_not_mutate_decision_log",
    "cdl_068_commit_2_mutates_only_cdl_068_row",
    "cdl_017_remains_open_after_cdl_068_ratification",
)
CRITERION_HEADINGS = (
    "### 4.1 Criterion 1 satisfied",
    "### 4.2 Criterion 2 satisfied",
    "### 4.3 Criterion 3 satisfied",
    "### 4.4 Criterion 4 satisfied",
    "### 4.5 Criterion 5 satisfied",
    "### 4.6 Criterion 6 satisfied",
)
COMMIT1_SUBJECT = ("phase 743", "cdl-068 ratification evidence")
COMMIT2_SUBJECT = ("phase 743", "cdl-068 decision log ratification")
COMMIT1_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(STATUS_PATH),
}
COMMIT2_PATHS = {str(DECISION_LOG_PATH)}


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
    raise AssertionError("phase_743_commit_not_present_in_local_history")


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


def test_ratification_artifact_exists_with_required_headings_and_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_742_dossier_verdict_is_explicitly_reread_not_paraphrased() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert str(DOSSIER_PATH) in text
    assert "all checklist items satisfied - `CDL-068` is ready for ratification in Phase `743`" in text


def test_topology_parameters_are_expressed_as_floors_and_ceilings_with_exact_cadence() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "`shuffle_cadence_epochs = 1`" in text
    assert "`k_degree_floor >= 4`" in text
    assert "`push_fanout_ceiling <= 3`" in text
    assert "`distinct_cluster_floor >= 4`" in text
    assert "`max_cluster_share_ceiling <= 33%`" in text


def test_vrf_trigger_is_expressed_as_exact_threshold_not_range() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "`vrf_upgrade_threshold_validator_count = 10`" in text
    assert "vrf_upgrade_threshold_validator_count >= 10" not in text
    assert "vrf_upgrade_threshold_validator_count <= 10" not in text
    assert "vrf_upgrade_threshold_validator_count 10-10" not in text


def test_all_six_prelock_criteria_are_restated_individually_with_dossier_citations() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in CRITERION_HEADINGS:
        assert heading in text
    for idx in range(1, 7):
        assert f"Phase `742` dossier Section `4.{idx}`" in text
    assert text.count("Status: satisfied.") >= 6


def test_status_backfill_mentions_two_commit_phase_743_and_next_phase_744() -> None:
    text = _normalized(_read(STATUS_PATH))
    assert "## Phase 743" in text
    assert "CDL-068 topology shuffle authorization ratification" in text
    assert str(ARTIFACT_PATH) in text
    assert "two-commit phase record" in text
    assert "Phase 744 — coherence report, capsule v5.2, and closure gate" in text


def test_commit_1_touches_exact_expected_paths_and_excludes_decision_log() -> None:
    commit_ref = _try_resolve_commit_ref(COMMIT1_SUBJECT, COMMIT1_PATHS)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
        assert changed_paths == COMMIT1_PATHS
        assert str(DECISION_LOG_PATH) not in changed_paths
        return

    assert _current_phase_paths_in_worktree(COMMIT1_PATHS) == COMMIT1_PATHS


def test_commit_2_touches_only_decision_log() -> None:
    commit_ref = _try_resolve_commit_ref(COMMIT2_SUBJECT, COMMIT2_PATHS)
    if commit_ref:
        assert _changed_paths_for_commit(commit_ref) == COMMIT2_PATHS
        return

    result = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_cdl_068_row_is_ratified_in_commit_2_and_cdl_017_remains_open() -> None:
    commit_ref = _resolve_commit_ref(COMMIT2_SUBJECT, COMMIT2_PATHS)
    current_log = _git_show_text(commit_ref, DECISION_LOG_PATH)
    parent_log = _git_show_text(f"{commit_ref}^", DECISION_LOG_PATH)

    current_cdl_068 = _line_for_cdl(current_log, "CDL-068")
    parent_cdl_068 = _line_for_cdl(parent_log, "CDL-068")
    current_cdl_017 = _line_for_cdl(current_log, "CDL-017")

    assert "| ratified |" in current_cdl_068
    assert "ratified_phase: 743" in current_cdl_068
    assert "ratified_date: 2026-04-20" in current_cdl_068
    assert (
        "evidence_document: docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md"
        in current_cdl_068
    )
    assert "| open |" in parent_cdl_068
    assert "ratified_phase: 743" not in parent_cdl_068
    assert "| open |" in current_cdl_017
