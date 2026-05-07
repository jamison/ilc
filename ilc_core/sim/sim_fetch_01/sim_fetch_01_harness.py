from __future__ import annotations

# SIM-FETCH-01: Canonical Fetch Distribution Simulation Harness
#
# Phase 1238c — Window 1233-1240 (Fix3: tier-stratified metrics + verdict decomposition)
# Governing authority: docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md
#
# CDL-087 ratification is NOT authorized by this harness.
#
# This module lives in ilc_core/sim/ (not a sensitive taboo scan root).
# It uses _DeterministicRNG, a SHA-256 counter-mode PRNG, for reproducible
# simulation. This PRNG must NOT be imported or used in any production protocol
# code path. Production code must use secrets.SystemRandom() for stochastic needs.

import hashlib
from bisect import bisect_left
from collections import OrderedDict
from decimal import Decimal, InvalidOperation
from typing import Any

SIM_FETCH_01_HARNESS_VERSION = "sim_fetch_01_harness_1238c.v0.1"
SIM_FETCH_01_FIX1_VERSION = "sim_fetch_01_fix1_hardening_1238a.v0.1"
SIM_FETCH_01_FIX2_VERSION = "sim_fetch_01_fix2_request_model_1238b.v0.1"
SIM_FETCH_01_FIX3_VERSION = "sim_fetch_01_fix3_tier_verdict_1238c.v0.1"
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

# Default fraction of tier inventory each peer initially holds (configurable in Fix4)
_DEFAULT_TIER_B_PEER_INVENTORY_FRACTION = 6  # 60%
_DEFAULT_TIER_C_PEER_INVENTORY_FRACTION = 2  # 20%

# Default Zipf exponents (s=1.0 for Tier A canonical content; s=0.5 lighter tail for Tier B)
_DEFAULT_ZIPF_EXPONENT_TIER_A = Decimal("1.0")
_DEFAULT_ZIPF_EXPONENT_TIER_B = Decimal("0.5")


class _DeterministicRNG:
    """
    Deterministic hash-derived PRNG for SIM-FETCH-01 simulation only.

    Uses SHA-256 in counter mode: each draw is sha256(seed_bytes || counter_bytes).
    The counter increments monotonically across all draws within one simulation run.

    Contract: identical seed + draw sequence → identical output.
    Must NOT be used in production protocol code (use secrets.SystemRandom).
    """

    def __init__(self, seed: int) -> None:
        # Mask to unsigned 64-bit to handle any integer seed value
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
        # Divide by 2^64 — exact in Decimal arithmetic
        return Decimal(val) / Decimal("18446744073709551616")

    def poisson_count(self, n_agents: int, avg_per_agent: Decimal) -> int:
        """
        Poisson-like total request count for an epoch.

        Models n_agents agents, each making avg_per_agent requests.
        Each agent contributes floor(avg) requests unconditionally,
        plus 1 additional request with probability frac(avg) (Bernoulli trial).

        Expected total = n_agents * avg_per_agent.
        For integer avg, result is deterministic (no variance).
        This is a Binomial approximation of the Poisson process.
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
    """
    Build cumulative distribution for Zipf(n, exponent).

    P(rank k) ∝ 1/k^exponent for k=1..n. Rank 1 is most popular.
    Returns list of n cumulative probabilities; last entry is exactly 1.
    """
    weights = [Decimal(1) / (Decimal(k) ** exponent) for k in range(1, n + 1)]
    total = sum(weights)
    cdf: list[Decimal] = []
    running = Decimal("0")
    for w in weights:
        running += w / total
        cdf.append(running)
    cdf[-1] = Decimal("1")  # Ensure last entry is exactly 1 (no floating rounding)
    return cdf


def _zipf_draw(rng: _DeterministicRNG, cdf: list[Decimal]) -> int:
    """
    Draw artifact index from pre-built Zipf CDF.
    Returns 0-indexed artifact ID (rank 1 → index 0, most popular).

    Uses bisect_left: cdf is monotonically increasing, last entry is exactly 1,
    and rng.fraction() returns values in [0, 1), so the result is always in-bounds.
    """
    return bisect_left(cdf, rng.fraction())


def _compute_top_quartile_concentration(req_counts: dict[int, int]) -> str:
    """
    Fraction of total requests served by the top 25% of artifacts (by popularity).

    A Zipf distribution should produce concentration >> uniform (where it would be ~0.25).
    """
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
    """Convert a rate value to Decimal with strict validation.

    Rejects: float (precision), bool (type confusion), out-of-range [0, 1],
    non-finite Decimal.
    """
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
    """Convert a positive Decimal parameter, rejecting float, bool, and out-of-range."""
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
    Apply SIM-FETCH-01 aggregate pass/fail thresholds (design spec §7).

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
    This verdict reflects that reality by excluding Tier C from the failure rate.

    This is NOT a CDL-087 ratification verdict. CDL-087 ratification is not
    authorized by this harness regardless of this verdict's value. A spec amendment
    is required before this verdict can be used as a ratification input.
    """
    if total_tier_ab_requests < 100:
        return "inconclusive"
    if not cache_rate_a.is_finite() or not tier_ab_failure_rate.is_finite():
        return "inconclusive"

    # Block conditions
    if cache_rate_a < Decimal("0.50"):
        return "fail"
    if tier_ab_failure_rate > Decimal("0.20"):
        return "fail"
    if cb_fraction > Decimal("0.20"):
        return "fail"

    # Support conditions
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

    # --- Validate Zipf exponents ---
    zipf_exp_a = _to_pos_decimal(
        scenario_config.get("zipf_exponent_tier_a", str(_DEFAULT_ZIPF_EXPONENT_TIER_A)),
        "zipf_exponent_tier_a",
        Decimal("0.1"),
        Decimal("5.0"),
    )
    zipf_exp_b = _to_pos_decimal(
        scenario_config.get("zipf_exponent_tier_b", str(_DEFAULT_ZIPF_EXPONENT_TIER_B)),
        "zipf_exponent_tier_b",
        Decimal("0.1"),
        Decimal("5.0"),
    )

    # --- Validate avg requests per agent ---
    avg_per_agent = _to_pos_decimal(
        scenario_config.get("avg_requests_per_agent", "3"),
        "avg_requests_per_agent",
        Decimal("0.01"),
        Decimal("100"),
    )

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
    cb_threshold_raw = scenario_config.get(
        "circuit_breaker_threshold", max(max_req // n_peers, 1)
    )
    if (
        isinstance(cb_threshold_raw, bool)
        or not isinstance(cb_threshold_raw, int)
        or cb_threshold_raw < 1
    ):
        raise ValueError("sim_fetch_01_invalid_circuit_breaker_threshold")
    cb_threshold: int = cb_threshold_raw

    # --- Hash-derived deterministic PRNG (simulation only; not for protocol use) ---
    rng = _DeterministicRNG(seed)

    # --- Pre-compute Zipf CDFs (once per run, not per epoch) ---
    # Tier A and Tier B use Zipf artifact selection to model hot-artifact concentration.
    # Tier C uses uniform selection (no infrastructure-grade caching obligation).
    cdf_a = _build_zipf_cdf(tier_counts[_TIER_A], zipf_exp_a)
    cdf_b = _build_zipf_cdf(tier_counts[_TIER_B], zipf_exp_b)

    # --- Initialize per-peer LRU caches ---
    caches = [_LRUCache(cache_cap) for _ in range(n_peers)]

    # --- Initialize peer inventories ---
    tier_b_frac = scenario_config.get(
        "tier_b_peer_inventory_fraction", _DEFAULT_TIER_B_PEER_INVENTORY_FRACTION
    )
    tier_c_frac = scenario_config.get(
        "tier_c_peer_inventory_fraction", _DEFAULT_TIER_C_PEER_INVENTORY_FRACTION
    )
    if isinstance(tier_b_frac, bool) or not isinstance(tier_b_frac, int) or not (1 <= tier_b_frac <= 10):
        raise ValueError("sim_fetch_01_invalid_tier_b_peer_inventory_fraction")
    if isinstance(tier_c_frac, bool) or not isinstance(tier_c_frac, int) or not (1 <= tier_c_frac <= 10):
        raise ValueError("sim_fetch_01_invalid_tier_c_peer_inventory_fraction")

    peer_inventories: list[dict[str, set[int]]] = []
    for _ in range(n_peers):
        inv_b_size = max(1, tier_counts[_TIER_B] * tier_b_frac // 10)
        inv_c_size = max(1, tier_counts[_TIER_C] * tier_c_frac // 10)
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
    serve_pressure: dict[int, int] = {p: 0 for p in range(n_peers)}

    # Per-artifact request counts for popularity / concentration metrics
    artifact_req_counts: dict[str, dict[int, int]] = {
        _TIER_A: {},
        _TIER_B: {},
        _TIER_C: {},
    }

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

        # Poisson-like per-epoch request count (replaces fixed n_agents * 3)
        # OOM guard: still capped at max_requests_per_epoch
        n_requests = min(rng.poisson_count(n_agents, avg_per_agent), max_req)

        # Per-peer request counter for circuit breaker (reset each epoch)
        peer_req_count = [0] * n_peers

        for _ in range(n_requests):
            # Select tier by rate thresholds using deterministic RNG
            roll = rng.fraction()
            if roll < rate_a:
                tier = _TIER_A
            elif roll < rate_a + rate_b:
                tier = _TIER_B
            else:
                tier = _TIER_C

            # Select artifact within tier:
            # Tier A/B: Zipf distribution (models hot-artifact concentration)
            # Tier C: uniform (no mandatory caching; no infrastructure hot-spot model)
            if tier == _TIER_A:
                art_id = _zipf_draw(rng, cdf_a)
            elif tier == _TIER_B:
                art_id = _zipf_draw(rng, cdf_b)
            else:
                art_id = rng.randint(0, tier_counts[_TIER_C] - 1)

            # Track per-artifact request volume for popularity metrics
            artifact_req_counts[tier][art_id] = artifact_req_counts[tier].get(art_id, 0) + 1

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
                wb_error_404_by_tier[tier] += 1
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
                cdl_078_credits += 1  # Tier A successful serves credit CDL-078 reputation
            elif tier == _TIER_B:
                if not in_cache:
                    caches[peer_id].put(cache_key)
                bytes_by_tier[_TIER_B] += _BYTES_PER_TIER[_TIER_B]
                cdl_078_credits += 1  # Tier B successful serves also credited
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

    # --- Per-tier failure rates (Fix3) ---
    # CDL-087 §3: Tier C has no infrastructure-grade service obligation.
    # These per-tier rates expose the failure profile without conflating tiers.
    failure_rate_by_tier = {
        _TIER_A: _safe_ratio(wb_error_404_by_tier[_TIER_A], max(total_fetch[_TIER_A], 1)),
        _TIER_B: _safe_ratio(wb_error_404_by_tier[_TIER_B], max(total_fetch[_TIER_B], 1)),
        _TIER_C: _safe_ratio(wb_error_404_by_tier[_TIER_C], max(total_fetch[_TIER_C], 1)),
    }
    total_tier_ab = total_fetch[_TIER_A] + total_fetch[_TIER_B]
    tier_ab_failure_rate_str = _safe_ratio(
        wb_error_404_by_tier[_TIER_A] + wb_error_404_by_tier[_TIER_B],
        max(total_tier_ab, 1),
    )
    tier_c_advisory_failure_rate_str = failure_rate_by_tier[_TIER_C]

    tier_service_verdict = _compute_tier_service_verdict(
        cache_rate_a=Decimal(cache_rate_a),
        tier_ab_failure_rate=Decimal(tier_ab_failure_rate_str),
        cb_fraction=Decimal(cb_activations) / Decimal(max(total_requests, 1)),
        spp=spp,
        total_tier_ab_requests=total_tier_ab,
    )

    # Artifact popularity: top-quartile concentration by tier
    top_q_concentration = {
        t: _compute_top_quartile_concentration(artifact_req_counts[t]) for t in _TIERS
    }

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
            "zipf_exponent_tier_a": str(zipf_exp_a),
            "zipf_exponent_tier_b": str(zipf_exp_b),
            "avg_requests_per_agent": str(avg_per_agent),
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
            # Derived aliases (design spec §5 test contract)
            "cache_hit_rate_high_centrality": cache_rate_a,
            "cache_hit_rate_tail": cache_rate_c,
            "request_pressure_by_tier": {
                "A": total_fetch[_TIER_A],
                "B": total_fetch[_TIER_B],
                "C": total_fetch[_TIER_C],
            },
            "serve_pressure_by_peer": spp,
            "failure_rate": failure_rate_str,
            # Fix2: artifact popularity / Zipf concentration metrics
            "top_quartile_request_concentration_by_tier": top_q_concentration,
            # Fix3: tier-stratified failure rates
            # CDL-087 §3: Tier C has no infrastructure-grade service obligation.
            # These rates expose the per-tier failure profile without conflating tiers.
            "failure_rate_by_tier": failure_rate_by_tier,
            "tier_ab_failure_rate": tier_ab_failure_rate_str,
            "tier_c_advisory_failure_rate": tier_c_advisory_failure_rate_str,
        },
        # aggregate_verdict: backward-compatible alias for verdict (Fix3)
        "aggregate_verdict": verdict,
        # tier_service_verdict: Tier A+B only — INFORMATIONAL, NOT CDL-087 ratification.
        # A spec amendment is required before this can be used as a ratification input.
        "tier_service_verdict": tier_service_verdict,
        "cdl_087_ratification_not_authorized_note": (
            "tier_service_verdict does not authorize CDL-087 ratification"
        ),
        "verdict": verdict,
    }
