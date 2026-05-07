from __future__ import annotations

import json
from decimal import Decimal

import pytest


_BASE_EVIDENCE_SCENARIO: dict = {
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
}


_EVIDENCE_SWEEP_CONFIG: dict = {
    "base_scenario": _BASE_EVIDENCE_SCENARIO,
    "grid": {
        "adaptive_replication_enabled": [False],
        "directory_staleness_rate": ["0", "1.00"],
        "max_retry_hops": [1, 2],
        "werner_overlay_enabled": [False, True],
    },
    "max_sweep_scenarios": 8,
}


def test_phase_1238i_fix9_version_token_present() -> None:
    import ilc_core.sim.sim_fetch_01.sim_fetch_01_harness as mod

    assert mod.SIM_FETCH_01_HARNESS_VERSION == "sim_fetch_01_harness_1238i.v0.1"
    assert mod.SIM_FETCH_01_FIX9_VERSION == (
        "sim_fetch_01_fix9_cdl_087_evidence_matrix_1238i.v0.1"
    )


def test_phase_1238i_evidence_sweep_returns_required_shape() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_evidence_sweep,
    )

    result = run_sim_fetch_01_cdl_087_evidence_sweep(_EVIDENCE_SWEEP_CONFIG)

    assert result["methodology"] == "karpathy_auto_research_fixed_evaluator_parameter_sweep"
    assert result["scenario_count"] == 8
    assert result["grid_keys"] == [
        "adaptive_replication_enabled",
        "directory_staleness_rate",
        "max_retry_hops",
        "werner_overlay_enabled",
    ]
    assert len(result["rows"]) == 8
    assert len(result["recommended_scenarios"]) <= 5


def test_phase_1238i_evidence_sweep_identifies_pass_and_fail_envelopes() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_evidence_sweep,
    )

    result = run_sim_fetch_01_cdl_087_evidence_sweep(_EVIDENCE_SWEEP_CONFIG)

    assert result["verdict_counts"]["pass"] > 0
    assert result["verdict_counts"]["fail"] > 0
    assert (
        result["cdl_087_ratification_recommendation"]
        == "candidate_envelope_identified_for_governance_review"
    )


def test_phase_1238i_evidence_evaluator_uses_routed_not_random_baseline() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_evidence_sweep,
    )

    result = run_sim_fetch_01_cdl_087_evidence_sweep(_EVIDENCE_SWEEP_CONFIG)
    row = result["rows"][0]
    metrics = row["key_metrics"]

    assert Decimal(metrics["single_hop_random_tier_ab_failure_rate"]) > Decimal("0.20")
    assert Decimal(metrics["routed_effective_tier_ab_failure_rate"]) == Decimal("0")
    assert row["evaluator"]["verdict"] == "pass"


def test_phase_1238i_evidence_sweep_caps_scenario_count() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_evidence_sweep,
    )

    with pytest.raises(ValueError, match="scenario_count_exceeded"):
        run_sim_fetch_01_cdl_087_evidence_sweep(
            {
                **_EVIDENCE_SWEEP_CONFIG,
                "grid": {
                    **_EVIDENCE_SWEEP_CONFIG["grid"],
                    "seed": [1, 2],
                },
                "max_sweep_scenarios": 8,
            }
        )


def test_phase_1238i_evidence_sweep_rejects_float_inputs() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_evidence_sweep,
    )

    with pytest.raises(ValueError, match="float_forbidden"):
        run_sim_fetch_01_cdl_087_evidence_sweep(
            {
                **_EVIDENCE_SWEEP_CONFIG,
                "grid": {
                    **_EVIDENCE_SWEEP_CONFIG["grid"],
                    "directory_staleness_rate": [0.5],
                },
            }
        )


def test_phase_1238i_evidence_json_export_is_canonical_and_bounded() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        export_sim_fetch_01_evidence_json,
        run_sim_fetch_01_cdl_087_evidence_sweep,
    )

    result = run_sim_fetch_01_cdl_087_evidence_sweep(_EVIDENCE_SWEEP_CONFIG)
    payload = export_sim_fetch_01_evidence_json(result)
    parsed = json.loads(payload)

    assert parsed == result
    assert payload == json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
    with pytest.raises(ValueError, match="max_bytes_exceeded"):
        export_sim_fetch_01_evidence_json(result, max_bytes=10)


def test_phase_1238i_evidence_sweep_is_non_authorizing_and_deterministic() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import (
        run_sim_fetch_01_cdl_087_evidence_sweep,
    )

    r1 = run_sim_fetch_01_cdl_087_evidence_sweep(_EVIDENCE_SWEEP_CONFIG)
    r2 = run_sim_fetch_01_cdl_087_evidence_sweep(_EVIDENCE_SWEEP_CONFIG)

    assert r1 == r2
    assert r1["cdl_087_ratification_authorized"] is False
    for row in r1["rows"]:
        assert row["scenario"]["werner_overlay_enabled"] in (False, True)
        assert row["key_metrics"]["werner_ecu_pressure_mint_authorized"] is False
        assert row["key_metrics"]["werner_ilc_settlement_authorized"] is False
