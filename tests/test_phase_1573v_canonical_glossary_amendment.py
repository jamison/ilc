from __future__ import annotations

from pathlib import Path


GLOSSARY = Path("docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md")
STATUS = Path("docs/phases/STATUS.md")


def _glossary_text() -> str:
    return GLOSSARY.read_text(encoding="utf-8")


def test_star_map_disambiguation_section_present() -> None:
    text = _glossary_text()

    assert "### 2.12 Star Map, Projection, and Group Node Disambiguation" in text
    assert '#### 2.12.1 "Star Map" Disambiguation' in text
    assert "**AtlasSliceManifest**" in text
    assert "The canonical \"star map\" object going forward" in text
    assert "**Route index**" in text
    assert "**Published star-map navigation node**" in text
    assert "**Graph projection label**" in text


def test_atlas_slice_manifest_is_canonical_star_map_object() -> None:
    text = _glossary_text()

    assert "Use `AtlasSliceManifest` when referring to the signed executable map" in text
    assert "Do not use it to mean ADR-0003 route indexes" in text
    assert "CDL-098 authorizes Genesis to sign public-section AtlasSliceManifest" in text


def test_tier_and_graph_projection_disambiguation_present() -> None:
    text = _glossary_text()

    assert "#### 2.12.2 `graph_projection` Versus `tier`" in text
    assert "**graph_projection**" in text
    assert "**tier**" in text
    assert "Fix55-established five-bucket LMDB node field" in text
    assert "Phase 1576a" in text
    assert "Never conflate CDL-071 temporal tiers" in text


def test_group_node_taxonomy_contains_all_four_terms() -> None:
    text = _glossary_text()

    assert "#### 2.12.3 Group Node Taxonomy" in text
    for term in (
        "repo_group_node",
        "jury_group_node",
        "SigningGroupRulesNode",
        "GatedShardPolicyNode",
    ):
        assert term in text
    assert "not an ADR-0035 type definition node" in text
    assert "not a CDL-099 definition-node instance" in text


def test_phase_1573v_status_tokens_present() -> None:
    status = STATUS.read_text(encoding="utf-8")

    assert "canonical_glossary_star_map_disambiguation_complete_phase_1573v" in status
    assert "canonical_glossary_tier_graph_projection_disambiguation_complete_phase_1573v" in status
    assert "canonical_glossary_group_node_taxonomy_added_phase_1573v" in status
