from __future__ import annotations

from pathlib import Path


SPEC_PATH = Path("docs/specs/ilc_cdl087_ratification_authorization_preflight_1276_v0.1.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1276_cdl087_ratification_authorization_preflight_walkthrough.md"
)
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

REQUIRED_TOKENS = (
    "cdl087_ratification_authorization_preflight_phase_1276.v0.1",
    "cdl087_ratification_requires_explicit_human_ratification_authorization_phase_1276",
    "cdl087_register_mutation_not_authorized_by_default_phase_1276",
    "no_public_fetch_serving_enabled_phase_1276",
)

NON_CLAIMS = (
    "CDL-087 ratification",
    "CDL register mutation",
    "CDL-088 opening",
    "public fetch serving",
    "public sidecar/projection serving",
    "public P2P exposure",
    "public claimability activation",
    "ECU mint authorization",
    "ILC settlement or withdrawal runtime activation",
    "v0.2 signing",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1276_required_tokens_are_recorded_everywhere() -> None:
    texts = (
        _read(SPEC_PATH),
        _read(STATUS_PATH),
        _read(PLANNING_INDEX_PATH),
        _read(WALKTHROUGH_PATH),
        _read(ROADMAP_PATH),
    )

    for text in texts:
        for token in REQUIRED_TOKENS:
            assert token in text


def test_phase_1276_records_no_ratification_no_register_mutation_decision() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    for text in (spec, walkthrough):
        assert (
            "cdl087_ratification_decision_phase_1276="
            "no_ratification_no_register_mutation_authority_absent"
        ) in text
        assert (
            "cdl087_evidence_status_phase_1276="
            "ready_for_explicit_authorized_ratification_attempt"
        ) in text
        assert "cdl087_register_diff_disposition_phase_1276=clean_no_mutation" in text
        assert "cdl087_conditions_1_to_6_preflighted_no_ratification_phase_1276" in text


def test_phase_1276_condition_matrix_cites_current_evidence_chain() -> None:
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

    for evidence_token in (
        "cdl_087_production_candidate_evidence_readiness_phase_1258.v0.1",
        "production_candidate_tier_classification_runtime_evidence_recorded_phase_1259",
        "bootstrap_snapshot_builder_verifier_evidence_recorded_phase_1259",
        "cdl_087_observability_collection_window_phase_1260.v0.1",
        "cdl_077_rate_limiter_final_regression_recorded_phase_1260",
        "cdl_087_sensitive_ratification_review_phase_1266.v0.1",
    ):
        assert evidence_token in spec


def test_phase_1276_preserves_cdl087_open_register_state() -> None:
    register = _read(CDL_REGISTER_PATH)
    spec = _read(SPEC_PATH)

    cdl087_rows = [line for line in register.splitlines() if line.startswith("| CDL-087 |")]
    assert len(cdl087_rows) == 1
    row = cdl087_rows[0]
    assert "| open |" in row
    assert "ratified_phase:" not in row
    assert "phase_1276" not in row
    assert "cdl087_ratification_authorization_preflight_phase_1276.v0.1" not in register

    assert "CDL-087 remains open" in spec
    assert "No CDL row is added" in spec


def test_phase_1276_records_broad_discovery_not_exact_token_only() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    for text in (spec, walkthrough):
        assert "Exact-token" in text
        assert "schema" in text
        assert "Concept discovery" in text
        assert "Contradiction" in text
        assert "canonical fetch" in text
        assert "bootstrap snapshot" in text
        assert "register mutation" in text


def test_phase_1276_public_non_claims_remain_blocked() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    planning = _read(PLANNING_INDEX_PATH)
    roadmap = _read(ROADMAP_PATH)

    for text in (spec, walkthrough):
        for phrase in NON_CLAIMS:
            assert phrase in text

    assert "no_public_fetch_serving_enabled_phase_1276" in planning
    assert "public_rc_remains_blocked_after_phase_1276" in roadmap
    assert "TransportPrincipal public-path activation" in spec


def test_phase_1276_frontier_updates_status_planning_and_next_phase() -> None:
    planning = _read(PLANNING_INDEX_PATH)
    status = _read(STATUS_PATH)
    roadmap = _read(ROADMAP_PATH)

    assert "Window 1273-1280 OPEN through Phase 1276" in planning
    assert "Phase 1277 is next and remains SENSITIVE" in planning
    assert "## Phase 1276" in status
    assert "Phase 1277 - TransportPrincipal public-path ADR" in status
    assert "Window frontier | Window 1273-1280 OPEN through Phase 1276" in roadmap


def test_phase_1276_graph_delta_is_recorded() -> None:
    spec = _read(SPEC_PATH)
    status = _read(STATUS_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    expected = (
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_cdl087_ratification_authorization_preflight_1276_v0.1.md -> planning/cdl087",
        "graph_delta=support_tests_added:tests/test_phase_1276_cdl087_ratification_authorization_preflight.py -> validation",
        "graph_delta=support_tests_changed:tests/test_window_1273_1280_prompt_drafts.py -> validation/frontier",
        "graph_delta=support_only:docs/phases/phase_1276_cdl087_ratification_authorization_preflight_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in spec
        assert graph_delta in status
        assert graph_delta in walkthrough
