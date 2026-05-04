"""Phase 1151 — Genesis 32-node composability audit."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
ALLOWED_CLASSES = {
    "primitive",
    "historical_artifact",
    "parameterized_policy",
    "claim_composite",
    "runtime_binding_pending",
}


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> object:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_a1_audit_file_exists_and_parses() -> None:
    audit = _json("out/genesis_32_node_composability_audit_v0.1.json")
    assert isinstance(audit, dict)
    assert audit["artifact"] == "genesis_32_node_composability_audit_v0.1"
    assert audit["phase"] == 1151


def test_a2_audit_covers_all_32_signed_genesis_nodes() -> None:
    audit = _json("out/genesis_32_node_composability_audit_v0.1.json")
    star_map = _json("out/genesis_core_star_map_v0.1.json")
    audit_ids = {entry["node_id"] for entry in audit["entries"]}
    star_ids = {node["candidate_id"] for node in star_map["nodes"]}
    assert audit["node_count"] == 32
    assert audit_ids == star_ids


def test_a3_projection_classes_are_from_allowed_set() -> None:
    audit = _json("out/genesis_32_node_composability_audit_v0.1.json")
    for entry in audit["entries"]:
        assert entry["projection_class"] in ALLOWED_CLASSES


def test_a4_every_entry_has_rationale_and_authority_source() -> None:
    audit = _json("out/genesis_32_node_composability_audit_v0.1.json")
    for entry in audit["entries"]:
        assert entry["rationale"]
        assert entry["authority_source_ref"] == entry["node_id"]
        assert entry["source_star_map_version"] == "v0.1"


def test_a5_summary_doc_contains_gate_token() -> None:
    text = _read("docs/sims/sim_spectral_04/composability_audit_1151_v0.1.md")
    assert "genesis_32_node_composability_audit_committed_phase_1151" in text
    assert "Class Counts" in text


def test_a6_all_five_projection_classes_are_used() -> None:
    audit = _json("out/genesis_32_node_composability_audit_v0.1.json")
    assert set(audit["class_counts"]) == ALLOWED_CLASSES
