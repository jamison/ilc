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


# ---------------------------------------------------------------------------
# Detection table — all four quadrants
# ---------------------------------------------------------------------------

# Path A-B-C has lambda2 = 0.5 (analytical: path P3 with equal unit stakes).
# Triangle A-B-C has lambda2 = 0.75 (complete graph K3 with equal unit stakes).
# These two graphs provide the rising/falling control points for the four cells.


def test_update_spectral_trajectory_accelerating_growth_cell() -> None:
    # Δλ > 0, ΔΔλ > 0 → "Accelerating growth / Topology strengthening"
    # history: lambda2 grew by 0.1 last epoch; new lambda2 = 0.5 → delta 0.2 → accel +0.1
    history = [
        SpectralEpochRecord(
            epoch=1,
            lambda2=0.2,
            lambda2_delta=0.0,
            lambda2_accel=0.0,
            spectral_gap=0.5,
            fiedler_vector_epoch=1,
        ),
        SpectralEpochRecord(
            epoch=2,
            lambda2=0.3,
            lambda2_delta=0.1,
            lambda2_accel=0.1,
            spectral_gap=0.5,
            fiedler_vector_epoch=2,
        ),
    ]

    record = update_spectral_trajectory(
        history=history,
        L_new=_laplacian(["A", "B", "C"], [["A", "B"], ["B", "C"]]),
        epoch=3,
    )

    assert record.lambda2 == pytest.approx(0.5)
    assert record.lambda2_delta == pytest.approx(0.2)   # 0.5 - 0.3
    assert record.lambda2_accel == pytest.approx(0.1)   # 0.2 - 0.1
    assert record.lambda2_delta > 0.0
    assert record.lambda2_accel > 0.0


def test_update_spectral_trajectory_partition_healing_cell() -> None:
    # Δλ < 0, ΔΔλ > 0 → "Decelerating decline / Partition healing"
    # history: lambda2 fell steeply last epoch; new value declines less steeply
    history = [
        SpectralEpochRecord(
            epoch=1,
            lambda2=0.8,
            lambda2_delta=0.0,
            lambda2_accel=0.0,
            spectral_gap=0.5,
            fiedler_vector_epoch=1,
        ),
        SpectralEpochRecord(
            epoch=2,
            lambda2=0.6,
            lambda2_delta=-0.2,
            lambda2_accel=0.0,
            spectral_gap=0.5,
            fiedler_vector_epoch=2,
        ),
    ]

    record = update_spectral_trajectory(
        history=history,
        L_new=_laplacian(["A", "B", "C"], [["A", "B"], ["B", "C"]]),
        epoch=3,
    )

    assert record.lambda2 == pytest.approx(0.5)
    assert record.lambda2_delta == pytest.approx(-0.1)   # 0.5 - 0.6
    assert record.lambda2_accel == pytest.approx(0.1)    # -0.1 - (-0.2)
    assert record.lambda2_delta < 0.0
    assert record.lambda2_accel > 0.0


def test_update_spectral_trajectory_partition_risk_escalating_cell() -> None:
    # Δλ < 0, ΔΔλ < 0 → "Accelerating decline / Partition risk escalating"
    # This is the highest-priority alarm pattern in the detection table.
    # history: lambda2 was declining slowly; new value drops sharply
    history = [
        SpectralEpochRecord(
            epoch=1,
            lambda2=0.8,
            lambda2_delta=0.0,
            lambda2_accel=0.0,
            spectral_gap=0.5,
            fiedler_vector_epoch=1,
        ),
        SpectralEpochRecord(
            epoch=2,
            lambda2=0.75,
            lambda2_delta=-0.05,
            lambda2_accel=0.0,
            spectral_gap=0.5,
            fiedler_vector_epoch=2,
        ),
    ]

    record = update_spectral_trajectory(
        history=history,
        L_new=_laplacian(["A", "B", "C"], [["A", "B"], ["B", "C"]]),
        epoch=3,
    )

    assert record.lambda2 == pytest.approx(0.5)
    assert record.lambda2_delta == pytest.approx(-0.25)   # 0.5 - 0.75
    assert record.lambda2_accel == pytest.approx(-0.20)   # -0.25 - (-0.05)
    assert record.lambda2_delta < 0.0
    assert record.lambda2_accel < 0.0


# ---------------------------------------------------------------------------
# Sequential pipeline test
# ---------------------------------------------------------------------------


def test_update_spectral_trajectory_sequential_call_chain_is_consistent() -> None:
    # Run three calls where each output feeds the next, verify that delta and
    # accel fields are consistent end-to-end (no off-by-one in history indexing).
    #
    # L1: single binary edge A-B → lambda2 = 1.0
    # L2: path A-B-C → lambda2 = 0.5
    # L3: triangle A-B-C → lambda2 = 0.75
    L1 = _laplacian(["A", "B"], [["A", "B"]])
    L2 = _laplacian(["A", "B", "C"], [["A", "B"], ["B", "C"]])
    L3 = _laplacian(["A", "B", "C"], [["A", "B"], ["B", "C"], ["A", "C"]])

    r1 = update_spectral_trajectory([], L1, 1)
    r2 = update_spectral_trajectory([r1], L2, 2)
    r3 = update_spectral_trajectory([r1, r2], L3, 3)

    # r1: no history
    assert r1.lambda2_delta == 0.0
    assert r1.lambda2_accel == 0.0

    # r2: one prior — delta correct, accel still 0.0
    assert r2.lambda2_delta == pytest.approx(r2.lambda2 - r1.lambda2)
    assert r2.lambda2_accel == 0.0

    # r3: two priors — delta and accel both derived from live records
    assert r3.lambda2_delta == pytest.approx(r3.lambda2 - r2.lambda2)
    assert r3.lambda2_accel == pytest.approx(r3.lambda2_delta - r2.lambda2_delta)


# ---------------------------------------------------------------------------
# Epoch monotonicity guard
# ---------------------------------------------------------------------------


def test_update_spectral_trajectory_raises_on_same_epoch_as_last_history() -> None:
    L = _laplacian(["A", "B", "C"], [["A", "B"], ["B", "C"]])
    r1 = update_spectral_trajectory([], L, 5)

    with pytest.raises(ValueError, match="not strictly greater"):
        update_spectral_trajectory([r1], L, 5)


def test_update_spectral_trajectory_raises_on_epoch_before_last_history() -> None:
    L = _laplacian(["A", "B", "C"], [["A", "B"], ["B", "C"]])
    r1 = update_spectral_trajectory([], L, 5)

    with pytest.raises(ValueError, match="not strictly greater"):
        update_spectral_trajectory([r1], L, 4)
