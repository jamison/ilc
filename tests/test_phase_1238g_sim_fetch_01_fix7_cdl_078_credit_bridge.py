from __future__ import annotations

"""
Phase 1238g — Fix7: CDL-078 serving-peer credit bridge tests.

Verifies:
- Fix7 version token is present
- serve-credit metrics distinguish serving peer from served Graph Node/artifact
- legacy CDL-087 §6 total is preserved
- random-path credits sum by serving peer and tier
- routed-path credits attach to the successful serving holder
- rescued routed serves credit the retry serving peer
- Tier C serves do not receive CDL-078 credit by default
- CDL-087 ratification remains unauthorized
"""

from decimal import Decimal

_TIER_B_SCENARIO: dict = {
    "n_serving_peers": 5,
    "n_epochs": 30,
    "n_agents": 20,
    "tier_a_artifact_count": 1,
    "tier_b_artifact_count": 20,
    "tier_c_artifact_count": 1,
    "tier_a_request_rate": "0.00",
    "tier_b_request_rate": "1.00",
    "tier_c_request_rate": "0.00",
    "cache_capacity_per_peer": 50,
    "max_requests_per_epoch": 1000,
    "seed": 123,
    "zipf_exponent_tier_b": "0.5",
    "directory_staleness_rate": "0",
    "tier_b_exact_holder_count_per_artifact": 3,
}

_STALE_RESCUE_SCENARIO: dict = {
    **_TIER_B_SCENARIO,
    "directory_staleness_rate": "1",
    "max_retry_hops": 2,
}

_TIER_C_SCENARIO: dict = {
    **_TIER_B_SCENARIO,
    "tier_b_request_rate": "0.00",
    "tier_c_request_rate": "1.00",
    "tier_c_peer_inventory_fraction": 10,
}


def test_phase_1238g_fix7_version_token_present() -> None:
    import ilc_core.sim.sim_fetch_01.sim_fetch_01_harness as mod

    assert mod.SIM_FETCH_01_HARNESS_VERSION == "sim_fetch_01_harness_1238g.v0.1"
    assert mod.SIM_FETCH_01_FIX7_VERSION == (
        "sim_fetch_01_fix7_cdl_078_credit_bridge_1238g.v0.1"
    )


def test_phase_1238g_credit_bridge_metrics_present() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_TIER_B_SCENARIO)["aggregate_over_epochs"]
    for key in (
        "serve_credit_attribution_model",
        "serve_credit_served_graph_node_only_count",
        "serve_events_credited_cdl_078_by_serving_peer",
        "serve_events_credited_cdl_078_by_tier",
        "serve_credit_serving_peer_total",
        "serve_credit_artifact_only_crediting_allowed",
        "routed_serve_events_credited_cdl_078",
        "routed_serve_events_credited_cdl_078_by_serving_peer",
        "routed_serve_events_credited_cdl_078_by_tier",
        "routed_serve_credit_rescue_count",
    ):
        assert key in metrics


def test_phase_1238g_random_credit_total_sums_by_peer_and_tier() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_TIER_B_SCENARIO)["aggregate_over_epochs"]
    legacy_total = metrics["serve_events_credited_cdl_078"]
    by_peer = metrics["serve_events_credited_cdl_078_by_serving_peer"]
    by_tier = metrics["serve_events_credited_cdl_078_by_tier"]

    assert legacy_total == metrics["serve_credit_serving_peer_total"]
    assert legacy_total == sum(by_peer.values())
    assert legacy_total == sum(by_tier.values())
    assert by_tier["A"] == 0
    assert by_tier["B"] == legacy_total
    assert by_tier["C"] == 0
    assert any(v > 0 for v in by_peer.values())


def test_phase_1238g_credit_model_rejects_artifact_only_attribution() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_TIER_B_SCENARIO)["aggregate_over_epochs"]
    assert metrics["serve_credit_attribution_model"] == "serving_peer_operator_instance"
    assert metrics["serve_credit_served_graph_node_only_count"] == 0
    assert metrics["serve_credit_artifact_only_crediting_allowed"] is False


def test_phase_1238g_routed_credit_total_sums_by_peer_and_tier() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_TIER_B_SCENARIO)["aggregate_over_epochs"]
    routed_total = metrics["routed_serve_events_credited_cdl_078"]
    by_peer = metrics["routed_serve_events_credited_cdl_078_by_serving_peer"]
    by_tier = metrics["routed_serve_events_credited_cdl_078_by_tier"]

    assert routed_total == sum(by_peer.values())
    assert routed_total == sum(by_tier.values())
    assert by_tier["A"] == 0
    assert by_tier["B"] == routed_total
    assert by_tier["C"] == 0
    assert routed_total > 0


def test_phase_1238g_rescued_routed_serves_receive_peer_credit() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_STALE_RESCUE_SCENARIO)["aggregate_over_epochs"]
    assert metrics["routed_rescue_count"] > 0
    assert metrics["routed_serve_credit_rescue_count"] == metrics["routed_rescue_count"]
    assert metrics["routed_retry_exhausted_count"] == 0
    assert Decimal(metrics["routed_failure_rate_by_tier"]["B"]) == Decimal("0.000000")


def test_phase_1238g_tier_c_serves_do_not_credit_cdl_078_by_default() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_TIER_C_SCENARIO)["aggregate_over_epochs"]
    assert metrics["want_block_success_count"] > 0
    assert metrics["serve_events_credited_cdl_078"] == 0
    assert metrics["routed_serve_events_credited_cdl_078"] == 0
    assert sum(metrics["serve_events_credited_cdl_078_by_serving_peer"].values()) == 0
    assert sum(metrics["routed_serve_events_credited_cdl_078_by_serving_peer"].values()) == 0


def test_phase_1238g_cdl_087_ratification_still_not_authorized() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_TIER_B_SCENARIO)
    assert result["cdl_087_ratification_authorized"] is False

