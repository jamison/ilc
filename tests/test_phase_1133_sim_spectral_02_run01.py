"""Phase 1133 — SIM-SPECTRAL-02 Run 01 evidence tests."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "out/sim_spectral_02_run01_summary.json"
NOTES = ROOT / "docs/sims/sim_spectral_02/run01_raw_notes_1133.md"


def _load_summary() -> list[dict[str, object]]:
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def test_r1_run01_summary_exists_and_is_valid_json_list() -> None:
    assert SUMMARY.exists()
    assert isinstance(_load_summary(), list)


def test_r2_run01_summary_contains_exactly_192_entries() -> None:
    assert len(_load_summary()) == 192


def test_r3_all_four_run01_scenarios_are_present() -> None:
    scenarios = {entry["scenario"] for entry in _load_summary()}
    assert {"S1", "S2", "S3", "S4"}.issubset(scenarios)


def test_r4_raw_notes_exist_with_completion_token() -> None:
    assert NOTES.exists()
    text = NOTES.read_text(encoding="utf-8")
    assert "sim_spectral_02_run01_complete_phase_1133" in text
