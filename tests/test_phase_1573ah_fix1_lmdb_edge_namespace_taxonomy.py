from __future__ import annotations

import re
from pathlib import Path

from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    _KNOWN_EDGE_TYPES,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = (
    REPO_ROOT
    / "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md"
)
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"


def _taxonomy_text() -> str:
    return TAXONOMY.read_text(encoding="utf-8")


def _fix38_edge_types() -> set[str]:
    text = _taxonomy_text()
    section = text.split("## §4 — Canonical ILC Edge Type Namespace", 1)[1]
    section = section.split("## §4a — Additional Canonical Native Edge Definitions", 1)[0]
    return set(re.findall(r"^### ([A-Z_]+)$", section, flags=re.MULTILINE))


def _lmdb_reserved_extra_edge_types() -> set[str]:
    text = _taxonomy_text()
    section = text.split("## §4a — Additional Canonical Native Edge Definitions", 1)[1]
    section = section.split("## §5 — Classification Decision Tree", 1)[0]
    return set(re.findall(r"^\| `([A-Z_]+)` \|", section, flags=re.MULTILINE))


def test_taxonomy_reserves_every_lmdb_writer_edge_type() -> None:
    documented = _fix38_edge_types() | _lmdb_reserved_extra_edge_types()

    assert _KNOWN_EDGE_TYPES <= documented
    assert "GOVERNS" in _lmdb_reserved_extra_edge_types()
    assert "CONTAINS_FILE" in _lmdb_reserved_extra_edge_types()
    assert "PROPOSES_CHANGE_TO" in _lmdb_reserved_extra_edge_types()


def test_single_canonical_namespace_uses_profiles_for_phase_intake_and_lmdb() -> None:
    fix38 = _fix38_edge_types()
    extra = _lmdb_reserved_extra_edge_types()
    text = _taxonomy_text()

    assert "SOURCE_TREE_MEMBER" in fix38
    assert "TESTS" in fix38
    assert "GOVERNS" not in fix38
    assert "GOVERNS" in extra
    assert "CONTAINS_FILE" not in fix38
    assert "CONTAINS_FILE" in extra
    assert "one canonical ILC edge namespace" in text
    assert "usage_profile=phase_intake" in text
    assert "usage_profile=atlas_native_reserved" in text
    assert "usage_profile=legacy_reserved_no_new_use" in text


def test_live_lmdb_uses_only_reserved_writer_edge_types() -> None:
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        edges = writer.store.iter_edges()
    finally:
        writer.close()

    live_edge_types = {str(edge.get("edge_type", "")) for edge in edges}
    assert live_edge_types <= _KNOWN_EDGE_TYPES


def test_taxonomy_warns_against_blind_lmdb_edge_substitution() -> None:
    text = _taxonomy_text()

    assert "Do not run a blind migration" in text
    assert "Safe substitutions are contextual, not mechanical" in text
    assert "The current difference between phase-intake and Atlas-native usage profiles is" in text
    assert "single canonical ILC edge namespace" in text


def test_taxonomy_defines_recipe_retirement_plan_for_legacy_edges() -> None:
    text = _taxonomy_text()

    assert "## §4b — Simplification, Recipes, and Retirement Plan" in text
    assert "| `REFERENCES` | `legacy_retire_candidate` |" in text
    assert "| `IMPLEMENTS_MODULE` | `legacy_retire_candidate` |" in text
    assert "| `RATIFICATION_EVIDENCE_FOR` | `recipe_retire_candidate` |" in text
    assert "| `USES` | `recipe_retire_candidate` |" in text
    assert "| `OPENED_FOR` | `recipe_retire_candidate` |" in text
    assert "| `PRELOCK_FOR` | `recipe_retire_candidate` |" in text
    assert "Near-term cleanup target: retire `REFERENCES`, `IMPLEMENTS_MODULE`" in text


def test_taxonomy_keeps_native_primitives_and_materialized_shortcuts() -> None:
    text = _taxonomy_text()

    assert "| `CONTAINS_FILE` | `materialized_shortcut_keep` |" in text
    assert "| `SAME_SOURCE` | `materialized_shortcut_keep` |" in text
    assert "| `GOVERNS` | `native_primitive_keep` |" in text
    assert "| `CONSTRAINS` | `native_primitive_keep` |" in text
    assert "| `SAME_AUTHORITY` | `native_primitive_keep` |" in text
    assert "| `SUPERSEDED_BY` | `native_primitive_keep` |" in text
