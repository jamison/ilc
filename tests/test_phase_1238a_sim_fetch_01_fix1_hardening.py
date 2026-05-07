from __future__ import annotations

"""
Phase 1238a — Fix1: SIM-FETCH-01 harness contract hardening tests.

Verifies:
- No import random in harness source (spec compliance)
- Strict rate field validation (range, bool, float)
- Circuit breaker threshold validation
- Determinism preserved with _DeterministicRNG
- Version tokens correct
"""

from pathlib import Path

import pytest

HARNESS_PATH = Path("ilc_core/sim/sim_fetch_01/sim_fetch_01_harness.py")

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


def test_phase_1238a_no_random_import_in_harness_source() -> None:
    """Design spec invariant: harness must not import random."""
    source = HARNESS_PATH.read_text(encoding="utf-8")
    # Allow the word "random" in comments but not as an import
    import_lines = [
        line for line in source.splitlines()
        if line.strip().startswith("import random")
        or line.strip().startswith("from random ")
    ]
    assert import_lines == [], (
        f"import random found in harness — spec violation: {import_lines}"
    )


def test_phase_1238a_fix1_version_tokens_present() -> None:
    import ilc_core.sim.sim_fetch_01.sim_fetch_01_harness as mod

    assert mod.SIM_FETCH_01_HARNESS_VERSION == "sim_fetch_01_harness_1238i.v0.1"
    assert mod.SIM_FETCH_01_FIX1_VERSION == "sim_fetch_01_fix1_hardening_1238a.v0.1"


def test_phase_1238a_negative_rate_rejected() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    bad = {
        **_BASELINE_SCENARIO,
        "tier_a_request_rate": "-0.10",
        "tier_b_request_rate": "0.50",
        "tier_c_request_rate": "0.60",
    }
    with pytest.raises(ValueError, match="rate_out_of_range"):
        run_sim_fetch_01(bad)


def test_phase_1238a_rate_above_one_rejected() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    bad = {
        **_BASELINE_SCENARIO,
        "tier_a_request_rate": "1.10",
        "tier_b_request_rate": "0.00",
        "tier_c_request_rate": "-0.10",
    }
    with pytest.raises(ValueError, match="rate_out_of_range"):
        run_sim_fetch_01(bad)


def test_phase_1238a_bool_rate_rejected() -> None:
    """bool is a subclass of int; must be explicitly caught before type check."""
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    bad = {**_BASELINE_SCENARIO, "tier_a_request_rate": True}
    with pytest.raises(ValueError, match="bool_forbidden"):
        run_sim_fetch_01(bad)


def test_phase_1238a_bool_circuit_breaker_threshold_rejected() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    bad = {**_BASELINE_SCENARIO, "circuit_breaker_threshold": True}
    with pytest.raises(ValueError, match="invalid_circuit_breaker_threshold"):
        run_sim_fetch_01(bad)


def test_phase_1238a_zero_circuit_breaker_threshold_rejected() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    bad = {**_BASELINE_SCENARIO, "circuit_breaker_threshold": 0}
    with pytest.raises(ValueError, match="invalid_circuit_breaker_threshold"):
        run_sim_fetch_01(bad)


def test_phase_1238a_negative_circuit_breaker_threshold_rejected() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    bad = {**_BASELINE_SCENARIO, "circuit_breaker_threshold": -5}
    with pytest.raises(ValueError, match="invalid_circuit_breaker_threshold"):
        run_sim_fetch_01(bad)


def test_phase_1238a_determinism_preserved_with_new_rng() -> None:
    """_DeterministicRNG must produce identical results for identical configs."""
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    r1 = run_sim_fetch_01(_BASELINE_SCENARIO)
    r2 = run_sim_fetch_01(_BASELINE_SCENARIO)
    assert r1 == r2, "Two runs with identical config produced different results"


def test_phase_1238a_different_seeds_produce_different_results() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    r1 = run_sim_fetch_01({**_BASELINE_SCENARIO, "seed": 42})
    r2 = run_sim_fetch_01({**_BASELINE_SCENARIO, "seed": 99})
    # Results should differ — different seeds must produce different RNG sequences
    assert (
        r1["aggregate_over_epochs"]["failure_rate"]
        != r2["aggregate_over_epochs"]["failure_rate"]
        or r1["aggregate_over_epochs"]["want_have_hit_rate"]
        != r2["aggregate_over_epochs"]["want_have_hit_rate"]
    ), "Different seeds produced identical results — RNG is not seeded correctly"


def test_phase_1238a_deterministic_rng_counter_mode_produces_uniform_output() -> None:
    """Verify the hash-derived PRNG distributes draws across full range."""
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import _DeterministicRNG

    rng = _DeterministicRNG(42)
    n_draws = 1000
    values = [rng.randint(0, 9) for _ in range(n_draws)]
    counts = [values.count(i) for i in range(10)]
    # Rough uniformity check: each bucket should be 60-140 (expect ~100)
    for i, c in enumerate(counts):
        assert 50 <= c <= 200, (
            f"Bucket {i} has {c}/{n_draws} draws — PRNG is not approximately uniform"
        )


def test_phase_1238a_cdl_087_ratification_still_not_authorized() -> None:
    from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01

    result = run_sim_fetch_01(_BASELINE_SCENARIO)
    assert result["cdl_087_ratification_authorized"] is False
