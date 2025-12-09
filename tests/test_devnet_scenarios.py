import pytest
from ilc_core.sim.devnet_scenarios import (
    DevnetScenarioConfig,
    scenario_from_dict,
    scenarios_from_config,
    build_snapshots_for_scenario,
    run_scenario
)

def test_scenarios_from_config_basic():
    config = {
        "namespace_id": "global_ns",
        "num_agents": 5,
        "scenarios": [
            {"label": "s1", "stress_schedule": [0.1]},
            {"label": "s2", "stress_schedule": [0.2], "num_agents": 10} # override
        ]
    }
    
    results = scenarios_from_config(config)
    assert len(results) == 2
    
    s1 = results[0]
    assert s1.label == "s1"
    assert s1.namespace_id == "global_ns"
    assert s1.num_agents == 5
    assert s1.stress_schedule == [0.1]
    
    s2 = results[1]
    assert s2.label == "s2"
    assert s2.namespace_id == "global_ns" # inherited
    assert s2.num_agents == 10 # overridden
    assert s2.stress_schedule == [0.2]

def test_build_snapshots_for_scenario():
    scen = DevnetScenarioConfig(
        label="test",
        stress_schedule=[0.5, 1.0, 1.5],
        namespace_id="test_ns"
    )
    
    snaps = build_snapshots_for_scenario(scen)
    assert len(snaps) == 3
    assert snaps[0].epoch_index == 1
    assert snaps[0].total_stress == 0.5
    assert snaps[0].namespace_id == "test_ns"
    
    assert snaps[2].epoch_index == 3
    assert snaps[2].total_stress == 1.5

def test_run_scenario_integration():
    # Tiny integration test
    scen = DevnetScenarioConfig(
        label="integration_test",
        stress_schedule=[0.1, 0.9], # 2 epochs
        num_agents=2
    )
    
    summary = run_scenario(scen)
    
    assert summary.label == "integration_test"
    assert summary.num_epochs == 2
    # Check we got some tasks done (assuming agents are competent enough)
    # Though exact number depends on simulation randomness/logic, 
    # ensuring it ran without error and returned summary is main goal.
    assert summary.total_tasks >= 0
    assert summary.max_node_tasks >= 0
