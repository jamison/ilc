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
        assert nodes[f"truth_primitive:{primitive}"]["inclusion_status"] == "must_include"
    for axiom in ("axiom:math:01", "axiom:physics:01", "axiom:logic:01"):
        assert nodes[axiom]["canonicality_tier"] == "binding_config"


def test_genesis_node_candidate_crawl_records_edge_features_for_sim_use() -> None:
    payload = _payload()
    edges = payload["edges"]
    assert isinstance(edges, list)
    assert edges
    assert any(edge["edge_type"] == "EPOCH_BOUNDARY" for edge in edges)
    assert any(edge["feature_hints"].get("sim_weight_seed") is not None for edge in edges)


def test_genesis_node_candidate_crawl_keeps_review_required_sources() -> None:
    payload = _payload()
    review_sources = payload["review_required_sources"]
    assert isinstance(review_sources, list)
    assert review_sources
    assert {item["candidate_action"] for item in review_sources} == {"review_required"}


def test_genesis_node_candidate_decision_log_records_review_queue_rule() -> None:
    text = DECISION_LOG.read_text(encoding="utf-8")
    assert "GND-0021" in text
    assert "review queue" in text
