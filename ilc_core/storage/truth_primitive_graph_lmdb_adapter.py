# SPDX-License-Identifier: AGPL-3.0-only
"""LMDB adapter for CDL-075 truth primitive graph persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ilc_core.storage.lmdb_public_runtime import (
    DEFAULT_MAP_SIZE_BYTES,
    _LmdbRuntimeBase,
    _encode_key,
    _encode_json,
)


TRUTH_PRIMITIVE_GRAPH_LMDB_ADAPTER_VERSION = "truth_primitive_graph_lmdb_adapter_1250.v0.1"


class TruthPrimitiveGraphStore(_LmdbRuntimeBase):
    """CDL-075 LMDB-backed store for truth primitive nodes and edges.

    Named databases:
        b"nodes" - key=CIDv1 string, value=JSON canonical node record
        b"edges" - key="{source}:{edge_type}:{target}", value=JSON edge record
        b"native_submit_replay" - key=replay tuple digest, value=replay payload
    """

    def __init__(
        self,
        root: Path | str,
        *,
        map_size: int = DEFAULT_MAP_SIZE_BYTES,
    ) -> None:
        super().__init__(
            root,
            db_names=(b"nodes", b"edges", b"native_submit_replay"),
            map_size=map_size,
        )

    def write_truth_primitive_batch(
        self,
        *,
        node_id: str | None,
        node_record: dict[str, Any] | None,
        edge_records: list[tuple[str, dict[str, Any]]],
        replay_key: str | None = None,
        replay_payload: dict[str, Any] | None = None,
    ) -> dict[str, int | bool]:
        """Atomically persist replay marker, node, and edges for an accepted submit."""

        with self.env.begin(write=True) as txn:
            if replay_key is not None:
                replay_db = self._dbs[b"native_submit_replay"]
                if txn.get(_encode_key(replay_key), db=replay_db) is not None:
                    return {
                        "replay_rejected": True,
                        "replay_written": 0,
                        "nodes_written": 0,
                        "edges_written": 0,
                    }
                txn.put(
                    _encode_key(replay_key),
                    _encode_json(replay_payload or {}),
                    db=replay_db,
                )
                replay_written = 1
            else:
                replay_written = 0

            node_written = 0
            if node_id is not None and node_record is not None:
                node_key = _encode_key(node_id)
                nodes_db = self._dbs[b"nodes"]
                if txn.get(node_key, db=nodes_db) is None:
                    txn.put(node_key, _encode_json(node_record), db=nodes_db)
                    node_written = 1

            edges_written = 0
            edges_db = self._dbs[b"edges"]
            for edge_key, record in edge_records:
                encoded_key = _encode_key(edge_key)
                if txn.get(encoded_key, db=edges_db) is None:
                    txn.put(encoded_key, _encode_json(record), db=edges_db)
                    edges_written += 1

        return {
            "replay_rejected": False,
            "replay_written": replay_written,
            "nodes_written": node_written,
            "edges_written": edges_written,
        }

    def put_node_if_absent(self, node_id: str, record: dict[str, Any]) -> bool:
        """Write node record only if the CIDv1 key is not present."""
        key = _encode_key(node_id)
        value = _encode_json(record)
        with self.env.begin(write=True, db=self._dbs[b"nodes"]) as txn:
            existing = txn.get(key)
            if existing is not None:
                return False
            txn.put(key, value)
            return True

    def put_edge_if_absent(self, edge_key: str, record: dict[str, Any]) -> bool:
        """Write edge record only if the composite edge key is not present."""
        key = _encode_key(edge_key)
        value = _encode_json(record)
        with self.env.begin(write=True, db=self._dbs[b"edges"]) as txn:
            existing = txn.get(key)
            if existing is not None:
                return False
            txn.put(key, value)
            return True

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """Retrieve a canonical node record by CIDv1."""
        payload = self._get_json(b"nodes", node_id)
        return payload if isinstance(payload, dict) else None

    def get_native_submit_replay(self, replay_key: str) -> dict[str, Any] | None:
        """Retrieve a native-submit replay marker by stable replay key."""
        payload = self._get_json(b"native_submit_replay", replay_key)
        return payload if isinstance(payload, dict) else None

    def get_edge(self, edge_key: str) -> dict[str, Any] | None:
        """Retrieve an edge record by composite key."""
        payload = self._get_json(b"edges", edge_key)
        return payload if isinstance(payload, dict) else None

    def iter_nodes(self) -> list[dict[str, Any]]:
        """Return all stored node records in key-sorted order."""
        rows = [row for row in self._iter_json(b"nodes") if isinstance(row, dict)]
        return sorted(rows, key=lambda row: str(row.get("primitive", "")))

    def iter_edges(self) -> list[dict[str, Any]]:
        """Return all stored edge records in key-sorted order."""
        rows = [row for row in self._iter_json(b"edges") if isinstance(row, dict)]
        return sorted(
            rows,
            key=lambda row: (
                str(row.get("source", "")),
                str(row.get("edge_type", "")),
                str(row.get("target", "")),
            ),
        )


__all__ = [
    "TRUTH_PRIMITIVE_GRAPH_LMDB_ADAPTER_VERSION",
    "TruthPrimitiveGraphStore",
]
