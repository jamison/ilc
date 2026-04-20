from __future__ import annotations

import subprocess
from pathlib import Path


ROADMAP_PATH = Path("docs/specs/ilc_master_completion_roadmap_v0.1.md")
M_SERIES_PATH = Path("docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
TEST_PATH = Path("tests/test_phase_750_master_completion_roadmap_and_m_series_lane_update.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EXACT_REQUIRED_PATHS = {
    str(ROADMAP_PATH),
    str(M_SERIES_PATH),
    str(STATUS_PATH),
    str(TEST_PATH),
}
PHASE_SUBJECT = ("phase 750", "master roadmap", "m-series lane update")


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
    raise AssertionError("phase_750_commit_not_present_in_local_history")


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


def test_required_phase_750_files_exist() -> None:
    assert ROADMAP_PATH.exists()
    assert M_SERIES_PATH.exists()


def test_master_roadmap_records_live_frontier_and_artifact_gated_convergence() -> None:
    text = _normalized(_read(ROADMAP_PATH))
    assert "`M-021` is current and recorded as complete." in text
    assert "`M-022` is the next planned Gemini phase." in text
    assert "the later Mysticeti convergence window is commissioned but not open" in text
    assert "`CDL-017` remains open and unratified" in text
    assert "Convergence entry remains artifact-gated." in text


def test_master_roadmap_preserves_m021_conditional_branch_and_security_notes() -> None:
    text = _normalized(_read(ROADMAP_PATH))
    assert "including the explicit HIGH-001 two-layer-defence note" in text
    assert "documented HIGH-002 / CRIT-001 dispositions" in text
    assert "if a real external audit has been engaged and findings exist" in text
    assert "rather than being erased from the plan" in text


def test_master_roadmap_keeps_m022_exitability_and_cdl_017_separate_from_convergence() -> None:
    text = _normalized(_read(ROADMAP_PATH))
    assert "Strong exitability drill" in text
    assert "it does not by itself ratify `CDL-017` and it does not skip the later convergence window" in text
    assert "`CDL-017` is not ratified inside convergence." in text
    assert "separate subsequent Codex window" in text


def test_m_series_updates_m021_and_m022_scope_owner_and_route() -> None:
    text = _normalized(_read(M_SERIES_PATH))
    assert "### M-021 — Audit Remediation + SIM-LEAKAGE-01 Execution" in text
    assert "**Owner:** Gemini (execution) / Claude (audit)" in text
    assert "pending-if-activated rather than being erased from the lane" in text
    assert "results include raw numbers and methodology, not just a verdict" in text
    assert "### M-022 — Gemini Lane Handoff Package + Exitability Drill" in text
    assert "Physical exitability drill evidence is present" in text
    assert "M-022 does not ratify `CDL-017`." in text


def test_m_series_separates_convergence_from_later_cdl_017_window() -> None:
    text = _normalized(_read(M_SERIES_PATH))
    assert "Later Codex convergence and post-convergence route" in text
    assert "convergence_and_cdl_017_ratification_are_separate_windows" in text
    assert "After the later convergence window closes, the **separate subsequent `CDL-017` ratification window** opens" in text
    assert "convergence_requires_explicit_human_authorization_for_first_validator_deployment" in text


def test_m_series_timeline_and_security_summary_are_advanced_and_honest() -> None:
    text = _normalized(_read(M_SERIES_PATH))
    assert "Estimated elapsed time with LLM-augmented development" not in text
    assert "| M-021 | SIM-LEAKAGE-01 primary + security-fix verification + conditional external-audit remediation | M-020 + external audit if engaged | **COMPLETE** `4a8fdd9e` |" in text
    assert "| M-022 | Exitability drill primary + Gemini handoff package | M-021 | **NEXT** |" in text
    assert "SEC-009 ✓ CLOSED `19efe35d`" in text
    assert "SEC-010 ✓ CLOSED `16147c2b`" in text
    assert "HIGH-002 DOCUMENTED LIMITATION `16147c2b`" in text
    assert "HIGH-001 DOCUMENTED TWO-LAYER DEFENCE" in text
    assert "CDL-017 remains OPEN and routes through the post-convergence Codex ratification window" in text


def test_phase_750_commit_touches_expected_paths_only_and_no_runtime_or_decision_log_files() -> None:
    commit_ref = _try_resolve_commit_ref(PHASE_SUBJECT, EXACT_REQUIRED_PATHS)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
        assert changed_paths == EXACT_REQUIRED_PATHS
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
        assert not any(
            path == "ilc_consensus" or path.startswith("ilc_consensus/")
            for path in changed_paths
        )
        return

    assert _current_phase_paths_in_worktree(EXACT_REQUIRED_PATHS) == EXACT_REQUIRED_PATHS

