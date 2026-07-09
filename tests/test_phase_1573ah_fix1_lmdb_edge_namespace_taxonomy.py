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
    section = text.split("## §4 — Fix38 Annotation Edge Type Taxonomy", 1)[1]
    section = section.split("## §4a — Atlas/LMDB Reserved Native Edge Namespace", 1)[0]
    return set(re.findall(r"^### ([A-Z_]+)$", section, flags=re.MULTILINE))


def _lmdb_reserved_extra_edge_types() -> set[str]:
    text = _taxonomy_text()
    section = text.split("## §4a — Atlas/LMDB Reserved Native Edge Namespace", 1)[1]
    section = section.split("## §5 — Classification Decision Tree", 1)[0]
    return set(re.findall(r"^\| `([A-Z_]+)` \|", section, flags=re.MULTILINE))


def test_taxonomy_reserves_every_lmdb_writer_edge_type() -> None:
    documented = _fix38_edge_types() | _lmdb_reserved_extra_edge_types()

    assert _KNOWN_EDGE_TYPES <= documented
    assert "GOVERNS" in _lmdb_reserved_extra_edge_types()
    assert "CONTAINS_FILE" in _lmdb_reserved_extra_edge_types()
    assert "PROPOSES_CHANGE_TO" in _lmdb_reserved_extra_edge_types()


def test_fix38_subset_is_narrower_than_lmdb_native_namespace() -> None:
    fix38 = _fix38_edge_types()
    extra = _lmdb_reserved_extra_edge_types()

    assert "SOURCE_TREE_MEMBER" in fix38
    assert "TESTS" in fix38
    assert "GOVERNS" not in fix38
    assert "GOVERNS" in extra
    assert "CONTAINS_FILE" not in fix38
    assert "CONTAINS_FILE" in extra


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
    assert "The current discrepancy between the Fix38 subset and the Atlas/LMDB edge set is" in text
    assert "intentional after this section" in text
