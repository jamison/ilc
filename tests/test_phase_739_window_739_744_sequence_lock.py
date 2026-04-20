from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_phase_739_744_sequence_lock_v0.1.md")
TEST_PATH = Path("tests/test_phase_739_window_739_744_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_739_g8_window_739_744_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Inherited gates and constraints",
    "## 3. Window meaning",
    "## 4. Row 5 and Row 7 runtime posture at open",
    "## 5. CDL-068 ratification posture at open",
    "## 6. Phase table and sequencing",
    "## 7. Explicit separation obligations",
    "## 8. Non-goals",
    "## 9. Source inputs",
)
REQUIRED_TOKENS = (
    "window_739_744_sequence_lock_active",
    "rows_5_and_7_runtime_form_window_active",
    "row_5_runtime_evidence_packaging_window_active",
    "row_7_runtime_evidence_packaging_window_active",
    "rows_5_and_7_remain_spec_closed_runtime_pending_at_window_open",
    "cdl_068_evidence_checklist_complete_at_window_open",
    "cdl_068_ratification_authorized_in_window_739_744",
    "cdl_068_ratification_independent_of_rows_5_and_7_runtime_closure",
    "no_cdl_017_ratification_in_window_739_744",
    "track_b_m018_complete_m019_next",
)
PHASE_MAIN_SUBJECT = ("phase 739", "window 739-744 sequence lock")
PHASE_BACKFILL_SUBJECT = ("phase 739", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
    str(PLANNING_INDEX_PATH),
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
    raise AssertionError("phase_739_commit_not_present_in_local_history")


def test_artifact_exists_and_contains_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_artifact_records_live_frontier_and_track_b_line() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Window `733-738` is closed. Capsule `v5.1` is the live main-lane frontier" in text
    assert "`CDL-017` remains open and unratified." in text
    assert "`CDL-068` is already open and unratified at window entry." in text
    assert "Rows `5` and `7` remain `spec_closed_runtime_pending`." in text
    assert "Row `8` remains an inherited criteria lock and is not a runtime-confirmation lane in this window." in text
    assert (
        "`**Current:** M-018 (Workload F: Bounded Public Auditability) complete. "
        "run_m018_workload_f_verdict=pass`" in text
    )
    assert "`**Next planned phase:** M-019 (Adversarial Hardening and Byzantine Fault Simulation)`" in text


def test_artifact_records_rows_5_and_7_runtime_pending_posture_honestly() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "`row_5_post_697_status=spec_closed_runtime_pending`" in text
    assert "live operator-path leakage measurement on a multi-machine validator network" in text
    assert "public-legitimacy observability floor must remain intact" in text
    assert "`row_7_post_698_status=spec_closed_runtime_pending`" in text
    assert "TLC proof exists for `N=4`, `F=1`, `MaxRound=5`, and `Liveness`" in text
    assert "censorship-resistance runtime confirmation may use Gemini `M-019` censoring-validator evidence" in text
    assert "strong exitability does not share the same evidence source as `M-019` and requires a separate export / verify / replay / migrate drill" in text
    assert "export, independent verify, replay, and migrate without privileged original-operator consent" in text
    assert "the honest result is commissioning / evidence-package completion only" in text


def test_artifact_records_cdl_068_checklist_complete_and_ratification_ready() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "`CDL-068` enters this window open, checklist-complete, and eligible for ratification." in text
    assert "`SIM-TOPOLOGY-01` completed in Phase `735` with `recommended_k_degree 4`" in text
    assert "cadence `1`, fanout `3`" in text
    assert "`distinct_cluster_floor_recommendation 4`" in text
    assert "`max_cluster_share_ceiling_recommendation 33`" in text
    assert "`SIM-VALIDATOR-01` completed in Phase `734` with `vrf_upgrade_threshold_validator_count 10`" in text
    assert "`stake_floor_candidate_interval_micro_ecu 400000000-450000000`" in text
    assert "Phase `743` may therefore ratify `CDL-068`" in text
    assert "all six inherited prelock criteria from the Phase `736` opening" in text
    assert "commit 1 publishes the ratification artifact, evidence-checklist satisfaction record, and tests" in text
    assert "commit 2 mutates exactly the `CDL-068` row" in text


def test_artifact_records_phase_table_boundaries_non_goals_and_clean_decision_log() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "| 1 | 739 | sequence lock |" in text
    assert "| 5 | 743 | `CDL-068` ratification | constitutional ratification |" in text
    assert "| 6 | 744 | coherence report + capsule v5.2 + closure gate |" in text
    assert "only Phase `743` may mutate the decision log" in text
    assert "Phase `744` is the closure gate for the window." in text
    assert "any ratification of `CDL-017`," in text
    assert "any sovereign substrate selection," in text
    assert "any mutation of `ilc_core/` or `ilc_consensus/`," in text
    assert "any claim that row `8` was advanced or runtime-confirmed in this window," in text
    assert "No hidden runtime closure is authorized by sequence-lock rhetoric." in text
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_739_main_commit_touches_expected_paths_only() -> None:
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


def test_phase_739_backfill_commit_touches_walkthrough_status_and_planning_index_only() -> None:
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
