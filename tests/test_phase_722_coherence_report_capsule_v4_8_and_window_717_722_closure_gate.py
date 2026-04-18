from __future__ import annotations

import subprocess
from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_coherence_report_722_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v4.8.md")
CLOSURE_GATE_PATH = Path("docs/specs/ilc_window_717_722_closure_gate_722_v0.1.md")
TEST_PATH = Path("tests/test_phase_722_coherence_report_capsule_v4_8_and_window_717_722_closure_gate.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_722_g8_coherence_report_capsule_v4_8_and_window_717_722_closure_gate_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
COHERENCE_HEADINGS = (
    "## 1. Baseline",
    "## 2. Window 717-722 completed outputs",
    "## 3. No-ratification and no-results boundary",
    "## 4. Final ADR-0015 family disposition",
    "## 5. Carry-forward",
)
CLOSURE_GATE_HEADINGS = (
    "## 1. Completion checklist",
    "## 2. Boundary confirmations",
    "## 3. Track B verification",
    "## 4. Carry-forward",
    "## 5. Closure verdict",
)
REQUIRED_TOKENS = (
    "window_717_722_coherence_report_published",
    "no_cdl_ratification_occurred_in_window_717_722",
    "phase_721_commissioning_only_results_not_claimed",
    "window_723_726_carry_forward_explicit",
    "window_717_722_closure_gate_published",
    "track_b_status_verified_from_status_tail",
)
PHASE_MAIN_SUBJECT = ("phase 722", "coherence report", "capsule v4.8", "closure gate")
PHASE_BACKFILL_SUBJECT = ("phase 722", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(CLOSURE_GATE_PATH),
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
    raise AssertionError("phase_722_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_artifacts_exist_and_contain_required_headings_in_order() -> None:
    coherence_text = _read(COHERENCE_PATH)
    gate_text = _read(CLOSURE_GATE_PATH)
    coherence_positions = [coherence_text.index(heading) for heading in COHERENCE_HEADINGS]
    gate_positions = [gate_text.index(heading) for heading in CLOSURE_GATE_HEADINGS]
    assert coherence_positions == sorted(coherence_positions)
    assert gate_positions == sorted(gate_positions)


def test_artifacts_contain_required_tokens() -> None:
    combined = "\n".join((_read(COHERENCE_PATH), _read(CLOSURE_GATE_PATH)))
    for token in REQUIRED_TOKENS:
        assert token in combined


def test_coherence_report_records_final_family_state() -> None:
    text = _read(COHERENCE_PATH)
    assert "transfer tax: `amended_accept` and `launch_bound`" in text
    assert "cooling period: `amended_accept` and `launch_bound`" in text
    assert "commons dedication: `amended_accept` and `launch_bound`" in text
    assert "leasehold / reversion: `deferred`" in text
    assert "any new transfer-economics CDL opening is explicitly deferred" in text


def test_capsule_v4_8_records_live_frontier_and_track_b_line() -> None:
    text = _read(CAPSULE_PATH)
    assert "Capsule v4.8 supersedes v4.7." in text
    assert "Window 717-722 is now closed as the ADR-0015 family closure lane." in text
    assert "Window 723-726 is the next planned continuation." in text
    assert "Track B status: `M-015 complete; next planned phase M-016 (Workload D: Replayability and State Extraction)`" in text


def test_closure_gate_confirms_completion_boundary_and_carry_forward() -> None:
    text = _read(CLOSURE_GATE_PATH)
    assert "Phase `717` sequence lock" in text
    assert "Phase `718` ADR-0015 family inventory and scoping" in text
    assert "Phase `719` transfer-tax and cooling package" in text
    assert "Phase `720` commons dedication and treasury-routing note" in text
    assert "Phase `721` ADR-0015 disposition" in text
    assert "no simulation-result claim was made in-window" in text
    assert "Window `723-726` as the next main-lane continuation." in text


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


def test_phase_722_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_722_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
