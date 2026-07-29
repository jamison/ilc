#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
SIM-ROUTING-01: spectral routing convergence validation.

Gate: H-009 positive (SIM-BEACON-01 noise budget calibrated).

The simulation uses H-005 topology labels (T1-T4) and compares:
  - greedy spectral descent
  - greedy spectral descent with immediate random-walk fallback on cycle
  - random walk
  - naive DHT-style ID routing

No runtime code is mutated here. Deterministic NumPy PRNG use is simulation-only.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Callable

import numpy as np

from ilc_core.analysis.spectral_utils import spectral_distance


CLUSTER_CENTERS: list[float] = [0.123813, 0.153647, 0.163024, 0.172453]
BEACON_SIGMA: float = 0.005
THETA_FLOOR: float = 0.001
MAX_PEERS: int = 16
MAX_HOPS_FACTOR: int = 3
N_TRIALS: int = 2_000
SEED: int = 42

# Pass criteria are declared here and copied into the results artifact before
# the result tables. Partition-near T4 is a stress topology, so its convergence
# floor is lower but still bounded.
HEALTHY_CONVERGENCE_FLOOR: float = 0.85
PARTITION_NEAR_CONVERGENCE_FLOOR: float = 0.60
TWO_PHASE_CONVERGENCE_FLOOR: float = 0.80


@dataclass(frozen=True)
class TopologyProfile:
    name: str
    h005_class: str
    n: int
    centers: list[float]
    jitter: float
    graph_kind: str
    spectral_floor: float


TOPOLOGIES: tuple[TopologyProfile, ...] = (
    TopologyProfile(
        name="T1_random",
        h005_class="T1_random",
        n=500,
        centers=CLUSTER_CENTERS,
        jitter=0.0025,
        graph_kind="random",
        spectral_floor=HEALTHY_CONVERGENCE_FLOOR,
    ),
    TopologyProfile(
        name="T2_panel_heavy",
        h005_class="T2_panel_heavy",
        n=500,
        centers=CLUSTER_CENTERS,
        jitter=0.0020,
        graph_kind="panel_heavy",
        spectral_floor=HEALTHY_CONVERGENCE_FLOOR,
    ),
    TopologyProfile(
        name="T3_coalition_sparse",
        h005_class="T3_coalition_sparse",
        n=500,
        centers=CLUSTER_CENTERS,
        jitter=0.0035,
        graph_kind="coalition_sparse",
        spectral_floor=HEALTHY_CONVERGENCE_FLOOR,
    ),
    TopologyProfile(
        name="T4_partition_near",
        h005_class="T4_adversarial_sybil / partition-near stress",
        n=500,
        centers=[0.0012, 0.0100, 0.0200, 0.0310],
        jitter=0.0010,
        graph_kind="partition_near",
        spectral_floor=PARTITION_NEAR_CONVERGENCE_FLOOR,
    ),
)


@dataclass(frozen=True)
class RoutingResult:
    converged: bool
    hops: int
    failure_mode: str
    used_fallback: bool = False


@dataclass(frozen=True)
class ValidatorPopulation:
    clusters: list[int]
    obs_fps: list[list[float]]
    dht_ids: list[float]


def _build_population(profile: TopologyProfile, rng: np.random.Generator) -> ValidatorPopulation:
    n_clusters = len(profile.centers)
    clusters = [i % n_clusters for i in range(profile.n)]
    rng.shuffle(clusters)  # type: ignore[arg-type]

    centers = np.array(profile.centers)
    true_vals = np.array([centers[c] for c in clusters])
    true_vals += rng.normal(0.0, profile.jitter, size=profile.n)
    obs_vals = true_vals + rng.normal(0.0, BEACON_SIGMA, size=profile.n)
    dht_ids = rng.uniform(0.0, 1.0, size=profile.n)

    return ValidatorPopulation(
        clusters=clusters,
        obs_fps=[[float(v)] for v in obs_vals],
        dht_ids=dht_ids.tolist(),
    )


def _cluster_members(clusters: list[int]) -> dict[int, np.ndarray]:
    grouped: dict[int, list[int]] = {}
    for node_id, cluster in enumerate(clusters):
        grouped.setdefault(cluster, []).append(node_id)
    return {cluster: np.array(nodes, dtype=np.intp) for cluster, nodes in grouped.items()}


def _sample_peer(
    candidates: np.ndarray,
    *,
    exclude: int,
    size: int,
    rng: np.random.Generator,
) -> list[int]:
    candidates = candidates[candidates != exclude]
    if len(candidates) == 0 or size <= 0:
        return []
    chosen = rng.choice(candidates, size=min(size, len(candidates)), replace=False)
    return [int(v) for v in chosen]


def _build_graph(profile: TopologyProfile, pop: ValidatorPopulation, rng: np.random.Generator) -> list[list[int]]:
    n = profile.n
    all_nodes = np.arange(n, dtype=np.intp)
    by_cluster = _cluster_members(pop.clusters)
    graph: list[list[int]] = []

    for node_id, cluster in enumerate(pop.clusters):
        if profile.graph_kind == "random":
            peers = _sample_peer(all_nodes, exclude=node_id, size=MAX_PEERS, rng=rng)
        elif profile.graph_kind == "panel_heavy":
            same = _sample_peer(by_cluster[cluster], exclude=node_id, size=12, rng=rng)
            other = _sample_peer(all_nodes[pop.clusters != cluster] if isinstance(pop.clusters, np.ndarray) else np.array([i for i, c in enumerate(pop.clusters) if c != cluster], dtype=np.intp), exclude=node_id, size=4, rng=rng)
            peers = same + other
        elif profile.graph_kind == "coalition_sparse":
            same = _sample_peer(by_cluster[cluster], exclude=node_id, size=4, rng=rng)
            other = _sample_peer(np.array([i for i, c in enumerate(pop.clusters) if c != cluster], dtype=np.intp), exclude=node_id, size=2, rng=rng)
            peers = same + other
        elif profile.graph_kind == "partition_near":
            same = _sample_peer(by_cluster[cluster], exclude=node_id, size=10, rng=rng)
            # Sparse cross-cluster bridge keeps the graph near the partition-risk
            # boundary while still allowing routing to escape local neighborhoods.
            other = _sample_peer(np.array([i for i, c in enumerate(pop.clusters) if c != cluster], dtype=np.intp), exclude=node_id, size=1, rng=rng)
            peers = same + other
        else:
            raise ValueError(f"unknown_topology_kind:{profile.graph_kind}")
        graph.append(peers)
    return graph


def _route_greedy(
    source: int,
    target: int,
    pop: ValidatorPopulation,
    graph: list[list[int]],
    max_hops: int,
    *,
    fallback: bool,
    rng: np.random.Generator,
) -> RoutingResult:
    target_fp = pop.obs_fps[target]
    target_cluster = pop.clusters[target]
    current = source
    visited: set[int] = {current}

    for hop in range(1, max_hops + 1):
        if pop.clusters[current] == target_cluster:
            return RoutingResult(True, hop - 1, "", used_fallback=False)
        neighbors = graph[current]
        if not neighbors:
            return RoutingResult(False, hop - 1, "no_peers", used_fallback=False)
        best = min(neighbors, key=lambda nb: spectral_distance(pop.obs_fps[nb], target_fp))
        if best in visited:
            if not fallback:
                return RoutingResult(False, hop, "cycle", used_fallback=False)
            return _route_random(
                current,
                target,
                pop,
                graph,
                max_hops - (hop - 1),
                rng,
                used_fallback=True,
            )
        visited.add(best)
        current = best

    converged = pop.clusters[current] == target_cluster
    return RoutingResult(converged, max_hops, "" if converged else "max_hops")


def _route_random(
    source: int,
    target: int,
    pop: ValidatorPopulation,
    graph: list[list[int]],
    max_hops: int,
    rng: np.random.Generator,
    *,
    used_fallback: bool = False,
) -> RoutingResult:
    target_cluster = pop.clusters[target]
    current = source

    for hop in range(1, max_hops + 1):
        if pop.clusters[current] == target_cluster:
            return RoutingResult(True, hop - 1, "", used_fallback=used_fallback)
        neighbors = graph[current]
        if not neighbors:
            return RoutingResult(False, hop - 1, "no_peers", used_fallback=used_fallback)
        current = int(rng.choice(neighbors))

    converged = pop.clusters[current] == target_cluster
    return RoutingResult(
        converged,
        max_hops,
        "" if converged else "max_hops",
        used_fallback=used_fallback,
    )


def _route_dht(
    source: int,
    target: int,
    pop: ValidatorPopulation,
    graph: list[list[int]],
    max_hops: int,
) -> RoutingResult:
    target_dht = pop.dht_ids[target]
    target_cluster = pop.clusters[target]
    current = source
    visited: set[int] = {current}

    for hop in range(1, max_hops + 1):
        if pop.clusters[current] == target_cluster:
            return RoutingResult(True, hop - 1, "")
        neighbors = graph[current]
        if not neighbors:
            return RoutingResult(False, hop - 1, "no_peers")
        best = min(neighbors, key=lambda nb: abs(pop.dht_ids[nb] - target_dht))
        if best in visited:
            return RoutingResult(False, hop, "cycle")
        visited.add(best)
        current = best

    converged = pop.clusters[current] == target_cluster
    return RoutingResult(converged, max_hops, "" if converged else "max_hops")


def _aggregate(results: list[RoutingResult]) -> dict[str, object]:
    successes = [r for r in results if r.converged]
    hops = np.array([r.hops for r in successes], dtype=float)
    if len(hops) == 0:
        percentiles = {"p5": 0.0, "p50": 0.0, "p95": 0.0}
        mean_hops = 0.0
    else:
        p5, p50, p95 = np.percentile(hops, [5, 50, 95])
        percentiles = {
            "p5": round(float(p5), 2),
            "p50": round(float(p50), 2),
            "p95": round(float(p95), 2),
        }
        mean_hops = round(float(np.mean(hops)), 2)
    return {
        "convergence_rate": round(len(successes) / len(results), 4),
        "mean_hops_on_success": mean_hops,
        "hop_distribution": percentiles,
        "failure_cycle": sum(1 for r in results if r.failure_mode == "cycle"),
        "failure_max_hops": sum(1 for r in results if r.failure_mode == "max_hops"),
        "failure_no_peers": sum(1 for r in results if r.failure_mode == "no_peers"),
        "fallback_used": sum(1 for r in results if r.used_fallback),
    }


def _non_cluster_arrays(clusters: list[int]) -> list[np.ndarray]:
    n_clusters = len(set(clusters))
    arrays: list[np.ndarray] = []
    for cluster in range(n_clusters):
        arrays.append(np.array([i for i, c in enumerate(clusters) if c != cluster], dtype=np.intp))
    return arrays


def _run_profile(profile: TopologyProfile, rng: np.random.Generator) -> dict[str, object]:
    pop = _build_population(profile, rng)
    graph = _build_graph(profile, pop, rng)
    max_hops = MAX_HOPS_FACTOR * math.ceil(math.log2(profile.n))
    non_cluster = _non_cluster_arrays(pop.clusters)

    algorithms: dict[str, tuple[Callable[[int, int], RoutingResult], list[RoutingResult]]] = {
        "spectral_greedy": (
            lambda s, t: _route_greedy(s, t, pop, graph, max_hops, fallback=False, rng=rng),
            [],
        ),
        "spectral_two_phase": (
            lambda s, t: _route_greedy(s, t, pop, graph, max_hops, fallback=True, rng=rng),
            [],
        ),
        "random_walk": (
            lambda s, t: _route_random(s, t, pop, graph, max_hops, rng),
            [],
        ),
        "dht_naive": (
            lambda s, t: _route_dht(s, t, pop, graph, max_hops),
            [],
        ),
    }

    for _ in range(N_TRIALS):
        source = int(rng.integers(0, profile.n))
        target = int(rng.choice(non_cluster[pop.clusters[source]]))
        for route_fn, results in algorithms.values():
            results.append(route_fn(source, target))

    stats = {name: _aggregate(results) for name, (_fn, results) in algorithms.items()}
    greedy_pass = stats["spectral_greedy"]["convergence_rate"] >= profile.spectral_floor
    two_phase_pass = stats["spectral_two_phase"]["convergence_rate"] >= TWO_PHASE_CONVERGENCE_FLOOR

    return {
        "h005_class": profile.h005_class,
        "n": profile.n,
        "graph_kind": profile.graph_kind,
        "max_hops": max_hops,
        "spectral_floor": profile.spectral_floor,
        "near_partition": profile.name == "T4_partition_near",
        "stats": stats,
        "greedy_floor_pass": bool(greedy_pass),
        "two_phase_floor_pass": bool(two_phase_pass),
    }


def main() -> None:
    rng = np.random.default_rng(SEED)
    profile_results = {profile.name: _run_profile(profile, rng) for profile in TOPOLOGIES}
    verdict = all(
        result["greedy_floor_pass"] and result["two_phase_floor_pass"]
        for result in profile_results.values()
    )
    output = {
        "inputs": {
            "beacon_sigma": BEACON_SIGMA,
            "healthy_convergence_floor": HEALTHY_CONVERGENCE_FLOOR,
            "max_hops_factor": MAX_HOPS_FACTOR,
            "max_peers": MAX_PEERS,
            "n_trials": N_TRIALS,
            "partition_near_convergence_floor": PARTITION_NEAR_CONVERGENCE_FLOOR,
            "seed": SEED,
            "theta_floor": THETA_FLOOR,
            "two_phase_convergence_floor": TWO_PHASE_CONVERGENCE_FLOOR,
        },
        "topology_results": profile_results,
        "verdict": "pass" if verdict else "fail",
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
