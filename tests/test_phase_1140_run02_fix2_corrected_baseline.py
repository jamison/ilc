import collections
import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "out" / "sim_spectral_02_run02_fix2_summary.json"
NOTES = ROOT / "docs" / "sims" / "sim_spectral_02" / "run02_fix2_raw_notes_1140.md"


def _rows() -> list[dict]:
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def test_f1_run02_fix2_summary_has_333_entries() -> None:
    rows = _rows()
    assert len(rows) == 333
    assert collections.Counter(row["scenario"] for row in rows) == {
        "S1": 117,
        "S2": 54,
        "S3": 54,
        "S4": 54,
        "G1": 18,
        "G2": 18,
        "G3": 18,
    }


def test_f2_run02_fix2_preserves_original_track_distribution() -> None:
    rows = _rows()
    assert collections.Counter(row["track"] for row in rows) == {
        "A": 126,
        "B": 72,
        "C": 72,
        "D1": 21,
        "D2": 21,
        "D3": 21,
    }


def test_f3_run02_fix2_uses_default_greek_weights() -> None:
    for row in _rows():
        assert row["alpha"] == 1.0
        assert row["beta"] == 1.0
        assert row["gamma"] == 1.0
        assert row["delta"] == 1.0


def test_f4_structural_impedance_check_is_not_vacuous() -> None:
    rows = _rows()
    nonzero_entries = [
        row for row in rows if any(value != 0.0 for value in row["structural_impedance_per_epoch"])
    ]
    assert len(nonzero_entries) == 72
    assert any(row["scenario"] == "S1" for row in nonzero_entries)
    assert any(row["scenario"] == "S2" for row in nonzero_entries)


def test_f5_corrected_track_a_s3_s1_ratio_is_recorded() -> None:
    rows = [row for row in _rows() if row["track"] == "A"]
    s1 = [row["rolling_slope"] for row in rows if row["scenario"] == "S1"]
    s3 = [row["rolling_slope"] for row in rows if row["scenario"] == "S3"]
    ratio = (sum(s3) / len(s3)) / (sum(s1) / len(s1))
    assert round(ratio, 12) == round(0.6416011282246747, 12)


def test_f6_notes_exist_with_completion_token() -> None:
    text = NOTES.read_text(encoding="utf-8")
    assert "run02_fix2_corrected_baseline_committed_phase_1140" in text
    assert "S3/S1 = 0.6416011282246747" in text
