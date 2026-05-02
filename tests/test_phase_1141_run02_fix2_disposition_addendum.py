import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADDENDUM = (
    ROOT
    / "docs"
    / "sims"
    / "sim_spectral_02"
    / "run02_fix2_disposition_addendum_1141_v0.1.md"
)
SUMMARY = ROOT / "out" / "sim_spectral_02_run02_fix2_summary.json"


def test_a1_addendum_exists_with_completion_token() -> None:
    text = ADDENDUM.read_text(encoding="utf-8")
    assert "run02_fix2_disposition_addendum_committed_phase_1141" in text


def test_a2_addendum_supersedes_phase_1136_numeric_baseline() -> None:
    text = ADDENDUM.read_text(encoding="utf-8")
    assert "supersedes Phase 1136" in text
    assert "out/sim_spectral_02_run02_fix2_summary.json" in text


def test_a3_corrected_s3_s1_ratio_matches_summary() -> None:
    rows = json.loads(SUMMARY.read_text(encoding="utf-8"))
    track_a = [row for row in rows if row["track"] == "A"]
    s1 = [row["rolling_slope"] for row in track_a if row["scenario"] == "S1"]
    s3 = [row["rolling_slope"] for row in track_a if row["scenario"] == "S3"]
    ratio = (sum(s3) / len(s3)) / (sum(s1) / len(s1))

    text = ADDENDUM.read_text(encoding="utf-8")
    assert round(ratio, 12) == round(0.6416011282246747, 12)
    assert "S3/S1 = 0.6416011282246747" in text


def test_a4_scenario_b_advisory_remains_in_force() -> None:
    text = ADDENDUM.read_text(encoding="utf-8")
    assert "Scenario B Advisory remains in force" in text
    assert "does not resolve S3 Sybil discrimination" in text


def test_a5_sim_spectral_03_must_use_corrected_baseline() -> None:
    text = ADDENDUM.read_text(encoding="utf-8")
    assert "SIM-SPECTRAL-03 must use" in text
    assert "corrected Run 02 comparison baseline" in text
