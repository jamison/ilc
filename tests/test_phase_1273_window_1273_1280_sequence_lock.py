from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SEQUENCE_LOCK = "docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1273_1280_candidate_phase_grouping_v0.1.md"
AUDIT = "docs/specs/ilc_window_1273_1280_prompt_package_outside_audit_2026_05_09_v0.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1273_window_1273_1280_sequence_lock_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "window_1273_1280_sequence_lock_committed",
    "window_1273_1280_sequence_lock_verdict=pass",
    "phase_1274_cdl048_conversion_sweeper_runtime_requires_explicit_go",
    "window_1273_1280_no_public_rc_or_public_claimability_activation",
    "human_question_escalation_required_for_uncertain_authority",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1273_sequence_lock_required_tokens_are_published() -> None:
    lock = read(SEQUENCE_LOCK)
    planning = read(PLANNING)
    status = read(STATUS)
    walkthrough = read(WALKTHROUGH)

    for token in REQUIRED_TOKENS:
        assert token in lock
        assert token in planning
        assert token in status
        assert token in walkthrough


def test_phase_1273_sequence_lock_consumes_guidance_audit_and_current_canon() -> None:
    lock = read(SEQUENCE_LOCK)

    expected_inputs = (
        "docs/specs/ilc_antigravity_context_capsule_v5.50.md",
        "docs/specs/ilc_window_1265_1272_handoff_1272_v0.1.md",
        "docs/specs/ilc_phase_1265_1272_sequence_lock_v0.1.md",
        GUIDANCE,
        AUDIT,
        "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md",
        "docs/specs/ilc_constitutional_decision_log_v0.1.md",
        "docs/specs/ilc_cdl_087_sensitive_ratification_review_1266_v0.1.md",
        "docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md",
        "docs/specs/ilc_sidecar_loopback_projection_endpoint_boundary_1268_v0.1.md",
        "docs/specs/ilc_werner_default_topology_pressure_profile_1269_v0.1.md",
        "docs/specs/ilc_gap13_claimability_conversion_sweeper_preflight_1270_v0.1.md",
        "docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md",
        "docs/phases/phase_1271_fix1_atlas_g_006_manifest_profile_consistency_hardening_walkthrough.md",
        "ilc_core/protocol/public_wallet_runtime.py",
        "ilc_core/protocol/public_receipt_runtime.py",
        "ilc_core/rc/atlas_graph_discipline.py",
        "ilc_core/graph/sidecar_query_runtime.py",
    )
    for source in expected_inputs:
        assert source in lock

    assert "window_1265_1272_closed_phase_1272" in lock
    assert "public_rc_remains_blocked_after_phase_1272" in lock
    assert "planning_index_session_start_frontier_hardened_after_audit" in lock
    assert "window_1273_1280_audit_no_authority_expansion" in lock


def test_phase_1273_discovery_discipline_records_broad_search_not_exact_only() -> None:
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


def test_phase_1273_claimability_cdl048_boundary_is_sensitive_and_no_activation() -> None:
    lock = read(SEQUENCE_LOCK)
    cdl_register = read(CDL_REGISTER)

    assert "| CDL-048 |" in cdl_register
    assert "| ratified |" in cdl_register
    assert "ecu_conversion_deadline = 4 issuance epochs" in lock
    assert "public_claimability_runtime_not_activated_phase_1270" in lock
    assert "wallet_withdrawal_transfer_spend_not_enabled_phase_1270" in lock
    assert "The conversion sweeper runtime is not complete" in lock
    assert "Phase 1274 may implement a bounded runtime skeleton only after explicit GO" in lock


def test_phase_1273_cdl087_fix1_addendum_records_authorized_later_mutation() -> None:
    lock = read(SEQUENCE_LOCK)
    cdl_register = read(CDL_REGISTER)

    assert "cdl_087_ratification_not_executed_by_default_phase_1266" in lock
    assert "cdl_087_register_mutation_requires_explicit_ratification_authorization_phase_1266" in lock
    assert "## 6. Phase 1278 Fix1 Ratification Addendum" in lock
    assert "cdl087_ratified_phase_1278_fix1" in lock
    assert "cdl087_register_mutated_phase_1278_fix1" in lock
    assert "| CDL-087 |" in cdl_register
    assert "| ratified |" in cdl_register


def test_phase_1273_locked_order_and_sensitive_gates_are_explicit() -> None:
    lock = read(SEQUENCE_LOCK)

    expected_rows = (
        "| 1 | 1273 | Window 1273-1280 sequence lock | **SENSITIVE** |",
        "| 2 | 1274 | CDL-048 conversion-sweeper runtime skeleton and exact ECU lot ledger boundary | **SENSITIVE** |",
        "| 3 | 1275 | Public claimability proof-binding runtime boundary | **SENSITIVE** |",
        "| 4 | 1276 | CDL-087 ratification authorization preflight / decision packet | **SENSITIVE** |",
        "| 5 | 1277 | TransportPrincipal public-path ADR and runtime integration preflight | **SENSITIVE** |",
        "| 6 | 1278 | Sidecar non-loopback/public projection authorization preflight | **SENSITIVE** |",
        "| 7 | 1279 | Release manifest and source allowlist pre-publication preflight | NON-SENSITIVE only if inventory/procedure docs and validation; no publication, signing, or release artifact production |",
        "| 8 | 1280 | Window coherence, blocker classification, and closure gate | **SENSITIVE** |",
    )
    for row in expected_rows:
        assert row in lock

    for phase in ("GO Phase 1274", "GO Phase 1275", "GO Phase 1276", "GO Phase 1277", "GO Phase 1278", "GO Phase 1280"):
        assert phase in lock

    assert "Because Phase 1274 is sensitive" in lock
    assert "no later non-sensitive phase is executable immediately after Phase 1273" in lock


def test_phase_1273_public_economic_and_release_non_claims_are_preserved() -> None:
    lock = read(SEQUENCE_LOCK)
    for phrase in (
        "public RC claim",
        "public repository publication",
        "public P2P exposure",
        "public fetch serving",
        "public sidecar/projection serving",
        "public claimability activation",
        "wallet withdrawal, wallet transfer, or wallet spend semantics",
        "wallet signing authority or ledger-write authority",
        "CDL mutation beyond the authorized CDL-087 Phase 1278 Fix1 register mutation",
        "Werner CDL opening/prelock, or CDL-088 opening",
        "ECU mint authorization",
        "ILC settlement or withdrawal runtime activation",
        "public release artifact production",
        "v0.2 signing",
        "Genesis Atlas mutation, regeneration, or signing",
    ):
        assert phrase in lock

    assert "graph_reachability_verdict=pass_graph_gate_only_release_artifacts_blocked" in lock
    assert "release manifest/source allowlist work may be prepared only as inventory" in lock


def test_phase_1273_human_escalation_rule_is_embedded() -> None:
    lock = read(SEQUENCE_LOCK)
    assert "If a phase discovers a decision that cannot be resolved from committed canon" in lock
    assert "the phase must stop and prompt the human reviewer" in lock
    assert "Do not silently choose broader authority" in lock
    assert "default_to_no_authorization_when_canon_is_ambiguous" in lock


def test_phase_1273_frontier_updates_planning_and_status() -> None:
    planning = read(PLANNING)
    status = read(STATUS)

    assert "Window 1273-1280 OPEN through Phase 1278 Fix1" in planning
    assert SEQUENCE_LOCK in planning
    assert "Phase 1279 remains the next locked non-sensitive inventory phase" in planning
    assert "Window 1273-1280 sequence lock" in planning
    assert "## Phase 1273" in status
    assert "Phase 1274 - CDL-048 conversion-sweeper runtime skeleton" in status
    assert "requires explicit `GO Phase 1274`" in status


def test_phase_1273_graph_delta_is_recorded() -> None:
    lock = read(SEQUENCE_LOCK)
    walkthrough = read(WALKTHROUGH)

    expected_graph_deltas = (
        "graph_delta=support_only:docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/phase_1273_window_1273_1280_sequence_lock_walkthrough.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1273_window_1273_1280_sequence_lock.py -> validation",
    )
    for graph_delta in expected_graph_deltas:
        assert graph_delta in lock
        assert graph_delta in walkthrough
