# SPDX-License-Identifier: AGPL-3.0-only
"""
Persistent ledger backend implementation using file storage.
"""

from __future__ import annotations

import json
import os
import tempfile
from typing import cast

from ilc_core.ledger.backend import EpochRecord, InMemoryLedgerBackend, JsonObject
from ilc_core.ledger.exact_numeric import exact_to_canonical_string, to_decimal
from ilc_core.ledger.stake_snapshot import StakeSnapshot
from ilc_core.protocol.event_log import ProtocolEvent


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
        self._defer_balance_persistence = False
        self._balances_dirty = False

        self._ensure_directories()
        self._load_state()

    def _ensure_directories(self) -> None:
        """Ensure storage directories exist."""
        os.makedirs(self.epochs_dir, exist_ok=True)
        os.makedirs(self.snapshots_dir, exist_ok=True)

    def _load_state(self) -> None:
        """Load state from disk into memory."""
        self._load_balances()
        self._load_epoch_records()
        self._load_stake_snapshots()

    def _load_json_file(self, path: str) -> JsonObject | None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
        if isinstance(data, dict):
            return cast(JsonObject, data)
        return None

    def _load_balances(self) -> None:
        if not os.path.exists(self.balances_file):
            return
        data = self._load_json_file(self.balances_file)
        if isinstance(data, dict):
            self.balances = {
                agent_id: to_decimal(amount, token="file_ledger_balance_invalid")
                for agent_id, amount in data.items()
                if isinstance(agent_id, str)
            }

    def _load_epoch_records(self) -> None:
        # Shape: { "epoch_id": "...", "status": "...", ... }
        for filename in os.listdir(self.epochs_dir):
            if not filename.endswith(".json"):
                continue
            path = os.path.join(self.epochs_dir, filename)
            record = self._load_json_file(path)
            if isinstance(record, dict) and "epoch_id" in record:
                epoch_id = record["epoch_id"]
                if isinstance(epoch_id, str):
                    self.epoch_records[epoch_id] = cast(EpochRecord, record)

    def _load_stake_snapshots(self) -> None:
        # Shape: { "epoch_id": "...", "stakes": {}, ... }
        for filename in os.listdir(self.snapshots_dir):
            if not filename.endswith(".json"):
                continue
            path = os.path.join(self.snapshots_dir, filename)
            snapshot = self._parse_stake_snapshot_file(path)
            if snapshot:
                self.stake_snapshots[snapshot.epoch_id] = snapshot

    def _parse_stake_snapshot_file(self, path: str) -> StakeSnapshot | None:
        """Parse a single stake snapshot file."""
        data = self._load_json_file(path)
        if not isinstance(data, dict):
            return None
        if data.get("schema_version") != 1:
            return None
        try:
            return StakeSnapshot(
                epoch_id=cast(str, data["epoch_id"]),
                epoch_index=cast(int, data["epoch_index"]),
                namespace_id=cast(str, data["namespace_id"]),
                stakes=cast(dict[str, object], data["stakes"]),
                total_stake=cast(object, data["total_stake"]),
                created_at=cast(str, data["created_at"]),
            )
        except (KeyError, ValueError):
            return None

    def _atomic_write(self, path: str, data: object) -> None:
        """
        Write data to a file atomically using a unique temp file.

        1. Write to a unique .tmp (tempfile.mkstemp in same directory)
        2. Flush/sync
        3. os.replace(tmp, target)

        Using a unique temp name prevents concurrent-process corruption when
        multiple nodes share the same filesystem path.
        """
        target = os.path.abspath(path)
        parent = os.path.dirname(target)
        stem = os.path.splitext(os.path.basename(target))[0]
        fd, tmp_path = tempfile.mkstemp(dir=parent, prefix=f".{stem}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, sort_keys=True, allow_nan=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, target)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    # --- Overrides for persistence ---

    def _persist_balances(self) -> None:
        self._atomic_write(
            self.balances_file,
            {
                account_id: exact_to_canonical_string(
                    balance,
                    token="file_ledger_balance_invalid",
                )
                for account_id, balance in self.balances.items()
            },
        )

    def _set_balance(self, agent_id: str, new_balance: object) -> None:
        """Update balance and persist balances.json."""
        super()._set_balance(agent_id, new_balance)
        if self._defer_balance_persistence:
            self._balances_dirty = True
            return
        self._persist_balances()

    def apply_epoch_settlement(self, epoch_event: ProtocolEvent) -> None:
        balances_before = self.balances.copy()
        self._defer_balance_persistence = True
        self._balances_dirty = False
        try:
            super().apply_epoch_settlement(epoch_event)
        except Exception:
            self.balances = balances_before
            raise
        finally:
            should_persist = self._balances_dirty
            self._defer_balance_persistence = False
            self._balances_dirty = False
        if should_persist:
            self._persist_balances()

    def _store_epoch_record(self, record: EpochRecord) -> None:
        """Update epoch record and persist individual epoch file."""
        super()._store_epoch_record(record)
        path = os.path.join(self.epochs_dir, f"{record['epoch_id']}.json")
        self._atomic_write(path, record)

    def _store_stake_snapshot(self, snapshot: StakeSnapshot) -> None:
        """Update snapshot and persist individual snapshot file."""
        data: JsonObject = {
            "schema_version": 1,
            "epoch_id": snapshot.epoch_id,
            "epoch_index": snapshot.epoch_index,
            "namespace_id": snapshot.namespace_id,
            "stakes": {
                agent_id: exact_to_canonical_string(amount, token="file_ledger_stake_invalid")
                for agent_id, amount in snapshot.stakes.items()
            },
            "total_stake": exact_to_canonical_string(
                snapshot.total_stake,
                token="file_ledger_total_stake_invalid",
            ),
            "created_at": snapshot.created_at,
        }
        path = os.path.join(self.snapshots_dir, f"{snapshot.epoch_id}.json")
        self._atomic_write(path, data)
