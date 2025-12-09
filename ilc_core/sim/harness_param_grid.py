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
    
def apply_params_to_scenario(
    scenario: DevnetScenarioConfig, 
    params: Dict[str, Any]
) -> None:
    """Helper: Apply matching keys to scenario, ignore others."""
    for k, v in params.items():
        if hasattr(scenario, k):
            setattr(scenario, k, v)

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
        grid: Dictionary mapping parameter names to lists of values to sweep.
        apply_params: Optional hook to apply parameters to the scenario. 
                      If None, matching keys are applied directly to scenario fields.
                      NOTE: keys in `grid` that do not match DevnetScenarioConfig fields
                      are ignored by the default logic but are still recorded in 
                      GridRunResult.params and exported to CSV. These serve as 
                      "external knobs" (e.g. controller gains).
        label_suffix_builder: Optional callback to generate a custom label suffix from params.
        rng_seed: Optional master seed. If provided, a deterministic derivation is used 
                  to seed each individual run.

    Returns:
        List of GridRunResult objects containing params and experiment summary.
        label_suffix_builder: Optional hook to generate label suffixes.
        rng_seed: Optional master seed. If set, each grid point run gets a
                  deterministic seed derived from this (rng_seed + run_index).
        export_root: Optional root directory to save per-run NDJSON events.
        export_prefix: Prefix for per-run export directories/files.
        
    Keys in `grid` that match `DevnetScenarioConfig` fields are applied automatically.
    Keys that do not match are ignored by the config updater but recorded in results
    (useful for external knobs like econ params).
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
        
        # 5. Summarize
        summary = summarize_multi_epoch_run(
            label=scenario.label,
            multi=multi_result
        )
        
        results.append(GridRunResult(
            params=params,
            summary=summary
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
        "avg_tasks_per_epoch", "avg_reward_per_task", "max_node_tasks"
    ]
    
    header = param_keys + summary_fields
    
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
                
            writer.writerow(row)
