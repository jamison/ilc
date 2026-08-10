# SPDX-License-Identifier: AGPL-3.0-only
"""Epoch-keyed LMDB audit table for attribution event records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import lmdb


ATTRIBUTION_AUDIT_LMDB_VERSION = "attribution_audit_lmdb_phase_1594.v0.1"
DEFAULT_ATTRIBUTION_AUDIT_MAP_SIZE_BYTES = 128 * 1024 * 1024
ATTR_EVENTS_DB_NAME = b"attr_events"
EPOCH_INDEX_DB_NAME = b"epoch_index"
ATTR_EVENT_KEY_PREFIX = b"attr_event:"
EPOCH_INDEX_KEY_PREFIX = b"epoch:"


def _require_epoch(epoch: Any) -> int:
    if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
        raise ValueError("attribution_audit_epoch_invalid")
    return epoch


def _event_key(epoch: int, ordinal: int) -> bytes:
    return (
        ATTR_EVENT_KEY_PREFIX
        + epoch.to_bytes(8, "big", signed=False)
        + ordinal.to_bytes(8, "big", signed=False)
    )


def _epoch_index_key(epoch: int) -> bytes:
    return EPOCH_INDEX_KEY_PREFIX + epoch.to_bytes(8, "big", signed=False)


def _encode_json(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8",
    )


def _decode_list(payload: bytes | None) -> list[Any]:
    if payload is None:
        return []
    decoded = json.loads(payload.decode("utf-8"))
    if not isinstance(decoded, list):
        raise ValueError("attribution_audit_epoch_index_invalid")
    return decoded


def _decode_dict(payload: bytes) -> dict[str, Any]:
    decoded = json.loads(payload.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("attribution_audit_event_invalid")
    return cast(dict[str, Any], decoded)


class AttributionAuditLmdbStore:
    """Durable attribution event audit table keyed by epoch and ordinal."""

    def __init__(
        self,
        storage_dir: str | Path,
        *,
        map_size_bytes: int = DEFAULT_ATTRIBUTION_AUDIT_MAP_SIZE_BYTES,
    ) -> None:
        if isinstance(map_size_bytes, bool) or not isinstance(map_size_bytes, int):
            raise ValueError("attribution_audit_map_size_invalid")
        if map_size_bytes <= 0:
            raise ValueError("attribution_audit_map_size_invalid")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.env = lmdb.open(
            str(self.storage_dir.resolve()),
            create=True,
            subdir=True,
            max_dbs=2,
            map_size=map_size_bytes,
            lock=True,
        )
        self._attr_events_db = self.env.open_db(ATTR_EVENTS_DB_NAME)
        self._epoch_index_db = self.env.open_db(EPOCH_INDEX_DB_NAME)

    def write_epoch_events(self, epoch: int, events: list[dict[str, Any]]) -> None:
        normalized_epoch = _require_epoch(epoch)
        if not isinstance(events, list):
            raise ValueError("attribution_audit_events_invalid")
        normalized_events: list[dict[str, Any]] = []
        for event in events:
            if not isinstance(event, dict):
                raise ValueError("attribution_audit_event_invalid")
            normalized_events.append(dict(event))
        with self.env.begin(write=True) as txn:
            index_key = _epoch_index_key(normalized_epoch)
            if txn.get(index_key, db=self._epoch_index_db) is not None:
                raise ValueError("attribution_audit_epoch_already_written")
            ordinal_keys: list[str] = []
            for ordinal, event in enumerate(normalized_events):
                key = _event_key(normalized_epoch, ordinal)
                if txn.get(key, db=self._attr_events_db) is not None:
                    raise ValueError("attribution_audit_epoch_already_written")
                txn.put(key, _encode_json(event), db=self._attr_events_db)
                ordinal_keys.append(key.hex())
            txn.put(index_key, _encode_json(ordinal_keys), db=self._epoch_index_db)

    def read_epoch_events(self, epoch: int) -> list[dict[str, Any]]:
        normalized_epoch = _require_epoch(epoch)
        with self.env.begin() as txn:
            raw_keys = _decode_list(
                txn.get(_epoch_index_key(normalized_epoch), db=self._epoch_index_db),
            )
            events: list[dict[str, Any]] = []
            for raw_key in raw_keys:
                if not isinstance(raw_key, str):
                    raise ValueError("attribution_audit_epoch_index_invalid")
                value = txn.get(bytes.fromhex(raw_key), db=self._attr_events_db)
                if value is None:
                    raise ValueError("attribution_audit_event_missing")
                events.append(_decode_dict(value))
            return events

    def get_epoch_count(self, epoch: int) -> int:
        return len(self.read_epoch_events(epoch))

    def list_epochs(self) -> list[int]:
        """Return all written epoch numbers in ascending numeric order."""
        epochs: list[int] = []
        with self.env.begin(db=self._epoch_index_db) as txn:
            with txn.cursor() as cursor:
                for key, _value in cursor:
                    if not key.startswith(EPOCH_INDEX_KEY_PREFIX):
                        continue
                    epoch_bytes = key[len(EPOCH_INDEX_KEY_PREFIX) :]
                    if len(epoch_bytes) != 8:
                        raise ValueError("attribution_audit_epoch_index_key_invalid")
                    epochs.append(int.from_bytes(epoch_bytes, "big", signed=False))
        return sorted(epochs)


__all__ = [
    "ATTRIBUTION_AUDIT_LMDB_VERSION",
    "ATTR_EVENTS_DB_NAME",
    "AttributionAuditLmdbStore",
    "EPOCH_INDEX_DB_NAME",
]
