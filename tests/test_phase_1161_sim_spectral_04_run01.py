import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "out/sim_spectral_04_run01_summary.json"
NOTES = ROOT / "docs/sims/sim_spectral_04/run01_raw_notes_1161.md"


def _summary() -> dict:
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def test_phase_1161_summary_exists_with_token() -> None:
    data = _summary()
    assert data["artifact"] == "sim_spectral_04_run01_summary"
    assert data["phase"] == "1161"
    assert data["token"] == "sim_spectral_04_run01_committed_phase_1161"


def test_phase_1161_projection_shape() -> None:
    data = _summary()
    assert data["projection_vertex_count"] == 56
    assert data["projection_edge_count"] == 125
    assert data["projection_hash"] == "fc1496ea12319338d10db0e63f78087b3a72c46a31507d09b35234c79a45a2ab"


def test_phase_1161_gate_preview_values() -> None:
    gate = _summary()["gate_evaluation"]
    assert gate["s1_projection_positive_all_seeds"] is True
    assert gate["matched_s3_s1_below_threshold_all_seeds"] is False
    assert gate["matched_g2_s1_below_threshold_all_seeds"] is True
    assert gate["no_result_depends_on_raw_100_controls"] is True
    assert gate["sim_spectral_04_gate_pass"] is False


def test_phase_1161_raw_notes_record_required_controls() -> None:
    text = NOTES.read_text(encoding="utf-8")
    assert "S3_matched" in text
    assert "G2_matched" in text
    assert "S3_raw_100" in text
    assert "G2_raw_100" in text
