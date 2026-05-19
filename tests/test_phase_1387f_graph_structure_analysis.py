"""Phase 1387f — SIM-GRAPHOPT-01: graph structure analysis extension.

Tests verify:
- graph_structure_analysis section is present in diagnostic
- Authority-trace depth distribution is computed and bounded
- Max depth ≤ 3 (hub-and-spoke invariant: attestation root → all nodes in ≤ 2 hops)
- Duplicate recipe groups detected (GOVERNS/CONSTRAINS confirmed merge candidate)
- GOVERNS and CONSTRAINS share the same primitive recipe (validate.claim ∘ link.claim)
- Edges missing decomposition_recipe correctly tallied by type
- ATTESTATION and PROVENANCE edges account for all missing recipes
- Orphan nodes (basis-reachable, no outgoing edges) are detected
- All traced core nodes have non-negative depth
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIAGNOSTIC_JSON = ROOT / "out" / "genesis_compile_coverage_diagnostic_v0.1.json"


def _data() -> dict:
    return json.loads(DIAGNOSTIC_JSON.read_text())


def _gsa() -> dict:
    return _data()["graph_structure_analysis"]


def test_graph_structure_analysis_section_present() -> None:
    data = _data()
    assert "graph_structure_analysis" in data, "graph_structure_analysis section missing"


def test_authority_trace_depth_section_present() -> None:
    gsa = _gsa()
    assert "authority_trace_depth" in gsa
    dt = gsa["authority_trace_depth"]
    assert "depth_histogram" in dt
    assert "max_depth" in dt
    assert "mean_depth" in dt
    assert "traced_core_node_count" in dt


def test_authority_trace_max_depth_bounded() -> None:
    """Hub-and-spoke invariant: all core nodes within 2 hops of attestation root."""
    dt = _gsa()["authority_trace_depth"]
    assert dt["max_depth"] <= 3, (
        f"Expected max authority-trace depth ≤ 3; got {dt['max_depth']}. "
        "The graph should remain a shallow hub-and-spoke from the attestation root."
    )


def test_authority_trace_depth_histogram_covers_all_traced_nodes() -> None:
    dt = _gsa()["authority_trace_depth"]
    histogram_total = sum(dt["depth_histogram"].values())
    assert histogram_total == dt["traced_core_node_count"], (
        f"Depth histogram sum {histogram_total} != traced count {dt['traced_core_node_count']}"
    )


def test_all_core_nodes_authority_traceable() -> None:
    """After Phase 1387e: 53/54 core nodes authority-traceable (attestation root excluded)."""
    dt = _gsa()["authority_trace_depth"]
    # Attestation root is not traceable to itself — 1 node excluded is correct
    assert dt["nodes_not_authority_traceable_count"] <= 1, (
        f"Expected at most 1 non-traceable node (the attestation root itself); "
        f"got {dt['nodes_not_authority_traceable_count']}"
    )


def test_duplicate_recipe_groups_detected() -> None:
    gsa = _gsa()
    assert gsa["duplicate_recipe_group_count"] >= 1, (
        "Expected at least 1 duplicate recipe group (GOVERNS/CONSTRAINS); found none"
    )


def test_governs_constrains_share_recipe() -> None:
    """GOVERNS and CONSTRAINS confirmed merge candidates per ADR-0035 §4.3."""
    gsa = _gsa()
    groups = gsa["duplicate_recipe_groups"]
    found = False
    for g in groups:
        types = set(g["edge_types_sharing_recipe"])
        if "GOVERNS" in types and "CONSTRAINS" in types:
            found = True
            assert g["merge_candidate"] is True
            break
    assert found, "GOVERNS/CONSTRAINS duplicate-recipe group not found"


def test_edges_missing_recipe_count_zero_after_1387h() -> None:
    # Phase 1387f found 30 edges (17 ATTESTATION + 13 PROVENANCE) missing recipes.
    # Phase 1387h canonicalized all 30; the gap is now closed.
    gsa = _gsa()
    assert gsa["edges_missing_recipe_count"] == 0, (
        f"Expected 0 edges missing recipe after Phase 1387h; got {gsa['edges_missing_recipe_count']}"
    )


def test_orphan_node_count_positive() -> None:
    """Orphan nodes (leaf nodes with no outgoing star-map edges) should exist."""
    gsa = _gsa()
    assert gsa["orphan_node_count"] > 0, (
        "Expected orphan nodes to be detected (leaf nodes in the star map)"
    )


def test_orphan_nodes_are_basis_reachable() -> None:
    """All orphan nodes must be basis-reachable (we only track reachable orphans)."""
    gsa = _gsa()
    data = _data()
    reachable_ids = set(data["tier_analysis"]["genesis_derivable_node_ids"])
    for node_id in gsa["orphan_nodes"]:
        assert node_id in reachable_ids, (
            f"Orphan node {node_id!r} is not basis-reachable — unexpected"
        )


def test_phase_1387f_token_in_compiler() -> None:
    compiler = (ROOT / "tools" / "genesis_compile_coverage_diagnostic.py").read_text()
    assert "Phase 1387f" in compiler, "Phase 1387f annotation not found in compiler"
