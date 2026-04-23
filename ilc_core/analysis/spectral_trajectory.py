# H-006b Part 3: temporal spectral trajectory analytics.
#
# Gate history:
#   sim_spectral_embedding_01_clusters_viable=true (H-006b Part 1 SIM, commit 550bfc77)
#   sim_local_lambda2_viable=true (H-006b Part 2 SIM, commit d76c562e)
#     → both gates positive; Part 3 implementation cleared
#   run_h006b_multiscale_spectral_verdict=pass (commit 0e494432)
#
# Authority: docs/antigravity_tasks/codex_brief__h006b_multiscale_spectral_analysis.md §4
# ADR-0032 §2.4: detection pattern table (ΔΔλ / Δλ sign combinations)
# SIM epoch drift results: docs/research/ilc_sim_spectral_multiscale_results_v0.1.md §11
#   — 3/4 content_type clusters showed monotonic λ₂ growth across three epochs
#   — governance cluster dipped -0.000515 at epoch 2 then rose +0.001343 at epoch 3
#     (consistent with non-uniform edge additions in a sparse cluster; not a failure)
#
# Key design choices:
#   N_BATCH=1 (H-005 R7): always full eigendecomposition, never lazy Rayleigh.
#   T2-class topologies show spectral_gap ≈ 0.0094, which puts them below
#   RAYLEIGH_SPECTRAL_GAP_MIN=0.05 — Rayleigh error was 41% after one epoch.
#   Both lambda2 and spectral_gap are computed from a single LAPACK call
#   (_compute_fiedler_and_gap) to guarantee mutual consistency.
#
# Scope: standalone analytics type only. EpochSettlementRecord is NOT modified here.
#   delta_lambda_vec, eigenvec_epoch, spectral_gap fields in the epoch KPI store
#   are gated on CDL H-CON-03 (not yet opened). Gossip wiring is H-013 scope.

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import scipy.linalg

from ilc_core.analysis.laplacian_analytics import LaplacianError


@dataclass
class SpectralEpochRecord:
    """One epoch's snapshot in the temporal spectral trajectory.

    All float fields are dimensionless (normalized Laplacian eigenvalues ∈ [0, 2]).

    Fields:
        epoch: Validation-epoch number (1-minute cadence per CDL-051).
        lambda2: Fiedler value λ₂ — the second-smallest eigenvalue of the
            normalized hypergraph Laplacian.  λ₂ = 0 means the graph is
            disconnected; λ₂ close to THETA_FLOOR=0.001 is partition-risk.
        lambda2_delta: λ₂(t) − λ₂(t−1).  Positive = topology strengthening,
            negative = connectivity declining.  0.0 when history is empty.
        lambda2_accel: Δλ₂(t) − Δλ₂(t−1)  [second difference, ΔΔλ₂].
            Used with lambda2_delta for the four-quadrant detection table
            (see update_spectral_trajectory docstring).  0.0 when fewer than
            two prior records exist.
        spectral_gap: λ₃ − λ₂.  Large gap means the Fiedler cut is stable
            and the lazy Rayleigh approximation is safe; small gap (< 0.05)
            means Fiedler direction is degenerate — full recompute required.
        fiedler_vector_epoch: Epoch at which v₂ was last fully recomputed.
            In this implementation fiedler_vector_epoch always equals epoch
            because N_BATCH=1 forces a full recompute every epoch.  The field
            is retained for forward compatibility with a future batched path.
    """
    epoch: int
    lambda2: float
    lambda2_delta: float
    lambda2_accel: float
    spectral_gap: float
    fiedler_vector_epoch: int


def _compute_fiedler_and_gap(L: np.ndarray) -> Tuple[float, float]:
    """Return (lambda2, spectral_gap) from a single eigendecomposition.

    Uses subset_by_index=[0, 2] for n >= 5, or full decomposition for smaller
    matrices, so that both values are derived from the same LAPACK call.  This
    ensures spectral_gap == lambda3 − lambda2 with no floating-point skew from
    two independent eigh calls on the same matrix.

    Special case n == 2: only two eigenvalues exist (λ₁, λ₂); there is no λ₃,
    so spectral_gap is defined as 0.0.

    Raises:
        LaplacianError: if L has fewer than 2 nodes.
    """
    n = L.shape[0]
    if n < 2:
        raise LaplacianError(
            "Laplacian must have at least 2 nodes for Fiedler computation"
        )
    if n == 2:
        # No λ₃ exists for a 2-node graph; gap is undefined → 0.0.
        evals, _ = scipy.linalg.eigh(L)
        return float(evals[1]), 0.0
    if n >= 5:
        # subset_by_index=[0, 2] returns eigenvalues at global sorted indices
        # 0, 1, 2 (three values): evals[0]=λ₁, evals[1]=λ₂, evals[2]=λ₃.
        evals, _ = scipy.linalg.eigh(L, subset_by_index=[0, 2])
    else:
        evals, _ = scipy.linalg.eigh(L)
    lambda2 = float(evals[1])
    lambda3 = float(evals[2])
    return lambda2, max(0.0, lambda3 - lambda2)


def update_spectral_trajectory(
    history: List[SpectralEpochRecord],
    L_new: np.ndarray,
    epoch: int,
) -> SpectralEpochRecord:
    """Compute the next spectral trajectory record from the latest Laplacian.

    Always uses full eigendecomposition via ``_compute_fiedler_and_gap()`` —
    no lazy Rayleigh path (N_BATCH=1 per H-005).  Both ``lambda2`` and
    ``spectral_gap`` are derived from the same LAPACK call so they are
    mutually consistent.

    ``lambda2_delta`` and ``lambda2_accel`` default to ``0.0`` when prior
    history is insufficient.

    Detection pattern table (ΔΔλ / Δλ sign combinations):

    | lambda2_accel sign | lambda2_delta sign | Pattern              | Interpretation              |
    |--------------------|--------------------|----------------------|-----------------------------|
    | +                  | +                  | Accelerating growth  | Topology strengthening      |
    | -                  | +                  | Decelerating growth  | Stabilizing                 |
    | +                  | -                  | Decelerating decline | Partition healing           |
    | -                  | -                  | Accelerating decline | Partition risk escalating   |

    Args:
        history: Prior records in ascending epoch order.
        L_new: Normalized hypergraph Laplacian for the current epoch.
        epoch: Current epoch number.  Must be strictly greater than
            ``history[-1].epoch`` when history is non-empty.

    Raises:
        ValueError: if ``epoch`` is not strictly greater than the last
            recorded epoch (non-monotonic history would produce silent sign
            errors in delta and accel).
        LaplacianError: if L_new has fewer than 2 nodes.

    Scope boundary: ``SpectralEpochRecord`` is a standalone analytics type. Do
    not wire it to ``EpochSettlementRecord``, ``delta_lambda_vec``, or any
    gossip path in this phase.
    """
    if history and epoch <= history[-1].epoch:
        raise ValueError(
            f"epoch {epoch} is not strictly greater than history[-1].epoch "
            f"{history[-1].epoch}; history must be in ascending epoch order"
        )

    lambda2, gap = _compute_fiedler_and_gap(L_new)

    lambda2_delta = 0.0
    lambda2_accel = 0.0
    if history:
        lambda2_delta = float(lambda2 - history[-1].lambda2)
    if len(history) >= 2:
        lambda2_accel = float(lambda2_delta - history[-1].lambda2_delta)

    return SpectralEpochRecord(
        epoch=epoch,
        lambda2=lambda2,
        lambda2_delta=lambda2_delta,
        lambda2_accel=lambda2_accel,
        spectral_gap=gap,
        fiedler_vector_epoch=epoch,
    )
