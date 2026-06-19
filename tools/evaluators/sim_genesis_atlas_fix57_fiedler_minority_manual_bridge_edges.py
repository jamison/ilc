#!/usr/bin/env python3
"""Apply Fix57 manually reviewed bridge edges to the unified Genesis Atlas LMDB.

PUBLIC_RC_EXCLUDE: fix57_fiedler_minority_manual_bridge_edges_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB research annotation pass; not Genesis signing, public graph upload, canonical mutation, runtime activation, or public RC publication.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (  # noqa: E402
    GenesisAtlasCandidateStore,
)
from ilc_core.storage.lmdb_public_runtime import DEFAULT_MAP_SIZE_BYTES  # noqa: E402
from tools.evaluators.sim_genesis_atlas_fix56_projection_aware_fiedler_rebaseline import (  # noqa: E402
    SPECTRAL_CAVEAT,
    _candidate_id,
    _edge_source,
    _edge_target,
    _edge_type,
    _fiedler_projection,
    _projection_nodes,
)


PHASE = "1545p-Fix57"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix57_non_out_minority_manual_read_ledger_v0.1.json"
FIX56_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix56_fiedler_rebaseline_report_v0.1.json"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix57_manual_bridge_edge_application_report_v0.1.json"

ALLOWED_EDGE_TYPES = frozenset(
    {
        "DERIVED_FROM",
        "GENERATED_BY",
        "EVIDENCES",
        "CLASSIFIED_BY",
        "SOURCE_TREE_MEMBER",
        "TESTS",
        "IMPLEMENTS",
        "REFERENCES_AUTHORITY",
        "CARRIES_FORWARD",
    }
)

APPLY_STATUS = "deep_manual_confirmed_not_applied"
SUPPORT_ONLY_STATUS = "manual_confirmed_support_only_not_applied"
ASSISTED_ONLY_STATUS = "recommended_not_applied"
EXPECTED_LEDGER_STATUS = "deep_manual_confirmation_complete"


def _canonical_text(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _atomic_write_json(path: Path, payload: Any) -> None:
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
            handle.write(_canonical_text(payload))
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _edge_id(source: str, edge_type: str, target: str) -> str:
    digest = hashlib.sha256(f"{source}|{edge_type}|{target}".encode("utf-8")).hexdigest()[:16]
    return f"edge:{digest}"


def _validate_confidence(value: Any) -> str:
    try:
        confidence = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("fix57_edge_confidence_invalid") from exc
    if not confidence.is_finite():
        raise ValueError("fix57_edge_confidence_not_finite")
    return str(confidence)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix57_json_object_required:{path}")
    return payload


def _load_ledger() -> dict[str, Any]:
    ledger = _load_json(LEDGER_PATH)
    entries = ledger.get("entries")
    if not isinstance(entries, list) or not all(isinstance(row, dict) for row in entries):
        raise ValueError("fix57_ledger_entries_list_required")
    if ledger.get("full_non_out_pass_status") != EXPECTED_LEDGER_STATUS:
        raise ValueError("fix57_ledger_deep_manual_confirmation_missing")
    edge_counts = Counter(
        str(edge.get("candidate_status", ""))
        for entry in entries
        for edge in entry.get("recommended_edges", [])
        if isinstance(edge, dict)
    )
    if edge_counts[APPLY_STATUS] < 1:
        raise ValueError("fix57_no_deep_manual_confirmed_edges_to_apply")
    return ledger


def _candidate_edges(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for entry in ledger["entries"]:
        recommended_edges = entry.get("recommended_edges", [])
        if not isinstance(recommended_edges, list):
            raise ValueError("fix57_recommended_edges_list_required")
        for edge in recommended_edges:
            if not isinstance(edge, dict):
                raise ValueError("fix57_recommended_edge_object_required")
            if edge.get("candidate_status") == APPLY_STATUS:
                edges.append(edge)
    return edges


def _edge_status_counts(ledger: dict[str, Any]) -> Counter[str]:
    return Counter(
        str(edge.get("candidate_status", ""))
        for entry in ledger["entries"]
        for edge in entry.get("recommended_edges", [])
        if isinstance(edge, dict)
    )


def _semantic_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (_edge_source(edge), _edge_type(edge), _edge_target(edge))


def _existing_edge_indexes(edges: list[dict[str, Any]]) -> tuple[set[str], set[tuple[str, str, str]]]:
    edge_ids: set[str] = set()
    semantics: set[tuple[str, str, str]] = set()
    for edge in edges:
        source, edge_type, target = _semantic_key(edge)
        if source and edge_type and target:
            semantics.add((source, edge_type, target))
            edge_ids.add(_edge_id(source, edge_type, target))
        explicit = edge.get("edge_id")
        if isinstance(explicit, str) and explicit:
            edge_ids.add(explicit)
    return edge_ids, semantics


def _build_edge(edge: dict[str, Any]) -> dict[str, Any]:
    source = edge.get("source")
    target = edge.get("target")
    edge_type = edge.get("edge_type")
    if not isinstance(source, str) or not source:
        raise ValueError("fix57_edge_source_missing")
    if not isinstance(target, str) or not target:
        raise ValueError("fix57_edge_target_missing")
    if not isinstance(edge_type, str) or not edge_type:
        raise ValueError("fix57_edge_type_missing")
    confidence = _validate_confidence(edge.get("confidence", "0.85"))
    edge_id = _edge_id(source, edge_type, target)
    return {
        "annotation_method": "manual_reviewed",
        "annotation_phase": "phase_1545p_fix57",
        "annotation_reviewer": "human",
        "candidate_status": "applied_to_unified_lmdb_fix57",
        "confidence": confidence,
        "edge_id": edge_id,
        "edge_type": edge_type,
        "evidence": str(edge.get("evidence", "")),
        "source": source,
        "source_annotation_method": str(edge.get("annotation_method", "")),
        "source_annotation_phase": str(edge.get("annotation_phase", "")),
        "source_candidate_status": str(edge.get("candidate_status", "")),
        "src": source,
        "target": target,
        "tgt": target,
    }


def _validate_edges(
    *,
    candidate_edges: list[dict[str, Any]],
    node_ids: set[str],
    existing_edge_ids: set[str],
    existing_semantics: set[tuple[str, str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    validated: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen_edge_ids: set[str] = set()
    seen_semantics: set[tuple[str, str, str]] = set()
    for raw_edge in candidate_edges:
        try:
            edge = _build_edge(raw_edge)
        except ValueError as exc:
            rejected.append({"raw_edge": raw_edge, "rejection_reason": str(exc)})
            continue
        source = edge["source"]
        target = edge["target"]
        edge_type = edge["edge_type"]
        edge_id = edge["edge_id"]
        semantic = (source, edge_type, target)
        reason = ""
        if edge_type == "GOVERNS":
            reason = "fix57_governs_edge_forbidden"
        elif edge_type not in ALLOWED_EDGE_TYPES:
            reason = f"fix57_edge_type_not_allowed:{edge_type}"
        elif source not in node_ids:
            reason = "fix57_source_node_missing"
        elif target not in node_ids:
            reason = "fix57_target_node_missing"
        elif source == target:
            reason = "fix57_self_loop_rejected"
        elif edge_id in existing_edge_ids or semantic in existing_semantics:
            reason = "fix57_duplicate_existing_edge_rejected"
        elif edge_id in seen_edge_ids or semantic in seen_semantics:
            reason = "fix57_duplicate_batch_edge_rejected"
        if reason:
            rejected.append(
                {
                    "edge_id": edge_id,
                    "edge_type": edge_type,
                    "rejection_reason": reason,
                    "source": source,
                    "target": target,
                }
            )
            continue
        validated.append(edge)
        seen_edge_ids.add(edge_id)
        seen_semantics.add(semantic)
    return validated, rejected


def _public_eligible_lambda2(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> float:
    projection_nodes = _projection_nodes(nodes, "public_eligible")
    metrics, _cluster = _fiedler_projection(
        projection="public_eligible",
        nodes=projection_nodes,
        edges=edges,
    )
    return float(metrics["lambda2"])


def _fix56_public_eligible_lambda2() -> float:
    report = _load_json(FIX56_REPORT_PATH)
    return float(report["projections"]["public_eligible"]["lambda2"])


def _compact_rejection(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "edge_id": edge.get("edge_id", ""),
        "edge_type": edge.get("edge_type", ""),
        "rejection_reason": edge.get("rejection_reason", ""),
        "source": edge.get("source", ""),
        "target": edge.get("target", ""),
    }


def _report_edge(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "annotation_method": edge["annotation_method"],
        "annotation_phase": edge["annotation_phase"],
        "edge_id": edge["edge_id"],
        "edge_type": edge["edge_type"],
        "source_annotation_method": edge["source_annotation_method"],
        "source_annotation_phase": edge["source_annotation_phase"],
        "src": edge["src"],
        "tgt": edge["tgt"],
    }


def run() -> dict[str, Any]:
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError("fix57_unified_lmdb_missing")
    ledger = _load_ledger()
    candidate_edges = _candidate_edges(ledger)
    edge_status_counts = _edge_status_counts(ledger)

    store = GenesisAtlasCandidateStore(
        LMDB_ROOT,
        allow_synthetic_edge_keys=True,
        map_size=DEFAULT_MAP_SIZE_BYTES * 4,
    )
    try:
        nodes = store.iter_nodes()
        pre_edges = store.iter_edges()
        graph_payload = store.get_graph_payload()
        if not isinstance(graph_payload, dict):
            raise ValueError("fix57_graph_payload_missing")
        graph_edges = graph_payload.get("edges")
        if not isinstance(graph_edges, list):
            raise ValueError("fix57_graph_payload_edges_list_required")
        pre_graph_edge_count = len(graph_edges)
        node_ids = {_candidate_id(node) for node in nodes}
        existing_edge_ids, existing_semantics = _existing_edge_indexes(pre_edges)
        pre_existing_fix57_edges = [
            edge for edge in pre_edges if edge.get("annotation_phase") == "phase_1545p_fix57"
        ]
        if pre_existing_fix57_edges:
            raise ValueError("fix57_edges_already_present_in_lmdb")

        validated_edges, rejected_edges = _validate_edges(
            candidate_edges=candidate_edges,
            node_ids=node_ids,
            existing_edge_ids=existing_edge_ids,
            existing_semantics=existing_semantics,
        )
        pre_edge_count = len(pre_edges)
        store.put_edges(validated_edges)
        updated_payload = dict(graph_payload)
        updated_payload["edges"] = [*graph_edges, *validated_edges]
        store.put_graph_payload(updated_payload)
        post_edges = store.iter_edges()
        post_edge_count = len(post_edges)
        expected_post_edge_count = pre_edge_count + len(validated_edges)
        if post_edge_count != expected_post_edge_count:
            raise ValueError(
                f"fix57_lmdb_edge_count_mismatch:{pre_edge_count}:{len(validated_edges)}:{post_edge_count}"
            )
        updated_payload_readback = store.get_graph_payload()
        if not isinstance(updated_payload_readback, dict):
            raise ValueError("fix57_graph_payload_readback_missing")
        if len(updated_payload_readback.get("edges", [])) != pre_graph_edge_count + len(validated_edges):
            raise ValueError("fix57_graph_payload_edge_count_mismatch")

        post_lambda2 = _public_eligible_lambda2(nodes, post_edges)
        pre_lambda2 = _fix56_public_eligible_lambda2()
        payload_digest = hashlib.sha256(_canonical_text(updated_payload_readback).encode("utf-8")).hexdigest()
        rejection_reasons = Counter(str(edge.get("rejection_reason", "")) for edge in rejected_edges)
        report: dict[str, Any] = {
            "edge_application": {
                "attempted": len(candidate_edges),
                "rejected": len(rejected_edges),
                "rejection_reason_counts": dict(sorted(rejection_reasons.items())),
                "rejections": [_compact_rejection(edge) for edge in rejected_edges],
                "validated_and_applied": len(validated_edges),
            },
            "fiedler": {
                "delta_lambda2": float(post_lambda2 - pre_lambda2),
                "post_application_lambda2": float(post_lambda2),
                "pre_application_lambda2": float(pre_lambda2),
                "projection": "public_eligible",
            },
            "ledger_edge_counts": {
                "deep_manual_confirmed_not_applied": int(edge_status_counts[APPLY_STATUS]),
                "manual_confirmed_support_only_not_applied": int(edge_status_counts[SUPPORT_ONLY_STATUS]),
                "recommended_not_applied": int(edge_status_counts[ASSISTED_ONLY_STATUS]),
                "total_recommended_edges": int(sum(edge_status_counts.values())),
            },
            "ledger_entry_counts": {
                "full_non_out_pass_status": str(ledger["full_non_out_pass_status"]),
                "total_entries": len(ledger["entries"]),
            },
            "ledger_path": "docs/specs/ilc_fix57_public_eligible_minority_audit_ledger_v0.1.md",
            "ledger_source": str(LEDGER_PATH.relative_to(REPO_ROOT)),
            "lmdb_edge_counts": {
                "delta": len(validated_edges),
                "post_application": post_edge_count,
                "pre_application": pre_edge_count,
            },
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "new_edges": [_report_edge(edge) for edge in validated_edges],
            "phase": PHASE,
            "post_application_graph_payload_digest": payload_digest,
            "spectral_caveat": (
                "lambda2 improvement is a spectral research metric -- it does not constitute "
                "protocol authority improvement"
            ),
            "status": "PASS",
        }
        store.put_meta("fix57_manual_bridge_edge_application", report)
    finally:
        store.close()

    _atomic_write_json(REPORT_PATH, report)
    print(
        "Done. status=PASS, "
        f"add_edge_rows={len(candidate_edges)}, "
        f"validated={report['edge_application']['validated_and_applied']}, "
        f"rejected={report['edge_application']['rejected']}, "
        f"pre_edges={report['lmdb_edge_counts']['pre_application']}, "
        f"post_edges={report['lmdb_edge_counts']['post_application']}, "
        f"pre_lambda2={report['fiedler']['pre_application_lambda2']}, "
        f"post_lambda2={report['fiedler']['post_application_lambda2']}"
    )
    return report


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
