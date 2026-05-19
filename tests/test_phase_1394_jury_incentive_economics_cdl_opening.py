"""Phase 1394 / J-004 jury incentive economics CDL opening tests."""

from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md"
WALKTHROUGH = (
    REPO
    / "docs/phases/phase_1394_jury_incentive_economics_cdl_opening_walkthrough.md"
)
PLAN = REPO / "docs/specs/ilc_jury_epoch_work_canonicalization_phase_plan_v0.1.md"
STATUS = REPO / "docs/phases/STATUS.md"
PLANNING_INDEX = REPO / "docs/PLANNING_INDEX.md"


REQUIRED_TOKENS = (
    "jury_incentive_economics_cdl_opened_phase_j004",
    "approval_volume_bias_risk_recorded",
    "fixed_plus_accuracy_weighted_panel_compensation_recommended",
    "reviewer_payment_not_activated_phase_j004",
)


SOURCE_ANCHORS = (
    "docs/specs/ilc_jury_epoch_work_canon_map_v0.1.md",
    "docs/specs/ilc_public_node_review_taxonomy_v0.1.md",
    "docs/adr/ADR_0040_Jury_Eligibility_Assignment.md",
    "docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md",
    "docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md",
    "ilc_core/epoch/validator_reward_pool_routing_runtime.py",
    "docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md",
    "ilc_core/epoch/treasury_governance_runtime.py",
    "docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md",
    "ilc_core/economics/epoch_attribution_settle_runtime.py",
    "docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md",
    "ilc_core/ledger/public_economics_admission_firewall.py",
    "docs/research/ilc_inverted_ecu_model_precanon_v0.1.md",
    "docs/research/ilc_jury_deliberation_research_memo_791_v0.1.md",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_artifact_exists():
    assert ARTIFACT.exists()


def test_required_tokens_present():
    text = _read(ARTIFACT)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_artifact_is_opening_not_ratification():
    text = _read(ARTIFACT)
    assert "Status:** CDL economics lane opened; not ratified" in text
    assert "does not ratify payment amounts" in text
    assert "does not activate any slashing" in text


def test_source_anchors_are_cited():
    text = _read(ARTIFACT)
    for anchor in SOURCE_ANCHORS:
        assert anchor in text


def test_approval_only_payment_rejected():
    text = _read(ARTIFACT)
    assert "approval_only_panel_payment_rejected" in text
    assert "Approval-only reviewer payment" in text
    assert "Rejected" in text


def test_split_compensation_model_recommended():
    text = _read(ARTIFACT)
    assert "fixed_base_plus_delayed_accuracy_bonus_recommended" in text
    assert "Base review fee" in text
    assert "Delayed accuracy-weighted bonus" in text


def test_existing_economics_not_misrepresented_as_reviewer_payment():
    text = _read(ARTIFACT)
    assert "validator_rewards_not_reviewer_rewards_without_cdl_bridge" in text
    assert "treasury_governance_not_reviewer_budget_without_cdl_bridge" in text
    assert "cdl_083_refutation_attribution_not_general_reviewer_compensation" in text


def test_public_economics_firewall_preserved():
    text = _read(ARTIFACT)
    assert "public_only_economics_firewall_preserved_for_reviewer_payment" in text
    assert "Phase 1387a public-economics admission firewall" in text


def test_candidate_funding_sources_recorded():
    text = _read(ARTIFACT)
    assert "petition_bond_candidate_funding_source_recorded" in text
    assert "fixed_pooled_review_budget_candidate_recorded" in text
    assert "reviewer_payment_activation_requires_later_ratification" in text


def test_non_authorization_phrase_present():
    text = _read(ARTIFACT)
    assert (
        "No runtime mutation, CDL register mutation, ledger mutation, reviewer "
        "payment activation, public economics activation, production jury activation"
    ) in text


def test_walkthrough_exists_and_has_graph_delta():
    assert WALKTHROUGH.exists()
    text = _read(WALKTHROUGH)
    assert "graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md -> jury_epoch_work_canon" in text
    assert "reviewer_payment_not_activated_phase_j004" in text


def test_status_records_phase_1394():
    text = _read(STATUS)
    assert "Phase 1394 / J-004" in text
    assert "jury_incentive_economics_cdl_opened_phase_j004" in text
    assert "reviewer_payment_not_activated_phase_j004" in text


def test_planning_index_records_phase_1394():
    text = _read(PLANNING_INDEX)
    assert "Phase 1394 / J-004 addendum" in text
    assert "fixed_plus_accuracy_weighted_panel_compensation_recommended" in text
    assert "Phase 1395 / J-005" in text


def test_j_series_plan_marks_j004_complete():
    text = _read(PLAN)
    assert "| J-004 | Phase 1394 | COMPLETE: jury incentive economics CDL opening |" in text
    assert "**Status:** J-004 / Phase 1394 COMPLETE" in text
    assert "reviewer_payment_not_activated_phase_j004" in text

