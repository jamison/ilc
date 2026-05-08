from __future__ import annotations

from pathlib import Path


SPEC_PATH = Path("docs/specs/ilc_cdl_087_sensitive_ratification_review_1266_v0.1.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1266_cdl087_sensitive_ratification_review_walkthrough.md"
)
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

REQUIRED_TOKENS = (
    "cdl_087_sensitive_ratification_review_phase_1266.v0.1",
    "cdl_087_ratification_decision_recorded_phase_1266",
    "cdl_087_ratification_not_executed_by_default_phase_1266",
    "cdl_087_register_mutation_requires_explicit_ratification_authorization_phase_1266",
    "no_public_fetch_serving_enabled_phase_1266",
)

PUBLIC_NON_CLAIMS = (
    "CDL-087 ratification",
    "CDL register mutation",
    "CDL-088 opening",
    "public fetch serving",
    "public sidecar/projection serving",
    "public P2P exposure",
    "TransportPrincipal runtime activation",
    "public RC claim",
    "public repository publication",
    "public claimability activation",
    "ECU mint authorization",
    "ILC settlement or withdrawal runtime activation",
    "v0.2 signing",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1266_review_packet_records_required_tokens_everywhere() -> None:
    spec = _read(SPEC_PATH)
    status = _read(STATUS_PATH)
    planning = _read(PLANNING_INDEX_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    roadmap = _read(ROADMAP_PATH)

    for text in (spec, status, planning, walkthrough, roadmap):
        for token in REQUIRED_TOKENS:
            assert token in text


def test_phase_1266_decision_is_no_ratification_no_register_mutation() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    for text in (spec, walkthrough):
        assert (
            "cdl_087_ratification_decision_phase_1266=no_ratification_no_register_mutation"
            in text
        )
        assert "cdl_087_register_diff_disposition_phase_1266=clean_no_mutation" in text
        assert "cdl_087_conditions_1_to_6_reviewed_no_ratification_phase_1266" in text

    assert "not an explicit authorization to ratify CDL-087" in spec
    assert "no ratification, and no register mutation" in spec


def test_phase_1266_condition_table_reviews_all_six_conditions() -> None:
    spec = _read(SPEC_PATH)

    for condition in (
        "1. SIM-FETCH-01 passes",
        "2. Tier A/B/C classification in a production-candidate serving peer",
        "3. Bootstrap snapshot format implemented and Genesis-verifiable",
        "4. Required observability signals collected for one SIM window",
        "5. CDL-077 limiter remains active and unmodified",
        "6. Fetch-incentive projection / credit bridge",
    ):
        assert condition in spec

    assert "production_candidate_tier_classification_runtime_evidence_recorded_phase_1259" in spec
    assert "bootstrap_snapshot_builder_verifier_evidence_recorded_phase_1259" in spec
    assert "cdl_087_observability_collection_window_phase_1260.v0.1" in spec
    assert "cdl_077_rate_limiter_final_regression_recorded_phase_1260" in spec


def test_phase_1266_preserves_cdl_register_open_state_without_mutation_marker() -> None:
    spec = _read(SPEC_PATH)
    register = _read(CDL_REGISTER_PATH)

    cdl087_rows = [line for line in register.splitlines() if line.startswith("| CDL-087 |")]
    assert len(cdl087_rows) == 1
    row = cdl087_rows[0]
    assert "| open |" in row
    assert "ratified_phase:" not in row
    assert "phase_1266" not in row

    assert "CDL-087 remains open" in spec
    assert "No CDL row is added" in spec


def test_phase_1266_records_broad_discovery_not_exact_token_only() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    for text in (spec, walkthrough):
        assert "Exact-token" in text
        assert "schema" in text
        assert "Concept discovery" in text
        assert "Contradiction" in text
        assert "serving peer" in text
        assert "Graph Node" in text


def test_phase_1266_public_non_claims_remain_blocked() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    planning = _read(PLANNING_INDEX_PATH)
    roadmap = _read(ROADMAP_PATH)

    for text in (spec, walkthrough):
        for phrase in PUBLIC_NON_CLAIMS:
            assert phrase in text

    assert "no_public_fetch_serving_enabled_phase_1266" in planning
    assert "public_rc_remains_blocked_after_phase_1266" in roadmap
    assert "public_rc_remains_blocked_after_phase_1267" in roadmap
    assert "public_rc_remains_blocked_after_phase_1269" in roadmap
    assert "CDL-087 remains open/prelocked/not ratified after Phase 1266" in planning


def test_phase_1266_frontier_updates_planning_status_and_next_phase() -> None:
    planning = _read(PLANNING_INDEX_PATH)
    status = _read(STATUS_PATH)

    assert "Window 1265-1272 OPEN / PASS through Phase 1269" in planning
    assert str(SPEC_PATH) in planning
    assert "## Phase 1266" in status
    assert "## Phase 1267" in status
    assert "## Phase 1268" in status
    assert "phase_1267_transport_principal_runtime_identity_pre_public_path_next" in status


def test_phase_1266_graph_delta_is_recorded() -> None:
    spec = _read(SPEC_PATH)
    status = _read(STATUS_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    expected = (
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_cdl_087_sensitive_ratification_review_1266_v0.1.md -> planning/cdl087",
        "graph_delta=support_tests_added:tests/test_phase_1266_cdl087_sensitive_ratification_review.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1266_cdl087_sensitive_ratification_review_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in spec
        assert graph_delta in status
        assert graph_delta in walkthrough
