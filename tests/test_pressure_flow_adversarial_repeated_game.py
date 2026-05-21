from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from simulations.sim_pressure_flow_adversarial_repeated_game import (
    ADVERSARIAL_REPEATED_GAME_RESEARCH_TOKEN,
    MODEL_VERSION,
    NO_INVERTED_ECU_ACTIVATION_TOKEN,
    NO_RUNTIME_ACTIVATION_TOKEN,
    SIMULATION_ID,
    export_repeated_game_json,
    run_repeated_game_suite,
)


MODULE_PATH = Path("simulations/sim_pressure_flow_adversarial_repeated_game.py")


def _results_by_key():
    return {
        (result.action_id, result.policy_id, result.strategy_id): result
        for result in run_repeated_game_suite()
    }


def test_repeated_game_suite_shape_is_deterministic() -> None:
    results = run_repeated_game_suite()

    assert len(results) == 45
    assert {result.action_id for result in results} == {
        "jury_or_review_panel_payment",
        "maintenance_lottery_or_vrf_pool",
        "open_market_maintenance_payment",
        "cwea_productive_credit_warrant",
        "bootstrap_inviter_reward",
    }
    assert {result.policy_id for result in results} == {
        "light_controls",
        "strict_delay_discount",
        "strict_delay_discount_liability",
    }
    assert {result.strategy_id for result in results} == {
        "honest_reference",
        "static_ring",
        "adaptive_ring",
    }


def test_strict_liability_reduces_adaptive_ring_attempt_share_for_high_risk_actions() -> None:
    results = _results_by_key()

    for action_id in (
        "open_market_maintenance_payment",
        "cwea_productive_credit_warrant",
        "bootstrap_inviter_reward",
    ):
        light = results[(action_id, "light_controls", "adaptive_ring")]
        strict_liability = results[(action_id, "strict_delay_discount_liability", "adaptive_ring")]
        assert strict_liability.ring_attempt_share < light.ring_attempt_share
        assert strict_liability.cumulative_net_extraction_ecu <= Decimal("0")


def test_static_ring_is_economically_negative_under_all_policies() -> None:
    for result in run_repeated_game_suite():
        if result.strategy_id == "static_ring":
            assert result.cumulative_net_extraction_ecu <= Decimal("0")
            assert result.final_capacity_ecu == Decimal("25.000000")


def test_jury_review_ring_capture_remains_lower_than_productive_credit_ring_capture() -> None:
    results = _results_by_key()
    jury = results[("jury_or_review_panel_payment", "strict_delay_discount_liability", "adaptive_ring")]
    cwea = results[("cwea_productive_credit_warrant", "strict_delay_discount_liability", "adaptive_ring")]

    assert abs(jury.cumulative_net_extraction_ecu) < abs(cwea.cumulative_net_extraction_ecu)
    assert jury.final_capacity_ecu > cwea.final_capacity_ecu


def test_repeated_game_export_is_canonical_and_non_authorizing() -> None:
    results = run_repeated_game_suite()
    exported = export_repeated_game_json(results)
    parsed = json.loads(exported)

    assert exported == json.dumps(
        parsed,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    assert parsed["simulation_id"] == SIMULATION_ID
    assert parsed["model_version"] == MODEL_VERSION
    assert parsed["epochs_per_case"] == 24
    assert parsed["row_count"] == 45
    assert parsed["tokens"] == [
        ADVERSARIAL_REPEATED_GAME_RESEARCH_TOKEN,
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


def test_repeated_game_module_is_public_rc_excluded_and_not_runtime_policy() -> None:
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
