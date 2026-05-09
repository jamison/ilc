from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPEC = ROOT / "docs/specs/ilc_release_publication_signing_authorization_preflight_1287_v0.1.md"
WALKTHROUGH = (
    ROOT
    / "docs/phases/phase_1287_release_publication_signing_authorization_preflight_walkthrough.md"
)
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.51.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "release_publication_signing_authorization_preflight_phase_1287.v0.1",
    "public_repository_publication_not_authorized_phase_1287",
    "release_artifact_production_not_authorized_phase_1287",
    "source_allowlist_export_not_executed_phase_1287",
    "release_keys_not_generated_phase_1287",
    "release_envelope_not_produced_phase_1287",
    "v0_2_signing_not_authorized_phase_1287",
    "genesis_atlas_mutation_not_authorized_phase_1287",
)

CARRY_FORWARD_TOKENS = (
    "release_publication_signing_verdict_phase_1287=preflight_only_no_publication_no_signing",
    "public_package_publication_not_authorized_phase_1287",
    "public_rc_claim_not_authorized_phase_1287",
    "genesis_atlas_signing_not_authorized_phase_1287",
    "phase_1288_window_1281_1288_closure_gate_next",
    "public_rc_remains_blocked_after_phase_1287",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1287_required_tokens_are_published_across_frontier_docs() -> None:
    for path in (SPEC, WALKTHROUGH, PLANNING, STATUS, ROADMAP, CAPSULE):
        text = read(path)
        for token in REQUIRED_TOKENS + CARRY_FORWARD_TOKENS:
            assert token in text


def test_phase_1287_records_discovery_discipline_and_source_expansion() -> None:
    for path in (SPEC, WALKTHROUGH):
        text = read(path)
        for phrase in (
            "§0a Known-token audit",
            "§0b Concept-discovery search",
            "§0c Contradiction and non-claim search",
            "§0d Source expansion and newly discovered tokens",
            "Exact-token `rg`",
        ):
            assert phrase in text

    spec = read(SPEC)
    for source in (
        "docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md",
        "docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md",
        "docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md",
        "docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md",
        "docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md",
        "docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md",
        "docs/specs/ilc_constitutional_decision_log_v0.1.md",
    ):
        assert source in spec


def test_phase_1287_preserves_no_publication_or_signing_authority() -> None:
    spec = read(SPEC)

    assert "release_publication_signing_verdict_phase_1287=preflight_only_no_publication_no_signing" in spec
    assert "No publication or signing authority is activated" in spec
    assert "No source allowlist export is executed" in spec
    assert "No release artifact manifest instance is produced" in spec
    assert "No release keys or release envelopes are generated" in spec
    assert "No Genesis Atlas mutation, regeneration, or signing is authorized" in spec
    assert "No v0.2 signing is authorized" in spec
    assert "No public RC claim is authorized" in spec


def test_phase_1287_records_counsel_publication_and_signing_gates() -> None:
    spec = read(SPEC)

    for phrase in (
        "Counsel-approved license instruments",
        "CLA or explicit no-external-contributor policy",
        "Trademark and fork-labeling policy",
        "Patent/publication review",
        "Source allowlist export",
        "Public repository publication",
        "Public package publication",
        "Release artifact production",
        "Release-key generation",
        "Release-envelope production",
        "Genesis Atlas mutation/regeneration/signing",
        "v0.2 signing",
        "Public RC claim",
    ):
        assert phrase in spec


def test_phase_1287_frontier_routes_to_phase_1288_closure() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    status = read(STATUS)

    assert "Window 1281-1288 is OPEN through Phase 1287" in planning
    assert "Window 1281-1288 is open through Phase 1287" in capsule
    assert "## Phase 1287" in status
    assert "phase_1288_window_1281_1288_closure_gate_next" in planning
    assert "public_rc_remains_blocked_after_phase_1287" in planning


def test_phase_1287_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    register = read(CDL_REGISTER)

    assert "release_publication_signing_authorization_preflight_phase_1287.v0.1" not in register
    assert "| CDL-087 |" in register
    assert "| ratified |" in register
    assert "| CDL-088 |" not in register


def test_phase_1287_graph_delta_is_recorded() -> None:
    expected = (
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_release_publication_signing_authorization_preflight_1287_v0.1.md -> release/publication",
        "graph_delta=support_tests_added:tests/test_phase_1287_release_publication_signing_authorization_preflight.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1287_release_publication_signing_authorization_preflight_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in read(SPEC)
        assert graph_delta in read(WALKTHROUGH)
        assert graph_delta in read(STATUS)
