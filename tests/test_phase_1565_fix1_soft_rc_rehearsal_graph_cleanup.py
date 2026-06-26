"""Phase 1565-Fix1 soft-RC rehearsal graph cleanup regression tests."""

from __future__ import annotations

import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (
    GenesisAtlasCandidateStore,
)


REPO = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO / "out/genesis_base_graph_v0.4_unified.lmdb"
RECEIPT = (
    REPO
    / "docs/specs/ilc_phase_1565_fix1_soft_rc_rehearsal_identity_topology_graph_cleanup_v0.1.json"
)
STATUS = REPO / "docs/phases/STATUS.md"

CRITERIA_NODE = (
    "repo:file:ee5ac82dbf4cd780:"
    "docs_specs_ilc_private_soft_rc_rehearsal_criteria_1423_v0_1_md"
)
ROADMAP_NODE = (
    "repo:file:fdf957b301cc90b6:"
    "docs_specs_ilc_launch_roadmap_three_machines_seven_agents_v1_1_md"
)
CANONICAL_TARGETS = {
    "adr:0038_agent_birth_attestation",
    "adr:0041_agent_init_and_ingestion_protocol",
    "cdl:042_agent_id_flat_namespace",
    "cdl:069_pq_identity_epoch_endorsement",
    "cdl:090_identity_bootstrap",
}


def _receipt() -> dict[str, object]:
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def _lmdb_rows() -> tuple[set[str], list[dict[str, object]]]:
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        nodes = {str(node.get("candidate_id")) for node in store.iter_nodes()}
        edges = store.iter_edges()
    finally:
        store.close()
    return nodes, edges


def test_fix1_receipt_records_successful_cleanup() -> None:
    receipt = _receipt()
    assert receipt["phase"] == "1565-Fix1"
    assert receipt["status"] == "PASS"
    assert receipt["target_node"] == CRITERIA_NODE
    assert receipt["missing_canonical_targets"] == []
    assert len(receipt["added_edges"]) == 4
    assert {
        (edge["edge_type"], edge["target"]) for edge in receipt["added_edges"]
    } == {
        ("REFERENCES_AUTHORITY", "cdl:042_agent_id_flat_namespace"),
        ("REFERENCES_AUTHORITY", "cdl:069_pq_identity_epoch_endorsement"),
        ("REFERENCES_AUTHORITY", "cdl:090_identity_bootstrap"),
        ("DERIVED_FROM", ROADMAP_NODE),
    }
    assert receipt["post_apply"]["dangling_edges"] == 0
    assert receipt["post_apply"]["edge_id_debt"] == 0


def test_fix1_live_lmdb_has_canonical_identity_authority_edges() -> None:
    nodes, edges = _lmdb_rows()
    assert CRITERIA_NODE in nodes
    assert CANONICAL_TARGETS <= nodes

    semantics = {
        (edge.get("source"), edge.get("edge_type"), edge.get("target"))
        for edge in edges
    }
    for target in CANONICAL_TARGETS:
        assert (CRITERIA_NODE, "REFERENCES_AUTHORITY", target) in semantics
    assert (CRITERIA_NODE, "DERIVED_FROM", ROADMAP_NODE) in semantics


def test_fix1_did_not_add_governs_edges() -> None:
    _, edges = _lmdb_rows()
    assert not [
        edge
        for edge in edges
        if edge.get("annotation_phase") == "1565-Fix1"
        and edge.get("edge_type") == "GOVERNS"
    ]


def test_fix1_legacy_edge_queues_are_review_only() -> None:
    receipt = _receipt()
    assert len(receipt["legacy_file_target_authority_edges"]) == 5
    assert receipt["legacy_file_target_authority_edge_note"].startswith("Filtered")
    assert receipt["legacy_missing_evidence_edges"]
    assert "No legacy LMDB edges deleted." in receipt["non_claims"]


def test_fix1_status_tokens_present() -> None:
    text = STATUS.read_text(encoding="utf-8")
    for token in (
        "phase_1565_fix1_soft_rc_rehearsal_graph_cleanup_complete",
        "soft_rc_rehearsal_identity_topology_edges_normalized_phase_1565_fix1",
        "soft_rc_rehearsal_graph_cleanup_no_governs_edges_added_phase_1565_fix1",
        "public_path_remains_blocked_phase_1565_fix1",
    ):
        assert token in text
