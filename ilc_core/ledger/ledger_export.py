import json
import csv
from os import PathLike
from pathlib import Path
from dataclasses import asdict
from typing import Any, Dict

from ilc_core.ledger.backend import LedgerBackend

def export_ledger_state_json(ledger: LedgerBackend, path: PathLike) -> None:
    """
    Export full ledger state to a JSON file.
    
    Includes:
    - epoch_records
    - stake_snapshots
    - balances
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Access internal storage (assuming InMemory/File backend structure)
    epoch_records = getattr(ledger, "epoch_records", {})
    balances = getattr(ledger, "balances", {})
    raw_snapshots = getattr(ledger, "stake_snapshots", {})
    
    # Convert snapshots to dicts
    snapshots_data = {}
    for epoch_id, snap in raw_snapshots.items():
        if hasattr(snap, "to_dict"):
            snapshots_data[epoch_id] = snap.to_dict()
        else:
            snapshots_data[epoch_id] = asdict(snap)
            
    data = {
        "epoch_records": epoch_records,
        "stake_snapshots": snapshots_data,
        "balances": balances
    }
    
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def export_ledger_state_csv(ledger: LedgerBackend, path: PathLike) -> None:
    """
    Export ledger epoch records to a CSV file.
    
    Note: Currently only exports flat epoch records. 
    Snapshots and balances are available in the JSON export.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    epoch_records = getattr(ledger, "epoch_records", {})
    
    if not epoch_records:
        # Create empty file
        p.touch()
        return

    # Flatten logic
    rows = []
    headers = set()
    
    # Pre-scan for headers (optional, or just use hardcoded common ones then dynamic)
    # We want a stable order.
    # Common keys: epoch_id, epoch_index, status, distribution_status, summary.*
    
    for rec in epoch_records.values():
        row = rec.copy()
        
        # Flatten metrics/summary
        summary = row.pop("summary", None) or {}
        for k, v in summary.items():
            row[f"summary_{k}"] = v
            
        # Flatten checksums
        checksums = row.pop("checksums", None) or {}
        for k, v in checksums.items():
            row[f"checksum_{k}"] = v
            
        rows.append(row)
        headers.update(row.keys())
        
    # Sort headers for stability
    header_list = sorted(list(headers))
    # Move epoch_index, epoch_id to front if present
    for k in ["epoch_id", "epoch_index"]:
        if k in header_list:
            header_list.remove(k)
            header_list.insert(0, k)
            
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header_list)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
