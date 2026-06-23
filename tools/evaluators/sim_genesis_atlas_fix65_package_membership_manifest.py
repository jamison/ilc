# SPDX-License-Identifier: AGPL-3.0-only
"""Fix65 Genesis package membership manifest and M0 root.

PUBLIC_RC_EXCLUDE: fix65_package_membership_manifest_local_atlas_maintenance
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB maintenance. No Genesis
signing, public graph upload, public RC activation, runtime activation, ECU
minting, or ILC settlement.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from ilc_core.distribution.genesis_package_manifest import (
    GENESIS_PACKAGE_ARTIFACT_ID,
    GENESIS_PACKAGE_MANIFEST_VERSION,
    build_genesis_package_manifest,
    canonical_sha256,
    file_sha256,
)
from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    AtlasPhaseFileRegistration,
    deterministic_edge_id,
    repo_file_ref_id,
    write_json_atomic,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
PROMPT_PATH = REPO_ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix65_g10_package_membership_manifest.md"
MODULE_PATH = REPO_ROOT / "ilc_core/distribution/genesis_package_manifest.py"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix65_package_membership_manifest.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix65_package_membership_manifest.py"
MANIFEST_PATH = REPO_ROOT / "docs/specs/ilc_fix65_package_membership_manifest_v0.1.json"
REPORT_PATH = REPO_ROOT / "docs/specs/ilc_fix65_package_membership_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix65_package_membership_manifest_walkthrough.md"
PHASE = "1545p-Fix65"
PHASE_TOKEN = "phase_1545p_fix65"
METHOD = "fix65_package_membership_manifest"
PREIMAGE_VERSION = "v0.4"
NODE_PREIMAGE_FIELDS = (
    "candidate_id",
    "label",
    "node_kind",
    "graph_projection",
    "canonicality_tier",
    "annotation_method",
    "annotation_phase",
)
INPUT_TOKENS = (
    "fix63e_complete",
    "fix64_complete",
)
OUTPUT_TOKENS = (
    "fix65_package_membership_manifest_committed",
    "fix65_m0_merkle_root_recorded",
    "fix65_public_rc_exclude_marker_count_reported",
    "fix65_complete",
)


def _status_text() -> str:
    return STATUS_PATH.read_text(encoding="utf-8")


def _verify_tokens() -> None:
    status = _status_text()
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix65_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix65_output_token_already_present:{token}")


def _candidate_id(node: Mapping[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix65_node_candidate_id_missing")
    return value


def _edge_source(edge: Mapping[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix65_edge_source_missing")


def _edge_target(edge: Mapping[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix65_edge_target_missing")


def _edge_type(edge: Mapping[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix65_edge_type_missing")
    return value


def _edge_id(edge: Mapping[str, Any]) -> str:
    value = edge.get("edge_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix65_edge_id_missing")
    return value


def _edge(
    *,
    source: str,
    edge_type: str,
    target: str,
    candidate_status: str = "fix65_package_membership_edge",
) -> dict[str, Any]:
    return {
        "annotation_method": METHOD,
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": candidate_status,
        "confidence": "high",
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "evidence": MANIFEST_PATH.relative_to(REPO_ROOT).as_posix(),
        "source": source,
        "src": source,
        "target": target,
        "tgt": target,
    }


def _artifact_node(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "annotation_method": METHOD,
        "annotation_phase": PHASE_TOKEN,
        "candidate_id": GENESIS_PACKAGE_ARTIFACT_ID,
        "candidate_status": "fix65_unsigned_pre_rc_package_membership_manifest",
        "creator_agent_id": "genesis_agent:01",
        "genesis_attested": False,
        "graph_delta": "support_only_until_signing",
        "graph_projection": "public_protocol_graph",
        "label": "Genesis package membership Merkle root v0.4",
        "manifest_sha256": manifest["manifest_sha256"],
        "merkle_root_m0": manifest["merkle_root_m0"],
        "node_kind": "package_membership_manifest_artifact",
        "package_member_count": manifest["member_count"],
        "public_rc_exclude_marker_count": manifest["public_rc_exclude_marker_count"],
        "schema_version": manifest["schema_version"],
        "tier": "public_protocol_candidate",
    }


def _artifact_edges(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    edges = [
        _edge(
            source=GENESIS_PACKAGE_ARTIFACT_ID,
            edge_type="REFERENCES_AUTHORITY",
            target="adr:0009_bundle_distribution",
        ),
        _edge(
            source=GENESIS_PACKAGE_ARTIFACT_ID,
            edge_type="CLASSIFIED_BY",
            target="policy:public_path_still_blocked_phase_1545p",
        ),
    ]
    for member in manifest["members"]:
        edges.append(
            _edge(
                source=GENESIS_PACKAGE_ARTIFACT_ID,
                edge_type="CONTAINS_FILE",
                target=member["candidate_id"],
            )
        )
    return edges


def _phase_file_registrations() -> list[AtlasPhaseFileRegistration]:
    return [
        AtlasPhaseFileRegistration(
            path=PROMPT_PATH.relative_to(REPO_ROOT),
            node_kind="phase_prompt_node",
            graph_projection="support_candidate_graph",
            graph_delta="support_only",
            required_edges=(("CARRIES_FORWARD", GENESIS_PACKAGE_ARTIFACT_ID),),
        ),
        AtlasPhaseFileRegistration(
            path=MODULE_PATH.relative_to(REPO_ROOT),
            node_kind="runtime_source_file_node",
            graph_projection="support_candidate_graph",
            graph_delta="support_only",
            required_edges=(("IMPLEMENTS", GENESIS_PACKAGE_ARTIFACT_ID),),
        ),
        AtlasPhaseFileRegistration(
            path=EVALUATOR_PATH.relative_to(REPO_ROOT),
            node_kind="tooling_source_file_node",
            graph_projection="support_candidate_graph",
            graph_delta="support_only",
            required_edges=(("IMPLEMENTS", GENESIS_PACKAGE_ARTIFACT_ID),),
        ),
        AtlasPhaseFileRegistration(
            path=TEST_PATH.relative_to(REPO_ROOT),
            node_kind="test_evidence_node",
            graph_projection="support_candidate_graph",
            graph_delta="support_only",
            required_edges=(("TESTS", GENESIS_PACKAGE_ARTIFACT_ID),),
        ),
        AtlasPhaseFileRegistration(
            path=MANIFEST_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            graph_delta="support_only",
            required_edges=(("EVIDENCES", GENESIS_PACKAGE_ARTIFACT_ID),),
        ),
        AtlasPhaseFileRegistration(
            path=REPORT_PATH.relative_to(REPO_ROOT),
            node_kind="spec_document_node",
            graph_projection="support_candidate_graph",
            graph_delta="support_only",
            required_edges=(("EVIDENCES", GENESIS_PACKAGE_ARTIFACT_ID),),
        ),
        AtlasPhaseFileRegistration(
            path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            node_kind="phase_walkthrough_node",
            graph_projection="support_candidate_graph",
            graph_delta="support_only",
            required_edges=(("EVIDENCES", GENESIS_PACKAGE_ARTIFACT_ID),),
        ),
        AtlasPhaseFileRegistration(
            path=STATUS_PATH.relative_to(REPO_ROOT),
            node_kind="phase_status_log",
            graph_projection="support_candidate_graph",
            graph_delta="support_only",
            skip_carries_forward=True,
        ),
    ]


def _repo_file_node_for_path(path: str) -> dict[str, Any]:
    absolute = REPO_ROOT / path
    sha256 = file_sha256(absolute)
    return {
        "annotation_method": METHOD,
        "annotation_phase": PHASE_TOKEN,
        "candidate_id": f"repo:file:{sha256[:16]}:{_path_slug(path)}",
        "candidate_status": "fix65_phase_file_repo_counterpart",
        "creator_agent_id": "genesis_agent:01",
        "genesis_attested": False,
        "graph_delta": "support_only",
        "graph_projection": "support_candidate_graph",
        "label": path,
        "node_kind": _node_kind_for_path(path),
        "size_bytes": absolute.stat().st_size,
        "source_identity_status": "content_addressed_at_fix65_phase_registration",
        "source_path": path,
        "source_sha256": sha256,
        "tier": "support_candidate",
    }


def _path_slug(path: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in path.lower()).strip("_")


def _public_protocol_current_file_node(
    *,
    stale_node: Mapping[str, Any],
    path: str,
    actual_sha256: str,
) -> dict[str, Any]:
    absolute = REPO_ROOT / path
    node = dict(stale_node)
    node.update(
        {
            "annotation_method": METHOD,
            "annotation_phase": PHASE_TOKEN,
            "candidate_id": f"repo:file:{actual_sha256[:16]}:{_path_slug(path)}",
            "candidate_status": "fix65_public_protocol_current_source_hash_node",
            "graph_projection": "public_protocol_graph",
            "label": path,
            "node_kind": str(stale_node.get("node_kind") or _node_kind_for_path(path)),
            "size_bytes": absolute.stat().st_size,
            "source_identity_status": "current_content_addressed_at_fix65",
            "source_path": path,
            "source_sha256": actual_sha256,
            "supersedes_source_hash_node": str(stale_node["candidate_id"]),
            "tier": str(stale_node.get("tier") or "public_protocol_candidate"),
        }
    )
    node.pop("superseded_by", None)
    node.pop("superseded_source_sha256", None)
    return node


def _repair_public_protocol_source_hashes(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    """Repair stale public-protocol repo:file hashes before M0 selection."""

    nodes = writer.store.iter_nodes()
    node_by_id = {_candidate_id(node): node for node in nodes}
    by_path_and_hash = {
        (str(node.get("source_path")), str(node.get("source_sha256"))): node
        for node in nodes
        if str(node.get("candidate_id", "")).startswith("repo:file:")
        and isinstance(node.get("source_path"), str)
        and isinstance(node.get("source_sha256"), str)
    }
    nodes_to_add: list[dict[str, Any]] = []
    edges_to_add: list[dict[str, Any]] = []
    updates: dict[str, dict[str, Any]] = {}
    repairs: list[dict[str, str]] = []

    for node in nodes:
        candidate_id = _candidate_id(node)
        if not candidate_id.startswith("repo:file:"):
            continue
        if node.get("graph_projection") != "public_protocol_graph":
            continue
        path = node.get("source_path")
        recorded_sha256 = node.get("source_sha256")
        if not isinstance(path, str) or not isinstance(recorded_sha256, str):
            continue
        absolute = REPO_ROOT / path
        if not absolute.is_file():
            continue
        actual_sha256 = file_sha256(absolute)
        if actual_sha256 == recorded_sha256:
            continue

        existing_current = by_path_and_hash.get((path, actual_sha256))
        if existing_current is not None:
            current_id = _candidate_id(existing_current)
            updates[current_id] = {
                "annotation_method": METHOD,
                "annotation_phase": PHASE_TOKEN,
                "candidate_status": "fix65_public_protocol_current_source_hash_promoted",
                "graph_projection": "public_protocol_graph",
                "node_kind": str(node.get("node_kind") or _node_kind_for_path(path)),
                "source_identity_status": "current_content_addressed_at_fix65",
                "supersedes_source_hash_node": candidate_id,
            }
        else:
            current_node = _public_protocol_current_file_node(
                stale_node=node,
                path=path,
                actual_sha256=actual_sha256,
            )
            current_id = _candidate_id(current_node)
            if current_id not in node_by_id:
                nodes_to_add.append(current_node)
                node_by_id[current_id] = current_node

        updates[candidate_id] = {
            "annotation_method": METHOD,
            "annotation_phase": PHASE_TOKEN,
            "candidate_status": "fix65_superseded_public_protocol_source_hash",
            "graph_delta": "support_only_superseded_source_hash",
            "graph_projection": "support_candidate_graph",
            "source_identity_status": "superseded_by_current_source_hash_at_fix65",
            "superseded_by": current_id,
            "superseded_source_sha256": actual_sha256,
        }
        edges_to_add.append(
            _edge(
                source=current_id,
                edge_type="DERIVED_FROM",
                target=candidate_id,
                candidate_status="fix65_current_source_hash_derives_from_superseded_node",
            )
        )
        repairs.append(
            {
                "actual_source_sha256": actual_sha256,
                "current_candidate_id": current_id,
                "recorded_source_sha256": recorded_sha256,
                "source_path": path,
                "superseded_candidate_id": candidate_id,
            }
        )

    add_receipt = writer.apply_plan(
        AtlasLmdbWritePlan(
            nodes_to_add=nodes_to_add,
            edges_to_add=edges_to_add,
            metadata={"operation": "fix65_public_protocol_source_hash_repair"},
            phase=f"{PHASE}:public_protocol_source_hash_repair",
            dry_run=False,
        )
    )
    if add_receipt["status"] != "PASS" or add_receipt["rejected_edge_count"]:
        raise ValueError(f"fix65_source_hash_repair_add_failed:{add_receipt}")
    update_receipt = writer.update_node_fields(
        updates,
        phase=f"{PHASE}:public_protocol_source_hash_repair",
        dry_run=False,
        metadata={"operation": "fix65_public_protocol_source_hash_repair"},
    )
    if update_receipt["status"] != "PASS" or update_receipt["rejected_update_count"]:
        raise ValueError(f"fix65_source_hash_repair_update_failed:{update_receipt}")
    return {
        "add_receipt": add_receipt,
        "created_current_node_count": len(nodes_to_add),
        "promoted_existing_node_count": sum(
            1 for repair in repairs if repair["current_candidate_id"] not in {node["candidate_id"] for node in nodes_to_add}
        ),
        "repair_count": len(repairs),
        "repairs": repairs,
        "status": "PASS",
        "update_receipt": update_receipt,
    }


def _node_kind_for_path(path: str) -> str:
    suffix = Path(path).suffix
    if path.startswith("ilc_core/") and suffix == ".py":
        return "runtime_source_file_node"
    if path.startswith("tests/") and suffix == ".py":
        return "test_evidence_node"
    if path.startswith("tools/") and suffix == ".py":
        return "tooling_source_file_node"
    if path.startswith("docs/antigravity_tasks/"):
        return "phase_prompt_node"
    if path.startswith("docs/phases/"):
        return "phase_walkthrough_node" if "walkthrough" in path else "phase_status_log"
    if path.startswith("docs/specs/") and suffix == ".json":
        return "spec_json_artifact_node"
    if path.startswith("docs/specs/") and suffix == ".md":
        return "spec_document_node"
    return "repo_material_node"


def _phase_file_same_source_plan(writer: AtlasLmdbSafeWriter) -> AtlasLmdbWritePlan:
    nodes = writer.store.iter_nodes()
    edges = writer.store.iter_edges()
    existing_by_path = {
        str(node.get("source_path")): _candidate_id(node)
        for node in nodes
        if str(node.get("candidate_id", "")).startswith("repo:file:")
        and isinstance(node.get("source_path"), str)
        and node.get("source_path")
    }
    edge_semantics = {(_edge_source(edge), _edge_type(edge), _edge_target(edge)) for edge in edges}
    nodes_to_add: list[dict[str, Any]] = []
    edges_to_add: list[dict[str, Any]] = []
    for registration in _phase_file_registrations():
        path = Path(registration.path).as_posix()
        file_ref_id = repo_file_ref_id(path)
        target_id = existing_by_path.get(path)
        if target_id is None:
            node = _repo_file_node_for_path(path)
            target_id = node["candidate_id"]
            nodes_to_add.append(node)
            existing_by_path[path] = target_id
        semantic = (file_ref_id, "SAME_SOURCE", target_id)
        if semantic not in edge_semantics:
            edges_to_add.append(
                _edge(
                    source=file_ref_id,
                    edge_type="SAME_SOURCE",
                    target=target_id,
                    candidate_status="fix65_phase_file_same_source_identity_edge",
                )
            )
    return AtlasLmdbWritePlan(
        nodes_to_add=nodes_to_add,
        edges_to_add=edges_to_add,
        metadata={"operation": "fix65_phase_file_same_source_resolution"},
        phase=f"{PHASE}:phase_file_same_source",
        dry_run=False,
    )


def _node_preimage(node: Mapping[str, Any]) -> dict[str, Any]:
    fields = {field: node.get(field) for field in NODE_PREIMAGE_FIELDS}
    node_id = fields["candidate_id"]
    if not isinstance(node_id, str) or not node_id:
        raise ValueError("fix65_node_candidate_id_missing_for_preimage")
    return {
        "canonical_sha256": canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": PREIMAGE_VERSION,
    }


def _edge_preimage(edge: Mapping[str, Any]) -> dict[str, Any]:
    fields = {
        "edge_id": _edge_id(edge),
        "edge_type": _edge_type(edge),
        "source": _edge_source(edge),
        "target": _edge_target(edge),
    }
    return {
        "canonical_sha256": canonical_sha256(fields),
        "edge_id": fields["edge_id"],
        "fields": fields,
        "preimage_version": PREIMAGE_VERSION,
    }


def _write_report(manifest: Mapping[str, Any], receipts: Mapping[str, Any]) -> None:
    lines = [
        "# Phase 1545p-Fix65 Package Membership Report",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: fix65_package_membership_report -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Local unsigned package-membership report; no public RC activation or signing authority. -->",
        "",
        f"- Schema version: `{manifest['schema_version']}`",
        f"- Artifact: `{manifest['artifact_id']}`",
        f"- Member count: `{manifest['member_count']}`",
        f"- M0 Merkle root: `{manifest['merkle_root_m0']}`",
        f"- Manifest SHA-256: `{manifest['manifest_sha256']}`",
        f"- PUBLIC_RC_EXCLUDE marker count: `{manifest['public_rc_exclude_marker_count']}`",
        f"- Public-protocol source hash repairs: `{receipts['source_hash_repair']['repair_count']}`",
        f"- LMDB artifact edge receipt: `{receipts['artifact_application']['status']}`",
        f"- Phase file registration: `{receipts['phase_file_registration']['status']}`",
        f"- Phase file SAME_SOURCE receipt: `{receipts['phase_file_same_source']['status']}`",
        f"- Node preimage receipt: `{receipts['node_preimages']['status']}`",
        f"- Edge preimage receipt: `{receipts['edge_preimages']['status']}`",
        "",
        "## Non-Claims",
        "",
        "- This report does not sign the package manifest.",
        "- This report does not authorize public RC or public distribution.",
        "- PUBLIC_RC_EXCLUDE marker count remains a blocker for a public-clean package claim.",
    ]
    repairs = receipts["source_hash_repair"].get("repairs", [])
    if repairs:
        lines.extend(["", "## Source Hash Repairs", ""])
        for repair in repairs:
            lines.append(
                "- "
                f"`{repair['source_path']}`: superseded "
                f"`{repair['superseded_candidate_id']}` with "
                f"`{repair['current_candidate_id']}`."
            )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_walkthrough(manifest: Mapping[str, Any], final_info: Mapping[str, Any]) -> None:
    lines = [
        "# Phase 1545p-Fix65 Package Membership Manifest Walkthrough",
        "",
        "## Summary",
        "",
        "Fix65 generated an unsigned pre-RC package-membership manifest over the live unified Atlas LMDB public-protocol file set.",
        "",
        "## Results",
        "",
        f"- Member count: `{manifest['member_count']}`",
        f"- M0 Merkle root: `{manifest['merkle_root_m0']}`",
        f"- Manifest SHA-256: `{manifest['manifest_sha256']}`",
        f"- PUBLIC_RC_EXCLUDE marker count: `{manifest['public_rc_exclude_marker_count']}`",
        f"- Post-run LMDB nodes: `{final_info['node_count']}`",
        f"- Post-run LMDB edges: `{final_info['edge_count']}`",
        f"- Post-run dangling edges: `{final_info['dangling_edge_count']}`",
        f"- Post-run edge ID debt: `{final_info['edge_id_debt_count']}`",
        "",
        "## Verification",
        "",
        "- `python -m py_compile ilc_core/distribution/genesis_package_manifest.py tools/evaluators/sim_genesis_atlas_fix65_package_membership_manifest.py`",
        "- `python tools/evaluators/sim_genesis_atlas_fix65_package_membership_manifest.py`",
        "- `python -m pytest tests/test_phase_1545p_fix65_package_membership_manifest.py -q`",
        "",
        "No ellipses in walkthrough.",
    ]
    WALKTHROUGH_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _append_status(manifest: Mapping[str, Any]) -> None:
    text = _status_text()
    if "fix65_complete" in text:
        return
    lines = [
        "",
        "### Phase 1545p-Fix65 — Package Membership Manifest",
        "",
        "**Status:** complete",
        "",
        (
            "**Output:** Generated the unsigned pre-RC Genesis package membership "
            f"manifest over `{manifest['member_count']}` public-protocol files, "
            f"recorded M0 `{manifest['merkle_root_m0']}`, reported "
            f"`{manifest['public_rc_exclude_marker_count']}` PUBLIC_RC_EXCLUDE "
            "markers as a public-clean blocker, registered phase files in LMDB, "
            "refreshed preimages, and preserved all non-activation boundaries."
        ),
        "",
        "**Tokens:** " + ",".join(OUTPUT_TOKENS),
        "",
    ]
    STATUS_PATH.write_text(text.rstrip() + "\n" + "\n".join(lines), encoding="utf-8")


def run() -> dict[str, Any]:
    _verify_tokens()
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        source_hash_repair = _repair_public_protocol_source_hashes(writer)
        nodes = writer.store.iter_nodes()
        manifest = build_genesis_package_manifest(nodes, repo_root=REPO_ROOT)
        if manifest["member_count"] <= 0:
            raise ValueError("fix65_manifest_empty")
        write_json_atomic(MANIFEST_PATH, manifest)

        artifact_plan = AtlasLmdbWritePlan(
            nodes_to_add=[_artifact_node(manifest)],
            edges_to_add=_artifact_edges(manifest),
            metadata={"operation": "fix65_package_membership_artifact"},
            phase=PHASE,
            dry_run=False,
        )
        artifact_receipt = writer.apply_plan(artifact_plan)
        if artifact_receipt["status"] != "PASS" or artifact_receipt["rejected_edge_count"]:
            raise ValueError(f"fix65_artifact_application_failed:{artifact_receipt}")

        receipts: dict[str, Any] = {
            "artifact_application": artifact_receipt,
            "source_hash_repair": source_hash_repair,
        }
        _write_report(manifest, {
            **receipts,
            "phase_file_registration": {"status": "PENDING"},
            "phase_file_same_source": {"status": "PENDING"},
            "node_preimages": {"status": "PENDING"},
            "edge_preimages": {"status": "PENDING"},
        })
        _write_walkthrough(manifest, writer.inspect())
        _append_status(manifest)

        phase_registration = writer.register_phase_files(PHASE, _phase_file_registrations(), dry_run=False)
        if phase_registration["status"] != "PASS" or phase_registration["rejected_edge_count"]:
            raise ValueError(f"fix65_phase_file_registration_failed:{phase_registration}")
        receipts["phase_file_registration"] = phase_registration

        same_source_receipt = writer.apply_plan(_phase_file_same_source_plan(writer))
        if same_source_receipt["status"] != "PASS" or same_source_receipt["rejected_edge_count"]:
            raise ValueError(f"fix65_phase_file_same_source_failed:{same_source_receipt}")
        receipts["phase_file_same_source"] = same_source_receipt

        current_nodes = writer.store.iter_nodes()
        current_edges = writer.store.iter_edges()
        node_receipt = writer.write_preimages(
            [_node_preimage(node) for node in current_nodes],
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "node", "reason": "fix65_package_manifest_mutation"},
        )
        edge_receipt = writer.write_preimages(
            [_edge_preimage(edge) for edge in current_edges],
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "edge", "reason": "fix65_package_manifest_mutation"},
        )
        receipts["node_preimages"] = node_receipt
        receipts["edge_preimages"] = edge_receipt
        _write_report(manifest, receipts)
        final_info = writer.inspect()
        _write_walkthrough(manifest, final_info)
        return {
            "final_lmdb": final_info,
            "manifest": {
                "manifest_sha256": manifest["manifest_sha256"],
                "member_count": manifest["member_count"],
                "merkle_root_m0": manifest["merkle_root_m0"],
                "public_rc_exclude_marker_count": manifest["public_rc_exclude_marker_count"],
            },
            "receipts": receipts,
            "status": "PASS",
        }
    finally:
        writer.close()


def main() -> int:
    print(json.dumps(run(), allow_nan=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
