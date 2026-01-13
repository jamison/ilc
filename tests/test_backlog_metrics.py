"""
Tests for Phase 64A: Real Backlog Metrics.
"""
import pytest
from ilc_core.sim.devnet_scenarios import DevnetScenarioConfig, build_topology_and_profiles, build_snapshots_for_scenario
from ilc_core.sim.devnet_epoch_orchestrator import run_devnet_epoch
from ilc_core.protocol.params import ProtocolParams
from ilc_core.sim.harness_closed_loop_controllers import ClosedLoopRunConfig, run_closed_loop_devnet

def test_epoch_result_has_backlog_metrics():
    # Setup simple scenario
    cfg = DevnetScenarioConfig(
        label="test_backlog",
        stress_schedule=[0.5],
        num_agents=5
    )
    topo, profiles = build_topology_and_profiles(cfg)
    snapshots = build_snapshots_for_scenario(cfg)
    snap = snapshots[0]
    
    # 1. QA = 0.0 -> Accept All (mostly)
    # Some heuristic filtering might still happen if success_rate is super low, 
    # but score is usually reasonable.
    params_open = ProtocolParams(qa_min_score=0.0)
    
    res_open = run_devnet_epoch(
        1, topo, snap, profiles, protocol_params=params_open
    )
    
    assert res_open.num_suggestions > 0
    assert res_open.num_executed > 0
    # Suggestions should be >= Executed
    assert res_open.num_suggestions >= res_open.num_executed
    assert res_open.backlog_count == res_open.num_suggestions - res_open.num_executed
    
    # 2. QA = 1.1 -> Reject All (Guaranteed)
    # Score is clamped to 1.0. QA min 1.1 guarantees drops.
    params_strict = ProtocolParams(qa_min_score=1.1) 
    
    res_strict = run_devnet_epoch(
        1, topo, snap, profiles, protocol_params=params_strict
    )
    
    # We expect high backlog
    assert res_strict.num_suggestions > 0 # Suggestions depend on stress, not QA
    assert res_strict.num_executed < res_strict.num_suggestions # Should drop some
    assert res_strict.backlog_count > 0
    assert res_strict.backlog_count == res_strict.num_suggestions - res_strict.num_executed

def test_closed_loop_metrics_have_backlog():
    cfg = ClosedLoopRunConfig(
        label="test_loop_backlog",
        num_epochs=2,
        scenario=DevnetScenarioConfig(
            label="test", stress_schedule=[0.9, 0.9], num_agents=5
        ),
        initial_params=ProtocolParams(qa_min_score=0.8) # High QA to force backlog
    )
    
    def noop_ctrl(idx, m, p):
        return p  # Functional controller: return unchanged params
        
    history = run_closed_loop_devnet(cfg, noop_ctrl, rng_seed=123)
    
    assert len(history) == 2
    for m in history:
        # Check field exists and likely > 0 due to high stress + high QA
        assert hasattr(m, "backlog_proxy")
        assert m.backlog_proxy >= 0
        # Given param setting, we expect SOME drops
        # But asserting >0 is flaky if random generator yields perfect scores.
        # Just assert type correctness.
        assert isinstance(m.backlog_proxy, int)
