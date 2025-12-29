# Simulation Harnesses Overview

The ILC Core simulation framework provides three primary harnesses for executing experiments on `Devnet` topologies. These harnesses abstract away the complexity of multi-epoch execution, seeding, and result aggregation.

## 1. Parameter Grid Harness (`harness_param_grid`)

**Purpose**: Execute parameter sweeps over a defined grid of values (Cartesian product).
**Use Case**: Finding optimal constants (e.g., `weight_supports`, `burn_rate`) or characterizing system stability across different scales (`num_agents`).

### Usage Example
```python
from ilc_core.sim.harness_param_grid import run_param_grid_on_devnet, export_param_grid_results_to_csv
from ilc_core.sim.devnet_scenarios import DevnetScenarioConfig

base = DevnetScenarioConfig("grid_exp", num_agents=10)
grid = {
    "num_agents": [10, 20, 50],
    "burn_rate": [0.0, 0.1, 0.5]
}

results = run_param_grid_on_devnet(
    base_scenario=base,
    grid=grid,
    rng_seed=42,                  # Deterministic Execution
    export_root="./logs/grid_v1"  # Enable NDJSON Logging
)

# Export Summary CSV
export_param_grid_results_to_csv(results, "./logs/grid_v1/summary.csv")
```

### Outputs
*   **Summary CSV**: Contains all grid parameters + aggregated metrics + distribution metrics (min/max/var of rewards).
    *   **New (Phase 64B)**: Includes `mean_backlog_per_epoch`, `max_backlog`, and `mean_backlog_ratio`.
*   **NDJSON Logs** (if `export_root` set):
    *   `./logs/grid_v1/grid_grid_exp_num_agents=10_burn_rate=0.0/epoch_0001/devnet_events.ndjson`
    *   ... (one folder per grid point)

### Phase 62A – MVP Baseline Grid Sweep
*   **Script**: `simulations/sim_mvp_baseline_grid.py`
*   **Description**: Runs a 3×3 grid over `num_agents ∈ {16,32,64}` × `stress_profile` (MILD/MEDIUM/HEAVY) on the locked MVP devnet config.
*   **Outputs**:
    *   **CSV**: `out/phase_62a/mvp_baseline_grid_results.csv`
    *   **NDJSON**: `out/phase_62a/mvp_baseline_*/epoch_*/devnet_events.ndjson`

---

## 2. Economic Scenarios Harness (`harness_econ_scenarios`)

**Purpose**: Compare specific, named economic configurations (A/B testing).
**Use Case**: testing "High Burn" vs "Low Burn" vs "Base" scenarios without a full combinatorial grid.

### Usage Example
```python
from ilc_core.sim.harness_econ_scenarios import (
    run_econ_scenarios_on_devnet, 
    EconScenarioConfig, 
    export_econ_summaries_with_overrides_to_csv
)

configs = [
    EconScenarioConfig("Baseline", {"burn_rate": 0.05}),
    EconScenarioConfig("HighBurn", {"burn_rate": 0.50})
]

summaries = run_econ_scenarios_on_devnet(
    base_scenario=base,
    econ_scenarios=configs,
    rng_seed=123,
    export_root="./logs/econ_v1"
)
```

### Outputs
*   **Summary CSV**: Includes backlog metrics (Phase 64B).
*   **NDJSON Logs**:
    *   `./logs/econ_v1/Baseline/epoch_0001/devnet_events.ndjson`
    *   `./logs/econ_v1/HighBurn/epoch_0001/devnet_events.ndjson`

---

## 3. Closed-Loop Controller Harness (`harness_closed_loop_controllers`)

**Purpose**: Simulate feedback loops where a controller adjusts parameters dynamically between epochs based on observed metrics (e.g., PID controller adjusting burn rate based on backlog).
**Status**: Supports `ClosedLoopEpochMetrics` integrated with real backlog signals (Phase 64A).
**Note**: Does **not** yet support direct NDJSON export or real protocol parameter mutation (pending Phase 63/64 wiring to global state).

### Key Components
*   `ClosedLoopRunConfig`: Defines the target scenario and duration.
*   `ClosedLoopEpochMetrics`: Feedback signal passed to the controller (backlog, error rates).
