import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "out/sim_atlas_precision_replay_1545p_fix20.json"
REPORT_PATH = ROOT / "docs/sims/sim_atlas_precision_replay_1545p_fix20_v0.1.md"


def _payload() -> dict:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def test_phase_1545p_fix20_outputs_exist_and_pass() -> None:
    assert JSON_PATH.exists()
    assert REPORT_PATH.exists()
    payload = _payload()
    assert payload["schema_version"] == "sim_atlas_precision_replay_1545p_fix20.v0.1"
    assert payload["phase"] == "1545p-Fix20"
    assert payload["status"] == "PASS"


def test_phase_1545p_fix20_preserves_fix19_golden_recall() -> None:
    golden = _payload()["golden_replay"]
    assert golden["expected_atom_count"] == 64
    assert golden["covered_atom_count"] == 64
    assert golden["missing_atom_count"] == 0
    assert golden["recall_ratio"] == "64/64"


def test_phase_1545p_fix20_negative_precision_controls_pass() -> None:
    controls = _payload()["negative_controls"]
    assert controls["control_count"] == 6
    assert controls["passed_count"] == 6
    assert controls["failed_count"] == 0
    assert controls["precision_control_ratio"] == "6/6"
    for control in controls["controls"]:
        assert control["forbidden_hits"] == []
        assert control["missing_required"] == []


def test_phase_1545p_fix20_rejected_replay_is_review_only() -> None:
    replay = _payload()["rejected_file_replay"]
    assert replay["replay_file_count"] == 12
    assert replay["total_detected_atom_count"] == 49
    assert replay["review_candidate_count"] == 12
    allowed_classes = {
        "authority_with_nonactivation_boundary_review",
        "schema_boundary_review",
        "candidate_state_review",
        "schema_support_review",
        "no_candidate_signal",
    }
    for row in replay["files"]:
        assert row["candidate_review_class"] in allowed_classes
        assert "promote" not in row["candidate_review_class"]


def test_phase_1545p_fix20_manual_spot_checks_pass_with_caveat() -> None:
    manual = _payload()["manual_spot_checks"]
    assert manual["spot_check_count"] == 5
    assert manual["passed_count"] == 5
    assert manual["failed_count"] == 0
    assert manual["spot_check_ratio"] == "5/5"
    assert "do not establish two-standard-deviation confidence" in manual["statistical_caveat"]
    for row in manual["checks"]:
        assert row["missing_expected"] == []
        assert row["forbidden_hits"] == []


def test_phase_1545p_fix20_tokens_and_non_claims() -> None:
    payload = _payload()
    tokens = set(payload["tokens"])
    assert "sim_atlas_precision_replay_committed_phase_1545p_fix20" in tokens
    assert "atlas_negative_precision_controls_passed_phase_1545p_fix20" in tokens
    assert "atlas_rejected_file_replay_completed_phase_1545p_fix20" in tokens
    assert "manual_spot_check_sample_recorded_phase_1545p_fix20" in tokens
    assert "public_path_remains_blocked_phase_1545p_fix20" in tokens
    non_claims = "\n".join(payload["non_claims"])
    assert "No canonical Genesis graph mutation occurred." in non_claims
    assert "No Genesis v0.4 signing occurred." in non_claims
    assert "No public RC activation occurred." in non_claims
    assert "No Atlas edge candidate is promoted by this SIM." in non_claims


def test_phase_1545p_fix20_report_records_research_only_boundary() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    assert "SIM-ATLAS-PRECISION-01" in report
    assert "PUBLIC_RC_EXCLUDE: atlas_precision_replay_research_only" in report
    assert "two-standard-deviation statistical estimate" in report
    assert "graph_delta=support_only" in report
    assert "atlas_rejected_file_candidates_not_promoted_phase_1545p_fix20" in report
