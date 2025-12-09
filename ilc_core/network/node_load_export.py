import csv
import json
from pathlib import Path
from typing import Dict, Any, Union
from os import PathLike

def export_node_load_to_csv(
    node_load: Dict[str, Dict[str, Any]],
    path: Union[str, PathLike],
) -> None:
    """
    Export node load metrics to CSV.

    Input format:
        {
          "node_id_1": {"num_tasks": float, "total_reward": float, "avg_reward": float, ...},
          "node_id_2": {...},
        }

    CSV format: one row per node, with a 'node_id' column plus all metric keys.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    # If empty, create an empty file and return (we don't know the header)
    if not node_load:
        p.touch()
        return

    # Flatten mapping to list of row dicts, adding node_id into each row
    rows = []
    all_keys = set(["node_id"])
    for node_id, metrics in node_load.items():
        row = {"node_id": node_id}
        if metrics:
            row.update(metrics)
            all_keys.update(metrics.keys())
        rows.append(row)

    # Deterministic ordering: sort by node_id and sort header alphabetically
    rows.sort(key=lambda r: r["node_id"])
    header = sorted(list(all_keys))

    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

def export_node_load_to_json(
    node_load: Dict[str, Dict[str, Any]],
    path: Union[str, PathLike],
) -> None:
    """
    Export node load metrics to JSON as a list of row dicts with 'node_id' included.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if not node_load:
        # For JSON we can safely emit an empty list
        with p.open("w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
        return

    rows = []
    for node_id, metrics in node_load.items():
        row = {"node_id": node_id}
        if metrics:
            row.update(metrics)
        rows.append(row)

    rows.sort(key=lambda r: r["node_id"])

    with p.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
