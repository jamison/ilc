"""Genesis node candidate crawl artifact tests."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
CRAWL_JSON = ROOT / "out/genesis_node_candidate_crawl.json"
INVENTORY = ROOT / "docs/sims/sim_spectral_02/genesis_node_candidate_inventory_v0.1.md"
DECISION_LOG = ROOT / "docs/sims/sim_spectral_02/genesis_node_candidate_decision_log_v0.1.md"


def _payload() -> dict[str, object]:
    data = json.loads(CRAWL_JSON.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_genesis_node_candidate_crawl_outputs_exist() -> None:
    assert CRAWL_JSON.exists()
    assert INVENTORY.exists()
    assert DECISION_LOG.exists()


def test_genesis_node_candidate_crawl_has_required_top_level_sections() -> None:
    payload = _payload()
    assert {"decision_log", "edges", "metadata", "nodes", "review_required_sources"}.issubset(payload)


def test_genesis_node_candidate_crawl_includes_new_seven_and_axioms() -> None:
    payload = _payload()
    nodes = {node["candidate_id"]: node for node in payload["nodes"]}
    for primitive in (
        "assert.truth",
        "validate.claim",
        "contradict.assert",
        "refute.claim",
        "revise.assert",
        "link.claim",
        "commit.epoch",
    ):
        node = nodes[f"truth_primitive:{primitive}"]
        assert node["inclusion_status"] == "must_include"
        assert node["genesis_attested"] is True
        assert node["genesis_attested_by"] == "genesis_agent:01"
        assert node["economic_boundary"] == "genesis_attested_provenance_flow"
        assert node["economic_cap_policy"] == "policy:genesis_theta_hard_0_05"
        assert node["graph_projection"] == "core_star_map"
    for axiom in ("axiom:math:01", "axiom:physics:01", "axiom:logic:01"):
        assert nodes[axiom]["canonicality_tier"] == "binding_config"


def test_genesis_node_candidate_crawl_promotes_required_genesis_star_map_nodes() -> None:
    payload = _payload()
    nodes = {node["candidate_id"]: node for node in payload["nodes"]}
    for candidate_id in (
        "artifact:genesis_agent1_pubkey_record_838a",
        "ceremony:genesis_agent1_keygen_838a",
        "policy:genesis_accrual_governor",
        "policy:genesis_theta_soft_exp_minus_3",
        "policy:genesis_authority_sunset",
        "adr:0029_hypergraph_substrate",
        "adr:0030_node_embedding_substrate",
        "adr:0032_temporal_hypergraph",
        "adr:0033_star_map_homoiconic_entity",
        "cdl:081_hyperedge_ecu_attribution",
        "cdl:083_panel_quorum_refutation",
        "cdl:084_provenance_chain_attribution",
    ):
        assert nodes[candidate_id]["graph_projection"] == "core_star_map"


def test_genesis_node_candidate_crawl_records_edge_features_for_sim_use() -> None:
    payload = _payload()
    edges = payload["edges"]
    assert isinstance(edges, list)
    assert edges
    assert any(edge["edge_type"] == "EPOCH_BOUNDARY" for edge in edges)
    assert any(edge["feature_hints"].get("sim_weight_seed") is not None for edge in edges)
    primitive_attestation_edges = [
        edge
        for edge in edges
        if edge["source"] == "genesis_agent:01" and edge["target"].startswith("truth_primitive:")
    ]
    assert len(primitive_attestation_edges) == 7
    assert all(edge["edge_type"] == "ATTESTATION" for edge in primitive_attestation_edges)
    assert all(
        edge["feature_hints"]["economic_cap_policy"] == "policy:genesis_theta_hard_0_05"
        for edge in primitive_attestation_edges
    )


def test_genesis_node_candidate_crawl_uses_correct_operator_and_provenance_edge_semantics() -> None:
    payload = _payload()
    edges = payload["edges"]
    assert not any(
        edge["source"] == "truth_primitive:assert.truth" and edge["edge_type"] == "ATTESTATION"
        for edge in edges
    )
    assert {
        edge["target"]
        for edge in edges
        if edge["source"] == "truth_primitive:assert.truth" and edge["edge_type"] == "PRIMITIVE_INVOCATION"
    } == {"axiom:math:01", "axiom:physics:01", "axiom:logic:01"}
    assert any(
        edge["source"] == "truth_primitive:assert.truth"
        and edge["target"] == "artifact:genesis_authority_assertion_schema"
        and edge["edge_type"] == "PROVENANCE"
        for edge in edges
    )


def test_genesis_node_candidate_crawl_keeps_review_required_sources() -> None:
    payload = _payload()
    review_sources = payload["review_required_sources"]
    assert isinstance(review_sources, list)
    assert review_sources
    assert {item["candidate_action"] for item in review_sources} == {"review_required"}
    assert {item["graph_projection"] for item in review_sources} == {"support_candidate_graph"}
    assert all("promotion_path" in item for item in review_sources)


def test_genesis_node_candidate_decision_log_records_review_queue_rule() -> None:
    payload = _payload()
    assert all(item["id"] == item["decision_id"] for item in payload["decision_log"])
    text = DECISION_LOG.read_text(encoding="utf-8")
    assert "GND-0021" in text
    assert "GND-0026" in text
    assert "review queue" in text
