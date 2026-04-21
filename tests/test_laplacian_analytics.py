"""Tests for ilc_core/analysis/laplacian_analytics.py (H-006a).

Calibration constants under test are locked to SIM-SPECTRAL-01 results:
  docs/research/ilc_sim_spectral_01_results_v0.1.md
"""
from __future__ import annotations

import numpy as np
import pytest

from ilc_core.analysis.laplacian_analytics import (
    N_BATCH,
    N_BOOTSTRAP,
    EPSILON_TRIGGER,
    THETA_FLOOR,
    RAYLEIGH_SPECTRAL_GAP_MIN,
    MIN_HYPEREDGE_MEMBERSHIPS,
    RayleighGateError,
    LaplacianError,
    build_hypergraph_laplacian,
    bootstrap_fiedler_concentration,
    compute_fiedler,
    delta_laplacian_frobenius,
    established_subgraph_nodes,
    fiedler_centrality,
    partition_risk_alert,
    rayleigh_approx_lambda2,
    spectral_gap,
)


# ---------------------------------------------------------------------------
# Calibration constants
# ---------------------------------------------------------------------------


def test_calibration_constants_locked_to_h005():
    """Constants must match the SIM-SPECTRAL-01 carry-forward table exactly."""
    assert N_BATCH == 1
    assert N_BOOTSTRAP == 44
    assert abs(EPSILON_TRIGGER - 0.3391) < 1e-9
    assert abs(THETA_FLOOR - 0.001) < 1e-9
    assert abs(RAYLEIGH_SPECTRAL_GAP_MIN - 0.05) < 1e-9
    assert MIN_HYPEREDGE_MEMBERSHIPS == 2


# ---------------------------------------------------------------------------
# Known analytical case: 3-node path graph P₃
# ---------------------------------------------------------------------------
#
# P₃: nodes A-B-C with edges (A,B) and (B,C), all equal stakes=1.0
# Represented as two binary hyperedges.
# For a path graph P₃ the normalized Laplacian eigenvalues are:
#   λ₁=0, λ₂=1, λ₃=2  (but our hypergraph Laplacian differs slightly
#   for non-uniform degree — test verifies λ₁≈0 and λ₂>0)


def _build_path_graph():
    nodes = ["A", "B", "C"]
    hyperedges = [["A", "B"], ["B", "C"]]
    stakes = {"A": 1.0, "B": 1.0, "C": 1.0}
    return nodes, hyperedges, stakes


def test_build_hypergraph_laplacian_path_graph_shape_and_symmetry():
    nodes, hyperedges, stakes = _build_path_graph()
    L, ordered = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    assert L.shape == (3, 3)
    assert ordered == ["A", "B", "C"]
    # Symmetric
    assert np.allclose(L, L.T, atol=1e-12)


def test_build_hypergraph_laplacian_path_graph_smallest_eigenvalue_is_zero():
    nodes, hyperedges, stakes = _build_path_graph()
    L, _ = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    eigenvalues = np.linalg.eigvalsh(L)
    # Connected graph → λ₁ = 0
    assert abs(eigenvalues[0]) < 1e-10


def test_compute_fiedler_path_graph_lambda2_positive():
    nodes, hyperedges, stakes = _build_path_graph()
    L, _ = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    lambda2, v2 = compute_fiedler(L)
    assert lambda2 > 1e-10
    assert v2.shape == (3,)
    # v2 should be unit-norm (eigh returns orthonormal eigenvectors)
    assert abs(np.linalg.norm(v2) - 1.0) < 1e-10


def test_spectral_gap_path_graph_positive():
    nodes, hyperedges, stakes = _build_path_graph()
    L, _ = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    gap = spectral_gap(L)
    assert gap > 0.0


# ---------------------------------------------------------------------------
# Sybil topology: low-stake Sybil nodes cannot inflate λ₂
# ---------------------------------------------------------------------------


def test_sybil_nodes_cannot_inflate_lambda2():
    """Low-stake Sybil bridge edge cannot restore connectivity to a near-disconnected graph.

    The harmonic mean weight W(e) is bounded above by the minimum member stake.
    A Sybil coalition at stake=0.01 that tries to bridge two disconnected clusters
    produces a bridge edge weight ≈ 0.01 — far too weak to raise λ₂ meaningfully.
    An honest bridge (stake=1.0) produces W(e)=1.0 and significantly higher λ₂.

    This tests SIM-SPECTRAL-01 §7 spoofability verdict: HARD_TO_FAKE.
    """
    # Two disconnected clusters: {A, B} and {C, D}, each internally connected
    cluster1 = ["A", "B"]
    cluster2 = ["C", "D"]
    all_nodes = cluster1 + cluster2 + ["S1"]

    # Honest bridge: B and C linked via an honest node at stake=1.0
    edges_honest = [["A", "B"], ["C", "D"], ["B", "C"]]
    stakes_honest = {n: 1.0 for n in all_nodes}
    # (S1 is present but isolated — not in any edge)
    L_honest, _ = build_hypergraph_laplacian(all_nodes, edges_honest, stakes_honest)
    lambda2_honest, _ = compute_fiedler(L_honest)

    # Sybil bridge: B and C linked only through a Sybil node at stake=0.01
    # W(e) for ["B", "S1", "C"] = harmonic_mean([1.0, 0.01, 1.0]) ≈ 0.029
    edges_sybil = [["A", "B"], ["C", "D"], ["B", "S1", "C"]]
    stakes_sybil = {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "S1": 0.01}
    L_sybil, _ = build_hypergraph_laplacian(all_nodes, edges_sybil, stakes_sybil)
    lambda2_sybil, _ = compute_fiedler(L_sybil)

    # Sybil bridge produces much lower λ₂ than honest bridge
    assert lambda2_sybil < lambda2_honest


# ---------------------------------------------------------------------------
# Rayleigh gate
# ---------------------------------------------------------------------------


def test_rayleigh_approx_raises_when_gap_below_threshold():
    nodes, hyperedges, stakes = _build_path_graph()
    L, _ = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    _, v2 = compute_fiedler(L)

    # Gap of 0.04 is below RAYLEIGH_SPECTRAL_GAP_MIN=0.05 → must raise
    with pytest.raises(RayleighGateError):
        rayleigh_approx_lambda2(L, v2, gap=0.04)


def test_rayleigh_approx_succeeds_when_gap_above_threshold():
    # P₃ path graph (A-B-C, two binary hyperedges) has spectral gap = 0.5,
    # well above RAYLEIGH_SPECTRAL_GAP_MIN=0.05. K4 as a single 4-way hyperedge
    # was the previous topology but produces a degenerate spectrum (gap=0) that
    # always caused pytest.skip — the Rayleigh success branch was never exercised.
    nodes, hyperedges, stakes = _build_path_graph()
    L, _ = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    gap = spectral_gap(L)

    # Verify the topology actually has a gap above threshold (regression guard).
    assert gap > RAYLEIGH_SPECTRAL_GAP_MIN, (
        f"P3 spectral gap {gap:.4f} must exceed RAYLEIGH_SPECTRAL_GAP_MIN={RAYLEIGH_SPECTRAL_GAP_MIN}"
    )

    lambda2_exact, v2 = compute_fiedler(L)
    # Rayleigh quotient at the exact eigenvector must return λ₂ to floating-point precision.
    est = rayleigh_approx_lambda2(L, v2, gap=gap)
    assert abs(est - lambda2_exact) < 1e-6


# ---------------------------------------------------------------------------
# Delta Laplacian Frobenius
# ---------------------------------------------------------------------------


def test_delta_laplacian_frobenius_zero_for_identical():
    nodes, hyperedges, stakes = _build_path_graph()
    L, _ = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    assert delta_laplacian_frobenius(L, L) == 0.0


def test_delta_laplacian_frobenius_positive_for_different():
    nodes, hyperedges, stakes = _build_path_graph()
    L_old, _ = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    # Add another hyperedge
    hyperedges2 = [["A", "B"], ["B", "C"], ["A", "C"]]
    L_new, _ = build_hypergraph_laplacian(nodes, hyperedges2, stakes)
    delta = delta_laplacian_frobenius(L_new, L_old)
    assert delta > 0.0


def test_delta_laplacian_frobenius_epsilon_trigger_value():
    """Confirm EPSILON_TRIGGER constant matches H-005 calibration."""
    assert abs(EPSILON_TRIGGER - 0.3391) < 1e-9


# ---------------------------------------------------------------------------
# Fiedler centrality
# ---------------------------------------------------------------------------


def test_fiedler_centrality_returns_values_in_unit_interval():
    nodes, hyperedges, stakes = _build_path_graph()
    L, node_list = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    _, v2 = compute_fiedler(L)
    centrality = fiedler_centrality(v2, node_list)
    assert set(centrality.keys()) == set(nodes)
    for val in centrality.values():
        assert 0.0 <= val <= 1.0


def test_fiedler_centrality_max_is_one():
    nodes, hyperedges, stakes = _build_path_graph()
    L, node_list = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    _, v2 = compute_fiedler(L)
    centrality = fiedler_centrality(v2, node_list)
    assert abs(max(centrality.values()) - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# Bootstrap Fiedler concentration
# ---------------------------------------------------------------------------


def test_bootstrap_concentration_genesis_only_graph_is_one():
    """At genesis (4 nodes, all founding), C(t) should be 1.0."""
    nodes = ["G1", "G2", "G3", "G4"]
    hyperedges = [["G1", "G2", "G3", "G4"]]
    stakes = {n: 1.0 for n in nodes}
    L, node_list = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    _, v2 = compute_fiedler(L)
    ct = bootstrap_fiedler_concentration(v2, node_list, genesis_node_ids=nodes)
    # All nodes are genesis → C(t) = mean(|v₂[all]|) / mean(|v₂[all]|) = 1.0
    assert abs(ct - 1.0) < 1e-10


def test_bootstrap_concentration_decreases_as_non_genesis_nodes_join():
    """C(t) should be < 1.0 when non-genesis nodes are present."""
    genesis = ["G1", "G2", "G3", "G4"]
    non_genesis = [f"N{i}" for i in range(10)]
    nodes = genesis + non_genesis
    stakes = {n: 1.0 for n in nodes}
    # Genesis all-to-all + non-genesis join via binary edges
    hyperedges = [["G1", "G2", "G3", "G4"]] + [[f"N{i}", "G1"] for i in range(10)]
    L, node_list = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    _, v2 = compute_fiedler(L)
    ct = bootstrap_fiedler_concentration(v2, node_list, genesis_node_ids=genesis)
    # Not all nodes are genesis, so C(t) != 1.0
    assert ct != 1.0
    assert ct >= 0.0


# ---------------------------------------------------------------------------
# Established subgraph filter
# ---------------------------------------------------------------------------


def test_established_subgraph_excludes_single_connection_nodes():
    nodes = ["A", "B", "C", "NEW"]
    memberships = {"A": 3, "B": 2, "C": 5, "NEW": 1}
    result = established_subgraph_nodes(nodes, memberships)
    assert "A" in result
    assert "B" in result
    assert "C" in result
    assert "NEW" not in result


def test_established_subgraph_empty_when_all_below_threshold():
    nodes = ["X", "Y"]
    memberships = {"X": 1, "Y": 1}
    result = established_subgraph_nodes(nodes, memberships)
    assert result == []


# ---------------------------------------------------------------------------
# Partition risk alert
# ---------------------------------------------------------------------------


def test_partition_alert_bootstrap_mode_healthy():
    """Bootstrap mode (n < 44): healthy C(t) → no alert."""
    nodes = ["G1", "G2", "G3", "G4"]
    hyperedges = [["G1", "G2", "G3", "G4"]]
    stakes = {n: 1.0 for n in nodes}
    L, node_list = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    lambda2, v2 = compute_fiedler(L)
    alert, reason = partition_risk_alert(lambda2, len(nodes), nodes, v2, node_list)
    assert not alert
    assert "bootstrap_mode" in reason
    assert "healthy" in reason


def test_partition_alert_production_mode_fires_below_theta_floor():
    """Production mode: λ₂ < THETA_FLOOR → alert fires."""
    # Construct a near-disconnected graph (two weakly coupled components)
    # by giving the bridge hyperedge a very low-stake member
    nodes = ["A", "B", "C", "D"]
    # Two components linked only through a near-zero weight edge
    hyperedges = [["A", "B"], ["C", "D"], ["B", "C"]]
    stakes = {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0}
    L, node_list = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    lambda2, v2 = compute_fiedler(L)

    # Manually inject a near-zero lambda2 to test the alert logic directly
    # (without needing to construct a pathological real graph)
    alert, reason = partition_risk_alert(
        lambda2=0.0005,  # below THETA_FLOOR=0.001
        n_nodes=100,     # production mode (>= N_BOOTSTRAP=44)
        genesis_node_ids=[],
        v2=v2,
        node_list=node_list,
    )
    assert alert
    assert "production_mode" in reason


def test_partition_alert_production_mode_no_alert_above_theta_floor():
    """Production mode: λ₂ >= THETA_FLOOR → no alert."""
    nodes, hyperedges, stakes = _build_path_graph()
    L, node_list = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    _, v2 = compute_fiedler(L)
    alert, reason = partition_risk_alert(
        lambda2=0.01,   # above THETA_FLOOR=0.001
        n_nodes=100,
        genesis_node_ids=[],
        v2=v2,
        node_list=node_list,
    )
    assert not alert
    assert "production_mode" in reason


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_build_hypergraph_laplacian_raises_on_empty_nodes():
    with pytest.raises(LaplacianError):
        build_hypergraph_laplacian([], [], {})


def test_build_hypergraph_laplacian_raises_on_unknown_member():
    with pytest.raises(LaplacianError):
        build_hypergraph_laplacian(
            ["A", "B"], [["A", "UNKNOWN"]], {"A": 1.0, "B": 1.0}
        )


def test_compute_fiedler_raises_on_single_node():
    L = np.array([[0.0]])
    with pytest.raises(LaplacianError):
        compute_fiedler(L)
