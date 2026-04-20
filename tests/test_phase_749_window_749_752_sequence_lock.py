from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_phase_749_752_sequence_lock_v0.1.md")
TEST_PATH = Path("tests/test_phase_749_window_749_752_sequence_lock.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Inherited gates and constraints",
    "## 3. Window meaning",
    "## 4. Convergence-window posture at open",
    "## 5. Planning-consolidation posture at open",
    "## 6. Phase table and sequencing",
    "## 7. Explicit separation obligations",
    "## 8. Non-goals",
    "## 9. Source inputs",
)
REQUIRED_TOKENS = (
    "window_749_752_sequence_lock_active",
    "track_b_m021_complete_m022_next",
    "planning_consolidation_window_active",
    "master_completion_roadmap_authorized_in_window_749_752",
    "stale_planning_doc_retirement_authorized_in_window_749_752",
    "m_series_lane_update_authorized_in_window_749_752",
    "no_convergence_window_open_in_window_749_752",
    "no_cdl_017_ratification_in_window_749_752",
    "no_option_b_graduation_in_window_749_752",
    "rows_5_and_7_remain_spec_closed_runtime_pending_at_window_open",
    "row_8_remains_inherited_at_window_open",
    "uncommitted_m_track_drafts_do_not_satisfy_convergence_entry",
)
PHASE_SUBJECT = ("phase 749", "window 749-752 sequence lock")
EXACT_REQUIRED_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
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
    raise AssertionError("phase_749_commit_not_present_in_local_history")


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


def test_artifact_exists_and_contains_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_artifact_records_live_track_b_line_and_frozen_main_lane_boundary() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Window `745-748` is closed." in text
    assert "Capsule `v5.3` is the latest closed-window capsule." in text
    assert "M-021 (SIM-LEAKAGE-01 execution / audit remediation) complete." in text
    assert "sim_leakage_01_verdict=fail accurately documented and remediation fixes cleanly verified." in text
    assert "M-022 (Gemini Lane Handoff Package)" in text


def test_artifact_preserves_inherited_row_and_cdl_posture() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "`CDL-017` remains open and unratified." in text
    assert "row `5` remains `spec_closed_runtime_pending`." in text
    assert "row `7` remains `spec_closed_runtime_pending`." in text
    assert "row `8` remains inherited and unchanged." in text
    assert "ADR-0028 Option D remains the active posture." in text


def test_artifact_keeps_convergence_entry_artifact_gated() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Convergence entry still requires committed artifact-class re-verification" in text
    assert "Uncommitted Gemini worktree drafts remain below that authority threshold" in text
    assert "do not satisfy convergence entry" in text


def test_artifact_authorizes_planning_consolidation_outputs_only() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "create `docs/specs/ilc_master_completion_roadmap_v0.1.md`" in text
    assert "update `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`" in text
    assert "add archival or superseded headers to designated older planning docs" in text
    assert "advance `docs/PLANNING_INDEX.md`" in text


def test_artifact_records_phase_table_and_non_goals() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "| 1 | 749 | sequence lock | gate / planning |" in text
    assert "| 2 | 750 | master completion roadmap + M-series lane update | planning |" in text
    assert "| 3 | 751 | archival headers + planning-index advance | planning / archival |" in text
    assert "| 4 | 752 | coherence report + closure gate | gate / handoff |" in text
    assert "any ratification of `CDL-017`," in text
    assert "any move of row `5` to `runtime_closed`," in text
    assert "any move of row `7` to `runtime_closed`," in text
    assert "any Option B graduation claim," in text
    assert "any mutation of `ilc_core/` or `ilc_consensus/`," in text
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_749_commit_touches_expected_paths_only() -> None:
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
