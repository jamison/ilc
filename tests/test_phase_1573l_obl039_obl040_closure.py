from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLOSURE = ROOT / "docs/specs/ilc_obl039_obl040_pre_rc_closure_record_1573l_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
OBL_REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
EVIDENCE = ROOT / "docs/sims/ilc_block6_obl040_rerun006_evidence_1573k_v0.1.json"
ROLLBACK = ROOT / "docs/sims/ilc_block6_obl040_rerun006_rollback_receipt_1573k_v0.1.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_closure_record_exists() -> None:
    assert CLOSURE.exists()


def test_closure_record_contains_required_tokens() -> None:
    text = _read(CLOSURE)
    assert "obl_039_pre_rc_fully_closed_phase_1573l" in text
    assert "obl_040_pre_rc_fully_closed_phase_1573l" in text
    assert "obl_039_obl_040_economic_activation_evidence_committed_phase_1573l" in text


def test_closure_record_preserves_disposable_non_production_boundary() -> None:
    text = _read(CLOSURE)
    assert "disposable namespace" in text
    assert "No production value write occurred" in text
    assert "production value-write path not live" in text
    assert "pre-RC evidence satisfied" in text


def test_status_records_phase_1573l_tokens() -> None:
    text = _read(STATUS)
    for token in (
        "obl_039_pre_rc_fully_closed_phase_1573l",
        "obl_040_pre_rc_fully_closed_phase_1573l",
        "obl_039_obl_040_economic_activation_evidence_committed_phase_1573l",
        "public_path_remains_blocked_phase_1573l",
    ):
        assert token in text


def test_planning_index_records_phase_1573l_complete_and_1573m_next() -> None:
    text = _read(PLANNING)
    assert "Phase 1573l is COMPLETE" in text
    assert "Phase 1573m is NEXT" in text
    assert "obl_039_obl_040_economic_activation_evidence_committed_phase_1573l" in text


def test_obligation_register_rows_are_pre_rc_closed_not_production_live() -> None:
    text = _read(OBL_REGISTER)
    assert "OBL-039" in text
    assert "OBL-040" in text
    assert "closed - pre-RC evidence satisfied; production value path not live" in text
    assert "production value-write path not live" in text


def test_rerun006_evidence_still_exists_and_confirms_replay() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert evidence["four_machine_replay"]["identical"] is True
    assert evidence["genesis_tranche_confirmation"]["amount_ecu"] == "1296000"
    assert (
        evidence["genesis_tranche_confirmation"]["genesis_tranche_treatment"]
        == "applied_by_authorized_value_path"
    )


def test_rollback_receipt_confirms_namespace_wiped_and_seven_steps() -> None:
    receipt = json.loads(ROLLBACK.read_text(encoding="utf-8"))
    assert receipt["namespace_wiped"] is True
    assert receipt["steps_completed"] == [1, 2, 3, 4, 5, 6, 7]
    assert all(step["status"] == "complete" for step in receipt["step_confirmations"])


def test_phase_1574_reference_note_present() -> None:
    text = _read(CLOSURE)
    assert "Phase 1574 publication readiness audit must verify" in text
    assert "production value path" in text
