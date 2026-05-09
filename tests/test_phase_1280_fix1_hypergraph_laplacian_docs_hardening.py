from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


PACKET = "docs/specs/ilc_phase_1280_fix1_hypergraph_laplacian_docs_hardening_v0.1.md"
WALKTHROUGH = "docs/phases/phase_1280_fix1_hypergraph_laplacian_docs_hardening_walkthrough.md"


TARGET_DOCS = (
    "docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md",
    "docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.7.md",
    "docs/research/ilc_hypergraph_implementation_lane_h_series_v0.1.md",
    "docs/research/ilc_subgraph_laplacian_research_memo_791_v0.1.md",
    "docs/specs/ilc_atlas_graph_integrated_phase_discipline_forward_planning_1241_v0.1.md",
    "docs/specs/ilc_atlas_g_1241_plus_candidate_phase_grouping_v0.1.md",
    "docs/specs/ilc_dynamic_epistemic_traversal_engine_forward_planning_1241_v0.1.md",
)


REQUIRED_TOKENS = (
    "phase_1280_fix1_hypergraph_laplacian_docs_hardened",
    "h_series_020_plus_registered_phase_1280_fix1",
    "ip_lane_001_plus_registered_phase_1280_fix1",
    "publication_ip_boundary_tracked_without_public_rc_activation_phase_1280_fix1",
    "public_rc_candidate_standard_preserved_phase_1280_fix1",
    "public_rc_remains_blocked_after_phase_1280_fix1",
)


H_TOKENS = (
    "h020_hypergraph_laplacian_tracker_refresh_registered",
    "h021_dual_hypergraph_utility_registered",
    "h022_incremental_structural_proof_chain_plan_registered",
    "h023_spectral_hash_cdl_preflight_registered",
    "h024_posk_cdl_preflight_ip_gated_registered",
    "h025_sim_reuse_01_commissioning_registered",
    "h026_edge_type_coefficient_reuse_cap_cdl_preflight_registered",
    "h027_named_subgraph_laplacian_sparse_eigensolver_plan_registered",
    "h028_star_expansion_authorization_preflight_registered",
)


IP_TOKENS = (
    "ip001_ip_inventory_disclosure_control_registered",
    "ip002_merkle_laplacian_provisional_draft_registered",
    "ip003_posk_provisional_draft_registered",
    "ip004_sealed_spectral_beacon_routing_provisional_draft_registered",
    "ip005_homoiconic_star_expansion_provisional_draft_registered",
    "ip006_publication_clearance_matrix_registered",
)


def test_phase_1280_fix1_packet_registers_required_tokens_and_lanes() -> None:
    packet = read(PACKET)
    for token in REQUIRED_TOKENS + H_TOKENS + IP_TOKENS:
        assert token in packet

    assert "H-020" in packet
    assert "H-028" in packet
    assert "IP-001" in packet
    assert "IP-006" in packet
    assert "PUBLIC_RC_EXCLUDE: internal_ip_publication_planning_not_public_rc_launch_surface" in packet


def test_all_seven_target_docs_have_phase_1280_fix1_status_addenda() -> None:
    for path in TARGET_DOCS:
        text = read(path)
        assert "Phase 1280 Fix1" in text
        assert "Addendum" in text


def test_merkle_laplacian_paper_is_public_rc_excluded_and_format_fixed() -> None:
    text = read("docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md")

    assert text.startswith("<!-- PUBLIC_RC_EXCLUDE:")
    assert "**Δ** is real symmetric" in text
    assert "**Δ*\n* is real symmetric" not in text
    assert "Historical v0.1 research draft" in text
    assert "SIM-SPECTRAL-01, SIM-BEACON-01, and SIM-ROUTING-01 have completed" in text


def test_h_series_docs_mark_stale_status_and_register_continuation() -> None:
    classification = read("docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.7.md")
    h_series = read("docs/research/ilc_hypergraph_implementation_lane_h_series_v0.1.md")

    assert "CDL-085 is ratified by Phase 1185" in classification
    assert "Historical Window 1139–1147 Status Snapshot" in classification
    assert "RATIFIED Phase 1185" in classification

    assert "H-020" in h_series
    assert "H-028" in h_series
    assert "RESOLVED by CDL-081 ratification" in h_series
    assert "RESOLVED by CDL-083 ratification" in h_series
    assert "PENDING external IP/counsel assessment" in h_series


def test_atlas_and_dte_docs_are_hardened_against_stale_routing() -> None:
    atlas_plan = read("docs/specs/ilc_atlas_graph_integrated_phase_discipline_forward_planning_1241_v0.1.md")
    atlas_grouping = read("docs/specs/ilc_atlas_g_1241_plus_candidate_phase_grouping_v0.1.md")
    dte = read("docs/specs/ilc_dynamic_epistemic_traversal_engine_forward_planning_1241_v0.1.md")

    assert "ATLAS-G-001 through ATLAS-G-003 were consumed by Phase 1247" in atlas_plan
    assert "ATLAS-G-007 through ATLAS-G-010 remain future work" in atlas_plan
    assert "CONSUMED Phase 1247" in atlas_grouping
    assert "CONSUMED Phase 1271 / Fix1" in atlas_grouping
    assert "CDL-087 is ratified by Phase 1278 Fix1" in dte
    assert "not currently scheduled" in dte


def test_planning_index_and_window_guidance_reference_fix1_without_opening_window() -> None:
    planning = read("docs/PLANNING_INDEX.md")
    guidance = read("docs/specs/ilc_window_1281_1288_candidate_phase_grouping_v0.1.md")

    for text in (planning, guidance):
        assert PACKET in text
        assert "h_series_020_plus_registered_phase_1280_fix1" in text
        assert "ip_lane_001_plus_registered_phase_1280_fix1" in text
        assert "public_rc_remains_blocked_after_phase_1280_fix1" in text

    assert "Window 1281-1288 is not open until an explicit Phase 1281 sequence lock" in planning
    assert "This document does not open Window 1281-1288" in guidance


def test_phase_1280_fix1_non_authorization_boundary_is_explicit() -> None:
    packet = read(PACKET)
    roadmap = read("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")

    forbidden_authorities = (
        "file any patent application",
        "publish, submit, or preprint any paper",
        "authorize public RC",
        "mutate any CDL row",
        "activate public fetch serving",
        "activate public claimability",
        "authorize v0.2 signing",
    )
    for authority in forbidden_authorities:
        assert authority in packet

    assert "## 27. Phase 1280 Fix1 Hypergraph/Laplacian Planning Hardening Addendum" in roadmap
    assert "public_rc_remains_blocked_after_phase_1280_fix1" in roadmap


def test_walkthrough_records_graph_delta_and_verification() -> None:
    walkthrough_path = "docs/phases/phase_1280_fix1_hypergraph_laplacian_docs_hardening_walkthrough.md"
    walkthrough = read(walkthrough_path)

    for token in REQUIRED_TOKENS:
        assert token in walkthrough
    assert "graph_delta=support_only:docs/specs/ilc_phase_1280_fix1_hypergraph_laplacian_docs_hardening_v0.1.md -> planning/frontier" in walkthrough
    assert "tests/test_phase_1280_fix1_hypergraph_laplacian_docs_hardening.py" in walkthrough
