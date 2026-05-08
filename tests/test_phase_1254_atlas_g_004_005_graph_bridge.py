from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.rc.atlas_graph_discipline import (
    ATLAS_G_004_005_BRIDGE_VERSION,
    ATLAS_G_004_COMPLETION_TOKEN,
    ATLAS_G_005_COMPLETION_TOKEN,
    PACKAGE_MODULARITY_EDGE_POLICY_TOKEN,
    PHASE_1254_COMPLETE_TOKEN,
    PHASE_1254_LEGACY_GRAPH_DELTA_DISPOSITION_TOKEN,
    build_atlas_g_004_005_artifact,
    build_high_authority_source_classification,
    build_import_dependency_graph_bridge,
    export_atlas_g_004_005_artifact_json,
)


ARTIFACT_JSON = Path(
    "docs/specs/ilc_atlas_g_004_005_high_authority_dependency_bridge_1254_v0.1.json"
)
ARTIFACT_MD = Path(
    "docs/specs/ilc_atlas_g_004_005_high_authority_dependency_bridge_1254_v0.1.md"
)
STATUS = Path("docs/phases/STATUS.md")
WALKTHROUGH = Path("docs/phases/phase_1254_atlas_g_004_005_graph_bridge_walkthrough.md")
PHASE_1251_AUDIT_MD = Path("docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.md")
PHASE_1251_AUDIT_JSON = Path("docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.json")


def _artifact() -> dict[str, object]:
    return build_atlas_g_004_005_artifact()


def _edges_by_type(artifact: dict[str, object], edge_type: str) -> list[dict[str, object]]:
    bridge = artifact["dependency_graph_bridge"]
    assert isinstance(bridge, dict)
    edges = bridge["edges"]
    assert isinstance(edges, list)
    return [edge for edge in edges if edge["edge_type"] == edge_type]


def test_phase_1254_artifact_is_canonical_and_matches_builder() -> None:
    artifact = _artifact()
    assert artifact["status"] == "pass"
    assert artifact["version"] == ATLAS_G_004_005_BRIDGE_VERSION

    exported = export_atlas_g_004_005_artifact_json(artifact)
    assert exported == json.dumps(
        json.loads(exported),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )

    committed = ARTIFACT_JSON.read_text(encoding="utf-8")
    assert committed.endswith("\n")
    assert committed.strip() == exported


def test_phase_1254_required_tokens_and_concept_terms_are_recorded() -> None:
    artifact = _artifact()
    tokens = set(artifact["required_tokens"])
    assert {
        ATLAS_G_004_COMPLETION_TOKEN,
        ATLAS_G_005_COMPLETION_TOKEN,
        PHASE_1254_LEGACY_GRAPH_DELTA_DISPOSITION_TOKEN,
        PHASE_1254_COMPLETE_TOKEN,
    } <= tokens

    combined_text = "\n".join(
        [
            ARTIFACT_JSON.read_text(encoding="utf-8"),
            ARTIFACT_MD.read_text(encoding="utf-8"),
            WALKTHROUGH.read_text(encoding="utf-8"),
            STATUS.read_text(encoding="utf-8"),
        ]
    )
    for concept in (
        "high-authority",
        "dependency bridge",
        "import root",
        "Rust crate",
        "CLI entrypoint",
        "package profile",
        "legacy graph_delta",
        "core/support/archive",
    ):
        assert concept in combined_text


def test_high_authority_sources_are_classified_core_support_or_archive() -> None:
    classification = build_high_authority_source_classification()
    assert classification["status"] == "pass"
    assert classification["class_counts"]["core"] > 0
    assert classification["class_counts"]["support"] > 0
    assert classification["class_counts"]["archive"] > 0

    by_path = {source["path"]: source for source in classification["sources"]}
    assert by_path["docs/PLANNING_INDEX.md"]["authority_class"] == "core"
    assert (
        by_path["docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"][
            "authority_class"
        ]
        == "core"
    )
    assert (
        by_path["docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md"][
            "authority_class"
        ]
        == "archive"
    )
    assert (
        by_path["docs/phases/phase_1253_transport_principal_identity_spec_walkthrough.md"][
            "authority_class"
        ]
        == "support"
    )
    assert by_path["ilc_core/rc/atlas_graph_discipline.py"]["authority_class"] == "core"

    for source in classification["sources"]:
        path = source["path"]
        assert isinstance(path, str)
        assert not path.startswith("/")
        assert ".." not in Path(path).parts


def test_legacy_graph_delta_gap_disposition_uses_correct_fix1_route() -> None:
    classification = build_high_authority_source_classification()
    disposition = classification["legacy_graph_delta_gap_disposition"]

    assert disposition["finding_id"] == "RCGAP-1250-FIX1-002"
    assert disposition["missing_legacy_graph_delta_count"] == 129
    assert disposition["bulk_legacy_backfill_authorized"] is False
    assert disposition["token"] == PHASE_1254_LEGACY_GRAPH_DELTA_DISPOSITION_TOKEN
    assert "do not blindly edit" not in json.dumps(disposition)
    assert any(
        item["action"] == "preserve_archive_classification_and_avoid_bulk_history_rewrites"
        for item in disposition["priority_backfill_policy"]
    )

    phase_1251_json = json.loads(PHASE_1251_AUDIT_JSON.read_text(encoding="utf-8"))
    routes = phase_1251_json["fix1_finding_scope"]["non_package_findings_remain_routed"]
    assert routes["phase_1254"]["finding_ids"] == ["RCGAP-1250-FIX1-002"]
    assert routes["phase_1252"]["finding_ids"] == [
        "RCGAP-1250-FIX1-003",
        "RCGAP-1250-FIX1-006",
    ]
    phase_1251_text = PHASE_1251_AUDIT_MD.read_text(encoding="utf-8")
    assert "`phase_1254`: `RCGAP-1250-FIX1-002`" in phase_1251_text


def test_dependency_bridge_contains_expected_edge_families() -> None:
    artifact = _artifact()
    bridge = artifact["dependency_graph_bridge"]
    assert bridge["status"] == "pass"
    assert bridge["package_modularity_edge_policy_token"] == PACKAGE_MODULARITY_EDGE_POLICY_TOKEN
    assert bridge["edge_count"] < bridge["max_edges"]

    edge_types = set(bridge["edge_types"])
    assert {
        "high_authority_source_classified_as",
        "package_component_reachable_from_anchor",
        "package_profile_exports_surface",
        "package_profile_requires_component",
        "python_cli_entrypoint",
        "python_surface_imports_root",
        "rust_binary_entrypoint",
        "rust_crate_dependency",
    } <= edge_types


def test_dependency_bridge_connects_package_profiles_and_non_excisable_components() -> None:
    artifact = _artifact()
    package_edges = _edges_by_type(artifact, "package_profile_requires_component")
    required_pairs = {
        (
            "package_profile:openclaw_skill_claimable",
            "package_component:canonical_json_policy",
        ),
        (
            "package_profile:openclaw_skill_claimable",
            "package_component:ecu_ilc_economic_boundary",
        ),
        (
            "package_profile:openclaw_skill_claimable",
            "package_component:genesis_lineage_verification",
        ),
        (
            "package_profile:openclaw_skill_claimable",
            "package_component:protocol_bundle_verification",
        ),
        (
            "package_profile:openclaw_skill_claimable",
            "package_component:rust_consensus_core_binding",
        ),
    }
    actual_pairs = {(edge["source"], edge["target"]) for edge in package_edges}
    assert required_pairs <= actual_pairs

    surface_edges = _edges_by_type(artifact, "package_profile_exports_surface")
    assert (
        "package_profile:openclaw_skill_claimable",
        "package_surface:public_claimability",
    ) in {(edge["source"], edge["target"]) for edge in surface_edges}


def test_dependency_bridge_connects_import_roots_rust_crates_and_cli_entrypoints() -> None:
    artifact = _artifact()

    python_edges = _edges_by_type(artifact, "python_surface_imports_root")
    assert ("python_surface:ilc_logic", "python_import_root:ilc_core") in {
        (edge["source"], edge["target"]) for edge in python_edges
    }

    rust_edges = _edges_by_type(artifact, "rust_crate_dependency")
    assert {"rust_dependency:quinn", "rust_dependency:rustls", "rust_dependency:tokio"} <= {
        edge["target"] for edge in rust_edges
    }

    cli_edges = _edges_by_type(artifact, "python_cli_entrypoint")
    assert ("python_console_script:ilc", "python_callable:ilc_core.cli.main:main") in {
        (edge["source"], edge["target"]) for edge in cli_edges
    }

    for edge in artifact["dependency_graph_bridge"]["edges"]:
        assert str(edge["edge_id"]).startswith("atlas-g-1254:")
        assert len(str(edge["edge_id"]).removeprefix("atlas-g-1254:")) == 64
        for path in edge["evidence_paths"]:
            assert not str(path).startswith("/")
            assert ".." not in Path(str(path)).parts


def test_phase_1254_bounds_fail_closed() -> None:
    with pytest.raises(ValueError, match="atlas_g_1254_high_authority_source_limit"):
        build_high_authority_source_classification(max_sources=1)
    with pytest.raises(ValueError, match="atlas_g_1254_dependency_edge_limit"):
        build_import_dependency_graph_bridge(max_edges=1)


def test_phase_1254_non_authorization_boundary_and_status_updated() -> None:
    artifact = _artifact()
    assert "no_v0_2_signing" in artifact["non_authorization_boundary"]
    assert "no_public_rc_claim" in artifact["non_authorization_boundary"]
    assert "no_genesis_atlas_v0_2_regeneration" in artifact["non_authorization_boundary"]

    status_text = STATUS.read_text(encoding="utf-8")
    assert "## Phase 1254" in status_text
    assert PHASE_1254_COMPLETE_TOKEN in status_text
    assert "Phase 1255" in status_text
