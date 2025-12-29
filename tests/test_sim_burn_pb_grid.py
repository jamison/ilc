"""
Tests for Phase 64E: Burn x PB Sensitivity Grid.
"""
import pytest
import csv
from pathlib import Path
from ilc_core.sim.devnet_experiments import DevnetExperimentSummary
from ilc_core.analysis.econ_accounting import compute_econ_accounting
from simulations.sim_burn_pb_grid import main as run_grid_sim

def test_econ_accounting_strict_validation():
    summ = DevnetExperimentSummary(
        label="test", namespace_id="ns", num_epochs=1,
        total_tasks=100, total_reward=1000.0,
        avg_tasks_per_epoch=0, avg_reward_per_task=0, max_node_tasks=0,
        mean_backlog_per_epoch=0, max_backlog=0, mean_backlog_ratio=0
    )
    
    # 1. Invalid Range
    with pytest.raises(ValueError, match="Invalid burn_rate"):
        compute_econ_accounting(summ, -0.1, 0.5)
    with pytest.raises(ValueError, match="Invalid burn_rate"):
        compute_econ_accounting(summ, 1.1, 0.0)
        
    # 2. Invalid Sum
    with pytest.raises(ValueError, match=r"burn_rate \+ pb_rate must be <= 1.0"):
        compute_econ_accounting(summ, 0.6, 0.5) # Sum 1.1

    # 3. Boundary Condition (Sum = 1.0) - Should Pass
    acc = compute_econ_accounting(summ, 0.5, 0.5)
    assert acc.net_issued == 0.0
    
    # 4. Valid
    acc = compute_econ_accounting(summ, 0.1, 0.1)
    assert acc.burned == 100.0
    assert acc.net_issued == 800.0
    assert acc.vault_delta == 100.0

def test_sim_burn_pb_grid_integration(tmp_path, monkeypatch):
    # Integration test for the script
    # We mock run_econ_scenarios_on_devnet to return a dummy summary to save time
    
    dummy_summary = DevnetExperimentSummary(
        label="baseline_run", namespace_id="ns", num_epochs=20,
        total_tasks=1000, total_reward=1000.0,
        avg_tasks_per_epoch=50, avg_reward_per_task=1, max_node_tasks=10,
        mean_backlog_per_epoch=5, max_backlog=10, mean_backlog_ratio=0.1
    )
    
    # Mock the harness
    def mock_run(*args, **kwargs):
        return [dummy_summary]
        
    monkeypatch.setattr("simulations.sim_burn_pb_grid.run_econ_scenarios_on_devnet", mock_run)
    
    # Redirect output to tmp_path
    monkeypatch.chdir(tmp_path)
    # Ensure export dirs exist in tmp
    (tmp_path / "out/phase_64e/raw").mkdir(parents=True)
    
    # Run
    run_grid_sim()
    
    # Verify CSV
    csv_path = tmp_path / "out/phase_64e/burn_pb_grid.csv"
    assert csv_path.exists()
    
    with open(csv_path, "r") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 16 # 4x4 grid
        
        # Check a row
        row0 = reader[0]
        assert float(row0["total_reward"]) == 1000.0
        assert row0["label"].startswith("burn")
        
        # Check invariants
        gross = float(row0["gross_rewards"])
        burn = float(row0["burned"])
        pb = float(row0["pb_allocated"])
        net = float(row0["net_issued"])
        
        assert abs(gross - (burn + pb + net)) < 1e-6
