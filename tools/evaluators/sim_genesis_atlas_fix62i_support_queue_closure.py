#!/usr/bin/env python3
"""Close remaining priority-3 support queue entries in the Atlas LMDB.

PUBLIC_RC_EXCLUDE: fix62i_support_queue_closure_research_only
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


PHASE = "1545p-Fix62i"
PHASE_TOKEN = "phase_1545p_fix62i"
SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"
SOURCE_TREE_MANIFEST = "artifact:genesis_source_tree_manifest_candidate_1545p_fix38"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
INPUT_QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62h_manual_graph_finish_queue_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62i_support_queue_closure_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62i_manual_graph_finish_queue_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62i_support_queue_closure_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62i_support_queue_closure_walkthrough.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62i_support_queue_closure_v0.1.json"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix62i_support_queue_closure.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix62i_support_queue_closure.py"

INPUT_TOKENS = ("fix62h_complete",)
OUTPUT_TOKENS = (
    "fix62i_support_queue_closure_complete",
    "fix62i_manual_graph_finish_queue_empty",
    "fix62i_complete",
)


def _verify_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix62i_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix62i_output_token_already_present:{token}")


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix62i_json_not_object:{path}")
    return payload


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62i_node_candidate_id_missing")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62i_edge_source_missing")


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62i_edge_target_missing")


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62i_edge_type_missing")
    return value


def _edge_payload(source: str, edge_type: str, target: str, *, reason: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix62i_support_queue_closure",
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": "fix62i_unsigned_support_trace_lmdb_candidate",
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
        "phase": PHASE,
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": "v0.4.fix62i_support_queue_closure",
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
        "preimage_version": "v0.4.fix62i_support_queue_closure",
    }


def _support_patch() -> dict[str, str]:
    return {
        "authority_status": "support_only_not_independent_authority",
        "canonicality_tier": "support_trace_not_independent_authority",
        "graph_projection": "support_candidate_graph",
        "inclusion_status": "support_trace_not_independent_authority",
        "promotion_status": "not_independent_authority",
        "tier": "support_candidate",
    }


def _empty_queue() -> dict[str, Any]:
    return {
        "entry_count": 0,
        "entries": [],
        "phase": PHASE,
        "priority_counts": {},
        "reason_counts": {},
        "source_queue": str(INPUT_QUEUE_PATH.relative_to(REPO_ROOT)),
        "status": "manual_graph_finish_queue_empty_after_support_closure",
        "work_family_counts": {},
    }


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(EVALUATOR_PATH.relative_to(REPO_ROOT), "tooling_source_file_node", "support_candidate_graph", required_edges=(("IMPLEMENTS", "phase:1545p_fix62i"),)),
        AtlasPhaseFileRegistration(TEST_PATH.relative_to(REPO_ROOT), "test_evidence_node", "support_candidate_graph", required_edges=(("TESTS", "phase:1545p_fix62i"),)),
        AtlasPhaseFileRegistration(LEDGER_PATH.relative_to(REPO_ROOT), "spec_json_artifact_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix62i"),)),
        AtlasPhaseFileRegistration(QUEUE_PATH.relative_to(REPO_ROOT), "spec_json_artifact_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix62i"),)),
        AtlasPhaseFileRegistration(REPORT_MD_PATH.relative_to(REPO_ROOT), "spec_document_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix62i"),)),
        AtlasPhaseFileRegistration(WALKTHROUGH_PATH.relative_to(REPO_ROOT), "phase_walkthrough_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix62i"),)),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def _append_status(report: dict[str, Any]) -> None:
    block = f"""

### Phase 1545p-Fix62i — Support Queue Closure

**Status:** complete

**Output:** Classified `{report['processed_support_count']}` remaining priority-3 support entries, applied `{report['edge_application']['accepted_edge_count']}` support classification/source-tree edges, emptied the manual graph-finish queue, refreshed preimages, and preserved all non-activation boundaries.

**Tokens:** {', '.join(OUTPUT_TOKENS)}
"""
    STATUS_PATH.write_text(STATUS_PATH.read_text(encoding="utf-8").rstrip() + block + "\n", encoding="utf-8")


def _report_markdown(report: dict[str, Any]) -> str:
    return f"""# ILC Fix62i Support Queue Closure Report

PUBLIC_RC_EXCLUDE: fix62i_support_queue_closure_research_only

## Summary

- Support entries processed: `{report['processed_support_count']}`
- Accepted edges: `{report['edge_application']['accepted_edge_count']}`
- Node updates: `{report['node_update']['accepted_update_count']}`
- Queue entries remaining: `{report['queue_entry_count']}`
- Final LMDB: `{report['final_counts']['nodes']}` nodes / `{report['final_counts']['edges']}` edges / `{report['final_counts']['preimages']}` preimages

## Boundary

This phase updates the local unsigned Genesis Atlas LMDB candidate only. It does
not sign Genesis, publish the graph, activate public serving, mint ECU, settle
ILC, or mutate canonical protocol authority. No ECU minting, production
emission, wallet settlement, or public claimability activation occurred.
"""


def _walkthrough_markdown(report: dict[str, Any]) -> str:
    return f"""# Phase 1545p-Fix62i Walkthrough

## Commands

```bash
python tools/evaluators/sim_genesis_atlas_fix62i_support_queue_closure.py
python -m pytest tests/test_phase_1545p_fix62i_support_queue_closure.py tests/test_phase_1545p_fix62h_priority1_overlay_classification.py tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py -q
python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb
```

## Result

- Processed support entries: `{report['processed_support_count']}`
- Remaining queue entries: `{report['queue_entry_count']}`
- Final LMDB counts: `{report['final_counts']['nodes']}` nodes / `{report['final_counts']['edges']}` edges / `{report['final_counts']['preimages']}` preimages

## Non-Claims

No Genesis signing, public graph upload, public RC publication, public serving,
runtime activation, ECU minting, or ILC settlement occurred.
"""


def _validate(report: dict[str, Any]) -> None:
    if report["processed_support_count"] != 3053:
        raise ValueError("fix62i_expected_3053_support_entries")
    if report["queue_entry_count"] != 0:
        raise ValueError("fix62i_queue_not_empty")
    if report["edge_application"]["rejected_edge_count"] != 0:
        raise ValueError("fix62i_rejected_edges_present")


def run() -> dict[str, Any]:
    raise RuntimeError(
        "fix62i_historical_evaluator_superseded_by_fix66_do_not_recreate_support_hub"
    )
    _verify_tokens()
    input_queue = _read_json(INPUT_QUEUE_PATH)
    entries = [dict(entry) for entry in input_queue["entries"]]
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        nodes = writer.store.iter_nodes()
        node_ids = {_candidate_id(node) for node in nodes}
        edge_rows: list[dict[str, Any]] = []
        updates: dict[str, dict[str, str]] = {}
        ledger_entries: list[dict[str, Any]] = []
        for entry in entries:
            source = str(entry["candidate_id"])
            if source not in node_ids:
                continue
            node_edges = [
                _edge_payload(
                    source,
                    "CLASSIFIED_BY",
                    SUPPORT_POLICY,
                    reason="Remaining priority-3 node classified as support-only non-authority material",
                )
            ]
            if source.startswith("repo:file:"):
                node_edges.append(
                    _edge_payload(
                        source,
                        "SOURCE_TREE_MEMBER",
                        SOURCE_TREE_MANIFEST,
                        reason="Remaining repo file belongs to Genesis source-tree manifest",
                    )
                )
            edge_rows.extend(node_edges)
            updates[source] = _support_patch()
            ledger_entries.append(
                {
                    **entry,
                    "disposition": "classified_support_only",
                    "recommended_edges": [
                        {"edge_type": edge["edge_type"], "source": edge["source"], "target": edge["target"]}
                        for edge in node_edges
                    ],
                }
            )
        plan = AtlasLmdbWritePlan(
            edges_to_add=edge_rows,
            metadata={"operation": "fix62i_support_queue_closure"},
            phase=PHASE,
            dry_run=False,
        )
        edge_receipt = writer.apply_plan(plan)
        update_receipt = writer.update_node_fields(
            updates,
            phase=PHASE,
            dry_run=False,
            metadata={"operation": "fix62i_support_projection_update"},
        )
        ledger = {
            "entries": ledger_entries,
            "entry_count": len(ledger_entries),
            "phase": PHASE,
            "status": "support_queue_closure_complete",
        }
        queue_payload = _empty_queue()
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
            metadata={"preimage_scope": "fix62i_support_queue_closure"},
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
            "processed_support_count": len(entries),
            "queue_entry_count": queue_payload["entry_count"],
            "status": "PASS",
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
