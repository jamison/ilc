from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md"
NAMESPACE_POLICY = "docs/specs/ilc_edge_namespace_and_extension_policy_v0.1.md"


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _flat(path: str) -> str:
    return " ".join(_read(path).split())


def test_agents_references_canonical_graph_classification_sources() -> None:
    text = _read("AGENTS.md")
    flat = _flat("AGENTS.md")

    assert "Canonical graph classification sources:" in text
    assert TAXONOMY in text
    assert NAMESPACE_POLICY in text
    assert "do not invent custom edge types" in flat
    assert "user extension edges remain" in flat
    assert "non-canonical unless a later governance process ratifies them" in flat


def test_claude_references_canonical_graph_classification_sources() -> None:
    text = _read("CLAUDE.md")
    flat = _flat("CLAUDE.md")

    assert "**Full taxonomy:**" in text
    assert "**Namespace policy:**" in text
    assert TAXONOMY in text
    assert NAMESPACE_POLICY in text
    assert "do not invent custom edge types" in flat
    assert "extension edges remain non-canonical unless later ratified" in flat


def test_phase_prompt_schema_references_taxonomy_and_namespace_policy() -> None:
    text = _read("docs/antigravity_tasks/README.md")
    flat = _flat("docs/antigravity_tasks/README.md")

    assert "Canonical graph classification sources:" in text
    assert TAXONOMY in text
    assert NAMESPACE_POLICY in text
    assert "Until `ilc_edge_namespace_and_extension_policy_v0.1.md` exists" in text
    assert "use only edge types from the taxonomy spec" in flat
    assert "extension edges remain" in flat
    assert "non-canonical unless later ratified" in flat
