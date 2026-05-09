from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


HANDOFF = "docs/specs/ilc_window_1281_1288_handoff_1288_v0.1.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1288_window_1281_1288_closure_gate_walkthrough.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.51.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"


REQUIRED_TOKENS = [
    "window_1281_1288_closed_phase_1288",
    "window_1281_1288_closure_gate_verdict=pass",
    "phase_1288_window_1281_1288_closure_complete",
    "window_1289_plus_sequence_lock_required_before_next_phase_assignment",
    "public_rc_remains_blocked_after_phase_1288",
]


def test_phase_1288_required_tokens_are_published() -> None:
    texts = (
        read(HANDOFF),
        read(ROADMAP),
        read(PLANNING),
        read(STATUS),
        read(WALKTHROUGH),
        read(CAPSULE),
    )

    for text in texts:
        for token in REQUIRED_TOKENS:
            assert token in text


def test_handoff_follows_closure_schema_and_mempalace_disposition() -> None:
    handoff = read(HANDOFF)
    required_sections = [
        "## 1. Window identity and closure basis",
        "## 2. Canon checks and token audit",
        "## 3. Inputs and closure inheritance",
        "## 4. Closure verdict summary",
        "## 5. Public claimability and verifier/API status",
        "## 6. TransportPrincipal, sidecar, and public-path status",
        "## 7. Release, publication, and signing status",
        "## 8. Public-RC blocker classification",
        "## 9. Exit criteria reconciliation",
        "## 10. Carry-forward items and residual blockers",
        "## 11. Next-window entry criteria and routing",
        "## 12. MemPalace refresh disposition",
        "## 13. Non-authorization boundary",
        "## 14. Graph delta",
    ]
    positions = [handoff.index(section) for section in required_sections]
    assert positions == sorted(positions)

    assert "Status: handoff artifact" in handoff
    assert "Classification: closure and carry-forward handoff" in handoff
    assert "Closure verdict: pass" in handoff
    assert "Disposition: required" in handoff
    assert "Active working set impacted: yes" in handoff
    assert "bash tools/mempalace/build_active_working_set.sh" in handoff


def test_all_window_phases_are_mapped_to_closure_status() -> None:
    handoff = read(HANDOFF)
    expected_phase_rows = [
        "| 1281 | Sequence lock | Closed.",
        "| 1282 | Context Capsule v5.51 frontier refresh | Closed.",
        "| 1282 Fix1 | Claimability runtime audit hardening | Closed",
        "| 1283 | Public claimability authority decision preflight | Closed",
        "| 1284 | Claimability verifier/API boundary preflight | Closed",
        "| 1285 | TransportPrincipal public-path activation preflight | Closed",
        "| 1286 | Sidecar public projection privacy/serving preflight | Closed",
        "| 1287 | Release publication/signing authorization preflight | Closed",
        "| 1288 | Closure gate | Passed.",
    ]
    for row in expected_phase_rows:
        assert row in handoff


def test_closure_preserves_no_public_claimability_or_api_authority() -> None:
    handoff = read(HANDOFF)

    for token in (
        "public_claimability_authority_decision_preflight_phase_1283.v0.1",
        "public_claimability_activation_requires_explicit_human_authorization_phase_1283",
        "public_claimability_activation_not_authorized_by_default_phase_1283",
        "wallet_withdrawal_transfer_spend_still_blocked_phase_1283",
        "public_claimability_authority_verdict_phase_1283=no_activation_no_public_api",
        "public_claimability_verifier_api_boundary_preflight_phase_1284.v0.1",
        "claimability_api_public_serving_not_enabled_phase_1284",
        "claimability_verifier_authority_not_activated_phase_1284",
        "public_claimability_verifier_api_boundary_verdict_phase_1284=internal_boundary_only_no_public_api",
    ):
        assert token in handoff


def test_closure_preserves_transport_sidecar_and_release_blocks() -> None:
    handoff = read(HANDOFF)

    for token in (
        "transport_principal_public_path_activation_verdict_phase_1285=preflight_only_no_public_path_activation",
        "transport_principal_public_path_authority_not_activated_phase_1285",
        "sidecar_public_projection_privacy_serving_verdict_phase_1286=preflight_only_no_public_serving",
        "no_new_public_listener_phase_1286",
        "peer_discovery_not_enabled_phase_1286",
        "release_publication_signing_verdict_phase_1287=preflight_only_no_publication_no_signing",
        "public_repository_publication_not_authorized_phase_1287",
        "release_artifact_production_not_authorized_phase_1287",
        "source_allowlist_export_not_executed_phase_1287",
        "release_keys_not_generated_phase_1287",
        "release_envelope_not_produced_phase_1287",
        "v0_2_signing_not_authorized_phase_1287",
        "genesis_atlas_mutation_not_authorized_phase_1287",
        "public_rc_claim_not_authorized_phase_1287",
    ):
        assert token in handoff


def test_planning_capsule_and_roadmap_mark_window_closed() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)

    assert "Window 1281-1288 CLOSED / PASS through Phase 1288" in planning
    assert "Window 1281-1288 closed with pass verdict through Phase 1288" in capsule
    assert "Window frontier | Window 1281-1288 CLOSED / PASS through Phase 1288" in roadmap
    assert HANDOFF in planning
    assert HANDOFF in roadmap
    assert "Window 1289+ sequence lock required" in planning
    assert "window_1289_plus_sequence_lock_required_before_next_phase_assignment" in planning


def test_no_cdl_mutation_or_cdl088_opening_from_phase_1288() -> None:
    cdl_register = read(CDL_REGISTER)

    assert "window_1281_1288_closed_phase_1288" not in cdl_register
    assert "phase_1288_window_1281_1288_closure_complete" not in cdl_register
    assert "| CDL-087 |" in cdl_register
    assert "| ratified |" in cdl_register
    assert "| CDL-088 |" not in cdl_register


def test_phase_1288_graph_delta_is_recorded() -> None:
    handoff = read(HANDOFF)
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)

    expected_graph_deltas = (
        "graph_delta=support_only:docs/specs/ilc_window_1281_1288_handoff_1288_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/phase_1288_window_1281_1288_closure_gate_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1288_window_1281_1288_closure_gate.py -> validation",
        "graph_delta=support_tests_changed:tests/test_phase_1287_release_publication_signing_authorization_preflight.py -> validation/frontier",
    )
    for graph_delta in expected_graph_deltas:
        assert graph_delta in handoff
        assert graph_delta in walkthrough
        assert graph_delta in status
