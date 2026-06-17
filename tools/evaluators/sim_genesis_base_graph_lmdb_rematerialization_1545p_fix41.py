#!/usr/bin/env python3
"""Materialize the current Genesis Atlas candidate into local LMDB.

PUBLIC_RC_EXCLUDE: genesis_base_graph_lmdb_rematerialization_research_only
PUBLIC_RC_EXCLUDE_REASON: Local deterministic projection of an unsigned Atlas candidate; not Genesis signing, public graph upload, public RC activation, or canonical graph mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (  # noqa: E402
    GENESIS_ATLAS_CANDIDATE_LMDB_ADAPTER_VERSION,
    GenesisAtlasCandidateStore,
)
from ilc_core.storage.lmdb_public_runtime import DEFAULT_MAP_SIZE_BYTES  # noqa: E402


PHASE = "1545p-Fix41"
SIM_ID = "SIM-GENESIS-BASE-GRAPH-LMDB-REMATERIALIZATION-01"
SCHEMA_VERSION = "sim_genesis_base_graph_lmdb_rematerialization_1545p_fix41.v0.1"

DEFAULT_CANDIDATE = REPO_ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json"
DEFAULT_LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4.lmdb"
DEFAULT_REEXPORT = REPO_ROOT / "out/genesis_base_graph_v0.4_lmdb_reexport.json"
DEFAULT_DIGEST = REPO_ROOT / "out/genesis_base_graph_v0.4_lmdb_digest.json"
DEFAULT_WALKTHROUGH = REPO_ROOT / "docs/phases/phase_1545p_fix41_lmdb_rematerialization_walkthrough.md"

OUTPUT_TOKENS = [
    "fix41_lmdb_materialized",
    "fix41_round_trip_digest_verified",
    "fix41_tier_indexes_verified",
    "fix41_complete",
    "public_path_remains_blocked_phase_1545p_fix41",
]

NON_CLAIMS = [
    "No Genesis v0.4 signing occurred.",
    "No canonical Atlas mutation occurred.",
    "No public graph upload or publication occurred.",
    "No public RC activation occurred.",
    "No runtime, economic, sidecar, or network activation occurred.",
    "LMDB is a derived local projection; JSON candidate plus preimages remain the authority source for any future signing gate.",
]


def _canonical_text(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _load_candidate(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fix41_candidate_object_required")
    nodes = payload.get("nodes")
    edges = payload.get("edges")
    if not isinstance(nodes, list) or not all(isinstance(row, dict) for row in nodes):
        raise ValueError("fix41_candidate_nodes_list_required")
    if not isinstance(edges, list) or not all(isinstance(row, dict) for row in edges):
        raise ValueError("fix41_candidate_edges_list_required")
    return payload


def _fresh_lmdb_root(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _node_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix41_candidate_node_missing_candidate_id")
    return value


def _edge_id_present(edge: dict[str, Any]) -> bool:
    value = edge.get("edge_id")
    return isinstance(value, str) and bool(value)


def _tier_group_counts(store: GenesisAtlasCandidateStore) -> dict[str, int]:
    return {
        "canonical": len(store.node_ids_by_tier_group("canonical")),
        "support": len(store.node_ids_by_tier_group("support")),
        "private": len(store.node_ids_by_tier_group("private")),
    }


def _materialize(
    *,
    candidate_path: Path,
    lmdb_root: Path,
    reexport_path: Path,
    digest_path: Path,
    walkthrough_path: Path,
    map_size: int,
) -> dict[str, Any]:
    graph = _load_candidate(candidate_path)
    nodes: list[dict[str, Any]] = graph["nodes"]
    edges: list[dict[str, Any]] = graph["edges"]

    node_ids = [_node_id(node) for node in nodes]
    duplicate_node_ids = sorted(node_id for node_id, count in Counter(node_ids).items() if count > 1)
    if duplicate_node_ids:
        raise ValueError(f"fix41_duplicate_node_ids:{duplicate_node_ids[:10]}")

    edge_ids_present = sum(1 for edge in edges if _edge_id_present(edge))
    missing_edge_ids = len(edges) - edge_ids_present

    source_file_sha256 = _sha256_file(candidate_path)
    source_canonical = _canonical_text(graph)
    source_canonical_sha256 = _sha256_text(source_canonical)

    _fresh_lmdb_root(lmdb_root)
    store = GenesisAtlasCandidateStore(
        lmdb_root,
        allow_synthetic_edge_keys=True,
        map_size=map_size,
    )
    try:
        manifest = {
            "adapter_version": GENESIS_ATLAS_CANDIDATE_LMDB_ADAPTER_VERSION,
            "candidate_phase": graph.get("phase"),
            "candidate_schema_version": graph.get("schema_version"),
            "candidate_sha256": source_file_sha256,
            "candidate_status": graph.get("candidate_status"),
            "materialization_date": date.today().isoformat(),
            "materialization_phase": PHASE,
            "source_candidate": "fix41a",
            "source_candidate_path": _display_path(candidate_path),
        }
        store.put_meta("materialization_manifest", manifest)
        store.put_graph_payload(graph)
        store.put_nodes(nodes)
        store.put_edges(edges)

        lmdb_nodes = store.iter_nodes()
        lmdb_edges = store.iter_edges()
        tier_group_counts = _tier_group_counts(store)
        stored_graph = store.get_graph_payload()
        stored_manifest = store.get_meta("materialization_manifest")
    finally:
        store.close()

    if stored_graph is None:
        raise ValueError("fix41_lmdb_graph_payload_missing")
    if stored_manifest is None:
        raise ValueError("fix41_lmdb_manifest_missing")

    reexport_canonical = _canonical_text(stored_graph)
    reexport_canonical_sha256 = _sha256_text(reexport_canonical)
    _atomic_write(reexport_path, reexport_canonical)
    reexport_file_sha256 = _sha256_file(reexport_path)

    tier_group_total = sum(tier_group_counts.values())
    round_trip = {
        "canonical_digest_match": source_canonical_sha256 == reexport_canonical_sha256,
        "node_count_match": len(nodes) == len(lmdb_nodes),
        "edge_count_match": len(edges) == len(lmdb_edges),
        "graph_payload_present": True,
        "tier_group_total_matches_node_count": tier_group_total == len(nodes),
        "tier_indexes_present": all(tier_group_counts[group] > 0 for group in ("canonical", "support", "private")),
    }
    if not all(round_trip.values()):
        raise ValueError(f"fix41_round_trip_or_index_check_failed:{round_trip}")

    payload = {
        "adapter_version": GENESIS_ATLAS_CANDIDATE_LMDB_ADAPTER_VERSION,
        "counts": {
            "edge_ids_present": edge_ids_present,
            "lmdb_edge_count": len(lmdb_edges),
            "lmdb_node_count": len(lmdb_nodes),
            "missing_edge_ids": missing_edge_ids,
            "source_edge_count": len(edges),
            "source_node_count": len(nodes),
        },
        "digests": {
            "reexport_canonical_sha256": reexport_canonical_sha256,
            "reexport_file_sha256": reexport_file_sha256,
            "source_canonical_sha256": source_canonical_sha256,
            "source_file_sha256": source_file_sha256,
        },
        "lmdb_root": _display_path(lmdb_root),
        "manifest": stored_manifest,
        "non_claims": NON_CLAIMS,
        "phase": PHASE,
        "round_trip": round_trip,
        "schema_version": SCHEMA_VERSION,
        "sim_id": SIM_ID,
        "source_candidate": "fix41a",
        "source_candidate_path": _display_path(candidate_path),
        "status": "PASS",
        "tier_group_counts": tier_group_counts,
        "tokens": OUTPUT_TOKENS,
    }
    _atomic_write(digest_path, _canonical_text(payload))
    _atomic_write(walkthrough_path, _walkthrough(payload))
    return payload


def _walkthrough(payload: dict[str, Any]) -> str:
    counts = payload["counts"]
    digests = payload["digests"]
    tiers = payload["tier_group_counts"]
    lines = [
        "# Phase 1545p-Fix41 LMDB Rematerialization Walkthrough",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: fix41_lmdb_rematerialization_walkthrough -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: local unsigned Atlas candidate LMDB projection evidence; not public RC material -->",
        "",
        f"**Status:** {payload['status']}",
        "**Sensitivity:** NON-SENSITIVE",
        f"**Input candidate:** `{payload['source_candidate_path']}`",
        f"**LMDB output:** `{payload['lmdb_root']}`",
        "",
        "## Summary",
        "",
        "Fix41 materialized the post-Fix41a unsigned Genesis Atlas candidate into a",
        "local LMDB projection. The LMDB projection stores the complete graph payload,",
        "node rows, edge rows, metadata, and tier indexes. It is a derived local query",
        "store, not a signing authority.",
        "",
        "## Counts",
        "",
        "| Metric | Count |",
        "|---|---:|",
    ]
    for key in sorted(counts):
        lines.append(f"| `{key}` | `{counts[key]}` |")
    lines.extend(
        [
            "",
            "## Tier Group Indexes",
            "",
            "| Tier group | Count |",
            "|---|---:|",
        ]
    )
    for key in ("canonical", "support", "private"):
        lines.append(f"| `{key}` | `{tiers[key]}` |")
    lines.extend(
        [
            "",
            "## Digest Verification",
            "",
            "| Digest | SHA-256 |",
            "|---|---|",
        ]
    )
    for key in sorted(digests):
        lines.append(f"| `{key}` | `{digests[key]}` |")
    lines.extend(
        [
            "",
            "## Round Trip Checks",
            "",
            "| Check | Result |",
            "|---|---|",
        ]
    )
    for key, value in payload["round_trip"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Output Tokens", ""])
    for token in payload["tokens"]:
        lines.append(f"- `{token}`")
    lines.extend(["", "## Non-Claims", ""])
    for claim in payload["non_claims"]:
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "## Graph Delta",
            "",
            "```text",
            "graph_delta=support_only:out/genesis_base_graph_v0.4_lmdb_digest.json",
            "graph_delta=support_only:docs/phases/phase_1545p_fix41_lmdb_rematerialization_walkthrough.md",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_LMDB_ROOT)
    parser.add_argument("--reexport", type=Path, default=DEFAULT_REEXPORT)
    parser.add_argument("--digest", type=Path, default=DEFAULT_DIGEST)
    parser.add_argument("--walkthrough", type=Path, default=DEFAULT_WALKTHROUGH)
    parser.add_argument("--map-size", type=int, default=DEFAULT_MAP_SIZE_BYTES * 8)
    args = parser.parse_args()

    payload = _materialize(
        candidate_path=args.candidate.resolve(),
        lmdb_root=args.output.resolve(),
        reexport_path=args.reexport.resolve(),
        digest_path=args.digest.resolve(),
        walkthrough_path=args.walkthrough.resolve(),
        map_size=args.map_size,
    )
    print(_canonical_text(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
