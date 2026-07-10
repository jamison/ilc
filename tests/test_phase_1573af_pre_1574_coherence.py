from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/phases/STATUS.md"
REPORT = ROOT / "docs/specs/ilc_mid_block_coherence_report_1573af_v0.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.71_mid_block_1573af.md"


REQUIRED_TOKENS = [
    "ccss_metadata_leakage_audit_committed_phase_1573p",
    "ccss_side_channel_sim_committed_phase_1573q",
    "ccss_cover_batching_design_committed_phase_1573r",
    "ccss_contact_gate_policy_spec_committed_phase_1573s",
    "ccss_contact_gate_local_evaluator_committed_phase_1573t",
    "obl_register_sweep_complete_phase_1573u",
    "canonical_glossary_star_map_disambiguation_complete_phase_1573v",
    "atlas_slice_manifest_build_pipeline_spec_committed_phase_1573w",
    "adr_multi_slice_encrustation_model_existing_adr0037_confirmed_phase_1573x",
    "fix65a_lmdb_graph_projection_coverage_repair_complete_phase_1573y",
    "fix65b_section_level_integrity_repair_complete_phase_1573y",
    "invite_batch_record_runtime_committed_phase_1573z",
    "cdl_029_amendment_2_cmax_denominator_phase_1573aa",
    "genesis_accrual_governor_cmax_denominator_fix_phase_1573ab",
    "genesis_accumulation_canonical_sim_complete_phase_1573ac",
    "cdl_102_inviter_chaining_economics_opened_phase_1573ad",
    "projection_policy_node_added_phase_1573ae",
    "signing_group_rules_node_added_phase_1573ae",
]


def test_all_1573p_to_1573ae_tokens_present() -> None:
    status = STATUS.read_text(encoding="utf-8")
    missing = [token for token in REQUIRED_TOKENS if token not in status]
    assert missing == []


def test_mid_block_report_exists_and_covers_expected_lanes() -> None:
    text = REPORT.read_text(encoding="utf-8")
    for phrase in [
        "Mid-block coherence checkpoint, not the final pre-1574 gate",
        "CCSS Privacy And Contact Gates",
        "Atlas, Star Map, And Slice Manifest Lane",
        "Invite And Economics Lane",
        "ProjectionPolicyNode and SigningGroupRulesNode",
        "Phase 1573ar is the final pre-1574 coherence gate",
    ]:
        assert phrase in text


def test_capsule_successor_records_frontier_and_supersession() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "v5.71" in text
    assert "Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.70_pre_block6.md`" in text
    assert "mid_block_coherence_snapshot_committed_phase_1573af" in text
    assert "Phase 1573af is a mid-block coherence checkpoint" in text
    assert "Phase 1573ar is the planned final pre-1574 coherence gate" in text


def test_report_and_capsule_preserve_non_authorization_floor() -> None:
    report = REPORT.read_text(encoding="utf-8")
    capsule = CAPSULE.read_text(encoding="utf-8")
    for text in (report, capsule):
        assert "public rc" in text.lower()
        assert "does not authorize" in text.lower()
        assert "Genesis signing" in text
