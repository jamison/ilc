from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SEQUENCE_LOCK = "docs/specs/ilc_phase_1265_1272_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1265_1272_candidate_phase_grouping_v0.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1265_window_1265_1272_sequence_lock_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "window_1265_1272_sequence_lock_committed",
    "window_1265_1272_sequence_lock_verdict=pass",
    "phase_1266_cdl087_sensitive_review_requires_explicit_go",
    "window_1265_1272_no_public_rc_or_public_p2p",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1265_sequence_lock_required_tokens_are_published() -> None:
    lock = read(SEQUENCE_LOCK)
    planning = read(PLANNING)
    status = read(STATUS)
    walkthrough = read(WALKTHROUGH)

    for token in REQUIRED_TOKENS:
        assert token in lock
        assert token in planning
        assert token in status
        assert token in walkthrough


def test_phase_1265_sequence_lock_consumes_guidance_and_current_canon() -> None:
    lock = read(SEQUENCE_LOCK)

    expected_inputs = (
        "docs/specs/ilc_antigravity_context_capsule_v5.50.md",
        "docs/specs/ilc_window_1257_1264_handoff_1264_v0.1.md",
        GUIDANCE,
        "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md",
        "docs/specs/ilc_constitutional_decision_log_v0.1.md",
        "docs/specs/ilc_cdl_087_production_candidate_evidence_readiness_1258_v0.1.md",
        "docs/specs/ilc_cdl_087_serving_peer_evidence_slice_1259_v0.1.md",
        "docs/specs/ilc_cdl_087_observability_and_limiter_regression_1260_v0.1.md",
        "docs/specs/ilc_sidecar_projection_endpoint_boundary_1261_v0.1.md",
        "docs/specs/ilc_werner_flow_governor_cdl_decision_1263_v0.1.md",
        "docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md",
        "docs/specs/ilc_gap13_public_claimability_resolution_boundary_1252_v0.1.md",
    )
    for source in expected_inputs:
        assert source in lock

    assert "window_1257_1264_closed_phase_1264" in lock
    assert "public_rc_remains_blocked_after_phase_1264" in lock


def test_phase_1265_discovery_discipline_records_broad_search_not_exact_only() -> None:
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


def test_phase_1265_cdl087_review_gate_is_sensitive_and_not_ratification() -> None:
    lock = read(SEQUENCE_LOCK)
    cdl_register = read(CDL_REGISTER)

    assert "CDL-087 remains:" in lock
    assert "OPEN / PRELOCKED / NOT RATIFIED" in lock
    assert "cdl_087_ratification_not_executed_by_default_phase_1266" in lock
    assert "Phase 1266 must not ratify CDL-087 or mutate the CDL register by default" in lock
    assert "| CDL-087 |" in cdl_register
    assert "| open |" in cdl_register


def test_phase_1265_locked_order_and_sensitive_gates_are_explicit() -> None:
    lock = read(SEQUENCE_LOCK)

    expected_rows = (
        "| 1 | 1265 | Window 1265-1272 sequence lock | **SENSITIVE** |",
        "| 2 | 1266 | CDL-087 sensitive ratification review and decision packet | **SENSITIVE** |",
        "| 3 | 1267 | TransportPrincipal runtime identity pre-public-path slice | NON-SENSITIVE unless widened to public exposure |",
        "| 4 | 1268 | Sidecar loopback projection endpoint boundary or prototype | NON-SENSITIVE only if local loopback/subprocess/Unix-socket |",
        "| 5 | 1269 | Werner default SIM-FETCH topology-pressure profile follow-up | NON-SENSITIVE simulation/evidence |",
        "| 6 | 1270 | Gap 13 claimability conversion-sweeper preflight | **SENSITIVE** |",
        "| 7 | 1271 | ATLAS-G-006 public-RC graph reachability gate | NON-SENSITIVE unless widened to Genesis or release artifacts |",
        "| 8 | 1272 | Window coherence, blocker classification, and closure gate | **SENSITIVE** |",
    )
    for row in expected_rows:
        assert row in lock

    assert "GO Phase 1266" in lock
    assert "GO Phase 1270" in lock
    assert "GO Phase 1272" in lock


def test_phase_1265_public_and_economic_non_claims_are_preserved() -> None:
    lock = read(SEQUENCE_LOCK)
    for phrase in (
        "public RC claim",
        "public repository publication",
        "public P2P exposure",
        "public sidecar/projection serving",
        "public claimability activation",
        "CDL mutation, CDL-087 ratification, Werner CDL opening/prelock",
        "ECU mint authorization",
        "ILC settlement or withdrawal runtime activation",
        "release-key generation",
        "v0.2 signing",
    ):
        assert phrase in lock

    assert "sidecar_projection_endpoint_public_path_requires_transport_principal_auth" in lock
    assert "heat_signal_must_not_directly_mint_ecu" in lock
    assert "direct_werner_ecu_creation_rejected_phase_1263" in lock


def test_phase_1265_frontier_updates_planning_and_status() -> None:
    planning = read(PLANNING)
    status = read(STATUS)

    assert "Window 1265-1272 OPEN / PASS through Phase 1265" in planning
    assert SEQUENCE_LOCK in planning
    assert "Phase 1266 remains SENSITIVE and requires explicit `GO Phase 1266`" in planning
    assert "## Phase 1265" in status
    assert "Phase 1266 - CDL-087 sensitive ratification review" in status


def test_phase_1265_graph_delta_is_recorded() -> None:
    lock = read(SEQUENCE_LOCK)
    walkthrough = read(WALKTHROUGH)

    expected_graph_deltas = (
        "graph_delta=support_only:docs/specs/ilc_phase_1265_1272_sequence_lock_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/phase_1265_window_1265_1272_sequence_lock_walkthrough.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1265_window_1265_1272_sequence_lock.py -> validation",
    )
    for graph_delta in expected_graph_deltas:
        assert graph_delta in lock
        assert graph_delta in walkthrough
