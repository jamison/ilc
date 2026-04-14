from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest


CHECKLIST_JSON_PATH = Path("docs/specs/ilc_option_b_graduation_checklist_state_664_v0.1.json")
GATE_SCRIPT_PATH = Path("tools/run_window_659_664_constitutional_closure_gate_phase_664.sh")
TEST_PATH = Path("tests/test_phase_664_window_659_664_closure_and_handoff.py")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v4.0.md")
HANDOFF_PATH = Path("docs/specs/ilc_window_659_664_handoff_664_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_664_g8_window_659_664_closure_and_handoff_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_664_SUBJECT_TOKENS = ("phase 664", "window 659-664 closure and handoff")
PHASE_664_BACKFILL_SUBJECT_TOKENS = ("phase 664", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(CHECKLIST_JSON_PATH),
    str(GATE_SCRIPT_PATH),
    str(TEST_PATH),
    str(CAPSULE_PATH),
    str(HANDOFF_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HANDOFF_HEADINGS = (
    "## 1. Window identity and closure basis",
    "## 2. Inputs and closure inheritance",
    "## 3. Closure verdict summary",
    "## 4. Carry-forward items and residual blockers",
    "## 5. Next-window entry criteria and routing",
    "## 6. MemPalace refresh disposition",
    "## 7. Option-B checklist delta",
)
REQUIRED_HANDOFF_TOKENS = (
    "window_659_664_handoff_664_closed",
    "window_659_664_constitutional_lane_status_pass",
    "row_6_closed_after_664_if_and_only_if_cdl_065_ratified_and_gate_passed",
    "rows_5_and_7_through_9_remain_open_after_664",
    "cdl_062_still_unopened_after_664",
    "option_d_posture_active_after_664",
    "window_665_670_transport_and_discovery_maturity_is_next_planned_lane",
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


def _subject_matches(subject: str, tokens: tuple[str, ...]) -> bool:
    lowered = subject.lower()
    return all(token in lowered for token in tokens)


def _find_commit_ref(*, subject_tokens: tuple[str, ...]) -> str | None:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if _subject_matches(subject, subject_tokens):
            return commit_hash
    return None


def _resolve_commit_ref(*, subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
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
        if _subject_matches(subject, subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_tokens}")


def _require_commit_or_skip(subject_tokens: tuple[str, ...]) -> None:
    if _find_commit_ref(subject_tokens=subject_tokens) is None:
        pytest.skip(f"commit_not_yet_present:{subject_tokens}")


def test_handoff_exists_and_contains_all_required_headings_in_schema_order() -> None:
    text = _read(HANDOFF_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HANDOFF_HEADINGS]
    assert positions == sorted(positions)


def test_handoff_contains_all_required_tokens() -> None:
    text = _read(HANDOFF_PATH)
    for token in REQUIRED_HANDOFF_TOKENS:
        assert token in text


def test_checklist_state_json_exists_and_records_all_nine_rows() -> None:
    payload = json.loads(CHECKLIST_JSON_PATH.read_text(encoding="utf-8"))
    assert payload["artifact"] == "ilc_option_b_graduation_checklist_state_664_v0.1"
    assert payload["window"] == "659-664"
    assert payload["option_b_selected"] is False
    assert payload["option_d_active"] is True
    assert len(payload["rows"]) == 9


def test_checklist_state_json_records_row_6_as_closed() -> None:
    payload = json.loads(CHECKLIST_JSON_PATH.read_text(encoding="utf-8"))
    statuses = {row["row"]: row["status"] for row in payload["rows"]}
    assert statuses["6. coupling invariants that keep protocol truth and graph legitimacy upstream of settlement backend choice"] == "closed"


def test_checklist_state_json_preserves_row_5_as_not_started() -> None:
    payload = json.loads(CHECKLIST_JSON_PATH.read_text(encoding="utf-8"))
    statuses = {row["row"]: row["status"] for row in payload["rows"]}
    assert statuses["5. privacy-preserving public legitimacy mechanism at the settlement layer"] == "not_started"


def test_checklist_state_json_preserves_rows_7_through_9_as_open_states() -> None:
    payload = json.loads(CHECKLIST_JSON_PATH.read_text(encoding="utf-8"))
    statuses = {row["row"]: row["status"] for row in payload["rows"]}
    assert statuses["7. censorship-resistance requirement for public legitimacy surfaces"] == "partial"
    assert statuses["8. independence from external constitutional centers as a future-substrate selection criterion"] == "partial"
    assert statuses["9. transport and discovery operational maturity threshold for public participant use"] == "partial"


def test_capsule_v4_exists_and_records_row_6_closure_plus_honest_carry_forward() -> None:
    text = _read(CAPSULE_PATH)
    assert "ILC Antigravity Context Capsule v4.0" in text
    assert "Window 659-664 is now closed as the row-6 coupling-invariants governance-lock" in text
    assert "row 6 is now `closed`" in text
    assert "rows 7-9 remain open" in text
    assert "`CDL-062` remains unopened" in text


def test_closure_gate_script_exists_is_executable_and_wires_phases_659_through_664_without_recursion() -> None:
    script_text = _read(GATE_SCRIPT_PATH)
    assert GATE_SCRIPT_PATH.is_file()
    assert os.access(GATE_SCRIPT_PATH, os.X_OK)
    assert "tests/test_phase_659_window_659_664_sequence_lock.py" in script_text
    assert "tests/test_phase_660_coupling_surface_inventory_and_invariant_matrix.py" in script_text
    assert "tests/test_phase_661_coupling_counterexample_and_row_sharpening.py" in script_text
    assert "tests/test_phase_662_cdl_065_opening_and_admissibility_matrix.py" in script_text
    assert "tests/test_phase_663_cdl_065_ratification_and_row6_closure_candidate.py" in script_text
    assert "tests/test_phase_664_window_659_664_closure_and_handoff.py" in script_text
    assert "run_window_659_664_constitutional_closure_gate_phase_664.sh" not in script_text


def test_decision_log_remains_unchanged_in_phase_664() -> None:
    result = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_phase_664_main_and_backfill_commit_path_sets_obey_phase_scope() -> None:
    _require_commit_or_skip(PHASE_664_SUBJECT_TOKENS)
    main_commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_664_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(main_commit_ref) == EXACT_REQUIRED_MAIN_PATHS
    if _find_commit_ref(subject_tokens=PHASE_664_BACKFILL_SUBJECT_TOKENS) is None:
        pytest.skip(f"commit_not_yet_present:{PHASE_664_BACKFILL_SUBJECT_TOKENS}")
    backfill_commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_664_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(backfill_commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
