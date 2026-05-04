"""Phase 1172 — CDL-085 opening."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> object:
    return json.loads(_read(path))


def test_cdl_085_opening_spec_exists_and_is_open() -> None:
    text = _read("docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md")
    assert "# CDL-085: Werner Phi-Bound Provenance Equivalence Limit" in text
    assert "**Status:** OPEN" in text
    assert "cdl_085_open_phase_1172" in text
    assert "cdl_085_sim_gate_lifted_phase_1172_sim_spectral_05_gate_pass" in text


def test_cdl_log_has_open_cdl_085_row_and_no_ratification() -> None:
    log = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    row = next(line for line in log.splitlines() if line.startswith("| CDL-085 |"))
    assert "| open |" in row
    assert "opened_phase: 1172" in row
    assert "opened_date: 2026-05-04" in row
    assert "ratified_phase" not in row


def test_cdl_085_opening_cites_sim_spectral_05_and_adr_0037_criterion() -> None:
    text = _read("docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md")
    assert "sim_spectral_05_gate_pass" in text
    assert "ADR-0037 §3.2" in text
    assert "provenance equivalence criterion" in text
    assert "non-Genesis injection point" in text


def test_cdl_085_opening_does_not_lock_edge_mint_phi_bound() -> None:
    text = _read("docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md")
    assert "`EDGE_MINT_PHI_BOUND` remains unset" in text
    assert "This opening does not:" in text
    assert "set `EDGE_MINT_PHI_BOUND`" in text


def test_phase_1172_walkthrough_records_human_go_and_opening_only_boundary() -> None:
    text = _read("docs/phases/phase_1172_cdl_085_opening_walkthrough.md")
    assert "GO Phase 1172" in text
    assert "CDL-085 status: `OPEN`" in text
    assert "Runtime mutation: none" in text
    assert "Ratification: none" in text


def test_signed_v01_star_map_unchanged() -> None:
    star_map = _json("out/genesis_core_star_map_v0.1.json")
    envelope = _json("out/genesis_signing_root_envelope_v0.1.json")
    assert isinstance(star_map, dict)
    assert len(star_map["nodes"]) == 32
    assert len(star_map["edges"]) == 55
    assert isinstance(envelope, dict)
    assert envelope["envelope_hash"] == ROOT_HASH
