"""Genesis node candidate crawl artifact tests."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
CRAWL_JSON = ROOT / "out/genesis_node_candidate_crawl.json"
RAW_LEDGER = ROOT / "out/genesis_node_candidate_raw_match_ledger.ndjson"
REJECTED_LEDGER = ROOT / "out/genesis_node_candidate_rejected_sources.ndjson"
INVENTORY = ROOT / "docs/sims/sim_spectral_02/genesis_node_candidate_inventory_v0.1.md"
DECISION_LOG = ROOT / "docs/sims/sim_spectral_02/genesis_node_candidate_decision_log_v0.1.md"


def _payload() -> dict[str, object]:
    data = json.loads(CRAWL_JSON.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_genesis_node_candidate_crawl_outputs_exist() -> None:
    assert CRAWL_JSON.exists()
    assert RAW_LEDGER.exists()
    assert REJECTED_LEDGER.exists()
    assert INVENTORY.exists()
    assert DECISION_LOG.exists()


def test_genesis_node_candidate_crawl_has_required_top_level_sections() -> None:
    payload = _payload()
    assert {
        "decision_log",
        "dredge_summary",
        "edges",
        "metadata",
        "nodes",
        "promotion_trace",
        "raw_match_ledger_sample",
        "rejected_candidate_sources_sample",
        "review_required_sources",
    }.issubset(payload)


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
        assert node["core_star_map_candidate"] is True
    for axiom in ("axiom:math:01", "axiom:physics:01", "axiom:logic:01"):
        assert nodes[axiom]["canonicality_tier"] == "binding_config"
        assert nodes[axiom]["economic_boundary"] == "genesis_attested_provenance_flow"
        assert nodes[axiom]["core_star_map_candidate"] is True


def test_genesis_node_candidate_crawl_promotes_required_genesis_star_map_nodes() -> None:
    payload = _payload()
    nodes = {node["candidate_id"]: node for node in payload["nodes"]}
    for candidate_id in (
        "artifact:genesis_agent1_pubkey_record_838a",
        "ceremony:genesis_agent1_keygen_838a",
        "policy:genesis_accrual_governor",
        "policy:provenance_decay_alpha_0_45",
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
    assert nodes["policy:provenance_decay_alpha_0_45"]["canonicality_tier"] == "ratified_cdl"
    assert "overlay:morphogenetic_hypergraph_substrate" not in nodes


def test_genesis_node_candidate_crawl_records_edge_features_for_sim_use() -> None:
    payload = _payload()
    edges = payload["edges"]
    assert isinstance(edges, list)
    assert edges
    assert any(edge["feature_hints"].get("sim_weight_seed") is not None for edge in edges)
    proposed_edges = [
        edge
        for edge in edges
        if edge["edge_type"] in {"PRIMITIVE_INVOCATION", "GOVERNS", "CONSTRAINS"}
    ]
    assert proposed_edges
    assert all(edge["feature_hints"]["proposed_edge_type"] is True for edge in proposed_edges)
    assert all(edge["feature_hints"]["edge_type_status"] == "atlas_proposal_pending_ADR" for edge in proposed_edges)
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
    assert any(
        edge["source"] == "genesis_agent:01"
        and edge["target"] == "policy:genesis_freshness_exemption"
        and edge["edge_type"] == "CONSTRAINS"
        for edge in edges
    )
    assert not any(edge["edge_id"] == "edge:genesis_exemption_to_genesis_agent" for edge in edges)


def test_genesis_node_candidate_crawl_keeps_review_required_sources() -> None:
    payload = _payload()
    review_sources = payload["review_required_sources"]
    assert isinstance(review_sources, list)
    assert review_sources
    assert {item["candidate_action"] for item in review_sources} == {"review_required"}
    assert {item["graph_projection"] for item in review_sources} == {"support_candidate_graph"}
    assert all("promotion_path" in item for item in review_sources)


def test_genesis_node_candidate_crawl_keeps_rejected_candidate_ledger() -> None:
    payload = _payload()
    raw_count = sum(1 for _ in RAW_LEDGER.open(encoding="utf-8"))
    rejected_count = sum(1 for _ in REJECTED_LEDGER.open(encoding="utf-8"))
    assert raw_count >= rejected_count > 0
    sample = [json.loads(line) for line in REJECTED_LEDGER.read_text(encoding="utf-8").splitlines()[:5]]
    assert all(item["candidate_action"] == "rejected_candidate_source" for item in sample)
    assert all(item["exclusion_reason"] for item in sample)
    assert payload["dredge_summary"]["raw_match_count"] == raw_count
    assert payload["dredge_summary"]["rejected_candidate_source_count"] == rejected_count
    assert "rejections_by_reason" in payload["dredge_summary"]
    assert payload["audit_artifacts"]["raw_match_ledger_ndjson"].endswith("genesis_node_candidate_raw_match_ledger.ndjson")


def test_genesis_node_candidate_crawl_records_promotion_trace() -> None:
    payload = _payload()
    nodes = {node["candidate_id"] for node in payload["nodes"]}
    trace = {item["candidate_id"]: item for item in payload["promotion_trace"]}
    assert nodes == set(trace)
    assert trace["truth_primitive:assert.truth"]["core_star_map_candidate"] is True
    assert trace["policy:genesis_freshness_exemption"]["core_star_map_candidate"] == "review"


def test_genesis_node_candidate_decision_log_records_review_queue_rule() -> None:
    payload = _payload()
    assert all(item["id"] == item["decision_id"] for item in payload["decision_log"])
    text = DECISION_LOG.read_text(encoding="utf-8")
    assert "GND-0021" in text
    assert "GND-0026" in text
    assert "GND-0029" in text
    assert "GND-0030" in text
    assert "review queue" in text
