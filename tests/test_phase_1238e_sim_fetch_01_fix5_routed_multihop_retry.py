from __future__ import annotations

"""
Phase 1238e — Fix5: routed multi-hop WANT-HAVE retry tests.

Verifies:
- Fix5 version token is present
- max_retry_hops is validated and recorded
- post-retry routed metrics are present
- max_retry_hops=1 preserves Fix4 single-hop behavior
- multi-hop retry rescues stale first-hop misses in the 3-of-5 holder scenario
- first-hop diagnostics are stable when retry depth changes
- CDL-087 ratification remains unauthorized
"""

from decimal import Decimal

import pytest

_CONTROLLED_TIER_B_3_OF_5_STALE: dict = {
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
    "directory_staleness_rate": "1",
    "tier_b_exact_holder_count_per_artifact": 3,
}


def test_phase_1238e_fix5_version_token_present() -> None:
    import ilc_core.sim.sim_fetch_01.sim_fetch_01_harness as mod

    assert mod.SIM_FETCH_01_HARNESS_VERSION == "sim_fetch_01_harness_1238g.v0.1"
    assert mod.SIM_FETCH_01_FIX5_VERSION == (
        "sim_fetch_01_fix5_routed_multihop_retry_1238e.v0.1"
    )


def test_phase_1238e_multihop_metrics_present() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_CONTROLLED_TIER_B_3_OF_5_STALE)["aggregate_over_epochs"]
    for key in (
        "routed_single_hop_failure_rate_by_tier",
        "routed_single_hop_tier_ab_failure_rate",
        "routed_effective_failure_rate_by_tier",
        "routed_effective_tier_ab_failure_rate",
        "routed_max_retry_hops",
        "routed_total_probe_count",
        "routed_avg_hops_per_successful_request",
        "routed_rescue_count",
        "routed_retry_exhausted_count",
    ):
        assert key in metrics


def test_phase_1238e_default_max_retry_hops_preserves_fix4_single_hop() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(_CONTROLLED_TIER_B_3_OF_5_STALE)["aggregate_over_epochs"]
    assert metrics["routed_max_retry_hops"] == 1
    assert (
        metrics["routed_failure_rate_by_tier"]
        == metrics["routed_single_hop_failure_rate_by_tier"]
    )
    assert metrics["routed_rescue_count"] == 0


def test_phase_1238e_two_hops_rescue_stale_tier_b_misses() -> None:
    """
    With a fully stale directory, hop 1 is random and misses ~40% of the time
    when each Tier B artifact has exactly 3 holders among 5 peers. Hop 2 should
    traverse the holder directory and rescue every hop-1 miss.
    """
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    metrics = run_sim_fetch_01(
        {**_CONTROLLED_TIER_B_3_OF_5_STALE, "max_retry_hops": 2}
    )["aggregate_over_epochs"]

    single_hop_b = Decimal(metrics["routed_single_hop_failure_rate_by_tier"]["B"])
    effective_b = Decimal(metrics["routed_failure_rate_by_tier"]["B"])
    assert Decimal("0.30") <= single_hop_b <= Decimal("0.50")
    assert effective_b == Decimal("0.000000")
    assert metrics["routed_retry_exhausted_count"] == 0
    assert metrics["routed_rescue_count"] > 0
    assert Decimal(metrics["routed_avg_hops_per_successful_request"]) > Decimal("1")


def test_phase_1238e_first_hop_diagnostics_stable_when_retry_depth_changes() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    one_hop = run_sim_fetch_01(
        {**_CONTROLLED_TIER_B_3_OF_5_STALE, "max_retry_hops": 1}
    )["aggregate_over_epochs"]
    two_hops = run_sim_fetch_01(
        {**_CONTROLLED_TIER_B_3_OF_5_STALE, "max_retry_hops": 2}
    )["aggregate_over_epochs"]
    assert (
        one_hop["routed_single_hop_failure_rate_by_tier"]
        == two_hops["routed_single_hop_failure_rate_by_tier"]
    )
    assert one_hop["routed_total_probe_count"] < two_hops["routed_total_probe_count"]


def test_phase_1238e_max_retry_hops_validation() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    with pytest.raises(ValueError, match="invalid_max_retry_hops"):
        run_sim_fetch_01({**_CONTROLLED_TIER_B_3_OF_5_STALE, "max_retry_hops": 0})
    with pytest.raises(ValueError, match="invalid_max_retry_hops"):
        run_sim_fetch_01({**_CONTROLLED_TIER_B_3_OF_5_STALE, "max_retry_hops": True})
    with pytest.raises(ValueError, match="max_retry_hops_exceeds_n_peers"):
        run_sim_fetch_01({**_CONTROLLED_TIER_B_3_OF_5_STALE, "max_retry_hops": 6})


def test_phase_1238e_scenario_records_max_retry_hops() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(
        {**_CONTROLLED_TIER_B_3_OF_5_STALE, "max_retry_hops": 2}
    )
    assert result["scenario"]["max_retry_hops"] == 2


def test_phase_1238e_cdl_087_ratification_still_not_authorized() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(
        {**_CONTROLLED_TIER_B_3_OF_5_STALE, "max_retry_hops": 2}
    )
    assert result["cdl_087_ratification_authorized"] is False
