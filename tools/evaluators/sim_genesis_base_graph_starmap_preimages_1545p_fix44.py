#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Build Fix44 star-map index, node preimages, and signing packet.

PUBLIC_RC_EXCLUDE: genesis_base_graph_starmap_preimages_fix44_research_only
PUBLIC_RC_EXCLUDE_REASON: Unsigned candidate signing-packet preparation only;
no Genesis signing, canonical graph mutation, public graph publication, public
RC activation, runtime activation, minting, settlement, or ADR/CDL mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE = "1545p-Fix44"
SCHEMA_VERSION = "genesis_base_graph_starmap_preimages_1545p_fix44.v0.1"

CANDIDATE = REPO_ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json"
LMDB_REEXPORT = REPO_ROOT / "out/genesis_base_graph_v0.4_lmdb_reexport.json"
LMDB_DIGEST = REPO_ROOT / "out/genesis_base_graph_v0.4_lmdb_digest.json"
CORE_STAR_MAP = REPO_ROOT / "out/genesis_core_star_map_v0.4_candidate.json"
FIX43_QUEUE = REPO_ROOT / "out/genesis_base_graph_fix44_target_queue.json"
STAR_MAP_OUT = REPO_ROOT / "out/genesis_base_graph_v0.4_star_map_index.json"
PREIMAGE_OUT = REPO_ROOT / "out/genesis_base_graph_v0.4_node_preimages.jsonl"
SIGNING_PACKET_OUT = REPO_ROOT / "docs/specs/ilc_genesis_base_graph_v04_signing_packet.md"
WALKTHROUGH_OUT = REPO_ROOT / "docs/phases/phase_1545p_fix44_starmap_signing_packet_walkthrough.md"

FIX41A_SHA256 = "3bcf8cdf248ea44248e72dce0c8209c92302826399b42524235cf8ee59936e52"
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"

TOKENS = [
    "fix44_star_map_index_produced",
    "fix44_node_preimages_produced",
    "fix44_signing_packet_committed",
    "fix44_digest_equivalence_tests_passing",
    "fix44_complete",
    "genesis_base_graph_v04_candidate_pipeline_complete",
    "public_path_remains_blocked_phase_1545p_fix44",
]

NON_CLAIMS = [
    "No Genesis signing occurred.",
    "No signed genesis_base_graph_v0.4.json artifact was produced.",
    "No canonical Atlas mutation occurred.",
    "No public graph publication occurred.",
    "No public repository push occurred.",
    "No public RC activation occurred.",
    "No runtime, economic, sidecar, network, ADR, or CDL activation occurred.",
    "The star-map index is a derived navigation artifact and is not authority-bearing.",
]


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _pretty_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        tmp_path.unlink(missing_ok=True)
        raise


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix44_json_object_required:{path}")
    return payload


def _node_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id") or node.get("node_id") or node.get("id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix44_node_missing_candidate_id")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    value = edge.get("source_candidate_id") or edge.get("source") or edge.get("from")
    return value if isinstance(value, str) else ""


def _edge_target(edge: dict[str, Any]) -> str:
    value = edge.get("target_candidate_id") or edge.get("target") or edge.get("to")
    return value if isinstance(value, str) else ""


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type") or edge.get("type")
    return value if isinstance(value, str) and value else "UNKNOWN"


def _node_kind(node: dict[str, Any]) -> str:
    return str(node.get("node_kind") or node.get("category") or "unknown")


def _tier(node: dict[str, Any]) -> str:
    return str(node.get("tier") or "unknown")


def _tier_group(node: dict[str, Any]) -> str:
    tier = _tier(node).lower()
    canonicality_tier = str(node.get("canonicality_tier", "")).lower()
    node_kind = _node_kind(node).lower()
    sensitivity = str(node.get("sensitivity", "")).lower()
    inclusion_status = str(node.get("inclusion_status", "")).lower()
    if tier == "genesis_core" or "genesis_core" in canonicality_tier:
        return "canonical"
    if (
        "private" in tier
        or "excluded" in tier
        or "private" in sensitivity
        or "public_rc_exclude" in sensitivity
        or "excluded" in inclusion_status
    ):
        return "private"
    if "test" in node_kind:
        return "support"
    return "support"


def _annotation_method(node: dict[str, Any]) -> str:
    if node.get("manually_annotated") is True:
        return "manual_reviewed"
    if node.get("prepass_annotated") is True:
        return "semantic_prepass"
    source_phase = str(node.get("source_phase") or node.get("phase") or "")
    if source_phase:
        return source_phase
    if str(node.get("node_kind", "")).startswith("repo_"):
        return "scripted_repo_crawl"
    return "unspecified"


def _is_authority_spine_node(node_id: str, node: dict[str, Any]) -> bool:
    if node_id == NODE0:
        return True
    prefix = node_id.split(":", 1)[0]
    if prefix in {"truth_primitive", "policy", "adr", "cdl", "genesis_agent", "ceremony"}:
        return True
    category = str(node.get("category", "")).lower()
    node_kind = str(node.get("node_kind", "")).lower()
    tier = _tier(node).lower()
    return (
        "authority" in category
        or "policy" in category
        or "authority" in node_kind
        or tier == "genesis_core"
    )


def _edge_id(edge: dict[str, Any], index: int) -> str:
    value = edge.get("edge_id")
    if isinstance(value, str) and value:
        return value
    return "synthetic:" + hashlib.sha256(_canonical_json({"index": index, "edge": edge}).encode("utf-8")).hexdigest()[:32]


def _edge_adjacency(edges: list[dict[str, Any]], edge_ids_by_index: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for index, edge in enumerate(edges):
        edge_id = edge_ids_by_index[index]
        source = _edge_source(edge)
        target = _edge_target(edge)
        if source:
            result.setdefault(source, []).append(edge_id)
        if target and target != source:
            result.setdefault(target, []).append(edge_id)
    return {node_id: sorted(set(edge_ids)) for node_id, edge_ids in result.items()}


def _build_star_map(candidate: dict[str, Any], candidate_sha256: str, lmdb_digest: dict[str, Any]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = candidate["nodes"]
    edges: list[dict[str, Any]] = candidate["edges"]
    by_node_type: dict[str, list[str]] = {}
    by_exact_tier: dict[str, list[str]] = {}
    by_tier = {"canonical": [], "support": [], "private": []}
    by_annotation_method: dict[str, list[str]] = {}
    authority_spine_nodes: list[str] = []

    for node in nodes:
        node_id = _node_id(node)
        by_node_type.setdefault(_node_kind(node), []).append(node_id)
        by_exact_tier.setdefault(_tier(node), []).append(node_id)
        by_tier[_tier_group(node)].append(node_id)
        by_annotation_method.setdefault(_annotation_method(node), []).append(node_id)
        if _is_authority_spine_node(node_id, node):
            authority_spine_nodes.append(node_id)

    edges_by_type: dict[str, list[str]] = {}
    for index, edge in enumerate(edges):
        edges_by_type.setdefault(_edge_type(edge), []).append(_edge_id(edge, index))

    for mapping in (by_node_type, by_exact_tier, by_tier, by_annotation_method, edges_by_type):
        for key, values in mapping.items():
            mapping[key] = sorted(set(values))

    return {
        "artifact_class": "star_map_index",
        "derived_from": "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json",
        "derivation_phase": "fix44",
        "edge_count": len(edges),
        "format_version": "genesis_base_graph_star_map_index.v0.4_candidate",
        "index": {
            "authority_spine_nodes": sorted(set(authority_spine_nodes)),
            "by_annotation_method": dict(sorted(by_annotation_method.items())),
            "by_exact_tier": dict(sorted(by_exact_tier.items())),
            "by_node_type": dict(sorted(by_node_type.items())),
            "by_tier": by_tier,
            "edges_by_type": dict(sorted(edges_by_type.items())),
        },
        "is_authority_bearing": False,
        "metadata": {
            "candidate_sha256": candidate_sha256,
            "lmdb_digest_sha256": lmdb_digest.get("digests", {}).get("reexport_canonical_sha256"),
            "non_claim": "Derived navigation index only; signed JSON and node preimages are the future signing inputs.",
            "source_candidate": "fix41a",
            "source_candidate_status": candidate.get("candidate_status"),
        },
        "node_count": len(nodes),
        "note": "Derived navigation index. Source of truth: future signed genesis_base_graph_v0.4.json plus genesis_base_graph_v0.4_node_preimages.jsonl.",
        "schema_version": SCHEMA_VERSION,
    }


def _build_preimages(candidate: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    nodes: list[dict[str, Any]] = candidate["nodes"]
    edges: list[dict[str, Any]] = candidate["edges"]
    edge_ids_by_index = [_edge_id(edge, index) for index, edge in enumerate(edges)]
    edge_adjacency = _edge_adjacency(edges, edge_ids_by_index)
    preimages: list[dict[str, Any]] = []
    pending_count = 0

    for node in sorted(nodes, key=_node_id):
        node_id = _node_id(node)
        preimage_payload = {
            "candidate_source": "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json",
            "edge_ids": edge_adjacency.get(node_id, []),
            "node": node,
            "node_id": node_id,
            "preimage_schema_version": "genesis_base_graph_node_preimage.v0.4_candidate",
            "source_phase": "1545p-Fix44",
        }
        preimage = _canonical_json(preimage_payload).rstrip("\n")
        pending_count += 1
        preimages.append(
            {
                "cid": "pending_float_free_dag_cbor_preimage_contract",
                "cid_status": "pending",
                "node_id": node_id,
                "preimage": preimage,
                "preimage_encoding": "canonical_json_utf8",
                "preimage_sha256": _sha256_text(preimage),
                "source_phase": "fix44",
            }
        )

    summary = {
        "cid_pending_count": pending_count,
        "cid_pending_reason": "candidate node records contain floats and JSON-only metadata; Fix44 does not invent a lossy DAG-CBOR normalization before a ratified preimage contract",
        "preimage_count": len(preimages),
    }
    return preimages, summary


def _classify_counts(candidate: dict[str, Any], core_star_map: dict[str, Any]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = candidate["nodes"]
    edges: list[dict[str, Any]] = candidate["edges"]
    private_nodes = {_node_id(node) for node in nodes if _tier_group(node) == "private"}
    public_nodes = {_node_id(node) for node in nodes if _tier_group(node) != "private"}
    review_edges = [
        edge for edge in edges if str(edge.get("candidate_status", "")).lower() in {"fix38_proposed", "fix41a_proposed"}
    ]
    private_edges = [
        edge for edge in edges if _edge_source(edge) in private_nodes or _edge_target(edge) in private_nodes
    ]
    public_edges = [
        edge for edge in edges if _edge_source(edge) in public_nodes and _edge_target(edge) in public_nodes
    ]
    return {
        "base_graph_edge_count": len(edges),
        "base_graph_node_count": len(nodes),
        "core_star_map_edge_count": len(core_star_map.get("edges", [])),
        "core_star_map_node_count": len(core_star_map.get("nodes", [])),
        "private_edge_count": len(private_edges),
        "private_node_count": len(private_nodes),
        "public_release_fit_edge_count": len(public_edges),
        "public_release_fit_node_count": len(public_nodes),
        "review_only_edge_count": len(review_edges),
        "review_only_edge_status_counts": dict(Counter(str(edge.get("candidate_status", "")) for edge in review_edges)),
        "tier_group_counts": dict(Counter(_tier_group(node) for node in nodes)),
        "tier_counts": dict(Counter(_tier(node) for node in nodes)),
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    _atomic_write(path, "".join(_canonical_json(row) for row in rows))


def _signing_packet(
    *,
    counts: dict[str, Any],
    candidate_sha256: str,
    lmdb_digest: dict[str, Any],
    queue: dict[str, Any],
    star_map_sha256: str,
    preimage_sha256: str,
    preimage_summary: dict[str, Any],
) -> str:
    tier_group_counts = counts["tier_group_counts"]
    tier_counts = counts["tier_counts"]
    queue_count = queue.get("entry_count")
    return f"""# ILC Genesis Base Graph v0.4 Signing Packet

<!-- PUBLIC_RC_EXCLUDE: genesis_base_graph_v04_signing_packet_unsigned_candidate -->
<!-- PUBLIC_RC_EXCLUDE_REASON: Human decision packet for a future signing gate; no public RC or graph publication is authorized by this document. -->

**Status:** UNSIGNED CANDIDATE SIGNING PACKET
**Phase:** 1545p-Fix44
**Source candidate:** `out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json`
**Source SHA-256:** `{candidate_sha256}`

## Boundary

This packet is a proposal for the later Phase 1573 signing gate. It does not
sign any artifact, produce `out/genesis_base_graph_v0.4.json`, ratify CDL-098,
authorize public RC, publish a graph, or mutate the canonical Atlas.

## Artifact Inputs

| Artifact | Role | SHA-256 or digest |
|---|---|---|
| `out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json` | unsigned source candidate | `{candidate_sha256}` |
| `out/genesis_base_graph_v0.4_lmdb_reexport.json` | LMDB round-trip re-export | `{lmdb_digest.get('digests', {}).get('reexport_canonical_sha256')}` |
| `out/genesis_base_graph_v0.4_star_map_index.json` | derived navigation index | `{star_map_sha256}` |
| `out/genesis_base_graph_v0.4_node_preimages.jsonl` | deterministic node preimages | `{preimage_sha256}` |

## What Is Core

The core Genesis star-map candidate remains the separate Fix18/Fix41-compatible
core artifact: `out/genesis_core_star_map_v0.4_candidate.json`.

| Core artifact metric | Count |
|---|---:|
| Core star-map nodes | `{counts['core_star_map_node_count']}` |
| Core star-map edges | `{counts['core_star_map_edge_count']}` |

This core artifact is Phase 1573 Artifact 1 and is CDL-098-independent.

## What Is Base Graph

The base graph candidate is the full Fix41a enriched candidate.

| Base graph metric | Count |
|---|---:|
| Nodes | `{counts['base_graph_node_count']}` |
| Edges | `{counts['base_graph_edge_count']}` |
| Canonical tier-group nodes | `{tier_group_counts.get('canonical', 0)}` |
| Support tier-group nodes | `{tier_group_counts.get('support', 0)}` |
| Private tier-group nodes | `{tier_group_counts.get('private', 0)}` |

This base graph is Phase 1573 Artifact 2 and requires CDL-098 or equivalent
Genesis graph update authority before signing.

## What Is Private Or Local

Private/local material remains in the local candidate for completeness and
private Genesis custody. It must not appear in the public export profile.

| Private/local metric | Count |
|---|---:|
| Private/local nodes | `{counts['private_node_count']}` |
| Edges touching private/local nodes | `{counts['private_edge_count']}` |

## What Is Public-Release-Fit

Public-release-fit here means non-private under the current tier-group
classifier. It is still unsigned candidate material, not public release
authorization.

| Public-release-fit candidate metric | Count |
|---|---:|
| Nodes | `{counts['public_release_fit_node_count']}` |
| Edges with both endpoints public-release-fit | `{counts['public_release_fit_edge_count']}` |

## What Remains Review-Only

Review-only material includes proposed candidate traces from Fix38/Fix41a that
have not been promoted to authority-bearing canonical graph state.

| Review-only metric | Count |
|---|---:|
| Review-only candidate edges | `{counts['review_only_edge_count']}` |

Review-only edge status counts:

```json
{json.dumps(counts['review_only_edge_status_counts'], sort_keys=True, indent=2, allow_nan=False)}
```

## Tier Distribution

```json
{json.dumps(tier_counts, sort_keys=True, indent=2, allow_nan=False)}
```

## Node Preimage Status

| Preimage metric | Count |
|---|---:|
| Preimage rows | `{preimage_summary['preimage_count']}` |
| CID pending rows | `{preimage_summary['cid_pending_count']}` |

CID derivation remains pending because the current candidate node records
contain floats and JSON-only metadata. Fix44 preserves canonical JSON preimages
and does not invent a lossy DAG-CBOR normalization before a ratified preimage
contract exists.

## Fix43 Target Queue Carry-Forward

`out/genesis_base_graph_fix44_target_queue.json` is present with
`entry_count={queue_count}`. It is not consumed by this signing-packet phase.
Targeted percolation annotation of those low-PageRank protocol-relevant nodes
is deferred to Fix44a or Fix45.

## Human Decision Required

Before Phase 1573 signs Artifact 2, Genesis must confirm or modify this packet:

- whether the Fix41a base graph is the correct signing candidate;
- whether private/local nodes remain local-only;
- whether review-only candidate edges remain unsigned support material;
- whether CDL-098 or equivalent authority is in force for base graph signing;
- whether CID derivation should proceed from the current canonical JSON
  preimages or wait for a ratified float-free DAG-CBOR preimage contract.

## Non-Claims

{chr(10).join(f'- {claim}' for claim in NON_CLAIMS)}
"""


def _walkthrough(
    *,
    counts: dict[str, Any],
    preimage_summary: dict[str, Any],
    star_map: dict[str, Any],
    queue: dict[str, Any],
    candidate_sha256: str,
) -> str:
    tier_group_counts = counts["tier_group_counts"]
    return f"""# Phase 1545p-Fix44: Star-Map Index and Signing Packet Walkthrough

## Status

COMPLETE.

Fix44 produced the derived star-map index, deterministic node preimage JSONL,
and unsigned Genesis base graph signing packet for the Fix41a candidate. No
Genesis signing, canonical graph mutation, public graph publication, public RC
activation, runtime/economic/network/sidecar activation, or ADR/CDL mutation
occurred.

## Inputs

- Source candidate: `out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json`
- Source SHA-256: `{candidate_sha256}`
- Fix41 LMDB: `out/genesis_base_graph_v0.4.lmdb/`
- Fix43 carry-forward queue: `out/genesis_base_graph_fix44_target_queue.json`

## Star-Map Index

| Metric | Count |
|---|---:|
| Nodes | `{star_map['node_count']}` |
| Edges | `{star_map['edge_count']}` |
| Authority spine nodes | `{len(star_map['index']['authority_spine_nodes'])}` |
| Canonical tier-group nodes | `{len(star_map['index']['by_tier']['canonical'])}` |
| Support tier-group nodes | `{len(star_map['index']['by_tier']['support'])}` |
| Private tier-group nodes | `{len(star_map['index']['by_tier']['private'])}` |

The star-map index has `is_authority_bearing=false` and is a derived navigation
projection only.

## Node Preimages

| Metric | Count |
|---|---:|
| Preimage JSONL rows | `{preimage_summary['preimage_count']}` |
| CID pending rows | `{preimage_summary['cid_pending_count']}` |

All rows currently use `cid=pending_float_free_dag_cbor_preimage_contract`.
Reason: `{preimage_summary['cid_pending_reason']}`.

## Signing Packet Summary

| Section | Count |
|---|---:|
| Core star-map nodes | `{counts['core_star_map_node_count']}` |
| Core star-map edges | `{counts['core_star_map_edge_count']}` |
| Base graph nodes | `{counts['base_graph_node_count']}` |
| Base graph edges | `{counts['base_graph_edge_count']}` |
| Private/local nodes | `{counts['private_node_count']}` |
| Private/local edges | `{counts['private_edge_count']}` |
| Public-release-fit candidate nodes | `{counts['public_release_fit_node_count']}` |
| Public-release-fit candidate edges | `{counts['public_release_fit_edge_count']}` |
| Review-only candidate edges | `{counts['review_only_edge_count']}` |

## Fix43 Carry-Forward

`out/genesis_base_graph_fix44_target_queue.json` is present with
`entry_count={queue.get('entry_count')}`. This phase did not consume or modify
that queue. Targeted percolation annotation of those 500 protocol-relevant
low-PageRank nodes is deferred to Fix44a or Fix45.

## Digest Equivalence Tests

The Fix44 pytest suite verifies:

- Candidate SHA-256 matches the Fix41a expected SHA-256.
- LMDB re-export canonical digest matches the candidate canonical digest.
- Every candidate node has exactly one preimage JSONL row.
- Every star-map index node appears in the candidate.
- The star-map index is not authority-bearing.
- The Fix43 target queue remains present with 500 entries.

## Tokens

{chr(10).join(f'- `{token}`' for token in TOKENS)}

## Non-Claims

{chr(10).join(f'- {claim}' for claim in NON_CLAIMS)}
"""


def run(
    *,
    candidate_path: Path = CANDIDATE,
    lmdb_reexport_path: Path = LMDB_REEXPORT,
    lmdb_digest_path: Path = LMDB_DIGEST,
    core_star_map_path: Path = CORE_STAR_MAP,
    queue_path: Path = FIX43_QUEUE,
    star_map_out: Path = STAR_MAP_OUT,
    preimage_out: Path = PREIMAGE_OUT,
    signing_packet_out: Path = SIGNING_PACKET_OUT,
    walkthrough_out: Path = WALKTHROUGH_OUT,
) -> dict[str, Any]:
    candidate = _load_json(candidate_path)
    lmdb_reexport = _load_json(lmdb_reexport_path)
    lmdb_digest = _load_json(lmdb_digest_path)
    core_star_map = _load_json(core_star_map_path)
    queue = _load_json(queue_path)

    candidate_sha256 = _sha256_file(candidate_path)
    if candidate_sha256 != FIX41A_SHA256:
        raise ValueError(f"fix44_unexpected_fix41a_sha256:{candidate_sha256}")
    if _canonical_json(candidate) != _canonical_json(lmdb_reexport):
        raise ValueError("fix44_lmdb_reexport_candidate_mismatch")
    if lmdb_digest.get("digests", {}).get("source_file_sha256") != candidate_sha256:
        raise ValueError("fix44_lmdb_digest_source_sha_mismatch")
    if queue.get("entry_count") != 500:
        raise ValueError("fix44_target_queue_entry_count_mismatch")

    star_map = _build_star_map(candidate, candidate_sha256, lmdb_digest)
    preimages, preimage_summary = _build_preimages(candidate)
    counts = _classify_counts(candidate, core_star_map)

    _atomic_write(star_map_out, _pretty_json(star_map))
    _write_jsonl(preimage_out, preimages)
    star_map_sha256 = _sha256_file(star_map_out)
    preimage_sha256 = _sha256_file(preimage_out)
    _atomic_write(
        signing_packet_out,
        _signing_packet(
            counts=counts,
            candidate_sha256=candidate_sha256,
            lmdb_digest=lmdb_digest,
            preimage_sha256=preimage_sha256,
            preimage_summary=preimage_summary,
            queue=queue,
            star_map_sha256=star_map_sha256,
        ),
    )
    _atomic_write(
        walkthrough_out,
        _walkthrough(
            counts=counts,
            preimage_summary=preimage_summary,
            star_map=star_map,
            queue=queue,
            candidate_sha256=candidate_sha256,
        ),
    )

    return {
        "counts": counts,
        "non_claims": NON_CLAIMS,
        "preimage_summary": preimage_summary,
        "queue_entry_count": queue.get("entry_count"),
        "schema_version": SCHEMA_VERSION,
        "sha256": {
            "candidate": candidate_sha256,
            "node_preimages": preimage_sha256,
            "star_map_index": star_map_sha256,
        },
        "status": "PASS",
        "tokens": TOKENS,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Fix44 star-map/preimage/signing-packet builder.")
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    args = parser.parse_args()
    payload = run(candidate_path=args.candidate)
    print(_canonical_json(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
