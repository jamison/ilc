# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 888 — CDL-075 truth primitive read-path query CLI helper.

Wires TruthPrimitiveGraphStore read operations into the ILC CLI `query`
command as two new subcommands:

    ilc query truth-node --node-id <cid>
        Retrieve a persisted truth primitive node by its CIDv1 identifier.

    ilc query truth-edges --node-id <cid>
        List all edges whose source or target matches the given identifier.

Both subcommands require ILC_TRUTH_GRAPH_STORE_PATH to be set.
Read-only — no mutation of the LMDB store occurs via this path.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ilc_core.epistemic.truth_primitive_graph_store import (
    CDL_075_DEPENDENCY as STORE_CDL_075_DEPENDENCY,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import (
    TruthPrimitiveGraphStore,
)

D2E_QUERY_TRUTH_CLI_VERSION = "d2e_query_truth_cli_888.v0.1"
CDL_075_DEPENDENCY = STORE_CDL_075_DEPENDENCY

if CDL_075_DEPENDENCY != "cdl_075_truth_primitive_graph_persistence.v0.1":
    raise ValueError("query_truth_cli_cdl_075_dependency_mismatch")


class QueryTruthCommandError(Exception):
    """Typed error for truth query command failures."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


def _open_store(store_path: str) -> TruthPrimitiveGraphStore:
    """Open the CDL-075 LMDB graph store at the given path."""
    return TruthPrimitiveGraphStore(Path(store_path))


def _require_store_path() -> str:
    """Return ILC_TRUTH_GRAPH_STORE_PATH or raise a typed error."""
    store_path = os.environ.get("ILC_TRUTH_GRAPH_STORE_PATH", "").strip()
    if not store_path:
        raise QueryTruthCommandError(
            "query_truth_store_path_not_configured",
            "ILC_TRUTH_GRAPH_STORE_PATH is not set; "
            "truth-node and truth-edges require a CDL-075 graph store path",
        )
    return store_path


def handle_query_truth_node(node_id: str) -> dict[str, Any]:
    """Retrieve a persisted truth primitive node by CIDv1 identifier.

    Args:
        node_id: CIDv1 string (multibase base32 lowercase, 'b' prefix).

    Returns:
        Dict with subcommand, node_id, node_record, and version.

    Raises:
        QueryTruthCommandError: If store path is not configured, node_id
            is empty, or the node is not found.
    """
    if not node_id or not isinstance(node_id, str):
        raise QueryTruthCommandError(
            "query_truth_node_id_missing",
            "--node-id must be a non-empty CIDv1 string",
        )

    store_path = _require_store_path()
    store = _open_store(store_path)
    try:
        record = store.get_node(node_id)
    finally:
        store.close()

    if record is None:
        raise QueryTruthCommandError(
            "query_truth_node_not_found",
            f"truth primitive node not found: {node_id}",
        )

    return {
        "subcommand": "truth-node",
        "node_id": node_id,
        "node_record": record,
        "store_path": store_path,
        "version": D2E_QUERY_TRUTH_CLI_VERSION,
    }


def handle_query_truth_edges(node_id: str) -> dict[str, Any]:
    """List all edges whose source or target matches the given identifier.

    Scans the CDL-075 edges database and returns all edge records where
    either the 'source' or 'target' field equals node_id.

    Args:
        node_id: CIDv1 string or agent_id to match against edge endpoints.

    Returns:
        Dict with subcommand, node_id, edges list, count, and version.

    Raises:
        QueryTruthCommandError: If store path is not configured or node_id
            is empty.
    """
    if not node_id or not isinstance(node_id, str):
        raise QueryTruthCommandError(
            "query_truth_node_id_missing",
            "--node-id must be a non-empty string",
        )

    store_path = _require_store_path()
    store = _open_store(store_path)
    try:
        all_edges = store.iter_edges()
    finally:
        store.close()

    matching = [
        edge for edge in all_edges
        if edge.get("source") == node_id or edge.get("target") == node_id
    ]

    return {
        "subcommand": "truth-edges",
        "node_id": node_id,
        "edges": matching,
        "count": len(matching),
        "store_path": store_path,
        "version": D2E_QUERY_TRUTH_CLI_VERSION,
    }
