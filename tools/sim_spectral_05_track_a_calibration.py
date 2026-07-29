#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""SIM-SPECTRAL-05 Track A structural discriminant calibration."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.sim_spectral_02 import (
    _normalized_lambda2,
    _scenario_laplacian,
    load_s1_claim_projection_topology,
)


PHASE = 1169
SEEDS = [42, 1337, 2026]
S1_ARTIFACT = Path("out/genesis_claim_composition_projection_v0.1.json")
OUT_PATH = Path("out/sim_spectral_05_track_a_calibration_summary.json")
S3_TOPOLOGY = "synthetic_sybil_cluster"
NODE_COUNT = 56
EPOCHS = 30
FLOOR_VALUES = [0.001, 0.005, 0.01, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5]
SYBIL_WEIGHT_SAMPLES = [0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.3]


def _ring_laplacian(n_nodes: int) -> np.ndarray:
    matrix = np.zeros((n_nodes, n_nodes), dtype=float)
    for index in range(n_nodes):
        neighbor = (index + 1) % n_nodes
        matrix[index, index] += 1.0
        matrix[neighbor, neighbor] += 1.0
        matrix[index, neighbor] -= 1.0
        matrix[neighbor, index] -= 1.0
    return matrix


def _sybil_laplacian(n_nodes: int, cluster_weight: float) -> np.ndarray:
    matrix = _ring_laplacian(n_nodes)
    cluster_size = max(4, n_nodes // 5)
    for i in range(cluster_size):
        for j in range(i + 1, cluster_size):
            matrix[i, i] += cluster_weight
            matrix[j, j] += cluster_weight
            matrix[i, j] -= cluster_weight
            matrix[j, i] -= cluster_weight
    return matrix


def _degree_gini(laplacian: np.ndarray) -> float:
    degrees = sorted(float(value) for value in np.diag(laplacian))
    total = sum(degrees)
    if not degrees or total <= 0:
        return 0.0
    n = len(degrees)
    weighted_sum = sum((2 * (index + 1) - n - 1) * degree for index, degree in enumerate(degrees))
    return float(weighted_sum / (n * total))


def _stats(laplacian: np.ndarray) -> dict[str, float]:
    eigenvalues = np.linalg.eigvalsh(laplacian)
    lambda2 = float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
    lambda_max = float(eigenvalues[-1]) if len(eigenvalues) else 0.0
    return {
        "degree_gini": _degree_gini(laplacian),
        "lambda2": lambda2,
        "lambda2_normalized": _normalized_lambda2(laplacian),
        "lambda_max": lambda_max,
        "spectral_gap": lambda_max - lambda2,
    }


def _mean(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def _std(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = _mean(values)
    return float(math.sqrt(sum((value - mean) ** 2 for value in values) / len(values)))


def _zscore(s1_value: float, sample_values: list[float]) -> float:
    std = _std(sample_values)
    if std <= 1e-12:
        return 0.0
    return float((s1_value - _mean(sample_values)) / std)


def _verdict(zscore: float) -> str:
    return "discriminates_against_sybil" if abs(zscore) >= 2.0 else "insufficient_separation"


def _discriminant_result(name: str, s1_stats: dict[str, float], s3_stats: dict[str, float]) -> dict[str, Any]:
    sample_values = [_stats(_sybil_laplacian(NODE_COUNT, weight))[name] for weight in SYBIL_WEIGHT_SAMPLES]
    zscore = _zscore(s1_stats[name], sample_values)
    return {
        "s1": {
            "value": round(s1_stats[name], 12),
        },
        "s3": {
            "canonical_value": round(s3_stats[name], 12),
            "distribution_max": round(max(sample_values), 12),
            "distribution_mean": round(_mean(sample_values), 12),
            "distribution_min": round(min(sample_values), 12),
            "distribution_std": round(_std(sample_values), 12),
            "sample_count": len(sample_values),
        },
        "zscore_vs_sybil_distribution": round(zscore, 6),
        "verdict": _verdict(zscore),
    }


def _floor_sweep(s1_stats: dict[str, float], s3_stats: dict[str, float]) -> list[dict[str, Any]]:
    rows = []
    for floor in FLOOR_VALUES:
        s1_impedance = max(0.0, floor - s1_stats["lambda2_normalized"]) / floor
        s3_impedance = max(0.0, floor - s3_stats["lambda2_normalized"]) / floor
        rows.append(
            {
                "s1_activates": s1_impedance > 0.0,
                "s1_impedance": round(s1_impedance, 12),
                "s3_activates": s3_impedance > 0.0,
                "s3_impedance": round(s3_impedance, 12),
                "theta_floor": floor,
            }
        )
    return rows


def build_summary() -> dict[str, Any]:
    s1_laplacian, s1_diagnostics = load_s1_claim_projection_topology(S1_ARTIFACT)
    s3_laplacian, s3_label, _ = _scenario_laplacian("S3", NODE_COUNT, 0, EPOCHS, seed=SEEDS[0])
    if s3_label != S3_TOPOLOGY:
        raise ValueError("sim_spectral_05_unexpected_s3_topology")

    s1_stats = _stats(s1_laplacian)
    s3_stats = _stats(s3_laplacian)
    discriminants = {
        "degree_gini": _discriminant_result("degree_gini", s1_stats, s3_stats),
        "lambda_max": _discriminant_result("lambda_max", s1_stats, s3_stats),
        "spectral_gap": _discriminant_result("spectral_gap", s1_stats, s3_stats),
    }
    track_a_pass = any(
        result["verdict"] == "discriminates_against_sybil" for result in discriminants.values()
    )
    return {
        "discriminants": discriminants,
        "gate_token": "sim_spectral_05_track_a_completed_phase_1169",
        "lambda2_floor_sweep": _floor_sweep(s1_stats, s3_stats),
        "phase": PHASE,
        "program_spec": "docs/sims/sim_spectral_05/program.md",
        "s1_artifact": str(S1_ARTIFACT),
        "s1_diagnostics": s1_diagnostics,
        "s3_topology": S3_TOPOLOGY,
        "s3_topology_distribution": {
            "cluster_weight_samples": SYBIL_WEIGHT_SAMPLES,
            "description": "same ring-plus-dense-cluster generator as synthetic_sybil_cluster, swept over cluster edge weights for calibration distribution",
        },
        "seeds": SEEDS,
        "track_a_verdict": "track_a_pass" if track_a_pass else "track_a_fail",
    }


def main() -> None:
    summary = build_summary()
    OUT_PATH.write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
