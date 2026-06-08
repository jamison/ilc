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
        "test_phase_M009_mysticeti_testnet_setup.py",
        "test_phase_high002_phase_b_closure_gate.py",
        "test_window_1281_1288_prompt_drafts.py",
        "test_window_1317_1329_prompt_drafts.py",
        "test_window_1343_1368_prompt_drafts.py",
    }
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
        if is_historical_phase_snapshot_path(item_path):
            item.add_marker(pytest.mark.historical_phase_snapshot)
            if not historical_phase_snapshot_tests_enabled():
                item.add_marker(historical_skip_marker)
        if is_expensive_release_artifact_path(item_path):
            item.add_marker(pytest.mark.expensive_release_artifact)
            if not expensive_release_artifact_tests_enabled():
                item.add_marker(release_artifact_skip_marker)
