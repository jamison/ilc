from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPT = (
    REPO_ROOT
    / "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1573ah_g8_edge_namespace_extension_policy.md"
)
PHASE_1574_PROMPT = (
    REPO_ROOT
    / "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_1573ah_prompt_defines_namespace_policy_scope() -> None:
    text = _text(PROMPT)

    assert "# Phase 1573ah-G8: Edge Namespace and Extension Policy" in text
    assert "**Sensitivity:** **NON-SENSITIVE**" in text
    assert "Atlas/Fix38 operational edge taxonomy" in text
    assert "ADR-0035/CDL-099 protocol `HyperEdge.hyperedge_type`" in text
    assert "`CROSS_SECTION_REF` is a reserved section-architecture edge type" in text


def test_1573ah_prompt_requires_user_extension_noncanonical_boundary() -> None:
    text = _text(PROMPT)

    assert "`user:<agent_id>:<edge_type>`" in text
    assert "`x-<domain>:<edge_type>`" in text
    assert "user extension edges are non-canonical by default" in text
    assert "forbid collision with reserved bare ILC terms" in text
    assert "cannot carry ILC authority, settlement meaning" in text


def test_1573ah_prompt_preserves_governance_and_signing_boundaries() -> None:
    text = _text(PROMPT)

    assert "canonical taxonomy changes require governance" in text
    assert "protocol `HyperEdge.hyperedge_type` additions or semantic changes route" in text
    assert "through ADR-0035/CDL-100 and CDL ratification" in text
    assert "The phase must not expand the 57-node Genesis signing core" in text
    assert "edge_namespace_policy_no_signing_core_expansion_phase_1573ah" in text


def test_1573ah_prompt_requires_graph_registration_and_tests() -> None:
    text = _text(PROMPT)

    assert "docs/specs/ilc_edge_namespace_and_extension_policy_v0.1.md" in text
    assert "tests/test_phase_1573ah_edge_namespace_extension_policy.py" in text
    assert "Fix38/Atlas annotation ledger records" in text
    assert "REFERENCES_AUTHORITY `cdl:CDL-098`, `cdl:CDL-099`, `cdl:CDL-100`, `adr:ADR-0035`" in text


def test_phase_1574_prompt_depends_on_1573ah_policy() -> None:
    text = _text(PHASE_1574_PROMPT)

    assert "edge_namespace_extension_policy_committed_phase_1573ah" in text
    assert "canonical edge namespace and user extension policy complete" in text
