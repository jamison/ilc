import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_phase_1339_diagnostic_has_no_missing_decomposition_recipes() -> None:
    diagnostic = _load_json("out/genesis_compile_coverage_diagnostic_v0.2_candidate.json")

    assert diagnostic["verdict"] == "PARTIAL_WITH_STRUCTURAL_GAPS"
    assert diagnostic["edge_recipe_analysis"]["missing_decomposition_recipe_count"] == 0
    assert diagnostic["authority_traceability"]["authority_traceable_core_nodes_ratio"] == "1.000000"
    assert (
        diagnostic["authority_traceability"]["authority_traceable_core_nodes"]
        == diagnostic["compile_coverage"]["core_nodes_total"]
    )


def test_phase_1339_add_before_signing_nodes_present_and_unsigned() -> None:
    star_map = _load_json("out/genesis_core_star_map_v0.2_candidate.json")
    nodes = {node["candidate_id"]: node for node in star_map["nodes"]}

    required_nodes = {
        "adr:0037_genesis_canonical_lineage_contract",
        "cdl:v1_temporal_decay",
        "cdl:v2_sybil_resistance",
        "cdl:v3_quorum_diversity",
        "cdl:v7_agent_decomposition",
        "cdl:085_werner_phi_bound",
        "policy:reuse_attribution_rate_0_20",
        "policy:edge_mint_phi_bound_0_60",
    }

    assert required_nodes <= set(nodes)
    for candidate_id in required_nodes:
        assert nodes[candidate_id]["signature_status"] == "pending_signing"
        assert nodes[candidate_id]["star_map_version"] == "v0.2_candidate"

    assert nodes["policy:reuse_attribution_rate_0_20"]["symbol"] == "REUSE_ATTRIBUTION_RATE"
    assert nodes["policy:reuse_attribution_rate_0_20"]["value"]["literal"] == "0.20"
    assert nodes["policy:edge_mint_phi_bound_0_60"]["symbol"] == "EDGE_MINT_PHI_BOUND"
    assert nodes["policy:edge_mint_phi_bound_0_60"]["value"]["literal"] == "0.60"


def test_phase_1339_finalization_report_records_non_authorization_boundary() -> None:
    report = (ROOT / "docs/specs/ilc_atlas_g_tail_finalization_1339_v0.1.md").read_text(
        encoding="utf-8"
    )

    assert "atlas_g_mutation_regeneration_finalization_phase_1339.v0.1" in report
    assert "atlas_g_007_candidate_regeneration_classified_phase_1339" in report
    assert "atlas_g_008_non_excisability_packet_classified_phase_1339" in report
    assert "phase_1340_v0_2_signing_ceremony_gate_next" in report
    assert "public_rc_remains_blocked_after_phase_1339" in report
    assert "no_genesis_v0_2_signing" in _load_json(
        "docs/specs/ilc_atlas_g_tail_finalization_1339_v0.1.json"
    )["non_authorizations"]
