from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_adjacent_gated_economy_carry_forward_selection_728_v0.1.md")
TEST_PATH = Path(
    "tests/test_phase_728_adjacent_gated_economy_carry_forward_selection_and_boundary_lock.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_728_g8_adjacent_gated_economy_carry_forward_selection_and_boundary_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Candidate carry-forward set",
    "## 3. Selected lane and justification",
    "## 4. Boundary and separation obligations",
    "## 5. Deferred alternatives",
    "## 6. Non-goals",
    "## 7. Source inputs",
)
REQUIRED_TOKENS = (
    "adjacent_gated_economy_carry_forward_selected",
    "rights_licenses_and_private_gated_hardening_selected_for_729_730",
    "financial_shard_lane_remains_deferred_in_727_732",
    "cdl_062_lane_remains_separate_from_private_gated_hardening",
    "no_new_cdl_opening_recommended_in_phase_728",
)
PHASE_MAIN_SUBJECT = ("phase 728", "gated economy carry-forward selection")
PHASE_BACKFILL_SUBJECT = ("phase 728", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
    raise AssertionError("phase_728_commit_not_present_in_local_history")


def _try_resolve_commit_ref(
    subject_tokens: tuple[str, ...], expected_paths: set[str]
) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_artifact_exists_and_contains_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_artifact_records_candidate_set_and_selection() -> None:
    text = _read(ARTIFACT_PATH)
    assert "reopen financial-shard trigger work" in text
    assert "merge the window into `CDL-062` sovereign-substrate work" in text
    assert "advance adjacent gated-economy hardening around rights, licensing, and\n   private/gated contract surfaces" in text
    assert "The selected lane for `729-730` is adjacent gated-economy hardening." in text


def test_artifact_records_why_financial_shard_and_cdl_062_remain_deferred() -> None:
    text = _read(ARTIFACT_PATH)
    assert "financial-shard activation remains deferred and not yet eligible" in text
    assert "`CDL-062` remains separate from private/gated hardening" in text
    assert "ADR-0022 remains the architectural anchor" in text
    assert "no new CDL opening tied to this lane" in text


def test_artifact_records_non_goals_and_runtime_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert "decision-log mutation" in text
    assert "runtime implementation" in text
    assert "any mutation of `ilc_core/` or `ilc_consensus/`" in text
    assert "The task here is lane selection and boundary lock, not constitutional closure." in text


def test_decision_log_and_runtime_surfaces_remain_unmutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
    )
    if main_commit and backfill_commit:
        for commit_ref in (main_commit, backfill_commit):
            changed_paths = _changed_paths_for_commit(commit_ref)
            assert str(DECISION_LOG_PATH) not in changed_paths
            assert not any(
                path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths
            )
            assert not any(
                path == "ilc_consensus" or path.startswith("ilc_consensus/")
                for path in changed_paths
            )
        return

    result_decision = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert not result_decision.stdout.strip()


def test_phase_728_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_728_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
