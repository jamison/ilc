from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Dict, List, Optional, TypedDict, TypeAlias
from os import PathLike
from pathlib import Path
import csv
import json

from ilc_core.sim.devnet_multi_epoch import DevnetMultiEpochResult


_REPORT_QUANTUM = Decimal("0.000000000001")


def _stable_float(value: float) -> float:
    return float(Decimal(str(value)).quantize(_REPORT_QUANTUM, rounding=ROUND_HALF_EVEN))


class SettlementMetrics(TypedDict, total=False):
    num_epochs_total: int
    num_epochs_settled: int
    num_epochs_rolled_back: int
    num_epochs_superseded: int
    num_snapshots: int
    total_rewards_distributed: float
    total_rewards_stubbed: float


SettlementMetricsOpt: TypeAlias = SettlementMetrics | None


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
    # Phase 64B: Backlog Metrics
    mean_backlog_per_epoch: float = 0.0
    max_backlog: float = 0.0
    mean_backlog_ratio: float = 0.0
    # Phase 70F: Settlement Metrics
    settlement_metrics: SettlementMetricsOpt = None

def summarize_multi_epoch_run(
    label: str,
    multi: DevnetMultiEpochResult,
    settlement_metrics: SettlementMetricsOpt = None,
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
    avg_tasks_per_epoch = _stable_float(total_tasks / max(num_epochs, 1) if num_epochs > 0 else 0.0)
    avg_reward_per_task = _stable_float((total_reward / total_tasks) if total_tasks > 0 else 0.0)
    
    # Phase 64B: Backlog Aggregation
    backlogs = [float(er.backlog_count) for er in multi.epoch_results]
    # Ratio = backlog / max(1, suggestions). Note: suggestions = backlog + executed.
    ratios = [
        float(er.backlog_count) / max(1.0, float(er.num_suggestions)) 
        for er in multi.epoch_results
    ]
    
    mean_backlog = _stable_float(sum(backlogs) / max(num_epochs, 1) if num_epochs > 0 else 0.0)
    max_backlog_val = max(backlogs) if backlogs else 0.0
    mean_ratio = _stable_float(sum(ratios) / max(num_epochs, 1) if num_epochs > 0 else 0.0)

    return DevnetExperimentSummary(
        label=label,
        namespace_id=ns_id,
        num_epochs=num_epochs,
        total_tasks=total_tasks,
        total_reward=total_reward,
        avg_tasks_per_epoch=avg_tasks_per_epoch,
        avg_reward_per_task=avg_reward_per_task,
        max_node_tasks=max_node_tasks,
        mean_backlog_per_epoch=mean_backlog,
        max_backlog=max_backlog_val,
        mean_backlog_ratio=mean_ratio,
        settlement_metrics=settlement_metrics,
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
        "max_node_tasks",
        # Phase 64B
        "mean_backlog_per_epoch", "max_backlog", "mean_backlog_ratio",
        # Phase 70F: Settlement Metrics
        "settlement_num_epochs_total",
        "settlement_num_epochs_settled",
        "settlement_num_epochs_rolled_back",
        "settlement_num_epochs_superseded",
        "settlement_num_snapshots",
        "settlement_total_rewards_distributed",
        "settlement_total_rewards_stubbed",
    ]
    
    # Pre-process rows to flatten settlement_metrics
    rows = []
    for s in summaries:
        row = asdict(s)
        metrics = row.pop("settlement_metrics", None)
        
        # Default empty values for settlement columns
        stats = {
            "num_epochs_total": 0,
            "num_epochs_settled": 0,
            "num_epochs_rolled_back": 0,
            "num_epochs_superseded": 0,
            "num_snapshots": 0,
            "total_rewards_distributed": 0.0,
            "total_rewards_stubbed": 0.0,
        }
        
        if metrics:
            stats.update(metrics)
            
        for k, v in stats.items():
            row[f"settlement_{k}"] = v
            
        rows.append(row)
    
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def export_experiment_summaries_to_json(
    summaries: List[DevnetExperimentSummary],
    path: PathLike,
) -> None:
    """
    Write experiment summaries to a JSON list, including flattened metrics.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    rows = []
    for s in summaries:
        row = asdict(s)
        metrics = row.pop("settlement_metrics", None) or {}
        
        # We assume parity with CSV: prefix with settlement_
        for k, v in metrics.items():
            row[f"settlement_{k}"] = v
            
        rows.append(row)
        
    with p.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
