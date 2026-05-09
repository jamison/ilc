from __future__ import annotations

from pathlib import Path


SPEC_PATH = Path("docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_1278_fix1_cdl087_ratification_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

REQUIRED_TOKENS = (
    "cdl087_ratification_evidence_phase_1278_fix1.v0.1",
    "cdl087_ratified_phase_1278_fix1",
    "cdl087_register_mutated_phase_1278_fix1",
    "cdl087_conditions_1_to_6_reproved_phase_1278_fix1",
    "cdl087_public_fetch_serving_not_enabled_phase_1278_fix1",
    "cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1",
    "no_cdl088_opening_phase_1278_fix1",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl087_row() -> str:
    rows = [
        line
        for line in _read(CDL_REGISTER_PATH).splitlines()
        if line.startswith("| CDL-087 |")
    ]
    assert len(rows) == 1
    return rows[0]


def test_phase_1278_fix1_required_tokens_are_recorded_everywhere() -> None:
    texts = (
        _read(SPEC_PATH),
        _read(WALKTHROUGH_PATH),
        _read(STATUS_PATH),
        _read(PLANNING_INDEX_PATH),
        _read(ROADMAP_PATH),
        _read(SEQUENCE_LOCK_PATH),
    )

    for text in texts:
        for token in REQUIRED_TOKENS:
            assert token in text


def test_phase_1278_fix1_register_row_is_ratified_with_evidence_refs() -> None:
    row = _cdl087_row()

    assert "| ratified |" in row
    assert "| open |" not in row
    assert "ratified_phase: 1278 Fix1" in row
    assert "ratified_date: 2026-05-09" in row
    assert "ratification_token: cdl087_ratified_phase_1278_fix1" in row
    assert "register_mutation_token: cdl087_register_mutated_phase_1278_fix1" in row
    assert (
        "evidence_document: "
        "docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md"
    ) in row


def test_phase_1278_fix1_reproves_all_six_conditions() -> None:
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
        "sim_fetch_01_cdl_087_robustness_suite_1238j",
        "cdl_087_production_candidate_evidence_readiness_phase_1258.v0.1",
        "production_candidate_tier_classification_runtime_evidence_recorded_phase_1259",
        "bootstrap_snapshot_builder_verifier_evidence_recorded_phase_1259",
        "cdl_087_observability_collection_window_phase_1260.v0.1",
        "cdl_077_rate_limiter_final_regression_recorded_phase_1260",
        "cdl087_conditions_1_to_6_preflighted_no_ratification_phase_1276",
    ):
        assert evidence_token in spec


def test_phase_1278_fix1_records_authority_and_public_path_non_activation() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    row = _cdl087_row()

    assert (
        "GO Phase 1278 Fix1. I authorize CDL-087 ratification and CDL register mutation"
        in spec
    )
    assert "public_fetch_serving_status: not_enabled" in row
    assert "public_sidecar_projection_status: blocked_pending_separate_authorization" in row

    for text in (spec, walkthrough):
        assert "public fetch serving" in text
        assert "public sidecar/projection serving" in text
        assert "public P2P exposure" in text
        assert "public RC claim" in text
        assert "CDL-088" in text
        assert "v0.2 signing" in text


def test_phase_1278_fix1_updates_frontier_and_next_phase() -> None:
    planning = _read(PLANNING_INDEX_PATH)
    roadmap = _read(ROADMAP_PATH)
    status = _read(STATUS_PATH)
    sequence_lock = _read(SEQUENCE_LOCK_PATH)

    assert "Window 1273-1280 OPEN through Phase 1279" in planning
    assert "CDL-087 is RATIFIED" in planning
    assert "Phase 1280 remains the next locked sensitive closure phase" in planning
    assert "Window frontier | Window 1273-1280 OPEN through Phase 1279" in roadmap
    assert "CDL-087 | **RATIFIED** in Phase 1278 Fix1" in roadmap
    assert "public_rc_remains_blocked_after_phase_1278_fix1" in roadmap
    assert "## Phase 1278 Fix1" in status
    assert "Phase 1279 - release manifest/source allowlist prepublication preflight" in status
    assert "## 6. Phase 1278 Fix1 Ratification Addendum" in sequence_lock


def test_phase_1278_fix1_graph_delta_is_recorded() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)

    expected = (
        "graph_delta=load_bearing_register_changed:docs/specs/ilc_constitutional_decision_log_v0.1.md -> governance/cdl087",
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md -> governance/cdl087",
        "graph_delta=support_tests_added:tests/test_phase_1278_fix1_cdl087_ratification.py -> validation",
        "graph_delta=support_tests_changed:tests/test_window_1273_1280_prompt_drafts.py -> validation/frontier",
        "graph_delta=support_only:docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/phase_1278_fix1_cdl087_ratification_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in spec
        assert graph_delta in walkthrough
        assert graph_delta in status
