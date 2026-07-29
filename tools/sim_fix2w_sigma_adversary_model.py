#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1568-Fix2w H-013 sigma adversary-model simulation.

This is a standalone research/SIM tool. It intentionally imports no ilc_core
modules and does not mutate protocol state.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

import numpy as np


SIGMA_VALUES = (0.005, 0.01, 0.02, 0.05, 0.10, 0.20)
N_AGENT_VALUES = (100, 500, 1000)
T_OBS_VALUES = (1, 2, 5, 10, 20, 50, 100)
FANOUT = 3
DEFAULT_TRIALS = 500
LOCAL_GRAPH_NODE_COUNT = 18
LOCAL_GRAPH_EXPECTED_DEGREE = 6
LAMBDA_DIMENSIONS = 8
PRIVACY_TARGET_P_CORRECT = 0.01
PRIVACY_TARGET_N = 1000
PRIVACY_TARGET_T_OBS_MAX = 20
PINNED_SIGMA = 0.05


def _stable_json(record: dict[str, object]) -> str:
    return json.dumps(record, sort_keys=True, separators=(",", ":"))


def _normalized_laplacian_spectrum(adjacency: np.ndarray) -> np.ndarray:
    degree = adjacency.sum(axis=1).astype(float)
    inv_sqrt_degree = np.zeros_like(degree)
    positive = degree > 0
    inv_sqrt_degree[positive] = 1.0 / np.sqrt(degree[positive])
    normalized_adjacency = (inv_sqrt_degree[:, None] * adjacency) * inv_sqrt_degree[None, :]
    return np.linalg.eigvalsh(np.eye(adjacency.shape[0]) - normalized_adjacency)


def generate_agent_templates(
    *,
    n_agents: int,
    seed: int,
    local_node_count: int = LOCAL_GRAPH_NODE_COUNT,
    expected_degree: int = LOCAL_GRAPH_EXPECTED_DEGREE,
    dimensions: int = LAMBDA_DIMENSIONS,
) -> np.ndarray:
    """Generate deterministic lambda_local templates from local ER graph spectra."""

    if dimensions > local_node_count:
        raise ValueError("dimensions_must_not_exceed_local_node_count")
    edge_probability = min(0.95, expected_degree / float(local_node_count - 1))
    rng = np.random.default_rng(seed)
    templates = np.empty((n_agents, dimensions), dtype=float)
    for agent_index in range(n_agents):
        upper = rng.random((local_node_count, local_node_count)) < edge_probability
        upper = np.triu(upper, 1)
        adjacency = (upper + upper.T).astype(float)
        eigenvalues = _normalized_laplacian_spectrum(adjacency)
        templates[agent_index] = np.sort(eigenvalues)[-dimensions:]
    return templates


def _trial_seed(seed: int, *, sigma_index: int, n_index: int, t_index: int) -> int:
    return seed + 10_000 * sigma_index + 1_000 * n_index + 100 * t_index + 17


def run_sweep_point(
    *,
    templates: np.ndarray,
    sigma: float,
    t_obs: int,
    trials: int,
    seed: int,
) -> tuple[int, float]:
    """Return hit count and p_correct for one parameter triple."""

    rng = np.random.default_rng(seed)
    n_agents, dimensions = templates.shape
    observation_count = t_obs * FANOUT
    sample_mean_noise_sigma = sigma / np.sqrt(observation_count)
    target_indices = rng.integers(0, n_agents, size=trials)
    noise = rng.normal(
        loc=0.0,
        scale=sample_mean_noise_sigma,
        size=(trials, dimensions),
    )
    observed_means = templates[target_indices] + noise
    hits = 0
    for trial_index, observed_mean in enumerate(observed_means):
        squared_distances = np.sum((templates - observed_mean) ** 2, axis=1)
        if int(np.argmin(squared_distances)) == int(target_indices[trial_index]):
            hits += 1
    return hits, hits / float(trials)


def run_sweep(*, seed: int, trials: int) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    templates_by_n = {
        n_agents: generate_agent_templates(n_agents=n_agents, seed=seed + n_agents)
        for n_agents in N_AGENT_VALUES
    }
    for n_index, n_agents in enumerate(N_AGENT_VALUES):
        templates = templates_by_n[n_agents]
        for sigma_index, sigma in enumerate(SIGMA_VALUES):
            for t_index, t_obs in enumerate(T_OBS_VALUES):
                hits, p_correct = run_sweep_point(
                    templates=templates,
                    sigma=sigma,
                    t_obs=t_obs,
                    trials=trials,
                    seed=_trial_seed(
                        seed,
                        sigma_index=sigma_index,
                        n_index=n_index,
                        t_index=t_index,
                    ),
                )
                records.append(
                    {
                        "fanout": FANOUT,
                        "hit_count": hits,
                        "n_agents": n_agents,
                        "p_correct": round(p_correct, 6),
                        "seed": seed,
                        "sigma": f"{sigma:.3f}".rstrip("0").rstrip("."),
                        "t_obs": t_obs,
                        "trial_count": trials,
                    }
                )
    return records


def verdict_for(records: Iterable[dict[str, object]]) -> dict[str, object]:
    target_records = [
        record
        for record in records
        if record["n_agents"] == PRIVACY_TARGET_N
        and int(record["t_obs"]) <= PRIVACY_TARGET_T_OBS_MAX
    ]
    pinned_records = [
        record
        for record in target_records
        if float(str(record["sigma"])) == PINNED_SIGMA
    ]
    pinned_passes = all(
        float(record["p_correct"]) <= PRIVACY_TARGET_P_CORRECT
        for record in pinned_records
    )
    passing_sigmas: list[float] = []
    for sigma in SIGMA_VALUES:
        sigma_records = [
            record for record in target_records if float(str(record["sigma"])) == sigma
        ]
        if sigma_records and all(
            float(record["p_correct"]) <= PRIVACY_TARGET_P_CORRECT
            for record in sigma_records
        ):
            passing_sigmas.append(sigma)
    target_t20 = next(
        record
        for record in pinned_records
        if int(record["t_obs"]) == PRIVACY_TARGET_T_OBS_MAX
    )
    return {
        "minimum_passing_sigma": (
            f"{min(passing_sigmas):.3f}".rstrip("0").rstrip(".")
            if passing_sigmas
            else None
        ),
        "pinned_sigma": f"{PINNED_SIGMA:.2f}",
        "pinned_sigma_n1000_t20_p_correct": target_t20["p_correct"],
        "privacy_target": "p_correct_leq_0.01_at_n1000_t_obs_leq_20",
        "verdict": "validated" if pinned_passes else "not_validated",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.trials <= 0:
        raise SystemExit("trials_must_be_positive")
    records = run_sweep(seed=args.seed, trials=args.trials)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(_stable_json(record) + "\n")
    summary = verdict_for(records)
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(_stable_json(summary) + "\n", encoding="utf-8")
    print(_stable_json(summary), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
