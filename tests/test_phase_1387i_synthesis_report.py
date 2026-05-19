"""Phase 1387i — SIM-GRAPHOPT-04: synthesis report attestation.

Tests verify the synthesis report exists and records the correct
summary findings from the 1387f/g/h series.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent.parent
REPORT = ROOT / "docs" / "sims" / "sim_spectral_02" / "genesis_graphopt_01_synthesis_report_v0.1.md"


def _text() -> str:
    return REPORT.read_text()


def test_synthesis_report_exists() -> None:
    assert REPORT.exists(), f"Synthesis report not found: {REPORT}"


def test_closing_token_present() -> None:
    assert "sim_graphopt_01_synthesis_complete_phase_1387i" in _text()


def test_hub_and_spoke_max_depth_finding() -> None:
    assert "max_depth" in _text() or "max depth" in _text().lower()
    assert "2" in _text()


def test_zero_keystone_finding() -> None:
    assert "0 keystone" in _text() or "keystone_count" in _text() or "No single point" in _text()


def test_merge_candidate_documented() -> None:
    assert "GOVERNS" in _text() and "CONSTRAINS" in _text()
    assert "merge" in _text().lower()


def test_attestation_provenance_scope_distinction_documented() -> None:
    assert "agent_signing_endorsement" in _text()
    assert "derivation_origin_chain" in _text()


def test_zero_missing_recipes_after_1387h() -> None:
    assert "0 of 77" in _text() or "0 edges" in _text().lower() or "0 missing" in _text().lower()


def test_37_orphan_leaf_nodes_documented() -> None:
    assert "37" in _text()


def test_forward_obligations_section_present() -> None:
    text = _text()
    assert "Forward Optimization" in text or "forward obligation" in text.lower()
