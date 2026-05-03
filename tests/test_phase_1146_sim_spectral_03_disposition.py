from pathlib import Path


DISPOSITION = Path("docs/sims/sim_spectral_03/disposition_1146_v0.1.md")


def _text() -> str:
    return DISPOSITION.read_text()


def test_d1_disposition_exists_with_closing_token() -> None:
    assert DISPOSITION.exists()
    assert "sim_spectral_03_disposition_committed_phase_1146" in _text()


def test_d2_cdl_085_recommendation_is_defer() -> None:
    assert "CDL-085 recommendation: DEFER" in _text()


def test_d3_corrected_run02_comparison_values_present() -> None:
    text = _text()
    assert "corrected Run 02" in text
    assert "Phase 1145" in text
    assert "0.6416011282246747" in text
    assert "1.6736470076736112" in text
    assert "0.8640456434014127" in text
    assert "2.2539040876901315" in text


def test_d4_named_architectural_finding_present() -> None:
    assert "raw_authority_graph_is_not_the_right_spectral_work_graph" in _text()


def test_d5_all_forward_obligation_tokens_present() -> None:
    text = _text()
    tokens = [
        "sim_spectral_04_claim_composition_projection_required_before_cdl_085_reconsideration",
        "genesis_32_node_composability_audit_required",
        "matched_size_controls_required_for_future_spectral_sims",
        "genesis_canonical_lineage_contract_required_before_public_rc",
        "truth_primitive_permanence_requires_community_ratification_before_genesis_sunset",
        "public_rc_envelope_hash_transition_policy_required",
        "contributor_agreement_required_before_public_repo",
    ]
    for token in tokens:
        assert token in text


def test_d6_no_cdl_mutation_authorization_present() -> None:
    assert "ILC_CDL_MUTATION_AUTHORIZED" not in _text()
