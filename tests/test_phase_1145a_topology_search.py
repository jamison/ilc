"""Phase 1145a — SIM-SPECTRAL-03 topology calibration search tests."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "out/sim_spectral_03_topology_search_summary.json"
NOTES = ROOT / "docs/sims/sim_spectral_03/run01a_topology_search_notes.md"
STAR_MAP = ROOT / "out/genesis_core_star_map_v0.1.json"


def _summary() -> dict[str, object]:
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def test_t1_summary_exists_with_harness_id() -> None:
    data = _summary()
    assert data["harness"] == "sim_spectral_03_topology_search"
    assert data["phase"] == "1145a"


def test_t2_variants_searched_nonzero() -> None:
    data = _summary()
    assert data["variants_searched"] == 180
    assert len(data["variants"]) == 180


def test_t3_run01_baseline_constants_match() -> None:
    baseline = _summary()["run01_baseline"]
    assert baseline["s1_mean_slope"] == 0.21355627860399237
    assert baseline["s3_s1_ratio"] == 1.6736470076736112
    assert baseline["g2_s1_ratio"] == 2.2539040876901315


def test_t4_all_variants_have_required_keys() -> None:
    required = {
        "backbone_variant",
        "diagnostics",
        "edge_type_filter",
        "g2_s1_100_ratio",
        "g2_s1_32_ratio",
        "matched_size_gate_pass",
        "phase1145_gate_pass",
        "s1_mean_slope",
        "s3_s1_100_ratio",
        "s3_s1_32_ratio",
        "variant_id",
        "weight_floor",
        "weight_scale",
    }
    for variant in _summary()["variants"]:
        assert required <= set(variant)


def test_t5_no_variant_passes_phase1145_or_matched_size_gate() -> None:
    data = _summary()
    assert data["variants_passing_phase1145_gate"] == 0
    assert data["variants_passing_matched_size_gate"] == 0
    assert data["best_phase1145_comparable_variant"] is None
    assert data["best_matched_size_variant"] is None


def test_t6_matched_size_controls_are_recorded() -> None:
    controls = _summary()["matched_32_controls"]
    assert controls["s3_mean_slope"] == 0.1816844223923865
    assert controls["g2_mean_slope"] == 0.1630902836367425


def test_t7_signed_star_map_is_unchanged_and_signed() -> None:
    star_map = json.loads(STAR_MAP.read_text(encoding="utf-8"))
    assert len(star_map["nodes"]) == 32
    assert len(star_map["edges"]) == 55
    assert all(node["signature_status"] == "signed" for node in star_map["nodes"])
    assert all(node["star_map_version"] == "v0.1" for node in star_map["nodes"])


def test_t8_notes_contain_phase_token_and_defer_guidance() -> None:
    text = NOTES.read_text(encoding="utf-8")
    assert "sim_spectral_03_topology_search_1145a_committed" in text
    assert "Phase 1146 should keep CDL-085 SIM-gated" in text
