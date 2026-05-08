from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


HANDOFF = "docs/specs/ilc_window_1257_1264_handoff_1264_v0.1.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1264_window_1257_1264_closure_gate_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"


REQUIRED_TOKENS = [
    "window_1257_1264_closed_phase_1264",
    "window_1257_1264_closure_gate_verdict=pass",
    "phase_1264_window_1257_1264_closure_complete",
    "window_1265_plus_sequence_lock_required_before_next_phase_assignment",
]


def test_phase_1264_required_tokens_are_published() -> None:
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
        "## 4. CDL-087 condition status at closure",
        "## 5. Sidecar, TransportPrincipal, and public-path status",
        "## 6. Werner status and direct ECU rejection",
        "## 7. Carry-forward items and residual blockers",
        "## 8. Next-window entry criteria and routing",
        "## 9. MemPalace refresh disposition",
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
        "| 1257 | Sequence lock | Closed.",
        "| 1258 | CDL-087 production-candidate evidence readiness | Closed",
        "| 1259 | CDL-087 serving-peer evidence slice | Closed",
        "| 1260 | CDL-087 observability and limiter regression | Closed",
        "| 1261 | Sidecar projection endpoint boundary | Closed",
        "| 1262 | Werner overlay validation | Closed",
        "| 1263 | Werner flow-governor CDL decision | Closed",
        "| 1264 | Closure gate | Passed.",
    ]
    for row in expected_phase_rows:
        assert row in handoff


def test_cdl087_conditions_are_classified_without_ratification() -> None:
    handoff = read(HANDOFF)
    cdl_register = read(CDL_REGISTER)

    required_condition_tokens = [
        "condition_1_sim_fetch_01_passed_for_governance_review",
        "condition_2_production_candidate_tier_classification_local_evidence_recorded_phase_1259",
        "condition_3_bootstrap_snapshot_builder_verifier_local_evidence_recorded_phase_1259",
        "condition_4_observability_collection_window_local_evidence_recorded_phase_1260",
        "condition_5_cdl077_limiter_regression_recorded_phase_1260",
        "condition_6_fetch_incentive_projection_resolved_at_projection_level",
        "cdl_087_ratification_readiness_verdict_phase_1260=ready_for_later_sensitive_ratification_review",
        "no_cdl_087_ratification_phase_1260",
    ]
    for token in required_condition_tokens:
        assert token in handoff

    assert "| CDL-087 |" in cdl_register
    assert "| open |" in cdl_register
    assert "window_1257_1264_closed_phase_1264" not in cdl_register


def test_public_path_and_werner_boundaries_remain_blocked() -> None:
    handoff = read(HANDOFF)
    planning = read(PLANNING)
    roadmap = read(ROADMAP)

    required_boundaries = [
        "sidecar_projection_endpoint_authorization_verdict_phase_1261=blocked_public_path",
        "sidecar_projection_endpoint_not_publicly_exposed_phase_1261",
        "transport_principal_policy_gate_rechecked_phase_1261",
        "werner_flow_governor_cdl_decision_phase_1263=no_open_no_prelock",
        "werner_flow_governor_cdl_not_opened_without_evidence_phase_1263",
        "direct_werner_ecu_creation_rejected_phase_1263",
        "heat_signal_must_not_directly_mint_ecu",
    ]
    for token in required_boundaries:
        assert token in handoff

    assert "Public RC remains blocked" in planning
    assert "public_rc_remains_blocked_after_phase_1264" in roadmap
    assert "Public/non-loopback sidecar projection serving remains blocked" in handoff


def test_planning_index_preserves_phase_1264_handoff_after_frontier_advances() -> None:
    planning = read(PLANNING)

    assert HANDOFF in planning
    assert "Window 1265-1272 CLOSED / PASS through Phase 1272" in planning
    assert "Exact-token `rg` is only a schema/completion check" in planning
