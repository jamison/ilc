#!/usr/bin/env python3
"""SIM-SPECTRAL-03 topology calibration search for Phase 1145a.

This is a non-canonical research harness. It does not mutate the signed Genesis
star map. Variants are simulation overlays used to audit whether Phase 1145's
weak S1 result is a real graph-design signal or a measurement/calibration
artifact.
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.analysis.laplacian_analytics import N_BOOTSTRAP, THETA_FLOOR
from tools.sim_spectral_02 import (
    WEIGHT_PROFILES,
    _durability,
    _node_sort_key,
    _normalized_lambda2,
    _rolling_slope,
    _scenario_laplacian,
    _simulate_homoiconic_components,
    compute_el_x,
    compute_structural_impedance,
    compute_x,
    load_genesis_nodes,
    load_time_series,
    normalize_epoch_values,
)


# -- PARAMETERS (agent-mutable) -------------------------------------------------
STAR_MAP_PATH = Path("out/genesis_core_star_map_v0.1.json")
OUTPUT_PATH = Path("out/sim_spectral_03_topology_search_summary.json")

SEEDS = (42, 1337, 2026)
EPOCHS = 30
K_VALUES = (0.5, 0.7, 0.9, 1.0, 1.2, 1.4)
WEIGHT_PROFILE = "uniform_available"
KNOWLEDGE_WORK_MODEL = "homoiconic"

WEIGHT_SCALE_VALUES = (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.61, 3.0, 4.0)
WEIGHT_FLOOR_VALUES = (0.0, 0.7, 1.0)
WEIGHT_CAP_VALUES: tuple[float | None, ...] = (None,)
EDGE_TYPE_FILTERS: dict[str, frozenset[str] | None] = {
    "all": None,
    "authority_only": frozenset({"GOVERNS", "ATTESTATION", "PROVENANCE"}),
}
BACKBONE_VARIANTS = ("none", "ring_closure", "star_to_root")
RING_CLOSURE_WEIGHT = 0.5
ATTESTATION_ROOT_ID = "artifact:genesis_intent_attestation_init_authority_map"

RUN01_S1_MEAN_SLOPE = 0.21355627860399237
RUN01_S3_MEAN_SLOPE = 0.3574178266554839
RUN01_G2_MEAN_SLOPE = 0.481335369297431
RUN01_S3_S1_RATIO = 1.6736470076736112
RUN01_G2_S1_RATIO = 2.2539040876901315

RUN02_FIX2_S1_MEAN_SLOPE = 0.557071692882566
RUN02_FIX2_S3_S1_THRESHOLD = 0.6416011282246747
RUN02_FIX2_G2_S1_THRESHOLD = 0.8640456434014127
# -- END PARAMETERS -------------------------------------------------------------


def _base_edge_weight(edge: dict[str, Any]) -> float:
    feature_hints = edge.get("feature_hints")
    sim_weight_seed = feature_hints.get("sim_weight_seed") if isinstance(feature_hints, dict) else None
    confidence = edge.get("confidence")
    if type(sim_weight_seed) in (int, float) and math.isfinite(sim_weight_seed) and sim_weight_seed > 0:
        return float(sim_weight_seed)
    if type(confidence) in (int, float) and math.isfinite(confidence) and confidence > 0:
        return float(confidence)
    return 1.0


def _normalize_variant_weight(
    base_weight: float,
    *,
    weight_floor: float,
    weight_cap: float | None,
    weight_scale: float,
) -> float:
    if weight_scale <= 0:
        raise ValueError("sim_spectral_03_weight_scale_must_be_positive")
    if weight_floor < 0:
        raise ValueError("sim_spectral_03_weight_floor_must_be_non_negative")
    if weight_cap is not None and weight_cap <= 0:
        raise ValueError("sim_spectral_03_weight_cap_must_be_positive")
    weight = max(weight_floor, base_weight)
    if weight_cap is not None:
        weight = min(weight, weight_cap)
    return weight * weight_scale


def build_variant_laplacian(
    star_map_path: Path,
    *,
    weight_scale: float,
    weight_floor: float,
    weight_cap: float | None,
    edge_type_filter: frozenset[str] | None,
    backbone_variant: str,
) -> tuple[np.ndarray, dict[str, Any]]:
    data = json.loads(star_map_path.read_text(encoding="utf-8"))
    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("sim_spectral_03_star_map_nodes_missing")
    if not isinstance(edges, list) or not edges:
        raise ValueError("sim_spectral_03_star_map_edges_missing")

    node_ids = sorted(node["candidate_id"] for node in nodes if isinstance(node, dict))
    if len(node_ids) != 32 or len(node_ids) != len(set(node_ids)):
        raise ValueError("sim_spectral_03_star_map_expected_32_unique_nodes")
    if backbone_variant not in BACKBONE_VARIANTS:
        raise ValueError("sim_spectral_03_unknown_backbone_variant")

    node_index = {node_id: index for index, node_id in enumerate(node_ids)}
    adjacency = np.zeros((len(node_ids), len(node_ids)), dtype=float)
    effective_weights: list[float] = []
    surviving_edge_count = 0

    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("sim_spectral_03_star_map_edge_bad_shape")
        edge_type = edge.get("edge_type")
        if edge_type_filter is not None and edge_type not in edge_type_filter:
            continue
        source = edge.get("source")
        target = edge.get("target")
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("sim_spectral_03_star_map_edge_bad_shape")
        if source == target:
            continue
        if source not in node_index or target not in node_index:
            raise ValueError("sim_spectral_03_star_map_edge_references_unknown_node")
        weight = _normalize_variant_weight(
            _base_edge_weight(edge),
            weight_floor=weight_floor,
            weight_cap=weight_cap,
            weight_scale=weight_scale,
        )
        source_index = node_index[source]
        target_index = node_index[target]
        adjacency[source_index, target_index] += weight
        adjacency[target_index, source_index] += weight
        effective_weights.append(weight)
        surviving_edge_count += 1

    backbone_edges_added = 0
    if backbone_variant == "ring_closure":
        for index in range(len(node_ids)):
            target_index = (index + 1) % len(node_ids)
            weight = RING_CLOSURE_WEIGHT * weight_scale
            adjacency[index, target_index] += weight
            adjacency[target_index, index] += weight
            effective_weights.append(weight)
            backbone_edges_added += 1
    elif backbone_variant == "star_to_root":
        root_index = node_index.get(ATTESTATION_ROOT_ID)
        if root_index is None:
            raise ValueError("sim_spectral_03_attestation_root_missing")
        weighted_degrees = adjacency.sum(axis=1)
        median_degree = float(np.median(weighted_degrees))
        for index, degree in enumerate(weighted_degrees):
            if index == root_index or degree >= median_degree:
                continue
            weight = 1.0 * weight_scale
            adjacency[index, root_index] += weight
            adjacency[root_index, index] += weight
            effective_weights.append(weight)
            backbone_edges_added += 1

    edge_count = int(np.count_nonzero(np.triu(adjacency, k=1)))
    if edge_count == 0:
        raise ValueError("sim_spectral_03_variant_has_no_edges")

    laplacian = np.diag(adjacency.sum(axis=1)) - adjacency
    diagnostics = {
        "backbone_edges_added": backbone_edges_added,
        "backbone_variant": backbone_variant,
        "edge_type_filter_size": None if edge_type_filter is None else len(edge_type_filter),
        "effective_weight_max": max(effective_weights) if effective_weights else 0.0,
        "effective_weight_min": min(effective_weights) if effective_weights else 0.0,
        "edge_count": edge_count,
        "lambda2_normalized": _normalized_lambda2(laplacian),
        "node_count": len(node_ids),
        "source_file": str(star_map_path),
        "surviving_edge_count": surviving_edge_count,
        "weighted_degree_max": float(adjacency.sum(axis=1).max()),
        "weighted_degree_median": float(np.median(adjacency.sum(axis=1))),
        "weighted_degree_min": float(adjacency.sum(axis=1).min()),
    }
    return laplacian, diagnostics


def _run_calibrated_simulation(
    *,
    scenario: str,
    k: float,
    seed: int,
    epochs: int,
    node_limit: int,
    s1_variant_laplacian: np.ndarray | None = None,
    s1_variant_diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if node_limit <= 0:
        raise ValueError("sim_spectral_03_node_limit_must_be_positive")
    series = load_time_series()
    node_ids = sorted(series, key=_node_sort_key)[:node_limit]
    if len(node_ids) != node_limit:
        raise ValueError("sim_spectral_03_node_limit_exceeds_time_series")
    observed_epochs = len(next(iter(series.values())))
    genesis_nodes = load_genesis_nodes()
    n_genesis = min(len(genesis_nodes), node_limit)
    weights = WEIGHT_PROFILES[WEIGHT_PROFILE]
    if KNOWLEDGE_WORK_MODEL != "homoiconic":
        raise ValueError("sim_spectral_03_only_homoiconic_model_supported")
    homoiconic_components, knowledge_work_diagnostics = _simulate_homoiconic_components(
        scenario=scenario,
        seed=seed,
        epochs=epochs,
        series=series,
        node_ids=node_ids,
        n_genesis=n_genesis,
    )

    el_values: list[float] = []
    mean_x_values: list[float] = []
    structural_impedance_values: list[float] = []
    efficiency_values: list[float] = []
    vt_values: list[float] = []
    laplacian_source = ""
    topology_diagnostics: dict[str, Any] = {}

    for epoch_index in range(epochs):
        if scenario == "S1" and s1_variant_laplacian is not None:
            if s1_variant_laplacian.shape != (node_limit, node_limit):
                raise ValueError("sim_spectral_03_variant_laplacian_shape_mismatch")
            laplacian = s1_variant_laplacian.copy()
            laplacian_source = "genesis_star_map_variant"
            topology_diagnostics = dict(s1_variant_diagnostics or {})
        else:
            laplacian, laplacian_source, topology_diagnostics = _scenario_laplacian(
                scenario,
                node_limit,
                epoch_index,
                epochs,
                series=series if scenario == "S1" else None,
                seed=seed,
            )

        lambda2 = _normalized_lambda2(laplacian)
        structural_impedance = compute_structural_impedance(lambda2, THETA_FLOOR)
        raw_components_by_node: list[dict[str, float]] = []
        provenance_values: list[float] = []
        contention_values: list[float] = []
        for node_index, node_id in enumerate(node_ids):
            observed = series[node_id][epoch_index % observed_epochs]
            components = homoiconic_components[epoch_index][node_index]
            raw_components_by_node.append(components)
            provenance_values.append(observed + components.get("synthetic_provenance_bonus", 0.0))
            contention_values.append(components["contention"])

        component_keys = ("survived_refutations", "reuse_count", "validation_integrity")
        normalized_provenance = normalize_epoch_values(provenance_values)
        normalized_by_key = {
            key: normalize_epoch_values([components[key] for components in raw_components_by_node])
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
            for node_index in range(node_limit)
        ]
        x_values = np.array([compute_x(value, k) for value in durability_values], dtype=float)
        el_x = compute_el_x(laplacian, x_values)
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

    return {
        "el_x_per_epoch": el_values,
        "epistemic_efficiency_per_epoch": efficiency_values,
        "epochs": epochs,
        "k": k,
        "knowledge_work_diagnostics": knowledge_work_diagnostics,
        "knowledge_work_model": KNOWLEDGE_WORK_MODEL,
        "laplacian_source": laplacian_source,
        "mean_x_per_epoch": mean_x_values,
        "n_bootstrap": N_BOOTSTRAP,
        "node_count": node_limit,
        "rolling_slope": _rolling_slope(efficiency_values),
        "scenario": scenario,
        "seed": seed,
        "structural_impedance_per_epoch": structural_impedance_values,
        "theta_floor": THETA_FLOOR,
        "topology_diagnostics": topology_diagnostics,
        "v_t_per_epoch": vt_values,
        "weight_profile": WEIGHT_PROFILE,
    }


def _mean(values: list[float]) -> float:
    if not values:
        raise ValueError("sim_spectral_03_mean_requires_values")
    return float(sum(values) / len(values))


def _slopes_by_seed(rows: list[dict[str, Any]]) -> dict[int, float]:
    by_seed: dict[int, list[float]] = {seed: [] for seed in SEEDS}
    for row in rows:
        by_seed[int(row["seed"])].append(float(row["rolling_slope"]))
    return {seed: _mean(values) for seed, values in by_seed.items()}


def _scenario_rows(
    *,
    scenario: str,
    node_limit: int,
    s1_variant_laplacian: np.ndarray | None = None,
    s1_variant_diagnostics: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for seed in SEEDS:
        for k in K_VALUES:
            rows.append(
                _run_calibrated_simulation(
                    scenario=scenario,
                    k=k,
                    seed=seed,
                    epochs=EPOCHS,
                    node_limit=node_limit,
                    s1_variant_laplacian=s1_variant_laplacian,
                    s1_variant_diagnostics=s1_variant_diagnostics,
                )
            )
    return rows


def _variant_id(
    *,
    weight_scale: float,
    weight_floor: float,
    weight_cap: float | None,
    edge_type_filter_name: str,
    backbone_variant: str,
) -> str:
    cap_label = "none" if weight_cap is None else str(weight_cap)
    return f"scale_{weight_scale}_floor_{weight_floor}_cap_{cap_label}_{edge_type_filter_name}_{backbone_variant}"


def _evaluate_variant(
    *,
    weight_scale: float,
    weight_floor: float,
    weight_cap: float | None,
    edge_type_filter_name: str,
    edge_type_filter: frozenset[str] | None,
    backbone_variant: str,
    s3_100_by_seed: dict[int, float],
    g2_100_by_seed: dict[int, float],
    s3_32_by_seed: dict[int, float],
    g2_32_by_seed: dict[int, float],
) -> dict[str, Any]:
    laplacian, diagnostics = build_variant_laplacian(
        STAR_MAP_PATH,
        weight_scale=weight_scale,
        weight_floor=weight_floor,
        weight_cap=weight_cap,
        edge_type_filter=edge_type_filter,
        backbone_variant=backbone_variant,
    )
    s1_rows = _scenario_rows(
        scenario="S1",
        node_limit=32,
        s1_variant_laplacian=laplacian,
        s1_variant_diagnostics=diagnostics,
    )
    s1_by_seed = _slopes_by_seed(s1_rows)
    s1_mean = _mean(list(s1_by_seed.values()))
    s3_100_mean = _mean(list(s3_100_by_seed.values()))
    g2_100_mean = _mean(list(g2_100_by_seed.values()))
    s3_32_mean = _mean(list(s3_32_by_seed.values()))
    g2_32_mean = _mean(list(g2_32_by_seed.values()))

    s3_s1_100_per_seed = [s3_100_by_seed[seed] / s1_by_seed[seed] for seed in SEEDS]
    g2_s1_100_per_seed = [g2_100_by_seed[seed] / s1_by_seed[seed] for seed in SEEDS]
    s3_s1_32_per_seed = [s3_32_by_seed[seed] / s1_by_seed[seed] for seed in SEEDS]
    g2_s1_32_per_seed = [g2_32_by_seed[seed] / s1_by_seed[seed] for seed in SEEDS]

    s3_s1_100 = s3_100_mean / s1_mean
    g2_s1_100 = g2_100_mean / s1_mean
    s3_s1_32 = s3_32_mean / s1_mean
    g2_s1_32 = g2_32_mean / s1_mean
    phase1145_gate_pass = (
        all(ratio < RUN02_FIX2_S3_S1_THRESHOLD for ratio in s3_s1_100_per_seed)
        and all(ratio < RUN02_FIX2_G2_S1_THRESHOLD for ratio in g2_s1_100_per_seed)
    )
    matched_size_gate_pass = (
        all(ratio < RUN02_FIX2_S3_S1_THRESHOLD for ratio in s3_s1_32_per_seed)
        and all(ratio < RUN02_FIX2_G2_S1_THRESHOLD for ratio in g2_s1_32_per_seed)
    )
    return {
        "backbone_variant": backbone_variant,
        "calibration_note": "simulation_overlay_only_signed_star_map_not_mutated",
        "diagnostics": diagnostics,
        "edge_type_filter": edge_type_filter_name,
        "g2_100_mean_slope": g2_100_mean,
        "g2_32_mean_slope": g2_32_mean,
        "g2_s1_100_ratio": g2_s1_100,
        "g2_s1_100_ratio_per_seed": g2_s1_100_per_seed,
        "g2_s1_32_ratio": g2_s1_32,
        "g2_s1_32_ratio_per_seed": g2_s1_32_per_seed,
        "matched_size_gate_pass": matched_size_gate_pass,
        "phase1145_gate_pass": phase1145_gate_pass,
        "s1_mean_slope": s1_mean,
        "s1_slope_by_seed": {str(seed): value for seed, value in s1_by_seed.items()},
        "s1_slope_delta_vs_run01": s1_mean - RUN01_S1_MEAN_SLOPE,
        "s1_slope_delta_vs_run02_fix2": s1_mean - RUN02_FIX2_S1_MEAN_SLOPE,
        "s3_100_mean_slope": s3_100_mean,
        "s3_32_mean_slope": s3_32_mean,
        "s3_s1_100_ratio": s3_s1_100,
        "s3_s1_100_ratio_per_seed": s3_s1_100_per_seed,
        "s3_s1_32_ratio": s3_s1_32,
        "s3_s1_32_ratio_per_seed": s3_s1_32_per_seed,
        "variant_id": _variant_id(
            weight_scale=weight_scale,
            weight_floor=weight_floor,
            weight_cap=weight_cap,
            edge_type_filter_name=edge_type_filter_name,
            backbone_variant=backbone_variant,
        ),
        "weight_cap": weight_cap,
        "weight_floor": weight_floor,
        "weight_scale": weight_scale,
    }


def _best_variant(variants: list[dict[str, Any]], gate: str) -> dict[str, Any] | None:
    candidates = [variant for variant in variants if variant[gate] is True]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda variant: (
            variant["s3_s1_100_ratio"] if gate == "phase1145_gate_pass" else variant["s3_s1_32_ratio"],
            variant["weight_scale"],
            variant["diagnostics"]["backbone_edges_added"],
        ),
    )[0]


def run_search() -> dict[str, Any]:
    s3_100_rows = _scenario_rows(scenario="S3", node_limit=100)
    g2_100_rows = _scenario_rows(scenario="G2", node_limit=100)
    s3_32_rows = _scenario_rows(scenario="S3", node_limit=32)
    g2_32_rows = _scenario_rows(scenario="G2", node_limit=32)

    s3_100_by_seed = _slopes_by_seed(s3_100_rows)
    g2_100_by_seed = _slopes_by_seed(g2_100_rows)
    s3_32_by_seed = _slopes_by_seed(s3_32_rows)
    g2_32_by_seed = _slopes_by_seed(g2_32_rows)

    variants: list[dict[str, Any]] = []
    search_space = itertools.product(
        WEIGHT_SCALE_VALUES,
        WEIGHT_FLOOR_VALUES,
        WEIGHT_CAP_VALUES,
        EDGE_TYPE_FILTERS.items(),
        BACKBONE_VARIANTS,
    )
    for weight_scale, weight_floor, weight_cap, edge_type_item, backbone_variant in search_space:
        edge_type_filter_name, edge_type_filter = edge_type_item
        variants.append(
            _evaluate_variant(
                weight_scale=weight_scale,
                weight_floor=weight_floor,
                weight_cap=weight_cap,
                edge_type_filter_name=edge_type_filter_name,
                edge_type_filter=edge_type_filter,
                backbone_variant=backbone_variant,
                s3_100_by_seed=s3_100_by_seed,
                g2_100_by_seed=g2_100_by_seed,
                s3_32_by_seed=s3_32_by_seed,
                g2_32_by_seed=g2_32_by_seed,
            )
        )

    best_phase1145 = _best_variant(variants, "phase1145_gate_pass")
    best_matched_size = _best_variant(variants, "matched_size_gate_pass")
    summary = {
        "calibration_scope": "simulation_overlays_only_signed_star_map_immutable",
        "committed_token": "sim_spectral_03_topology_search_1145a_committed",
        "corrected_run02_thresholds": {
            "g2_s1": RUN02_FIX2_G2_S1_THRESHOLD,
            "s3_s1": RUN02_FIX2_S3_S1_THRESHOLD,
        },
        "harness": "sim_spectral_03_topology_search",
        "matched_32_controls": {
            "g2_mean_slope": _mean(list(g2_32_by_seed.values())),
            "s3_mean_slope": _mean(list(s3_32_by_seed.values())),
        },
        "phase": "1145a",
        "run01_baseline": {
            "g2_mean_slope": RUN01_G2_MEAN_SLOPE,
            "g2_s1_ratio": RUN01_G2_S1_RATIO,
            "s1_mean_slope": RUN01_S1_MEAN_SLOPE,
            "s3_mean_slope": RUN01_S3_MEAN_SLOPE,
            "s3_s1_ratio": RUN01_S3_S1_RATIO,
        },
        "run02_fix2_baseline": {
            "g2_s1_ratio": RUN02_FIX2_G2_S1_THRESHOLD,
            "s1_mean_slope": RUN02_FIX2_S1_MEAN_SLOPE,
            "s3_s1_ratio": RUN02_FIX2_S3_S1_THRESHOLD,
        },
        "search_parameters": {
            "backbone_variants": list(BACKBONE_VARIANTS),
            "edge_type_filters": list(EDGE_TYPE_FILTERS),
            "k_values": list(K_VALUES),
            "seeds": list(SEEDS),
            "weight_cap_values": list(WEIGHT_CAP_VALUES),
            "weight_floor_values": list(WEIGHT_FLOOR_VALUES),
            "weight_scale_values": list(WEIGHT_SCALE_VALUES),
        },
        "variants": variants,
        "variants_passing_matched_size_gate": sum(1 for variant in variants if variant["matched_size_gate_pass"]),
        "variants_passing_phase1145_gate": sum(1 for variant in variants if variant["phase1145_gate_pass"]),
        "variants_searched": len(variants),
        "best_matched_size_variant": best_matched_size,
        "best_phase1145_comparable_variant": best_phase1145,
        "no_phase1145_comparable_variant_found": best_phase1145 is None,
    }
    return summary


def main() -> dict[str, Any]:
    summary = run_search()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(summary, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, allow_nan=False, indent=2, sort_keys=True))
    return summary


if __name__ == "__main__":
    main()
