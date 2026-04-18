from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_sequestered_financial_shard_eligibility_prefilter_724_v0.1.md")
TEST_PATH = Path(
    "tests/test_phase_724_financial_shard_eligibility_prefilter_and_lane_separation.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_724_g8_financial_shard_eligibility_prefilter_and_lane_separation_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Candidate scope",
    "## 3. Eligibility prefilter",
    "## 4. Separation boundaries",
    "## 5. Current verdict",
)
REQUIRED_TOKENS = (
    "financial_shard_eligibility_prefilter_complete",
    "historical_adr_0018_reference_not_live_accepted_adr",
    "cdl_062_sovereign_substrate_lane_remains_separate",
    "private_gated_access_lane_remains_separate",
    "current_financial_shard_activation_not_eligible",
)
PHASE_MAIN_SUBJECT = ("phase 724", "financial shard eligibility prefilter")
PHASE_BACKFILL_SUBJECT = ("phase 724", "walkthrough", "backfill")
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
    raise AssertionError("phase_724_commit_not_present_in_local_history")


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


def test_artifact_records_candidate_scope_and_current_verdict() -> None:
    text = _read(ARTIFACT_PATH)
    assert "securities-like trading, HFT, and financial instruments" in text
    assert "The sequestered financial-shard concept remains a real later-lane candidate" in text
    assert "current financial-shard activation is not eligible" in text


def test_artifact_records_prefilter_and_b_hft_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert "public launch must already exist" in text
    assert "at least one post-launch monitoring cycle must have completed" in text
    assert "a concrete demand signal" in text
    assert "requires a separate `B_hft` lane rather\nthan sharing `B_e`" in text


def test_artifact_records_lane_separation_boundaries() -> None:
    text = _read(ARTIFACT_PATH)
    assert "This lane is not ordinary shard-lifecycle law." in text
    assert "This lane is not ADR-0022/private-gated access hardening." in text
    assert "This lane is not `CDL-062`." in text


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
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_724_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_724_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
