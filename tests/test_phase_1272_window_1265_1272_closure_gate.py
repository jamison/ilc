from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


HANDOFF = "docs/specs/ilc_window_1265_1272_handoff_1272_v0.1.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1272_window_1265_1272_closure_gate_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"


REQUIRED_TOKENS = [
    "window_1265_1272_closed_phase_1272",
    "window_1265_1272_closure_gate_verdict=pass",
    "phase_1272_window_1265_1272_closure_complete",
    "window_1273_plus_sequence_lock_required_before_next_phase_assignment",
]


def test_phase_1272_required_tokens_are_published() -> None:
    handoff = read(HANDOFF)
    roadmap = read(ROADMAP)
    planning = read(PLANNING)
    status = read(STATUS)
    walkthrough = read(WALKTHROUGH)

    for token in REQUIRED_TOKENS:
        assert token in handoff
        assert token in roadmap
        assert token in planning
        assert token in status
        assert token in walkthrough


def test_handoff_follows_closure_schema_and_mempalace_disposition() -> None:
    handoff = read(HANDOFF)
    required_sections = [
        "## 1. Window identity and closure basis",
        "## 2. Inputs and closure inheritance",
        "## 3. Closure verdict summary",
        "## 4. CDL-087 status at closure",
        "## 5. TransportPrincipal, sidecar, and public-path status",
        "## 6. Werner status and economic boundary",
        "## 7. Gap 13, claimability, and conversion-sweeper status",
        "## 8. ATLAS-G-006 and release-artifact status",
        "## 9. Carry-forward items and residual blockers",
        "## 10. Next-window entry criteria and routing",
        "## 11. MemPalace refresh disposition",
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
        "| 1265 | Sequence lock | Closed.",
        "| 1266 | CDL-087 sensitive ratification review | Closed",
        "| 1267 | TransportPrincipal pre-public runtime identity | Closed",
        "| 1268 | Sidecar loopback projection endpoint boundary | Closed",
        "| 1269 | Werner default topology-pressure profile | Closed",
        "| 1270 | Gap 13 claimability conversion-sweeper preflight | Closed",
        "| 1271 | ATLAS-G-006 public-RC graph reachability gate | Closed",
        "| 1271 Fix1 | ATLAS-G-006 manifest/profile consistency hardening | Closed",
        "| 1272 | Closure gate | Passed.",
    ]
    for row in expected_phase_rows:
        assert row in handoff


def test_cdl087_handoff_records_historical_open_before_later_fix1() -> None:
    handoff = read(HANDOFF)
    cdl_register = read(CDL_REGISTER)

    required_tokens = [
        "cdl_087_sensitive_ratification_review_phase_1266.v0.1",
        "cdl_087_ratification_decision_phase_1266=no_ratification_no_register_mutation",
        "cdl_087_ratification_not_executed_by_default_phase_1266",
        "cdl_087_register_mutation_requires_explicit_ratification_authorization_phase_1266",
        "no_public_fetch_serving_enabled_phase_1266",
        "OPEN / PRELOCKED / NOT RATIFIED",
    ]
    for token in required_tokens:
        assert token in handoff

    assert "| CDL-087 |" in cdl_register
    assert "| ratified |" in cdl_register
    assert "ratified_phase: 1278 Fix1" in cdl_register
    assert "window_1265_1272_closed_phase_1272" not in cdl_register


def test_public_path_claimability_and_release_boundaries_remain_blocked() -> None:
    handoff = read(HANDOFF)
    roadmap = read(ROADMAP)

    required_boundaries = [
        "transport_principal_runtime_not_public_p2p_activation_phase_1267",
        "requester_id_rate_limit_fallback_still_forbidden_phase_1267",
        "sidecar_loopback_only_no_non_loopback_serving_phase_1268",
        "sidecar_public_path_still_blocked_phase_1268",
        "no_werner_ecu_minting_or_ilc_settlement_phase_1269",
        "direct_werner_ecu_creation_rejected_phase_1263",
        "public_claimability_runtime_not_activated_phase_1270",
        "wallet_withdrawal_transfer_spend_not_enabled_phase_1270",
        "public_release_artifact_not_authorized_phase_1271",
        "no_genesis_atlas_mutation_phase_1271",
        "atlas_g_006_manifest_profile_mismatch",
        "public_rc_remains_blocked_after_phase_1272",
    ]
    for token in required_boundaries:
        assert token in handoff

    assert "Public RC remains blocked after Phase 1272" in roadmap
    assert "public_rc_remains_blocked_after_phase_1272" in roadmap


def test_planning_index_marks_window_closed_and_requires_new_sequence_lock() -> None:
    planning = read(PLANNING)

    assert "Window 1265-1272 CLOSED / PASS through Phase 1272" in planning
    assert HANDOFF in planning
    assert "Window 1273-1280 CLOSED / PASS through Phase 1280" in planning
    assert "window_1281_plus_sequence_lock_required_before_next_phase_assignment" in planning
    assert "release_manifest_allowlist_publication_preflight_phase_1279.v0.1" in planning
    assert "Exact-token `rg` is only a schema/completion check" in planning


def test_roadmap_baseline_and_addendum_record_phase_1272_closure() -> None:
    roadmap = read(ROADMAP)

    assert "Window 1273-1280 CLOSED / PASS through Phase 1280" in roadmap
    assert HANDOFF in roadmap
    assert "## 18. Phase 1272 Window 1265-1272 Closure Addendum" in roadmap
    assert "ATLAS-G-006 is no longer the selected-profile graph reachability blocker" in roadmap
    assert "cdl087_ratified_phase_1278_fix1" in roadmap


def test_phase_1272_graph_delta_is_recorded() -> None:
    handoff = read(HANDOFF)
    walkthrough = read(WALKTHROUGH)

    expected_graph_deltas = (
        "graph_delta=support_only:docs/specs/ilc_window_1265_1272_handoff_1272_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/phase_1272_window_1265_1272_closure_gate_walkthrough.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1272_window_1265_1272_closure_gate.py -> validation",
    )
    for graph_delta in expected_graph_deltas:
        assert graph_delta in handoff
        assert graph_delta in walkthrough
