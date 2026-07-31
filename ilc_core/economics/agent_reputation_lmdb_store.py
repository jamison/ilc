# SPDX-License-Identifier: AGPL-3.0-only
"""GAP-REPUTATION-06 durable AgentReputationRecord LMDB store.

The store is intentionally standalone and default-off for production use. It
persists already-derived canonical reputation records by epoch without wiring
them into validator admission, wallet claimability, settlement, or public RC.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Sequence, cast

import lmdb

from ilc_core.economics.agent_reputation_extractor import (
    AgentReputationRecord,
    compute_agent_reputation_root,
)


AGENT_REPUTATION_LMDB_STORE_VERSION = "agent_reputation_lmdb_store_GAP_REPUTATION_06.v0.1"
CDL_106_DEPENDENCY = "cdl_106_agent_reputation_record_opened_GAP_REPUTATION_01"
PRODUCTION_REPUTATION_STORE_NOT_ACTIVATED_TOKEN = (
    "production_reputation_store_not_activated_GAP_REPUTATION_06"
)
DEFAULT_REPUTATION_STORE_MAP_SIZE_BYTES = 512 * 1024 * 1024

_RECORDS_DB_NAME = b"records"
_ROOTS_DB_NAME = b"roots"
_RECORD_KEY_PREFIX = b"rep_records:"
_ROOT_KEY_PREFIX = b"rep_root:"
_MAX_U64 = (1 << 64) - 1


def require_production_reputation_store_activation() -> None:
    raise ValueError(PRODUCTION_REPUTATION_STORE_NOT_ACTIVATED_TOKEN)


def _require_epoch(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("reputation_store_epoch_must_be_non_negative_int")
    if value > _MAX_U64:
        raise ValueError("reputation_store_epoch_out_of_u64_range")
    return value


def _epoch_key(prefix: bytes, epoch: int) -> bytes:
    return prefix + epoch.to_bytes(8, "big", signed=False)


def _validate_json_safe(value: object) -> None:
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return
    if isinstance(value, float):
        raise ValueError("reputation_store_float_value_rejected")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("reputation_store_non_finite_decimal_rejected")
        raise ValueError("reputation_store_decimal_value_must_be_canonical_string")
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            _validate_json_safe(item)
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("reputation_store_mapping_keys_must_be_strings")
            _validate_json_safe(item)
        return
    raise ValueError("reputation_store_value_not_json_safe")


def _encode_json(payload: object) -> bytes:
    _validate_json_safe(payload)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )


def _decode_records(payload: bytes | None) -> list[dict[str, Any]] | None:
    if payload is None:
        return None
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError("reputation_store_records_payload_invalid")
    return cast(list[dict[str, Any]], value)


class AgentReputationLmdbStore:
    """Epoch-keyed LMDB persistence for AgentReputationRecord canonical records."""

    def __init__(self, storage_dir: str | Path):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.env = lmdb.open(
            str(self.storage_dir),
            create=True,
            subdir=True,
            max_dbs=2,
            map_size=DEFAULT_REPUTATION_STORE_MAP_SIZE_BYTES,
            lock=True,
        )
        self._records_db = self.env.open_db(_RECORDS_DB_NAME)
        self._roots_db = self.env.open_db(_ROOTS_DB_NAME)

    def close(self) -> None:
        self.env.close()

    def __enter__(self) -> "AgentReputationLmdbStore":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def write_epoch_records(
        self,
        epoch: int,
        records: Sequence[AgentReputationRecord],
    ) -> str:
        normalized_epoch = _require_epoch(epoch)
        if not records:
            raise ValueError("reputation_store_empty_records_rejected")
        for record in records:
            if not isinstance(record, AgentReputationRecord):
                raise ValueError("reputation_store_record_type_invalid")
            if record.epoch != normalized_epoch:
                raise ValueError("reputation_store_epoch_mismatch_rejected")

        root_hex = compute_agent_reputation_root(records)
        canonical_records = sorted(
            [record.to_canonical_record() for record in records],
            key=lambda item: item["agent_id"],
        )
        encoded_records = _encode_json(canonical_records)
        encoded_root = root_hex.encode("utf-8")
        records_key = _epoch_key(_RECORD_KEY_PREFIX, normalized_epoch)
        root_key = _epoch_key(_ROOT_KEY_PREFIX, normalized_epoch)

        with self.env.begin(write=True) as txn:
            if txn.get(records_key, db=self._records_db) is not None:
                raise ValueError("reputation_store_epoch_already_written")
            if txn.get(root_key, db=self._roots_db) is not None:
                raise ValueError("reputation_store_epoch_already_written")
            txn.put(records_key, encoded_records, db=self._records_db)
            txn.put(root_key, encoded_root, db=self._roots_db)
        return root_hex

    def read_epoch_records(self, epoch: int) -> tuple[list[dict[str, Any]], str]:
        normalized_epoch = _require_epoch(epoch)
        with self.env.begin() as txn:
            records_payload = txn.get(
                _epoch_key(_RECORD_KEY_PREFIX, normalized_epoch),
                db=self._records_db,
            )
            root_payload = txn.get(
                _epoch_key(_ROOT_KEY_PREFIX, normalized_epoch),
                db=self._roots_db,
            )
        if records_payload is None or root_payload is None:
            raise ValueError("reputation_store_epoch_not_found")
        return _decode_records(records_payload) or [], root_payload.decode("utf-8")

    def get_committed_root(self, epoch: int) -> str:
        normalized_epoch = _require_epoch(epoch)
        with self.env.begin(db=self._roots_db) as txn:
            root_payload = txn.get(_epoch_key(_ROOT_KEY_PREFIX, normalized_epoch))
        if root_payload is None:
            raise ValueError("reputation_store_epoch_not_found")
        return root_payload.decode("utf-8")


__all__ = [
    "AGENT_REPUTATION_LMDB_STORE_VERSION",
    "CDL_106_DEPENDENCY",
    "DEFAULT_REPUTATION_STORE_MAP_SIZE_BYTES",
    "PRODUCTION_REPUTATION_STORE_NOT_ACTIVATED_TOKEN",
    "AgentReputationLmdbStore",
    "require_production_reputation_store_activation",
]
