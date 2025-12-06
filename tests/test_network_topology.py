import pytest
from ilc_core.network.topology import (
    NodeRole, 
    NodeConfig, 
    DevnetTopology,
    build_line_topology, 
    build_star_topology, 
    assign_agents_round_robin, 
    compute_node_load_metrics
)

def test_build_line_topology():
    node_ids = ["n1", "n2", "n3"]
    topology = build_line_topology(node_ids)
    
    assert len(topology.nodes) == 3
    assert topology.nodes["n1"].role == NodeRole.WORKER
    
    # Check connections
    assert "n2" in topology.adjacency["n1"]
    assert "n1" in topology.adjacency["n2"]
    assert "n3" in topology.adjacency["n2"]
    assert "n2" in topology.adjacency["n3"]
    
    # n1 only connects to n2
    assert len(topology.adjacency["n1"]) == 1
    # n2 connects to n1, n3
    assert len(topology.adjacency["n2"]) == 2

def test_build_star_topology():
    center = "c"
    leaves = ["l1", "l2"]
    topology = build_star_topology(center, leaves)
    
    assert topology.nodes["c"].role == NodeRole.ORCHESTRATOR
    assert topology.nodes["l1"].role == NodeRole.WORKER
    
    # Center connects to all leaves
    assert len(topology.adjacency["c"]) == 2
    assert "l1" in topology.adjacency["c"]
    assert "l2" in topology.adjacency["c"]
    
    # Leaves connect only to center
    assert len(topology.adjacency["l1"]) == 1
    assert "c" in topology.adjacency["l1"]

def test_assign_agents_round_robin():
    # Setup topology with 2 workers
    topology = build_line_topology(["w1", "w2"])
    
    agents = ["a1", "a2", "a3"]
    
    mapping = assign_agents_round_robin(agents, topology, role=NodeRole.WORKER)
    
    assert len(mapping) == 3
    # Round robin: w1, w2, w1
    # Since w1 < w2, w1 is first candidate 
    
    # Actually order depends on sort inside helper
    # Candidates sorted: w1, w2
    assert mapping["a1"] == "w1"
    assert mapping["a2"] == "w2"
    assert mapping["a3"] == "w1"
    
    # Check attached agents updated
    assert "a1" in topology.nodes["w1"].attached_agents
    assert "a3" in topology.nodes["w1"].attached_agents
    assert "a2" in topology.nodes["w2"].attached_agents

def test_compute_node_load_metrics():
    # Mapping: a1->n1 (2 tasks), a2->n2 (1 task)
    mapping = {"a1": "n1", "a2": "n2"}
    
    tasks = [
        {"agent_id": "a1", "reward": 10},
        {"agent_id": "a1", "reward": 5},
        {"agent_id": "a2", "reward": 100},
    ]
    
    metrics = compute_node_load_metrics(tasks, mapping)
    
    assert "n1" in metrics
    assert metrics["n1"]["num_tasks"] == 2
    assert metrics["n1"]["total_reward"] == 15.0
    assert metrics["n1"]["avg_reward"] == 7.5
    
    assert "n2" in metrics
    assert metrics["n2"]["num_tasks"] == 1
    assert metrics["n2"]["total_reward"] == 100.0
    assert metrics["n2"]["avg_reward"] == 100.0
