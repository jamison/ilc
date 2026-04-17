from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_phase_701_706_sequence_lock_v0.1.md")
TEST_PATH = Path("tests/test_phase_701_window_701_706_sequence_lock.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_701_g8_window_701_706_sequence_lock_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Inherited gates and constraints",
    "## 3. Window meaning",
    "## 4. Phase table and sequencing",
    "## 5. Non-goals",
    "## 6. Source inputs",
)
REQUIRED_TOKENS = (
    "window_701_706_sequence_lock_active",
    "phase_703_four_component_kernel_scope_locked",
    "phase_703_candidate_profiles_even_bal_robust_refine",
    "phase_703_adapt_excluded_from_fixed_vector_sweep",
    "phase_703_replay_tiers_100_agent_preflight_10000_agent_evidence",
    "cdl_066_017_067_carry_forward_not_in_scope_for_ratification_here",
    "window_701_706_no_rows_5_9_reopened",
)
PHASE_701_SUBJECT = ("phase 701", "window 701-706 sequence lock")
PHASE_701_BACKFILL_SUBJECT = ("phase 701", "walkthrough", "backfill")
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
    raise AssertionError("phase_701_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
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


def test_artifact_locks_phase_703_kernel_scope_correctly() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`reuse`" in text
    assert "`contradiction_resilience`" in text
    assert "`validation_integrity`" in text
    assert "`path_uplift`" in text
    assert "stake" in text
    assert "diversity-floor" in text
    assert "temporal-decay" in text


def test_artifact_records_fixed_vector_family_and_replay_tiers() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`EVEN = 0.25 / 0.25 / 0.25 / 0.25`" in text
    assert "`BAL = 0.35 / 0.25 / 0.20 / 0.20`" in text
    assert "`ROBUST = 0.20 / 0.45 / 0.20 / 0.15`" in text
    assert "`REFINE = 0.45 / 0.15 / 0.20 / 0.20`" in text
    assert "`100-agent` deterministic preflight" in text
    assert "`10,000-agent` deterministic evidence-bearing" in text


def test_artifact_explicitly_excludes_adapt_and_ratification_of_open_cdls() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`ADAPT` is excluded" in text
    assert "no ratification of `CDL-066`, `CDL-017`, or `CDL-067`" in text


def test_decision_log_and_runtime_paths_remain_unmutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_701_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_701_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
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
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0

    result_ilc_core = subprocess.run(
        ["git", "diff", "--exit-code", "--", "ilc_core/"],
        capture_output=True,
        text=True,
    )
    assert result_ilc_core.returncode == 0

    result_ilc_consensus = subprocess.run(
        ["git", "diff", "--exit-code", "--", "ilc_consensus/"],
        capture_output=True,
        text=True,
    )
    assert result_ilc_consensus.returncode == 0


def test_phase_701_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_701_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_701_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_701_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
