from __future__ import annotations

import json
from pathlib import Path

from ilc_core.sim.phase_1511p_economic_parameter_sims import (
    NO_BOUNTY_PAYOUT_ACTIVATION_TOKEN,
    NO_COOLING_PERIOD_RUNTIME_CHANGE_TOKEN,
    NO_FEE_BURN_CHANGE_TOKEN,
    NO_SETTLEMENT_MINTING_WALLET_TREASURY_WRITES_TOKEN,
    NO_TRANSFER_TAX_RUNTIME_CHANGE_TOKEN,
    NO_TREASURY_FLOW_ACTIVATION_TOKEN,
    OBL_017_BOUNTY_MECHANISM_SIM_TOKEN,
    OBL_018_TRANSFER_TAX_SIM_TOKEN,
    OBL_019_COOLING_PERIOD_SIM_TOKEN,
    SIM_011_BOUNTY_LABEL_COLLISION_DISAMBIGUATED_TOKEN,
    build_bounty_mechanism_sim_result,
    build_transfer_tax_and_cooling_sim_result,
    export_phase_1511p_json,
)


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1511p_g9_sim_batch_bounty_transfer_tax_cooling.md"
BOUNTY_JSON = ROOT / "docs/sims/ilc_cdl047_bounty_mechanism_sim_1511p_v0.1.json"
BOUNTY_MD = ROOT / "docs/sims/ilc_cdl047_bounty_mechanism_sim_1511p_v0.1.md"
TRANSFER_COOLING_JSON = ROOT / "docs/sims/ilc_transfer_tax_and_cooling_sim_1511p_v0.1.json"
TRANSFER_COOLING_MD = ROOT / "docs/sims/ilc_transfer_tax_and_cooling_sim_1511p_v0.1.md"
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1511p_sim_batch_bounty_transfer_tax_cooling_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
AGENTS = ROOT / "AGENTS.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
ADR_0015 = ROOT / "docs/adr/ADR_0015_Node_Transfer_Economics.md"
ADR_0016 = ROOT / "docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md"
MODULE = ROOT / "ilc_core/sim/phase_1511p_economic_parameter_sims.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(_read(path))


def _row_for(obligation_id: str) -> str:
    for line in _read(REGISTER).splitlines():
        if line.startswith(f"| {obligation_id} |"):
            return line
    raise AssertionError(f"missing row {obligation_id}")


def _walk_no_float(value: object) -> None:
    assert not isinstance(value, float)
    if isinstance(value, dict):
        for item in value.values():
            _walk_no_float(item)
    elif isinstance(value, list):
        for item in value:
            _walk_no_float(item)


def test_phase_1511p_json_outputs_are_canonical_and_float_free() -> None:
    for path in (BOUNTY_JSON, TRANSFER_COOLING_JSON):
        body = _read(path).strip()
        payload = json.loads(body)
        assert json.dumps(payload, sort_keys=True, allow_nan=False, separators=(",", ":")) == body
        _walk_no_float(payload)

    assert export_phase_1511p_json(build_bounty_mechanism_sim_result()) == _read(
        BOUNTY_JSON
    ).strip()
    assert export_phase_1511p_json(build_transfer_tax_and_cooling_sim_result()) == _read(
        TRANSFER_COOLING_JSON
    ).strip()


def test_bounty_sim_records_cdl047_cdl050_and_label_collision_boundaries() -> None:
    payload = _json(BOUNTY_JSON)
    markdown = _read(BOUNTY_MD)

    assert payload["accepted_candidates"]["bounty_request_band"] == "0.10_to_0.15_of_b_e"
    assert payload["accepted_candidates"]["deadline_epochs"] == 4
    assert payload["parameter_anchors"]["bounty_cap_fraction_of_b_e"] == "0.15"
    assert payload["parameter_anchors"]["burn_floor_fraction"] == "0.05"
    assert payload["non_authorization"]["bounty_payout_activated"] is False
    assert payload["non_authorization"]["treasury_flow_activated"] is False
    assert "CDL-050 is treated as a bounded Treasury ECU-governor compatibility surface" in (
        payload["p_e_interaction_note"]
    )
    assert SIM_011_BOUNTY_LABEL_COLLISION_DISAMBIGUATED_TOKEN in payload["tokens"]
    assert "historical CDL-058 `SIM-011`" in markdown
    assert "This is a calibration recommendation only. It is not payout authority." in markdown


def test_transfer_tax_and_cooling_sim_satisfies_phase_721_replay_contract() -> None:
    payload = _json(TRANSFER_COOLING_JSON)
    markdown = _read(TRANSFER_COOLING_MD)

    assert payload["accepted_candidates"]["transfer_tax_candidate_range"] == "0.05_to_0.08"
    assert payload["accepted_candidates"]["transfer_tax_default_candidate"] == "0.05"
    assert payload["accepted_candidates"]["cooling_period_range_epochs"] == "3_to_4"
    assert payload["accepted_candidates"]["default_cooling_period_candidate_epochs"] == 3
    assert any(row["verdict"] == "pass" for row in payload["transfer_tax_rows"])
    assert any(row["verdict"] == "reject" for row in payload["transfer_tax_rows"])
    assert any(row["verdict"] == "pass" for row in payload["cooling_period_rows"])
    assert any(row["verdict"] == "reject" for row in payload["cooling_period_rows"])
    assert payload["non_authorization"]["transfer_tax_runtime_changed"] is False
    assert payload["non_authorization"]["cooling_period_policy_changed"] is False
    assert "These are calibration recommendations only. They are not runtime policy." in markdown


def test_phase_1511p_tokens_register_and_frontier_are_updated() -> None:
    texts = {
        "prompt": _read(PROMPT),
        "bounty_md": _read(BOUNTY_MD),
        "transfer_md": _read(TRANSFER_COOLING_MD),
        "register": _read(REGISTER),
        "sequence_lock": _read(SEQUENCE_LOCK),
        "walkthrough": _read(WALKTHROUGH),
        "status": _read(STATUS),
        "planning_index": _read(PLANNING_INDEX),
        "agents": _read(AGENTS),
    }
    tokens = [
        OBL_017_BOUNTY_MECHANISM_SIM_TOKEN,
        OBL_018_TRANSFER_TAX_SIM_TOKEN,
        OBL_019_COOLING_PERIOD_SIM_TOKEN,
        SIM_011_BOUNTY_LABEL_COLLISION_DISAMBIGUATED_TOKEN,
        NO_BOUNTY_PAYOUT_ACTIVATION_TOKEN,
        NO_TREASURY_FLOW_ACTIVATION_TOKEN,
        NO_TRANSFER_TAX_RUNTIME_CHANGE_TOKEN,
        NO_COOLING_PERIOD_RUNTIME_CHANGE_TOKEN,
        NO_FEE_BURN_CHANGE_TOKEN,
        NO_SETTLEMENT_MINTING_WALLET_TREASURY_WRITES_TOKEN,
    ]
    for token in tokens:
        assert any(token in text for text in texts.values()), token
        assert token in texts["walkthrough"], token
        assert token in texts["status"], token

    for obligation_id in ("OBL-017", "OBL-018", "OBL-019"):
        row = _row_for(obligation_id)
        assert "| closed |" in row
        assert "1511p" in row

    for obligation_id in ("OBL-012", "OBL-015"):
        assert "| open |" in _row_for(obligation_id)

    assert "Phase 1512p" in texts["status"]
    assert texts["planning_index"].count("⬅ CURRENT") == 1


def test_phase_1511p_preserves_governance_and_non_activation_boundaries() -> None:
    cdl_register = _read(CDL_REGISTER)
    adr_0015 = _read(ADR_0015)
    adr_0016 = _read(ADR_0016)
    module = _read(MODULE)

    assert "| CDL-096 |" not in cdl_register
    assert "| CDL-047 |" in cdl_register
    assert "| CDL-050 |" in cdl_register
    assert "**Status:** Proposed" in adr_0015
    assert "**Status:** Proposed" in adr_0016

    forbidden = [
        "import random",
        "datetime.now",
        "time.time",
        "mint_ecu",
        "settle_ilc",
        "ILC_CDL_MUTATION_AUTHORIZED",
        "RUST_P2P_BRIDGE_NOT_ACTIVATED = False",
    ]
    for phrase in forbidden:
        assert phrase not in module

    assert "json.dumps(" in module
    assert "sort_keys=True" in module
    assert "allow_nan=False" in module
    assert "os.replace" in module
