from dataclasses import dataclass, asdict
from typing import Dict, Any, List
from os import PathLike
from pathlib import Path
import csv

from ilc_core.sim.devnet_multi_epoch import DevnetMultiEpochResult

@dataclass
class DevnetExperimentSummary:
    label: str
    namespace_id: str
    num_epochs: int
    total_tasks: float
    total_reward: float
    avg_tasks_per_epoch: float
    avg_reward_per_task: float
    max_node_tasks: float

def summarize_multi_epoch_run(
    label: str,
    multi: DevnetMultiEpochResult,
) -> DevnetExperimentSummary:
    """
    Summarize a multi-epoch run into a single KPI row.
    """
    # Basic metadata
    ns_id = multi.namespace_id
    num_epochs = len(multi.epoch_results)
    
    # Aggregations from aggregated node load
    # multi.aggregate_node_load is check: {node_id: {num_tasks, total_reward, avg_reward}}
    
    total_tasks = 0.0
    total_reward = 0.0
    max_node_tasks = 0.0
    
    for metrics in multi.aggregate_node_load.values():
        t = metrics.get("num_tasks", 0.0)
        r = metrics.get("total_reward", 0.0)
        
        total_tasks += t
        total_reward += r
        if t > max_node_tasks:
            max_node_tasks = t
            
    # Derived averages
    avg_tasks_per_epoch = total_tasks / max(num_epochs, 1) if num_epochs > 0 else 0.0
    avg_reward_per_task = (total_reward / total_tasks) if total_tasks > 0 else 0.0
    
    return DevnetExperimentSummary(
        label=label,
        namespace_id=ns_id,
        num_epochs=num_epochs,
        total_tasks=total_tasks,
        total_reward=total_reward,
        avg_tasks_per_epoch=avg_tasks_per_epoch,
        avg_reward_per_task=avg_reward_per_task,
        max_node_tasks=max_node_tasks,
    )

def export_experiment_summaries_to_csv(
    summaries: List[DevnetExperimentSummary],
    path: PathLike,
) -> None:
    """
    Write one row per experiment summary.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Use dataclass fields for header
    # We can get them from the first item or the class definition if list is empty
    # But asdict requires an instance. If empty, we can just use typing hints or hardcode, 
    # but easier to just use the class annotations if available, or just instantiate a dummy if needed.
    # Actually, proper way is fields(DevnetExperimentSummary), but let's keep it simple.
    
    header = [
        "label", "namespace_id", "num_epochs", 
        "total_tasks", "total_reward", 
        "avg_tasks_per_epoch", "avg_reward_per_task", 
        "max_node_tasks"
    ]
    
    rows = [asdict(s) for s in summaries]
    
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
