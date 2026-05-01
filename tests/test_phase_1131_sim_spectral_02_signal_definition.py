"""Phase 1131 — SIM-SPECTRAL-02 signal definition tests."""

from __future__ import annotations

import json
import pathlib
import re

from ilc_core.analysis.laplacian_analytics import THETA_FLOOR


ROOT = pathlib.Path(__file__).resolve().parents[1]
SIGNAL_DEF = ROOT / "docs/sims/sim_spectral_02/sim_spectral_02_signal_definition_v0.1.md"
TIME_SERIES = ROOT / "out/sim_provenance_01_time_series.json"


def _read_signal_def() -> str:
    return SIGNAL_DEF.read_text(encoding="utf-8")


def test_t1_signal_definition_exists_with_closing_token() -> None:
    assert SIGNAL_DEF.exists()
    assert "sim_spectral_02_signal_definition_committed" in _read_signal_def()


def test_t2_sim_provenance_time_series_is_parseable_json() -> None:
    data = json.loads(TIME_SERIES.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert len(data) == 100
    assert {len(values) for values in data.values()} == {200}


def test_t3_theta_floor_imported_from_laplacian_analytics() -> None:
    assert THETA_FLOOR == 0.001


def test_t4_signal_definition_declares_at_least_three_k_candidates() -> None:
    src = _read_signal_def()
    k_values = set(re.findall(r"`(0\.[0-9]+|1\.[0-9]+)`", src))
    assert {"0.3", "0.7", "1.2"}.issubset(k_values)
    assert len(k_values) >= 3


def test_t5_durability_inventory_declares_all_data_classes() -> None:
    src = _read_signal_def()
    assert "OBSERVED" in src
    assert "SYNTHETIC" in src
    assert "EXCLUDED" in src
    assert "| `provenance_descendant_count` | OBSERVED |" in src
