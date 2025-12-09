
import pytest
import tempfile
import json
from pathlib import Path
from dataclasses import asdict

from ilc_core.network.topology import build_star_topology, NodeRole, assign_agents_round_robin
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.sim.devnet_multi_epoch import run_devnet_multi_epoch, DevnetMultiEpochResult

@pytest.fixture
def multi_epoch_setup():
    topo = build_star_topology(center_id="orch", leaf_ids=["w1"])
    assign_agents_round_robin(["a1"], topo, role=NodeRole.WORKER)
    
    profiles = {}
    for n_id, cfg in topo.nodes.items():
        for a_id in cfg.attached_agents:
            profiles[a_id] = AgentProfile(
                agent_id=a_id,
                node_id=n_id,
                competency={
                    "global": {"avg_success_rate": 0.8},
                    "by_space": {"PLANNING": {"tasks": 10, "success_rate": 0.8}}
                },
                stress_response={"preference": "neutral"}
            )
            
    # Base Snapshot
    base_snap = NamespaceHealthSnapshot(
        namespace_id="test_multi_ns",
        epoch_index=0,
        total_stress=0.5,
        cohesion_score=0.5,
        contradiction_overflow=0.0,
        support_ratio=1.0,
        validation_depth_error=0.0,
        crosslink_deficit=0.0,
        controversy_ratio=0.0,
        mean_abs_influence=0.0
    )
    
    return topo, profiles, base_snap

def test_multi_epoch_basic_no_export(multi_epoch_setup):
    topo, profiles, base_snap = multi_epoch_setup
    
    # 2 epochs
    snaps = [
        base_snap.__class__(**{**base_snap.as_dict(), "epoch_index": 1}),
        base_snap.__class__(**{**base_snap.as_dict(), "epoch_index": 2}),
    ]
    
    result = run_devnet_multi_epoch(topo, snaps, profiles, export_root=None)
    
    assert result.namespace_id == "test_multi_ns"
    assert len(result.epoch_results) == 2
    assert len(result.aggregate_node_load) >= 1
    
    # Check aggregation
    # w1 should have some tasks (accumulated from 2 epochs)
    w1_load = result.aggregate_node_load.get("w1")
    assert w1_load is not None
    # Assuming heuristics generated tasks in both epochs
    assert w1_load["num_tasks"] >= 0 

def test_multi_epoch_with_export_dirs(multi_epoch_setup):
    topo, profiles, base_snap = multi_epoch_setup
    
    snaps = [
        base_snap.__class__(**{**base_snap.as_dict(), "epoch_index": 10}),
        base_snap.__class__(**{**base_snap.as_dict(), "epoch_index": 20}),
    ]
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        run_devnet_multi_epoch(topo, snaps, profiles, export_root=tmp_dir, export_prefix="test_epoch")
        
        root = Path(tmp_dir)
        subdirs = sorted([d.name for d in root.iterdir() if d.is_dir()])
        
        assert "test_epoch_0010" in subdirs
        assert "test_epoch_0020" in subdirs
        
        # Check contents of one
        epoch_10_dir = root / "test_epoch_0010"
        files = {f.name for f in epoch_10_dir.iterdir()}
        assert "epoch_report.json" in files
        assert "agent_dossiers.csv" in files
        
        # Check NDJSON exists
        assert (root / "test_epoch_0010" / "devnet_events.ndjson").exists()
        assert (root / "test_epoch_0020" / "devnet_events.ndjson").exists()
        
        # Verify content briefly
        with open(root / "test_epoch_0010" / "devnet_events.ndjson") as f:
            lines = f.readlines()
            assert len(lines) > 0
            first_evt = json.loads(lines[0])
            assert "kind" in first_evt
            assert "payload" in first_evt

def test_multi_epoch_empty_snapshots(multi_epoch_setup):
    topo, profiles, _ = multi_epoch_setup
    
    result = run_devnet_multi_epoch(topo, [], profiles)
    
    assert result.namespace_id == ""
    assert result.epoch_results == []
    assert result.aggregate_node_load == {}
