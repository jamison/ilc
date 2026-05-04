"""Phase 1150 — GENESIS-COMPILE checkpoint #2."""

from __future__ import annotations

import hashlib
import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SIGNED_V01_DIAGNOSTIC_SHA256 = "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> object:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_c1_diagnostic_exists_and_parses_required_keys() -> None:
    diagnostic = _json("out/genesis_compile_coverage_diagnostic_v0.2_candidate.json")
    assert isinstance(diagnostic, dict)
    assert "authority_traceability" in diagnostic
    assert "compile_coverage" in diagnostic
    assert diagnostic["compile_coverage"]["core_nodes_total"] == 36


def test_c2_authority_traceability_gate_passes() -> None:
    diagnostic = _json("out/genesis_compile_coverage_diagnostic_v0.2_candidate.json")
    authority = diagnostic["authority_traceability"]
    assert authority["authority_traceable_core_nodes"] >= 34
    assert authority["authority_traceable_core_nodes"] == 36
    assert authority["authority_traceable_core_nodes_ratio"] == "1.000000"


def test_c3_signed_v01_diagnostic_hash_is_unchanged() -> None:
    path = ROOT / "out/genesis_compile_coverage_diagnostic_v0.1.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == SIGNED_V01_DIAGNOSTIC_SHA256


def test_c4_checkpoint_report_records_pass_and_legacy_verdict_boundary() -> None:
    text = _read("docs/sims/sim_spectral_02/genesis_compile_checkpoint_2_1150_v0.1.md")
    assert "genesis_compile_checkpoint_2_pass" in text
    assert "Tool verdict | `FAIL_CORE_INADEQUATE`" in text
    assert "legacy basis-reachability" in text


def test_c5_versioned_report_exists_without_overwriting_v01_report() -> None:
    assert (ROOT / "docs/sims/sim_spectral_02/genesis_compile_coverage_diagnostic_v0.2_candidate.md").exists()
    assert (ROOT / "docs/sims/sim_spectral_02/genesis_compile_coverage_diagnostic_v0.1.md").exists()
