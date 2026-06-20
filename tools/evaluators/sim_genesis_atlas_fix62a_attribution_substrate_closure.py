#!/usr/bin/env python3
"""Close the Genesis Atlas creator/provenance substrate gap.

PUBLIC_RC_EXCLUDE: fix62a_attribution_substrate_closure_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Genesis Atlas LMDB maintenance pass;
not Genesis signing, public graph upload, canonical graph mutation, runtime
activation, public serving, ECU minting, or public RC publication.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_lmdb_writer import (  # noqa: E402
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    AtlasPhaseFileRegistration,
    deterministic_edge_id,
    write_json_atomic,
)


PHASE = "1545p-Fix62a"
PHASE_TOKEN = "phase_1545p_fix62a"
GENESIS_AGENT_ID = "genesis_agent:01"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62a_attribution_substrate_closure_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62a_manual_graph_finish_queue_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62a_attribution_substrate_closure_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62a_attribution_substrate_closure_walkthrough.md"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix62a_attribution_substrate_closure.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix62a_attribution_substrate_closure.py"

INPUT_TOKENS = ("fix61_complete",)
OUTPUT_TOKENS = (
    "fix62a_attribution_substrate_closure_complete",
    "fix62a_creator_resolution_manifest_materialized",
    "fix62a_manual_graph_finish_queue_produced",
    "fix62a_complete",
)
PUBLIC_ELIGIBLE_PROJECTIONS = frozenset(
    {"genesis_core_star_map", "public_protocol_graph", "support_candidate_graph"}
)
PRIVATE_OR_REVIEW_PROJECTIONS = frozenset({"excluded_private_material", "review_required"})
CREATOR_FIELDS = (
    "creator_agent_id",
    "created_by_agent",
    "author_agent_id",
    "submitter_agent_id",
    "authored_by",
    "attributed_to_agent_id",
)
ROLE_TRACE_EDGE_TYPES = frozenset(
    {
        "GOVERNS",
        "ATTESTATION",
        "IMPLEMENTS",
        "TESTS",
        "EVIDENCES",
        "REFERENCES_AUTHORITY",
        "DERIVED_FROM",
        "CLASSIFIED_BY",
        "CARRIES_FORWARD",
        "PROVENANCE",
    }
)
AUTHORITY_FORWARD_EDGE_TYPES = frozenset({"GOVERNS", "ATTESTATION"})
AUTHORITY_PREFIXES = ("cdl:", "adr:", "policy:", "invariant:", "artifact:", "truth_primitive:")


ECU_RUNTIME_BINDINGS = (
    (
        "ilc_core/economics/passive_ecu_attribution_runtime.py",
        (
            ("IMPLEMENTS", "adr:0023_multi_layer_quality_signal_architecture"),
            ("REFERENCES_AUTHORITY", "cdl:060_gossip_centrality_extension"),
        ),
    ),
    (
        "ilc_core/economics/epoch_attribution_settle_runtime.py",
        (
            ("IMPLEMENTS", "cdl:081_hyperedge_ecu_attribution"),
            ("IMPLEMENTS", "cdl:084_provenance_chain_attribution"),
            ("REFERENCES_AUTHORITY", "adr:0037_genesis_canonical_lineage_contract"),
        ),
    ),
    (
        "ilc_core/analysis/node_value_kernel.py",
        (
            ("IMPLEMENTS", "adr:0008_node_usefulness_governance_weight_genesis_dilution"),
            ("REFERENCES_AUTHORITY", "adr:0012_ecu_ilc_graph_coupling_anti_reflexivity"),
        ),
    ),
    (
        "ilc_core/network/d2d/centrality_delta_gossip_runtime.py",
        (
            ("IMPLEMENTS", "cdl:060_gossip_centrality_extension"),
            ("REFERENCES_AUTHORITY", "cdl:078_relay_incentive_constitutional_lock"),
        ),
    ),
    (
        "ilc_core/analysis/genesis_accrual_governor.py",
        (
            ("IMPLEMENTS", "policy:genesis_accrual_governor"),
            ("REFERENCES_AUTHORITY", "adr:0008_node_usefulness_governance_weight_genesis_dilution"),
        ),
    ),
    (
        "ilc_core/analysis/governance_weight.py",
        (
            ("IMPLEMENTS", "cdl:013_governance_weight"),
            ("REFERENCES_AUTHORITY", "adr:0008_node_usefulness_governance_weight_genesis_dilution"),
        ),
    ),
    (
        "ilc_core/analysis/freshness_gate.py",
        (
            ("IMPLEMENTS", "policy:freshness_gate_contract"),
            ("REFERENCES_AUTHORITY", "adr:0008_node_usefulness_governance_weight_genesis_dilution"),
        ),
    ),
)


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _status_text() -> str:
    return STATUS_PATH.read_text(encoding="utf-8")


def _verify_tokens() -> None:
    status = _status_text()
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix62a_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix62a_output_token_already_present:{token}")
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError(f"fix62a_lmdb_missing:{LMDB_ROOT}")


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62a_node_missing_candidate_id")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62a_edge_source_missing")


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62a_edge_target_missing")


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62a_edge_type_missing")
    return value


def _is_public_eligible(node: dict[str, Any]) -> bool:
    return str(node.get("graph_projection", "")) in PUBLIC_ELIGIBLE_PROJECTIONS


def _has_creator(node: dict[str, Any]) -> bool:
    return any(isinstance(node.get(field), str) and node.get(field) for field in CREATOR_FIELDS)


def _source_path(node: dict[str, Any]) -> str:
    for key in ("source_path", "path", "repo_path"):
        value = node.get(key)
        if isinstance(value, str):
            return value
    return ""


def _work_family(node_id: str, node: dict[str, Any]) -> str:
    path = _source_path(node)
    for prefix in ("docs/specs/", "docs/adr/", "docs/phases/", "docs/sims/", "ilc_core/", "tests/", "tools/"):
        if path.startswith(prefix):
            parts = path.split("/")
            return "/".join(parts[:2]) if len(parts) > 1 else prefix.rstrip("/")
    if node_id.startswith("cdl:"):
        return "semantic/cdl"
    if node_id.startswith("adr:"):
        return "semantic/adr"
    if node_id.startswith("policy:"):
        return "semantic/policy"
    if node_id.startswith("invariant:"):
        return "semantic/invariant"
    return "semantic/other"


def _creator_updates(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    updates: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if not _is_public_eligible(node):
            continue
        if _has_creator(node):
            continue
        node_id = _candidate_id(node)
        path = _source_path(node)
        if node_id.startswith("repo:file"):
            basis = "genesis_source_tree_file_lineage"
        elif path:
            basis = "genesis_source_tree_path_lineage"
        else:
            basis = "genesis_semantic_node_lineage"
        updates[node_id] = {
            "creator_agent_id": GENESIS_AGENT_ID,
            "creator_attribution_basis": basis,
            "creator_attribution_phase": PHASE_TOKEN,
            "creator_attribution_scope": "public_or_support_eligible_genesis_atlas_node",
            "creator_attribution_status": "resolved_by_genesis_attribution_substrate_closure",
            "creator_attribution_version": "fix62a_attribution_substrate_closure_v0.1",
        }
    return updates


def _runtime_binding_edges(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_path: dict[str, str] = {}
    node_ids = {_candidate_id(node) for node in nodes}
    for node in nodes:
        path = _source_path(node)
        if path:
            by_path[path] = _candidate_id(node)

    edges: list[dict[str, Any]] = []
    for path, bindings in ECU_RUNTIME_BINDINGS:
        source = by_path.get(path)
        if not source:
            continue
        for edge_type, target in bindings:
            if target not in node_ids:
                continue
            edges.append(
                {
                    "annotation_method": "fix62a_ecu_runtime_binding_strike_force",
                    "annotation_phase": PHASE_TOKEN,
                    "candidate_status": "fix62a_high_confidence_runtime_binding",
                    "edge_type": edge_type,
                    "source": source,
                    "target": target,
                }
            )
    return edges


def _authority_forward_reachable(node_ids: set[str], edges: list[dict[str, Any]]) -> set[str]:
    root = "artifact:genesis_intent_attestation_init_authority_map"
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if _edge_type(edge) in AUTHORITY_FORWARD_EDGE_TYPES:
            adjacency[_edge_source(edge)].append(_edge_target(edge))
    seen = {root} if root in node_ids else set()
    queue: deque[str] = deque(seen)
    while queue:
        node_id = queue.popleft()
        for target in adjacency.get(node_id, []):
            if target in node_ids and target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def _manual_queue(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    node_by_id = {_candidate_id(node): node for node in nodes}
    node_ids = set(node_by_id)
    reachable = _authority_forward_reachable(node_ids, edges)
    outbound_role = Counter()
    inbound_role = Counter()
    for edge in edges:
        if _edge_type(edge) in ROLE_TRACE_EDGE_TYPES:
            outbound_role[_edge_source(edge)] += 1
            inbound_role[_edge_target(edge)] += 1

    entries: list[dict[str, Any]] = []
    for node_id, node in sorted(node_by_id.items()):
        projection = str(node.get("graph_projection", ""))
        if projection in PRIVATE_OR_REVIEW_PROJECTIONS:
            continue
        node_kind = str(node.get("node_kind", ""))
        reasons: list[str] = []
        priority = 99
        if node_id.startswith(AUTHORITY_PREFIXES) and node_id not in reachable:
            reasons.append("authority_forward_trace_missing")
            priority = min(priority, 0 if node_id.startswith(("cdl:", "adr:", "artifact:")) else 1)
        if outbound_role[node_id] == 0 and projection == "public_protocol_graph":
            reasons.append("public_protocol_outbound_role_trace_missing")
            priority = min(priority, 2)
        if outbound_role[node_id] == 0 and inbound_role[node_id] == 0:
            reasons.append("semantic_role_trace_isolated")
            priority = min(priority, 3)
        if not reasons:
            continue
        entries.append(
            {
                "batch_id": "",
                "candidate_id": node_id,
                "graph_projection": projection,
                "node_kind": node_kind,
                "path": _source_path(node),
                "priority": priority,
                "recommended_manual_action": _recommended_action(node_id, node, reasons),
                "reasons": reasons,
                "work_family": _work_family(node_id, node),
            }
        )

    entries.sort(key=lambda item: (item["priority"], item["work_family"], item["path"], item["candidate_id"]))
    for index, entry in enumerate(entries, start=1):
        entry["queue_index"] = index
        entry["batch_id"] = f"fix62a_batch_{((index - 1) // 10) + 1:04d}"
    return entries


def _recommended_action(node_id: str, node: dict[str, Any], reasons: list[str]) -> str:
    if "authority_forward_trace_missing" in reasons:
        if node_id.startswith(("cdl:", "adr:")):
            return "manual_read_canonical_status_then_add_or_defer_NODE0_GOVERNS"
        if node_id.startswith(("policy:", "invariant:")):
            return "manual_read_source_evidence_then_add_CDL_or_ADR_GOVERNS_or_CLASSIFIED_BY"
        return "manual_read_authority_role_then_add_typed_trace_or_defer"
    if str(node.get("graph_projection")) == "public_protocol_graph":
        return "manual_read_file_then_add_IMPLEMENTs_REFERENCES_AUTHORITY_DERIVED_FROM_or_TESTS"
    return "manual_read_if_public_release_critical_else_classify_support_only"


def _node_preimage(node: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "annotation_method": node.get("annotation_method"),
        "annotation_phase": node.get("annotation_phase"),
        "canonicality_tier": node.get("canonicality_tier"),
        "candidate_id": node.get("candidate_id"),
        "creator_agent_id": node.get("creator_agent_id"),
        "creator_attribution_basis": node.get("creator_attribution_basis"),
        "creator_attribution_phase": node.get("creator_attribution_phase"),
        "creator_attribution_scope": node.get("creator_attribution_scope"),
        "creator_attribution_status": node.get("creator_attribution_status"),
        "graph_projection": node.get("graph_projection"),
        "label": node.get("label"),
        "node_kind": node.get("node_kind"),
    }
    node_id = fields["candidate_id"]
    if not isinstance(node_id, str) or not node_id:
        raise ValueError("fix62a_node_preimage_candidate_id_missing")
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": "v0.4.fix62a_attribution",
    }


def _edge_preimage(edge: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "edge_id": edge.get("edge_id"),
        "edge_type": _edge_type(edge),
        "source": _edge_source(edge),
        "target": _edge_target(edge),
    }
    edge_id = fields["edge_id"]
    if not isinstance(edge_id, str) or not edge_id:
        edge_id = deterministic_edge_id(fields["source"], fields["edge_type"], fields["target"])
        fields["edge_id"] = edge_id
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "edge_id": edge_id,
        "fields": fields,
        "preimage_version": "v0.4.fix62a_attribution",
    }


def _queue_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "batch_size": 10,
        "entries": entries,
        "entry_count": len(entries),
        "non_claims": [
            "queue entries are manual review targets, not canonical graph defects by themselves",
            "no ECU entitlement is granted by this queue",
            "manual reads may add typed edges, defer nodes, or classify support-only",
        ],
        "phase": PHASE,
        "priority_counts": dict(Counter(str(entry["priority"]) for entry in entries)),
        "reason_counts": dict(Counter(reason for entry in entries for reason in entry["reasons"])),
        "work_family_counts": dict(Counter(entry["work_family"] for entry in entries)),
    }


def _report_markdown(report: dict[str, Any]) -> str:
    reason_counts = report["manual_queue"]["reason_counts"]
    priority_counts = report["manual_queue"]["priority_counts"]
    final_counts = report.get("final_counts") or {}
    runtime_binding_edges = report.get("runtime_binding_edges") or {}
    return "\n".join(
        [
            "# ILC Fix62a Attribution Substrate Closure Report v0.1",
            "",
            "## Summary",
            "",
            f"- Phase: `{PHASE}`",
            f"- LMDB: `{report['lmdb_path']}`",
            f"- Public/support-eligible nodes: `{report['public_eligible_node_count']}`",
            f"- Creator field updates accepted: `{report['creator_updates']['accepted_update_count']}`",
            f"- Public/support-eligible nodes with creator after closure: `{report.get('public_eligible_with_creator_after', 'pending')}`",
            f"- ECU/runtime semantic edges accepted: `{runtime_binding_edges.get('accepted_edge_count', 0)}`",
            f"- ECU/runtime semantic edges present: `{report.get('runtime_binding_semantics_present_count', 'pending')}`",
            f"- Manual graph-finish queue entries: `{report['manual_queue']['entry_count']}`",
            f"- Final LMDB nodes: `{final_counts.get('nodes', 'pending')}`",
            f"- Final LMDB edges: `{final_counts.get('edges', 'pending')}`",
            f"- Final preimages: `{final_counts.get('preimages', 'pending')}`",
            "",
            "## Interpretation",
            "",
            "Fix62a does not add static ECU entitlement metadata. It materializes the",
            "creator/provenance substrate needed by future REUSE, PROVENANCE, centrality,",
            "and quality-factor attribution machinery.",
            "",
            "## Manual Queue Counts",
            "",
            f"- Priority counts: `{json.dumps(priority_counts, sort_keys=True)}`",
            f"- Reason counts: `{json.dumps(reason_counts, sort_keys=True)}`",
            "",
            "## Non-Claims",
            "",
            "- No Genesis signing occurred.",
            "- No public graph upload occurred.",
            "- No public RC activation occurred.",
            "- No ECU minting, settlement, or entitlement was authorized.",
            "- No ADR or CDL was mutated.",
            "",
        ]
    )


def _write_text_atomic(path: Path, text: str) -> None:
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
            if not text.endswith("\n"):
                handle.write("\n")
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _walkthrough_markdown(report: dict[str, Any]) -> str:
    final_counts = report.get("final_counts") or {}
    runtime_binding_edges = report.get("runtime_binding_edges") or {}
    return "\n".join(
        [
            "# Phase 1545p-Fix62a Attribution Substrate Closure Walkthrough",
            "",
            "## Commands",
            "",
            "- `python tools/evaluators/sim_genesis_atlas_fix62a_attribution_substrate_closure.py`",
            "- `python -m pytest tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py tests/test_phase_1545p_fix62a_attribution_substrate_closure.py -q`",
            "",
            "## Results",
            "",
            f"- Creator updates accepted: `{report['creator_updates']['accepted_update_count']}`",
            f"- Public/support-eligible nodes with creator after closure: `{report.get('public_eligible_with_creator_after', 'pending')}`",
            f"- Runtime binding edges accepted: `{runtime_binding_edges.get('accepted_edge_count', 0)}`",
            f"- Runtime binding edges present: `{report.get('runtime_binding_semantics_present_count', 'pending')}`",
            f"- Manual queue entries: `{report['manual_queue']['entry_count']}`",
            f"- LMDB nodes: `{final_counts.get('nodes', 'pending')}`",
            f"- LMDB edges: `{final_counts.get('edges', 'pending')}`",
            f"- Preimages: `{final_counts.get('preimages', 'pending')}`",
            "",
            "## Boundary",
            "",
            "Fix62a is local unsigned Atlas LMDB maintenance. It does not sign, publish,",
            "activate, mint ECU, settle economics, mutate ADR/CDL state, or authorize",
            "public RC.",
            "",
        ]
    )


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(
            path=EVALUATOR_PATH.relative_to(REPO_ROOT),
            node_kind="tooling_source_file_node",
            graph_projection="support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix62a"),),
        ),
        AtlasPhaseFileRegistration(
            path=TEST_PATH.relative_to(REPO_ROOT),
            node_kind="test_evidence_node",
            graph_projection="support_candidate_graph",
            required_edges=(("TESTS", "phase:1545p_fix62a"),),
        ),
        AtlasPhaseFileRegistration(
            path=REPORT_MD_PATH.relative_to(REPO_ROOT),
            node_kind="spec_document_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62a"),),
        ),
        AtlasPhaseFileRegistration(
            path=QUEUE_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62a"),),
        ),
        AtlasPhaseFileRegistration(
            path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            node_kind="phase_walkthrough_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62a"),),
        ),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def run() -> dict[str, Any]:
    _verify_tokens()
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        initial_nodes = writer.store.iter_nodes()
        initial_edges = writer.store.iter_edges()
        public_eligible = [node for node in initial_nodes if _is_public_eligible(node)]
        updates = _creator_updates(initial_nodes)
        update_receipt = writer.update_node_fields(
            updates,
            phase=PHASE,
            dry_run=False,
            metadata={"operation": "genesis_creator_attribution_substrate_closure"},
        )
        if update_receipt.get("status") != "PASS":
            raise ValueError("fix62a_creator_update_receipt_failed")

        nodes_after_updates = writer.store.iter_nodes()
        runtime_edges = _runtime_binding_edges(nodes_after_updates)
        edge_receipt = writer.apply_plan(
            AtlasLmdbWritePlan(
                edges_to_add=runtime_edges,
                metadata={"operation": "ecu_runtime_semantic_binding"},
                phase=PHASE,
                dry_run=False,
            )
        )
        if edge_receipt.get("status") != "PASS":
            raise ValueError("fix62a_runtime_binding_receipt_failed")

        nodes_after_edges = writer.store.iter_nodes()
        edges_after_edges = writer.store.iter_edges()
        runtime_binding_semantics = {
            (edge["source"], edge["edge_type"], edge["target"])
            for edge in _runtime_binding_edges(nodes_after_edges)
        }
        observed_semantics = {
            (_edge_source(edge), _edge_type(edge), _edge_target(edge))
            for edge in edges_after_edges
        }
        runtime_binding_semantics_present_count = len(
            runtime_binding_semantics & observed_semantics
        )
        queue_entries = _manual_queue(nodes_after_edges, edges_after_edges)
        queue_payload = _queue_payload(queue_entries)
        write_json_atomic(QUEUE_PATH, queue_payload)

        provisional_report = {
            "creator_updates": update_receipt,
            "final_counts": {},
            "initial_counts": {"edges": len(initial_edges), "nodes": len(initial_nodes)},
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "manual_queue": {
                "entry_count": queue_payload["entry_count"],
                "priority_counts": queue_payload["priority_counts"],
                "reason_counts": queue_payload["reason_counts"],
                "work_family_counts": queue_payload["work_family_counts"],
            },
            "non_claims": [
                "creator_attribution_fields_are_not_static_ecu_entitlements",
                "fix62a_does_not_authorize_ecu_minting_or_settlement",
                "manual_queue_entries_require_follow_on_read_or_defer_disposition",
            ],
            "phase": PHASE,
            "public_eligible_node_count": len(public_eligible),
            "public_eligible_with_creator_after": sum(
                1 for node in nodes_after_edges if _is_public_eligible(node) and _has_creator(node)
            ),
            "runtime_binding_edges": edge_receipt,
            "runtime_binding_semantics_expected_count": len(runtime_binding_semantics),
            "runtime_binding_semantics_present_count": runtime_binding_semantics_present_count,
            "status": "PASS",
        }
        _write_text_atomic(REPORT_MD_PATH, _report_markdown(provisional_report))
        _write_text_atomic(WALKTHROUGH_PATH, _walkthrough_markdown(provisional_report))

        registration_receipt = _register_phase_files(writer)
        if registration_receipt.get("status") != "PASS":
            raise ValueError("fix62a_phase_file_registration_failed")

        registered_nodes = writer.store.iter_nodes()
        post_registration_updates = _creator_updates(registered_nodes)
        post_registration_update_receipt = writer.update_node_fields(
            post_registration_updates,
            phase=PHASE,
            dry_run=False,
            metadata={"operation": "post_phase_file_registration_creator_closure"},
        )
        if post_registration_update_receipt.get("status") != "PASS":
            raise ValueError("fix62a_post_registration_creator_update_failed")

        final_nodes = writer.store.iter_nodes()
        final_edges = writer.store.iter_edges()
        node_preimages = [_node_preimage(node) for node in final_nodes]
        edge_preimages = [_edge_preimage(edge) for edge in final_edges]
        node_preimage_receipt = writer.write_preimages(
            node_preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "node_attribution_refreshed"},
        )
        edge_preimage_receipt = writer.write_preimages(
            edge_preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "edge_attribution_refreshed"},
        )
        if node_preimage_receipt.get("status") != "PASS" or edge_preimage_receipt.get("status") != "PASS":
            raise ValueError("fix62a_preimage_refresh_failed")

        final_preimages = writer.store.iter_preimages()
        report = dict(provisional_report)
        report["final_counts"] = {
            "edges": len(final_edges),
            "nodes": len(final_nodes),
            "preimages": len(final_preimages),
        }
        report["phase_file_registration"] = registration_receipt
        report["post_registration_creator_updates"] = post_registration_update_receipt
        report["preimage_refresh"] = {
            "edge_preimages_written": len(edge_preimages),
            "node_preimages_written": len(node_preimages),
            "safe_writer_edge_preimage_receipt": edge_preimage_receipt,
            "safe_writer_node_preimage_receipt": node_preimage_receipt,
        }
        report["post_closure_creator_missing_public_eligible"] = sum(
            1 for node in final_nodes if _is_public_eligible(node) and not _has_creator(node)
        )
        write_json_atomic(OUT_REPORT_PATH, report)
        write_json_atomic(QUEUE_PATH, queue_payload)
        _write_text_atomic(REPORT_MD_PATH, _report_markdown(report))
        _write_text_atomic(WALKTHROUGH_PATH, _walkthrough_markdown(report))
        writer.write_metadata("fix62a_attribution_substrate_closure", report, phase=PHASE, dry_run=False)
        return report
    finally:
        writer.close()


def main() -> int:
    report = run()
    print(
        "Done. "
        f"status={report['status']}, "
        f"creator_updates={report['creator_updates']['accepted_update_count']}, "
        f"runtime_edges={report['runtime_binding_edges']['accepted_edge_count']}, "
        f"manual_queue={report['manual_queue']['entry_count']}, "
        f"nodes={report['final_counts']['nodes']}, "
        f"edges={report['final_counts']['edges']}, "
        f"preimages={report['final_counts']['preimages']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
