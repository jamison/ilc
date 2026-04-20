from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_phase_745_748_sequence_lock_v0.1.md")
TEST_PATH = Path("tests/test_phase_745_window_745_748_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_745_g8_window_745_748_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
M_SERIES_PATH = Path("docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Inherited gates and constraints",
    "## 3. Window meaning",
    "## 4. Convergence-window commissioning posture at open",
    "## 5. ADR-0031 housekeeping posture at open",
    "## 6. Phase table and sequencing",
    "## 7. Explicit separation obligations",
    "## 8. Non-goals",
    "## 9. Source inputs",
)
REQUIRED_TOKENS = (
    "window_745_748_sequence_lock_active",
    "track_b_m019_complete_m020_next",
    "convergence_window_commissioning_window_active",
    "convergence_window_artifact_gated_entry_required",
    "adr_0031_housekeeping_acceptance_authorized_in_window_745_748",
    "rows_5_and_7_remain_spec_closed_runtime_pending_at_window_open",
    "no_cdl_017_ratification_in_window_745_748",
    "no_option_b_graduation_in_window_745_748",
    "no_legal_facts_annex_in_window_745_748",
    "convergence_window_not_open_at_phase_745",
    "convergence_window_requires_three_committed_artifact_classes",
    "adr_0031_proto_contract_already_present",
    "adr_0031_acceptance_requires_no_new_runtime_work",
)
PHASE_MAIN_SUBJECT = ("phase 745", "window 745-748 sequence lock")
PHASE_BACKFILL_SUBJECT = ("phase 745", "walkthrough", "backfill")
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
    raise AssertionError("phase_745_commit_not_present_in_local_history")


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
    assert "Window `739-744` is closed." in text
    assert "Capsule `v5.2` is the frozen main-lane frontier at sequence-lock time." in text
    assert "`CDL-017` remains open and unratified." in text
    assert "Rows `5` and `7` remain `spec_closed_runtime_pending`." in text
    assert "Row `8` remains an inherited criteria lock and is not a runtime-confirmation lane in this window." in text
    assert (
        "`**Current:** M-019 (Adversarial Hardening and Byzantine Fault Simulation) complete. "
        "run_m019_adversarial_hardening_verdict=pass`" in text
    )
    assert "`**Next planned phase:** M-020 (External Security Audit Preparation)`" in text


def test_artifact_records_convergence_window_as_commissioning_only_and_artifact_gated() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "The convergence window commissioned by this packet is a later bounded window." in text
    assert "It does not open at Phase `745`; it is only defined here." in text
    assert "The convergence window does not open until **all three** committed artifact classes exist:" in text
    assert "a committed Gemini runtime artifact bundle satisfying the Phase `741` Section `3.2` censorship-resistance contract" in text
    assert "a committed `SIM-LEAKAGE-01` results artifact for row `5`" in text
    assert "a committed Gemini strong-exitability drill results artifact" in text
    assert "the artifact bundle controls. The numeric label does not." in text
    assert "uncommitted Gemini worktree draft remains below that authority threshold and therefore does not satisfy convergence entry." in text


def test_artifact_records_adr_0031_as_housekeeping_only_with_proto_already_present() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "ADR-0031 enters this window as a housekeeping-only candidate rather than as a live implementation gate." in text
    assert "`repeated EdgeRecord edges = 2;`" in text
    assert "`repeated HyperEdgeRecord hyperedges = 3;`" in text
    assert "`message EdgeRecord { ... }`" in text
    assert "`message HyperEdgeRecord { ... }`" in text
    assert "accept ADR-0031 only if re-reading the ADR confirms that no additional implementation work, wire-format change, or runtime mutation is still missing" in text


def test_artifact_records_phase_table_boundaries_and_non_goals() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "| 1 | 745 | sequence lock | gate / planning |" in text
    assert "| 2 | 746 | convergence-window commissioning spec + ADR-0031 housekeeping check | planning + ADR housekeeping |" in text
    assert "| 4 | 748 | coherence report + closure gate | gate / handoff |" in text
    assert "Phase `748` is the closure gate for the window." in text
    assert "any ratification of `CDL-017`," in text
    assert "any move of row `5` to `runtime_closed`," in text
    assert "any move of row `7` to `runtime_closed`," in text
    assert "the deferred legal positioning technical facts annex," in text
    assert "any mutation of `ilc_core/` or `ilc_consensus/`," in text
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_artifact_does_not_treat_uncommitted_drafts_as_authoritative() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "uncommitted working-tree drafts do not satisfy any convergence-window entry condition." in text


def test_phase_745_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
        assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
        assert not any(
            path == "ilc_consensus" or path.startswith("ilc_consensus/")
            for path in changed_paths
        )
        return

    assert _current_phase_paths_in_worktree(EXACT_REQUIRED_MAIN_PATHS) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_745_backfill_commit_touches_walkthrough_status_and_planning_index_only() -> None:
    commit_ref = _try_resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
        assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert str(M_SERIES_PATH) not in changed_paths
        return

    assert _current_phase_paths_in_worktree(EXACT_REQUIRED_BACKFILL_PATHS) == EXACT_REQUIRED_BACKFILL_PATHS
