"""
Tests for Phase 63D: Protocol Knobs Micro-Sweep.
"""
import pytest
import shutil
from pathlib import Path
from simulations.sim_protocol_knobs_micro_sweep import run_micro_sweep

@pytest.fixture
def temp_sweep_dir(tmp_path):
    d = tmp_path / "sweep_out"
    d.mkdir()
    return d

def test_micro_sweep_runs_and_obeys_physics(temp_sweep_dir):
    """
    Run a tiny version of the factorial sweep and check basic invariants.
    """
    # Use fewer agents/epochs for speed
    stress_schedule = [0.9, 0.9] # 2 epochs
    num_agents = 4
    
    csv_path = run_micro_sweep(
        output_dir=temp_sweep_dir,
        rng_seed=42, # Fixed seed
        num_agents=num_agents,
        stress_schedule=stress_schedule
    )
    
    assert csv_path.exists()
    
    import csv
    with open(csv_path, "r") as f:
        rows = list(csv.DictReader(f))
        
    assert len(rows) == 8 # 2x2x2
    
    # Check Baseline (qa=0, toll=0, comp=False)
    # This should be row 0 or close to it depending on itertools order
    # qa, toll, comp order -> 0,0,False is first
    
    base_row = next(r for r in rows if r["label"] == "qa0.0_toll0.0_comp0")
    
    total_tasks_base = float(base_row["total_tasks"])
    total_reward_base = float(base_row["total_reward"])
    
    # 1. Baseline Validity
    assert total_tasks_base > 0
    assert total_reward_base > 0
    
    # 2. QA Effect: Higher QA should filtered strictly <= baseline tasks
    # (holding toll/comp constant)
    high_qa_row = next(r for r in rows if r["label"] == "qa0.6_toll0.0_comp0")
    total_tasks_hi_qa = float(high_qa_row["total_tasks"])
    
    assert total_tasks_hi_qa <= total_tasks_base
    
    # 3. Toll Effect: Higher Toll should reduce Total Reward strictly <= baseline reward
    # (assuming filtering is same, i.e. comparing qa0/comp0)
    # Logic: Reward = (base * score^k) - toll. If toll > 0, reward is less per task.
    # Task count should be identical if only toll changed (toll doesn't filter, QA does).
    hi_toll_row = next(r for r in rows if r["label"] == "qa0.0_toll0.25_comp0")
    total_tasks_hi_toll = float(hi_toll_row["total_tasks"])
    total_reward_hi_toll = float(hi_toll_row["total_reward"])
    
    assert total_tasks_hi_toll == total_tasks_base # Toll shouldn't drop tasks
    assert total_reward_hi_toll < total_reward_base # Toll should drop reward sum
    
    # 4. Check Distribution Stats Present
    assert float(base_row["max_node_reward"]) >= float(base_row["min_node_reward"])
    assert float(base_row["reward_variance"]) >= 0.0
