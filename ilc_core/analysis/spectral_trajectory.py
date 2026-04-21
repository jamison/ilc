"""H-006b Part 3: temporal spectral trajectory analytics.

This module keeps spectral trajectory state in a standalone analytics type. It
does not mutate EpochSettlementRecord, gossip payloads, or any settlement path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from ilc_core.analysis.laplacian_analytics import compute_fiedler, spectral_gap


@dataclass
class SpectralEpochRecord:
    epoch: int
    lambda2: float
    lambda2_delta: float
    lambda2_accel: float
    spectral_gap: float
    fiedler_vector_epoch: int


def update_spectral_trajectory(
    history: List[SpectralEpochRecord],
    L_new: np.ndarray,
    epoch: int,
) -> SpectralEpochRecord:
    """Compute the next spectral trajectory record from the latest Laplacian.

    Always uses full ``compute_fiedler()`` — no lazy Rayleigh path is allowed
    here because ``N_BATCH=1`` was selected in H-005.

    ``lambda2_delta`` and ``lambda2_accel`` default to ``0.0`` when prior
    history is insufficient.

    Detection pattern table (ΔΔλ / Δλ sign combinations):

    | lambda2_accel sign | lambda2_delta sign | Pattern              | Interpretation              |
    |--------------------|--------------------|----------------------|-----------------------------|
    | +                  | +                  | Accelerating growth  | Topology strengthening      |
    | -                  | +                  | Decelerating growth  | Stabilizing                 |
    | +                  | -                  | Decelerating decline | Partition healing           |
    | -                  | -                  | Accelerating decline | Partition risk escalating   |

    Scope boundary: ``SpectralEpochRecord`` is a standalone analytics type. Do
    not wire it to ``EpochSettlementRecord``, ``delta_lambda_vec``, or any
    gossip path in this phase.
    """

    lambda2, _fiedler = compute_fiedler(L_new)
    gap = spectral_gap(L_new)

    lambda2_delta = 0.0
    lambda2_accel = 0.0
    if history:
        lambda2_delta = float(lambda2 - history[-1].lambda2)
    if len(history) >= 2:
        lambda2_accel = float(lambda2_delta - history[-1].lambda2_delta)

    return SpectralEpochRecord(
        epoch=epoch,
        lambda2=float(lambda2),
        lambda2_delta=lambda2_delta,
        lambda2_accel=lambda2_accel,
        spectral_gap=float(gap),
        fiedler_vector_epoch=epoch,
    )
