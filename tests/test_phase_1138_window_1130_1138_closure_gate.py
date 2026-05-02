"""Phase 1138 — Window 1130-1138 closure gate."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess


SELFTEST_MODE = os.environ.get("ILC_PHASE_1138_GATE_SELFTEST") == "1"

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> object:
    data = json.loads((ROOT / path).read_text(encoding="utf-8"))
    return data


def test_cat0_selftest_env_recognized() -> None:
    assert isinstance(SELFTEST_MODE, bool)


def test_cat1_sequence_lock_exists_with_closure_gate_token() -> None:
    text = _read("docs/specs/ilc_phase_1130_1138_sequence_lock_v0.1.md")
    assert "window_1130_1138_sequence_lock_committed_phase_1130" in text
    assert "window_1130_1138_closure_gate_phase_1138_sensitive" in text
    assert "No CDL opening or ratification in this window" in text
    assert "No `ilc_core/` runtime mutations in this window" in text


def test_cat1_guidance_records_phase_1138_sensitive_tail_slot() -> None:
    text = _read("docs/specs/ilc_window_1130_1138_candidate_phase_grouping_v0.1.md")
    assert "| 9 | 1138 | Window 1130–1138 closure gate | Gate | **SENSITIVE** |" in text
    assert "ILC_PHASE_1138_GATE_SELFTEST=1" in text
    assert "Status: CLOSED — Phase 1138 closure gate passed" in text


def test_cat2_core_sim_spectral_artifacts_exist() -> None:
    for path in (
        "docs/sims/sim_spectral_02/sim_spectral_02_signal_definition_v0.1.md",
        "docs/sims/sim_spectral_02/program.md",
        "out/sim_spectral_02_run01_summary.json",
        "out/sim_spectral_02_run02_summary.json",
        "out/sim_spectral_02_run02_flat_baseline_1135.json",
        "docs/sims/sim_spectral_02/run01_disposition_1134_v0.1.md",
        "docs/sims/sim_spectral_02/run02_disposition_1136_v0.1.md",
    ):
        assert (ROOT / path).exists(), path


def test_cat2_run02_matrix_contains_333_entries() -> None:
    summary = _json("out/sim_spectral_02_run02_summary.json")
    assert isinstance(summary, list)
    assert len(summary) == 333


def test_cat3_run02_disposition_records_scenario_b_advisory_conditions() -> None:
    text = _read("docs/sims/sim_spectral_02/run02_disposition_1136_v0.1.md")
    assert "sim_spectral_02_scenario_b_advisory_phase_1136" in text
    assert "sim_spectral_02_genesis_seed_carry_forward_phase_1136" in text
    assert "sim_spectral_02_bootstrap_adr_proposed_phase_1136" in text
    assert "gaming resistance" in text
    assert "SIM-SPECTRAL-03" in text
    assert "λ₂ > 0" in text or "lambda2 > 0" in text


def test_cat3_beta_probe_recorded_in_raw_notes() -> None:
    text = _read("docs/sims/sim_spectral_02/run02_raw_notes_1135.md")
    assert "Post-Run β Calibration Probe" in text
    assert "S3" in text
    assert "0.647" in text


def test_cat4_genesis_atlas_artifacts_exist_and_have_expected_shape() -> None:
    star_map = _json("out/genesis_core_star_map_v0.1.json")
    compile_diag = _json("out/genesis_compile_coverage_diagnostic_v0.1.json")
    assert isinstance(star_map, dict)
    assert isinstance(compile_diag, dict)
    assert len(star_map["nodes"]) == 31
    assert len(star_map["edges"]) == 35
    assert star_map["metadata"]["transition_basis"] == [
        "truth_primitive:assert.truth",
        "truth_primitive:validate.claim",
        "truth_primitive:contradict.assert",
        "truth_primitive:refute.claim",
        "truth_primitive:revise.assert",
        "truth_primitive:link.claim",
        "truth_primitive:commit.epoch",
    ]
    assert compile_diag["verdict"] == "PARTIAL_WITH_STRUCTURAL_GAPS"


def test_cat4_genesis_compile_records_structural_gap_not_protocol_failure() -> None:
    report = _read("docs/sims/sim_spectral_02/genesis_compile_coverage_diagnostic_v0.1.md")
    assert "`PARTIAL_WITH_STRUCTURAL_GAPS`" in report
    assert "not as a protocol failure" in report
    assert "support-graph expansion queue" in report
    assert "genesis_compile_coverage_diagnostic_complete_v0_1" in report


def test_cat4_proposed_core_edges_all_have_decomposition_recipes() -> None:
    compile_diag = _json("out/genesis_compile_coverage_diagnostic_v0.1.json")
    assert isinstance(compile_diag, dict)
    edge_analysis = compile_diag["edge_recipe_analysis"]
    assert edge_analysis["proposed_edge_count"] == 9
    assert edge_analysis["missing_decomposition_recipe_count"] == 0
    assert edge_analysis["proposed_edge_type_counts"] == {
        "CONSTRAINS": 2,
        "GOVERNS": 4,
        "PRIMITIVE_INVOCATION": 3,
    }


def test_cat5_coherence_report_and_capsule_v538_are_current() -> None:
    coherence = _read("docs/specs/ilc_integration_coherence_report_1137_v0.1.md")
    capsule = _read("docs/specs/ilc_antigravity_context_capsule_v5.38.md")
    assert "coherence_report_1137_verdict=pass" in coherence
    assert "capsule_v5_38_supersedes_v5_37" in capsule
    assert "Window 1130–1138 phases 1130–1137 are complete" in capsule
    assert "342 tests" in capsule
    assert "Genesis Atlas Tier-1" in capsule
    assert "GENESIS-COMPILE-01 checkpoints" in capsule


def test_cat6_handoff_exists_and_closes_window() -> None:
    text = _read("docs/specs/ilc_window_1130_1138_handoff_1138_v0.1.md")
    assert "window_1130_1138_closed_phase_1138" in text
    assert "window_1130_1138_closure_gate_verdict=pass" in text
    assert "Human GO token: `GO Phase 1138`" in text
    assert "Scenario B Advisory conditions" in text
    assert "GENESIS-COMPILE-01 gap" in text


def test_cat6_status_tail_records_phase_1138_as_frontier() -> None:
    text = _read("docs/phases/STATUS.md")
    assert "## Phase 1138" in text
    assert "window_1130_1138_closed_phase_1138" in text
    assert "**Next planned phase:** Window 1139+ guidance" in text


def test_cat7_planning_index_points_to_current_capsule_and_closure() -> None:
    text = _read("docs/PLANNING_INDEX.md")
    assert "**Last updated:** 2026-05-02" in text
    assert "Window 1130-1138 CLOSED via Phase 1138" in text
    assert "docs/specs/ilc_antigravity_context_capsule_v5.38.md" in text
    assert "docs/specs/ilc_window_1130_1138_handoff_1138_v0.1.md" in text


def test_cat7_launch_roadmap_has_window_1130_1138_postscript() -> None:
    text = _read("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.8.md")
    assert "Postscript 2026-05-02 — Window 1130-1138 Closure" in text
    assert "SIM-SPECTRAL-02" in text
    assert "GENESIS-COMPILE-01" in text
    assert "CDL-085 remains SIM-gated" in text


def test_cat8_no_ilc_core_files_changed_in_window() -> None:
    result = subprocess.run(
        ["git", "diff", "--name-only", "7cf996e8", "--", "ilc_core"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""
