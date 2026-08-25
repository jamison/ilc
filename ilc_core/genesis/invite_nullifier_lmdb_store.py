# SPDX-License-Identifier: AGPL-3.0-only
"""Durable LMDB invite-nullifier registry for Phase 1576r-Fix1.

The in-memory Phase 1576p registry remains valid for local tests and ephemeral
flows. This module provides the pre-RC restart-durable surface required before
the 1591 substrate soak.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import lmdb

from ilc_core.genesis.invite_nullifier_registry import (
    _MAX_REGISTRY_SIZE,
    InviteNullifierError,
    InviteNullifierRegistry,
    _require_sha256_hex,
)


INVITE_NULLIFIER_LMDB_STORE_VERSION = "invite_nullifier_lmdb_store_1576r_fix1.v0.1"
DEFAULT_INVITE_NULLIFIER_MAP_SIZE_BYTES = 64 * 1024 * 1024

_NULLIFIERS_DB_NAME = b"nullifiers"
_META_DB_NAME = b"meta"
_SCHEMA_VERSION_KEY = b"schema_version"
_NULLIFIER_VALUE = json.dumps(
    {"schema_version": INVITE_NULLIFIER_LMDB_STORE_VERSION, "seen": True},
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")


class InviteNullifierLmdbRegistry(InviteNullifierRegistry):
    """Restart-durable invite nullifier registry backed by LMDB.

    The public method contract intentionally matches `InviteNullifierRegistry`:
    duplicate `register_nullifier()` calls are idempotent, `register_if_new()`
    returns False for duplicates, and all malformed nullifiers fail closed with
    `InviteNullifierError`.
    """

    def __init__(
        self,
        storage_dir: str | Path,
        *,
        map_size_bytes: int = DEFAULT_INVITE_NULLIFIER_MAP_SIZE_BYTES,
        max_registry_size: int = _MAX_REGISTRY_SIZE,
    ) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._MAX_REGISTRY_SIZE = _require_positive_int(
            max_registry_size,
            "invite_nullifier_lmdb_max_registry_size_invalid",
        )
        normalized_map_size = _require_positive_int(
            map_size_bytes,
            "invite_nullifier_lmdb_map_size_invalid",
        )
        self.env = lmdb.open(
            str(self.storage_dir),
            create=True,
            subdir=True,
            max_dbs=2,
            map_size=normalized_map_size,
            lock=True,
        )
        self._nullifiers_db = self.env.open_db(_NULLIFIERS_DB_NAME)
        self._meta_db = self.env.open_db(_META_DB_NAME)
        with self.env.begin(write=True) as txn:
            existing = txn.get(_SCHEMA_VERSION_KEY, db=self._meta_db)
            encoded_version = INVITE_NULLIFIER_LMDB_STORE_VERSION.encode("utf-8")
            if existing is None:
                txn.put(_SCHEMA_VERSION_KEY, encoded_version, db=self._meta_db)
            elif existing != encoded_version:
                raise InviteNullifierError("invite_nullifier_lmdb_schema_version_mismatch")

    def close(self) -> None:
        self.env.close()

    def __enter__(self) -> "InviteNullifierLmdbRegistry":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def register_nullifier(self, nullifier_hex: str) -> None:
        _require_sha256_hex(nullifier_hex, "invite_nullifier_invalid")
        key = _nullifier_key(nullifier_hex)
        with self.env.begin(write=True, db=self._nullifiers_db) as txn:
            if txn.get(key) is not None:
                return
            if txn.stat()["entries"] >= self._MAX_REGISTRY_SIZE:
                raise InviteNullifierError("invite_nullifier_registry_full")
            txn.put(key, _NULLIFIER_VALUE)

    def register_if_new(self, nullifier_hex: str) -> bool:
        _require_sha256_hex(nullifier_hex, "invite_nullifier_invalid")
        key = _nullifier_key(nullifier_hex)
        with self.env.begin(write=True, db=self._nullifiers_db) as txn:
            if txn.get(key) is not None:
                return False
            if txn.stat()["entries"] >= self._MAX_REGISTRY_SIZE:
                raise InviteNullifierError("invite_nullifier_registry_full")
            txn.put(key, _NULLIFIER_VALUE)
            return True

    def discard_nullifier(self, nullifier_hex: str) -> None:
        _require_sha256_hex(nullifier_hex, "invite_nullifier_invalid")
        with self.env.begin(write=True, db=self._nullifiers_db) as txn:
            txn.delete(_nullifier_key(nullifier_hex))

    def is_known(self, nullifier_hex: str) -> bool:
        _require_sha256_hex(nullifier_hex, "invite_nullifier_invalid")
        with self.env.begin(db=self._nullifiers_db) as txn:
            payload = txn.get(_nullifier_key(nullifier_hex))
        if payload is None:
            return False
        _validate_nullifier_value(payload)
        return True

    def __len__(self) -> int:
        with self.env.begin(db=self._nullifiers_db) as txn:
            return int(txn.stat()["entries"])


def _nullifier_key(nullifier_hex: str) -> bytes:
    return nullifier_hex.encode("ascii")


def _validate_nullifier_value(payload: bytes) -> None:
    try:
        decoded: Any = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InviteNullifierError("invite_nullifier_lmdb_payload_invalid") from exc
    if decoded != {
        "schema_version": INVITE_NULLIFIER_LMDB_STORE_VERSION,
        "seen": True,
    }:
        raise InviteNullifierError("invite_nullifier_lmdb_payload_invalid")


def _require_positive_int(value: object, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise InviteNullifierError(token)
    return value


__all__ = [
    "DEFAULT_INVITE_NULLIFIER_MAP_SIZE_BYTES",
    "INVITE_NULLIFIER_LMDB_STORE_VERSION",
    "InviteNullifierLmdbRegistry",
]
