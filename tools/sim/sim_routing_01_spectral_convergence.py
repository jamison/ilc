#!/usr/bin/env python3
"""
SIM-ROUTING-01: spectral routing convergence validation.

Gate: H-009 positive (SIM-BEACON-01 noise budget calibrated).

Questions:
  1. Does greedy spectral descent (hop toward peer with lowest
     spectral_distance to target fingerprint) converge to the target
     epistemic cluster reliably?
  2. How does it compare to a random walk and a naive DHT baseline?
  3. What failure modes exist, and how does beacon noise degrade routing?

Inputs (all from committed H-series results):
  - H-006b local-lambda2 cluster centers as spectral fingerprints
  - SIM-BEACON-01 recommended noise sigma=0.005 as observed fingerprint noise
  - SIM-BEACON-01 scale jitter (N=500: 0.0025, N=10000: 0.0015)
  - MAX_PEERS=16 from gossip peer registry (ilc_core/network/d2d/gossip_peer_registry.py)

No runtime code is mutated here.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

from ilc_core.analysis.spectral_utils import spectral_distance


# ---------------------------------------------------------------------------
# Constants from committed H-series results
# ---------------------------------------------------------------------------

# H-006b local-lambda2 cluster centers (ascending order, 4 clusters).
CLUSTER_CENTERS: list[float] = [0.123813, 0.153647, 0.163024, 0.172453]

# SIM-BEACON-01: recommended noise sigma for spectral beacon emission.
BEACON_SIGMA: float = 0.005

# Per-regime cluster jitter (from SIM-BEACON-01; see that script for derivation notes).
SCALE_JITTER: dict[str, float] = {
    "N500": 0.0025,
    "N10000": 0.0015,
}

# Network sizes per regime.
SCALE_N: dict[str, int] = {
    "N500": 500,
    "N10000": 10_000,
}

# Bounded peer count from D2d gossip peer registry MAX_PEERS.
MAX_PEERS: int = 16

# Max hops before declaring routing failure (3 * ceil(log2(N))).
MAX_HOPS_FACTOR: int = 3

# Monte Carlo trials per regime.
N_TRIALS: int = 2_000

# Random seed for reproducibility.
SEED: int = 42


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class RoutingResult:
    converged: bool
    hops: int
    failure_mode: str  # "": success; "cycle": revisited node; "max_hops": budget exhausted


@dataclass
class AlgorithmStats:
    convergence_rate: float
    mean_hops: float           # mean over SUCCESSFUL trials only
    median_hops: float         # median over successful trials only
    failure_cycle: int         # count of cycle failures
    failure_max_hops: int      # count of max-hops failures
    failure_no_peers: int      # count of dead-end failures


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def _build_random_graph(n: int, k: int, rng: np.random.Generator) -> list[list[int]]:
    """Build a random k-peer overlay graph.

    Each node receives k peers sampled uniformly at random (without self-loops).
    Edges are directed for simplicity; the routing algorithms use the adjacency
    list as-is.  For n > k, every node has exactly k peers.
    """
    peers: list[list[int]] = []
    all_nodes = np.arange(n)
    for i in range(n):
        candidates = np.delete(all_nodes, i)
        chosen = rng.choice(candidates, size=min(k, n - 1), replace=False)
        peers.append(chosen.tolist())
    return peers


# ---------------------------------------------------------------------------
# Validator population
# ---------------------------------------------------------------------------

@dataclass
class ValidatorPopulation:
    clusters: list[int]         # cluster assignment per validator
    true_fps: list[list[float]] # true (unnoised) spectral fingerprint
    obs_fps: list[list[float]]  # observed (noised by BEACON_SIGMA) fingerprint
    dht_ids: list[float]        # uniform [0,1] ID for DHT baseline


def _build_population(
    n: int,
    scale_jitter: float,
    rng: np.random.Generator,
) -> ValidatorPopulation:
    """Assign each validator to a cluster and generate spectral fingerprints.

    Validators are assigned to clusters round-robin (equal cluster sizes).
    True fingerprint = cluster_center + N(0, scale_jitter).
    Observed fingerprint = true_fingerprint + N(0, BEACON_SIGMA).
    DHT ID = uniform [0, 1].
    """
    n_clusters = len(CLUSTER_CENTERS)
    clusters = [i % n_clusters for i in range(n)]
    rng.shuffle(clusters)  # type: ignore[arg-type]

    centers = np.array(CLUSTER_CENTERS)
    true_vals = np.array([centers[c] for c in clusters])
    true_vals += rng.normal(0.0, scale_jitter, size=n)
    obs_vals = true_vals + rng.normal(0.0, BEACON_SIGMA, size=n)
    dht_ids = rng.uniform(0.0, 1.0, size=n)

    # Wrap as single-element lists (spectral_distance accepts List[float]).
    # Fingerprints are 1-dimensional (λ₂ only) because the H-006b cluster centers
    # are scalar values.  The full H-006b spectral embedding produces k-dimensional
    # fingerprints (k=4-8 eigenvectors); using those would improve cluster separation
    # and increase routing accuracy beyond what this simulation shows.  The 1D
    # constraint is a conservative lower bound on spectral routing performance.
    return ValidatorPopulation(
        clusters=clusters,
        true_fps=[[float(v)] for v in true_vals],
        obs_fps=[[float(v)] for v in obs_vals],
        dht_ids=dht_ids.tolist(),
    )


# ---------------------------------------------------------------------------
# Routing algorithms
# ---------------------------------------------------------------------------

def _route_spectral(
    source: int,
    target: int,
    pop: ValidatorPopulation,
    graph: list[list[int]],
    max_hops: int,
    use_true: bool = False,
) -> RoutingResult:
    """Greedy spectral descent routing.

    At each hop, move to the neighbor whose observed fingerprint has the
    smallest spectral_distance to the target's observed fingerprint.
    Terminates on cluster convergence, cycle detection, or max hops.

    Args:
        use_true: if True, use true (unnoised) fingerprints for routing;
                  comparing true vs. observed shows the noise penalty.
    """
    fps = pop.true_fps if use_true else pop.obs_fps
    target_fp = fps[target]
    target_cluster = pop.clusters[target]

    current = source
    visited: set[int] = {current}

    for hop in range(1, max_hops + 1):
        if pop.clusters[current] == target_cluster:
            return RoutingResult(converged=True, hops=hop - 1, failure_mode="")
        neighbors = graph[current]
        if not neighbors:
            return RoutingResult(converged=False, hops=hop, failure_mode="no_peers")
        best = min(neighbors, key=lambda nb: spectral_distance(fps[nb], target_fp))
        if best in visited:
            # hops=hop here is the attempt number when the cycle was detected, not
            # the count of completed movements.  Failure hops are excluded from
            # _aggregate's mean/median calculation so this asymmetry does not affect
            # the reported statistics.
            return RoutingResult(converged=False, hops=hop, failure_mode="cycle")
        visited.add(best)
        current = best

    converged = pop.clusters[current] == target_cluster
    return RoutingResult(
        converged=converged,
        hops=max_hops,
        failure_mode="" if converged else "max_hops",
    )


def _route_random(
    source: int,
    target: int,
    pop: ValidatorPopulation,
    graph: list[list[int]],
    max_hops: int,
    rng: np.random.Generator,
) -> RoutingResult:
    """Random walk baseline: hop to a uniformly random neighbor."""
    target_cluster = pop.clusters[target]
    current = source

    for hop in range(1, max_hops + 1):
        if pop.clusters[current] == target_cluster:
            return RoutingResult(converged=True, hops=hop - 1, failure_mode="")
        neighbors = graph[current]
        if not neighbors:
            return RoutingResult(converged=False, hops=hop, failure_mode="no_peers")
        current = int(rng.choice(neighbors))

    converged = pop.clusters[current] == target_cluster
    return RoutingResult(
        converged=converged,
        hops=max_hops,
        failure_mode="" if converged else "max_hops",
    )


def _route_dht(
    source: int,
    target: int,
    pop: ValidatorPopulation,
    graph: list[list[int]],
    max_hops: int,
) -> RoutingResult:
    """Naive DHT baseline: hop toward neighbor whose DHT ID is closest to target.

    DHT routing optimises for ID-space proximity, not epistemic cluster membership.
    This baseline isolates how much of spectral routing's advantage is attributable
    to the spectral signal vs. any structured graph traversal.
    """
    target_dht = pop.dht_ids[target]
    target_cluster = pop.clusters[target]

    current = source
    visited: set[int] = {current}

    for hop in range(1, max_hops + 1):
        if pop.clusters[current] == target_cluster:
            return RoutingResult(converged=True, hops=hop - 1, failure_mode="")
        neighbors = graph[current]
        if not neighbors:
            return RoutingResult(converged=False, hops=hop, failure_mode="no_peers")
        best = min(neighbors, key=lambda nb: abs(pop.dht_ids[nb] - target_dht))
        if best in visited:
            return RoutingResult(converged=False, hops=hop, failure_mode="cycle")
        visited.add(best)
        current = best

    converged = pop.clusters[current] == target_cluster
    return RoutingResult(
        converged=converged,
        hops=max_hops,
        failure_mode="" if converged else "max_hops",
    )


# ---------------------------------------------------------------------------
# Statistics aggregation
# ---------------------------------------------------------------------------

def _aggregate(results: list[RoutingResult]) -> AlgorithmStats:
    n = len(results)
    successes = [r for r in results if r.converged]
    hop_counts = [r.hops for r in successes]
    return AlgorithmStats(
        convergence_rate=round(len(successes) / n, 4),
        mean_hops=round(float(np.mean(hop_counts)), 2) if hop_counts else 0.0,
        median_hops=round(float(np.median(hop_counts)), 2) if hop_counts else 0.0,
        failure_cycle=sum(1 for r in results if r.failure_mode == "cycle"),
        failure_max_hops=sum(1 for r in results if r.failure_mode == "max_hops"),
        failure_no_peers=sum(1 for r in results if r.failure_mode == "no_peers"),
    )


def _stats_dict(s: AlgorithmStats) -> dict[str, object]:
    return {
        "convergence_rate": s.convergence_rate,
        "mean_hops_on_success": s.mean_hops,
        "median_hops_on_success": s.median_hops,
        "failure_cycle": s.failure_cycle,
        "failure_max_hops": s.failure_max_hops,
        "failure_no_peers": s.failure_no_peers,
    }


# ---------------------------------------------------------------------------
# Trial runner
# ---------------------------------------------------------------------------

def _run_scale(
    scale_name: str,
    rng: np.random.Generator,
) -> dict[str, object]:
    n = SCALE_N[scale_name]
    scale_jitter = SCALE_JITTER[scale_name]
    max_hops = MAX_HOPS_FACTOR * math.ceil(math.log2(n))

    pop = _build_population(n, scale_jitter, rng)
    graph = _build_random_graph(n, MAX_PEERS, rng)
    n_clusters = len(CLUSTER_CENTERS)

    # Precompute per-cluster candidate arrays for O(1) trial setup.
    # For each cluster c, non_cluster_arrays[c] holds all validators NOT in cluster c.
    # This avoids an O(n) scan per trial (2000 trials × N=10000 = 20M ops otherwise).
    cluster_members: list[list[int]] = [[] for _ in range(n_clusters)]
    for idx, c in enumerate(pop.clusters):
        cluster_members[c].append(idx)
    non_cluster_arrays: list[np.ndarray] = []
    for c in range(n_clusters):
        others = [v for oc, members in enumerate(cluster_members) if oc != c for v in members]
        non_cluster_arrays.append(np.array(others, dtype=np.intp))

    spectral_results: list[RoutingResult] = []
    spectral_true_results: list[RoutingResult] = []
    random_results: list[RoutingResult] = []
    dht_results: list[RoutingResult] = []

    for _ in range(N_TRIALS):
        # Source and target must be in different clusters.
        source = int(rng.integers(0, n))
        source_cluster = pop.clusters[source]
        target = int(rng.choice(non_cluster_arrays[source_cluster]))

        spectral_results.append(
            _route_spectral(source, target, pop, graph, max_hops, use_true=False)
        )
        spectral_true_results.append(
            _route_spectral(source, target, pop, graph, max_hops, use_true=True)
        )
        random_results.append(
            _route_random(source, target, pop, graph, max_hops, rng)
        )
        dht_results.append(
            _route_dht(source, target, pop, graph, max_hops)
        )

    spectral_stats = _aggregate(spectral_results)
    spectral_true_stats = _aggregate(spectral_true_results)
    random_stats = _aggregate(random_results)
    dht_stats = _aggregate(dht_results)

    noise_penalty = round(
        spectral_true_stats.convergence_rate - spectral_stats.convergence_rate, 4
    )

    return {
        "n": n,
        "max_hops": max_hops,
        "scale_jitter": scale_jitter,
        "spectral_noisy": _stats_dict(spectral_stats),
        "spectral_true": _stats_dict(spectral_true_stats),
        "random_walk": _stats_dict(random_stats),
        "dht_naive": _stats_dict(dht_stats),
        "noise_penalty_convergence_rate": noise_penalty,
        "spectral_vs_random_lift": round(
            spectral_stats.convergence_rate - random_stats.convergence_rate, 4
        ),
        "spectral_vs_dht_lift": round(
            spectral_stats.convergence_rate - dht_stats.convergence_rate, 4
        ),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    rng = np.random.default_rng(SEED)

    output: dict[str, object] = {
        "inputs": {
            "cluster_centers": CLUSTER_CENTERS,
            "beacon_sigma": BEACON_SIGMA,
            "max_peers": MAX_PEERS,
            "n_trials": N_TRIALS,
            "max_hops_factor": MAX_HOPS_FACTOR,
            "seed": SEED,
        },
        "scale_results": {},
    }

    for scale_name in ("N500", "N10000"):
        output["scale_results"][scale_name] = _run_scale(scale_name, rng)  # type: ignore[index]

    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
