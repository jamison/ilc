from __future__ import annotations

import json
from pathlib import Path


SPEC_PATH = Path("docs/specs/ilc_werner_flow_governor_overlay_validation_1262_v0.1.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1262_werner_flow_governor_overlay_validation_walkthrough.md"
)
FORWARD_PLAN_PATH = Path(
    "docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md"
)
FIX8_JSON_PATH = Path(
    "docs/sims/sim_fetch_01/sim_fetch_01_werner_overlay_results_1238h_v0.1.json"
)
FIX9_JSON_PATH = Path(
    "docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_evidence_matrix_1238i_v0.1.json"
)
FIX10_JSON_PATH = Path(
    "docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_robustness_suite_1238j_v0.1.json"
)
HARNESS_PATH = Path("ilc_core/sim/sim_fetch_01/sim_fetch_01_harness.py")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


REQUIRED_TOKENS = (
    "werner_flow_governor_overlay_validation_phase_1262.v0.1",
    "werner_overlay_promote_or_retire_verdict_recorded_phase_1262",
    "heat_signal_must_not_directly_mint_ecu_phase_1262",
    "no_werner_ecu_minting_or_ilc_settlement_phase_1262",
)

FORWARD_PLAN_TOKENS = (
    "flow_governor_cdl_required_before_runtime_policy_deployment",
    "flow_governor_spectral_trust_threshold_required_before_policy_use",
    "heat_signal_must_not_directly_mint_ecu",
    "werner_overlay_opt_in_must_be_promoted_or_retired_after_validation",
    "werner_default_topology_pressure_profile_required_before_runtime_cdl",
    "werner_heat_prefers_reputation_routing_admission_before_ecu_creation",
)


def _spec_text() -> str:
    return SPEC_PATH.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase_1262_spec_records_required_tokens_and_promotion_verdict() -> None:
    text = _spec_text()

    for token in REQUIRED_TOKENS:
        assert token in text

    assert (
        "werner_overlay_verdict_phase_1262=promote_to_default_sim_fetch_topology_pressure_profile_after_followup"
        in text
    )
    assert "topology_pressure_model=werner_v1" in text
    assert "does not change runtime economic policy" in text
    assert "does not change SIM-FETCH default behavior in code" in text


def test_forward_plan_supports_promotion_but_blocks_runtime_policy_and_direct_mint() -> None:
    spec = _spec_text()
    forward_plan = FORWARD_PLAN_PATH.read_text(encoding="utf-8")

    for token in FORWARD_PLAN_TOKENS:
        assert token in spec
        assert token in forward_plan

    assert "The Werner Flow Governor is NOT a rate limiter" in forward_plan
    assert "heat must not directly create ECU" in forward_plan
    assert "simulation overlay" in forward_plan
    assert "not as runtime policy" in forward_plan


def test_fix8_overlay_artifact_is_non_authorizing_and_emits_recommendations() -> None:
    artifact = _json(FIX8_JSON_PATH)
    metrics = artifact["aggregate_over_epochs"]

    assert metrics["werner_overlay_enabled"] is True
    assert metrics["werner_overlay_mode"] == "sim_fetch_topology_pressure_only"
    assert metrics["werner_ecu_pressure_mint_authorized"] is False
    assert metrics["werner_ilc_settlement_authorized"] is False
    assert "does not mint ECU, settle ILC" in metrics["werner_authorization_note"]
    assert metrics["werner_topology_recommendation_by_tier"]["B"] == "expand_capacity"
    assert metrics["werner_topology_recommendation_by_tier"]["C"] == "cool_capacity"


def test_fix9_matrix_keeps_every_werner_row_non_authorizing() -> None:
    artifact = _json(FIX9_JSON_PATH)

    assert artifact["scenario_count"] == 48
    assert artifact["verdict_counts"] == {"fail": 8, "needs_review": 2, "pass": 38}
    assert "does not ratify CDL-087, mint ECU, settle ILC" in artifact[
        "non_authorization_note"
    ]

    rows = artifact["rows"]
    assert any(row["params"]["werner_overlay_enabled"] is True for row in rows)
    for row in rows:
        metrics = row["key_metrics"]
        assert metrics["werner_ecu_pressure_mint_authorized"] is False
        assert metrics["werner_ilc_settlement_authorized"] is False


def test_fix10_robustness_suite_preserves_non_minting_boundary() -> None:
    artifact = _json(FIX10_JSON_PATH)

    assert artifact["overall_robustness_verdict"] == "pass"
    assert artifact["accepted_profile_count"] == 4
    assert "does not ratify CDL-087, mint ECU, settle ILC" in artifact[
        "non_authorization_note"
    ]
    for profile in artifact["profiles"]:
        assert profile["accepted"] is True
        for scenario in profile["representative_scenarios"]:
            metrics = scenario["key_metrics"]
            assert metrics["werner_ecu_pressure_mint_authorized"] is False
            assert metrics["werner_ilc_settlement_authorized"] is False


def test_harness_keeps_werner_overlay_simulation_only() -> None:
    harness = HARNESS_PATH.read_text(encoding="utf-8")

    assert "sim_fetch_topology_pressure_only" in harness
    assert "simulation-only" in harness
    assert "not an ECU mint, ILC settlement, or CDL-087 ratification" in harness
    assert '"werner_ecu_pressure_mint_authorized": False' in harness
    assert '"werner_ilc_settlement_authorized": False' in harness


def test_phase_1262_status_planning_walkthrough_and_cdl_register_boundary() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    planning = PLANNING_INDEX_PATH.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH_PATH.read_text(encoding="utf-8")
    cdl_register = CDL_REGISTER_PATH.read_text(encoding="utf-8")

    for text in (status, planning, walkthrough):
        for token in REQUIRED_TOKENS:
            assert token in text

    assert "Phase 1263" in status
    assert "SENSITIVE" in status
    assert "Phase 1263" in planning
    assert "| CDL-087 |" in cdl_register
    assert "| ratified |" in cdl_register
    assert "ratified_phase: 1278 Fix1" in cdl_register
