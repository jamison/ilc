# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import lmdb

from ilc_core.ledger.exact_numeric import normalize_json_scalars


LMDB_PUBLIC_RUNTIME_VERSION = "lmdb_public_runtime_v0.1"
DEFAULT_MAP_SIZE_BYTES = 256 * 1024 * 1024
DEFAULT_MAX_NAMED_DBS = 16
MAX_PUBLIC_RECEIPT_INDEX_IDS = 10_000
_ENV_CACHE: dict[str, tuple[lmdb.Environment, int, int, int]] = {}
_ENV_CACHE_LOCK = threading.Lock()


def _encode_key(value: str) -> bytes:
    return value.encode("utf-8")


def _encode_json(payload: Any) -> bytes:
    return json.dumps(
        normalize_json_scalars(payload),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _decode_json(payload: bytes | None) -> Any:
    if payload is None:
        return None
    return json.loads(payload.decode("utf-8"))


def _compound_index_key(*parts: str) -> str:
    return json.dumps(list(parts), sort_keys=False, separators=(",", ":"), allow_nan=False)


class _LmdbRuntimeBase:
    def __init__(
        self,
        root: Path | str,
        *,
        db_names: tuple[bytes, ...],
        map_size: int = DEFAULT_MAP_SIZE_BYTES,
    ) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._root_key = str(self.root.resolve())
        with _ENV_CACHE_LOCK:
            cached = _ENV_CACHE.get(self._root_key)
            requested_max_dbs = max(DEFAULT_MAX_NAMED_DBS, len(db_names))
            if cached is None:
                self.env = lmdb.open(
                    self._root_key,
                    create=True,
                    subdir=True,
                    max_dbs=requested_max_dbs,
                    map_size=map_size,
                    lock=True,
                )
                _ENV_CACHE[self._root_key] = (self.env, 1, map_size, requested_max_dbs)
            else:
                self.env, refcount, cached_map_size, cached_max_dbs = cached
                if map_size > cached_map_size:
                    raise ValueError("lmdb_runtime_cached_env_map_size_too_small")
                if requested_max_dbs > cached_max_dbs:
                    raise ValueError("lmdb_runtime_cached_env_max_dbs_too_small")
                _ENV_CACHE[self._root_key] = (
                    self.env,
                    refcount + 1,
                    cached_map_size,
                    cached_max_dbs,
                )
            self._dbs = {name: self.env.open_db(name) for name in db_names}
        self._closed = False

    def _put_json(self, db_name: bytes, key: str, payload: Any) -> None:
        with self.env.begin(write=True, db=self._dbs[db_name]) as txn:
            txn.put(_encode_key(key), _encode_json(payload))

    def _get_json(self, db_name: bytes, key: str) -> Any:
        with self.env.begin(db=self._dbs[db_name]) as txn:
            return _decode_json(txn.get(_encode_key(key)))

    def _iter_json(self, db_name: bytes) -> list[Any]:
        rows: list[Any] = []
        with self.env.begin(db=self._dbs[db_name]) as txn:
            cursor = txn.cursor(db=self._dbs[db_name])
            for _, value in cursor:
                rows.append(_decode_json(value))
        return rows

    def _delete(self, db_name: bytes, key: str) -> None:
        with self.env.begin(write=True, db=self._dbs[db_name]) as txn:
            txn.delete(_encode_key(key))

    def close(self) -> None:
        with _ENV_CACHE_LOCK:
            if self._closed:
                return
            cached = _ENV_CACHE.get(self._root_key)
            if cached is None:
                self.env.close()
            else:
                env, refcount, map_size, max_dbs = cached
                if refcount <= 1:
                    env.close()
                    _ENV_CACHE.pop(self._root_key, None)
                else:
                    _ENV_CACHE[self._root_key] = (env, refcount - 1, map_size, max_dbs)
            self._closed = True


@dataclass(frozen=True)
class WalletBatchRow:
    wallet: dict[str, Any]
    history: dict[str, Any]


class WalletBatchTransaction:
    """Public atomic wallet/history transaction facade for lifecycle writers."""

    def __init__(self, txn: lmdb.Transaction, wallets_db: object, history_db: object) -> None:
        self._txn = txn
        self._wallets_db = wallets_db
        self._history_db = history_db

    def iter_wallet_rows(self) -> Iterator[tuple[str, dict[str, Any]]]:
        cursor = self._txn.cursor(db=self._wallets_db)
        for key, value in cursor:
            payload = _decode_json(value)
            if isinstance(payload, dict):
                yield key.decode("utf-8"), payload

    def get_wallet_pair(self, agent_id: str) -> WalletBatchRow:
        wallet = _decode_json(self._txn.get(_encode_key(agent_id), db=self._wallets_db))
        history = _decode_json(self._txn.get(_encode_key(agent_id), db=self._history_db))
        return WalletBatchRow(
            wallet=wallet if isinstance(wallet, dict) else {},
            history=history if isinstance(history, dict) else {},
        )

    def put_wallet_pair(
        self,
        agent_id: str,
        *,
        wallet_payload: dict[str, Any],
        history_payload: dict[str, Any],
    ) -> None:
        self._txn.put(_encode_key(agent_id), _encode_json(wallet_payload), db=self._wallets_db)
        self._txn.put(_encode_key(agent_id), _encode_json(history_payload), db=self._history_db)


class LmdbGraphStore(_LmdbRuntimeBase):
    def __init__(self, root: Path | str, *, map_size: int = DEFAULT_MAP_SIZE_BYTES) -> None:
        super().__init__(root, db_names=(b"nodes", b"links", b"meta"), map_size=map_size)

    def put_node(self, node_id: str, payload: dict[str, Any]) -> None:
        self._put_json(b"nodes", node_id, payload)

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        payload = self._get_json(b"nodes", node_id)
        return payload if isinstance(payload, dict) else None

    def iter_nodes(self) -> list[dict[str, Any]]:
        rows = [row for row in self._iter_json(b"nodes") if isinstance(row, dict)]
        return sorted(rows, key=lambda row: str(row.get("id", "")))

    def put_link(self, link_id: str, payload: dict[str, Any]) -> None:
        self._put_json(b"links", link_id, payload)

    def get_link(self, link_id: str) -> dict[str, Any] | None:
        payload = self._get_json(b"links", link_id)
        return payload if isinstance(payload, dict) else None

    def iter_links(self) -> list[dict[str, Any]]:
        rows = [row for row in self._iter_json(b"links") if isinstance(row, dict)]
        return sorted(
            rows,
            key=lambda row: (
                str(row.get("source_id", "")),
                str(row.get("target_id", "")),
                str(row.get("id", "")),
            ),
        )

    def put_quorum_record(self, payload: dict[str, Any]) -> None:
        self._put_json(b"meta", "quorum_record", payload)

    def get_quorum_record(self) -> dict[str, Any] | None:
        payload = self._get_json(b"meta", "quorum_record")
        return payload if isinstance(payload, dict) else None

    def delete_quorum_record(self) -> None:
        self._delete(b"meta", "quorum_record")


class LmdbWalletStore(_LmdbRuntimeBase):
    def __init__(self, root: Path | str, *, map_size: int = DEFAULT_MAP_SIZE_BYTES) -> None:
        super().__init__(
            root,
            db_names=(b"wallets", b"wallet_history", b"epoch_commit_markers"),
            map_size=map_size,
        )

    def put_wallet(self, agent_id: str, payload: dict[str, Any]) -> None:
        self._put_json(b"wallets", agent_id, payload)

    def get_wallet(self, agent_id: str) -> dict[str, Any] | None:
        payload = self._get_json(b"wallets", agent_id)
        return payload if isinstance(payload, dict) else None

    def iter_wallets(self) -> dict[str, dict[str, Any]]:
        rows: dict[str, dict[str, Any]] = {}
        with self.env.begin(db=self._dbs[b"wallets"]) as txn:
            cursor = txn.cursor(db=self._dbs[b"wallets"])
            for key, value in cursor:
                payload = _decode_json(value)
                if isinstance(payload, dict):
                    rows[key.decode("utf-8")] = payload
        return dict(sorted(rows.items()))

    @contextmanager
    def wallet_batch_transaction(self) -> Iterator[WalletBatchTransaction]:
        with self.env.begin(write=True) as txn:
            yield WalletBatchTransaction(
                txn=txn,
                wallets_db=self._dbs[b"wallets"],
                history_db=self._dbs[b"wallet_history"],
            )

    def put_wallet_history(self, agent_id: str, payload: dict[str, Any]) -> None:
        self._put_json(b"wallet_history", agent_id, payload)

    def put_wallet_and_history(
        self,
        agent_id: str,
        wallet_payload: dict[str, Any],
        history_payload: dict[str, Any],
    ) -> None:
        with self.env.begin(write=True) as txn:
            txn.put(
                _encode_key(agent_id),
                _encode_json(wallet_payload),
                db=self._dbs[b"wallets"],
            )
            txn.put(
                _encode_key(agent_id),
                _encode_json(history_payload),
                db=self._dbs[b"wallet_history"],
            )

    def get_wallet_history(self, agent_id: str) -> dict[str, Any] | None:
        payload = self._get_json(b"wallet_history", agent_id)
        return payload if isinstance(payload, dict) else None

    def delete_wallet_history(self, agent_id: str) -> None:
        self._delete(b"wallet_history", agent_id)

    def put_epoch_commit_marker(self, epoch_id: str, payload: dict[str, Any]) -> None:
        self._put_json(b"epoch_commit_markers", epoch_id, payload)

    def get_epoch_commit_marker(self, epoch_id: str) -> dict[str, Any] | None:
        payload = self._get_json(b"epoch_commit_markers", epoch_id)
        return payload if isinstance(payload, dict) else None


class LmdbPublicReceiptStore(_LmdbRuntimeBase):
    def __init__(self, root: Path | str, *, map_size: int = DEFAULT_MAP_SIZE_BYTES) -> None:
        super().__init__(
            root,
            db_names=(b"public_receipts", b"receipts_by_signer", b"receipts_by_kind_epoch"),
            map_size=map_size,
        )

    def put_receipt(self, receipt_id: str, payload: dict[str, Any]) -> None:
        self._put_json(b"public_receipts", receipt_id, payload)
        signer_agent_id = payload.get("signer_agent_id")
        if isinstance(signer_agent_id, str) and signer_agent_id:
            self._append_index_id(
                db_name=b"receipts_by_signer",
                key=signer_agent_id,
                receipt_id=receipt_id,
            )
        artifact_kind = payload.get("artifact_kind")
        epoch_id = payload.get("epoch_id")
        if (
            isinstance(artifact_kind, str)
            and artifact_kind
            and isinstance(epoch_id, str)
            and epoch_id
        ):
            self._append_index_id(
                db_name=b"receipts_by_kind_epoch",
                key=_compound_index_key(artifact_kind, epoch_id),
                receipt_id=receipt_id,
            )

    def get_receipt(self, receipt_id: str) -> dict[str, Any] | None:
        payload = self._get_json(b"public_receipts", receipt_id)
        return payload if isinstance(payload, dict) else None

    def get_receipts_by_signer(self, signer_agent_id: str) -> list[dict[str, Any]]:
        return self._resolve_index_rows(db_name=b"receipts_by_signer", key=signer_agent_id)

    def get_receipts_by_artifact_epoch(
        self,
        artifact_kind: str,
        epoch_id: str,
    ) -> list[dict[str, Any]]:
        rows = self._resolve_index_rows(
            db_name=b"receipts_by_kind_epoch",
            key=_compound_index_key(artifact_kind, epoch_id),
        )
        if rows:
            return rows
        return self._resolve_index_rows(
            db_name=b"receipts_by_kind_epoch",
            key=f"{artifact_kind}::{epoch_id}",
        )

    def _append_index_id(self, *, db_name: bytes, key: str, receipt_id: str) -> None:
        with self.env.begin(write=True, db=self._dbs[db_name]) as txn:
            existing = _decode_json(txn.get(_encode_key(key)))
            if isinstance(existing, list):
                receipt_ids = [item for item in existing if isinstance(item, str)]
            else:
                receipt_ids = []
            if receipt_id not in receipt_ids:
                if len(receipt_ids) >= MAX_PUBLIC_RECEIPT_INDEX_IDS:
                    raise ValueError("public_receipt_index_capacity_exceeded")
                receipt_ids.append(receipt_id)
                txn.put(_encode_key(key), _encode_json(sorted(receipt_ids)))

    def _resolve_index_rows(self, *, db_name: bytes, key: str) -> list[dict[str, Any]]:
        receipt_ids = self._get_json(db_name, key)
        if not isinstance(receipt_ids, list):
            return []
        rows: list[dict[str, Any]] = []
        for receipt_id in sorted(item for item in receipt_ids if isinstance(item, str)):
            payload = self.get_receipt(receipt_id)
            if isinstance(payload, dict):
                rows.append(payload)
        return rows


class LmdbAdmissionStore(LmdbPublicReceiptStore):
    def put_admission_receipt(self, receipt_id: str, payload: dict[str, Any]) -> None:
        self.put_receipt(receipt_id, payload)

    def get_admission_receipt(self, receipt_id: str) -> dict[str, Any] | None:
        return self.get_receipt(receipt_id)
