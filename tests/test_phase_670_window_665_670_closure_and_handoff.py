from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF_PATH = ROOT / "docs/specs/ilc_window_665_670_handoff_670_v0.1.md"
CHECKLIST_PATH = ROOT / "docs/specs/ilc_option_b_graduation_checklist_state_670_v0.1.json"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v4.1.md"
GATE_PATH = ROOT / "tools/run_window_665_670_transport_maturity_closure_gate_phase_670.sh"
DECISION_LOG_PATH = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


REQUIRED_HEADINGS = [
    "## 1. Window identity and closure basis",
    "## 2. Inputs and closure inheritance",
    "## 3. Closure verdict summary",
    "## 4. Row-9 maturity basis",
    "## 5. Carry-forward items and residual blockers",
    "## 6. Next-window entry criteria and routing",
    "## 7. MemPalace refresh disposition",
    "## 8. Option-B checklist delta",
]

REQUIRED_TOKENS = [
    "window_665_670_handoff_670_closed",
    "window_665_670_transport_lane_status_pass",
    "row_9_closed_after_670_if_and_only_if_maturity_contract_met_and_gate_passed",
    "row_9_partial_after_670_if_thresholds_not_met_or_evidence_incomplete",
    "rows_5_7_8_remain_open_after_670",
    "cdl_062_still_unopened_after_670",
    "option_d_posture_active_after_670",
    "window_671_676_censorship_and_independence_is_next_planned_lane",
]


def _read_handoff() -> str:
    return HANDOFF_PATH.read_text(encoding="utf-8")


def _load_checklist() -> dict:
    return json.loads(CHECKLIST_PATH.read_text(encoding="utf-8"))


def test_handoff_exists_and_contains_required_headings_in_order() -> None:
    text = _read_handoff()
    positions = []
    for heading in REQUIRED_HEADINGS:
        position = text.find(heading)
        assert position != -1
        positions.append(position)
    assert positions == sorted(positions)


def test_handoff_contains_required_tokens() -> None:
    text = _read_handoff()
    for token in REQUIRED_TOKENS:
        assert token in text


def test_checklist_json_exists_and_records_all_nine_rows() -> None:
    payload = _load_checklist()
    assert CHECKLIST_PATH.exists()
    assert len(payload["rows"]) == 9


def test_checklist_json_preserves_rows_one_through_six_correctly() -> None:
    rows = {row["row"].split(".")[0]: row for row in _load_checklist()["rows"]}
    for row_id in ("1", "2", "3", "4"):
        assert rows[row_id]["status"] == "runtime_closed"
    assert rows["5"]["status"] == "not_started"
    assert rows["6"]["status"] == "closed"


def test_checklist_json_records_row9_as_closed() -> None:
    rows = {row["row"].split(".")[0]: row for row in _load_checklist()["rows"]}
    assert rows["9"]["status"] == "closed"


def test_handoff_and_checklist_agree_on_row9_disposition() -> None:
    handoff = _read_handoff()
    row9 = next(row for row in _load_checklist()["rows"] if row["row"].startswith("9."))
    assert row9["status"] == "closed"
    assert "row 9 is now `closed`" in handoff


def test_rows_five_seven_and_eight_remain_open_in_handoff_and_checklist() -> None:
    handoff = _read_handoff()
    rows = {row["row"].split(".")[0]: row for row in _load_checklist()["rows"]}
    assert rows["5"]["status"] == "not_started"
    assert rows["7"]["status"] == "partial"
    assert rows["8"]["status"] == "partial"
    assert "rows 5, 7, and 8 remain open" in handoff


def test_capsule_v41_exists_and_records_row9_closure_plus_next_lane() -> None:
    text = CAPSULE_PATH.read_text(encoding="utf-8")
    assert "Window 665-670 is now closed as the row-9 transport maturity lane." in text
    assert "row 9 is now `closed`" in text
    assert "Window 671-676 for censorship-resistance and" in text


def test_closure_gate_script_exists_is_executable_and_has_no_recursion() -> None:
    assert GATE_PATH.exists()
    mode = os.stat(GATE_PATH).st_mode
    assert mode & stat.S_IXUSR
    text = GATE_PATH.read_text(encoding="utf-8")
    assert "test_phase_665_window_665_670_sequence_lock.py" in text
    assert "test_phase_670_window_665_670_closure_and_handoff.py" in text
    assert "run_window_665_670_transport_maturity_closure_gate_phase_670.sh" not in text.strip().splitlines()[-1]


def test_decision_log_remains_unchanged_in_this_phase() -> None:
    subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH.relative_to(ROOT))],
        cwd=ROOT,
        check=True,
    )
