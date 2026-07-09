from __future__ import annotations

import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_lmdb_writer import AtlasLmdbSafeWriter


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
MIGRATION_JSON = (
    REPO_ROOT / "docs/specs/ilc_atlas_edge_retirement_migration_1573aj_v0.1.json"
)
PHASE_1574_PROMPT = (
    REPO_ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md"
)
STATUS = REPO_ROOT / "docs/phases/STATUS.md"
TAXONOMY = (
    REPO_ROOT
    / "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md"
)

RETIRED_EDGE_TYPES = {
    "REFERENCES",
    "IMPLEMENTS_MODULE",
    "RATIFICATION_EVIDENCE_FOR",
    "USES",
    "OPENED_FOR",
    "PRELOCK_FOR",
}


def _receipt() -> dict:
    return json.loads(MIGRATION_JSON.read_text(encoding="utf-8"))


def _live_edge_counts() -> dict[str, int]:
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        counts: dict[str, int] = {}
        for edge in writer.store.iter_edges():
            edge_type = str(edge.get("edge_type", ""))
            counts[edge_type] = counts.get(edge_type, 0) + 1
        return counts
    finally:
        writer.close()


def test_migration_receipt_schema_and_counts() -> None:
    receipt = _receipt()

    assert receipt["phase"] == "1573aj"
    assert receipt["status"] == "PASS"
    assert receipt["mutated"] is True
    assert receipt["source_candidate_edge_count"] == 80
    assert receipt["removed_edge_count"] == 80
    assert receipt["replacement_edge_row_count"] == 80
    assert receipt["replacement_unique_semantic_count"] == 79
    assert receipt["accepted_replacement_edge_count"] == 75
    assert receipt["replacement_apply_receipt"]["skipped_edge_count"] == 5
    assert receipt["already_present_replacement_semantic_count"] == 4
    assert receipt["duplicate_replacement_semantic_count"] == 1


def test_retired_labels_absent_in_receipt_and_live_lmdb() -> None:
    receipt = _receipt()
    live_counts = _live_edge_counts()

    assert receipt["final_retired_edge_counts"] == {
        edge_type: 0 for edge_type in sorted(RETIRED_EDGE_TYPES)
    }
    for edge_type in RETIRED_EDGE_TYPES:
        assert live_counts.get(edge_type, 0) == 0


def test_lmdb_invariants_pass_after_migration() -> None:
    receipt = _receipt()
    inspect = receipt["post_inspect"]

    assert inspect["node_count"] == 18589
    assert inspect["edge_count"] == 89339
    assert inspect["edge_id_debt_count"] == 0
    assert inspect["dangling_edge_count"] == 0
    assert inspect["duplicate_semantic_edge_extra_row_count"] == 0
    assert all(inspect["invariants"].values())


def test_applied_replacement_edges_are_unique_and_duplicates_accounted_for() -> None:
    receipt = _receipt()
    accepted_edges = receipt["replacement_apply_receipt"]["accepted_edges"]
    edge_ids = [edge["edge_id"] for edge in accepted_edges]

    assert len(edge_ids) == len(set(edge_ids))
    assert receipt["applied_replacement_edge_ids_unique"] is True
    assert len(receipt["already_present_replacement_semantics"]) == 4
    assert len(receipt["duplicate_replacement_semantics"]) == 1


def test_phase_1574_accepts_1573aj_apply_gate() -> None:
    prompt = PHASE_1574_PROMPT.read_text(encoding="utf-8")

    assert "atlas_edge_retirement_apply_ready_phase_1573ai" in prompt
    assert "atlas_edge_retirement_migration_applied_phase_1573aj" in prompt
    assert "halt Phase 1574 and run" in prompt


def test_status_records_all_1573aj_tokens() -> None:
    text = STATUS.read_text(encoding="utf-8")

    for token in (
        "atlas_edge_retirement_migration_applied_phase_1573aj",
        "atlas_edge_retirement_retired_labels_absent_or_exceptioned_phase_1573aj",
        "atlas_edge_retirement_lmdb_validated_phase_1573aj",
        "atlas_edge_retirement_preimages_rebuilt_phase_1573aj",
        "public_path_remains_blocked_phase_1573aj",
    ):
        assert token in text


def test_cites_edge_type_is_reserved_for_non_authoritative_citations() -> None:
    text = TAXONOMY.read_text(encoding="utf-8")

    assert "| `CITES` | Source artifact cites" in text
    assert "| `CITES` | `native_reference_keep` |" in text
    assert "Non-authoritative citation/link relation" in text
