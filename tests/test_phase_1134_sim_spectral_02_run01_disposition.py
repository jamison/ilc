"""Phase 1134 — SIM-SPECTRAL-02 Run 01 disposition tests."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
DISPOSITION = ROOT / "docs/sims/sim_spectral_02/run01_disposition_1134_v0.1.md"


def _text() -> str:
    return DISPOSITION.read_text(encoding="utf-8")


def test_d1_disposition_exists_with_completion_token() -> None:
    assert DISPOSITION.exists()
    assert "sim_spectral_02_run01_disposition_committed_phase_1134" in _text()


def test_d2_scenario_a_declared_without_positive_or_negative_tokens() -> None:
    text = _text()
    assert "sim_spectral_02_scenario_a_ambiguous" in text
    assert "_b_positive" not in text
    assert "_c_negative" not in text


def test_d3_track_d_framed_as_connectivity_trust_threshold() -> None:
    text = _text().lower()
    assert "connectivity" in text
    assert "trust threshold" in text


def test_d4_evidentiary_caveat_preserves_observed_provenance_boundary() -> None:
    text = _text()
    assert "provenance_descendant_count" in text
    assert "OBSERVED" in text


def test_d5_coactivity_correction_mentions_ancestor_boundary() -> None:
    text = _text().lower()
    assert "coactivity" in text
    assert "ancestor" in text
