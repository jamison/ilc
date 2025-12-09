import csv
import json
from pathlib import Path
from typing import Dict, Union, Any
from os import PathLike

def export_node_load_to_csv(
    node_load: Dict[str, Dict[str, float]], 
    path: Union[str, PathLike]
) -> None:
    """
    Export node load metrics to a CSV file.
    Rows: node_id, num_tasks, total_reward, avg_reward
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    header = ["node_id", "num_tasks", "total_reward", "avg_reward"]
    
    rows = []
    for node_id, metrics in node_load.items():
        row = {
            "node_id": node_id,
            "num_tasks": metrics.get("num_tasks", 0.0),
            "total_reward": metrics.get("total_reward", 0.0),
            "avg_reward": metrics.get("avg_reward", 0.0)
        }
        rows.append(row)
    
    # Sort by node_id for stability
    rows.sort(key=lambda x: x["node_id"])
    
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

def export_node_load_to_json(
    node_load: Dict[str, Dict[str, float]], 
    path: Union[str, PathLike]
) -> None:
    """
    Export node load metrics to a JSON file (list of dicts).
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Transform to list of dicts to match CSV structure/easier parsing
    data = []
    for node_id, metrics in node_load.items():
        item = {"node_id": node_id}
        item.update(metrics)
        data.append(item)
        
    # Sort
    data.sort(key=lambda x: x["node_id"])
    
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
