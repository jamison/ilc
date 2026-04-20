from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


COHERENCE_PATH = Path(
    "docs/specs/ilc_coherence_report_phase_738_window_733_738_v0.1.md"
)
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v5.1.md")
GATE_PATH = Path("docs/specs/ilc_window_733_738_closure_gate_738_v0.1.md")
TEST_PATH = Path("tests/test_phase_738_window_733_738_closure_gate.py")
PRELOCK_PATH = Path("docs/research/ilc_validator_agent_design_evidence_v0.1.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_738_g8_coherence_report_capsule_v5_1_and_window_733_738_closure_gate_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_MAIN_SUBJECT = ("phase 738", "capsule v5.1", "window 733-738 closure gate")
PHASE_BACKFILL_SUBJECT = ("phase 738", "walkthrough", "status", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(GATE_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
    str(ROADMAP_PATH),
}

# Category 3 selftest guard chain: latest prior closure-gate env var plus Phase 738.
CATEGORY_3_SELFTEST_ENV_CHAIN = (
    "ILC_PHASE_619_GATE_SELFTEST=1",
    "ILC_PHASE_738_GATE_SELFTEST=1",
)


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
    raise AssertionError("phase_738_commit_not_present_in_local_history")


def _skip_if_category_3_selftest() -> None:
    if os.environ.get("ILC_PHASE_738_GATE_SELFTEST") == "1":
        pytest.skip("phase_738_selftest_context_skip_commit_history_checks")


def test_coherence_report_exists_and_contains_required_assertions() -> None:
    text = _read(COHERENCE_PATH)
    required = [
        "no `CDL-017` ratification occurred in-window",
        "`CDL-068` opened in Phase `736` and remains unratified at window close",
        "sim_validator_01_verdict=pass",
        "sim_topology_01_verdict=pass",
        "cdl_017_prelock_codex_side_complete",
        "adr_0019_verdict_accepted_with_scope_amendment",
        "track_b_m017_complete_m018_next",
        "all six Q1-Q6 answers were imported from the settled 2026-04-19 pre-window",
    ]
    for item in required:
        assert item in text


def test_capsule_v51_exists_and_supersedes_v50() -> None:
    text = _read(CAPSULE_PATH)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.0.md" in text
    assert "Capsule v5.1 supersedes v5.0." in text
    assert "Window 733-738 is now closed as the CDL-017 prelock evidence lane." in text
    assert "Window 739-744 is the next main-lane continuation." in text


def test_capsule_contains_window_733_738_closure_summary_and_gap_1_update() -> None:
    text = _read(CAPSULE_PATH)
    assert "## 5. Window 733-738 Closure Summary" in text
    assert "Gap 1 is now `PRELOCK_EVIDENCE_COMPLETE_CODEX_SIDE — pending Gemini M-022 for ratification`" in text
    assert "`stake_floor_candidate_interval_micro_ecu 400000000-450000000`" in text
    assert "`recommended_k_degree 4`" in text
    assert "`distinct_cluster_floor_recommendation 4`" in text
    assert "`max_cluster_share_ceiling_recommendation 33`" in text


def test_closure_gate_exists_and_contains_required_full_pass_tokens() -> None:
    text = _read(GATE_PATH)
    assert "window_733_738_closure_gate_pass" in text
    assert "cdl_017_prelock_codex_side_complete" in text
    assert "window_739_744_is_next_main_lane" in text
    assert "track_b_m017_complete_m018_next" in text
    assert "The Codex-side prelock is complete; the Gemini M-022 handoff is the remaining" in text


def test_gate_completion_token_matches_phase_737_artifact_and_is_exclusive() -> None:
    gate = _read(GATE_PATH)
    prelock = _read(PRELOCK_PATH)
    assert "cdl_017_prelock_codex_side_complete" in prelock
    assert "cdl_017_prelock_codex_side_advanced_with_carry_forward" not in prelock
    assert "cdl_017_prelock_codex_side_complete" in gate
    assert "cdl_017_prelock_codex_side_advanced_with_carry_forward" not in gate


def test_closure_gate_names_required_carry_forward_and_defers_ratification() -> None:
    text = _read(GATE_PATH)
    required = [
        "rows `5` and `7` runtime form as the primary next-window objective",
        "`CDL-068` ratification evidence and later ratification text",
        "stronger public-substrate replayability proof",
        "Option B graduation gate in Window `745-748`",
        "`CDL-017` ratification is deferred to the Mysticeti convergence window.",
    ]
    for item in required:
        assert item in text


def test_no_cdl_ratification_is_claimed_for_cdl_017_or_cdl_068() -> None:
    combined = "\n".join(
        [
            _read(COHERENCE_PATH),
            _read(CAPSULE_PATH),
            _read(GATE_PATH),
        ]
    )
    assert "CDL-017 ratified" not in combined
    assert "CDL-068 ratified" not in combined


def test_category_3_selftest_guard_chain_extends_latest_prior_closure_gate_chain() -> None:
    text = _read(TEST_PATH)
    assert "Category 3 selftest guard chain" in text
    for token in CATEGORY_3_SELFTEST_ENV_CHAIN:
        assert token in text


def test_phase_738_main_commit_touches_expected_paths_only() -> None:
    _skip_if_category_3_selftest()
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(
        path == "ilc_core" or path.startswith("ilc_core/")
        for path in changed_paths
    )
    assert not any(
        path == "ilc_consensus" or path.startswith("ilc_consensus/")
        for path in changed_paths
    )


def test_phase_738_backfill_commit_touches_expected_paths_only() -> None:
    _skip_if_category_3_selftest()
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert not any(
        path == "ilc_core" or path.startswith("ilc_core/")
        for path in changed_paths
    )
    assert not any(
        path == "ilc_consensus" or path.startswith("ilc_consensus/")
        for path in changed_paths
    )


def test_backfill_records_walkthrough_status_and_launch_roadmap_frontier() -> None:
    assert WALKTHROUGH_PATH.exists()
    status = _read(STATUS_PATH)
    roadmap = _read(ROADMAP_PATH)
    assert "## Phase 738" in status
    assert "cdl_017_prelock_codex_side_complete" in status
    assert "Window 739-744 — MVP gate runtime form (rows 5 and 7) + CDL-068 ratification evidence." in status
    assert (
        "Session context**: Window 733-738 CLOSED (today); capsule v5.1 current; M-017 complete; next planned phase M-018"
        in roadmap
    )
    assert "733-738 | CDL-017 prelock evidence window" in roadmap
    assert "PRELOCK_EVIDENCE_COMPLETE_CODEX_SIDE" in roadmap
