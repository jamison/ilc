"""Phase 1149 — Atlas Tier-2 curated seed patch."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"

NEW_ADR_IDS = {
    "adr:0019_graph_native_governance_compilation_boundary",
    "adr:0026_protocol_vs_harness_product_boundary",
    "adr:0028_settlement_substrate_graduation_governance_route",
    "adr:0031_subgraph_homomorphism_query_contract",
}


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> object:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_t1_v02_curated_seed_exists_and_parses() -> None:
    seed = _json("docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.2.json")
    assert isinstance(seed, dict)
    assert seed["format_version"] == "genesis_core_star_map_curated_seed.v0.2_candidate"
    assert seed["metadata"]["status"] == "v0.2_candidate_unsigned"


def test_t2_v02_candidate_star_map_has_36_nodes() -> None:
    star_map = _json("out/genesis_core_star_map_v0.2_candidate.json")
    assert isinstance(star_map, dict)
    assert len(star_map["nodes"]) == 36
    assert len(star_map["edges"]) == 63


def test_t3_all_four_accepted_adr_nodes_present() -> None:
    star_map = _json("out/genesis_core_star_map_v0.2_candidate.json")
    node_ids = {node["candidate_id"] for node in star_map["nodes"]}
    assert NEW_ADR_IDS <= node_ids


def test_t4_new_adr_nodes_are_pending_candidate_signing() -> None:
    star_map = _json("out/genesis_core_star_map_v0.2_candidate.json")
    nodes = {node["candidate_id"]: node for node in star_map["nodes"]}
    for candidate_id in NEW_ADR_IDS:
        node = nodes[candidate_id]
        assert node["genesis_attested"] is True
        assert node["genesis_attested_by"] == "genesis_agent:01"
        assert node["signature_status"] == "pending_signing"
        assert node["star_map_version"] == "v0.2_candidate"


def test_t5_signed_v01_star_map_and_root_envelope_unchanged() -> None:
    star_map = _json("out/genesis_core_star_map_v0.1.json")
    root_envelope = _json("out/genesis_signing_root_envelope_v0.1.json")
    assert len(star_map["nodes"]) == 32
    assert len(star_map["edges"]) == 55
    assert root_envelope["envelope_hash"] == ROOT_HASH


def test_t6_crawler_accepts_versioned_curated_seed_flag() -> None:
    help_text = __import__("subprocess").run(
        ["python3", "tools/crawl_genesis_node_candidates.py", "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "--curated-seed" in help_text


def test_t7_walkthrough_records_phase_token() -> None:
    text = _read("docs/phases/phase_1149_atlas_tier2_curated_seed_patch_walkthrough.md")
    assert "atlas_tier2_curated_seed_patch_committed_phase_1149" in text
    assert "v0.2 candidate" in text
