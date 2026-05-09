from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


HANDOFF = "docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1280_window_1273_1280_closure_gate_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"


REQUIRED_TOKENS = [
    "window_1273_1280_closed_phase_1280",
    "window_1273_1280_closure_gate_verdict=pass",
    "phase_1280_window_1273_1280_closure_complete",
    "window_1281_plus_sequence_lock_required_before_next_phase_assignment",
    "public_rc_remains_blocked_after_phase_1280",
]


def test_phase_1280_required_tokens_are_published() -> None:
    texts = (
        read(HANDOFF),
        read(ROADMAP),
        read(PLANNING),
        read(STATUS),
        read(WALKTHROUGH),
    )

    for text in texts:
        for token in REQUIRED_TOKENS:
            assert token in text


def test_handoff_follows_closure_schema_and_mempalace_disposition() -> None:
    handoff = read(HANDOFF)
    required_sections = [
        "## 1. Window identity and closure basis",
        "## 2. Inputs and closure inheritance",
        "## 3. Closure verdict summary",
        "## 4. Claimability and CDL-048 status",
        "## 5. CDL-087 status",
        "## 6. TransportPrincipal, sidecar, and public-path status",
        "## 7. Release, publication, and signing status",
        "## 8. Exit criteria reconciliation",
        "## 9. Carry-forward items and residual blockers",
        "## 10. Next-window entry criteria and routing",
        "## 11. MemPalace refresh disposition",
        "## 12. Non-authorization boundary",
        "## 13. Graph delta",
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
        "| 1273 | Sequence lock | Closed.",
        "| 1274 | CDL-048 conversion-sweeper runtime skeleton | Closed",
        "| 1275 | Claimability proof-binding runtime boundary | Closed",
        "| 1276 | CDL-087 authorization preflight | Closed",
        "| 1277 | TransportPrincipal public-path preflight | Closed",
        "| 1278 | Sidecar non-loopback/public projection preflight | Closed",
        "| 1278 Fix1 | CDL-087 ratification | Closed.",
        "| 1279 | Release manifest/source allowlist prepublication | Closed",
        "| 1280 | Closure gate | Passed.",
    ]
    for row in expected_phase_rows:
        assert row in handoff


def test_cdl087_is_ratified_but_public_paths_remain_blocked() -> None:
    handoff = read(HANDOFF)
    cdl_register = read(CDL_REGISTER)

    required_tokens = [
        "cdl087_ratification_evidence_phase_1278_fix1.v0.1",
        "cdl087_ratified_phase_1278_fix1",
        "cdl087_register_mutated_phase_1278_fix1",
        "cdl087_conditions_1_to_6_reproved_phase_1278_fix1",
        "cdl087_public_fetch_serving_not_enabled_phase_1278_fix1",
        "cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1",
        "no_cdl088_opening_phase_1278_fix1",
    ]
    for token in required_tokens:
        assert token in handoff

    assert "| CDL-087 |" in cdl_register
    assert "| ratified |" in cdl_register
    assert "ratified_phase: 1278 Fix1" in cdl_register
    assert "window_1273_1280_closed_phase_1280" not in cdl_register


def test_claimability_release_and_public_activation_boundaries_remain_blocked() -> None:
    handoff = read(HANDOFF)
    roadmap = read(ROADMAP)

    required_boundaries = [
        "conversion_sweeper_no_public_claimability_activation_phase_1274",
        "wallet_withdrawal_transfer_spend_still_blocked_phase_1274",
        "non_loopback_claimability_api_still_blocked_phase_1275",
        "public_claimability_not_activated_phase_1275",
        "transport_principal_public_p2p_not_activated_phase_1277",
        "requester_id_fallback_still_forbidden_phase_1277",
        "non_loopback_projection_still_blocked_phase_1277",
        "sidecar_public_serving_not_enabled_phase_1278",
        "no_new_public_listener_phase_1278",
        "non_loopback_bind_not_enabled_phase_1278",
        "public_projection_endpoint_not_enabled_phase_1278",
        "public_repository_publication_not_authorized_phase_1279",
        "release_artifact_production_not_authorized_phase_1279",
        "v0_2_signing_not_authorized_phase_1279",
        "source_allowlist_export_not_executed_phase_1279",
        "release_keys_not_generated_phase_1279",
        "release_envelope_not_produced_phase_1279",
        "genesis_atlas_mutation_not_authorized_phase_1279",
        "public_rc_remains_blocked_after_phase_1280",
    ]
    for token in required_boundaries:
        assert token in handoff

    assert "Public RC remains blocked after Phase 1280" in roadmap
    assert "public_rc_remains_blocked_after_phase_1280" in roadmap


def test_planning_index_marks_window_closed_and_requires_new_sequence_lock() -> None:
    planning = read(PLANNING)
    session_start = planning.split("## 1. Session-Start Canon", maxsplit=1)[1].split(
        "## 2.", maxsplit=1
    )[0]

    assert "Window 1273-1280 CLOSED / PASS through Phase 1280" in planning
    assert HANDOFF in planning
    assert "window_1281_plus_sequence_lock_required_before_next_phase_assignment" in planning
    assert "Window 1281+ sequence lock required" in planning
    assert "Window 1273-1280 handoff" in session_start
    assert "ilc_window_1273_1280_handoff_1280_v0.1.md" in session_start
    assert "Window 1265-1272 handoff** (closed reference)" in session_start
    assert "Exact-token `rg` is only a schema/completion check" in planning


def test_roadmap_baseline_and_addendum_record_phase_1280_closure() -> None:
    roadmap = read(ROADMAP)

    assert "Window frontier | Window 1273-1280 CLOSED / PASS through Phase 1280" in roadmap
    assert HANDOFF in roadmap
    assert "## 26. Phase 1280 Window 1273-1280 Closure Addendum" in roadmap
    assert "window_1281_plus_sequence_lock_required_before_next_phase_assignment" in roadmap
    assert "Public RC remains blocked after Phase 1280" in roadmap


def test_phase_1280_graph_delta_is_recorded() -> None:
    handoff = read(HANDOFF)
    walkthrough = read(WALKTHROUGH)

    expected_graph_deltas = (
        "graph_delta=support_only:docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/phase_1280_window_1273_1280_closure_gate_walkthrough.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1280_window_1273_1280_closure_gate.py -> validation",
    )
    for graph_delta in expected_graph_deltas:
        assert graph_delta in handoff
        assert graph_delta in walkthrough
