import csv
from pathlib import Path
import pytest

import simulations.sim_closed_loop_backlog_control as sim
from ilc_core.sim.harness_closed_loop_controllers import ClosedLoopEpochMetrics
from ilc_core.protocol.params import ProtocolParams


def test_controller_directionality_and_no_mutation():
    # Use no smoothing (alpha=1.0) and no deadband (0.0) to test raw PI directionality
    controller = sim.make_backlog_controller(target_backlog_ratio=0.30, smoothing_alpha=1.0, deadband=0.0)

    start = ProtocolParams(qa_enabled=True, qa_min_score=0.90)

    # High backlog => should LOOSEN => qa_min_score should go DOWN
    m_hi = ClosedLoopEpochMetrics(
        epoch_index=0,
        total_tasks=50,
        backlog_proxy=50,
        total_reward=0.0,
        avg_reward_per_task=0.0,
        total_suggestions=100,
    )
    out_hi = controller(0, m_hi, start)
    assert out_hi.qa_min_score < start.qa_min_score
    assert start.qa_min_score == 0.90  # unchanged (No mutation)

    # Low backlog => should TIGHTEN => qa_min_score should go UP (relative to previous applied)
    # Note: PI controller state is internal to the closure. 
    # State has integral accumulated from previous step.
    # Previous step error: 0.5 - 0.3 = +0.2. Integral = 0.2.
    # This step: backlog 0 -> ratio 0. Error = 0 - 0.3 = -0.3.
    # Integral becomes 0.2 - 0.3 = -0.1.
    # Adjustment = Kp(-0.3) + Ki(-0.1) = -0.18 - 0.02 = -0.20. (Negative adj means INCREASE QA)
    # QA_next = last_qa - (-0.20) = last_qa + 0.20.
    
    m_lo = ClosedLoopEpochMetrics(
        epoch_index=1,
        total_tasks=100,
        backlog_proxy=0,
        total_reward=0.0,
        avg_reward_per_task=0.0,
        total_suggestions=100,
    )
    out_lo = controller(1, m_lo, start)
    
    # Verify it went UP relative to the PREVIOUS output (which reduced it)
    assert out_lo.qa_min_score > out_hi.qa_min_score
    assert start.qa_min_score == 0.90  # still unchanged


def test_sim_creates_phase_65b_history_csv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Use a small epoch count for speed
    sim.run_sim(num_epochs=3, out_label="phase_65b", rng_seed=1)

    out_path = Path("out") / "phase_65b" / "backlog_control_history.csv"
    assert out_path.exists()

    with out_path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 3
    # Phase 65C: New CSV columns are qa_used, qa_next, delta_qa
    assert "qa_used" in rows[0]
    assert "qa_next" in rows[0]
    assert "delta_qa" in rows[0]
    assert "backlog_ratio" in rows[0]
