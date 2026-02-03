"""
Persistent ledger backend implementation using file storage.
"""

import os
import json
import shutil
from typing import Dict, Any, Optional

from ilc_core.ledger.backend import InMemoryLedgerBackend
from ilc_core.ledger.stake_snapshot import StakeSnapshot


class FileLedgerBackend(InMemoryLedgerBackend):
    """
    A persistent ledger backend that stores state in JSON files.
    
    Directory structure:
    storage_dir/
      balances.json     - Map of agent_id -> balance
      epochs/           - One JSON file per epoch record (e.g. epoch_123.json)
      snapshots/        - One JSON file per stake snapshot (e.g. epoch_123.json)
    """

    def __init__(self, storage_dir: str):
        super().__init__()
        self.storage_dir = storage_dir
        self.epochs_dir = os.path.join(storage_dir, "epochs")
        self.snapshots_dir = os.path.join(storage_dir, "snapshots")
        self.balances_file = os.path.join(storage_dir, "balances.json")

        self._ensure_directories()
        self._load_state()

    def _ensure_directories(self):
        """Ensure storage directories exist."""
        os.makedirs(self.epochs_dir, exist_ok=True)
        os.makedirs(self.snapshots_dir, exist_ok=True)

    def _load_state(self):
        """Load state from disk into memory."""
        # Load balances
        if os.path.exists(self.balances_file):
            try:
                with open(self.balances_file, "r") as f:
                    self.balances = json.load(f)
            except json.JSONDecodeError:
                # If corrupt or empty, start fresh (or raise? MVP: start fresh/warn)
                # For safety, let's just log/pass.
                pass

        # Load epochs
        # Shape: { "epoch_id": "...", "status": "...", ... }
        for filename in os.listdir(self.epochs_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.epochs_dir, filename)
                try:
                    with open(path, "r") as f:
                        record = json.load(f)
                        self.epoch_records[record["epoch_id"]] = record
                except (json.JSONDecodeError, KeyError):
                    continue

        # Load snapshots
        # Shape: { "epoch_id": "...", "stakes": {}, ... }
        for filename in os.listdir(self.snapshots_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.snapshots_dir, filename)
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                        # We only check for shape compatibility
                        if "schema_version" in data and data["schema_version"] == 1:
                            snapshot = StakeSnapshot(
                                epoch_id=data["epoch_id"],
                                epoch_index=data["epoch_index"],
                                namespace_id=data["namespace_id"],
                                stakes=data["stakes"],
                                total_stake=data["total_stake"],
                                created_at=data["created_at"],
                            )
                            self.stake_snapshots[snapshot.epoch_id] = snapshot
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

    def _atomic_write(self, path: str, data: Any):
        """
        Write data to a file atomically.
        
        1. Write to .tmp
        2. Flush/Success
        3. os.replace(tmp, target)
        """
        tmp_path = path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)

    # --- Overrides for persistence ---

    def _set_balance(self, agent_id: str, new_balance: float) -> None:
        """Update balance and persist balances.json."""
        super()._set_balance(agent_id, new_balance)
        # For MVP, we dump the whole balances dict. 
        # In a real system, this would be an append-log or DB.
        self._atomic_write(self.balances_file, self.balances)

    def _store_epoch_record(self, record: Dict[str, Any]) -> None:
        """Update epoch record and persist individual epoch file."""
        super()._store_epoch_record(record)
        path = os.path.join(self.epochs_dir, f"{record['epoch_id']}.json")
        self._atomic_write(path, record)

    def _store_stake_snapshot(self, snapshot: StakeSnapshot) -> None:
        """Update snapshot and persist individual snapshot file."""
        # Note: InMemory put_stake_snapshot calls this hook AFTER updating self.stake_snapshots.
        # But wait, InMemory.put_stake_snapshot updates self.stake_snapshots directly in MVP...
        # Ah, I added the hook in previous step:
        # self.stake_snapshots[snapshot.epoch_id] = snapshot
        # self._store_stake_snapshot(snapshot)
        
        # So super() is already done (conceptually, though hook logic assumes side-effect outside).
        # Wait, if I call super().put_stake_snapshot, it calls my _store_stake_snapshot.
        # So I don't need to call super() inside _store_stake_snapshot.
        
        data = {
            "schema_version": 1,
            "epoch_id": snapshot.epoch_id,
            "epoch_index": snapshot.epoch_index,
            "namespace_id": snapshot.namespace_id,
            "stakes": snapshot.stakes,
            "total_stake": snapshot.total_stake,
            "created_at": snapshot.created_at,
        }
        path = os.path.join(self.snapshots_dir, f"{snapshot.epoch_id}.json")
        self._atomic_write(path, data)
