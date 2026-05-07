from __future__ import annotations

"""
Phase 1238h — Fix8: Werner topology overlay tests.

Verifies:
- Fix8 version token is present
- Werner overlay metrics are emitted
- overlay is disabled by default and never authorizes ECU/ILC settlement
- high Tier B routed pressure emits heat and capacity-expansion signals
- zero Tier C pressure emits cooling signals when evaluated
- overlay config validation rejects unsafe inputs
- deterministic config produces deterministic overlay traces
"""

from decimal import Decimal

import pytest

_WERNER_SCENARIO: dict = {
    "n_serving_peers": 5,
    "n_epochs": 6,
    "n_agents": 30,
    "tier_a_artifact_count": 1,
    "tier_b_artifact_count": 20,
    "tier_c_artifact_count": 1,
    "tier_a_request_rate": "0.00",
    "tier_b_request_rate": "1.00",
    "tier_c_request_rate": "0.00",
    "cache_capacity_per_peer": 50,
    "max_requests_per_epoch": 500,
    "seed": 123,
    "zipf_exponent_tier_b": "0.5",
    "directory_staleness_rate": "0",
    "tier_b_exact_holder_count_per_artifact": 3,
    "max_retry_hops": 1,
    "werner_overlay_enabled": True,
    "werner_smoothing_alpha": "0.25",
    "werner_heat_signal_threshold": 20,
    "werner_cooling_signal_threshold": 2,
    "werner_pressure_tiers": ["B", "C"],
}


def test_phase_1238h_fix8_version_token_present() -> None:
    import ilc_core.sim.sim_fetch_01.sim_fetch_01_harness as mod

    assert mod.SIM_FETCH_01_HARNESS_VERSION == "sim_fetch_01_harness_1238j.v0.1"
    assert mod.SIM_FETCH_01_FIX8_VERSION == (
        "sim_fetch_01_fix8_werner_topology_overlay_1238h.v0.1"
    )


def test_phase_1238h_werner_metrics_present() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_WERNER_SCENARIO)["aggregate_over_epochs"]
    for key in (
        "werner_overlay_enabled",
        "werner_overlay_mode",
        "werner_topology_smoothing_model",
        "werner_pressure_tiers",
        "werner_raw_pressure_by_epoch_by_tier",
        "werner_smoothed_pressure_by_epoch_by_tier",
        "werner_heat_signal_by_epoch_by_tier",
        "werner_cooling_signal_by_epoch_by_tier",
        "werner_heat_signal_count_by_tier",
        "werner_cooling_signal_count_by_tier",
        "werner_topology_recommendation_by_tier",
        "werner_ecu_pressure_signal_by_tier",
        "werner_ecu_pressure_mint_authorized",
        "werner_ilc_settlement_authorized",
    ):
        assert key in metrics


def test_phase_1238h_werner_disabled_by_default_and_non_authorizing() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    config = {k: v for k, v in _WERNER_SCENARIO.items() if not k.startswith("werner_")}
    result = run_sim_fetch_01(config)
    metrics = result["aggregate_over_epochs"]

    assert metrics["werner_overlay_enabled"] is False
    assert metrics["werner_raw_pressure_by_epoch_by_tier"]["B"] == []
    assert metrics["werner_topology_recommendation_by_tier"]["B"] == "not_evaluated"
    assert metrics["werner_ecu_pressure_mint_authorized"] is False
    assert metrics["werner_ilc_settlement_authorized"] is False
    assert result["cdl_087_ratification_authorized"] is False


def test_phase_1238h_high_tier_b_pressure_emits_heat_and_expand_signal() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_WERNER_SCENARIO)["aggregate_over_epochs"]

    assert metrics["werner_overlay_enabled"] is True
    assert metrics["werner_heat_signal_count_by_tier"]["B"] > 0
    assert metrics["werner_topology_recommendation_by_tier"]["B"] == "expand_capacity"
    assert Decimal(metrics["werner_ecu_pressure_signal_by_tier"]["B"]) > Decimal("0")
    assert len(metrics["werner_smoothed_pressure_by_epoch_by_tier"]["B"]) == (
        _WERNER_SCENARIO["n_epochs"]
    )


def test_phase_1238h_zero_tier_c_pressure_emits_cooling_signal() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_WERNER_SCENARIO)["aggregate_over_epochs"]

    assert metrics["werner_heat_signal_count_by_tier"]["C"] == 0
    assert metrics["werner_cooling_signal_count_by_tier"]["C"] == (
        _WERNER_SCENARIO["n_epochs"]
    )
    assert metrics["werner_topology_recommendation_by_tier"]["C"] == "cool_capacity"
    assert metrics["werner_ecu_pressure_signal_by_tier"]["C"] == "0.000000"


def test_phase_1238h_werner_validation_rejects_unsafe_inputs() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    with pytest.raises(ValueError, match="invalid_werner_overlay_enabled"):
        run_sim_fetch_01({**_WERNER_SCENARIO, "werner_overlay_enabled": "true"})
    with pytest.raises(ValueError, match="float_forbidden"):
        run_sim_fetch_01({**_WERNER_SCENARIO, "werner_smoothing_alpha": 0.5})
    with pytest.raises(ValueError, match="invalid_werner_heat_signal_threshold"):
        run_sim_fetch_01({**_WERNER_SCENARIO, "werner_heat_signal_threshold": 0})
    with pytest.raises(ValueError, match="invalid_werner_cooling_signal_threshold"):
        run_sim_fetch_01(
            {
                **_WERNER_SCENARIO,
                "werner_heat_signal_threshold": 5,
                "werner_cooling_signal_threshold": 5,
            }
        )
    with pytest.raises(ValueError, match="invalid_werner_pressure_tiers"):
        run_sim_fetch_01({**_WERNER_SCENARIO, "werner_pressure_tiers": ["A"]})


def test_phase_1238h_werner_overlay_is_deterministic() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    r1 = run_sim_fetch_01(_WERNER_SCENARIO)
    r2 = run_sim_fetch_01(_WERNER_SCENARIO)
    assert r1["aggregate_over_epochs"]["werner_smoothed_pressure_by_epoch_by_tier"] == (
        r2["aggregate_over_epochs"]["werner_smoothed_pressure_by_epoch_by_tier"]
    )
    assert r1 == r2
