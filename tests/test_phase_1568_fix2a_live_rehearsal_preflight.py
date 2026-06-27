from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1568_fix2a_g10_live_rehearsal_preflight.md"
SCENARIO = ROOT / "testbed/scenarios/block6_seven_agent_v1.json"
REPORT_JSON = ROOT / "docs/specs/ilc_phase_1568_fix2a_live_rehearsal_preflight_v0.1.json"
REPORT_MD = ROOT / "docs/specs/ilc_phase_1568_fix2a_live_rehearsal_preflight_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fix2a_status_section() -> str:
    status = STATUS.read_text(encoding="utf-8")
    marker = "### Phase 1568-Fix2a - Live Rehearsal Preflight and Blocker Map"
    start = status.index(marker)
    next_marker = status.find("\n### Phase ", start + len(marker))
    return status[start:] if next_marker == -1 else status[start:next_marker]


def test_fix2a_artifacts_exist_and_do_not_claim_live_rerun() -> None:
    for path in (PROMPT, SCENARIO, REPORT_JSON, REPORT_MD):
        assert path.exists(), path
    prompt = PROMPT.read_text(encoding="utf-8")
    report = REPORT_MD.read_text(encoding="utf-8")
    assert "Do not emit `phase_1568_live_rehearsal_rerun_pass_phase_1568_fix2`" in prompt
    assert "No live rehearsal was run." in report
    assert "phase_1568_live_rehearsal_rerun_pass_phase_1568_fix2" not in _fix2a_status_section()


def test_corrected_scenario_uses_block6_topology_and_exact_quantity_strings() -> None:
    scenario = _json(SCENARIO)
    assert scenario["scenario_id"] == "block6-seven-agent-cycle-v1"
    agents = scenario["agents"]
    assert len(agents) == 7
    assert len({agent["agent_id"] for agent in agents}) == 7
    assert {agent["node_name"] for agent in agents} == {
        "jamisons-imac",
        "ilc-node-2",
        "ilc-node-3",
    }
    assert scenario["outsider_receiver"]["node_name"] == "ilc-node-6"
    assert "ilc-node-1" not in json.dumps(scenario, sort_keys=True)
    assert isinstance(scenario["difficulty_factor"], str)
    assert isinstance(scenario["ecu_estimate"], str)


def test_preflight_report_records_expected_blockers_and_guard_dispositions() -> None:
    report = _json(REPORT_JSON)
    assert report["status"] == "PASS_PREFLIGHT_BLOCKERS_RECORDED"
    blocker_ids = {blocker["id"] for blocker in report["blockers"]}
    assert "fix2a_blocker_001_exact_numeric_task_ingestion" in blocker_ids
    assert "fix2a_blocker_002_initialized_agent_identity_binding" in blocker_ids
    assert "fix2a_blocker_003_d2d_services_not_running" in blocker_ids
    assert "fix2a_blocker_004_prior_lane3_same_agent_balance_checks" in blocker_ids
    assert "fix2a_blocker_005_private_rehearsal_admission_boundary" in blocker_ids

    guards = {entry["guard"]: entry for entry in report["guard_inventory"]}
    assert guards["PRODUCTION_EMISSION_NOT_ACTIVATED"]["live_value"] is True
    assert guards["VALIDATOR_ADMISSION_NOT_ACTIVATED"]["live_value"] is True
    assert guards["TREASURY_DISTRIBUTION_NOT_ACTIVATED"]["live_value"] is True
    assert guards["PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED"]["live_value"] is True
    assert guards["CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS"]["live_value"] == 4
    assert (
        report["public_economics_firewall_disposition"]["disposition"]
        == "preserve_public_firewall_add_private_rehearsal_boundary_before_live_rerun"
    )


def test_status_tokens_record_preflight_without_live_completion() -> None:
    status = _fix2a_status_section()
    required = [
        "phase_1568_fix2a_live_rehearsal_preflight_complete",
        "phase_1568_fix2a_guard_inventory_committed",
        "phase_1568_fix2a_block6_scenario_committed",
        "phase_1568_fix2a_d2d_readiness_recorded",
        "phase_1568_fix2a_public_economics_firewall_disposition_recorded",
        "phase_1568_fix2a_prior_lane3_same_agent_defect_recorded",
        "phase_1568_fix2a_live_rerun_remains_blocked_pending_fix2b",
        "public_path_remains_blocked_phase_1568_fix2a",
    ]
    for token in required:
        assert token in status
    assert "phase_1568_live_rehearsal_rerun_pass_phase_1568_fix2" not in status
