import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_MD = ROOT / "docs/specs/ilc_whole_graph_atlas_objective_contract_1545p_fix24_v0.1.md"
CONTRACT_JSON = ROOT / "out/atlas_research/whole_graph_atlas_objective_contract_1545p_fix24.json"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix24_whole_graph_atlas_objective_contract_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


REQUIRED_TOKENS = {
    "whole_graph_atlas_objective_contract_committed_phase_1545p_fix24",
    "v04_v05_atlas_scope_boundary_recorded_phase_1545p_fix24",
    "block6_phase1573_scope_mismatch_recorded_phase_1545p_fix24",
    "atlas_objective_vector_v2_committed_phase_1545p_fix24",
    "atlas_signing_gate_not_reached_phase_1545p_fix24",
    "public_path_remains_blocked_phase_1545p_fix24",
}


OBJECTIVE_FIELDS = {
    "objective_id",
    "purpose",
    "input_artifacts",
    "measurement_method",
    "numerator",
    "denominator",
    "pass_condition",
    "warning_condition",
    "failure_condition",
    "known_false_positive_modes",
    "known_false_negative_modes",
    "promotion_boundary",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _contract() -> dict:
    return json.loads(_read(CONTRACT_JSON))


def test_contract_files_and_tokens_present():
    surfaces = [_read(CONTRACT_MD), _read(WALKTHROUGH), _read(STATUS), _read(PLANNING)]
    for token in REQUIRED_TOKENS:
        assert token in _read(CONTRACT_JSON)
        assert any(token in surface for surface in surfaces)


def test_json_schema_records_rootedness_and_scope_mismatch():
    data = _contract()
    standard = data["genesis_rootedness_standard"]

    assert data["block6_phase1573_scope"]["fix22_fix23_full_repo_signing_authorized"] is False
    assert data["block6_phase1573_scope"]["current_authorized_input"] == "out/genesis_core_star_map_v0.4_candidate.json"
    assert data["inputs"]["fix18_core_candidate"]["nodes"] == 57
    assert data["inputs"]["fix22_full_repo_candidate"]["nodes"] == 10029
    assert data["inputs"]["fix23_lmdb_projection"]["local_unsigned_projection"] is True

    assert standard["authority_root_node"] == "artifact:genesis_intent_attestation_init_authority_map"
    assert "genesis_bound_transition_envelope_view" in standard["genesis_rootedness_views"]
    assert "IMPLEMENTS" in standard["accepted_typed_trace_roles"]
    assert "CLASSIFIED_BY" in standard["accepted_typed_trace_roles"]
    assert "authority" in standard["lambda2_not_sufficient_for"]
    assert "governance_effect" in standard["merkle_not_sufficient_for"]


def test_every_objective_has_required_fields_and_hard_invariants_are_separate():
    data = _contract()
    objective_ids = {entry["objective_id"] for entry in data["objective_vector"]}

    assert len(data["objective_vector"]) >= 10
    assert "endpoint_validity" in data["tier1_hard_invariants"]
    assert "privacy_tier_preservation" in data["tier1_hard_invariants"]
    assert "anti_gaming_penalty" not in data["tier1_hard_invariants"]
    assert "spectral_laplacian_health" in data["tier2_objective_vector"]
    assert "no_activation_preservation" not in data["tier2_objective_vector"]

    for entry in data["objective_vector"]:
        assert OBJECTIVE_FIELDS <= set(entry)
        assert entry["objective_id"] in objective_ids
        assert entry["promotion_boundary"]


def test_docs_preserve_non_claims_and_no_placeholder_ellipses():
    combined = "\n".join([_read(CONTRACT_MD), _read(WALKTHROUGH)])
    normalized = " ".join(combined.split())

    assert "No Genesis v0.4 signing occurred." in combined
    assert "No public RC activation occurred." in combined
    assert "No ADR or CDL mutation occurred." in combined
    assert "not semantically rooted Genesis Atlas nodes" in normalized
    assert "signed source-tree or release manifest as hashed repository material" in normalized
    assert "..." not in combined
    assert "…" not in combined
