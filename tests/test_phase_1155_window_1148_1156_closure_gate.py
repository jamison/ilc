"""Phase 1155 — Window 1148-1156 closure gate."""

from __future__ import annotations

import json
import os
import pathlib
from decimal import Decimal

from ilc_core.types import PROVENANCE_DECAY_ALPHA


ROOT = pathlib.Path(__file__).resolve().parents[1]
SELFTEST_MODE = os.environ.get("ILC_PHASE_1155_GATE_SELFTEST") == "1"

ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
PROMOTED_ADR_IDS = {
    "adr:0019_graph_native_governance_compilation_boundary",
    "adr:0026_protocol_vs_harness_product_boundary",
    "adr:0028_settlement_substrate_graduation_governance_route",
    "adr:0031_subgraph_homomorphism_query_contract",
}


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> object:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_cat0_selftest_env_required() -> None:
    assert SELFTEST_MODE is True


def test_cat1_sequence_lock_and_guidance_close_window() -> None:
    lock = _read("docs/specs/ilc_phase_1148_1156_sequence_lock_v0.1.md")
    guidance = _read("docs/specs/ilc_window_1148_1156_candidate_phase_grouping_v0.1.md")
    assert "window_1148_1156_sequence_lock_committed" in lock
    assert "Phase 1155" in lock
    assert "Phase 1156" in lock
    assert "conditional SENSITIVE" in lock
    assert "**Status:** CLOSED" in guidance
    assert "Phase 1155 closure gate passed" in guidance
    assert "phase_1156_deferred_not_authorized" in guidance


def test_cat2_adr_status_normalization_tokens_present() -> None:
    text = _read("docs/specs/ilc_phase_1148_1156_sequence_lock_v0.1.md")
    for token in (
        "adr_status_normalization_required_before_tier2_promotion",
        "adr_0019_tier2_promote_phase_1149",
        "adr_0026_tier2_promote_phase_1149",
        "adr_0028_tier2_promote_phase_1149",
        "adr_0031_tier2_promote_phase_1149",
        "adr_0012_tier2_blocked_status_proposed_not_accepted",
        "adr_0020_tier2_blocked_status_proposed_not_accepted",
        "adr_0022_tier2_blocked_status_proposed_not_accepted",
        "adr_0023_tier2_blocked_status_proposed_not_accepted",
        "adr_0008_tier2_blocked_status_proposed_not_accepted",
        "adr_0034_tier2_deferred_to_window_1166_plus",
        "adr_0020_acceptance_review_priority_before_tier3_embedding_linkage",
    ):
        assert token in text


def test_cat3_v02_candidate_has_expected_shape_and_promotions() -> None:
    star_map = _json("out/genesis_core_star_map_v0.2_candidate.json")
    assert isinstance(star_map, dict)
    assert len(star_map["nodes"]) == 36
    assert len(star_map["edges"]) == 63
    node_ids = {node["candidate_id"] for node in star_map["nodes"]}
    assert PROMOTED_ADR_IDS <= node_ids
    for node in star_map["nodes"]:
        if node["candidate_id"] in PROMOTED_ADR_IDS:
            assert node["genesis_attested"] is True
            assert node["signature_status"] == "pending_signing"
            assert node["star_map_version"] == "v0.2_candidate"


def test_cat4_signed_v01_genesis_artifacts_remain_unchanged() -> None:
    star_map = _json("out/genesis_core_star_map_v0.1.json")
    envelope = _json("out/genesis_signing_root_envelope_v0.1.json")
    assert isinstance(star_map, dict)
    assert len(star_map["nodes"]) == 32
    assert len(star_map["edges"]) == 55
    assert isinstance(envelope, dict)
    assert envelope["envelope_hash"] == ROOT_HASH
    for node in star_map["nodes"]:
        assert node["genesis_attested"] is True
        assert node["signature_status"] == "signed"
        assert node["star_map_version"] == "v0.1"


def test_cat5_checkpoint_2_authority_gate_passes_despite_legacy_tool_verdict() -> None:
    diagnostic = _json("out/genesis_compile_coverage_diagnostic_v0.2_candidate.json")
    assert isinstance(diagnostic, dict)
    authority = diagnostic["authority_traceability"]
    assert authority["authority_traceable_core_nodes"] == 36
    assert authority["authority_traceable_core_nodes_ratio"] == "1.000000"
    assert diagnostic["compile_coverage"]["core_nodes_total"] == 36
    assert diagnostic["verdict"] == "FAIL_CORE_INADEQUATE"
    report = _read("docs/sims/sim_spectral_02/genesis_compile_checkpoint_2_1150_v0.1.md")
    assert "genesis_compile_checkpoint_2_pass" in report
    assert "36/36" in report
    assert "FAIL_CORE_INADEQUATE" in report
    assert "legacy basis-reachability" in report
    assert "outside the Phase 1150 authority gate" in report


def test_cat6_composability_audit_covers_32_nodes_and_all_classes() -> None:
    audit = _json("out/genesis_32_node_composability_audit_v0.1.json")
    assert isinstance(audit, dict)
    assert audit["token"] == "genesis_32_node_composability_audit_committed_phase_1151"
    assert audit["node_count"] == 32
    assert set(audit["class_counts"]) == {
        "primitive",
        "historical_artifact",
        "parameterized_policy",
        "claim_composite",
        "runtime_binding_pending",
    }
    assert sum(audit["class_counts"].values()) == 32


def test_cat7_sim_spectral_04_program_spec_records_controls() -> None:
    program = _read("docs/sims/sim_spectral_04/program.md")
    assert "sim_spectral_04_program_committed_phase_1152" in program
    assert "matched-size S3 and G2 controls" in program
    assert "0.6416011282246747" in program
    assert "0.8640456434014127" in program
    assert "tools/build_genesis_claim_composition_projection.py" in program


def test_cat8_canonical_lineage_contract_spec_records_network_id_and_release_key() -> None:
    spec = _read("docs/specs/ilc_genesis_canonical_lineage_contract_planning_spec_v0.1.md")
    assert "genesis_canonical_lineage_contract_planning_spec_committed_phase_1153" in spec
    assert 'network_id = H("ILC_NETWORK_ID_V1" || genesis_root_envelope_hash)' in spec
    assert "artifact:genesis_intent_attestation_init_authority_map" in spec
    assert "Operational Release Key Genesis Binding" in spec
    assert ROOT_HASH in spec


def test_cat9_obligations_synthesis_does_not_authorize_legal_or_signing_changes() -> None:
    synthesis = _read("docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md")
    assert "pre_public_rc_obligations_synthesis_committed_phase_1154" in synthesis
    assert "Contributor agreement" in synthesis
    assert "License strategy" in synthesis
    assert "Trademark / identity policy" in synthesis
    assert "authorize Phase 1156 signing" in synthesis
    assert "make legal conclusions" in synthesis


def test_cat10_cdl085_sim_gated_and_runtime_frontier_unchanged() -> None:
    capsule = _read("docs/specs/ilc_antigravity_context_capsule_v5.40.md")
    runtime = _read("ilc_core/economics/epoch_attribution_settle_runtime.py")
    assert "CDL-085" in capsule
    assert "SIM-gated" in capsule
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")
    assert "epoch_attribution_settle_runtime_1129_fix1.v0.5" in runtime


def test_cat11_capsule_v540_supersedes_v539_and_records_frontier() -> None:
    capsule = _read("docs/specs/ilc_antigravity_context_capsule_v5.40.md")
    assert "capsule_v5_40_supersedes_v5_39" in capsule
    assert "window_1148_1156_closed_phase_1155" in capsule
    assert "atlas_tier2_v0_2_candidate_36_nodes_unsigned" in capsule
    assert "sim_spectral_04_program_committed_phase_1152" in capsule
    assert "Phase 1156 is deferred and not authorized" in capsule


def test_cat12_coherence_report_records_pass_and_legacy_verdict_nuance() -> None:
    report = _read("docs/specs/ilc_integration_coherence_report_1155_v0.1.md")
    assert "coherence_report_1155_verdict=pass" in report
    assert "36/36" in report
    assert "FAIL_CORE_INADEQUATE" in report
    assert "not the checkpoint #2 criterion" in report
    assert "v0.2 candidate remains unsigned" in report


def test_cat13_handoff_closes_window_and_defers_phase_1156() -> None:
    handoff = _read("docs/specs/ilc_window_1148_1156_handoff_1155_v0.1.md")
    assert "window_1148_1156_closed_phase_1155" in handoff
    assert "window_1148_1156_closure_gate_verdict=pass" in handoff
    assert "phase_1156_deferred_not_authorized" in handoff
    assert "Human GO token: `GO Phase 1155`" in handoff
    assert "MemPalace Refresh Disposition" in handoff


def test_cat14_planning_index_points_to_capsule_v540_and_handoff() -> None:
    index = _read("docs/PLANNING_INDEX.md")
    assert "**Last updated:** 2026-05-04" in index
    assert "Window 1148-1156 CLOSED via Phase 1155" in index
    assert "docs/specs/ilc_antigravity_context_capsule_v5.40.md" in index
    assert "docs/specs/ilc_window_1148_1156_handoff_1155_v0.1.md" in index


def test_cat15_launch_roadmap_has_window_1148_1156_postscript() -> None:
    roadmap = _read("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.8.md")
    assert "Postscript 2026-05-04 — Window 1148-1156 Closure" in roadmap
    assert "36/36 authority-traceable" in roadmap
    assert "Phase 1156" in roadmap
    assert "CDL-085 remains SIM-gated" in roadmap


def test_cat16_status_records_phase_1155_frontier() -> None:
    status = _read("docs/phases/STATUS.md")
    assert "## Phase 1155" in status
    assert "window_1148_1156_closed_phase_1155" in status
    assert "phase_1156_deferred_not_authorized" in status
    assert "**Next planned phase:** Window 1157+ guidance" in status


def test_cat17_walkthrough_records_closure_tokens() -> None:
    walkthrough = _read("docs/phases/phase_1155_window_1148_1156_closure_gate_walkthrough.md")
    assert "window_1148_1156_closed_phase_1155" in walkthrough
    assert "window_1148_1156_closure_gate_verdict=pass" in walkthrough
    assert "coherence_report_1155_verdict=pass" in walkthrough
    assert "capsule_v5_40_supersedes_v5_39" in walkthrough
    assert "phase_1156_deferred_not_authorized" in walkthrough
