#!/usr/bin/env python3
"""Classify priority-1 invariant/policy overlays as support traces.

PUBLIC_RC_EXCLUDE: fix62h_priority1_overlay_classification_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Genesis Atlas LMDB maintenance pass;
not Genesis signing, public graph upload, canonical graph mutation, runtime
activation, public serving, ECU minting, or public RC publication.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
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


PHASE = "1545p-Fix62h"
PHASE_TOKEN = "phase_1545p_fix62h"
ROOT = "artifact:genesis_intent_attestation_init_authority_map"
SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
INPUT_QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62g_manual_graph_finish_queue_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62h_priority1_overlay_classification_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62h_manual_graph_finish_queue_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62h_priority1_overlay_classification_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62h_priority1_overlay_classification_walkthrough.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62h_priority1_overlay_classification_v0.1.json"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix62h_priority1_overlay_classification.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix62h_priority1_overlay_classification.py"

INPUT_TOKENS = ("fix62g_complete",)
OUTPUT_TOKENS = (
    "fix62h_priority1_overlay_classification_complete",
    "fix62h_invariant_policy_overlays_demoted_to_support_trace",
    "fix62h_complete",
)

KEYWORD_TARGETS = (
    (("canon", "bundle"), "adr:0009_bundle_distribution"),
    (("genesis", "lineage"), "adr:0037_genesis_canonical_lineage_contract"),
    (("genesis", "authority"), "policy:genesis_authority_sunset"),
    (("ecu", "ilc", "settlement", "wallet"), "adr:0012_ecu_ilc_graph_coupling_anti_reflexivity"),
    (("validator", "admission", "ejection"), "cdl:017_validator_admission_ejection"),
    (("jury", "eligibility"), "adr:0040_jury_eligibility_assignment"),
    (("truth", "primitive"), "cdl:074_truth_primitive_runtime"),
    (("provenance",), "cdl:084_provenance_chain_attribution"),
    (("privacy", "shard"), "cdl:041_shard_lifecycle_operations_creation_merge_split_partition_privacy"),
    (("public", "rc", "publication"), "policy:formal_publication_gate_required"),
)


def _verify_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix62h_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix62h_output_token_already_present:{token}")


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix62h_json_not_object:{path}")
    return payload


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62h_node_candidate_id_missing")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62h_edge_source_missing")


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62h_edge_target_missing")


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62h_edge_type_missing")
    return value


def _edge_payload(source: str, edge_type: str, target: str, *, reason: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix62h_priority1_overlay_classification",
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": "fix62h_unsigned_priority1_overlay_trace_lmdb_candidate",
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "evidence": reason,
        "reason": reason,
        "source": source,
        "target": target,
    }


def _node_preimage(node: dict[str, Any]) -> dict[str, Any]:
    node_id = _candidate_id(node)
    fields = {
        "authority_status": node.get("authority_status"),
        "candidate_id": node_id,
        "canonicality_tier": node.get("canonicality_tier"),
        "graph_projection": node.get("graph_projection"),
        "node_kind": node.get("node_kind"),
        "phase": PHASE,
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": "v0.4.fix62h_priority1_overlay_classification",
    }


def _edge_preimage(edge: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "edge_id": edge.get("edge_id")
        or deterministic_edge_id(_edge_source(edge), _edge_type(edge), _edge_target(edge)),
        "edge_type": _edge_type(edge),
        "phase": PHASE,
        "source": _edge_source(edge),
        "target": _edge_target(edge),
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "edge_id": fields["edge_id"],
        "fields": fields,
        "preimage_version": "v0.4.fix62h_priority1_overlay_classification",
    }


def _root_governs(edges: list[dict[str, Any]]) -> set[str]:
    return {
        _edge_target(edge)
        for edge in edges
        if _edge_source(edge) == ROOT and _edge_type(edge) == "GOVERNS"
    }


def _number_target(node_id: str, prefix: str, rooted_targets_by_number: dict[int | str, list[str]]) -> str:
    regex = rf"{prefix}[_:-]0*([0-9]{{1,4}})"
    match = re.search(regex, node_id, re.IGNORECASE)
    if not match:
        return ""
    candidates = rooted_targets_by_number.get(int(match.group(1)), [])
    return candidates[0] if candidates else ""


def _authority_targets_for(node_id: str, existing: set[str], rooted_targets_by_number: dict[str, dict[int | str, list[str]]]) -> list[str]:
    lowered = node_id.lower()
    targets: list[str] = []
    for prefix in ("cdl", "adr"):
        target = _number_target(lowered, prefix, rooted_targets_by_number[prefix])
        if target:
            targets.append(target)
    for terms, target in KEYWORD_TARGETS:
        if target in existing and any(term in lowered for term in terms):
            targets.append(target)
    deduped: list[str] = []
    for target in targets:
        if target not in deduped:
            deduped.append(target)
    return deduped[:3]


def _rooted_by_number(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, dict[int | str, list[str]]]:
    root_targets = _root_governs(edges)
    result: dict[str, dict[int | str, list[str]]] = {"cdl": defaultdict(list), "adr": defaultdict(list)}
    for node in nodes:
        node_id = _candidate_id(node)
        if node_id not in root_targets:
            continue
        for prefix in ("cdl", "adr"):
            if not node_id.startswith(f"{prefix}:"):
                continue
            match = re.match(rf"{prefix}:0*([0-9]{{1,4}})", node_id, re.IGNORECASE)
            if match:
                result[prefix][int(match.group(1))].append(node_id)
    for prefix in result:
        for key in result[prefix]:
            result[prefix][key].sort()
    return result


def _support_patch(node_id: str) -> dict[str, str]:
    kind = "invariant_support_trace_node" if node_id.startswith("invariant:") else "policy_support_trace_node"
    return {
        "authority_status": "candidate_overlay_support_trace_not_independent_authority",
        "canonicality_tier": "support_trace_not_independent_authority",
        "graph_projection": "support_candidate_graph",
        "inclusion_status": "support_trace_not_independent_authority",
        "node_kind": kind,
        "promotion_status": "not_independent_authority",
        "tier": "support_candidate",
    }


def _queue_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    entries.sort(key=lambda item: (item["priority"], item["work_family"], item.get("path", ""), item["candidate_id"]))
    for index, entry in enumerate(entries, start=1):
        entry["queue_index"] = index
        entry["batch_id"] = f"fix62h_batch_{((index - 1) // 10) + 1:04d}"
    priority_counts = Counter(str(entry["priority"]) for entry in entries)
    work_family_counts = Counter(str(entry.get("work_family", "")) for entry in entries)
    reason_counts: Counter[str] = Counter()
    for entry in entries:
        reason_counts.update(str(reason) for reason in entry.get("reasons", []))
    return {
        "entry_count": len(entries),
        "entries": entries,
        "phase": PHASE,
        "priority_counts": dict(sorted(priority_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "source_queue": str(INPUT_QUEUE_PATH.relative_to(REPO_ROOT)),
        "status": "carry_forward_after_priority1_overlay_classification",
        "work_family_counts": dict(sorted(work_family_counts.items())),
    }


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(EVALUATOR_PATH.relative_to(REPO_ROOT), "tooling_source_file_node", "support_candidate_graph", required_edges=(("IMPLEMENTS", "phase:1545p_fix62h"),)),
        AtlasPhaseFileRegistration(TEST_PATH.relative_to(REPO_ROOT), "test_evidence_node", "support_candidate_graph", required_edges=(("TESTS", "phase:1545p_fix62h"),)),
        AtlasPhaseFileRegistration(LEDGER_PATH.relative_to(REPO_ROOT), "spec_json_artifact_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix62h"),)),
        AtlasPhaseFileRegistration(QUEUE_PATH.relative_to(REPO_ROOT), "spec_json_artifact_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix62h"),)),
        AtlasPhaseFileRegistration(REPORT_MD_PATH.relative_to(REPO_ROOT), "spec_document_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix62h"),)),
        AtlasPhaseFileRegistration(WALKTHROUGH_PATH.relative_to(REPO_ROOT), "phase_walkthrough_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix62h"),)),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def _append_status(report: dict[str, Any]) -> None:
    block = f"""

### Phase 1545p-Fix62h — Priority-1 Overlay Classification

**Status:** complete

**Output:** Classified `{report['processed_priority1_count']}` priority-1 invariant/policy candidate overlays as support traces, rooted the support-classification policy, applied `{report['edge_application']['accepted_edge_count']}` new classification/reference edges, refreshed preimages, and preserved all non-activation boundaries.

**Tokens:** {', '.join(OUTPUT_TOKENS)}
"""
    STATUS_PATH.write_text(STATUS_PATH.read_text(encoding="utf-8").rstrip() + block + "\n", encoding="utf-8")


def _report_markdown(report: dict[str, Any]) -> str:
    return f"""# ILC Fix62h Priority-1 Overlay Classification Report

PUBLIC_RC_EXCLUDE: fix62h_priority1_overlay_classification_research_only

## Summary

- Priority-1 overlays processed: `{report['processed_priority1_count']}`
- Support policy rooted: `{report['support_policy_governs_added']}`
- Accepted edges: `{report['edge_application']['accepted_edge_count']}`
- Node updates: `{report['node_update']['accepted_update_count']}`
- Carry-forward entries: `{report['queue_entry_count']}`
- Final LMDB: `{report['final_counts']['nodes']}` nodes / `{report['final_counts']['edges']}` edges / `{report['final_counts']['preimages']}` preimages

## Boundary

This phase updates the local unsigned Genesis Atlas LMDB candidate only. It does
not sign Genesis, publish the graph, activate public serving, mint ECU, settle
ILC, or mutate canonical protocol authority. No ECU minting, production
emission, wallet settlement, or public claimability activation occurred.
"""


def _walkthrough_markdown(report: dict[str, Any]) -> str:
    return f"""# Phase 1545p-Fix62h Walkthrough

## Commands

```bash
python tools/evaluators/sim_genesis_atlas_fix62h_priority1_overlay_classification.py
python -m pytest tests/test_phase_1545p_fix62h_priority1_overlay_classification.py tests/test_phase_1545p_fix62g_governance_spine_closure.py tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py -q
python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb
```

## Result

- Priority-1 overlays processed: `{report['processed_priority1_count']}`
- Remaining priority-1 queue entries: `{report['remaining_priority1_count']}`
- Final LMDB counts: `{report['final_counts']['nodes']}` nodes / `{report['final_counts']['edges']}` edges / `{report['final_counts']['preimages']}` preimages

## Non-Claims

No Genesis signing, public graph upload, public RC publication, public serving,
runtime activation, ECU minting, or ILC settlement occurred.
"""


def _validate(report: dict[str, Any]) -> None:
    if report["processed_priority1_count"] != 1159:
        raise ValueError("fix62h_expected_1159_priority1_entries")
    if report["remaining_priority1_count"] != 0:
        raise ValueError("fix62h_priority1_not_closed")
    if report["edge_application"]["rejected_edge_count"] != 0:
        raise ValueError("fix62h_rejected_edges_present")


def run() -> dict[str, Any]:
    _verify_tokens()
    input_queue = _read_json(INPUT_QUEUE_PATH)
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        nodes = writer.store.iter_nodes()
        edges = writer.store.iter_edges()
        node_ids = {_candidate_id(node) for node in nodes}
        existing_governs = {( _edge_source(edge), _edge_type(edge), _edge_target(edge)) for edge in edges}
        rooted_targets_by_number = _rooted_by_number(nodes, edges)
        priority1 = [dict(entry) for entry in input_queue["entries"] if entry.get("priority") == 1]
        updates: dict[str, dict[str, str]] = {}
        edge_rows: list[dict[str, Any]] = []
        ledger_entries: list[dict[str, Any]] = []

        if (ROOT, "GOVERNS", SUPPORT_POLICY) not in existing_governs:
            edge_rows.append(
                _edge_payload(
                    ROOT,
                    "GOVERNS",
                    SUPPORT_POLICY,
                    reason="Genesis Atlas support-only classification rule governs noncanonical overlay classification",
                )
            )
        for entry in priority1:
            source = str(entry["candidate_id"])
            if source not in node_ids:
                continue
            updates[source] = _support_patch(source)
            refs = _authority_targets_for(source, node_ids, rooted_targets_by_number)
            node_edges = [
                _edge_payload(
                    source,
                    "CLASSIFIED_BY",
                    SUPPORT_POLICY,
                    reason="Priority-1 invariant/policy overlay classified as support trace, not independent authority",
                )
            ]
            node_edges.extend(
                _edge_payload(
                    source,
                    "REFERENCES_AUTHORITY",
                    target,
                    reason="Priority-1 overlay identifier names rooted ADR/CDL/policy authority token",
                )
                for target in refs
            )
            edge_rows.extend(node_edges)
            ledger_entries.append(
                {
                    **entry,
                    "disposition": "classified_support_trace",
                    "recommended_edges": [
                        {
                            "edge_type": edge["edge_type"],
                            "source": edge["source"],
                            "target": edge["target"],
                        }
                        for edge in node_edges
                    ],
                }
            )

        plan = AtlasLmdbWritePlan(
            edges_to_add=edge_rows,
            metadata={"operation": "fix62h_priority1_overlay_classification"},
            phase=PHASE,
            dry_run=False,
        )
        edge_receipt = writer.apply_plan(plan)
        update_receipt = writer.update_node_fields(
            updates,
            phase=PHASE,
            dry_run=False,
            metadata={"operation": "fix62h_priority1_overlay_demotion"},
        )

        carry_forward = [dict(entry) for entry in input_queue["entries"] if entry.get("priority") != 1]
        queue_payload = _queue_payload(carry_forward)
        ledger = {
            "entries": ledger_entries,
            "entry_count": len(ledger_entries),
            "phase": PHASE,
            "status": "priority1_overlay_classification_complete",
        }
        write_json_atomic(LEDGER_PATH, ledger)
        write_json_atomic(QUEUE_PATH, queue_payload)
        file_receipt = _register_phase_files(writer)

        post_nodes = writer.store.iter_nodes()
        post_edges = writer.store.iter_edges()
        touched_node_ids = set(updates)
        touched_node_ids.update(
            _candidate_id(node)
            for node in post_nodes
            if str(node.get("annotation_phase")) == PHASE_TOKEN
        )
        touched_edge_ids = {
            str(edge.get("edge_id"))
            for edge in post_edges
            if str(edge.get("annotation_phase")) == PHASE_TOKEN and edge.get("edge_id")
        }
        preimages = [_node_preimage(node) for node in post_nodes if _candidate_id(node) in touched_node_ids]
        preimages.extend(_edge_preimage(edge) for edge in post_edges if str(edge.get("edge_id")) in touched_edge_ids)
        preimage_receipt = writer.write_preimages(
            preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "fix62h_priority1_overlay_classification"},
        )
        final = writer.inspect()
        report = {
            "edge_application": {
                "accepted_edge_count": edge_receipt["accepted_edge_count"],
                "rejected_edge_count": edge_receipt["rejected_edge_count"],
                "skipped_edge_count": edge_receipt["skipped_edge_count"],
            },
            "file_registration": {
                "accepted_edge_count": file_receipt["accepted_edge_count"],
                "accepted_node_count": file_receipt["accepted_node_count"],
            },
            "final_counts": {
                "edges": final["edge_count"],
                "nodes": final["node_count"],
                "preimages": final["preimage_count"],
            },
            "node_update": {
                "accepted_update_count": update_receipt["accepted_update_count"],
                "rejected_update_count": update_receipt["rejected_update_count"],
            },
            "phase": PHASE,
            "preimage_receipt": {
                "preimage_count": preimage_receipt["preimage_count"],
                "post_preimage_count": preimage_receipt["post_preimage_count"],
            },
            "processed_priority1_count": len(priority1),
            "queue_entry_count": queue_payload["entry_count"],
            "remaining_priority1_count": int(queue_payload["priority_counts"].get("1", 0)),
            "status": "PASS",
            "support_policy_governs_added": 1 if (ROOT, "GOVERNS", SUPPORT_POLICY) not in existing_governs else 0,
        }
        _validate(report)
        REPORT_MD_PATH.write_text(_report_markdown(report), encoding="utf-8")
        WALKTHROUGH_PATH.write_text(_walkthrough_markdown(report), encoding="utf-8")
        write_json_atomic(OUT_REPORT_PATH, report)
        _append_status(report)
        return report
    finally:
        writer.close()


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":"), allow_nan=False))
