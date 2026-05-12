from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

HANDOFF = "docs/specs/ilc_window_1303_1316_handoff_1316_v0.1.md"
PROMPT = "docs/antigravity_tasks/antigravity_prompt__phase_1316_g8_window_1303_1316_closure_implementation_audit.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = "docs/phases/phase_1316_window_1303_1316_closure_implementation_audit_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "window_1303_1316_closed_phase_1316",
    "window_1303_1316_closure_gate_verdict=pass_or_blocked_with_carry_forward",
    "phase_1316_window_1303_1316_closure_complete",
    "window_1317_plus_sequence_lock_required_before_next_phase_assignment",
    "implementation_hardening_blockers_classified_phase_1316",
    "public_rc_remains_blocked_after_phase_1316",
)

PHASE_LEDGER_TOKENS = (
    "window_1303_1316_sequence_lock_committed",
    "context_capsule_v5_53_frontier_refresh_phase_1304.v0.1",
    "offline_claimability_receipt_verifier_sidecar_phase_1305.v0.1",
    "proof_binding_canonical_hash_negative_path_tests_phase_1306.v0.1",
    "graph_native_sidecar_registry_manifest_phase_1307.v0.1",
    "public_rc_exclude_helper_pruning_replacement_plan_phase_1308.v0.1",
    "transport_principal_admission_sidecar_lifecycle_hardening_phase_1309.v0.1",
    "revocation_replay_admission_ban_tests_phase_1310.v0.1",
    "local_graph_memory_projection_sidecar_phase_1311.v0.1",
    "projection_privacy_field_filtering_tests_phase_1312.v0.1",
    "public_fetch_p2p_activation_candidate_default_off_phase_1313.v0.1",
    "wallet_withdrawal_transfer_spend_semantics_preflight_phase_1314.v0.1",
    "ecu_minting_ilc_settlement_boundary_preflight_phase_1315.v0.1",
)

BLOCKER_PHRASES = (
    "legacy public-labeled FastAPI routes",
    "public claimability verifier/API serving authority",
    "replay/nullifier and duplicate-claim registry policy",
    "PUBLIC_RC_EXCLUDE helper replacement and dry-run export proof",
    "Rust public-P2P substrate ADR/integration gate",
    "TransportPrincipal public-path activation authority",
    "public sidecar/projection serving authority",
    "source allowlist export execution",
    "clean materialized public tree production",
    "release artifact production",
    "release-key generation",
    "Genesis Atlas mutation/regeneration/signing",
    "v0.2 signing authorization",
    "wallet-facing action activation",
    "ECU minting activation",
    "ILC settlement activation",
    "final value-path activation authority",
)

NON_AUTHORIZATION_PHRASES = (
    "public RC claim",
    "source allowlist export execution",
    "public repository publication",
    "public package publication",
    "release artifact production",
    "release-key generation",
    "release envelope production",
    "release signing material",
    "public claimability activation",
    "public verifier service",
    "public claim endpoint",
    "public P2P",
    "public fetch serving",
    "public sidecar/projection serving",
    "non-loopback bind",
    "public listener",
    "peer discovery",
    "helper promotion",
    "marker removal",
    "helper stripping",
    "CDL mutation",
    "CDL-088 opening",
    "Genesis Atlas mutation",
    "v0.2 signing",
    "wallet-facing withdrawal request",
    "wallet-facing transfer request",
    "wallet-facing spend request",
    "wallet-provider signing",
    "wallet-provider ledger-write",
    "ECU minting",
    "ILC settlement",
    "value-path activation",
)

GRAPH_DELTAS = (
    "graph_delta=support_only:docs/specs/ilc_window_1303_1316_handoff_1316_v0.1.md -> planning/frontier",
    "graph_delta=support_tests_added:tests/test_phase_1316_window_1303_1316_closure_implementation_audit.py -> validation",
    "graph_delta=support_only:docs/phases/phase_1316_window_1303_1316_closure_implementation_audit_walkthrough.md -> planning/frontier",
    "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
    "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.53.md -> planning/frontier",
    "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1316_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(HANDOFF)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)
        assert token in read(CAPSULE)
        assert token in read(ROADMAP)


def test_phase_1316_closes_window_and_requires_next_sequence_lock() -> None:
    for path in (HANDOFF, PLANNING, CAPSULE, ROADMAP, STATUS, WALKTHROUGH):
        text = read(path)
        assert "Window 1303-1316 is CLOSED / PASS with carry-forward through Phase 1316" in text
        assert "window_1317_plus_sequence_lock_required_before_next_phase_assignment" in text


def test_phase_1316_phase_ledger_covers_1303_through_1315() -> None:
    handoff = read(HANDOFF)
    walkthrough = read(WALKTHROUGH)

    for phase in range(1303, 1316):
        assert f"| {phase} |" in handoff
        assert f"| {phase} |" in walkthrough

    for token in PHASE_LEDGER_TOKENS:
        assert token in handoff
        assert token in walkthrough


def test_phase_1316_blocker_classification_is_explicit() -> None:
    for path in (HANDOFF, WALKTHROUGH, PLANNING, CAPSULE, ROADMAP):
        text = read(path)
        for phrase in BLOCKER_PHRASES:
            assert phrase in text


def test_phase_1316_records_no_activation_boundary() -> None:
    for path in (HANDOFF, WALKTHROUGH, STATUS):
        compact = " ".join(read(path).split())
        for phrase in NON_AUTHORIZATION_PHRASES:
            assert phrase in compact


def test_phase_1316_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    cdl = read(CDL_REGISTER)
    handoff = read(HANDOFF)

    assert "window_1303_1316_closed_phase_1316" not in cdl
    assert "| CDL-088 |" not in cdl
    assert "CDL mutation" in handoff
    assert "CDL-088 opening" in handoff


def test_phase_1316_graph_delta_is_recorded() -> None:
    for text in (read(HANDOFF), read(WALKTHROUGH), read(STATUS)):
        for graph_delta in GRAPH_DELTAS:
            assert graph_delta in text
