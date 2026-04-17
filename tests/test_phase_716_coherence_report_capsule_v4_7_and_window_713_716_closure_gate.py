from __future__ import annotations

import subprocess
from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_coherence_report_716_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v4.7.md")
CLOSURE_PATH = Path("docs/specs/ilc_window_713_716_closure_gate_716_v0.1.md")
TEST_PATH = Path("tests/test_phase_716_coherence_report_capsule_v4_7_and_window_713_716_closure_gate.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_716_g8_coherence_report_capsule_v4_7_and_window_713_716_closure_gate_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
COHERENCE_REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Window 713-716 completed outputs",
    "## 3. No-ratification boundary",
    "## 4. Commissioning-only resilience state",
    "## 5. Carry-forward",
)
CAPSULE_REQUIRED_HEADINGS = (
    "## 1. Current frontier state",
    "## 2. Frozen inherited boundary state",
    "## 3. Window 713-716 closure state",
    "## 4. Remaining later-lane blockers",
    "## 5. Next authorized continuation",
)
CLOSURE_REQUIRED_HEADINGS = (
    "## 1. Completion checklist",
    "## 2. Boundary confirmations",
    "## 3. Track B verification",
    "## 4. Carry-forward",
    "## 5. Closure verdict",
)
COHERENCE_REQUIRED_TOKENS = (
    "window_713_716_coherence_report_published",
    "phase_714_every_live_gossip_parameter_classified",
    "phase_715_commissioning_only_no_results_claimed",
    "no_cdl_ratification_occurred_in_window_713_716",
    "topology_shuffling_still_unratified_in_window_713_716",
)
CLOSURE_REQUIRED_TOKENS = (
    "window_713_716_closure_gate_published",
    "no_cdl_ratification_occurred_in_window_713_716",
    "benchmark_commissioning_completed_without_results_claim",
    "track_b_status_verified_from_status_tail",
    "window_717_722_carry_forward_explicit",
)
PHASE_MAIN_SUBJECT = ("phase 716", "coherence report", "capsule v4.7", "closure gate")
PHASE_BACKFILL_SUBJECT = ("phase 716", "walkthrough", "status", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(CLOSURE_PATH),
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
    raise AssertionError("phase_716_commit_not_present_in_local_history")


def _try_resolve_commit_ref(
    subject_tokens: tuple[str, ...], expected_paths: set[str]
) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_artifacts_have_required_headings_in_order() -> None:
    coherence_text = _read(COHERENCE_PATH)
    capsule_text = _read(CAPSULE_PATH)
    closure_text = _read(CLOSURE_PATH)
    coherence_positions = [coherence_text.index(heading) for heading in COHERENCE_REQUIRED_HEADINGS]
    capsule_positions = [capsule_text.index(heading) for heading in CAPSULE_REQUIRED_HEADINGS]
    closure_positions = [closure_text.index(heading) for heading in CLOSURE_REQUIRED_HEADINGS]
    assert coherence_positions == sorted(coherence_positions)
    assert capsule_positions == sorted(capsule_positions)
    assert closure_positions == sorted(closure_positions)


def test_coherence_and_closure_artifacts_contain_required_tokens() -> None:
    coherence_text = _read(COHERENCE_PATH)
    closure_text = _read(CLOSURE_PATH)
    for token in COHERENCE_REQUIRED_TOKENS:
        assert token in coherence_text
    for token in CLOSURE_REQUIRED_TOKENS:
        assert token in closure_text


def test_artifacts_record_window_closure_without_new_ratification_or_results_claims() -> None:
    coherence_text = _read(COHERENCE_PATH)
    closure_text = _read(CLOSURE_PATH)
    assert "No CDL ratification occurred in Window `713-716`" in coherence_text
    assert "commissioned partition-repair evidence and defined the missing-signal" in coherence_text
    assert "no benchmark-result claim was made in-window" in closure_text
    assert "topology shuffling remains unratified here" in closure_text


def test_capsule_supersedes_v46_and_records_live_track_b_line() -> None:
    text = _read(CAPSULE_PATH)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v4.6.md" in text
    assert "Window 713-716 is now closed as the adaptive-gossip and resilience-operationalization lane." in text
    assert "Window 717-722 is the next planned continuation." in text
    assert "Track B status: `M-013 complete; next planned phase TBD`" in text


def test_capsule_and_closure_artifacts_record_explicit_carry_forward() -> None:
    capsule_text = _read(CAPSULE_PATH)
    closure_text = _read(CLOSURE_PATH)
    assert "execution of the commissioned partition-repair evidence pack" in capsule_text
    assert "Window `717-722` as the next main-lane continuation" in closure_text
    assert "node transfer economics" in capsule_text


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


def test_phase_716_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_716_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
