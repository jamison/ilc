"""Phase 1147 — Window 1139-1147 closure gate."""

from __future__ import annotations

import json
import os
import pathlib
from decimal import Decimal

from ilc_core.types import PROVENANCE_DECAY_ALPHA


ROOT = pathlib.Path(__file__).resolve().parents[1]
SELFTEST_MODE = os.environ.get("ILC_PHASE_1147_GATE_SELFTEST") == "1"

ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> object:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_cat0_selftest_env_required() -> None:
    assert SELFTEST_MODE is True


def test_cat1_sequence_lock_and_guidance_cover_window() -> None:
    lock = _read("docs/specs/ilc_phase_1139_1147_sequence_lock_v0.1.md")
    guidance = _read("docs/specs/ilc_window_1139_1147_candidate_phase_grouping_v0.1.md")
    assert "window_1139_1147_sequence_lock_committed_phase_1139" in lock
    assert "Phase 1142s" in lock
    assert "Phase 1147" in lock
    assert "SENSITIVE" in lock
    assert "**Status:** CLOSED" in guidance
    assert "Phase 1147 closure gate passed" in guidance


def test_cat2_run02_fix2_baseline_exists_with_333_entries() -> None:
    summary = _json("out/sim_spectral_02_run02_fix2_summary.json")
    assert isinstance(summary, list)
    assert len(summary) == 333
    notes = _read("docs/sims/sim_spectral_02/run02_fix2_disposition_addendum_1141_v0.1.md")
    assert "run02_fix2_disposition_addendum_committed_phase_1141" in notes
    assert "0.6416011282246747" in notes
    assert "0.8640456434014127" in notes


def test_cat3_signed_genesis_star_map_has_expected_shape() -> None:
    star_map = _json("out/genesis_core_star_map_v0.1.json")
    assert isinstance(star_map, dict)
    assert len(star_map["nodes"]) == 32
    assert len(star_map["edges"]) == 55
    for node in star_map["nodes"]:
        assert node["genesis_attested"] is True
        assert node["signature_status"] == "signed"
        assert node["star_map_version"] == "v0.1"


def test_cat3_root_envelope_and_signature_are_present() -> None:
    envelope = _json("out/genesis_signing_root_envelope_v0.1.json")
    assert isinstance(envelope, dict)
    assert envelope["envelope_hash"] == ROOT_HASH
    assert envelope["signing_context"] == "ILC_GENESIS_ROOT_ENVELOPE_V1"
    assert (ROOT / "out/genesis_signing_root_envelope_v0.1.sig").exists()


def test_cat4_genesis_compile_checkpoint_passes_authority_gate() -> None:
    diag = _json("out/genesis_compile_coverage_diagnostic_v0.1.json")
    assert isinstance(diag, dict)
    auth = diag["authority_traceability"]
    assert auth["authority_traceable_core_nodes"] >= 28
    assert diag["compile_coverage"]["core_nodes_total"] == 32
    checkpoint = _read("docs/sims/sim_spectral_02/genesis_compile_checkpoint_1_1143_v0.1.md")
    assert "genesis_compile_checkpoint_1_pass" in checkpoint


def test_cat5_sim_spectral_03_outputs_and_disposition_exist() -> None:
    run01 = _json("out/sim_spectral_03_run01_summary.json")
    topology = _json("out/sim_spectral_03_topology_search_summary.json")
    disposition = _read("docs/sims/sim_spectral_03/disposition_1146_v0.1.md")
    assert isinstance(run01, list)
    assert len(run01) == 333
    assert isinstance(topology, dict)
    assert topology["variants_passing_phase1145_gate"] == 0
    assert topology["variants_passing_matched_size_gate"] == 0
    assert "sim_spectral_03_disposition_committed_phase_1146" in disposition
    assert "CDL-085 recommendation: DEFER" in disposition
    assert "raw_authority_graph_is_not_the_right_spectral_work_graph" in disposition


def test_cat6_phase_1146_obligations_are_carried_forward() -> None:
    handoff = _read("docs/specs/ilc_window_1139_1147_handoff_1147_v0.1.md")
    for token in (
        "sim_spectral_04_claim_composition_projection_required_before_cdl_085_reconsideration",
        "genesis_32_node_composability_audit_required",
        "matched_size_controls_required_for_future_spectral_sims",
        "genesis_canonical_lineage_contract_required_before_public_rc",
        "truth_primitive_permanence_requires_community_ratification_before_genesis_sunset",
        "public_rc_envelope_hash_transition_policy_required",
        "contributor_agreement_required_before_public_repo",
    ):
        assert token in handoff


def test_cat7_cdl_084_runtime_constants_unchanged() -> None:
    runtime = _read("ilc_core/economics/epoch_attribution_settle_runtime.py")
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")
    assert "epoch_attribution_settle_runtime_1129_fix1.v0.5" in runtime
    assert "cdl_084_provenance_chain_attribution_ratified_1113.v0.1" in runtime


def test_cat8_coherence_report_records_runtime_audit_nuance() -> None:
    report = _read("docs/specs/ilc_integration_coherence_report_1147_v0.1.md")
    assert "coherence_report_1147_verdict=pass" in report
    assert "runtime semantic mutation" in report
    assert "102ed6f2" in report
    report_lower = report.lower()
    assert "canon bundle" in report_lower
    assert "signing step" in report_lower


def test_cat9_capsule_v539_supersedes_v538() -> None:
    capsule = _read("docs/specs/ilc_antigravity_context_capsule_v5.39.md")
    assert "capsule_v5_39_supersedes_v5_38" in capsule
    assert "window_1139_1147_three_lane_complete" in capsule
    assert "run02_fix2_corrected_baseline_committed" in capsule
    assert "sim_spectral_03_disposition_phase_1146" in capsule
    assert ROOT_HASH in capsule


def test_cat10_handoff_closes_window_and_records_human_go() -> None:
    handoff = _read("docs/specs/ilc_window_1139_1147_handoff_1147_v0.1.md")
    assert "window_1139_1147_closed_phase_1147" in handoff
    assert "window_1139_1147_closure_gate_verdict=pass" in handoff
    assert "Human GO token: `GO Phase 1147`" in handoff
    assert "MemPalace Refresh Disposition" in handoff


def test_cat11_planning_index_points_to_capsule_and_handoff() -> None:
    index = _read("docs/PLANNING_INDEX.md")
    assert "**Last updated:** 2026-05-04" in index
    assert "Window 1139-1147 CLOSED via Phase 1147" in index
    assert "docs/specs/ilc_antigravity_context_capsule_v5.39.md" in index
    assert "docs/specs/ilc_window_1139_1147_handoff_1147_v0.1.md" in index


def test_cat12_launch_roadmap_has_window_1139_1147_postscript() -> None:
    roadmap = _read("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.8.md")
    assert "Postscript 2026-05-04 — Window 1139-1147 Closure" in roadmap
    assert "CDL-085 remains SIM-gated" in roadmap
    assert "claim-composition projection" in roadmap


def test_cat13_status_records_phase_1147_frontier() -> None:
    status = _read("docs/phases/STATUS.md")
    assert "## Phase 1147" in status
    assert "window_1139_1147_closed_phase_1147" in status
    assert "**Next planned phase:** Window 1148+ guidance" in status


def test_cat14_claim_composition_plan_is_referenced() -> None:
    plan = _read("docs/specs/ilc_genesis_claim_composition_projection_plan_1146_v0.1.md")
    handoff = _read("docs/specs/ilc_window_1139_1147_handoff_1147_v0.1.md")
    assert "raw_authority_graph_is_not_the_right_spectral_work_graph" in plan
    assert "ilc_genesis_claim_composition_projection_plan_1146_v0.1.md" in handoff


def test_cat15_license_and_contributor_obligations_are_not_silent() -> None:
    handoff = _read("docs/specs/ilc_window_1139_1147_handoff_1147_v0.1.md")
    assert "License strategy" in handoff
    assert "Contributor agreement" in handoff
    assert "Trademark / identity policy" in handoff
    assert "counsel" in handoff.lower()


def test_cat16_walkthrough_records_closure_tokens() -> None:
    walkthrough = _read("docs/phases/phase_1147_window_1139_1147_closure_gate_walkthrough.md")
    assert "window_1139_1147_closed_phase_1147" in walkthrough
    assert "window_1139_1147_closure_gate_verdict=pass" in walkthrough
    assert "coherence_report_1147_verdict=pass" in walkthrough
    assert "capsule_v5_39_supersedes_v5_38" in walkthrough
