from __future__ import annotations

import subprocess
from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_coherence_report_712_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v4.6.md")
CLOSURE_GATE_PATH = Path("docs/specs/ilc_window_707_712_closure_gate_712_v0.1.md")
TEST_PATH = Path(
    "tests/test_phase_712_coherence_report_capsule_v4_6_and_window_707_712_closure_gate.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_712_g8_coherence_report_capsule_v4_6_and_window_707_712_closure_gate_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

COHERENCE_HEADINGS = (
    "## 1. Window 707-712 summary",
    "## 2. Ratification and non-ratification state",
    "## 3. Validator-agent and topology-prelock outcomes",
    "## 4. Carry-forward into 713-716 and convergence",
    "## 5. Final coherence statement",
)
COHERENCE_TOKENS = (
    "window_707_712_coherence_report_complete",
    "cdl_066_ratified_in_window_707_712",
    "cdl_067_ratified_in_window_707_712",
    "cdl_017_remains_open_unratified_after_window_707_712",
    "validator_agent_prelock_and_sim_commissioning_complete",
    "window_713_716_and_convergence_carry_forward_explicit",
)
CLOSURE_HEADINGS = (
    "## 1. Window identity and closure basis",
    "## 2. Mandatory checklist confirmation",
    "## 3. Ratification state and preserved non-ratifications",
    "## 4. Track B frontier verification",
    "## 5. Carry-forward routing",
    "## 6. Closure statement",
)
CLOSURE_TOKENS = (
    "window_707_712_closure_gate_712_complete",
    "phase_707_711_outputs_confirmed",
    "cdl_066_and_cdl_067_ratifications_confirmed",
    "cdl_017_prelock_complete_but_still_open",
    "window_713_716_and_convergence_routing_confirmed",
)
PHASE_MAIN_SUBJECT = ("phase 712", "coherence report capsule v4.6 and closure gate")
PHASE_BACKFILL_SUBJECT = ("phase 712", "walkthrough", "backfill")
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
    raise AssertionError("phase_712_commit_not_present_in_local_history")


def test_coherence_report_contains_required_structure_and_tokens() -> None:
    text = _read(COHERENCE_PATH)
    positions = [text.index(heading) for heading in COHERENCE_HEADINGS]
    assert positions == sorted(positions)
    for token in COHERENCE_TOKENS:
        assert token in text


def test_coherence_report_records_window_results_and_carry_forward() -> None:
    text = _read(COHERENCE_PATH)
    assert "`CDL-066` as the narrow sender-authorization constitutional lane" in text
    assert "`CDL-067` as the narrow settlement-state governance vehicle" in text
    assert "`CDL-017`" in text and "only mature enough for prelock evidence and commissioning" in text
    assert "Window `713-716` takes the next main-lane step as adaptive gossip and resilience operationalization" in text
    assert "rows `5` and `7` remain `spec_closed_runtime_pending`" in text


def test_capsule_v46_contains_required_frontier_lines_and_live_track_b_state() -> None:
    text = _read(CAPSULE_PATH)
    assert "Capsule v4.6 supersedes v4.5." in text
    assert "Window 707-712 is now closed as the governance-minimization and validator-agent prelock lane." in text
    assert "Window 713-716 is the next planned continuation." in text
    assert "`CDL-066` is now `ratified`" in text
    assert "`CDL-067` is now `ratified`" in text
    assert "`CDL-017` remains `open` and unratified" in text
    assert "Track B status: `M-011 binary_complete; M-012 next planned; real 4-validator run still pending provisioning`" in text


def test_closure_gate_contains_required_structure_and_tokens() -> None:
    text = _read(CLOSURE_GATE_PATH)
    positions = [text.index(heading) for heading in CLOSURE_HEADINGS]
    assert positions == sorted(positions)
    for token in CLOSURE_TOKENS:
        assert token in text


def test_closure_gate_confirms_checklist_track_b_and_carry_forward() -> None:
    text = _read(CLOSURE_GATE_PATH)
    assert "Phase `707` sequence lock published" in text
    assert "Phase `708` `CDL-066` ratification evidence published" in text
    assert "Phase `709` `CDL-067` ratification evidence published" in text
    assert "Phase `710` validator-agent design evidence published" in text
    assert "Phase `711` `CDL-039` scope note published" in text
    assert "real 4-validator run still pending provisioning" in text
    assert "Window `713-716` adaptive gossip and resilience operationalization" in text


def test_decision_log_states_match_window_close_claims() -> None:
    log_text = _read(DECISION_LOG_PATH)
    cdl_066_line = next(line for line in log_text.splitlines() if line.startswith("| CDL-066 |"))
    cdl_067_line = next(line for line in log_text.splitlines() if line.startswith("| CDL-067 |"))
    cdl_017_line = next(line for line in log_text.splitlines() if line.startswith("| CDL-017 |"))
    assert "| ratified |" in cdl_066_line
    assert "| ratified |" in cdl_067_line
    assert "| open |" in cdl_017_line


def test_phase_712_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_712_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
