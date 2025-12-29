"""
Tests for Phase 64B: Backlog Summary Metrics.
"""
import pytest
from ilc_core.sim.devnet_scenarios import DevnetScenarioConfig, build_topology_and_profiles, build_snapshots_for_scenario
from ilc_core.sim.devnet_multi_epoch import run_devnet_multi_epoch
from ilc_core.sim.devnet_experiments import summarize_multi_epoch_run
from ilc_core.protocol.params import ProtocolParams

def test_backlog_summary_correctness():
    # Setup scenario
    cfg = DevnetScenarioConfig(
        label="test_backlog_summary",
        stress_schedule=[0.8, 0.8], # 2 epochs
        num_agents=10
    )
    topo, profiles = build_topology_and_profiles(cfg)
    snapshots = build_snapshots_for_scenario(cfg)
    
    # 1. Run Strict (High Backlog)
    # Use QA=1.1 to force drops (if scores capped at 1.0)
    p_strict = ProtocolParams(qa_min_score=1.1)
    
    multi_strict = run_devnet_multi_epoch(
        topology=topo, snapshots=snapshots, profiles=profiles,
        rng_seed=42, protocol_params=p_strict
    )
    
    summ_strict = summarize_multi_epoch_run("strict", multi_strict)
    
    # Assertions
    # With QA=1.1, executes 0. Backlog should be all suggestions.
    # Suggestions should be > 0.
    assert summ_strict.mean_backlog_per_epoch > 0
    assert summ_strict.max_backlog >= summ_strict.mean_backlog_per_epoch
    # Ratio should be 1.0 (all dropped)
    # Note: ratio = backlog / max(1, suggestions)
    # If suggestions > 0, and executed=0, backlog=suggestions, so ratio=1.0.
    assert summ_strict.mean_backlog_ratio == pytest.approx(1.0)
    
    # 2. Run Lenient (Low Backlog)
    p_lenient = ProtocolParams(qa_min_score=0.0)
    multi_lenient = run_devnet_multi_epoch(
        topology=topo, snapshots=snapshots, profiles=profiles,
        rng_seed=42, protocol_params=p_lenient
    )
    summ_lenient = summarize_multi_epoch_run("lenient", multi_lenient)
    
    # Assertions
    # Should execute most/all tasks.
    # Backlog should be lower than strict.
    assert summ_lenient.mean_backlog_per_epoch < summ_strict.mean_backlog_per_epoch
    # Likely close to 0, but heuristic drops possible?
    # For MVP logic, usually 0 if QA=0.
    assert summ_lenient.mean_backlog_ratio <= 0.1
    
    # 3. Aggregation Logic Check
    # Check max
    epoch_backlogs = [er.backlog_count for er in multi_strict.epoch_results]
    assert summ_strict.max_backlog == max(epoch_backlogs)
    assert summ_strict.mean_backlog_per_epoch == pytest.approx(sum(epoch_backlogs)/len(epoch_backlogs))

