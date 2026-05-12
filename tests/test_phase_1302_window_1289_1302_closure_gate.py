from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

HANDOFF = "docs/specs/ilc_window_1289_1302_handoff_1302_v0.1.md"
PROMPT = "docs/antigravity_tasks/antigravity_prompt__phase_1302_g8_window_1289_1302_closure_gate.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = "docs/phases/phase_1302_window_1289_1302_closure_gate_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "window_1289_1302_closed_phase_1302",
    "window_1289_1302_closure_gate_verdict=pass_or_blocked_with_carry_forward",
    "phase_1302_window_1289_1302_closure_complete",
    "window_1303_plus_sequence_lock_required_before_next_phase_assignment",
    "public_rc_exclude_helper_stripping_carried_forward_to_window_1303_plus",
    "public_rc_remains_blocked_after_phase_1302",
)

PHASE_LEDGER_TOKENS = (
    "window_1289_1302_sequence_lock_committed",
    "context_capsule_v5_52_frontier_refresh_phase_1290.v0.1",
    "public_claimability_verifier_contract_preflight_phase_1291.v0.1",
    "claimability_package_profile_allowlist_rehearsal_phase_1292.v0.1",
    "public_rc_exclude_helper_promotion_removal_register_phase_1293.v0.1",
    "claimability_package_allowlist_rehearsal_phase_1294.v0.1",
    "transport_principal_lifecycle_revocation_replay_preflight_phase_1295.v0.1",
    "hostile_network_admission_ban_rate_privacy_plan_phase_1296.v0.1",
    "sidecar_public_safe_projection_schema_phase_1297.v0.1",
    "sidecar_bind_listener_peer_discovery_authority_preflight_phase_1298.v0.1",
    "release_allowlist_artifact_genesis_readiness_preflight_phase_1299.v0.1",
    "counsel_ip_publication_clearance_inventory_phase_1300.v0.1",
    "deep_no_activation_assertion_audit_phase_1301.v0.1",
)

BLOCKER_PHRASES = (
    "legacy_public_labeled_fastapi_routes_carry_forward_phase_1301",
    "legacy_public_labeled_fastapi_routes_not_public_rc_clean_phase_1301",
    "Final public claimability verifier/API authority",
    "`PUBLIC_RC_EXCLUDE` helper replacement, stripping",
    "Rust public P2P integration",
    "privacy filter implementation/review",
    "source allowlist export execution",
    "release artifact production",
    "release-key generation",
    "release envelope production",
    "Genesis Atlas mutation/regeneration/signing",
    "v0.2 signing",
    "CDL-088 opening",
    "wallet withdrawal",
    "ECU minting",
    "ILC settlement",
)

NON_AUTHORIZATION_PHRASES = (
    "source allowlist export execution",
    "materialized export manifest production",
    "public repository publication",
    "public package publication",
    "release artifact production",
    "release-key generation",
    "release envelope production",
    "release signing material generation",
    "helper promotion",
    "marker removal",
    "helper stripping",
    "public claimability activation",
    "public verifier service activation",
    "public P2P exposure",
    "public fetch serving activation",
    "public sidecar/projection serving",
    "non-loopback sidecar bind",
    "public listener",
    "peer discovery",
    "TransportPrincipal public-path activation",
    "CDL mutation",
    "CDL-088 opening",
    "Genesis Atlas mutation",
    "Genesis Atlas signing",
    "v0.2 signing",
    "wallet withdrawal",
    "wallet transfer",
    "wallet spend",
    "ECU minting",
    "ILC settlement",
)

GRAPH_DELTAS = (
    "graph_delta=support_only:docs/specs/ilc_window_1289_1302_handoff_1302_v0.1.md -> planning/frontier",
    "graph_delta=support_tests_added:tests/test_phase_1302_window_1289_1302_closure_gate.py -> validation",
    "graph_delta=support_only:docs/phases/phase_1302_window_1289_1302_closure_gate_walkthrough.md -> planning/frontier",
    "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
    "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier",
    "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1302_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(HANDOFF)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)
        assert token in read(CAPSULE)
        assert token in read(ROADMAP)


def test_phase_1302_closes_window_and_routes_next_sequence_lock() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)
    status = read(STATUS)

    assert "Window 1289-1302 is CLOSED / PASS through Phase 1302" in planning
    assert "Window 1289-1302 is closed through Phase 1302" in capsule
    assert "Window 1289-1302 CLOSED / PASS through Phase 1302" in roadmap
    assert "## Phase 1302" in status
    assert "Window 1303+ sequence lock is required before assigning further phases" in status
    assert "Phase 1303" in planning


def test_phase_1302_phase_ledger_covers_1289_through_1302() -> None:
    handoff = read(HANDOFF)
    walkthrough = read(WALKTHROUGH)

    for phase in range(1289, 1303):
        assert f"| {phase} |" in handoff
        assert f"| {phase} |" in walkthrough

    for token in PHASE_LEDGER_TOKENS:
        assert token in handoff
        assert token in walkthrough


def test_phase_1302_carry_forward_blockers_are_explicit() -> None:
    for text in (read(HANDOFF), read(WALKTHROUGH), read(PLANNING), read(CAPSULE), read(ROADMAP)):
        for phrase in BLOCKER_PHRASES:
            assert phrase in text


def test_phase_1302_records_no_activation_boundary() -> None:
    for path in (HANDOFF, WALKTHROUGH, STATUS):
        compact = " ".join(read(path).split())
        for phrase in NON_AUTHORIZATION_PHRASES:
            assert phrase in compact


def test_phase_1302_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    cdl = read(CDL_REGISTER)
    handoff = read(HANDOFF)

    assert "window_1289_1302_closed_phase_1302" not in cdl
    assert "| CDL-088 |" not in cdl
    assert "CDL mutation" in handoff
    assert "CDL-088 opening" in handoff


def test_phase_1302_graph_delta_is_recorded() -> None:
    for text in (read(HANDOFF), read(WALKTHROUGH), read(STATUS)):
        for graph_delta in GRAPH_DELTAS:
            assert graph_delta in text
