from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SEQUENCE_LOCK = "docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1281_1288_candidate_phase_grouping_v0.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1281_window_1281_1288_sequence_lock_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "window_1281_1288_sequence_lock_committed",
    "window_1281_1288_sequence_lock_verdict=pass",
    "phase_1282_context_capsule_v5_51_refresh_next",
    "window_1281_1288_no_public_rc_or_public_activation",
    "human_question_escalation_required_for_uncertain_authority",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1281_sequence_lock_required_tokens_are_published() -> None:
    lock = read(SEQUENCE_LOCK)
    planning = read(PLANNING)
    status = read(STATUS)
    walkthrough = read(WALKTHROUGH)

    for token in REQUIRED_TOKENS:
        assert token in lock
        assert token in planning
        assert token in status
        assert token in walkthrough


def test_phase_1281_sequence_lock_consumes_current_canon_and_guidance() -> None:
    lock = read(SEQUENCE_LOCK)

    expected_inputs = (
        "docs/specs/ilc_antigravity_context_capsule_v5.50.md",
        "docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md",
        "docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md",
        GUIDANCE,
        "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md",
        "docs/specs/ilc_constitutional_decision_log_v0.1.md",
        "docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md",
        "docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md",
        "docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md",
        "docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md",
        "docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md",
        "docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md",
        "docs/specs/ilc_phase_1280_fix1_hypergraph_laplacian_docs_hardening_v0.1.md",
        "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
        "ilc_core/ledger/claimability_proof_binding_runtime.py",
        "ilc_core/network/d2d/transport_principal_public_path_preflight.py",
        "ilc_core/graph/sidecar_public_path_preflight.py",
    )
    for source in expected_inputs:
        assert source in lock

    assert "window_1273_1280_closed_phase_1280" in lock
    assert "public_rc_remains_blocked_after_phase_1280_fix1" in lock
    assert "window_1281_1288_candidate_phase_grouping_recorded_after_phase_1280" in lock


def test_phase_1281_discovery_discipline_records_broad_search_not_exact_only() -> None:
    lock = read(SEQUENCE_LOCK)
    for phrase in (
        "Required-token audit",
        "Concept-discovery search",
        "Contradiction and non-claim search",
        "Source expansion",
        "Exact-token `rg` is a schema/completion check only",
        "token components, synonyms",
        "MemPalace may be used only as advisory retrieval support",
        "unknown_unknown_discovery_required_before_phase_execution",
    ):
        assert phrase in lock


def test_phase_1281_locked_order_and_sensitive_gates_are_explicit() -> None:
    lock = read(SEQUENCE_LOCK)

    expected_rows = (
        "| 1 | 1281 | Window 1281-1288 sequence lock | **SENSITIVE** |",
        "| 2 | 1282 | Context Capsule v5.51 frontier refresh | NON-SENSITIVE docs/canon refresh only |",
        "| 3 | 1283 | Public claimability authority decision preflight | **SENSITIVE** |",
        "| 4 | 1284 | Public claimability verifier/API boundary preflight | **SENSITIVE** |",
        "| 5 | 1285 | TransportPrincipal public-path activation preflight | **SENSITIVE** |",
        "| 6 | 1286 | Sidecar public projection privacy/serving preflight | **SENSITIVE** |",
        "| 7 | 1287 | Release publication and v0.2 signing authorization preflight | **SENSITIVE** |",
        "| 8 | 1288 | Window 1281-1288 closure gate | **SENSITIVE** |",
    )
    for row in expected_rows:
        assert row in lock

    assert "Phase 1282 is non-sensitive" in lock
    assert "Phase 1283 is sensitive" in lock
    assert "no later phase is executable immediately after Phase 1282" in lock


def test_phase_1281_cdl087_state_and_cdl088_non_opening_are_preserved() -> None:
    lock = read(SEQUENCE_LOCK)
    cdl_register = read(CDL_REGISTER)

    assert "| CDL-087 |" in cdl_register
    assert "| ratified |" in cdl_register
    assert "cdl087_ratified_phase_1278_fix1" in lock
    assert "cdl087_register_mutated_phase_1278_fix1" in lock
    assert "cdl087_public_fetch_serving_not_enabled_phase_1278_fix1" in lock
    assert "cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1" in lock
    assert "no_cdl088_opening_phase_1278_fix1" in lock
    assert "CDL mutation or CDL-088 opening" in lock


def test_phase_1281_public_claimability_and_public_path_non_claims_are_preserved() -> None:
    lock = read(SEQUENCE_LOCK)
    for phrase in (
        "conversion_sweeper_no_public_claimability_activation_phase_1274",
        "wallet_withdrawal_transfer_spend_still_blocked_phase_1274",
        "non_loopback_claimability_api_still_blocked_phase_1275",
        "public_claimability_not_activated_phase_1275",
        "transport_principal_public_p2p_not_activated_phase_1277",
        "non_loopback_projection_still_blocked_phase_1277",
        "sidecar_public_serving_not_enabled_phase_1278",
        "no_new_public_listener_phase_1278",
        "public_projection_endpoint_not_enabled_phase_1278",
    ):
        assert phrase in lock

    assert "No public P2P, public fetch serving, non-loopback bind" in lock


def test_phase_1281_release_publication_and_signing_non_claims_are_preserved() -> None:
    lock = read(SEQUENCE_LOCK)
    for phrase in (
        "public_repository_publication_not_authorized_phase_1279",
        "release_artifact_production_not_authorized_phase_1279",
        "v0_2_signing_not_authorized_phase_1279",
        "source_allowlist_export_not_executed_phase_1279",
        "release_keys_not_generated_phase_1279",
        "release_envelope_not_produced_phase_1279",
        "genesis_atlas_mutation_not_authorized_phase_1279",
        "Source publication",
        "v0.2 signing remain blocked until explicit authority exists",
    ):
        assert phrase in lock


def test_phase_1281_human_escalation_rule_is_embedded() -> None:
    lock = read(SEQUENCE_LOCK)
    assert "If a phase discovers a decision that cannot be resolved from committed canon" in lock
    assert "the phase must stop and prompt the human reviewer" in lock
    assert "Do not silently choose broader authority" in lock
    assert "default_to_no_authorization_when_canon_is_ambiguous" in lock


def test_phase_1281_frontier_updates_planning_and_status() -> None:
    planning = read(PLANNING)
    status = read(STATUS)

    assert "Window 1281-1288 is OPEN through Phase 1282 Fix1" in planning
    assert SEQUENCE_LOCK in planning
    assert "## Phase 1281" in status
    assert "Phase 1282 - Context Capsule v5.51 frontier refresh" in status
    assert "Phase 1283 is sensitive" in status


def test_phase_1281_graph_delta_is_recorded() -> None:
    lock = read(SEQUENCE_LOCK)
    walkthrough = read(WALKTHROUGH)

    expected_graph_deltas = (
        "graph_delta=support_only:docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/phase_1281_window_1281_1288_sequence_lock_walkthrough.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1281_window_1281_1288_sequence_lock.py -> validation",
        "graph_delta=support_tests_changed:tests/test_window_1281_1288_prompt_drafts.py -> validation/frontier",
    )
    for graph_delta in expected_graph_deltas:
        assert graph_delta in lock
        assert graph_delta in walkthrough
