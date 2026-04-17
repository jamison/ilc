from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_phase_713_716_sequence_lock_v0.1.md")
TEST_PATH = Path("tests/test_phase_713_window_713_716_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_713_g8_window_713_716_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Inherited gates and constraints",
    "## 3. Window meaning",
    "## 4. Phase table and sequencing",
    "## 5. Live parameter inventory obligation",
    "## 6. Non-goals",
    "## 7. Source inputs",
)
REQUIRED_TOKENS = (
    "window_713_716_sequence_lock_active",
    "law_vs_freedom_classification_required_for_all_live_gossip_parameters",
    "cdl_060_and_cdl_061_settled_not_reopened_in_window_713_716",
    "no_cdl_ratification_in_window_713_716",
    "partition_repair_and_missing_signal_commissioning_not_results",
    "track_b_status_must_be_verified_from_status_tail",
)
PHASE_MAIN_SUBJECT = ("phase 713", "window 713-716 sequence lock")
PHASE_BACKFILL_SUBJECT = ("phase 713", "walkthrough", "backfill")
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
    raise AssertionError("phase_713_commit_not_present_in_local_history")


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


def test_artifact_locks_window_meaning_and_no_ratification_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert "adaptive-gossip and resilience-operationalization lane" in text
    assert "no CDL ratification" in text
    assert "no ratification of `CDL-017`" in text
    assert "no opening of `CDL-062`" in text
    assert "no final Option B production selection" in text


def test_artifact_records_phase_table_and_closure_phase() -> None:
    text = _read(ARTIFACT_PATH)
    assert "| 1 | 713 | sequence lock |" in text
    assert "| 4 | 716 | closure |" in text
    assert "Phase `715` commissions evidence and defines behavior" in text
    assert "Phase `716` may summarize only what Phases `714-715` actually establish" in text


def test_artifact_records_inventory_obligation_and_source_inputs() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`PEER_DISCOVERY_MODE`" in text
    assert "`MAX_PEERS`" in text
    assert "`MAX_FANOUT`" in text
    assert "`request_timeout_seconds`" in text
    assert "`ILC-Epoch`" in text
    assert "docs/specs/ilc_cdl_060_gossip_centrality_extension_ratification_evidence_541_v0.1.md" in text


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


def test_phase_713_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_713_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
