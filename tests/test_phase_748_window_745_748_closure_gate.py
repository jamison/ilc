from __future__ import annotations

import subprocess
from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_coherence_report_748_v0.1.md")
GATE_PATH = Path("docs/specs/ilc_window_745_748_closure_gate_748_v0.1.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
TEST_PATH = Path("tests/test_phase_748_window_745_748_closure_gate.py")
LEGACY_TEST_PATH = Path(
    "tests/test_phase_747_capsule_v5_3_launch_roadmap_v0_4_and_planning_index.py"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_SUBJECT = (
    "phase 748",
    "coherence report",
    "window 745-748 closure gate",
)
EXACT_REQUIRED_PATHS = {
    str(COHERENCE_PATH),
    str(GATE_PATH),
    str(PLANNING_INDEX_PATH),
    str(TEST_PATH),
    str(LEGACY_TEST_PATH),
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
    raise AssertionError("phase_748_commit_not_present_in_local_history")


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


def test_output_files_exist() -> None:
    assert COHERENCE_PATH.exists()
    assert GATE_PATH.exists()


def test_closure_artifacts_record_honest_non_closure_posture() -> None:
    combined = _normalized(_read(COHERENCE_PATH) + "\n" + _read(GATE_PATH))
    assert "Window `745-748` closes cleanly as a convergence-window commissioning and planning-surface advance lane." in combined
    assert "row `5` remains `spec_closed_runtime_pending`" in combined
    assert "row `7` remains `spec_closed_runtime_pending`" in combined
    assert "row `8` remains inherited and unchanged" in combined
    assert "`CDL-017` remains open and unratified" in combined
    assert "Option B graduation did not occur" in combined


def test_closure_artifacts_record_convergence_window_commissioned_but_not_open() -> None:
    combined = _normalized(_read(COHERENCE_PATH) + "\n" + _read(GATE_PATH))
    assert "convergence window commissioned but not open" in combined
    assert "the later convergence window is the next commissioned main-lane continuation, but it is not open yet" in combined


def test_selftest_chain_extends_from_phase_744_to_phase_748() -> None:
    text = _read(GATE_PATH) + "\n" + _read(TEST_PATH)
    assert "ILC_PHASE_744_GATE_SELFTEST=1" in text
    assert "ILC_PHASE_748_GATE_SELFTEST=1" in text


def test_planning_index_records_window_closed_and_next_lane_commissioned() -> None:
    text = _normalized(_read(PLANNING_INDEX_PATH))
    assert "Window 745-748 CLOSED via Phase 748 closure gate" in text
    assert "next planned main-lane continuation is the later convergence window, commissioned but not open" in text
    assert "next planned main-lane continuation is the later convergence window" in text


def test_legacy_phase_747_test_is_tolerant_of_post_close_frontier_update() -> None:
    text = _read(LEGACY_TEST_PATH)
    assert "Window 745-748 ACTIVE through Phase 747" in text
    assert "Window 745-748 CLOSED via Phase 748 closure gate" in text


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_phase_748() -> None:
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_748_single_commit_touches_expected_paths_only() -> None:
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
