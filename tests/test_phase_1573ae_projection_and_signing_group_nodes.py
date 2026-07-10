from __future__ import annotations

from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (
    GenesisAtlasCandidateStore,
)


ROOT = Path(__file__).resolve().parents[1]
LMDB = ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
PROJECTION_SCRIPT = ROOT / "tools/add_projection_policy_node_1573ae.py"
SIGNING_SCRIPT = ROOT / "tools/add_signing_group_rules_node_1573ae.py"
CDL_098 = "cdl:CDL-098"
PROJECTION_NODE = "knowledge:projection_policy:graph_projection_naming_policy_v0.1"
SIGNING_NODE = "knowledge:signing_group_rules:atlas_slice_manifest_signing_v0.1"


def _store() -> GenesisAtlasCandidateStore:
    return GenesisAtlasCandidateStore(LMDB, allow_synthetic_edge_keys=True)


def _node(candidate_id: str) -> dict[str, object]:
    store = _store()
    try:
        node = store.get_node(candidate_id)
    finally:
        store.close()
    assert node is not None
    return node


def _edges() -> list[dict[str, object]]:
    store = _store()
    try:
        return store.iter_edges()
    finally:
        store.close()


def test_projection_policy_node_present_with_canonical_fields() -> None:
    node = _node(PROJECTION_NODE)
    assert node["node_kind"] == "knowledge_node"
    assert node["node_type"] == "ProjectionPolicyNode"
    assert node["policy_id"] == "graph_projection_naming_policy_v0.1"
    assert node["authority"] == CDL_098
    assert node["graph_projection"] == "genesis_core_star_map"
    assert node["top_level_buckets"] == [
        "genesis_core_star_map",
        "public_protocol_graph",
        "support_candidate_graph",
        "excluded_private_material",
        "review_required",
    ]
    assert node["sub_label_rule"] == "{top_bucket}/{community-label}"
    assert node["sub_label_case"] == "kebab-case"


def test_signing_group_rules_node_present_with_canonical_fields() -> None:
    node = _node(SIGNING_NODE)
    assert node["node_kind"] == "knowledge_node"
    assert node["node_type"] == "SigningGroupRulesNode"
    assert node["authority"] == CDL_098
    assert node["graph_projection"] == "public_protocol_graph"
    assert node["authorized_projections"] == [
        "genesis_core_star_map",
        "public_protocol_graph",
        "support_candidate_graph",
    ]
    assert node["forbidden_public_projections"] == [
        "excluded_private_material",
        "review_required",
    ]
    assert node["key_type"] == "ml_dsa_65"
    assert node["expiry_condition"] == "superseded_by_later_cdl_or_signing_group_rules_node"
    quorum_spec = node["quorum_spec"]
    assert isinstance(quorum_spec, dict)
    assert quorum_spec["authority_basis"] == "CDL-098 Section 2g"
    assert quorum_spec["human_go_required"] is True
    assert quorum_spec["no_self_authorization"] is True


def test_cdl_098_governs_both_knowledge_nodes() -> None:
    semantics = {
        (edge.get("source"), edge.get("edge_type"), edge.get("target"))
        for edge in _edges()
    }
    assert (CDL_098, "GOVERNS", PROJECTION_NODE) in semantics
    assert (CDL_098, "GOVERNS", SIGNING_NODE) in semantics


def test_nodes_are_not_adr0035_type_definition_nodes() -> None:
    for candidate_id in (PROJECTION_NODE, SIGNING_NODE):
        node = _node(candidate_id)
        assert node["node_kind"] == "knowledge_node"
        assert node["node_type"] not in {
            "TypeDefinitionNode",
            "DefinitionNode",
            "ADR0035TypeDefinitionNode",
        }
        assert "definition_node_type" not in node
        assert "cdl_099_definition_node_instance" not in node


def test_lmdb_write_scripts_are_durable_repo_artifacts() -> None:
    assert PROJECTION_SCRIPT.exists()
    assert SIGNING_SCRIPT.exists()
    assert "/tmp/" not in PROJECTION_SCRIPT.as_posix()
    assert "/tmp/" not in SIGNING_SCRIPT.as_posix()
    projection_text = PROJECTION_SCRIPT.read_text(encoding="utf-8")
    signing_text = SIGNING_SCRIPT.read_text(encoding="utf-8")
    assert "handle_atlas_apply_node_edge_plan" in projection_text
    assert "handle_atlas_apply_node_edge_plan" in signing_text
    assert "PUBLIC_RC_EXCLUDE" in projection_text
    assert "PUBLIC_RC_EXCLUDE" in signing_text
