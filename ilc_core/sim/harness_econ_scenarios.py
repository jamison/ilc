from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Callable, Union, Optional
from os import PathLike
from pathlib import Path
import csv

from ilc_core.sim.devnet_scenarios import (
    DevnetScenarioConfig,
    build_topology_and_profiles,
    build_snapshots_for_scenario,
)
from ilc_core.sim.devnet_multi_epoch import run_devnet_multi_epoch
from ilc_core.sim.devnet_experiments import (
    summarize_multi_epoch_run, 
    DevnetExperimentSummary,
    export_experiment_summaries_to_csv
)

@dataclass
class EconScenarioConfig:
    label: str
    param_overrides: Dict[str, Any]

def run_econ_scenarios_on_devnet(
    base_scenario: DevnetScenarioConfig,
    econ_scenarios: List[EconScenarioConfig],
    *,
    apply_econ: Callable[[Dict[str, Any]], None],
) -> List[DevnetExperimentSummary]:
    """
    Run a set of economic scenarios using a base devnet configuration.

    Args:
        base_scenario: The template configuration for topology/agents/stress.
        econ_scenarios: List of economic configurations to test.
        apply_econ: Hook to apply global economic parameter overrides.

    Returns:
        List of DevnetExperimentSummary objects.
    """
    results = []
    
    for econ_scen in econ_scenarios:
        # 1. Apply Econ Params (Global Hook)
        apply_econ(econ_scen.param_overrides)
        
        # 2. Build Components from Base Scenario
        # (We rebuild per scenario in case apply_econ affects building logic, 
        # though usually it affects runtime logic)
        topo, profiles = build_topology_and_profiles(base_scenario)
        snapshots = build_snapshots_for_scenario(base_scenario)
        
        # 3. Run Simulation
        multi_result = run_devnet_multi_epoch(
            topology=topo,
            snapshots=snapshots,
            profiles=profiles,
            export_root=None
        )
        
        # 4. Summarize (Use econ scenario label)
        summary = summarize_multi_epoch_run(
            label=econ_scen.label,
            multi=multi_result
        )
        results.append(summary)
        
    return results

def export_econ_scenario_summaries_to_csv(
    summaries: List[DevnetExperimentSummary],
    path: Union[str, PathLike],
) -> None:
    """
    Export results to CSV (thin wrapper around standard summary export).
    """
    export_experiment_summaries_to_csv(summaries, path)
