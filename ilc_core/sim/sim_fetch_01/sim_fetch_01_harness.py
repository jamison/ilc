from __future__ import annotations

# SIM-FETCH-01: Canonical Fetch Distribution Simulation Harness
#
# Phase 1238d — Window 1233-1240 (Fix4: routed holder model)
# Governing authority: docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md
#
# CDL-087 ratification is NOT authorized by this harness.
#
# This module lives in ilc_core/sim/ (not a sensitive taboo scan root).
# It uses _DeterministicRNG (SHA-256 counter-mode) for reproducible simulation.
# This PRNG must NOT be imported or used in any production protocol code path.
# Production code must use secrets.SystemRandom() for stochastic needs.

import hashlib
from bisect import bisect_left
from collections import OrderedDict
from decimal import Decimal, InvalidOperation
from typing import Any

SIM_FETCH_01_HARNESS_VERSION = "sim_fetch_01_harness_1238d.v0.1"
SIM_FETCH_01_FIX1_VERSION = "sim_fetch_01_fix1_hardening_1238a.v0.1"
SIM_FETCH_01_FIX2_VERSION = "sim_fetch_01_fix2_request_model_1238b.v0.1"
SIM_FETCH_01_FIX3_VERSION = "sim_fetch_01_fix3_tier_verdict_1238c.v0.1"
SIM_FETCH_01_FIX4_VERSION = "sim_fetch_01_fix4_routed_holder_model_1238d.v0.1"
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


def run_sim_fetch_01(scenario_config: dict) -> dict:
    """
    Run SIM-FETCH-01 fetch distribution simulation.

    Returns metrics under two availability models in parallel:

    single_hop_random_*: Null model — uniform random peer selection. Worst-case
        availability; shows what happens when the requester has no routing signal.

    routed_*: Holder-directory model — requests routed to known holders of each
        artifact. Zero failures for replicated artifacts under zero directory staleness.
        CDL-087 evaluation should use routed_ metrics, not random_ metrics.

    Both models process the same tiers and artifacts per epoch; only peer selection
    and circuit-breaker behavior differ (routed model has no CB in Fix4).

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
    serve_pressure: dict[int, int] = {p: 0 for p in range(n_peers)}
    artifact_req_counts: dict[str, dict[int, int]] = {_TIER_A: {}, _TIER_B: {}, _TIER_C: {}}

    # --- Aggregate counters: routed holder model (Fix4) ---
    # No circuit breaker in routed model (Fix4 scope: availability only; CB behavior deferred to Fix5)
    routed_total_fetch: dict[str, int] = {_TIER_A: 0, _TIER_B: 0, _TIER_C: 0}
    routed_error_404_by_tier: dict[str, int] = {_TIER_A: 0, _TIER_B: 0, _TIER_C: 0}
    routed_holder_lookups: int = 0      # Requests where directory lookup was attempted
    routed_holder_found: int = 0        # Requests routed to a known holder (not stale, has holders)
    routed_stale_fallbacks: int = 0     # Lookups that fell back due to directory staleness

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

            # === ROUTED HOLDER MODEL (Fix4) ===
            # Processed before random-model peer selection so it is not affected by CB.
            # Routed model: route to a known holder; fall back to random if directory is stale.
            routed_holder_lookups += 1
            holders = holder_directory[tier][art_id]

            if not holders:
                # Artifact not replicated on any peer — genuine 404 regardless of routing
                routed_total_fetch[tier] += 1
                routed_error_404_by_tier[tier] += 1
            else:
                # Determine if this directory lookup is stale
                is_stale = (
                    directory_staleness_rate > Decimal("0")
                    and rng_routed.fraction() < directory_staleness_rate
                )
                if is_stale:
                    # Stale: fall back to random peer (routed model degrades to random model)
                    routed_stale_fallbacks += 1
                    stale_peer = rng_routed.randint(0, n_peers - 1)
                    routed_total_fetch[tier] += 1
                    if art_id not in peer_inventories[stale_peer][tier]:
                        routed_error_404_by_tier[tier] += 1
                else:
                    # Fresh directory + known holders → route to a holder (always succeeds)
                    routed_holder_found += 1
                    holder_list = sorted(holders)  # Sorted for determinism
                    routed_peer = holder_list[rng_routed.randint(0, len(holder_list) - 1)]
                    routed_total_fetch[tier] += 1
                    # Holder definitely has the artifact — no 404

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
            elif tier == _TIER_B:
                if not in_cache:
                    caches[peer_id].put(cache_key)
                bytes_by_tier[_TIER_B] += _BYTES_PER_TIER[_TIER_B]
                cdl_078_credits += 1
            else:
                cache_attempts_c += 1
                if in_cache:
                    cache_hits_c += 1
                else:
                    caches[peer_id].put(cache_key)
                bytes_by_tier[_TIER_C] += _BYTES_PER_TIER[_TIER_C]
                non_cacheable_vol += 1

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

    # --- Routed model metrics (Fix4) ---
    total_routed = sum(routed_total_fetch.values())
    routed_failure_rate_by_tier = {
        _TIER_A: _safe_ratio(routed_error_404_by_tier[_TIER_A], max(routed_total_fetch[_TIER_A], 1)),
        _TIER_B: _safe_ratio(routed_error_404_by_tier[_TIER_B], max(routed_total_fetch[_TIER_B], 1)),
        _TIER_C: _safe_ratio(routed_error_404_by_tier[_TIER_C], max(routed_total_fetch[_TIER_C], 1)),
    }
    total_tier_ab_routed = routed_total_fetch[_TIER_A] + routed_total_fetch[_TIER_B]
    routed_tier_ab_failure_rate = _safe_ratio(
        routed_error_404_by_tier[_TIER_A] + routed_error_404_by_tier[_TIER_B],
        max(total_tier_ab_routed, 1),
    )

    # Routed tier_service_verdict uses routed failure rates.
    # cache_rate_a from the random model is used as a proxy (same artifact distribution).
    # cb_fraction = 0 for routed model (no CB in Fix4).
    routed_tier_service_verdict = _compute_tier_service_verdict(
        cache_rate_a=Decimal(cache_rate_a),
        tier_ab_failure_rate=Decimal(routed_tier_ab_failure_rate),
        cb_fraction=Decimal("0"),
        spp=spp,
        total_tier_ab_requests=total_tier_ab_routed,
    )

    routed_holder_hit_rate = _safe_ratio(routed_holder_found, max(routed_holder_lookups, 1))
    routed_staleness_rate_observed = _safe_ratio(routed_stale_fallbacks, max(routed_holder_lookups, 1))

    # --- Holder count statistics (Fix4) ---
    holder_count_stats = {t: _holder_count_stats(holder_directory, t) for t in _TIERS}

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
            "routed_failure_rate_by_tier": routed_failure_rate_by_tier,
            "routed_tier_ab_failure_rate": routed_tier_ab_failure_rate,
            "routed_tier_service_verdict": routed_tier_service_verdict,
            "routed_holder_hit_rate": routed_holder_hit_rate,
            "routed_staleness_rate_observed": routed_staleness_rate_observed,
            # Fix4: holder directory coverage statistics
            "known_holder_count_stats_by_tier": holder_count_stats,
        },
        # Top-level verdicts
        "aggregate_verdict": verdict,
        "tier_service_verdict": rand_tier_service_verdict,   # backward compat alias
        "verdict": verdict,
    }
