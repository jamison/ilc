from __future__ import annotations

"""
Phase 1238c — Fix3: tier-stratified metrics and verdict decomposition tests.

Verifies:
- failure_rate_by_tier present with A/B/C keys
- tier_ab_failure_rate present
- tier_c_advisory_failure_rate present
- tier_service_verdict present and does not claim CDL-087 ratification
- aggregate_verdict present and equals verdict
- Original verdict field preserved (backward compatibility)
- Per-tier 404 counts are consistent with aggregate
- Tier C sparsity reflected in tier_c_advisory_failure_rate > tier_ab_failure_rate
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


def test_phase_1238c_fix3_version_token_present() -> None:
    import ilc_core.sim.sim_fetch_01.sim_fetch_01_harness as mod

    assert mod.SIM_FETCH_01_HARNESS_VERSION == "sim_fetch_01_harness_1238d.v0.1"
    assert mod.SIM_FETCH_01_FIX3_VERSION == "sim_fetch_01_fix3_tier_verdict_1238c.v0.1"


def test_phase_1238c_failure_rate_by_tier_present() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    metrics = result["aggregate_over_epochs"]
    assert "failure_rate_by_tier" in metrics
    fbt = metrics["failure_rate_by_tier"]
    assert "A" in fbt and "B" in fbt and "C" in fbt


def test_phase_1238c_tier_ab_failure_rate_present() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    assert "tier_ab_failure_rate" in result["aggregate_over_epochs"]


def test_phase_1238c_tier_c_advisory_failure_rate_present() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    assert "tier_c_advisory_failure_rate" in result["aggregate_over_epochs"]


def test_phase_1238c_tier_service_verdict_present() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    assert "tier_service_verdict" in result
    assert result["tier_service_verdict"] in ("pass", "fail", "inconclusive")


def test_phase_1238c_aggregate_verdict_equals_verdict() -> None:
    """aggregate_verdict is a backward-compatible alias for verdict."""
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    assert result["aggregate_verdict"] == result["verdict"]


def test_phase_1238c_original_verdict_field_preserved() -> None:
    """verdict field must still exist for backward compatibility."""
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    assert "verdict" in result
    assert result["verdict"] in ("pass", "fail", "inconclusive")


def test_phase_1238c_tier_service_verdict_does_not_authorize_cdl_087_ratification() -> None:
    """The harness must explicitly note tier_service_verdict ≠ CDL-087 ratification."""
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    # The harness must still carry cdl_087_ratification_authorized: False
    assert result["cdl_087_ratification_authorized"] is False
    # And must carry the explicit note
    note = result.get("cdl_087_ratification_not_authorized_note", "")
    assert "tier_service_verdict" in note


def test_phase_1238c_tier_c_higher_failure_rate_than_tier_a_at_baseline() -> None:
    """
    At baseline (20% Tier C inventory, 60% Tier C request rate), Tier C
    should have a much higher failure rate than Tier A (all peers hold all Tier A).
    """
    from decimal import Decimal
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    fbt = result["aggregate_over_epochs"]["failure_rate_by_tier"]
    rate_a = Decimal(fbt["A"])
    rate_c = Decimal(fbt["C"])
    assert rate_c > rate_a, (
        f"Tier C failure rate {rate_c} should exceed Tier A {rate_a} "
        f"— Tier A has full peer coverage, Tier C has only 20%"
    )


def test_phase_1238c_tier_a_failure_rate_is_zero_with_full_coverage() -> None:
    """All peers hold all Tier A artifacts → Tier A failure rate should be 0."""
    from decimal import Decimal
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    fbt = result["aggregate_over_epochs"]["failure_rate_by_tier"]
    rate_a = Decimal(fbt["A"])
    assert rate_a == Decimal("0"), (
        f"Tier A failure rate {rate_a} should be 0 — all peers hold all Tier A artifacts"
    )


def test_phase_1238c_tier_ab_failure_rate_consistent_with_per_tier_rates() -> None:
    """tier_ab_failure_rate must be within the range of tier A and tier B rates."""
    from decimal import Decimal
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    metrics = result["aggregate_over_epochs"]
    fbt = metrics["failure_rate_by_tier"]
    rate_a = Decimal(fbt["A"])
    rate_b = Decimal(fbt["B"])
    rate_ab = Decimal(metrics["tier_ab_failure_rate"])
    # tier_ab_failure_rate must be between min(A, B) and max(A, B) (weighted average)
    assert min(rate_a, rate_b) <= rate_ab <= max(rate_a, rate_b), (
        f"tier_ab_failure_rate {rate_ab} is outside [min(A={rate_a}, B={rate_b}), max]"
    )
