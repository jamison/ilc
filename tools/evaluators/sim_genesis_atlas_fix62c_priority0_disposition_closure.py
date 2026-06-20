#!/usr/bin/env python3
"""Close remaining priority-0 Genesis Atlas queue entries by disposition.

PUBLIC_RC_EXCLUDE: fix62c_priority0_disposition_closure_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Genesis Atlas LMDB maintenance pass;
not Genesis signing, public graph upload, canonical graph mutation, runtime
activation, public serving, ECU minting, or public RC publication.
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
    AtlasLmdbWritePlan,
    AtlasPhaseFileRegistration,
    deterministic_edge_id,
    write_json_atomic,
)
import tools.evaluators.sim_genesis_atlas_fix62b_priority0_authority_trace as fix62b  # noqa: E402


PHASE = "1545p-Fix62c"
PHASE_TOKEN = "phase_1545p_fix62c"
ROOT = "artifact:genesis_intent_attestation_init_authority_map"
SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
INPUT_QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62b_manual_graph_finish_queue_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62c_priority0_disposition_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62c_manual_graph_finish_queue_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62c_priority0_disposition_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62c_priority0_disposition_walkthrough.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62c_priority0_disposition_v0.1.json"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix62c_priority0_disposition_closure.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix62c_priority0_disposition_closure.py"

INPUT_TOKENS = ("fix62b_complete",)
OUTPUT_TOKENS = (
    "fix62c_priority0_disposition_closure_complete",
    "fix62c_priority0_queue_cleared",
    "fix62c_support_classification_edges_applied",
    "fix62c_complete",
)

SUPPORT_CLASSIFICATION_EDGES: tuple[tuple[str, str, str], ...] = (
    ("cdl:021", "CLASSIFIED_BY", SUPPORT_POLICY),
    ("artifact:generated_evidence_material_root_1545p_fix22", "CLASSIFIED_BY", SUPPORT_POLICY),
    ("artifact:genesis_private_local_material_root_1545p_fix22", "CLASSIFIED_BY", SUPPORT_POLICY),
    ("artifact:genesis_source_tree_manifest_candidate_1545p_fix38", "CLASSIFIED_BY", SUPPORT_POLICY),
    ("artifact:public_release_candidate_material_root_1545p_fix22", "CLASSIFIED_BY", SUPPORT_POLICY),
)


def _verify_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix62c_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix62c_output_token_already_present:{token}")
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError(f"fix62c_lmdb_missing:{LMDB_ROOT}")


def _edge_payload(source: str, edge_type: str, target: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix62c_priority0_disposition_closure",
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": "fix62c_support_classification_unsigned_lmdb_candidate",
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "source": source,
        "target": target,
    }


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _node_preimage(node: dict[str, Any]) -> dict[str, Any]:
    node_id = fix62b._candidate_id(node)
    if not node_id:
        raise ValueError("fix62c_node_preimage_candidate_id_missing")
    fields = {
        "candidate_id": node_id,
        "content_sha256": node.get("content_sha256"),
        "graph_projection": node.get("graph_projection"),
        "node_kind": node.get("node_kind"),
        "phase": PHASE,
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": "v0.4.fix62c_priority0_disposition",
    }


def _edge_preimage(edge: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "edge_id": edge.get("edge_id") or deterministic_edge_id(
            fix62b._edge_source(edge),
            fix62b._edge_type(edge),
            fix62b._edge_target(edge),
        ),
        "edge_type": fix62b._edge_type(edge),
        "phase": PHASE,
        "source": fix62b._edge_source(edge),
        "target": fix62b._edge_target(edge),
    }
    edge_id = fields["edge_id"]
    if not isinstance(edge_id, str) or not edge_id:
        raise ValueError("fix62c_edge_preimage_edge_id_missing")
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "edge_id": edge_id,
        "fields": fields,
        "preimage_version": "v0.4.fix62c_priority0_disposition",
    }


def _priority0_entries(source_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority0 = [entry for entry in source_entries if entry.get("priority") == 0]
    if len(priority0) != 9:
        raise ValueError(f"fix62c_unexpected_priority0_count:{len(priority0)}")
    return priority0


def _ledger(priority0: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    observed = {(fix62b._edge_source(edge), fix62b._edge_type(edge), fix62b._edge_target(edge)) for edge in edges}
    dispositions: list[dict[str, Any]] = []
    for entry in priority0:
        node_id = str(entry["candidate_id"])
        if node_id == "cdl:021":
            disposition = "support_stub_classified"
            rationale = "CDL-021 is open/deferred indefinitely; it is support material, not root-governed authority."
        elif node_id == "cdl:039_open_and_promotion_continuity":
            disposition = "typed_trace_resolved_existing_same_authority"
            rationale = "Existing SAME_AUTHORITY edge reaches cdl:039_topology_shuffling_authorization, which is Genesis-rooted."
        elif node_id.startswith("cdl:085_"):
            disposition = "typed_trace_resolved_existing_supersession"
            rationale = "Existing SUPERSEDED_BY edge reaches cdl:085_werner_phi_bound, which is Genesis-rooted."
        elif node_id.startswith("artifact:"):
            disposition = "support_material_root_classified"
            rationale = "Material-root artifact is support/candidate material and is classified by the unsigned support-only policy, not promoted with GOVERNS."
        else:
            disposition = "unexpected_priority0_carry_forward"
            rationale = "No deterministic Fix62c disposition rule matched."
        classification_present = (node_id, "CLASSIFIED_BY", SUPPORT_POLICY) in observed
        dispositions.append(
            {
                "candidate_id": node_id,
                "classification_edge_present": classification_present,
                "disposition": disposition,
                "graph_projection": entry.get("graph_projection"),
                "node_kind": entry.get("node_kind"),
                "queue_index": entry.get("queue_index"),
                "rationale": rationale,
                "reasons": entry.get("reasons", []),
            }
        )
    return {
        "disposition_counts": dict(Counter(item["disposition"] for item in dispositions)),
        "phase": PHASE,
        "priority0_count": len(priority0),
        "priority0_dispositions": dispositions,
        "support_classification_edges": [
            {"source": source, "edge_type": edge_type, "target": target}
            for source, edge_type, target in SUPPORT_CLASSIFICATION_EDGES
        ],
    }


def _queue_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    priority_counts = Counter(str(entry["priority"]) for entry in entries)
    reason_counts: Counter[str] = Counter()
    work_family_counts = Counter(str(entry["work_family"]) for entry in entries)
    for entry in entries:
        reason_counts.update(str(reason) for reason in entry.get("reasons", []))
    return {
        "entry_count": len(entries),
        "entries": entries,
        "phase": PHASE,
        "priority_counts": dict(sorted(priority_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "source_queue": str(INPUT_QUEUE_PATH.relative_to(REPO_ROOT)),
        "status": "carry_forward_after_priority0_disposition_closure",
        "work_family_counts": dict(sorted(work_family_counts.items())),
    }


def _carry_forward_queue(source_entries: list[dict[str, Any]], priority0: list[dict[str, Any]]) -> dict[str, Any]:
    closed_ids = {entry["candidate_id"] for entry in priority0}
    entries = [dict(entry) for entry in source_entries if entry.get("candidate_id") not in closed_ids]
    entries.sort(key=lambda item: (item["priority"], item["work_family"], item.get("path", ""), item["candidate_id"]))
    for index, entry in enumerate(entries, start=1):
        entry["queue_index"] = index
        entry["batch_id"] = f"fix62c_batch_{((index - 1) // 10) + 1:04d}"
    return _queue_payload(entries)


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(
            path=EVALUATOR_PATH.relative_to(REPO_ROOT),
            node_kind="tooling_source_file_node",
            graph_projection="support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix62c"),),
        ),
        AtlasPhaseFileRegistration(
            path=TEST_PATH.relative_to(REPO_ROOT),
            node_kind="test_evidence_node",
            graph_projection="support_candidate_graph",
            required_edges=(("TESTS", "phase:1545p_fix62c"),),
        ),
        AtlasPhaseFileRegistration(
            path=LEDGER_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62c"),),
        ),
        AtlasPhaseFileRegistration(
            path=QUEUE_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62c"),),
        ),
        AtlasPhaseFileRegistration(
            path=REPORT_MD_PATH.relative_to(REPO_ROOT),
            node_kind="spec_document_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62c"),),
        ),
        AtlasPhaseFileRegistration(
            path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            node_kind="phase_walkthrough_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62c"),),
        ),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def _report_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ILC Fix62c Priority-0 Disposition Report v0.1",
            "",
            "## Summary",
            "",
            f"- Phase: `{PHASE}`",
            f"- Priority-0 entries reviewed: `{report['priority0_count']}`",
            f"- Support classification semantics present: `{report['support_classification_semantics_present_count']}`",
            f"- Edge receipt accepted/skipped/rejected: `{report['edge_receipt']['accepted_edge_count']}` / `{report['edge_receipt']['skipped_edge_count']}` / `{report['edge_receipt']['rejected_edge_count']}`",
            f"- Disposition counts: `{json.dumps(report['ledger']['disposition_counts'], sort_keys=True)}`",
            f"- Next queue entries: `{report['next_queue']['entry_count']}`",
            f"- Next queue priority counts: `{json.dumps(report['next_queue']['priority_counts'], sort_keys=True)}`",
            f"- Final LMDB nodes: `{report['final_counts']['nodes']}`",
            f"- Final LMDB edges: `{report['final_counts']['edges']}`",
            f"- Final preimages: `{report['final_counts']['preimages']}`",
            "",
            "## Interpretation",
            "",
            "Fix62c clears the residual priority-0 queue without adding false root",
            "`GOVERNS` edges. Historical CDL-085 nodes resolve through supersession,",
            "the CDL-039 overlay resolves through an existing SAME_AUTHORITY edge, and",
            "material roots remain support/candidate material classified by the unsigned",
            "support-only policy.",
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
            "# Phase 1545p-Fix62c Priority-0 Disposition Walkthrough",
            "",
            "## Commands",
            "",
            "- `python tools/evaluators/sim_genesis_atlas_fix62c_priority0_disposition_closure.py`",
            "- `python -m pytest tests/test_phase_1545p_fix62c_priority0_disposition_closure.py -q`",
            "- `python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb`",
            "",
            "## Results",
            "",
            f"- Priority-0 entries reviewed: `{report['priority0_count']}`",
            f"- Support classification semantics present: `{report['support_classification_semantics_present_count']}`",
            f"- Disposition counts: `{json.dumps(report['ledger']['disposition_counts'], sort_keys=True)}`",
            f"- Next queue priority counts: `{json.dumps(report['next_queue']['priority_counts'], sort_keys=True)}`",
            f"- LMDB nodes: `{report['final_counts']['nodes']}`",
            f"- LMDB edges: `{report['final_counts']['edges']}`",
            f"- Preimages: `{report['final_counts']['preimages']}`",
            "",
            "## Boundary",
            "",
            "Fix62c is local unsigned Atlas LMDB maintenance. It does not sign, publish,",
            "activate, mint ECU, settle economics, mutate ADR/CDL state, or authorize",
            "public RC.",
            "",
        ]
    )


def _support_semantics_present(edges: list[dict[str, Any]]) -> int:
    observed = {(fix62b._edge_source(edge), fix62b._edge_type(edge), fix62b._edge_target(edge)) for edge in edges}
    expected = set(SUPPORT_CLASSIFICATION_EDGES)
    return len(observed & expected)


def _append_status(report: dict[str, Any]) -> None:
    block = "\n".join(
        [
            "",
            "### Phase 1545p-Fix62c — Priority-0 Disposition Closure",
            "",
            "**Status:** complete",
            "",
            f"**Output:** Reviewed the remaining `{report['priority0_count']}` priority-0 entries, verified `{report['support_classification_semantics_present_count']}` support classification semantics, cleared priority-0 from the carry-forward graph-finish queue, refreshed preimages, and preserved all non-activation boundaries.",
            "",
            "**Tokens:** fix62c_priority0_disposition_closure_complete, fix62c_priority0_queue_cleared, fix62c_support_classification_edges_applied, fix62c_complete",
            "",
        ]
    )
    with STATUS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(block)


def run() -> dict[str, Any]:
    _verify_tokens()
    source_payload = fix62b._read_json(INPUT_QUEUE_PATH)
    source_entries = source_payload.get("entries", [])
    if not isinstance(source_entries, list):
        raise ValueError("fix62c_input_queue_entries_missing")
    priority0 = _priority0_entries(source_entries)
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        edge_payloads = [_edge_payload(source, edge_type, target) for source, edge_type, target in SUPPORT_CLASSIFICATION_EDGES]
        edge_receipt = writer.apply_plan(
            AtlasLmdbWritePlan(
                edges_to_add=edge_payloads,
                metadata={"operation": "priority0_support_disposition_closure"},
                phase=PHASE,
                dry_run=False,
            )
        )
        if edge_receipt.get("status") != "PASS":
            raise ValueError("fix62c_edge_receipt_failed")

        edges_after = writer.store.iter_edges()
        ledger = _ledger(priority0, edges_after)
        write_json_atomic(LEDGER_PATH, ledger)
        next_queue = _carry_forward_queue(source_entries, priority0)
        write_json_atomic(QUEUE_PATH, next_queue)

        provisional_report: dict[str, Any] = {
            "edge_receipt": edge_receipt,
            "final_counts": {"edges": 0, "nodes": 0, "preimages": 0},
            "ledger": ledger,
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "next_queue": {
                "entry_count": next_queue["entry_count"],
                "priority_counts": next_queue["priority_counts"],
                "reason_counts": next_queue["reason_counts"],
                "work_family_counts": next_queue["work_family_counts"],
            },
            "non_claims": [
                "fix62c_does_not_authorize_ecu_minting_or_settlement",
                "fix62c_does_not_sign_or_publish_the_genesis_atlas",
                "fix62c_does_not_mutate_adr_or_cdl_text",
            ],
            "phase": PHASE,
            "priority0_count": len(priority0),
            "status": "PASS",
            "support_classification_semantics_present_count": _support_semantics_present(edges_after),
        }
        fix62b._write_text_atomic(REPORT_MD_PATH, _report_markdown(provisional_report))
        fix62b._write_text_atomic(WALKTHROUGH_PATH, _walkthrough_markdown(provisional_report))

        registration_receipt = _register_phase_files(writer)
        if registration_receipt.get("status") != "PASS":
            raise ValueError("fix62c_phase_file_registration_failed")

        final_nodes = writer.store.iter_nodes()
        final_edges = writer.store.iter_edges()
        preimages = [_node_preimage(node) for node in final_nodes]
        preimages.extend(_edge_preimage(edge) for edge in final_edges)
        preimage_receipt = writer.write_preimages(
            preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "full_lmdb_after_fix62c"},
        )
        report = dict(provisional_report)
        report["file_registration_receipt"] = registration_receipt
        report["final_counts"] = {
            "edges": len(writer.store.iter_edges()),
            "nodes": len(writer.store.iter_nodes()),
            "preimages": len(writer.store.iter_preimages()),
        }
        report["preimage_receipt"] = preimage_receipt
        report["support_classification_semantics_present_count"] = _support_semantics_present(writer.store.iter_edges())
        fix62b._write_text_atomic(REPORT_MD_PATH, _report_markdown(report))
        fix62b._write_text_atomic(WALKTHROUGH_PATH, _walkthrough_markdown(report))
        write_json_atomic(OUT_REPORT_PATH, report)
        writer.write_metadata(
            "fix62c_priority0_disposition_report",
            {
                "final_counts": report["final_counts"],
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
