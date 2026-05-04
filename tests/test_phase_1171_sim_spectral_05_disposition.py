"""Phase 1171 — SIM-SPECTRAL-05 Track B run and combined disposition."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> object:
    return json.loads(_read(path))


def test_track_b_summary_exists_and_reports_pass() -> None:
    summary = _json("out/sim_spectral_05_track_b_run_summary.json")
    assert isinstance(summary, dict)
    assert summary["phase"] == 1171
    assert summary["s3_topology"] == "sybil_cluster_branchial"
    assert summary["track_b_verdict"] == "track_b_pass"
    assert summary["gate_verdict"] == "sim_spectral_05_gate_pass"


def test_track_b_convergence_rates_clear_program_thresholds() -> None:
    summary = _json("out/sim_spectral_05_track_b_run_summary.json")
    assert isinstance(summary, dict)
    thresholds = summary["track_b_thresholds"]
    assert summary["s1_convergence_rate"]["mean"] >= thresholds["s1_mean_minimum"]
    assert summary["s3_convergence_rate"]["mean"] <= thresholds["s3_mean_maximum"]
    assert summary["separation"]["mean_delta"] >= thresholds["separation_minimum"]


def test_disposition_contains_track_a_and_track_b_sections() -> None:
    disposition = _read("docs/sims/sim_spectral_05/disposition_1171_v0.1.md")
    assert "## 4. Track A Verdict" in disposition
    assert "## 5. Track B Verdict" in disposition
    assert "track_a_pass" in disposition
    assert "track_b_pass" in disposition


def test_disposition_cites_adr_0037_provenance_equivalence_criterion() -> None:
    disposition = _read("docs/sims/sim_spectral_05/disposition_1171_v0.1.md")
    assert "ADR-0037 §3.2" in disposition
    assert "Genesis convergence" in disposition
    assert "Injection-point separation absence" in disposition


def test_disposition_records_gate_token_and_sensitive_phase_boundary() -> None:
    disposition = _read("docs/sims/sim_spectral_05/disposition_1171_v0.1.md")
    assert "sim_spectral_05_gate_pass" in disposition
    assert "GO Phase 1172" in disposition
    assert "Phase 1172 remains SENSITIVE" in disposition


def test_observer_slices_and_deferred_slice_tokens_are_recorded() -> None:
    disposition = _read("docs/sims/sim_spectral_05/disposition_1171_v0.1.md")
    assert "Claim-composition" in disposition
    assert "Provenance" in disposition
    assert "Authority" in disposition
    assert "sim_spectral_05_runtime_binding_slice_deferred_window_1176" in disposition
    assert "sim_spectral_05_economic_flow_slice_deferred_window_1176" in disposition
    assert "sim_spectral_05_gossip_slice_deferred_window_1176" in disposition


def test_signed_v01_star_map_unchanged() -> None:
    star_map = _json("out/genesis_core_star_map_v0.1.json")
    envelope = _json("out/genesis_signing_root_envelope_v0.1.json")
    assert isinstance(star_map, dict)
    assert len(star_map["nodes"]) == 32
    assert len(star_map["edges"]) == 55
    assert isinstance(envelope, dict)
    assert envelope["envelope_hash"] == ROOT_HASH
