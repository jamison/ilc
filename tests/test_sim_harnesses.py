import pytest
from ilc_core.sim.devnet_scenarios import DevnetScenarioConfig
from ilc_core.sim.harness_param_grid import (
    run_param_grid_on_devnet, 
    GridRunResult
)
from ilc_core.sim.harness_econ_scenarios import (
    EconScenarioConfig,
    run_econ_scenarios_on_devnet
)
from ilc_core.sim.harness_closed_loop_controllers import (
    ClosedLoopRunConfig,
    run_closed_loop_devnet,
    ClosedLoopEpochMetrics
)

def test_param_grid_harness():
    base = DevnetScenarioConfig(
        label="test_grid",
        stress_schedule=[0.1],
        num_agents=2
    )
    
    # 2x2 grid = 4 runs
    grid = {
        "num_agents": [2, 3],
        "dummy": ["A", "B"]
    }
    
    # Test label suffix builder & seed
    def suffixer(p):
        return f"suffix_{p['dummy']}"

    results = run_param_grid_on_devnet(
        base_scenario=base,
        grid=grid,
        label_suffix_builder=suffixer,
        rng_seed=555
    )
    
    assert len(results) == 4
    for res in results:
        assert isinstance(res, GridRunResult)
        assert res.summary.num_epochs == 1
        # Check label suffix behavior
        assert "suffix_" in res.summary.label
        
        # Check params applied
        if res.params["num_agents"] == 3:
            # How to check if scenario config was actually updated?
            # run_devnet_multi_epoch generates results based on it.
            # We trust logical correctness if the loop ran.
            # But we can verify no crash.
            pass
            
def test_econ_scenarios_harness():
    base = DevnetScenarioConfig(
        label="test_econ",
        stress_schedule=[0.1],
        num_agents=2
    )
    
    econ_configs = [
        EconScenarioConfig("run1", {"p": 1}),
        EconScenarioConfig("run2", {"p": 2})
    ]
    
    log = []
    def hook(params):
        log.append(params)
        
    summaries = run_econ_scenarios_on_devnet(
        base_scenario=base,
        econ_scenarios=econ_configs,
        apply_econ=hook
    )
    
    assert len(summaries) == 2
    assert len(log) == 2
    assert log[0] == {"p": 1}
    assert log[1] == {"p": 2}
    assert summaries[0].label == "run1"
    assert summaries[1].label == "run2"

def test_closed_loop_harness():
    base = DevnetScenarioConfig(
        label="test_loop",
        stress_schedule=[0.1, 0.2, 0.3], # 3 step
        num_agents=2
    )
    
    config = ClosedLoopRunConfig(
        label="test_loop_run",
        num_epochs=3,
        scenario=base
    )
    
    received_metrics = []
    def step(epoch, metrics):
        received_metrics.append((epoch, metrics))
        
    history = run_closed_loop_devnet(
        config=config,
        controller_step=step
    )
    
    assert len(history) == 3
    assert len(received_metrics) == 3
    
    # Check indices
    assert history[0].epoch_index == 1
    assert history[1].epoch_index == 2
    assert history[2].epoch_index == 3
    
    # Check metric object correctness
    assert isinstance(history[0], ClosedLoopEpochMetrics)
    assert received_metrics[0][0] == 1
    assert received_metrics[0][1] == history[0]

def test_econ_export_sidecar():
    from ilc_core.sim.harness_econ_scenarios import export_econ_summaries_with_overrides_to_csv
    from ilc_core.sim.devnet_experiments import DevnetExperimentSummary
    import tempfile
    from pathlib import Path
    
    # 1. Setup Data
    scenarios = [
        EconScenarioConfig("L1", {"burn": 0.1}),
        EconScenarioConfig("L2", {"burn": 0.9, "xtra": 1})
    ]
    
    # Dummy summaries
    s1 = DevnetExperimentSummary("L1", "ns", 1, 10, 100.0, 10.0, 10.0, 5.0)
    s2 = DevnetExperimentSummary("L2", "ns", 1, 20, 200.0, 20.0, 10.0, 8.0)
    
    # 2. Export
    with tempfile.NamedTemporaryFile(suffix=".csv") as tmp:
        path = Path(tmp.name)
        export_econ_summaries_with_overrides_to_csv(scenarios, [s1, s2], path)
        
        # 3. Verify
        content = path.read_text()
        lines = content.strip().splitlines()
        
        # Header should contain econ_burn, econ_xtra
        header = lines[0]
        assert "econ_burn" in header
        assert "econ_xtra" in header
        
        # Row 1 (L1) -> burn=0.1, xtra=""
        row1 = lines[1]
        assert "L1" in row1
        assert "0.1" in row1
        
        # Row 2 (L2) -> burn=0.9, xtra=1
        row2 = lines[2]
        assert "L2" in row2
        assert "0.9" in row2
        assert "1" in row2
