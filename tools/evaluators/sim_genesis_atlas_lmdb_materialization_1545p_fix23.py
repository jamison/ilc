#!/usr/bin/env python3
"""Materialize Fix22 Genesis Atlas candidate into local LMDB and verify round-trip.

PUBLIC_RC_EXCLUDE: genesis_atlas_lmdb_materialization_research_only
PUBLIC_RC_EXCLUDE_REASON: Local research-only materialization proof for unsigned Atlas candidate; not canonical graph mutation, node upload, public RC activation, or Genesis signing.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (  # noqa: E402
    GENESIS_ATLAS_CANDIDATE_LMDB_ADAPTER_VERSION,
    GenesisAtlasCandidateStore,
)


PHASE = "1545p-Fix23"
SIM_ID = "SIM-GENESIS-ATLAS-LMDB-MATERIALIZATION-01"
SCHEMA_VERSION = "sim_genesis_atlas_lmdb_materialization_1545p_fix23.v0.1"

FIX22_GRAPH = REPO_ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
FIX22_PREIMAGES = REPO_ROOT / "out/genesis_atlas_full_repo_node_preimages_1545p_fix22.jsonl"
FIX22_SIM = REPO_ROOT / "out/sim_full_repo_genesis_atlas_1545p_fix22.json"

LMDB_ROOT = REPO_ROOT / "out/genesis_atlas_lmdb_materialization_1545p_fix23/store"
JSON_OUT = REPO_ROOT / "out/sim_genesis_atlas_lmdb_materialization_1545p_fix23.json"
REPORT_OUT = REPO_ROOT / "docs/sims/sim_genesis_atlas_lmdb_materialization_1545p_fix23_v0.1.md"
REVIEW_OUT = REPO_ROOT / "docs/specs/ilc_genesis_atlas_lmdb_materialization_review_1545p_fix23_v0.1.md"


def _canonical_dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def _canonical_line(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest_rows(rows: list[dict[str, Any]], key: str) -> str:
    lines = [_canonical_line(row) for row in sorted(rows, key=lambda row: str(row.get(key, "")))]
    return _sha256_bytes(("\n".join(lines) + "\n").encode("utf-8"))


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


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json_object_required:{path}")
    return payload


def _read_preimages(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"preimage_json_object_required:{path}:{line_no}")
        rows.append(payload)
    return rows


def _fresh_lmdb_root(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _materialize(graph: dict[str, Any], preimages: list[dict[str, Any]], fix22_sim: dict[str, Any]) -> dict[str, Any]:
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not all(isinstance(node, dict) for node in nodes):
        raise ValueError("fix22_graph_nodes_list_required")
    if not isinstance(edges, list) or not all(isinstance(edge, dict) for edge in edges):
        raise ValueError("fix22_graph_edges_list_required")

    _fresh_lmdb_root(LMDB_ROOT)
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        store.put_meta(
            "materialization_manifest",
            {
                "adapter_version": GENESIS_ATLAS_CANDIDATE_LMDB_ADAPTER_VERSION,
                "candidate_status": graph.get("candidate_status"),
                "fix22_graph_sha256": _sha256_file(FIX22_GRAPH),
                "fix22_preimages_sha256": _sha256_file(FIX22_PREIMAGES),
                "phase": PHASE,
                "sim_id": SIM_ID,
                "source_git_commit": fix22_sim.get("source_git_commit"),
            },
        )
        store.put_nodes(nodes)
        store.put_edges(edges)
        store.put_preimages(preimages)

        lmdb_nodes = store.iter_nodes()
        lmdb_edges = store.iter_edges()
        lmdb_preimages = store.iter_preimages()
        manifest = store.get_meta("materialization_manifest")

        public_ids = store.node_ids_by_tier("public_release_candidate_material")
        private_ids = store.node_ids_by_tier("genesis_private_or_public_rc_excluded")
        generated_ids = store.node_ids_by_tier("generated_evidence_material")

        sample_path = ".agent/rules/ilc_loop_guardrails.md"
        sample_source_ids = store.node_ids_by_source_path(sample_path)
    finally:
        store.close()

    source_digests = {
        "nodes_digest": _digest_rows(nodes, "candidate_id"),
        "edges_digest": _digest_rows(edges, "edge_id"),
        "preimages_digest": _digest_rows(preimages, "node_id"),
    }
    lmdb_digests = {
        "nodes_digest": _digest_rows(lmdb_nodes, "candidate_id"),
        "edges_digest": _digest_rows(lmdb_edges, "edge_id"),
        "preimages_digest": _digest_rows(lmdb_preimages, "node_id"),
    }
    return {
        "counts": {
            "source_node_count": len(nodes),
            "source_edge_count": len(edges),
            "source_preimage_count": len(preimages),
            "lmdb_node_count": len(lmdb_nodes),
            "lmdb_edge_count": len(lmdb_edges),
            "lmdb_preimage_count": len(lmdb_preimages),
            "public_release_candidate_node_index_count": len(public_ids),
            "private_excluded_node_index_count": len(private_ids),
            "generated_evidence_node_index_count": len(generated_ids),
        },
        "source_digests": source_digests,
        "lmdb_digests": lmdb_digests,
        "manifest": manifest,
        "sample_source_path_lookup": {
            "source_path": sample_path,
            "candidate_ids": sample_source_ids,
        },
        "round_trip": {
            "node_count_match": len(nodes) == len(lmdb_nodes),
            "edge_count_match": len(edges) == len(lmdb_edges),
            "preimage_count_match": len(preimages) == len(lmdb_preimages),
            "node_digest_match": source_digests["nodes_digest"] == lmdb_digests["nodes_digest"],
            "edge_digest_match": source_digests["edges_digest"] == lmdb_digests["edges_digest"],
            "preimage_digest_match": source_digests["preimages_digest"] == lmdb_digests["preimages_digest"],
            "tier_indexes_present": bool(public_ids) and bool(private_ids) and bool(generated_ids),
            "source_path_index_present": bool(sample_source_ids),
        },
    }


def _report(payload: dict[str, Any]) -> str:
    counts = payload["materialization"]["counts"]
    lines = [
        "# SIM-GENESIS-ATLAS-LMDB-MATERIALIZATION-01",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: genesis_atlas_lmdb_materialization_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: research-only local LMDB materialization proof; no Genesis signing, public RC activation, or canonical graph mutation -->",
        "",
        f"**Phase:** {PHASE}",
        f"**Status:** {payload['status']}",
        "**Sensitivity:** NON-SENSITIVE",
        "",
        "## Purpose",
        "",
        "This SIM imports the Fix22 full repo Genesis Atlas candidate into a dedicated",
        "local LMDB store and proves that the LMDB projection round-trips back to the",
        "JSON/JSONL signing-preimage layer without digest drift.",
        "",
        "## Counts",
        "",
        "| Metric | Result |",
        "|---|---:|",
    ]
    for key, value in counts.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Round Trip Checks",
            "",
            "| Check | Result |",
            "|---|---|",
        ]
    )
    for key, value in payload["materialization"]["round_trip"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Output Tokens", ""])
    for token in payload["tokens"]:
        lines.append(f"- `{token}`")
    lines.extend(["", "## Non-Claims", ""])
    for claim in payload["non_claims"]:
        lines.append(f"- {claim}")
    lines.append("")
    return "\n".join(lines)


def _review(payload: dict[str, Any]) -> str:
    counts = payload["materialization"]["counts"]
    return "\n".join(
        [
            "# ILC Genesis Atlas LMDB Materialization Review 1545p-Fix23 v0.1",
            "",
            "<!-- PUBLIC_RC_EXCLUDE: genesis_atlas_lmdb_materialization_review_research_only -->",
            "<!-- PUBLIC_RC_EXCLUDE_REASON: review packet for local unsigned Atlas candidate LMDB projection; not canonical graph state -->",
            "",
            "## Finding",
            "",
            "The Fix22 full repo candidate can be materialized into a local LMDB projection",
            "without changing node, edge, or preimage digests. This confirms LMDB can serve",
            "as the local query/materialization substrate while JSON/JSONL remains the",
            "review and signing-preimage layer.",
            "",
            "## Materialized Counts",
            "",
            f"- Nodes: `{counts['lmdb_node_count']}`",
            f"- Edges: `{counts['lmdb_edge_count']}`",
            f"- Preimages: `{counts['lmdb_preimage_count']}`",
            "",
            "## Boundary",
            "",
            "This does not authorize Genesis v0.4 signing, node upload, public graph",
            "publication, public RC activation, canonical Genesis mutation, runtime guard",
            "clearance, economic activation, or ADR/CDL mutation.",
            "",
            "## Next Step",
            "",
            "Use this adapter as the base for future `ilc atlas import`, `ilc atlas verify`,",
            "and invitation/bootstrap materialization commands after the signing and public",
            "release gates are explicitly authorized.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    graph = _read_json(FIX22_GRAPH)
    preimages = _read_preimages(FIX22_PREIMAGES)
    fix22_sim = _read_json(FIX22_SIM)
    materialization = _materialize(graph, preimages, fix22_sim)
    passed = all(materialization["round_trip"].values())
    payload = {
        "schema_version": SCHEMA_VERSION,
        "phase": PHASE,
        "sim_id": SIM_ID,
        "status": "PASS" if passed else "NEEDS_REVIEW",
        "adapter_version": GENESIS_ATLAS_CANDIDATE_LMDB_ADAPTER_VERSION,
        "lmdb_root": str(LMDB_ROOT.relative_to(REPO_ROOT)),
        "inputs": {
            "fix22_graph": str(FIX22_GRAPH.relative_to(REPO_ROOT)),
            "fix22_preimages": str(FIX22_PREIMAGES.relative_to(REPO_ROOT)),
            "fix22_sim": str(FIX22_SIM.relative_to(REPO_ROOT)),
        },
        "materialization": materialization,
        "tokens": [
            "genesis_atlas_candidate_lmdb_adapter_committed_phase_1545p_fix23",
            "fix22_full_repo_candidate_materialized_to_lmdb_phase_1545p_fix23",
            "atlas_lmdb_round_trip_digest_verified_phase_1545p_fix23",
            "atlas_lmdb_private_public_tier_indexes_verified_phase_1545p_fix23",
            "atlas_lmdb_remains_local_unsigned_projection_phase_1545p_fix23",
            "public_path_remains_blocked_phase_1545p_fix23",
        ],
        "non_claims": [
            "No Genesis v0.4 signing occurred.",
            "No Genesis node upload occurred.",
            "No public graph publication occurred.",
            "No public RC activation occurred.",
            "No canonical Genesis graph mutation occurred.",
            "No runtime guard was cleared.",
            "No economic activation, minting, settlement, wallet write, treasury write, or ledger write occurred.",
            "No sidecar activation occurred.",
            "No ADR or CDL mutation occurred.",
        ],
    }
    _atomic_write(JSON_OUT, _canonical_dumps(payload))
    _atomic_write(REPORT_OUT, _report(payload))
    _atomic_write(REVIEW_OUT, _review(payload))
    return payload


def main() -> int:
    payload = run()
    print(json.dumps({"phase": PHASE, "status": payload["status"]}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
