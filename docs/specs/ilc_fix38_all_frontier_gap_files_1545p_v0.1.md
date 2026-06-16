# Phase 1545p-Fix38 All Frontier Gap Files

PUBLIC_RC_EXCLUDE: fix38_frontier_review_support_artifact
PUBLIC_RC_EXCLUDE_REASON: Research/support-only listing of Fix38 test registry frontier files; not a public RC artifact, graph mutation, signing artifact, activation artifact, or governance mutation.

## Summary

- Source artifact: `out/test_registry_frontier_report_1545p_fix38.json`
- Report digest: `test_frontier_report:ea8775648977f90f02d913d10ede5498`
- Frontier file count: `756`
- Frontier classes included: `missing_candidate_node`, `missing_tests_edge`, `missing_expected_authority_trace`
- Random sample seed: `phase1545p-fix38-frontier-files-v1`

## Boundary

This document lists frontier files for manual review and graph-refresh planning. It does not mutate the graph, promote edges, sign nodes, upload nodes, activate public RC, activate runtime, or mutate ADR/CDL state.

## Files

| # | Batch | File | Gap classes | Connectivity class |
|---:|---|---|---|---|
| 1 | `batch_001_frontier_files_0001_0010` | `tests/test_adm_003_7_plus_1_panel_role_354.py` | `missing_tests_edge` | `phase_artifact_validation` |
| 2 | `batch_001_frontier_files_0001_0010` | `tests/test_adr_0008_reconciliation_cleanup.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 3 | `batch_001_frontier_files_0001_0010` | `tests/test_adr_0033_star_map_homoiconic_entity.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 4 | `batch_001_frontier_files_0001_0010` | `tests/test_adr_0034_d2d_sealed_sender.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 5 | `batch_001_frontier_files_0001_0010` | `tests/test_adr_stale_reconciliation_strike_force_1156.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 6 | `batch_001_frontier_files_0001_0010` | `tests/test_agent_auto_strategy.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 7 | `batch_001_frontier_files_0001_0010` | `tests/test_agent_descriptors.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 8 | `batch_001_frontier_files_0001_0010` | `tests/test_agent_dossier_export.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 9 | `batch_001_frontier_files_0001_0010` | `tests/test_agent_profiles.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 10 | `batch_001_frontier_files_0001_0010` | `tests/test_agent_strategy.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 11 | `batch_002_frontier_files_0011_0020` | `tests/test_analysis_hygiene_phase_223.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 12 | `batch_002_frontier_files_0011_0020` | `tests/test_backlog_summary_metrics.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 13 | `batch_002_frontier_files_0011_0020` | `tests/test_bootstrap_operations_runbook_235.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 14 | `batch_002_frontier_files_0011_0020` | `tests/test_broad_exception_boundary_policy_phase_1011.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 15 | `batch_002_frontier_files_0011_0020` | `tests/test_canon_bundle_key_registry.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 16 | `batch_002_frontier_files_0011_0020` | `tests/test_canon_bundle_key_registry_cli.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 17 | `batch_002_frontier_files_0011_0020` | `tests/test_canon_bundle_sign_cli.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 18 | `batch_002_frontier_files_0011_0020` | `tests/test_canon_cli.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 19 | `batch_002_frontier_files_0011_0020` | `tests/test_canon_export_cli.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 20 | `batch_002_frontier_files_0011_0020` | `tests/test_cdl_001_signer_lineage_runtime.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 21 | `batch_003_frontier_files_0021_0030` | `tests/test_cdl_002_key_compromise_runtime.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 22 | `batch_003_frontier_files_0021_0030` | `tests/test_cdl_006_challenge_node_runtime_1382.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 23 | `batch_003_frontier_files_0021_0030` | `tests/test_cdl_007_rollback_resistance_runtime.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 24 | `batch_003_frontier_files_0021_0030` | `tests/test_cdl_011_015_ratification_evidence_gate_phase_215.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 25 | `batch_003_frontier_files_0021_0030` | `tests/test_cdl_028_fee_burn_candidate_lock_274_fix1.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 26 | `batch_003_frontier_files_0021_0030` | `tests/test_cdl_088_opening.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 27 | `batch_003_frontier_files_0021_0030` | `tests/test_cdl_ratification_verification_gate_269.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 28 | `batch_003_frontier_files_0021_0030` | `tests/test_cdl_v1_ratification_330.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 29 | `batch_003_frontier_files_0021_0030` | `tests/test_cdl_v1_temporal_decay_runtime_388.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 30 | `batch_003_frontier_files_0021_0030` | `tests/test_cdl_v2_ratification_331.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 31 | `batch_004_frontier_files_0031_0040` | `tests/test_cdl_v2_sybil_resistance_runtime_389.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 32 | `batch_004_frontier_files_0031_0040` | `tests/test_cdl_v3_diversity_floor_runtime_397.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 33 | `batch_004_frontier_files_0031_0040` | `tests/test_cdl_v3_ratification_332.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 34 | `batch_004_frontier_files_0031_0040` | `tests/test_cdl_v7_popperian_gate_runtime_398.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 35 | `batch_004_frontier_files_0031_0040` | `tests/test_cdl_v7_ratification_335.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 36 | `batch_004_frontier_files_0031_0040` | `tests/test_cdl_v_batch_a_open_and_evidence_prelock_324.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 37 | `batch_004_frontier_files_0031_0040` | `tests/test_cdl_v_batch_b_open_and_evidence_prelock_325.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 38 | `batch_004_frontier_files_0031_0040` | `tests/test_claim_lifecycle_playground.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 39 | `batch_004_frontier_files_0031_0040` | `tests/test_claim_reward_flow.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 40 | `batch_004_frontier_files_0031_0040` | `tests/test_claim_scores.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 41 | `batch_005_frontier_files_0041_0050` | `tests/test_cli_error_output_standardization_guardrail.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 42 | `batch_005_frontier_files_0041_0050` | `tests/test_cli_key_loader_dedupe_phase_999.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 43 | `batch_005_frontier_files_0041_0050` | `tests/test_code_health.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 44 | `batch_005_frontier_files_0041_0050` | `tests/test_commit_epoch_emission_phase_193.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 45 | `batch_005_frontier_files_0041_0050` | `tests/test_competency_kpis.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 46 | `batch_005_frontier_files_0041_0050` | `tests/test_config_dependency_policy_phase_1006.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 47 | `batch_005_frontier_files_0041_0050` | `tests/test_contradiction.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 48 | `batch_005_frontier_files_0041_0050` | `tests/test_contradiction_war.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 49 | `batch_005_frontier_files_0041_0050` | `tests/test_crypto_migration_bundle_registry_completion_284.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 50 | `batch_005_frontier_files_0041_0050` | `tests/test_crypto_migration_initial_tranche_283.py` | `missing_tests_edge` | `phase_artifact_validation` |
| 51 | `batch_006_frontier_files_0051_0060` | `tests/test_crypto_surface_inventory_lock_280.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 52 | `batch_006_frontier_files_0051_0060` | `tests/test_cw1_convergence_window_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 53 | `batch_006_frontier_files_0051_0060` | `tests/test_cw2_row_5_runtime_closure_evaluation.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 54 | `batch_006_frontier_files_0051_0060` | `tests/test_cw4_row_7_exitability_closure_evaluation.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 55 | `batch_006_frontier_files_0051_0060` | `tests/test_cw5_row_8_disposition_and_option_b_gate_synthesis.py` | `missing_tests_edge` | `adr_or_governance_validation` |
| 56 | `batch_006_frontier_files_0051_0060` | `tests/test_cw6_convergence_window_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 57 | `batch_006_frontier_files_0051_0060` | `tests/test_d2e_03_readiness_257.py` | `missing_tests_edge` | `phase_artifact_validation` |
| 58 | `batch_006_frontier_files_0051_0060` | `tests/test_d2e_05_query_subsystem_300.py` | `missing_tests_edge` | `phase_artifact_validation` |
| 59 | `batch_006_frontier_files_0051_0060` | `tests/test_d2e_06_verify_subsystem_302.py` | `missing_tests_edge` | `phase_artifact_validation` |
| 60 | `batch_006_frontier_files_0051_0060` | `tests/test_dag_audit_cli.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 61 | `batch_007_frontier_files_0061_0070` | `tests/test_data_center_ballast.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 62 | `batch_007_frontier_files_0061_0070` | `tests/test_data_center_controller.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 63 | `batch_007_frontier_files_0061_0070` | `tests/test_devnet_experiments.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 64 | `batch_007_frontier_files_0061_0070` | `tests/test_devnet_multi_epoch.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 65 | `batch_007_frontier_files_0061_0070` | `tests/test_devnet_scenarios.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 66 | `batch_007_frontier_files_0061_0070` | `tests/test_docs_links_resolve.py` | `missing_tests_edge` | `adr_or_governance_validation` |
| 67 | `batch_007_frontier_files_0061_0070` | `tests/test_domain_exception_hierarchy_guardrail.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 68 | `batch_007_frontier_files_0061_0070` | `tests/test_domain_exception_migration_closure_gate.py` | `missing_expected_authority_trace` | `authority_trace_review_required` |
| 69 | `batch_007_frontier_files_0061_0070` | `tests/test_domain_exception_migration_guardrail.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 70 | `batch_007_frontier_files_0061_0070` | `tests/test_domain_exception_rollout_foundation.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 71 | `batch_008_frontier_files_0071_0080` | `tests/test_domain_sigmoid_sim.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 72 | `batch_008_frontier_files_0071_0080` | `tests/test_duplicate_definitions.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 73 | `batch_008_frontier_files_0071_0080` | `tests/test_edge_link_boundary_phase_1007.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 74 | `batch_008_frontier_files_0071_0080` | `tests/test_edge_removal_phase1_guardrails.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 75 | `batch_008_frontier_files_0071_0080` | `tests/test_embedding_pipeline.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 76 | `batch_008_frontier_files_0071_0080` | `tests/test_epistemic_code.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 77 | `batch_008_frontier_files_0071_0080` | `tests/test_epistemic_work_task_playground.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 78 | `batch_008_frontier_files_0071_0080` | `tests/test_epoch_ledger.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 79 | `batch_008_frontier_files_0071_0080` | `tests/test_epoch_playground_event_log.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 80 | `batch_008_frontier_files_0071_0080` | `tests/test_epoch_playground_sim.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 81 | `batch_009_frontier_files_0081_0090` | `tests/test_epoch_summary_emission_phase_194.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 82 | `batch_009_frontier_files_0081_0090` | `tests/test_eve_life.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 83 | `batch_009_frontier_files_0081_0090` | `tests/test_event_log_envelope_guardrail_phase_195.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 84 | `batch_009_frontier_files_0081_0090` | `tests/test_event_log_retention_rotation_gate_phase_196.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 85 | `batch_009_frontier_files_0081_0090` | `tests/test_event_log_retention_rotation_phase_196.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 86 | `batch_009_frontier_files_0081_0090` | `tests/test_fairness_metrics.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 87 | `batch_009_frontier_files_0081_0090` | `tests/test_fastapi_route_cleanup_1378.py` | `missing_tests_edge` | `phase_artifact_validation` |
| 88 | `batch_009_frontier_files_0081_0090` | `tests/test_freshness_gate_invariants_gate_phase_217.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 89 | `batch_009_frontier_files_0081_0090` | `tests/test_freshness_gate_phase_217.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 90 | `batch_009_frontier_files_0081_0090` | `tests/test_genesis_accrual_governor_gate_phase_218.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 91 | `batch_010_frontier_files_0091_0100` | `tests/test_genesis_accrual_governor_phase_218.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 92 | `batch_010_frontier_files_0091_0100` | `tests/test_genesis_compile_coverage_diagnostic.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 93 | `batch_010_frontier_files_0091_0100` | `tests/test_genesis_install_smoke_phase_224.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 94 | `batch_010_frontier_files_0091_0100` | `tests/test_genesis_integration_smoke_phase_224.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 95 | `batch_010_frontier_files_0091_0100` | `tests/test_genesis_node_candidate_crawl.py` | `missing_expected_authority_trace` | `authority_trace_review_required` |
| 96 | `batch_010_frontier_files_0091_0100` | `tests/test_genesis_packaging_distribution_sequence_phase_222.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 97 | `batch_010_frontier_files_0091_0100` | `tests/test_genesis_readiness_audit_reverification_gate_phase_1012.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 98 | `batch_010_frontier_files_0091_0100` | `tests/test_genesis_readiness_remediation_closure_gate_phase_1009.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 99 | `batch_010_frontier_files_0091_0100` | `tests/test_genesis_star_map_gap_analysis.py` | `missing_expected_authority_trace, missing_tests_edge` | `authority_trace_review_required` |
| 100 | `batch_010_frontier_files_0091_0100` | `tests/test_genesis_work_task_model.py` | `missing_expected_authority_trace, missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 101 | `batch_011_frontier_files_0101_0110` | `tests/test_getting_started_docs_phase_1010.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 102 | `batch_011_frontier_files_0101_0110` | `tests/test_glossary_term_elevation_phase_992_near_prep.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 103 | `batch_011_frontier_files_0101_0110` | `tests/test_governance_config.py` | `missing_expected_authority_trace, missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 104 | `batch_011_frontier_files_0101_0110` | `tests/test_governance_config_diagnostics.py` | `missing_expected_authority_trace, missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 105 | `batch_011_frontier_files_0101_0110` | `tests/test_governance_engine.py` | `missing_expected_authority_trace, missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 106 | `batch_011_frontier_files_0101_0110` | `tests/test_governance_ingest_helper_domain_exceptions.py` | `missing_expected_authority_trace, missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 107 | `batch_011_frontier_files_0101_0110` | `tests/test_governance_weight_phase_207.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 108 | `batch_011_frontier_files_0101_0110` | `tests/test_graph_edges.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 109 | `batch_011_frontier_files_0101_0110` | `tests/test_graph_kpis.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 110 | `batch_011_frontier_files_0101_0110` | `tests/test_hardware_archetypes.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 111 | `batch_012_frontier_files_0111_0120` | `tests/test_hash_id_compatibility_contract_281.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 112 | `batch_012_frontier_files_0111_0120` | `tests/test_homoiconic_test_registry_forward_plan.py` | `missing_candidate_node` | `forward_plan_document_validation` |
| 113 | `batch_012_frontier_files_0111_0120` | `tests/test_homoiconic_test_registry_implementation_guidance.py` | `missing_candidate_node` | `implementation_guidance_and_window_validation` |
| 114 | `batch_012_frontier_files_0111_0120` | `tests/test_idea_descent_genesis_star_map_loop.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 115 | `batch_012_frontier_files_0111_0120` | `tests/test_idea_descent_phase_prompt_loop.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 116 | `batch_012_frontier_files_0111_0120` | `tests/test_ilc_cluster_a_governance_apply.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 117 | `batch_012_frontier_files_0111_0120` | `tests/test_ilc_cluster_a_ingest.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 118 | `batch_012_frontier_files_0111_0120` | `tests/test_ilc_cluster_a_replay_determinism.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 119 | `batch_012_frontier_files_0111_0120` | `tests/test_ilc_cluster_a_replay_proof_ci_gate.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 120 | `batch_012_frontier_files_0111_0120` | `tests/test_ilc_cluster_a_replay_proof_ci_gate_baseline.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 121 | `batch_013_frontier_files_0121_0130` | `tests/test_ilc_cluster_a_replay_proof_cli_batch.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 122 | `batch_013_frontier_files_0121_0130` | `tests/test_ilc_governance_record_schema.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 123 | `batch_013_frontier_files_0121_0130` | `tests/test_ilc_node_v0.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 124 | `batch_013_frontier_files_0121_0130` | `tests/test_integration_coherence_248.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 125 | `batch_013_frontier_files_0121_0130` | `tests/test_integration_coherence_336.py` | `missing_tests_edge` | `phase_artifact_validation` |
| 126 | `batch_013_frontier_files_0121_0130` | `tests/test_issuance_analysis_256.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 127 | `batch_013_frontier_files_0121_0130` | `tests/test_issuance_evidence_closure_266.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 128 | `batch_013_frontier_files_0121_0130` | `tests/test_issuance_governance_activation_survey_247.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 129 | `batch_013_frontier_files_0121_0130` | `tests/test_issuance_governance_plan_233.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 130 | `batch_013_frontier_files_0121_0130` | `tests/test_kernel.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 131 | `batch_014_frontier_files_0131_0140` | `tests/test_known_records_migration_phase_197.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 132 | `batch_014_frontier_files_0131_0140` | `tests/test_ledger_config_typed_contract_guardrails_phase1.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 133 | `batch_014_frontier_files_0131_0140` | `tests/test_ledger_export_domain_exceptions.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 134 | `batch_014_frontier_files_0131_0140` | `tests/test_ledger_persistence.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 135 | `batch_014_frontier_files_0131_0140` | `tests/test_ledger_signature_migration_contract_282.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 136 | `batch_014_frontier_files_0131_0140` | `tests/test_ledger_typed_contract_guardrails_phase2.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 137 | `batch_014_frontier_files_0131_0140` | `tests/test_ledger_typed_contract_guardrails_phase3.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 138 | `batch_014_frontier_files_0131_0140` | `tests/test_ledger_typed_contract_guardrails_phase4.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 139 | `batch_014_frontier_files_0131_0140` | `tests/test_license_presence_phase_997.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 140 | `batch_014_frontier_files_0131_0140` | `tests/test_light_cone_kpis.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 141 | `batch_015_frontier_files_0141_0150` | `tests/test_lineage_event_schema_phase_240.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 142 | `batch_015_frontier_files_0141_0150` | `tests/test_lmdb_public_runtime_store.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 143 | `batch_015_frontier_files_0141_0150` | `tests/test_local_spectral_analytics.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 144 | `batch_015_frontier_files_0141_0150` | `tests/test_logging_config.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 145 | `batch_015_frontier_files_0141_0150` | `tests/test_logging_entry_surface_contracts.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 146 | `batch_015_frontier_files_0141_0150` | `tests/test_main_track_return_closure_gate_phase_201.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 147 | `batch_015_frontier_files_0141_0150` | `tests/test_main_track_return_closure_gate_phase_211.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 148 | `batch_015_frontier_files_0141_0150` | `tests/test_main_track_return_closure_gate_phase_221.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 149 | `batch_015_frontier_files_0141_0150` | `tests/test_main_track_return_preflight_gate_phase_200.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 150 | `batch_015_frontier_files_0141_0150` | `tests/test_main_track_return_preflight_gate_phase_210.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 151 | `batch_016_frontier_files_0151_0160` | `tests/test_main_track_return_preflight_gate_phase_220.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 152 | `batch_016_frontier_files_0151_0160` | `tests/test_mcp_cli_adapter.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 153 | `batch_016_frontier_files_0151_0160` | `tests/test_mcp_cli_domain_exceptions.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 154 | `batch_016_frontier_files_0151_0160` | `tests/test_mempalace_logic_gate_profile_and_window_607_615.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 155 | `batch_016_frontier_files_0151_0160` | `tests/test_merkle_laplacian_v02_followon_sims.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 156 | `batch_016_frontier_files_0151_0160` | `tests/test_merkle_laplacian_v02_strike_force_sim.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 157 | `batch_016_frontier_files_0151_0160` | `tests/test_meta_test_integrity_controls.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 158 | `batch_016_frontier_files_0151_0160` | `tests/test_mutation_canary_phase_297.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 159 | `batch_016_frontier_files_0151_0160` | `tests/test_namespace_health.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 160 | `batch_016_frontier_files_0151_0160` | `tests/test_network.py` | `missing_tests_edge` | `phase_artifact_validation` |
| 161 | `batch_017_frontier_files_0161_0170` | `tests/test_network_gossip.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 162 | `batch_017_frontier_files_0161_0170` | `tests/test_network_topology.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 163 | `batch_017_frontier_files_0161_0170` | `tests/test_no_ellipses_in_walkthroughs.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 164 | `batch_017_frontier_files_0161_0170` | `tests/test_no_silent_exception_pass_phase_1000.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 165 | `batch_017_frontier_files_0161_0170` | `tests/test_node_id_dual_contract_phase_1002.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 166 | `batch_017_frontier_files_0161_0170` | `tests/test_node_id_migration_utility_phase_1004.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 167 | `batch_017_frontier_files_0161_0170` | `tests/test_node_id_runtime_bridge_phase_1003.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 168 | `batch_017_frontier_files_0161_0170` | `tests/test_node_load_export.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 169 | `batch_017_frontier_files_0161_0170` | `tests/test_node_schema_implementation_readiness_356.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 170 | `batch_017_frontier_files_0161_0170` | `tests/test_node_value_conformance_phase_206.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 171 | `batch_018_frontier_files_0171_0180` | `tests/test_node_value_extraction_phase_204.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 172 | `batch_018_frontier_files_0171_0180` | `tests/test_node_value_governance_conformance_gate_phase_219.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 173 | `batch_018_frontier_files_0171_0180` | `tests/test_node_value_governance_conformance_phase_219.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 174 | `batch_018_frontier_files_0171_0180` | `tests/test_node_value_input_canon_phase_203.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 175 | `batch_018_frontier_files_0171_0180` | `tests/test_node_value_kernel_phase_205.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 176 | `batch_018_frontier_files_0171_0180` | `tests/test_node_value_policy_migration_phase_209.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 177 | `batch_018_frontier_files_0171_0180` | `tests/test_nodeid_strict_canonical_closure_gate_phase_1014.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 178 | `batch_018_frontier_files_0171_0180` | `tests/test_non_replay_domain_exception_foundation.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 179 | `batch_018_frontier_files_0171_0180` | `tests/test_non_replay_domain_exception_migration_closure_gate.py` | `missing_expected_authority_trace` | `authority_trace_review_required` |
| 180 | `batch_018_frontier_files_0171_0180` | `tests/test_non_replay_domain_exception_migration_guardrail.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 181 | `batch_019_frontier_files_0181_0190` | `tests/test_operator_config_docs_phase_1008.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 182 | `batch_019_frontier_files_0181_0190` | `tests/test_outcome_logger.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 183 | `batch_019_frontier_files_0181_0190` | `tests/test_package_hygiene_phase_1005.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 184 | `batch_019_frontier_files_0181_0190` | `tests/test_paradigm_shift.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 185 | `batch_019_frontier_files_0181_0190` | `tests/test_patent_application_numbers_status.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 186 | `batch_019_frontier_files_0181_0190` | `tests/test_path_lift_counterfactual_phase_214.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 187 | `batch_019_frontier_files_0181_0190` | `tests/test_phase_0947_h012_epoch_attribution_settle.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 188 | `batch_019_frontier_files_0181_0190` | `tests/test_phase_1101_window_945_1101_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 189 | `batch_019_frontier_files_0181_0190` | `tests/test_phase_1107_h_con_02_panel_quorum_settle.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 190 | `batch_019_frontier_files_0181_0190` | `tests/test_phase_1115_cdl_084_provenance_chain_attribution.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 191 | `batch_020_frontier_files_0191_0200` | `tests/test_phase_1120_sim_provenance_01_commissioning.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 192 | `batch_020_frontier_files_0191_0200` | `tests/test_phase_1121_sim_provenance_01_run02_disposition.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 193 | `batch_020_frontier_files_0191_0200` | `tests/test_phase_1123_window_1118_1123_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 194 | `batch_020_frontier_files_0191_0200` | `tests/test_phase_1127_cdl_084_q2_amendment.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 195 | `batch_020_frontier_files_0191_0200` | `tests/test_phase_1129_fix1_provenance_input_hardening.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 196 | `batch_020_frontier_files_0191_0200` | `tests/test_phase_1131_sim_spectral_02_signal_definition.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 197 | `batch_020_frontier_files_0191_0200` | `tests/test_phase_1132_sim_spectral_02_harness.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 198 | `batch_020_frontier_files_0191_0200` | `tests/test_phase_1133_sim_spectral_02_fix2.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 199 | `batch_020_frontier_files_0191_0200` | `tests/test_phase_1133_sim_spectral_02_fix3.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 200 | `batch_020_frontier_files_0191_0200` | `tests/test_phase_1133_sim_spectral_02_run01.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 201 | `batch_021_frontier_files_0201_0210` | `tests/test_phase_1134_sim_spectral_02_run01_disposition.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 202 | `batch_021_frontier_files_0201_0210` | `tests/test_phase_1135_fix1_sim_spectral_02_run02_homoiconic.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 203 | `batch_021_frontier_files_0201_0210` | `tests/test_phase_1135_sim_spectral_02_run02.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 204 | `batch_021_frontier_files_0201_0210` | `tests/test_phase_1136_sim_spectral_02_run02_disposition.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 205 | `batch_021_frontier_files_0201_0210` | `tests/test_phase_1136a_genesis_morphogenic_hypergraph_atlas.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 206 | `batch_021_frontier_files_0201_0210` | `tests/test_phase_1137_coherence_capsule_v5_38.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 207 | `batch_021_frontier_files_0201_0210` | `tests/test_phase_1140_run02_fix2_corrected_baseline.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 208 | `batch_021_frontier_files_0201_0210` | `tests/test_phase_1141_run02_fix2_disposition_addendum.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 209 | `batch_021_frontier_files_0201_0210` | `tests/test_phase_1142_atlas_tier1_genesis_attestation.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 210 | `batch_021_frontier_files_0201_0210` | `tests/test_phase_1142s_genesis_signing_ceremony.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 211 | `batch_022_frontier_files_0211_0220` | `tests/test_phase_1143_genesis_compile_checkpoint_1.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 212 | `batch_022_frontier_files_0211_0220` | `tests/test_phase_1144_sim_spectral_03_harness.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 213 | `batch_022_frontier_files_0211_0220` | `tests/test_phase_1145_sim_spectral_03_run01.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 214 | `batch_022_frontier_files_0211_0220` | `tests/test_phase_1145a_topology_search.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 215 | `batch_022_frontier_files_0211_0220` | `tests/test_phase_1146_sim_spectral_03_disposition.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 216 | `batch_022_frontier_files_0211_0220` | `tests/test_phase_1147_window_1139_1147_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 217 | `batch_022_frontier_files_0211_0220` | `tests/test_phase_1150_genesis_compile_checkpoint_2.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 218 | `batch_022_frontier_files_0211_0220` | `tests/test_phase_1151_composability_audit.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 219 | `batch_022_frontier_files_0211_0220` | `tests/test_phase_1152_sim_spectral_04_program_spec.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 220 | `batch_022_frontier_files_0211_0220` | `tests/test_phase_1154_pre_public_rc_obligations_synthesis.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 221 | `batch_023_frontier_files_0221_0230` | `tests/test_phase_1157_adr_0020_acceptance.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 222 | `batch_023_frontier_files_0221_0230` | `tests/test_phase_1158_adr_batch_acceptance.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 223 | `batch_023_frontier_files_0221_0230` | `tests/test_phase_1159_adr_0036_release_key_draft.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 224 | `batch_023_frontier_files_0221_0230` | `tests/test_phase_1160_claim_composition_projection_build.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 225 | `batch_023_frontier_files_0221_0230` | `tests/test_phase_1161_sim_spectral_04_run01.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 226 | `batch_023_frontier_files_0221_0230` | `tests/test_phase_1162_sim_spectral_04_disposition.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 227 | `batch_023_frontier_files_0221_0230` | `tests/test_phase_1169_sim_spectral_05_track_a.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 228 | `batch_023_frontier_files_0221_0230` | `tests/test_phase_1170_branchial_projection_build.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 229 | `batch_023_frontier_files_0221_0230` | `tests/test_phase_1171_sim_spectral_05_disposition.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 230 | `batch_023_frontier_files_0221_0230` | `tests/test_phase_1172_cdl_085_opening.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 231 | `batch_024_frontier_files_0231_0240` | `tests/test_phase_1173_adr_0036_0037_acceptance.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 232 | `batch_024_frontier_files_0231_0240` | `tests/test_phase_1176_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 233 | `batch_024_frontier_files_0231_0240` | `tests/test_phase_1177_cdl_085_prelock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 234 | `batch_024_frontier_files_0231_0240` | `tests/test_phase_1179_sim_spectral_05_runtime_binding_slice.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 235 | `batch_024_frontier_files_0231_0240` | `tests/test_phase_1180_sim_spectral_05_economic_flow_slice.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 236 | `batch_024_frontier_files_0231_0240` | `tests/test_phase_1181_coherence_capsule_v5_43.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 237 | `batch_024_frontier_files_0231_0240` | `tests/test_phase_1183_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 238 | `batch_024_frontier_files_0231_0240` | `tests/test_phase_1184_cdl_085_prelock_hardening.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 239 | `batch_024_frontier_files_0231_0240` | `tests/test_phase_1185_cdl_085_ratification.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 240 | `batch_024_frontier_files_0231_0240` | `tests/test_phase_1187_sim_spectral_05_gossip_slice.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 241 | `batch_025_frontier_files_0241_0250` | `tests/test_phase_1188_cdl_001_scoping.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 242 | `batch_025_frontier_files_0241_0250` | `tests/test_phase_1191_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 243 | `batch_025_frontier_files_0241_0250` | `tests/test_phase_1193_v0_2_signing_skip.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 244 | `batch_025_frontier_files_0241_0250` | `tests/test_phase_1194_cdl_086_public_launch_packaging_blocker.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 245 | `batch_025_frontier_files_0241_0250` | `tests/test_phase_1195_tier3_runtime_linkage.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 246 | `batch_025_frontier_files_0241_0250` | `tests/test_phase_1196_persistent_rate_limiter.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 247 | `batch_025_frontier_files_0241_0250` | `tests/test_phase_1197_canon_bundle_signing_repair.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 248 | `batch_025_frontier_files_0241_0250` | `tests/test_phase_1200_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 249 | `batch_025_frontier_files_0241_0250` | `tests/test_phase_1202_persistent_rate_limiter.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 250 | `batch_025_frontier_files_0241_0250` | `tests/test_phase_1203_cdl_086_deliberation.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 251 | `batch_026_frontier_files_0251_0260` | `tests/test_phase_1209_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 252 | `batch_026_frontier_files_0251_0260` | `tests/test_phase_1210_phi_bound_enforcement.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 253 | `batch_026_frontier_files_0251_0260` | `tests/test_phase_1211_truth_primitive_permanence_packet.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 254 | `batch_026_frontier_files_0251_0260` | `tests/test_phase_1212_rate_limiter_wiring.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 255 | `batch_026_frontier_files_0251_0260` | `tests/test_phase_1214_cdl_086_deferral.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 256 | `batch_026_frontier_files_0251_0260` | `tests/test_phase_1215_v0_2_signing_skip.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 257 | `batch_026_frontier_files_0251_0260` | `tests/test_phase_1217_post_closure_audit_hardening.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 258 | `batch_026_frontier_files_0251_0260` | `tests/test_phase_1218_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 259 | `batch_026_frontier_files_0251_0260` | `tests/test_phase_1218b_security_hardening.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 260 | `batch_026_frontier_files_0251_0260` | `tests/test_phase_1221_v0_2_signing_skip.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 261 | `batch_027_frontier_files_0261_0270` | `tests/test_phase_1222_reciprocal_fetch_admission_spec.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 262 | `batch_027_frontier_files_0261_0270` | `tests/test_phase_1223_coherence_capsule_v5_48.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 263 | `batch_027_frontier_files_0261_0270` | `tests/test_phase_1224_fix1_post_closure_audit_hardening.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 264 | `batch_027_frontier_files_0261_0270` | `tests/test_phase_1225_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 265 | `batch_027_frontier_files_0261_0270` | `tests/test_phase_1228_cdl_087_prelock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 266 | `batch_027_frontier_files_0261_0270` | `tests/test_phase_1229_agent_graph_projection_runtime.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 267 | `batch_027_frontier_files_0261_0270` | `tests/test_phase_1230_v0_2_signing_skip.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 268 | `batch_027_frontier_files_0261_0270` | `tests/test_phase_1231_coherence_capsule_v5_49.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 269 | `batch_027_frontier_files_0261_0270` | `tests/test_phase_1235_commit_epoch_canonical_mutation.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 270 | `batch_027_frontier_files_0261_0270` | `tests/test_phase_1236_commit_epoch_emission_connector.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 271 | `batch_028_frontier_files_0271_0280` | `tests/test_phase_1236_fix1_commit_epoch_full_connector_spec.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 272 | `batch_028_frontier_files_0271_0280` | `tests/test_phase_1236_fix2_commit_epoch_quorum_projection.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 273 | `batch_028_frontier_files_0271_0280` | `tests/test_phase_1236_fix3_commit_epoch_causal_frontier_projection.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 274 | `batch_028_frontier_files_0271_0280` | `tests/test_phase_1236_fix4_commit_epoch_finalized_adapter.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 275 | `batch_028_frontier_files_0271_0280` | `tests/test_phase_1236_fix5_rust_fixture_mapping.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 276 | `batch_028_frontier_files_0271_0280` | `tests/test_phase_1236_fix6_devnet_end_to_end_harness.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 277 | `batch_028_frontier_files_0271_0280` | `tests/test_phase_1237_fix2_ego_graph_query.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 278 | `batch_028_frontier_files_0271_0280` | `tests/test_phase_1237_fix3_centrality_metrics.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 279 | `batch_028_frontier_files_0271_0280` | `tests/test_phase_1237_fix4_convergence_trace.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 280 | `batch_028_frontier_files_0271_0280` | `tests/test_phase_1237_fix5_dispatcher_integration.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 281 | `batch_029_frontier_files_0281_0290` | `tests/test_phase_1237_fix6_canonical_export_bundle.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 282 | `batch_029_frontier_files_0281_0290` | `tests/test_phase_1237_l3_sidecar_spec.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 283 | `batch_029_frontier_files_0281_0290` | `tests/test_phase_1237_post_fix7_sidecar_audit_hardening.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 284 | `batch_029_frontier_files_0281_0290` | `tests/test_phase_1237_sidecar_query_runtime.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 285 | `batch_029_frontier_files_0281_0290` | `tests/test_phase_1238_sim_fetch_01_harness.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 286 | `batch_029_frontier_files_0281_0290` | `tests/test_phase_1238a_sim_fetch_01_fix1_hardening.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 287 | `batch_029_frontier_files_0281_0290` | `tests/test_phase_1238b_sim_fetch_01_fix2_request_model.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 288 | `batch_029_frontier_files_0281_0290` | `tests/test_phase_1238c_sim_fetch_01_fix3_tier_verdict.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 289 | `batch_029_frontier_files_0281_0290` | `tests/test_phase_1238d_sim_fetch_01_fix4_routed_holder_model.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 290 | `batch_029_frontier_files_0281_0290` | `tests/test_phase_1238e_sim_fetch_01_fix5_routed_multihop_retry.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 291 | `batch_030_frontier_files_0291_0300` | `tests/test_phase_1238f_sim_fetch_01_fix6_adaptive_heat_replication.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 292 | `batch_030_frontier_files_0291_0300` | `tests/test_phase_1238g_sim_fetch_01_fix7_cdl_078_credit_bridge.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 293 | `batch_030_frontier_files_0291_0300` | `tests/test_phase_1238h_sim_fetch_01_fix8_werner_overlay.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 294 | `batch_030_frontier_files_0291_0300` | `tests/test_phase_1238i_sim_fetch_01_fix9_cdl_087_evidence_matrix.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 295 | `batch_030_frontier_files_0291_0300` | `tests/test_phase_1238j_sim_fetch_01_fix10_robustness_suite.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 296 | `batch_030_frontier_files_0291_0300` | `tests/test_phase_1241_1248_prompt_schema_and_tokens.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 297 | `batch_030_frontier_files_0291_0300` | `tests/test_phase_1242_roadmap_v1_1.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 298 | `batch_030_frontier_files_0291_0300` | `tests/test_phase_1243_package_boundary_inventory.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 299 | `batch_030_frontier_files_0291_0300` | `tests/test_phase_1244_import_boundary_lint_and_protocol_stubs.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 300 | `batch_030_frontier_files_0291_0300` | `tests/test_phase_1245_openclaw_nemoclaw_skill_preview_dependency_isolation.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 301 | `batch_031_frontier_files_0301_0310` | `tests/test_phase_1246_cdl_087_governance_review_disposition.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 302 | `batch_031_frontier_files_0301_0310` | `tests/test_phase_1248_window_1241_1248_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 303 | `batch_031_frontier_files_0301_0310` | `tests/test_phase_1250_fix1_rc_frontier_gap_audit.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 304 | `batch_031_frontier_files_0301_0310` | `tests/test_phase_1250_gap14_adapter_extraction.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 305 | `batch_031_frontier_files_0301_0310` | `tests/test_phase_1252_post_audit_route_consistency.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 306 | `batch_031_frontier_files_0301_0310` | `tests/test_phase_1253_transport_principal_identity_spec.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 307 | `batch_031_frontier_files_0301_0310` | `tests/test_phase_1254_atlas_g_004_005_graph_bridge.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 308 | `batch_031_frontier_files_0301_0310` | `tests/test_phase_1258_cdl087_production_candidate_evidence_readiness.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 309 | `batch_031_frontier_files_0301_0310` | `tests/test_phase_1259_cdl087_serving_peer_evidence_slice.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 310 | `batch_031_frontier_files_0301_0310` | `tests/test_phase_1260_cdl087_observability_and_limiter_regression.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 311 | `batch_032_frontier_files_0311_0320` | `tests/test_phase_1262_werner_flow_governor_overlay_validation.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 312 | `batch_032_frontier_files_0311_0320` | `tests/test_phase_1268_sidecar_loopback_projection_endpoint_boundary.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 313 | `batch_032_frontier_files_0311_0320` | `tests/test_phase_1287_release_publication_signing_authorization_preflight.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 314 | `batch_032_frontier_files_0311_0320` | `tests/test_phase_1289_window_1289_1302_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 315 | `batch_032_frontier_files_0311_0320` | `tests/test_phase_1290_context_capsule_v5_52_frontier_refresh.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 316 | `batch_032_frontier_files_0311_0320` | `tests/test_phase_1299_release_allowlist_artifact_genesis_readiness_preflight.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 317 | `batch_032_frontier_files_0311_0320` | `tests/test_phase_1300_counsel_ip_publication_clearance_inventory.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 318 | `batch_032_frontier_files_0311_0320` | `tests/test_phase_1302_window_1289_1302_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 319 | `batch_032_frontier_files_0311_0320` | `tests/test_phase_1303_window_1303_1316_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 320 | `batch_032_frontier_files_0311_0320` | `tests/test_phase_1304_context_capsule_v5_53_frontier_refresh.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 321 | `batch_033_frontier_files_0321_0330` | `tests/test_phase_1316_window_1303_1316_closure_implementation_audit.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 322 | `batch_033_frontier_files_0321_0330` | `tests/test_phase_1317_window_1317_1329_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 323 | `batch_033_frontier_files_0321_0330` | `tests/test_phase_1318_context_capsule_v5_54_frontier_refresh.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 324 | `batch_033_frontier_files_0321_0330` | `tests/test_phase_1323_fix2_openclaw_vps_install_skill_discovery.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 325 | `batch_033_frontier_files_0321_0330` | `tests/test_phase_1323_fix3_layered_license_posture.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 326 | `batch_033_frontier_files_0321_0330` | `tests/test_phase_1323_openclaw_nemoclaw_claimable_profile_full_dry_run.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 327 | `batch_033_frontier_files_0321_0330` | `tests/test_phase_1326_ccss_003_sealed_sender_local_delivery_boundary.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 328 | `batch_033_frontier_files_0321_0330` | `tests/test_phase_1327_ccss_004_gossip_jitter_cover_policy_tests.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 329 | `batch_033_frontier_files_0321_0330` | `tests/test_phase_1330_window_1330_1342_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 330 | `batch_033_frontier_files_0321_0330` | `tests/test_phase_1331_context_capsule_v5_55_release_candidate_freeze.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 331 | `batch_034_frontier_files_0331_0340` | `tests/test_phase_1331_fix3_network_dos_hardening.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 332 | `batch_034_frontier_files_0331_0340` | `tests/test_phase_1332_fix4_pre_1333_hardening.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 333 | `batch_034_frontier_files_0331_0340` | `tests/test_phase_1333_source_allowlist_export_execution_gate.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 334 | `batch_034_frontier_files_0331_0340` | `tests/test_phase_1334_release_artifact_production_gate.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 335 | `batch_034_frontier_files_0331_0340` | `tests/test_phase_1335_release_keys_envelopes_generation_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 336 | `batch_034_frontier_files_0331_0340` | `tests/test_phase_1336_public_claimability_api_activation_or_carry_forward_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 337 | `batch_034_frontier_files_0331_0340` | `tests/test_phase_1337_public_path_sidecar_activation_or_exclusion_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 338 | `batch_034_frontier_files_0331_0340` | `tests/test_phase_1338_wallet_ecu_ilc_activation_or_carry_forward_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 339 | `batch_034_frontier_files_0331_0340` | `tests/test_phase_1340_v0_2_signing_ceremony_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 340 | `batch_034_frontier_files_0331_0340` | `tests/test_phase_1341_public_rc_publication_claim_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 341 | `batch_035_frontier_files_0341_0350` | `tests/test_phase_1342_window_1330_1342_closure_handoff.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 342 | `batch_035_frontier_files_0341_0350` | `tests/test_phase_1344_issuance_stack_scoping.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 343 | `batch_035_frontier_files_0341_0350` | `tests/test_phase_1348_cdl_047_treasury_governance_runtime.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 344 | `batch_035_frontier_files_0341_0350` | `tests/test_phase_1350_cdl_083_ejected_stake_treasury_distribution.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 345 | `batch_035_frontier_files_0341_0350` | `tests/test_phase_1351a_cdl_029_amendment_post_theta_hard_dust_routing.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 346 | `batch_035_frontier_files_0341_0350` | `tests/test_phase_1352_issuance_economics_integration_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 347 | `batch_035_frontier_files_0341_0350` | `tests/test_phase_1354_cdl_068_topology_shuffle_vrf.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 348 | `batch_035_frontier_files_0341_0350` | `tests/test_phase_1357_reputation_h11_float_kill.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 349 | `batch_035_frontier_files_0341_0350` | `tests/test_phase_1358_production_bridge.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 350 | `batch_035_frontier_files_0341_0350` | `tests/test_phase_1359_high_001_defense.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 351 | `batch_036_frontier_files_0351_0360` | `tests/test_phase_1360_multi_operator_testnet.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 352 | `batch_036_frontier_files_0351_0360` | `tests/test_phase_1361_adaptive_pruning.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 353 | `batch_036_frontier_files_0351_0360` | `tests/test_phase_1363_blocking_authority_prelock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 354 | `batch_036_frontier_files_0351_0360` | `tests/test_phase_1367_pre_gate_fix_pass.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 355 | `batch_036_frontier_files_0351_0360` | `tests/test_phase_1369_fix1_numeric_hardening.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 356 | `batch_036_frontier_files_0351_0360` | `tests/test_phase_1369_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 357 | `batch_036_frontier_files_0351_0360` | `tests/test_phase_1371_identity_bootstrap_cdl_opening.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 358 | `batch_036_frontier_files_0351_0360` | `tests/test_phase_1372_identity_bootstrap_cdl_prelock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 359 | `batch_036_frontier_files_0351_0360` | `tests/test_phase_1375_cdl_088_prelock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 360 | `batch_036_frontier_files_0351_0360` | `tests/test_phase_1385_tla_safetynodualcert_disposition.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 361 | `batch_037_frontier_files_0361_0370` | `tests/test_phase_1385a_spec_d_epoch_checkpoint_safety.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 362 | `batch_037_frontier_files_0361_0370` | `tests/test_phase_1386_genesis_validator_bootstrap_record.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 363 | `batch_037_frontier_files_0361_0370` | `tests/test_phase_1387b_sim_genesis_compile_02.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 364 | `batch_037_frontier_files_0361_0370` | `tests/test_phase_1387c_compiler_basis_expansion.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 365 | `batch_037_frontier_files_0361_0370` | `tests/test_phase_1387d_adr_0035_spec.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 366 | `batch_037_frontier_files_0361_0370` | `tests/test_phase_1387e_star_map_expansion.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 367 | `batch_037_frontier_files_0361_0370` | `tests/test_phase_1387f_graph_structure_analysis.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 368 | `batch_037_frontier_files_0361_0370` | `tests/test_phase_1387g_epistemic_leverage.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 369 | `batch_037_frontier_files_0361_0370` | `tests/test_phase_1387h_edge_recipe_canonicalization.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 370 | `batch_037_frontier_files_0361_0370` | `tests/test_phase_1387i_synthesis_report.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 371 | `batch_038_frontier_files_0371_0380` | `tests/test_phase_1388a_cdl_048_self_counsel_clearance.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 372 | `batch_038_frontier_files_0371_0380` | `tests/test_phase_1389b_claimability_public_mode_runtime.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 373 | `batch_038_frontier_files_0371_0380` | `tests/test_phase_1389b_claimability_public_mode_runtime_docs.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 374 | `batch_038_frontier_files_0371_0380` | `tests/test_phase_1390_window_closure_handoff.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 375 | `batch_038_frontier_files_0371_0380` | `tests/test_phase_1396_j006_jury_assignment_runtime.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 376 | `batch_038_frontier_files_0371_0380` | `tests/test_phase_1397_j007_shadow_public_ingestion_harness.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 377 | `batch_038_frontier_files_0371_0380` | `tests/test_phase_1401_cdl_091_runtime_stub.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 378 | `batch_038_frontier_files_0371_0380` | `tests/test_phase_1409_cdl_093_maintenance_lottery_stub.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 379 | `batch_038_frontier_files_0371_0380` | `tests/test_phase_1410_fix1_pre_vrf_hardening.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 380 | `batch_038_frontier_files_0371_0380` | `tests/test_phase_1410_vrf_adr.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 381 | `batch_039_frontier_files_0381_0390` | `tests/test_phase_1411_vrf_proof_verifier.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 382 | `batch_039_frontier_files_0381_0390` | `tests/test_phase_1412_vrf_integration.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 383 | `batch_039_frontier_files_0381_0390` | `tests/test_phase_1413_vrf_integration.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 384 | `batch_039_frontier_files_0381_0390` | `tests/test_phase_1414_review_lane_adr.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 385 | `batch_039_frontier_files_0381_0390` | `tests/test_phase_1415_review_lane_admission_runtime.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 386 | `batch_039_frontier_files_0381_0390` | `tests/test_phase_1416_review_lane_dedup_payment_stub.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 387 | `batch_039_frontier_files_0381_0390` | `tests/test_phase_1417_review_lane_integration.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 388 | `batch_039_frontier_files_0381_0390` | `tests/test_phase_1418_anti_capture_diversity_adr.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 389 | `batch_039_frontier_files_0381_0390` | `tests/test_phase_1419_anti_capture_diversity_verification.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 390 | `batch_039_frontier_files_0381_0390` | `tests/test_phase_1423_rehearsal_criteria.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 391 | `batch_040_frontier_files_0391_0400` | `tests/test_phase_1425_pre_gate_verification.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 392 | `batch_040_frontier_files_0391_0400` | `tests/test_phase_1428_window_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 393 | `batch_040_frontier_files_0391_0400` | `tests/test_phase_1433_rehearsal_verdict.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 394 | `batch_040_frontier_files_0391_0400` | `tests/test_phase_1436_public_fetch_serving_activation.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 395 | `batch_040_frontier_files_0391_0400` | `tests/test_phase_1438_cdl088_public_claimability_activation.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 396 | `batch_040_frontier_files_0391_0400` | `tests/test_phase_1439_public_verifier_api_activation.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 397 | `batch_040_frontier_files_0391_0400` | `tests/test_phase_1440_claimability_integration_tests.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 398 | `batch_040_frontier_files_0391_0400` | `tests/test_phase_1441_gap_13_closure_verdict.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 399 | `batch_040_frontier_files_0391_0400` | `tests/test_phase_1442_werner_diagnostic_wiring.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 400 | `batch_040_frontier_files_0391_0400` | `tests/test_phase_1443_agpl_license_header_audit_allowlist.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 401 | `batch_041_frontier_files_0401_0410` | `tests/test_phase_1444_cla_text_finalization.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 402 | `batch_041_frontier_files_0401_0410` | `tests/test_phase_1445_gap_7_partial_closure.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 403 | `batch_041_frontier_files_0401_0410` | `tests/test_phase_1446_v03_genesis_root_signing_ceremony.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 404 | `batch_041_frontier_files_0401_0410` | `tests/test_phase_1447_release_artifact_signing_manifest.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 405 | `batch_041_frontier_files_0401_0410` | `tests/test_phase_1460p_provider_usage_adapter.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 406 | `batch_041_frontier_files_0401_0410` | `tests/test_phase_1461p_local_node_capture_consent_gate.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 407 | `batch_041_frontier_files_0401_0410` | `tests/test_phase_1462p_idle_capacity_scheduler.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 408 | `batch_041_frontier_files_0401_0410` | `tests/test_phase_1464p_co_attestation_receipt.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 409 | `batch_041_frontier_files_0401_0410` | `tests/test_phase_1464p_maintenance_task_executor.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 410 | `batch_041_frontier_files_0401_0410` | `tests/test_phase_1465p_harness_integration.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 411 | `batch_042_frontier_files_0411_0420` | `tests/test_phase_1466p_layer0_protocol_bundle.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 412 | `batch_042_frontier_files_0411_0420` | `tests/test_phase_1475p_layer1_genesis_bundle.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 413 | `batch_042_frontier_files_0411_0420` | `tests/test_phase_1476p_adr0009_cross_layer.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 414 | `batch_042_frontier_files_0411_0420` | `tests/test_phase_1476p_adr0009_layers23.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 415 | `batch_042_frontier_files_0411_0420` | `tests/test_phase_1477p_harness_kernel_integration.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 416 | `batch_042_frontier_files_0411_0420` | `tests/test_phase_1483p_rust_p2p_bridge.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 417 | `batch_042_frontier_files_0411_0420` | `tests/test_phase_1485p_consent_gate_local_write.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 418 | `batch_042_frontier_files_0411_0420` | `tests/test_phase_1490p_cdl094_admission_wire.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 419 | `batch_042_frontier_files_0411_0420` | `tests/test_phase_1494p_cdl095_runtime_completions.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 420 | `batch_042_frontier_files_0411_0420` | `tests/test_phase_1502p_cdl031_dynamic_ranking_multiplier.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 421 | `batch_043_frontier_files_0421_0430` | `tests/test_phase_1508p_werner_sim_fetch_rerun.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 422 | `batch_043_frontier_files_0421_0430` | `tests/test_phase_1509p_cdl096_eligibility_checkpoint.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 423 | `batch_043_frontier_files_0421_0430` | `tests/test_phase_1512p_genesis_governance_node_frameworks.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 424 | `batch_043_frontier_files_0421_0430` | `tests/test_phase_1513p_window_coherence_capsule.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 425 | `batch_043_frontier_files_0421_0430` | `tests/test_phase_1514p_window_1505p_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 426 | `batch_043_frontier_files_0421_0430` | `tests/test_phase_1516p_adr_0009_layer0_layer1_integration.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 427 | `batch_043_frontier_files_0421_0430` | `tests/test_phase_1517p_adr_0009_layer2_layer3_integration.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 428 | `batch_043_frontier_files_0421_0430` | `tests/test_phase_1518p_adr_0009_bundle_verifier.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 429 | `batch_043_frontier_files_0421_0430` | `tests/test_phase_1524p_adr0035_dependency_reconciliation.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 430 | `batch_043_frontier_files_0421_0430` | `tests/test_phase_1525p_adr0035_definition_node_schema.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 431 | `batch_044_frontier_files_0431_0440` | `tests/test_phase_1526p_adr0035_type_system_cdl_opening.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 432 | `batch_044_frontier_files_0431_0440` | `tests/test_phase_1527p_adr0035_cdl_prelock.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 433 | `batch_044_frontier_files_0431_0440` | `tests/test_phase_1528p_adr0035_cdl_ratification.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 434 | `batch_044_frontier_files_0431_0440` | `tests/test_phase_1529p_adr0035_type_registry_scaffold.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 435 | `batch_044_frontier_files_0431_0440` | `tests/test_phase_1532p_obl020_emission_production_path.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 436 | `batch_044_frontier_files_0431_0440` | `tests/test_phase_1533p_obl020_settlement_roots.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 437 | `batch_044_frontier_files_0431_0440` | `tests/test_phase_1534p_obl020_canonical_economic_events.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 438 | `batch_044_frontier_files_0431_0440` | `tests/test_phase_1535p_obl020_economic_round_trip.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 439 | `batch_044_frontier_files_0431_0440` | `tests/test_phase_1539p_obl021_validator_admission_ejection.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 440 | `batch_044_frontier_files_0431_0440` | `tests/test_phase_1540p_obl022_treasury_validator_reward.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 441 | `batch_045_frontier_files_0441_0450` | `tests/test_phase_1541p_obl022_ejected_stake.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 442 | `batch_045_frontier_files_0441_0450` | `tests/test_phase_1542p_obl027_expansion_bounty.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 443 | `batch_045_frontier_files_0441_0450` | `tests/test_phase_1543p_block4b_round_trip.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 444 | `batch_045_frontier_files_0441_0450` | `tests/test_phase_1545p_fix13_agentic_graph_grammar_axiom_inventory.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 445 | `batch_045_frontier_files_0441_0450` | `tests/test_phase_1545p_fix19_atlas_axiomatic_calibration.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 446 | `batch_045_frontier_files_0441_0450` | `tests/test_phase_1545p_fix20_atlas_precision_replay.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 447 | `batch_045_frontier_files_0441_0450` | `tests/test_phase_1545p_fix22_full_repo_genesis_atlas.py` | `missing_candidate_node` | `full_repo_atlas_candidate_artifact_validation` |
| 448 | `batch_045_frontier_files_0441_0450` | `tests/test_phase_1545p_fix23_genesis_atlas_lmdb_materialization.py` | `missing_candidate_node` | `lmdb_materialization_adapter_and_sim_validation` |
| 449 | `batch_045_frontier_files_0441_0450` | `tests/test_phase_1545p_fix24_whole_graph_atlas_objective_contract.py` | `missing_candidate_node` | `whole_graph_objective_contract_validation` |
| 450 | `batch_045_frontier_files_0441_0450` | `tests/test_phase_1545p_fix25_whole_graph_baseline_diagnostic.py` | `missing_candidate_node` | `whole_graph_baseline_diagnostic_validation` |
| 451 | `batch_046_frontier_files_0451_0460` | `tests/test_phase_1545p_fix26_axiomatic_extraction_replay.py` | `missing_candidate_node` | `axiomatic_extraction_replay_validation` |
| 452 | `batch_046_frontier_files_0451_0460` | `tests/test_phase_1545p_fix27_rewrite_candidate_generation.py` | `missing_candidate_node` | `rewrite_candidate_generation_validation` |
| 453 | `batch_046_frontier_files_0451_0460` | `tests/test_phase_1545p_fix28_projection_hydration_sim.py` | `missing_candidate_node` | `projection_hydration_sim_validation` |
| 454 | `batch_046_frontier_files_0451_0460` | `tests/test_phase_1545p_fix29_spectral_non_excisability_sim.py` | `missing_candidate_node` | `spectral_non_excisability_sim_validation` |
| 455 | `batch_046_frontier_files_0451_0460` | `tests/test_phase_1545p_fix2_historical_snapshot_policy.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 456 | `batch_046_frontier_files_0451_0460` | `tests/test_phase_1545p_fix30_long_autoresearch_optimization.py` | `missing_candidate_node` | `long_autoresearch_optimization_validation` |
| 457 | `batch_046_frontier_files_0451_0460` | `tests/test_phase_1545p_fix31_candidate_reducer_v04_v05.py` | `missing_candidate_node` | `candidate_reducer_decision_packet_validation` |
| 458 | `batch_046_frontier_files_0451_0460` | `tests/test_phase_1545p_fix32_homoiconic_test_registry_contract.py` | `missing_candidate_node` | `homoiconic_test_registry_contract_validation` |
| 459 | `batch_046_frontier_files_0451_0460` | `tests/test_phase_1545p_fix33_test_graph_coverage.py` | `missing_candidate_node` | `test_graph_coverage_checker_validation` |
| 460 | `batch_046_frontier_files_0451_0460` | `tests/test_phase_1545p_fix4_patent_delivery_status.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 461 | `batch_047_frontier_files_0461_0470` | `tests/test_phase_1545p_fix5_public_disclosure_patent_coverage.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 462 | `batch_047_frontier_files_0461_0470` | `tests/test_phase_1545p_fix6_genesis_v03_methodology_preservation.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 463 | `batch_047_frontier_files_0461_0470` | `tests/test_phase_1545p_fix7_genesis_common_registry_node_candidates.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 464 | `batch_047_frontier_files_0461_0470` | `tests/test_phase_1546p_block5_sequence_lock_gap_refresh.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 465 | `batch_047_frontier_files_0461_0470` | `tests/test_phase_1546p_idea_descent_rehearsal_sidecar.py` | `missing_expected_authority_trace` | `adr_or_governance_validation` |
| 466 | `batch_047_frontier_files_0461_0470` | `tests/test_phase_1549p_obl028_adaptive_fee_burn.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 467 | `batch_047_frontier_files_0461_0470` | `tests/test_phase_1550p_obl029_peer_funded_bounty.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 468 | `batch_047_frontier_files_0461_0470` | `tests/test_phase_1552p_cdl096_prelock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 469 | `batch_047_frontier_files_0461_0470` | `tests/test_phase_1556_pre_rc_completion_gap_refresh.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 470 | `batch_047_frontier_files_0461_0470` | `tests/test_phase_1557_hb001_genesis_authority_assertion.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 471 | `batch_048_frontier_files_0471_0480` | `tests/test_phase_1558_hb003_layer0_truth_primitive_schemas.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 472 | `batch_048_frontier_files_0471_0480` | `tests/test_phase_1559_hb002_serving_receipt.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 473 | `batch_048_frontier_files_0471_0480` | `tests/test_phase_1560_agent_init_live.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 474 | `batch_048_frontier_files_0471_0480` | `tests/test_phase_1560_genesis_serving_receiver.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 475 | `batch_048_frontier_files_0471_0480` | `tests/test_phase_1560_preflight_blocker.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 476 | `batch_048_frontier_files_0471_0480` | `tests/test_phase_1561_ecu_live_smoke.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 477 | `batch_048_frontier_files_0471_0480` | `tests/test_phase_1561_fix1_balance_report_cli.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 478 | `batch_048_frontier_files_0471_0480` | `tests/test_phase_1562_invitation_provenance_chain.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 479 | `batch_048_frontier_files_0471_0480` | `tests/test_phase_226_security_triage_artifacts.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 480 | `batch_048_frontier_files_0471_0480` | `tests/test_phase_236_preflight.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 481 | `batch_049_frontier_files_0481_0490` | `tests/test_phase_396_cdl_v3_v7_governance_authorization_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 482 | `batch_049_frontier_files_0481_0490` | `tests/test_phase_428_cdl_049_bounded_existential_alignment_ratification.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 483 | `batch_049_frontier_files_0481_0490` | `tests/test_phase_429_sim_009_pe_stabilization_commissioning.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 484 | `batch_049_frontier_files_0481_0490` | `tests/test_phase_430_sim_009_results_synthesis_and_disposition.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 485 | `batch_049_frontier_files_0481_0490` | `tests/test_phase_431_pe_stabilization_carry_forward_decision.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 486 | `batch_049_frontier_files_0481_0490` | `tests/test_phase_436_runtime_tranche_benchmark_harness_and_tranche_completion.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 487 | `batch_049_frontier_files_0481_0490` | `tests/test_phase_437_runtime_tranche_findings_memo_and_regression_hardening.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 488 | `batch_049_frontier_files_0481_0490` | `tests/test_phase_438_treasury_pe_prerequisite_satisfaction_review.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 489 | `batch_049_frontier_files_0481_0490` | `tests/test_phase_439_coherence_and_capsule_v1_8.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 490 | `batch_049_frontier_files_0481_0490` | `tests/test_phase_446_consensus_runtime_iii_harness_integration.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 491 | `batch_050_frontier_files_0491_0500` | `tests/test_phase_447_consensus_adversarial_regression.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 492 | `batch_050_frontier_files_0491_0500` | `tests/test_phase_448_coherence_and_capsule_v1_9.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 493 | `batch_050_frontier_files_0491_0500` | `tests/test_phase_450_window_sequence_lock_and_lane_identity_freeze.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 494 | `batch_050_frontier_files_0491_0500` | `tests/test_phase_452_l1_l2_prerequisite_disposition.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 495 | `batch_050_frontier_files_0491_0500` | `tests/test_phase_454_sim_t_evidence_package.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 496 | `batch_050_frontier_files_0491_0500` | `tests/test_phase_455_sim_t_comparative_synthesis.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 497 | `batch_050_frontier_files_0491_0500` | `tests/test_phase_456_cdl_050_blocker_clearance_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 498 | `batch_050_frontier_files_0491_0500` | `tests/test_phase_456_fix_10_nonlinear_control_mechanism_implementation.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 499 | `batch_050_frontier_files_0491_0500` | `tests/test_phase_456_fix_13_post_nonlinear_control_blocker_disposition_review.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 500 | `batch_050_frontier_files_0491_0500` | `tests/test_phase_456_fix_14_cdl_050_blocker_clearance_gate_rerun.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 501 | `batch_051_frontier_files_0501_0510` | `tests/test_phase_456_fix_2_recovery_rule_execution_and_blocker_1_reassessment.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 502 | `batch_051_frontier_files_0501_0510` | `tests/test_phase_456_fix_3_recovery_rule_mechanism_implementation.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 503 | `batch_051_frontier_files_0501_0510` | `tests/test_phase_456_fix_6_oscillator_mechanism_implementation.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 504 | `batch_051_frontier_files_0501_0510` | `tests/test_phase_456_fix_8_oscillator_execution_and_blocker_1_reassessment.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 505 | `batch_051_frontier_files_0501_0510` | `tests/test_phase_456_fix_9_post_oscillator_blocker_disposition_review.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 506 | `batch_051_frontier_files_0501_0510` | `tests/test_phase_456_post_fix_5_blocker_disposition_review.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 507 | `batch_051_frontier_files_0501_0510` | `tests/test_phase_456_waggle_dance_wide_field_surface.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 508 | `batch_051_frontier_files_0501_0510` | `tests/test_phase_459_post1_waggle_oscillator_hybrid_intake_and_admissibility_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 509 | `batch_051_frontier_files_0501_0510` | `tests/test_phase_459_post2_waggle_oscillator_hybrid_contrast_field_attestation_and_brief_freeze.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 510 | `batch_051_frontier_files_0501_0510` | `tests/test_phase_460_window_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 511 | `batch_052_frontier_files_0511_0520` | `tests/test_phase_461_adr_0021_epistemic_finality_claims.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 512 | `batch_052_frontier_files_0511_0520` | `tests/test_phase_462_refutation_criterion_schema_specification.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 513 | `batch_052_frontier_files_0511_0520` | `tests/test_phase_467_tla_plus_cdl_051_shell_specification.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 514 | `batch_052_frontier_files_0511_0520` | `tests/test_phase_470_consensus_diversity_floor_finality_runtime.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 515 | `batch_052_frontier_files_0511_0520` | `tests/test_phase_473_consensus_adversarial_hardening_and_findings.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 516 | `batch_052_frontier_files_0511_0520` | `tests/test_phase_475_window_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 517 | `batch_052_frontier_files_0511_0520` | `tests/test_phase_479_genesis_validator_bootstrap_specification.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 518 | `batch_052_frontier_files_0511_0520` | `tests/test_phase_483_coherence_and_capsule_v2_2.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 519 | `batch_052_frontier_files_0511_0520` | `tests/test_phase_485_window_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 520 | `batch_052_frontier_files_0511_0520` | `tests/test_phase_487_sim_010_validator_incentive_economics_execution_and_evidence.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 521 | `batch_053_frontier_files_0521_0530` | `tests/test_phase_489_validator_economic_incentive_framework_opening_stub.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 522 | `batch_053_frontier_files_0521_0530` | `tests/test_phase_493_validator_staking_and_liveness_enforcement_prelock_hardening.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 523 | `batch_053_frontier_files_0521_0530` | `tests/test_phase_495_sequence_lock_and_cdl_055_disposition.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 524 | `batch_053_frontier_files_0521_0530` | `tests/test_phase_497_validator_trust_tier_governance_boundary_analysis.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 525 | `batch_053_frontier_files_0521_0530` | `tests/test_phase_498_epoch_boundary_enforcement_architectural_scoping.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 526 | `batch_053_frontier_files_0521_0530` | `tests/test_phase_499_validator_trust_tier_elevation_opening_stub.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 527 | `batch_053_frontier_files_0521_0530` | `tests/test_phase_503_coherence_report_and_capsule_v2_3.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 528 | `batch_053_frontier_files_0521_0530` | `tests/test_phase_508_epoch_boundary_cdl_vehicle_selection.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 529 | `batch_053_frontier_files_0521_0530` | `tests/test_phase_509_epoch_boundary_cdl_opening_stub.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 530 | `batch_053_frontier_files_0521_0530` | `tests/test_phase_515_sequence_lock_and_carry_forward_intake.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 531 | `batch_054_frontier_files_0531_0540` | `tests/test_phase_522_adr_0023_cdl_scoping_analysis.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 532 | `batch_054_frontier_files_0531_0540` | `tests/test_phase_528_adr_0023_simulation_synthesis.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 533 | `batch_054_frontier_files_0531_0540` | `tests/test_phase_533_coherence_report_and_capsule_v2_6.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 534 | `batch_054_frontier_files_0531_0540` | `tests/test_phase_551_passive_ecu_attribution_hardening.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 535 | `batch_054_frontier_files_0531_0540` | `tests/test_phase_555_window_555_564_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 536 | `batch_054_frontier_files_0531_0540` | `tests/test_phase_556_adr_023_signal_floor_invariant.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 537 | `batch_054_frontier_files_0531_0540` | `tests/test_phase_559_gossip_transport_hardening.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 538 | `batch_054_frontier_files_0531_0540` | `tests/test_phase_563_coherence_report_and_capsule.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 539 | `batch_054_frontier_files_0531_0540` | `tests/test_phase_565_window_565_574_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 540 | `batch_054_frontier_files_0531_0540` | `tests/test_phase_566_transport_operationalization_boundary_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 541 | `batch_055_frontier_files_0541_0550` | `tests/test_phase_575_window_575_584_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 542 | `batch_055_frontier_files_0541_0550` | `tests/test_phase_576_rc0_1_settlement_wallet_boundary_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 543 | `batch_055_frontier_files_0541_0550` | `tests/test_phase_577_rc0_1_persisted_graph_contract_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 544 | `batch_055_frontier_files_0541_0550` | `tests/test_phase_578_rc0_1_curated_genesis_bootstrap_lineage_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 545 | `batch_055_frontier_files_0541_0550` | `tests/test_phase_581_settlement_wallet_query_integration.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 546 | `batch_055_frontier_files_0541_0550` | `tests/test_phase_585_window_585_594_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 547 | `batch_055_frontier_files_0541_0550` | `tests/test_phase_587_public_identity_activation_and_namespace_boundary_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 548 | `batch_055_frontier_files_0541_0550` | `tests/test_phase_588_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 549 | `batch_055_frontier_files_0541_0550` | `tests/test_phase_589_settlement_linked_public_legitimacy_and_payout_traceability_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 550 | `batch_055_frontier_files_0541_0550` | `tests/test_phase_590_genesis_authority_sunset_and_fork_legitimacy_coherence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 551 | `batch_056_frontier_files_0551_0560` | `tests/test_phase_591_public_runtime_integration_over_receipt_boundary.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 552 | `batch_056_frontier_files_0551_0560` | `tests/test_phase_595_rc0_1_strike_force_consolidation_and_runtime_hardening.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 553 | `batch_056_frontier_files_0551_0560` | `tests/test_phase_596_window_596_605_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 554 | `batch_056_frontier_files_0551_0560` | `tests/test_phase_597_genesis_governance_dilution_and_brake_semantics_closure.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 555 | `batch_056_frontier_files_0551_0560` | `tests/test_phase_598_freshness_gate_provenance_and_genesis_exemption_closure.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 556 | `batch_056_frontier_files_0551_0560` | `tests/test_phase_601_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 557 | `batch_056_frontier_files_0551_0560` | `tests/test_phase_602_topological_exemption_boundary_and_public_tokenomics_statement.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 558 | `batch_056_frontier_files_0551_0560` | `tests/test_phase_603_genesis_carry_forward_synthesis_and_readiness_delta_addendum.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 559 | `batch_056_frontier_files_0551_0560` | `tests/test_phase_604_coherence_report_and_capsule_v3_2.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 560 | `batch_056_frontier_files_0551_0560` | `tests/test_phase_606_mempalace_internal_retrieval_adoption.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 561 | `batch_057_frontier_files_0561_0570` | `tests/test_phase_607_window_607_612_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 562 | `batch_057_frontier_files_0561_0570` | `tests/test_phase_609_ecu_ilc_runtime_boundary_reconciliation.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 563 | `batch_057_frontier_files_0561_0570` | `tests/test_phase_612_settlement_substrate_closure_and_mvp_gated_replan.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 564 | `batch_057_frontier_files_0561_0570` | `tests/test_phase_613_window_613_619_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 565 | `batch_057_frontier_files_0561_0570` | `tests/test_phase_620_window_620_622_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 566 | `batch_057_frontier_files_0561_0570` | `tests/test_phase_624_window_624_630_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 567 | `batch_057_frontier_files_0561_0570` | `tests/test_phase_626_cdl_063_ecu_directed_commission_prelock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 568 | `batch_057_frontier_files_0561_0570` | `tests/test_phase_630_window_624_630_coherence_and_closure.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 569 | `batch_057_frontier_files_0561_0570` | `tests/test_phase_631_window_631_636_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 570 | `batch_057_frontier_files_0561_0570` | `tests/test_phase_632_tier0_numeric_inventory_and_cdl_064_opening.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 571 | `batch_058_frontier_files_0571_0580` | `tests/test_phase_635_tier0_exact_numeric_runtime_migration.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 572 | `batch_058_frontier_files_0571_0580` | `tests/test_phase_636_tier0_numeric_hardening_and_closure.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 573 | `batch_058_frontier_files_0571_0580` | `tests/test_phase_637_window_637_641_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 574 | `batch_058_frontier_files_0571_0580` | `tests/test_phase_641_residual_numeric_cleanup_and_closure.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 575 | `batch_058_frontier_files_0571_0580` | `tests/test_phase_642_window_642_648_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 576 | `batch_058_frontier_files_0571_0580` | `tests/test_phase_644_canonical_json_and_signature_boundary_hardening.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 577 | `batch_058_frontier_files_0571_0580` | `tests/test_phase_647_security_hardening_gate_and_fix_induced_regression_audit.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 578 | `batch_058_frontier_files_0571_0580` | `tests/test_phase_648_window_642_648_closure_and_handoff.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 579 | `batch_058_frontier_files_0571_0580` | `tests/test_phase_649_window_649_654_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 580 | `batch_058_frontier_files_0571_0580` | `tests/test_phase_651_public_receipt_runtime.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 581 | `batch_059_frontier_files_0581_0590` | `tests/test_phase_653_public_wallet_runtime_integration.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 582 | `batch_059_frontier_files_0581_0590` | `tests/test_phase_654_window_649_654_closure_and_handoff.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 583 | `batch_059_frontier_files_0581_0590` | `tests/test_phase_655_window_655_658_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 584 | `batch_059_frontier_files_0581_0590` | `tests/test_phase_656_canon_export_and_registry_signature_reproducibility.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 585 | `batch_059_frontier_files_0581_0590` | `tests/test_phase_657_registry_channel_promotion_sync_reproducibility.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 586 | `batch_059_frontier_files_0581_0590` | `tests/test_phase_658_window_655_658_hardening_and_handoff.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 587 | `batch_059_frontier_files_0581_0590` | `tests/test_phase_659_window_659_664_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 588 | `batch_059_frontier_files_0581_0590` | `tests/test_phase_662_cdl_065_opening_and_admissibility_matrix.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 589 | `batch_059_frontier_files_0581_0590` | `tests/test_phase_665_window_665_670_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 590 | `batch_059_frontier_files_0581_0590` | `tests/test_phase_669_transport_hardening_and_maturity_decision.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 591 | `batch_060_frontier_files_0591_0600` | `tests/test_phase_670_window_665_670_closure_and_handoff.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 592 | `batch_060_frontier_files_0591_0600` | `tests/test_phase_676_window_671_676_closure_and_handoff.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 593 | `batch_060_frontier_files_0591_0600` | `tests/test_phase_677_window_677_682_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 594 | `batch_060_frontier_files_0591_0600` | `tests/test_phase_682_window_677_682_closure_and_handoff.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 595 | `batch_060_frontier_files_0591_0600` | `tests/test_phase_697_row_5_mechanism_proof_mysticeti.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 596 | `batch_060_frontier_files_0591_0600` | `tests/test_phase_698_row_7_tlc_evidence_mysticeti.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 597 | `batch_060_frontier_files_0591_0600` | `tests/test_phase_699_row_8_mysticeti_sovereign_config.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 598 | `batch_060_frontier_files_0591_0600` | `tests/test_phase_700_coherence_capsule_v4_4_and_window_693_700_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 599 | `batch_060_frontier_files_0591_0600` | `tests/test_phase_701_window_701_706_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 600 | `batch_060_frontier_files_0591_0600` | `tests/test_phase_703_bal_profile_kernel_calibration_and_replay_contract.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 601 | `batch_061_frontier_files_0601_0610` | `tests/test_phase_704_post_banking_doctrine_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 602 | `batch_061_frontier_files_0601_0610` | `tests/test_phase_705_inverted_ecu_runtime_traceability_and_doctrine_preservation.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 603 | `batch_061_frontier_files_0601_0610` | `tests/test_phase_706_coherence_capsule_v4_5_and_window_701_706_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 604 | `batch_061_frontier_files_0601_0610` | `tests/test_phase_707_window_707_712_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 605 | `batch_061_frontier_files_0601_0610` | `tests/test_phase_711_validator_sim_commissioning_and_cdl_039_scope_note.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 606 | `batch_061_frontier_files_0601_0610` | `tests/test_phase_712_coherence_report_capsule_v4_6_and_window_707_712_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 607 | `batch_061_frontier_files_0601_0610` | `tests/test_phase_713_window_713_716_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 608 | `batch_061_frontier_files_0601_0610` | `tests/test_phase_714_adaptive_gossip_contract_and_law_vs_freedom_classification.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 609 | `batch_061_frontier_files_0601_0610` | `tests/test_phase_715_partition_repair_benchmark_pack_and_missing_signal_doctrine.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 610 | `batch_061_frontier_files_0601_0610` | `tests/test_phase_716_coherence_report_capsule_v4_7_and_window_713_716_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 611 | `batch_062_frontier_files_0611_0620` | `tests/test_phase_717_window_717_722_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 612 | `batch_062_frontier_files_0611_0620` | `tests/test_phase_718_adr_0015_inventory_and_scoping.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 613 | `batch_062_frontier_files_0611_0620` | `tests/test_phase_720_commons_dedication_and_leasehold_reversion_calibration.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 614 | `batch_062_frontier_files_0611_0620` | `tests/test_phase_722_coherence_report_capsule_v4_8_and_window_717_722_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 615 | `batch_062_frontier_files_0611_0620` | `tests/test_phase_723_window_723_726_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 616 | `batch_062_frontier_files_0611_0620` | `tests/test_phase_724_financial_shard_eligibility_prefilter_and_lane_separation.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 617 | `batch_062_frontier_files_0611_0620` | `tests/test_phase_726_coherence_report_capsule_v4_9_and_window_723_726_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 618 | `batch_062_frontier_files_0611_0620` | `tests/test_phase_727_window_727_732_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 619 | `batch_062_frontier_files_0611_0620` | `tests/test_phase_732_capsule_v5_0_and_window_727_732_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 620 | `batch_062_frontier_files_0611_0620` | `tests/test_phase_733_window_733_738_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 621 | `batch_063_frontier_files_0621_0630` | `tests/test_phase_734_sim_validator_01_results.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 622 | `batch_063_frontier_files_0621_0630` | `tests/test_phase_735_sim_topology_01_results.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 623 | `batch_063_frontier_files_0621_0630` | `tests/test_phase_736_cdl_068_opening.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 624 | `batch_063_frontier_files_0621_0630` | `tests/test_phase_737_cdl_017_prelock_evidence_and_adr_0019_disposition.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 625 | `batch_063_frontier_files_0621_0630` | `tests/test_phase_738_window_733_738_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 626 | `batch_063_frontier_files_0621_0630` | `tests/test_phase_739_window_739_744_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 627 | `batch_063_frontier_files_0621_0630` | `tests/test_phase_745_window_745_748_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 628 | `batch_063_frontier_files_0621_0630` | `tests/test_phase_749_window_749_752_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 629 | `batch_063_frontier_files_0621_0630` | `tests/test_phase_750_master_completion_roadmap_and_m_series_lane_update.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 630 | `batch_063_frontier_files_0621_0630` | `tests/test_phase_751_stale_planning_doc_archival_and_planning_index_advance.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 631 | `batch_064_frontier_files_0631_0640` | `tests/test_phase_755_cdl_017_ratification_readiness_dossier.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 632 | `batch_064_frontier_files_0631_0640` | `tests/test_phase_764_cdl_017_interaction_synthesis_and_activation_boundary_record.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 633 | `batch_064_frontier_files_0631_0640` | `tests/test_phase_765_cdl_017_ratification_evidence.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 634 | `batch_064_frontier_files_0631_0640` | `tests/test_phase_768_sec_004_acceptance.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 635 | `batch_064_frontier_files_0631_0640` | `tests/test_phase_769_m007_hook_activation.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 636 | `batch_064_frontier_files_0631_0640` | `tests/test_phase_770_codex_audit.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 637 | `batch_064_frontier_files_0631_0640` | `tests/test_phase_771_lane_doc_update.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 638 | `batch_064_frontier_files_0631_0640` | `tests/test_phase_773_coherence_and_capsule.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 639 | `batch_064_frontier_files_0631_0640` | `tests/test_phase_776_layer1_log_hygiene.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 640 | `batch_064_frontier_files_0631_0640` | `tests/test_phase_777_sim_run1.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 641 | `batch_065_frontier_files_0641_0650` | `tests/test_phase_779_sim_run2.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 642 | `batch_065_frontier_files_0641_0650` | `tests/test_phase_780_row5_evaluation.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 643 | `batch_065_frontier_files_0641_0650` | `tests/test_phase_781_coherence_and_capsule.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 644 | `batch_065_frontier_files_0641_0650` | `tests/test_phase_813_checklist_v0_2.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 645 | `batch_065_frontier_files_0641_0650` | `tests/test_phase_830_settlement_path_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 646 | `batch_065_frontier_files_0641_0650` | `tests/test_phase_831_row5_b_impl_obligations_1_3.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 647 | `batch_065_frontier_files_0641_0650` | `tests/test_phase_832_row5_b_impl_obligations_4_5.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 648 | `batch_065_frontier_files_0641_0650` | `tests/test_phase_833_row5_b_impl_obligation_6_sim_leakage_03.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 649 | `batch_065_frontier_files_0641_0650` | `tests/test_phase_834_row5_b_impl_strike_force_closure_gate.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 650 | `batch_065_frontier_files_0641_0650` | `tests/test_phase_835_settlement_gate_preflight.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 651 | `batch_066_frontier_files_0651_0660` | `tests/test_phase_836_first_validator_entry_conditions_check.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 652 | `batch_066_frontier_files_0651_0660` | `tests/test_phase_837_track1_coherence_and_capsule.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 653 | `batch_066_frontier_files_0651_0660` | `tests/test_phase_838a_genesis_agent1_keygen.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 654 | `batch_066_frontier_files_0651_0660` | `tests/test_phase_838b_sphincs_shamir_split.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 655 | `batch_066_frontier_files_0651_0660` | `tests/test_phase_838c_epoch_endorsement_runtime.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 656 | `batch_066_frontier_files_0651_0660` | `tests/test_phase_838d_agent_id_runtime_v2.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 657 | `batch_066_frontier_files_0651_0660` | `tests/test_phase_838e_genesis_record_schema.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 658 | `batch_066_frontier_files_0651_0660` | `tests/test_phase_838f_endorsement_packet_schema.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 659 | `batch_066_frontier_files_0651_0660` | `tests/test_phase_844_row5_rust_routing_instrumentation.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 660 | `batch_066_frontier_files_0651_0660` | `tests/test_phase_845_sim_leakage_03_live_run.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 661 | `batch_067_frontier_files_0661_0670` | `tests/test_phase_846_cdl_072_bound_b_and_row5_closure.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 662 | `batch_067_frontier_files_0661_0670` | `tests/test_phase_847_window_844_847_closure_gate.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 663 | `batch_067_frontier_files_0661_0670` | `tests/test_phase_849_graduation_checklist_v0_3.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 664 | `batch_067_frontier_files_0661_0670` | `tests/test_phase_850_851_cdl_071_temporal_tier.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 665 | `batch_067_frontier_files_0661_0670` | `tests/test_phase_852_window_848_852_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 666 | `batch_067_frontier_files_0661_0670` | `tests/test_phase_858_hb_001_genesis_assertion_schema.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 667 | `batch_067_frontier_files_0661_0670` | `tests/test_phase_859_hb_003_layer_0_bundle_schema_section.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 668 | `batch_067_frontier_files_0661_0670` | `tests/test_phase_865_872_cdl_074_truth_primitive_runtime.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 669 | `batch_067_frontier_files_0661_0670` | `tests/test_phase_879_886_truth_primitive_graph_store.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 670 | `batch_067_frontier_files_0661_0670` | `tests/test_phase_888_891_query_truth_cli.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 671 | `batch_068_frontier_files_0671_0680` | `tests/test_phase_921_929_cdl_080_star_map.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 672 | `batch_068_frontier_files_0671_0680` | `tests/test_phase_932_933_h013_spectral_beacon.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 673 | `batch_068_frontier_files_0671_0680` | `tests/test_phase_942_cdl_081_hyperedge_ecu_attribution.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 674 | `batch_068_frontier_files_0671_0680` | `tests/test_phase_M009_mysticeti_testnet_setup.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 675 | `batch_068_frontier_files_0671_0680` | `tests/test_phase_M012_full_bft_transfer.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 676 | `batch_068_frontier_files_0671_0680` | `tests/test_phase_M013_workload_a_results.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 677 | `batch_068_frontier_files_0671_0680` | `tests/test_phase_M014_workload_b_results.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 678 | `batch_068_frontier_files_0671_0680` | `tests/test_phase_M015_workload_c_results.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 679 | `batch_068_frontier_files_0671_0680` | `tests/test_phase_M016_workload_d_results.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 680 | `batch_068_frontier_files_0671_0680` | `tests/test_phase_M017_workload_e_results.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 681 | `batch_069_frontier_files_0681_0690` | `tests/test_phase_M018_workload_f_results.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 682 | `batch_069_frontier_files_0681_0690` | `tests/test_phase_M019_adversarial_hardening_results.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 683 | `batch_069_frontier_files_0681_0690` | `tests/test_phase_commit_manifest_296.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 684 | `batch_069_frontier_files_0681_0690` | `tests/test_phase_high002_phase_b_closure_gate.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 685 | `batch_069_frontier_files_0681_0690` | `tests/test_problem_space_kpis.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 686 | `batch_069_frontier_files_0681_0690` | `tests/test_protocol_event_export.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 687 | `batch_069_frontier_files_0681_0690` | `tests/test_protocol_event_log.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 688 | `batch_069_frontier_files_0681_0690` | `tests/test_protocol_params.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 689 | `batch_069_frontier_files_0681_0690` | `tests/test_public_rc_drift_reconciliation_successor_manifest_plan.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 690 | `batch_069_frontier_files_0681_0690` | `tests/test_public_rc_general_go_live_forward_plan.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 691 | `batch_070_frontier_files_0691_0700` | `tests/test_public_rc_package_profiles.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 692 | `batch_070_frontier_files_0691_0700` | `tests/test_quickstart_parity_phase_998.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 693 | `batch_070_frontier_files_0691_0700` | `tests/test_ratification_sequence_250.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 694 | `batch_070_frontier_files_0691_0700` | `tests/test_ratification_sequence_270.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 695 | `batch_070_frontier_files_0691_0700` | `tests/test_rc0_1_benchmark_runner.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 696 | `batch_070_frontier_files_0691_0700` | `tests/test_rc_dredge_stack_tools.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 697 | `batch_070_frontier_files_0691_0700` | `tests/test_refutation_profitability_invariant_gate_phase_212.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 698 | `batch_070_frontier_files_0691_0700` | `tests/test_refutation_profitability_invariant_phase_212.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 699 | `batch_070_frontier_files_0691_0700` | `tests/test_release_readiness_package_238.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 700 | `batch_070_frontier_files_0691_0700` | `tests/test_replay_proof_schema_parity.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 701 | `batch_071_frontier_files_0701_0710` | `tests/test_reuse_diversity_invariants_gate_phase_216.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 702 | `batch_071_frontier_files_0701_0710` | `tests/test_reuse_diversity_invariants_phase_216.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 703 | `batch_071_frontier_files_0701_0710` | `tests/test_reward_loop.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 704 | `batch_071_frontier_files_0701_0710` | `tests/test_rl_bandit_sim.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 705 | `batch_071_frontier_files_0701_0710` | `tests/test_routed_tasks_export.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 706 | `batch_071_frontier_files_0701_0710` | `tests/test_runtime_logging_closure_gate.py` | `missing_expected_authority_trace` | `authority_trace_review_required` |
| 707 | `batch_071_frontier_files_0701_0710` | `tests/test_security_ratification_gate_252.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 708 | `batch_071_frontier_files_0701_0710` | `tests/test_security_runtime_closure_gate_phase_249.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 709 | `batch_071_frontier_files_0701_0710` | `tests/test_security_runtime_cross_cdl_interactions_244.py` | `missing_expected_authority_trace` | `cdl_or_constitutional_validation` |
| 710 | `batch_071_frontier_files_0701_0710` | `tests/test_security_runtime_implementation_plan_232.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 711 | `batch_072_frontier_files_0711_0720` | `tests/test_security_runtime_sequence_240.py` | `missing_tests_edge` | `cdl_or_constitutional_validation` |
| 712 | `batch_072_frontier_files_0711_0720` | `tests/test_sensitive_runtime_coding_taboos.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 713 | `batch_072_frontier_files_0711_0720` | `tests/test_server_app_factory_phase_1001.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 714 | `batch_072_frontier_files_0711_0720` | `tests/test_server_instance_isolation_phase_199.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 715 | `batch_072_frontier_files_0711_0720` | `tests/test_server_lifecycle_phase_198.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 716 | `batch_072_frontier_files_0711_0720` | `tests/test_settlement_metrics.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 717 | `batch_072_frontier_files_0711_0720` | `tests/test_settlement_stability.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 718 | `batch_072_frontier_files_0711_0720` | `tests/test_settlement_verification.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 719 | `batch_072_frontier_files_0711_0720` | `tests/test_sidecar_ccss_cli_public_ux.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 720 | `batch_072_frontier_files_0711_0720` | `tests/test_sidecar_query_completeness_1379.py` | `missing_tests_edge` | `adr_or_governance_validation` |
| 721 | `batch_073_frontier_files_0721_0730` | `tests/test_signing_provider_interface_262.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 722 | `batch_073_frontier_files_0721_0730` | `tests/test_silent_exception_logging_guardrail.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 723 | `batch_073_frontier_files_0721_0730` | `tests/test_sim_closed_loop_backlog_control.py` | `missing_tests_edge` | `phase_artifact_validation` |
| 724 | `batch_073_frontier_files_0721_0730` | `tests/test_sim_embed_01_results.py` | `missing_tests_edge` | `adr_or_governance_validation` |
| 725 | `batch_073_frontier_files_0721_0730` | `tests/test_sim_harnesses.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 726 | `batch_073_frontier_files_0721_0730` | `tests/test_sim_leakage_02_autoresearch.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 727 | `batch_073_frontier_files_0721_0730` | `tests/test_sim_routing_01_results.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 728 | `batch_073_frontier_files_0721_0730` | `tests/test_stress_response_kpis.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 729 | `batch_073_frontier_files_0721_0730` | `tests/test_task_primitive.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 730 | `batch_073_frontier_files_0721_0730` | `tests/test_task_queue.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 731 | `batch_074_frontier_files_0731_0740` | `tests/test_task_queue_reward_flow.py` | `missing_tests_edge` | `general_test_frontier_validation` |
| 732 | `batch_074_frontier_files_0731_0740` | `tests/test_task_routing_suggestions.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 733 | `batch_074_frontier_files_0731_0740` | `tests/test_telemetry_rlhook.py` | `missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 734 | `batch_074_frontier_files_0731_0740` | `tests/test_track1_closure_guardrail_gate_ops.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 735 | `batch_074_frontier_files_0731_0740` | `tests/test_utility_flow_rewards_phase_208.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 736 | `batch_074_frontier_files_0731_0740` | `tests/test_validate_phase_prompt_alpha_subphase.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 737 | `batch_074_frontier_files_0731_0740` | `tests/test_window_1257_1264_prompt_drafts.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 738 | `batch_074_frontier_files_0731_0740` | `tests/test_window_1265_1272_prompt_drafts.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 739 | `batch_074_frontier_files_0731_0740` | `tests/test_window_1273_1280_prompt_drafts.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 740 | `batch_074_frontier_files_0731_0740` | `tests/test_window_1289_1302_prompt_drafts.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 741 | `batch_075_frontier_files_0741_0750` | `tests/test_window_1303_1316_deep_code_audit_hardening.py` | `missing_expected_authority_trace` | `phase_artifact_validation` |
| 742 | `batch_075_frontier_files_0741_0750` | `tests/test_window_1303_1316_prompt_drafts.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 743 | `batch_075_frontier_files_0741_0750` | `tests/test_window_1317_1329_prompt_drafts.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 744 | `batch_075_frontier_files_0741_0750` | `tests/test_window_1330_1342_prompt_drafts.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 745 | `batch_075_frontier_files_0741_0750` | `tests/test_window_1343_1368_prompt_drafts.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 746 | `batch_075_frontier_files_0741_0750` | `tests/test_window_1369_1390_public_economics_gap_planning.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 747 | `batch_075_frontier_files_0741_0750` | `tests/test_window_545_554_audit_regressions.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 748 | `batch_075_frontier_files_0741_0750` | `tests/test_window_555_560_transport_audit_regressions.py` | `missing_expected_authority_trace` | `runtime_or_protocol_module_validation` |
| 749 | `batch_075_frontier_files_0741_0750` | `tests/test_window_555_562_peer_registry_audit_regressions.py` | `missing_expected_authority_trace, missing_tests_edge` | `runtime_or_protocol_module_validation` |
| 750 | `batch_075_frontier_files_0741_0750` | `tests/test_window_767_774_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `authority_trace_review_required` |
| 751 | `batch_076_frontier_files_0751_0756` | `tests/test_window_767_774_integration_gate_772.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 752 | `batch_076_frontier_files_0751_0756` | `tests/test_window_775_782_closure_gate.py` | `missing_expected_authority_trace, missing_tests_edge` | `cdl_or_constitutional_validation` |
| 753 | `batch_076_frontier_files_0751_0756` | `tests/test_window_811_822_option_b_selection_and_pre_rc_hardening.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 754 | `batch_076_frontier_files_0751_0756` | `tests/test_window_823_829_sequence_lock.py` | `missing_expected_authority_trace, missing_tests_edge` | `adr_or_governance_validation` |
| 755 | `batch_076_frontier_files_0751_0756` | `tests/test_window_b_scope_b1_b4_holdpoint.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |
| 756 | `batch_076_frontier_files_0751_0756` | `tests/test_window_b_scope_b5_lock_and_commissioning.py` | `missing_expected_authority_trace, missing_tests_edge` | `phase_artifact_validation` |

## Reproducible Random Sample

The following ten files were sampled with Python `random.Random(seed)` using the seed recorded above.

1. `tests/test_event_log_retention_rotation_gate_phase_196.py` — `missing_expected_authority_trace` — `phase_artifact_validation`
2. `tests/test_node_id_runtime_bridge_phase_1003.py` — `missing_expected_authority_trace` — `phase_artifact_validation`
3. `tests/test_phase_1135_sim_spectral_02_run02.py` — `missing_expected_authority_trace, missing_tests_edge` — `phase_artifact_validation`
4. `tests/test_phase_1137_coherence_capsule_v5_38.py` — `missing_expected_authority_trace, missing_tests_edge` — `cdl_or_constitutional_validation`
5. `tests/test_phase_1215_v0_2_signing_skip.py` — `missing_expected_authority_trace, missing_tests_edge` — `phase_artifact_validation`
6. `tests/test_phase_1350_cdl_083_ejected_stake_treasury_distribution.py` — `missing_expected_authority_trace, missing_tests_edge` — `cdl_or_constitutional_validation`
7. `tests/test_phase_1388a_cdl_048_self_counsel_clearance.py` — `missing_expected_authority_trace, missing_tests_edge` — `cdl_or_constitutional_validation`
8. `tests/test_phase_447_consensus_adversarial_regression.py` — `missing_expected_authority_trace, missing_tests_edge` — `cdl_or_constitutional_validation`
9. `tests/test_phase_676_window_671_676_closure_and_handoff.py` — `missing_expected_authority_trace, missing_tests_edge` — `phase_artifact_validation`
10. `tests/test_sidecar_query_completeness_1379.py` — `missing_tests_edge` — `adr_or_governance_validation`
