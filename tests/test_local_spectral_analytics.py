"""Tests for H-006b Part 2 local spectral analytics."""

from __future__ import annotations

import pytest

from ilc_core.analysis.laplacian_analytics import (
    LaplacianError,
    build_hypergraph_laplacian,
    compute_fiedler,
)
from ilc_core.analysis.local_spectral_analytics import (
    compute_local_lambda2,
    fiedler_centrality_delta,
)


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


def test_compute_local_lambda2_raises_when_content_type_assignment_is_missing() -> None:
    nodes = ["A", "B"]
    hyperedges = [["A", "B"]]
    stakes = {"A": 1.0, "B": 1.0}
    content_type_map = {"A": "alpha"}

    with pytest.raises(LaplacianError):
        compute_local_lambda2(nodes, hyperedges, stakes, content_type_map)


def test_fiedler_centrality_delta_subtracts_same_node_set() -> None:
    observed = fiedler_centrality_delta(
        {"A": 0.7, "B": 0.2},
        {"A": 0.5, "B": 0.3},
    )

    assert observed == pytest.approx({"A": 0.2, "B": -0.1})


def test_fiedler_centrality_delta_treats_new_nodes_as_zero_in_previous_snapshot() -> None:
    observed = fiedler_centrality_delta(
        {"A": 0.4, "B": 0.1},
        {"A": 0.3},
    )

    assert observed == pytest.approx({"A": 0.1, "B": 0.1})


def test_fiedler_centrality_delta_treats_dropped_nodes_as_zero_in_current_snapshot() -> None:
    observed = fiedler_centrality_delta(
        {"A": 0.4},
        {"A": 0.3, "B": 0.2},
    )

    assert observed == pytest.approx({"A": 0.1, "B": -0.2})


def test_fiedler_centrality_delta_returns_empty_dict_for_empty_inputs() -> None:
    assert fiedler_centrality_delta({}, {}) == {}


def test_fiedler_centrality_delta_preserves_all_zero_deltas() -> None:
    observed = fiedler_centrality_delta(
        {"A": 0.0, "B": 0.0},
        {"A": 0.0, "B": 0.0},
    )

    assert observed == {"A": 0.0, "B": 0.0}
