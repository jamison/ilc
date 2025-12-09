from dataclasses import dataclass
from typing import List, Callable, Optional, Dict
import math

from ilc_core.sim.devnet_scenarios import (
    DevnetScenarioConfig,
    build_topology_and_profiles,
    build_snapshots_for_scenario
)
from ilc_core.sim.devnet_multi_epoch import run_devnet_multi_epoch
from ilc_core.sim.devnet_experiments import summarize_multi_epoch_run
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot

@dataclass
class ClosedLoopRunConfig:
    label: str
    num_epochs: int
    scenario: DevnetScenarioConfig

@dataclass
class ClosedLoopEpochMetrics:
    epoch_index: int
    total_tasks: float
    total_reward: float
    avg_reward_per_task: float
    backlog_proxy: float  # Placeholder for now

def run_closed_loop_devnet(
    config: ClosedLoopRunConfig,
    controller_step: Callable[[int, ClosedLoopEpochMetrics], None],
) -> List[ClosedLoopEpochMetrics]:
    """
    Run a devnet simulation epoch-by-epoch, invoking a controller step
    after each epoch to allow parameter adjustment.
    """
    metrics_history: List[ClosedLoopEpochMetrics] = []
    
    # Build initial state
    # We build topology/profiles once (assuming static network for MVP closed loop)
    topo, profiles = build_topology_and_profiles(config.scenario)
    
    # We will derive stress from scenario schedule if available, or just reuse last value?
    # For MVP, let's assume scenario.stress_schedule has at least 'num_epochs' entries
    # OR replicate the last one if we run out.
    base_schedule = config.scenario.stress_schedule
    
    for i in range(config.num_epochs):
        epoch_idx = i + 1
        
        # 1. Determine Stress for this epoch
        if i < len(base_schedule):
            stress_val = base_schedule[i]
        else:
            stress_val = base_schedule[-1] if base_schedule else 0.5
            
        # 2. Build ONE snapshot for this single epoch
        # (We use correct epoch index)
        # We reuse the logic from build_snapshots_for_scenario but just for one point
        # A bit hacky: create a temporary config with 1-item schedule to use builder?
        # Or just instantiate manually like the builder does.
        # Let's instantiate manually to avoid overhead/confusion.
        
        # Need defaults constants? They are in devnet_scenarios but not exported publicly
        # in a clean way except via build_snapshots. 
        # Actually, let's just make a mini config for this epoch to reuse builder consistency.
        mini_config = DevnetScenarioConfig(
            label=f"{config.label}_epoch_{epoch_idx}",
            stress_schedule=[stress_val],
            namespace_id=config.scenario.namespace_id,
            num_agents=config.scenario.num_agents,
            topology_kind=config.scenario.topology_kind,
            center_id=config.scenario.center_id,
            worker_ids=config.scenario.worker_ids
        )
        
        one_epoch_snapshots = build_snapshots_for_scenario(mini_config)
        # Fixup epoch index in the generated snapshot (builder starts at 1)
        # But wait, run_devnet_multi_epoch expects snapshots.
        # If we pass a list of 1 snapshot, it will run 1 epoch.
        # But we want the epoch_index to be correct (i+1). 
        # build_snapshots_for_scenario(mini_config) will use index 0 -> epoch 1.
        # If we are at i=5 (epoch 6), we need to fix it.
        one_epoch_snapshots[0].epoch_index = epoch_idx
        
        # 3. Run ONE epoch
        # (We pass the existing topo/profiles)
        multi_result = run_devnet_multi_epoch(
            topology=topo,
            snapshots=one_epoch_snapshots,
            profiles=profiles,
            export_root=None
        )
        
        # 4. Computing Metrics
        # We can use summarize_multi_epoch_run on this 1-epoch result
        summary = summarize_multi_epoch_run(
            label=f"epoch_{epoch_idx}",
            multi=multi_result
        )
        
        # 5. Build Metric Object
        m = ClosedLoopEpochMetrics(
            epoch_index=epoch_idx,
            total_tasks=summary.total_tasks,
            total_reward=summary.total_reward,
            avg_reward_per_task=summary.avg_reward_per_task,
            backlog_proxy=0.0 # Placeholder
        )
        metrics_history.append(m)
        
        # 6. Controller Hook
        controller_step(epoch_idx, m)
        
    return metrics_history
