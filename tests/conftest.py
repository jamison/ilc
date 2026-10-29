"""Pytest collection policy for current regression versus archival snapshots."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pytest


RUN_HISTORICAL_PHASE_SNAPSHOTS_ENV = "ILC_RUN_HISTORICAL_PHASE_SNAPSHOT_TESTS"
RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS_ENV = "ILC_RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS"

# These files assert old phase/window closure snapshots, not current runtime
# behavior. Keep them runnable under an explicit opt-in, but do not let them
# dominate default broad-suite health checks.
HISTORICAL_PHASE_SNAPSHOT_TEST_FILES = frozenset(
    {
        "test_phase_1101_window_945_1101_closure_gate.py",
        "test_phase_1109_window_1102_1109_closure_gate.py",
        "test_phase_1115_cdl_084_provenance_chain_attribution.py",
        "test_phase_1117_window_1110_1117_closure_gate.py",
        "test_phase_1127_cdl_084_q2_amendment.py",
        "test_phase_1129_fix1_provenance_input_hardening.py",
        "test_phase_1129_window_1124_1129_closure_gate.py",
        "test_phase_1130_window_1130_1138_sequence_lock.py",
        "test_phase_1137_coherence_capsule_v5_38.py",
        "test_phase_1138_window_1130_1138_closure_gate.py",
        "test_phase_1139_window_1139_1147_sequence_lock.py",
        "test_phase_1142s_genesis_signing_ceremony.py",
        "test_phase_1147_window_1139_1147_closure_gate.py",
        "test_phase_1149_atlas_tier2_patch.py",
        "test_phase_1150_genesis_compile_checkpoint_2.py",
        "test_phase_1155_window_1148_1156_closure_gate.py",
        "test_phase_1157_adr_0020_acceptance.py",
        "test_phase_1158_adr_batch_acceptance.py",
        "test_phase_1159_adr_0036_release_key_draft.py",
        "test_phase_1165_window_1156_1165_closure_gate.py",
        "test_phase_1172_cdl_085_opening.py",
        "test_phase_1174_coherence_capsule_v5_42.py",
        "test_phase_1175_window_1166_1175_closure_gate.py",
        "test_phase_1177_cdl_085_prelock.py",
        "test_phase_1182_window_1176_1182_closure_gate.py",
        "test_phase_1183_sequence_lock.py",
        "test_phase_1184_cdl_085_prelock_hardening.py",
        "test_phase_1190_window_1183_1190_closure_gate.py",
        "test_phase_1191_sequence_lock.py",
        "test_phase_1192_roadmap_v1_0.py",
        "test_phase_1193_v0_2_signing_skip.py",
        "test_phase_1194_cdl_086_public_launch_packaging_blocker.py",
        "test_phase_1195_tier3_runtime_linkage.py",
        "test_phase_1196_persistent_rate_limiter.py",
        "test_phase_1197_canon_bundle_signing_repair.py",
        "test_phase_1198_coherence_capsule_v5_45.py",
        "test_phase_1199_window_1191_1199_closure_gate.py",
        "test_phase_1200_sequence_lock.py",
        "test_phase_1203_cdl_086_deliberation.py",
        "test_phase_1205_v0_2_signing_skip.py",
        "test_phase_1206_truth_primitive_permanence.py",
        "test_phase_1207_coherence_capsule_v5_46.py",
        "test_phase_1208_window_1200_1208_closure_gate.py",
        "test_phase_1209_sequence_lock.py",
        "test_phase_1211_truth_primitive_permanence_packet.py",
        "test_phase_1217_window_1209_1217_closure_gate.py",
        "test_phase_1218_sequence_lock.py",
        "test_phase_1224_window_1218_1224_closure_gate.py",
        "test_phase_1239_coherence_capsule_v5_50.py",
        "test_phase_1240_window_1233_1240_closure_gate.py",
        "test_phase_1248_window_1241_1248_closure_gate.py",
        "test_phase_1250_fix1_rc_frontier_gap_audit.py",
        "test_phase_1251_gap14_package_ci_gate.py",
        "test_phase_1253_transport_principal_identity_spec.py",
        "test_phase_1254_atlas_g_004_005_graph_bridge.py",
        "test_phase_1256_window_1249_1256_closure_gate.py",
        "test_phase_1266_cdl087_sensitive_ratification_review.py",
        "test_phase_1272_window_1265_1272_closure_gate.py",
        "test_phase_1274_cdl048_conversion_sweeper_runtime_skeleton.py",
        "test_phase_1276_cdl087_ratification_authorization_preflight.py",
        "test_phase_1278_fix1_cdl087_ratification.py",
        "test_phase_1279_release_manifest_allowlist_prepublication_preflight.py",
        "test_phase_1280_fix1_hypergraph_laplacian_docs_hardening.py",
        "test_phase_1280_window_1273_1280_closure_gate.py",
        "test_phase_1281_window_1281_1288_sequence_lock.py",
        "test_phase_1282_context_capsule_v5_51_frontier_refresh.py",
        "test_phase_1285_transport_principal_public_path_activation_preflight.py",
        "test_phase_1286_sidecar_public_projection_privacy_serving_preflight.py",
        "test_phase_1287_release_publication_signing_authorization_preflight.py",
        "test_phase_1288_window_1281_1288_closure_gate.py",
        "test_phase_1290_context_capsule_v5_52_frontier_refresh.py",
        "test_phase_1292_claimability_package_profile_allowlist_rehearsal.py",
        "test_phase_1295_transport_principal_lifecycle_revocation_replay_preflight.py",
        "test_phase_1296_hostile_network_admission_ban_rate_privacy_plan.py",
        "test_phase_1297_sidecar_public_safe_projection_schema.py",
        "test_phase_1298_sidecar_bind_listener_peer_discovery_authority_preflight.py",
        "test_phase_1299_release_allowlist_artifact_genesis_readiness_preflight.py",
        "test_phase_1300_counsel_ip_publication_clearance_inventory.py",
        "test_phase_1301_deep_no_activation_assertion_audit.py",
        "test_phase_1302_window_1289_1302_closure_gate.py",
        "test_phase_1304_context_capsule_v5_53_frontier_refresh.py",
        "test_phase_1316_window_1303_1316_closure_implementation_audit.py",
        "test_phase_1318_context_capsule_v5_54_frontier_refresh.py",
        "test_phase_1319_source_allowlist_export_rehearsal.py",
        "test_phase_1320_release_artifact_manifest_instance_rehearsal.py",
        "test_phase_1321_release_key_envelope_procedure_rehearsal.py",
        "test_phase_1322_fix1_vps_git_workflow_restore.py",
        "test_phase_1329_window_1317_1329_closure_gate.py",
        "test_phase_1331_context_capsule_v5_55_release_candidate_freeze.py",
        "test_phase_1331_fix1_pre_1332_security_hardening.py",
        "test_phase_1331_fix2_economics_numeric_and_canon_export.py",
        "test_phase_1331_fix3_network_dos_hardening.py",
        "test_phase_1332_final_deterministic_code_security_audit.py",
        "test_phase_1333_source_allowlist_export_execution_gate.py",
        "test_phase_1343_window_1343_1368_sequence_lock_capsule_v5_56.py",
        "test_phase_1345_fix1_cmax_provenance_activation_planning.py",
        "test_phase_1351a_cdl_029_amendment_post_theta_hard_dust_routing.py",
        "test_phase_1353_cdl_017_validator_admission_ejection.py",
        "test_phase_1360_multi_operator_testnet.py",
        "test_phase_1362_blocking_authority_vehicle_opening.py",
        "test_phase_1369_sequence_lock.py",
        "test_phase_1370_agent_birth_attestation_adr.py",
        "test_phase_1371_identity_bootstrap_cdl_opening.py",
        "test_phase_1372_identity_bootstrap_cdl_prelock.py",
        "test_phase_1375_cdl_088_prelock.py",
        "test_phase_1388_cdl_048_activation_counsel_clearance_blocked.py",
        "test_phase_1400_cdl_091_ratification.py",
        "test_phase_1402_cdl_092_opening.py",
        "test_phase_1403_cdl_092_deliberation.py",
        "test_phase_1404_cdl_092_prelock.py",
        "test_phase_1405_cdl_092_ratification.py",
        "test_phase_1407_cdl_093_prelock.py",
        "test_phase_1407_fix0_cdl_053_opening.py",
        "test_phase_1407_fix1_cdl_053_prelock.py",
        "test_phase_1407_fix3_cdl_093_prelock_amendment.py",
        "test_phase_1410_vrf_adr.py",
        "test_phase_1420_copyright_counsel_disposition.py",
        "test_phase_1422_launch_readiness_manifest_schema.py",
        "test_phase_1426_soft_rc_gate_rerun.py",
        "test_phase_1431_rehearsal_identity_ceremony.py",
        "test_phase_1434_transport_principal_cdl_opening.py",
        "test_phase_1435_transport_principal_cdl_ratification.py",
        "test_phase_1504p_window_1498p_closure_gate.py",
        "test_phase_1505p_window_1505p_1514p_sequence_lock.py",
        "test_phase_1506p_werner_topology_data_capture_schema.py",
        "test_phase_1507p_werner_topology_capture_run.py",
        "test_phase_1508p_werner_sim_fetch_rerun.py",
        "test_phase_1509p_cdl096_eligibility_checkpoint.py",
        "test_phase_1510p_spec_only_obl_batch.py",
        "test_phase_1511p_sim_batch_bounty_transfer_tax_cooling.py",
        "test_phase_1513p_window_coherence_capsule.py",
        "test_phase_1514p_window_1505p_closure_gate.py",
        "test_phase_1515p_window_1515p_1522p_sequence_lock.py",
        "test_phase_1522p_window_1515p_1522p_closure_gate.py",
        "test_phase_1523p_window_1523p_1530p_sequence_lock.py",
        "test_phase_1531p_block4_gap_refresh.py",
        "test_phase_1537p_window_1531p_1537p_closure_gate.py",
        "test_phase_1545p_window_1538p_1545p_closure_gate.py",
        "test_phase_436_runtime_tranche_benchmark_harness_and_tranche_completion.py",
        "test_phase_455_sim_t_comparative_synthesis.py",
        "test_phase_456_cdl_050_blocker_clearance_gate.py",
        "test_phase_456_fix_10_nonlinear_control_mechanism_implementation.py",
        "test_phase_456_fix_10_pre1_nonlinear_control_mechanism_prerequisite_lock.py",
        "test_phase_456_fix_11_nonlinear_control_commission_brief_freeze.py",
        "test_phase_456_fix_12_nonlinear_control_execution_and_blocker_1_reassessment.py",
        "test_phase_456_fix_13_post_nonlinear_control_blocker_disposition_review.py",
        "test_phase_456_fix_14_cdl_050_blocker_clearance_gate_rerun.py",
        "test_phase_456_fix_1_recovery_rule_sequence_lock_and_commission_brief.py",
        "test_phase_456_fix_2_recovery_rule_execution_and_blocker_1_reassessment.py",
        "test_phase_456_fix_3_pre1_recovery_rule_mechanism_prerequisite_lock.py",
        "test_phase_456_fix_3_recovery_rule_mechanism_implementation.py",
        "test_phase_456_fix_4_recovery_rule_commission_brief_freeze.py",
        "test_phase_456_fix_5_recovery_rule_execution_and_blocker_1_reassessment.py",
        "test_phase_456_fix_6_oscillator_mechanism_implementation.py",
        "test_phase_456_fix_6_pre1_oscillator_mechanism_prerequisite_lock.py",
        "test_phase_456_fix_7_oscillator_commission_brief_freeze.py",
        "test_phase_456_fix_8_oscillator_execution_and_blocker_1_reassessment.py",
        "test_phase_456_fix_9_post_oscillator_blocker_disposition_review.py",
        "test_phase_456_post_fix_5_blocker_disposition_review.py",
        "test_phase_456_waggle_dance_wide_field_surface.py",
        "test_phase_457_cdl_050_opening_rerun_path.py",
        "test_phase_459_post1_waggle_oscillator_hybrid_intake_and_admissibility_lock.py",
        "test_phase_459_post2_waggle_oscillator_hybrid_contrast_field_attestation_and_brief_freeze.py",
        "test_phase_459_post3_waggle_oscillator_hybrid_contrast_execution_and_post_window_blocker_reassessment.py",
        "test_phase_459_post4_local_hysteretic_oscillator_field_attestation_and_brief_freeze.py",
        "test_phase_459_post5_local_hysteretic_oscillator_execution_and_post_window_blocker_reassessment.py",
        "test_phase_489_validator_economic_incentive_framework_opening_stub.py",
        "test_phase_491_validator_economic_incentive_framework_ratification_evidence.py",
        "test_phase_496_validator_staking_liveness_ratification_evidence.py",
        "test_phase_499_validator_trust_tier_elevation_opening_stub.py",
        "test_phase_501_validator_trust_tier_elevation_ratification_evidence.py",
        "test_phase_502_adm_001_v0_3_validator_trust_tier_amendment.py",
        "test_phase_508_epoch_boundary_cdl_vehicle_selection.py",
        "test_phase_509_epoch_boundary_cdl_opening_stub.py",
        "test_phase_510_epoch_boundary_cdl_prelock_hardening.py",
        "test_phase_511_epoch_boundary_cdl_ratification_evidence.py",
        "test_phase_515_sequence_lock_and_carry_forward_intake.py",
        "test_phase_517_sim_011_re_admission_calibration.py",
        "test_phase_520_cdl_058_ratification_evidence.py",
        "test_phase_522_adr_0023_cdl_scoping_analysis.py",
        "test_phase_531_cdl_059_ratification_evidence.py",
        "test_phase_533_coherence_report_and_capsule_v2_6.py",
        "test_phase_541_cdl_060_ratification_evidence.py",
        "test_phase_543_coherence_report_and_capsule_v2_7.py",
        "test_phase_572_three_machine_smoke_harness.py",
        "test_phase_606_fix1_mempalace_operational_enablement_and_workflow_integration.py",
        "test_phase_606_fix2_mempalace_retrieval_correctness_and_manifest_hardening.py",
        "test_phase_606_mempalace_internal_retrieval_adoption.py",
        "test_phase_676_window_671_676_closure_and_handoff.py",
        "test_phase_682_window_677_682_closure_and_handoff.py",
        "test_phase_710_validator_agent_design_evidence_and_cdl_017_prelock_mapping.py",
        "test_phase_711_validator_sim_commissioning_and_cdl_039_scope_note.py",
        "test_phase_712_coherence_report_capsule_v4_6_and_window_707_712_closure_gate.py",
        "test_phase_731_coherence_report_for_window_727_732.py",
        "test_phase_732_capsule_v5_0_and_window_727_732_closure_gate.py",
        "test_phase_738_window_733_738_closure_gate.py",
        "test_phase_744_window_739_744_closure_gate.py",
        "test_phase_747_capsule_v5_3_launch_roadmap_v0_4_and_planning_index.py",
        "test_phase_748_window_745_748_closure_gate.py",
        "test_phase_750_master_completion_roadmap_and_m_series_lane_update.py",
        "test_phase_751_stale_planning_doc_archival_and_planning_index_advance.py",
        "test_phase_753_window_753_756_sequence_lock.py",
        "test_phase_763_window_763_766_sequence_lock.py",
        "test_phase_764_cdl_017_interaction_synthesis_and_activation_boundary_record.py",
        "test_phase_830_settlement_path_gate.py",
        "test_phase_834_row5_b_impl_strike_force_closure_gate.py",
        "test_phase_836_first_validator_entry_conditions_check.py",
        "test_phase_843_closure_gate.py",
        "test_phase_844_row5_rust_routing_instrumentation.py",
        "test_phase_849_graduation_checklist_v0_3.py",
        "test_phase_850_851_cdl_071_temporal_tier.py",
        "test_phase_1575a_economic_soft_rc_rehearsal.py",
        "test_phase_1575b_fix9_epoch_0_to_1_private_transition_rehearsal.py",
        "test_phase_M009_mysticeti_testnet_setup.py",
        "test_phase_high002_phase_b_closure_gate.py",
        "test_window_545_554_closure_gate_554.py",
        "test_window_1281_1288_prompt_drafts.py",
        "test_window_1317_1329_prompt_drafts.py",
        "test_window_1343_1368_prompt_drafts.py",
    }
)

# These files retain useful current assertions alongside individual assertions
# that deliberately describe a superseded planning frontier or activation
# snapshot. Keep only those exact historical nodes opt-in.
HISTORICAL_PHASE_SNAPSHOT_TEST_NODEIDS = frozenset(
    {
        "tests/test_gap_public_rc_export_fix_01_export_rehearsal.py::test_gap_public_rc_export_fix_01_checked_in_report_matches_current_repo",
        "tests/test_phase_447_consensus_adversarial_regression.py::test_findings_memo_exists_and_contains_required_headings_and_tokens",
        "tests/test_phase_1564_window_1556_1564_closure_gate.py::test_phase_1564_agents_records_closed_window_and_block6_gate",
        "tests/test_phase_1573ai_1573aj_atlas_edge_retirement_prompts.py::test_1573aj_prompt_halts_without_ready_token",
        "tests/test_phase_1573ar_pre_1574_final_coherence.py::test_planning_index_current_marker_is_on_1573ar_frontier",
        "tests/test_phase_1573l_obl039_obl040_closure.py::test_planning_index_records_phase_1573l_complete_and_1573m_next",
        "tests/test_phase_1573y_fix65ab_lmdb_repair.py::test_fix65a_receipt_records_projection_repair",
        "tests/test_phase_1573y_fix65ab_lmdb_repair.py::test_fix65b_receipt_records_section_integrity_and_carry_forward_debt",
        "tests/test_phase_1575b_fix6a_distributed_private_rehearsal.py::test_phase_1575b_fix6a_runner_builds_host_local_evidence",
        "tests/test_phase_1575b_fix6a_distributed_private_rehearsal.py::test_phase_1575b_fix6a_aggregate_passes_matching_remote_records",
        "tests/test_phase_1575b_fix6a_distributed_private_rehearsal.py::test_phase_1575b_fix6a_aggregate_fails_on_remote_divergence",
        "tests/test_phase_1575b_fix6a_distributed_private_rehearsal.py::test_phase_1575b_fix6a_aggregate_fails_without_required_remote_host",
        "tests/test_phase_1575c_public_rc_gate_001.py::test_genesis_v04_source_and_v05_signature_boundary",
        "tests/test_phase_1575c_public_rc_gate_001.py::test_only_phase_1575g_single_lock_guards_cleared_in_runtime_source",
        "tests/test_phase_1575g_economic_guard_clearance.py::test_phase_1575g_economic_modules_are_marker_free",
        "tests/test_phase_1575g_economic_guard_clearance.py::test_phase_1575g_source_export_required_inclusion_passes_for_six_modules",
        "tests/test_phase_1575s_genesis_ilc_minting_authorization.py::test_phase_1575s_historical_soak_root_is_superseded_by_s_infinity_runtime",
        "tests/test_phase_1575s_genesis_ilc_minting_authorization.py::test_phase_1575s_new_evidence_generation_fails_closed_after_s_infinity_change",
        "tests/test_phase_1575s_genesis_ilc_minting_authorization.py::test_phase_1575s_historical_evidence_verifies",
        "tests/test_phase_1575s_genesis_ilc_minting_authorization.py::test_phase_1575s_non_claims_all_false",
        "tests/test_phase_1575s_genesis_ilc_minting_authorization.py::test_phase_1575s_output_tokens_present",
        "tests/test_phase_1575s_genesis_ilc_minting_authorization.py::test_phase_1575s_rejects_tampered_balance",
        "tests/test_phase_1575s_genesis_ilc_minting_authorization.py::test_phase_1575s_rejects_tampered_payload_hash",
        "tests/test_phase_1575s_genesis_ilc_minting_authorization.py::test_phase_1575s_run_fails_closed_after_s_infinity_change",
        "tests/test_reconciliation_v0435_source_freeze.py::test_v0435_source_version_and_package_declaration_are_exact",
    }
)

_HISTORICAL_GRAPH_SNAPSHOT_TEST_NODEIDS = frozenset(
    {
        "tests/test_phase_1545p_fix27_rewrite_candidate_generation.py::test_fix27_summary_counts_and_tokens",
        "tests/test_phase_1545p_fix27_rewrite_candidate_generation.py::test_fix27_rule_families_and_review_classes_present",
        "tests/test_phase_1545p_fix27_rewrite_candidate_generation.py::test_fix27_records_have_required_dpo_and_proof_fields",
        "tests/test_phase_1545p_fix27_rewrite_candidate_generation.py::test_fix27_reclassifies_b10_b12_genesis_fallback_edges",
        "tests/test_phase_1545p_fix38_graph_derived_frontier_report.py::test_fix38_runner_can_regenerate_deterministically",
        "tests/test_phase_1545p_fix40_post_fix38_integrity_coverage.py::test_fix40_runner_can_regenerate_outputs",
        "tests/test_phase_1545p_fix42_viz_lmdb_adapter.py::test_fix42_public_material_view_is_deterministic_and_public_scoped",
        "tests/test_phase_1545p_fix42_viz_lmdb_adapter.py::test_fix42_exporter_defaults_to_unified_lmdb_and_fix61_digest",
        "tests/test_phase_1545p_fix42_viz_lmdb_adapter.py::test_fix42_governance_and_authority_views_are_shaped",
        "tests/test_phase_1545p_fix42_viz_lmdb_adapter.py::test_fix42_test_registry_view_contains_test_nodes",
        "tests/test_phase_1545p_fix42_viz_lmdb_adapter.py::test_fix42_committed_public_view_matches_report",
        "tests/test_phase_1545p_fix44_digest_equivalence.py::test_candidate_lmdb_digest_equivalence",
        "tests/test_phase_1545p_fix50_authority_edge_repair.py::test_fix50_candidate_exists_and_adds_edges_without_adding_nodes",
        "tests/test_phase_1545p_fix50_authority_edge_repair.py::test_fix50_new_edges_have_deterministic_ids_and_candidate_metadata",
        "tests/test_phase_1545p_fix50_authority_edge_repair.py::test_fix50_governs_edges_respect_authority_scope",
        "tests/test_phase_1545p_fix50_authority_edge_repair.py::test_fix50_governs_does_not_target_lifecycle_or_open_nodes",
        "tests/test_phase_1545p_fix50_authority_edge_repair.py::test_fix50_does_not_recreate_fix38_source_tree_hub_edges",
        "tests/test_phase_1545p_fix50_authority_edge_repair.py::test_fix50_new_governs_edges_are_acyclic",
        "tests/test_phase_1545p_fix51_epistemic_gap_schema.py::test_fix51_validator_passes_on_candidate",
        "tests/test_phase_1545p_fix51_epistemic_gap_schema.py::test_fix51_candidate_contains_valid_seed_gap_node",
        "tests/test_phase_1545p_fix51_epistemic_gap_schema.py::test_fix51_gap_nodes_have_inbound_expects_resolution_and_no_governs_contact",
        "tests/test_phase_1545p_fix51_epistemic_gap_schema.py::test_fix51_preserves_fix50_content_and_adds_only_minimal_seed",
        "tests/test_phase_1545p_fix51_epistemic_gap_schema.py::test_fix51_does_not_recreate_fix38_source_tree_hub_edges",
        "tests/test_phase_1545p_fix52_authority_sim_battery.py::test_fix52_authority_validator_passes_on_fix51_candidate",
        "tests/test_phase_1545p_fix52_authority_sim_battery.py::test_fix52_does_not_mutate_fix51_candidate_counts",
        "tests/test_phase_1545p_fix56_projection_aware_fiedler_rebaseline.py::test_fix56_report_exists_and_valid",
        "tests/test_phase_1545p_fix56_projection_aware_fiedler_rebaseline.py::test_fix56_all_local_lambda2_recorded",
        "tests/test_phase_1545p_fix56_projection_aware_fiedler_rebaseline.py::test_fix56_public_eligible_minority_cluster_exists",
        "tests/test_phase_1545p_fix56_projection_aware_fiedler_rebaseline.py::test_fix56_authority_only_projection_nonempty",
        "tests/test_phase_1545p_fix56_projection_aware_fiedler_rebaseline.py::test_fix56_no_private_nodes_in_public_eligible_cluster",
        "tests/test_phase_1545p_fix58_fix48_residual_semantic_queue.py::test_fix58_report_exists_and_valid",
        "tests/test_phase_1545p_fix58_fix48_residual_semantic_queue.py::test_fix58_new_edges_have_manual_reviewed_annotation",
        "tests/test_phase_1545p_fix58_fix48_residual_semantic_queue.py::test_fix58_no_governs_edges_added",
        "tests/test_phase_1545p_fix58_fix48_residual_semantic_queue.py::test_fix58_lmdb_edge_count_nondecreasing",
        "tests/test_phase_1545p_fix58_fix48_residual_semantic_queue.py::test_fix58_residual_queue_fully_dispositioned",
        "tests/test_phase_1545p_fix61_projection_export_package.py::test_fix61_core_star_map_json_exists_and_valid",
        "tests/test_phase_1545p_fix61_projection_export_package.py::test_fix61_authority_projection_json_exists_and_valid",
        "tests/test_phase_1545p_fix61_projection_export_package.py::test_fix61_base_graph_json_exists_and_valid",
        "tests/test_phase_1545p_fix61_projection_export_package.py::test_fix61_no_private_nodes_in_core_star_map",
        "tests/test_phase_1545p_fix61_projection_export_package.py::test_fix61_no_private_nodes_in_authority_projection",
        "tests/test_phase_1545p_fix61_projection_export_package.py::test_fix61_no_private_nodes_in_base_graph",
        "tests/test_phase_1545p_fix61_projection_export_package.py::test_fix61_exports_are_subsets_of_base_graph",
        "tests/test_phase_1545p_fix61_projection_export_package.py::test_fix61_star_map_index_has_authority_coverage_fields",
        "tests/test_phase_1545p_fix61_projection_export_package.py::test_fix61_projection_summary_has_all_projections",
        "tests/test_phase_1545p_fix61_projection_export_package.py::test_fix61_lmdb_preimage_count_matches_live_graph",
        "tests/test_phase_1545p_fix62a_attribution_substrate_closure.py::test_fix62a_outputs_exist_and_are_valid_json",
        "tests/test_phase_1545p_fix62a_attribution_substrate_closure.py::test_fix62a_creator_substrate_closed_for_public_eligible_nodes",
        "tests/test_phase_1545p_fix62a_attribution_substrate_closure.py::test_fix62a_runtime_bindings_and_manual_queue_present",
        "tests/test_phase_1545p_fix62b_priority0_authority_trace.py::test_fix62b_outputs_exist_and_are_valid_json",
        "tests/test_phase_1545p_fix62b_priority0_authority_trace.py::test_fix62b_applies_bounded_authority_edges",
        "tests/test_phase_1545p_fix62c_priority0_disposition_closure.py::test_fix62c_outputs_exist_and_are_valid_json",
        "tests/test_phase_1545p_fix62d_authority_normalization.py::test_fix62d_outputs_exist_and_are_valid_json",
        "tests/test_phase_1545p_fix62d_authority_normalization.py::test_fix62d_normalizes_known_accepted_and_ratified_targets",
        "tests/test_phase_1545p_fix62d_authority_normalization.py::test_fix62d_does_not_promote_open_or_proposed_authority",
        "tests/test_phase_1545p_fix62d_authority_normalization.py::test_fix62d_priority1_token_edges_and_queue_shrink",
        "tests/test_phase_1545p_fix62h_priority1_overlay_classification.py::test_fix62h_report_closes_priority1",
        "tests/test_phase_1545p_fix62h_priority1_overlay_classification.py::test_fix62h_support_policy_is_rooted_and_overlay_nodes_are_classified",
        "tests/test_phase_1545p_fix62h_priority1_overlay_classification.py::test_fix62h_no_dangling_recommended_edges",
        "tests/test_phase_1545p_fix62i_support_queue_closure.py::test_fix62i_report_closes_support_queue",
        "tests/test_phase_1545p_fix62i_support_queue_closure.py::test_fix62i_lmdb_contains_support_edges_and_node_classification",
        "tests/test_phase_1545p_fix63_manual_governs_audit.py::test_fix63_report_and_ledger_cover_all_nodes",
        "tests/test_phase_1545p_fix63_manual_governs_audit.py::test_fix63_accepted_adrs_are_root_governed_and_proposed_are_not",
        "tests/test_phase_1545p_fix63_manual_governs_audit.py::test_fix63_cdl_shadow_duplicates_are_support_projection",
        "tests/test_phase_1545p_fix63_manual_governs_audit.py::test_fix63_truth_primitive_governs_regression_guard",
        "tests/test_phase_1545p_fix63c_floating_invariant_direct_read.py::test_fix63c_lmdb_is_clean_after_writes",
        "tests/test_phase_1545p_fix63d_cdl_adr_lifecycle_governance_cleanup.py::test_fix63d_lmdb_is_clean_after_writes",
        "tests/test_phase_1545p_fix67_classification_projection_hardening.py::test_only_package_root_classified_by_edge_remains_for_public_path_policy",
        "tests/test_phase_1545p_fix70_authority_lattice_repair.py::test_cross_family_count_increased",
        "tests/test_phase_1545p_fix70_authority_lattice_repair.py::test_auth_total_count_increased",
        "tests/test_phase_1545p_fix70_authority_lattice_repair.py::test_genesis_root_governs_edges_preserved",
        "tests/test_phase_1545p_fix72_measurement_suite.py::test_fix72_fiedler_and_spectral_counts_match_snapshot",
        "tests/test_phase_1545p_fix72_measurement_suite.py::test_fix72_lmdb_registration_integrity_and_lineage",
        "tests/test_phase_1565_fix1_soft_rc_rehearsal_graph_cleanup.py::test_fix1_live_lmdb_has_canonical_identity_authority_edges",
        "tests/test_phase_1573ae_projection_and_signing_group_nodes.py::test_projection_policy_node_present_with_canonical_fields",
        "tests/test_phase_1573ae_projection_and_signing_group_nodes.py::test_signing_group_rules_node_present_with_canonical_fields",
        "tests/test_phase_1573ae_projection_and_signing_group_nodes.py::test_cdl_098_governs_both_knowledge_nodes",
        "tests/test_phase_1573ae_projection_and_signing_group_nodes.py::test_nodes_are_not_adr0035_type_definition_nodes",
        "tests/test_phase_1573ae_projection_and_signing_group_nodes.py::test_lmdb_write_scripts_are_durable_repo_artifacts",
        "tests/test_phase_1575c_fix3_genesis_core_slice_0_authority_package.py::test_fix3_builder_materializes_core_and_slice1_packages",
        "tests/test_phase_1575c_fix3_genesis_core_slice_0_authority_package.py::test_fix3_signing_payloads_are_domain_separated",
    }
)

# These exact nodes consume immutable Phase 1545/1565/1573/1575 graph
# materializations. They remain runnable through the existing historical
# opt-in; neighboring current-runtime assertions in the same files stay active.
HISTORICAL_PHASE_SNAPSHOT_TEST_NODEIDS = (
    HISTORICAL_PHASE_SNAPSHOT_TEST_NODEIDS | _HISTORICAL_GRAPH_SNAPSHOT_TEST_NODEIDS
)

EXPENSIVE_RELEASE_ARTIFACT_TEST_FILES = frozenset(
    {
        "test_genesis_distribution_surface_phase_225.py",
        "test_genesis_release_artifacts_phase_228.py",
        "test_reproducible_build_phase_230.py",
    }
)


def historical_phase_snapshot_tests_enabled() -> bool:
    return os.environ.get(RUN_HISTORICAL_PHASE_SNAPSHOTS_ENV) == "1"


def expensive_release_artifact_tests_enabled() -> bool:
    return os.environ.get(RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS_ENV) == "1"


def is_historical_phase_snapshot_path(path: str | Path) -> bool:
    return Path(path).name in HISTORICAL_PHASE_SNAPSHOT_TEST_FILES


def is_historical_phase_snapshot_nodeid(nodeid: str) -> bool:
    return nodeid in HISTORICAL_PHASE_SNAPSHOT_TEST_NODEIDS


def is_expensive_release_artifact_path(path: str | Path) -> bool:
    return Path(path).name in EXPENSIVE_RELEASE_ARTIFACT_TEST_FILES


def historical_phase_snapshot_files() -> tuple[str, ...]:
    return tuple(sorted(HISTORICAL_PHASE_SNAPSHOT_TEST_FILES))


def expensive_release_artifact_files() -> tuple[str, ...]:
    return tuple(sorted(EXPENSIVE_RELEASE_ARTIFACT_TEST_FILES))


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        (
            "expensive_release_artifact: release-artifact build/install proof "
            f"tests that require {RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS_ENV}=1"
        ),
    )
    config.addinivalue_line(
        "markers",
        (
            "historical_phase_snapshot: archived phase-snapshot tests that "
            f"require {RUN_HISTORICAL_PHASE_SNAPSHOTS_ENV}=1"
        ),
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: Iterable[pytest.Item]
) -> None:
    historical_skip_marker = pytest.mark.skip(
        reason=(
            "historical phase-snapshot test; set "
            f"{RUN_HISTORICAL_PHASE_SNAPSHOTS_ENV}=1 to run"
        )
    )
    release_artifact_skip_marker = pytest.mark.skip(
        reason=(
            "expensive release-artifact test; set "
            f"{RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS_ENV}=1 to run"
        )
    )
    for item in items:
        item_path = getattr(item, "path", None) or getattr(item, "fspath")
        if is_historical_phase_snapshot_path(item_path) or is_historical_phase_snapshot_nodeid(
            item.nodeid
        ):
            item.add_marker(pytest.mark.historical_phase_snapshot)
            if not historical_phase_snapshot_tests_enabled():
                item.add_marker(historical_skip_marker)
        if is_expensive_release_artifact_path(item_path):
            item.add_marker(pytest.mark.expensive_release_artifact)
            if not expensive_release_artifact_tests_enabled():
                item.add_marker(release_artifact_skip_marker)
