"""Phase 1165 — Window 1156-1165 closure gate."""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
from decimal import Decimal

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
)
from ilc_core.types import PROVENANCE_DECAY_ALPHA


ROOT = pathlib.Path(__file__).resolve().parents[1]
SELFTEST_MODE = os.environ.get("ILC_PHASE_1165_GATE_SELFTEST") == "1"

ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
COMPILE_V01_SHA256 = "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"
V02_ACCEPTED_ADR_IDS = {
    "adr:0020_knowledge_node_first_design_principle",
    "adr:0012_ecu_ilc_graph_coupling_anti_reflexivity",
    "adr:0022_local_first_private_publication_bound_economics",
    "adr:0023_multi_layer_quality_signal_architecture",
    "adr:0008_node_usefulness_governance_weight_genesis_dilution",
}


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> object:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_cat0_selftest_env_required() -> None:
    if not SELFTEST_MODE:
        pytest.skip("set ILC_PHASE_1165_GATE_SELFTEST=1 to run selftest guard check")
    assert SELFTEST_MODE is True


def test_cat1_sequence_lock_committed() -> None:
    text = _read("docs/specs/ilc_phase_1156_1165_sequence_lock_v0.1.md")
    assert "window_1156_1165_sequence_lock_committed" in text
    assert "phase_1156_deferred_not_authorized" in text
    assert "GO Phase 1163" in text


def test_cat2_adr_0020_acceptance_recorded() -> None:
    review = _read("docs/sims/sim_spectral_04/adr_0020_acceptance_review_1157_v0.1.md")
    adr = _read("docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md")
    assert "adr_0020_accepted_phase_1157" in review
    assert "adr_0020_acceptance_review_priority_before_tier3_embedding_linkage" in review
    assert "satisfied" in review
    assert "**Status:** Accepted" in adr


def test_cat3_adr_batch_acceptance_recorded_for_all_four_phase_1158_adrs() -> None:
    review = _read("docs/sims/sim_spectral_04/adr_batch_acceptance_review_1158_v0.1.md")
    for token in (
        "adr_0012_accepted_phase_1158",
        "adr_0022_accepted_phase_1158",
        "adr_0023_accepted_phase_1158_scoped_quality_signal_architecture",
        "adr_0008_accepted_phase_1158",
    ):
        assert token in review


def test_cat4_adr_0008_explicit_quality_gate_closed() -> None:
    review = _read("docs/sims/sim_spectral_04/adr_batch_acceptance_review_1158_v0.1.md")
    assert "adr_0008_acceptance_review_complete" in review
    adr = _read("docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md")
    assert "Status: Accepted" in adr


def test_cat5_adr_0036_draft_remains_proposed_and_unaccepted() -> None:
    # Read at the Phase 1165 closure commit — ADR-0036 was Proposed at window close.
    # Historical hardening: forward progress (Phase 1173 acceptance) must not break
    # prior window gate assertions.
    result = subprocess.run(
        ["git", "show", "265e4b58:docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md"],
        capture_output=True, text=True, check=True, cwd=ROOT,
    )
    text = result.stdout
    assert "**Status:** Proposed" in text
    assert "adr_0036_release_key_draft_committed_phase_1159" in text
    assert "does not create the key" in text


def test_cat6_projection_tool_exists() -> None:
    assert (ROOT / "tools/build_genesis_claim_composition_projection.py").exists()


def test_cat7_projection_artifact_valid_and_tokened() -> None:
    data = _json("out/genesis_claim_composition_projection_v0.1.json")
    assert isinstance(data, dict)
    assert data["token"] == "sim_spectral_04_claim_composition_projection_built_phase_1160"
    assert data["vertex_count"] == 56
    assert data["edge_count"] == 125
    assert len(data["vertices"]) == 56
    assert len(data["edges"]) == 125
    assert data["source_star_map"] == "out/genesis_core_star_map_v0.1.json"
    assert data["authority_source_count"] == 32


def test_cat8_sim_spectral_04_run_summary_valid() -> None:
    data = _json("out/sim_spectral_04_run01_summary.json")
    assert isinstance(data, dict)
    assert data["token"] == "sim_spectral_04_run01_committed_phase_1161"
    assert data["projection_vertex_count"] == 56
    assert data["projection_edge_count"] == 125
    gate = data["gate_evaluation"]
    assert gate["s1_projection_positive_all_seeds"] is True
    assert gate["matched_g2_s1_below_threshold_all_seeds"] is True
    assert gate["matched_s3_s1_below_threshold_all_seeds"] is False
    assert gate["sim_spectral_04_gate_pass"] is False


def test_cat9_sim_spectral_04_disposition_gate_fail_recorded() -> None:
    text = _read("docs/sims/sim_spectral_04/disposition_1162_v0.1.md")
    assert "sim_spectral_04_gate_fail" in text
    assert "cdl_085_sim_gated_pending_sybil_discrimination_resolution" in text
    assert "Phase 1163 does not execute" in text


def test_cat10_phase_1163_correctly_skipped() -> None:
    assert not (ROOT / "docs/specs/ilc_cdl_085_werner_phi_bound_opening_1163_v0.1.md").exists()
    disposition = _read("docs/sims/sim_spectral_04/disposition_1162_v0.1.md")
    handoff = _read("docs/specs/ilc_window_1156_1165_handoff_1165_v0.1.md")
    assert "sim_spectral_04_gate_fail" in disposition
    assert "phase_1163_correctly_skipped_sim_spectral_04_gate_fail" in handoff


def test_cat11_signed_v01_star_map_and_root_envelope_unchanged() -> None:
    star_map = _json("out/genesis_core_star_map_v0.1.json")
    envelope = _json("out/genesis_signing_root_envelope_v0.1.json")
    assert isinstance(star_map, dict)
    assert len(star_map["nodes"]) == 32
    assert len(star_map["edges"]) == 55
    assert isinstance(envelope, dict)
    assert envelope["envelope_hash"] == ROOT_HASH
    assert envelope["star_map_node_count"] == 32
    for node in star_map["nodes"]:
        assert node["genesis_attested"] is True
        assert node["signature_status"] == "signed"
        assert node["star_map_version"] == "v0.1"


def test_cat12_compile_coverage_v01_hash_unchanged() -> None:
    assert _sha256("out/genesis_compile_coverage_diagnostic_v0.1.json") == COMPILE_V01_SHA256


def test_cat13_runtime_semantics_unchanged() -> None:
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1129_fix1.v0.5"
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert not isinstance(PROVENANCE_DECAY_ALPHA, float)


def test_cat14_v02_candidate_shape_and_phase_1158_promotions() -> None:
    data = _json("out/genesis_core_star_map_v0.2_candidate.json")
    assert isinstance(data, dict)
    assert len(data["nodes"]) == 41
    assert len(data["edges"]) == 73
    node_ids = {node["candidate_id"] for node in data["nodes"]}
    assert V02_ACCEPTED_ADR_IDS <= node_ids
    for candidate_id in V02_ACCEPTED_ADR_IDS:
        node = next(node for node in data["nodes"] if node["candidate_id"] == candidate_id)
        assert node["signature_status"] == "pending_signing"
        assert node["star_map_version"] == "v0.2_candidate"


def test_cat15_capsule_v541_current_and_closed() -> None:
    text = _read("docs/specs/ilc_antigravity_context_capsule_v5.41.md")
    assert "capsule_v5_41_supersedes_v5_40" in text
    assert "window_1156_1165_closed_phase_1165" in text
    for token in (
        "sim_spectral_05_structural_impedance_and_spectral_discriminant_calibration_required",
        "sim_spectral_05_branchial_claim_state_projection_required",
        "sim_spectral_05_multi_slice_observer_convergence_framework_required",
        "genesis_multi_slice_encrustation_model_required_for_lineage_contract_adr",
        "genesis_equivalence_and_merge_policy_required_for_lineage_contract_adr",
        "popperian_equivalence_criterion_required_as_merge_gate_in_lineage_contract_adr",
    ):
        assert token in text


def test_cat16_coherence_report_records_post_phase_1164_supplements() -> None:
    text = _read("docs/specs/ilc_integration_coherence_report_1164_v0.1.md")
    for token in (
        "sim_spectral_05_branchial_claim_state_projection_required",
        "sim_spectral_05_multi_slice_observer_convergence_framework_required",
        "genesis_multi_slice_encrustation_model_required_for_lineage_contract_adr",
        "genesis_equivalence_and_merge_policy_required_for_lineage_contract_adr",
        "popperian_equivalence_criterion_required_as_merge_gate_in_lineage_contract_adr",
    ):
        assert token in text


def test_cat17_research_references_exist() -> None:
    for path in (
        "docs/research/sim_spectral_04_structural_perturbation_research_1164_v0.1.md",
        "docs/research/sim_spectral_wolfram_branchial_framing_1164_supplement_v0.2.md",
        "docs/research/genesis_equivalence_merge_policy_forward_planning_v0.1.md",
        "docs/research/references/wolfram_physics_project_2021_update.md",
    ):
        assert (ROOT / path).exists()


def test_cat18_handoff_exists_and_matches_schema_fields() -> None:
    text = _read("docs/specs/ilc_window_1156_1165_handoff_1165_v0.1.md")
    for heading in (
        "## 1. Window identity and closure basis",
        "## 2. Inputs and closure inheritance",
        "## 3. Closure verdict summary",
        "## 4. Carry-forward items and residual blockers",
        "## 5. Next-window entry criteria and routing",
        "## 6. MemPalace refresh disposition",
    ):
        assert heading in text
    assert "window_1156_1165_closed_phase_1165" in text
    assert "window_1156_1165_closure_gate_verdict=pass" in text
    assert "`Disposition:` required" in text
    assert "`Active working set impacted:` yes" in text


def test_cat19_planning_index_marks_window_closed() -> None:
    # Read at the Phase 1165 closure commit — PLANNING_INDEX was updated by Phase 1166
    # Strike Force to mark Window 1166-1175 in progress.  Historical hardening prevents
    # forward progress from breaking prior window gate assertions.
    result = subprocess.run(
        ["git", "show", "265e4b58:docs/PLANNING_INDEX.md"],
        capture_output=True, text=True, check=True, cwd=ROOT,
    )
    text = result.stdout
    assert "Window 1156-1165 CLOSED" in text
    assert "docs/specs/ilc_window_1156_1165_handoff_1165_v0.1.md" in text
    assert "Context Capsule v5.41" in text
    assert "Window 1166+ guidance pending" in text


def test_cat20_window_guidance_marked_closed() -> None:
    text = _read("docs/specs/ilc_window_1156_1165_candidate_phase_grouping_v0.1.md")
    assert "**Status:** CLOSED" in text
    assert "Phase 1165 closure gate passed" in text
    assert "window_1156_1165_closed_phase_1165" in text


def test_cat21_walkthrough_records_completion() -> None:
    text = _read("docs/phases/phase_1165_window_1156_1165_closure_gate_walkthrough.md")
    assert "**Status:** completed" in text
    assert "window_1156_1165_closed_phase_1165" in text
    assert "Closure verdict: PASS" in text


def test_cat22_status_records_phase_1165() -> None:
    text = _read("docs/phases/STATUS.md")
    assert "## Phase 1165" in text
    assert "window_1156_1165_closed_phase_1165" in text
    assert "Window 1166+ guidance pending" in text


def test_cat23_launch_roadmap_has_window_1156_1165_postscript() -> None:
    text = _read("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.8.md")
    assert "Postscript 2026-05-04 — Window 1156-1165 Closure" in text
    assert "window_1156_1165_closed_phase_1165" in text
    assert "Genesis Canonical Lineage Contract ADR" in text
