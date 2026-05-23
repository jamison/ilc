# SPDX-License-Identifier: AGPL-3.0-or-later
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
    """

    def __init__(
        self,
        root: Path | str,
        *,
        map_size: int = DEFAULT_MAP_SIZE_BYTES,
    ) -> None:
        super().__init__(root, db_names=(b"nodes", b"edges"), map_size=map_size)

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
