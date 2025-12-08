from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from os import PathLike
from pathlib import Path

from ilc_core.network.topology import DevnetTopology
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.sim.devnet_epoch_orchestrator import DevnetEpochResult, run_devnet_epoch

@dataclass
class DevnetMultiEpochResult:
    namespace_id: str
    topology: DevnetTopology
    epoch_results: List[DevnetEpochResult]
    aggregate_node_load: Dict[str, Dict[str, float]]

def run_devnet_multi_epoch(
    topology: DevnetTopology,
    snapshots: List[NamespaceHealthSnapshot],
    profiles: Dict[str, AgentProfile],
    *,
    export_root: Optional[PathLike] = None,
    export_prefix: str = "epoch",
) -> DevnetMultiEpochResult:
    """
    Execute multiple devnet epochs sequentially based on a list of snapshots.
    
    Args:
        topology: The network topology (assumed static across epochs).
        snapshots: A list of NamespaceHealthSnapshot objects defining the sequence of epochs.
        profiles: Agent profiles (assumed static).
        export_root: Optional directory to create per-epoch export subdirectories in.
        export_prefix: Prefix for per-epoch directories (e.g. "epoch_0010").
        
    Returns:
        DevnetMultiEpochResult containing all per-epoch results and aggregated node load metrics.
    """
    
    # 1. Preconditions
    if not snapshots:
        return DevnetMultiEpochResult(
            namespace_id="",
            topology=topology,
            epoch_results=[],
            aggregate_node_load={}
        )

    # 2. Epoch Loop
    epoch_results: List[DevnetEpochResult] = []
    
    for snapshot in snapshots:
        epoch_index = snapshot.epoch_index
        export_dir_for_epoch = None
        
        if export_root:
            p_root = Path(export_root)
            # e.g. epoch_0010
            dir_name = f"{export_prefix}_{epoch_index:04d}"
            export_dir_for_epoch = p_root / dir_name
            
        result = run_devnet_epoch(
            epoch_index=epoch_index,
            topology=topology,
            namespace_snapshot=snapshot,
            profiles=profiles,
            export_dir=export_dir_for_epoch
        )
        epoch_results.append(result)

    # 3. Aggregate Node Load
    # We want to sum num_tasks and total_reward across all epochs per node.
    # Then recompute avg_reward.
    
    # First, gather all node IDs seen across any epoch
    all_nodes = set()
    for res in epoch_results:
        all_nodes.update(res.node_load_metrics.keys())
        
    agg_load: Dict[str, Dict[str, float]] = {}
    
    for node_id in all_nodes:
        total_tasks = 0.0
        total_reward = 0.0
        
        for res in epoch_results:
            metrics = res.node_load_metrics.get(node_id)
            if metrics:
                total_tasks += metrics.get("num_tasks", 0.0)
                total_reward += metrics.get("total_reward", 0.0)
        
        avg_rew = (total_reward / total_tasks) if total_tasks > 0 else 0.0
        
        agg_load[node_id] = {
            "num_tasks": total_tasks,
            "total_reward": total_reward,
            "avg_reward": avg_rew
        }

    # 4. Namespace ID
    # Assume single namespace for MVP
    ns_id = snapshots[0].namespace_id
    
    return DevnetMultiEpochResult(
        namespace_id=ns_id,
        topology=topology,
        epoch_results=epoch_results,
        aggregate_node_load=agg_load
    )
