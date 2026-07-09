from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ilc_core.storage.genesis_atlas_lmdb_writer import AtlasLmdbSafeWriter


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
REHEARSAL_JSON = (
    REPO_ROOT / "docs/specs/ilc_atlas_edge_retirement_rehearsal_1573ai_v0.1.json"
)
PHASE_1574_PROMPT = (
    REPO_ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md"
)

CANDIDATE_EDGE_TYPES = {
    "REFERENCES",
    "IMPLEMENTS_MODULE",
    "RATIFICATION_EVIDENCE_FOR",
    "USES",
    "OPENED_FOR",
    "PRELOCK_FOR",
}

KEEP_CLASS_EDGE_TYPES = {
    "CONTAINS_FILE",
    "CONTAINS_GROUP",
    "CONTAINS_PARTITION",
    "SAME_SOURCE",
    "GOVERNS",
    "CONSTRAINS",
    "SAME_AUTHORITY",
    "SUPERSEDED_BY",
}


def _rehearsal() -> dict:
    return json.loads(REHEARSAL_JSON.read_text(encoding="utf-8"))


def _live_candidate_rows() -> list[dict]:
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        return [
            edge
            for edge in writer.store.iter_edges()
            if str(edge.get("edge_type", "")) in CANDIDATE_EDGE_TYPES
        ]
    finally:
        writer.close()


def test_rehearsal_json_exists_and_is_schema_valid() -> None:
    payload = _rehearsal()

    assert payload["phase"] == "1573ai"
    assert payload["lmdb_path"] == "out/genesis_base_graph_v0.4_unified.lmdb"
    assert payload["lmdb_mutated"] is False
    assert payload["apply_recommendation"] in {
        "ready_for_1573aj",
        "defer_for_manual_review",
    }
    assert set(payload["source_edge_counts"]) == CANDIDATE_EDGE_TYPES
    assert isinstance(payload["replacement_plan"], list)


def test_source_edge_counts_match_live_lmdb_read_counts() -> None:
    payload = _rehearsal()
    live_counts = Counter(str(edge.get("edge_type", "")) for edge in _live_candidate_rows())

    assert payload["source_edge_counts"] == {
        edge_type: live_counts.get(edge_type, 0)
        for edge_type in payload["candidate_edge_types"]
    }
    assert payload["total_candidate_rows"] == sum(live_counts.values())


def test_every_candidate_row_is_covered_exactly_once() -> None:
    payload = _rehearsal()
    live_edge_ids = sorted(str(edge.get("edge_id", "")) for edge in _live_candidate_rows())
    plan_edge_ids = sorted(row["original_edge_id"] for row in payload["replacement_plan"])

    assert payload["all_rows_covered"] is True
    assert plan_edge_ids == live_edge_ids
    assert len(plan_edge_ids) == len(set(plan_edge_ids))


def test_no_keep_class_edge_type_appears_in_migration_plan() -> None:
    payload = _rehearsal()

    original_types = {row["original_edge_type"] for row in payload["replacement_plan"]}
    replacement_types = {
        replacement["edge_type"]
        for row in payload["replacement_plan"]
        for replacement in row["proposed_replacement_edges"]
    }
    assert original_types <= CANDIDATE_EDGE_TYPES
    assert not (original_types & KEEP_CLASS_EDGE_TYPES)
    assert not (replacement_types & KEEP_CLASS_EDGE_TYPES)


def test_rehearsal_records_no_lmdb_mutation_and_manual_deferral() -> None:
    payload = _rehearsal()

    assert payload["lmdb_mutated"] is False
    assert payload["classification_counts"]["needs_manual_source_read"] == payload[
        "total_candidate_rows"
    ]
    assert payload["apply_recommendation"] == "defer_for_manual_review"


def test_phase_1574_depends_on_1573ai_rehearsal_gate() -> None:
    prompt = PHASE_1574_PROMPT.read_text(encoding="utf-8")

    assert "atlas_edge_retirement_rehearsal_complete_phase_1573ai" in prompt
    assert "atlas_edge_retirement_apply_deferred_with_receipt_phase_1573ai" in prompt
    assert "atlas_edge_retirement_migration_applied_phase_1573aj" in prompt
