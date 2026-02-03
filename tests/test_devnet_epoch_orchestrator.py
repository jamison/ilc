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
from ilc_core.protocol.event_log import (
    EventLogger,
    validate_epoch_config_payload,
    validate_task_outcome_payload,
    validate_epoch_summary_payload,
)

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
        
        # Routed Tasks & Node Load export checks
        assert (p / "routed_tasks.csv").exists()
        assert (p / "routed_tasks.json").exists()
        assert (p / "node_load.csv").exists()
        assert (p / "node_load.json").exists()

        # Quick content check
        with (p / "epoch_report.json").open() as f:
            data = json.load(f)
            assert data["epoch_index"] == 10
            assert data["namespace"]["namespace_id"] == "test_ns"

        # Basic content check for new files
        with (p / "routed_tasks.json").open() as f:
            tasks = json.load(f)
            # 2 agents, each with 2 competency spaces -> 4 tasks
            assert len(tasks) == 4

        with (p / "node_load.json").open() as f:
            loads = json.load(f)
            assert len(loads) > 0

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


def test_devnet_emission_validates_payloads(minimal_setup):
    """
    Integration test: Run devnet epoch with event_logger and validate
    all emitted payloads using lenient validators.
    
    This test will fail if event payloads drift from required fields.
    """
    topo, profiles, snapshot = minimal_setup
    
    # Create event logger
    logger = EventLogger(events=[])
    
    # Run devnet epoch with event logger
    result = run_devnet_epoch(
        epoch_index=10,
        topology=topo,
        namespace_snapshot=snapshot,
        profiles=profiles,
        event_logger=logger,
    )
    
    # Verify events were emitted
    assert len(logger.events) > 0
    
    # Categorize and validate events
    epoch_config_events = []
    task_outcome_events = []
    epoch_summary_events = []
    
    for evt in logger.events:
        if evt.kind == "epoch_config":
            epoch_config_events.append(evt)
            # Validate payload - should not raise
            validate_epoch_config_payload(evt.payload)
        elif evt.kind == "task_outcome":
            task_outcome_events.append(evt)
            validate_task_outcome_payload(evt.payload)
        elif evt.kind == "epoch_summary":
            epoch_summary_events.append(evt)
            validate_epoch_summary_payload(evt.payload)
    
    # Should have exactly 1 epoch_config and 1 epoch_summary
    assert len(epoch_config_events) == 1
    assert len(epoch_summary_events) == 1
    
    # Should have task_outcome events (one per routed task)
    assert len(task_outcome_events) == len(result.routed_task_rows)
    
    # Verify epoch_config required fields
    config = epoch_config_events[0].payload
    assert config["epoch_index"] == 10
    assert "benchmark_suite_id" in config
    assert "created_at" in config
    assert config["namespace_id"] == "test_ns"
    
    # Verify epoch_summary required fields
    summary = epoch_summary_events[0].payload
    assert summary["epoch_index"] == 10
    assert "total_tasks" in summary
    assert "total_reward" in summary

