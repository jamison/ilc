#!/usr/bin/env python3
"""Remove false root authority edges to proposed ADR candidate nodes.

PUBLIC_RC_EXCLUDE: fix62e_false_authority_cleanup_research_only
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


PHASE = "1545p-Fix62e"
PHASE_TOKEN = "phase_1545p_fix62e"
ROOT = "artifact:genesis_intent_attestation_init_authority_map"
SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
INPUT_QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62d_manual_graph_finish_queue_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62e_false_authority_cleanup_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62e_manual_graph_finish_queue_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62e_false_authority_cleanup_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62e_false_authority_cleanup_walkthrough.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62e_false_authority_cleanup_v0.1.json"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix62e_false_authority_cleanup.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix62e_false_authority_cleanup.py"

INPUT_TOKENS = ("fix62d_complete",)
OUTPUT_TOKENS = (
    "fix62e_false_authority_cleanup_complete",
    "fix62e_proposed_adr_root_edges_removed",
    "fix62e_complete",
)

PROPOSED_ADR_TARGETS: dict[str, str] = {
    "adr:0015_node_transfer_economics": "docs/adr/ADR_0015_Node_Transfer_Economics.md",
    "adr:0018_sequestered_financial_shard": "docs/adr/ADR_0018_Sequestered_Financial_Shard.md",
    "adr:0024_agent_skills_infrastructure": "docs/adr/ADR_0024_Agent_Skills_Infrastructure.md",
}


def _verify_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix62e_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix62e_output_token_already_present:{token}")


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _edge_payload(source: str, edge_type: str, target: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix62e_false_authority_cleanup",
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": "fix62e_support_classification_unsigned_lmdb_candidate",
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "evidence": "proposed_adr_status_body_and_preexisting_false_root_edge_audit",
        "source": source,
        "target": target,
    }


def _node_preimage(node: dict[str, Any]) -> dict[str, Any]:
    node_id = fix62b._candidate_id(node)
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
        "preimage_version": "v0.4.fix62e_false_authority_cleanup",
    }


def _edge_preimage(edge: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "edge_id": edge.get("edge_id")
        or deterministic_edge_id(
            fix62b._edge_source(edge),
            fix62b._edge_type(edge),
            fix62b._edge_target(edge),
        ),
        "edge_type": fix62b._edge_type(edge),
        "phase": PHASE,
        "source": fix62b._edge_source(edge),
        "target": fix62b._edge_target(edge),
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "edge_id": fields["edge_id"],
        "fields": fields,
        "preimage_version": "v0.4.fix62e_false_authority_cleanup",
    }


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix62e_json_not_object:{path}")
    return payload


def _verify_proposed_adr_sources() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node_id, relative_path in PROPOSED_ADR_TARGETS.items():
        path = REPO_ROOT / relative_path
        text = path.read_text(encoding="utf-8")
        if "**Status:** Proposed" not in text:
            raise ValueError(f"fix62e_expected_proposed_status_missing:{relative_path}")
        rows.append({"node_id": node_id, "source_path": relative_path, "status": "Proposed"})
    return rows


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
        "status": "carry_forward_after_false_authority_cleanup",
        "work_family_counts": dict(sorted(work_family_counts.items())),
    }


def _carry_forward_queue(source_entries: list[dict[str, Any]]) -> dict[str, Any]:
    entries = [dict(entry) for entry in source_entries]
    entries.sort(key=lambda item: (item["priority"], item["work_family"], item.get("path", ""), item["candidate_id"]))
    for index, entry in enumerate(entries, start=1):
        entry["queue_index"] = index
        entry["batch_id"] = f"fix62e_batch_{((index - 1) // 10) + 1:04d}"
    return _queue_payload(entries)


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(
            path=EVALUATOR_PATH.relative_to(REPO_ROOT),
            node_kind="tooling_source_file_node",
            graph_projection="support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix62e"),),
        ),
        AtlasPhaseFileRegistration(
            path=TEST_PATH.relative_to(REPO_ROOT),
            node_kind="test_evidence_node",
            graph_projection="support_candidate_graph",
            required_edges=(("TESTS", "phase:1545p_fix62e"),),
        ),
        AtlasPhaseFileRegistration(
            path=LEDGER_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62e"),),
        ),
        AtlasPhaseFileRegistration(
            path=QUEUE_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62e"),),
        ),
        AtlasPhaseFileRegistration(
            path=REPORT_MD_PATH.relative_to(REPO_ROOT),
            node_kind="spec_document_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62e"),),
        ),
        AtlasPhaseFileRegistration(
            path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            node_kind="phase_walkthrough_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62e"),),
        ),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def _report_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ILC Fix62e False Authority Cleanup Report v0.1",
            "",
            "## Summary",
            "",
            f"- Phase: `{PHASE}`",
            f"- Proposed ADR root edges removed: `{report['edge_removal_receipt']['removed_edge_count']}`",
            f"- Proposed ADR node updates accepted: `{report['node_update_receipt']['accepted_update_count']}`",
            f"- Support classification semantics present: `{report['support_classification_semantics_present_count']}`",
            f"- Final LMDB nodes: `{report['final_counts']['nodes']}`",
            f"- Final LMDB edges: `{report['final_counts']['edges']}`",
            f"- Final preimages: `{report['final_counts']['preimages']}`",
            "",
            "## Non-Claims",
            "",
            "- No Genesis signing occurred.",
            "- No public graph upload occurred.",
            "- No public RC activation occurred.",
            "- No ECU minting, settlement, or entitlement was authorized.",
            "- No ADR text was mutated.",
            "",
        ]
    )


def _walkthrough_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Phase 1545p-Fix62e False Authority Cleanup Walkthrough",
            "",
            "## Commands",
            "",
            "- `python tools/evaluators/sim_genesis_atlas_fix62e_false_authority_cleanup.py`",
            "- `python -m pytest tests/test_phase_1545p_fix62e_false_authority_cleanup.py -q`",
            "- `python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb`",
            "",
            "## Results",
            "",
            f"- Proposed ADR root edges removed: `{report['edge_removal_receipt']['removed_edge_count']}`",
            f"- Support classification semantics present: `{report['support_classification_semantics_present_count']}`",
            f"- LMDB nodes: `{report['final_counts']['nodes']}`",
            f"- LMDB edges: `{report['final_counts']['edges']}`",
            f"- Preimages: `{report['final_counts']['preimages']}`",
            "",
        ]
    )


def _append_status(report: dict[str, Any]) -> None:
    block = "\n".join(
        [
            "",
            "### Phase 1545p-Fix62e — False Authority Cleanup",
            "",
            "**Status:** complete",
            "",
            f"**Output:** Removed `{report['edge_removal_receipt']['removed_edge_count']}` pre-existing root GOVERNS edges to explicitly Proposed ADR candidate nodes, reclassified those nodes as support/proposal artifacts, refreshed preimages, and preserved all non-activation boundaries.",
            "",
            "**Tokens:** fix62e_false_authority_cleanup_complete, fix62e_proposed_adr_root_edges_removed, fix62e_complete",
            "",
        ]
    )
    with STATUS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(block)


def run() -> dict[str, Any]:
    _verify_tokens()
    proposed_rows = _verify_proposed_adr_sources()
    source_queue = _read_json(INPUT_QUEUE_PATH)
    source_entries = source_queue.get("entries", [])
    if not isinstance(source_entries, list):
        raise ValueError("fix62e_source_queue_entries_missing")

    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        removals = {(ROOT, "GOVERNS", node_id) for node_id in PROPOSED_ADR_TARGETS}
        edge_removal_receipt = writer.remove_edges_by_semantic(
            removals,
            phase=PHASE,
            dry_run=False,
            metadata={"scope": "remove_false_root_governs_to_proposed_adrs"},
        )
        if edge_removal_receipt.get("status") != "PASS":
            raise ValueError("fix62e_edge_removal_failed")

        updates = {
            node_id: {
                "authority_cleanup_phase": PHASE_TOKEN,
                "authority_status": "proposed_adr_not_authority",
                "canonicality_tier": "proposed_adr_not_authority",
                "graph_projection": "support_candidate_graph",
                "inclusion_status": "support_only_not_authority",
                "node_kind": "adr_proposal_artifact",
                "promotion_status": "deferred_until_accepted",
                "tier": "support_candidate",
            }
            for node_id in PROPOSED_ADR_TARGETS
        }
        node_update_receipt = writer.update_node_fields(
            updates,
            phase=PHASE,
            dry_run=False,
            metadata={"scope": "proposed_adr_reclassification"},
        )
        if node_update_receipt.get("status") != "PASS":
            raise ValueError("fix62e_node_update_failed")

        classification_edges = [
            _edge_payload(node_id, "CLASSIFIED_BY", SUPPORT_POLICY)
            for node_id in PROPOSED_ADR_TARGETS
        ]
        classification_receipt = writer.apply_plan(
            AtlasLmdbWritePlan(
                edges_to_add=classification_edges,
                metadata={"operation": "classify_proposed_adr_support_nodes"},
                phase=PHASE,
                dry_run=False,
            )
        )
        if classification_receipt.get("status") != "PASS":
            raise ValueError("fix62e_classification_edge_application_failed")

        next_queue = _carry_forward_queue(source_entries)
        write_json_atomic(QUEUE_PATH, next_queue)
        observed_semantics = {
            (fix62b._edge_source(edge), fix62b._edge_type(edge), fix62b._edge_target(edge))
            for edge in writer.store.iter_edges()
        }
        classification_semantics = {
            (node_id, "CLASSIFIED_BY", SUPPORT_POLICY) for node_id in PROPOSED_ADR_TARGETS
        }
        ledger = {
            "edge_removal_targets": [
                {"source": source, "edge_type": edge_type, "target": target}
                for source, edge_type, target in sorted(removals)
            ],
            "phase": PHASE,
            "proposed_adr_sources": proposed_rows,
            "status": "PASS",
            "support_classification_semantics_present_count": len(
                classification_semantics & observed_semantics
            ),
        }
        write_json_atomic(LEDGER_PATH, ledger)
        provisional_report: dict[str, Any] = {
            "classification_receipt": classification_receipt,
            "edge_removal_receipt": edge_removal_receipt,
            "final_counts": {"edges": 0, "nodes": 0, "preimages": 0},
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "next_queue": {
                "entry_count": next_queue["entry_count"],
                "priority_counts": next_queue["priority_counts"],
            },
            "node_update_receipt": node_update_receipt,
            "non_claims": [
                "fix62e_does_not_authorize_ecu_minting_or_settlement",
                "fix62e_does_not_sign_or_publish_the_genesis_atlas",
                "fix62e_does_not_mutate_adr_or_cdl_text",
            ],
            "phase": PHASE,
            "status": "PASS",
            "support_classification_semantics_present_count": ledger[
                "support_classification_semantics_present_count"
            ],
        }
        fix62b._write_text_atomic(REPORT_MD_PATH, _report_markdown(provisional_report))
        fix62b._write_text_atomic(WALKTHROUGH_PATH, _walkthrough_markdown(provisional_report))

        registration_receipt = _register_phase_files(writer)
        if registration_receipt.get("status") != "PASS":
            raise ValueError("fix62e_phase_file_registration_failed")

        final_nodes = writer.store.iter_nodes()
        final_edges = writer.store.iter_edges()
        preimages = [_node_preimage(node) for node in final_nodes]
        preimages.extend(_edge_preimage(edge) for edge in final_edges)
        preimage_receipt = writer.write_preimages(
            preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "full_lmdb_after_fix62e"},
        )
        if preimage_receipt.get("status") != "PASS":
            raise ValueError("fix62e_preimage_write_failed")

        report = dict(provisional_report)
        report["file_registration_receipt"] = registration_receipt
        report["final_counts"] = {
            "edges": len(writer.store.iter_edges()),
            "nodes": len(writer.store.iter_nodes()),
            "preimages": len(writer.store.iter_preimages()),
        }
        report["preimage_receipt"] = preimage_receipt
        write_json_atomic(OUT_REPORT_PATH, report)
        fix62b._write_text_atomic(REPORT_MD_PATH, _report_markdown(report))
        fix62b._write_text_atomic(WALKTHROUGH_PATH, _walkthrough_markdown(report))
        writer.write_metadata(
            "fix62e_false_authority_cleanup_report",
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
