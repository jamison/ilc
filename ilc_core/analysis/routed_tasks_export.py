# SPDX-License-Identifier: AGPL-3.0-only
import csv
import json
from pathlib import Path
from typing import Union
from os import PathLike

from ilc_core.analysis.routed_tasks import TaskRowDictList

ROUTED_TASKS_CSV_HEADER = ("agent_id", "task_id", "task_type")

def export_routed_tasks_to_csv(
    routed_task_rows: TaskRowDictList,
    path: Union[str, PathLike]
) -> None:
    """
    Export a list of routed task dictionaries to a CSV file.
    """
    if not routed_task_rows:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(ROUTED_TASKS_CSV_HEADER)
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
    routed_task_rows: TaskRowDictList,
    path: Union[str, PathLike]
) -> None:
    """
    Export a list of routed task dictionaries to a JSON file.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    with p.open("w", encoding="utf-8") as f:
        json.dump(routed_task_rows, f, indent=2)
