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

def run_param_grid_on_devnet(
    base_scenario: DevnetScenarioConfig,
    grid: Dict[str, List[Any]],
    *,
    apply_params: Optional[Callable[[DevnetScenarioConfig, Dict[str, Any]], DevnetScenarioConfig]] = None,
    label_suffix_builder: Optional[Callable[[Dict[str, Any]], str]] = None,
    rng_seed: Optional[int] = None,
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
    """
    keys = sorted(grid.keys())
    values_list = [grid[k] for k in keys]
    
    results = []
    
    # Iterate over cartesian product
    for combination in itertools.product(*values_list):
        # Build params dict for this point
        params = dict(zip(keys, combination))
        
        # Clone base scenario
        # We use copy.deepcopy to ensure no mutable state leaks between runs
        # (though currently config is mostly immutable dataclass, good practice)
        current_scenario = copy.deepcopy(base_scenario)
        
        # Apply parameters
        if apply_params:
            current_scenario = apply_params(current_scenario, params)
        else:
            # Default application: set attributes if they exist
            # Note: non-matching keys are intentionally ignored here (external knobs)
            for k, v in params.items():
                if hasattr(current_scenario, k):
                    setattr(current_scenario, k, v)
        
        # Construct label
        if label_suffix_builder:
            suffix = label_suffix_builder(params)
            current_scenario.label = f"{base_scenario.label}_{suffix}"
        else:
            param_str = "_".join(f"{k}={v}" for k, v in params.items())
            current_scenario.label = f"{base_scenario.label}_{param_str}"
        
        # Deterministic seed derivation
        run_seed = None
        if rng_seed is not None:
            # Sort items to ensure deterministic hashing regardless of dict iteration order
            # (though params is created from sorted keys above, safety first)
            p_tuple = tuple(sorted(params.items()))
            run_seed = hash((rng_seed, p_tuple)) & 0xffffffff
        
        # Execute scenario
        # 1. Build components
        topo, profiles = build_topology_and_profiles(current_scenario)
        snapshots = build_snapshots_for_scenario(current_scenario)
        
        # 2. Run multi-epoch
        multi_result = run_devnet_multi_epoch(
            topology=topo,
            snapshots=snapshots,
            profiles=profiles,
            export_root=None,
            rng_seed=run_seed
        )
        
        # 3. Summarize
        summary = summarize_multi_epoch_run(
            label=current_scenario.label,
            multi=multi_result
        )
        
        results.append(GridRunResult(params=params, summary=summary))
        
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
