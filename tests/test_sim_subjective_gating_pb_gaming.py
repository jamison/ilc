"""
Smoke test for Phase 63B simulation script.
"""
from pathlib import Path
from simulations.sim_subjective_gating_pb_gaming import run_subjective_gating_pb_gaming
import csv

def test_subjective_gating_sim_runs(tmp_path):
    """
    Run a minimal version of the simulation (fewer agents/epochs) to verify CSV generation.
    """
    export_root = tmp_path / "phase_63b_test"
    
    # Run tiny sim
    run_subjective_gating_pb_gaming(
        export_root=export_root,
        num_agents=10,
        num_epochs=4,
        rng_seed=123
    )
    
    # Verify artifacts
    assert export_root.exists()
    
    # NDJSON logs
    raw_dir = export_root / "raw_events"
    assert raw_dir.exists()
    assert len(list(raw_dir.glob("epoch_*"))) > 0
    
    # CSV
    csv_path = export_root / "subjective_gating_pb_gaming.csv"
    assert csv_path.exists()
    
    # Check CSV Content
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) > 0
    # 3 modes * 3 gest * 3 intensities = 27 rows
    assert len(rows) == 27 
    
    row0 = rows[0]
    required = ["gating_mode", "pb_intensity", "pb_over_honest_ratio", "gini"]
    for k in required:
        assert k in row0
        
    # Check soundness
    assert float(row0["pb_mean_reward"]) >= 0.0
