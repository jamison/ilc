from __future__ import annotations

# SIM-FETCH-01: Canonical Fetch Distribution Simulation Harness
#
# Phase 1238 — Window 1233-1240
# Governing authority: docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md
#
# CDL-087 ratification is NOT authorized by this harness.
#
# This module lives in ilc_core/sim/ (not a sensitive taboo scan root).
# It uses random.Random(seed) for reproducible simulation. This seeded RNG
# must not be imported or used in any production protocol code path.
# Production code must use secrets.SystemRandom() for stochastic needs.

import random
from collections import OrderedDict
from decimal import Decimal, InvalidOperation
from typing import Any

SIM_FETCH_01_HARNESS_VERSION = "sim_fetch_01_harness_1238.v0.1"
CDL_087_DEPENDENCY = "cdl_087_prelock_committed_phase_1228"

_TIER_A = "A"
_TIER_B = "B"
_TIER_C = "C"
_TIERS = (_TIER_A, _TIER_B, _TIER_C)

_DEFAULT_MAX_REQUESTS_PER_EPOCH = 500

# Synthetic byte units per served artifact, by tier (CDL-087 §5 / design spec §5)
_BYTES_PER_TIER = {
    _TIER_A: Decimal("1"),
    _TIER_B: Decimal("1") / Decimal("2"),
    _TIER_C: Decimal("1") / Decimal("10"),
}

# Fraction of tier inventory each peer initially holds
_TIER_B_PEER_INVENTORY_FRACTION = 6  # 60%
_TIER_C_PEER_INVENTORY_FRACTION = 2  # 20%


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
    """Convert a rate value to Decimal, rejecting float inputs."""
    if isinstance(val, float):
        raise ValueError(f"sim_fetch_01_float_forbidden_in_economic_field_{name}")
    try:
        d = Decimal(str(val))
    except InvalidOperation:
        raise ValueError(f"sim_fetch_01_invalid_decimal_{name}")
    _reject_non_finite(d, name)
    return d


def _safe_ratio(num: int, denom: int) -> str:
    """Compute num/denom as a canonical Decimal string; returns '0' on zero denom."""
    if denom == 0:
        return "0"
    return str((Decimal(num) / Decimal(denom)).quantize(Decimal("0.000001")))


def _compute_verdict(
    cache_rate_a: Decimal,
    failure_rate: Decimal,
    tier_a_fraction: Decimal,
    cb_fraction: Decimal,
    spp: dict[str, int],
    total_requests: int,
) -> str:
    """
    Apply SIM-FETCH-01 pass/fail thresholds (design spec §7).

    Returns: 'pass', 'fail', or 'inconclusive'.
    CDL-087 ratification is not authorized regardless of verdict.
    """
    # Inconclusive conditions
    if total_requests < 1000:
        return "inconclusive"
    if not cache_rate_a.is_finite() or not failure_rate.is_finite():
        return "inconclusive"
    if not spp or all(v == 0 for v in spp.values()):
        return "inconclusive"

    # Block-ratification conditions (any one blocks)
    if cache_rate_a < Decimal("0.50"):
        return "fail"
    if failure_rate > Decimal("0.20"):
        return "fail"
    if cb_fraction > Decimal("0.20"):
        return "fail"

    # Support-ratification conditions (all must hold)
    if (
        cache_rate_a >= Decimal("0.70")
        and failure_rate <= Decimal("0.10")
        and tier_a_fraction <= Decimal("0.20")
        and cb_fraction <= Decimal("0.05")
    ):
        # Check serve pressure distribution: max/mean <= 3.0
        pressures = list(spp.values())
        max_p = Decimal(max(pressures))
        mean_p = Decimal(sum(pressures)) / Decimal(len(pressures))
        if mean_p > 0 and max_p / mean_p <= Decimal("3.0"):
            return "pass"

    return "inconclusive"


def run_sim_fetch_01(scenario_config: dict) -> dict:
    """
    Run SIM-FETCH-01 fetch distribution simulation.

    Accepts scenario parameters as a config dict (no hardcoded constants).
    Returns a result dict with CDL-087 §6 observability metrics aggregated
    over all simulated epochs.

    Time axis: epoch sequence number. No wall-clock is used.
    Deterministic: identical scenario_config (including seed) produces identical output.

    OOM guard: total requests per epoch are capped at max_requests_per_epoch.

    CDL-087 ratification is NOT authorized by this harness.
    """
    # --- Validate integer parameters ---
    _required_pos_int = [
        "n_serving_peers",
        "n_epochs",
        "n_agents",
        "tier_a_artifact_count",
        "tier_b_artifact_count",
        "tier_c_artifact_count",
        "cache_capacity_per_peer",
    ]
    for key in _required_pos_int:
        if key not in scenario_config:
            raise ValueError(f"sim_fetch_01_missing_config_{key}")
        val = scenario_config[key]
        if isinstance(val, bool) or not isinstance(val, int) or val < 1:
            raise ValueError(f"sim_fetch_01_invalid_config_{key}")

    # --- Validate rate parameters ---
    rate_a = _to_rate_decimal(
        scenario_config.get("tier_a_request_rate", "0"), "tier_a_request_rate"
    )
    rate_b = _to_rate_decimal(
        scenario_config.get("tier_b_request_rate", "0"), "tier_b_request_rate"
    )
    rate_c = _to_rate_decimal(
        scenario_config.get("tier_c_request_rate", "0"), "tier_c_request_rate"
    )
    if rate_a + rate_b + rate_c != Decimal("1"):
        raise ValueError("sim_fetch_01_request_rates_must_sum_to_one")

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

    # Circuit breaker threshold: requests per peer per epoch before 429 fires
    cb_threshold: int = scenario_config.get(
        "circuit_breaker_threshold", max(max_req // n_peers, 1)
    )

    # --- Seeded RNG for reproducibility (simulation only; not for protocol use) ---
    rng = random.Random(seed)

    # --- Initialize per-peer LRU caches ---
    caches = [_LRUCache(cache_cap) for _ in range(n_peers)]

    # --- Initialize peer inventories ---
    # Tier A: all peers hold all Tier A artifacts (canonical infrastructure)
    # Tier B: each peer holds ~60% of Tier B artifacts
    # Tier C: each peer holds ~20% of Tier C artifacts
    peer_inventories: list[dict[str, set[int]]] = []
    for _ in range(n_peers):
        inv_b_size = max(1, tier_counts[_TIER_B] * _TIER_B_PEER_INVENTORY_FRACTION // 10)
        inv_c_size = max(1, tier_counts[_TIER_C] * _TIER_C_PEER_INVENTORY_FRACTION // 10)
        peer_inventories.append(
            {
                _TIER_A: set(range(tier_counts[_TIER_A])),
                _TIER_B: set(
                    rng.sample(
                        range(tier_counts[_TIER_B]),
                        min(inv_b_size, tier_counts[_TIER_B]),
                    )
                ),
                _TIER_C: set(
                    rng.sample(
                        range(tier_counts[_TIER_C]),
                        min(inv_c_size, tier_counts[_TIER_C]),
                    )
                ),
            }
        )

    # --- Aggregate counters ---
    total_fetch: dict[str, int] = {_TIER_A: 0, _TIER_B: 0, _TIER_C: 0}
    want_have_hits: int = 0
    want_have_misses: int = 0
    wb_success: int = 0
    wb_error_404: int = 0
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
    serve_pressure: dict[int, int] = {p: 0 for p in range(n_peers)}

    # --- Simulation loop ---
    for _epoch in range(n_epochs):
        # Tier B cache invalidation at epoch boundary (Tier B content is mutable
        # per epoch; Tier A is immutable and remains in cache across epochs)
        for p in range(n_peers):
            new_cache = _LRUCache(cache_cap)
            for key in list(caches[p]._data):
                if key[0] == _TIER_A:
                    new_cache.put(key)
            caches[p] = new_cache

        # OOM guard: requests per epoch capped at max_requests_per_epoch
        n_requests = min(n_agents * 3, max_req)

        # Per-peer request counter for circuit breaker (reset each epoch)
        peer_req_count = [0] * n_peers

        for _ in range(n_requests):
            # Select tier by rate thresholds
            roll = Decimal(str(rng.random()))
            if roll < rate_a:
                tier = _TIER_A
            elif roll < rate_a + rate_b:
                tier = _TIER_B
            else:
                tier = _TIER_C

            # Select artifact within tier
            art_id = rng.randint(0, tier_counts[tier] - 1)

            # Select serving peer (uniform baseline)
            peer_id = rng.randint(0, n_peers - 1)
            serve_pressure[peer_id] += 1

            # Circuit breaker check (CDL-077 rate-limit model)
            if peer_req_count[peer_id] >= cb_threshold:
                wb_error_429 += 1
                cb_activations += 1
                continue
            peer_req_count[peer_id] += 1

            total_fetch[tier] += 1

            # WANT-HAVE probe: does this peer hold this artifact?
            has_artifact = art_id in peer_inventories[peer_id][tier]

            if not has_artifact:
                # WANT-HAVE miss → WANT-BLOCK error 404
                want_have_misses += 1
                wb_error_404 += 1
                if tier == _TIER_A:
                    cache_attempts_a += 1
                elif tier == _TIER_C:
                    cache_attempts_c += 1
                    non_cacheable_vol += 1  # Tier C: no mandatory caching
                continue

            # WANT-HAVE hit → proceed to WANT-BLOCK
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
                cdl_078_credits += 1  # Tier A serves credit CDL-078 routing reputation
            elif tier == _TIER_B:
                if not in_cache:
                    caches[peer_id].put(cache_key)
                bytes_by_tier[_TIER_B] += _BYTES_PER_TIER[_TIER_B]
                cdl_078_credits += 1  # Tier B hot-operational serves also credited
            else:
                # Tier C: no mandatory caching per CDL-087 §3
                cache_attempts_c += 1
                if in_cache:
                    cache_hits_c += 1
                else:
                    caches[peer_id].put(cache_key)
                bytes_by_tier[_TIER_C] += _BYTES_PER_TIER[_TIER_C]
                non_cacheable_vol += 1  # All Tier C requests are non-cacheable by policy

    # --- Compute aggregate rates ---
    total_want_have = want_have_hits + want_have_misses
    total_requests = (
        total_fetch[_TIER_A] + total_fetch[_TIER_B] + total_fetch[_TIER_C] + wb_error_429
    )

    wh_hit_rate = _safe_ratio(want_have_hits, total_want_have)
    wh_miss_rate = _safe_ratio(want_have_misses, total_want_have)
    cache_rate_a = _safe_ratio(cache_hits_a, cache_attempts_a)
    cache_rate_c = _safe_ratio(cache_hits_c, cache_attempts_c)
    failure_rate_str = _safe_ratio(
        wb_error_404 + wb_error_429, max(total_requests, 1)
    )

    # serve_pressure_by_peer: string keys for JSON safety
    spp = {f"peer_{p}": serve_pressure[p] for p in range(n_peers)}

    # --- Compute verdict ---
    verdict = _compute_verdict(
        cache_rate_a=Decimal(cache_rate_a),
        failure_rate=Decimal(failure_rate_str),
        tier_a_fraction=(
            Decimal(total_fetch[_TIER_A]) / Decimal(max(total_requests, 1))
        ),
        cb_fraction=Decimal(cb_activations) / Decimal(max(total_requests, 1)),
        spp=spp,
        total_requests=total_requests,
    )

    return {
        "sim": "SIM-FETCH-01",
        "sim_version": SIM_FETCH_01_HARNESS_VERSION,
        "cdl_087_dependency": CDL_087_DEPENDENCY,
        "cdl_087_ratification_authorized": False,
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
            "cache_capacity_per_peer": cache_cap,
            "max_requests_per_epoch": max_req,
            "seed": seed,
        },
        "aggregate_over_epochs": {
            # CDL-087 §6 required signals (exact names)
            "fetch_requests_by_tier": {
                "A": total_fetch[_TIER_A],
                "B": total_fetch[_TIER_B],
                "C": total_fetch[_TIER_C],
            },
            "want_have_hit_rate": wh_hit_rate,
            "want_have_miss_rate": wh_miss_rate,
            "want_block_success_count": wb_success,
            "want_block_error_404": wb_error_404,
            "want_block_error_429": wb_error_429,
            "want_block_error_400": wb_error_400,
            "cache_hit_rate_tier_a": cache_rate_a,
            "bytes_served_by_tier": {
                "A": str(bytes_by_tier[_TIER_A]),
                "B": str(bytes_by_tier[_TIER_B]),
                "C": str(bytes_by_tier[_TIER_C]),
            },
            "non_cacheable_request_volume": non_cacheable_vol,
            "circuit_breaker_activations": cb_activations,
            "serve_events_credited_cdl_078": cdl_078_credits,
            # Derived aliases required by Phase 1238 test contract (design spec §5)
            "cache_hit_rate_high_centrality": cache_rate_a,  # alias for cache_hit_rate_tier_a
            "cache_hit_rate_tail": cache_rate_c,
            "request_pressure_by_tier": {
                "A": total_fetch[_TIER_A],
                "B": total_fetch[_TIER_B],
                "C": total_fetch[_TIER_C],
            },
            "serve_pressure_by_peer": spp,
            "failure_rate": failure_rate_str,
        },
        "verdict": verdict,
    }
