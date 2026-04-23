"""
ADR-0033 verification.
"""

from pathlib import Path

TYPES_PATH = Path("ilc_core/types.py")


ADR_PATH = Path("docs/adr/ADR_0033_Star_Map_Homoiconic_Epistemiological_Entity.md")
README_PATH = Path("docs/adr/README.md")


def _read() -> str:
    return ADR_PATH.read_text(encoding="utf-8")


def test_adr_exists_and_is_accepted() -> None:
    text = _read()
    assert ADR_PATH.is_file()
    assert "**Status:** Accepted" in text
    assert "`run_h003_star_map_homoiconic_adr_verdict=accepted`" in text


def test_adr_declares_star_map_results_first_class_nodes() -> None:
    text = _read()
    assert "published star-map navigation results are first-class nodes" in text
    assert '`Node.type = "star_map"`' in text


def test_adr_defines_identity_and_claim_form_contract() -> None:
    text = _read()
    for marker in (
        "source_node_set_digest",
        "parameter_digest",
        "result_payload",
        "claim-form contract",
    ):
        assert marker in text


def test_adr_has_explicit_interaction_matrix() -> None:
    text = _read()
    for marker in ("ADR-0003 remains unchanged", "ADR-0005 remains unchanged", "ADR-0029 remains unchanged"):
        assert marker in text


def test_adr_defers_economic_formula() -> None:
    text = _read()
    assert "does **not** define the ECU formula" in text
    assert "H-CON-01" in text


def test_adr_readme_index_mentions_adr_0033() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    assert "ADR-0033" in text
    assert "Star Map Homoiconic Epistemiological Entity" in text


def test_adr_authorizes_exactly_the_three_entity_kinds() -> None:
    # ADR §2.3 authorizes route_cluster, panel_result, and navigation_overlay as
    # node-addressable entity kinds.  Anything not on that list is implicitly
    # unauthorized until a future ADR extends it.  This test pins all three so
    # that a silent rename or removal is caught immediately.
    text = _read()
    for kind in ("route_cluster", "panel_result", "navigation_overlay"):
        assert kind in text, f"entity kind '{kind}' missing from ADR-0033 §2.3"


def test_star_map_node_type_exists_in_runtime_types() -> None:
    # ADR §2.2 asserts "uses the already-existing runtime node type Node.type='star_map'".
    # This test cross-checks ilc_core/types.py directly so that removing or renaming
    # the token in the runtime would fail here rather than silently diverging from
    # the ADR's claim.
    types_text = TYPES_PATH.read_text(encoding="utf-8")
    assert '"star_map"' in types_text, (
        "Node.type='star_map' not found in ilc_core/types.py — "
        "ADR-0033 §2.2 claims this is an already-existing runtime node type"
    )
