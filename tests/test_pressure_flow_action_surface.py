from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from simulations.sim_pressure_flow_action_surface import (
    ACTION_SURFACE_RESEARCH_TOKEN,
    MODEL_VERSION,
    NO_INVERTED_ECU_ACTIVATION_TOKEN,
    NO_RUNTIME_ACTIVATION_TOKEN,
    SIMULATION_ID,
    export_action_surface_json,
    run_action_surface_suite,
)


MODULE_PATH = Path("simulations/sim_pressure_flow_action_surface.py")


def _results_by_key() -> dict[tuple[str, bool], object]:
    return {
        (result.action_id, result.guardrails_enabled): result
        for result in run_action_surface_suite()
    }


def test_protocol_burn_has_no_same_cluster_capture_surface() -> None:
    results = _results_by_key()
    burn = results[("protocol_burn_or_decay", False)]
    guarded_burn = results[("protocol_burn_or_decay", True)]

    assert burn.immediate_ring_capture_ecu == Decimal("0.000000")
    assert guarded_burn.immediate_ring_capture_ecu == Decimal("0.000000")
    assert burn.risk_band == "low"
    assert guarded_burn.risk_band == "low"


def test_jury_review_randomization_is_lower_risk_than_self_directed_credit() -> None:
    results = _results_by_key()
    jury = results[("jury_or_review_panel_payment", True)]
    cwea = results[("cwea_productive_credit_warrant", True)]
    open_market = results[("open_market_maintenance_payment", True)]

    assert jury.receiver_selection == "vrf_or_panel_assignment"
    assert jury.ring_capture_index < cwea.ring_capture_index
    assert jury.ring_capture_index < open_market.ring_capture_index
    assert jury.risk_band == "low"


def test_action_guardrails_reduce_high_risk_self_directed_surfaces() -> None:
    results = _results_by_key()

    for action_id in (
        "storage_retrieval_service_payment",
        "open_market_maintenance_payment",
        "cwea_productive_credit_warrant",
        "bootstrap_inviter_reward",
    ):
        uncontrolled = results[(action_id, False)]
        guarded = results[(action_id, True)]
        assert uncontrolled.risk_band == "high"
        assert guarded.ring_capture_index < uncontrolled.ring_capture_index
        assert guarded.immediate_ring_capture_ecu < uncontrolled.immediate_ring_capture_ecu
        assert guarded.clawback_liability_ecu > uncontrolled.clawback_liability_ecu


def test_maintenance_lottery_needs_vrf_pool_controls_to_be_low_risk() -> None:
    results = _results_by_key()
    uncontrolled = results[("maintenance_lottery_or_vrf_pool", False)]
    guarded = results[("maintenance_lottery_or_vrf_pool", True)]

    assert uncontrolled.risk_band == "high"
    assert guarded.risk_band == "low"
    assert guarded.receiver_selection == "vrf_pool_draw"
    assert guarded.immediate_ring_capture_ecu < uncontrolled.immediate_ring_capture_ecu


def test_action_surface_export_is_canonical_and_non_authorizing() -> None:
    exported = export_action_surface_json(run_action_surface_suite())
    parsed = json.loads(exported)

    assert exported == json.dumps(
        parsed,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    assert parsed["simulation_id"] == SIMULATION_ID
    assert parsed["model_version"] == MODEL_VERSION
    assert parsed["tokens"] == [
        ACTION_SURFACE_RESEARCH_TOKEN,
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


def test_action_surface_module_is_public_rc_excluded_and_not_runtime_policy() -> None:
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
