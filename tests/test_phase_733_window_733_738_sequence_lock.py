from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_phase_733_738_sequence_lock_v0.1.md")
TEST_PATH = Path("tests/test_phase_733_window_733_738_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_733_g8_window_733_738_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Inherited gates and constraints",
    "## 3. Pre-window conversation record (Q1–Q6)",
    "## 4. Window meaning",
    "## 5. Phase table and sequencing",
    "## 6. Explicit separation obligations",
    "## 7. Non-goals",
    "## 8. Source inputs",
)
REQUIRED_TOKENS = (
    "window_733_738_sequence_lock_active",
    "cdl_017_prelock_window_active",
    "pre_window_conversation_record_complete_2026_04_19",
    "no_cdl_017_ratification_in_window_733_738",
    "cdl_068_opens_this_window",
    "sim_validator_01_commissioned_phase_711",
    "sim_topology_01_commissioned_phase_711",
    "track_b_m017_complete_m018_next",
)
PHASE_MAIN_SUBJECT = ("phase 733", "window 733-738 sequence lock")
PHASE_BACKFILL_SUBJECT = ("phase 733", "walkthrough", "backfill")
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
    raise AssertionError("phase_733_commit_not_present_in_local_history")


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


def test_artifact_records_live_frontier_and_track_b_line() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Window `727-732` is closed. Capsule `v5.0` is the live main-lane frontier" in text
    assert "`CDL-017` remains open and unratified." in text
    assert "`**Current:** M-017 (Workload E: Validator Operability) complete natively.`" in text
    assert "`**Next planned phase:** M-018 (Workload F: Bounded Public Auditability)`" in text


def test_artifact_imports_q1_q6_record_and_drafting_notes() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Q1 = derived sub-key with governance-internal linkage" in text
    assert "Q2 = SIM-VALIDATOR-01 must demonstrate equivocation rendered economically" in text
    assert "Q3 = new CDL for topology shuffle authorization, not CDL-039 amendment." in text
    assert "Q4 = validation pools are separate CDL scope, not CDL-017." in text
    assert "Q5 = epoch-hash for mainnet v1 with explicit VRF upgrade forward obligation" in text
    assert "Q6 = metric definition locked (`validator_cluster_id`), numeric thresholds" in text
    assert "the derivation relationship is assertable to the governance mechanism during" in text
    assert "epoch-hash is the production v1 randomness source for topology shuffle; a VRF" in text


def test_artifact_records_phase_table_boundaries_and_closure_phase() -> None:
    text = _read(ARTIFACT_PATH)
    assert "| 1 | 733 | sequence lock + Q1-Q6 record import |" in text
    assert "| 6 | 738 | coherence report + capsule v5.1 + closure gate |" in text
    assert "only Phase `736` may open `CDL-068`" in text
    assert "Phase `738` is the closure gate for the window." in text
    assert "if `SIM-TOPOLOGY-01` is only partial-complete in Phase `735`" in text


def test_artifact_records_non_ratification_boundary_and_non_goals() -> None:
    text = _read(ARTIFACT_PATH)
    assert "This window does not ratify `CDL-017`. It does not ratify `CDL-068`." in text
    assert "No hidden runtime implementation is authorized" in text
    assert "any ratification of `CDL-017`," in text
    assert "any claim that Q1-Q6 were newly resolved in this phase," in text
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_733_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in _changed_paths_for_commit(commit_ref)
    assert not any(
        path == "ilc_core" or path.startswith("ilc_core/")
        for path in _changed_paths_for_commit(commit_ref)
    )
    assert not any(
        path == "ilc_consensus" or path.startswith("ilc_consensus/")
        for path in _changed_paths_for_commit(commit_ref)
    )


def test_phase_733_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in _changed_paths_for_commit(commit_ref)
    assert not any(
        path == "ilc_core" or path.startswith("ilc_core/")
        for path in _changed_paths_for_commit(commit_ref)
    )
    assert not any(
        path == "ilc_consensus" or path.startswith("ilc_consensus/")
        for path in _changed_paths_for_commit(commit_ref)
    )
