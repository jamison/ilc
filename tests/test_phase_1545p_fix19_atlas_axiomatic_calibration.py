import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "out/sim_atlas_axiomatic_calibration_1545p_fix19.json"
REPORT_PATH = ROOT / "docs/sims/sim_atlas_axiomatic_calibration_1545p_fix19_v0.1.md"


def _payload() -> dict:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def test_phase_1545p_fix19_outputs_exist_and_pass() -> None:
    assert JSON_PATH.exists()
    assert REPORT_PATH.exists()
    payload = _payload()
    assert payload["schema_version"] == "sim_atlas_axiomatic_calibration_1545p_fix19.v0.1"
    assert payload["phase"] == "1545p-Fix19"
    assert payload["status"] == "PASS"


def test_phase_1545p_fix19_truth_primitive_basis_is_new_seven() -> None:
    payload = _payload()
    assert payload["truth_primitives"] == [
        "assert.truth",
        "validate.claim",
        "contradict.assert",
        "refute.claim",
        "revise.assert",
        "link.claim",
        "commit.epoch",
    ]
    assert "star.map" not in payload["truth_primitives"]


def test_phase_1545p_fix19_dual_corpus_and_recall_metrics() -> None:
    metrics = _payload()["metrics"]
    assert metrics["file_count"] == 16
    assert metrics["programmatic_file_count"] == 8
    assert metrics["semantic_file_count"] == 8
    assert metrics["expected_atom_count"] == 64
    assert metrics["found_atom_count"] == 64
    assert metrics["missing_atom_count"] == 0
    assert metrics["atom_recall_ratio"] == "64/64"
    assert metrics["recipe_coverage_ratio"] == "7/7"


def test_phase_1545p_fix19_recipe_library_covers_authority_and_refutation() -> None:
    recipe_library = _payload()["recipe_library"]
    assert recipe_library["authority_assertion"] == ["assert.truth", "link.claim"]
    assert recipe_library["activation_refutation"] == [
        "assert.truth",
        "refute.claim",
        "link.claim",
    ]
    assert recipe_library["contradiction_guard"] == [
        "contradict.assert",
        "refute.claim",
        "link.claim",
    ]
    assert recipe_library["canonicalization_validation"] == [
        "validate.claim",
        "commit.epoch",
        "link.claim",
    ]


def test_phase_1545p_fix19_programmatic_and_semantic_files_are_distinct() -> None:
    payload = _payload()
    programmatic = {row["path"] for row in payload["file_results"] if row["camp"] == "programmatic"}
    semantic = {row["path"] for row in payload["file_results"] if row["camp"] == "semantic"}
    assert len(programmatic) == 8
    assert len(semantic) == 8
    assert programmatic.isdisjoint(semantic)
    assert "ilc_core/genesis/assertion_schema.py" in programmatic
    assert "docs/sims/sim_genesis_01_v04_candidate_assembly_1545p_fix18_v0.1.md" in semantic


def test_phase_1545p_fix19_non_claims_and_tokens_are_present() -> None:
    payload = _payload()
    tokens = set(payload["tokens"])
    assert "sim_atlas_axiomatic_calibration_committed_phase_1545p_fix19" in tokens
    assert "golden_corpus_dual_camp_recorded_phase_1545p_fix19" in tokens
    assert "truth_primitive_recipe_calibration_recorded_phase_1545p_fix19" in tokens
    assert "atlas_model_training_target_recorded_phase_1545p_fix19" in tokens
    assert "public_path_remains_blocked_phase_1545p_fix19" in tokens
    non_claims = "\n".join(payload["non_claims"])
    assert "No canonical Genesis graph mutation occurred." in non_claims
    assert "No Genesis v0.4 signing occurred." in non_claims
    assert "No public RC activation occurred." in non_claims
    assert "No Atlas edge candidate is promoted by this SIM." in non_claims


def test_phase_1545p_fix19_report_records_research_only_boundary() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    assert "SIM-ATLAS-AXIOMATIC-01" in report
    assert "PUBLIC_RC_EXCLUDE: atlas_axiomatic_calibration_research_only" in report
    assert "graph_delta=support_only" in report
    assert "atlas_extractor_training_not_canonical_promotion_phase_1545p_fix19" in report
