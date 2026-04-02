from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import lmdb


LMDB_PUBLIC_RUNTIME_VERSION = "lmdb_public_runtime_v0.1"
DEFAULT_MAP_SIZE_BYTES = 256 * 1024 * 1024
_ENV_CACHE: dict[str, lmdb.Environment] = {}


def _encode_key(value: str) -> bytes:
    return value.encode("utf-8")


def _encode_json(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _decode_json(payload: bytes | None) -> Any:
    if payload is None:
        return None
    return json.loads(payload.decode("utf-8"))


class _LmdbRuntimeBase:
    def __init__(self, root: Path | str, *, db_names: tuple[bytes, ...], map_size: int = DEFAULT_MAP_SIZE_BYTES) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        root_key = str(self.root.resolve())
        self.env = _ENV_CACHE.get(root_key)
        if self.env is None:
            self.env = lmdb.open(
                root_key,
                create=True,
                subdir=True,
                max_dbs=max(1, len(db_names)),
                map_size=map_size,
                lock=True,
            )
            _ENV_CACHE[root_key] = self.env
        self._dbs = {name: self.env.open_db(name) for name in db_names}

    def _put_json(self, db_name: bytes, key: str, payload: Any) -> None:
        with self.env.begin(write=True, db=self._dbs[db_name]) as txn:
            txn.put(_encode_key(key), _encode_json(payload))

    def _get_json(self, db_name: bytes, key: str) -> Any:
        with self.env.begin(db=self._dbs[db_name]) as txn:
            return _decode_json(txn.get(_encode_key(key)))

    def _iter_json(self, db_name: bytes) -> list[Any]:
        rows: list[Any] = []
        with self.env.begin(db=self._dbs[db_name]) as txn:
            cursor = txn.cursor()
            for _, value in cursor:
                rows.append(_decode_json(value))
        return rows


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


class LmdbWalletStore(_LmdbRuntimeBase):
    def __init__(self, root: Path | str, *, map_size: int = DEFAULT_MAP_SIZE_BYTES) -> None:
        super().__init__(root, db_names=(b"wallets", b"wallet_history"), map_size=map_size)

    def put_wallet(self, agent_id: str, payload: dict[str, Any]) -> None:
        self._put_json(b"wallets", agent_id, payload)

    def get_wallet(self, agent_id: str) -> dict[str, Any] | None:
        payload = self._get_json(b"wallets", agent_id)
        return payload if isinstance(payload, dict) else None

    def iter_wallets(self) -> dict[str, dict[str, Any]]:
        rows: dict[str, dict[str, Any]] = {}
        with self.env.begin(db=self._dbs[b"wallets"]) as txn:
            cursor = txn.cursor()
            for key, value in cursor:
                payload = _decode_json(value)
                if isinstance(payload, dict):
                    rows[key.decode("utf-8")] = payload
        return dict(sorted(rows.items()))

    def put_wallet_history(self, agent_id: str, payload: dict[str, Any]) -> None:
        self._put_json(b"wallet_history", agent_id, payload)

    def get_wallet_history(self, agent_id: str) -> dict[str, Any] | None:
        payload = self._get_json(b"wallet_history", agent_id)
        return payload if isinstance(payload, dict) else None
