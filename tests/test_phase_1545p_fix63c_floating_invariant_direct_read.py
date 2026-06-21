from __future__ import annotations

import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_lmdb_writer import AtlasLmdbSafeWriter


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "docs/specs/ilc_fix63c_floating_invariant_queue_v0.1.json"
LEDGER = ROOT / "docs/specs/ilc_fix63c_floating_invariant_direct_read_ledger_v0.1.json"
REPORT = ROOT / "docs/specs/ilc_fix63c_floating_invariant_direct_read_report_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix63c_floating_invariant_direct_read_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
LMDB = ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix63c_outputs_exist_and_use_live_queue() -> None:
    queue = _json(QUEUE)
    ledger = _json(LEDGER)

    assert queue["phase"] == "1545p-Fix63c"
    assert queue["floating_invariant_count"] >= 300
    assert ledger["pre_execution_floating_invariant_count"] == queue["floating_invariant_count"]
    assert len(ledger["entries"]) == queue["floating_invariant_count"]


def test_fix63c_entries_are_direct_source_reads_not_status_proxy() -> None:
    ledger = _json(LEDGER)

    for entry in ledger["entries"]:
        if entry["direct_read_status"] == "complete":
            assert entry["source_file"] != "docs/phases/STATUS.md"
            assert entry["direct_read"]["path"] == entry["source_file"]
            assert entry["direct_read"]["line_refs"]
            assert entry["recommended_edges"]
        else:
            assert entry["disposition"].startswith("escalated")


def test_fix63c_edges_are_allowed_and_have_evidence() -> None:
    ledger = _json(LEDGER)
    allowed = {"EVIDENCES", "REFERENCES_AUTHORITY", "TESTS", "IMPLEMENTS", "CLASSIFIED_BY"}
    edge_count = 0
    entries_with_evidence_link = 0
    for entry in ledger["entries"]:
        has_evidence_edge = False
        for edge in entry.get("recommended_edges", []):
            edge_count += 1
            assert edge["edge_type"] in allowed
            assert edge["source"] == entry["candidate_id"]
            assert edge["evidence"].startswith(f"{entry['source_file']}:")
            if edge["edge_type"] == "EVIDENCES":
                has_evidence_edge = True
        has_duplicate_evidence = any(
            edge["edge_type"] == "EVIDENCES"
            for edge in entry.get("duplicate_edges_observed", [])
        )
        if has_evidence_edge or has_duplicate_evidence:
            entries_with_evidence_link += 1
    assert edge_count == ledger["recommended_edge_count"]
    assert entries_with_evidence_link == ledger["pre_execution_floating_invariant_count"]


def test_fix63c_status_tokens_and_walkthrough_nonclaims() -> None:
    status = STATUS.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")

    for token in (
        "fix63c_floating_invariant_direct_read_complete",
        "fix63c_floating_invariants_enriched",
        "fix63c_complete",
    ):
        assert token in status
    for phrase in (
        "does not authorize public RC",
        "ECU minting",
        "ILC settlement",
        "Genesis signing",
    ):
        assert phrase in walkthrough or phrase in report


def test_fix63c_lmdb_is_clean_after_writes() -> None:
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
