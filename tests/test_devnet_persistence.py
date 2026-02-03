
import pytest
import tempfile
import json
from pathlib import Path
from ilc_core.sim.devnet_scenarios import DevnetScenarioConfig, run_scenario
from ilc_core.ledger import get_ledger_backend

def test_devnet_persistence_integration():
    """
    Verify that running a scenario with ledger_backend_kind="file"
    creates the expected directory structure and files, and that
    restart preserves state.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        ledger_dir = Path(tmp_dir) / "ledger"
        
        # 1. Config for Run 1
        scenario = DevnetScenarioConfig(
            label="persist_test",
            stress_schedule=[0.5], # 1 epoch
            ledger_backend_kind="file",
            ledger_storage_dir=str(ledger_dir),
            num_agents=2
        )
        
        # 2. Run Scenario
        summary = run_scenario(scenario)
        
        # 3. Assertions on Output Files
        assert ledger_dir.exists()
        assert (ledger_dir / "balances.json").exists()
        assert (ledger_dir / "epochs").exists()
        assert (ledger_dir / "snapshots").exists()
        
        # Check Epoch Record
        # We expect epoch 1 to be settled
        epoch_files = list((ledger_dir / "epochs").glob("*.json"))
        assert len(epoch_files) == 1
        with open(epoch_files[0]) as f:
            rec = json.load(f)
            assert rec["status"] == "settled"
            assert rec["epoch_index"] == 1
            
        # Check Snapshot
        snap_files = list((ledger_dir / "snapshots").glob("*.json"))
        assert len(snap_files) == 1
        with open(snap_files[0]) as f:
            snap = json.load(f)
            assert snap.get("schema_version") == 1
            assert len(snap["stakes"]) == 2
            
        # 4. Restart Verification
        # Create a new backend pointing to the same dir
        backend_new = get_ledger_backend("file", str(ledger_dir))
        
        # Check if it sees the old state
        # Agent IDs are a0, a1 usually
        # Balances might be 0 if no rewards, but the record should be there
        
        ns_id = scenario.namespace_id # "ns_scenario"
        epoch_id = f"{ns_id}:0001"
        
        rec_loaded = backend_new.get_epoch_record(epoch_id)
        assert rec_loaded is not None
        assert rec_loaded["epoch_index"] == 1
        assert rec_loaded["status"] == "settled"
        
        snap_loaded = backend_new.get_stake_snapshot(epoch_id)
        assert snap_loaded is not None
        assert snap_loaded.namespace_id == ns_id
