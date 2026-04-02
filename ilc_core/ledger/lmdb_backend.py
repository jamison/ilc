from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import lmdb

from ilc_core.ledger.backend import EpochRecord, InMemoryLedgerBackend, JsonObject
from ilc_core.ledger.stake_snapshot import StakeSnapshot


LMDB_LEDGER_BACKEND_VERSION = "lmdb_ledger_backend_v0.1"
DEFAULT_MAP_SIZE_BYTES = 256 * 1024 * 1024
_ENV_CACHE: dict[str, lmdb.Environment] = {}


def _encode_key(value: str) -> bytes:
    return value.encode("utf-8")


def _encode_json(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _decode_json(payload: bytes | None) -> JsonObject | None:
    if payload is None:
        return None
    value = json.loads(payload.decode("utf-8"))
    if isinstance(value, dict):
        return cast(JsonObject, value)
    return None


class LmdbLedgerBackend(InMemoryLedgerBackend):
    def __init__(self, storage_dir: str | Path):
        super().__init__()
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        root_key = str(self.storage_dir.resolve())
        self.env = _ENV_CACHE.get(root_key)
        if self.env is None:
            self.env = lmdb.open(
                root_key,
                create=True,
                subdir=True,
                max_dbs=3,
                map_size=DEFAULT_MAP_SIZE_BYTES,
                lock=True,
            )
            _ENV_CACHE[root_key] = self.env
        self._balances_db = self.env.open_db(b"balances")
        self._epochs_db = self.env.open_db(b"epochs")
        self._snapshots_db = self.env.open_db(b"snapshots")
        self._load_state()

    def _load_state(self) -> None:
        self._load_balances()
        self._load_epoch_records()
        self._load_stake_snapshots()

    def _load_balances(self) -> None:
        with self.env.begin(db=self._balances_db) as txn:
            cursor = txn.cursor()
            for key, value in cursor:
                decoded = _decode_json(value)
                if decoded is None:
                    continue
                amount = decoded.get("amount")
                if isinstance(amount, (int, float)) and not isinstance(amount, bool):
                    self.balances[key.decode("utf-8")] = float(amount)

    def _load_epoch_records(self) -> None:
        with self.env.begin(db=self._epochs_db) as txn:
            cursor = txn.cursor()
            for _, value in cursor:
                decoded = _decode_json(value)
                if decoded is None:
                    continue
                epoch_id = decoded.get("epoch_id")
                if isinstance(epoch_id, str) and epoch_id:
                    self.epoch_records[epoch_id] = cast(EpochRecord, decoded)

    def _load_stake_snapshots(self) -> None:
        with self.env.begin(db=self._snapshots_db) as txn:
            cursor = txn.cursor()
            for _, value in cursor:
                decoded = _decode_json(value)
                if decoded is None or decoded.get("schema_version") != 1:
                    continue
                try:
                    snapshot = StakeSnapshot(
                        epoch_id=cast(str, decoded["epoch_id"]),
                        epoch_index=cast(int, decoded["epoch_index"]),
                        namespace_id=cast(str, decoded["namespace_id"]),
                        stakes=cast(dict[str, float], decoded["stakes"]),
                        total_stake=cast(float, decoded["total_stake"]),
                        created_at=cast(str, decoded["created_at"]),
                    )
                except (KeyError, ValueError, TypeError):
                    continue
                self.stake_snapshots[snapshot.epoch_id] = snapshot

    def _set_balance(self, agent_id: str, new_balance: float) -> None:
        super()._set_balance(agent_id, new_balance)
        with self.env.begin(write=True, db=self._balances_db) as txn:
            txn.put(_encode_key(agent_id), _encode_json({"amount": new_balance}))

    def _store_epoch_record(self, record: EpochRecord) -> None:
        super()._store_epoch_record(record)
        epoch_id = cast(str, record["epoch_id"])
        with self.env.begin(write=True, db=self._epochs_db) as txn:
            txn.put(_encode_key(epoch_id), _encode_json(record))

    def _store_stake_snapshot(self, snapshot: StakeSnapshot) -> None:
        payload: JsonObject = {
            "schema_version": 1,
            "epoch_id": snapshot.epoch_id,
            "epoch_index": snapshot.epoch_index,
            "namespace_id": snapshot.namespace_id,
            "stakes": snapshot.stakes,
            "total_stake": snapshot.total_stake,
            "created_at": snapshot.created_at,
        }
        with self.env.begin(write=True, db=self._snapshots_db) as txn:
            txn.put(_encode_key(snapshot.epoch_id), _encode_json(payload))
