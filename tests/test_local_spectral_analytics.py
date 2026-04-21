"""Tests for H-006b Part 2 local spectral analytics."""

from __future__ import annotations

import pytest

from ilc_core.analysis.laplacian_analytics import (
    LaplacianError,
    build_hypergraph_laplacian,
    compute_fiedler,
)
from ilc_core.analysis.local_spectral_analytics import compute_local_lambda2


def test_compute_local_lambda2_matches_per_cluster_path_graphs() -> None:
    nodes = ["A", "B", "C", "D", "E"]
    hyperedges = [["A", "B"], ["B", "C"], ["D", "E"], ["C", "D"]]
    stakes = {node_id: 1.0 for node_id in nodes}
    content_type_map = {
        "A": "alpha",
        "B": "alpha",
        "C": "alpha",
        "D": "beta",
        "E": "beta",
    }

    observed = compute_local_lambda2(nodes, hyperedges, stakes, content_type_map)

    alpha_laplacian, _ = build_hypergraph_laplacian(
        ["A", "B", "C"],
        [["A", "B"], ["B", "C"]],
        stakes,
    )
    beta_laplacian, _ = build_hypergraph_laplacian(
        ["D", "E"],
        [["D", "E"]],
        stakes,
    )
    expected_alpha, _ = compute_fiedler(alpha_laplacian)
    expected_beta, _ = compute_fiedler(beta_laplacian)

    assert observed == pytest.approx(
        {
            "alpha": expected_alpha,
            "beta": expected_beta,
        }
    )


def test_compute_local_lambda2_returns_zero_for_isolated_cluster() -> None:
    nodes = ["A", "B", "C"]
    hyperedges = [["A", "C"]]
    stakes = {node_id: 1.0 for node_id in nodes}
    content_type_map = {
        "A": "alpha",
        "B": "alpha",
        "C": "beta",
    }

    observed = compute_local_lambda2(nodes, hyperedges, stakes, content_type_map)

    assert observed == {"alpha": 0.0, "beta": 0.0}


def test_compute_local_lambda2_raises_on_unknown_hyperedge_member() -> None:
    nodes = ["A", "B"]
    hyperedges = [["A", "Z"]]
    stakes = {"A": 1.0, "B": 1.0}
    content_type_map = {"A": "alpha", "B": "alpha"}

    with pytest.raises(LaplacianError):
        compute_local_lambda2(nodes, hyperedges, stakes, content_type_map)
