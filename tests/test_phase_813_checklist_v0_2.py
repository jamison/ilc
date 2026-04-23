from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = REPO_ROOT / "docs/specs/ilc_option_b_graduation_checklist_state_813_v0.2.json"


def _load() -> dict:
    return json.loads(CHECKLIST.read_text(encoding="utf-8"))


def _row(data: dict, number: str) -> dict:
    return next(item for item in data["rows"] if item["row"].startswith(number))


def test_row5_status_is_parallel_obligation_acknowledged() -> None:
    data = _load()
    assert _row(data, "5.")["status"] == "parallel_obligation_acknowledged"


def test_row5_marks_pre_public_rc_obligation() -> None:
    data = _load()
    assert _row(data, "5.")["pre_public_rc_obligation"] is True


def test_row7_uses_runtime_closed_with_cw4_source() -> None:
    data = _load()
    row7 = _row(data, "7.")
    assert row7["status"] == "runtime_closed"
    assert row7["source_ref"] == "docs/specs/ilc_row_7_exitability_closure_evaluation_cw4_v0.1.md"


def test_row8_uses_phase809_pass_source() -> None:
    data = _load()
    row8 = _row(data, "8.")
    assert row8["status"] == "pass"
    assert row8["source_ref"] == "docs/phases/phase_809_option_b_gate_post805_resynthesis.md"


def test_option_b_selected_remains_false_in_v02() -> None:
    data = _load()
    assert data["option_b_selected"] is False
