#!/usr/bin/env python3
"""Repair edge IDs and materialize unsigned Atlas LMDB preimages.

PUBLIC_RC_EXCLUDE: fix60_edge_id_preimage_debt_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Genesis Atlas LMDB maintenance pass;
not Genesis signing, public graph upload, canonical mutation, runtime
activation, or public RC publication.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_lmdb_writer import (  # noqa: E402
    AtlasLmdbSafeWriter,
    write_json_atomic,
)


PHASE = "1545p-Fix60"
PREIMAGE_VERSION = "v0.4"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
FIX59_REPORT = REPO_ROOT / "out/genesis_atlas_fix59_missing_target_materialization_report_v0.1.json"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix60_edge_id_preimage_debt_report_v0.1.json"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"

INPUT_TOKENS = (
    "fix59_complete",
    "fix59_new_edges_have_deterministic_edge_ids",
    "fix59_missing_edge_id_debt_recorded_for_fix60",
)
OUTPUT_TOKENS = (
    "fix60_edge_id_debt_cleared",
    "fix60_node_preimages_materialized",
    "fix60_lmdb_preimage_count_equals_node_count",
    "fix60_complete",
)
NODE_PREIMAGE_FIELDS = (
    "candidate_id",
    "label",
    "node_kind",
    "graph_projection",
    "canonicality_tier",
    "annotation_method",
    "annotation_phase",
)


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix60_json_object_required:{path}")
    return payload


def _status_text() -> str:
    return STATUS_PATH.read_text(encoding="utf-8")


def _verify_tokens() -> None:
    status = _status_text()
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix60_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix60_output_token_already_present:{token}")
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError(f"fix60_lmdb_missing:{LMDB_ROOT}")


def _edge_source(edge: dict[str, Any]) -> str:
    value = edge.get("source", edge.get("source_candidate_id", edge.get("src", edge.get("from"))))
    if not isinstance(value, str) or not value:
        raise ValueError("fix60_edge_source_missing")
    return value


def _edge_target(edge: dict[str, Any]) -> str:
    value = edge.get("target", edge.get("target_candidate_id", edge.get("tgt", edge.get("to"))))
    if not isinstance(value, str) or not value:
        raise ValueError("fix60_edge_target_missing")
    return value


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type", edge.get("type", edge.get("kind")))
    if not isinstance(value, str) or not value:
        raise ValueError("fix60_edge_type_missing")
    return value


def _edge_id(edge: dict[str, Any]) -> str:
    value = edge.get("edge_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix60_edge_id_missing_after_repair")
    return value


def _edge_id_counts(edges: list[dict[str, Any]]) -> dict[str, int]:
    present = sum(1 for edge in edges if isinstance(edge.get("edge_id"), str) and edge.get("edge_id"))
    return {
        "missing": len(edges) - present,
        "present": present,
        "total": len(edges),
    }


def _node_preimage(node: dict[str, Any]) -> dict[str, Any]:
    fields = {field: node.get(field) for field in NODE_PREIMAGE_FIELDS}
    node_id = fields["candidate_id"]
    if not isinstance(node_id, str) or not node_id:
        raise ValueError("fix60_node_candidate_id_missing")
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


def _spot_checks(preimages: list[dict[str, Any]], *, limit: int = 5) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for record in preimages[:limit]:
        fields = record.get("fields")
        if not isinstance(fields, dict):
            raise ValueError("fix60_preimage_fields_missing")
        expected = _canonical_sha256(fields)
        observed = record.get("canonical_sha256")
        checks.append(
            {
                "canonical_sha256": observed,
                "expected_sha256": expected,
                "node_id": str(record.get("node_id", record.get("edge_id", ""))),
                "pass": observed == expected,
            }
        )
    return checks


def run() -> dict[str, Any]:
    _verify_tokens()
    fix59_report = _load_json(FIX59_REPORT)
    fix59_node_count = fix59_report.get("post_materialization_node_count")
    if not isinstance(fix59_node_count, int):
        raise ValueError("fix60_fix59_node_count_missing")

    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        nodes_before = writer.store.iter_nodes()
        edges_before = writer.store.iter_edges()
        if len(edges_before) < 74981:
            raise ValueError(f"fix60_edge_count_below_fix55_baseline:{len(edges_before)}")
        before_counts = _edge_id_counts(edges_before)

        repair_receipt = writer.repair_missing_edge_ids(phase=PHASE, dry_run=False)
        if repair_receipt.get("status") != "PASS":
            raise ValueError("fix60_edge_id_repair_failed")

        nodes = writer.store.iter_nodes()
        edges = writer.store.iter_edges()
        after_counts = _edge_id_counts(edges)
        if after_counts["missing"] != 0:
            raise ValueError(f"fix60_edge_id_debt_remaining:{after_counts['missing']}")

        node_preimages = [_node_preimage(node) for node in nodes]
        node_receipt = writer.write_preimages(
            node_preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "node"},
        )
        if node_receipt.get("status") != "PASS":
            raise ValueError("fix60_node_preimage_write_failed")

        edge_preimages = [_edge_preimage(edge) for edge in edges]
        edge_receipt = writer.write_preimages(
            edge_preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "edge"},
        )
        if edge_receipt.get("status") != "PASS":
            raise ValueError("fix60_edge_preimage_write_failed")

        node_preimage_readback_count = sum(
            1
            for record in writer.store.iter_preimages()
            if isinstance(record.get("node_id"), str) and record.get("node_id")
        )
        if node_preimage_readback_count != len(nodes):
            raise ValueError(
                f"fix60_node_preimage_count_mismatch:{node_preimage_readback_count}:{len(nodes)}"
            )

        report = {
            "edge_id_gaps_repaired": int(repair_receipt.get("repaired_edge_count", 0)),
            "edge_preimage_count_written": len(edge_preimages),
            "edges_missing_edge_id_after": after_counts["missing"],
            "edges_missing_edge_id_before": before_counts["missing"],
            "edges_with_edge_id_after": after_counts["present"],
            "edges_with_edge_id_before": before_counts["present"],
            "fix59_reported_node_count": fix59_node_count,
            "fix59_to_live_node_delta": len(nodes) - fix59_node_count,
            "lmdb_edge_count": len(edges),
            "lmdb_node_count": len(nodes),
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "node_preimage_count_written": len(node_preimages),
            "node_preimage_readback_count": node_preimage_readback_count,
            "non_claims": [
                "preimages are unsigned",
                "fix60 does not sign gossip publish or activate anything",
                "preimage format may require refinement at genesis signing ceremony",
            ],
            "phase": PHASE,
            "preimage_version": PREIMAGE_VERSION,
            "safe_writer_edge_id_repair_receipt": repair_receipt,
            "safe_writer_edge_preimage_receipt": edge_receipt,
            "safe_writer_node_preimage_receipt": node_receipt,
            "spot_checks": _spot_checks(node_preimages),
            "status": "PASS",
        }
        write_json_atomic(REPORT_PATH, report)
        writer.write_metadata("fix60_edge_id_preimage_debt", report, phase=PHASE, dry_run=False)
        return report
    finally:
        writer.close()


def main() -> int:
    report = run()
    print(
        "Done. "
        f"status={report['status']}, "
        f"nodes={report['lmdb_node_count']}, "
        f"node_preimages={report['node_preimage_count_written']}, "
        f"edge_id_gaps_repaired={report['edge_id_gaps_repaired']}, "
        f"edge_preimages={report['edge_preimage_count_written']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
