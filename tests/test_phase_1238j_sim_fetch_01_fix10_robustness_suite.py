from __future__ import annotations

import json

import pytest


_BASE_ROBUSTNESS_SCENARIO: dict = {
    "n_serving_peers": 5,
    "n_epochs": 8,
    "n_agents": 24,
    "tier_a_artifact_count": 5,
    "tier_b_artifact_count": 30,
    "tier_c_artifact_count": 60,
    "tier_a_request_rate": "0.20",
    "tier_b_request_rate": "0.50",
    "tier_c_request_rate": "0.30",
    "cache_capacity_per_peer": 50,
    "max_requests_per_epoch": 100,
    "seed": 42,
    "avg_requests_per_agent": "3",
    "zipf_exponent_tier_a": "1.0",
    "zipf_exponent_tier_b": "0.5",
    "directory_staleness_rate": "0",
    "tier_b_exact_holder_count_per_artifact": 3,
    "max_retry_hops": 1,
    "adaptive_replication_enabled": False,
    "werner_overlay_enabled": False,
    "werner_smoothing_alpha": "0.25",
    "werner_heat_signal_threshold": 20,
    "werner_cooling_signal_threshold": 2,
    "werner_pressure_tiers": ["B", "C"],
}


_ROBUSTNESS_CONFIG: dict = {
    "base_scenario": _BASE_ROBUSTNESS_SCENARIO,
    "max_total_scenarios": 32,
    "profiles": [
        {
            "profile_id": "fresh_holder_directory_control",
            "description": "Fresh holder directory should pass.",
            "acceptance_rule": "all_pass",
            "grid": {
                "directory_staleness_rate": ["0"],
                "max_retry_hops": [1, 2],
                "werner_overlay_enabled": [False, True],
            },
        },
        {
            "profile_id": "stale_directory_one_hop_negative_control",
            "description": "Fully stale one-hop routing should fail.",
            "acceptance_rule": "all_fail",
            "grid": {
                "directory_staleness_rate": ["1.00"],
                "max_retry_hops": [1],
                "tier_b_exact_holder_count_per_artifact": [2, 3],
            },
        },
        {
            "profile_id": "stale_directory_two_hop_rescue",
            "description": "Two-hop routing should rescue stale first hop.",
            "acceptance_rule": "all_pass",
            "grid": {
                "directory_staleness_rate": ["1.00"],
                "max_retry_hops": [2],
                "tier_b_exact_holder_count_per_artifact": [1, 2, 3],
            },
        },
        {
            "profile_id": "low_holder_adaptive_recovery",
            "description": "Adaptive replication should recover low holder count.",
            "acceptance_rule": "any_pass",
            "scenario_overrides": {
                "tier_b_exact_holder_count_per_artifact": 1,
                "adaptive_replication_enabled": True,
                "heat_replication_threshold": 1,
                "max_adaptive_replications_per_epoch": 20,
                "n_epochs": 8,
            },
            "grid": {
                "directory_staleness_rate": ["0.25"],
                "max_retry_hops": [1, 2],
                "adaptive_replication_enabled": [True],
            },
        },
    ],
}


def test_phase_1238j_fix10_version_token_present() -> None:
    import ilc_core.sim.sim_fetch_01.sim_fetch_01_harness as mod

    assert mod.SIM_FETCH_01_HARNESS_VERSION == "sim_fetch_01_harness_1238j.v0.1"
    assert mod.SIM_FETCH_01_FIX10_VERSION == (
        "sim_fetch_01_fix10_robustness_suite_1238j.v0.1"
    )


def test_phase_1238j_robustness_suite_returns_required_shape() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_robustness_suite,
    )

    result = run_sim_fetch_01_cdl_087_robustness_suite(_ROBUSTNESS_CONFIG)

    assert result["methodology"] == "adversarial_robustness_envelope_expansion"
    assert result["overall_robustness_verdict"] == "pass"
    assert result["profile_count"] == 4
    assert result["accepted_profile_count"] == 4
    assert result["total_scenario_count"] == 11
    assert len(result["profiles"]) == 4


def test_phase_1238j_negative_control_must_fail_and_be_accepted() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_robustness_suite,
    )

    result = run_sim_fetch_01_cdl_087_robustness_suite(_ROBUSTNESS_CONFIG)
    profile = {
        row["profile_id"]: row for row in result["profiles"]
    }["stale_directory_one_hop_negative_control"]

    assert profile["acceptance_rule"] == "all_fail"
    assert profile["accepted"] is True
    assert profile["verdict_counts"]["fail"] == profile["scenario_count"]
    assert "routed_tier_ab_failure_above_block_floor" in profile["fail_reason_counts"]


def test_phase_1238j_two_hop_rescue_profile_passes() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_robustness_suite,
    )

    result = run_sim_fetch_01_cdl_087_robustness_suite(_ROBUSTNESS_CONFIG)
    profile = {
        row["profile_id"]: row for row in result["profiles"]
    }["stale_directory_two_hop_rescue"]

    assert profile["accepted"] is True
    assert profile["verdict_counts"]["pass"] == profile["scenario_count"]
    assert profile["metric_extrema"]["max_routed_effective_tier_ab_failure_rate"] == "0.000000"


def test_phase_1238j_wrong_acceptance_rule_fails_overall_suite() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_robustness_suite,
    )

    bad_config = {
        **_ROBUSTNESS_CONFIG,
        "profiles": [
            {
                **_ROBUSTNESS_CONFIG["profiles"][1],
                "acceptance_rule": "all_pass",
            }
        ],
    }
    result = run_sim_fetch_01_cdl_087_robustness_suite(bad_config)

    assert result["overall_robustness_verdict"] == "fail"
    assert result["accepted_profile_count"] == 0


def test_phase_1238j_robustness_suite_rejects_float_and_caps() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_robustness_suite,
    )

    with pytest.raises(ValueError, match="float_forbidden"):
        run_sim_fetch_01_cdl_087_robustness_suite(
            {
                **_ROBUSTNESS_CONFIG,
                "profiles": [
                    {
                        **_ROBUSTNESS_CONFIG["profiles"][0],
                        "grid": {"directory_staleness_rate": [0.25]},
                    }
                ],
            }
        )

    with pytest.raises(ValueError, match="total_scenario_count_exceeded"):
        run_sim_fetch_01_cdl_087_robustness_suite(
            {**_ROBUSTNESS_CONFIG, "max_total_scenarios": 1}
        )


def test_phase_1238j_robustness_suite_is_non_authorizing_and_deterministic() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_robustness_suite,
    )

    r1 = run_sim_fetch_01_cdl_087_robustness_suite(_ROBUSTNESS_CONFIG)
    r2 = run_sim_fetch_01_cdl_087_robustness_suite(_ROBUSTNESS_CONFIG)

    assert r1 == r2
    assert r1["cdl_087_ratification_authorized"] is False


def test_phase_1238j_robustness_json_export_remains_canonical() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        export_sim_fetch_01_evidence_json,
        run_sim_fetch_01_cdl_087_robustness_suite,
    )

    result = run_sim_fetch_01_cdl_087_robustness_suite(_ROBUSTNESS_CONFIG)
    payload = export_sim_fetch_01_evidence_json(result)

    assert json.loads(payload) == result
    assert payload == json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
