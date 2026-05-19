"""Phase 1387h — SIM-GRAPHOPT-03: ATTESTATION/PROVENANCE edge recipe canonicalization.

Tests verify:
- All 77 star-map edges now carry decomposition_recipe
- ATTESTATION recipe: assert.truth ∘ link.claim, scope=agent_signing_endorsement
- PROVENANCE recipe: assert.truth ∘ link.claim, scope=derivation_origin_chain
- ATTESTATION and PROVENANCE are correctly distinguished by scope (not merged)
- A second duplicate-recipe group is now surfaced:
  ATTESTATION/PRIMITIVE_INVOCATION/PROVENANCE all share (assert.truth, link.claim)
  with distinct scope parameters — valid under ADR-0035 §4.3
- GOVERNS/CONSTRAINS remain the primary merge candidate (validate.claim ∘ link.claim)
- Total duplicate recipe groups = 2
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
STAR_MAP = ROOT / "out" / "genesis_core_star_map_v0.1.json"
DIAGNOSTIC_JSON = ROOT / "out" / "genesis_compile_coverage_diagnostic_v0.1.json"


def _edges_by_type(edge_type: str) -> list[dict]:
    data = json.loads(STAR_MAP.read_text())
    return [e for e in data["edges"] if e["edge_type"] == edge_type]


def _gsa() -> dict:
    return json.loads(DIAGNOSTIC_JSON.read_text())["graph_structure_analysis"]


def test_all_edges_have_decomposition_recipe() -> None:
    data = json.loads(STAR_MAP.read_text())
    missing = [e["edge_id"] for e in data["edges"] if not e.get("decomposition_recipe")]
    assert missing == [], f"Edges still missing decomposition_recipe: {missing}"


def test_attestation_recipe_primitives() -> None:
    for edge in _edges_by_type("ATTESTATION"):
        dr = edge.get("decomposition_recipe", {})
        prims = set(dr.get("primitives", []))
        assert prims == {"assert.truth", "link.claim"}, (
            f"ATTESTATION edge {edge['edge_id']} has wrong primitives: {prims}"
        )


def test_attestation_recipe_scope() -> None:
    for edge in _edges_by_type("ATTESTATION"):
        scope = edge.get("decomposition_recipe", {}).get("scope", "")
        assert scope == "agent_signing_endorsement", (
            f"ATTESTATION edge {edge['edge_id']} has wrong scope: {scope!r}"
        )


def test_provenance_recipe_primitives() -> None:
    for edge in _edges_by_type("PROVENANCE"):
        dr = edge.get("decomposition_recipe", {})
        prims = set(dr.get("primitives", []))
        assert prims == {"assert.truth", "link.claim"}, (
            f"PROVENANCE edge {edge['edge_id']} has wrong primitives: {prims}"
        )


def test_provenance_recipe_scope() -> None:
    for edge in _edges_by_type("PROVENANCE"):
        scope = edge.get("decomposition_recipe", {}).get("scope", "")
        assert scope == "derivation_origin_chain", (
            f"PROVENANCE edge {edge['edge_id']} has wrong scope: {scope!r}"
        )


def test_attestation_provenance_distinguished_by_scope() -> None:
    """ATTESTATION and PROVENANCE share a primitive recipe but have different scopes —
    valid under ADR-0035 §4.3 (scope parameter distinguishes the cases)."""
    att_scopes = {e["decomposition_recipe"]["scope"] for e in _edges_by_type("ATTESTATION")}
    prov_scopes = {e["decomposition_recipe"]["scope"] for e in _edges_by_type("PROVENANCE")}
    assert att_scopes.isdisjoint(prov_scopes), (
        f"ATTESTATION and PROVENANCE should have distinct scopes; "
        f"overlap: {att_scopes & prov_scopes}"
    )


def test_diagnostic_edges_missing_recipe_zero() -> None:
    gsa = _gsa()
    assert gsa["edges_missing_recipe_count"] == 0, (
        f"Expected 0 missing after canonicalization; got {gsa['edges_missing_recipe_count']}"
    )


def test_duplicate_recipe_group_count_two() -> None:
    """Two duplicate groups after canonicalization:
    1. GOVERNS/CONSTRAINS: validate.claim ∘ link.claim
    2. ATTESTATION/PRIMITIVE_INVOCATION/PROVENANCE: assert.truth ∘ link.claim
    """
    gsa = _gsa()
    assert gsa["duplicate_recipe_group_count"] == 2, (
        f"Expected 2 duplicate recipe groups; got {gsa['duplicate_recipe_group_count']}"
    )


def test_second_duplicate_group_contains_attestation_and_provenance() -> None:
    gsa = _gsa()
    groups = gsa["duplicate_recipe_groups"]
    att_prov_group = None
    for g in groups:
        types = set(g["edge_types_sharing_recipe"])
        if "ATTESTATION" in types and "PROVENANCE" in types:
            att_prov_group = g
            break
    assert att_prov_group is not None, (
        "No duplicate group containing both ATTESTATION and PROVENANCE found"
    )
    # PRIMITIVE_INVOCATION also shares this recipe
    assert "PRIMITIVE_INVOCATION" in set(att_prov_group["edge_types_sharing_recipe"]), (
        "PRIMITIVE_INVOCATION should also be in the ATTESTATION/PROVENANCE recipe group"
    )


def test_governs_constrains_group_still_present() -> None:
    gsa = _gsa()
    groups = gsa["duplicate_recipe_groups"]
    gc_group = next(
        (g for g in groups if set(g["edge_types_sharing_recipe"]) == {"GOVERNS", "CONSTRAINS"}),
        None,
    )
    assert gc_group is not None, "GOVERNS/CONSTRAINS merge-candidate group not found"
    assert gc_group["merge_candidate"] is True
