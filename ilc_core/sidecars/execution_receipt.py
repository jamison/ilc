# SPDX-License-Identifier: AGPL-3.0-only
"""Local sidecar execution receipt schema and append-only LMDB store."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, cast

import lmdb


SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION = "sidecar_execution_receipt_GAP_HARNESS_SIDECAR_05.v0.1"
SIDECAR_EXECUTION_RECEIPT_TOKEN = "sidecar_execution_receipt_schema_committed_GAP_HARNESS_SIDECAR_05"
DEFAULT_SIDECAR_EXECUTION_RECEIPT_MAP_SIZE_BYTES = 64 * 1024 * 1024
MAX_SIDECAR_EXECUTION_RECEIPT_BYTES = 64 * 1024
MAX_SIDECAR_EXECUTION_RECEIPTS_PER_EPOCH = 10_000
RECEIPTS_DB_NAME = b"receipts"
TOKEN_INDEX_DB_NAME = b"token_index"

ACTION_TYPES = frozenset(
    {
        "attribution_batch",
        "ecu_transfer",
        "graph_submit",
        "ilc_transfer",
        "query",
        "unknown",
    }
)
STATUSES = frozenset({"failure", "partial", "success"})
_HEX = frozenset("0123456789abcdef")
_RECEIPT_KEY_BYTES = 12
_RECEIPT_PAYLOAD_KEYS = frozenset(
    {
        "action_type",
        "agent_id_hex",
        "epoch",
        "error_token",
        "inputs_hash",
        "outputs_hash",
        "receipt_token",
        "schema_version",
        "status",
        "tool_id",
    }
)


class SidecarExecutionReceiptError(ValueError):
    """Stable execution receipt validation/store error."""


@dataclass(frozen=True, init=False)
class SidecarExecutionReceipt:
    """Local record of a completed sidecar tool action."""

    receipt_token: str
    tool_id: str
    action_type: str
    epoch: int
    agent_id_hex: str
    inputs_hash: str
    outputs_hash: str
    status: str
    error_token: str

    def __init__(
        self,
        *,
        tool_id: str,
        action_type: str,
        epoch: int,
        agent_id_hex: str,
        inputs_hash: str,
        outputs_hash: str,
        status: str,
        error_token: str = "",
    ) -> None:
        normalized = _receipt_payload_without_token(
            tool_id=tool_id,
            action_type=action_type,
            epoch=epoch,
            agent_id_hex=agent_id_hex,
            inputs_hash=inputs_hash,
            outputs_hash=outputs_hash,
            status=status,
            error_token=error_token,
        )
        receipt_token = _sha256_canonical(normalized)
        object.__setattr__(self, "receipt_token", receipt_token)
        for key, value in normalized.items():
            object.__setattr__(self, key, value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_type": self.action_type,
            "agent_id_hex": self.agent_id_hex,
            "epoch": self.epoch,
            "error_token": self.error_token,
            "inputs_hash": self.inputs_hash,
            "outputs_hash": self.outputs_hash,
            "receipt_token": self.receipt_token,
            "schema_version": SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION,
            "status": self.status,
            "tool_id": self.tool_id,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "SidecarExecutionReceipt":
        if not isinstance(payload, Mapping):
            raise SidecarExecutionReceiptError("sidecar_execution_receipt_payload_invalid")
        if set(payload) != _RECEIPT_PAYLOAD_KEYS:
            raise SidecarExecutionReceiptError("sidecar_execution_receipt_field_set_invalid")
        schema_version = payload.get("schema_version")
        if schema_version != SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION:
            raise SidecarExecutionReceiptError("sidecar_execution_receipt_schema_version_invalid")
        receipt = cls(
            tool_id=_required_str(payload, "tool_id"),
            action_type=_required_str(payload, "action_type"),
            epoch=_required_int(payload, "epoch"),
            agent_id_hex=_required_str(payload, "agent_id_hex"),
            inputs_hash=_required_str(payload, "inputs_hash"),
            outputs_hash=_required_str(payload, "outputs_hash"),
            status=_required_str(payload, "status"),
            error_token=_required_str(payload, "error_token"),
        )
        if payload.get("receipt_token") != receipt.receipt_token:
            raise SidecarExecutionReceiptError("sidecar_execution_receipt_token_mismatch")
        return receipt


class SidecarExecutionReceiptStore:
    """Append-only local LMDB store for sidecar execution receipts."""

    def __init__(
        self,
        storage_dir: str | Path,
        *,
        map_size_bytes: int = DEFAULT_SIDECAR_EXECUTION_RECEIPT_MAP_SIZE_BYTES,
    ) -> None:
        if isinstance(map_size_bytes, bool) or not isinstance(map_size_bytes, int):
            raise SidecarExecutionReceiptError("sidecar_execution_receipt_map_size_invalid")
        if map_size_bytes <= 0:
            raise SidecarExecutionReceiptError("sidecar_execution_receipt_map_size_invalid")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.env = lmdb.open(
            str(self.storage_dir.resolve()),
            create=True,
            lock=True,
            map_size=map_size_bytes,
            max_dbs=2,
            subdir=True,
        )
        self._receipts_db = self.env.open_db(RECEIPTS_DB_NAME)
        self._token_index_db = self.env.open_db(TOKEN_INDEX_DB_NAME)

    def append_receipt(self, receipt: SidecarExecutionReceipt) -> None:
        if not isinstance(receipt, SidecarExecutionReceipt):
            raise SidecarExecutionReceiptError("sidecar_execution_receipt_invalid")
        encoded_receipt = _encode_receipt(receipt)
        with self.env.begin(write=True) as txn:
            token_key = receipt.receipt_token.encode("utf-8")
            if txn.get(token_key, db=self._token_index_db) is not None:
                raise SidecarExecutionReceiptError("sidecar_execution_receipt_token_duplicate")
            ordinal = _next_epoch_ordinal(txn, self._receipts_db, receipt.epoch)
            key = _receipt_key(receipt.epoch, ordinal)
            if txn.get(key, db=self._receipts_db) is not None:
                raise SidecarExecutionReceiptError("sidecar_execution_receipt_key_duplicate")
            txn.put(key, encoded_receipt, db=self._receipts_db)
            txn.put(token_key, key, db=self._token_index_db)

    def read_receipts_for_epoch(self, epoch: int) -> list[SidecarExecutionReceipt]:
        normalized_epoch = _require_epoch(epoch)
        prefix = normalized_epoch.to_bytes(8, "big", signed=False)
        receipts: list[SidecarExecutionReceipt] = []
        with self.env.begin(db=self._receipts_db) as txn:
            with txn.cursor() as cursor:
                if not cursor.set_range(prefix):
                    return []
                for key, value in cursor:
                    if not key.startswith(prefix):
                        break
                    receipts.append(_decode_receipt(value))
        return receipts

    def lookup_by_token(self, token: str) -> SidecarExecutionReceipt | None:
        _require_hex(token, "sidecar_execution_receipt_token_invalid", length=64)
        with self.env.begin() as txn:
            key = txn.get(token.encode("utf-8"), db=self._token_index_db)
            if key is None:
                return None
            if len(key) != _RECEIPT_KEY_BYTES:
                raise SidecarExecutionReceiptError("sidecar_execution_receipt_token_index_corrupted")
            value = txn.get(key, db=self._receipts_db)
            if value is None:
                raise SidecarExecutionReceiptError("sidecar_execution_receipt_index_target_missing")
            return _decode_receipt(value)


def hash_receipt_component(payload: Mapping[str, Any]) -> str:
    """Return the SHA-256 hash of a canonical JSON receipt component."""

    if not isinstance(payload, Mapping):
        raise SidecarExecutionReceiptError("sidecar_execution_receipt_component_invalid")
    return _sha256_canonical(payload)


def _receipt_payload_without_token(
    *,
    tool_id: str,
    action_type: str,
    epoch: int,
    agent_id_hex: str,
    inputs_hash: str,
    outputs_hash: str,
    status: str,
    error_token: str,
) -> dict[str, Any]:
    normalized_tool_id = _require_text(tool_id, "sidecar_execution_receipt_tool_id_invalid", max_chars=128)
    normalized_action_type = _require_choice(
        action_type,
        ACTION_TYPES,
        "sidecar_execution_receipt_action_type_invalid",
    )
    normalized_epoch = _require_epoch(epoch)
    normalized_agent_id_hex = _require_hex(
        agent_id_hex,
        "sidecar_execution_receipt_agent_id_invalid",
        length=96,
    )
    normalized_inputs_hash = _require_hex(
        inputs_hash,
        "sidecar_execution_receipt_inputs_hash_invalid",
        length=64,
    )
    normalized_outputs_hash = _require_hex(
        outputs_hash,
        "sidecar_execution_receipt_outputs_hash_invalid",
        length=64,
    )
    normalized_status = _require_choice(
        status,
        STATUSES,
        "sidecar_execution_receipt_status_invalid",
    )
    normalized_error_token = _normalize_error_token(error_token, normalized_status)
    return {
        "action_type": normalized_action_type,
        "agent_id_hex": normalized_agent_id_hex,
        "epoch": normalized_epoch,
        "error_token": normalized_error_token,
        "inputs_hash": normalized_inputs_hash,
        "outputs_hash": normalized_outputs_hash,
        "status": normalized_status,
        "tool_id": normalized_tool_id,
    }


def _normalize_error_token(error_token: str, status: str) -> str:
    normalized_error_token = _require_text(
        error_token,
        "sidecar_execution_receipt_error_token_invalid",
        allow_empty=True,
        max_chars=128,
    )
    if status in {"failure", "partial"} and not normalized_error_token:
        raise SidecarExecutionReceiptError("sidecar_execution_receipt_failure_error_token_required")
    if status == "success" and normalized_error_token:
        raise SidecarExecutionReceiptError("sidecar_execution_receipt_error_token_without_failure")
    return normalized_error_token


def _receipt_key(epoch: int, ordinal: int) -> bytes:
    normalized_epoch = _require_epoch(epoch)
    if isinstance(ordinal, bool) or not isinstance(ordinal, int) or ordinal < 0:
        raise SidecarExecutionReceiptError("sidecar_execution_receipt_ordinal_invalid")
    if ordinal > 0xFFFFFFFF:
        raise SidecarExecutionReceiptError("sidecar_execution_receipt_ordinal_invalid")
    return (
        normalized_epoch.to_bytes(8, "big", signed=False)
        + ordinal.to_bytes(4, "big", signed=False)
    )


def _next_epoch_ordinal(txn: Any, receipts_db: Any, epoch: int) -> int:
    prefix = _require_epoch(epoch).to_bytes(8, "big", signed=False)
    ordinal_count = 0
    with txn.cursor(db=receipts_db) as cursor:
        if cursor.set_range(prefix):
            for key, _value in cursor:
                if not key.startswith(prefix):
                    break
                if len(key) != _RECEIPT_KEY_BYTES:
                    raise SidecarExecutionReceiptError("sidecar_execution_receipt_key_corrupted")
                ordinal_count += 1
    if ordinal_count >= MAX_SIDECAR_EXECUTION_RECEIPTS_PER_EPOCH:
        raise SidecarExecutionReceiptError("sidecar_execution_receipt_epoch_full")
    return ordinal_count


def _encode_receipt(receipt: SidecarExecutionReceipt) -> bytes:
    encoded = json.dumps(
        receipt.to_dict(),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if len(encoded) > MAX_SIDECAR_EXECUTION_RECEIPT_BYTES:
        raise SidecarExecutionReceiptError("sidecar_execution_receipt_too_large")
    return encoded


def _decode_receipt(payload: bytes) -> SidecarExecutionReceipt:
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SidecarExecutionReceiptError("sidecar_execution_receipt_corrupted") from exc
    if not isinstance(decoded, dict):
        raise SidecarExecutionReceiptError("sidecar_execution_receipt_payload_invalid")
    return SidecarExecutionReceipt.from_dict(cast(dict[str, Any], decoded))


def _sha256_canonical(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _required_str(payload: Mapping[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if type(value) is not str:
        raise SidecarExecutionReceiptError(f"sidecar_execution_receipt_{field_name}_invalid")
    return value


def _required_int(payload: Mapping[str, Any], field_name: str) -> int:
    value = payload.get(field_name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise SidecarExecutionReceiptError(f"sidecar_execution_receipt_{field_name}_invalid")
    return value


def _require_epoch(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SidecarExecutionReceiptError("sidecar_execution_receipt_epoch_invalid")
    return value


def _require_text(
    value: Any,
    token: str,
    *,
    allow_empty: bool = False,
    max_chars: int,
) -> str:
    if type(value) is not str:
        raise SidecarExecutionReceiptError(token)
    if not allow_empty and not value:
        raise SidecarExecutionReceiptError(token)
    if len(value) > max_chars:
        raise SidecarExecutionReceiptError(token)
    return value


def _require_choice(value: Any, choices: frozenset[str], token: str) -> str:
    if type(value) is not str or value not in choices:
        raise SidecarExecutionReceiptError(token)
    return value


def _require_hex(value: Any, token: str, *, length: int) -> str:
    if type(value) is not str or len(value) != length:
        raise SidecarExecutionReceiptError(token)
    if value.lower() != value or any(char not in _HEX for char in value):
        raise SidecarExecutionReceiptError(token)
    return value


__all__ = [
    "ACTION_TYPES",
    "DEFAULT_SIDECAR_EXECUTION_RECEIPT_MAP_SIZE_BYTES",
    "MAX_SIDECAR_EXECUTION_RECEIPT_BYTES",
    "MAX_SIDECAR_EXECUTION_RECEIPTS_PER_EPOCH",
    "RECEIPTS_DB_NAME",
    "SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION",
    "SIDECAR_EXECUTION_RECEIPT_TOKEN",
    "STATUSES",
    "SidecarExecutionReceipt",
    "SidecarExecutionReceiptError",
    "SidecarExecutionReceiptStore",
    "TOKEN_INDEX_DB_NAME",
    "hash_receipt_component",
]
