from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from simulations.sim_pressure_flow_remaining_strike_force_suite import (
    MODEL_VERSION,
    NO_INVERTED_ECU_ACTIVATION_TOKEN,
    NO_RUNTIME_ACTIVATION_TOKEN,
    SUITE_TOKEN,
    export_remaining_strike_force_json,
    run_remaining_strike_force_suite,
)


MODULE_PATH = Path("simulations/sim_pressure_flow_remaining_strike_force_suite.py")


def _results_by_sim():
    return {
        result.sim_id: result
        for result in run_remaining_strike_force_suite()
    }


def _case(result, case_id: str):
    for case in result.cases:
        if case.case_id == case_id:
            return case
    raise AssertionError(f"missing case {case_id}")


def test_remaining_suite_shape_and_order() -> None:
    results = run_remaining_strike_force_suite()

    assert [result.sim_id for result in results] == [
        "SIM-PRESSURE-FLOW-03",
        "SIM-CWEA-01",
        "SIM-PRESSURE-SPECTRAL-01",
        "SIM-PRESSURE-JURY-01",
        "SIM-MAINTENANCE-POOL-01",
        "SIM-INVITER-01",
        "SIM-SERVICE-01",
        "SIM-PRESSURE-FLOW-04",
        "SIM-PRESSURE-MARKET-01",
        "SIM-CWEA-02",
    ]
    assert sum(len(result.cases) for result in results) == 23


def test_cycle_detection_reduces_multicluster_capture() -> None:
    result = _results_by_sim()["SIM-PRESSURE-FLOW-03"]
    no_detection = _case(result, "no_cycle_detection")
    guarded = _case(result, "cycle_detection_receiver_liability")

    assert guarded.metrics["net_capture_ecu"] < no_detection.metrics["net_capture_ecu"]
    assert guarded.metrics["receiver_liability_ecu"] > Decimal("0")
    assert guarded.metrics["admission_throttle"] > Decimal("0")


def test_cwea_receiver_liability_and_no_socialized_loss() -> None:
    result = _results_by_sim()["SIM-CWEA-01"]
    failed = _case(result, "failed_warrant")
    ring = _case(result, "ring_warrant")

    assert failed.metrics["socialized_loss_ecu"] == Decimal("0")
    assert ring.metrics["receiver_liability_ecu"] > Decimal("0")
    assert ring.metrics["originator_liability_ecu"] > Decimal("0")


def test_spectral_detector_flags_ring_not_honest_flow() -> None:
    result = _results_by_sim()["SIM-PRESSURE-SPECTRAL-01"]
    honest = _case(result, "honest_distributed_flow")
    ring = _case(result, "collusive_ring_flow")

    assert honest.metrics["flagged"] == Decimal("0")
    assert ring.metrics["flagged"] == Decimal("1")
    assert ring.metrics["fiedler_concentration_proxy"] > honest.metrics["fiedler_concentration_proxy"]


def test_jury_is_safest_diagnostic_surface_and_maintenance_needs_vrf() -> None:
    results = _results_by_sim()
    jury = _case(results["SIM-PRESSURE-JURY-01"], "vrf_cluster_diverse_review")
    maintenance_open = _case(results["SIM-MAINTENANCE-POOL-01"], "capturable_eligibility")
    maintenance_vrf = _case(results["SIM-MAINTENANCE-POOL-01"], "vrf_pool_draw")

    assert jury.metrics["same_cluster_farming_risk"] < Decimal("0.01")
    assert maintenance_vrf.metrics["capture_share"] < maintenance_open.metrics["capture_share"]
    assert maintenance_vrf.metrics["vrf_entropy"] > maintenance_open.metrics["vrf_entropy"]


def test_inviter_service_delay_market_and_cwea_frontier_findings() -> None:
    results = _results_by_sim()
    inviter_immediate = _case(results["SIM-INVITER-01"], "immediate_reward")
    inviter_delayed = _case(results["SIM-INVITER-01"], "delayed_survival_liability")
    service_receipt = _case(results["SIM-SERVICE-01"], "receipt_only")
    service_proof = _case(results["SIM-SERVICE-01"], "proof_of_service_receiver_diversity")
    short_delay = _case(results["SIM-PRESSURE-FLOW-04"], "short_delay")
    medium_delay = _case(results["SIM-PRESSURE-FLOW-04"], "medium_delay")
    market_moderate = _case(results["SIM-PRESSURE-MARKET-01"], "moderate_clawback_pressure")
    market_severe = _case(results["SIM-PRESSURE-MARKET-01"], "severe_clawback_pressure")
    cwea_balanced = _case(results["SIM-CWEA-02"], "balanced_controls")
    cwea_heavy = _case(results["SIM-CWEA-02"], "heavy_controls")

    assert inviter_delayed.metrics["sybil_profit_ecu"] < inviter_immediate.metrics["sybil_profit_ecu"]
    assert service_proof.metrics["self_dealing_capture_ecu"] < service_receipt.metrics["self_dealing_capture_ecu"]
    assert medium_delay.metrics["false_settlement_rate"] < short_delay.metrics["false_settlement_rate"]
    assert market_moderate.metrics["quality_index"] > market_severe.metrics["quality_index"]
    assert cwea_balanced.metrics["utility_index"] > cwea_heavy.metrics["utility_index"]
    assert cwea_heavy.metrics["safety_index"] > cwea_balanced.metrics["safety_index"]


def test_remaining_suite_export_is_canonical_and_non_authorizing() -> None:
    results = run_remaining_strike_force_suite()
    exported = export_remaining_strike_force_json(results)
    parsed = json.loads(exported)

    assert exported == json.dumps(
        parsed,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    assert parsed["model_version"] == MODEL_VERSION
    assert parsed["simulation_count"] == 10
    assert parsed["case_count"] == 23
    assert parsed["tokens"] == [
        SUITE_TOKEN,
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


def test_remaining_suite_module_is_public_rc_excluded_and_not_runtime_policy() -> None:
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
