# SPDX-License-Identifier: AGPL-3.0-only
"""LMDB adapter for CDL-075 truth primitive graph persistence."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from ilc_core.storage.lmdb_public_runtime import (
    DEFAULT_MAP_SIZE_BYTES,
    _LmdbRuntimeBase,
    _encode_key,
    _encode_json,
)


TRUTH_PRIMITIVE_GRAPH_LMDB_ADAPTER_VERSION = "truth_primitive_graph_lmdb_adapter_1250.v0.1"
MAX_RELEASE_ASSERTION_GRAPH_SCAN_NODES = 4_096
MAX_RELEASE_ASSERTION_CANDIDATES = 128


def _mapping(value: Any) -> dict[str, Any] | None:
    return dict(value) if isinstance(value, dict) else None


def _decode_mapping_from_base64_json(value: str) -> dict[str, Any] | None:
    try:
        decoded = base64.b64decode(value.encode("utf-8"), validate=True)
        payload = json.loads(decoded.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return _mapping(payload)


def _release_version_key(value: Any) -> tuple[int, ...]:
    if not isinstance(value, str):
        return ()
    parts = value.split(".")
    if not (2 <= len(parts) <= 4):
        return ()
    try:
        parsed = tuple(int(part) for part in parts)
    except ValueError:
        return ()
    if any(part < 0 for part in parsed):
        return ()
    return parsed


def _is_release_assertion_payload(value: dict[str, Any]) -> bool:
    return (
        value.get("schema_version") == "software_release_assertion.v0.1"
        and isinstance(value.get("software_release_node"), dict)
        and isinstance(value.get("release_attestation_edges"), list)
    )


def _reconstruct_native_submit_envelope(record: dict[str, Any]) -> dict[str, Any] | None:
    required = {"v", "primitive", "agent_id", "epoch", "payload", "native_submit_sig"}
    if not required <= set(record):
        return None
    envelope = {
        "v": record["v"],
        "primitive": record["primitive"],
        "agent_id": record["agent_id"],
        "epoch": record["epoch"],
        "payload": record["payload"],
        "sig": record["native_submit_sig"],
    }
    from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
    from ilc_core.epistemic.truth_primitive_submission_runtime import (
        verify_native_submit_sig_envelope,
    )

    try:
        verify_native_submit_sig_envelope(envelope)
    except EpistemicSubmissionError:
        return None
    return envelope


def _with_reconstructed_provenance(
    assertion: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    result = dict(assertion)
    envelope = _reconstruct_native_submit_envelope(record)
    if envelope is not None:
        result["native_submit_envelope"] = envelope
    return result


def _extract_release_assertion_payload(record: dict[str, Any]) -> dict[str, Any] | None:
    """Extract the full release assertion payload from known graph-node shapes."""

    if _is_release_assertion_payload(record):
        return dict(record)

    direct = _mapping(record.get("software_release_assertion"))
    if direct is not None and _is_release_assertion_payload(direct):
        return _with_reconstructed_provenance(direct, record)

    content = _mapping(record.get("content"))
    if content is not None:
        nested = _mapping(content.get("software_release_assertion"))
        if nested is not None and _is_release_assertion_payload(nested):
            return _with_reconstructed_provenance(nested, record)

    payload = record.get("payload")
    if isinstance(payload, str):
        # Historical/alternate graph evidence may store the envelope payload as
        # base64 JSON. Native submit persistence currently stores a mapping.
        payload = _decode_mapping_from_base64_json(payload)
    payload_mapping = _mapping(payload)
    if payload_mapping is None:
        return None
    if _is_release_assertion_payload(payload_mapping):
        return _with_reconstructed_provenance(payload_mapping, record)
    payload_content = _mapping(payload_mapping.get("content"))
    if payload_content is None:
        return None
    nested = _mapping(payload_content.get("software_release_assertion"))
    if nested is not None and _is_release_assertion_payload(nested):
        return _with_reconstructed_provenance(nested, record)
    return None


def _release_assertion_sort_key(assertion: dict[str, Any]) -> tuple[str, tuple[int, ...], str]:
    node = _mapping(assertion.get("software_release_node")) or {}
    return (
        str(node.get("release_date", "")),
        _release_version_key(node.get("version")),
        str(assertion.get("assertion_cid") or node.get("cid") or ""),
    )


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

    def get_latest_release_assertion(self, channel: str) -> dict[str, Any] | None:
        """Return the latest full software-release assertion for a channel.

        The public fetch endpoint serves the signed assertion payload, not a bare
        SoftwareReleaseNode. Current native submit persistence stores it under
        node_record["payload"]["content"]["software_release_assertion"]; the
        extractor also accepts the envelope/base64 variants used by historical
        ceremony evidence so the read path stays conservative during upgrades.
        """

        if not isinstance(channel, str) or not channel.strip():
            return None
        normalized_channel = channel.strip()
        from ilc_core.release.upgrade_check import UpgradeCheckError, validate_release_assertion

        matches: list[dict[str, Any]] = []
        scanned = 0
        bounds_exceeded = False
        for row in self._iter_json(b"nodes"):
            scanned += 1
            if scanned > MAX_RELEASE_ASSERTION_GRAPH_SCAN_NODES:
                bounds_exceeded = True
                break
            if not isinstance(row, dict):
                continue
            assertion = _extract_release_assertion_payload(row)
            if assertion is None:
                continue
            release_node = _mapping(assertion.get("software_release_node")) or {}
            if release_node.get("release_channel") == normalized_channel:
                try:
                    validate_release_assertion(assertion)
                except UpgradeCheckError:
                    continue
                if len(matches) >= MAX_RELEASE_ASSERTION_CANDIDATES:
                    bounds_exceeded = True
                    break
                matches.append(assertion)
        if bounds_exceeded:
            return None
        if not matches:
            return None
        return max(matches, key=_release_assertion_sort_key)

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

    def dump_raw_db_hex(self, db_name: bytes) -> list[dict[str, str]]:
        """Return raw key/value hex rows for deterministic parity-vector tooling."""

        if db_name not in self._dbs:
            raise ValueError("truth_primitive_graph_db_unknown")
        rows: list[dict[str, str]] = []
        with self.env.begin(db=self._dbs[db_name]) as txn:
            cursor = txn.cursor(db=self._dbs[db_name])
            for key, value in cursor:
                rows.append({"key_hex": bytes(key).hex(), "value_hex": bytes(value).hex()})
        return rows


__all__ = [
    "TRUTH_PRIMITIVE_GRAPH_LMDB_ADAPTER_VERSION",
    "TruthPrimitiveGraphStore",
]
