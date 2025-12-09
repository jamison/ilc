import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Union
from os import PathLike

def export_routed_tasks_to_csv(
    routed_task_rows: List[Dict[str, Any]], 
    path: Union[str, PathLike]
) -> None:
    """
    Export a list of routed task dictionaries to a CSV file.
    """
    if not routed_task_rows:
        # Create empty file or do nothing? Usually creation is better for pipelines.
        # But we need header. If empty, we can't infer header.
        # Let's create an empty file if list is empty, or skip writing header if no known keys.
        # Standard approach: ensure path parent exists, touch file.
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()
        return

    # Determine unique keys for header
    keys = set()
    for row in routed_task_rows:
        keys.update(row.keys())
    
    # Sort keys for deterministic output, prioritizing some common ones if we wanted, 
    # but alphabetical or 'definition order' from dataclass would be cleaner.
    # Since we receive dicts, let's just sort alphabetically for now to be stable.
    header = sorted(list(keys))
    
    # Specific ordering preference if possible? 
    # Let's just stick to sorted for now.
    
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(routed_task_rows)

def export_routed_tasks_to_json(
    routed_task_rows: List[Dict[str, Any]], 
    path: Union[str, PathLike]
) -> None:
    """
    Export a list of routed task dictionaries to a JSON file.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    with p.open("w", encoding="utf-8") as f:
        json.dump(routed_task_rows, f, indent=2)
