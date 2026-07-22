#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""SIM: CCSS Threshold Diffusion v0.1.

Phase 1576d research SIM. This models the future Graph-Diffused Threshold
Envelope design from Phase 1576c. It does not implement CCSS runtime, Shamir
sharing, relay batching, or any activation guard.
"""

from __future__ import annotations

import hashlib
import json
from math import comb
from pathlib import Path
import random
import time
from typing import Any


SIM_VERSION = "sim_ccss_threshold_diffusion_v0.1"
SEED = 1577
K_BATCH = 128
FIXED_BUNDLE_BYTES = 65536
BATCH_WINDOW_S = 120.0
SOURCE_EDGE_BURST_WINDOW_S = 1.0
OUTPUT_PATH = Path("out/sim_ccss_threshold_diffusion_results.json")

MN_PAIRS = [(2, 3), (3, 5), (3, 7), (5, 9)]
K_VALUES = [64, 128, 256]
COVER_RATIOS = [1, 4, 8, 16]
P_PATH_VALUES = [0.5, 0.6, 0.7, 0.8, 0.9, 0.99]
ADVERSARY_CLASSES = [
    "relay_output",
    "honest_relay",
    "malicious_relay",
    "source_edge_gpo",
]
N_TRIALS = 500


def _row_seed(*parts: object) -> int:
    payload = json.dumps(parts, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(str(SEED).encode("ascii") + b":" + payload).digest()
    return int.from_bytes(digest[:8], "big")


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, allow_nan=False, indent=2) + "\n"


def p_delivery_analytical(n: int, m: int, p: float) -> float:
    return sum(comb(n, i) * (p**i) * ((1 - p) ** (n - i)) for i in range(m, n + 1))


def bandwidth_multiplier(n: int, cover_ratio: int) -> float:
    return float(n * (1 + cover_ratio))


def relay_guessing_advantage(k: int) -> float:
    return 1.0 / float(k)


def productive_cover_useful_work_ratio(cover_ratio: int) -> float:
    if cover_ratio >= 8:
        return 0.90
    if cover_ratio >= 4:
        return 0.80
    if cover_ratio >= 2:
        return 0.65
    return 0.50


def simulate_delivery(
    *,
    n: int,
    m: int,
    p_path: float,
    n_trials: int,
    rng: random.Random,
) -> float:
    successes = 0
    for _ in range(n_trials):
        arrived = sum(1 for _ in range(n) if rng.random() < p_path)
        successes += int(arrived >= m)
    return successes / n_trials


def _relay_output_linking_success(
    *,
    n: int,
    m: int,
    k: int,
    rng: random.Random,
) -> bool:
    linked = sum(1 for _ in range(n) if rng.random() < 1.0 / float(k))
    return linked >= m


def _honest_relay_linking_success(
    *,
    n: int,
    m: int,
    rng: random.Random,
) -> bool:
    share_times = [rng.uniform(0.0, BATCH_WINDOW_S) for _ in range(n)]
    eps_s = 1.0
    best_cluster = 0
    for t_ref in share_times:
        best_cluster = max(best_cluster, sum(1 for t in share_times if abs(t - t_ref) <= eps_s))
    return best_cluster >= m


def _malicious_relay_linking_success(
    *,
    n: int,
    m: int,
    k: int,
    cover_ratio: int,
    rng: random.Random,
) -> bool:
    stripped_k = max(1, k - cover_ratio)
    linked = sum(1 for _ in range(n) if rng.random() < 1.0 / float(stripped_k))
    return linked >= m


def _source_edge_gpo_linking_success(
    *,
    n: int,
    m: int,
    rng: random.Random,
) -> bool:
    # Vulnerable ingress model: one sender emits all shares inside one client
    # session burst. Without an L6 shuffle, source-edge observation can group
    # the burst even though relay-output fields remain opaque.
    session_start = rng.uniform(0.0, BATCH_WINDOW_S - SOURCE_EDGE_BURST_WINDOW_S)
    share_times = [
        session_start + rng.uniform(0.0, SOURCE_EDGE_BURST_WINDOW_S) for _ in range(n)
    ]
    return (max(share_times) - min(share_times) <= SOURCE_EDGE_BURST_WINDOW_S) and n >= m


def simulate_share_linking(
    *,
    n: int,
    m: int,
    k: int,
    cover_ratio: int,
    adversary_class: str,
    n_trials: int,
    rng: random.Random,
) -> float:
    successes = 0
    for _ in range(n_trials):
        if adversary_class == "relay_output":
            success = _relay_output_linking_success(n=n, m=m, k=k, rng=rng)
        elif adversary_class == "honest_relay":
            success = _honest_relay_linking_success(n=n, m=m, rng=rng)
        elif adversary_class == "malicious_relay":
            success = _malicious_relay_linking_success(
                n=n,
                m=m,
                k=k,
                cover_ratio=cover_ratio,
                rng=rng,
            )
        elif adversary_class == "source_edge_gpo":
            success = _source_edge_gpo_linking_success(n=n, m=m, rng=rng)
        else:
            raise ValueError(f"unknown_adversary_class:{adversary_class}")
        successes += int(success)
    return successes / n_trials


def run_config(
    *,
    m: int,
    n: int,
    k: int,
    cover_ratio: int,
    p_path: float,
    adversary_class: str,
) -> dict[str, Any]:
    if not (n > m >= 2):
        raise ValueError("threshold_must_be_meaningful")
    if k < 64:
        raise ValueError("minimum_cell_size_violation")
    if cover_ratio < 1:
        raise ValueError("cover_required")
    warnings: list[str] = []
    if n > k:
        warnings.append("shares_exceed_cell_capacity")

    rng = random.Random(_row_seed(m, n, k, cover_ratio, p_path, adversary_class))
    analytical = p_delivery_analytical(n=n, m=m, p=p_path)
    empirical = simulate_delivery(
        n=n,
        m=m,
        p_path=p_path,
        n_trials=N_TRIALS,
        rng=rng,
    )
    linking = simulate_share_linking(
        n=n,
        m=m,
        k=k,
        cover_ratio=cover_ratio,
        adversary_class=adversary_class,
        n_trials=N_TRIALS,
        rng=rng,
    )

    return {
        "m": m,
        "n": n,
        "k": k,
        "cover_ratio": cover_ratio,
        "p_path": p_path,
        "adversary_class": adversary_class,
        "p_delivery_analytical": round(analytical, 12),
        "p_delivery_empirical": round(empirical, 12),
        "p_delivery_abs_error": round(abs(empirical - analytical), 12),
        "guessing_advantage": round(relay_guessing_advantage(k), 12),
        "p_share_linking_success": round(linking, 12),
        "recipient_scan_cost_envelopes": k,
        "relay_envelopes_per_message": n * (1 + cover_ratio),
        "bandwidth_multiplier": bandwidth_multiplier(n, cover_ratio),
        "productive_cover_useful_work_ratio": productive_cover_useful_work_ratio(cover_ratio),
        "n_trials": N_TRIALS,
        "warnings": warnings,
    }


def run_sweep() -> dict[str, Any]:
    started = time.time()
    results: list[dict[str, Any]] = []
    for m, n in MN_PAIRS:
        for k in K_VALUES:
            for cover_ratio in COVER_RATIOS:
                for p_path in P_PATH_VALUES:
                    for adversary_class in ADVERSARY_CLASSES:
                        results.append(
                            run_config(
                                m=m,
                                n=n,
                                k=k,
                                cover_ratio=cover_ratio,
                                p_path=p_path,
                                adversary_class=adversary_class,
                            )
                        )

    target = [
        row
        for row in results
        if row["m"] == 3
        and row["n"] == 7
        and row["k"] == 128
        and row["cover_ratio"] == 8
        and row["p_path"] == 0.8
    ]
    return {
        "sim_version": SIM_VERSION,
        "seed": SEED,
        "phase": "1576d",
        "scope": "research_sim_only_no_runtime_activation",
        "source_spec": "docs/specs/ilc_ccss_graph_diffused_threshold_envelope_design_1576c_v0.1.md",
        "parameters": {
            "k_batch": K_BATCH,
            "fixed_bundle_bytes": FIXED_BUNDLE_BYTES,
            "batch_window_s": BATCH_WINDOW_S,
            "source_edge_burst_window_s": SOURCE_EDGE_BURST_WINDOW_S,
            "mn_pairs": MN_PAIRS,
            "k_values": K_VALUES,
            "cover_ratios": COVER_RATIOS,
            "p_path_values": P_PATH_VALUES,
            "adversary_classes": ADVERSARY_CLASSES,
            "n_trials": N_TRIALS,
        },
        "results": results,
        "target_rows_m3_n7_k128_cover8_p08": target,
        "summary": {
            "result_count": len(results),
            "target_relay_output_p_delivery_analytical": next(
                row["p_delivery_analytical"]
                for row in target
                if row["adversary_class"] == "relay_output"
            ),
            "target_relay_output_guessing_advantage": next(
                row["guessing_advantage"]
                for row in target
                if row["adversary_class"] == "relay_output"
            ),
            "target_relay_output_bandwidth_multiplier": next(
                row["bandwidth_multiplier"]
                for row in target
                if row["adversary_class"] == "relay_output"
            ),
            "target_source_edge_gpo_linking_success": next(
                row["p_share_linking_success"]
                for row in target
                if row["adversary_class"] == "source_edge_gpo"
            ),
            "source_edge_gpo_requires_l6_shuffle": True,
            "threshold_diffusion_sim_results_phase_1576d": True,
        },
        "elapsed_seconds": round(time.time() - started, 6),
        "non_claims": {
            "runtime_activated": False,
            "guard_cleared": False,
            "formal_anonymity_proven": False,
            "gpo_defeated_without_l6": False,
            "shamir_implemented_in_ilc_core": False,
        },
    }


def main() -> None:
    data = run_sweep()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(_stable_json(data), encoding="utf-8")
    print(
        "PASS: "
        f"{data['summary']['result_count']} result records written to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
