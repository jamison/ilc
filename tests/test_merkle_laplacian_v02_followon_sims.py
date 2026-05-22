import json
from pathlib import Path

from tools.sim import sim_merkle_laplacian_v02_followon as followon


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sim/sim_merkle_laplacian_v02_followon.py"
RESULT_MD = (
    ROOT / "docs/sims/sim_merkle_laplacian_v02/followon_results_2026_05_22_v0.1.md"
)
RESULT_JSON = (
    ROOT / "docs/sims/sim_merkle_laplacian_v02/followon_results_2026_05_22_v0.1.json"
)
TRANSCRIPT_SPEC = (
    ROOT
    / "docs/specs/ilc_merkle_laplacian_v02_canonicalization_and_posk_transcript_spec_v0.1.md"
)
FORWARD_1459 = ROOT / "docs/specs/ilc_window_1459_forward_plan_v0.1.md"
PAPER = (
    ROOT / "docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.2.md"
)


def test_followon_script_is_internal_only() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "PUBLIC_RC_EXCLUDE: internal_research_simulation" in source
    assert "does not activate epoch commitments" in source
    assert "SIM-POSK-PARAM-02" in source
    assert "SIM-SPECTRAL-CROSSIMPL-02" in source
    assert "SIM-COSPECTRAL-01" in source
    assert "SIM-DIRECTED-SPECTRAL-02" in source


def test_followon_json_records_gate_tokens_and_dependencies() -> None:
    data = json.loads(RESULT_JSON.read_text(encoding="utf-8"))

    assert data["public_rc_exclude"] is True
    assert data["overall_verdict"] == (
        "internal_followon_positive_with_activation_dependencies_remaining"
    )
    assert data["gate_tokens"] == [
        "sim_posk_param_02_multiple_nonce_calibration_complete=true",
        "sim_spectral_crossimpl_02_python_vector_conformance=true",
        "sim_cospectral_01_bounded_random_k8_distinct_m_collision_found=false",
        "sim_directed_spectral_02_extension_required=true",
    ]


def test_posk_param_sim_requires_multiple_nonces_and_fetch_control() -> None:
    data = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
    posk = data["sims"]["SIM-POSK-PARAM-02"]
    recommended = posk["recommended_minimum"]

    assert recommended["sample_size"] >= 64
    assert recommended["nonce_count"] >= 4
    assert recommended["meets_1_percent_target"] is True
    assert recommended["max_observed_stale_or_partial_pass_rate"] <= 0.01
    assert posk["post_challenge_full_fetch_passes_if_allowed"] is True
    assert "local-storage attestation" in posk["required_protocol_control"]


def test_crossimpl_and_cospectral_findings_are_scoped_correctly() -> None:
    data = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
    cross = data["sims"]["SIM-SPECTRAL-CROSSIMPL-02"]
    cospectral = data["sims"]["SIM-COSPECTRAL-01"]

    assert cross["independent_python_implementation_matches_helper"] is True
    assert cross["rust_or_non_python_port_still_required"] is True
    assert cross["mismatch_count"] == 0

    assert cospectral["formal_cospectral_construction_still_required"] is True
    assert cospectral["k8_duplicate_hash_observations_found"] is True
    assert cospectral["k8_distinct_m_s_collision_found"] is False
    k2 = next(row for row in cospectral["rows"] if row["k"] == 2)
    assert k2["distinct_m_s_collisions"] > 0


def test_directed_followon_records_extension_requirement() -> None:
    data = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
    directed = data["sims"]["SIM-DIRECTED-SPECTRAL-02"]

    assert directed["undirected_closure_s_hash_equal_under_edge_reversal"] is True
    assert directed["candidate_directional_flow_hash_distinguishes_reversal"] is True
    assert directed["directed_flow_claims_require_extra_commitment_channel"] is True
    assert directed["candidate_directional_proxy_is_not_ratified_design"] is True


def test_followon_markdown_answers_dependency_question() -> None:
    text = RESULT_MD.read_text(encoding="utf-8")

    assert "Can continue now:" in text
    assert "Blocked until later SENSITIVE gates:" in text
    assert "Public paper release or any external publication" in text
    assert "Activating `S(t)` in epoch commitments" in text
    assert "Activating PoSK as an admission gate" in text
    assert "sample_size=64, nonce_count=4" in text
    assert "distinct-M `S(t)` collisions at k=2 but not at k=8" in text
    assert "k=8 duplicate hash observations had identical `M(t)` roots" in text


def test_paper_integrates_followon_repairs_without_activation_claims() -> None:
    text = PAPER.read_text(encoding="utf-8")

    assert "2026-05-22 Follow-On SIM Addendum" in text
    assert "sim_posk_param_02_multiple_nonce_calibration_complete=true" in text
    assert "sim_cospectral_01_bounded_random_k8_distinct_m_collision_found=false" in text
    assert "S(*t*) is not claimed to be a standalone unique graph identity" in text
    assert "not asserted to be injective over graphs" in text
    assert "short response timeout calibrated to local computation" in text
    assert "sample_size=64" in text
    assert "nonce_count=4" in text
    assert "Spectral equality alone does not imply isomorphism" in text
    assert "does not authorize publication" in text


def test_transcript_spec_and_forward_plan_record_followon_status() -> None:
    spec = TRANSCRIPT_SPEC.read_text(encoding="utf-8")
    plan = FORWARD_1459.read_text(encoding="utf-8")

    assert "sample_size=64" in spec
    assert "nonce_count=4" in spec
    assert "Non-Python cross-implementation vector reproduction" in spec
    assert "SIM-DIRECTED-SPECTRAL-02" in spec

    assert "Follow-on internal SIM evidence recorded" in plan
    assert "sim_spectral_crossimpl_02_python_vector_conformance=true" in plan
    assert "sim_directed_spectral_02_extension_required=true" in plan
    assert "formal/crafted cospectral-work obligation" in plan


def test_followon_run_all_is_deterministic_against_recorded_json() -> None:
    recorded = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
    rerun = followon.run_all()

    assert rerun["gate_tokens"] == recorded["gate_tokens"]
    assert (
        rerun["sims"]["SIM-POSK-PARAM-02"]["recommended_minimum"]
        == recorded["sims"]["SIM-POSK-PARAM-02"]["recommended_minimum"]
    )
    assert (
        rerun["sims"]["SIM-COSPECTRAL-01"]["rows"]
        == recorded["sims"]["SIM-COSPECTRAL-01"]["rows"]
    )
