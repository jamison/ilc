# ADR-0029: Hypergraph Laplacian analytics for ILC partition-risk monitoring.
#
# Implements the full Laplacian analytics pipeline from SIM-SPECTRAL-01 (H-005).
# Calibration constants are locked to the H-005 results document:
#   docs/research/ilc_sim_spectral_01_results_v0.1.md
#
# Gate history:
#   H-001 positive → W(e) = stake_harmonic_mean selected
#   H-004 accepted → ADR-0029 accepted
#   H-005 positive → sim_spectral_01_lambda2_signal_viable=true
#   H-006a → this implementation

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np
import scipy.linalg


# ---------------------------------------------------------------------------
# Calibration constants from SIM-SPECTRAL-01 (H-005)
# ---------------------------------------------------------------------------

# Full eigendecomposition every epoch; no lazy Rayleigh for T2-class topologies.
N_BATCH: int = 1

# Frobenius norm of Laplacian delta that triggers an immediate forced recompute.
EPSILON_TRIGGER: float = 0.3391

# Maximum acceptable relative Rayleigh approximation error (1%).
DELTA_MAX_REL: float = 0.01

# Node count below which bootstrap mode is active (use C(t) instead of raw λ₂).
N_BOOTSTRAP: int = 44

# Partition-risk alert threshold on the established subgraph.
THETA_FLOOR: float = 0.001

# Rayleigh approximation is only valid when spectral_gap > this value.
RAYLEIGH_SPECTRAL_GAP_MIN: float = 0.05

# Minimum hyperedge memberships for a node to be part of the established subgraph.
MIN_HYPEREDGE_MEMBERSHIPS: int = 2


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class RayleighGateError(ValueError):
    """Raised when Rayleigh approximation is requested below the spectral_gap gate."""


class LaplacianError(ValueError):
    """Raised for structurally invalid inputs to Laplacian construction."""


# ---------------------------------------------------------------------------
# Weight function
# ---------------------------------------------------------------------------


def _stake_harmonic_mean(stakes: Sequence[float]) -> float:
    """W(e) = harmonic mean of member stakes (H-001 result)."""
    if not stakes:
        return 0.0
    n = len(stakes)
    # Guard against zero-stake members — they produce infinite harmonic mean
    # terms which would make the edge weight 0, correctly reflecting that a
    # Sybil node in a hyperedge kills the edge's connectivity contribution.
    if any(s <= 0.0 for s in stakes):
        return 0.0
    return n / sum(1.0 / s for s in stakes)


# ---------------------------------------------------------------------------
# Established-subgraph filter
# ---------------------------------------------------------------------------


def established_subgraph_nodes(
    nodes: Sequence[str],
    hyperedge_memberships: Dict[str, int],
    min_memberships: int = MIN_HYPEREDGE_MEMBERSHIPS,
) -> List[str]:
    """Return nodes with at least min_memberships hyperedge memberships.

    Used when computing the admission-gate Laplacian: single-connection new
    arrivals are excluded to prevent their pendant edges from collapsing λ₂
    to zero (see SIM-SPECTRAL-01 R4 / §4).
    """
    return [n for n in nodes if hyperedge_memberships.get(n, 0) >= min_memberships]


# ---------------------------------------------------------------------------
# Laplacian construction
# ---------------------------------------------------------------------------


def build_hypergraph_laplacian(
    nodes: Sequence[str],
    hyperedges: Sequence[Sequence[str]],
    stakes: Dict[str, float],
) -> Tuple[np.ndarray, List[str]]:
    """Build the normalized hypergraph Laplacian L = I - D^{-1/2} Θ D^{-1/2}.

    Args:
        nodes: Ordered list of node IDs to include in the Laplacian.
        hyperedges: Each hyperedge is a list of node IDs (members).
        stakes: Mapping of node_id → stake (used for W(e) = stake_harmonic_mean).

    Returns:
        (L, ordered_nodes) where L is an (n×n) numpy float64 array and
        ordered_nodes is the canonical node ordering for interpreting L rows/cols.

    Raises:
        LaplacianError: if nodes list is empty or a hyperedge references an
            unknown node.
    """
    node_list = list(nodes)
    n = len(node_list)
    if n == 0:
        raise LaplacianError("nodes list must be non-empty")

    node_idx: Dict[str, int] = {node: i for i, node in enumerate(node_list)}

    # Validate hyperedge membership
    for edge in hyperedges:
        for member in edge:
            if member not in node_idx:
                raise LaplacianError(
                    f"hyperedge member '{member}' is not in the node list"
                )

    # Build the theta matrix Θ and weighted degree vector d.
    #
    # Θ[u,v] = Σ_{e: u,v ∈ e} W(e) / |e|   (Zhou et al. 2006)
    # d[v]   = Σ_{e: v ∈ e} W(e)            (weighted vertex degree, NOT Θ diagonal)
    #
    # The diagonal of Θ is Σ_{e: v∈e} W(e)/|e|, which is strictly smaller than d[v]
    # for any hyperedge with |e| > 1.  Using np.diag(Θ) for d would produce a
    # non-positive-semidefinite Laplacian with negative eigenvalues.
    theta = np.zeros((n, n), dtype=np.float64)
    d = np.zeros(n, dtype=np.float64)

    for edge in hyperedges:
        if len(edge) < 2:
            continue  # self-loops add no connectivity
        member_stakes = [stakes.get(m, 0.0) for m in edge]
        w = _stake_harmonic_mean(member_stakes)
        if w <= 0.0:
            continue
        deg = float(len(edge))
        indices = [node_idx[m] for m in edge]
        for i in indices:
            d[i] += w          # weighted degree: sum of W(e) for edges containing v
            for j in indices:
                theta[i, j] += w / deg

    # Normalize: L = I - D^{-1/2} Θ D^{-1/2}
    # For isolated nodes (d[i] == 0): d_inv_sqrt[i] = 0 and theta[i,:] = 0,
    # so L[i,j] = I[i,j].  L[i,i] = 1 (eigenvalue 1), NOT 0.
    d_sqrt = np.sqrt(np.maximum(d, 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        d_inv_sqrt = np.where(d_sqrt > 0.0, 1.0 / d_sqrt, 0.0)
    L = np.eye(n, dtype=np.float64) - d_inv_sqrt[:, None] * theta * d_inv_sqrt[None, :]

    # Symmetrize to correct for floating-point drift
    L = (L + L.T) / 2.0

    return L, node_list


# ---------------------------------------------------------------------------
# Eigendecomposition
# ---------------------------------------------------------------------------


def compute_fiedler(L: np.ndarray) -> Tuple[float, np.ndarray]:
    """Full eigendecomposition; return (λ₂, v₂) — the Fiedler value and vector.

    Always performs full recomputation. The lazy Rayleigh path is separate
    (rayleigh_approx_lambda2) and gated on spectral_gap > RAYLEIGH_SPECTRAL_GAP_MIN.

    Args:
        L: Symmetric (n×n) normalized hypergraph Laplacian.

    Returns:
        (lambda2, v2) where lambda2 is the second-smallest eigenvalue (float)
        and v2 is the corresponding eigenvector (length-n numpy array).

    Raises:
        LaplacianError: if L has fewer than 2 nodes.
    """
    n = L.shape[0]
    if n < 2:
        raise LaplacianError("Laplacian must have at least 2 nodes for Fiedler computation")

    # eigh returns eigenvalues in ascending order for symmetric matrices.
    # subset_by_index=[0, 1] returns only the two smallest — efficient for large n.
    if n >= 4:
        eigenvalues, eigenvectors = scipy.linalg.eigh(L, subset_by_index=[0, 1])
    else:
        # For very small matrices eigh with subset is less stable; use full decomp.
        eigenvalues, eigenvectors = scipy.linalg.eigh(L)

    lambda2 = float(eigenvalues[1])
    v2 = eigenvectors[:, 1]

    return lambda2, v2


def spectral_gap(L: np.ndarray) -> float:
    """Return λ₃ − λ₂ (the spectral gap).

    Used to gate Rayleigh approximation validity. A gap < RAYLEIGH_SPECTRAL_GAP_MIN
    means the Fiedler vector direction is unstable under perturbation and
    the lazy Rayleigh path must not be used.

    Args:
        L: Symmetric (n×n) normalized hypergraph Laplacian.

    Returns:
        gap = λ₃ − λ₂ (float). Returns 0.0 if n < 3.
    """
    n = L.shape[0]
    if n < 3:
        return 0.0

    if n >= 5:
        eigenvalues, _ = scipy.linalg.eigh(L, subset_by_index=[0, 2])
        lambda2 = float(eigenvalues[1])
        lambda3 = float(eigenvalues[2])
    else:
        eigenvalues, _ = scipy.linalg.eigh(L)
        lambda2 = float(eigenvalues[1])
        lambda3 = float(eigenvalues[2])

    return max(0.0, lambda3 - lambda2)


# ---------------------------------------------------------------------------
# Rayleigh approximation (lazy path — gated)
# ---------------------------------------------------------------------------


def rayleigh_approx_lambda2(
    L_new: np.ndarray,
    v2_prev: np.ndarray,
    gap: float,
) -> float:
    """Estimate λ₂(t) using the Rayleigh quotient from the previous Fiedler vector.

    λ₂(t) ≈ v₂(t−1)ᵀ · L(t) · v₂(t−1)

    This is the lazy recomputation path. It is only valid when the spectral gap
    is large enough that the Fiedler vector direction is stable. Per SIM-SPECTRAL-01
    R8, T2-class topologies (gap ≈ 0.0094) show 41% error after one epoch —
    well beyond DELTA_MAX_REL = 0.01. Only use this when gap > RAYLEIGH_SPECTRAL_GAP_MIN.

    Args:
        L_new: Updated Laplacian at time t.
        v2_prev: Fiedler eigenvector from the previous epoch (t−1).
        gap: Spectral gap from the previous epoch.

    Returns:
        Estimated λ₂ (float).

    Raises:
        RayleighGateError: if gap <= RAYLEIGH_SPECTRAL_GAP_MIN.
    """
    if gap <= RAYLEIGH_SPECTRAL_GAP_MIN:
        raise RayleighGateError(
            f"spectral_gap={gap:.6f} <= RAYLEIGH_SPECTRAL_GAP_MIN={RAYLEIGH_SPECTRAL_GAP_MIN}; "
            "use compute_fiedler() for full recomputation"
        )
    v = v2_prev / np.linalg.norm(v2_prev)
    return float(v @ L_new @ v)


# ---------------------------------------------------------------------------
# Laplacian delta (for ε_trigger check)
# ---------------------------------------------------------------------------


def delta_laplacian_frobenius(L_new: np.ndarray, L_old: np.ndarray) -> float:
    """Return ‖L_new − L_old‖_F (Frobenius norm of the Laplacian delta).

    Used to decide whether to force a full recompute mid-batch even when
    N_BATCH > 1. If ‖ΔL‖_F > EPSILON_TRIGGER, trigger immediate recompute.

    Per SIM-SPECTRAL-01 R7, EPSILON_TRIGGER = 0.3391 was observed at the
    first epoch threshold crossing for T2 (panel-heavy topology).
    """
    return float(np.linalg.norm(L_new - L_old, ord="fro"))


# ---------------------------------------------------------------------------
# Fiedler centrality
# ---------------------------------------------------------------------------


def fiedler_centrality(
    v2: np.ndarray,
    node_list: List[str],
) -> Dict[str, float]:
    """Return per-node Fiedler centrality scores |v₂[i]|, normalized to [0, 1].

    Non-redundant with stake-weighted degree (ρ ≈ 0.40–0.52 across topologies;
    SIM-SPECTRAL-01 R5 / §5). Measures how structurally bridging a node is.

    Args:
        v2: Fiedler eigenvector (length n).
        node_list: Canonical node ordering matching v2 indices.

    Returns:
        Dict mapping node_id → centrality in [0, 1].
    """
    abs_v2 = np.abs(v2)
    max_val = float(np.max(abs_v2))
    if max_val == 0.0:
        return {node: 0.0 for node in node_list}
    normalized = abs_v2 / max_val
    return {node: float(normalized[i]) for i, node in enumerate(node_list)}


# ---------------------------------------------------------------------------
# Bootstrap Fiedler concentration
# ---------------------------------------------------------------------------


def bootstrap_fiedler_concentration(
    v2: np.ndarray,
    node_list: List[str],
    genesis_node_ids: Sequence[str],
) -> float:
    """Return C(t) = mean |v₂[genesis]| / mean |v₂| global.

    Used below N_BOOTSTRAP=44 instead of raw λ₂ for partition-risk assessment.
    Below N_BOOTSTRAP, raw λ₂ is near-zero even for healthy sparse bootstraps
    (SIM-SPECTRAL-01 R1/R2). C(t) > 0.5 is the bootstrap health gate.

    Args:
        v2: Fiedler eigenvector.
        node_list: Canonical node ordering.
        genesis_node_ids: IDs of genesis (founding) nodes.

    Returns:
        C(t) float. Returns 0.0 if no genesis nodes are present in node_list.
    """
    node_idx = {node: i for i, node in enumerate(node_list)}
    abs_v2 = np.abs(v2)

    genesis_indices = [node_idx[g] for g in genesis_node_ids if g in node_idx]
    if not genesis_indices:
        return 0.0

    global_mean = float(np.mean(abs_v2))
    if global_mean == 0.0:
        return 0.0

    genesis_mean = float(np.mean(abs_v2[genesis_indices]))
    return genesis_mean / global_mean


# ---------------------------------------------------------------------------
# Partition-risk alert
# ---------------------------------------------------------------------------


def partition_risk_alert(
    lambda2: float,
    n_nodes: int,
    genesis_node_ids: Sequence[str],
    v2: np.ndarray,
    node_list: List[str],
) -> Tuple[bool, str]:
    """Integrate bootstrap and production-mode partition-risk logic.

    Bootstrap mode (n_nodes < N_BOOTSTRAP=44):
        Alert if C(t) <= 0.5. Raw λ₂ is suppressed — it is unreliable
        for sparse bootstrap graphs (SIM-SPECTRAL-01 R1).

    Production mode (n_nodes >= N_BOOTSTRAP):
        Alert if λ₂ < THETA_FLOOR=0.001 on the established subgraph.

    Args:
        lambda2: Fiedler value from compute_fiedler().
        n_nodes: Number of nodes in the current Laplacian.
        genesis_node_ids: IDs of genesis nodes (for C(t) computation).
        v2: Fiedler eigenvector.
        node_list: Canonical node ordering.

    Returns:
        (alert: bool, reason: str) — True means partition risk detected.
    """
    if n_nodes < N_BOOTSTRAP:
        ct = bootstrap_fiedler_concentration(v2, node_list, genesis_node_ids)
        if ct <= 0.5:
            return True, f"bootstrap_mode: C(t)={ct:.4f} <= 0.5 (genesis concentration too low)"
        return False, f"bootstrap_mode: C(t)={ct:.4f} > 0.5 (healthy)"

    if lambda2 < THETA_FLOOR:
        return True, f"production_mode: lambda2={lambda2:.6f} < theta_floor={THETA_FLOOR}"
    return False, f"production_mode: lambda2={lambda2:.6f} >= theta_floor={THETA_FLOOR}"
