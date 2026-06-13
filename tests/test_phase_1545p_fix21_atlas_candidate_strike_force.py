import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_JSON = ROOT / "out/sim_atlas_candidate_strike_force_1545p_fix21.json"
CONTRACT_JSON = ROOT / "out/atlas_research/genesis_atlas_extraction_contract_1545p_fix21.json"
QUEUE_JSONL = ROOT / "out/atlas_research/genesis_atlas_candidate_queue_1545p_fix21.jsonl"
REDUCED_JSON = ROOT / "out/atlas_research/genesis_atlas_reduced_candidates_1545p_fix21.json"
VARIANTS_JSON = ROOT / "out/genesis_atlas_v0.4_candidate_variants_1545p_fix21.json"
FULL_JSON = ROOT / "out/genesis_atlas_v0.4_full_candidate_1545p_fix21.json"
REPORT_MD = ROOT / "docs/sims/sim_atlas_candidate_strike_force_1545p_fix21_v0.1.md"
REVIEW_MD = ROOT / "docs/specs/ilc_genesis_atlas_candidate_review_packet_1545p_fix21_v0.1.md"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix21_outputs_exist_and_pass() -> None:
    for path in [SIM_JSON, CONTRACT_JSON, QUEUE_JSONL, REDUCED_JSON, VARIANTS_JSON, FULL_JSON, REPORT_MD, REVIEW_MD]:
        assert path.exists(), path
    payload = read_json(SIM_JSON)
    assert payload["schema_version"] == "sim_atlas_candidate_strike_force_1545p_fix21.v0.1"
    assert payload["phase"] == "1545p-Fix21"
    assert payload["status"] == "PASS"


def test_fix21_contract_and_calibration_battery_pass() -> None:
    payload = read_json(SIM_JSON)
    battery = payload["sim_battery"]
    assert battery["checks"]["contract_required_fields_present"] is True
    assert battery["checks"]["golden_recall_preserved"] is True
    assert battery["checks"]["negative_controls_pass"] is True
    assert battery["checks"]["manual_spot_checks_pass"] is True
    assert battery["checks"]["expanded_corpus_pass"] is True
    assert battery["expanded_corpus"]["expanded_corpus_file_count"] == 36
    assert battery["expanded_corpus"]["pass_ratio"] == "36/36"


def test_fix21_candidate_queue_and_reducer_are_research_only() -> None:
    payload = read_json(SIM_JSON)
    queue = payload["sim_battery"]["candidate_queue"]
    reduced = payload["reduced_candidates"]
    assert queue["atom_candidate_count"] == 4097
    assert queue["source_file_count"] == 1162
    assert reduced["selected_source_candidate_count"] == 240
    assert payload["sim_battery"]["checks"]["no_extracted_candidate_promoted_to_genesis_core"] is True

    first_queue_line = QUEUE_JSONL.read_text(encoding="utf-8").splitlines()[0]
    first_record = json.loads(first_queue_line)
    assert first_record["authority_boundary"] == "review_only_not_promoted"
    assert first_record["promotion_class"] != "genesis_core_candidate"


def test_fix21_candidate_variants_are_endpoint_valid_and_tiered() -> None:
    variants = read_json(VARIANTS_JSON)
    assert variants["recommended_variant"] == "core_plus_common_registry"
    summary = read_json(SIM_JSON)["sim_battery"]["variants"]
    assert summary["core_only"]["node_count"] == 57
    assert summary["core_plus_common_registry"]["node_count"] == 75
    assert summary["core_plus_hydration"]["node_count"] == 79
    assert summary["maximal_research"]["node_count"] == 322
    for variant in summary.values():
        assert variant["invalid_endpoint_count"] == 0
    assert summary["maximal_research"]["tier_counts"]["support_research"] == 240


def test_fix21_full_candidate_is_unsigned_support_only() -> None:
    full = read_json(FULL_JSON)
    assert full["candidate_status"] == "unsigned_support_only_not_canonical"
    assert full["recommended_signing_input"] == "core_plus_common_registry"
    assert full["tiers_are_authoritative"] is False
    non_claims = "\n".join(full["non_claims"])
    assert "No canonical Genesis graph mutation occurred." in non_claims
    assert "No Genesis v0.4 signing occurred." in non_claims
    assert "No public RC activation occurred." in non_claims
    assert "No extracted Atlas edge candidate is promoted to signed Genesis core by this SIM." in non_claims


def test_fix21_human_review_packet_preserves_block6_boundary() -> None:
    report = REPORT_MD.read_text(encoding="utf-8")
    review = REVIEW_MD.read_text(encoding="utf-8")
    assert "SIM-ATLAS-CANDIDATE-STRIKE-FORCE-01" in report
    assert "PUBLIC_RC_EXCLUDE: atlas_candidate_strike_force_research_only" in report
    assert "Use `core_plus_common_registry` as the next human-review target" in review
    assert "Do not use `maximal_research` as a signing target." in review
    assert "does not authorize public RC, signing, guard clearance" in review
