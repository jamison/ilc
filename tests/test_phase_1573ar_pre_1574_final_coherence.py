from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/specs/ilc_block6_pre_rc_coherence_report_1573ar_v0.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.72_pre_1574.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1573ar_pre_1574_final_coherence_walkthrough.md"

REQUIRED_STATUS_TOKENS = (
    "pre_1574_final_coherence_complete_phase_1573ar",
    "capsule_updated_pre_1574_phase_1573ar",
    "public_path_remains_blocked_phase_1573ar",
)

REQUIRED_PRECONDITION_TOKENS = (
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
    "invite_cli_plumbing_committed_phase_1573z",
    "cdl_029_amendment_2_cmax_denominator_phase_1573aa",
    "genesis_accrual_governor_cmax_denominator_fix_phase_1573ab",
    "genesis_accumulation_canonical_sim_complete_phase_1573ac",
    "cdl_102_inviter_chaining_economics_opened_phase_1573ad",
    "projection_policy_node_added_phase_1573ae",
    "pre_1574_coherence_report_committed_phase_1573af",
    "release_engineering_track_disposition_audit_committed_phase_1573ag",
    "edge_namespace_extension_policy_committed_phase_1573ah",
    "atlas_edge_retirement_rehearsal_complete_phase_1573ai",
    "atlas_edge_retirement_migration_applied_phase_1573aj",
    "api_ingress_boundary_classified_phase_1573ak",
    "public_rc_exclude_import_closure_clean_phase_1573al",
    "key_compromise_transactionality_reviewed_phase_1573am",
    "hb002_bootstrap_gossip_protocol_spec_complete_phase_1573an",
    "adr0009_layer0_bundle_test_vectors_complete_phase_1573ao",
    "atlas_slice_manifest_class_implemented_phase_1573ap",
    "inviter_chaining_cdl_prelocked_phase_1573aq",
    "genesis_recovery_transaction_boundary_spec_committed_phase_1573as",
    "genesis_recovery_fake_key_vectors_committed_phase_1573at",
    "genesis_recovery_ceremony_runbook_committed_phase_1573au",
    "cdl_002_credential_supersession_reframe_complete_phase_1573av",
    "mcp_public_rc_surface_disposition_complete_phase_1573aw",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1573ar_status_tokens_present() -> None:
    text = _read(STATUS)
    for token in REQUIRED_STATUS_TOKENS:
        assert token in text


def test_precondition_tokens_remain_present() -> None:
    text = _read(STATUS)
    for token in REQUIRED_PRECONDITION_TOKENS:
        assert token in text


def test_coherence_report_records_pass_and_1574_gate() -> None:
    text = _read(REPORT)

    assert "**Overall verdict:** PASS." in text
    assert "All required Phase 1573p-1573aw tokens are present" in text
    assert "Phase 1574 may be authorized only by explicit human GO" in text
    assert "a0d0a3578" in text


def test_context_capsule_is_v572_and_points_to_1574_next() -> None:
    text = _read(CAPSULE)

    assert "# ILC Context Capsule v5.72 - Pre-1574 Final Coherence" in text
    assert "Block 6 Window 1565-1575 is complete through Phase 1573ar" in text
    assert "Phase 1574 is the next SENSITIVE publication readiness audit" in text
    assert "Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.71_mid_block_1573af.md`" in text


def test_planning_index_current_marker_is_on_1573ar_frontier() -> None:
    text = _read(PLANNING)

    current_lines = [line for line in text.splitlines() if "⬅ CURRENT" in line]
    non_meta_current_lines = [line for line in current_lines if "exactly one `⬅ CURRENT`" not in line]
    assert len(non_meta_current_lines) == 1
    assert "Phase 1573ar Pre-1574 final coherence" in non_meta_current_lines[0]
    assert "ilc_antigravity_context_capsule_v5.72_pre_1574.md" in non_meta_current_lines[0]


def test_walkthrough_records_non_authorization_floor() -> None:
    text = _read(WALKTHROUGH)

    for phrase in (
        "no public RC",
        "no public mirror push",
        "no CDL mutation",
        "no ADR opening",
        "no runtime activation",
        "no Genesis signing",
    ):
        assert phrase in text
