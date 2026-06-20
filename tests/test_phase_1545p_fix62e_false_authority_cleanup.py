from __future__ import annotations

import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


REPORT_PATH = Path("out/genesis_atlas_fix62e_false_authority_cleanup_v0.1.json")
LEDGER_PATH = Path("docs/specs/ilc_fix62e_false_authority_cleanup_ledger_v0.1.json")
QUEUE_PATH = Path("docs/specs/ilc_fix62e_manual_graph_finish_queue_v0.1.json")
REPORT_MD_PATH = Path("docs/specs/ilc_fix62e_false_authority_cleanup_report_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_1545p_fix62e_false_authority_cleanup_walkthrough.md")
EVALUATOR_PATH = Path("tools/evaluators/sim_genesis_atlas_fix62e_false_authority_cleanup.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
LMDB_ROOT = Path("out/genesis_base_graph_v0.4_unified.lmdb")
ROOT = "artifact:genesis_intent_attestation_init_authority_map"
SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"
PROPOSED = {
    "adr:0015_node_transfer_economics",
    "adr:0018_sequestered_financial_shard",
    "adr:0024_agent_skills_infrastructure",
}


def _load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_fix62e_outputs_exist_and_are_valid_json() -> None:
    assert REPORT_PATH.exists()
    assert LEDGER_PATH.exists()
    assert QUEUE_PATH.exists()
    report = _load_json(REPORT_PATH)
    ledger = _load_json(LEDGER_PATH)
    queue = _load_json(QUEUE_PATH)
    assert report["phase"] == "1545p-Fix62e"
    assert report["status"] == "PASS"
    assert ledger["phase"] == "1545p-Fix62e"
    assert queue["phase"] == "1545p-Fix62e"
    assert queue["entry_count"] == len(queue["entries"])


def test_fix62e_removes_proposed_adr_root_governs_edges() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
        edges = {
            (edge["source"], edge["edge_type"], edge["target"])
            for edge in store.iter_edges()
        }
    finally:
        store.close()
    for node_id in PROPOSED:
        assert (ROOT, "GOVERNS", node_id) not in edges
        assert (node_id, "CLASSIFIED_BY", SUPPORT_POLICY) in edges
        assert nodes[node_id]["canonicality_tier"] == "proposed_adr_not_authority"
        assert nodes[node_id]["graph_projection"] == "support_candidate_graph"


def test_fix62e_receipts_record_expected_cleanup() -> None:
    report = _load_json(REPORT_PATH)
    ledger = _load_json(LEDGER_PATH)
    assert report["edge_removal_receipt"]["removed_edge_count"] == 3
    assert report["node_update_receipt"]["accepted_update_count"] == 3
    assert report["support_classification_semantics_present_count"] == 3
    assert len(ledger["edge_removal_targets"]) == 3


def test_fix62e_uses_safe_writer_not_raw_adapter_mutation() -> None:
    source = EVALUATOR_PATH.read_text(encoding="utf-8")
    assert "AtlasLmdbSafeWriter" in source
    assert "remove_edges_by_semantic(" in source
    assert "update_node_fields(" in source
    assert "apply_plan(" in source
    assert "write_preimages(" in source
    assert ".put_nodes(" not in source
    assert ".put_edges(" not in source
    assert ".replace_edges(" not in source


def test_fix62e_docs_preserve_non_activation_boundary() -> None:
    combined = "\n".join(
        [
            REPORT_MD_PATH.read_text(encoding="utf-8"),
            WALKTHROUGH_PATH.read_text(encoding="utf-8"),
        ]
    )
    assert "No Genesis signing occurred." in combined
    assert "No public RC activation occurred." in combined
    assert "No ECU minting, settlement, or entitlement was authorized." in combined
    assert "No ADR text was mutated." in combined


def test_fix62e_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix62e_false_authority_cleanup_complete" in text
    assert "fix62e_proposed_adr_root_edges_removed" in text
    assert "fix62e_complete" in text
