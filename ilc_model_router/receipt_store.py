# SPDX-License-Identifier: AGPL-3.0-only
"""Atomic LMDB persistence for local Model Router receipts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final, cast

import lmdb

from ilc_core.sidecars.execution_receipt import (
    DEFAULT_SIDECAR_EXECUTION_RECEIPT_MAP_SIZE_BYTES,
    MAX_SIDECAR_EXECUTION_RECEIPTS_PER_EPOCH,
    RECEIPTS_DB_NAME,
    TOKEN_INDEX_DB_NAME,
    SidecarExecutionReceipt,
    SidecarExecutionReceiptError,
)

from .receipt_schema import (
    RouterCompanionRecord,
    RouterReceipt,
    RouterReceiptError,
)

ROUTER_RECEIPT_STORE_VERSION: Final[str] = "model_router_receipt_store_phase_1612.v0.1"
RECEIPTS_DB: Final[bytes] = RECEIPTS_DB_NAME
TOKEN_INDEX_DB: Final[bytes] = TOKEN_INDEX_DB_NAME
COMPANION_DB: Final[bytes] = b"companion_meta"
NULLIFIERS_DB: Final[bytes] = b"nullifiers"
PENDING_NULLIFIER_VALUE: Final[bytes] = b"pending:model-router-receipt:v1"
MAX_ROUTER_RECEIPTS_PER_EPOCH: int = MAX_SIDECAR_EXECUTION_RECEIPTS_PER_EPOCH
MAX_ROUTER_COMPANION_BYTES: Final[int] = 16 * 1024
_RECEIPT_KEY_BYTES: Final[int] = 12
_HEX = frozenset("0123456789abcdef")


def open_router_receipt_env(
    storage_dir: str | Path,
    *,
    map_size_bytes: int = DEFAULT_SIDECAR_EXECUTION_RECEIPT_MAP_SIZE_BYTES,
) -> lmdb.Environment:
    """Open a router receipt LMDB environment with the required sub-dbs."""

    if isinstance(map_size_bytes, bool) or not isinstance(map_size_bytes, int) or map_size_bytes <= 0:
        raise RouterReceiptError("model_router_map_size_invalid")
    path = Path(storage_dir)
    path.mkdir(parents=True, exist_ok=True)
    env = lmdb.open(
        str(path.resolve()),
        create=True,
        lock=True,
        map_size=map_size_bytes,
        max_dbs=4,
        subdir=True,
    )
    _open_dbs(env)
    return env


def store_router_receipt(
    env: lmdb.Environment,
    receipt: RouterReceipt,
    nullifier: bytes,
) -> None:
    """Atomically store a router receipt, companion record, and nullifier."""

    _store_router_receipt_with_nullifier_state(
        env,
        receipt,
        nullifier,
        expected_nullifier_value=None,
    )


def reserve_router_nullifier(env: lmdb.Environment, nullifier: bytes) -> None:
    """Reserve a nullifier before provider dispatch."""

    clean_nullifier = _require_nullifier(nullifier)
    _receipts_db, _token_index_db, _companion_db, nullifiers_db = _open_dbs(env)
    with env.begin(write=True) as txn:
        if txn.get(clean_nullifier, db=nullifiers_db) is not None:
            raise RouterReceiptError("model_router_nullifier_collision")
        txn.put(clean_nullifier, PENDING_NULLIFIER_VALUE, db=nullifiers_db)


def finalize_reserved_router_receipt(
    env: lmdb.Environment,
    receipt: RouterReceipt,
    nullifier: bytes,
) -> None:
    """Atomically finalize a reserved nullifier with the full router receipt."""

    _store_router_receipt_with_nullifier_state(
        env,
        receipt,
        nullifier,
        expected_nullifier_value=PENDING_NULLIFIER_VALUE,
    )


def _store_router_receipt_with_nullifier_state(
    env: lmdb.Environment,
    receipt: RouterReceipt,
    nullifier: bytes,
    *,
    expected_nullifier_value: bytes | None,
) -> None:
    if not isinstance(receipt, RouterReceipt):
        raise RouterReceiptError("model_router_receipt_invalid")
    clean_nullifier = _require_nullifier(nullifier)
    receipts_db, token_index_db, companion_db, nullifiers_db = _open_dbs(env)
    core_receipt = receipt.to_core_receipt()
    encoded_core = _encode_core_receipt(core_receipt)
    encoded_companion = _encode_companion(receipt.companion)
    token_key = receipt.receipt_token.encode("ascii")
    with env.begin(write=True) as txn:
        current_nullifier_value = txn.get(clean_nullifier, db=nullifiers_db)
        if expected_nullifier_value is None and current_nullifier_value is not None:
            raise RouterReceiptError("model_router_nullifier_collision")
        if expected_nullifier_value is not None and current_nullifier_value != expected_nullifier_value:
            raise RouterReceiptError("model_router_nullifier_not_reserved")
        if txn.get(token_key, db=token_index_db) is not None:
            raise RouterReceiptError("model_router_receipt_token_duplicate")
        ordinal = _next_epoch_ordinal(txn, receipts_db, receipt.epoch)
        key = _receipt_key(receipt.epoch, ordinal)
        if txn.get(key, db=receipts_db) is not None:
            raise RouterReceiptError("model_router_receipt_key_duplicate")
        txn.put(key, encoded_core, db=receipts_db)
        txn.put(token_key, key, db=token_index_db)
        txn.put(token_key, encoded_companion, db=companion_db)
        txn.put(clean_nullifier, token_key, db=nullifiers_db)


def lookup_by_token(env: lmdb.Environment, receipt_token: str) -> RouterReceipt | None:
    """Look up a full RouterReceipt by receipt token."""

    token_key = _require_receipt_token(receipt_token).encode("ascii")
    receipts_db, token_index_db, companion_db, _nullifiers_db = _open_dbs(env)
    with env.begin() as txn:
        key = txn.get(token_key, db=token_index_db)
        if key is None:
            return None
        if len(key) != _RECEIPT_KEY_BYTES:
            raise RouterReceiptError("model_router_token_index_corrupted")
        core_raw = txn.get(key, db=receipts_db)
        if core_raw is None:
            raise RouterReceiptError("model_router_index_target_missing")
        companion_raw = txn.get(token_key, db=companion_db)
        if companion_raw is None:
            raise RouterReceiptError("model_router_companion_missing")
        core = _decode_core_receipt(core_raw)
        companion = _decode_companion(companion_raw)
    return RouterReceipt.from_core_and_companion(core, companion)


def list_router_receipts(env: lmdb.Environment, *, limit: int = 100) -> list[RouterReceipt]:
    """List router receipts in epoch/ordinal order."""

    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1 or limit > 1000:
        raise RouterReceiptError("model_router_list_limit_invalid")
    receipts_db, _token_index_db, companion_db, _nullifiers_db = _open_dbs(env)
    receipts: list[RouterReceipt] = []
    with env.begin() as txn:
        with txn.cursor(db=receipts_db) as cursor:
            for key, core_raw in cursor:
                if len(key) != _RECEIPT_KEY_BYTES:
                    raise RouterReceiptError("model_router_receipt_key_corrupted")
                core = _decode_core_receipt(core_raw)
                companion_raw = txn.get(core.receipt_token.encode("ascii"), db=companion_db)
                if companion_raw is None:
                    raise RouterReceiptError("model_router_companion_missing")
                companion = _decode_companion(companion_raw)
                receipts.append(RouterReceipt.from_core_and_companion(core, companion))
                if len(receipts) >= limit:
                    break
    return receipts


def check_nullifier(env: lmdb.Environment, nullifier: bytes) -> bool:
    """Return True if a nullifier is already present."""

    clean_nullifier = _require_nullifier(nullifier)
    _receipts_db, _token_index_db, _companion_db, nullifiers_db = _open_dbs(env)
    with env.begin() as txn:
        return txn.get(clean_nullifier, db=nullifiers_db) is not None


def _open_dbs(env: lmdb.Environment) -> tuple[Any, Any, Any, Any]:
    return (
        env.open_db(RECEIPTS_DB),
        env.open_db(TOKEN_INDEX_DB),
        env.open_db(COMPANION_DB),
        env.open_db(NULLIFIERS_DB),
    )


def _encode_core_receipt(receipt: SidecarExecutionReceipt) -> bytes:
    encoded = json.dumps(
        receipt.to_dict(),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return encoded


def _encode_companion(companion: RouterCompanionRecord) -> bytes:
    encoded = json.dumps(
        companion.to_dict(),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if len(encoded) > MAX_ROUTER_COMPANION_BYTES:
        raise RouterReceiptError("model_router_companion_too_large")
    return encoded


def _decode_core_receipt(payload: bytes) -> SidecarExecutionReceipt:
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RouterReceiptError("model_router_core_receipt_corrupted") from exc
    if not isinstance(decoded, dict):
        raise RouterReceiptError("model_router_core_receipt_payload_invalid")
    try:
        return SidecarExecutionReceipt.from_dict(cast(dict[str, Any], decoded))
    except SidecarExecutionReceiptError as exc:
        raise RouterReceiptError(str(exc)) from exc


def _decode_companion(payload: bytes) -> RouterCompanionRecord:
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RouterReceiptError("model_router_companion_corrupted") from exc
    if not isinstance(decoded, dict):
        raise RouterReceiptError("model_router_companion_payload_invalid")
    return RouterCompanionRecord.from_dict(cast(dict[str, Any], decoded))


def _next_epoch_ordinal(txn: Any, receipts_db: Any, epoch: int) -> int:
    prefix = _require_epoch(epoch).to_bytes(8, "big", signed=False)
    ordinal_count = 0
    with txn.cursor(db=receipts_db) as cursor:
        if cursor.set_range(prefix):
            for key, _value in cursor:
                if not key.startswith(prefix):
                    break
                if len(key) != _RECEIPT_KEY_BYTES:
                    raise RouterReceiptError("model_router_receipt_key_corrupted")
                ordinal_count += 1
    if ordinal_count >= MAX_ROUTER_RECEIPTS_PER_EPOCH:
        raise RouterReceiptError("model_router_epoch_cap_exceeded")
    return ordinal_count


def _receipt_key(epoch: int, ordinal: int) -> bytes:
    normalized_epoch = _require_epoch(epoch)
    if isinstance(ordinal, bool) or not isinstance(ordinal, int) or ordinal < 0:
        raise RouterReceiptError("model_router_receipt_ordinal_invalid")
    if ordinal > 0xFFFFFFFF:
        raise RouterReceiptError("model_router_receipt_ordinal_invalid")
    return (
        normalized_epoch.to_bytes(8, "big", signed=False)
        + ordinal.to_bytes(4, "big", signed=False)
    )


def _require_epoch(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RouterReceiptError("model_router_epoch_invalid")
    return value


def _require_nullifier(value: bytes) -> bytes:
    if type(value) is not bytes or len(value) != 32:
        raise RouterReceiptError("model_router_nullifier_invalid")
    return value


def _require_receipt_token(value: Any) -> str:
    if type(value) is not str or len(value) != 64:
        raise RouterReceiptError("model_router_receipt_token_invalid")
    if value.lower() != value or any(char not in _HEX for char in value):
        raise RouterReceiptError("model_router_receipt_token_invalid")
    return value


__all__ = [
    "COMPANION_DB",
    "MAX_ROUTER_COMPANION_BYTES",
    "MAX_ROUTER_RECEIPTS_PER_EPOCH",
    "NULLIFIERS_DB",
    "PENDING_NULLIFIER_VALUE",
    "RECEIPTS_DB",
    "ROUTER_RECEIPT_STORE_VERSION",
    "TOKEN_INDEX_DB",
    "check_nullifier",
    "finalize_reserved_router_receipt",
    "list_router_receipts",
    "lookup_by_token",
    "open_router_receipt_env",
    "reserve_router_nullifier",
    "store_router_receipt",
]
