#!/usr/bin/env python3
"""SIM-SPECTRAL-02 harness: relative epistemic energy signal exploration."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

from ilc_core.analysis.laplacian_analytics import N_BOOTSTRAP, THETA_FLOOR


TIME_SERIES_PATH = Path("out/sim_provenance_01_time_series.json")
GENESIS_PATH = Path("config/genesis.json")
SCENARIOS = ("S1", "S2", "S3", "S4", "G1", "G2", "G3")
KNOWLEDGE_WORK_MODELS = ("flat", "homoiconic")
PROVENANCE_DECAY_ALPHA_SIM = 0.45
PROVENANCE_MAX_DEPTH_SIM = 3
S1_TOPOLOGIES = ("synthetic", "coactivity", "ancestor-edge", "genesis-star-map")
WEIGHT_PROFILES: dict[str, dict[str, float]] = {
    "observed_provenance_only": {
        "survived_refutations": 0.0,
        "reuse_count": 0.0,
        "provenance_descendant_count": 1.0,
        "validation_integrity": 0.0,
    },
    "uniform_available": {
        "survived_refutations": 0.25,
        "reuse_count": 0.25,
        "provenance_descendant_count": 0.25,
        "validation_integrity": 0.25,
    },
    "provenance_heavy": {
        "survived_refutations": 0.10,
        "reuse_count": 0.15,
        "provenance_descendant_count": 0.60,
        "validation_integrity": 0.15,
    },
    "validation_heavy": {
        "survived_refutations": 0.10,
        "reuse_count": 0.10,
        "provenance_descendant_count": 0.30,
        "validation_integrity": 0.50,
    },
}


def _node_sort_key(node_id: str) -> tuple[str, int | str]:
    prefix, separator, suffix = node_id.rpartition("_")
    if separator and suffix.isdigit():
        return prefix, int(suffix)
    return node_id, node_id


def compute_x(durability: float, k: float) -> float:
    """x_i = exp(-k * Durability_t). Result is in [0, 1]."""
    safe_durability = max(0.0, float(durability))
    x_value = math.exp(-k * safe_durability)
    x_value = min(1.0, max(0.0, x_value))
    if not 0.0 <= x_value <= 1.0:
        raise ValueError("sim_spectral_02_x_out_of_bounds")
    return x_value


def compute_el_x(L: np.ndarray, x: np.ndarray) -> float:
    """E_L(x) = x^T L x."""
    return float(x @ L @ x)


def compute_structural_impedance(lambda2: float, theta_floor: float = THETA_FLOOR) -> float:
    """Bounded structural impedance; never use raw 1/lambda2."""
    if theta_floor <= 0:
        raise ValueError("sim_spectral_02_theta_floor_must_be_positive")
    impedance = max(0.0, theta_floor - lambda2) / theta_floor
    impedance = min(1.0, max(0.0, impedance))
    if not 0.0 <= impedance <= 1.0:
        raise ValueError("sim_spectral_02_structural_impedance_out_of_bounds")
    return impedance


def normalize_epoch_values(values: list[float]) -> list[float]:
    """Per-epoch max normalization. Returns values in [0, 1]."""
    max_value = max(values) if values else 0.0
    if max_value == 0.0:
        return [0.0] * len(values)
    return [value / max_value for value in values]


def load_time_series(path: Path = TIME_SERIES_PATH) -> dict[str, list[int]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise ValueError("sim_spectral_02_time_series_must_be_non_empty_dict")
    normalized: dict[str, list[int]] = {}
    lengths: set[int] = set()
    for node_id, values in data.items():
        if not isinstance(node_id, str) or not isinstance(values, list):
            raise ValueError("sim_spectral_02_time_series_bad_shape")
        if not all(type(value) is int and value >= 0 for value in values):
            raise ValueError("sim_spectral_02_time_series_values_must_be_non_negative_int")
        normalized[node_id] = values
        lengths.add(len(values))
    if len(lengths) != 1:
        raise ValueError("sim_spectral_02_time_series_epoch_lengths_must_match")
    return normalized


def load_genesis_nodes(path: Path = GENESIS_PATH) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    axioms = data.get("axiomatic_core")
    if not isinstance(axioms, list) or not axioms:
        raise ValueError("sim_spectral_02_genesis_axiomatic_core_missing")
    for axiom in axioms:
        if not isinstance(axiom, dict) or not isinstance(axiom.get("id"), str):
            raise ValueError("sim_spectral_02_genesis_axiom_bad_shape")
    return axioms


def _ring_laplacian(n_nodes: int, weak_link: float | None = None) -> np.ndarray:
    adjacency = np.zeros((n_nodes, n_nodes), dtype=float)
    for index in range(n_nodes):
        weight = 1.0
        if weak_link is not None and {index, (index + 1) % n_nodes} == {n_nodes // 2 - 1, n_nodes // 2}:
            weight = weak_link
        j = (index + 1) % n_nodes
        adjacency[index, j] = weight
        adjacency[j, index] = weight
    degree = np.diag(adjacency.sum(axis=1))
    return degree - adjacency


def _coactivity_laplacian(series: dict[str, list[int]], epoch: int = 0) -> tuple[np.ndarray, str, dict[str, Any]]:
    """Build S1 topology from observed PROVENANCE descendant-count coactivity."""
    node_ids = sorted(series, key=_node_sort_key)
    n_nodes = len(node_ids)
    counts = np.array([series[node_id][epoch] for node_id in node_ids], dtype=float)
    active = np.where(counts > 0)[0]
    if len(active) < 2:
        return _ring_laplacian(n_nodes), "synthetic_fallback", {"edge_count": n_nodes}

    adjacency = np.zeros((n_nodes, n_nodes), dtype=float)
    for source in active:
        for target in active:
            if source != target:
                adjacency[source, target] = math.sqrt(counts[source] * counts[target])

    max_weight = float(adjacency.max())
    if max_weight > 0.0:
        adjacency /= max_weight
    # Preserve S1 as a healthy connected baseline: the observed provenance counts
    # identify strong active-node edges, while this weak backbone prevents inactive
    # nodes from becoming artificial singleton partitions.
    backbone_weight = 0.30
    for index in range(n_nodes):
        target = (index + 1) % n_nodes
        adjacency[index, target] = max(adjacency[index, target], backbone_weight)
        adjacency[target, index] = max(adjacency[target, index], backbone_weight)
    degree = np.diag(adjacency.sum(axis=1))
    edge_count = int(np.count_nonzero(np.triu(adjacency, k=1)))
    return degree - adjacency, "coactivity", {"edge_count": edge_count}


def _ancestor_edge_laplacian(
    series: dict[str, list[int]],
    *,
    epoch: int,
    seed: int,
) -> tuple[np.ndarray, str, dict[str, Any]]:
    """Build a symmetrized S1 Laplacian from synthetic ancestor-edge records."""
    node_ids = sorted(series, key=_node_sort_key)
    n_nodes = len(node_ids)
    observed_epoch = epoch % len(next(iter(series.values())))
    counts = [series[node_id][observed_epoch] for node_id in node_ids]
    rng = random.Random(seed)

    depth_weights = [PROVENANCE_DECAY_ALPHA_SIM**depth for depth in range(1, PROVENANCE_MAX_DEPTH_SIM + 1)]
    tiers = [
        rng.choices(
            list(range(1, PROVENANCE_MAX_DEPTH_SIM + 1)),
            weights=depth_weights,
            k=1,
        )[0]
        for _ in range(n_nodes)
    ]
    for i, count in enumerate(counts):
        if count > 0 and tiers[i] == PROVENANCE_MAX_DEPTH_SIM:
            tiers[i] = PROVENANCE_MAX_DEPTH_SIM - 1

    directed = np.zeros((n_nodes, n_nodes), dtype=float)
    generated_marginals = [0] * n_nodes
    depth_distribution = {str(depth): 0 for depth in range(1, PROVENANCE_MAX_DEPTH_SIM + 1)}

    for source, count in enumerate(counts):
        if count == 0:
            continue
        candidates = [
            target
            for target in range(n_nodes)
            if target != source and tiers[target] > tiers[source]
        ]
        if not candidates:
            candidates = [target for target in range(n_nodes) if target > source]
            if not candidates:
                candidates = [target for target in range(n_nodes) if target < source]
        if not candidates:
            continue
        for target in rng.sample(candidates, min(count, len(candidates))):
            hop = tiers[target] - tiers[source]
            directed[source, target] += PROVENANCE_DECAY_ALPHA_SIM**hop
            generated_marginals[source] += 1
            depth_distribution[str(hop)] += 1

    symmetrized = (directed + directed.T) / 2.0
    degree = np.diag(symmetrized.sum(axis=1))
    laplacian = degree - symmetrized
    edge_count = int(np.count_nonzero(np.triu(symmetrized, k=1)))
    marginal_errors = [
        abs(observed - generated)
        for observed, generated in zip(counts, generated_marginals)
    ]
    total_observed = sum(counts)
    total_generated = sum(generated_marginals)
    marginal_error_rate = (
        abs(total_observed - total_generated) / total_observed
        if total_observed > 0
        else 0.0
    )
    diagnostics = {
        "clique_guard_ok": edge_count < 5 * n_nodes,
        "depth_distribution": depth_distribution,
        "edge_count": edge_count,
        "epoch": observed_epoch,
        "marginal_error_mean": float(np.mean(np.array(marginal_errors, dtype=float))) if marginal_errors else 0.0,
        "marginal_error_rate": marginal_error_rate,
        "max_in_degree": float(symmetrized.sum(axis=0).max()) if n_nodes else 0.0,
        "max_observed_count": max(counts) if counts else 0,
        "max_out_degree": float(symmetrized.sum(axis=1).max()) if n_nodes else 0.0,
        "self_loops": int(np.count_nonzero(np.diag(directed))),
        "total_generated_edges": total_generated,
        "total_observed_descendant_count": total_observed,
    }
    return laplacian, "ancestor_edge", diagnostics


def load_s1_star_map_topology(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    """Load a signed Genesis core star map as an undirected S1 seed topology."""
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("sim_spectral_02_star_map_nodes_missing")
    if not isinstance(edges, list) or not edges:
        raise ValueError("sim_spectral_02_star_map_edges_missing")

    node_ids: list[str] = []
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("candidate_id"), str):
            raise ValueError("sim_spectral_02_star_map_node_bad_shape")
        node_ids.append(node["candidate_id"])
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("sim_spectral_02_star_map_duplicate_node_id")

    node_ids = sorted(node_ids)
    node_index = {node_id: index for index, node_id in enumerate(node_ids)}
    adjacency = np.zeros((len(node_ids), len(node_ids)), dtype=float)
    skipped_self_loops = 0

    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("sim_spectral_02_star_map_edge_bad_shape")
        source = edge.get("source")
        target = edge.get("target")
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("sim_spectral_02_star_map_edge_bad_shape")
        if source not in node_index or target not in node_index:
            raise ValueError("sim_spectral_02_star_map_edge_references_unknown_node")
        if source == target:
            skipped_self_loops += 1
            continue

        feature_hints = edge.get("feature_hints")
        sim_weight_seed = feature_hints.get("sim_weight_seed") if isinstance(feature_hints, dict) else None
        confidence = edge.get("confidence")
        if type(sim_weight_seed) in (int, float) and math.isfinite(sim_weight_seed) and sim_weight_seed > 0:
            weight = float(sim_weight_seed)
        elif type(confidence) in (int, float) and math.isfinite(confidence) and confidence > 0:
            weight = float(confidence)
        else:
            weight = 1.0

        source_index = node_index[source]
        target_index = node_index[target]
        adjacency[source_index, target_index] += weight
        adjacency[target_index, source_index] += weight

    edge_count = int(np.count_nonzero(np.triu(adjacency, k=1)))
    if edge_count == 0:
        raise ValueError("sim_spectral_02_star_map_has_no_usable_edges")
    degree = np.diag(adjacency.sum(axis=1))
    diagnostics = {
        "edge_count": edge_count,
        "node_count": len(node_ids),
        "source_file": str(path),
        "source_format": "genesis_core_star_map_v0.1",
        "skipped_self_loops": skipped_self_loops,
        "topology_node_ids": node_ids,
        "weighted": True,
    }
    return degree - adjacency, diagnostics


def _scenario_laplacian(
    scenario: str,
    n_nodes: int,
    epoch_index: int,
    epochs: int,
    series: dict[str, list[int]] | None = None,
    seed: int = 0,
    s1_topology: str = "synthetic",
    s1_topology_epoch: int = 100,
    s1_star_map_topology: tuple[np.ndarray, dict[str, Any]] | None = None,
) -> tuple[np.ndarray, str, dict[str, Any]]:
    if scenario == "S1":
        if s1_topology == "genesis-star-map":
            if s1_star_map_topology is None:
                raise ValueError("sim_spectral_02_s1_star_map_topology_missing")
            L, diagnostics = s1_star_map_topology
            return L.copy(), "genesis_star_map", dict(diagnostics)
        if s1_topology == "coactivity" and series is not None:
            return _coactivity_laplacian(series, epoch=s1_topology_epoch)
        if s1_topology == "ancestor-edge" and series is not None:
            return _ancestor_edge_laplacian(series, epoch=s1_topology_epoch, seed=seed)
        return _ring_laplacian(n_nodes), "synthetic_ring", {"edge_count": n_nodes}
    if scenario == "S2":
        progress = epoch_index / max(1, epochs - 1)
        weak_link = max(0.00001, 1.0 - progress)
        return _ring_laplacian(n_nodes, weak_link=weak_link), "synthetic_partition", {}
    if scenario in {"S3", "G1", "G2"}:
        L = _ring_laplacian(n_nodes)
        cluster_size = max(4, n_nodes // 5)
        for i in range(cluster_size):
            for j in range(i + 1, cluster_size):
                L[i, i] += 0.15
                L[j, j] += 0.15
                L[i, j] -= 0.15
                L[j, i] -= 0.15
        return L, "synthetic_sybil_cluster", {}
    return _ring_laplacian(n_nodes), "synthetic_ring", {}


def _normalized_lambda2(L: np.ndarray) -> float:
    """Compute normalized algebraic connectivity from combinatorial Laplacian."""
    degrees = np.diag(L)
    if not np.any(degrees > 0):
        return 0.0
    d_inv_sqrt = np.diag([1.0 / math.sqrt(d) if d > 0 else 0.0 for d in degrees])
    L_norm = d_inv_sqrt @ L @ d_inv_sqrt
    eigenvalues = np.linalg.eigvalsh(L_norm)
    if len(eigenvalues) < 2:
        return 0.0
    return max(0.0, float(eigenvalues[1]))


def _synthetic_components(
    scenario: str,
    epoch_index: int,
    node_index: int,
    rng: random.Random,
) -> dict[str, float]:
    progress = epoch_index + 1
    jitter = rng.random() * 0.05
    if scenario == "S1":
        return {
            "survived_refutations": 0.02 * progress + jitter,
            "reuse_count": 0.04 * progress + jitter,
            "validation_integrity": min(1.0, 0.55 + 0.01 * progress + jitter),
            "contention": 0.05,
        }
    if scenario == "S2":
        return {
            "survived_refutations": 0.01 * progress,
            "reuse_count": 0.02 * progress,
            "validation_integrity": 0.45 + jitter,
            "contention": 0.20 + 0.01 * progress,
        }
    if scenario in {"S3", "G1", "G2"}:
        cluster = node_index < 20
        artificial_reuse = 0.12 * progress if scenario == "G1" else 0.08 * progress
        artificial_provenance = 0.10 * progress if scenario == "G2" else 0.0
        return {
            "survived_refutations": 0.0 if cluster else 0.01 * progress,
            "reuse_count": artificial_reuse if cluster else 0.01 * progress,
            "validation_integrity": 0.20 + jitter if cluster else 0.45 + jitter,
            "synthetic_provenance_bonus": artificial_provenance if cluster else 0.0,
            "contention": 0.45 if cluster else 0.15,
        }
    if scenario in {"S4", "G3"}:
        staged_refutation = 0.08 * progress if scenario == "G3" else 0.0
        return {
            "survived_refutations": staged_refutation,
            "reuse_count": 0.01 * progress,
            "validation_integrity": 0.30 + jitter,
            "contention": 0.60,
        }
    raise ValueError(f"unknown scenario: {scenario}")


def _homoiconic_metadata(n_nodes: int, n_genesis: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    domains = ("Arithmetic", "Thermodynamics", "Logic", "Cross-domain")
    depth_weights = [PROVENANCE_DECAY_ALPHA_SIM**depth for depth in range(1, PROVENANCE_MAX_DEPTH_SIM + 1)]
    metadata: list[dict[str, Any]] = []
    for node_index in range(n_nodes):
        if node_index < n_genesis:
            metadata.append(
                {
                    "domain": domains[node_index % 3],
                    "genesis_ancestor": node_index,
                    "genesis_exempt": True,
                    "tier": 0,
                }
            )
            continue
        domain = rng.choices(domains, weights=(0.30, 0.30, 0.30, 0.10), k=1)[0]
        ancestor = rng.randrange(n_genesis) if domain == "Cross-domain" else domains.index(domain)
        metadata.append(
            {
                "domain": domain,
                "genesis_ancestor": ancestor,
                "genesis_exempt": False,
                "tier": rng.choices(
                    list(range(1, PROVENANCE_MAX_DEPTH_SIM + 1)),
                    weights=depth_weights,
                    k=1,
                )[0],
            }
        )
    return metadata


def _validation_probability(scenario: str, tier: int) -> float:
    table = {
        "S1": (0.90, 0.80, 0.70),
        "S2": (0.60, 0.40, 0.30),
        "S3": (0.60, 0.60, 0.60),
        "S4": (0.50, 0.35, 0.20),
        "G1": (0.65, 0.55, 0.45),
        "G2": (0.70, 0.60, 0.50),
        "G3": (0.60, 0.45, 0.30),
    }
    values = table.get(scenario, table["S1"])
    return values[max(1, min(PROVENANCE_MAX_DEPTH_SIM, tier)) - 1]


def _simulate_homoiconic_components(
    *,
    scenario: str,
    seed: int,
    epochs: int,
    series: dict[str, list[int]],
    node_ids: list[str],
    n_genesis: int,
) -> tuple[list[list[dict[str, float]]], dict[str, Any]]:
    rng = random.Random(seed)
    n_nodes = len(node_ids)
    observed_epochs = len(next(iter(series.values())))
    metadata = _homoiconic_metadata(n_nodes, n_genesis, seed)
    validation_passes = [0.0] * n_nodes
    reuse_counts = [0.0] * n_nodes
    survived_refutations = [0.0] * n_nodes
    failed_challenges = [0.0] * n_nodes
    by_epoch: list[list[dict[str, float]]] = []

    for epoch_index in range(epochs):
        components_for_epoch: list[dict[str, float]] = []
        progress = epoch_index + 1
        cascade_penalty_by_ancestor = {idx: 0.0 for idx in range(n_genesis)}
        if scenario in {"S4", "G3"} and progress % 7 == 0:
            cascade_penalty_by_ancestor[rng.randrange(n_genesis)] = 0.25

        observed_counts = [series[node_id][epoch_index % observed_epochs] for node_id in node_ids]
        max_observed = max(observed_counts) if observed_counts else 0

        for node_index, node_id in enumerate(node_ids):
            observed = observed_counts[node_index]
            node_meta = metadata[node_index]
            if node_meta["genesis_exempt"]:
                validation_passes[node_index] = progress
                reuse_counts[node_index] += 1.0 + (max_observed / max(1, n_genesis))
                components_for_epoch.append(
                    {
                        "contention": 0.01,
                        "reuse_count": math.log1p(reuse_counts[node_index]),
                        "survived_refutations": 0.0,
                        "validation_integrity": 1.0,
                    }
                )
                continue

            tier = int(node_meta["tier"])
            validation_prob = _validation_probability(scenario, tier)
            if scenario == "S3" and node_index < max(n_genesis + 1, n_nodes // 5):
                validation_prob = 0.35
            validation_prob = max(
                0.0,
                validation_prob - cascade_penalty_by_ancestor[int(node_meta["genesis_ancestor"])],
            )
            if rng.random() < validation_prob:
                validation_passes[node_index] += 1.0
            validation_integrity = validation_passes[node_index] / progress

            if scenario == "S3":
                reuse_rate = 0.85 if node_index < max(n_genesis + 1, n_nodes // 5) else 0.30
            elif scenario == "G1":
                reuse_rate = 0.40
            elif scenario == "G2":
                reuse_rate = 0.18
            elif scenario == "S1":
                reuse_rate = 0.10 + 0.20 * validation_integrity
            elif scenario == "S2":
                reuse_rate = 0.05 + 0.08 * validation_integrity
            else:
                reuse_rate = 0.04 + 0.06 * validation_integrity
            reuse_rate += min(0.12, 0.02 * observed)
            if rng.random() < min(0.95, reuse_rate):
                reuse_increment = (
                    4.0
                    if scenario == "S3" and node_index < max(n_genesis + 1, n_nodes // 5)
                    else 1.0
                )
                reuse_counts[node_index] += reuse_increment
                ancestor = int(node_meta["genesis_ancestor"])
                reuse_counts[ancestor] += 0.25

            challenge_rate = min(0.45, 0.03 + 0.28 * (1.0 - validation_integrity))
            if scenario in {"S4", "G3"}:
                challenge_rate += 0.12
            if rng.random() < challenge_rate:
                if rng.random() < validation_integrity:
                    survived_refutations[node_index] += 1.0
                else:
                    failed_challenges[node_index] += 1.0

            synthetic_provenance_bonus = 0.0
            if scenario == "G2":
                synthetic_provenance_bonus = 0.10 * progress if node_index < n_nodes // 5 else 0.0

            contention = {
                "S1": 0.05,
                "S2": 0.20 + 0.01 * progress,
                "S3": 0.45 if node_index < n_nodes // 5 else 0.15,
                "S4": 0.60,
                "G1": 0.45,
                "G2": 0.35,
                "G3": 0.60,
            }.get(scenario, 0.05)
            components_for_epoch.append(
                {
                    "contention": contention,
                    "reuse_count": math.log1p(reuse_counts[node_index]),
                    "survived_refutations": math.log1p(survived_refutations[node_index]),
                    "synthetic_provenance_bonus": synthetic_provenance_bonus,
                    "validation_integrity": max(
                        0.0,
                        validation_integrity - min(0.20, 0.05 * failed_challenges[node_index]),
                    ),
                }
            )
        by_epoch.append(components_for_epoch)

    final_components = by_epoch[-1]
    diagnostics = {
        "genesis_exempt_count": n_genesis,
        "genesis_nodes_count": n_genesis,
        "mean_reuse_count": float(np.mean([component["reuse_count"] for component in final_components])),
        "mean_survived_refutations": float(
            np.mean([component["survived_refutations"] for component in final_components])
        ),
        "mean_validation_integrity": float(
            np.mean([component["validation_integrity"] for component in final_components])
        ),
    }
    return by_epoch, diagnostics


def _durability(
    provenance_descendant_count: float,
    components: dict[str, float],
    weights: dict[str, float],
) -> float:
    return max(
        0.0,
        weights["survived_refutations"] * components["survived_refutations"]
        + weights["reuse_count"] * components["reuse_count"]
        + weights["provenance_descendant_count"] * provenance_descendant_count
        + weights["validation_integrity"] * components["validation_integrity"],
    )


def _rolling_slope(values: list[float]) -> float:
    """Return the linear regression slope over epoch indices.

    X-axis is uniform integer epoch indices [0, 1, ..., n-1].  This assumes
    epochs are evenly spaced; any epoch-skipping in the input data would
    compress or expand the apparent slope accordingly.
    """
    if len(values) < 2:
        return 0.0
    x_axis = np.arange(len(values), dtype=float)
    return float(np.polyfit(x_axis, np.array(values, dtype=float), 1)[0])


def run_simulation(
    *,
    scenario: str,
    k: float,
    weight_profile: str,
    seed: int,
    epochs: int,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
    delta: float = 1.0,
    time_series_path: Path = TIME_SERIES_PATH,
    normalize_durability: bool = True,
    s1_topology: str = "synthetic",
    s1_topology_epoch: int = 100,
    s1_topology_file: Path | None = None,
    knowledge_work_model: str = "homoiconic",
) -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ValueError("sim_spectral_02_unknown_scenario")
    if weight_profile not in WEIGHT_PROFILES:
        raise ValueError("sim_spectral_02_unknown_weight_profile")
    if k <= 0 or epochs <= 0:
        raise ValueError("sim_spectral_02_k_and_epochs_must_be_positive")
    if s1_topology not in S1_TOPOLOGIES:
        raise ValueError("sim_spectral_02_unknown_s1_topology")
    if knowledge_work_model not in KNOWLEDGE_WORK_MODELS:
        raise ValueError("sim_spectral_02_unknown_knowledge_work_model")
    if s1_topology_file is not None and scenario != "S1":
        raise ValueError("sim_spectral_02_s1_topology_file_only_valid_for_s1")
    if s1_topology == "genesis-star-map" and s1_topology_file is None:
        raise ValueError("sim_spectral_02_genesis_star_map_requires_topology_file")
    if s1_topology_file is not None:
        s1_topology = "genesis-star-map"

    series = load_time_series(time_series_path)
    node_ids = sorted(series, key=_node_sort_key)
    n_nodes = len(node_ids)
    s1_star_map_topology: tuple[np.ndarray, dict[str, Any]] | None = None
    if s1_topology_file is not None:
        s1_star_map_topology = load_s1_star_map_topology(s1_topology_file)
        star_map_node_count = int(s1_star_map_topology[1]["node_count"])
        if len(node_ids) < star_map_node_count:
            raise ValueError("sim_spectral_02_time_series_too_small_for_star_map_topology")
        # The star map supplies graph topology (Laplacian); time series supplies
        # node activity values. IDs are from different namespaces (semantic star
        # map IDs vs generic time-series node IDs), so mapping is positional:
        # time series nodes sorted by _node_sort_key are assigned to star map
        # positions by index. Excess time series nodes are discarded.
        node_ids = node_ids[:star_map_node_count]
        n_nodes = star_map_node_count
    observed_epochs = len(next(iter(series.values())))
    genesis_nodes = load_genesis_nodes()
    n_genesis = min(len(genesis_nodes), n_nodes)
    homoiconic_components: list[list[dict[str, float]]] | None = None
    knowledge_work_diagnostics: dict[str, Any] = {}
    if knowledge_work_model == "homoiconic":
        homoiconic_components, knowledge_work_diagnostics = _simulate_homoiconic_components(
            scenario=scenario,
            seed=seed,
            epochs=epochs,
            series=series,
            node_ids=node_ids,
            n_genesis=n_genesis,
        )
    rng = random.Random(seed)
    weights = WEIGHT_PROFILES[weight_profile]

    el_values: list[float] = []
    mean_x_values: list[float] = []
    structural_impedance_values: list[float] = []
    efficiency_values: list[float] = []
    vt_values: list[float] = []
    laplacian_source = ""
    topology_diagnostics: dict[str, Any] = {}

    for epoch_index in range(epochs):
        L, laplacian_source, topology_diagnostics = _scenario_laplacian(
            scenario,
            n_nodes,
            epoch_index,
            epochs,
            series=series if scenario == "S1" else None,
            seed=seed,
            s1_topology=s1_topology,
            s1_topology_epoch=s1_topology_epoch,
            s1_star_map_topology=s1_star_map_topology,
        )
        lambda2 = _normalized_lambda2(L)
        structural_impedance = compute_structural_impedance(lambda2, THETA_FLOOR)
        raw_components_by_node: list[dict[str, float]] = []
        provenance_values: list[float] = []
        contention_values: list[float] = []
        for node_index, node_id in enumerate(node_ids):
            observed = series[node_id][epoch_index % observed_epochs]
            if homoiconic_components is not None:
                components = homoiconic_components[epoch_index][node_index]
            else:
                components = _synthetic_components(scenario, epoch_index, node_index, rng)
            raw_components_by_node.append(components)
            provenance_values.append(observed + components.get("synthetic_provenance_bonus", 0.0))
            contention_values.append(components["contention"])

        component_keys = ("survived_refutations", "reuse_count", "validation_integrity")
        if normalize_durability:
            normalized_provenance = normalize_epoch_values(provenance_values)
            normalized_by_key = {
                key: normalize_epoch_values([components[key] for components in raw_components_by_node])
                for key in component_keys
            }
        else:
            normalized_provenance = provenance_values
            normalized_by_key = {
                key: [components[key] for components in raw_components_by_node]
                for key in component_keys
            }
        durability_values = [
            _durability(
                normalized_provenance[node_index],
                {
                    "survived_refutations": normalized_by_key["survived_refutations"][node_index],
                    "reuse_count": normalized_by_key["reuse_count"][node_index],
                    "validation_integrity": normalized_by_key["validation_integrity"][node_index],
                },
                weights,
            )
            for node_index in range(n_nodes)
        ]

        x_values = np.array([compute_x(value, k) for value in durability_values], dtype=float)
        el_x = compute_el_x(L, x_values)
        mean_x = float(np.mean(x_values))
        contention = float(np.mean(contention_values))
        durable_work = float(sum(durability_values))
        relative_cost = 1.0 + el_x + structural_impedance + contention
        efficiency = durable_work / relative_cost if relative_cost > 0 else 0.0
        vt = (alpha * el_x) + (beta * mean_x) + (gamma * structural_impedance) + (delta * contention)

        el_values.append(el_x)
        mean_x_values.append(mean_x)
        structural_impedance_values.append(structural_impedance)
        efficiency_values.append(efficiency)
        vt_values.append(vt)

    slope = _rolling_slope(efficiency_values)
    verdict = "pass" if (scenario == "S1" and slope > 0) or (scenario != "S1" and slope <= 0) else "ambiguous"

    return {
        "scenario": scenario,
        "k": k,
        "weight_profile": weight_profile,
        "seed": seed,
        "epochs": epochs,
        "node_count": n_nodes,
        "n_bootstrap": N_BOOTSTRAP,
        "theta_floor": THETA_FLOOR,
        "normalize_durability": normalize_durability,
        "knowledge_work_diagnostics": knowledge_work_diagnostics,
        "knowledge_work_model": knowledge_work_model,
        "laplacian_source": laplacian_source,
        "s1_topology": s1_topology,
        "s1_topology_epoch": s1_topology_epoch,
        "s1_topology_file": str(s1_topology_file) if s1_topology_file is not None else None,
        "topology_diagnostics": topology_diagnostics,
        "data_classes": {
            "genesis_nodes_count": n_genesis if knowledge_work_model == "homoiconic" else 0,
            "provenance_descendant_count": "OBSERVED",
            "survived_refutations": "SYNTHETIC_HOMOICONIC"
            if knowledge_work_model == "homoiconic"
            else "SYNTHETIC",
            "reuse_count": "SYNTHETIC_HOMOICONIC"
            if knowledge_work_model == "homoiconic"
            else "SYNTHETIC",
            "validation_integrity": "SYNTHETIC_HOMOICONIC"
            if knowledge_work_model == "homoiconic"
            else "SYNTHETIC",
            "path_uplift": "EXCLUDED",
        },
        "el_x_per_epoch": el_values,
        "mean_x_per_epoch": mean_x_values,
        "structural_impedance_per_epoch": structural_impedance_values,
        "epistemic_efficiency_per_epoch": efficiency_values,
        "v_t_per_epoch": vt_values,
        "rolling_slope": slope,
        "verdict": verdict,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", required=True, choices=SCENARIOS)
    parser.add_argument("--k", required=True, type=float)
    parser.add_argument("--weight-profile", required=True, choices=tuple(WEIGHT_PROFILES))
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--epochs", required=True, type=int)
    parser.add_argument("--alpha", default=1.0, type=float)
    parser.add_argument("--beta", default=1.0, type=float)
    parser.add_argument("--gamma", default=1.0, type=float)
    parser.add_argument("--delta", default=1.0, type=float)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--s1-topology", default="synthetic", choices=S1_TOPOLOGIES)
    parser.add_argument(
        "--s1-topology-file",
        default=None,
        type=Path,
        help="Genesis core star-map JSON to use as the S1 seed topology.",
    )
    parser.add_argument("--s1-topology-epoch", default=100, type=int)
    parser.add_argument("--knowledge-work-model", default="homoiconic", choices=KNOWLEDGE_WORK_MODELS)
    parser.add_argument(
        "--normalize-durability",
        default="true",
        choices=("true", "false"),
        help="Whether to max-normalize Durability_t components per epoch across nodes.",
    )
    return parser


def main(argv: list[str] | None = None) -> dict[str, Any]:
    args = _build_parser().parse_args(argv)
    result = run_simulation(
        scenario=args.scenario,
        k=args.k,
        weight_profile=args.weight_profile,
        seed=args.seed,
        epochs=args.epochs,
        alpha=args.alpha,
        beta=args.beta,
        gamma=args.gamma,
        delta=args.delta,
        normalize_durability=args.normalize_durability == "true",
        s1_topology=args.s1_topology,
        s1_topology_epoch=args.s1_topology_epoch,
        s1_topology_file=args.s1_topology_file,
        knowledge_work_model=args.knowledge_work_model,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, allow_nan=False, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
