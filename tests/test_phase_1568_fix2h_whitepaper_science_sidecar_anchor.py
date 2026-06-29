import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/specs/ilc_whitepaper_science_claim_routing_matrix_v0.1.json"
ANCHOR = ROOT / "docs/specs/ilc_native_sidecar_typed_subgraph_anchor_v0.1.md"
TYPE_REGISTRY = ROOT / "ilc_core/bundle/type_registry.py"


REQUIRED_CLAIMS = {
    "directed_morphogenetic_hypergraph",
    "normalized_hypergraph_laplacian",
    "merkle_laplacian_dual_commitment",
    "posk_challenge_bound_proof",
    "ecu_from_accepted_poil",
    "inverted_ecu_spend_to_keep",
    "inverse_ecu_backward_attribution",
    "systolic_diastolic_werner_pressure",
    "jury_assignment_privacy_and_discoverability",
    "subjective_aesthetic_lane",
    "sidecars_as_typed_subgraphs",
    "engram_pool_modification_threat",
    "four_layer_epistemic_independence",
    "eu_sovereign_ai_national_cluster_fiedler",
    "jepa_world_model_representational_independence",
    "substrate_custody_attestation",
    "last_mile_harness_sidecar_pipeline",
    "multi_model_endorsement_co_attestation",
    "model_router_provider_agnostic",
    "werner_credit_idle_capacity_loop",
}


def test_matrix_has_required_claims_and_schema():
    payload = json.loads(MATRIX.read_text())
    assert payload["schema_version"] == "ilc_whitepaper_science_claim_routing_matrix.v0.1"
    claim_ids = {row["claim_id"] for row in payload["claims"]}
    assert REQUIRED_CLAIMS <= claim_ids
    assert len(payload["claims"]) >= len(REQUIRED_CLAIMS)


def test_matrix_records_public_rc_non_claims():
    payload = json.loads(MATRIX.read_text())
    assert "not_public_rc_activation" in payload["non_claims"]
    assert "not_type_registry_activation" in payload["non_claims"]
    assert "not_public_sidecar_serving" in payload["non_claims"]


def test_sidecar_anchor_keeps_public_surfaces_default_off():
    text = ANCHOR.read_text()
    assert "public_serving_enabled=false" in text
    assert "public_rc_exclude_private_agentic_harness=true" in text
    assert "model_router_exists=false" in text
    assert "gaia_x_adapter_exists=false" in text
    assert "werner_credit_exists=false" in text


def test_adr0035_type_registry_guard_not_cleared():
    text = TYPE_REGISTRY.read_text()
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in text
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = False" not in text
