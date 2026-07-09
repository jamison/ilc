from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY = REPO_ROOT / "docs/specs/ilc_edge_namespace_and_extension_policy_v0.1.md"
TAXONOMY = (
    REPO_ROOT
    / "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md"
)
PHASE_1574_PROMPT = (
    REPO_ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _taxonomy_edge_types() -> set[str]:
    text = _read(TAXONOMY)
    section_4 = text.split("## §4 — Canonical ILC Edge Type Namespace", 1)[1].split(
        "## §4a — Additional Canonical Native Edge Definitions", 1
    )[0]
    section_4a = text.split("## §4a — Additional Canonical Native Edge Definitions", 1)[
        1
    ].split("## §4b — Simplification, Recipes, and Retirement Plan", 1)[0]
    return set(re.findall(r"^### ([A-Z_]+)$", section_4, flags=re.MULTILINE)) | set(
        re.findall(r"^\| `([A-Z_]+)` \|", section_4a, flags=re.MULTILINE)
    )


def test_policy_spec_exists() -> None:
    assert POLICY.exists()
    assert "# ILC Edge Namespace and Extension Policy v0.1" in _read(POLICY)


def test_policy_lists_every_current_atlas_fix38_edge_type() -> None:
    policy = _read(POLICY)

    for edge_type in sorted(_taxonomy_edge_types()):
        assert f"`{edge_type}`" in policy


def test_policy_lists_cdl099_protocol_hyperedge_types() -> None:
    policy = _read(POLICY)

    for hyperedge_type in {
        "panel",
        "co_authorship",
        "refutation_coalition",
        "epoch_boundary",
        "jury_verdict",
    }:
        assert f"`{hyperedge_type}`" in policy


def test_policy_reserves_cross_section_ref() -> None:
    policy = _read(POLICY)

    assert "`CROSS_SECTION_REF` is a reserved section-architecture edge type" in policy
    assert "Public-to-private `CROSS_SECTION_REF` stubs are forbidden by default" in policy


def test_policy_requires_namespaced_noncanonical_user_extensions() -> None:
    policy = _read(POLICY)

    assert "`user:<agent_id>:<edge_type>`" in policy
    assert "`x-<domain>:<edge_type>`" in policy
    assert "Extension edge names are non-canonical by default" in policy
    assert "Extension edges must not use bare reserved ILC terms" in policy


def test_policy_routes_canonical_taxonomy_changes_to_governance() -> None:
    policy = _read(POLICY)

    assert "Atlas/Fix38 operational taxonomy changes require a phase" in policy
    assert "Protocol `HyperEdge.hyperedge_type` additions or semantic changes route through" in policy
    assert "Section edge changes route through CDL-098" in policy


def test_policy_does_not_expand_57_node_signing_core() -> None:
    policy = _read(POLICY)

    assert "This policy does not expand the 57-node Genesis signing core" in policy
    assert "not part of the 57-node Genesis signing core unless" in policy


def test_phase_1574_requires_edge_namespace_policy_token() -> None:
    prompt = _read(PHASE_1574_PROMPT)

    assert "edge_namespace_extension_policy_committed_phase_1573ah" in prompt
