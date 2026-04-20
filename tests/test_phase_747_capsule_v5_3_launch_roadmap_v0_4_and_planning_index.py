from __future__ import annotations

import subprocess
from pathlib import Path


CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v5.3.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.4.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
TEST_PATH = Path("tests/test_phase_747_capsule_v5_3_launch_roadmap_v0_4_and_planning_index.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_CAPSULE_HEADINGS = (
    "## 1. Current frontier state",
    "## 2. Frozen inherited boundary state",
    "## 3. Window 745-748 active state",
    "## 4. Remaining later-lane blockers and carry-forward",
    "## 5. Window 745-748 Progress Summary",
    "## 6. Next authorized continuation",
)
PHASE_SUBJECT = (
    "phase 747",
    "capsule v5.3",
    "launch roadmap v0.4",
    "planning index",
)
EXACT_REQUIRED_PATHS = {
    str(CAPSULE_PATH),
    str(ROADMAP_PATH),
    str(PLANNING_INDEX_PATH),
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
    raise AssertionError("phase_747_commit_not_present_in_local_history")


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


def test_capsule_exists_and_contains_required_headings_in_order() -> None:
    text = _read(CAPSULE_PATH)
    positions = [text.index(heading) for heading in REQUIRED_CAPSULE_HEADINGS]
    assert positions == sorted(positions)


def test_capsule_records_active_window_frontier_adr_0031_and_non_open_convergence() -> None:
    text = _normalized(_read(CAPSULE_PATH))
    assert "Capsule v5.3 supersedes v5.2." in text
    assert "Window 745-748 is now active through Phase `747`." in text
    assert "Phase `748` is the remaining in-window closure phase." in text
    assert "the later Mysticeti convergence window is now commissioned but **not open**" in text
    assert "ADR-0031 is now accepted in Phase `746`" in text
    assert "`CDL-017` remains open and unratified" in text
    assert "row `5` remains `spec_closed_runtime_pending`" in text
    assert "row `7` remains `spec_closed_runtime_pending`" in text
    assert "row `8` remains inherited and unchanged" in text


def test_capsule_and_roadmap_keep_track_b_line_bound_to_status_tail() -> None:
    combined = _normalized(_read(CAPSULE_PATH) + "\n" + _read(ROADMAP_PATH) + "\n" + _read(STATUS_PATH))
    assert "M-019 complete; next planned phase M-020" in combined
    assert "authoritative Track B line from `STATUS.md`: M-019 complete, next planned phase M-020" in combined
    assert "The authoritative current/next Track B line still comes from `docs/phases/STATUS.md`" in combined


def test_roadmap_v0_4_records_convergence_commissioning_and_remaining_gaps_honestly() -> None:
    text = _normalized(_read(ROADMAP_PATH))
    assert "**Version**: v0.4" in text
    assert "**Supersedes**: `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`" in text
    assert "| 745-748 (active) | Phase `745` opened the convergence-window commissioning lane; Phase `746` commissioned the later convergence window and accepted ADR-0031 as housekeeping-only; Phase `747` advanced capsule `v5.3`, roadmap `v0.4`, and `PLANNING_INDEX.md` |" in text
    assert "Rows `5` and `7` remain `spec_closed_runtime_pending`." in text
    assert "The later convergence window is now commissioned precisely to absorb these runtime-closure obligations. It is not open yet." in text
    assert "The legal positioning memo remains not written." in text
    assert "`M-019` complete" in text


def test_planning_index_advances_to_v5_3_v0_4_and_phase_748_next() -> None:
    text = _normalized(_read(PLANNING_INDEX_PATH))
    assert "Window 745-748 ACTIVE through Phase 747" in text
    assert "capsule v5.3 current" in text
    assert "next planned main-lane phase is Phase 748 closure gate" in text
    assert "`docs/specs/ilc_antigravity_context_capsule_v5.3.md`" in text
    assert "`docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.4.md`" in text
    assert "ADR-0031 | Subgraph Homomorphism Query Contract — gRPC EdgeRecord | **Accepted — Phase 746 housekeeping status alignment; proto contract already present**" in text


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_phase_747() -> None:
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_747_single_commit_touches_expected_paths_only() -> None:
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
