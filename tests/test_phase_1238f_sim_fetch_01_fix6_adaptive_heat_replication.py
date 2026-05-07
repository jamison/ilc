from __future__ import annotations

"""
Phase 1238f — Fix6: adaptive heat-driven replication tests.

Verifies:
- Fix6 version token is present
- adaptive replication metrics are present
- disabled-by-default behavior preserves holder topology
- heat-driven replication increases holder counts for hot Tier B artifacts
- effective routed failure declines across epochs as holders are added
- replication controls are validated
- CDL-087 ratification remains unauthorized
"""

from decimal import Decimal

import pytest

_HEAT_SCENARIO: dict = {
    "n_serving_peers": 5,
    "n_epochs": 8,
    "n_agents": 50,
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
    "directory_staleness_rate": "1",
    "tier_b_exact_holder_count_per_artifact": 1,
    "max_retry_hops": 1,
    "heat_replication_threshold": 1,
    "max_adaptive_replications_per_epoch": 20,
    "adaptive_replication_tiers": ["B"],
}


def test_phase_1238f_fix6_version_token_present() -> None:
    import ilc_core.sim.sim_fetch_01.sim_fetch_01_harness as mod

    assert mod.SIM_FETCH_01_HARNESS_VERSION == "sim_fetch_01_harness_1238h.v0.1"
    assert mod.SIM_FETCH_01_FIX6_VERSION == (
        "sim_fetch_01_fix6_adaptive_heat_replication_1238f.v0.1"
    )


def test_phase_1238f_adaptive_metrics_present() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_HEAT_SCENARIO)["aggregate_over_epochs"]
    for key in (
        "adaptive_replication_enabled",
        "adaptive_replication_events_by_tier",
        "adaptive_replication_total_events",
        "adaptive_replication_epochs_active",
        "adaptive_replication_tiers",
        "adaptive_heat_threshold",
        "adaptive_max_replications_per_epoch",
        "initial_known_holder_count_stats_by_tier",
        "final_known_holder_count_stats_by_tier",
        "routed_failure_rate_by_epoch_by_tier",
        "adaptive_holder_mean_by_epoch_by_tier",
    ):
        assert key in metrics


def test_phase_1238f_disabled_by_default_preserves_holder_topology() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_HEAT_SCENARIO)["aggregate_over_epochs"]
    assert metrics["adaptive_replication_enabled"] is False
    assert metrics["adaptive_replication_total_events"] == 0
    assert (
        metrics["initial_known_holder_count_stats_by_tier"]["B"]
        == metrics["known_holder_count_stats_by_tier"]["B"]
    )


def test_phase_1238f_heat_replication_increases_tier_b_holder_mean() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(
        {**_HEAT_SCENARIO, "adaptive_replication_enabled": True}
    )["aggregate_over_epochs"]

    initial_mean = Decimal(metrics["initial_known_holder_count_stats_by_tier"]["B"]["mean"])
    final_mean = Decimal(metrics["known_holder_count_stats_by_tier"]["B"]["mean"])
    assert initial_mean == Decimal("1.000000")
    assert final_mean == Decimal("5.000000")
    assert metrics["adaptive_replication_events_by_tier"]["B"] == 80
    assert metrics["adaptive_replication_total_events"] == 80


def test_phase_1238f_heat_replication_reduces_epoch_failure_rate() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(
        {**_HEAT_SCENARIO, "adaptive_replication_enabled": True}
    )["aggregate_over_epochs"]
    epoch_rates = [
        Decimal(v) for v in metrics["routed_failure_rate_by_epoch_by_tier"]["B"]
    ]
    holder_means = [
        Decimal(v) for v in metrics["adaptive_holder_mean_by_epoch_by_tier"]["B"]
    ]
    assert epoch_rates[0] > Decimal("0.70")
    assert epoch_rates[-1] == Decimal("0.000000")
    assert holder_means[0] == Decimal("2.000000")
    assert holder_means[-1] == Decimal("5.000000")


def test_phase_1238f_replication_epoch_cap_limits_growth() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    capped = run_sim_fetch_01(
        {
            **_HEAT_SCENARIO,
            "adaptive_replication_enabled": True,
            "max_adaptive_replications_per_epoch": 1,
        }
    )["aggregate_over_epochs"]
    assert capped["adaptive_replication_total_events"] == _HEAT_SCENARIO["n_epochs"]
    assert Decimal(capped["known_holder_count_stats_by_tier"]["B"]["mean"]) < Decimal("2")


def test_phase_1238f_adaptive_replication_validation() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    with pytest.raises(ValueError, match="invalid_adaptive_replication_enabled"):
        run_sim_fetch_01({**_HEAT_SCENARIO, "adaptive_replication_enabled": "true"})
    with pytest.raises(ValueError, match="invalid_heat_replication_threshold"):
        run_sim_fetch_01({**_HEAT_SCENARIO, "heat_replication_threshold": 0})
    with pytest.raises(ValueError, match="invalid_max_adaptive_replications_per_epoch"):
        run_sim_fetch_01({**_HEAT_SCENARIO, "max_adaptive_replications_per_epoch": True})
    with pytest.raises(ValueError, match="invalid_adaptive_replication_tiers"):
        run_sim_fetch_01({**_HEAT_SCENARIO, "adaptive_replication_tiers": ["A"]})


def test_phase_1238f_scenario_records_adaptive_controls() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01({**_HEAT_SCENARIO, "adaptive_replication_enabled": True})
    scenario = result["scenario"]
    assert scenario["adaptive_replication_enabled"] is True
    assert scenario["heat_replication_threshold"] == 1
    assert scenario["max_adaptive_replications_per_epoch"] == 20
    assert scenario["adaptive_replication_tiers"] == ["B"]


def test_phase_1238f_cdl_087_ratification_still_not_authorized() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01({**_HEAT_SCENARIO, "adaptive_replication_enabled": True})
    assert result["cdl_087_ratification_authorized"] is False

