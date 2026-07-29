#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
SIM-BEACON-01: privacy / utility calibration for spectral beacon emission.

The committed model is deliberately bounded:

- signal centers come from H-006b local lambda2 cluster baselines
- production-floor scaling uses the SIM-001 10,000-agent floor as the larger
  Monte Carlo regime, not as a fresh graph generator
- output is a calibration recommendation for sigma, theta, and cadence

No runtime code is mutated here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np


CLUSTER_CENTERS = np.array([0.123813, 0.153647, 0.163024, 0.172453], dtype=float)

# Per-regime local-cluster jitter (std-dev of samples around each center).
# These are engineering estimates grounded in H-006b multiscale results:
#   - cluster centers span a total range of ~0.049 across 4 clusters
#   - average inter-cluster spacing is ~0.016
#   - N=500 testnet: validator neighborhoods are less stable; jitter ~0.0025
#     (≈15% of average inter-cluster spacing)
#   - N=10000 production floor: larger networks produce tighter spectral profiles;
#     jitter ~0.0015 (≈9% of average inter-cluster spacing)
# These values are not derived from a fresh graph generator (see module docstring).
# If H-006b or H-005 produce revised per-regime variance estimates, update here.
SCALES = {
    "N500": 0.0025,
    "N10000": 0.0015,
}
CANDIDATES = [
    (0.005, 0.010),
    (0.006, 0.010),
    (0.006, 0.012),
    (0.007, 0.012),
]


@dataclass(frozen=True)
class ScaleMetrics:
    fingerprint_accuracy: float
    proximity_tpr: float
    proximity_fpr: float
    proximity_fnr: float


def _simulate(scale_std: float, sigma: float, theta: float, *, seed: int = 42, n: int = 50_000) -> ScaleMetrics:
    rng = np.random.default_rng(seed)

    labels = rng.integers(0, len(CLUSTER_CENTERS), size=n)
    samples = rng.normal(CLUSTER_CENTERS[labels], scale_std)
    noisy = samples + rng.normal(0.0, sigma, size=n)
    pred = np.argmin(np.abs(noisy[:, None] - CLUSTER_CENTERS[None, :]), axis=1)
    fingerprint_accuracy = float((pred == labels).mean())

    same = rng.random(n) < 0.5
    same_idx = rng.integers(0, len(CLUSTER_CENTERS), size=n)
    pair = rng.choice(len(CLUSTER_CENTERS), size=(n, 2), replace=True)
    mask_samepair = pair[:, 0] == pair[:, 1]
    while mask_samepair.any():
        pair[mask_samepair, 1] = rng.integers(0, len(CLUSTER_CENTERS), size=mask_samepair.sum())
        mask_samepair = pair[:, 0] == pair[:, 1]

    a = np.where(
        same,
        rng.normal(CLUSTER_CENTERS[same_idx], scale_std),
        rng.normal(CLUSTER_CENTERS[pair[:, 0]], scale_std),
    ) + rng.normal(0.0, sigma, size=n)
    b = np.where(
        same,
        rng.normal(CLUSTER_CENTERS[same_idx], scale_std),
        rng.normal(CLUSTER_CENTERS[pair[:, 1]], scale_std),
    ) + rng.normal(0.0, sigma, size=n)

    predicted_positive = np.abs(a - b) <= theta
    tp = np.sum(same & predicted_positive)
    fn = np.sum(same & ~predicted_positive)
    fp = np.sum(~same & predicted_positive)
    tn = np.sum(~same & ~predicted_positive)
    tpr = tp / max(tp + fn, 1)
    fpr = fp / max(fp + tn, 1)
    return ScaleMetrics(
        fingerprint_accuracy=round(fingerprint_accuracy, 3),
        proximity_tpr=round(float(tpr), 3),
        proximity_fpr=round(float(fpr), 3),
        proximity_fnr=round(float(1.0 - tpr), 3),
    )


def _raw_fingerprint_accuracy(scale_std: float, *, seed: int = 42, n: int = 50_000) -> float:
    rng = np.random.default_rng(seed)
    labels = rng.integers(0, len(CLUSTER_CENTERS), size=n)
    samples = rng.normal(CLUSTER_CENTERS[labels], scale_std)
    pred = np.argmin(np.abs(samples[:, None] - CLUSTER_CENTERS[None, :]), axis=1)
    return round(float((pred == labels).mean()), 3)


def _passes(metrics: dict[str, ScaleMetrics]) -> bool:
    return all(
        value.proximity_tpr >= 0.79
        and value.proximity_fpr <= 0.20
        and value.fingerprint_accuracy <= 0.82
        for value in metrics.values()
    )


def main() -> None:
    output: dict[str, object] = {
        "cluster_centers": [round(x, 6) for x in CLUSTER_CENTERS.tolist()],
        "raw_fingerprint_accuracy": {
            scale: _raw_fingerprint_accuracy(scale_std)
            for scale, scale_std in SCALES.items()
        },
        "candidate_metrics": [],
    }

    chosen: dict[str, object] | None = None
    for sigma, theta in CANDIDATES:
        metrics = {
            scale: _simulate(scale_std, sigma, theta)
            for scale, scale_std in SCALES.items()
        }
        record = {
            "sigma": sigma,
            "theta": theta,
            "metrics": {
                scale: metrics[scale].__dict__
                for scale in metrics
            },
            "passes": _passes(metrics),
        }
        output["candidate_metrics"].append(record)
        if chosen is None and record["passes"]:
            chosen = record

    # frequency_epochs is a design judgment, NOT derived from the simulation above.
    # The simulation calibrates sigma and theta only.  The cadence of 4 epochs is
    # grounded in H-006b local-lambda2 drift observations: per-epoch delta values
    # fall in the 0.0005–0.0051 band, which is the same order of magnitude as the
    # selected sigma=0.005.  Emitting every epoch would therefore add noise-dominated,
    # easily-correlatable structure; a 4-epoch cadence lets real signal accumulate
    # while reducing tracking surface.  This is a routing/privacy engineering trade-off,
    # not a constitutional constant; it can be revisited by a future SIM-ROUTING-01 pass.
    output["recommended"] = {
        "sigma": chosen["sigma"],
        "theta": chosen["theta"],
        "frequency_epochs": 4,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
