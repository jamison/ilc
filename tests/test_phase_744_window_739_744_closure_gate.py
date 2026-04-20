from __future__ import annotations

import subprocess
from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_coherence_report_744_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v5.2.md")
GATE_PATH = Path("docs/specs/ilc_window_739_744_closure_gate_744_v0.1.md")
TEST_PATH = Path("tests/test_phase_744_window_739_744_closure_gate.py")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS_COHERENCE = (
    "## 1. Window verdict",
    "## 2. Phase-by-phase coherence",
    "## 3. Constitutional and runtime state at close",
    "## 4. Track B verification and cross-lane posture",
    "## 5. Carry-forward and residual blockers",
)
REQUIRED_HEADINGS_CAPSULE = (
    "## 1. Current frontier state",
    "## 2. Frozen inherited boundary state",
    "## 3. Window 739-744 closure state",
    "## 4. Remaining later-lane blockers and carry-forward",
    "## 5. Window 739-744 Closure Summary",
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
PHASE_MAIN_SUBJECT = (
    "phase 744",
    "coherence",
    "capsule v5.2",
    "window 739-744 closure gate",
)
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(GATE_PATH),
    str(TEST_PATH),
    str(STATUS_PATH),
    str(PLANNING_INDEX_PATH),
    str(ROADMAP_PATH),
}

# Category 3 selftest guard chain: latest prior closure-gate env var plus Phase 744.
CATEGORY_3_SELFTEST_ENV_CHAIN = (
    "ILC_PHASE_738_GATE_SELFTEST=1",
    "ILC_PHASE_744_GATE_SELFTEST=1",
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
    raise AssertionError("phase_744_commit_not_present_in_local_history")


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


def test_closure_artifacts_record_cdl_068_ratified_status_with_phase_and_date() -> None:
    combined = _normalized(_read(COHERENCE_PATH) + "\n" + _read(CAPSULE_PATH) + "\n" + _read(GATE_PATH))
    assert "`CDL-068` is now ratified" in combined
    assert "`CDL-068` was ratified in Phase `743`" in combined
    assert "`ratified_phase: 743`" in combined
    assert "`ratified_date: 2026-04-20`" in combined


def test_cdl_017_remains_open_and_unratified_everywhere() -> None:
    combined = _normalized(_read(COHERENCE_PATH) + "\n" + _read(CAPSULE_PATH) + "\n" + _read(GATE_PATH))
    assert "`CDL-017` remains open and unratified" in combined
    assert "`CDL-017` still open" in combined
    assert "`CDL-017` is now ratified" not in combined


def test_row_5_row_7_and_row_8_posture_remains_honest_without_premature_closure() -> None:
    combined = _normalized(_read(COHERENCE_PATH) + "\n" + _read(CAPSULE_PATH) + "\n" + _read(GATE_PATH))
    assert "row `5` remains `spec_closed_runtime_pending`" in combined
    assert "row `7` remains `spec_closed_runtime_pending`" in combined
    assert "row `8` remains an inherited criteria lock" in combined
    assert "No row-5, row-7, or row-8 runtime closure is claimed by this gate." in combined


def test_selftest_chain_extends_from_phase_738_to_phase_744() -> None:
    text = _read(TEST_PATH) + "\n" + _read(GATE_PATH)
    assert "Category 3 selftest guard chain" in text
    for token in CATEGORY_3_SELFTEST_ENV_CHAIN:
        assert token in text


def test_carry_forward_routes_to_window_745_748_and_the_convergence_window() -> None:
    combined = _normalized(_read(COHERENCE_PATH) + "\n" + _read(CAPSULE_PATH) + "\n" + _read(GATE_PATH))
    required = [
        "Window `745-748` is the next main-lane continuation",
        "Option B graduation remains deferred until rows `5` and `7` are honestly runtime-closed",
        "the Mysticeti convergence window must absorb actual `SIM-LEAKAGE-01` execution for row `5`",
        "the Gemini `M-019` censorship artifact bundle required by Phase `741` Section `3.2`",
        "the separate strong-exitability drill for row `7`",
    ]
    for item in required:
        assert item in combined


def test_planning_index_and_launch_roadmap_advance_to_the_post_744_frontier() -> None:
    planning = _read(PLANNING_INDEX_PATH)
    roadmap = _read(ROADMAP_PATH)
    assert "capsule v5.2" in planning
    assert "Window 739-744 CLOSED" in planning
    assert "Window 745-748 is the next main-lane continuation to be defined" in planning
    assert "`CDL-068` is ratified and no longer part of the live open-CDL frontier" in planning
    assert "**Produced**: 2026-04-20" in roadmap
    assert "Window 739-744 CLOSED (today); capsule v5.2 current; M-018 complete; next planned phase M-019" in roadmap
    assert "| 739-744 | Rows 5 and 7 runtime evidence packaging plus `CDL-068` ratification; capsule v5.2 frontier close |" in roadmap
    assert "| CDL-068 | **RATIFIED** — Phase 743 |" in roadmap


def test_track_b_line_is_re_read_from_status_tail() -> None:
    combined = _normalized(_read(COHERENCE_PATH) + "\n" + _read(CAPSULE_PATH) + "\n" + _read(GATE_PATH) + "\n" + _read(STATUS_PATH))
    assert "M-018 (Workload F: Bounded Public Auditability) complete" in combined
    assert "M-019 (Adversarial Hardening and Byzantine Fault Simulation)" in combined
    assert "track_b_m018_complete_m019_next" in combined


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_phase_744() -> None:
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


def test_phase_744_single_commit_touches_expected_paths_only() -> None:
    commit_ref = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    if commit_ref:
        assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS
        return

    assert _current_phase_paths_in_worktree(EXACT_REQUIRED_MAIN_PATHS) == EXACT_REQUIRED_MAIN_PATHS
