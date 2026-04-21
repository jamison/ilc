# ADR-0029: Spectral utility functions for hypergraph analytics.
#
# spectral_distance() is the routing metric used by spectral routing (SIM-ROUTING-01).
# It is defined here so it is always available as a primitive once the hyperedge
# substrate is in place, without waiting for the full beacon/routing implementation.
#
# Gate for full spectral pipeline: SIM-HYPEREDGE-01 -> SIM-SPECTRAL-01 -> CDL.
# Gate for spectral beacon emission: SIM-BEACON-01 (noise budget calibration).
# Gate for spectral routing: SIM-ROUTING-01 (convergence validation).
from __future__ import annotations

import math
from typing import List


def spectral_distance(fingerprint_a: List[float], fingerprint_b: List[float]) -> float:
    """
    L2 distance between two spectral fingerprints (top-k eigenvalue vectors).

    ||lambda_A - lambda_B||_2

    This is the routing metric for greedy spectral descent: a hop toward the peer
    whose fingerprint minimises this distance moves toward the target epistemic
    neighbourhood. Vectors must be the same length; shorter vector is zero-padded.
    """
    len_a, len_b = len(fingerprint_a), len(fingerprint_b)
    if len_a < len_b:
        fingerprint_a = fingerprint_a + [0.0] * (len_b - len_a)
    elif len_b < len_a:
        fingerprint_b = fingerprint_b + [0.0] * (len_a - len_b)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(fingerprint_a, fingerprint_b)))
