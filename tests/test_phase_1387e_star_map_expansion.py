"""Phase 1387e — Star map v0.1 expansion: 32 → 54 nodes.

Tests verify:
- Star map v0.1 now contains 54 nodes
- All 17 promoted v0.2_candidate nodes are present
- All 5 new governance spine ADRs (0001/0002/0003/0005/0006) are present
- Compiler diagnostic reflects 54/54 basis-reachable
- Verdict is still GENESIS_CORE_COMPLETE_SOURCE_COVERAGE_PARTIAL
- All promoted nodes have star_map_version='v0.1'
- New ADR nodes have promotion_path='governance_spine_expansion_phase_1387e'
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
STAR_MAP = ROOT / "out" / "genesis_core_star_map_v0.1.json"
DIAGNOSTIC_JSON = ROOT / "out" / "genesis_compile_coverage_diagnostic_v0.1.json"

# The 17 promoted nodes from v0.2_candidate
PROMOTED_V2_NODES = {
    "adr:0008_node_usefulness_governance_weight_genesis_dilution",
    "adr:0012_ecu_ilc_graph_coupling_anti_reflexivity",
    "adr:0019_graph_native_governance_compilation_boundary",
    "adr:0020_knowledge_node_first_design_principle",
    "adr:0022_local_first_private_publication_bound_economics",
    "adr:0023_multi_layer_quality_signal_architecture",
    "adr:0026_protocol_vs_harness_product_boundary",
    "adr:0028_settlement_substrate_graduation_governance_route",
    "adr:0031_subgraph_homomorphism_query_contract",
    "adr:0037_genesis_canonical_lineage_contract",
    "cdl:085_werner_phi_bound",
    "cdl:v1_temporal_decay",
    "cdl:v2_sybil_resistance",
    "cdl:v3_quorum_diversity",
    "cdl:v7_agent_decomposition",
    "policy:edge_mint_phi_bound_0_60",
    "policy:reuse_attribution_rate_0_20",
}

# New governance spine ADRs added in this phase
NEW_GOVERNANCE_SPINE_NODES = {
    "adr:0001_canonical_encoding_node_id_agent_interface",
    "adr:0002_ndjson_bundle_transport",
    "adr:0003_star_map_ngram_route_index",
    "adr:0005_star_map_observational_feeds",
    "adr:0006_eve_canonical_capsule_integrity",
}


def _star_map() -> dict:
    return json.loads(STAR_MAP.read_text())


def _diagnostic() -> dict:
    return json.loads(DIAGNOSTIC_JSON.read_text())


def test_star_map_total_nodes_54() -> None:
    data = _star_map()
    assert len(data["nodes"]) == 54, f"Expected 54 nodes; got {len(data['nodes'])}"


def test_all_promoted_v2_nodes_present() -> None:
    data = _star_map()
    ids = {n["candidate_id"] for n in data["nodes"]}
    missing = PROMOTED_V2_NODES - ids
    assert missing == set(), f"Promoted v0.2 nodes missing from v0.1: {missing}"


def test_all_new_governance_spine_nodes_present() -> None:
    data = _star_map()
    ids = {n["candidate_id"] for n in data["nodes"]}
    missing = NEW_GOVERNANCE_SPINE_NODES - ids
    assert missing == set(), f"New governance spine nodes missing: {missing}"


def test_promoted_nodes_have_v01_star_map_version() -> None:
    data = _star_map()
    nodes_by_id = {n["candidate_id"]: n for n in data["nodes"]}
    wrong = [
        cid for cid in PROMOTED_V2_NODES | NEW_GOVERNANCE_SPINE_NODES
        if nodes_by_id.get(cid, {}).get("star_map_version") != "v0.1"
    ]
    assert wrong == [], f"Nodes with wrong star_map_version: {wrong}"


def test_new_governance_spine_nodes_have_correct_promotion_path() -> None:
    data = _star_map()
    nodes_by_id = {n["candidate_id"]: n for n in data["nodes"]}
    wrong = [
        cid for cid in NEW_GOVERNANCE_SPINE_NODES
        if nodes_by_id.get(cid, {}).get("promotion_path") != "governance_spine_expansion_phase_1387e"
    ]
    assert wrong == [], f"Nodes with wrong promotion_path: {wrong}"


def test_all_54_nodes_are_core_star_map_candidates() -> None:
    data = _star_map()
    non_core = [n["candidate_id"] for n in data["nodes"] if not n.get("core_star_map_candidate")]
    assert non_core == [], f"Non-core candidates found: {non_core}"


def test_star_map_has_governs_edges_to_promoted_nodes() -> None:
    """GOVERNS edges from attestation root to all 17 promoted + 5 new nodes."""
    data = _star_map()
    attestation_root = "artifact:genesis_intent_attestation_init_authority_map"
    governs_targets = {
        e["target"] for e in data["edges"]
        if e["edge_type"] == "GOVERNS" and e["source"] == attestation_root
    }
    expected = PROMOTED_V2_NODES | NEW_GOVERNANCE_SPINE_NODES
    missing_edges = expected - governs_targets
    assert missing_edges == set(), (
        f"Missing GOVERNS edges from attestation root to: {missing_edges}"
    )


def test_diagnostic_basis_reachable_54_of_54() -> None:
    data = _diagnostic()
    cc = data["compile_coverage"]
    assert cc["core_nodes_total"] == 54, f"Expected 54 core nodes; got {cc['core_nodes_total']}"
    assert cc["basis_reachable_core_nodes"] == 54, (
        f"Expected 54/54 reachable; got {cc['basis_reachable_core_nodes']}"
    )


def test_diagnostic_verdict_genesis_core_complete() -> None:
    data = _diagnostic()
    assert data["verdict"] == "GENESIS_CORE_COMPLETE_SOURCE_COVERAGE_PARTIAL", (
        f"Unexpected verdict: {data['verdict']!r}"
    )


def test_diagnostic_basis_unreachable_empty() -> None:
    data = _diagnostic()
    unreachable = data["gaps"]["basis_unreachable_core_nodes"]
    assert unreachable == [], (
        f"Expected empty unreachable list; got {[n['candidate_id'] for n in unreachable]}"
    )


def test_diagnostic_tier_analysis_genesis_derivable_54() -> None:
    data = _diagnostic()
    tier = data["tier_analysis"]
    assert tier["genesis_derivable_node_count"] == 54, (
        f"Expected 54 genesis-derivable; got {tier['genesis_derivable_node_count']}"
    )
    assert tier["basis_unreachable_count"] == 0


def test_expansion_metadata_present() -> None:
    data = _star_map()
    meta = data.get("metadata", {})
    assert meta.get("expansion_phase") == "1387e", "expansion_phase metadata not set to 1387e"
