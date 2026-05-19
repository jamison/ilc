"""Phase 1387b — SIM-GENESIS-COMPILE-02: Genesis Node Compilation Review

Tests verify the canonical state of the genesis compile diagnostic and the
disposition recorded in phase_1387b_sim_genesis_compile_02_walkthrough.md.

These are analysis-attestation tests: they assert that the diagnostic artifacts
have the expected structure and that the phase walkthrough records the correct
disposition. They do not re-run the compiler.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent

DIAGNOSTIC_JSON = ROOT / "out" / "genesis_compile_coverage_diagnostic_v0.1.json"
CANDIDATES_JSON = ROOT / "out" / "genesis_node_candidates_v0.2_candidate.json"
WALKTHROUGH = ROOT / "docs" / "phases" / "phase_1387b_sim_genesis_compile_02_walkthrough.md"
ADR_DIR = ROOT / "docs" / "adr"

# Category A bootstrap axioms identified in this phase
BOOTSTRAP_AXIOM_NODES = {
    "artifact:genesis_intent_attestation_init_authority_map",
    "artifact:genesis_agent1_pubkey_record_838a",
    "ceremony:genesis_agent1_keygen_838a",
}


def test_diagnostic_basis_reachable_count_17() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    cc = data["compile_coverage"]
    assert cc["basis_reachable_core_nodes"] == 17, (
        f"Expected 17, got {cc['basis_reachable_core_nodes']}"
    )
    assert cc["core_nodes_total"] == 32, (
        f"Expected 32, got {cc['core_nodes_total']}"
    )


def test_diagnostic_verdict_partial_with_structural_gaps() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    assert data["verdict"] == "PARTIAL_WITH_STRUCTURAL_GAPS"


def test_authority_traceable_count_31() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    at = data["authority_traceability"]
    assert at["authority_traceable_core_nodes"] == 31, (
        f"Expected 31, got {at['authority_traceable_core_nodes']}"
    )


def test_basis_unreachable_exactly_15_nodes() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    unreachable = data["gaps"]["basis_unreachable_core_nodes"]
    assert len(unreachable) == 15, (
        f"Expected 15 basis-unreachable nodes, got {len(unreachable)}"
    )


def test_bootstrap_axiom_category_a_nodes_identified() -> None:
    """The 3 bootstrap-axiom nodes are in the unreachable list (Category A)."""
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    unreachable_ids = {n["candidate_id"] for n in data["gaps"]["basis_unreachable_core_nodes"]}
    for node_id in BOOTSTRAP_AXIOM_NODES:
        assert node_id in unreachable_ids, (
            f"Bootstrap axiom node {node_id!r} not found in basis-unreachable list"
        )


def test_candidate_manifest_has_56_nodes() -> None:
    data = json.loads(CANDIDATES_JSON.read_text())
    assert len(data["nodes"]) == 56, f"Expected 56 nodes, got {len(data['nodes'])}"


def test_all_candidates_are_core_star_map_candidates() -> None:
    data = json.loads(CANDIDATES_JSON.read_text())
    non_core = [n["candidate_id"] for n in data["nodes"] if not n.get("core_star_map_candidate")]
    assert non_core == [], f"Non-core candidates found: {non_core}"


def test_adr_0035_candidate_node_present_in_manifest() -> None:
    data = json.loads(CANDIDATES_JSON.read_text())
    nodes_by_id = {n["candidate_id"]: n for n in data["nodes"]}
    node = nodes_by_id.get("adr:0035_homoiconic_type_definition_system")
    assert node is not None, "adr:0035_homoiconic_type_definition_system not in candidate manifest"
    assert node["canonicality_tier"] == "draft_direction_accepted", (
        f"Expected draft_direction_accepted, got {node['canonicality_tier']!r}"
    )
    assert node["layer"] == "L4_morphogenic_overlay", (
        f"Expected L4_morphogenic_overlay, got {node['layer']!r}"
    )


def test_adr_0035_spec_doc_does_not_exist() -> None:
    """ADR-0035 is formally deferred — no spec doc should exist."""
    matches = list(ADR_DIR.glob("ADR_0035*.md"))
    assert matches == [], (
        f"ADR-0035 spec doc found (should be formally deferred): {matches}"
    )


def test_missing_decomposition_recipes_count_zero() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    count = data["edge_recipe_analysis"]["missing_decomposition_recipe_count"]
    assert count == 0, f"Expected 0 missing recipes, got {count}"


def test_phase_1387b_sim_genesis_compile_02_token() -> None:
    """Token attestation: phase walkthrough contains the canonical phase token."""
    text = WALKTHROUGH.read_text()
    assert "sim_genesis_compile_02_phase_1387b" in text, (
        "Phase token sim_genesis_compile_02_phase_1387b not found in walkthrough"
    )
