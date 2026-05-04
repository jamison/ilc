from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISPOSITION = ROOT / "docs/sims/sim_spectral_04/disposition_1162_v0.1.md"


def test_phase_1162_disposition_exists() -> None:
    assert DISPOSITION.exists()


def test_phase_1162_contains_exactly_one_gate_verdict_token() -> None:
    text = DISPOSITION.read_text(encoding="utf-8")
    assert text.count("sim_spectral_04_gate_pass") == 0
    assert text.count("sim_spectral_04_gate_fail") == 1


def test_phase_1162_fail_path_records_specific_diagnosis() -> None:
    text = DISPOSITION.read_text(encoding="utf-8")
    assert "cdl_085_sim_gated_pending_sybil_discrimination_resolution" in text
    assert "Matched-size S3/S1" in text
    assert "FAIL" in text


def test_phase_1162_comparison_table_references_raw_authority_baseline() -> None:
    text = DISPOSITION.read_text(encoding="utf-8")
    assert "SIM-SPECTRAL-03 raw authority" in text
    assert "0.21355627860399237" in text
    assert "1.6736470076736112" in text
    assert "2.2539040876901315" in text


def test_phase_1162_blocks_phase_1163_execution() -> None:
    text = DISPOSITION.read_text(encoding="utf-8")
    assert "Phase 1163 does not execute" in text
    assert "no CDL-085 opening is authorized" in text
