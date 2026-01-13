"""
Tests for Phase 63C: Closed-loop Protocol Knobs.
"""
from ilc_core.protocol.params import ProtocolParams
from ilc_core.analysis.routed_tasks import materialize_routed_tasks_for_epoch
from ilc_core.analysis.task_routing_suggestions import TaskRoutingSuggestion
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.sim.devnet_scenarios import build_topology_and_profiles, DevnetScenarioConfig
from ilc_core.sim.harness_closed_loop_controllers import ClosedLoopRunConfig, run_closed_loop_devnet
import pytest

def test_routed_tasks_obey_knobs():
    # Setup dummy data
    sugg_high = TaskRoutingSuggestion(
        agent_id="agent1",
        problem_space="A", suggested_task_type="T", 
        barrier_level="medium", score=0.9,
        rationale="test"
    )
    sugg_low = TaskRoutingSuggestion(
        agent_id="agent1",
        problem_space="A", suggested_task_type="T", 
        barrier_level="medium", score=0.1,
        rationale="test"
    )
    suggestions = {"agent1": [sugg_high, sugg_low]}
    
    profiles = {} # Dummy
    topology = None # Dummy if not used deeply
    
    snapshot = NamespaceHealthSnapshot(
        namespace_id="test", epoch_index=1,
        total_stress=0.5,
        # Required Dummy fields
        validation_depth_error=0.0,
        contradiction_overflow=0.0,
        crosslink_deficit=0.0,
        support_ratio=1.0,
        controversy_ratio=0.0,
        mean_abs_influence=0.0,
        cohesion_score=1.0
    )
    
    # 1. Test QA Filter
    # Set QA high implies low score task rejected
    params_qa = ProtocolParams(qa_min_score=0.5, base_reward=10.0)
    rows_qa = materialize_routed_tasks_for_epoch(
        1, snapshot, profiles, suggestions, topology, protocol_params=params_qa
    )
    assert len(rows_qa) == 1
    assert rows_qa[0].reward == 10.0 * (0.9 ** 1.0) # default kappa=1
    
    # 2. Test Kappa & Toll
    # Kappa=2 -> 0.9^2 = 0.81. Reward = 100 * 0.81 = 81.
    # Toll=1.0 -> 80.
    params_kt = ProtocolParams(
        qa_min_score=0.0, 
        competence_kappa=2.0, 
        base_reward=100.0,
        toll_per_task=1.0
    )
    rows_kt = materialize_routed_tasks_for_epoch(
        1, snapshot, profiles, suggestions, topology, protocol_params=params_kt
    )
    assert len(rows_kt) == 2
    
    # High score check
    # 100 * (0.9^2) - 1 = 81 - 1 = 80
    r_high = [r for r in rows_kt if r.reward > 10][0]
    assert abs(r_high.reward - 80.0) < 1e-6
    
    # Low score check
    # 100 * (0.1^2) - 1 = 1 - 1 = 0
    r_low = [r for r in rows_kt if r.reward < 10][0]
    assert abs(r_low.reward - 0.0) < 1e-6

def test_closed_loop_integration_runs():
    # Smoke test for the loop logic
    scenario = DevnetScenarioConfig(
        label="test_loop",
        stress_schedule=[0.5, 0.5],
        num_agents=5
    )
    
    params = ProtocolParams(base_reward=10.0)
    
    cfg = ClosedLoopRunConfig(
        label="test",
        num_epochs=2,
        scenario=scenario,
        initial_params=params
    )
    
    from dataclasses import replace
    def dummy_controller(idx, metrics, p):
        # Functional controller: return new params (no mutation)
        return replace(p, base_reward=p.base_reward + 1.0)
        
    history = run_closed_loop_devnet(cfg, dummy_controller, rng_seed=123)
    
    assert len(history) == 2
    # Verify logical progression? Indirectly, if it didn't crash, good.
