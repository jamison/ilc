"""Phase 1135 — SIM-SPECTRAL-02 Run 02 evidence tests."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUN02 = ROOT / "out/sim_spectral_02_run02_summary.json"
RUN01 = ROOT / "out/sim_spectral_02_run01_summary.json"
NOTES = ROOT / "docs/sims/sim_spectral_02/run02_raw_notes_1135.md"


def _load(path: pathlib.Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def test_r07_run02_summary_exists_and_is_valid_json_list() -> None:
    assert RUN02.exists()
    assert isinstance(_load(RUN02), list)


def test_r08_run02_summary_contains_exactly_333_entries() -> None:
    assert len(_load(RUN02)) == 333


def test_r09_all_four_scenarios_appear_in_track_a_entries() -> None:
    scenarios = {
        entry["scenario"]
        for entry in _load(RUN02)
        if entry.get("track") == "A" and entry.get("track_group") == "A-C"
    }
    assert {"S1", "S2", "S3", "S4"}.issubset(scenarios)


def test_r10_all_three_gaming_probes_appear_in_track_a_entries() -> None:
    probes = {
        entry["scenario"]
        for entry in _load(RUN02)
        if entry.get("track") == "A" and entry.get("track_group") == "gaming"
    }
    assert {"G1", "G2", "G3"}.issubset(probes)


def test_r11_track_d_has_all_modes_and_density_multipliers() -> None:
    track_d = [entry for entry in _load(RUN02) if entry.get("track_group") == "D"]
    assert {entry["track"] for entry in track_d} == {"D1", "D2", "D3"}
    assert {entry["density_multiplier"] for entry in track_d} == {0, 1, 2, 4, 6, 8, 10}


def test_r12_run01_summary_still_contains_192_entries() -> None:
    assert len(_load(RUN01)) == 192


def test_r13_run02_raw_notes_exist_with_completion_token() -> None:
    assert NOTES.exists()
    assert "sim_spectral_02_run02_complete_phase_1135" in NOTES.read_text(
        encoding="utf-8"
    )
