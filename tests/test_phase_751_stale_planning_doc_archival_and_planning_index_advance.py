from __future__ import annotations

import subprocess
from pathlib import Path


FOUNDATIONAL_PATH = Path("docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md")
TRANSITION_PATH = Path("docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md")
ROADMAP_V03_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
TEST_PATH = Path("tests/test_phase_751_stale_planning_doc_archival_and_planning_index_advance.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EXACT_REQUIRED_PATHS = {
    str(FOUNDATIONAL_PATH),
    str(TRANSITION_PATH),
    str(ROADMAP_V03_PATH),
    str(PLANNING_INDEX_PATH),
    str(STATUS_PATH),
    str(TEST_PATH),
}
PHASE_SUBJECT = ("phase 751", "archival", "planning index")


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
    raise AssertionError("phase_751_commit_not_present_in_local_history")


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


def test_archival_headers_are_present_at_top_of_three_stale_docs() -> None:
    foundational = _normalized("\n".join(_read(FOUNDATIONAL_PATH).splitlines()[:8]))
    transition = _normalized("\n".join(_read(TRANSITION_PATH).splitlines()[:8]))
    roadmap_v03 = _normalized("\n".join(_read(ROADMAP_V03_PATH).splitlines()[:6]))

    assert "**ARCHIVED 2026-04-20.**" in foundational
    assert "docs/specs/ilc_master_completion_roadmap_v0.1.md" in foundational
    assert "**ARCHIVED 2026-04-20.**" in transition
    assert "CDL-062" in transition
    assert "human conversation" in transition
    assert "**SUPERSEDED.**" in roadmap_v03
    assert "ilc_launch_roadmap_three_machines_seven_agents_v0.4.md" in roadmap_v03


def test_planning_index_current_frontier_and_startup_guidance_are_advanced() -> None:
    text = _normalized(_read(PLANNING_INDEX_PATH))
    assert (
        "Window 749-752 ACTIVE through Phase 750 master-roadmap and M-series-lane update" in text
        or "Window 749-752 CLOSED via Phase 752 closure gate" in text
        or "Window 753-756 CLOSED via Phase 756 closure gate" in text
    )
    assert "**Master Completion Roadmap v0.1** ⬅ CURRENT" in text
    assert (
        "**What's next** → master roadmap + current window sequence lock" in text
        or "**What's next** → master roadmap + latest main-lane sequence lock" in text
    )
    assert (
        "Window 749-752 is now active through Phase 750." in text
        or "Window 749-752 is now closed via Phase 752." in text
        or "Window 753-756 is now closed via Phase 756." in text
    )


def test_planning_index_points_archived_docs_to_master_roadmap_successor() -> None:
    text = _normalized(_read(PLANNING_INDEX_PATH))
    assert "Recently archived forward-planning docs:" in text
    assert "`docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` → successor: `docs/specs/ilc_master_completion_roadmap_v0.1.md`" in text
    assert "`docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md` → successor: `docs/specs/ilc_master_completion_roadmap_v0.1.md`" in text


def test_planning_index_no_longer_treats_archived_docs_as_session_start_canon() -> None:
    session_section = _normalized(_read(PLANNING_INDEX_PATH).split("## 2. Constitutional / Decision Documents")[0])
    assert "docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md" not in session_section
    assert "docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md" not in session_section
    assert "docs/specs/ilc_master_completion_roadmap_v0.1.md" in session_section


def test_launch_roadmap_v03_supersession_is_recorded_in_index() -> None:
    text = _normalized(_read(PLANNING_INDEX_PATH))
    assert "Launch Roadmap v0.3" in text
    assert "superseded by v0.4 and its surviving forward note is now carried by the master roadmap §6" in text


def test_decision_log_and_runtime_paths_remain_untouched() -> None:
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_751_commit_touches_expected_paths_only_and_no_runtime_files() -> None:
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
