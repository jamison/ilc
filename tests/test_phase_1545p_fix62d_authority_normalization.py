from __future__ import annotations

import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


REPORT_PATH = Path("out/genesis_atlas_fix62d_authority_normalization_v0.1.json")
LEDGER_PATH = Path("docs/specs/ilc_fix62d_authority_normalization_ledger_v0.1.json")
QUEUE_PATH = Path("docs/specs/ilc_fix62d_manual_graph_finish_queue_v0.1.json")
REPORT_MD_PATH = Path("docs/specs/ilc_fix62d_authority_normalization_report_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_1545p_fix62d_authority_normalization_walkthrough.md")
EVALUATOR_PATH = Path("tools/evaluators/sim_genesis_atlas_fix62d_authority_normalization.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
LMDB_ROOT = Path("out/genesis_base_graph_v0.4_unified.lmdb")
ROOT = "artifact:genesis_intent_attestation_init_authority_map"


def _load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_fix62d_outputs_exist_and_are_valid_json() -> None:
    assert REPORT_PATH.exists()
    assert LEDGER_PATH.exists()
    assert QUEUE_PATH.exists()
    report = _load_json(REPORT_PATH)
    ledger = _load_json(LEDGER_PATH)
    queue = _load_json(QUEUE_PATH)
    assert report["phase"] == "1545p-Fix62d"
    assert report["status"] == "PASS"
    assert ledger["phase"] == "1545p-Fix62d"
    assert queue["phase"] == "1545p-Fix62d"
    assert queue["entry_count"] == len(queue["entries"])


def test_fix62d_normalizes_known_accepted_and_ratified_targets() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
        edges = {
            (edge["source"], edge["edge_type"], edge["target"])
            for edge in store.iter_edges()
        }
    finally:
        store.close()

    assert nodes["adr:0009_bundle_distribution"]["canonicality_tier"] == "accepted_adr"
    assert nodes["cdl:096_werner_global_tier_authority"]["canonicality_tier"] == "ratified_cdl"
    assert nodes["cdl:087_canonical_fetch_distribution_policy"]["canonicality_tier"] == "ratified_cdl"
    assert (ROOT, "GOVERNS", "adr:0009_bundle_distribution") in edges
    assert (ROOT, "GOVERNS", "cdl:096_werner_global_tier_authority") in edges
    assert (ROOT, "GOVERNS", "cdl:087_canonical_fetch_distribution_policy") in edges


def test_fix62d_does_not_promote_open_or_proposed_authority() -> None:
    ledger = _load_json(LEDGER_PATH)
    selected = {item["canonical_node_id"] for item in ledger["authority_selections"]}
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
        edges = {
            (edge["source"], edge["edge_type"], edge["target"])
            for edge in store.iter_edges()
        }
    finally:
        store.close()

    assert nodes["cdl:021"].get("canonicality_tier") != "ratified_cdl"
    assert nodes["adr:0015_node_transfer_economics"].get("canonicality_tier") != "accepted_adr"
    assert "cdl:021" not in selected
    assert "adr:0015_node_transfer_economics" not in selected
    assert (ROOT, "GOVERNS", "cdl:021") not in edges


def test_fix62d_priority1_token_edges_and_queue_shrink() -> None:
    report = _load_json(REPORT_PATH)
    ledger = _load_json(LEDGER_PATH)
    queue = _load_json(QUEUE_PATH)
    assert report["token_reference_semantics_present_count"] > 100
    assert ledger["priority1_token_edge_count"] > 100
    assert queue["entry_count"] < 4570
    assert int(queue["priority_counts"]["1"]) < 1327


def test_fix62d_uses_safe_writer_not_raw_adapter_mutation() -> None:
    source = EVALUATOR_PATH.read_text(encoding="utf-8")
    assert "AtlasLmdbSafeWriter" in source
    assert "update_node_fields(" in source
    assert "apply_plan(" in source
    assert "write_preimages(" in source
    assert "write_metadata(" in source
    assert ".put_nodes(" not in source
    assert ".put_edges(" not in source
    assert ".replace_edges(" not in source


def test_fix62d_docs_preserve_non_activation_boundary() -> None:
    combined = "\n".join(
        [
            REPORT_MD_PATH.read_text(encoding="utf-8"),
            WALKTHROUGH_PATH.read_text(encoding="utf-8"),
        ]
    )
    assert "No Genesis signing occurred." in combined
    assert "No public RC activation occurred." in combined
    assert "No ECU minting, settlement, or entitlement was authorized." in combined
    assert "No proposed/open ADR or CDL was promoted." in combined


def test_fix62d_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix62d_authority_normalization_complete" in text
    assert "fix62d_accepted_adr_ratified_cdl_targets_rooted" in text
    assert "fix62d_priority1_token_refs_applied" in text
    assert "fix62d_complete" in text
