"""Tests for H-006b Part 3 spectral trajectory analytics."""

from __future__ import annotations

import pytest

from ilc_core.analysis.laplacian_analytics import build_hypergraph_laplacian
from ilc_core.analysis.spectral_trajectory import (
    SpectralEpochRecord,
    update_spectral_trajectory,
)


def _laplacian(nodes: list[str], hyperedges: list[list[str]]):
    stakes = {node_id: 1.0 for node_id in nodes}
    laplacian, _ = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    return laplacian


def test_update_spectral_trajectory_empty_history_sets_zero_delta_and_accel() -> None:
    record = update_spectral_trajectory(
        history=[],
        L_new=_laplacian(["A", "B", "C"], [["A", "B"], ["B", "C"]]),
        epoch=7,
    )

    assert record.epoch == 7
    assert record.lambda2 == pytest.approx(0.5)
    assert record.lambda2_delta == 0.0
    assert record.lambda2_accel == 0.0
    assert record.spectral_gap == pytest.approx(0.5)
    assert record.fiedler_vector_epoch == 7


def test_update_spectral_trajectory_one_prior_record_computes_delta_only() -> None:
    history = [
        SpectralEpochRecord(
            epoch=1,
            lambda2=0.5,
            lambda2_delta=0.0,
            lambda2_accel=0.0,
            spectral_gap=0.5,
            fiedler_vector_epoch=1,
        )
    ]

    record = update_spectral_trajectory(
        history=history,
        L_new=_laplacian(["A", "B", "C"], [["A", "B"], ["B", "C"], ["A", "C"]]),
        epoch=2,
    )

    assert record.lambda2 == pytest.approx(0.75)
    assert record.lambda2_delta == pytest.approx(0.25)
    assert record.lambda2_accel == 0.0


def test_update_spectral_trajectory_two_priors_hits_decelerating_growth_cell() -> None:
    history = [
        SpectralEpochRecord(
            epoch=1,
            lambda2=0.0,
            lambda2_delta=0.0,
            lambda2_accel=0.0,
            spectral_gap=1.0,
            fiedler_vector_epoch=1,
        ),
        SpectralEpochRecord(
            epoch=2,
            lambda2=0.5,
            lambda2_delta=0.5,
            lambda2_accel=0.5,
            spectral_gap=0.5,
            fiedler_vector_epoch=2,
        ),
    ]

    record = update_spectral_trajectory(
        history=history,
        L_new=_laplacian(["A", "B", "C"], [["A", "B"], ["B", "C"], ["A", "C"]]),
        epoch=3,
    )

    assert record.lambda2 == pytest.approx(0.75)
    assert record.lambda2_delta == pytest.approx(0.25)
    assert record.lambda2_accel == pytest.approx(-0.25)
    assert record.lambda2_delta > 0.0
    assert record.lambda2_accel < 0.0


def test_update_spectral_trajectory_disconnected_graph_reports_zero_lambda2() -> None:
    record = update_spectral_trajectory(
        history=[],
        L_new=_laplacian(["A", "B", "C", "D"], [["A", "B"], ["C", "D"]]),
        epoch=4,
    )

    assert record.lambda2 == pytest.approx(0.0, abs=1e-12)
    assert record.lambda2_delta == 0.0
    assert record.lambda2_accel == 0.0


def test_update_spectral_trajectory_fiedler_vector_epoch_matches_epoch_arg() -> None:
    record = update_spectral_trajectory(
        history=[],
        L_new=_laplacian(["A", "B", "C", "D"], [["A", "B"], ["B", "C"], ["C", "D"]]),
        epoch=11,
    )

    assert record.fiedler_vector_epoch == 11


def test_update_spectral_trajectory_spectral_gap_is_non_negative() -> None:
    record = update_spectral_trajectory(
        history=[],
        L_new=_laplacian(["A", "B", "C"], [["A", "B"], ["B", "C"], ["A", "C"]]),
        epoch=9,
    )

    assert record.spectral_gap >= 0.0
