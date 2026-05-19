from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

TAXONOMY = REPO / "docs/specs/ilc_public_node_review_taxonomy_v0.1.md"
WALKTHROUGH = REPO / "docs/phases/phase_1393_public_node_review_taxonomy_walkthrough.md"
J_PLAN = REPO / "docs/specs/ilc_jury_epoch_work_canonicalization_phase_plan_v0.1.md"

REQUIRED_TOKENS = {
    "public_node_review_taxonomy_phase_j003",
    "private_draft_nodes_do_not_require_jury",
    "reward_bearing_public_nodes_require_review_lane",
    "subjective_panel_non_blocking_boundary_preserved",
}

SOURCE_PATHS = {
    "docs/specs/ilc_jury_epoch_work_canon_map_v0.1.md",
    "docs/adr/ADR_0040_Jury_Eligibility_Assignment.md",
    "docs/specs/ilc_cdl_052_epistemic_node_submission_runtime_handoff_477_v0.1.md",
    "ilc_core/epistemic/node_submission_runtime.py",
    "docs/specs/ilc_cdl_059_aesthetic_panel_governance_ratification_evidence_531_v0.1.md",
    "ilc_core/epistemic/aesthetic_panel_runtime.py",
    "docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md",
    "ilc_core/economics/epoch_attribution_settle_runtime.py",
    "docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md",
    "ilc_core/ledger/public_economics_admission_firewall.py",
}

TAXONOMY_IDS = {
    "T0_PRIVATE_LOCAL_DRAFT",
    "T1_PUBLIC_NON_REWARD_METADATA",
    "T2_REWARD_BEARING_OBJECTIVE_NODE",
    "T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE",
    "T4_SUBJECTIVE_AESTHETIC_NODE",
    "T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM",
    "T6_VALIDATOR_CONSENSUS_CLAIM",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_taxonomy_artifact_exists_and_has_required_tokens():
    assert TAXONOMY.exists()
    text = read(TAXONOMY)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_taxonomy_cites_existing_sources():
    text = read(TAXONOMY)
    for rel_path in SOURCE_PATHS:
        assert (REPO / rel_path).exists(), rel_path
        assert rel_path in text


def test_all_required_taxonomy_ids_are_defined():
    text = read(TAXONOMY)
    for taxonomy_id in TAXONOMY_IDS:
        assert taxonomy_id in text


def test_private_drafts_do_not_require_jury_or_public_economics():
    text = read(TAXONOMY)
    assert "private_draft_nodes_do_not_require_jury" in text
    assert "T0_PRIVATE_LOCAL_DRAFT" in text
    assert "No jury review required" in text
    assert "They do not create public reputation, protocol ECU, public settlement rights" in text
    assert "Private timestamps, private commitments, or private draft history do not create" in text


def test_reward_bearing_public_objective_nodes_require_review_and_firewall():
    text = read(TAXONOMY)
    assert "reward_bearing_public_nodes_require_review_lane" in text
    assert "review_lane_reward_bearing_objective_requires_cdl052_cdlv7" in text
    assert "No reward-bearing objective node may construct public ECU" in text
    assert "Phase 1387a public-economics admission firewall" in text
    assert "mode_3_boundary_detected" in text
    assert "Mode 3 auditor-review execution remains incomplete" in text


def test_subjective_aesthetic_boundary_is_non_blocking_and_not_truth():
    text = read(TAXONOMY)
    assert "subjective_panel_non_blocking_boundary_preserved" in text
    assert "review_lane_subjective_aesthetic_cdl059_non_blocking" in text
    assert "not_objective_truth: True" in text
    assert "BLOCKING_AUTHORITY_ACTIVE =" in text
    assert "must not finalize objective truth" in text


def test_refutation_and_provenance_are_specialized_lanes():
    text = read(TAXONOMY)
    assert "review_lane_refutation_provenance_specialized" in text
    assert "CDL-083 settles only caller-filtered upheld `REFUTATION` events" in text
    assert "The payout recipient is the refuting agent" in text
    assert "PROVENANCE attribution follows CDL-084 chain-attribution economics" in text
    assert "not generic jury approval" in text


def test_validator_consensus_boundary_is_not_epistemic_jury():
    text = read(TAXONOMY)
    assert "review_lane_validator_consensus_evidence_not_jury" in text
    assert "validator_bft_certificates_are_not_epistemic_jury_verdicts" in text
    assert "They must not be described as 7+1 epistemic panel approvals" in text


def test_public_metadata_lane_is_non_reward_lightweight_only():
    text = read(TAXONOMY)
    assert "T1_PUBLIC_NON_REWARD_METADATA" in text
    assert "Lightweight schema / admission check" in text
    assert "If metadata later becomes reward-bearing" in text
    assert "it must be routed to the appropriate review lane" in text


def test_high_value_objective_lane_preserves_7_plus_1_panel_shape():
    text = read(TAXONOMY)
    for phrase in [
        "panel_size=8",
        "regular_reviewers=7",
        "outsider_seat=true",
        "reviewer_quorum=k=5 of m=7",
        "independence_k=3",
    ]:
        assert phrase in text
    assert "same-operator" in text
    assert "not independent" in text


def test_non_authorizations_are_explicit():
    text = read(TAXONOMY)
    for phrase in [
        "no runtime mutation",
        "no public graph admission activation",
        "no reviewer-payment activation",
        "no CDL mutation",
        "no public claimability activation",
        "no public economic event construction",
        "no production jury activation",
        "no graph write",
    ]:
        assert phrase in text


def test_j_plan_marks_j003_complete_after_execution():
    text = read(J_PLAN)
    assert "J-003 / 1393 now complete" in text
    assert "ilc_public_node_review_taxonomy_v0.1.md" in text


def test_walkthrough_exists_and_contains_graph_delta():
    assert WALKTHROUGH.exists()
    text = read(WALKTHROUGH)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "graph_delta=load_bearing_artifact_added:docs/specs/ilc_public_node_review_taxonomy_v0.1.md -> jury_epoch_work_canon" in text
    assert "No runtime mutation, CDL mutation, public graph admission activation, reviewer payment activation, production jury activation, public claimability activation, or public RC claim occurred" in text
