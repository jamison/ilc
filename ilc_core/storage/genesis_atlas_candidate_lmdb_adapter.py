# SPDX-License-Identifier: AGPL-3.0-only
"""LMDB adapter for unsigned Genesis Atlas candidate materialization.

PUBLIC_RC_EXCLUDE: genesis_atlas_candidate_lmdb_research_only
PUBLIC_RC_EXCLUDE_REASON: Local research/materialization adapter for unsigned Atlas candidates; not public graph activation, Genesis signing, or canonical graph mutation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ilc_core.storage.lmdb_public_runtime import (
    DEFAULT_MAP_SIZE_BYTES,
    _LmdbRuntimeBase,
    _encode_json,
    _encode_key,
)


GENESIS_ATLAS_CANDIDATE_LMDB_ADAPTER_VERSION = "genesis_atlas_candidate_lmdb_adapter_1545p_fix23.v0.1"


class GenesisAtlasCandidateStore(_LmdbRuntimeBase):
    """Local LMDB projection for unsigned Genesis Atlas candidate graphs.

    Named databases:
        b"nodes" - key=candidate_id, value=candidate node JSON
        b"edges" - key=edge_id, value=candidate edge JSON
        b"preimages" - key=node_id, value=unsigned candidate preimage JSON
        b"meta" - key=metadata token, value=JSON metadata
        b"nodes_by_tier" - key=tier, value=sorted candidate_id list
        b"nodes_by_source_path" - key=source path, value=sorted candidate_id list

    This adapter intentionally does not sign, publish, gossip, activate, or
    promote any candidate record. It is a local query/materialization substrate.
    """

    def __init__(
        self,
        root: Path | str,
        *,
        map_size: int = DEFAULT_MAP_SIZE_BYTES * 4,
    ) -> None:
        super().__init__(
            root,
            db_names=(
                b"nodes",
                b"edges",
                b"preimages",
                b"meta",
                b"nodes_by_tier",
                b"nodes_by_source_path",
            ),
            map_size=map_size,
        )

    def put_meta(self, key: str, payload: dict[str, Any]) -> None:
        self._put_json(b"meta", key, payload)

    def get_meta(self, key: str) -> dict[str, Any] | None:
        payload = self._get_json(b"meta", key)
        return payload if isinstance(payload, dict) else None

    def put_nodes(self, nodes: list[dict[str, Any]]) -> None:
        """Bulk-write candidate nodes and deterministic indexes."""
        tier_index: dict[str, list[str]] = {}
        path_index: dict[str, list[str]] = {}
        with self.env.begin(write=True) as txn:
            nodes_db = self._dbs[b"nodes"]
            for node in nodes:
                node_id = _candidate_id(node)
                txn.put(_encode_key(node_id), _encode_json(node), db=nodes_db)
                tier = str(node.get("tier", "unknown"))
                tier_index.setdefault(tier, []).append(node_id)
                source_path = node.get("source_path")
                if isinstance(source_path, str) and source_path:
                    path_index.setdefault(source_path, []).append(node_id)
        self._write_string_list_index(b"nodes_by_tier", tier_index)
        self._write_string_list_index(b"nodes_by_source_path", path_index)

    def put_edges(self, edges: list[dict[str, Any]]) -> None:
        """Bulk-write candidate edges."""
        with self.env.begin(write=True, db=self._dbs[b"edges"]) as txn:
            for edge in edges:
                edge_id = _edge_id(edge)
                txn.put(_encode_key(edge_id), _encode_json(edge))

    def put_preimages(self, preimages: list[dict[str, Any]]) -> None:
        """Bulk-write deterministic unsigned node preimages."""
        with self.env.begin(write=True, db=self._dbs[b"preimages"]) as txn:
            for preimage in preimages:
                node_id = _preimage_node_id(preimage)
                txn.put(_encode_key(node_id), _encode_json(preimage))

    def get_node(self, candidate_id: str) -> dict[str, Any] | None:
        payload = self._get_json(b"nodes", candidate_id)
        return payload if isinstance(payload, dict) else None

    def get_edge(self, edge_id: str) -> dict[str, Any] | None:
        payload = self._get_json(b"edges", edge_id)
        return payload if isinstance(payload, dict) else None

    def get_preimage(self, node_id: str) -> dict[str, Any] | None:
        payload = self._get_json(b"preimages", node_id)
        return payload if isinstance(payload, dict) else None

    def iter_nodes(self) -> list[dict[str, Any]]:
        rows = [row for row in self._iter_json(b"nodes") if isinstance(row, dict)]
        return sorted(rows, key=lambda row: str(row.get("candidate_id", "")))

    def iter_edges(self) -> list[dict[str, Any]]:
        rows = [row for row in self._iter_json(b"edges") if isinstance(row, dict)]
        return sorted(rows, key=lambda row: str(row.get("edge_id", "")))

    def iter_preimages(self) -> list[dict[str, Any]]:
        rows = [row for row in self._iter_json(b"preimages") if isinstance(row, dict)]
        return sorted(rows, key=lambda row: str(row.get("node_id", "")))

    def node_ids_by_tier(self, tier: str) -> list[str]:
        payload = self._get_json(b"nodes_by_tier", tier)
        return sorted(item for item in payload if isinstance(item, str)) if isinstance(payload, list) else []

    def node_ids_by_source_path(self, source_path: str) -> list[str]:
        payload = self._get_json(b"nodes_by_source_path", source_path)
        return sorted(item for item in payload if isinstance(item, str)) if isinstance(payload, list) else []

    def _write_string_list_index(self, db_name: bytes, index: dict[str, list[str]]) -> None:
        with self.env.begin(write=True, db=self._dbs[db_name]) as txn:
            for key, values in sorted(index.items()):
                txn.put(_encode_key(key), _encode_json(sorted(set(values))))


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("genesis_atlas_candidate_node_missing_candidate_id")
    return value


def _edge_id(edge: dict[str, Any]) -> str:
    value = edge.get("edge_id")
    if not isinstance(value, str) or not value:
        raise ValueError("genesis_atlas_candidate_edge_missing_edge_id")
    return value


def _preimage_node_id(preimage: dict[str, Any]) -> str:
    value = preimage.get("node_id")
    if not isinstance(value, str) or not value:
        raise ValueError("genesis_atlas_candidate_preimage_missing_node_id")
    return value


__all__ = [
    "GENESIS_ATLAS_CANDIDATE_LMDB_ADAPTER_VERSION",
    "GenesisAtlasCandidateStore",
]
