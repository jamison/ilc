#!/usr/bin/env python3
"""Export Fix61 Genesis Atlas projections from the unified LMDB.

PUBLIC_RC_EXCLUDE: fix61_projection_export_package_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas projection export; not Genesis
signing, public graph upload, public RC publication, runtime activation, or
canonical graph mutation.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_lmdb_writer import (  # noqa: E402
    AtlasLmdbSafeWriter,
    AtlasPhaseFileRegistration,
    repo_file_ref_id,
    write_json_atomic,
)


PHASE = "1545p-Fix61"
PHASE_TOKEN = "phase_1545p_fix61"
PREIMAGE_VERSION = "v0.4"
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
CURATED_CANDIDATE_PATH = REPO_ROOT / "out/genesis_core_star_map_v0.4_candidate.json"
FIX55_FIEDLER_PATH = REPO_ROOT / "out/genesis_atlas_fix55_fiedler_projection_analysis_v0.1.json"
FIX56_FIEDLER_PATH = REPO_ROOT / "out/genesis_atlas_fix56_fiedler_rebaseline_report_v0.1.json"
FIX57_FIEDLER_PATH = REPO_ROOT / "out/genesis_atlas_fix57_manual_bridge_edge_application_report_v0.1.json"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"

CORE_OUT = REPO_ROOT / "out/genesis_core_star_map_v0.4.json"
AUTHORITY_OUT = REPO_ROOT / "out/genesis_authority_projection_v0.4.json"
BASE_OUT = REPO_ROOT / "out/genesis_base_graph_v0.4.json"
INDEX_OUT = REPO_ROOT / "out/genesis_core_star_map_index_v0.4.json"
SUMMARY_OUT = REPO_ROOT / "out/genesis_atlas_fix61_projection_summary_v0.1.json"
DIGEST_OUT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified_lmdb_digest_fix61.json"

PUBLIC_ELIGIBLE_PROJECTIONS = {
    "genesis_core_star_map",
    "public_protocol_graph",
    "support_candidate_graph",
}
EXCLUDED_PROJECTIONS = {"excluded_private_material", "review_required"}
INPUT_TOKENS = (
    "fix55_graph_projection_classified",
    "fix55_lmdb_all_nodes_have_graph_projection",
    "fix60_complete",
    "fix60_node_preimages_materialized",
    "fix60_lmdb_preimage_count_equals_node_count",
)
OUTPUT_TOKENS = (
    "fix61_projection_export_package_complete",
    "fix61_core_star_map_json_produced",
    "fix61_base_graph_json_produced",
    "fix61_star_map_index_produced",
    "fix61_complete",
)
CURATED_ALIAS_MAP = {
    "adr:0009_protocol_native_bundle_distribution": "adr:0009_bundle_distribution",
    "adr:0035_type_definition_authority": "cdl:097_type_definition_node_authority",
}
NODE_PREIMAGE_FIELDS = (
    "candidate_id",
    "label",
    "node_kind",
    "graph_projection",
    "canonicality_tier",
    "annotation_method",
    "annotation_phase",
)


def _canonical_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix61_json_object_required:{path}")
    return payload


def _status_text() -> str:
    return STATUS_PATH.read_text(encoding="utf-8")


def _verify_tokens() -> None:
    status = _status_text()
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix61_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix61_output_token_already_present:{token}")
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError(f"fix61_lmdb_missing:{LMDB_ROOT}")
    if not CURATED_CANDIDATE_PATH.exists():
        raise ValueError(f"fix61_curated_candidate_missing:{CURATED_CANDIDATE_PATH}")


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix61_node_candidate_id_missing")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    value = edge.get("source", edge.get("source_candidate_id", edge.get("src", edge.get("from"))))
    if not isinstance(value, str) or not value:
        raise ValueError("fix61_edge_source_missing")
    return value


def _edge_target(edge: dict[str, Any]) -> str:
    value = edge.get("target", edge.get("target_candidate_id", edge.get("tgt", edge.get("to"))))
    if not isinstance(value, str) or not value:
        raise ValueError("fix61_edge_target_missing")
    return value


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type", edge.get("type", edge.get("kind")))
    if not isinstance(value, str) or not value:
        raise ValueError("fix61_edge_type_missing")
    return value


def _edge_id(edge: dict[str, Any]) -> str:
    value = edge.get("edge_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix61_edge_id_missing")
    return value


def _node_preimage(node: dict[str, Any]) -> dict[str, Any]:
    fields = {field: node.get(field) for field in NODE_PREIMAGE_FIELDS}
    node_id = fields["candidate_id"]
    if not isinstance(node_id, str) or not node_id:
        raise ValueError("fix61_node_candidate_id_missing_for_preimage")
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": PREIMAGE_VERSION,
    }


def _edge_preimage(edge: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "edge_id": _edge_id(edge),
        "edge_type": _edge_type(edge),
        "source": _edge_source(edge),
        "target": _edge_target(edge),
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "edge_id": fields["edge_id"],
        "fields": fields,
        "preimage_version": PREIMAGE_VERSION,
    }


def _phase_file_registrations() -> list[AtlasPhaseFileRegistration]:
    evaluator = "tools/evaluators/sim_genesis_atlas_fix61_projection_export_package.py"
    test = "tests/test_phase_1545p_fix61_projection_export_package.py"
    walkthrough = "docs/phases/phase_1545p_fix61_projection_export_package_walkthrough.md"
    return [
        AtlasPhaseFileRegistration(
            path=evaluator,
            node_kind="tooling_source_file_node",
            graph_projection="support_candidate_graph",
            required_edges=(
                ("IMPLEMENTS", repo_file_ref_id("ilc_core/storage/genesis_atlas_lmdb_writer.py")),
                ("USES", repo_file_ref_id("ilc_core/storage/genesis_atlas_candidate_lmdb_adapter.py")),
            ),
        ),
        AtlasPhaseFileRegistration(
            path=test,
            node_kind="test_evidence_node",
            graph_projection="support_candidate_graph",
            required_edges=(("TESTS", repo_file_ref_id(evaluator)),),
        ),
        AtlasPhaseFileRegistration(
            path=walkthrough,
            node_kind="phase_walkthrough_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", f"phase:{PHASE_TOKEN}"),),
        ),
    ]


def _projection_payload(
    *,
    name: str,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    selection_rule: str,
    non_claims: list[str],
    extra_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "edges": edges,
        "metadata": {
            "edge_count": len(edges),
            "node_count": len(nodes),
            "non_claims": non_claims,
            "phase": PHASE,
            "projection": name,
            "selection_rule": selection_rule,
            "source_lmdb": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "status": "PASS",
            **dict(extra_metadata or {}),
        },
        "nodes": nodes,
    }


def _private_node_count(nodes: list[dict[str, Any]]) -> int:
    return sum(1 for node in nodes if str(node.get("graph_projection", "")) in EXCLUDED_PROJECTIONS)


def _verify_public_projection(name: str, nodes: list[dict[str, Any]], token: str) -> None:
    count = _private_node_count(nodes)
    if count:
        raise ValueError(f"{token}:{name}:{count}")


def _internal_edges(edges: list[dict[str, Any]], node_ids: set[str]) -> list[dict[str, Any]]:
    return [edge for edge in edges if _edge_source(edge) in node_ids and _edge_target(edge) in node_ids]


def _authority_source(node_id: str) -> bool:
    return node_id == NODE0 or node_id.startswith("cdl:") or node_id.startswith("adr:")


def _authority_coverage(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    inbound_governs: dict[str, set[str]] = {}
    for edge in edges:
        if _edge_type(edge) != "GOVERNS":
            continue
        source = _edge_source(edge)
        if not _authority_source(source):
            continue
        inbound_governs.setdefault(_edge_target(edge), set()).add(source)

    invariant_ids = [
        _candidate_id(node)
        for node in nodes
        if _candidate_id(node).startswith("invariant:")
        or str(node.get("node_kind", "")) == "operator_primitive"
    ]
    policy_ids = [_candidate_id(node) for node in nodes if _candidate_id(node).startswith("policy:")]
    invariant_with = sum(1 for node_id in invariant_ids if inbound_governs.get(node_id))
    policy_with = sum(1 for node_id in policy_ids if inbound_governs.get(node_id))
    return {
        "invariant_coverage_fraction": invariant_with / len(invariant_ids) if invariant_ids else 1.0,
        "invariant_nodes_total": len(invariant_ids),
        "invariant_nodes_with_governs_inbound": invariant_with,
        "policy_coverage_fraction": policy_with / len(policy_ids) if policy_ids else 1.0,
        "policy_nodes_total": len(policy_ids),
        "policy_nodes_with_governs_inbound": policy_with,
    }


def _degree_index(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    degree = Counter({_candidate_id(node): 0 for node in nodes})
    for edge in edges:
        degree[_edge_source(edge)] += 1
        degree[_edge_target(edge)] += 1
    return [
        {"candidate_id": node_id, "degree": count}
        for node_id, count in sorted(degree.items(), key=lambda item: (-item[1], item[0]))[:20]
    ]


def _curated_core_ids(live_node_ids: set[str]) -> tuple[list[str], list[dict[str, str]]]:
    candidate = _load_json(CURATED_CANDIDATE_PATH)
    raw_nodes = candidate.get("nodes")
    if not isinstance(raw_nodes, list):
        raise ValueError("fix61_curated_candidate_nodes_missing")
    resolved: list[str] = []
    aliases: list[dict[str, str]] = []
    for node in raw_nodes:
        if not isinstance(node, dict):
            raise ValueError("fix61_curated_candidate_node_object_required")
        source_id = _candidate_id(node)
        target_id = CURATED_ALIAS_MAP.get(source_id, source_id)
        if source_id != target_id:
            aliases.append({"candidate_id": source_id, "resolved_to": target_id})
        if target_id not in live_node_ids:
            raise ValueError(f"fix61_curated_core_node_missing_in_lmdb:{source_id}:{target_id}")
        resolved.append(target_id)
    deduped = sorted(set(resolved))
    if len(deduped) != len(resolved):
        raise ValueError("fix61_curated_core_alias_collision")
    if len(deduped) != 57:
        raise ValueError(f"fix61_curated_core_count_unexpected:{len(deduped)}")
    return deduped, aliases


def _fiedler_reference() -> dict[str, Any]:
    if FIX57_FIEDLER_PATH.exists():
        payload = _load_json(FIX57_FIEDLER_PATH)
        fiedler = payload.get("fiedler")
        if isinstance(fiedler, dict) and isinstance(fiedler.get("post_application_lambda2"), (int, float)):
            return {
                "note": "Fix61 does not recompute lambda2 - reference only",
                "source": str(FIX57_FIEDLER_PATH.relative_to(REPO_ROOT)),
                "value": float(fiedler["post_application_lambda2"]),
            }
    if FIX56_FIEDLER_PATH.exists():
        payload = _load_json(FIX56_FIEDLER_PATH)
        projections = payload.get("projections")
        if isinstance(projections, dict):
            public = projections.get("public_eligible")
            if isinstance(public, dict) and isinstance(public.get("lambda2"), (int, float)):
                return {
                    "note": "Fix61 does not recompute lambda2 - reference only",
                    "source": str(FIX56_FIEDLER_PATH.relative_to(REPO_ROOT)),
                    "value": float(public["lambda2"]),
                }
    if FIX55_FIEDLER_PATH.exists():
        payload = _load_json(FIX55_FIEDLER_PATH)
        projections = payload.get("projections")
        if isinstance(projections, dict):
            public = projections.get("public_eligible")
            if isinstance(public, dict) and isinstance(public.get("fiedler_value_lambda2"), (int, float)):
                return {
                    "note": "Fix61 does not recompute lambda2 - reference only",
                    "source": str(FIX55_FIEDLER_PATH.relative_to(REPO_ROOT)),
                    "value": float(public["fiedler_value_lambda2"]),
                }
    return {
        "note": "Fix61 does not recompute lambda2 - reference only",
        "source": "not_available",
        "value": None,
    }


def _digest_for_rows(rows: list[dict[str, Any]]) -> str:
    return _canonical_sha256(rows)


def run() -> dict[str, Any]:
    _verify_tokens()
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        registration_receipt = writer.register_phase_files(
            PHASE,
            _phase_file_registrations(),
            dry_run=False,
        )
        if registration_receipt.get("status") != "PASS":
            raise ValueError("fix61_phase_file_registration_failed")

        nodes = writer.store.iter_nodes()
        edges = writer.store.iter_edges()
        if len(edges) < 74981:
            raise ValueError(f"fix61_edge_count_below_fix55_baseline:{len(edges)}")

        node_preimages = [_node_preimage(node) for node in nodes]
        edge_preimages = [_edge_preimage(edge) for edge in edges]
        node_receipt = writer.write_preimages(
            node_preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "node", "reason": "fix61_support_registration_refresh"},
        )
        edge_receipt = writer.write_preimages(
            edge_preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "edge", "reason": "fix61_support_registration_refresh"},
        )
        if node_receipt.get("status") != "PASS" or edge_receipt.get("status") != "PASS":
            raise ValueError("fix61_preimage_refresh_failed")

        nodes = writer.store.iter_nodes()
        edges = writer.store.iter_edges()
        preimages = writer.store.iter_preimages()
        live_node_by_id = {_candidate_id(node): node for node in nodes}
        live_node_ids = set(live_node_by_id)

        curated_ids, alias_resolution = _curated_core_ids(live_node_ids)
        curated_id_set = set(curated_ids)
        curated_nodes = [live_node_by_id[node_id] for node_id in curated_ids]
        curated_edges = _internal_edges(edges, curated_id_set)
        _verify_public_projection(
            "curated_signing_core",
            curated_nodes,
            "private_node_in_core_star_map",
        )

        authority_nodes = [
            node for node in nodes if str(node.get("graph_projection", "")) == "genesis_core_star_map"
        ]
        authority_ids = {_candidate_id(node) for node in authority_nodes}
        authority_edges = _internal_edges(edges, authority_ids)
        _verify_public_projection(
            "authority_projection",
            authority_nodes,
            "private_node_in_authority_projection",
        )

        base_nodes = [
            node for node in nodes if str(node.get("graph_projection", "")) in PUBLIC_ELIGIBLE_PROJECTIONS
        ]
        base_ids = {_candidate_id(node) for node in base_nodes}
        base_edges = _internal_edges(edges, base_ids)
        _verify_public_projection("public_eligible_base_graph", base_nodes, "private_node_in_base_graph")

        if not curated_id_set.issubset(base_ids) or not authority_ids.issubset(base_ids):
            raise ValueError("core_star_map_not_subset_of_base_graph")

        curated_coverage = _authority_coverage(curated_nodes, curated_edges)
        authority_coverage = _authority_coverage(authority_nodes, authority_edges)
        base_coverage = _authority_coverage(base_nodes, base_edges)
        non_claims = [
            "these json artifacts are local unsigned research outputs",
            "fix61 does not sign publish gossip or activate any artifact",
            "genesis_core_star_map_v0.4.json is the curated signing-core candidate and is distinct from the full authority projection bucket",
            "genesis_authority_projection_v0.4.json is diagnostic/support evidence and is not the 57-node signing core",
            "no cdl mutation signing or runtime activation occurred",
        ]

        core_payload = _projection_payload(
            name="curated_signing_core",
            nodes=curated_nodes,
            edges=curated_edges,
            selection_rule="57-node v0.4 signing core from out/genesis_core_star_map_v0.4_candidate.json with explicit current-LMDB alias resolution",
            non_claims=[
                "genesis_core_star_map_v0.4.json is a curated unsigned signing-core candidate - not a signed artifact",
                "this projection is not final without Genesis authority review and Block 6 signing gate",
            ],
            extra_metadata={"alias_resolution": alias_resolution},
        )
        authority_payload = _projection_payload(
            name="authority_projection",
            nodes=authority_nodes,
            edges=authority_edges,
            selection_rule='graph_projection == "genesis_core_star_map"',
            non_claims=[
                "genesis_authority_projection_v0.4.json is the full authority projection bucket - not the 57-node signing core",
                "this projection is diagnostic/support evidence and is not a signed artifact",
            ],
        )
        base_payload = _projection_payload(
            name="public_eligible_base_graph",
            nodes=base_nodes,
            edges=base_edges,
            selection_rule='graph_projection in {"genesis_core_star_map","public_protocol_graph","support_candidate_graph"}',
            non_claims=[
                "genesis_base_graph_v0.4.json is a local public-eligible unsigned candidate graph",
                "this projection is not a public RC artifact and is not signed",
            ],
        )

        index = {
            "adr_node_inventory": sorted(_candidate_id(node) for node in curated_nodes if _candidate_id(node).startswith("adr:")),
            "authority_coverage": curated_coverage,
            "cdl_node_inventory": sorted(_candidate_id(node) for node in curated_nodes if _candidate_id(node).startswith("cdl:")),
            "edge_count": len(curated_edges),
            "node_count": len(curated_nodes),
            "non_claims": [
                "genesis_core_star_map_v0.4.json is a curated unsigned signing-core candidate - not a signed artifact",
                "genesis_authority_projection_v0.4.json is the full authority projection bucket - not the 57-node signing core",
                "this index is a local research artifact - not a signed or published artifact",
                "genesis_core_star_map_v0.4.json is not final without Genesis authority review and Block 6 signing gate",
            ],
            "phase": PHASE,
            "projection": "curated_signing_core",
            "status": "PASS",
            "top_20_nodes_by_degree": _degree_index(curated_nodes, curated_edges),
        }

        preimage_count = len(preimages)
        expected_preimage_count = len(nodes) + len(edges)
        if preimage_count != expected_preimage_count:
            raise ValueError(f"fix61_preimage_count_mismatch:{preimage_count}:{expected_preimage_count}")

        projection_counts = Counter(str(node.get("graph_projection", "")) for node in nodes)
        summary = {
            "authority_projection_is_subset_of_base_graph": True,
            "curated_alias_resolution": alias_resolution,
            "curated_signing_core_is_subset_of_base_graph": True,
            "lambda2_reference": _fiedler_reference(),
            "lmdb_edge_count_total": len(edges),
            "lmdb_node_count_total": len(nodes),
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "lmdb_preimage_count_total": preimage_count,
            "non_claims": non_claims,
            "phase": PHASE,
            "preimage_refresh": {
                "edge_preimage_count_written": len(edge_preimages),
                "node_preimage_count_written": len(node_preimages),
                "post_refresh_preimage_count": preimage_count,
                "status": "PASS",
            },
            "projection_bucket_counts": dict(sorted(projection_counts.items())),
            "projections": {
                "authority_projection": {
                    "authority_coverage": authority_coverage,
                    "edge_count": len(authority_edges),
                    "node_count": len(authority_nodes),
                    "private_node_count": 0,
                    "private_node_exclusion_proof": "verified_zero_excluded_private_material_nodes",
                },
                "curated_signing_core": {
                    "authority_coverage": curated_coverage,
                    "edge_count": len(curated_edges),
                    "node_count": len(curated_nodes),
                    "private_node_count": 0,
                    "private_node_exclusion_proof": "verified_zero_excluded_private_material_nodes",
                },
                "full_local": {
                    "edge_count": len(edges),
                    "node_count": len(nodes),
                    "note": "full local graph - not exported as separate JSON",
                },
                "public_eligible_base_graph": {
                    "authority_coverage": base_coverage,
                    "edge_count": len(base_edges),
                    "node_count": len(base_nodes),
                    "private_node_count": 0,
                    "private_node_exclusion_proof": "verified_zero_excluded_private_material_nodes",
                },
            },
            "safe_writer_edge_preimage_receipt": edge_receipt,
            "safe_writer_node_preimage_receipt": node_receipt,
            "safe_writer_registration_receipt": registration_receipt,
            "status": "PASS",
        }

        digest = {
            "edge_digest": _digest_for_rows(edges),
            "generated_output_digests": {},
            "lmdb_edge_count": len(edges),
            "lmdb_node_count": len(nodes),
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "lmdb_preimage_count": preimage_count,
            "node_digest": _digest_for_rows(nodes),
            "phase": PHASE,
            "preimage_digest": _digest_for_rows(preimages),
            "status": "PASS",
        }

        write_json_atomic(CORE_OUT, core_payload)
        write_json_atomic(AUTHORITY_OUT, authority_payload)
        write_json_atomic(BASE_OUT, base_payload)
        write_json_atomic(INDEX_OUT, index)
        write_json_atomic(SUMMARY_OUT, summary)
        for output in (CORE_OUT, AUTHORITY_OUT, BASE_OUT, INDEX_OUT, SUMMARY_OUT):
            digest["generated_output_digests"][str(output.relative_to(REPO_ROOT))] = hashlib.sha256(
                output.read_bytes()
            ).hexdigest()
        write_json_atomic(DIGEST_OUT, digest)

        writer.write_metadata("fix61_projection_export_package", summary, phase=PHASE, dry_run=False)
        return summary
    finally:
        writer.close()


def main() -> int:
    summary = run()
    print(
        "Done. "
        f"status={summary['status']}, "
        f"signing_core_nodes={summary['projections']['curated_signing_core']['node_count']}, "
        f"authority_projection_nodes={summary['projections']['authority_projection']['node_count']}, "
        f"base_graph_nodes={summary['projections']['public_eligible_base_graph']['node_count']}, "
        "private_excluded=verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
