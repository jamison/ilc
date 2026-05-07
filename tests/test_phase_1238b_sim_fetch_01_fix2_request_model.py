from __future__ import annotations

"""
Phase 1238b — Fix2: Poisson epoch count + Zipf artifact selection tests.

Verifies:
- Tier A/B artifact selection concentrates on hot artifacts (Zipf property)
- Higher Zipf exponent produces higher concentration
- top_quartile_request_concentration_by_tier present in output
- avg_requests_per_agent controls epoch request count
- Poisson count varies with fractional avg_requests_per_agent
- Zipf exponent out of range rejected
- Version tokens correct
"""

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
}


def test_phase_1238b_fix2_version_tokens_present() -> None:
    import ilc_core.sim.sim_fetch_01.sim_fetch_01_harness as mod

    assert mod.SIM_FETCH_01_HARNESS_VERSION == "sim_fetch_01_harness_1238g.v0.1"
    assert mod.SIM_FETCH_01_FIX2_VERSION == "sim_fetch_01_fix2_request_model_1238b.v0.1"


def test_phase_1238b_top_quartile_concentration_key_present() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    metrics = result["aggregate_over_epochs"]
    assert "top_quartile_request_concentration_by_tier" in metrics
    conc = metrics["top_quartile_request_concentration_by_tier"]
    assert "A" in conc and "B" in conc and "C" in conc


def test_phase_1238b_zipf_tier_a_concentrates_requests_on_hot_artifacts() -> None:
    """
    With Zipf s=1.0 over 20 Tier A artifacts, top 25% (5 artifacts) should
    receive well above the uniform expectation of 25% — expect ≥ 50%.
    """
    from decimal import Decimal
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01({**_BASELINE_SCENARIO, "zipf_exponent_tier_a": "1.0"})
    conc_a = Decimal(result["aggregate_over_epochs"]["top_quartile_request_concentration_by_tier"]["A"])
    assert conc_a >= Decimal("0.50"), (
        f"Tier A top-quartile concentration {conc_a} < 0.50 — Zipf distribution not working"
    )


def test_phase_1238b_higher_zipf_exponent_produces_higher_concentration() -> None:
    """Higher s → stronger Zipf → more concentration on rank-1 artifacts."""
    from decimal import Decimal
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    r_low = run_sim_fetch_01({**_BASELINE_SCENARIO, "zipf_exponent_tier_a": "0.5"})
    r_high = run_sim_fetch_01({**_BASELINE_SCENARIO, "zipf_exponent_tier_a": "2.0"})
    conc_low = Decimal(r_low["aggregate_over_epochs"]["top_quartile_request_concentration_by_tier"]["A"])
    conc_high = Decimal(r_high["aggregate_over_epochs"]["top_quartile_request_concentration_by_tier"]["A"])
    assert conc_high > conc_low, (
        f"Higher Zipf exponent did not produce higher concentration: "
        f"s=0.5 → {conc_low}, s=2.0 → {conc_high}"
    )


def test_phase_1238b_tier_c_uniform_lower_concentration_than_zipf_tier_a() -> None:
    """
    Tier C uses uniform artifact selection; should have lower concentration
    than Tier A (Zipf s=1.0) when both have enough requests.
    """
    from decimal import Decimal
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    conc = result["aggregate_over_epochs"]["top_quartile_request_concentration_by_tier"]
    conc_a = Decimal(conc["A"])
    conc_c = Decimal(conc["C"])
    # Tier A (Zipf s=1.0) should be more concentrated than Tier C (uniform)
    assert conc_a > conc_c, (
        f"Tier A concentration {conc_a} should exceed Tier C (uniform) {conc_c}"
    )


def test_phase_1238b_avg_requests_per_agent_scales_epoch_count() -> None:
    """Doubling avg_requests_per_agent should roughly double total requests."""
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    r_low = run_sim_fetch_01({
        **_BASELINE_SCENARIO,
        "avg_requests_per_agent": "1",
        "max_requests_per_epoch": 10000,
    })
    r_high = run_sim_fetch_01({
        **_BASELINE_SCENARIO,
        "avg_requests_per_agent": "2",
        "max_requests_per_epoch": 10000,
    })
    metrics_low = r_low["aggregate_over_epochs"]
    metrics_high = r_high["aggregate_over_epochs"]

    total_low = (
        sum(metrics_low["fetch_requests_by_tier"].values())
        + metrics_low["want_block_error_429"]
    )
    total_high = (
        sum(metrics_high["fetch_requests_by_tier"].values())
        + metrics_high["want_block_error_429"]
    )
    # avg=2 should produce roughly 2x requests as avg=1
    assert total_high > total_low * 1.7, (
        f"avg=2 produced {total_high} requests vs avg=1 produced {total_low} "
        f"— expected roughly 2x"
    )


def test_phase_1238b_zipf_exponent_too_low_rejected() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    bad = {**_BASELINE_SCENARIO, "zipf_exponent_tier_a": "0.05"}
    with pytest.raises(ValueError, match="value_out_of_range"):
        run_sim_fetch_01(bad)


def test_phase_1238b_zipf_exponent_too_high_rejected() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    bad = {**_BASELINE_SCENARIO, "zipf_exponent_tier_a": "5.5"}
    with pytest.raises(ValueError, match="value_out_of_range"):
        run_sim_fetch_01(bad)


def test_phase_1238b_float_zipf_exponent_rejected() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    bad = {**_BASELINE_SCENARIO, "zipf_exponent_tier_a": 1.0}
    with pytest.raises(ValueError, match="float_forbidden"):
        run_sim_fetch_01(bad)


def test_phase_1238b_float_avg_requests_per_agent_rejected() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    bad = {**_BASELINE_SCENARIO, "avg_requests_per_agent": 3.0}
    with pytest.raises(ValueError, match="float_forbidden"):
        run_sim_fetch_01(bad)


def test_phase_1238b_determinism_preserved_with_zipf() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    r1 = run_sim_fetch_01(_BASELINE_SCENARIO)
    r2 = run_sim_fetch_01(_BASELINE_SCENARIO)
    assert r1 == r2, "Two runs with identical config produced different results"


def test_phase_1238b_scenario_records_zipf_params() -> None:
    """Zipf exponents and avg_requests_per_agent must appear in result scenario dict."""
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    sc = result["scenario"]
    assert "zipf_exponent_tier_a" in sc
    assert "zipf_exponent_tier_b" in sc
    assert "avg_requests_per_agent" in sc
