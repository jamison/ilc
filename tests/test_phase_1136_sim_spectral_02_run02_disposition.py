"""
Phase 1136: SIM-SPECTRAL-02 Run 02 Disposition Evidence Tests
Tests D01–D05
"""

import os
import pathlib

REPO_ROOT = pathlib.Path(__file__).parent.parent
DISPOSITION_PATH = REPO_ROOT / "docs/sims/sim_spectral_02/run02_disposition_1136_v0.1.md"
RAW_NOTES_PATH = REPO_ROOT / "docs/sims/sim_spectral_02/run02_raw_notes_1135.md"


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def test_d01_disposition_file_exists():
    """D01: run02_disposition_1136_v0.1.md exists."""
    assert DISPOSITION_PATH.exists(), f"Missing: {DISPOSITION_PATH}"


def test_d02_disposition_contains_committed_token():
    """D02: Disposition file contains sim_spectral_02_run02_disposition_committed_phase_1136."""
    text = _read(DISPOSITION_PATH)
    assert "sim_spectral_02_run02_disposition_committed_phase_1136" in text, (
        "Missing closing token: sim_spectral_02_run02_disposition_committed_phase_1136"
    )


def test_d03_disposition_contains_genesis_seed_carry_forward_token():
    """D03: Disposition file contains sim_spectral_02_genesis_seed_carry_forward_phase_1136."""
    text = _read(DISPOSITION_PATH)
    assert "sim_spectral_02_genesis_seed_carry_forward_phase_1136" in text, (
        "Missing closing token: sim_spectral_02_genesis_seed_carry_forward_phase_1136"
    )


def test_d04_disposition_contains_bootstrap_adr_proposed_token():
    """D04: Disposition file contains sim_spectral_02_bootstrap_adr_proposed_phase_1136."""
    text = _read(DISPOSITION_PATH)
    assert "sim_spectral_02_bootstrap_adr_proposed_phase_1136" in text, (
        "Missing closing token: sim_spectral_02_bootstrap_adr_proposed_phase_1136"
    )


def test_d05_raw_notes_contains_beta_calibration_probe_section():
    """D05: run02_raw_notes_1135.md contains the Post-Run β Calibration Probe section."""
    text = _read(RAW_NOTES_PATH)
    assert "Post-Run β Calibration Probe" in text, (
        "run02_raw_notes_1135.md is missing the '## 9. Post-Run β Calibration Probe' section"
    )
