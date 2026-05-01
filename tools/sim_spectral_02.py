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
SCENARIOS = ("S1", "S2", "S3", "S4", "G1", "G2", "G3")
PROVENANCE_DECAY_ALPHA_SIM = 0.45
PROVENANCE_MAX_DEPTH_SIM = 3
S1_TOPOLOGIES = ("synthetic", "coactivity", "ancestor-edge")
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


def compute_x(durability: float, k: float) -> float:
    """x_i = exp(-k * Durability_t). Result is in [0, 1]."""
    x_value = math.exp(-k * durability)
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
    node_ids = sorted(series)
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
    node_ids = sorted(series)
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


def _scenario_laplacian(
    scenario: str,
    n_nodes: int,
    epoch_index: int,
    epochs: int,
    series: dict[str, list[int]] | None = None,
    seed: int = 0,
    s1_topology: str = "synthetic",
    s1_topology_epoch: int = 100,
) -> tuple[np.ndarray, str, dict[str, Any]]:
    if scenario == "S1":
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


def _lambda2(L: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvalsh(L)
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
    time_series_path: Path = TIME_SERIES_PATH,
    normalize_durability: bool = True,
    s1_topology: str = "synthetic",
    s1_topology_epoch: int = 100,
) -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ValueError("sim_spectral_02_unknown_scenario")
    if weight_profile not in WEIGHT_PROFILES:
        raise ValueError("sim_spectral_02_unknown_weight_profile")
    if k <= 0 or epochs <= 0:
        raise ValueError("sim_spectral_02_k_and_epochs_must_be_positive")
    if s1_topology not in S1_TOPOLOGIES:
        raise ValueError("sim_spectral_02_unknown_s1_topology")

    series = load_time_series(time_series_path)
    node_ids = sorted(series)
    n_nodes = len(node_ids)
    observed_epochs = len(next(iter(series.values())))
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
        )
        lambda2 = _lambda2(L)
        structural_impedance = compute_structural_impedance(lambda2, THETA_FLOOR)
        raw_components_by_node: list[dict[str, float]] = []
        provenance_values: list[float] = []
        contention_values: list[float] = []
        for node_index, node_id in enumerate(node_ids):
            observed = series[node_id][epoch_index % observed_epochs]
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
        vt = el_x + mean_x + structural_impedance + contention

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
        "laplacian_source": laplacian_source,
        "s1_topology": s1_topology,
        "s1_topology_epoch": s1_topology_epoch,
        "topology_diagnostics": topology_diagnostics,
        "data_classes": {
            "provenance_descendant_count": "OBSERVED",
            "survived_refutations": "SYNTHETIC",
            "reuse_count": "SYNTHETIC",
            "validation_integrity": "SYNTHETIC",
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
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--s1-topology", default="synthetic", choices=S1_TOPOLOGIES)
    parser.add_argument("--s1-topology-epoch", default=100, type=int)
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
        normalize_durability=args.normalize_durability == "true",
        s1_topology=args.s1_topology,
        s1_topology_epoch=args.s1_topology_epoch,
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
