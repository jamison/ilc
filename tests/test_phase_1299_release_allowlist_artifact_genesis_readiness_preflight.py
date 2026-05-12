from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_release_allowlist_artifact_genesis_readiness_preflight_1299_v0.1.md"
PROMPT = (
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1299_g8_release_allowlist_artifact_genesis_readiness_preflight.md"
)
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = (
    "docs/phases/"
    "phase_1299_release_allowlist_artifact_genesis_readiness_preflight_walkthrough.md"
)
ALLOWLIST = "docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md"
MANIFEST_SCHEMA = "docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md"
PREPUBLICATION = (
    "docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md"
)
PUBLICATION_PREFLIGHT = (
    "docs/specs/ilc_release_publication_signing_authorization_preflight_1287_v0.1.md"
)
ATLAS_G_006 = "docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md"
ATLAS_PLANNING = (
    "docs/specs/ilc_atlas_graph_integrated_phase_discipline_forward_planning_1241_v0.1.md"
)
PACKAGING_GATE = "docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md"
FORWARD_WINDOWS = (
    "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
)
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "release_allowlist_artifact_genesis_readiness_preflight_phase_1299.v0.1",
    "release_readiness_verdict_phase_1299=preflight_only_no_artifacts",
    "source_allowlist_export_not_executed_phase_1299",
    "release_artifact_not_produced_phase_1299",
    "release_keys_not_generated_phase_1299",
    "release_envelope_not_produced_phase_1299",
    "genesis_atlas_not_mutated_or_signed_phase_1299",
    "v0_2_signing_not_authorized_phase_1299",
    "public_rc_exclude_helper_stripping_deferred_to_package_materialization_after_phase_1299",
    "public_rc_remains_blocked_after_phase_1299",
    "phase_1300_counsel_ip_publication_clearance_inventory_next",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1299_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SPEC)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)

    for token in REQUIRED_TOKENS[:10]:
        assert token in read(CAPSULE)
        assert token in read(ROADMAP)


def test_phase_1299_binds_release_allowlist_artifact_and_atlas_sources() -> None:
    spec = read(SPEC)
    allowlist = read(ALLOWLIST)
    manifest_schema = read(MANIFEST_SCHEMA)
    prepublication = read(PREPUBLICATION)
    publication_preflight = read(PUBLICATION_PREFLIGHT)
    atlas = read(ATLAS_G_006)
    atlas_planning = read(ATLAS_PLANNING)
    packaging_gate = read(PACKAGING_GATE)
    forward_windows = read(FORWARD_WINDOWS)

    for phrase in (
        "allowlist_export_procedure_defined_phase_1255",
        "release_artifact_manifest_schema_committed_phase_1213",
        "release_manifest_allowlist_publication_preflight_phase_1279.v0.1",
        "release_publication_signing_authorization_preflight_phase_1287.v0.1",
        "atlas_g_006_public_rc_graph_reachability_gate_phase_1271.v0.1",
        "atlas_g_007_unsigned_v0_2_plus_candidate_regeneration_required",
        "public_rc_packaging_gate_sequence_implementation_then_dry_run_then_execution",
    ):
        assert phrase in spec

    assert "source_allowlist_export_materialization_must_fail_on_public_rc_exclude_markers" in allowlist
    assert "release_artifact_packet_must_reference_clean_export_gate" in manifest_schema
    assert "source_allowlist_prepublication_verdict_phase_1279=procedure_defined_execution_blocked" in prepublication
    assert "release_publication_signing_verdict_phase_1287=preflight_only_no_publication_no_signing" in publication_preflight
    assert "graph_reachability_verdict=pass_graph_gate_only_release_artifacts_blocked" in atlas
    assert "atlas_g_007_unsigned_v0_2_plus_candidate_regeneration_required" in atlas_planning
    assert "public_rc_package_export_must_be_public_tree_clean_not_flag_flip" in packaging_gate
    assert "public_rc_exclude_helper_stripping_routed_to_phase_1308_1319_1333" in forward_windows


def test_phase_1299_records_no_export_artifact_keys_envelope_or_signing() -> None:
    for path in (SPEC, WALKTHROUGH, STATUS):
        text = read(path)
        for phrase in (
            "source allowlist export execution",
            "materialized export manifest production",
            "public repository publication",
            "public package publication",
            "release artifact production",
            "release artifact manifest instance production",
            "release-key generation",
            "release envelope production",
            "Genesis Atlas mutation",
            "Genesis Atlas regeneration",
            "Genesis Atlas signing",
            "v0.2 signing",
            "public RC claim",
            "helper promotion",
            "marker removal",
            "helper stripping",
            "CDL mutation",
            "CDL-088 opening",
            "IP filing",
            "paper publication",
            "wallet withdrawal",
            "wallet transfer",
            "wallet spend",
            "ECU minting",
            "ILC settlement",
        ):
            assert phrase in text

        for token in REQUIRED_TOKENS[1:10]:
            assert token in text


def test_phase_1299_frontier_docs_advance_to_1300_without_release_authority() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)
    status = read(STATUS)

    assert "Window 1289-1302 is OPEN through Phase 1299" in planning
    assert "Window 1289-1302 is open through Phase 1299" in capsule
    assert "Window 1289-1302 OPEN through Phase 1299" in roadmap
    assert "Phase 1300 is sensitive" in planning
    assert "Phase 1300 is sensitive" in capsule
    assert "Phase 1300 is the next sensitive phase" in roadmap
    assert "## Phase 1299" in status
    assert "Phase 1300 - Counsel, IP, publication clearance inventory" in status


def test_phase_1299_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    cdl = read(CDL_REGISTER)
    spec = read(SPEC)

    assert "release_allowlist_artifact_genesis_readiness_preflight_phase_1299.v0.1" not in cdl
    assert "| CDL-088 |" not in cdl
    assert "CDL mutation" in spec
    assert "CDL-088 opening" in spec


def test_phase_1299_graph_delta_is_recorded() -> None:
    expected = (
        "graph_delta=support_only:docs/specs/ilc_release_allowlist_artifact_genesis_readiness_preflight_1299_v0.1.md -> release/publication",
        "graph_delta=support_tests_added:tests/test_phase_1299_release_allowlist_artifact_genesis_readiness_preflight.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1299_release_allowlist_artifact_genesis_readiness_preflight_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    )

    for text in (read(SPEC), read(WALKTHROUGH), read(STATUS)):
        for graph_delta in expected:
            assert graph_delta in text
