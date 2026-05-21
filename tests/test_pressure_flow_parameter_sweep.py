from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from simulations.sim_pressure_flow_parameter_sweep import (
    MODEL_VERSION,
    NO_INVERTED_ECU_ACTIVATION_TOKEN,
    NO_RUNTIME_ACTIVATION_TOKEN,
    PARAMETER_SWEEP_RESEARCH_TOKEN,
    SIMULATION_ID,
    export_parameter_sweep_json,
    parameter_grid,
    recommend_by_action,
    run_parameter_sweep,
)


MODULE_PATH = Path("simulations/sim_pressure_flow_parameter_sweep.py")


def _recommendations_by_action():
    rows = run_parameter_sweep()
    return {
        recommendation.action_id: recommendation
        for recommendation in recommend_by_action(rows)
    }


def test_parameter_sweep_grid_size_and_row_count_are_deterministic() -> None:
    rows = run_parameter_sweep()

    assert len(parameter_grid()) == 256
    assert len(rows) == 2048
    assert {row.action_id for row in rows} == {
        "protocol_burn_or_decay",
        "jury_or_review_panel_payment",
        "governance_proposal_or_appeal",
        "maintenance_lottery_or_vrf_pool",
        "storage_retrieval_service_payment",
        "open_market_maintenance_payment",
        "cwea_productive_credit_warrant",
        "bootstrap_inviter_reward",
    }


def test_naturally_low_risk_actions_remain_low_with_light_controls() -> None:
    recommendations = _recommendations_by_action()

    for action_id in (
        "protocol_burn_or_decay",
        "jury_or_review_panel_payment",
        "governance_proposal_or_appeal",
    ):
        recommendation = recommendations[action_id]
        assert recommendation.baseline_risk_band == "low"
        assert recommendation.recommended_risk_band == "low"

    assert recommendations["jury_or_review_panel_payment"].liquidity_retained_index > Decimal("0.89")


def test_high_risk_self_directed_actions_require_heavy_delay_and_discount() -> None:
    recommendations = _recommendations_by_action()

    for action_id in (
        "open_market_maintenance_payment",
        "cwea_productive_credit_warrant",
        "bootstrap_inviter_reward",
    ):
        recommendation = recommendations[action_id]
        assert recommendation.baseline_risk_band == "high"
        assert recommendation.recommended_risk_band == "low"
        assert recommendation.same_cluster_discount == Decimal("0.200000")
        assert recommendation.delayed_settlement_share == Decimal("0.900000")


def test_maintenance_pool_is_risky_without_vrf_like_controls_but_salvageable() -> None:
    recommendations = _recommendations_by_action()
    maintenance = recommendations["maintenance_lottery_or_vrf_pool"]

    assert maintenance.baseline_risk_band == "high"
    assert maintenance.recommended_risk_band == "low"
    assert maintenance.liquidity_retained_index > Decimal("0.94")
    assert maintenance.ring_capture_index < Decimal("0.01")


def test_parameter_sweep_export_is_canonical_and_non_authorizing() -> None:
    rows = run_parameter_sweep()
    exported = export_parameter_sweep_json(rows)
    parsed = json.loads(exported)

    assert exported == json.dumps(
        parsed,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    assert parsed["simulation_id"] == SIMULATION_ID
    assert parsed["model_version"] == MODEL_VERSION
    assert parsed["grid_size"] == 256
    assert parsed["row_count"] == 2048
    assert parsed["tokens"] == [
        PARAMETER_SWEEP_RESEARCH_TOKEN,
        NO_RUNTIME_ACTIVATION_TOKEN,
        NO_INVERTED_ECU_ACTIVATION_TOKEN,
    ]
    assert parsed["authorization"] == {
        "cwea_activation_authorized": False,
        "ecu_mint_authorized": False,
        "ilc_settlement_authorized": False,
        "inverted_ecu_activation_authorized": False,
        "pressure_flow_reputation_authorized": False,
        "public_rc_surface": False,
        "runtime_policy_authorized": False,
    }


def test_parameter_sweep_module_is_public_rc_excluded_and_not_runtime_policy() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "PUBLIC_RC_EXCLUDE: pressure_flow_research_simulation_not_public_rc_surface" in source
    assert "json.dumps(" in source
    assert "sort_keys=True" in source
    assert "allow_nan=False" in source
    for forbidden in (
        "mint_ecu(",
        "settle_ilc(",
        "write_wallet",
        "PRODUCTION",
        "inverted_ecu_activation_authorized\": True",
        "pressure_flow_reputation_authorized\": True",
    ):
        assert forbidden not in source
