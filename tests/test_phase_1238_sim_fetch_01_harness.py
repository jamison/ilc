from __future__ import annotations

from pathlib import Path

import pytest

HARNESS_PATH = Path("ilc_core/sim/sim_fetch_01/sim_fetch_01_harness.py")
DESIGN_SPEC_PATH = Path("docs/sims/sim_fetch_01/sim_fetch_01_design_spec_1238_v0.1.md")

# Minimal valid baseline scenario
_BASELINE_SCENARIO: dict = {
    "n_serving_peers": 5,
    "n_epochs": 10,
    "n_agents": 20,
    "tier_a_artifact_count": 20,
    "tier_b_artifact_count": 80,
    "tier_c_artifact_count": 400,
    "tier_a_request_rate": "0.10",
    "tier_b_request_rate": "0.30",
    "tier_c_request_rate": "0.60",
    "cache_capacity_per_peer": 50,
    "max_requests_per_epoch": 100,
    "seed": 42,
}

# CDL-087 §6 required metric keys (exact names from prelock spec)
_CDL_087_Q4_KEYS = {
    "fetch_requests_by_tier",
    "want_have_hit_rate",
    "want_have_miss_rate",
    "want_block_success_count",
    "want_block_error_404",
    "want_block_error_429",
    "want_block_error_400",
    "cache_hit_rate_tier_a",
    "bytes_served_by_tier",
    "non_cacheable_request_volume",
    "circuit_breaker_activations",
    "serve_events_credited_cdl_078",
}

# Phase 1238 test contract fields (including test-contract-specified aliases)
_TEST_CONTRACT_KEYS = {
    "cache_hit_rate_high_centrality",
    "cache_hit_rate_tail",
    "request_pressure_by_tier",
    "serve_pressure_by_peer",
    "failure_rate",
}


def test_phase_1238_harness_imports_without_error() -> None:
    import ilc_core.sim.sim_fetch_01.sim_fetch_01_harness as mod

    assert mod.SIM_FETCH_01_HARNESS_VERSION == "sim_fetch_01_harness_1238.v0.1"
    assert mod.CDL_087_DEPENDENCY == "cdl_087_prelock_committed_phase_1228"


def test_phase_1238_design_spec_file_exists() -> None:
    assert DESIGN_SPEC_PATH.exists(), f"Design spec not found at {DESIGN_SPEC_PATH}"


def test_phase_1238_run_sim_returns_cdl_087_q4_metric_keys() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    metrics = result["aggregate_over_epochs"]
    for key in _CDL_087_Q4_KEYS:
        assert key in metrics, f"CDL-087 §6 metric missing from result: {key}"


def test_phase_1238_result_contains_required_field_names() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    metrics = result["aggregate_over_epochs"]
    for key in _TEST_CONTRACT_KEYS:
        assert key in metrics, f"Test-contract field missing from result: {key}"


def test_phase_1238_harness_rejects_float_values_in_economic_fields() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    bad_config = {**_BASELINE_SCENARIO, "tier_a_request_rate": 0.10}  # float, not str
    with pytest.raises(ValueError, match="float_forbidden"):
        run_sim_fetch_01(bad_config)


def test_phase_1238_harness_respects_max_requests_cap() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    cap = 10
    n_epochs = 3
    result = run_sim_fetch_01(
        {
            **_BASELINE_SCENARIO,
            "n_agents": 10_000,  # would generate many requests without cap
            "max_requests_per_epoch": cap,
            "n_epochs": n_epochs,
        }
    )
    metrics = result["aggregate_over_epochs"]
    total_processed = (
        sum(metrics["fetch_requests_by_tier"].values())
        + metrics["want_block_error_429"]
    )
    assert total_processed <= n_epochs * cap


def test_phase_1238_determinism_identical_config_produces_identical_result() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    r1 = run_sim_fetch_01(_BASELINE_SCENARIO)
    r2 = run_sim_fetch_01(_BASELINE_SCENARIO)
    assert r1 == r2, "Two runs with identical config produced different results"


def test_phase_1238_design_spec_states_ratification_not_authorized() -> None:
    text = DESIGN_SPEC_PATH.read_text(encoding="utf-8")
    assert "CDL-087 ratification NOT authorized" in text


def test_phase_1238_design_spec_references_prelock_spec_as_governing_authority() -> None:
    text = DESIGN_SPEC_PATH.read_text(encoding="utf-8")
    assert "cdl_087_prelock_spec_1228_v0.1.md" in text
