from __future__ import annotations

import re
import subprocess
from pathlib import Path


COMMISSION_PATH = Path("docs/specs/ilc_sim_validator_01_commissioning_711_v0.1.md")
RESULTS_PATH = Path("docs/research/ilc_sim_validator_01_results_v0.1.md")
SIM_PATH = Path("simulations/sim_validator_01_stake_floor_calibration.py")
REQUIRED_HEADINGS = (
    "## 1. Calibrated question and inputs",
    "## 2. Stake floor candidate interval",
    "## 3. Adversary payoff curves",
    "## 4. Sensitivity table",
    "## 5. VRF upgrade threshold recommendation",
    "## 6. Dominant assumptions",
    "## 7. Verdict",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_commission_brief_exists_and_contains_required_token() -> None:
    text = _read(COMMISSION_PATH)
    assert "sim_validator_01_commissioned" in text


def test_results_doc_exists() -> None:
    assert RESULTS_PATH.exists()


def test_results_doc_contains_required_headings() -> None:
    text = _read(RESULTS_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_results_doc_contains_verdict_token() -> None:
    text = _read(RESULTS_PATH)
    assert (
        "sim_validator_01_verdict=pass" in text
        or "sim_validator_01_verdict=fail" in text
    )


def test_results_doc_contains_numeric_stake_floor_interval_token() -> None:
    text = _read(RESULTS_PATH)
    assert re.search(
        r"stake_floor_candidate_interval_micro_ecu\s+\d+-\d+",
        text,
    )


def test_results_doc_contains_numeric_vrf_threshold_token() -> None:
    text = _read(RESULTS_PATH)
    assert re.search(
        r"vrf_upgrade_threshold_validator_count\s+\d+",
        text,
    )


def test_sensitivity_table_section_is_non_empty() -> None:
    text = _read(RESULTS_PATH)
    section = text.split("## 4. Sensitivity table", 1)[1].split(
        "## 5. VRF upgrade threshold recommendation", 1
    )[0]
    assert "| Parameter family |" in section
    assert "adversary gain bound capture bps" in section


def test_simulation_file_is_importable_with_no_side_effects() -> None:
    result = subprocess.run(
        ["python3", "-c", "import simulations.sim_validator_01_stake_floor_calibration"],
        capture_output=True,
        check=True,
        text=True,
    )
    assert result.stdout == ""
