"""Phase 1169 — SIM-SPECTRAL-05 Track A calibration."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> object:
    return json.loads(_read(path))


def test_track_a_summary_exists_and_labels_actual_sybil_topology() -> None:
    summary = _json("out/sim_spectral_05_track_a_calibration_summary.json")
    assert isinstance(summary, dict)
    assert summary["phase"] == 1169
    assert summary["s3_topology"] == "synthetic_sybil_cluster"
    assert summary["gate_token"] == "sim_spectral_05_track_a_completed_phase_1169"


def test_track_a_lambda2_floor_sweep_has_required_coverage() -> None:
    summary = _json("out/sim_spectral_05_track_a_calibration_summary.json")
    sweep = summary["lambda2_floor_sweep"]
    assert isinstance(sweep, list)
    assert len(sweep) >= 5
    assert all("theta_floor" in row for row in sweep)
    assert any(row["s3_activates"] is True for row in sweep)


def test_track_a_reports_required_discriminants_with_zscores() -> None:
    summary = _json("out/sim_spectral_05_track_a_calibration_summary.json")
    discriminants = summary["discriminants"]
    for key in ("lambda_max", "spectral_gap", "degree_gini"):
        assert key in discriminants
        assert isinstance(discriminants[key]["zscore_vs_sybil_distribution"], float)
        assert "s1" in discriminants[key]
        assert "s3" in discriminants[key]


def test_track_a_each_discriminant_has_explicit_verdict() -> None:
    summary = _json("out/sim_spectral_05_track_a_calibration_summary.json")
    allowed = {"discriminates_against_sybil", "insufficient_separation"}
    for key in ("lambda_max", "spectral_gap", "degree_gini"):
        assert summary["discriminants"][key]["verdict"] in allowed
    assert summary["track_a_verdict"] in {"track_a_pass", "track_a_fail"}


def test_track_a_notes_record_pass_without_claiming_overall_gate_pass() -> None:
    notes = _read("docs/sims/sim_spectral_05/track_a_calibration_notes_1169.md")
    assert "track_a_pass" in notes
    assert "This is not an overall SIM-SPECTRAL-05 pass" in notes
    assert "sim_spectral_05_track_a_completed_phase_1169" in notes


def test_signed_v01_star_map_unchanged() -> None:
    star_map = _json("out/genesis_core_star_map_v0.1.json")
    envelope = _json("out/genesis_signing_root_envelope_v0.1.json")
    assert isinstance(star_map, dict)
    assert len(star_map["nodes"]) == 32
    assert len(star_map["edges"]) == 55
    assert isinstance(envelope, dict)
    assert envelope["envelope_hash"] == ROOT_HASH
