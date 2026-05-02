"""Phase 1136A Genesis morphogenic hypergraph atlas evidence tests."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
CRAWL = ROOT / "out/genesis_node_candidate_crawl.json"
STAR_MAP = ROOT / "out/genesis_core_star_map_v0.1.json"
CURATED_SEED = ROOT / "docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json"


def _json(path: pathlib.Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_a01_star_map_contains_adr_0004_authority_node() -> None:
    star_map = _json(STAR_MAP)
    node_ids = {node["candidate_id"] for node in star_map["nodes"]}
    assert "adr:0004_genesis_truth_primitives" in node_ids


def test_a02_star_map_contains_seven_adr_0004_provenance_edges() -> None:
    star_map = _json(STAR_MAP)
    edges = [
        edge
        for edge in star_map["edges"]
        if edge["source"] == "adr:0004_genesis_truth_primitives"
        and edge["edge_type"] == "PROVENANCE"
        and edge["target"].startswith("truth_primitive:")
    ]
    assert len(edges) >= 7


def test_a03_all_proposed_crawl_edges_have_decomposition_recipe() -> None:
    crawl = _json(CRAWL)
    proposed_edges = [
        edge
        for edge in crawl["edges"]
        if edge.get("feature_hints", {}).get("proposed_edge_type") is True
    ]
    assert proposed_edges
    assert all("decomposition_recipe" in edge for edge in proposed_edges)


def test_a04_star_map_metadata_contains_projection_fields() -> None:
    star_map = _json(STAR_MAP)
    metadata = star_map["metadata"]
    assert metadata["derived_from"] == "out/genesis_observed_repo_hypergraph_v0.1.json"
    assert metadata["projection_rule"] == "high_authority_core_bootstrap_projection"
    assert metadata["observer_scope"] == "install_load_genesis_agent_view"
    assert "transition_basis" in metadata


def test_a05_transition_basis_has_exactly_seven_truth_primitives() -> None:
    star_map = _json(STAR_MAP)
    assert star_map["metadata"]["transition_basis"] == [
        "truth_primitive:assert.truth",
        "truth_primitive:validate.claim",
        "truth_primitive:contradict.assert",
        "truth_primitive:refute.claim",
        "truth_primitive:revise.assert",
        "truth_primitive:link.claim",
        "truth_primitive:commit.epoch",
    ]


def test_a06_epoch_boundary_commit_epoch_is_marked_irreducible() -> None:
    star_map = _json(STAR_MAP)
    basis = star_map["metadata"]["type_decomposition_basis"]
    epoch_boundary = basis["EPOCH_BOUNDARY"]
    assert epoch_boundary["irreducible"] is True
    assert epoch_boundary["primitives"] == ["commit.epoch"]


def test_a07_adr_0035_is_core_projection_with_draft_tier() -> None:
    crawl = _json(CRAWL)
    nodes = {node["candidate_id"]: node for node in crawl["nodes"]}
    node = nodes["adr:0035_homoiconic_type_definition_system"]
    assert node["core_star_map_candidate"] is True
    assert node["canonicality_tier"] == "draft_direction_accepted"


def test_a08_generated_outputs_record_and_apply_curated_seed() -> None:
    seed = _json(CURATED_SEED)
    crawl = _json(CRAWL)
    star_map = _json(STAR_MAP)

    assert crawl["metadata"]["curated_seed"] == "docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json"
    assert crawl["metadata"]["curated_seed_format_version"] == seed["format_version"]

    seed_node_ids = {node["candidate_id"] for node in seed["nodes"]}
    star_map_node_ids = {node["candidate_id"] for node in star_map["nodes"]}
    assert seed_node_ids.issubset(star_map_node_ids)

    seed_edge_ids = {edge["edge_id"] for edge in seed["edges"]}
    star_map_edge_ids = {edge["edge_id"] for edge in star_map["edges"]}
    assert seed_edge_ids.issubset(star_map_edge_ids)
