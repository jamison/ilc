import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "docs/specs/ilc_cdl096_eligibility_checkpoint_1509p_v0.1.json"
REPORT = ROOT / "docs/specs/ilc_cdl096_eligibility_checkpoint_1509p_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1509p_g9_cdl096_eligibility_checkpoint.md"
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1509p_cdl096_eligibility_checkpoint_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
AGENTS = ROOT / "AGENTS.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"

TOKENS = [
    "obl_038_cdl_096_eligibility_checkpoint_complete_phase_1509p",
    "cdl_096_eligible_to_open_phase_1509p",
    "werner_conditions_1_and_4_jointly_covered_phase_1509p",
    "no_cdl_096_opening_phase_1509p",
    "no_werner_flow_governor_activation_phase_1509p",
]


def _row_for(obligation_id: str) -> str:
    for line in REGISTER.read_text().splitlines():
        if line.startswith(f"| {obligation_id} |"):
            return line
    raise AssertionError(f"missing row {obligation_id}")


def test_checkpoint_json_is_canonical_and_records_eligibility_without_opening() -> None:
    body = CHECKPOINT.read_text().strip()
    payload = json.loads(body)

    assert json.dumps(payload, sort_keys=True, allow_nan=False, separators=(",", ":")) == body
    assert payload["eligible_to_open"] is True
    assert payload["cdl_096_opened"] is False
    assert payload["next_route"] == "later_sensitive_cdl096_opening_phase_required"
    assert payload["tokens"] == TOKENS
    assert {condition["condition"]: condition["covered"] for condition in payload["conditions"]} == {
        "condition_1_sim_fetch_topology_pressure": True,
        "condition_4_transport_principal_admission_binding": True,
    }
    assert set(payload["non_authorization"].values()) == {False}


def test_docs_and_frontier_record_tokens_and_no_cdl096_opening() -> None:
    texts = {
        "checkpoint": CHECKPOINT.read_text(),
        "report": REPORT.read_text(),
        "prompt": PROMPT.read_text(),
        "register": REGISTER.read_text(),
        "sequence_lock": SEQUENCE_LOCK.read_text(),
        "walkthrough": WALKTHROUGH.read_text(),
        "status": STATUS.read_text(),
        "planning_index": PLANNING_INDEX.read_text(),
        "agents": AGENTS.read_text(),
    }
    for token in TOKENS:
        for text in texts.values():
            assert token in text

    assert texts["planning_index"].count("⬅ CURRENT") == 1
    assert "Phase 1510p" in texts["status"]
    assert "no_cdl_096_opening_phase_1509p" in texts["report"]


def test_obligation_register_closes_werner_data_track_and_leaves_no_cdl_mutation() -> None:
    assert "| closed |" in _row_for("OBL-004")
    assert "| closed |" in _row_for("OBL-035")
    assert "| closed |" in _row_for("OBL-036")
    assert "| closed |" in _row_for("OBL-037")
    assert "| closed |" in _row_for("OBL-038")

    cdl_register = CDL_REGISTER.read_text()
    assert "| CDL-095 |" in cdl_register
    assert "| CDL-096 |" not in cdl_register
    assert "cdl_096_eligible_to_open_phase_1509p" not in cdl_register
