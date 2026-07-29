#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Apply the Phase 1573aj Atlas edge-retirement migration.

This tool consumes the source-read replacement plan emitted by Phase 1573ai-Fix1,
removes only the exact retired semantic triples, adds deterministic replacement
edges through the Atlas safe writer, and writes a receipt for tests and review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    _KNOWN_EDGE_TYPES,
    deterministic_edge_id,
    write_json_atomic,
)


PHASE = "1573aj"
READY_CLASSIFICATION = "manually_classified_phase_1573ai_fix1"
RETIRED_EDGE_TYPES = {
    "REFERENCES",
    "IMPLEMENTS_MODULE",
    "RATIFICATION_EVIDENCE_FOR",
    "USES",
    "OPENED_FOR",
    "PRELOCK_FOR",
}


class MigrationError(RuntimeError):
    """Raised when the rehearsal plan or live LMDB state is unsafe to mutate."""


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MigrationError(f"json_root_not_object:{path}")
    return payload


def _graph_payload_digest(writer: AtlasLmdbSafeWriter) -> str:
    payload = writer.store.get_graph_payload() or {}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _edge_semantic(edge: dict[str, Any]) -> tuple[str, str, str]:
    source = edge.get("source") or edge.get("src")
    target = edge.get("target") or edge.get("tgt")
    edge_type = edge.get("edge_type")
    if not all(isinstance(value, str) and value for value in (source, edge_type, target)):
        raise MigrationError(f"edge_semantic_missing:{edge}")
    return str(source), str(edge_type), str(target)


def _edge_counts(writer: AtlasLmdbSafeWriter) -> dict[str, int]:
    return dict(Counter(str(edge.get("edge_type", "")) for edge in writer.store.iter_edges()))


def _validate_plan(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("apply_recommendation") != "apply_ready":
        raise MigrationError("rehearsal_not_apply_ready")
    if payload.get("lmdb_mutated") is not False:
        raise MigrationError("rehearsal_already_mutated")
    if payload.get("all_rows_covered") is not True:
        raise MigrationError("rehearsal_rows_not_fully_covered")
    counts = payload.get("classification_counts")
    if not isinstance(counts, dict):
        raise MigrationError("classification_counts_missing")
    total = payload.get("total_candidate_rows")
    if counts.get(READY_CLASSIFICATION) != total:
        raise MigrationError("manual_classification_count_mismatch")
    if counts.get("needs_manual_source_read") != 0:
        raise MigrationError("manual_source_read_remaining")
    rows = payload.get("replacement_plan")
    if not isinstance(rows, list) or not rows:
        raise MigrationError("replacement_plan_missing")
    if len(rows) != total:
        raise MigrationError("replacement_plan_total_mismatch")

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise MigrationError(f"replacement_row_not_object:{index}")
        if row.get("classification") != READY_CLASSIFICATION:
            raise MigrationError(f"replacement_row_not_ready:{index}")
        original_type = row.get("original_edge_type")
        if original_type not in RETIRED_EDGE_TYPES:
            raise MigrationError(f"source_edge_type_not_retired:{index}:{original_type}")
        replacements = row.get("proposed_replacement_edges")
        if not isinstance(replacements, list) or not replacements:
            raise MigrationError(f"replacement_edges_missing:{index}")
        for replacement in replacements:
            if not isinstance(replacement, dict):
                raise MigrationError(f"replacement_edge_not_object:{index}")
            edge_type = replacement.get("edge_type")
            if edge_type not in _KNOWN_EDGE_TYPES:
                raise MigrationError(f"unknown_replacement_edge_type:{edge_type}")
            source = replacement.get("source")
            target = replacement.get("target")
            if not all(isinstance(value, str) and value for value in (source, target)):
                raise MigrationError(f"replacement_endpoint_missing:{index}")
    return rows


def _replacement_edges(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for row in rows:
        for replacement in row["proposed_replacement_edges"]:
            source = str(replacement["source"])
            edge_type = str(replacement["edge_type"])
            target = str(replacement["target"])
            edge_id = deterministic_edge_id(source, edge_type, target)
            edges.append(
                {
                    "annotation_method": "phase_1573aj_atlas_edge_retirement_apply",
                    "annotation_phase": "phase_1573aj",
                    "candidate_status": "applied_to_unified_lmdb_via_safe_writer",
                    "classification_basis": replacement.get(
                        "classification_basis",
                        "manual_source_read_phase_1573ai_fix1",
                    ),
                    "classification_reason": row.get("classification_reason", ""),
                    "edge_id": edge_id,
                    "edge_type": edge_type,
                    "replacement_for_edge_id": row.get("original_edge_id", ""),
                    "replacement_for_edge_type": row.get("original_edge_type", ""),
                    "source": source,
                    "src": source,
                    "target": target,
                    "tgt": target,
                }
            )
    return edges


def apply_migration(
    *,
    rehearsal_json: Path,
    lmdb_root: Path,
    receipt_json: Path,
    dry_run: bool,
) -> dict[str, Any]:
    payload = _load_json(rehearsal_json)
    rows = _validate_plan(payload)
    source_semantics = {
        (str(row["source"]), str(row["original_edge_type"]), str(row["target"]))
        for row in rows
    }
    replacements = _replacement_edges(rows)
    replacement_semantics = [_edge_semantic(edge) for edge in replacements]

    writer = AtlasLmdbSafeWriter(lmdb_root)
    try:
        before_inspect = writer.inspect()
        before_edge_counts = _edge_counts(writer)
        before_digest = _graph_payload_digest(writer)
        live_semantics = {_edge_semantic(edge) for edge in writer.store.iter_edges()}
        missing_source_semantics = sorted(source_semantics - live_semantics)
        if missing_source_semantics:
            raise MigrationError(f"source_semantics_missing:{len(missing_source_semantics)}")

        removal_dry_run = writer.remove_edges_by_semantic(
            source_semantics,
            phase=PHASE,
            dry_run=True,
            metadata={"source": "phase_1573ai_fix1_replacement_plan"},
        )
        if removal_dry_run["removed_edge_count"] != len(source_semantics):
            raise MigrationError("removal_dry_run_count_mismatch")
        if removal_dry_run["missing_semantic_count"] != 0:
            raise MigrationError("removal_dry_run_missing_semantics")

        removal_receipt = writer.remove_edges_by_semantic(
            source_semantics,
            phase=PHASE,
            dry_run=dry_run,
            metadata={"source": "phase_1573ai_fix1_replacement_plan"},
        )
        if dry_run:
            after_removal_semantics = live_semantics - source_semantics
        else:
            after_removal_semantics = {_edge_semantic(edge) for edge in writer.store.iter_edges()}

        already_present_semantics = sorted(set(replacement_semantics) & after_removal_semantics)
        duplicate_replacement_semantics = sorted(
            semantic
            for semantic, count in Counter(replacement_semantics).items()
            if count > 1
        )

        add_plan = AtlasLmdbWritePlan(
            edges_to_add=replacements,
            metadata={
                "migration_phase": PHASE,
                "source": "phase_1573ai_fix1_replacement_plan",
            },
            phase=PHASE,
            dry_run=dry_run,
        )
        add_receipt = writer.apply_plan(add_plan)
        if add_receipt["rejected_edge_count"] != 0:
            raise MigrationError(f"replacement_edges_rejected:{add_receipt['rejected_edges']}")

        after_inspect = writer.inspect()
        after_edge_counts = _edge_counts(writer)
        after_digest = _graph_payload_digest(writer)
        final_retired_counts = {
            edge_type: after_edge_counts.get(edge_type, 0) for edge_type in sorted(RETIRED_EDGE_TYPES)
        }
        preimage_receipt = writer.write_metadata(
            f"atlas_edge_retirement_preimage_consistency:{PHASE}",
            {
                "phase": PHASE,
                "preimage_action": "existing_preimages_preserved_edge_payload_rewritten",
                "preimage_count_after": after_inspect["preimage_count"],
                "preimage_count_before": before_inspect["preimage_count"],
            },
            phase=PHASE,
            dry_run=dry_run,
        )
        status = (
            "PASS"
            if dry_run
            or (
                all(after_inspect["invariants"].values())
                and after_inspect["edge_id_debt_count"] == 0
                and after_inspect["duplicate_semantic_edge_extra_row_count"] == 0
                and all(count == 0 for count in final_retired_counts.values())
            )
            else "FAIL"
        )
        receipt: dict[str, Any] = {
            "accepted_replacement_edge_count": add_receipt["accepted_edge_count"],
            "already_present_replacement_semantic_count": len(already_present_semantics),
            "already_present_replacement_semantics": [
                {"source": source, "edge_type": edge_type, "target": target}
                for source, edge_type, target in already_present_semantics
            ],
            "applied_replacement_edge_ids_unique": len(
                {edge["edge_id"] for edge in add_receipt.get("accepted_edges", [])}
            )
            == add_receipt["accepted_edge_count"],
            "before_edge_counts": before_edge_counts,
            "before_graph_payload_sha256": before_digest,
            "before_inspect": before_inspect,
            "duplicate_replacement_semantic_count": len(duplicate_replacement_semantics),
            "duplicate_replacement_semantics": [
                {"source": source, "edge_type": edge_type, "target": target}
                for source, edge_type, target in duplicate_replacement_semantics
            ],
            "dry_run": dry_run,
            "final_retired_edge_counts": final_retired_counts,
            "lmdb_path": str(lmdb_root),
            "mutated": not dry_run,
            "phase": PHASE,
            "post_edge_counts": after_edge_counts,
            "post_graph_payload_sha256": after_digest,
            "post_inspect": after_inspect,
            "preimage_receipt": preimage_receipt,
            "removal_receipt": removal_receipt,
            "removed_edge_count": removal_receipt["removed_edge_count"],
            "replacement_apply_receipt": add_receipt,
            "replacement_edge_row_count": len(replacements),
            "replacement_unique_semantic_count": len(set(replacement_semantics)),
            "retired_edge_types": sorted(RETIRED_EDGE_TYPES),
            "source_candidate_edge_count": len(source_semantics),
            "source_rehearsal_json": str(rehearsal_json),
            "status": status,
        }
        writer.write_metadata(
            f"atlas_edge_retirement_migration:{PHASE}",
            receipt,
            phase=PHASE,
            dry_run=dry_run,
        )
    finally:
        writer.close()

    write_json_atomic(receipt_json, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rehearsal-json",
        type=Path,
        default=Path("docs/specs/ilc_atlas_edge_retirement_rehearsal_1573ai_v0.1.json"),
    )
    parser.add_argument(
        "--lmdb",
        type=Path,
        default=Path("out/genesis_base_graph_v0.4_unified.lmdb"),
    )
    parser.add_argument(
        "--receipt-json",
        type=Path,
        default=Path("docs/specs/ilc_atlas_edge_retirement_migration_1573aj_v0.1.json"),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    receipt = apply_migration(
        rehearsal_json=args.rehearsal_json,
        lmdb_root=args.lmdb,
        receipt_json=args.receipt_json,
        dry_run=args.dry_run,
    )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
