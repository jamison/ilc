from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_phase_753_756_sequence_lock_v0.1.md")
TEST_PATH = Path("tests/test_phase_753_window_753_756_sequence_lock.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
LEGACY_TEST_PATH = Path("tests/test_phase_752_window_749_752_closure_gate.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Inherited gates and constraints",
    "## 3. Window meaning",
    "## 4. Pre-draft posture at open",
    "## 5. Phase table and sequencing",
    "## 6. Explicit separation obligations",
    "## 7. Non-goals",
    "## 8. Source inputs",
)
REQUIRED_TOKENS = (
    "window_753_756_sequence_lock_active",
    "track_b_m021_complete_m022_next",
    "convergence_window_guidance_pre_draft_authorized_in_window_753_756",
    "cdl_017_ratification_dossier_prework_authorized_in_window_753_756",
    "no_convergence_window_open_in_window_753_756",
    "no_cdl_017_ratification_in_window_753_756",
    "no_row_closure_claim_in_window_753_756",
    "no_option_b_graduation_in_window_753_756",
    "rows_5_and_7_remain_spec_closed_runtime_pending_at_window_open",
    "row_8_remains_inherited_at_window_open",
    "artifact_path_placeholders_required_not_phase_labels",
    "no_decision_log_mutation_in_window_753_756",
)
PHASE_SUBJECT = ("phase 753", "window 753-756 sequence lock")
EXACT_REQUIRED_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(STATUS_PATH),
    str(PLANNING_INDEX_PATH),
    str(LEGACY_TEST_PATH),
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
    raise AssertionError("phase_753_commit_not_present_in_local_history")


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


def test_artifact_records_live_frontier_and_track_b_line() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Window `749-752` is closed." in text
    assert "Capsule `v5.3` remains the latest closed-window capsule" in text
    assert "`CDL-017` remains open and unratified" in text
    assert "rows `5` and `7` remain `spec_closed_runtime_pending`" in text
    assert "row `8` remains inherited and unchanged" in text
    assert "M-021 (SIM-LEAKAGE-01 execution / audit remediation) complete." in text
    assert "sim_leakage_01_verdict=fail accurately documented and remediation fixes verified." in text
    assert "M-022 (Gemini Lane Handoff Package)" in text


def test_artifact_records_pre_draft_and_pre_work_only_boundary() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "convergence-window execution guidance pre-draft" in text
    assert "`CDL-017` ratification-readiness dossier assembled as pre-work" in text
    assert "does not open the convergence window" in text
    assert "does not ratify `CDL-017`" in text
    assert "`M-022 approval -> convergence window -> CDL-017 ratification window`" in text


def test_artifact_records_phase_table_and_non_goals() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "| 1 | 753 | sequence lock | gate / planning |" in text
    assert "| 2 | 754 | convergence-window guidance pre-draft | planning / pre-draft |" in text
    assert "| 3 | 755 | CDL-017 ratification-readiness dossier | planning / pre-work |" in text
    assert "| 4 | 756 | coherence report + closure gate | gate / handoff |" in text
    assert "any opening of the later convergence window," in text
    assert "any ratification of `CDL-017`," in text
    assert "any move of row `5` to `runtime_closed`," in text
    assert "any move of row `7` to `runtime_closed`," in text
    assert "any advancement of row `8`," in text
    assert "any decision-log mutation," in text


def test_planning_index_records_window_active_and_guidance_current() -> None:
    text = _normalized(_read(PLANNING_INDEX_PATH))
    assert (
        "Window 753-756 ACTIVE through Phase 753 sequence lock" in text
        or "Window 753-756 CLOSED via Phase 756 closure gate" in text
        or "Convergence window ACTIVE through Phase 760" in text
        or "Convergence window CLOSED through Phase 762" in text
        or "Window `763-766` CLOSED via Phase `766` closure gate" in text
    )
    assert (
        "**Latest main-lane sequence lock (753-756)** ⬅ CURRENT" in text
        or "**Active convergence sequence lock (CW-1 / Phase 757)** ⬅ CURRENT" in text
        or "**Convergence closure gate (CW-6 / Phase 762)** ⬅ CURRENT" in text
        or "**Latest closed main-lane closure (763-766)** ⬅ CURRENT" in text
    )
    assert (
        "**Active Codex window guidance (753-756)** ⬅ CURRENT" in text
        or "**Latest closed Codex window guidance (753-756)** ⬅ CURRENT" in text
        or "**Convergence Window Guidance (activated by CW-1)** ⬅ CURRENT" in text
        or "**Convergence Window Guidance**" in text
    )
    assert (
        "convergence window remains commissioned but not open" in text
        or "convergence window opened via the Phase 757 CW-1 sequence lock" in text
        or "Convergence window CLOSED through Phase 762" in text
        or "Window `763-766` CLOSED via Phase `766` closure gate" in text
    )


def test_legacy_phase_752_test_is_tolerant_of_post_open_frontier_update() -> None:
    text = _read(LEGACY_TEST_PATH)
    assert "Window 753-756 (pre-drafts) is the next queued Codex window" in text
    assert "Window 753-756 ACTIVE through Phase 753 sequence lock" in text
    assert "Window `763-766` CLOSED via Phase `766` closure gate" in text


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_phase_753() -> None:
    commit_ref = _try_resolve_commit_ref(PHASE_SUBJECT, EXACT_REQUIRED_PATHS)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
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


def test_phase_753_single_commit_touches_expected_paths_only() -> None:
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
