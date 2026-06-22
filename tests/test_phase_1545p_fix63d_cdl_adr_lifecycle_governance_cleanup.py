from __future__ import annotations

import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_lmdb_writer import AtlasLmdbSafeWriter


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "docs/specs/ilc_fix63d_cdl_adr_no_outbound_governs_queue_v0.1.json"
LEDGER = ROOT / "docs/specs/ilc_fix63d_cdl_adr_lifecycle_governance_cleanup_ledger_v0.1.json"
REPORT = ROOT / "docs/specs/ilc_fix63d_cdl_adr_lifecycle_governance_cleanup_report_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix63d_cdl_adr_lifecycle_governance_cleanup_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
EVALUATOR = ROOT / "tools/evaluators/sim_genesis_atlas_fix63d_cdl_adr_lifecycle_governance_cleanup.py"
LMDB = ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix63d_outputs_exist_and_use_live_queue() -> None:
    queue = _json(QUEUE)
    ledger = _json(LEDGER)

    assert queue["phase"] == "1545p-Fix63d"
    assert queue["queue_count"] == ledger["pre_execution_queue_count"]
    assert queue["queue_count"] >= 100
    assert set(queue["queue_counts"]) == {"adr", "cdl"}
    assert len(ledger["entries"]) == queue["queue_count"]


def test_fix63d_direct_reads_do_not_use_status_proxy() -> None:
    ledger = _json(LEDGER)

    for entry in ledger["entries"]:
        direct_read = entry["direct_read"]
        if direct_read["source_status"] != "escalated_no_source":
            assert direct_read["path"]
            assert direct_read["path"] != "docs/phases/STATUS.md"
            assert direct_read["line_refs"]


def test_fix63d_edges_are_procedural_and_not_false_governs() -> None:
    ledger = _json(LEDGER)
    allowed = {
        "SAME_AUTHORITY",
        "OPENED_FOR",
        "PRELOCK_FOR",
        "RATIFICATION_EVIDENCE_FOR",
        "PROPOSES_CHANGE_TO",
        "RESOLVED_BY",
        "DERIVED_FROM",
        "CLASSIFIED_BY",
        "GOVERNS",
    }
    lifecycle_dispositions = {
        "shadow_duplicate_same_authority",
        "lifecycle_opening_record",
        "lifecycle_prelock_record",
        "lifecycle_ratification_record",
        "adr_decision_or_lifecycle_record",
        "adr_proposal_record",
        "proposed_adr_record_no_governs",
        "open_cdl_support_record",
        "candidate_review_overlay",
    }
    edge_count = 0
    for entry in ledger["entries"]:
        for edge in entry.get("recommended_edges", []):
            edge_count += 1
            assert edge["edge_type"] in allowed
            assert edge["source"] == entry["candidate_id"]
            assert edge["evidence"].startswith(f"{entry['direct_read']['path']}:")
            if entry["disposition"] in lifecycle_dispositions:
                assert edge["edge_type"] != "GOVERNS"
    assert edge_count == ledger["recommended_edge_count"]


def test_fix63d_no_raw_lmdb_writes_in_evaluator() -> None:
    text = EVALUATOR.read_text(encoding="utf-8")
    forbidden = (".store.put_nodes(", ".store.put_edges(", ".store.put_meta(", ".store.put_graph_payload(", ".store.replace_edges(")
    assert not any(token in text for token in forbidden)
    assert "AtlasLmdbSafeWriter" in text


def test_fix63d_status_tokens_and_nonclaims() -> None:
    status = STATUS.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")

    for token in (
        "fix63d_cdl_adr_lifecycle_governance_cleanup_complete",
        "fix63d_no_blanket_governs_expansion",
        "fix63d_complete",
    ):
        assert token in status
    for phrase in (
        "does not authorize public RC",
        "ECU minting",
        "ILC settlement",
        "Genesis signing",
    ):
        assert phrase in walkthrough or phrase in report


def test_fix63d_lmdb_is_clean_after_writes() -> None:
    writer = AtlasLmdbSafeWriter(LMDB)
    try:
        info = writer.inspect()
    finally:
        writer.close()

    assert info["dangling_edge_count"] == 0
    assert info["edge_id_debt_count"] == 0
    assert info["graph_payload_node_count"] == info["node_count"]
    assert info["graph_payload_edge_count"] == info["edge_count"]
    assert all(info["invariants"].values())
