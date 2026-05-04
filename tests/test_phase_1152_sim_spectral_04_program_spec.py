"""Phase 1152 — SIM-SPECTRAL-04 program spec."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_program_spec_exists_with_token() -> None:
    text = _read("docs/sims/sim_spectral_04/program.md")
    assert "sim_spectral_04_program_committed_phase_1152" in text


def test_program_spec_names_projection_build_step() -> None:
    text = _read("docs/sims/sim_spectral_04/program.md")
    assert "tools/build_genesis_claim_composition_projection.py" in text
    assert "out/genesis_claim_composition_projection_v0.1.json" in text
    assert "out/genesis_32_node_composability_audit_v0.1.json" in text


def test_program_spec_mandates_matched_size_controls() -> None:
    text = _read("docs/sims/sim_spectral_04/program.md")
    assert "matched-size S3 and G2 controls as mandatory primary controls" in text
    assert "matched_size_controls_required_for_future_spectral_sims" in text


def test_program_spec_records_cdl085_gate_criteria() -> None:
    text = _read("docs/sims/sim_spectral_04/program.md")
    assert "Matched-size S3/S1 must be below `0.6416011282246747`" in text
    assert "Matched-size G2/S1 must be below `0.8640456434014127`" in text
    assert "would not automatically" in text


def test_program_spec_excludes_signed_artifact_mutation() -> None:
    text = _read("docs/sims/sim_spectral_04/program.md")
    assert "mutation of `out/genesis_core_star_map_v0.1.json`" in text
    assert "out/genesis_compile_coverage_diagnostic_v0.1.json" in text
    assert "opening or ratification of CDL-085" in text
