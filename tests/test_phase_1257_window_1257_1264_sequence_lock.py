from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SEQUENCE_LOCK = "docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1257_1264_candidate_phase_grouping_v0.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1257_window_1257_1264_sequence_lock_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "window_1257_1264_sequence_lock_committed",
    "window_1257_1264_sequence_lock_verdict=pass",
    "phase_1258_cdl087_evidence_readiness_requires_explicit_go",
    "window_1257_1264_no_public_rc_or_public_p2p",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1257_sequence_lock_required_tokens_are_published() -> None:
    lock = read(SEQUENCE_LOCK)
    planning = read(PLANNING)
    status = read(STATUS)
    walkthrough = read(WALKTHROUGH)

    for token in REQUIRED_TOKENS:
        assert token in lock
        assert token in planning
        assert token in status
        assert token in walkthrough


def test_phase_1257_sequence_lock_consumes_guidance_and_current_canon() -> None:
    lock = read(SEQUENCE_LOCK)

    expected_inputs = (
        "docs/specs/ilc_antigravity_context_capsule_v5.50.md",
        "docs/specs/ilc_window_1249_1256_handoff_1256_v0.1.md",
        GUIDANCE,
        "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md",
        "docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md",
        "docs/specs/ilc_cdl_087_governance_review_disposition_1246_v0.1.md",
        "docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md",
        "docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_robustness_suite_1238j_v0.1.md",
        "ilc_core/sim/sim_fetch_01/sim_fetch_01_harness.py",
        "ilc_core/graph/sidecar_query_runtime.py",
        CDL_REGISTER,
    )
    for source in expected_inputs:
        assert source in lock

    assert "window_1249_1256_closed_phase_1256" in lock
    assert "public_rc_remains_blocked_after_phase_1256" in lock


def test_phase_1257_discovery_discipline_records_broad_search_not_exact_only() -> None:
    lock = read(SEQUENCE_LOCK)
    for phrase in (
        "Required-token audit",
        "Concept-discovery search",
        "Contradiction and non-claim search",
        "Source expansion",
        "Exact-token `rg` is a schema/completion check only",
        "token components, synonyms, neighboring ideas, older names, code symbols",
        "MemPalace may be used only as advisory retrieval support",
        "unknown_unknown_discovery_required_before_phase_execution",
    ):
        assert phrase in lock


def test_phase_1257_cdl087_conditions_are_locked_without_ratification() -> None:
    lock = read(SEQUENCE_LOCK)
    cdl_register = read(CDL_REGISTER)

    assert "CDL-087 remains:" in lock
    assert "OPEN / PRELOCKED / NOT RATIFIED" in lock
    assert "cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence" in lock
    assert "| 2. Tier A/B/C classification in a production-candidate serving peer | Open blocker. |" in lock
    assert "| 3. Bootstrap snapshot format builder/verifier | Open blocker. |" in lock
    assert "| 4. Production-candidate observability collection for at least one SIM window | Open blocker. |" in lock
    assert "| 5. CDL-077 static rate limiter remains active and no unlimited fetch path exists | Final regression required. |" in lock
    assert "| 6. Fetch-incentive projection/credit bridge recheck | Requires recheck" in lock
    assert "| CDL-087 |" in cdl_register
    assert "| ratified |" in cdl_register
    assert "ratified_phase: 1278 Fix1" in cdl_register


def test_phase_1257_locked_order_and_sensitive_gates_are_explicit() -> None:
    lock = read(SEQUENCE_LOCK)

    expected_rows = (
        "| 1 | 1257 | Window 1257-1264 sequence lock | **SENSITIVE** |",
        "| 2 | 1258 | CDL-087 production-candidate evidence readiness and condition inventory | **SENSITIVE** |",
        "| 3 | 1259 | CDL-087 serving-peer evidence slice: Tier A/B/C classification plus bootstrap snapshot builder/verifier evidence | NON-SENSITIVE unless widened |",
        "| 4 | 1260 | CDL-087 observability collection window and final CDL-077 limiter regression | NON-SENSITIVE unless widened |",
        "| 5 | 1261 | Sidecar projection endpoint boundary and TransportPrincipal public-path gate recheck | NON-SENSITIVE boundary/spec |",
        "| 6 | 1262 | Werner Flow Governor overlay validation and promote/retire decision | NON-SENSITIVE |",
        "| 7 | 1263 | Werner flow-governor CDL opening/prelock decision if evidence supports it | **SENSITIVE** |",
        "| 8 | 1264 | Window coherence, blocker classification, and closure gate | **SENSITIVE** |",
    )
    for row in expected_rows:
        assert row in lock

    assert "GO Phase 1258" in lock
    assert "GO Phase 1263" in lock
    assert "GO Phase 1264" in lock


def test_phase_1257_public_and_economic_non_claims_are_preserved() -> None:
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


def test_phase_1257_frontier_updates_planning_and_status() -> None:
    planning = read(PLANNING)
    status = read(STATUS)

    assert "Window 1273-1280 OPEN through Phase 1278 Fix1" in planning
    assert SEQUENCE_LOCK in planning
    assert "Phase 1279 remains the next locked non-sensitive inventory phase" in planning
    assert "## Phase 1257" in status
    assert "Phase 1258 - CDL-087 production-candidate evidence readiness" in status


def test_phase_1257_graph_delta_is_recorded() -> None:
    lock = read(SEQUENCE_LOCK)
    walkthrough = read(WALKTHROUGH)

    expected_graph_deltas = (
        "graph_delta=support_only:docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/phase_1257_window_1257_1264_sequence_lock_walkthrough.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1257_window_1257_1264_sequence_lock.py -> validation",
    )
    for graph_delta in expected_graph_deltas:
        assert graph_delta in lock
        assert graph_delta in walkthrough
