"""
Integration test for simulations/sim_ecu_beta_theta_fairness.py
"""
import pytest
from pathlib import Path
from simulations.sim_ecu_beta_theta_fairness import run_ecu_beta_theta_fairness
import csv

def test_run_ecu_beta_theta_fairness_smoke(tmp_path):
    """
    Smoke test for the fairness experiment.
    Runs a tiny version of the simulation to ensure wiring works and CSV is produced.
    """
    export_root = tmp_path / "phase_63a_test"
    
    # Run small: 8 agents, 3 epochs
    run_ecu_beta_theta_fairness(
        export_root=export_root,
        num_agents=8,
        num_epochs=3,
        rng_seed=123
    )
    
    # Check outputs
    # 1. Raw NDJSON logs should exist
    raw_dir = export_root / "raw"
    assert raw_dir.exists()
    epoch_dirs = list(raw_dir.glob("epoch_*"))
    assert len(epoch_dirs) > 0 # At least one epoch dir
    
    # 2. Results CSV
    csv_path = export_root / "ecu_beta_theta_fairness.csv"
    assert csv_path.exists()
    
    # 3. Check CSV content
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) > 0
    # We expect beta_values (5) * theta_values (3) = 15 rows
    assert len(rows) == 15 
    
    row0 = rows[0]
    required_cols = ["beta", "theta", "num_agents", "total_payout", "reward_gini", "top10_share"]
    for k in required_cols:
        assert k in row0
        
    # Check for validity
    gini = float(row0["reward_gini"])
    assert 0.0 <= gini <= 1.0
    
    # Check that we didn't just get partial 0.0s (smoke test for schema fix propagation)
    # Total payout should be > 0 if agents did work
    # With 8 agents, 3 epochs, and canonical schema, expect > 0 unless catastrophic
    payout = float(row0["total_payout"])
    
    # Note: If payout is 0, it suggests schema mismatch or logic error.
    # Asserting > 0 is a good regression test for Phase 62B.
    assert payout > 0.0, "Total payout is 0.0 - check competency schema or task generation."
