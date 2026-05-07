from __future__ import annotations

"""
Phase 1238d — Fix4: routed holder model tests.

Verifies:
- routed holder metrics are present
- single-hop random metrics are preserved under explicit renamed keys
- Fix3 metric names remain backward-compatible aliases
- zero-staleness holder routing improves Tier B availability versus random probing
- a controlled 3-of-5 Tier B holder layout yields ~40% random miss and 0% routed miss
- directory staleness and peer role parameters are validated
"""

from decimal import Decimal

import pytest

_BASELINE_SCENARIO: dict = {
    "n_serving_peers": 5,
    "n_epochs": 100,
    "n_agents": 50,
    "tier_a_artifact_count": 20,
    "tier_b_artifact_count": 80,
    "tier_c_artifact_count": 400,
    "tier_a_request_rate": "0.10",
    "tier_b_request_rate": "0.30",
    "tier_c_request_rate": "0.60",
    "cache_capacity_per_peer": 50,
    "max_requests_per_epoch": 500,
    "seed": 42,
    "directory_staleness_rate": "0",
}

_CONTROLLED_TIER_B_3_OF_5: dict = {
    "n_serving_peers": 5,
    "n_epochs": 200,
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
    "directory_staleness_rate": "0",
    "tier_b_exact_holder_count_per_artifact": 3,
}


def test_phase_1238d_fix4_version_token_present() -> None:
    import ilc_core.sim.sim_fetch_01.sim_fetch_01_harness as mod

    assert mod.SIM_FETCH_01_HARNESS_VERSION == "sim_fetch_01_harness_1238h.v0.1"
    assert mod.SIM_FETCH_01_FIX4_VERSION == (
        "sim_fetch_01_fix4_routed_holder_model_1238d.v0.1"
    )


def test_phase_1238d_routed_metrics_present() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    metrics = result["aggregate_over_epochs"]
    for key in (
        "routed_failure_rate_by_tier",
        "routed_tier_ab_failure_rate",
        "routed_tier_service_verdict",
        "routed_holder_hit_rate",
        "routed_staleness_rate_observed",
        "known_holder_count_stats_by_tier",
    ):
        assert key in metrics


def test_phase_1238d_single_hop_random_metrics_and_fix3_aliases_match() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_BASELINE_SCENARIO)["aggregate_over_epochs"]
    assert metrics["failure_rate_by_tier"] == metrics["single_hop_random_failure_rate_by_tier"]
    assert metrics["tier_ab_failure_rate"] == metrics["single_hop_random_tier_ab_failure_rate"]
    assert (
        metrics["tier_c_advisory_failure_rate"]
        == metrics["single_hop_random_tier_c_advisory_failure_rate"]
    )


def test_phase_1238d_default_routed_tier_b_beats_random_null_model() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_BASELINE_SCENARIO)["aggregate_over_epochs"]
    random_b = Decimal(metrics["single_hop_random_failure_rate_by_tier"]["B"])
    routed_b = Decimal(metrics["routed_failure_rate_by_tier"]["B"])
    assert routed_b < random_b
    assert Decimal(metrics["routed_tier_ab_failure_rate"]) < Decimal(
        metrics["single_hop_random_tier_ab_failure_rate"]
    )


def test_phase_1238d_exact_three_of_five_holders_random_misses_routed_succeeds() -> None:
    """
    Each Tier B artifact is held by exactly 3 of 5 peers.

    Uniform random probing should miss about 40% of the time. Holder-directory
    routing with zero staleness should route every request to one of those
    three holders and therefore produce zero Tier B availability failures.
    """
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_CONTROLLED_TIER_B_3_OF_5)["aggregate_over_epochs"]
    stats_b = metrics["known_holder_count_stats_by_tier"]["B"]
    assert stats_b == {
        "min": 3,
        "mean": "3.000000",
        "max": 3,
        "zero_holder_count": 0,
    }

    random_b = Decimal(metrics["single_hop_random_failure_rate_by_tier"]["B"])
    routed_b = Decimal(metrics["routed_failure_rate_by_tier"]["B"])
    assert Decimal("0.30") <= random_b <= Decimal("0.50")
    assert routed_b == Decimal("0.000000")
    assert metrics["routed_holder_hit_rate"] == "1.000000"


def test_phase_1238d_directory_staleness_degrades_routed_model() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    fresh = run_sim_fetch_01(_CONTROLLED_TIER_B_3_OF_5)["aggregate_over_epochs"]
    stale = run_sim_fetch_01(
        {**_CONTROLLED_TIER_B_3_OF_5, "directory_staleness_rate": "1"}
    )["aggregate_over_epochs"]
    assert Decimal(fresh["routed_failure_rate_by_tier"]["B"]) == Decimal("0.000000")
    assert Decimal(stale["routed_failure_rate_by_tier"]["B"]) > Decimal("0.30")
    assert stale["routed_staleness_rate_observed"] == "1.000000"


def test_phase_1238d_hot_mirror_roles_raise_tier_b_holder_mean() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    baseline = run_sim_fetch_01(_BASELINE_SCENARIO)
    mirrored = run_sim_fetch_01(
        {
            **_BASELINE_SCENARIO,
            "hot_mirror_peer_count": 2,
            "hot_mirror_tier_b_fraction": 10,
        }
    )
    base_mean = Decimal(
        baseline["aggregate_over_epochs"]["known_holder_count_stats_by_tier"]["B"]["mean"]
    )
    mirror_mean = Decimal(
        mirrored["aggregate_over_epochs"]["known_holder_count_stats_by_tier"]["B"]["mean"]
    )
    assert mirror_mean > base_mean
    assert mirrored["scenario"]["peer_roles"][:2] == ["hot_mirror", "hot_mirror"]


def test_phase_1238d_directory_staleness_float_rejected() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    with pytest.raises(ValueError, match="float_forbidden"):
        run_sim_fetch_01({**_BASELINE_SCENARIO, "directory_staleness_rate": 0.5})


def test_phase_1238d_directory_staleness_out_of_range_rejected() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    with pytest.raises(ValueError, match="rate_out_of_range"):
        run_sim_fetch_01({**_BASELINE_SCENARIO, "directory_staleness_rate": "1.5"})


def test_phase_1238d_exact_holder_count_validation() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    with pytest.raises(ValueError, match="invalid_tier_b_exact_holder_count"):
        run_sim_fetch_01(
            {**_CONTROLLED_TIER_B_3_OF_5, "tier_b_exact_holder_count_per_artifact": 6}
        )
    with pytest.raises(ValueError, match="invalid_tier_b_exact_holder_count"):
        run_sim_fetch_01(
            {**_CONTROLLED_TIER_B_3_OF_5, "tier_b_exact_holder_count_per_artifact": True}
        )
