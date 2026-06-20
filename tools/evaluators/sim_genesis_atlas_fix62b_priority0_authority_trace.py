#!/usr/bin/env python3
"""Repair the highest-priority Genesis Atlas authority trace gaps.

PUBLIC_RC_EXCLUDE: fix62b_priority0_authority_trace_research_only
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


PHASE = "1545p-Fix62b"
PHASE_TOKEN = "phase_1545p_fix62b"
ROOT = "artifact:genesis_intent_attestation_init_authority_map"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
INPUT_QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62a_manual_graph_finish_queue_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62b_priority0_authority_trace_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62b_manual_graph_finish_queue_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62b_priority0_authority_trace_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62b_priority0_authority_trace_walkthrough.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62b_priority0_authority_trace_v0.1.json"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix62b_priority0_authority_trace.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix62b_priority0_authority_trace.py"

INPUT_TOKENS = ("fix62a_complete",)
OUTPUT_TOKENS = (
    "fix62b_priority0_authority_trace_complete",
    "fix62b_priority0_manual_ledger_materialized",
    "fix62b_lmdb_edges_applied",
    "fix62b_complete",
)
AUTHORITY_FORWARD_EDGE_TYPES = frozenset({"GOVERNS", "ATTESTATION"})
TYPED_TRACE_EDGE_TYPES = frozenset(
    {
        "GOVERNS",
        "ATTESTATION",
        "SAME_AUTHORITY",
        "DERIVED_FROM",
        "REFERENCES_AUTHORITY",
        "EVIDENCES",
        "CLASSIFIED_BY",
        "CARRIES_FORWARD",
        "PROVENANCE",
    }
)
PRIVATE_OR_REVIEW_PROJECTIONS = frozenset({"excluded_private_material", "review_required"})
AUTHORITY_PREFIXES = ("cdl:", "adr:", "policy:", "invariant:", "artifact:", "truth_primitive:")


EDGE_REPAIRS: tuple[dict[str, str], ...] = (
    {
        "source": ROOT,
        "edge_type": "GOVERNS",
        "target": "adr:0029_hypergraph_substrate",
        "evidence": "docs/adr/ADR_0029_Hypergraph_Substrate.md status accepted",
        "rationale": "ADR-0029 is an accepted ADR artifact; the priority-0 queue contained only a support alias endpoint.",
    },
    {
        "source": ROOT,
        "edge_type": "GOVERNS",
        "target": "cdl:020",
        "evidence": "docs/specs/ilc_cdl_020_d2_schema_baseline_ratification_evidence_319_v0.1.md",
        "rationale": "CDL-020 ratified_phase 319 evidence directly identifies this authority node.",
    },
    {
        "source": ROOT,
        "edge_type": "GOVERNS",
        "target": "cdl:024",
        "evidence": "docs/specs/ilc_cdl_024_wire_transport_ratification_evidence_329_v0.1.md",
        "rationale": "CDL-024 ratified_phase 329 evidence directly identifies this authority node.",
    },
    {
        "source": ROOT,
        "edge_type": "GOVERNS",
        "target": "cdl:027_epoch_length",
        "evidence": "docs/specs/ilc_constitutional_decision_log_v0.1.md CDL-027 row",
        "rationale": "CDL-027 is ratified in the constitutional decision log; no separate canonical target exists in the LMDB.",
    },
    {
        "source": ROOT,
        "edge_type": "GOVERNS",
        "target": "cdl:032",
        "evidence": "docs/specs/ilc_cdl_032_cli_first_sdk_ratification_evidence_253_v0.1.md",
        "rationale": "CDL-032 ratified_phase 253 evidence directly identifies this authority node.",
    },
    {
        "source": ROOT,
        "edge_type": "GOVERNS",
        "target": "cdl:033",
        "evidence": "docs/specs/ilc_cdl_033_openclaw_skill_publication_ratification_evidence_291_v0.1.md",
        "rationale": "CDL-033 ratified_phase 291 evidence directly identifies this authority node.",
    },
    {
        "source": ROOT,
        "edge_type": "GOVERNS",
        "target": "cdl:048_mandatory_conversion",
        "evidence": "docs/specs/ilc_constitutional_decision_log_v0.1.md CDL-048 row",
        "rationale": "CDL-048 mandatory conversion is ratified in the constitutional decision log and was not the same authority as the existing activation-counsel shorthand.",
    },
    {
        "source": ROOT,
        "edge_type": "GOVERNS",
        "target": "cdl:082",
        "evidence": "docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_ratification_evidence_949_v0.1.md",
        "rationale": "CDL-082 ratification evidence identifies a ratification target and later ratification phase.",
    },
    {
        "source": "adr:ADR_0029",
        "edge_type": "SAME_AUTHORITY",
        "target": "adr:0029_hypergraph_substrate",
        "evidence": "docs/adr/ADR_0029_Hypergraph_Substrate.md",
        "rationale": "Support alias endpoint points at the canonical accepted ADR-0029 authority node.",
    },
    {
        "source": "adr:0021_epistemic_finality_claims",
        "edge_type": "REFERENCES_AUTHORITY",
        "target": "cdl:051_epoch_state_quorum",
        "evidence": "docs/specs/ilc_adr_0021_epistemic_finality_claims_461_v0.1.md sections 2-4",
        "rationale": "ADR-0021 is a boundary artifact over CDL-051 protocol finality semantics.",
    },
    {
        "source": "adr:0021_epistemic_finality_claims",
        "edge_type": "REFERENCES_AUTHORITY",
        "target": "cdl:052_epistemic_evaluation_contract",
        "evidence": "docs/specs/ilc_adr_0021_epistemic_finality_claims_461_v0.1.md sections 3-4",
        "rationale": "ADR-0021 is a boundary artifact over CDL-052 graph-side epistemic evaluation semantics.",
    },
    {
        "source": "cdl:028",
        "edge_type": "SAME_AUTHORITY",
        "target": "cdl:028_fee_burn_split",
        "evidence": "docs/specs/ilc_constitutional_decision_log_v0.1.md CDL-028 row",
        "rationale": "Short CDL-028 overlay resolves to the fee-burn split authority node.",
    },
    {
        "source": "cdl:029_allocation_split",
        "edge_type": "SAME_AUTHORITY",
        "target": "cdl:029_80_15_5_allocation_distribution",
        "evidence": "docs/specs/ilc_constitutional_decision_log_v0.1.md CDL-029 row",
        "rationale": "Allocation split shorthand resolves to the governed 80/15/5 allocation authority node.",
    },
    {
        "source": "cdl:047_treasury_reserve",
        "edge_type": "SAME_AUTHORITY",
        "target": "cdl:047_treasury_governance",
        "evidence": "docs/specs/ilc_constitutional_decision_log_v0.1.md CDL-047 row",
        "rationale": "Treasury-reserve shorthand resolves to the governed treasury framework node.",
    },
    {
        "source": "cdl:062_sovereign_substrate_research_lane",
        "edge_type": "REFERENCES_AUTHORITY",
        "target": "cdl:065_coupling_invariants_governance_lock",
        "evidence": "docs/specs/ilc_constitutional_decision_log_v0.1.md CDL-065 row",
        "rationale": "CDL-062 remains an admissibility/research lane referenced by the ratified CDL-065 coupling lock.",
    },
    {
        "source": "cdl:085_prelock_spec",
        "edge_type": "EVIDENCES",
        "target": "cdl:085_werner_phi_bound",
        "evidence": "docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md",
        "rationale": "The prelock is explicit support evidence for the later ratified CDL-085 Werner phi-bound.",
    },
)

DEFERRED_PRIORITY0: dict[str, str] = {
    "cdl:021": "authority_stub_open_or_deferred_indefinitely_not_root_governed_by_this_pass",
    "cdl:039_open_and_promotion_continuity": "ambiguous_cdl039_overlay_not_mapped_to_topology_shuffling_without_manual_source_evidence",
    "artifact:generated_evidence_material_root_1545p_fix22": "support_material_root_already_classified_not_authority_bearing",
    "artifact:genesis_private_local_material_root_1545p_fix22": "private_material_root_not_public_authority_bearing",
    "artifact:genesis_source_tree_manifest_candidate_1545p_fix38": "candidate_manifest_has_backtrace_provenance_to_root_not_forward_authority",
    "artifact:public_release_candidate_material_root_1545p_fix22": "release_material_root_support_partition_not_direct_constitutional_authority",
}


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix62b_json_not_object:{path}")
    return payload


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


def _verify_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix62b_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix62b_output_token_already_present:{token}")
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError(f"fix62b_lmdb_missing:{LMDB_ROOT}")


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62b_node_missing_candidate_id")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62b_edge_source_missing")


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62b_edge_target_missing")


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62b_edge_type_missing")
    return value


def _authority_forward_reachable(node_ids: set[str], edges: list[dict[str, Any]]) -> set[str]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if _edge_type(edge) in AUTHORITY_FORWARD_EDGE_TYPES:
            adjacency[_edge_source(edge)].append(_edge_target(edge))
    seen = {ROOT} if ROOT in node_ids else set()
    queue: deque[str] = deque(seen)
    while queue:
        node_id = queue.popleft()
        for target in adjacency.get(node_id, []):
            if target in node_ids and target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def _typed_adjacency(edges: list[dict[str, Any]]) -> dict[str, list[str]]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if _edge_type(edge) in TYPED_TRACE_EDGE_TYPES:
            adjacency[_edge_source(edge)].append(_edge_target(edge))
    return adjacency


def _typed_trace_resolves_to_reachable_authority(
    node_id: str,
    adjacency: dict[str, list[str]],
    reachable: set[str],
) -> bool:
    if node_id in reachable:
        return True
    seen = {node_id}
    queue: deque[str] = deque([node_id])
    while queue:
        current = queue.popleft()
        for target in adjacency.get(current, []):
            if target in reachable:
                return True
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return False


def _manual_queue(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    node_by_id = {_candidate_id(node): node for node in nodes}
    node_ids = set(node_by_id)
    reachable = _authority_forward_reachable(node_ids, edges)
    typed_adjacency = _typed_adjacency(edges)
    outbound_role = Counter()
    inbound_role = Counter()
    for edge in edges:
        if _edge_type(edge) in TYPED_TRACE_EDGE_TYPES:
            outbound_role[_edge_source(edge)] += 1
            inbound_role[_edge_target(edge)] += 1

    entries: list[dict[str, Any]] = []
    for node_id, node in sorted(node_by_id.items()):
        projection = str(node.get("graph_projection", ""))
        if projection in PRIVATE_OR_REVIEW_PROJECTIONS:
            continue
        reasons: list[str] = []
        priority = 99
        if node_id.startswith(AUTHORITY_PREFIXES) and node_id not in reachable:
            if not _typed_trace_resolves_to_reachable_authority(node_id, typed_adjacency, reachable):
                reasons.append("authority_or_typed_trace_missing")
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
                "node_kind": str(node.get("node_kind", "")),
                "path": str(node.get("source_path", "") or node.get("path", "") or ""),
                "priority": priority,
                "recommended_manual_action": "manual_read_then_add_role_appropriate_typed_trace_or_support_disposition",
                "reasons": reasons,
                "work_family": _work_family(node_id, node),
            }
        )
    entries.sort(key=lambda item: (item["priority"], item["work_family"], item["path"], item["candidate_id"]))
    for index, entry in enumerate(entries, start=1):
        entry["queue_index"] = index
        entry["batch_id"] = f"fix62b_batch_{((index - 1) // 10) + 1:04d}"
    return entries


def _work_family(node_id: str, node: dict[str, Any]) -> str:
    path = str(node.get("source_path", "") or "")
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


def _edge_payload(item: dict[str, str]) -> dict[str, Any]:
    return {
        "annotation_method": "fix62b_priority0_manual_authority_trace",
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": "fix62b_priority0_trace_repair_unsigned_lmdb_candidate",
        "edge_id": deterministic_edge_id(item["source"], item["edge_type"], item["target"]),
        "edge_type": item["edge_type"],
        "evidence": item["evidence"],
        "rationale": item["rationale"],
        "source": item["source"],
        "target": item["target"],
    }


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
        raise ValueError("fix62b_node_preimage_candidate_id_missing")
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": "v0.4.fix62b_priority0_authority_trace",
    }


def _edge_preimage(edge: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "edge_id": edge.get("edge_id") or deterministic_edge_id(_edge_source(edge), _edge_type(edge), _edge_target(edge)),
        "edge_type": _edge_type(edge),
        "source": _edge_source(edge),
        "target": _edge_target(edge),
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "edge_id": fields["edge_id"],
        "fields": fields,
        "preimage_version": "v0.4.fix62b_priority0_authority_trace",
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


def _carry_forward_queue_from_input(
    *,
    source_entries: list[dict[str, Any]],
    ledger: dict[str, Any],
) -> dict[str, Any]:
    resolved_ids = {
        item["candidate_id"]
        for item in ledger["priority0_dispositions"]
        if item["disposition"] in {"authority_forward_resolved", "typed_trace_resolved"}
    }
    entries = [
        dict(entry)
        for entry in source_entries
        if str(entry.get("candidate_id")) not in resolved_ids
    ]
    entries.sort(key=lambda item: (item["priority"], item["work_family"], item.get("path", ""), item["candidate_id"]))
    for index, entry in enumerate(entries, start=1):
        entry["queue_index"] = index
        entry["batch_id"] = f"fix62b_batch_{((index - 1) // 10) + 1:04d}"
        if entry.get("priority") == 0:
            entry["recommended_manual_action"] = "manual_read_deferred_priority0_support_or_ambiguous_authority_disposition"
    return _queue_payload(entries)


def _priority0_entries() -> list[dict[str, Any]]:
    payload = _read_json(INPUT_QUEUE_PATH)
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("fix62b_input_queue_entries_missing")
    priority0 = [entry for entry in entries if entry.get("priority") == 0]
    if len(priority0) != 54:
        raise ValueError(f"fix62b_unexpected_priority0_count:{len(priority0)}")
    return priority0


def _ledger_payload(
    *,
    priority0: list[dict[str, Any]],
    receipt: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, Any]:
    node_ids = {_candidate_id(node) for node in nodes}
    reachable = _authority_forward_reachable(node_ids, edges)
    typed_adjacency = _typed_adjacency(edges)
    edge_targets = {(item["source"], item["edge_type"], item["target"]) for item in EDGE_REPAIRS}
    dispositions: list[dict[str, Any]] = []
    for entry in priority0:
        node_id = str(entry["candidate_id"])
        repair_edges = [
            {"source": source, "edge_type": edge_type, "target": target}
            for source, edge_type, target in sorted(edge_targets)
            if source == node_id or target == node_id
        ]
        if node_id in DEFERRED_PRIORITY0:
            disposition = "deferred_no_authority_promotion"
            rationale = DEFERRED_PRIORITY0[node_id]
        elif node_id in reachable:
            disposition = "authority_forward_resolved"
            rationale = "Node is reachable from Genesis root through GOVERNS/ATTESTATION after Fix62b."
        elif _typed_trace_resolves_to_reachable_authority(node_id, typed_adjacency, reachable):
            disposition = "typed_trace_resolved"
            rationale = "Node has a role-appropriate typed trace to a Genesis-rooted terminal."
        else:
            disposition = "carry_forward_manual_review"
            rationale = "No safe deterministic trace repair was applied in Fix62b."
        dispositions.append(
            {
                "candidate_id": node_id,
                "disposition": disposition,
                "graph_projection": entry.get("graph_projection"),
                "node_kind": entry.get("node_kind"),
                "path": entry.get("path"),
                "queue_index": entry.get("queue_index"),
                "rationale": rationale,
                "repair_edges": repair_edges,
                "reasons": entry.get("reasons", []),
            }
        )
    return {
        "applied_edge_count": receipt.get("accepted_edge_count", 0),
        "deferred_priority0": DEFERRED_PRIORITY0,
        "disposition_counts": dict(Counter(item["disposition"] for item in dispositions)),
        "edge_repair_count": len(EDGE_REPAIRS),
        "edge_repairs": list(EDGE_REPAIRS),
        "lmdb_receipt_summary": {
            "accepted_edge_count": receipt.get("accepted_edge_count", 0),
            "rejected_edge_count": receipt.get("rejected_edge_count", 0),
            "skipped_edge_count": receipt.get("skipped_edge_count", 0),
            "status": receipt.get("status"),
        },
        "phase": PHASE,
        "priority0_count": len(priority0),
        "priority0_dispositions": dispositions,
    }


def _edge_repair_semantics_present(edges: list[dict[str, Any]]) -> int:
    observed = {(_edge_source(edge), _edge_type(edge), _edge_target(edge)) for edge in edges}
    expected = {(item["source"], item["edge_type"], item["target"]) for item in EDGE_REPAIRS}
    return len(observed & expected)


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(
            path=EVALUATOR_PATH.relative_to(REPO_ROOT),
            node_kind="tooling_source_file_node",
            graph_projection="support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix62b"),),
        ),
        AtlasPhaseFileRegistration(
            path=TEST_PATH.relative_to(REPO_ROOT),
            node_kind="test_evidence_node",
            graph_projection="support_candidate_graph",
            required_edges=(("TESTS", "phase:1545p_fix62b"),),
        ),
        AtlasPhaseFileRegistration(
            path=LEDGER_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62b"),),
        ),
        AtlasPhaseFileRegistration(
            path=QUEUE_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62b"),),
        ),
        AtlasPhaseFileRegistration(
            path=REPORT_MD_PATH.relative_to(REPO_ROOT),
            node_kind="spec_document_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62b"),),
        ),
        AtlasPhaseFileRegistration(
            path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            node_kind="phase_walkthrough_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62b"),),
        ),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def _report_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ILC Fix62b Priority-0 Authority Trace Report v0.1",
            "",
            "## Summary",
            "",
            f"- Phase: `{PHASE}`",
            f"- LMDB: `{report['lmdb_path']}`",
            f"- Priority-0 entries reviewed: `{report['priority0_count']}`",
            f"- Edge repair candidates: `{report['edge_repair_count']}`",
            f"- Edges accepted by safe writer: `{report['edge_receipt']['accepted_edge_count']}`",
            f"- Edges skipped as already present: `{report['edge_receipt']['skipped_edge_count']}`",
            f"- Edge repair semantics present in LMDB: `{report['edge_repair_semantics_present_count']}`",
            f"- Edges rejected: `{report['edge_receipt']['rejected_edge_count']}`",
            f"- Disposition counts: `{json.dumps(report['ledger']['disposition_counts'], sort_keys=True)}`",
            f"- Next queue entries: `{report['next_queue']['entry_count']}`",
            f"- Final LMDB nodes: `{report['final_counts']['nodes']}`",
            f"- Final LMDB edges: `{report['final_counts']['edges']}`",
            f"- Final preimages: `{report['final_counts']['preimages']}`",
            "",
            "## Interpretation",
            "",
            "Fix62b repairs the highest-priority authority trace tranche without",
            "flattening aliases or support material into constitutional authority. Direct",
            "`GOVERNS` edges are added only where source reads or the CDL register show",
            "accepted/ratified authority. Alias and support nodes receive role-specific",
            "typed traces or are explicitly deferred.",
            "",
            "## Non-Claims",
            "",
            "- No Genesis signing occurred.",
            "- No public graph upload occurred.",
            "- No public RC activation occurred.",
            "- No ECU minting, settlement, or entitlement was authorized.",
            "- No ADR or CDL text was mutated.",
            "",
        ]
    )


def _walkthrough_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Phase 1545p-Fix62b Priority-0 Authority Trace Walkthrough",
            "",
            "## Commands",
            "",
            "- `python tools/evaluators/sim_genesis_atlas_fix62b_priority0_authority_trace.py`",
            "- `python -m pytest tests/test_phase_1545p_fix62b_priority0_authority_trace.py -q`",
            "- `python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb`",
            "",
            "## Results",
            "",
            f"- Priority-0 entries reviewed: `{report['priority0_count']}`",
            f"- Accepted edge repairs: `{report['edge_receipt']['accepted_edge_count']}`",
            f"- Edge repair semantics present in LMDB: `{report['edge_repair_semantics_present_count']}`",
            f"- Rejected edge repairs: `{report['edge_receipt']['rejected_edge_count']}`",
            f"- Disposition counts: `{json.dumps(report['ledger']['disposition_counts'], sort_keys=True)}`",
            f"- Next queue entries: `{report['next_queue']['entry_count']}`",
            f"- LMDB nodes: `{report['final_counts']['nodes']}`",
            f"- LMDB edges: `{report['final_counts']['edges']}`",
            f"- Preimages: `{report['final_counts']['preimages']}`",
            "",
            "## Boundary",
            "",
            "Fix62b is local unsigned Atlas LMDB maintenance. It does not sign, publish,",
            "activate, mint ECU, settle economics, mutate ADR/CDL state, or authorize",
            "public RC.",
            "",
        ]
    )


def _append_status(report: dict[str, Any]) -> None:
    block = "\n".join(
        [
            "",
            "### Phase 1545p-Fix62b — Priority-0 Authority Trace Strike Force",
            "",
            "**Status:** complete",
            "",
            f"**Output:** Reviewed `{report['priority0_count']}` priority-0 authority trace entries from the Fix62a graph-finish queue, verified `{report['edge_repair_semantics_present_count']}` repair semantics in the unified LMDB, materialized the Fix62b ledger and next queue, refreshed preimages, and preserved all non-activation boundaries.",
            "",
            "**Tokens:** fix62b_priority0_authority_trace_complete, fix62b_priority0_manual_ledger_materialized, fix62b_lmdb_edges_applied, fix62b_complete",
            "",
        ]
    )
    with STATUS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(block)


def run() -> dict[str, Any]:
    _verify_tokens()
    input_payload = _read_json(INPUT_QUEUE_PATH)
    source_entries = input_payload.get("entries", [])
    if not isinstance(source_entries, list):
        raise ValueError("fix62b_input_queue_entries_missing")
    priority0 = [entry for entry in source_entries if entry.get("priority") == 0]
    if len(priority0) != 54:
        raise ValueError(f"fix62b_unexpected_priority0_count:{len(priority0)}")
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        initial_nodes = writer.store.iter_nodes()
        initial_edges = writer.store.iter_edges()
        edge_payloads = [_edge_payload(item) for item in EDGE_REPAIRS]
        edge_receipt = writer.apply_plan(
            AtlasLmdbWritePlan(
                edges_to_add=edge_payloads,
                metadata={"operation": "priority0_authority_trace_repair"},
                phase=PHASE,
                dry_run=False,
            )
        )
        if edge_receipt.get("status") != "PASS":
            raise ValueError("fix62b_edge_receipt_failed")

        nodes_after_edges = writer.store.iter_nodes()
        edges_after_edges = writer.store.iter_edges()
        ledger = _ledger_payload(
            priority0=priority0,
            receipt=edge_receipt,
            nodes=nodes_after_edges,
            edges=edges_after_edges,
        )
        write_json_atomic(LEDGER_PATH, ledger)

        next_queue = _carry_forward_queue_from_input(
            source_entries=source_entries,
            ledger=ledger,
        )
        write_json_atomic(QUEUE_PATH, next_queue)

        provisional_report: dict[str, Any] = {
            "edge_receipt": edge_receipt,
            "edge_repair_count": len(EDGE_REPAIRS),
            "edge_repair_semantics_present_count": _edge_repair_semantics_present(edges_after_edges),
            "final_counts": {"edges": 0, "nodes": 0, "preimages": 0},
            "initial_counts": {"edges": len(initial_edges), "nodes": len(initial_nodes)},
            "ledger": ledger,
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "next_queue": {
                "entry_count": next_queue["entry_count"],
                "priority_counts": next_queue["priority_counts"],
                "reason_counts": next_queue["reason_counts"],
                "work_family_counts": next_queue["work_family_counts"],
            },
            "non_claims": [
                "fix62b_does_not_authorize_ecu_minting_or_settlement",
                "fix62b_does_not_sign_or_publish_the_genesis_atlas",
                "fix62b_does_not_mutate_adr_or_cdl_text",
            ],
            "phase": PHASE,
            "priority0_count": len(priority0),
            "status": "PASS",
        }
        _write_text_atomic(REPORT_MD_PATH, _report_markdown(provisional_report))
        _write_text_atomic(WALKTHROUGH_PATH, _walkthrough_markdown(provisional_report))

        registration_receipt = _register_phase_files(writer)
        if registration_receipt.get("status") != "PASS":
            raise ValueError("fix62b_phase_file_registration_failed")

        final_nodes = writer.store.iter_nodes()
        final_edges = writer.store.iter_edges()
        preimages = [_node_preimage(node) for node in final_nodes]
        preimages.extend(_edge_preimage(edge) for edge in final_edges)
        preimage_receipt = writer.write_preimages(
            preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "full_lmdb_after_fix62b"},
        )

        final_counts = {
            "edges": len(writer.store.iter_edges()),
            "nodes": len(writer.store.iter_nodes()),
            "preimages": len(writer.store.iter_preimages()),
        }
        report = dict(provisional_report)
        report["edge_repair_semantics_present_count"] = _edge_repair_semantics_present(final_edges)
        report["file_registration_receipt"] = registration_receipt
        report["final_counts"] = final_counts
        report["preimage_receipt"] = preimage_receipt
        _write_text_atomic(REPORT_MD_PATH, _report_markdown(report))
        _write_text_atomic(WALKTHROUGH_PATH, _walkthrough_markdown(report))
        write_json_atomic(OUT_REPORT_PATH, report)
        writer.write_metadata(
            "fix62b_priority0_authority_trace_report",
            {
                "final_counts": final_counts,
                "ledger_path": str(LEDGER_PATH.relative_to(REPO_ROOT)),
                "out_report_path": str(OUT_REPORT_PATH.relative_to(REPO_ROOT)),
                "phase": PHASE,
                "status": "PASS",
            },
            phase=PHASE,
            dry_run=False,
        )
        _append_status(report)
        return report
    finally:
        writer.close()


def main() -> int:
    report = run()
    print(json.dumps({"phase": PHASE, "status": report["status"], "final_counts": report["final_counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
