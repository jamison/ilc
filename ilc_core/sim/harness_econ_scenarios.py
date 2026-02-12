from dataclasses import dataclass, asdict
from typing import List, Dict, Callable, Union, Optional, Iterable, TypeAlias
from os import PathLike
from pathlib import Path
import csv 

# Add ProtocolParams import
from ilc_core.protocol.params import ProtocolParams, normalize_protocol_overrides

import logging

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
from ilc_core.ledger import get_ledger_backend


OverrideScalar: TypeAlias = str | int | float | bool | None
EconOverrideMap: TypeAlias = Dict[str, OverrideScalar]


@dataclass
class EconScenarioConfig:
    label: str
    param_overrides: EconOverrideMap

def default_apply_econ(overrides: EconOverrideMap) -> None:
    """
    Apply economic overrides (burn rates, PB rates, etc.) to the global
    protocol parameters / genesis state used by devnet simulations.

    This is an MVP helper for use in demos and simple experiments.
    It currently validates econ override keys against ProtocolParams and 
    logs warnings for unknown keys; it is intentionally a no-op on actual 
    protocol state in the MVP until singletons are established.
    """
    # 1. Normalize Keys / Coerce Types (Hygiene Phase 64C)
    normalized = normalize_protocol_overrides(overrides)

    # Validation step: map overrides to ProtocolParams fields
    valid_keys = set(ProtocolParams.__annotations__.keys())
    filtered_overrides = {}
    
    for k, v in normalized.items():
        if k in valid_keys:
            filtered_overrides[k] = v
        else:
            logging.warning(f"Unknown econ override key: {k} (ignored)")
            
    # Instantiate params to demonstrate valid shape (and catch type errors)
    if filtered_overrides:
        # NOTE: For MVP we only validate overrides by constructing a ProtocolParams
        # instance. We do not mutate any global state yet; wiring to a real
        # parameter registry is a future phase.
        params = ProtocolParams(**filtered_overrides)
        logging.debug(f"Effective econ params for this run: {params}")

def run_econ_scenarios_on_devnet(
    base_scenario: DevnetScenarioConfig,
    econ_scenarios: List[EconScenarioConfig],
    *,
    apply_econ: Callable[[EconOverrideMap], None],
    rng_seed: Optional[int] = None,
    export_root: Optional[PathLike] = None,
    export_prefix: str = "econ",
) -> List[DevnetExperimentSummary]:
    """
    Run a set of economic scenarios using a base devnet configuration.

    Args:
        base_scenario: The template configuration for topology/agents/stress.
        econ_scenarios: List of economic configurations to test.
        apply_econ: Hook to apply global economic parameter overrides.
        rng_seed: Base random seed. Each scenario uses rng_seed + list_index.
        export_root: Optional root directory to enable NDJSON exports.
                     If provided, creates subdirectories: 
                     `{export_root}/{scenario.label}/epoch_XXXX/devnet_events.ndjson`.
        export_prefix: Prefix for per-run export directories (default "econ", 
                       though usually the scenario label is used directly).

    Returns:
        List of DevnetExperimentSummary objects.
    """
    results = []
    
    for i, econ_scen in enumerate(econ_scenarios):
        # 1. Apply Econ Params (Global Hook)
        apply_econ(econ_scen.param_overrides)
        
        # 2. Build Components from Base Scenario
        topo, profiles = build_topology_and_profiles(base_scenario)
        snapshots = build_snapshots_for_scenario(base_scenario)
        
        # Derive seed
        run_seed = None
        if rng_seed is not None:
             # Simple stable derivation: master + index
            run_seed = rng_seed + i
            
        # Determine Per-Run Export Path
        run_export_dir = None
        if export_root:
            run_export_dir = Path(export_root) / econ_scen.label
            
        # 3. Run Simulation
        ledger = get_ledger_backend(
            kind=base_scenario.ledger_backend_kind,
            storage_dir=base_scenario.ledger_storage_dir
        )
        multi_result = run_devnet_multi_epoch(
            topology=topo,
            snapshots=snapshots,
            profiles=profiles,
            export_root=run_export_dir,
            rng_seed=run_seed,
            ledger_backend=ledger
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

def export_econ_summaries_with_overrides_to_csv(
    econ_scenarios: Iterable[EconScenarioConfig],
    summaries: Iterable[DevnetExperimentSummary],
    path: Union[str, PathLike],
) -> None:
    """
    Export econ scenario results to CSV, including both summary metrics
    and the econ overrides used for each run.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert iterables to lists to ensure alignment/reusability
    scenarios_list = list(econ_scenarios)
    summaries_list = list(summaries)
    
    if len(scenarios_list) != len(summaries_list):
        raise ValueError("Mismatch between scenarios and summaries count")
        
    if not scenarios_list:
        return
        
    # 1. Identify all override keys union
    override_keys = set()
    for sc in scenarios_list:
        override_keys.update(sc.param_overrides.keys())
    sorted_econ_keys = sorted(list(override_keys))
    
    # 2. Define headers
    # Base summary fields (hardcoded or inspected)
    summary_fields = [
        "label", "namespace_id", "num_epochs", 
        "total_tasks", "total_reward", 
        "avg_tasks_per_epoch", "avg_reward_per_task", 
        "max_node_tasks",
        # Phase 64B
        "mean_backlog_per_epoch", "max_backlog", "mean_backlog_ratio"
    ] 
    
    # Econ columns prefixed
    econ_cols = [f"econ_{k}" for k in sorted_econ_keys]
    header = summary_fields + econ_cols
    
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        
        for sc, summary in zip(scenarios_list, summaries_list):
            row = asdict(summary)
            
            # Add overrides
            for k in sorted_econ_keys:
                val = sc.param_overrides.get(k, "")
                row[f"econ_{k}"] = val
                
            writer.writerow(row)
