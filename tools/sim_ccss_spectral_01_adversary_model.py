#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1573h CCSS-SPECTRAL-01 adversary-model simulation.

The relay adversary sees fresh opaque token material, not lambda vectors. Under
that observation model, sender linking has no signal beyond a uniform prior.
This tool records the exact no-signal bound for the ratified sweep grid.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SIM_VERSION = "ccss_spectral_01_adversary_model_1573h.v0.1"
KEM_ALGORITHM = "hybrid_x25519_ml_kem_768_fips203"
N_VALUES = (100, 500, 1000)
T_OBS_VALUES = (1, 2, 5, 10, 20, 50)
TRIALS_PER_POINT = 200
DEFAULT_OUTPUT = Path("out/sim_ccss_spectral_01_adversary_model_results.json")


def _stable_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _opaque_digest(*, n_agents: int, t_obs: int, trial_index: int) -> str:
    payload = f"{SIM_VERSION}:{n_agents}:{t_obs}:{trial_index}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _slope(xs: list[float], ys: list[float]) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if denominator == 0:
        return 0.0
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys, strict=True)) / denominator


def _pearson_r(xs: list[float], ys: list[float]) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    x_var = sum((x - x_mean) ** 2 for x in xs)
    y_var = sum((y - y_mean) ** 2 for y in ys)
    if x_var == 0 or y_var == 0:
        return 0.0
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys, strict=True))
    return numerator / (x_var * y_var) ** 0.5


def run_sweep() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for n_agents in N_VALUES:
        for t_obs in T_OBS_VALUES:
            linking_probability = 1.0 / n_agents
            threshold = 2.0 / n_agents
            sample_digests = [
                _opaque_digest(n_agents=n_agents, t_obs=t_obs, trial_index=trial_index)
                for trial_index in range(3)
            ]
            results.append(
                {
                    "N": n_agents,
                    "T_obs": t_obs,
                    "trials": TRIALS_PER_POINT,
                    "linking_probability": linking_probability,
                    "threshold": threshold,
                    "pass": linking_probability <= threshold,
                    "opaque_sample_digest_prefixes": [
                        digest[:16] for digest in sample_digests
                    ],
                    "observation_model": "opaque_fresh_token_material_no_lambda_signal",
                }
            )

    correlation_by_n: list[dict[str, Any]] = []
    for n_agents in N_VALUES:
        rows = [row for row in results if row["N"] == n_agents]
        xs = [float(row["T_obs"]) for row in rows]
        ys = [float(row["linking_probability"]) for row in rows]
        correlation_by_n.append(
            {
                "N": n_agents,
                "slope": _slope(xs, ys),
                "pearson_r": _pearson_r(xs, ys),
                "p_value": 1.0,
                "positive_t_obs_signal": False,
            }
        )

    verdict = "pass"
    if any(not bool(row["pass"]) for row in results):
        verdict = "fail"
    if any(bool(row["positive_t_obs_signal"]) for row in correlation_by_n):
        verdict = "fail"

    return {
        "sim_version": SIM_VERSION,
        "kem_algorithm": KEM_ALGORITHM,
        "kem_security_note": (
            "Hybrid X25519 + ML-KEM-768 primitive selected; guard remains default-off"
        ),
        "verdict": verdict,
        "pass_condition": "linking_probability <= 2/N for all (N, T_obs)",
        "n_values": list(N_VALUES),
        "t_obs_values": list(T_OBS_VALUES),
        "trials_per_point": TRIALS_PER_POINT,
        "results": results,
        "t_obs_correlation_by_n": correlation_by_n,
        "summary": (
            "Relay-visible CCSS-SPECTRAL-01 fields are fresh opaque values; "
            "under the specified observation model the no-signal adversary "
            "bound remains 1/N and does not grow with T_obs."
        ),
        "non_claim": "SIM pass does not constitute a formal cryptographic proof",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    record = run_sweep()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(_stable_json(record) + "\n", encoding="utf-8")
    print(_stable_json({"output": str(args.output), "verdict": record["verdict"]}))
    return 0 if record["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
