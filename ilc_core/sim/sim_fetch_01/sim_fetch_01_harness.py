from __future__ import annotations

# SIM-FETCH-01: Canonical Fetch Distribution Simulation Harness
#
# Phase 1238j — Window 1233-1240 (Fix10: robustness evidence suite)
# Governing authority: docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md
#
# CDL-087 ratification is NOT authorized by this harness.
#
# This module lives in ilc_core/sim/ (not a sensitive taboo scan root).
# It uses _DeterministicRNG (SHA-256 counter-mode) for reproducible simulation.
# This PRNG must NOT be imported or used in any production protocol code path.
# Production code must use secrets.SystemRandom() for stochastic needs.

import hashlib
import itertools
import json
from bisect import bisect_left
from collections import OrderedDict
from decimal import Decimal, InvalidOperation
from typing import Any

SIM_FETCH_01_HARNESS_VERSION = "sim_fetch_01_harness_1238j.v0.1"
SIM_FETCH_01_FIX1_VERSION = "sim_fetch_01_fix1_hardening_1238a.v0.1"
SIM_FETCH_01_FIX2_VERSION = "sim_fetch_01_fix2_request_model_1238b.v0.1"
SIM_FETCH_01_FIX3_VERSION = "sim_fetch_01_fix3_tier_verdict_1238c.v0.1"
SIM_FETCH_01_FIX4_VERSION = "sim_fetch_01_fix4_routed_holder_model_1238d.v0.1"
SIM_FETCH_01_FIX5_VERSION = "sim_fetch_01_fix5_routed_multihop_retry_1238e.v0.1"
SIM_FETCH_01_FIX6_VERSION = "sim_fetch_01_fix6_adaptive_heat_replication_1238f.v0.1"
SIM_FETCH_01_FIX7_VERSION = "sim_fetch_01_fix7_cdl_078_credit_bridge_1238g.v0.1"
SIM_FETCH_01_FIX8_VERSION = "sim_fetch_01_fix8_werner_topology_overlay_1238h.v0.1"
SIM_FETCH_01_FIX9_VERSION = "sim_fetch_01_fix9_cdl_087_evidence_matrix_1238i.v0.1"
SIM_FETCH_01_FIX10_VERSION = "sim_fetch_01_fix10_robustness_suite_1238j.v0.1"
CDL_087_DEPENDENCY = "cdl_087_prelock_committed_phase_1228"

_TIER_A = "A"
_TIER_B = "B"
_TIER_C = "C"
_TIERS = (_TIER_A, _TIER_B, _TIER_C)

# Peer role constants
_PEER_ROLE_ANCHOR = "anchor"        # Full Tier A holder; primary Tier B hot-mirror candidate
_PEER_ROLE_HOT_MIRROR = "hot_mirror"    # Elevated Tier B inventory fraction
_PEER_ROLE_ARCHIVE_SHARD = "archive_shard"  # Elevated Tier C inventory fraction
_PEER_ROLE_GENERAL = "general"       # Standard inventory fractions

_DEFAULT_MAX_REQUESTS_PER_EPOCH = 500
_DEFAULT_MAX_SWEEP_SCENARIOS = 64
_DEFAULT_MAX_ROBUSTNESS_PROFILES = 16
_DEFAULT_MAX_ROBUSTNESS_SCENARIOS = 128
_DEFAULT_EVIDENCE_MATRIX_MAX_BYTES = 5_000_000

# Synthetic byte units per served artifact, by tier (CDL-087 §5 / design spec §5)
_BYTES_PER_TIER = {
    _TIER_A: Decimal("1"),
    _TIER_B: Decimal("1") / Decimal("2"),
    _TIER_C: Decimal("1") / Decimal("10"),
}

# Default inventory fractions (configurable since Fix1)
_DEFAULT_TIER_B_PEER_INVENTORY_FRACTION = 6  # 60%
_DEFAULT_TIER_C_PEER_INVENTORY_FRACTION = 2  # 20%

# Default Zipf exponents
_DEFAULT_ZIPF_EXPONENT_TIER_A = Decimal("1.0")
_DEFAULT_ZIPF_EXPONENT_TIER_B = Decimal("0.5")

# XOR mask for deriving the routed-model RNG seed from the main seed.
# The routed model uses a separate _DeterministicRNG so that staleness draws
# do not alter the main RNG's counter sequence and thus do not change the
# random-model outcomes when the two models are run in parallel.
_RNG_ROUTED_SEED_XOR = 0x5A4D3B2C1E0F9871
_RNG_RETRY_SEED_XOR = 0xC7D8E9F001234567
_RNG_REPLICATION_SEED_XOR = 0x9E3779B97F4A7C15


class _DeterministicRNG:
    """
    Deterministic hash-derived PRNG for SIM-FETCH-01 simulation only.

    Uses SHA-256 in counter mode: each draw is sha256(seed_bytes || counter_bytes).
    The counter increments monotonically across all draws within one run.

    Contract: identical seed + draw sequence → identical output.
    Must NOT be used in production protocol code (use secrets.SystemRandom).
    """

    def __init__(self, seed: int) -> None:
        self._seed_bytes = (seed & 0xFFFFFFFFFFFFFFFF).to_bytes(8, byteorder="big")
        self._counter = 0

    def _next_uint64(self) -> int:
        counter_bytes = self._counter.to_bytes(8, byteorder="big")
        self._counter += 1
        digest = hashlib.sha256(self._seed_bytes + counter_bytes).digest()
        return int.from_bytes(digest[:8], byteorder="big")

    def randint(self, lo: int, hi: int) -> int:
        """Return deterministic uniform integer in [lo, hi] inclusive."""
        span = hi - lo + 1
        return lo + (self._next_uint64() % span)

    def sample(self, population: range, k: int) -> list:
        """Return k deterministically chosen unique elements via partial Fisher-Yates."""
        items = list(population)
        n = len(items)
        for i in range(k):
            j = i + (self._next_uint64() % (n - i))
            items[i], items[j] = items[j], items[i]
        return items[:k]

    def fraction(self) -> Decimal:
        """Return deterministic uniform Decimal in [0, 1)."""
        val = self._next_uint64()
        return Decimal(val) / Decimal("18446744073709551616")

    def poisson_count(self, n_agents: int, avg_per_agent: Decimal) -> int:
        """
        Poisson-like total request count via per-agent Bernoulli approximation.
        Expected total = n_agents * avg_per_agent. Integer avg → deterministic.
        """
        base = int(avg_per_agent // Decimal("1"))
        frac_part = avg_per_agent - Decimal(base)
        count = n_agents * base
        if frac_part > Decimal("0"):
            for _ in range(n_agents):
                if self.fraction() < frac_part:
                    count += 1
        return count


def _build_zipf_cdf(n: int, exponent: Decimal) -> list[Decimal]:
    """Build cumulative Zipf(n, exponent) distribution. Last entry is exactly 1."""
    weights = [Decimal(1) / (Decimal(k) ** exponent) for k in range(1, n + 1)]
    total = sum(weights)
    cdf: list[Decimal] = []
    running = Decimal("0")
    for w in weights:
        running += w / total
        cdf.append(running)
    cdf[-1] = Decimal("1")
    return cdf


def _zipf_draw(rng: _DeterministicRNG, cdf: list[Decimal]) -> int:
    """Draw 0-indexed artifact ID from pre-built Zipf CDF (rank 1 → index 0)."""
    return bisect_left(cdf, rng.fraction())


def _build_holder_directory(
    peer_inventories: list[dict[str, set[int]]],
    tier_counts: dict[str, int],
    n_peers: int,
) -> dict[str, dict[int, frozenset[int]]]:
    """
    Build artifact → set-of-holder-peers index for each tier.

    This is the WANT-HAVE directory. An artifact with an empty holder set is
    unreachable under the routed model (no peer holds it at all).
    """
    directory: dict[str, dict[int, frozenset[int]]] = {}
    for tier in _TIERS:
        tier_dir: dict[int, frozenset[int]] = {}
        for art_id in range(tier_counts[tier]):
            holders = frozenset(
                p for p in range(n_peers) if art_id in peer_inventories[p][tier]
            )
            tier_dir[art_id] = holders
        directory[tier] = tier_dir
    return directory


def _holder_count_stats(
    holder_directory: dict[str, dict[int, frozenset[int]]], tier: str
) -> dict[str, Any]:
    """Summary statistics on holder counts for a tier: min/mean/max."""
    counts = [len(v) for v in holder_directory[tier].values()]
    if not counts:
        return {"min": 0, "mean": "0", "max": 0, "zero_holder_count": 0}
    return {
        "min": min(counts),
        "mean": str((Decimal(sum(counts)) / Decimal(len(counts))).quantize(Decimal("0.000001"))),
        "max": max(counts),
        "zero_holder_count": counts.count(0),
    }


def _holder_mean(
    holder_directory: dict[str, dict[int, frozenset[int]]], tier: str
) -> str:
    """Return mean holder count for a tier as a canonical Decimal string."""
    return _holder_count_stats(holder_directory, tier)["mean"]


def _compute_top_quartile_concentration(req_counts: dict[int, int]) -> str:
    """Fraction of total requests going to top 25% of artifacts (popularity measure)."""
    if not req_counts:
        return "0"
    sorted_counts = sorted(req_counts.values(), reverse=True)
    total = sum(sorted_counts)
    if total == 0:
        return "0"
    top_n = max(1, len(sorted_counts) // 4)
    top_total = sum(sorted_counts[:top_n])
    return str((Decimal(top_total) / Decimal(total)).quantize(Decimal("0.000001")))


class _LRUCache:
    """Bounded LRU cache for simulated artifact serving."""

    def __init__(self, capacity: int) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 1:
            raise ValueError("sim_fetch_01_cache_capacity_must_be_positive_int")
        self._capacity = capacity
        self._data: OrderedDict[tuple[str, int], None] = OrderedDict()

    def has(self, key: tuple[str, int]) -> bool:
        if key in self._data:
            self._data.move_to_end(key)
            return True
        return False

    def put(self, key: tuple[str, int]) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        else:
            if len(self._data) >= self._capacity:
                self._data.popitem(last=False)
            self._data[key] = None


def _reject_non_finite(d: Decimal, name: str) -> None:
    if not d.is_finite():
        raise ValueError(f"sim_fetch_01_non_finite_decimal_{name}")


def _to_rate_decimal(val: Any, name: str) -> Decimal:
    """Strict Decimal conversion for rate fields: rejects float, bool, out-of-range."""
    if isinstance(val, bool):
        raise ValueError(f"sim_fetch_01_bool_forbidden_in_rate_field_{name}")
    if isinstance(val, float):
        raise ValueError(f"sim_fetch_01_float_forbidden_in_economic_field_{name}")
    try:
        d = Decimal(str(val))
    except InvalidOperation:
        raise ValueError(f"sim_fetch_01_invalid_decimal_{name}")
    _reject_non_finite(d, name)
    if d < Decimal("0") or d > Decimal("1"):
        raise ValueError(f"sim_fetch_01_rate_out_of_range_{name}")
    return d


def _to_pos_decimal(val: Any, name: str, lo: Decimal, hi: Decimal) -> Decimal:
    """Strict Decimal conversion for positive parameter fields."""
    if isinstance(val, bool):
        raise ValueError(f"sim_fetch_01_bool_forbidden_in_field_{name}")
    if isinstance(val, float):
        raise ValueError(f"sim_fetch_01_float_forbidden_in_economic_field_{name}")
    try:
        d = Decimal(str(val))
    except InvalidOperation:
        raise ValueError(f"sim_fetch_01_invalid_decimal_{name}")
    _reject_non_finite(d, name)
    if d < lo or d > hi:
        raise ValueError(f"sim_fetch_01_value_out_of_range_{name}")
    return d


def _safe_ratio(num: int, denom: int) -> str:
    if denom == 0:
        return "0"
    return str((Decimal(num) / Decimal(denom)).quantize(Decimal("0.000001")))


def _quantized_decimal_str(value: Decimal) -> str:
    """Canonical simulation Decimal string for non-ratio observability metrics."""
    return str(value.quantize(Decimal("0.000001")))


def _compute_verdict(
    cache_rate_a: Decimal,
    failure_rate: Decimal,
    tier_a_fraction: Decimal,
    cb_fraction: Decimal,
    spp: dict[str, int],
    total_requests: int,
) -> str:
    """
    SIM-FETCH-01 aggregate verdict (design spec §7).
    Based on single-hop random-model metrics.
    CDL-087 ratification not authorized regardless of verdict.
    """
    if total_requests < 1000:
        return "inconclusive"
    if not cache_rate_a.is_finite() or not failure_rate.is_finite():
        return "inconclusive"
    if not spp or all(v == 0 for v in spp.values()):
        return "inconclusive"
    if cache_rate_a < Decimal("0.50"):
        return "fail"
    if failure_rate > Decimal("0.20"):
        return "fail"
    if cb_fraction > Decimal("0.20"):
        return "fail"
    if (
        cache_rate_a >= Decimal("0.70")
        and failure_rate <= Decimal("0.10")
        and tier_a_fraction <= Decimal("0.20")
        and cb_fraction <= Decimal("0.05")
    ):
        pressures = list(spp.values())
        max_p = Decimal(max(pressures))
        mean_p = Decimal(sum(pressures)) / Decimal(len(pressures))
        if mean_p > 0 and max_p / mean_p <= Decimal("3.0"):
            return "pass"
    return "inconclusive"


def _compute_tier_service_verdict(
    cache_rate_a: Decimal,
    tier_ab_failure_rate: Decimal,
    cb_fraction: Decimal,
    spp: dict[str, int],
    total_tier_ab_requests: int,
) -> str:
    """
    Tier A+B service quality verdict — INFORMATIONAL ONLY.

    CDL-087 §3 states Tier C has no infrastructure-grade service obligation.
    Can be applied to both the single-hop random model and the routed holder model;
    the metric inputs differ between the two.

    NOT a CDL-087 ratification verdict. CDL-087 ratification is not authorized by this harness.
    """
    if total_tier_ab_requests < 100:
        return "inconclusive"
    if not cache_rate_a.is_finite() or not tier_ab_failure_rate.is_finite():
        return "inconclusive"
    if cache_rate_a < Decimal("0.50"):
        return "fail"
    if tier_ab_failure_rate > Decimal("0.20"):
        return "fail"
    if cb_fraction > Decimal("0.20"):
        return "fail"
    if (
        cache_rate_a >= Decimal("0.70")
        and tier_ab_failure_rate <= Decimal("0.10")
        and cb_fraction <= Decimal("0.05")
    ):
        pressures = list(spp.values())
        if pressures:
            max_p = Decimal(max(pressures))
            mean_p = Decimal(sum(pressures)) / Decimal(len(pressures))
            if mean_p > 0 and max_p / mean_p <= Decimal("3.0"):
                return "pass"
    return "inconclusive"


def _reject_float_tree(value: Any, path: str) -> None:
    """Reject float anywhere in a sweep config before scenario execution."""
    if isinstance(value, float):
        raise ValueError(f"sim_fetch_01_float_forbidden_in_sweep_field_{path}")
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                raise ValueError("sim_fetch_01_sweep_dict_keys_must_be_strings")
            _reject_float_tree(v, f"{path}.{k}")
    elif isinstance(value, (list, tuple)):
        for idx, item in enumerate(value):
            _reject_float_tree(item, f"{path}[{idx}]")


def _cb_fraction_from_metrics(metrics: dict[str, Any]) -> Decimal:
    fetch_by_tier = metrics["fetch_requests_by_tier"]
    total = (
        int(fetch_by_tier[_TIER_A])
        + int(fetch_by_tier[_TIER_B])
        + int(fetch_by_tier[_TIER_C])
        + int(metrics["want_block_error_429"])
    )
    if total == 0:
        return Decimal("0")
    return Decimal(int(metrics["want_block_error_429"])) / Decimal(total)


def _evaluate_cdl_087_candidate(result: dict[str, Any]) -> dict[str, Any]:
    """
    Fixed evaluator for Phase 1238 Fix9 AutoResearch sweeps.

    This identifies candidate operating envelopes for later governance review.
    It never authorizes CDL-087 ratification.
    """
    metrics = result["aggregate_over_epochs"]
    cache_rate_a = Decimal(metrics["cache_hit_rate_tier_a"])
    routed_tier_a_failure = Decimal(metrics["routed_failure_rate_by_tier"][_TIER_A])
    routed_tier_ab_failure = Decimal(metrics["routed_effective_tier_ab_failure_rate"])
    routed_holder_hit_rate = Decimal(metrics["routed_holder_hit_rate"])
    cb_fraction = _cb_fraction_from_metrics(metrics)
    routed_cb_fraction = Decimal(metrics["routed_circuit_breaker_fraction"])

    fail_reasons: list[str] = []
    review_reasons: list[str] = []

    if cache_rate_a < Decimal("0.50"):
        fail_reasons.append("tier_a_cache_hit_rate_below_block_floor")
    elif cache_rate_a < Decimal("0.70"):
        review_reasons.append("tier_a_cache_hit_rate_below_support_floor")
    if routed_tier_a_failure > Decimal("0.02"):
        fail_reasons.append("routed_tier_a_failure_above_block_floor")
    if routed_tier_ab_failure > Decimal("0.20"):
        fail_reasons.append("routed_tier_ab_failure_above_block_floor")
    elif routed_tier_ab_failure > Decimal("0.10"):
        review_reasons.append("routed_tier_ab_failure_above_support_floor")
    if routed_holder_hit_rate < Decimal("0.80"):
        review_reasons.append("routed_holder_hit_rate_below_support_floor")
    if cb_fraction > Decimal("0.20"):
        fail_reasons.append("circuit_breaker_fraction_above_block_floor")
    elif cb_fraction > Decimal("0.05"):
        review_reasons.append("circuit_breaker_fraction_above_support_floor")
    if routed_cb_fraction > Decimal("0.20"):
        fail_reasons.append("routed_circuit_breaker_fraction_above_block_floor")
    elif routed_cb_fraction > Decimal("0.05"):
        review_reasons.append("routed_circuit_breaker_fraction_above_support_floor")
    if metrics["serve_credit_artifact_only_crediting_allowed"]:
        fail_reasons.append("artifact_only_crediting_allowed")
    if metrics["serve_credit_attribution_model"] != "serving_peer_operator_instance":
        fail_reasons.append("serve_credit_attribution_model_not_operator_instance")
    if metrics["werner_ecu_pressure_mint_authorized"]:
        fail_reasons.append("werner_ecu_pressure_mint_authorized")
    if metrics["werner_ilc_settlement_authorized"]:
        fail_reasons.append("werner_ilc_settlement_authorized")

    if fail_reasons:
        verdict = "fail"
    elif review_reasons:
        verdict = "needs_review"
    else:
        verdict = "pass"

    return {
        "verdict": verdict,
        "fail_reasons": fail_reasons,
        "review_reasons": review_reasons,
        "thresholds": {
            "tier_a_cache_hit_rate_support_floor": "0.70",
            "tier_a_cache_hit_rate_block_floor": "0.50",
            "routed_tier_a_failure_block_ceiling": "0.02",
            "routed_tier_ab_failure_support_ceiling": "0.10",
            "routed_tier_ab_failure_block_ceiling": "0.20",
            "routed_holder_hit_rate_support_floor": "0.80",
            "circuit_breaker_fraction_support_ceiling": "0.05",
            "circuit_breaker_fraction_block_ceiling": "0.20",
        },
    }


def _evidence_key_metrics(result: dict[str, Any]) -> dict[str, Any]:
    metrics = result["aggregate_over_epochs"]
    return {
        "cache_hit_rate_tier_a": metrics["cache_hit_rate_tier_a"],
        "circuit_breaker_fraction": _quantized_decimal_str(_cb_fraction_from_metrics(metrics)),
        "routed_avg_hops_per_successful_request": metrics["routed_avg_hops_per_successful_request"],
        "routed_circuit_breaker_fraction": metrics["routed_circuit_breaker_fraction"],
        "routed_effective_tier_ab_failure_rate": metrics["routed_effective_tier_ab_failure_rate"],
        "routed_failure_rate_by_tier": metrics["routed_failure_rate_by_tier"],
        "routed_holder_hit_rate": metrics["routed_holder_hit_rate"],
        "routed_rescue_count": metrics["routed_rescue_count"],
        "routed_retry_exhausted_count": metrics["routed_retry_exhausted_count"],
        "routed_serve_events_credited_cdl_078": metrics["routed_serve_events_credited_cdl_078"],
        "routed_tier_service_verdict": metrics["routed_tier_service_verdict"],
        "single_hop_random_tier_ab_failure_rate": metrics["single_hop_random_tier_ab_failure_rate"],
        "tier_c_advisory_routed_failure_rate": metrics["routed_failure_rate_by_tier"][_TIER_C],
        "adaptive_replication_total_events": metrics["adaptive_replication_total_events"],
        "werner_topology_recommendation_by_tier": metrics["werner_topology_recommendation_by_tier"],
        "werner_ecu_pressure_signal_by_tier": metrics["werner_ecu_pressure_signal_by_tier"],
        "werner_ecu_pressure_mint_authorized": metrics["werner_ecu_pressure_mint_authorized"],
        "werner_ilc_settlement_authorized": metrics["werner_ilc_settlement_authorized"],
    }


def _rank_evidence_row(row: dict[str, Any]) -> tuple[int, Decimal, Decimal, Decimal, str]:
    verdict_rank = {"pass": 0, "needs_review": 1, "fail": 2}[row["evaluator"]["verdict"]]
    metrics = row["key_metrics"]
    return (
        verdict_rank,
        Decimal(metrics["routed_effective_tier_ab_failure_rate"]),
        Decimal(metrics["tier_c_advisory_routed_failure_rate"]),
        Decimal(metrics["routed_avg_hops_per_successful_request"]),
        row["scenario_id"],
    )


def run_sim_fetch_01_cdl_087_evidence_sweep(sweep_config: dict) -> dict:
    """
    Run the Phase 1238 Fix9 AutoResearch evidence sweep for CDL-087.

    The sweep mutates declared scenario parameters, applies a fixed evaluator,
    and returns a bounded matrix. It does not embed full per-scenario traces.
    CDL-087 ratification is NOT authorized by this sweep.
    """
    if not isinstance(sweep_config, dict):
        raise ValueError("sim_fetch_01_sweep_config_must_be_dict")
    _reject_float_tree(sweep_config, "sweep_config")

    base_scenario = sweep_config.get("base_scenario")
    if not isinstance(base_scenario, dict):
        raise ValueError("sim_fetch_01_sweep_base_scenario_must_be_dict")

    grid = sweep_config.get("grid")
    if not isinstance(grid, dict) or not grid:
        raise ValueError("sim_fetch_01_sweep_grid_must_be_non_empty_dict")

    max_scenarios = sweep_config.get("max_sweep_scenarios", _DEFAULT_MAX_SWEEP_SCENARIOS)
    if isinstance(max_scenarios, bool) or not isinstance(max_scenarios, int) or max_scenarios < 1:
        raise ValueError("sim_fetch_01_invalid_max_sweep_scenarios")

    keys = sorted(grid.keys())
    values_by_key: list[list[Any]] = []
    scenario_count = 1
    for key in keys:
        values = grid[key]
        if not isinstance(key, str):
            raise ValueError("sim_fetch_01_sweep_grid_keys_must_be_strings")
        if not isinstance(values, (list, tuple)) or not values:
            raise ValueError(f"sim_fetch_01_sweep_grid_values_invalid_{key}")
        values_list = list(values)
        values_by_key.append(values_list)
        scenario_count *= len(values_list)
        if scenario_count > max_scenarios:
            raise ValueError("sim_fetch_01_sweep_scenario_count_exceeded")

    rows: list[dict[str, Any]] = []
    verdict_counts = {"pass": 0, "needs_review": 0, "fail": 0}

    for idx, values in enumerate(itertools.product(*values_by_key)):
        params = dict(zip(keys, values))
        scenario = dict(base_scenario)
        scenario.update(params)
        result = run_sim_fetch_01(scenario)
        evaluator = _evaluate_cdl_087_candidate(result)
        verdict_counts[evaluator["verdict"]] += 1
        rows.append({
            "scenario_id": f"sweep_{idx:04d}",
            "params": params,
            "scenario": result["scenario"],
            "evaluator": evaluator,
            "key_metrics": _evidence_key_metrics(result),
        })

    recommended = [
        {
            "scenario_id": row["scenario_id"],
            "params": row["params"],
            "verdict": row["evaluator"]["verdict"],
            "key_metrics": row["key_metrics"],
        }
        for row in sorted(rows, key=_rank_evidence_row)[:5]
    ]

    if verdict_counts["pass"] > 0:
        recommendation = "candidate_envelope_identified_for_governance_review"
    elif verdict_counts["needs_review"] > 0:
        recommendation = "additional_review_required_before_cdl_087"
    else:
        recommendation = "no_candidate_envelope_identified"

    return {
        "sim": "SIM-FETCH-01",
        "sweep_version": SIM_FETCH_01_FIX9_VERSION,
        "harness_version": SIM_FETCH_01_HARNESS_VERSION,
        "methodology": "karpathy_auto_research_fixed_evaluator_parameter_sweep",
        "cdl_087_dependency": CDL_087_DEPENDENCY,
        "cdl_087_ratification_authorized": False,
        "cdl_087_ratification_recommendation": recommendation,
        "non_authorization_note": (
            "This evidence matrix identifies candidate operating envelopes only; "
            "it does not ratify CDL-087, mint ECU, settle ILC, mutate production "
            "runtime, or authorize public network exposure."
        ),
        "grid_keys": keys,
        "scenario_count": scenario_count,
        "verdict_counts": verdict_counts,
        "recommended_scenarios": recommended,
        "rows": rows,
    }


def _reason_counts(rows: list[dict[str, Any]], reason_key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        for reason in row["evaluator"][reason_key]:
            counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items()))


def _robustness_acceptance(rule: str, verdict_counts: dict[str, int], total: int) -> bool:
    if rule == "all_pass":
        return verdict_counts["pass"] == total
    if rule == "any_pass":
        return verdict_counts["pass"] > 0
    if rule == "all_fail":
        return verdict_counts["fail"] == total
    if rule == "any_fail":
        return verdict_counts["fail"] > 0
    if rule == "no_fail":
        return verdict_counts["fail"] == 0
    if rule == "mixed_allowed":
        return True
    raise ValueError("sim_fetch_01_invalid_robustness_acceptance_rule")


def _profile_metric_extrema(rows: list[dict[str, Any]]) -> dict[str, str]:
    tier_ab = [
        Decimal(row["key_metrics"]["routed_effective_tier_ab_failure_rate"])
        for row in rows
    ]
    tier_c = [
        Decimal(row["key_metrics"]["tier_c_advisory_routed_failure_rate"])
        for row in rows
    ]
    holder_hit = [Decimal(row["key_metrics"]["routed_holder_hit_rate"]) for row in rows]
    cb_fraction = [Decimal(row["key_metrics"]["circuit_breaker_fraction"]) for row in rows]
    return {
        "min_routed_effective_tier_ab_failure_rate": _quantized_decimal_str(min(tier_ab)),
        "max_routed_effective_tier_ab_failure_rate": _quantized_decimal_str(max(tier_ab)),
        "max_tier_c_advisory_routed_failure_rate": _quantized_decimal_str(max(tier_c)),
        "min_routed_holder_hit_rate": _quantized_decimal_str(min(holder_hit)),
        "max_circuit_breaker_fraction": _quantized_decimal_str(max(cb_fraction)),
    }


def run_sim_fetch_01_cdl_087_robustness_suite(robustness_config: dict) -> dict:
    """
    Run named adversarial/robustness profiles over the Fix9 evidence sweep.

    Each profile declares an acceptance rule. This lets the suite validate both
    positive candidate envelopes and deliberate negative controls. For example,
    a one-hop fully stale directory profile should fail, while a two-hop routed
    retry profile should recover.

    CDL-087 ratification is NOT authorized by this suite.
    """
    if not isinstance(robustness_config, dict):
        raise ValueError("sim_fetch_01_robustness_config_must_be_dict")
    _reject_float_tree(robustness_config, "robustness_config")

    base_scenario = robustness_config.get("base_scenario")
    if not isinstance(base_scenario, dict):
        raise ValueError("sim_fetch_01_robustness_base_scenario_must_be_dict")

    profiles = robustness_config.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("sim_fetch_01_robustness_profiles_must_be_non_empty_list")

    max_profiles = robustness_config.get(
        "max_robustness_profiles",
        _DEFAULT_MAX_ROBUSTNESS_PROFILES,
    )
    if isinstance(max_profiles, bool) or not isinstance(max_profiles, int) or max_profiles < 1:
        raise ValueError("sim_fetch_01_invalid_max_robustness_profiles")
    if len(profiles) > max_profiles:
        raise ValueError("sim_fetch_01_robustness_profile_count_exceeded")

    max_total_scenarios = robustness_config.get(
        "max_total_scenarios",
        _DEFAULT_MAX_ROBUSTNESS_SCENARIOS,
    )
    if (
        isinstance(max_total_scenarios, bool)
        or not isinstance(max_total_scenarios, int)
        or max_total_scenarios < 1
    ):
        raise ValueError("sim_fetch_01_invalid_max_robustness_total_scenarios")

    profile_summaries: list[dict[str, Any]] = []
    total_scenarios = 0
    accepted_count = 0

    for profile in profiles:
        if not isinstance(profile, dict):
            raise ValueError("sim_fetch_01_robustness_profile_must_be_dict")
        profile_id = profile.get("profile_id")
        if not isinstance(profile_id, str) or not profile_id:
            raise ValueError("sim_fetch_01_invalid_robustness_profile_id")
        description = profile.get("description", "")
        if not isinstance(description, str):
            raise ValueError("sim_fetch_01_invalid_robustness_profile_description")

        acceptance_rule = profile.get("acceptance_rule", "any_pass")
        if not isinstance(acceptance_rule, str):
            raise ValueError("sim_fetch_01_invalid_robustness_acceptance_rule")

        overrides = profile.get("scenario_overrides", {})
        if not isinstance(overrides, dict):
            raise ValueError("sim_fetch_01_robustness_overrides_must_be_dict")
        grid = profile.get("grid")
        if not isinstance(grid, dict) or not grid:
            raise ValueError("sim_fetch_01_robustness_profile_grid_must_be_dict")

        max_profile_scenarios = profile.get(
            "max_sweep_scenarios",
            _DEFAULT_MAX_SWEEP_SCENARIOS,
        )
        if (
            isinstance(max_profile_scenarios, bool)
            or not isinstance(max_profile_scenarios, int)
            or max_profile_scenarios < 1
        ):
            raise ValueError("sim_fetch_01_invalid_profile_max_sweep_scenarios")

        sweep_result = run_sim_fetch_01_cdl_087_evidence_sweep({
            "base_scenario": {**base_scenario, **overrides},
            "grid": grid,
            "max_sweep_scenarios": max_profile_scenarios,
        })
        total_scenarios += int(sweep_result["scenario_count"])
        if total_scenarios > max_total_scenarios:
            raise ValueError("sim_fetch_01_robustness_total_scenario_count_exceeded")

        verdict_counts = sweep_result["verdict_counts"]
        accepted = _robustness_acceptance(
            acceptance_rule,
            verdict_counts,
            int(sweep_result["scenario_count"]),
        )
        if accepted:
            accepted_count += 1

        profile_summaries.append({
            "profile_id": profile_id,
            "description": description,
            "acceptance_rule": acceptance_rule,
            "accepted": accepted,
            "scenario_count": sweep_result["scenario_count"],
            "verdict_counts": verdict_counts,
            "evidence_recommendation": sweep_result["cdl_087_ratification_recommendation"],
            "metric_extrema": _profile_metric_extrema(sweep_result["rows"]),
            "fail_reason_counts": _reason_counts(sweep_result["rows"], "fail_reasons"),
            "review_reason_counts": _reason_counts(sweep_result["rows"], "review_reasons"),
            "representative_scenarios": sweep_result["recommended_scenarios"][:3],
        })

    overall_verdict = "pass" if accepted_count == len(profile_summaries) else "fail"
    return {
        "sim": "SIM-FETCH-01",
        "robustness_version": SIM_FETCH_01_FIX10_VERSION,
        "harness_version": SIM_FETCH_01_HARNESS_VERSION,
        "methodology": "adversarial_robustness_envelope_expansion",
        "cdl_087_dependency": CDL_087_DEPENDENCY,
        "cdl_087_ratification_authorized": False,
        "overall_robustness_verdict": overall_verdict,
        "accepted_profile_count": accepted_count,
        "profile_count": len(profile_summaries),
        "total_scenario_count": total_scenarios,
        "profiles": profile_summaries,
        "non_authorization_note": (
            "This robustness suite validates candidate and negative-control "
            "envelopes only; it does not ratify CDL-087, mint ECU, settle ILC, "
            "mutate production runtime, or authorize public network exposure."
        ),
    }


def export_sim_fetch_01_evidence_json(
    payload: dict,
    *,
    max_bytes: int = _DEFAULT_EVIDENCE_MATRIX_MAX_BYTES,
) -> str:
    """Canonical JSON export for SIM-FETCH-01 evidence artifacts."""
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
        raise ValueError("sim_fetch_01_invalid_evidence_json_max_bytes")
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(body.encode("utf-8")) > max_bytes:
        raise ValueError("sim_fetch_01_evidence_json_max_bytes_exceeded")
    return body


def run_sim_fetch_01(scenario_config: dict) -> dict:
    """
    Run SIM-FETCH-01 fetch distribution simulation.

    Returns metrics under two availability models in parallel:

    single_hop_random_*: Null model — uniform random peer selection. Worst-case
        availability; shows what happens when the requester has no routing signal.

    routed_*: Holder-directory model — requests routed to known holders of each
        artifact. Multi-hop retry can rescue a stale first hop by traversing to
        a known holder. CDL-087 evaluation should use routed_ metrics, not
        random_ metrics.

    Both models process the same tiers and artifacts per epoch; only peer selection
    differs. The routed model tracks separate holder-load circuit-breaker pressure.

    CDL-087 ratification is NOT authorized by this harness.
    """
    # --- Validate integer parameters ---
    for key in (
        "n_serving_peers", "n_epochs", "n_agents",
        "tier_a_artifact_count", "tier_b_artifact_count", "tier_c_artifact_count",
        "cache_capacity_per_peer",
    ):
        if key not in scenario_config:
            raise ValueError(f"sim_fetch_01_missing_config_{key}")
        val = scenario_config[key]
        if isinstance(val, bool) or not isinstance(val, int) or val < 1:
            raise ValueError(f"sim_fetch_01_invalid_config_{key}")

    # --- Validate rate parameters ---
    rate_a = _to_rate_decimal(scenario_config.get("tier_a_request_rate", "0"), "tier_a_request_rate")
    rate_b = _to_rate_decimal(scenario_config.get("tier_b_request_rate", "0"), "tier_b_request_rate")
    rate_c = _to_rate_decimal(scenario_config.get("tier_c_request_rate", "0"), "tier_c_request_rate")
    if rate_a + rate_b + rate_c != Decimal("1"):
        raise ValueError("sim_fetch_01_request_rates_must_sum_to_one")

    # --- Validate Zipf exponents ---
    zipf_exp_a = _to_pos_decimal(
        scenario_config.get("zipf_exponent_tier_a", str(_DEFAULT_ZIPF_EXPONENT_TIER_A)),
        "zipf_exponent_tier_a", Decimal("0.1"), Decimal("5.0"),
    )
    zipf_exp_b = _to_pos_decimal(
        scenario_config.get("zipf_exponent_tier_b", str(_DEFAULT_ZIPF_EXPONENT_TIER_B)),
        "zipf_exponent_tier_b", Decimal("0.1"), Decimal("5.0"),
    )

    # --- Validate avg requests per agent ---
    avg_per_agent = _to_pos_decimal(
        scenario_config.get("avg_requests_per_agent", "3"),
        "avg_requests_per_agent", Decimal("0.01"), Decimal("100"),
    )

    # --- Validate directory staleness rate (Fix4) ---
    directory_staleness_rate = _to_rate_decimal(
        scenario_config.get("directory_staleness_rate", "0"),
        "directory_staleness_rate",
    )

    # --- Validate multi-hop retry bound (Fix5) ---
    # Total WANT-HAVE probes per routed request. Default 1 preserves Fix4 results.
    max_retry_hops_raw = scenario_config.get("max_retry_hops", 1)
    if (
        isinstance(max_retry_hops_raw, bool)
        or not isinstance(max_retry_hops_raw, int)
        or max_retry_hops_raw < 1
    ):
        raise ValueError("sim_fetch_01_invalid_max_retry_hops")

    # --- Validate adaptive heat-driven replication controls (Fix6) ---
    adaptive_replication_enabled = scenario_config.get("adaptive_replication_enabled", False)
    if not isinstance(adaptive_replication_enabled, bool):
        raise ValueError("sim_fetch_01_invalid_adaptive_replication_enabled")

    heat_replication_threshold = scenario_config.get("heat_replication_threshold", 25)
    if (
        isinstance(heat_replication_threshold, bool)
        or not isinstance(heat_replication_threshold, int)
        or heat_replication_threshold < 1
    ):
        raise ValueError("sim_fetch_01_invalid_heat_replication_threshold")

    max_adaptive_replications_per_epoch = scenario_config.get(
        "max_adaptive_replications_per_epoch",
        25,
    )
    if (
        isinstance(max_adaptive_replications_per_epoch, bool)
        or not isinstance(max_adaptive_replications_per_epoch, int)
        or max_adaptive_replications_per_epoch < 1
    ):
        raise ValueError("sim_fetch_01_invalid_max_adaptive_replications_per_epoch")

    adaptive_tiers_raw = scenario_config.get("adaptive_replication_tiers", [_TIER_B, _TIER_C])
    if (
        not isinstance(adaptive_tiers_raw, (list, tuple))
        or not adaptive_tiers_raw
        or any(not isinstance(t, str) for t in adaptive_tiers_raw)
    ):
        raise ValueError("sim_fetch_01_invalid_adaptive_replication_tiers")
    adaptive_replication_tiers = tuple(dict.fromkeys(adaptive_tiers_raw))
    if any(t not in (_TIER_B, _TIER_C) for t in adaptive_replication_tiers):
        raise ValueError("sim_fetch_01_invalid_adaptive_replication_tiers")

    # --- Validate Werner topology overlay controls (Fix8) ---
    werner_overlay_enabled = scenario_config.get("werner_overlay_enabled", False)
    if not isinstance(werner_overlay_enabled, bool):
        raise ValueError("sim_fetch_01_invalid_werner_overlay_enabled")

    werner_smoothing_alpha = _to_rate_decimal(
        scenario_config.get("werner_smoothing_alpha", "0.50"),
        "werner_smoothing_alpha",
    )

    werner_heat_signal_threshold = scenario_config.get("werner_heat_signal_threshold", 50)
    if (
        isinstance(werner_heat_signal_threshold, bool)
        or not isinstance(werner_heat_signal_threshold, int)
        or werner_heat_signal_threshold < 1
    ):
        raise ValueError("sim_fetch_01_invalid_werner_heat_signal_threshold")

    werner_cooling_signal_threshold = scenario_config.get("werner_cooling_signal_threshold", 2)
    if (
        isinstance(werner_cooling_signal_threshold, bool)
        or not isinstance(werner_cooling_signal_threshold, int)
        or werner_cooling_signal_threshold < 0
        or werner_cooling_signal_threshold >= werner_heat_signal_threshold
    ):
        raise ValueError("sim_fetch_01_invalid_werner_cooling_signal_threshold")

    werner_pressure_tiers_raw = scenario_config.get("werner_pressure_tiers", [_TIER_B, _TIER_C])
    if (
        not isinstance(werner_pressure_tiers_raw, (list, tuple))
        or not werner_pressure_tiers_raw
        or any(not isinstance(t, str) for t in werner_pressure_tiers_raw)
    ):
        raise ValueError("sim_fetch_01_invalid_werner_pressure_tiers")
    werner_pressure_tiers = tuple(dict.fromkeys(werner_pressure_tiers_raw))
    if any(t not in (_TIER_B, _TIER_C) for t in werner_pressure_tiers):
        raise ValueError("sim_fetch_01_invalid_werner_pressure_tiers")

    # --- Validate OOM guard ---
    max_req = scenario_config.get("max_requests_per_epoch", _DEFAULT_MAX_REQUESTS_PER_EPOCH)
    if isinstance(max_req, bool) or not isinstance(max_req, int) or max_req < 1:
        raise ValueError("sim_fetch_01_invalid_max_requests_per_epoch")

    # --- Validate seed ---
    seed = scenario_config.get("seed", 42)
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("sim_fetch_01_invalid_seed")

    # --- Extract validated config ---
    n_peers: int = scenario_config["n_serving_peers"]
    n_epochs: int = scenario_config["n_epochs"]
    n_agents: int = scenario_config["n_agents"]
    tier_counts: dict[str, int] = {
        _TIER_A: scenario_config["tier_a_artifact_count"],
        _TIER_B: scenario_config["tier_b_artifact_count"],
        _TIER_C: scenario_config["tier_c_artifact_count"],
    }
    cache_cap: int = scenario_config["cache_capacity_per_peer"]

    if max_retry_hops_raw > n_peers:
        raise ValueError("sim_fetch_01_max_retry_hops_exceeds_n_peers")
    max_retry_hops: int = max_retry_hops_raw

    # --- Circuit breaker threshold ---
    cb_threshold_raw = scenario_config.get("circuit_breaker_threshold", max(max_req // n_peers, 1))
    if isinstance(cb_threshold_raw, bool) or not isinstance(cb_threshold_raw, int) or cb_threshold_raw < 1:
        raise ValueError("sim_fetch_01_invalid_circuit_breaker_threshold")
    cb_threshold: int = cb_threshold_raw

    # --- Peer role configuration (Fix4) ---
    # hot_mirror peers hold elevated Tier B inventory; archive_shard peers hold elevated Tier C.
    # These roles change initial inventory fractions; all peers hold full Tier A (anchor behavior).
    hot_mirror_count = scenario_config.get("hot_mirror_peer_count", 0)
    if isinstance(hot_mirror_count, bool) or not isinstance(hot_mirror_count, int) or hot_mirror_count < 0:
        raise ValueError("sim_fetch_01_invalid_hot_mirror_peer_count")
    if hot_mirror_count > n_peers:
        raise ValueError("sim_fetch_01_hot_mirror_peer_count_exceeds_n_peers")

    archive_shard_count = scenario_config.get("archive_shard_peer_count", 0)
    if isinstance(archive_shard_count, bool) or not isinstance(archive_shard_count, int) or archive_shard_count < 0:
        raise ValueError("sim_fetch_01_invalid_archive_shard_peer_count")
    if archive_shard_count > n_peers:
        raise ValueError("sim_fetch_01_archive_shard_peer_count_exceeds_n_peers")

    # Inventory fractions per role (integer tenths: 6 = 60%, 9 = 90%, etc.)
    tier_b_frac_general = scenario_config.get("tier_b_peer_inventory_fraction", _DEFAULT_TIER_B_PEER_INVENTORY_FRACTION)
    tier_c_frac_general = scenario_config.get("tier_c_peer_inventory_fraction", _DEFAULT_TIER_C_PEER_INVENTORY_FRACTION)
    for frac, name in [(tier_b_frac_general, "tier_b_peer_inventory_fraction"),
                       (tier_c_frac_general, "tier_c_peer_inventory_fraction")]:
        if isinstance(frac, bool) or not isinstance(frac, int) or not (1 <= frac <= 10):
            raise ValueError(f"sim_fetch_01_invalid_{name}")

    tier_b_frac_mirror = scenario_config.get("hot_mirror_tier_b_fraction", min(tier_b_frac_general + 3, 10))
    tier_c_frac_shard = scenario_config.get("archive_shard_tier_c_fraction", min(tier_c_frac_general + 3, 10))
    for frac, name in [(tier_b_frac_mirror, "hot_mirror_tier_b_fraction"),
                       (tier_c_frac_shard, "archive_shard_tier_c_fraction")]:
        if isinstance(frac, bool) or not isinstance(frac, int) or not (1 <= frac <= 10):
            raise ValueError(f"sim_fetch_01_invalid_{name}")

    # Controlled layout for Fix4 architectural tests:
    # each Tier B artifact is placed on exactly K peers. This makes the
    # "3 holders out of 5 peers" random-vs-routed comparison deterministic.
    tier_b_exact_holder_count = scenario_config.get("tier_b_exact_holder_count_per_artifact")
    if tier_b_exact_holder_count is not None:
        if (
            isinstance(tier_b_exact_holder_count, bool)
            or not isinstance(tier_b_exact_holder_count, int)
            or not (1 <= tier_b_exact_holder_count <= n_peers)
        ):
            raise ValueError("sim_fetch_01_invalid_tier_b_exact_holder_count_per_artifact")

    # --- RNGs ---
    # Main RNG: tier/artifact selection + random-model peer selection + inventory sampling
    rng = _DeterministicRNG(seed)
    # Routed RNG: staleness draws + routed holder selection (derived seed, independent sequence)
    rng_routed = _DeterministicRNG(seed ^ _RNG_ROUTED_SEED_XOR)
    # Retry RNG: later-hop holder traversal, isolated from first-hop diagnostics.
    rng_retry = _DeterministicRNG(seed ^ _RNG_RETRY_SEED_XOR)
    # Replication RNG: deterministic holder placement for heat-driven mirroring.
    rng_replication = _DeterministicRNG(seed ^ _RNG_REPLICATION_SEED_XOR)

    # --- Build Zipf CDFs ---
    cdf_a = _build_zipf_cdf(tier_counts[_TIER_A], zipf_exp_a)
    cdf_b = _build_zipf_cdf(tier_counts[_TIER_B], zipf_exp_b)

    # --- Initialize per-peer LRU caches ---
    caches = [_LRUCache(cache_cap) for _ in range(n_peers)]

    # --- Assign peer roles and initialize inventories ---
    peer_roles: list[str] = []
    peer_inventories: list[dict[str, set[int]]] = []
    for p in range(n_peers):
        if p < hot_mirror_count:
            role = _PEER_ROLE_HOT_MIRROR
            b_frac = tier_b_frac_mirror
            c_frac = tier_c_frac_general
        elif p < hot_mirror_count + archive_shard_count:
            role = _PEER_ROLE_ARCHIVE_SHARD
            b_frac = tier_b_frac_general
            c_frac = tier_c_frac_shard
        else:
            role = _PEER_ROLE_GENERAL
            b_frac = tier_b_frac_general
            c_frac = tier_c_frac_general
        peer_roles.append(role)

        inv_b_size = max(1, tier_counts[_TIER_B] * b_frac // 10)
        inv_c_size = max(1, tier_counts[_TIER_C] * c_frac // 10)
        peer_inventories.append({
            _TIER_A: set(range(tier_counts[_TIER_A])),  # All peers are Tier A anchors
            _TIER_B: (
                set()
                if tier_b_exact_holder_count is not None
                else set(
                    rng.sample(
                        range(tier_counts[_TIER_B]),
                        min(inv_b_size, tier_counts[_TIER_B]),
                    )
                )
            ),
            _TIER_C: set(rng.sample(range(tier_counts[_TIER_C]), min(inv_c_size, tier_counts[_TIER_C]))),
        })

    if tier_b_exact_holder_count is not None:
        for art_id in range(tier_counts[_TIER_B]):
            start_peer = art_id % n_peers
            for offset in range(tier_b_exact_holder_count):
                peer_inventories[(start_peer + offset) % n_peers][_TIER_B].add(art_id)

    # --- Build holder directory (Fix4) ---
    holder_directory = _build_holder_directory(peer_inventories, tier_counts, n_peers)
    initial_holder_count_stats = {t: _holder_count_stats(holder_directory, t) for t in _TIERS}

    # --- Aggregate counters: random (single-hop) model ---
    total_fetch: dict[str, int] = {_TIER_A: 0, _TIER_B: 0, _TIER_C: 0}
    want_have_hits: int = 0
    want_have_misses: int = 0
    wb_success: int = 0
    wb_error_404: int = 0
    wb_error_404_by_tier: dict[str, int] = {_TIER_A: 0, _TIER_B: 0, _TIER_C: 0}
    wb_error_429: int = 0
    wb_error_400: int = 0
    cache_attempts_a: int = 0
    cache_hits_a: int = 0
    cache_attempts_c: int = 0
    cache_hits_c: int = 0
    bytes_by_tier: dict[str, Decimal] = {t: Decimal("0") for t in _TIERS}
    non_cacheable_vol: int = 0
    cb_activations: int = 0
    cdl_078_credits: int = 0
    cdl_078_credits_by_serving_peer: dict[int, int] = {p: 0 for p in range(n_peers)}
    cdl_078_credits_by_tier: dict[str, int] = {t: 0 for t in _TIERS}
    serve_pressure: dict[int, int] = {p: 0 for p in range(n_peers)}
    artifact_req_counts: dict[str, dict[int, int]] = {_TIER_A: {}, _TIER_B: {}, _TIER_C: {}}

    # --- Aggregate counters: routed holder model (Fix4/Fix5) ---
    routed_total_fetch: dict[str, int] = {_TIER_A: 0, _TIER_B: 0, _TIER_C: 0}
    routed_single_hop_error_404_by_tier: dict[str, int] = {
        _TIER_A: 0,
        _TIER_B: 0,
        _TIER_C: 0,
    }
    routed_error_404_by_tier: dict[str, int] = {_TIER_A: 0, _TIER_B: 0, _TIER_C: 0}
    routed_holder_lookups: int = 0      # Requests where directory lookup was attempted
    routed_success_count: int = 0       # Requests that succeeded after <= max_retry_hops
    routed_stale_fallbacks: int = 0     # Lookups that fell back due to directory staleness
    routed_rescue_count: int = 0        # Requests rescued by hop > 1
    routed_retry_exhausted_count: int = 0
    routed_total_probe_count: int = 0
    routed_success_hop_total: int = 0
    routed_cb_activations: int = 0
    routed_cb_activations_by_tier: dict[str, int] = {_TIER_A: 0, _TIER_B: 0, _TIER_C: 0}
    routed_cdl_078_credits: int = 0
    routed_cdl_078_credits_by_serving_peer: dict[int, int] = {
        p: 0 for p in range(n_peers)
    }
    routed_cdl_078_credits_by_tier: dict[str, int] = {t: 0 for t in _TIERS}
    routed_cdl_078_rescue_credit_count: int = 0

    # --- Adaptive heat-driven replication counters (Fix6) ---
    adaptive_replication_events_by_tier: dict[str, int] = {t: 0 for t in _TIERS}
    adaptive_replication_total_events: int = 0
    adaptive_replication_epochs_active: int = 0
    routed_failure_rate_by_epoch_by_tier: dict[str, list[str]] = {t: [] for t in _TIERS}
    adaptive_holder_mean_by_epoch_by_tier: dict[str, list[str]] = {t: [] for t in _TIERS}

    # --- Werner topology pressure overlay counters (Fix8) ---
    werner_smoothed_pressure_state: dict[str, Decimal] = {t: Decimal("0") for t in _TIERS}
    werner_raw_pressure_by_epoch_by_tier: dict[str, list[str]] = {t: [] for t in _TIERS}
    werner_smoothed_pressure_by_epoch_by_tier: dict[str, list[str]] = {
        t: [] for t in _TIERS
    }
    werner_heat_signal_by_epoch_by_tier: dict[str, list[int]] = {t: [] for t in _TIERS}
    werner_cooling_signal_by_epoch_by_tier: dict[str, list[int]] = {
        t: [] for t in _TIERS
    }
    werner_heat_signal_count_by_tier: dict[str, int] = {t: 0 for t in _TIERS}
    werner_cooling_signal_count_by_tier: dict[str, int] = {t: 0 for t in _TIERS}
    werner_cumulative_smoothed_pressure_by_tier: dict[str, Decimal] = {
        t: Decimal("0") for t in _TIERS
    }

    # --- Simulation loop ---
    for _epoch in range(n_epochs):
        # Tier B cache invalidation at epoch boundary (Tier B content mutable per epoch)
        for p in range(n_peers):
            new_cache = _LRUCache(cache_cap)
            for key in list(caches[p]._data):
                if key[0] == _TIER_A:
                    new_cache.put(key)
            caches[p] = new_cache

        n_requests = min(rng.poisson_count(n_agents, avg_per_agent), max_req)
        peer_req_count = [0] * n_peers
        routed_peer_req_count = [0] * n_peers
        epoch_artifact_req_counts: dict[str, dict[int, int]] = {
            _TIER_A: {},
            _TIER_B: {},
            _TIER_C: {},
        }
        epoch_routed_total_fetch: dict[str, int] = {_TIER_A: 0, _TIER_B: 0, _TIER_C: 0}
        epoch_routed_error_404_by_tier: dict[str, int] = {
            _TIER_A: 0,
            _TIER_B: 0,
            _TIER_C: 0,
        }
        epoch_routed_success_by_peer_by_tier: dict[str, dict[int, int]] = {
            t: {p: 0 for p in range(n_peers)} for t in _TIERS
        }

        for _ in range(n_requests):
            # --- Shared: tier and artifact selection ---
            roll = rng.fraction()
            if roll < rate_a:
                tier = _TIER_A
            elif roll < rate_a + rate_b:
                tier = _TIER_B
            else:
                tier = _TIER_C

            if tier == _TIER_A:
                art_id = _zipf_draw(rng, cdf_a)
            elif tier == _TIER_B:
                art_id = _zipf_draw(rng, cdf_b)
            else:
                art_id = rng.randint(0, tier_counts[_TIER_C] - 1)

            artifact_req_counts[tier][art_id] = artifact_req_counts[tier].get(art_id, 0) + 1
            epoch_artifact_req_counts[tier][art_id] = (
                epoch_artifact_req_counts[tier].get(art_id, 0) + 1
            )

            # === ROUTED HOLDER MODEL (Fix4/Fix5) ===
            # Processed before random-model peer selection so it is not affected by CB.
            # Routed model: route to a known holder; if stale, first hop falls
            # back to random, then multi-hop retry traverses to a known holder.
            routed_holder_lookups += 1
            holders = holder_directory[tier][art_id]
            routed_total_fetch[tier] += 1
            epoch_routed_total_fetch[tier] += 1

            if not holders:
                # Artifact not replicated on any peer — genuine 404 regardless of routing
                routed_total_probe_count += 1
                routed_single_hop_error_404_by_tier[tier] += 1
                routed_error_404_by_tier[tier] += 1
                epoch_routed_error_404_by_tier[tier] += 1
                routed_retry_exhausted_count += 1
            else:
                # Determine if this directory lookup is stale
                is_stale = (
                    directory_staleness_rate > Decimal("0")
                    and rng_routed.fraction() < directory_staleness_rate
                )

                tried_peers: set[int] = set()
                success = False
                hops_used = 0
                successful_routed_peer: int | None = None

                if is_stale:
                    # Stale: fall back to random peer (routed model degrades to random model)
                    routed_stale_fallbacks += 1
                    stale_peer = rng_routed.randint(0, n_peers - 1)
                    tried_peers.add(stale_peer)
                    hops_used = 1
                    routed_total_probe_count += 1
                    success = art_id in peer_inventories[stale_peer][tier]
                    if success:
                        successful_routed_peer = stale_peer
                else:
                    # Fresh directory + known holders → route to a holder (always succeeds)
                    holder_list = sorted(holders)  # Sorted for determinism
                    first_peer = holder_list[rng_routed.randint(0, len(holder_list) - 1)]
                    tried_peers.add(first_peer)
                    hops_used = 1
                    routed_total_probe_count += 1
                    success = True
                    successful_routed_peer = first_peer

                if not success:
                    routed_single_hop_error_404_by_tier[tier] += 1

                    while hops_used < max_retry_hops:
                        remaining_holders = sorted(holders.difference(tried_peers))
                        if not remaining_holders:
                            break

                        retry_peer = remaining_holders[
                            rng_retry.randint(0, len(remaining_holders) - 1)
                        ]
                        tried_peers.add(retry_peer)
                        hops_used += 1
                        routed_total_probe_count += 1

                        if art_id in peer_inventories[retry_peer][tier]:
                            success = True
                            successful_routed_peer = retry_peer
                            routed_rescue_count += 1
                            break

                if success:
                    routed_success_count += 1
                    routed_success_hop_total += hops_used
                    if successful_routed_peer is None:
                        raise ValueError("sim_fetch_01_routed_success_peer_missing")
                    if routed_peer_req_count[successful_routed_peer] >= cb_threshold:
                        routed_cb_activations += 1
                        routed_cb_activations_by_tier[tier] += 1
                    routed_peer_req_count[successful_routed_peer] += 1
                    epoch_routed_success_by_peer_by_tier[tier][successful_routed_peer] += 1
                    if tier in (_TIER_A, _TIER_B):
                        routed_cdl_078_credits += 1
                        routed_cdl_078_credits_by_serving_peer[successful_routed_peer] += 1
                        routed_cdl_078_credits_by_tier[tier] += 1
                        if hops_used > 1:
                            routed_cdl_078_rescue_credit_count += 1
                else:
                    routed_error_404_by_tier[tier] += 1
                    epoch_routed_error_404_by_tier[tier] += 1
                    routed_retry_exhausted_count += 1

            # === RANDOM (SINGLE-HOP) MODEL ===
            # Uniform peer selection; circuit breaker applies.
            peer_id = rng.randint(0, n_peers - 1)
            serve_pressure[peer_id] += 1

            if peer_req_count[peer_id] >= cb_threshold:
                wb_error_429 += 1
                cb_activations += 1
                continue
            peer_req_count[peer_id] += 1
            total_fetch[tier] += 1

            has_artifact = art_id in peer_inventories[peer_id][tier]

            if not has_artifact:
                want_have_misses += 1
                wb_error_404 += 1
                wb_error_404_by_tier[tier] += 1
                if tier == _TIER_A:
                    cache_attempts_a += 1
                elif tier == _TIER_C:
                    cache_attempts_c += 1
                    non_cacheable_vol += 1
                continue

            want_have_hits += 1
            cache_key = (tier, art_id)
            in_cache = caches[peer_id].has(cache_key)
            wb_success += 1

            if tier == _TIER_A:
                cache_attempts_a += 1
                if in_cache:
                    cache_hits_a += 1
                else:
                    caches[peer_id].put(cache_key)
                bytes_by_tier[_TIER_A] += _BYTES_PER_TIER[_TIER_A]
                cdl_078_credits += 1
                cdl_078_credits_by_serving_peer[peer_id] += 1
                cdl_078_credits_by_tier[_TIER_A] += 1
            elif tier == _TIER_B:
                if not in_cache:
                    caches[peer_id].put(cache_key)
                bytes_by_tier[_TIER_B] += _BYTES_PER_TIER[_TIER_B]
                cdl_078_credits += 1
                cdl_078_credits_by_serving_peer[peer_id] += 1
                cdl_078_credits_by_tier[_TIER_B] += 1
            else:
                cache_attempts_c += 1
                if in_cache:
                    cache_hits_c += 1
                else:
                    caches[peer_id].put(cache_key)
                bytes_by_tier[_TIER_C] += _BYTES_PER_TIER[_TIER_C]
                non_cacheable_vol += 1

        # Record this epoch's effective routed availability before applying
        # heat-driven replication, then let heat change the next epoch's topology.
        for t in _TIERS:
            routed_failure_rate_by_epoch_by_tier[t].append(
                _safe_ratio(epoch_routed_error_404_by_tier[t], max(epoch_routed_total_fetch[t], 1))
            )

        if werner_overlay_enabled:
            for t in _TIERS:
                if t in werner_pressure_tiers:
                    serve_counts = list(epoch_routed_success_by_peer_by_tier[t].values())
                    mean_epoch_serve_pressure = Decimal(sum(serve_counts)) / Decimal(n_peers)
                    serve_skew_pressure = max(
                        Decimal(max(serve_counts)) - mean_epoch_serve_pressure,
                        Decimal("0"),
                    )
                    request_heat = Decimal(sum(epoch_artifact_req_counts[t].values()))
                    miss_heat = Decimal(epoch_routed_error_404_by_tier[t]) * Decimal("2")
                    raw_pressure = request_heat + miss_heat + serve_skew_pressure
                    prev_smoothed = werner_smoothed_pressure_state[t]
                    smoothed = (
                        (werner_smoothing_alpha * prev_smoothed)
                        + ((Decimal("1") - werner_smoothing_alpha) * raw_pressure)
                    )
                    werner_smoothed_pressure_state[t] = smoothed
                else:
                    raw_pressure = Decimal("0")
                    smoothed = Decimal("0")

                heat_signal = int(smoothed >= Decimal(werner_heat_signal_threshold))
                cooling_signal = int(
                    t in werner_pressure_tiers
                    and smoothed <= Decimal(werner_cooling_signal_threshold)
                )

                werner_raw_pressure_by_epoch_by_tier[t].append(
                    _quantized_decimal_str(raw_pressure)
                )
                werner_smoothed_pressure_by_epoch_by_tier[t].append(
                    _quantized_decimal_str(smoothed)
                )
                werner_heat_signal_by_epoch_by_tier[t].append(heat_signal)
                werner_cooling_signal_by_epoch_by_tier[t].append(cooling_signal)
                werner_heat_signal_count_by_tier[t] += heat_signal
                werner_cooling_signal_count_by_tier[t] += cooling_signal
                werner_cumulative_smoothed_pressure_by_tier[t] += smoothed

        epoch_replication_events = 0
        if adaptive_replication_enabled:
            for adaptive_tier in adaptive_replication_tiers:
                ranked_hot_artifacts = sorted(
                    (
                        (-count, art_id)
                        for art_id, count in epoch_artifact_req_counts[adaptive_tier].items()
                        if count >= heat_replication_threshold
                    )
                )
                for _neg_count, art_id in ranked_hot_artifacts:
                    holders = holder_directory[adaptive_tier][art_id]
                    if len(holders) >= n_peers:
                        continue
                    non_holders = [p for p in range(n_peers) if p not in holders]
                    if not non_holders:
                        continue

                    new_holder = non_holders[
                        rng_replication.randint(0, len(non_holders) - 1)
                    ]
                    peer_inventories[new_holder][adaptive_tier].add(art_id)
                    new_holders = set(holders)
                    new_holders.add(new_holder)
                    holder_directory[adaptive_tier][art_id] = frozenset(new_holders)

                    adaptive_replication_events_by_tier[adaptive_tier] += 1
                    adaptive_replication_total_events += 1
                    epoch_replication_events += 1
                    if epoch_replication_events >= max_adaptive_replications_per_epoch:
                        break
                if epoch_replication_events >= max_adaptive_replications_per_epoch:
                    break

        if epoch_replication_events > 0:
            adaptive_replication_epochs_active += 1

        for t in _TIERS:
            adaptive_holder_mean_by_epoch_by_tier[t].append(
                _holder_mean(holder_directory, t)
            )

    # --- Compute random-model aggregate rates ---
    total_want_have = want_have_hits + want_have_misses
    total_requests = total_fetch[_TIER_A] + total_fetch[_TIER_B] + total_fetch[_TIER_C] + wb_error_429

    wh_hit_rate = _safe_ratio(want_have_hits, total_want_have)
    wh_miss_rate = _safe_ratio(want_have_misses, total_want_have)
    cache_rate_a = _safe_ratio(cache_hits_a, cache_attempts_a)
    cache_rate_c = _safe_ratio(cache_hits_c, cache_attempts_c)
    failure_rate_str = _safe_ratio(wb_error_404 + wb_error_429, max(total_requests, 1))

    # serve_pressure: string keys for JSON safety
    spp = {f"peer_{p}": serve_pressure[p] for p in range(n_peers)}
    cdl_078_peer_credits = {
        f"peer_{p}": cdl_078_credits_by_serving_peer[p] for p in range(n_peers)
    }
    routed_cdl_078_peer_credits = {
        f"peer_{p}": routed_cdl_078_credits_by_serving_peer[p]
        for p in range(n_peers)
    }

    # --- Random model per-tier failure rates (Fix3, renamed Fix4) ---
    rand_failure_rate_by_tier = {
        _TIER_A: _safe_ratio(wb_error_404_by_tier[_TIER_A], max(total_fetch[_TIER_A], 1)),
        _TIER_B: _safe_ratio(wb_error_404_by_tier[_TIER_B], max(total_fetch[_TIER_B], 1)),
        _TIER_C: _safe_ratio(wb_error_404_by_tier[_TIER_C], max(total_fetch[_TIER_C], 1)),
    }
    total_tier_ab_rand = total_fetch[_TIER_A] + total_fetch[_TIER_B]
    rand_tier_ab_failure_rate = _safe_ratio(
        wb_error_404_by_tier[_TIER_A] + wb_error_404_by_tier[_TIER_B], max(total_tier_ab_rand, 1)
    )
    rand_tier_c_advisory = rand_failure_rate_by_tier[_TIER_C]

    rand_tier_service_verdict = _compute_tier_service_verdict(
        cache_rate_a=Decimal(cache_rate_a),
        tier_ab_failure_rate=Decimal(rand_tier_ab_failure_rate),
        cb_fraction=Decimal(cb_activations) / Decimal(max(total_requests, 1)),
        spp=spp,
        total_tier_ab_requests=total_tier_ab_rand,
    )

    # --- Routed model metrics (Fix4/Fix5) ---
    routed_single_hop_failure_rate_by_tier = {
        _TIER_A: _safe_ratio(
            routed_single_hop_error_404_by_tier[_TIER_A],
            max(routed_total_fetch[_TIER_A], 1),
        ),
        _TIER_B: _safe_ratio(
            routed_single_hop_error_404_by_tier[_TIER_B],
            max(routed_total_fetch[_TIER_B], 1),
        ),
        _TIER_C: _safe_ratio(
            routed_single_hop_error_404_by_tier[_TIER_C],
            max(routed_total_fetch[_TIER_C], 1),
        ),
    }
    routed_failure_rate_by_tier = {
        _TIER_A: _safe_ratio(routed_error_404_by_tier[_TIER_A], max(routed_total_fetch[_TIER_A], 1)),
        _TIER_B: _safe_ratio(routed_error_404_by_tier[_TIER_B], max(routed_total_fetch[_TIER_B], 1)),
        _TIER_C: _safe_ratio(routed_error_404_by_tier[_TIER_C], max(routed_total_fetch[_TIER_C], 1)),
    }
    total_tier_ab_routed = routed_total_fetch[_TIER_A] + routed_total_fetch[_TIER_B]
    routed_single_hop_tier_ab_failure_rate = _safe_ratio(
        routed_single_hop_error_404_by_tier[_TIER_A]
        + routed_single_hop_error_404_by_tier[_TIER_B],
        max(total_tier_ab_routed, 1),
    )
    routed_tier_ab_failure_rate = _safe_ratio(
        routed_error_404_by_tier[_TIER_A] + routed_error_404_by_tier[_TIER_B],
        max(total_tier_ab_routed, 1),
    )

    routed_holder_hit_rate = _safe_ratio(routed_success_count, max(routed_holder_lookups, 1))
    routed_staleness_rate_observed = _safe_ratio(routed_stale_fallbacks, max(routed_holder_lookups, 1))
    routed_avg_hops_per_successful_request = _safe_ratio(
        routed_success_hop_total,
        max(routed_success_count, 1),
    )
    routed_cb_fraction = Decimal(routed_cb_activations) / Decimal(max(routed_total_probe_count, 1))

    # Routed tier_service_verdict uses routed failure rates.
    # cache_rate_a from the random model is used as a proxy (same artifact distribution).
    routed_tier_service_verdict = _compute_tier_service_verdict(
        cache_rate_a=Decimal(cache_rate_a),
        tier_ab_failure_rate=Decimal(routed_tier_ab_failure_rate),
        cb_fraction=routed_cb_fraction,
        spp=spp,
        total_tier_ab_requests=total_tier_ab_routed,
    )

    # --- Holder count statistics (Fix4) ---
    holder_count_stats = {t: _holder_count_stats(holder_directory, t) for t in _TIERS}

    # --- Werner topology recommendations (Fix8) ---
    werner_topology_recommendation_by_tier: dict[str, str] = {}
    werner_ecu_pressure_signal_by_tier: dict[str, str] = {}
    for t in _TIERS:
        if not werner_overlay_enabled or t not in werner_pressure_tiers:
            werner_topology_recommendation_by_tier[t] = "not_evaluated"
            werner_ecu_pressure_signal_by_tier[t] = "0.000000"
            continue

        heat_count = werner_heat_signal_count_by_tier[t]
        cooling_count = werner_cooling_signal_count_by_tier[t]
        if heat_count > 0 and heat_count >= cooling_count:
            werner_topology_recommendation_by_tier[t] = "expand_capacity"
        elif cooling_count > 0 and heat_count == 0:
            werner_topology_recommendation_by_tier[t] = "cool_capacity"
        else:
            werner_topology_recommendation_by_tier[t] = "hold_capacity"

        werner_ecu_pressure_signal_by_tier[t] = _quantized_decimal_str(
            werner_cumulative_smoothed_pressure_by_tier[t] / Decimal(max(n_epochs, 1))
        )

    # --- Artifact popularity ---
    top_q_concentration = {
        t: _compute_top_quartile_concentration(artifact_req_counts[t]) for t in _TIERS
    }

    # --- Compute aggregate verdict (based on random model, per design spec §7) ---
    verdict = _compute_verdict(
        cache_rate_a=Decimal(cache_rate_a),
        failure_rate=Decimal(failure_rate_str),
        tier_a_fraction=Decimal(total_fetch[_TIER_A]) / Decimal(max(total_requests, 1)),
        cb_fraction=Decimal(cb_activations) / Decimal(max(total_requests, 1)),
        spp=spp,
        total_requests=total_requests,
    )

    return {
        "sim": "SIM-FETCH-01",
        "sim_version": SIM_FETCH_01_HARNESS_VERSION,
        "cdl_087_dependency": CDL_087_DEPENDENCY,
        "cdl_087_ratification_authorized": False,
        "cdl_087_ratification_not_authorized_note": (
            "tier_service_verdict does not authorize CDL-087 ratification"
        ),
        "scenario": {
            "n_serving_peers": n_peers,
            "n_epochs": n_epochs,
            "n_agents": n_agents,
            "tier_a_artifact_count": tier_counts[_TIER_A],
            "tier_b_artifact_count": tier_counts[_TIER_B],
            "tier_c_artifact_count": tier_counts[_TIER_C],
            "tier_a_request_rate": str(rate_a),
            "tier_b_request_rate": str(rate_b),
            "tier_c_request_rate": str(rate_c),
            "zipf_exponent_tier_a": str(zipf_exp_a),
            "zipf_exponent_tier_b": str(zipf_exp_b),
            "avg_requests_per_agent": str(avg_per_agent),
            "cache_capacity_per_peer": cache_cap,
            "max_requests_per_epoch": max_req,
            "seed": seed,
            "directory_staleness_rate": str(directory_staleness_rate),
            "max_retry_hops": max_retry_hops,
            "adaptive_replication_enabled": adaptive_replication_enabled,
            "heat_replication_threshold": heat_replication_threshold,
            "max_adaptive_replications_per_epoch": max_adaptive_replications_per_epoch,
            "adaptive_replication_tiers": list(adaptive_replication_tiers),
            "werner_overlay_enabled": werner_overlay_enabled,
            "werner_smoothing_alpha": str(werner_smoothing_alpha),
            "werner_heat_signal_threshold": werner_heat_signal_threshold,
            "werner_cooling_signal_threshold": werner_cooling_signal_threshold,
            "werner_pressure_tiers": list(werner_pressure_tiers),
            "hot_mirror_peer_count": hot_mirror_count,
            "archive_shard_peer_count": archive_shard_count,
            "tier_b_exact_holder_count_per_artifact": tier_b_exact_holder_count,
            "peer_roles": peer_roles,
        },
        "aggregate_over_epochs": {
            # CDL-087 §6 required signals (exact names) — random model
            "fetch_requests_by_tier": {t: total_fetch[t] for t in _TIERS},
            "want_have_hit_rate": wh_hit_rate,
            "want_have_miss_rate": wh_miss_rate,
            "want_block_success_count": wb_success,
            "want_block_error_404": wb_error_404,
            "want_block_error_429": wb_error_429,
            "want_block_error_400": wb_error_400,
            "cache_hit_rate_tier_a": cache_rate_a,
            "bytes_served_by_tier": {t: str(bytes_by_tier[t]) for t in _TIERS},
            "non_cacheable_request_volume": non_cacheable_vol,
            "circuit_breaker_activations": cb_activations,
            "serve_events_credited_cdl_078": cdl_078_credits,
            # Fix7: credit attribution bridge. Legacy total above is preserved,
            # but credit is now explicitly attributable to serving peers/operators.
            "serve_credit_attribution_model": "serving_peer_operator_instance",
            "serve_credit_served_graph_node_only_count": 0,
            "serve_events_credited_cdl_078_by_serving_peer": cdl_078_peer_credits,
            "serve_events_credited_cdl_078_by_tier": cdl_078_credits_by_tier,
            "serve_credit_serving_peer_total": cdl_078_credits,
            "serve_credit_artifact_only_crediting_allowed": False,
            # Derived aliases (design spec §5)
            "cache_hit_rate_high_centrality": cache_rate_a,
            "cache_hit_rate_tail": cache_rate_c,
            "request_pressure_by_tier": {t: total_fetch[t] for t in _TIERS},
            "serve_pressure_by_peer": spp,
            "failure_rate": failure_rate_str,
            # Fix2: artifact popularity
            "top_quartile_request_concentration_by_tier": top_q_concentration,
            # Fix3/Fix4: single-hop random model per-tier metrics (canonical names)
            "single_hop_random_failure_rate_by_tier": rand_failure_rate_by_tier,
            "single_hop_random_tier_ab_failure_rate": rand_tier_ab_failure_rate,
            "single_hop_random_tier_c_advisory_failure_rate": rand_tier_c_advisory,
            "single_hop_random_tier_service_verdict": rand_tier_service_verdict,
            # Backward-compatibility aliases (Fix3 names → Fix4 renamed equivalents)
            "failure_rate_by_tier": rand_failure_rate_by_tier,
            "tier_ab_failure_rate": rand_tier_ab_failure_rate,
            "tier_c_advisory_failure_rate": rand_tier_c_advisory,
            # Fix4: routed holder model metrics
            # CDL-087 evaluation should use routed_ metrics, not single_hop_random_.
            # Fix5: routed_failure_rate_by_tier is post-retry effective availability.
            "routed_single_hop_failure_rate_by_tier": routed_single_hop_failure_rate_by_tier,
            "routed_single_hop_tier_ab_failure_rate": routed_single_hop_tier_ab_failure_rate,
            "routed_failure_rate_by_tier": routed_failure_rate_by_tier,
            "routed_effective_failure_rate_by_tier": routed_failure_rate_by_tier,
            "routed_tier_ab_failure_rate": routed_tier_ab_failure_rate,
            "routed_effective_tier_ab_failure_rate": routed_tier_ab_failure_rate,
            "routed_tier_service_verdict": routed_tier_service_verdict,
            "routed_holder_hit_rate": routed_holder_hit_rate,
            "routed_staleness_rate_observed": routed_staleness_rate_observed,
            # Fix5: multi-hop retry metrics
            "routed_max_retry_hops": max_retry_hops,
            "routed_total_probe_count": routed_total_probe_count,
            "routed_avg_hops_per_successful_request": routed_avg_hops_per_successful_request,
            "routed_rescue_count": routed_rescue_count,
            "routed_retry_exhausted_count": routed_retry_exhausted_count,
            "routed_circuit_breaker_activations": routed_cb_activations,
            "routed_circuit_breaker_activations_by_tier": routed_cb_activations_by_tier,
            "routed_circuit_breaker_fraction": _quantized_decimal_str(routed_cb_fraction),
            # Fix7: routed serving-peer/operator credit attribution.
            "routed_serve_events_credited_cdl_078": routed_cdl_078_credits,
            "routed_serve_events_credited_cdl_078_by_serving_peer": routed_cdl_078_peer_credits,
            "routed_serve_events_credited_cdl_078_by_tier": routed_cdl_078_credits_by_tier,
            "routed_serve_credit_rescue_count": routed_cdl_078_rescue_credit_count,
            # Fix4: holder directory coverage statistics
            "initial_known_holder_count_stats_by_tier": initial_holder_count_stats,
            "known_holder_count_stats_by_tier": holder_count_stats,
            "final_known_holder_count_stats_by_tier": holder_count_stats,
            # Fix6: adaptive heat-driven replication metrics
            "adaptive_replication_enabled": adaptive_replication_enabled,
            "adaptive_replication_events_by_tier": adaptive_replication_events_by_tier,
            "adaptive_replication_total_events": adaptive_replication_total_events,
            "adaptive_replication_epochs_active": adaptive_replication_epochs_active,
            "adaptive_replication_tiers": list(adaptive_replication_tiers),
            "adaptive_heat_threshold": heat_replication_threshold,
            "adaptive_max_replications_per_epoch": max_adaptive_replications_per_epoch,
            "routed_failure_rate_by_epoch_by_tier": routed_failure_rate_by_epoch_by_tier,
            "adaptive_holder_mean_by_epoch_by_tier": adaptive_holder_mean_by_epoch_by_tier,
            # Fix8: Werner topology pressure overlay. This is a simulation-only
            # pressure signal, not an ECU mint, ILC settlement, or CDL-087 ratification.
            "werner_overlay_enabled": werner_overlay_enabled,
            "werner_overlay_mode": "sim_fetch_topology_pressure_only",
            "werner_topology_smoothing_model": (
                "epoch_path_laplacian_exponential_smoothing_surrogate"
            ),
            "werner_pressure_tiers": list(werner_pressure_tiers),
            "werner_smoothing_alpha": str(werner_smoothing_alpha),
            "werner_heat_signal_threshold": werner_heat_signal_threshold,
            "werner_cooling_signal_threshold": werner_cooling_signal_threshold,
            "werner_raw_pressure_by_epoch_by_tier": werner_raw_pressure_by_epoch_by_tier,
            "werner_smoothed_pressure_by_epoch_by_tier": (
                werner_smoothed_pressure_by_epoch_by_tier
            ),
            "werner_heat_signal_by_epoch_by_tier": werner_heat_signal_by_epoch_by_tier,
            "werner_cooling_signal_by_epoch_by_tier": (
                werner_cooling_signal_by_epoch_by_tier
            ),
            "werner_heat_signal_count_by_tier": werner_heat_signal_count_by_tier,
            "werner_cooling_signal_count_by_tier": werner_cooling_signal_count_by_tier,
            "werner_topology_recommendation_by_tier": (
                werner_topology_recommendation_by_tier
            ),
            "werner_ecu_pressure_signal_by_tier": werner_ecu_pressure_signal_by_tier,
            "werner_ecu_pressure_mint_authorized": False,
            "werner_ilc_settlement_authorized": False,
            "werner_authorization_note": (
                "Werner overlay emits topology pressure signals only; it does not "
                "mint ECU, settle ILC, authorize CDL-087, or mutate production runtime."
            ),
        },
        # Top-level verdicts
        "aggregate_verdict": verdict,
        "tier_service_verdict": rand_tier_service_verdict,   # backward compat alias
        "verdict": verdict,
    }
