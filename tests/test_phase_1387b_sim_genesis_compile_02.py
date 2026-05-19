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

# Signed v0.1 baseline — restored to Phase 1142s state (Option A hygiene, Phase 1387j).
# Properties added by Phase 1387c/e/f/g/h live in the candidate files below.
DIAGNOSTIC_JSON = ROOT / "out" / "genesis_compile_coverage_diagnostic_v0.1.json"
DIAGNOSTIC_JSON_CANDIDATE = ROOT / "out" / "genesis_compile_coverage_diagnostic_v0.3_candidate.json"
CANDIDATES_JSON = ROOT / "out" / "genesis_node_candidates_v0.2_candidate.json"
WALKTHROUGH = ROOT / "docs" / "phases" / "phase_1387b_sim_genesis_compile_02_walkthrough.md"
ADR_DIR = ROOT / "docs" / "adr"

# Category A bootstrap axioms identified in this phase
BOOTSTRAP_AXIOM_NODES = {
    "artifact:genesis_intent_attestation_init_authority_map",
    "artifact:genesis_agent1_pubkey_record_838a",
    "ceremony:genesis_agent1_keygen_838a",
}


def test_diagnostic_basis_reachable_count() -> None:
    # Signed v0.1 baseline (Phase 1142s): 17/32 basis-reachable, PARTIAL_WITH_STRUCTURAL_GAPS.
    # The v0.3_candidate state (Phase 1387c/e) reaches 54/54 — tested via candidate file.
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    cc = data["compile_coverage"]
    assert cc["core_nodes_total"] == 32, (
        f"Signed v0.1 baseline should have 32 core nodes, got {cc['core_nodes_total']}"
    )
    assert cc["basis_reachable_core_nodes"] == 17, (
        f"Signed v0.1 baseline should have 17 basis-reachable, got {cc['basis_reachable_core_nodes']}"
    )


def test_candidate_basis_reachable_count() -> None:
    # v0.3_candidate: Phase 1387c expanded transition basis; Phase 1387e expanded star map.
    # All 54 core nodes are now authority-reachable in the candidate state.
    data = json.loads(DIAGNOSTIC_JSON_CANDIDATE.read_text())
    cc = data["compile_coverage"]
    assert cc["core_nodes_total"] == 54, (
        f"Expected 54 core nodes in v0.3_candidate, got {cc['core_nodes_total']}"
    )
    assert cc["basis_reachable_core_nodes"] == cc["core_nodes_total"], (
        f"Expected all {cc['core_nodes_total']} core nodes reachable in v0.3_candidate; "
        f"got {cc['basis_reachable_core_nodes']}"
    )


def test_diagnostic_verdict_not_fail() -> None:
    # Phase 1387c supersedes the PARTIAL_WITH_STRUCTURAL_GAPS verdict by expanding
    # the transition basis; the verdict is now GENESIS_CORE_COMPLETE_SOURCE_COVERAGE_PARTIAL.
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    assert data["verdict"] != "FAIL_CORE_INADEQUATE", "Diagnostic must not be a failure verdict"


def test_authority_traceable_count_baseline() -> None:
    # Signed v0.1 baseline: 31 authority-traceable of 32 core nodes.
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    at = data["authority_traceability"]
    assert at["authority_traceable_core_nodes"] == 31, (
        f"Signed v0.1 baseline should have 31 authority-traceable, got {at['authority_traceable_core_nodes']}"
    )


def test_authority_traceable_count_53_candidate() -> None:
    # v0.3_candidate: 54 nodes; 53 authority-traceable (attestation root cannot
    # trace back to itself — correct by construction).
    data = json.loads(DIAGNOSTIC_JSON_CANDIDATE.read_text())
    at = data["authority_traceability"]
    assert at["authority_traceable_core_nodes"] == 53, (
        f"Expected 53 in v0.3_candidate, got {at['authority_traceable_core_nodes']}"
    )


def test_basis_unreachable_15_in_baseline() -> None:
    # Signed v0.1 baseline: 15 unreachable nodes (identified in Phase 1387b).
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    unreachable = data["gaps"]["basis_unreachable_core_nodes"]
    assert len(unreachable) == 15, (
        f"Signed v0.1 baseline should have 15 unreachable nodes; got {len(unreachable)}"
    )


def test_basis_unreachable_empty_in_candidate() -> None:
    # v0.3_candidate: Phase 1387c added Category A bootstrap axioms to transition
    # basis; gap is now closed.
    data = json.loads(DIAGNOSTIC_JSON_CANDIDATE.read_text())
    unreachable = data["gaps"]["basis_unreachable_core_nodes"]
    assert unreachable == [], (
        f"Expected empty unreachable list in v0.3_candidate; got {[n['candidate_id'] for n in unreachable]}"
    )


def test_bootstrap_axiom_category_a_nodes_now_in_basis() -> None:
    """The 3 bootstrap-axiom nodes identified in Phase 1387b are now in the
    v0.3_candidate genesis-derivable tier."""
    data = json.loads(DIAGNOSTIC_JSON_CANDIDATE.read_text())
    genesis_derivable = set(data["tier_analysis"]["genesis_derivable_node_ids"])
    for node_id in BOOTSTRAP_AXIOM_NODES:
        assert node_id in genesis_derivable, (
            f"Bootstrap axiom node {node_id!r} should now be genesis-derivable in v0.3_candidate"
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


def test_adr_0035_formal_adr_exists() -> None:
    """ADR-0035 formal ADR written in Phase 1387d — doc should now exist."""
    matches = list(ADR_DIR.glob("ADR_0035*.md"))
    assert len(matches) == 1, (
        f"Expected exactly one ADR-0035 file in docs/adr/; found: {matches}"
    )
    text = matches[0].read_text()
    assert "adr_0035_homoiconic_type_definition_system_direction_accepted" in text, (
        "ADR-0035 missing direction-accepted token"
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
