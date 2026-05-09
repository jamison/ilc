from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_cdl_087_production_candidate_evidence_readiness_1258_v0.1.md"
STATUS = "docs/phases/STATUS.md"
PLANNING = "docs/PLANNING_INDEX.md"
WALKTHROUGH = "docs/phases/phase_1258_cdl087_production_candidate_evidence_readiness_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "cdl_087_production_candidate_evidence_readiness_phase_1258.v0.1",
    "cdl_087_ratification_not_executed_phase_1258",
    "cdl_087_conditions_1_to_6_reconciled_phase_1258",
    "cdl_087_open_blockers_routed_phase_1258",
)

CONDITION_TOKENS = (
    "condition_1_sim_fetch_01_passed_for_governance_review",
    "condition_2_production_candidate_tier_classification_open",
    "condition_3_bootstrap_snapshot_format_open",
    "condition_4_production_candidate_observability_open",
    "condition_5_cdl_077_rate_limiter_preserved_pending_final_regression",
    "condition_6_fetch_incentive_projection_resolved_at_projection_level",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1258_required_tokens_are_published() -> None:
    spec = read(SPEC)
    status = read(STATUS)
    planning = read(PLANNING)
    walkthrough = read(WALKTHROUGH)

    for token in REQUIRED_TOKENS:
        assert token in spec
        assert token in status
        assert token in planning
        assert token in walkthrough


def test_phase_1258_reconciles_all_six_conditions() -> None:
    spec = read(SPEC)
    for token in CONDITION_TOKENS:
        assert token in spec

    for condition in range(1, 7):
        assert f"| {condition}." in spec

    assert "cdl_087_ratification_readiness_verdict_phase_1258=not_ready" in spec


def test_phase_1258_routes_open_blockers_to_1259_and_1260() -> None:
    spec = read(SPEC)

    assert "cdl_087_blocker_production_candidate_tier_classification_runtime" in spec
    assert "cdl_087_blocker_bootstrap_snapshot_builder_and_verifier" in spec
    assert "cdl_087_blocker_production_candidate_observability_collection_window" in spec
    assert "cdl_087_blocker_final_cdl_077_rate_limiter_regression" in spec
    assert "Phase 1259 serving-peer evidence slice" in spec
    assert "Phase 1260 observability collection-window artifact" in spec
    assert "Phase 1260 final limiter regression" in spec


def test_phase_1258_preserves_non_ratification_and_cdl_register_state() -> None:
    spec = read(SPEC)
    cdl_register = read(CDL_REGISTER)

    assert "OPEN / PRELOCKED / NOT RATIFIED" in spec
    assert "The CDL register is not mutated by this phase" in spec
    assert "CDL-087 ratification" in spec
    assert "| CDL-087 |" in cdl_register
    assert "| ratified |" in cdl_register
    assert "ratified_phase: 1278 Fix1" in cdl_register


def test_phase_1258_non_authorization_boundary_is_explicit() -> None:
    spec = read(SPEC)
    for phrase in (
        "CDL register mutation",
        "CDL-087 ratification",
        "public fetch serving",
        "public sidecar/projection serving",
        "public P2P exposure",
        "public RC claim",
        "Werner ECU minting",
        "ILC settlement activation",
        "v0.2 signing",
    ):
        assert phrase in spec


def test_phase_1258_updates_frontier_and_graph_delta() -> None:
    planning = read(PLANNING)
    status = read(STATUS)
    spec = read(SPEC)

    assert "Window 1273-1280 OPEN through Phase 1278 Fix1" in planning
    assert SPEC in planning
    assert "## Phase 1258" in status
    assert "Phase 1259 - CDL-087 serving-peer evidence slice" in status

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_cdl_087_production_candidate_evidence_readiness_1258_v0.1.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1258_cdl087_production_candidate_evidence_readiness.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1258_cdl087_production_candidate_evidence_readiness_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    ):
        assert graph_delta in spec
        assert graph_delta in read(WALKTHROUGH)
