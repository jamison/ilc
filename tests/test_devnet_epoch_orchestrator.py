import pytest
import tempfile
import json
from pathlib import Path
from dataclasses import replace

from ilc_core.network.topology import build_star_topology, NodeRole, assign_agents_round_robin
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.task_routing_suggestions import TaskRoutingSuggestion
from ilc_core.sim.devnet_epoch_orchestrator import run_devnet_epoch, DevnetEpochResult

@pytest.fixture
def minimal_setup():
    # Topology
    topo = build_star_topology(center_id="orch", leaf_ids=["w1", "w2"])
    
    # Agents
    agent_ids = ["a1", "a2"]
    assign_agents_round_robin(agent_ids, topo, role=NodeRole.WORKER)
    
    profiles = {}
    for n_id, cfg in topo.nodes.items():
        for a_id in cfg.attached_agents:
            profiles[a_id] = AgentProfile(
                agent_id=a_id,
                node_id=n_id,
                competency={
                    "global": {"avg_success_rate": 0.8},
                    "by_space": {
                        "LOCAL_CONSISTENCY": {"tasks": 10, "success_rate": 0.9},
                        "PLANNING": {"tasks": 10, "success_rate": 0.5}
                    }
                },
                # Ensure they get suggestions
                stress_response={"preference": "neutral"}
            )
            
    # Snapshot (medium stress)
    snapshot = NamespaceHealthSnapshot(
        namespace_id="test_ns",
        epoch_index=10,
        total_stress=0.5,
        cohesion_score=0.5,
        contradiction_overflow=0.1,
        support_ratio=0.8,
        validation_depth_error=0.0,
        crosslink_deficit=0.0,
        controversy_ratio=0.0,
        mean_abs_influence=0.0
    )
    
    return topo, profiles, snapshot

def test_basic_run_no_export(minimal_setup):
    topo, profiles, snapshot = minimal_setup
    
    result = run_devnet_epoch(
        epoch_index=10,
        topology=topo,
        namespace_snapshot=snapshot,
        profiles=profiles,
        export_dir=None
    )
    
    assert isinstance(result, DevnetEpochResult)
    assert result.epoch_index == 10
    assert result.namespace_id == "test_ns"
    
    # We expect some suggestions -> materialized tasks
    # (unless default suggestion logic yields nothing, but heuristic suggests based on competency)
    assert len(result.routed_task_rows) > 0
    
    # Check node Load
    # w1 and w2 should have load if tasks were assigned
    # Note: If random/heuristic fails to assign, this might flake if logic is super sparse.
    # But competency is present, so suggest_tasks should return something.
    assert len(result.node_load_metrics) >= 1

def test_run_with_export(minimal_setup):
    topo, profiles, snapshot = minimal_setup
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = run_devnet_epoch(
            epoch_index=10,
            topology=topo,
            namespace_snapshot=snapshot,
            profiles=profiles,
            export_dir=tmp_dir
        )
        
        p = Path(tmp_dir)
        files = {f.name for f in p.iterdir()}
        
        assert "agent_dossiers.csv" in files
        assert "agent_dossiers.json" in files
        assert "epoch_report.csv" in files
        assert "epoch_report.json" in files
        
        # Quick content check
        with (p / "epoch_report.json").open() as f:
            data = json.load(f)
            assert data["epoch_index"] == 10
            assert data["namespace"]["namespace_id"] == "test_ns"

def test_missing_agent_handling():
    # Test case where an agent has no profile node_id or isn't in topology (edge case)
    # The orchestrator should handle it (fallback to "unassigned" in agent_to_node)
    
    snapshot = NamespaceHealthSnapshot(
        namespace_id="ns", epoch_index=1, total_stress=0.5, cohesion_score=0.5,
        contradiction_overflow=0.0, support_ratio=0.5, validation_depth_error=0.0,
        crosslink_deficit=0.0, controversy_ratio=0.0, mean_abs_influence=0.0
    )
    topo = build_star_topology(center_id="o", leaf_ids=["w1"])
    
    # Profile with no node_id
    profiles = {
        "ghost": AgentProfile(agent_id="ghost", node_id=None, competency={})
    }
    
    result = run_devnet_epoch(1, topo, snapshot, profiles)
    
    # Should run without error
    # Load metrics might be computed for "unassigned"? 
    # compute_node_load_metrics initializes from set(agent_to_node.values())
    
    assert "unassigned" in result.node_load_metrics
