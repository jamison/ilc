from __future__ import annotations

import copy
import json
from pathlib import Path

from ilc_core.rc.atlas_graph_discipline import (
    ATLAS_G_006_MANIFEST_PROFILE_CONSISTENCY_FIX1_TOKEN,
    ATLAS_G_006_NO_GENESIS_ATLAS_MUTATION_TOKEN,
    ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_GATE_VERSION,
    ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_VERDICT_TOKEN,
    ATLAS_G_006_PUBLIC_RELEASE_ARTIFACT_NOT_AUTHORIZED_TOKEN,
    ATLAS_G_006_REQUIRED_EDGE_TYPES,
    ATLAS_G_006_REQUIRED_PROFILE_COMPONENTS,
    ATLAS_G_006_REQUIRED_PROFILE_SURFACES,
    build_atlas_g_004_005_artifact,
    build_atlas_g_006_public_rc_graph_reachability_gate,
    export_atlas_g_006_public_rc_graph_reachability_gate_json,
    package_profile_reachability_manifest,
)
from ilc_core.rc.package_profiles import (
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
)


SPEC_PATH = Path(
    "docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1271_atlas_g_006_public_rc_graph_reachability_gate_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

REQUIRED_TOKENS = (
    ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_GATE_VERSION,
    ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_VERDICT_TOKEN,
    ATLAS_G_006_PUBLIC_RELEASE_ARTIFACT_NOT_AUTHORIZED_TOKEN,
    ATLAS_G_006_NO_GENESIS_ATLAS_MUTATION_TOKEN,
)
FIX1_TOKENS = (ATLAS_G_006_MANIFEST_PROFILE_CONSISTENCY_FIX1_TOKEN,)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1271_gate_passes_for_selected_claimable_profile_without_release_authorization() -> None:
    gate = build_atlas_g_006_public_rc_graph_reachability_gate()

    assert gate["status"] == "pass"
    assert gate["gate_status"] == "pass"
    assert gate["selected_profile_id"] == PROFILE_OPENCLAW_SKILL_CLAIMABLE
    assert gate["graph_reachability_verdict"] == "pass_graph_gate_only_release_artifacts_blocked"
    assert gate["public_rc_claim_status"] == "not_authorized"
    assert gate["release_artifact_status"] == "not_authorized"
    assert gate["failing_checks"] == []
    assert set(REQUIRED_TOKENS) <= set(gate["required_tokens"])

    boundary = set(gate["non_authorization_boundary"])
    assert ATLAS_G_006_PUBLIC_RELEASE_ARTIFACT_NOT_AUTHORIZED_TOKEN in boundary
    assert ATLAS_G_006_NO_GENESIS_ATLAS_MUTATION_TOKEN in boundary
    assert "no_public_rc_claim" in boundary
    assert "no_public_repository_publication" in boundary
    assert "no_v0_2_signing" in boundary


def test_phase_1271_gate_requires_public_rc_claimable_profile() -> None:
    gate = build_atlas_g_006_public_rc_graph_reachability_gate(
        profile_id=PROFILE_OPENCLAW_SKILL_LOCAL
    )

    assert gate["status"] == "fail"
    assert gate["graph_reachability_verdict"] == "fail_closed_release_artifacts_blocked"
    assert "selected_profile_is_public_rc_target" in gate["failing_checks"]
    assert (
        "selected_profile_has_public_claimability_without_public_p2p"
        in gate["failing_checks"]
    )
    assert gate["release_artifact_status"] == "not_authorized"


def test_phase_1271_gate_fails_closed_on_missing_anchor_and_component() -> None:
    manifest = package_profile_reachability_manifest(PROFILE_OPENCLAW_SKILL_CLAIMABLE)
    bad_manifest = copy.deepcopy(manifest)
    bad_manifest["status"] = "fail"
    bad_manifest["missing_required_anchors"] = ["genesis"]
    bad_manifest["reachable_anchor_set"] = ["ecu", "hypergraph", "ilc"]
    bad_manifest["package_profile"]["components"] = [
        component
        for component in bad_manifest["package_profile"]["components"]
        if component != "public_claimability_runtime"
    ]

    gate = build_atlas_g_006_public_rc_graph_reachability_gate(
        reachability_manifest=bad_manifest
    )

    assert gate["status"] == "fail"
    assert "package_reachability_manifest_passes" in gate["failing_checks"]
    assert "all_required_anchors_reachable" in gate["failing_checks"]
    assert "required_components_present" in gate["failing_checks"]
    assert gate["release_artifact_status"] == "not_authorized"


def test_phase_1271_fix1_gate_fails_closed_on_manifest_profile_id_mismatch() -> None:
    manifest = package_profile_reachability_manifest(PROFILE_OPENCLAW_SKILL_CLAIMABLE)
    bad_manifest = copy.deepcopy(manifest)
    bad_manifest["profile_id"] = PROFILE_OPENCLAW_SKILL_LOCAL

    gate = build_atlas_g_006_public_rc_graph_reachability_gate(
        profile_id=PROFILE_OPENCLAW_SKILL_CLAIMABLE,
        reachability_manifest=bad_manifest,
    )
    checks = {check["check_id"]: check for check in gate["checks"]}

    assert gate["status"] == "fail"
    assert gate["graph_reachability_verdict"] == "fail_closed_release_artifacts_blocked"
    assert "manifest_profile_matches_selected_profile" in gate["failing_checks"]
    assert (
        checks["manifest_profile_matches_selected_profile"]["fail_reason"]
        == "atlas_g_006_manifest_profile_mismatch"
    )
    assert gate["release_artifact_status"] == "not_authorized"


def test_phase_1271_fix1_gate_fails_closed_on_nested_profile_id_mismatch() -> None:
    manifest = package_profile_reachability_manifest(PROFILE_OPENCLAW_SKILL_CLAIMABLE)
    bad_manifest = copy.deepcopy(manifest)
    bad_manifest["package_profile"]["profile_id"] = PROFILE_OPENCLAW_SKILL_LOCAL

    gate = build_atlas_g_006_public_rc_graph_reachability_gate(
        profile_id=PROFILE_OPENCLAW_SKILL_CLAIMABLE,
        reachability_manifest=bad_manifest,
    )
    checks = {check["check_id"]: check for check in gate["checks"]}

    assert gate["status"] == "fail"
    assert gate["graph_reachability_verdict"] == "fail_closed_release_artifacts_blocked"
    assert "manifest_profile_matches_selected_profile" in gate["failing_checks"]
    assert checks["manifest_profile_matches_selected_profile"]["evidence"] == {
        "manifest_profile_id": PROFILE_OPENCLAW_SKILL_CLAIMABLE,
        "package_profile_id": PROFILE_OPENCLAW_SKILL_LOCAL,
        "selected_profile_id": PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    }
    assert gate["release_artifact_status"] == "not_authorized"


def test_phase_1271_gate_fails_closed_on_missing_dependency_bridge_edges() -> None:
    bridge = build_atlas_g_004_005_artifact()
    bad_bridge = copy.deepcopy(bridge)
    dependency_bridge = bad_bridge["dependency_graph_bridge"]
    dependency_bridge["edge_types"] = [
        edge_type
        for edge_type in dependency_bridge["edge_types"]
        if edge_type != "package_profile_requires_component"
    ]
    dependency_bridge["edges"] = [
        edge
        for edge in dependency_bridge["edges"]
        if edge["edge_type"] != "package_profile_requires_component"
    ]

    gate = build_atlas_g_006_public_rc_graph_reachability_gate(bridge_artifact=bad_bridge)

    assert gate["status"] == "fail"
    assert "required_dependency_edge_types_present" in gate["failing_checks"]
    assert "required_profile_component_edges_present" in gate["failing_checks"]
    assert gate["release_artifact_status"] == "not_authorized"


def test_phase_1271_gate_covers_required_edge_components_and_surfaces() -> None:
    gate = build_atlas_g_006_public_rc_graph_reachability_gate()
    checks = {check["check_id"]: check for check in gate["checks"]}

    assert set(checks["required_dependency_edge_types_present"]["evidence"]["required_edge_types"]) == set(
        ATLAS_G_006_REQUIRED_EDGE_TYPES
    )
    assert set(checks["required_components_present"]["evidence"]["required_components"]) == set(
        ATLAS_G_006_REQUIRED_PROFILE_COMPONENTS
    )
    assert set(checks["required_surfaces_present"]["evidence"]["required_surfaces"]) == set(
        ATLAS_G_006_REQUIRED_PROFILE_SURFACES
    )


def test_phase_1271_export_is_canonical_json() -> None:
    exported_once = export_atlas_g_006_public_rc_graph_reachability_gate_json()
    exported_twice = export_atlas_g_006_public_rc_graph_reachability_gate_json()

    assert exported_once == exported_twice
    assert exported_once == json.dumps(
        json.loads(exported_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def test_phase_1271_required_tokens_are_recorded_everywhere() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    planning = _read(PLANNING_INDEX_PATH)
    roadmap = _read(ROADMAP_PATH)

    for text in (spec, walkthrough, status, planning, roadmap):
        for token in REQUIRED_TOKENS:
            assert token in text

    assert "Window 1265-1272 OPEN / PASS through Phase 1271" in planning
    assert "public_rc_remains_blocked_after_phase_1271" in roadmap
    assert "Phase 1272 - Window 1265-1272 closure gate" in status
    assert "phase_1272_window_1265_1272_closure_gate_requires_explicit_go" in status


def test_phase_1271_fix1_tokens_are_recorded_in_phase_surfaces() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    planning = _read(PLANNING_INDEX_PATH)
    roadmap = _read(ROADMAP_PATH)

    for text in (spec, walkthrough, status, planning, roadmap):
        for token in FIX1_TOKENS:
            assert token in text

    gate = build_atlas_g_006_public_rc_graph_reachability_gate()
    assert set(FIX1_TOKENS) <= set(gate["required_tokens"])


def test_phase_1271_records_discovery_non_claims_and_open_blockers() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    for text in (spec, walkthrough):
        assert "Exact-token" in text
        assert "Concept discovery" in text
        assert "Contradiction" in text
        assert "Source expansion" in text
        assert "pass_graph_gate_only_release_artifacts_blocked" in text
        assert "public release artifact" in text
        assert "Genesis Atlas mutation" in text
        assert "v0.2 signing" in text
        assert "public repository publication" in text
        assert "claimability runtime and conversion sweeper implementation" in text
        assert "CDL-087 ratification" in text


def test_phase_1271_graph_delta_is_recorded() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)

    expected = (
        "graph_delta=load_bearing_code_changed:ilc_core/rc/atlas_graph_discipline.py -> hypergraph/public_rc",
        "graph_delta=load_bearing_artifact_changed:docs/specs/ilc_atlas_g_004_005_high_authority_dependency_bridge_1254_v0.1.json -> hypergraph/public_rc",
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md -> hypergraph/public_rc",
        "graph_delta=support_tests_added:tests/test_phase_1271_atlas_g_006_public_rc_graph_reachability_gate.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1271_atlas_g_006_public_rc_graph_reachability_gate_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in spec
        assert graph_delta in walkthrough
        assert graph_delta in status


def test_phase_1271_does_not_mutate_cdl_or_genesis_release_authority() -> None:
    cdl_register = _read(CDL_REGISTER_PATH)
    spec = _read(SPEC_PATH)

    assert "phase_1271" not in cdl_register
    assert "no_genesis_atlas_mutation_phase_1271" in spec
    assert "public_release_artifact_not_authorized_phase_1271" in spec
    assert "Release artifact production remains unauthorized" in spec
