from __future__ import annotations

import subprocess
from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_coherence_report_726_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v4.9.md")
CLOSURE_GATE_PATH = Path("docs/specs/ilc_window_723_726_closure_gate_726_v0.1.md")
TEST_PATH = Path(
    "tests/test_phase_726_coherence_report_capsule_v4_9_and_window_723_726_closure_gate.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_726_g8_coherence_report_capsule_v4_9_and_window_723_726_closure_gate_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
COHERENCE_HEADINGS = (
    "## 1. Baseline",
    "## 2. Window 723-726 completed outputs",
    "## 3. No-activation and no-ratification boundary",
    "## 4. Final eligibility and deferment posture",
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
    "window_723_726_coherence_report_published",
    "no_financial_shard_activation_occurred_in_window_723_726",
    "no_cdl_ratification_occurred_in_window_723_726",
    "window_727_732_carry_forward_explicit",
    "window_723_726_closure_gate_published",
    "track_b_status_verified_from_status_tail",
)
PHASE_MAIN_SUBJECT = ("phase 726", "coherence report", "capsule v4.9", "closure gate")
PHASE_BACKFILL_SUBJECT = ("phase 726", "walkthrough", "backfill")
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
    raise AssertionError("phase_726_commit_not_present_in_local_history")


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


def test_coherence_report_records_final_posture() -> None:
    text = _read(COHERENCE_PATH)
    assert "the concept remains a real later-lane candidate" in text
    assert "current activation is explicitly not eligible" in text
    assert "any new CDL opening remains explicitly deferred" in text
    assert "relation to `CDL-062`: separate" in text
    assert "relation to ADR-0022/private-gated access hardening: separate" in text


def test_capsule_v4_9_records_live_frontier_and_track_b_line() -> None:
    text = _read(CAPSULE_PATH)
    assert "Capsule v4.9 supersedes v4.8." in text
    assert "Window 723-726 is now closed as the sequestered financial-shard eligibility" in text
    assert "Window 727-732 is the next planned continuation." in text
    assert "Track B status: `M-015 complete; next planned phase M-016 (Workload D: Replayability and State Extraction)`" in text


def test_closure_gate_confirms_completion_boundary_and_carry_forward() -> None:
    text = _read(CLOSURE_GATE_PATH)
    assert "Phase `723` sequence lock" in text
    assert "Phase `724` financial-shard eligibility prefilter" in text
    assert "Phase `725` post-launch trigger matrix" in text
    assert "Phase `725` contagion / firewall prerequisites" in text
    assert "no financial-shard activation occurred in-window" in text
    assert "Window `727-732` is the next main-lane continuation." in text


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


def test_phase_726_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_726_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
