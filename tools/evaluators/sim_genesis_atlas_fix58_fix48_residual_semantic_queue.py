#!/usr/bin/env python3
"""Apply Fix58 manually reviewed residual queue edges to the unified Atlas LMDB.

PUBLIC_RC_EXCLUDE: fix58_residual_semantic_queue_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB research annotation pass; not Genesis signing, public graph upload, canonical mutation, runtime activation, or public RC publication.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
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
    _candidate_id,
    _edge_source,
    _edge_target,
    _edge_type,
)


PHASE = "1545p-Fix58"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix58_residual_queue_review_ledger_v0.1.md"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix58_residual_queue_application_report_v0.1.json"
EXPECTED_ENTRIES = 101

ALLOWED_EDGE_TYPES = frozenset(
    {
        "REFERENCES_AUTHORITY",
        "TESTS",
        "IMPLEMENTS",
        "DERIVED_FROM",
        "CLASSIFIED_BY",
        "EVIDENCES",
        "CARRIES_FORWARD",
        "NEGATIVE_ASSERTS",
        "IMPORTS_MODULE",
        "SOURCE_TREE_MEMBER",
    }
)


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
        raise ValueError("fix58_edge_confidence_invalid") from exc
    if not confidence.is_finite():
        raise ValueError("fix58_edge_confidence_not_finite")
    return str(confidence)


def _load_ledger() -> dict[str, Any]:
    text = LEDGER_PATH.read_text(encoding="utf-8")
    match = re.search(r"```json\n(.*?)\n```", text, flags=re.DOTALL)
    if match is None:
        raise ValueError("fix58_ledger_json_block_missing")
    ledger = json.loads(match.group(1))
    if not isinstance(ledger, dict):
        raise ValueError("fix58_ledger_object_required")
    entries = ledger.get("entries")
    if not isinstance(entries, list) or not all(isinstance(row, dict) for row in entries):
        raise ValueError("fix58_ledger_entries_list_required")
    if len(entries) != EXPECTED_ENTRIES:
        raise ValueError(f"fix58_ledger_entry_count_mismatch:{len(entries)}")
    for entry in entries:
        disposition = entry.get("disposition")
        if disposition not in {"add_edge", "support_only", "defer"}:
            raise ValueError(f"fix58_invalid_disposition:{disposition}")
        if entry.get("disposition") == "add_edge":
            recommended_edges = entry.get("recommended_edges")
            if not isinstance(recommended_edges, list) or not recommended_edges:
                raise ValueError("fix58_add_edge_entry_without_edges")
    return ledger


def _edge_status_counts(ledger: dict[str, Any]) -> Counter[str]:
    return Counter(str(entry.get("disposition", "")) for entry in ledger["entries"])


def _candidate_edges(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for entry in ledger["entries"]:
        if entry.get("disposition") != "add_edge":
            continue
        recommended_edges = entry.get("recommended_edges", [])
        if not isinstance(recommended_edges, list):
            raise ValueError("fix58_recommended_edges_list_required")
        for edge in recommended_edges:
            if not isinstance(edge, dict):
                raise ValueError("fix58_recommended_edge_object_required")
            edges.append(edge)
    return edges


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
        raise ValueError("fix58_edge_source_missing")
    if not isinstance(target, str) or not target:
        raise ValueError("fix58_edge_target_missing")
    if not isinstance(edge_type, str) or not edge_type:
        raise ValueError("fix58_edge_type_missing")
    confidence = _validate_confidence(edge.get("confidence", "0.85"))
    edge_id = _edge_id(source, edge_type, target)
    return {
        "annotation_method": "manual_reviewed",
        "annotation_phase": "phase_1545p_fix58",
        "annotation_reviewer": "human",
        "candidate_status": "applied_to_unified_lmdb_fix58",
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
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    validated: list[dict[str, Any]] = []
    missing_target_rejections: list[dict[str, Any]] = []
    other_rejections: list[dict[str, Any]] = []
    seen_edge_ids: set[str] = set()
    seen_semantics: set[tuple[str, str, str]] = set()
    for raw_edge in candidate_edges:
        try:
            edge = _build_edge(raw_edge)
        except ValueError as exc:
            other_rejections.append({"raw_edge": raw_edge, "reason": str(exc)})
            continue
        source = edge["source"]
        target = edge["target"]
        edge_type = edge["edge_type"]
        edge_id = edge["edge_id"]
        semantic = (source, edge_type, target)
        reason = ""
        missing_endpoint = False
        if edge_type == "GOVERNS":
            reason = "governs_edge_forbidden"
        elif edge_type not in ALLOWED_EDGE_TYPES:
            reason = f"edge_type_not_allowed:{edge_type}"
        elif source not in node_ids:
            reason = "source_node_missing"
            missing_endpoint = True
        elif target not in node_ids:
            reason = "target_node_missing"
            missing_endpoint = True
        elif source == target:
            reason = "self_loop_rejected"
        elif edge_id in existing_edge_ids or semantic in existing_semantics:
            reason = "duplicate_existing_edge_rejected"
        elif edge_id in seen_edge_ids or semantic in seen_semantics:
            reason = "duplicate_batch_edge_rejected"
        if reason:
            rejection = {
                "edge_id": edge_id,
                "edge_type": edge_type,
                "reason": reason,
                "source": source,
                "target": target,
            }
            if missing_endpoint:
                missing_target_rejections.append(rejection)
            else:
                other_rejections.append(rejection)
            continue
        validated.append(edge)
        seen_edge_ids.add(edge_id)
        seen_semantics.add(semantic)
    return validated, missing_target_rejections, other_rejections


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
        raise ValueError("fix58_unified_lmdb_missing")
    ledger = _load_ledger()
    dispositions = _edge_status_counts(ledger)
    candidate_edges = _candidate_edges(ledger)

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
            raise ValueError("fix58_graph_payload_missing")
        graph_edges = graph_payload.get("edges")
        if not isinstance(graph_edges, list):
            raise ValueError("fix58_graph_payload_edges_list_required")
        pre_graph_edge_count = len(graph_edges)
        node_ids = {_candidate_id(node) for node in nodes}
        existing_edge_ids, existing_semantics = _existing_edge_indexes(pre_edges)
        pre_existing_fix58_edges = [
            edge for edge in pre_edges if edge.get("annotation_phase") == "phase_1545p_fix58"
        ]
        if pre_existing_fix58_edges:
            raise ValueError("fix58_edges_already_present_in_lmdb")

        validated_edges, missing_target_rejections, other_rejections = _validate_edges(
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
                f"fix58_lmdb_edge_count_mismatch:{pre_edge_count}:{len(validated_edges)}:{post_edge_count}"
            )
        updated_payload_readback = store.get_graph_payload()
        if not isinstance(updated_payload_readback, dict):
            raise ValueError("fix58_graph_payload_readback_missing")
        if len(updated_payload_readback.get("edges", [])) != pre_graph_edge_count + len(validated_edges):
            raise ValueError("fix58_graph_payload_edge_count_mismatch")

        report: dict[str, Any] = {
            "deferred_entries": [
                str(entry["node_id"])
                for entry in ledger["entries"]
                if entry.get("disposition") == "defer"
            ],
            "dispositions": {
                "add_edge": int(dispositions["add_edge"]),
                "defer": int(dispositions["defer"]),
                "support_only": int(dispositions["support_only"]),
            },
            "duplicate_or_policy_rejections": other_rejections,
            "edge_count_nondecreasing": post_edge_count >= pre_edge_count,
            "ledger_path": str(LEDGER_PATH.relative_to(REPO_ROOT)),
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "missing_target_rejections": missing_target_rejections,
            "new_edge_ids": [edge["edge_id"] for edge in validated_edges],
            "new_edges": [_report_edge(edge) for edge in validated_edges],
            "new_edges_applied": len(validated_edges),
            "new_edges_attempted": len(candidate_edges),
            "non_claims": [
                "Fix58 does not improve lambda2 or spectral connectivity",
                "Fix58 does not add GOVERNS edges",
                "New edges are manual-reviewed research annotations; they do not grant authority, signing eligibility, or public RC clearance",
                "No CDL mutation, signing, runtime activation",
            ],
            "phase": PHASE,
            "post_application_edge_count": post_edge_count,
            "pre_application_edge_count": pre_edge_count,
            "status": "PASS",
            "total_queue_entries": len(ledger["entries"]),
        }
        store.put_meta("fix58_residual_semantic_queue", report)
    finally:
        store.close()

    _atomic_write_json(REPORT_PATH, report)
    print(
        "Done. status=PASS, "
        f"dispositioned={report['total_queue_entries']}, "
        f"add_edge={report['dispositions']['add_edge']}, "
        f"support_only={report['dispositions']['support_only']}, "
        f"defer={report['dispositions']['defer']}, "
        f"new_edges_applied={report['new_edges_applied']}, "
        f"missing_target_rejected={len(report['missing_target_rejections'])}"
    )
    return report


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
