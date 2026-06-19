# SPDX-License-Identifier: AGPL-3.0-only
"""Read-only CLI helpers for the unsigned Genesis Atlas LMDB projection.

PUBLIC_RC_EXCLUDE: genesis_atlas_lmdb_read_cli_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB inspection helper; not
public graph activation, Genesis signing, canonical graph mutation, runtime
activation, public serving, or economic settlement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from ilc_core.ledger.exact_numeric import normalize_json_scalars
from ilc_core.storage.genesis_atlas_lmdb_writer import AtlasLmdbSafeWriter


ATLAS_LMDB_CLI_VERSION = "atlas_lmdb_cli_1545p_fix59c.v0.1"


class AtlasLmdbCliError(ValueError):
    """Typed error for Atlas LMDB read CLI failures."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(f"{token}: {message}")
        self.token = token
        self.message = message


def run_atlas_command(args: argparse.Namespace) -> dict[str, Any]:
    """Dispatch the `ilc atlas` command namespace."""
    subcommand = getattr(args, "atlas_subcommand", "")
    lmdb_path = str(getattr(args, "lmdb", "") or "")
    if subcommand == "status":
        return handle_atlas_status(lmdb_path)
    if subcommand == "validate":
        return handle_atlas_validate(lmdb_path)
    if subcommand == "node":
        return handle_atlas_node(lmdb_path, str(getattr(args, "node_id", "") or ""))
    if subcommand == "edges":
        return handle_atlas_edges(lmdb_path, str(getattr(args, "node_id", "") or ""))
    raise AtlasLmdbCliError("atlas_subcommand_missing", "atlas subcommand is required")


def handle_atlas_status(lmdb_path: str) -> dict[str, Any]:
    """Return deterministic status information for a local Atlas LMDB."""
    writer = _open_writer(lmdb_path)
    try:
        inspection = writer.inspect()
        payload = writer.store.get_graph_payload() or {}
        metadata = _metadata_snapshot(writer)
        edge_id_coverage = _edge_id_coverage(writer.store.iter_edges())
        graph_payload_sha256 = _sha256_json(payload) if payload else ""
        return {
            "subcommand": "status",
            "version": ATLAS_LMDB_CLI_VERSION,
            "lmdb_path": str(Path(lmdb_path)),
            "counts": {
                "nodes": inspection["node_count"],
                "edges": inspection["edge_count"],
                "preimages": inspection["preimage_count"],
                "graph_payload_nodes": inspection["graph_payload_node_count"],
                "graph_payload_edges": inspection["graph_payload_edge_count"],
            },
            "edge_id_coverage": edge_id_coverage,
            "graph_payload_sha256": graph_payload_sha256,
            "materialization_manifest": metadata.get("materialization_manifest", {}),
            "metadata": metadata,
            "invariants": inspection["invariants"],
            "dangling_edge_count": inspection["dangling_edge_count"],
            "read_only": True,
        }
    finally:
        writer.close()


def handle_atlas_validate(lmdb_path: str) -> dict[str, Any]:
    """Validate the local Atlas LMDB row stores and graph payload."""
    writer = _open_writer(lmdb_path)
    try:
        inspection = writer.inspect()
        edges = writer.store.iter_edges()
        coverage = _edge_id_coverage(edges)
        checks = {
            "no_dangling_edges": inspection["invariants"]["no_dangling_edges"],
            "payload_node_count_matches_rows": inspection["invariants"][
                "payload_node_count_matches_rows"
            ],
            "payload_edge_count_matches_rows": inspection["invariants"][
                "payload_edge_count_matches_rows"
            ],
            "tier_index_matches_rows": inspection["invariants"]["tier_index_matches_rows"],
            "tier_group_index_matches_rows": inspection["invariants"][
                "tier_group_index_matches_rows"
            ],
            "source_path_index_matches_rows": inspection["invariants"][
                "source_path_index_matches_rows"
            ],
        }
        hard_pass = all(checks.values())
        edge_id_status = (
            "complete" if coverage["missing_edge_id_count"] == 0 else "debt_present_carried_to_fix60"
        )
        return {
            "subcommand": "validate",
            "version": ATLAS_LMDB_CLI_VERSION,
            "lmdb_path": str(Path(lmdb_path)),
            "verdict": "pass" if hard_pass else "fail",
            "checks": checks,
            "edge_id_coverage": coverage,
            "edge_id_status": edge_id_status,
            "read_only": True,
        }
    finally:
        writer.close()


def handle_atlas_node(lmdb_path: str, node_id: str) -> dict[str, Any]:
    """Return a single Atlas node record by candidate ID."""
    if not node_id:
        raise AtlasLmdbCliError("atlas_node_id_missing", "--node-id must be non-empty")
    writer = _open_writer(lmdb_path)
    try:
        record = writer.store.get_node(node_id)
        if record is None:
            raise AtlasLmdbCliError("atlas_node_not_found", f"node not found: {node_id}")
        return {
            "subcommand": "node",
            "version": ATLAS_LMDB_CLI_VERSION,
            "lmdb_path": str(Path(lmdb_path)),
            "node_id": node_id,
            "node_record": _stable_object(record),
            "read_only": True,
        }
    finally:
        writer.close()


def handle_atlas_edges(lmdb_path: str, node_id: str) -> dict[str, Any]:
    """Return Atlas edges where source or target equals candidate ID."""
    if not node_id:
        raise AtlasLmdbCliError("atlas_node_id_missing", "--node-id must be non-empty")
    writer = _open_writer(lmdb_path)
    try:
        edges = [
            _stable_object(edge)
            for edge in writer.store.iter_edges()
            if _edge_source(edge) == node_id or _edge_target(edge) == node_id
        ]
        edges.sort(
            key=lambda edge: (
                str(edge.get("edge_id", "")),
                _edge_source(edge),
                _edge_type(edge),
                _edge_target(edge),
            )
        )
        return {
            "subcommand": "edges",
            "version": ATLAS_LMDB_CLI_VERSION,
            "lmdb_path": str(Path(lmdb_path)),
            "node_id": node_id,
            "count": len(edges),
            "edges": edges,
            "read_only": True,
        }
    finally:
        writer.close()


def _open_writer(lmdb_path: str) -> AtlasLmdbSafeWriter:
    if not isinstance(lmdb_path, str) or not lmdb_path.strip():
        raise AtlasLmdbCliError("atlas_lmdb_path_missing", "--lmdb must be provided")
    root = Path(lmdb_path)
    data_file = root / "data.mdb"
    lock_file = root / "lock.mdb"
    if not data_file.exists() or not lock_file.exists():
        raise AtlasLmdbCliError("atlas_lmdb_not_found", f"LMDB not found: {root}")
    return AtlasLmdbSafeWriter(root)


def _metadata_snapshot(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    keys = (
        "materialization_manifest",
        "fix55_graph_projection_classification",
        "fix59a_deferred_repair_reconciliation",
        "last_safe_writer_receipt",
    )
    return {
        key: value
        for key in keys
        if (value := writer.store.get_meta(key)) is not None
    }


def _edge_id_coverage(edges: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(edges)
    present = sum(1 for edge in edges if isinstance(edge.get("edge_id"), str) and edge["edge_id"])
    missing = total - present
    return {
        "edge_count": total,
        "present_edge_id_count": present,
        "missing_edge_id_count": missing,
        "present_fraction": _ratio_string(present, total),
    }


def _ratio_string(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0/0"
    return f"{numerator}/{denominator}"


def _sha256_json(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        normalize_json_scalars(payload),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _stable_object(payload: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(
        normalize_json_scalars(payload),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    value = json.loads(encoded)
    if not isinstance(value, dict):
        raise AtlasLmdbCliError("atlas_record_not_object", "LMDB record was not an object")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    return value if isinstance(value, str) else ""


__all__ = [
    "ATLAS_LMDB_CLI_VERSION",
    "AtlasLmdbCliError",
    "handle_atlas_edges",
    "handle_atlas_node",
    "handle_atlas_status",
    "handle_atlas_validate",
    "run_atlas_command",
]
