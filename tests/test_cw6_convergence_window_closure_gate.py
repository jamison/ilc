from __future__ import annotations

import os
import subprocess
from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_coherence_report_762_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v5.4.md")
GATE_PATH = Path("docs/specs/ilc_mysticeti_convergence_window_closure_gate_762_v0.1.md")
TEST_PATH = Path("tests/test_cw6_convergence_window_closure_gate.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS_COHERENCE = (
    "## 1. Window verdict",
    "## 2. Phase-by-phase coherence",
    "## 3. Constitutional and runtime posture at close",
    "## 4. Track B verification and cross-lane posture",
    "## 5. Carry-forward and reviewer gate",
)
REQUIRED_HEADINGS_CAPSULE = (
    "## 1. Current frontier state",
    "## 2. Frozen inherited boundary state",
    "## 3. Convergence-window closure state",
    "## 4. Remaining later-lane blockers and carry-forward",
    "## 5. Convergence Window Closure Summary",
    "## 6. Next authorized continuation",
)
REQUIRED_HEADINGS_GATE = (
    "## 1. Completion checklist",
    "## 2. Constitutional and runtime posture at closure",
    "## 3. Track B verification",
    "## 4. Planning-surface advance",
    "## 5. Carry-forward",
    "## 6. Selftest chain",
    "## 7. Closure verdict",
)
REQUIRED_TOKENS = (
    "mysticeti_convergence_window_closed",
    "convergence_window_row_7_runtime_closed",
    "convergence_window_row_5_honest_fail_recorded",
    "convergence_window_option_b_gate_no_go",
    "cdl_017_ratification_window_pending_reviewer_approval",
)
PHASE_MAIN_SUBJECT = (
    "cw-6",
    "phase 762",
    "coherence report",
    "convergence closure gate",
)
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(GATE_PATH),
    str(TEST_PATH),
    str(STATUS_PATH),
    str(PLANNING_INDEX_PATH),
    "tests/test_phase_751_stale_planning_doc_archival_and_planning_index_advance.py",
    "tests/test_phase_752_window_749_752_closure_gate.py",
    "tests/test_phase_753_window_753_756_sequence_lock.py",
    "tests/test_phase_756_window_753_756_closure_gate.py",
}
SELFTEST_ENV = "ILC_CW6_GATE_SELFTEST"
SELFTEST_CHAIN = (
    "ILC_CW5_GATE_SELFTEST=1",
    "ILC_CW6_GATE_SELFTEST=1",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _selftest() -> bool:
    return os.environ.get(SELFTEST_ENV) == "1"


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
    raise AssertionError("cw6_commit_not_present_in_local_history")


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


def test_output_files_exist_with_required_headings_in_order() -> None:
    if _selftest():
        return
    coherence = _read(COHERENCE_PATH)
    capsule = _read(CAPSULE_PATH)
    gate = _read(GATE_PATH)
    assert [coherence.index(h) for h in REQUIRED_HEADINGS_COHERENCE] == sorted(
        coherence.index(h) for h in REQUIRED_HEADINGS_COHERENCE
    )
    assert [capsule.index(h) for h in REQUIRED_HEADINGS_CAPSULE] == sorted(
        capsule.index(h) for h in REQUIRED_HEADINGS_CAPSULE
    )
    assert [gate.index(h) for h in REQUIRED_HEADINGS_GATE] == sorted(
        gate.index(h) for h in REQUIRED_HEADINGS_GATE
    )


def test_all_required_closure_tokens_are_present() -> None:
    if _selftest():
        return
    gate = _read(GATE_PATH)
    for token in REQUIRED_TOKENS:
        assert token in gate


def test_row_posture_and_option_b_state_are_recorded_honestly() -> None:
    if _selftest():
        return
    combined = _normalized(_read(COHERENCE_PATH) + "\n" + _read(CAPSULE_PATH) + "\n" + _read(GATE_PATH))
    assert "row `7` is `runtime_closed`" in combined
    assert "row `5` remains `spec_closed_runtime_pending`" in combined
    assert "row `8` remains an inherited criteria lock with no candidate evaluation" in combined
    assert "Option B gate is `no-go`" in combined or "Option B gate has been synthesized as `no-go`" in combined
    assert "Option B selection" in _read(GATE_PATH)


def test_cdl_017_remains_open_and_pending_reviewer_approval() -> None:
    if _selftest():
        return
    combined = _normalized(_read(COHERENCE_PATH) + "\n" + _read(CAPSULE_PATH) + "\n" + _read(GATE_PATH))
    assert "`CDL-017` remains open and unratified" in combined
    assert "later `CDL-017` ratification window pending reviewer approval" in combined
    assert "`CDL-017` is now ratified" not in combined


def test_selftest_chain_is_declared_in_gate_and_test_file() -> None:
    text = _read(TEST_PATH) + "\n" + _read(GATE_PATH)
    for token in SELFTEST_CHAIN:
        assert token in text
    assert SELFTEST_ENV in text


def test_planning_index_and_status_advance_to_post_convergence_frontier() -> None:
    if _selftest():
        return
    planning = _normalized(_read(PLANNING_INDEX_PATH))
    status = _read(STATUS_PATH)
    assert "Context Capsule v5.4" in planning
    assert (
        "Current frontier:** Convergence window CLOSED through Phase 762" in planning
        or "`CDL-017` ratification window ACTIVE through Phase `763`" in planning
        or "`CDL-017` ratification window ACTIVE through Phase `764`" in planning
    )
    assert (
        "pending reviewer approval" in planning
        or "Active CDL-017 Ratification Sequence Lock" in planning
    )
    assert "## Phase 761" in status
    assert "## Phase 762" in status
    assert "## Track B Advancement Record — 2026-04-21" in status
    assert "convergence window closed; later CDL-017 ratification window pending reviewer approval" in status


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_cw6() -> None:
    if _selftest():
        return
    commit_ref = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
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


def test_cw6_commit_touches_expected_paths_only() -> None:
    if _selftest():
        return
    commit_ref = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    if commit_ref:
        assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS
        return

    assert _current_phase_paths_in_worktree(EXACT_REQUIRED_MAIN_PATHS) == EXACT_REQUIRED_MAIN_PATHS
