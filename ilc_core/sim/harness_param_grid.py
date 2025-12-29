from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Callable, Union
from os import PathLike
from pathlib import Path
import csv
import itertools
import copy

from ilc_core.sim.devnet_scenarios import (
    DevnetScenarioConfig,
    build_topology_and_profiles,
    build_snapshots_for_scenario,
)
from ilc_core.sim.devnet_multi_epoch import run_devnet_multi_epoch
from ilc_core.sim.devnet_experiments import (
    summarize_multi_epoch_run, 
    DevnetExperimentSummary
)

@dataclass
class GridRunResult:
    params: Dict[str, Any]
    summary: DevnetExperimentSummary
    # Phase 61F: Distribution metrics for node rewards
    min_node_reward: float = 0.0
    max_node_reward: float = 0.0
    mean_node_reward: float = 0.0
    reward_variance: float = 0.0
    
def apply_params_to_scenario(
    scenario: DevnetScenarioConfig, 
    params: Dict[str, Any]
) -> DevnetScenarioConfig:
    """Helper: Apply matching keys to scenario, ignore others. Returns modified scenario."""
    for k, v in params.items():
        if hasattr(scenario, k):
            setattr(scenario, k, v)
    return scenario

def run_param_grid_on_devnet(
    base_scenario: DevnetScenarioConfig,
    grid: Dict[str, List[Any]],
    *,
    apply_params: Optional[Callable[[DevnetScenarioConfig, Dict[str, Any]], DevnetScenarioConfig]] = None,
    label_suffix_builder: Optional[Callable[[Dict[str, Any]], str]] = None,
    rng_seed: Optional[int] = None,
    export_root: Optional[PathLike] = None,
    export_prefix: str = "grid",
) -> List[GridRunResult]:
    """
    Run a parameter sweep over a cartesian product of grid values.

    Args:
        base_scenario: Template scenario configuration.
        grid: Mapping from parameter name to list of values.
              Keys that match DevnetScenarioConfig fields are applied by default.
              Keys that do not match are treated as "external knobs": they are
              ignored by the default applicator but still recorded in params/CSV.
        apply_params: Optional hook to customize how params are applied. If
              provided, this function is responsible for mutating/returning the
              scenario given the param dict.
        label_suffix_builder: Optional hook to build a compact suffix for
              scenario labels; useful when grids are large.
        rng_seed: Base random seed for deterministic runs. Each grid point uses
              rng_seed + run_index.
        export_root: Optional root directory to enable NDJSON exports.
                     If provided, creates subdirectories: 
                     `{export_root}/{export_prefix}_{scenario.label}/epoch_XXXX/devnet_events.ndjson`.
        export_prefix: Subdirectory prefix under export_root (default "grid").

    Returns:
        List of GridRunResult objects containing the param dict and
        DevnetExperimentSummary for each grid point.
    """
    results = []
    
    # Generate all combinations
    keys = sorted(grid.keys())
    values_lists = [grid[k] for k in keys]
    
    # Use enumerate to get a stable run_index for seeding
    for run_index, combination in enumerate(itertools.product(*values_lists)):
        # Construct params dict for this run
        params = dict(zip(keys, combination))
        
        # 1. Apply Params
        # (Deepcopy ensures we don't mutate the template or previous runs)
        scenario = copy.deepcopy(base_scenario)
        if apply_params:
            scenario = apply_params(scenario, params)
        else:
            apply_params_to_scenario(scenario, params)
        
        # 2. Update Label
        if label_suffix_builder:
            suffix = label_suffix_builder(params)
            scenario.label = f"{base_scenario.label}_{suffix}"
        else:
            # Default: append all params
            suffix_parts = [f"{k}={v}" for k, v in params.items()]
            scenario.label = f"{base_scenario.label}_{'_'.join(suffix_parts)}"
            
        # 3. Build Sim Components
        topo, profiles = build_topology_and_profiles(scenario)
        snapshots = build_snapshots_for_scenario(scenario)
        
        # Derive Seed
        run_seed = None
        if rng_seed is not None:
            # Simple stable derivation: master + index
            run_seed = rng_seed + run_index
            
        # Determine Per-Run Export Path
        run_export_dir = None
        if export_root:
            run_export_dir = Path(export_root) / f"{export_prefix}_{scenario.label}"
            
        # 4. Run Simulation
        multi_result = run_devnet_multi_epoch(
            topology=topo,
            snapshots=snapshots,
            profiles=profiles,
            export_root=run_export_dir,
            rng_seed=run_seed
        )
        
        # Phase 61F: Compute Distribution Metrics
        # Collect rewards from aggregate_node_load
        metrics = {
             "min_node_reward": 0.0,
             "max_node_reward": 0.0,
             "mean_node_reward": 0.0,
             "reward_variance": 0.0,
        }
        
        rewards = [node_data.get("total_reward", 0.0) 
                   for node_data in multi_result.aggregate_node_load.values()]
        
        if rewards:
            r_mean = sum(rewards) / len(rewards)
            # Population variance: sum((x - mean)^2) / N
            r_var = sum((r - r_mean) ** 2 for r in rewards) / len(rewards)
            
            metrics["min_node_reward"] = min(rewards)
            metrics["max_node_reward"] = max(rewards)
            metrics["mean_node_reward"] = r_mean
            metrics["reward_variance"] = r_var
            
        # 5. Summarize
        summary = summarize_multi_epoch_run(
            label=scenario.label,
            multi=multi_result
        )
        
        results.append(GridRunResult(
            params=params,
            summary=summary,
            min_node_reward=metrics["min_node_reward"],
            max_node_reward=metrics["max_node_reward"],
            mean_node_reward=metrics["mean_node_reward"],
            reward_variance=metrics["reward_variance"]
        ))
        
    return results

def export_param_grid_results_to_csv(
    results: List[GridRunResult],
    path: Union[str, PathLike],
) -> None:
    """
    Export grid run results to CSV.
    
    Columns: [Sorted Param Keys] + [Summary Fields]
    """
    if not results:
        return

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine header
    # 1. Param keys (assume consistent across results, take from first)
    param_keys = sorted(results[0].params.keys())
    
    # 2. Summary fields (hardcoded for stability, or could verify via verify)
    summary_fields = [
        "label", "num_epochs", "total_tasks", "total_reward", 
        "avg_tasks_per_epoch", "avg_reward_per_task", "max_node_tasks",
        # Phase 64B
        "mean_backlog_per_epoch", "max_backlog", "mean_backlog_ratio"
    ]
    
    # 3. Distribution fields
    dist_fields = [
        "min_node_reward", "max_node_reward", "mean_node_reward", "reward_variance"
    ]
    
    header = param_keys + summary_fields + dist_fields
    
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        
        for res in results:
            row = {}
            # Add params
            for k in param_keys:
                row[k] = res.params.get(k)
            
            # Add summary fields
            s_dict = asdict(res.summary)
            for k in summary_fields:
                row[k] = s_dict.get(k)
                
            # Add distribution fields
            row["min_node_reward"] = res.min_node_reward
            row["max_node_reward"] = res.max_node_reward
            row["mean_node_reward"] = res.mean_node_reward
            row["reward_variance"] = res.reward_variance
                
            writer.writerow(row)
