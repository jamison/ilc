from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CANON_MAP = REPO / "docs/specs/ilc_jury_epoch_work_canon_map_v0.1.md"

REQUIRED_TOKENS = {
    "jury_epoch_work_canon_map_phase_j001",
    "jury_participation_incentivized_not_obligatory_recorded",
    "objective_subjective_panel_split_confirmed",
}

REQUIRED_SOURCE_PATHS = {
    "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
    "docs/specs/ilc_rc0_1_7_plus_1_panel_live_submission_integration_580_v0.1.md",
    "docs/specs/ilc_cdl_052_epistemic_node_submission_runtime_handoff_477_v0.1.md",
    "ilc_core/epistemic/node_submission_runtime.py",
    "docs/specs/ilc_cdl_059_aesthetic_panel_governance_ratification_evidence_531_v0.1.md",
    "ilc_core/epistemic/aesthetic_panel_runtime.py",
    "docs/research/ilc_jury_deliberation_research_memo_791_v0.1.md",
    "docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md",
    "ilc_core/validator/topology_shuffle_runtime.py",
    "docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md",
    "docs/specs/epoch_init_control_loop_v0.1.md",
    "docs/specs/ilc_capability_proof_activation_readiness_contract_231_v0.1.md",
    "docs/specs/ilc_capability_proof_activation_readiness_gates_v0.1.md",
    "ilc_core/mining/benchmark.py",
    "docs/research/ilc_inverted_ecu_model_precanon_v0.1.md",
    "ilc_core/genesis/work_task.py",
    "ilc_core/work/task_queue.py",
    "docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md",
    "ilc_core/economics/epoch_attribution_settle_runtime.py",
    "docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md",
    "ilc_core/epoch/validator_reward_pool_routing_runtime.py",
}


def read_map() -> str:
    assert CANON_MAP.exists(), f"missing canon map: {CANON_MAP}"
    return CANON_MAP.read_text()


def test_required_tokens_present():
    text = read_map()
    for token in REQUIRED_TOKENS:
        assert token in text


def test_all_referenced_source_paths_exist_and_are_named():
    text = read_map()
    for relative_path in REQUIRED_SOURCE_PATHS:
        assert relative_path in text, f"source path not named: {relative_path}"
        assert (REPO / relative_path).exists(), f"source path missing: {relative_path}"


def test_panel_shape_and_quorum_ladder_are_preserved():
    text = read_map()
    required_fragments = [
        "panel_size=8",
        "regular_reviewers=7",
        "outsider_seat=true",
        "reviewer_quorum=k=5 of m=7",
        "independence_k=3",
        "L0 = 3",
        "L1 = 5",
        "L2 = 7",
        "L3 = 9",
        "appeals escalate by +2",
    ]
    for fragment in required_fragments:
        assert fragment in text


def test_reduced_and_misremembered_jury_tiers_are_not_promoted_to_canon():
    text = read_map()
    assert "not ratified" in text
    assert "`5+1` was not found as a ratified jury tier" in text
    assert "`5+2` was not found as a ratified jury pattern" in text


def test_objective_subjective_and_bft_boundaries_are_explicit():
    text = read_map()
    assert "objective / Popperian jury line" in text
    assert "subjective / aesthetic lane" in text
    assert "not objective truth" in text
    assert "not a validator BFT quorum" in text
    assert "validator BFT thresholds" in text


def test_jury_participation_is_not_obligatory():
    text = read_map()
    assert "incentivized and opt-in" in text
    assert "not obligatory" in text
    assert "no mandatory jury service for every connected agent" in text


def test_no_activation_non_claims_are_recorded():
    text = read_map()
    non_claims = [
        "no general production jury assignment runtime",
        "no general reviewer-payment activation",
        "no public graph canonicalization activation",
        "no production ingestion activation",
        "no production topology shuffle activation",
        "no CDL mutation",
        "no runtime mutation",
    ]
    for non_claim in non_claims:
        assert non_claim in text


def test_future_phase_routing_is_complete():
    text = read_map()
    for phase in ["1392", "1393", "1394", "1395", "1396", "1397", "1398"]:
        assert phase in text
    for label in ["J-002", "J-003", "J-004", "J-005", "J-006", "J-007", "J-008"]:
        assert label in text


def test_graph_delta_recorded():
    text = read_map()
    assert (
        "graph_delta=load_bearing_artifact_added:"
        "docs/specs/ilc_jury_epoch_work_canon_map_v0.1.md -> "
        "jury_epoch_work_canon"
    ) in text
