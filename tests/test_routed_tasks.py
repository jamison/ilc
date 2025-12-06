import pytest
from dataclasses import replace
from ilc_core.analysis.routed_tasks import (
    RoutedTaskRow,
    materialize_routed_tasks_for_epoch,
    routed_tasks_to_task_rows_dicts,
)
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.task_routing_suggestions import TaskRoutingSuggestion
from ilc_core.network.topology import DevnetTopology, NodeConfig, NodeRole

@pytest.fixture
def mock_topology():
    return DevnetTopology(
        nodes={
            "n1": NodeConfig(node_id="n1", role=NodeRole.WORKER, capacity_hint=10),
            "n2": NodeConfig(node_id="n2", role=NodeRole.WORKER, capacity_hint=10),
        },
        adjacency={}
    )

@pytest.fixture
def mock_profiles():
    # Use simple dict for competency as per AgentProfile definition
    comp_a1 = {"global": {"avg_success_rate": 0.8}, "by_space": {"testing": {"success_rate": 0.9}}}
    comp_a2 = {"global": {"avg_success_rate": 0.2}, "by_space": {}}
    
    return {
        "a1": AgentProfile(
            agent_id="a1",
            node_id="n1",
            competency=comp_a1
        ),
        "a2": AgentProfile(
            agent_id="a2",
            node_id="n2",
            competency=comp_a2
        ),
        "a3": AgentProfile(
            agent_id="a3",
            node_id=None, # Unassigned
            competency={}
        ),
    }

@pytest.fixture
def mock_snapshot():
    return NamespaceHealthSnapshot(
        namespace_id="ns1",
        epoch_index=1,
        total_stress=0.5, # medium regime
        cohesion_score=0.5,
        contradiction_overflow=0.0,
        support_ratio=1.0,
        validation_depth_error=0.0,
        crosslink_deficit=0.0,
        controversy_ratio=0.0,
        mean_abs_influence=0.0,
    )

def test_materialize_basic(mock_topology, mock_profiles, mock_snapshot):
    suggestions = {
        "a1": [
            TaskRoutingSuggestion(
                agent_id="a1",
                # no namespace_id
                suggested_task_type="refutation", # renamed from task_type
                problem_space="testing",
                barrier_level="low",
                score=0.8,
                rationale="foo" # renamed from reason, implies positional? No dataclass is kwarg friendly.
            )
        ]
    }
    
    rows = materialize_routed_tasks_for_epoch(
        epoch_index=1,
        namespace_snapshot=mock_snapshot,
        profiles=mock_profiles,
        suggestions=suggestions,
        topology=mock_topology
    )
    
    assert len(rows) == 1
    row = rows[0]
    assert row.agent_id == "a1"
    assert row.node_id == "n1" # propagated from profile
    assert row.namespace_id == "ns1"
    assert row.regime == "medium" # 0.5 stress
    assert row.success is True    # score 0.8 >= 0.5
    assert row.reward > 1.0       # base=1.0, score=0.8 -> > 1.0

def test_materialize_regimes(mock_topology, mock_profiles, mock_snapshot):
    # Test Low Stress
    low_snap = replace(mock_snapshot, total_stress=0.1)
    # Wait, empty suggestions -> empty rows. Need a suggestion.
    sugg = TaskRoutingSuggestion(
        agent_id="a1", 
        suggested_task_type="t", 
        problem_space="p", 
        barrier_level="l", 
        score=0.5, 
        rationale="r"
    )
    
    rows_low = materialize_routed_tasks_for_epoch(
        1, low_snap, mock_profiles, {"a1": [sugg]}, mock_topology
    )
    assert rows_low[0].regime == "low"
    
    # Test High Stress
    high_snap = replace(mock_snapshot, total_stress=1.5)
    rows_high = materialize_routed_tasks_for_epoch(
        1, high_snap, mock_profiles, {"a1": [sugg]}, mock_topology
    )
    assert rows_high[0].regime == "high"

def test_materialize_unassigned_node(mock_topology, mock_profiles, mock_snapshot):
    sugg = TaskRoutingSuggestion(
        agent_id="a3", 
        suggested_task_type="t", 
        problem_space="p", 
        barrier_level="l", 
        score=0.5, 
        rationale="r"
    )
    rows = materialize_routed_tasks_for_epoch(
        1, mock_snapshot, mock_profiles, {"a3": [sugg]}, mock_topology
    )
    assert rows[0].node_id == "unassigned"

def test_reward_and_success_logic(mock_topology, mock_profiles, mock_snapshot):
    # Score 0.1 -> Fail, Reward near base (but positive)
    bad_sugg = TaskRoutingSuggestion(
        agent_id="a1", 
        suggested_task_type="t", 
        problem_space="p", 
        barrier_level="l", 
        score=0.1, 
        rationale="r"
    )
    # Score 1.0 -> Success, Reward boosted
    good_sugg = TaskRoutingSuggestion(
        agent_id="a1", 
        suggested_task_type="t", 
        problem_space="p", 
        barrier_level="l", 
        score=1.0, 
        rationale="r"
    )
    
    rows = materialize_routed_tasks_for_epoch(
        1, mock_snapshot, mock_profiles, {"a1": [bad_sugg, good_sugg]}, mock_topology,
        base_reward=10.0
    )
    
    assert len(rows) == 2
    r_bad = rows[0]
    r_good = rows[1]
    
    assert r_bad.success is False
    assert r_bad.reward > 0
    assert r_bad.reward == 10.0 * (1.0 + 0.1 * 0.1) # 10 * 1.01 = 10.1
    
    assert r_good.success is True
    assert r_good.reward == 10.0 * (1.0 + 0.1 * 1.0) # 10 * 1.1 = 11.0

def test_dict_conversion(mock_topology, mock_profiles, mock_snapshot):
    sugg = TaskRoutingSuggestion(
        agent_id="a1", 
        suggested_task_type="t", 
        problem_space="p", 
        barrier_level="l", 
        score=0.8, 
        rationale="r"
    )
    rows = materialize_routed_tasks_for_epoch(
        1, mock_snapshot, mock_profiles, {"a1": [sugg]}, mock_topology
    )
    
    dicts = routed_tasks_to_task_rows_dicts(rows)
    assert len(dicts) == 1
    d = dicts[0]
    
    assert d["agent_id"] == "a1"
    assert d["node_id"] == "n1"
    assert "reward" in d
    assert "success" in d
    assert d["problem_space"] == "p"
