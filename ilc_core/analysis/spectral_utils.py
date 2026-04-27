# ADR-0029: Spectral utility functions for hypergraph analytics.
#
# spectral_distance() is the routing metric used by spectral routing (SIM-ROUTING-01).
# It is defined here so it is always available as a primitive once the hyperedge
# substrate is in place, without waiting for the full beacon/routing implementation.
#
# compute_weight() is the deterministic weight function for HyperEdge.weight_params.
# w(e, t) = α(edge_type) × f(reuse_count) × decay(stake, epoch_created, t)
# PROVISIONAL: reuse_count functional form is log(n+1) pending SIM-REUSE-01 validation.
# CDL required before any of these parameters are constitutionally locked.
#
# Gate for full spectral pipeline: SIM-HYPEREDGE-01 -> SIM-SPECTRAL-01 -> CDL.
# Gate for spectral beacon emission: SIM-BEACON-01 (noise budget calibration).
# Gate for spectral routing: SIM-ROUTING-01 (convergence validation).
# Gate for weight parameterization: SIM-REUSE-01 + CDL (EdgeType coefficients).
from __future__ import annotations

import math
from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:
    from ilc_core.types import WeightParams


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


def compute_weight(
    params: "WeightParams",
    current_epoch: int,
    cdl_v1_decay_fn: Optional[Callable[[float, int], float]] = None,
) -> float:
    """Compute edge weight deterministically from WeightParams.

    w(e, t) = α(edge_type) × f(reuse_count) × decay(stake, t)

    Where:
      α(edge_type)   = params.edge_type_coefficient  (CDL-ratified per type)
      f(reuse_count) = log(reuse_count + 1)          (PROVISIONAL: SIM-REUSE-01 pending)
      decay(stake,t) = cdl_v1_decay_fn(float(stake), current_epoch) if supplied,
                       else float(stake) (no decay — for tests and analytics)

    IMPORTANT: The reuse_count functional form (log vs. linear vs. capped) and
    the edge_type_coefficient values are UNRATIFIED. SIM-REUSE-01 must validate
    stability and gaming resistance before any CDL locks these values.
    Do not use this output in any consensus-critical path until CDL ratified.

    Pure function — no side effects, no I/O, deterministic.
    """
    base_stake = float(params.stake)
    decayed_stake = (
        cdl_v1_decay_fn(base_stake, current_epoch)
        if cdl_v1_decay_fn is not None
        else base_stake
    )
    # Provisional reuse signal: log(n+1) so zero reuse → 0 additive, not multiplicative zero
    reuse_signal = math.log(params.reuse_count + 1)
    return params.edge_type_coefficient * decayed_stake * (1.0 + reuse_signal)
