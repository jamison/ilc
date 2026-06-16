# ILC Test Registry Frontier Report - Phase 1545p-Fix38

## Summary

- Phase: `1545p-Fix38`
- Status: `pass`
- Report digest: `test_frontier_report:28eee1ccd7a5809d814964a0ab08b9f0`
- Graph candidate status: `unsigned_support_only_not_canonical`
- Scope: report-only support evidence; no test execution and no canonical graph mutation.
- Unified candidate file: `out/atlas_research/genesis_atlas_test_frontier_unified_candidate_1545p_fix38.json`
- Unified candidate digest: `fix38_unified_candidate:7891d425988e4b30a5f36a01c97bfc8f`

## File-Level Frontier

- Local test Python files: `1472`
- Mapped test files: `1458`
- Files with TESTS edges: `913`
- Missing candidate node count: `14`
- Missing TESTS edge count: `544`
- Missing expected authority trace count: `621`
- Dangling TESTS target count: `0`

## Function-Level Frontier

- Collected test function nodes: `12800`
- Candidate edge count: `72786`
- Deferred record count: `12800`
- Function nodes without inherited TESTS targets: `3766`

## Unified Candidate Overlay

- Candidate status: `unsigned_support_only_not_canonical_fix38_unified_candidate`
- Unified node count: `15656`
- Unified edge count: `70259`
- Overlay frontier files: `756`
- Overlay added nodes: `5621`
- Overlay added edges: `16434`
- Curated manual-edge files: `756`
- Curated semantic edges: `3608`
- Curated authority-trace edges: `1391`
- Authority edge policy: candidate role-specific traces only; no `GOVERNS` edges from tests and no direct test-to-Genesis authority shortcut.

## Evidence Frontier

- Fix36 default-local evidence commands: `8`
- Fix36 result statuses: `{"passed": 8}`
- Fix37 graph-hydrated commands: `6`
- Fix37 excluded git-history-dependent commands: `2`
- Fix37 hydrated files: `7`

## Manual Connectivity Annotation Batches

- Annotation mode: `manual_direct_read_batches`
- Batch size policy: `batches_of_10_plus_tail_batch`
- Manual annotation coverage for Fix33 missing candidate nodes: `14/14`
- Remaining missing candidate nodes after this pass: `0`
- All Fix33 frontier gap files annotated: `756/756`
- All-frontier annotation batches: `76`

| Tranche | Test file | Connectivity class | Proposed target count | Recommended action |
|---|---:|---|---:|---|
| tranche_001_missing_candidate_nodes_01_10 | `tests/test_homoiconic_test_registry_forward_plan.py` | forward_plan_document_validation | 3 | create_test_file_node_and_TESTS_edges_to_forward_plan_inventory_planning |
| tranche_001_missing_candidate_nodes_01_10 | `tests/test_homoiconic_test_registry_implementation_guidance.py` | implementation_guidance_and_window_validation | 5 | create_test_file_node_and_TESTS_edges_to_guidance_forward_plan_window_inventory_planning |
| tranche_001_missing_candidate_nodes_01_10 | `tests/test_phase_1545p_fix22_full_repo_genesis_atlas.py` | full_repo_atlas_candidate_artifact_validation | 5 | create_test_file_node_and_TESTS_edges_to_fix22_sim_graph_preimages_report_review |
| tranche_001_missing_candidate_nodes_01_10 | `tests/test_phase_1545p_fix23_genesis_atlas_lmdb_materialization.py` | lmdb_materialization_adapter_and_sim_validation | 4 | create_test_file_node_and_TESTS_edges_to_lmdb_adapter_and_fix23_artifacts |
| tranche_001_missing_candidate_nodes_01_10 | `tests/test_phase_1545p_fix24_whole_graph_atlas_objective_contract.py` | whole_graph_objective_contract_validation | 5 | create_test_file_node_and_TESTS_edges_to_fix24_contract_json_walkthrough_status_planning |
| tranche_001_missing_candidate_nodes_01_10 | `tests/test_phase_1545p_fix25_whole_graph_baseline_diagnostic.py` | whole_graph_baseline_diagnostic_validation | 6 | create_test_file_node_and_TESTS_edges_to_fix25_diagnostic_report_review_walkthrough_status_planning |
| tranche_001_missing_candidate_nodes_01_10 | `tests/test_phase_1545p_fix26_axiomatic_extraction_replay.py` | axiomatic_extraction_replay_validation | 8 | create_test_file_node_and_TESTS_edges_to_fix26_sim_atom_queue_graph_report_review_walkthrough_status_planning |
| tranche_001_missing_candidate_nodes_01_10 | `tests/test_phase_1545p_fix27_rewrite_candidate_generation.py` | rewrite_candidate_generation_validation | 4 | create_test_file_node_and_TESTS_edges_to_fix27_summary_candidates_fix22_graph_runner |
| tranche_001_missing_candidate_nodes_01_10 | `tests/test_phase_1545p_fix28_projection_hydration_sim.py` | projection_hydration_sim_validation | 5 | create_test_file_node_and_TESTS_edges_to_fix28_runner_summary_slices_report_review |
| tranche_001_missing_candidate_nodes_01_10 | `tests/test_phase_1545p_fix29_spectral_non_excisability_sim.py` | spectral_non_excisability_sim_validation | 7 | create_test_file_node_and_TESTS_edges_to_fix29_runner_summary_report_review_walkthrough_status_planning |
| tranche_002_missing_candidate_nodes_tail_11_14 | `tests/test_phase_1545p_fix30_long_autoresearch_optimization.py` | long_autoresearch_optimization_validation | 7 | create_test_file_node_and_TESTS_edges_to_fix30_summary_iterations_candidate_report_review_prompt_checkpoints |
| tranche_002_missing_candidate_nodes_tail_11_14 | `tests/test_phase_1545p_fix31_candidate_reducer_v04_v05.py` | candidate_reducer_decision_packet_validation | 6 | create_test_file_node_and_TESTS_edges_to_fix31_summary_variants_batch_plan_report_packet_walkthrough |
| tranche_002_missing_candidate_nodes_tail_11_14 | `tests/test_phase_1545p_fix32_homoiconic_test_registry_contract.py` | homoiconic_test_registry_contract_validation | 6 | create_test_file_node_and_TESTS_edges_to_fix32_contract_route_walkthrough_status_planning_inventory |
| tranche_002_missing_candidate_nodes_tail_11_14 | `tests/test_phase_1545p_fix33_test_graph_coverage.py` | test_graph_coverage_checker_validation | 7 | create_test_file_node_and_TESTS_edges_to_fix33_summary_report_prompt_tool_walkthrough_status_planning |

## Frontier Categories

- `missing_candidate_nodes`: `14`
- `missing_tests_edges`: `544`
- `missing_expected_authority_traces`: `621`
- `function_nodes_without_inherited_targets`: `3766`
- `gated_or_non_default_tests`: `426`
- `git_history_dependent_hydration_exclusions`: `2`
- `bounded_execution_evidence`: `recorded`
- `dangling_tests_targets`: `0`
- `approximate_graph_TESTS_target_gap`: `approximate_graph_TESTS_target_metric`

## All-Frontier Batch Annotation Summary

Every Fix33 file in `missing_candidate_node`, `missing_tests_edge`, or `missing_expected_authority_trace` was direct-read and assigned a batch annotation record.

| Batch | Annotated files |
|---|---:|
| `batch_001_frontier_files_0001_0010` | `10` |
| `batch_002_frontier_files_0011_0020` | `10` |
| `batch_003_frontier_files_0021_0030` | `10` |
| `batch_004_frontier_files_0031_0040` | `10` |
| `batch_005_frontier_files_0041_0050` | `10` |
| `batch_006_frontier_files_0051_0060` | `10` |
| `batch_007_frontier_files_0061_0070` | `10` |
| `batch_008_frontier_files_0071_0080` | `10` |
| `batch_009_frontier_files_0081_0090` | `10` |
| `batch_010_frontier_files_0091_0100` | `10` |
| `batch_011_frontier_files_0101_0110` | `10` |
| `batch_012_frontier_files_0111_0120` | `10` |
| `batch_013_frontier_files_0121_0130` | `10` |
| `batch_014_frontier_files_0131_0140` | `10` |
| `batch_015_frontier_files_0141_0150` | `10` |
| `batch_016_frontier_files_0151_0160` | `10` |
| `batch_017_frontier_files_0161_0170` | `10` |
| `batch_018_frontier_files_0171_0180` | `10` |
| `batch_019_frontier_files_0181_0190` | `10` |
| `batch_020_frontier_files_0191_0200` | `10` |
| `batch_021_frontier_files_0201_0210` | `10` |
| `batch_022_frontier_files_0211_0220` | `10` |
| `batch_023_frontier_files_0221_0230` | `10` |
| `batch_024_frontier_files_0231_0240` | `10` |
| `batch_025_frontier_files_0241_0250` | `10` |
| `batch_026_frontier_files_0251_0260` | `10` |
| `batch_027_frontier_files_0261_0270` | `10` |
| `batch_028_frontier_files_0271_0280` | `10` |
| `batch_029_frontier_files_0281_0290` | `10` |
| `batch_030_frontier_files_0291_0300` | `10` |
| `batch_031_frontier_files_0301_0310` | `10` |
| `batch_032_frontier_files_0311_0320` | `10` |
| `batch_033_frontier_files_0321_0330` | `10` |
| `batch_034_frontier_files_0331_0340` | `10` |
| `batch_035_frontier_files_0341_0350` | `10` |
| `batch_036_frontier_files_0351_0360` | `10` |
| `batch_037_frontier_files_0361_0370` | `10` |
| `batch_038_frontier_files_0371_0380` | `10` |
| `batch_039_frontier_files_0381_0390` | `10` |
| `batch_040_frontier_files_0391_0400` | `10` |
| `batch_041_frontier_files_0401_0410` | `10` |
| `batch_042_frontier_files_0411_0420` | `10` |
| `batch_043_frontier_files_0421_0430` | `10` |
| `batch_044_frontier_files_0431_0440` | `10` |
| `batch_045_frontier_files_0441_0450` | `10` |
| `batch_046_frontier_files_0451_0460` | `10` |
| `batch_047_frontier_files_0461_0470` | `10` |
| `batch_048_frontier_files_0471_0480` | `10` |
| `batch_049_frontier_files_0481_0490` | `10` |
| `batch_050_frontier_files_0491_0500` | `10` |
| `batch_051_frontier_files_0501_0510` | `10` |
| `batch_052_frontier_files_0511_0520` | `10` |
| `batch_053_frontier_files_0521_0530` | `10` |
| `batch_054_frontier_files_0531_0540` | `10` |
| `batch_055_frontier_files_0541_0550` | `10` |
| `batch_056_frontier_files_0551_0560` | `10` |
| `batch_057_frontier_files_0561_0570` | `10` |
| `batch_058_frontier_files_0571_0580` | `10` |
| `batch_059_frontier_files_0581_0590` | `10` |
| `batch_060_frontier_files_0591_0600` | `10` |
| `batch_061_frontier_files_0601_0610` | `10` |
| `batch_062_frontier_files_0611_0620` | `10` |
| `batch_063_frontier_files_0621_0630` | `10` |
| `batch_064_frontier_files_0631_0640` | `10` |
| `batch_065_frontier_files_0641_0650` | `10` |
| `batch_066_frontier_files_0651_0660` | `10` |
| `batch_067_frontier_files_0661_0670` | `10` |
| `batch_068_frontier_files_0671_0680` | `10` |
| `batch_069_frontier_files_0681_0690` | `10` |
| `batch_070_frontier_files_0691_0700` | `10` |
| `batch_071_frontier_files_0701_0710` | `10` |
| `batch_072_frontier_files_0711_0720` | `10` |
| `batch_073_frontier_files_0721_0730` | `10` |
| `batch_074_frontier_files_0731_0740` | `10` |
| `batch_075_frontier_files_0741_0750` | `10` |
| `batch_076_frontier_files_0751_0756` | `6` |

## Curated Manual Edge Batch

- Annotation source: `manual_best_effort_direct_read_edge_batch_phase_1545p_fix38`
- Curated files: `756`
- Curated semantic edges: `3608`
- Curated authority-trace edges: `1391`
- Git chronology is supporting cluster evidence only; direct-read semantics remain primary.

| Test file | Semantic edges | Authority trace edges | Recommended action |
|---|---:|---:|---|
| `tests/test_adm_003_7_plus_1_panel_role_354.py` | 6 | 2 | materialize ADM-003 artifact TESTS edge and candidate authority/boundary traces; keep commit-scope checks git-history-gated |
| `tests/test_adr_0008_reconciliation_cleanup.py` | 4 | 1 | materialize ADR-0008 TESTS edge and scoped-acceptance authority trace; preserve negative claim boundary |
| `tests/test_adr_0033_star_map_homoiconic_entity.py` | 6 | 1 | materialize ADR-0033 document/runtime TESTS edges and star_map type coverage edge |
| `tests/test_adr_0034_d2d_sealed_sender.py` | 5 | 3 | materialize ADR-0034 TESTS edge plus candidate CDL-060/CDL-061 boundary traces and non-authorization edges |
| `tests/test_adr_stale_reconciliation_strike_force_1156.py` | 5 | 1 | materialize memo/window guidance TESTS edges and planning-authority trace |
| `tests/test_agent_auto_strategy.py` | 6 | 0 | materialize runtime TESTS and EveAgent auto-mining COVERS_SYMBOL edges; no authority trace expected |
| `tests/test_agent_descriptors.py` | 4 | 0 | materialize agent descriptor runtime TESTS and COVERS_SYMBOL edges |
| `tests/test_agent_dossier_export.py` | 6 | 0 | materialize agent dossier export TESTS and COVERS_SYMBOL edges |
| `tests/test_agent_profiles.py` | 7 | 0 | materialize agent profile analysis TESTS and COVERS_SYMBOL edges |
| `tests/test_agent_strategy.py` | 7 | 0 | materialize EveAgent strategy TESTS and COVERS_SYMBOL edges; no authority trace expected |
| `tests/test_analysis_hygiene_phase_223.py` | 8 | 1 | materialize analysis hygiene runtime TESTS and stable-error edges plus candidate Phase 223 policy trace |
| `tests/test_backlog_summary_metrics.py` | 8 | 0 | materialize devnet simulation TESTS and backlog summary COVERS_SYMBOL edges; no authority trace expected |
| `tests/test_bootstrap_operations_runbook_235.py` | 4 | 4 | materialize bootstrap runbook TESTS edge and candidate CDL/runbook authority traces |
| `tests/test_broad_exception_boundary_policy_phase_1011.py` | 6 | 1 | materialize broad-exception policy TESTS edge and candidate Phase 1011 policy trace |
| `tests/test_canon_bundle_key_registry.py` | 7 | 0 | materialize canon bundle key registry TESTS and COVERS_SYMBOL edges |
| `tests/test_canon_bundle_key_registry_cli.py` | 5 | 0 | materialize key registry CLI TESTS and command-contract edges |
| `tests/test_canon_bundle_sign_cli.py` | 5 | 0 | materialize canon bundle sign CLI TESTS and command-contract edges |
| `tests/test_canon_cli.py` | 6 | 0 | materialize canon CLI TESTS and deterministic command-contract edges |
| `tests/test_canon_export_cli.py` | 6 | 0 | materialize canon export CLI TESTS and numeric-hardening command-contract edges |
| `tests/test_cdl_001_signer_lineage_runtime.py` | 7 | 1 | materialize CDL-001 signer-lineage runtime TESTS, COVERS_SYMBOL, and authority trace edges |
| `tests/test_cdl_002_key_compromise_runtime.py` | 7 | 2 | materialize CDL-002 key-compromise runtime TESTS, recovery-flow, and supporting CDL-001 lineage edges |
| `tests/test_cdl_006_challenge_node_runtime_1382.py` | 7 | 2 | materialize CDL-006 challenge runtime TESTS, audit-path, and Phase 1382 prompt authority trace edges |
| `tests/test_cdl_007_rollback_resistance_runtime.py` | 7 | 2 | materialize CDL-007 rollback-resistance TESTS, signer-lineage dependency, and replay/conflict regression edges |
| `tests/test_cdl_011_015_ratification_evidence_gate_phase_215.py` | 5 | 1 | materialize Phase 215 gate-script TESTS and command-contract edges |
| `tests/test_cdl_028_fee_burn_candidate_lock_274_fix1.py` | 8 | 2 | materialize CDL-028 simulation/evidence TESTS edges, deterministic-output regression, and non-ratification boundary |
| `tests/test_cdl_088_opening.py` | 7 | 2 | materialize CDL-088 opening/register/walkthrough TESTS edges and explicit no-activation boundary |
| `tests/test_cdl_ratification_verification_gate_269.py` | 7 | 1 | materialize Phase 269 gate-script and handoff TESTS edges with no-runtime-change boundary |
| `tests/test_cdl_v1_ratification_330.py` | 7 | 2 | materialize CDL-V1 ratification evidence, decision-register, historical-prelock, and mutation-scope guard edges |
| `tests/test_cdl_v1_temporal_decay_runtime_388.py` | 9 | 2 | materialize CDL-V1 runtime TESTS, COVERS_SYMBOL, Decimal-hardening, and handoff trace edges |
| `tests/test_cdl_v2_ratification_331.py` | 7 | 2 | materialize CDL-V2 ratification evidence, decision-register, historical-prelock, and mutation-scope guard edges |
| `tests/test_cdl_v2_sybil_resistance_runtime_389.py` | 8 | 2 | materialize CDL-V2 runtime TESTS, COVERS_SYMBOL, validation-hardening, and V1 dependency trace edges |
| `tests/test_cdl_v3_diversity_floor_runtime_397.py` | 8 | 2 | materialize CDL-V3 diversity-floor runtime TESTS, consensus-scope, and V2 dependency trace edges |
| `tests/test_cdl_v3_ratification_332.py` | 8 | 2 | materialize CDL-V3 ratification evidence and historical-prelock dependency edges |
| `tests/test_cdl_v7_popperian_gate_runtime_398.py` | 8 | 2 | materialize CDL-V7 Popperian runtime TESTS, COVERS_SYMBOL, historicalization, and V3 dependency trace edges |
| `tests/test_cdl_v7_ratification_335.py` | 8 | 2 | materialize CDL-V7 ratification evidence, decision-register, and reproducibility-protocol edges |
| `tests/test_cdl_v_batch_a_open_and_evidence_prelock_324.py` | 8 | 2 | materialize V-series batch A opening/prelock evidence and additive decision-register guard edges |
| `tests/test_cdl_v_batch_b_open_and_evidence_prelock_325.py` | 8 | 2 | materialize V-series batch B opening/prelock evidence and additive decision-register guard edges |
| `tests/test_claim_lifecycle_playground.py` | 4 | 0 | materialize claim-lifecycle simulation TESTS and refute-target linkage edges without authority trace |
| `tests/test_claim_reward_flow.py` | 4 | 0 | materialize claim reward-flow simulation TESTS and reward-output regression edges without authority trace |
| `tests/test_claim_scores.py` | 6 | 0 | materialize claim influence analysis TESTS and CSV export COVERS_SYMBOL edges without authority trace |
| `tests/test_cli_error_output_standardization_guardrail.py` | 5 | 0 | materialize shared CLI error module TESTS and AST refactor regression edges |
| `tests/test_cli_key_loader_dedupe_phase_999.py` | 7 | 0 | materialize shared key-loader TESTS and CLI deduplication regression edges |
| `tests/test_code_health.py` | 4 | 0 | materialize repo-wide code-health TESTS and production hygiene regression edges |
| `tests/test_commit_epoch_emission_phase_193.py` | 7 | 1 | materialize commit.epoch EventLogger and devnet finalization TESTS edges |
| `tests/test_competency_kpis.py` | 6 | 0 | materialize competency KPI and AgentProfile attachment TESTS edges |
| `tests/test_config_dependency_policy_phase_1006.py` | 5 | 1 | materialize JSON-default config dependency policy TESTS and fallback-regression edges |
| `tests/test_contradiction.py` | 4 | 0 | materialize contradiction-economy simulation TESTS edges without authority trace |
| `tests/test_contradiction_war.py` | 4 | 0 | materialize contradiction-war simulation TESTS and refutation de-canonicalization edges without authority trace |
| `tests/test_crypto_migration_bundle_registry_completion_284.py` | 7 | 1 | materialize Phase 284 bundle/registry fingerprint hardening TESTS and fail-closed edges |
| `tests/test_crypto_migration_initial_tranche_283.py` | 6 | 1 | materialize Phase 283 channel-signature migration TESTS and decision-log non-mutation edges |
| `tests/test_crypto_surface_inventory_lock_280.py` | 4 | 1 | materialize Phase 280 crypto inventory artifact TESTS and non-mutation edges |
| `tests/test_cw1_convergence_window_sequence_lock.py` | 5 | 1 | materialize CW-1 sequence-lock and artifact re-verification TESTS edges |
| `tests/test_cw2_row_5_runtime_closure_evaluation.py` | 5 | 1 | materialize CW-2 row-5 honest-fail and carry-forward TESTS edges |
| `tests/test_cw4_row_7_exitability_closure_evaluation.py` | 6 | 1 | materialize CW-4 row-7 exitability evidence and planning/status TESTS edges |
| `tests/test_cw5_row_8_disposition_and_option_b_gate_synthesis.py` | 5 | 2 | materialize CW-5 row-8/Option-B no-go and blocker carry-forward edges |
| `tests/test_cw6_convergence_window_closure_gate.py` | 8 | 1 | materialize CW-6 closure coherence/capsule/gate/status/planning edges |
| `tests/test_d2e_03_readiness_257.py` | 5 | 1 | materialize D2E-03 readiness and test-vector TESTS edges |
| `tests/test_d2e_05_query_subsystem_300.py` | 6 | 1 | materialize D2E-05 query CLI command-contract and envelope regression edges |
| `tests/test_d2e_06_verify_subsystem_302.py` | 6 | 1 | materialize D2E-06 verify CLI command-contract and envelope regression edges |
| `tests/test_dag_audit_cli.py` | 6 | 1 | materialize Rust DAG audit CLI, LMDB fixture, and fail-closed signature/chain-gap edges |
| `tests/test_data_center_ballast.py` | 4 | 0 | materialize data-center ballast simulation TESTS and non-degradation regression edges |
| `tests/test_data_center_controller.py` | 5 | 0 | materialize data-center ballast command-contract and non-degradation edges |
| `tests/test_devnet_experiments.py` | 5 | 0 | materialize devnet experiment summary and CSV export TESTS edges |
| `tests/test_devnet_multi_epoch.py` | 4 | 1 | materialize devnet multi-epoch runner, ledger, and commit.epoch event TESTS edges |
| `tests/test_devnet_scenarios.py` | 5 | 0 | materialize devnet scenario config and integration TESTS edges |
| `tests/test_docs_links_resolve.py` | 5 | 0 | materialize documentation link-integrity repo-dir TESTS edges |
| `tests/test_domain_exception_hierarchy_guardrail.py` | 5 | 0 | materialize centralized domain exception hierarchy TESTS edges |
| `tests/test_domain_exception_migration_closure_gate.py` | 5 | 1 | materialize domain exception closure gate command-contract edges |
| `tests/test_domain_exception_migration_guardrail.py` | 5 | 1 | materialize AST guardrail TESTS edges for migrated protocol exception surfaces |
| `tests/test_domain_exception_rollout_foundation.py` | 2 | 1 | materialize domain exception rollout foundation TESTS and hierarchy regression edges |
| `tests/test_domain_sigmoid_sim.py` | 4 | 2 | materialize simulation TESTS and EVIDENCES edges while keeping sandbox authority support-only |
| `tests/test_duplicate_definitions.py` | 4 | 1 | materialize repo hygiene TESTS edges and keep the policy terminal reviewable until governance-authority mapping is explicit |
| `tests/test_edge_link_boundary_phase_1007.py` | 6 | 1 | materialize Phase 1007 edge/link boundary TESTS edges with explicit semantic boundary invariant |
| `tests/test_edge_removal_phase1_guardrails.py` | 5 | 1 | materialize Phase 973 graph-migration guardrail TESTS edges and preserve allowlist boundary as reviewable evidence |
| `tests/test_embedding_pipeline.py` | 8 | 3 | materialize H-010 embedding pipeline TESTS edges with ADR-0030 and SIM-EMBED-01 candidate authority traces |
| `tests/test_epistemic_code.py` | 5 | 1 | materialize epistemic-code metric TESTS edges and leave scaffold authority as support-only pending stronger canon mapping |
| `tests/test_epistemic_work_task_playground.py` | 4 | 1 | materialize epistemic work-task simulation TESTS and EVIDENCES edges with support-only sandbox trace |
| `tests/test_epoch_ledger.py` | 6 | 2 | materialize epoch ledger TESTS edges and retain support-only economic-surface traces |
| `tests/test_epoch_playground_event_log.py` | 6 | 1 | materialize epoch playground event-log TESTS and simulation-evidence edges with support-only protocol event-log trace |
| `tests/test_epoch_playground_sim.py` | 4 | 1 | materialize end-to-end epoch playground simulation TESTS and EVIDENCES edges with support-only sandbox trace |
| `tests/test_epoch_summary_emission_phase_194.py` | 5 | 1 | materialize Phase 194 epoch_summary TESTS edges and schema regression invariant |
| `tests/test_eve_life.py` | 6 | 1 | materialize legacy agent smoke TESTS edges but do not treat as current agent-admission authority |
| `tests/test_event_log_envelope_guardrail_phase_195.py` | 6 | 1 | materialize Phase 195 event envelope guardrail TESTS edges |
| `tests/test_event_log_retention_rotation_gate_phase_196.py` | 3 | 1 | materialize Phase 196 gate-script TESTS and command-contract edges |
| `tests/test_event_log_retention_rotation_phase_196.py` | 4 | 1 | materialize Phase 196 retention runtime TESTS edges and deletion-boundary invariant |
| `tests/test_fairness_metrics.py` | 9 | 1 | materialize fairness metric TESTS edges but preserve toy-model limitation as a non-claim |
| `tests/test_fastapi_route_cleanup_1378.py` | 6 | 2 | materialize no-public-route cleanup TESTS edges and explicit no-activation non-claim edge |
| `tests/test_freshness_gate_invariants_gate_phase_217.py` | 3 | 2 | materialize Phase 217 freshness gate-script TESTS edges and dependency trace to Phase 212 |
| `tests/test_freshness_gate_phase_217.py` | 6 | 2 | materialize Phase 217 freshness gate runtime TESTS edges with node-value-kernel interaction trace |
| `tests/test_genesis_accrual_governor_gate_phase_218.py` | 3 | 2 | materialize Phase 218 governor gate-script TESTS edges and dependency trace to Phase 212 |
| `tests/test_genesis_accrual_governor_phase_218.py` | 6 | 2 | materialize Phase 218 genesis accrual governor runtime TESTS edges with policy trace |
| `tests/test_genesis_compile_coverage_diagnostic.py` | 6 | 1 | materialize compile diagnostic TESTS and EVIDENCES edges as diagnostic support, not canonical graph mutation |
| `tests/test_genesis_install_smoke_phase_224.py` | 5 | 1 | materialize Phase 224 install smoke TESTS edges and package command-contract edge |
| `tests/test_genesis_integration_smoke_phase_224.py` | 10 | 3 | materialize Phase 224 integration smoke TESTS edges across node-value, reward, governor, and conformance modules |
| `tests/test_genesis_node_candidate_crawl.py` | 7 | 2 | materialize Genesis node candidate crawl artifact TESTS edges as diagnostic/support edges pending promotion review |
| `tests/test_genesis_packaging_distribution_sequence_phase_222.py` | 4 | 1 | materialize Phase 222 sequence-lock doc TESTS edges and dependency-chain invariant |
| `tests/test_genesis_readiness_audit_reverification_gate_phase_1012.py` | 3 | 1 | materialize Phase 1012 reverification gate TESTS and command-contract edges |
| `tests/test_genesis_readiness_remediation_closure_gate_phase_1009.py` | 3 | 1 | materialize Phase 1009 remediation closure gate TESTS and command-contract edges |
| `tests/test_genesis_star_map_gap_analysis.py` | 7 | 2 | materialize star-map gap-analysis TESTS and EVIDENCES edges as diagnostic support pending promotion review |
| `tests/test_genesis_work_task_model.py` | 7 | 1 | materialize Genesis work-task model TESTS and bridge edges with support-only artifact trace |
| `tests/test_getting_started_docs_phase_1010.py` | 3 | 1 | materialize Phase 1010 documentation TESTS edges |
| `tests/test_glossary_term_elevation_phase_992_near_prep.py` | 4 | 1 | materialize near-prep glossary TESTS edges with explicit non-governance scope |
| `tests/test_governance_config.py` | 6 | 1 | materialize governance config TESTS edges with support-only config trace |
| `tests/test_governance_config_diagnostics.py` | 3 | 1 | materialize Phase 166 governance config diagnostic TESTS edges |
| `tests/test_governance_engine.py` | 5 | 1 | materialize governance fee-scaling TESTS edges |
| `tests/test_governance_ingest_helper_domain_exceptions.py` | 4 | 1 | materialize Phase 184 governance-ingest exception migration TESTS edges |
| `tests/test_governance_weight_phase_207.py` | 3 | 2 | materialize governance-weight pipeline TESTS edges and precision hardening trace |
| `tests/test_graph_edges.py` | 5 | 1 | materialize graph edge API TESTS edges and edge-surface removal invariant |
| `tests/test_graph_kpis.py` | 7 | 1 | materialize graph KPI TESTS edges with support-only analytics trace |
| `tests/test_hardware_archetypes.py` | 6 | 1 | materialize hardware archetype TESTS edges with support-only strategy-sim trace |
| `tests/test_hash_id_compatibility_contract_281.py` | 3 | 1 | materialize Phase 281 hash-ID contract doc TESTS edges and non-claim boundary |
| `tests/test_homoiconic_test_registry_forward_plan.py` | 5 | 1 | materialize homoiconic test registry forward-plan TESTS edges and executor non-claim |
| `tests/test_homoiconic_test_registry_implementation_guidance.py` | 5 | 2 | materialize implementation-guidance TESTS edges and forward-route trace to Window 1576-1584 |
| `tests/test_idea_descent_genesis_star_map_loop.py` | 6 | 1 | materialize idea-descent star-map sidecar TESTS/EVIDENCES edges without treating sidecar output as signing authority |
| `tests/test_idea_descent_phase_prompt_loop.py` | 6 | 1 | materialize idea-descent phase-prompt sidecar TESTS/EVIDENCES edges with no phase-authority promotion |
| `tests/test_ilc_cluster_a_governance_apply.py` | 4 | 1 | materialize Cluster A governance-apply TESTS edges with signature/digest invariant |
| `tests/test_ilc_cluster_a_ingest.py` | 4 | 1 | materialize Cluster A ingest TESTS edges and stable envelope invariant |
| `tests/test_ilc_cluster_a_replay_determinism.py` | 4 | 1 | materialize Cluster A replay determinism TESTS edges |
| `tests/test_ilc_cluster_a_replay_proof_ci_gate.py` | 4 | 1 | materialize Cluster A replay-proof CI gate TESTS edges |
| `tests/test_ilc_cluster_a_replay_proof_ci_gate_baseline.py` | 5 | 1 | materialize Cluster A CI baseline TESTS edges and deterministic drift invariant |
| `tests/test_ilc_cluster_a_replay_proof_cli_batch.py` | 5 | 1 | materialize Cluster A replay-proof CLI batch TESTS edges |
| `tests/test_ilc_governance_record_schema.py` | 4 | 1 | materialize governance record schema TESTS edges |
| `tests/test_ilc_node_v0.py` | 4 | 1 | materialize node_v0 TESTS edges with no-public-activation non-claim |
| `tests/test_integration_coherence_248.py` | 4 | 1 | materialize Phase 248 coherence doc TESTS edges and ratification non-claim |
| `tests/test_integration_coherence_336.py` | 4 | 1 | materialize Phase 336 coherence doc TESTS edges and mutation-boundary non-claim |
| `tests/test_issuance_analysis_256.py` | 4 | 1 | materialize Phase 256 issuance analysis TESTS edges and references to Phase 247/233 artifacts |
| `tests/test_issuance_evidence_closure_266.py` | 4 | 1 | materialize Phase 266 issuance evidence TESTS edges and CDL mutation non-claim |
| `tests/test_issuance_governance_activation_survey_247.py` | 3 | 1 | materialize Phase 247 issuance survey TESTS edges |
| `tests/test_issuance_governance_plan_233.py` | 3 | 1 | materialize Phase 233 issuance governance plan TESTS edges |
| `tests/test_kernel.py` | 6 | 1 | materialize legacy kernel smoke TESTS edges without current authority promotion |
| `tests/test_known_records_migration_phase_197.py` | 5 | 1 | materialize Phase 197 known-record migration TESTS edges |
| `tests/test_ledger_config_typed_contract_guardrails_phase1.py` | 4 | 1 | materialize phase-1 typed-contract scanner TESTS edges over ledger/config targets |
| `tests/test_ledger_export_domain_exceptions.py` | 5 | 1 | materialize Phase 185 ledger export exception TESTS edges |
| `tests/test_ledger_persistence.py` | 5 | 1 | materialize ledger persistence TESTS edges and wall-clock fixture non-claim |
| `tests/test_ledger_signature_migration_contract_282.py` | 3 | 1 | materialize Phase 282 ledger signature migration contract TESTS edges |
| `tests/test_ledger_typed_contract_guardrails_phase2.py` | 5 | 1 | materialize phase-2 typed-contract scanner TESTS edges over ledger settlement targets |
| `tests/test_ledger_typed_contract_guardrails_phase3.py` | 6 | 1 | materialize phase-3 typed-contract scanner TESTS edges over canonical bundle targets |
| `tests/test_ledger_typed_contract_guardrails_phase4.py` | 3 | 1 | materialize phase-4 typed-contract scanner TESTS edges over key-registry/export targets |
| `tests/test_license_presence_phase_997.py` | 6 | 1 | materialize license posture TESTS edges with current layered-license semantics |
| `tests/test_light_cone_kpis.py` | 5 | 1 | materialize light-cone KPI TESTS edges with support-only analytics trace |
| `tests/test_lineage_event_schema_phase_240.py` | 3 | 2 | materialize Phase 240 lineage-schema TESTS edges and non-ratification boundary trace |
| `tests/test_lmdb_public_runtime_store.py` | 7 | 1 | materialize LMDB public runtime TESTS edges and support-only three-machine hardening trace |
| `tests/test_local_spectral_analytics.py` | 5 | 2 | materialize H-006b spectral analytics TESTS edges with ADR-0032 support trace |
| `tests/test_logging_config.py` | 3 | 1 | materialize centralized logging bootstrap TESTS edge and Phase 163 trace |
| `tests/test_logging_entry_surface_contracts.py` | 4 | 1 | materialize logging entry-surface TESTS edges with Phase 168 support trace |
| `tests/test_main_track_return_closure_gate_phase_201.py` | 3 | 1 | materialize Phase 201 closure-gate TESTS edge and phase-range evidence trace |
| `tests/test_main_track_return_closure_gate_phase_211.py` | 3 | 1 | materialize Phase 211 closure-gate TESTS edge and phase-range evidence trace |
| `tests/test_main_track_return_closure_gate_phase_221.py` | 4 | 1 | materialize Phase 221 closure-gate TESTS edge and phase-range evidence trace |
| `tests/test_main_track_return_preflight_gate_phase_200.py` | 3 | 1 | materialize Phase 200 preflight-gate TESTS edge and phase-range evidence trace |
| `tests/test_main_track_return_preflight_gate_phase_210.py` | 3 | 1 | materialize Phase 210 preflight-gate TESTS edge and phase-range evidence trace |
| `tests/test_main_track_return_preflight_gate_phase_220.py` | 3 | 1 | materialize Phase 220 preflight-gate TESTS edge and phase-range evidence trace |
| `tests/test_mcp_cli_adapter.py` | 5 | 1 | materialize MCP CLI adapter TESTS edges with audit-provenance regression trace |
| `tests/test_mcp_cli_domain_exceptions.py` | 5 | 1 | materialize MCP CLI domain-exception TESTS edges with Phase 186 trace |
| `tests/test_mempalace_logic_gate_profile_and_window_607_615.py` | 6 | 2 | materialize MemPalace logic-gate and window-boundary TESTS edges |
| `tests/test_merkle_laplacian_v02_followon_sims.py` | 6 | 2 | materialize Merkle-Laplacian follow-on SIM evidence edges as internal research only |
| `tests/test_merkle_laplacian_v02_strike_force_sim.py` | 6 | 1 | materialize Merkle-Laplacian strike-force SIM evidence edges as internal research only |
| `tests/test_meta_test_integrity_controls.py` | 3 | 1 | materialize meta-test integrity control as suite-level regression guard |
| `tests/test_mutation_canary_phase_297.py` | 7 | 1 | materialize mutation-canary TESTS edges as security-regression guard traces |
| `tests/test_namespace_health.py` | 6 | 1 | materialize namespace-health analytics TESTS edges with support-only trace |
| `tests/test_network.py` | 5 | 1 | materialize legacy network gossip TESTS edges with ADR-0011 support trace |
| `tests/test_network_gossip.py` | 6 | 1 | materialize in-process gossip TESTS edges with ADR-0011 support trace |
| `tests/test_network_topology.py` | 6 | 1 | materialize devnet topology and node-load TESTS edges |
| `tests/test_no_ellipses_in_walkthroughs.py` | 4 | 1 | materialize no-ellipsis hygiene guard as suite-level documentation regression edge |
| `tests/test_no_silent_exception_pass_phase_1000.py` | 3 | 1 | materialize CLI silent-exception hygiene guard as suite-level regression edge |
| `tests/test_node_id_dual_contract_phase_1002.py` | 6 | 1 | materialize Phase 1002 node-id dual-contract TESTS edges |
| `tests/test_node_id_migration_utility_phase_1004.py` | 4 | 1 | materialize Phase 1004 migration-utility TESTS edges |
| `tests/test_node_id_runtime_bridge_phase_1003.py` | 4 | 1 | materialize Phase 1003 runtime-bridge TESTS edges |
| `tests/test_node_load_export.py` | 4 | 1 | materialize node-load export TESTS edges |
| `tests/test_node_schema_implementation_readiness_356.py` | 4 | 1 | materialize Phase 356 readiness artifact TESTS edge and non-implementation boundary trace |
| `tests/test_node_value_conformance_phase_206.py` | 6 | 1 | materialize Phase 206 node-value conformance TESTS edges |
| `tests/test_node_value_extraction_phase_204.py` | 6 | 1 | materialize Phase 204 node-value extraction TESTS edges |
| `tests/test_node_value_governance_conformance_gate_phase_219.py` | 3 | 1 | materialize Phase 219 gate-script TESTS edge and phase evidence trace |
| `tests/test_node_value_governance_conformance_phase_219.py` | 6 | 1 | materialize Phase 219 conformance-report TESTS edges |
| `tests/test_node_value_input_canon_phase_203.py` | 5 | 1 | materialize Phase 203 input-canon TESTS edges |
| `tests/test_node_value_kernel_phase_205.py` | 7 | 1 | materialize Phase 205 node-value kernel TESTS edges |
| `tests/test_node_value_policy_migration_phase_209.py` | 5 | 1 | materialize Phase 209 policy-migration TESTS edges |
| `tests/test_nodeid_strict_canonical_closure_gate_phase_1014.py` | 3 | 1 | materialize Phase 1014 NodeID closure-gate TESTS edge |
| `tests/test_non_replay_domain_exception_foundation.py` | 2 | 1 | materialize non-replay domain exception foundation TESTS edge |
| `tests/test_non_replay_domain_exception_migration_closure_gate.py` | 3 | 1 | materialize non-replay domain exception closure-gate TESTS edge |
| `tests/test_non_replay_domain_exception_migration_guardrail.py` | 9 | 1 | materialize non-replay exception migration guardrail as module-set TESTS edges |
| `tests/test_operator_config_docs_phase_1008.py` | 3 | 1 | materialize operator config documentation TESTS edges |
| `tests/test_outcome_logger.py` | 4 | 1 | materialize outcome logger TESTS edge as simulation/support evidence |
| `tests/test_package_hygiene_phase_1005.py` | 5 | 1 | materialize package hygiene TESTS edges |
| `tests/test_paradigm_shift.py` | 5 | 1 | materialize legacy paradigm-shift economics TESTS edge as support-only trace |
| `tests/test_patent_application_numbers_status.py` | 6 | 2 | materialize patent application-numbers status TESTS edge with explicit blocked-public-path boundary |
| `tests/test_path_lift_counterfactual_phase_214.py` | 4 | 1 | materialize Phase 214 path-lift counterfactual TESTS edges |
| `tests/test_phase_0947_h012_epoch_attribution_settle.py` | 4 | 2 | materialize H-012 attribution settlement evidence TESTS edges to CDL-081/CDL-083 terminals |
| `tests/test_phase_1101_window_945_1101_closure_gate.py` | 6 | 2 | materialize Phase 1101 closure-gate TESTS and evidence edges |
| `tests/test_phase_1107_h_con_02_panel_quorum_settle.py` | 5 | 2 | materialize CDL-083/H-CON-02 evidence TESTS edges |
| `tests/test_phase_1115_cdl_084_provenance_chain_attribution.py` | 5 | 2 | materialize CDL-084 provenance attribution evidence TESTS edges |
| `tests/test_phase_1120_sim_provenance_01_commissioning.py` | 9 | 2 | materialize SIM-PROVENANCE-01 commissioning TESTS and evidence edges |
| `tests/test_phase_1121_sim_provenance_01_run02_disposition.py` | 7 | 2 | materialize SIM-PROVENANCE-01 run02 disposition TESTS and evidence edges |
| `tests/test_phase_1123_window_1118_1123_closure_gate.py` | 9 | 2 | materialize Window 1118-1123 closure-gate TESTS and evidence edges |
| `tests/test_phase_1127_cdl_084_q2_amendment.py` | 6 | 2 | materialize CDL-084 Q2 amendment TESTS and authority trace edges |
| `tests/test_phase_1129_fix1_provenance_input_hardening.py` | 5 | 2 | materialize PROVENANCE input-hardening runtime TESTS edges |
| `tests/test_phase_1131_sim_spectral_02_signal_definition.py` | 5 | 2 | materialize SIM-SPECTRAL-02 signal-definition research TESTS edges |
| `tests/test_phase_1132_sim_spectral_02_harness.py` | 5 | 2 | materialize SIM-SPECTRAL-02 harness TESTS and evidence edges |
| `tests/test_phase_1133_sim_spectral_02_fix2.py` | 6 | 2 | materialize SIM-SPECTRAL-02 Fix2 diagnostic TESTS and evidence edges |
| `tests/test_phase_1133_sim_spectral_02_fix3.py` | 5 | 2 | materialize SIM-SPECTRAL-02 Fix3 diagnostic TESTS and evidence edges |
| `tests/test_phase_1133_sim_spectral_02_run01.py` | 4 | 2 | materialize SIM-SPECTRAL-02 Run01 summary TESTS and evidence edges |
| `tests/test_phase_1134_sim_spectral_02_run01_disposition.py` | 4 | 2 | materialize SIM-SPECTRAL-02 Run01 disposition TESTS and non-overclaim edges |
| `tests/test_phase_1135_fix1_sim_spectral_02_run02_homoiconic.py` | 6 | 2 | materialize SIM-SPECTRAL-02 Run02 Fix1 homoiconic rerun TESTS edges |
| `tests/test_phase_1135_sim_spectral_02_run02.py` | 5 | 2 | materialize SIM-SPECTRAL-02 Run02 matrix TESTS and evidence edges |
| `tests/test_phase_1136_sim_spectral_02_run02_disposition.py` | 4 | 2 | materialize SIM-SPECTRAL-02 Run02 disposition TESTS and evidence edges |
| `tests/test_phase_1136a_genesis_morphogenic_hypergraph_atlas.py` | 5 | 3 | materialize Genesis morphogenic atlas TESTS and star-map authority trace edges |
| `tests/test_phase_1137_coherence_capsule_v5_38.py` | 8 | 2 | materialize Phase 1137 coherence/capsule TESTS and evidence edges |
| `tests/test_phase_1140_run02_fix2_corrected_baseline.py` | 4 | 2 | materialize SIM-SPECTRAL-02 Run02 Fix2 baseline TESTS and evidence edges |
| `tests/test_phase_1141_run02_fix2_disposition_addendum.py` | 4 | 2 | materialize SIM-SPECTRAL-02 Run02 Fix2 disposition addendum TESTS edges |
| `tests/test_phase_1142_atlas_tier1_genesis_attestation.py` | 7 | 3 | materialize Genesis Tier-1 attestation TESTS and authority trace edges |
| `tests/test_phase_1142s_genesis_signing_ceremony.py` | 9 | 3 | materialize Genesis signing ceremony TESTS and signed-root authority trace edges |
| `tests/test_phase_1143_genesis_compile_checkpoint_1.py` | 5 | 2 | materialize GENESIS-COMPILE checkpoint #1 TESTS and authority trace edges |
| `tests/test_phase_1144_sim_spectral_03_harness.py` | 6 | 2 | materialize SIM-SPECTRAL-03 harness TESTS and signed-star-map linkage edges |
| `tests/test_phase_1145_sim_spectral_03_run01.py` | 5 | 2 | materialize SIM-SPECTRAL-03 Run01 TESTS and signed-star-map evidence edges |
| `tests/test_phase_1145a_topology_search.py` | 6 | 2 | materialize SIM-SPECTRAL-03 topology-search TESTS and non-pass evidence edges |
| `tests/test_phase_1146_sim_spectral_03_disposition.py` | 4 | 2 | materialize SIM-SPECTRAL-03 disposition TESTS and no-CDL-mutation boundary edges |
| `tests/test_phase_1147_window_1139_1147_closure_gate.py` | 8 | 3 | materialize Window 1139-1147 closure-gate TESTS and carry-forward obligation edges |
| `tests/test_phase_1150_genesis_compile_checkpoint_2.py` | 7 | 2 | materialize GENESIS-COMPILE checkpoint #2 TESTS and v0.1 preservation edges |
| `tests/test_phase_1151_composability_audit.py` | 5 | 2 | materialize Genesis composability audit TESTS and signed-star-map trace edges |
| `tests/test_phase_1152_sim_spectral_04_program_spec.py` | 4 | 2 | materialize SIM-SPECTRAL-04 program-spec TESTS and boundary edges |
| `tests/test_phase_1154_pre_public_rc_obligations_synthesis.py` | 4 | 2 | materialize pre-public-RC obligations synthesis TESTS and no-scope-creep edges |
| `tests/test_phase_1157_adr_0020_acceptance.py` | 5 | 2 | materialize ADR-0020 acceptance TESTS and unsigned v0.2 candidate trace edges |
| `tests/test_phase_1158_adr_batch_acceptance.py` | 8 | 2 | materialize Phase 1158 ADR acceptance batch TESTS and scope-boundary edges |
| `tests/test_phase_1159_adr_0036_release_key_draft.py` | 3 | 2 | materialize ADR-0036 proposed release-key draft TESTS and separation boundary edges |
| `tests/test_phase_1160_claim_composition_projection_build.py` | 4 | 2 | materialize claim-composition projection build TESTS and evidence edges |
| `tests/test_phase_1161_sim_spectral_04_run01.py` | 5 | 2 | materialize SIM-SPECTRAL-04 Run01 TESTS and gate-fail evidence edges |
| `tests/test_phase_1162_sim_spectral_04_disposition.py` | 4 | 2 | materialize SIM-SPECTRAL-04 disposition TESTS and no-opening boundary edges |
| `tests/test_phase_1169_sim_spectral_05_track_a.py` | 6 | 2 | materialize SIM-SPECTRAL-05 Track A TESTS and non-overclaim edges |
| `tests/test_phase_1170_branchial_projection_build.py` | 4 | 2 | materialize SIM-SPECTRAL-05 Track B projection TESTS and ADR-0037 criterion trace edges |
| `tests/test_phase_1171_sim_spectral_05_disposition.py` | 5 | 3 | materialize SIM-SPECTRAL-05 combined disposition TESTS and gate-pass evidence edges |
| `tests/test_phase_1172_cdl_085_opening.py` | 7 | 3 | materialize CDL-085 opening TESTS, gate-pass evidence, and no-ratification boundary edges |
| `tests/test_phase_1173_adr_0036_0037_acceptance.py` | 6 | 3 | materialize ADR-0036/0037 acceptance TESTS and authority trace edges |
| `tests/test_phase_1176_sequence_lock.py` | 2 | 1 | materialize Window 1176-1182 sequence-lock TESTS edge |
| `tests/test_phase_1177_cdl_085_prelock.py` | 4 | 1 | materialize CDL-085 prelock TESTS and pre-ratification boundary edges |
| `tests/test_phase_1179_sim_spectral_05_runtime_binding_slice.py` | 7 | 2 | materialize runtime-binding observer-slice TESTS and phi-bound trace edges |
| `tests/test_phase_1180_sim_spectral_05_economic_flow_slice.py` | 7 | 2 | materialize economic-flow observer-slice TESTS and phi-bound trace edges |
| `tests/test_phase_1181_coherence_capsule_v5_43.py` | 5 | 2 | materialize Phase 1181 coherence/capsule TESTS and deferral-boundary edges |
| `tests/test_phase_1183_sequence_lock.py` | 3 | 1 | materialize Window 1183-1190 sequence-lock TESTS edges |
| `tests/test_phase_1184_cdl_085_prelock_hardening.py` | 4 | 1 | materialize CDL-085 prelock hardening historical TESTS and boundary edges |
| `tests/test_phase_1185_cdl_085_ratification.py` | 7 | 2 | materialize CDL-085 ratification TESTS, runtime binding, and suppression-behavior edges |
| `tests/test_phase_1187_sim_spectral_05_gossip_slice.py` | 6 | 2 | materialize SIM-SPECTRAL-05 gossip-slice TESTS and phi-bound decision edges |
| `tests/test_phase_1188_cdl_001_scoping.py` | 5 | 2 | materialize CDL-001 scoping correction TESTS and non-reuse boundary edges |
| `tests/test_phase_1191_sequence_lock.py` | 4 | 1 | materialize Window 1191-1199 sequence-lock TESTS edges |
| `tests/test_phase_1193_v0_2_signing_skip.py` | 5 | 1 | materialize Phase 1193 v0.2 signing deferral TESTS and no-artifact edges |
| `tests/test_phase_1194_cdl_086_public_launch_packaging_blocker.py` | 6 | 2 | materialize CDL-086 opening TESTS and public-launch nonclaim edges |
| `tests/test_phase_1195_tier3_runtime_linkage.py` | 4 | 2 | materialize Tier-3 runtime-linkage scoping TESTS and non-mutation edges |
| `tests/test_phase_1196_persistent_rate_limiter.py` | 3 | 2 | materialize persistent rate-limiter scope TESTS and CDL-077 trace edges |
| `tests/test_phase_1197_canon_bundle_signing_repair.py` | 6 | 1 | materialize canon bundle signing repair TESTS and guardrail edges |
| `tests/test_phase_1200_sequence_lock.py` | 4 | 1 | materialize Window 1200-1208 sequence-lock TESTS edges |
| `tests/test_phase_1202_persistent_rate_limiter.py` | 6 | 2 | materialize persistent fetch rate limiter runtime TESTS and COVERS_SYMBOL edges |
| `tests/test_phase_1203_cdl_086_deliberation.py` | 6 | 1 | materialize CDL-086 deliberation TESTS and public-launch blocker edges |
| `tests/test_phase_1209_sequence_lock.py` | 4 | 1 | materialize Window 1209-1217 sequence-lock TESTS edges |
| `tests/test_phase_1210_phi_bound_enforcement.py` | 6 | 2 | materialize phi-bound runtime enforcement TESTS and COVERS_SYMBOL edges |
| `tests/test_phase_1211_truth_primitive_permanence_packet.py` | 3 | 2 | materialize truth-primitive permanence packet TESTS and boundary edges |
| `tests/test_phase_1212_rate_limiter_wiring.py` | 7 | 2 | materialize persistent rate limiter transport wiring TESTS and runtime edges |
| `tests/test_phase_1214_cdl_086_deferral.py` | 4 | 1 | materialize CDL-086 deferral TESTS and no-ratification-evidence edges |
| `tests/test_phase_1215_v0_2_signing_skip.py` | 4 | 1 | materialize Phase 1215 v0.2 signing deferral TESTS and no-artifact edges |
| `tests/test_phase_1217_post_closure_audit_hardening.py` | 4 | 1 | materialize post-1217 persistent rate limiter hardening TESTS edges |
| `tests/test_phase_1218_sequence_lock.py` | 5 | 2 | materialize Window 1218-1224 sequence-lock TESTS and attestation-boundary edges |
| `tests/test_phase_1218b_security_hardening.py` | 9 | 1 | materialize Phase 1218b security-hardening TESTS edges across network and ledger modules |
| `tests/test_phase_1221_v0_2_signing_skip.py` | 4 | 1 | materialize Phase 1221 v0.2 signing deferral TESTS and unsigned-candidate boundary edges |
| `tests/test_phase_1222_reciprocal_fetch_admission_spec.py` | 5 | 2 | materialize reciprocal fetch admission and graph projection interface spec TESTS edges |
| `tests/test_phase_1223_coherence_capsule_v5_48.py` | 6 | 1 | materialize Phase 1223 coherence/capsule TESTS and boundary edges |
| `tests/test_phase_1224_fix1_post_closure_audit_hardening.py` | 7 | 1 | materialize Phase 1224 Fix1 security-hardening TESTS edges |
| `tests/test_phase_1225_sequence_lock.py` | 5 | 1 | materialize Window 1225-1232 sequence-lock TESTS and nonauthorization edges |
| `tests/test_phase_1228_cdl_087_prelock.py` | 5 | 2 | materialize CDL-087 prelock TESTS and pull-first boundary edges |
| `tests/test_phase_1229_agent_graph_projection_runtime.py` | 9 | 2 | materialize agent graph projection runtime TESTS and COVERS_SYMBOL edges |
| `tests/test_phase_1230_v0_2_signing_skip.py` | 4 | 1 | materialize Phase 1230 v0.2 signing deferral TESTS and unsigned-candidate boundary edges |
| `tests/test_phase_1231_coherence_capsule_v5_49.py` | 6 | 2 | materialize Phase 1231 coherence/capsule TESTS and deferral edges |
| `tests/test_phase_1235_commit_epoch_canonical_mutation.py` | 10 | 2 | materialize canonical commit.epoch runtime TESTS and COVERS_SYMBOL edges |
| `tests/test_phase_1236_commit_epoch_emission_connector.py` | 6 | 2 | materialize commit.epoch emission connector TESTS and COVERS_SYMBOL edges |
| `tests/test_phase_1236_fix1_commit_epoch_full_connector_spec.py` | 4 | 2 | materialize Phase 1236 Fix1 spec TESTS and policy-boundary edges |
| `tests/test_phase_1236_fix2_commit_epoch_quorum_projection.py` | 6 | 2 | materialize quorum projection runtime TESTS and COVERS_SYMBOL edges |
| `tests/test_phase_1236_fix3_commit_epoch_causal_frontier_projection.py` | 6 | 2 | materialize causal frontier projection TESTS and COVERS_SYMBOL edges |
| `tests/test_phase_1236_fix4_commit_epoch_finalized_adapter.py` | 6 | 2 | materialize finalized adapter runtime TESTS and COVERS_SYMBOL edges |
| `tests/test_phase_1236_fix5_rust_fixture_mapping.py` | 6 | 2 | materialize Rust fixture mapping TESTS edges across Python and Rust consensus surfaces |
| `tests/test_phase_1236_fix6_devnet_end_to_end_harness.py` | 6 | 2 | materialize devnet harness TESTS and nonactivation boundary edges |
| `tests/test_phase_1237_fix2_ego_graph_query.py` | 6 | 2 | materialize sidecar ego-graph TESTS and projection compatibility edges |
| `tests/test_phase_1237_fix3_centrality_metrics.py` | 6 | 2 | materialize sidecar centrality TESTS and no-float metric edges |
| `tests/test_phase_1237_fix4_convergence_trace.py` | 6 | 2 | materialize sidecar convergence-trace TESTS and cycle-protection edges |
| `tests/test_phase_1237_fix5_dispatcher_integration.py` | 6 | 2 | materialize sidecar dispatcher TESTS, query surface, and harness-boundary edges |
| `tests/test_phase_1237_fix6_canonical_export_bundle.py` | 6 | 2 | materialize sidecar canonical export TESTS and canonical encoding edges |
| `tests/test_phase_1237_l3_sidecar_spec.py` | 5 | 2 | materialize sidecar spec TESTS, expansion-plan, and mutation-boundary edges |
| `tests/test_phase_1237_post_fix7_sidecar_audit_hardening.py` | 6 | 2 | materialize post-Fix7 sidecar hardening TESTS and bounded-query edges |
| `tests/test_phase_1237_sidecar_query_runtime.py` | 6 | 2 | materialize sidecar runtime skeleton TESTS and guardrail edges |
| `tests/test_phase_1238_sim_fetch_01_harness.py` | 5 | 2 | materialize SIM-FETCH-01 harness TESTS and CDL-087 prelock/nonratification edges |
| `tests/test_phase_1238a_sim_fetch_01_fix1_hardening.py` | 5 | 2 | materialize SIM-FETCH Fix1 hardening TESTS and deterministic-RNG boundary edges |
| `tests/test_phase_1238b_sim_fetch_01_fix2_request_model.py` | 4 | 2 | materialize SIM-FETCH Fix2 request-model TESTS and research-evidence edges |
| `tests/test_phase_1238c_sim_fetch_01_fix3_tier_verdict.py` | 4 | 2 | materialize SIM-FETCH Fix3 tier-verdict TESTS and nonratification edges |
| `tests/test_phase_1238d_sim_fetch_01_fix4_routed_holder_model.py` | 4 | 2 | materialize SIM-FETCH Fix4 routed-holder TESTS and research-only classification edges |
| `tests/test_phase_1238e_sim_fetch_01_fix5_routed_multihop_retry.py` | 4 | 2 | materialize SIM-FETCH Fix5 multihop retry TESTS and CDL-087 nonratification edges |
| `tests/test_phase_1238f_sim_fetch_01_fix6_adaptive_heat_replication.py` | 4 | 2 | materialize SIM-FETCH Fix6 adaptive-replication TESTS and research-only edges |
| `tests/test_phase_1238g_sim_fetch_01_fix7_cdl_078_credit_bridge.py` | 4 | 2 | materialize SIM-FETCH Fix7 CDL-078 credit-bridge TESTS and attribution-boundary edges |
| `tests/test_phase_1238h_sim_fetch_01_fix8_werner_overlay.py` | 4 | 2 | materialize SIM-FETCH Fix8 Werner-overlay TESTS and economic-nonactivation edges |
| `tests/test_phase_1238i_sim_fetch_01_fix9_cdl_087_evidence_matrix.py` | 5 | 2 | materialize SIM-FETCH Fix9 evidence-matrix TESTS and AutoResearch evidence edges |
| `tests/test_phase_1238j_sim_fetch_01_fix10_robustness_suite.py` | 5 | 2 | materialize SIM-FETCH Fix10 robustness-suite TESTS and adversarial-evidence edges |
| `tests/test_phase_1241_1248_prompt_schema_and_tokens.py` | 4 | 2 | materialize prompt-schema discipline TESTS across prompts, README, validator, and AGENTS |
| `tests/test_phase_1242_roadmap_v1_1.py` | 5 | 2 | materialize roadmap v1.1 control TESTS and public-RC nonclaim edges |
| `tests/test_phase_1243_package_boundary_inventory.py` | 6 | 2 | materialize package profile and import-boundary TESTS edges |
| `tests/test_phase_1244_import_boundary_lint_and_protocol_stubs.py` | 6 | 2 | materialize harness-interface and import-boundary TESTS edges |
| `tests/test_phase_1245_openclaw_nemoclaw_skill_preview_dependency_isolation.py` | 6 | 2 | materialize OpenClaw/NemoClaw local preview TESTS and local-only nonclaim edges |
| `tests/test_phase_1246_cdl_087_governance_review_disposition.py` | 4 | 2 | materialize CDL-087 governance disposition TESTS and review-only nonclaim edges |
| `tests/test_phase_1248_window_1241_1248_closure_gate.py` | 6 | 2 | materialize window closure TESTS and public-RC blocker carry-forward edges |
| `tests/test_phase_1250_fix1_rc_frontier_gap_audit.py` | 5 | 2 | materialize RC frontier gap audit TESTS and route-consistency edges |
| `tests/test_phase_1250_gap14_adapter_extraction.py` | 6 | 2 | materialize Gap14 adapter extraction TESTS across package boundary, protocol interfaces, and LMDB adapter |
| `tests/test_phase_1252_post_audit_route_consistency.py` | 4 | 2 | materialize post-audit route consistency TESTS edges |
| `tests/test_phase_1253_transport_principal_identity_spec.py` | 6 | 2 | materialize TransportPrincipal spec TESTS and public-P2P gating edges |
| `tests/test_phase_1254_atlas_g_004_005_graph_bridge.py` | 6 | 2 | materialize ATLAS-G dependency bridge TESTS and high-authority classification edges |
| `tests/test_phase_1258_cdl087_production_candidate_evidence_readiness.py` | 4 | 2 | materialize CDL-087 readiness TESTS and nonauthorization edges |
| `tests/test_phase_1259_cdl087_serving_peer_evidence_slice.py` | 5 | 2 | materialize CDL-087 serving-peer evidence TESTS and bootstrap snapshot edges |
| `tests/test_phase_1260_cdl087_observability_and_limiter_regression.py` | 6 | 2 | materialize CDL-087 observability and limiter-regression TESTS edges |
| `tests/test_phase_1262_werner_flow_governor_overlay_validation.py` | 5 | 2 | materialize Werner overlay validation TESTS and economic nonactivation edges |
| `tests/test_phase_1268_sidecar_loopback_projection_endpoint_boundary.py` | 5 | 2 | materialize sidecar loopback boundary TESTS and non-loopback gating edges |
| `tests/test_phase_1287_release_publication_signing_authorization_preflight.py` | 4 | 2 | materialize release publication/signing preflight TESTS and gate nonclaim edges |
| `tests/test_phase_1289_window_1289_1302_sequence_lock.py` | 4 | 2 | materialize window 1289-1302 sequence-lock TESTS and nonauthorization edges |
| `tests/test_phase_1290_context_capsule_v5_52_frontier_refresh.py` | 5 | 2 | materialize context capsule v5.52 TESTS and public-RC blocker edges |
| `tests/test_phase_1299_release_allowlist_artifact_genesis_readiness_preflight.py` | 4 | 2 | materialize release allowlist/artifact readiness preflight TESTS and no-signing edges |
| `tests/test_phase_1300_counsel_ip_publication_clearance_inventory.py` | 4 | 2 | materialize counsel/IP/publication clearance inventory TESTS and inventory-only edges |
| `tests/test_phase_1302_window_1289_1302_closure_gate.py` | 4 | 2 | materialize Window 1289-1302 closure TESTS and carry-forward blocker edges |
| `tests/test_phase_1303_window_1303_1316_sequence_lock.py` | 4 | 2 | materialize Window 1303-1316 sequence-lock TESTS and readiness-only boundary edges |
| `tests/test_phase_1304_context_capsule_v5_53_frontier_refresh.py` | 4 | 2 | materialize context capsule v5.53 TESTS and blocker-map edges |
| `tests/test_phase_1316_window_1303_1316_closure_implementation_audit.py` | 5 | 2 | materialize Window 1303-1316 closure audit TESTS and blocker-classification edges |
| `tests/test_phase_1317_window_1317_1329_sequence_lock.py` | 5 | 2 | materialize Window 1317-1329 sequence-lock TESTS and private release-dry-run boundary edges |
| `tests/test_phase_1318_context_capsule_v5_54_frontier_refresh.py` | 5 | 2 | materialize context capsule v5.54 TESTS and blocker-map edges |
| `tests/test_phase_1323_fix2_openclaw_vps_install_skill_discovery.py` | 5 | 2 | materialize OpenClaw private VPS install discovery TESTS and nonactivation edges |
| `tests/test_phase_1323_fix3_layered_license_posture.py` | 6 | 2 | materialize layered-license posture TESTS and counsel-review boundary edges |
| `tests/test_phase_1323_openclaw_nemoclaw_claimable_profile_full_dry_run.py` | 6 | 2 | materialize OpenClaw/NemoClaw private dry-run TESTS and identity-blocker edges |
| `tests/test_phase_1326_ccss_003_sealed_sender_local_delivery_boundary.py` | 6 | 2 | materialize CCSS-003 sealed-sender runtime TESTS, symbol coverage, and local-preview boundary edges |
| `tests/test_phase_1327_ccss_004_gossip_jitter_cover_policy_tests.py` | 6 | 2 | materialize CCSS-004 gossip policy TESTS, symbol coverage, and runtime-boundary edges |
| `tests/test_phase_1330_window_1330_1342_sequence_lock.py` | 5 | 2 | materialize Window 1330-1342 sequence-lock TESTS and final-RC nonauthorization edges |
| `tests/test_phase_1331_context_capsule_v5_55_release_candidate_freeze.py` | 5 | 2 | materialize context capsule v5.55 TESTS and final-RC blocker-map edges |
| `tests/test_phase_1331_fix3_network_dos_hardening.py` | 8 | 2 | materialize network DoS hardening TESTS and symbol coverage edges |
| `tests/test_phase_1332_fix4_pre_1333_hardening.py` | 10 | 2 | materialize pre-1333 hardening TESTS across network, CBOR, transport-principal, registry, Atlas, and source export gates |
| `tests/test_phase_1333_source_allowlist_export_execution_gate.py` | 6 | 2 | materialize source allowlist export gate TESTS and nonpublication boundary edges |
| `tests/test_phase_1334_release_artifact_production_gate.py` | 5 | 2 | materialize release artifact production gate TESTS and unsigned-artifact boundary edges |
| `tests/test_phase_1335_release_keys_envelopes_generation_gate.py` | 6 | 2 | materialize release key/envelope gate TESTS with ADR-0036/ADR-0037 trace and secret-boundary edges |
| `tests/test_phase_1336_public_claimability_api_activation_or_carry_forward_gate.py` | 5 | 2 | materialize public claimability API carry-forward TESTS and nonactivation boundary edges |
| `tests/test_phase_1337_public_path_sidecar_activation_or_exclusion_gate.py` | 5 | 2 | materialize public path sidecar exclusion TESTS and public-serving nonactivation edges |
| `tests/test_phase_1338_wallet_ecu_ilc_activation_or_carry_forward_gate.py` | 5 | 2 | materialize wallet/ECU/ILC carry-forward TESTS and value-path nonactivation edges |
| `tests/test_phase_1340_v0_2_signing_ceremony_gate.py` | 7 | 2 | materialize v0.2 signing ceremony TESTS, signature evidence, and secret-boundary edges |
| `tests/test_phase_1341_public_rc_publication_claim_gate.py` | 6 | 2 | materialize public RC publication claim gate TESTS and blocked-publication boundary edges |
| `tests/test_phase_1342_window_1330_1342_closure_handoff.py` | 5 | 2 | materialize Window 1330-1342 closure handoff TESTS and public-RC blocker edges |
| `tests/test_phase_1344_issuance_stack_scoping.py` | 6 | 2 | materialize issuance-stack scoping TESTS and multi-CDL surface trace edges |
| `tests/test_phase_1348_cdl_047_treasury_governance_runtime.py` | 8 | 2 | materialize CDL-047 treasury runtime TESTS, symbol coverage, evidence, and default-off boundary edges |
| `tests/test_phase_1350_cdl_083_ejected_stake_treasury_distribution.py` | 7 | 2 | materialize CDL-083 ejected-stake distribution TESTS, symbol coverage, evidence, and default-off boundary edges |
| `tests/test_phase_1351a_cdl_029_amendment_post_theta_hard_dust_routing.py` | 5 | 2 | materialize CDL-029 amendment TESTS, allocation symbol coverage, and dust-routing boundary edges |
| `tests/test_phase_1352_issuance_economics_integration_gate.py` | 6 | 2 | materialize issuance economics integration gate TESTS, multi-CDL stack trace, and nonactivation edges |
| `tests/test_phase_1354_cdl_068_topology_shuffle_vrf.py` | 6 | 2 | materialize CDL-068 topology shuffle TESTS, symbol coverage, and VRF/default-off boundary edges |
| `tests/test_phase_1357_reputation_h11_float_kill.py` | 7 | 2 | materialize H11 float-kill TESTS, Decimal runtime coverage, and CDL-060 deferral boundary edges |
| `tests/test_phase_1358_production_bridge.py` | 7 | 2 | materialize production bridge TESTS, secure gRPC/QUIC symbol coverage, and default-off transfer boundary edges |
| `tests/test_phase_1359_high_001_defense.py` | 8 | 2 | materialize HIGH-001 defense TESTS, redaction/mixing symbol coverage, and privacy/default-off boundary edges |
| `tests/test_phase_1360_multi_operator_testnet.py` | 6 | 2 | materialize multi-operator testnet topology TESTS and durable-connectivity carry-forward edges |
| `tests/test_phase_1361_adaptive_pruning.py` | 7 | 2 | materialize adaptive pruning TESTS, LMDB pruning symbol coverage, and production-pruning default-off edges |
| `tests/test_phase_1363_blocking_authority_prelock.py` | 5 | 2 | materialize CDL-089 prelock TESTS and blocking-authority governance-boundary edges |
| `tests/test_phase_1367_pre_gate_fix_pass.py` | 5 | 2 | materialize pre-gate fix TESTS and soft-RC nonclaim edges |
| `tests/test_phase_1369_fix1_numeric_hardening.py` | 7 | 2 | materialize numeric hardening TESTS across issuance, governance, Genesis guardrail, and LMDB pruning surfaces |
| `tests/test_phase_1369_sequence_lock.py` | 5 | 2 | materialize Window 1369-1390 sequence-lock TESTS and public-economics firewall edges |
| `tests/test_phase_1371_identity_bootstrap_cdl_opening.py` | 5 | 2 | materialize CDL-090 opening TESTS and identity-bootstrap nonclaim edges |
| `tests/test_phase_1372_identity_bootstrap_cdl_prelock.py` | 5 | 2 | materialize CDL-090 prelock TESTS and identity-bootstrap locked-constant edges |
| `tests/test_phase_1375_cdl_088_prelock.py` | 5 | 2 | materialize CDL-088 prelock TESTS and public-claimability activation-split edges |
| `tests/test_phase_1385_tla_safetynodualcert_disposition.py` | 6 | 2 | materialize TLA+ SafetyNoDualCert disposition TESTS, evidence, and deferred-formal-scope edges |
| `tests/test_phase_1385a_spec_d_epoch_checkpoint_safety.py` | 5 | 2 | materialize Spec D SafetyNoDualCert formal evidence TESTS and TLC evidence edges |
| `tests/test_phase_1386_genesis_validator_bootstrap_record.py` | 5 | 2 | materialize Genesis validator bootstrap exception TESTS and private-key/nonactivation boundary edges |
| `tests/test_phase_1387b_sim_genesis_compile_02.py` | 5 | 2 | materialize SIM-GENESIS-COMPILE-02 diagnostic TESTS and bootstrap-axiom evidence edges |
| `tests/test_phase_1387c_compiler_basis_expansion.py` | 3 | 2 | materialize compiler basis expansion TESTS and Category A bootstrap-axiom trace edges |
| `tests/test_phase_1387d_adr_0035_spec.py` | 4 | 2 | materialize ADR-0035 formal spec TESTS and type-system authority trace edges |
| `tests/test_phase_1387e_star_map_expansion.py` | 3 | 2 | materialize star map expansion TESTS and attestation-root governance-spine edges |
| `tests/test_phase_1387f_graph_structure_analysis.py` | 3 | 2 | materialize graph structure analysis TESTS and ADR-0035 recipe-analysis trace edges |
| `tests/test_phase_1387g_epistemic_leverage.py` | 3 | 2 | materialize epistemic leverage analysis TESTS and axiomatic-root resilience edges |
| `tests/test_phase_1387h_edge_recipe_canonicalization.py` | 3 | 2 | materialize edge recipe canonicalization TESTS and decomposition-recipe authority trace edges |
| `tests/test_phase_1387i_synthesis_report.py` | 3 | 2 | materialize graph optimization synthesis TESTS, diagnostic evidence, and forward-obligation edges |
| `tests/test_phase_1388a_cdl_048_self_counsel_clearance.py` | 6 | 2 | materialize CDL-048 self-counsel TESTS edges and candidate non-external-legal-opinion authority trace edges |
| `tests/test_phase_1389b_claimability_public_mode_runtime.py` | 8 | 3 | materialize claimability public-mode runtime TESTS, symbol coverage, and nullifier safety boundary edges |
| `tests/test_phase_1389b_claimability_public_mode_runtime_docs.py` | 4 | 2 | materialize Phase 1389b documentation TESTS edges and public-claimability nonactivation traces |
| `tests/test_phase_1390_window_closure_handoff.py` | 3 | 2 | materialize window closure handoff TESTS and support-lane gap tracking edges |
| `tests/test_phase_1396_j006_jury_assignment_runtime.py` | 5 | 2 | materialize J-006 jury assignment runtime TESTS, symbol coverage, and shadow-only authority trace edges |
| `tests/test_phase_1397_j007_shadow_public_ingestion_harness.py` | 6 | 3 | materialize J-007 shadow ingestion harness TESTS, symbol coverage, taxonomy, and nonactivation edges |
| `tests/test_phase_1401_cdl_091_runtime_stub.py` | 3 | 2 | materialize CDL-091 jury incentive stub TESTS, symbol coverage, and default-off payment safety edges |
| `tests/test_phase_1409_cdl_093_maintenance_lottery_stub.py` | 3 | 3 | materialize CDL-093 lottery stub TESTS, Werner-source trace, randomness-policy trace, and no-write boundaries |
| `tests/test_phase_1410_fix1_pre_vrf_hardening.py` | 8 | 2 | materialize pre-VRF hardening multi-runtime TESTS edges and ADR-0042 validation-gate traces |
| `tests/test_phase_1410_vrf_adr.py` | 2 | 2 | materialize ADR-0042 VRF spec TESTS edges and no-runtime/no-activation boundary traces |
| `tests/test_phase_1411_vrf_proof_verifier.py` | 5 | 2 | materialize VRF verifier TESTS, RFC vector evidence, symbol coverage, and private-key/proof-generation exclusion edges |
| `tests/test_phase_1412_vrf_integration.py` | 5 | 3 | materialize VRF jury-integration TESTS, canonical-alpha coverage, and shadow-path preservation edges |
| `tests/test_phase_1413_vrf_integration.py` | 5 | 2 | materialize VRF integration security-review TESTS and J-008 gate evidence edges |
| `tests/test_phase_1414_review_lane_adr.py` | 4 | 2 | materialize ADR-0043 review-lane contract TESTS and zero-weight/default-off boundary edges |
| `tests/test_phase_1415_review_lane_admission_runtime.py` | 5 | 2 | materialize review-lane admission runtime TESTS, canonical JSON coverage, and quote-only firewall edges |
| `tests/test_phase_1416_review_lane_dedup_payment_stub.py` | 4 | 2 | materialize review-lane dedup/payment stub TESTS, symbol coverage, and no-write boundary edges |
| `tests/test_phase_1417_review_lane_integration.py` | 5 | 2 | materialize review-lane integration TESTS, J-008 gate evidence, and default-off payment regression edges |
| `tests/test_phase_1418_anti_capture_diversity_adr.py` | 4 | 2 | materialize ADR-0044 anti-capture design TESTS and CDL-V3 diversity-floor trace edges |
| `tests/test_phase_1419_anti_capture_diversity_verification.py` | 5 | 3 | materialize anti-capture runtime TESTS, cluster diversity coverage, and J-008 evidence edges |
| `tests/test_phase_1423_rehearsal_criteria.py` | 2 | 4 | materialize private soft-RC rehearsal criteria TESTS, identity-boundary traces, topology traces, and no-activation constraints |
| `tests/test_phase_1425_pre_gate_verification.py` | 4 | 2 | materialize J-008 pre-gate verification TESTS, gate-evidence refs, and production-surface nonactivation edges |
| `tests/test_phase_1428_window_closure_gate.py` | 4 | 2 | materialize Window 1399-1428 closure TESTS, handoff inventory, and Window 1429 boundary edges |
| `tests/test_phase_1433_rehearsal_verdict.py` | 3 | 2 | materialize private rehearsal verdict TESTS, rights-safe dataset trace, transport correction, and wipe/nonactivation edges |
| `tests/test_phase_1436_public_fetch_serving_activation.py` | 9 | 2 | materialize public fetch/sidecar activation TESTS, transport-principal gate traces, OpenClaw relay traces, and public-RC/economic nonactivation edges |
| `tests/test_phase_1438_cdl088_public_claimability_activation.py` | 3 | 2 | materialize CDL-088 public claimability activation TESTS and economic/public-RC nonclaim edges |
| `tests/test_phase_1439_public_verifier_api_activation.py` | 7 | 2 | materialize public verifier API TESTS, route coverage, nullifier replay regression, and no-value-authority edges |
| `tests/test_phase_1440_claimability_integration_tests.py` | 8 | 2 | materialize Phase 1440 cross-module claimability/security TESTS and finding-resolution regression edges |
| `tests/test_phase_1441_gap_13_closure_verdict.py` | 4 | 2 | materialize Gap 13 closure TESTS, upstream evidence-token traces, and no-value-activation boundaries |
| `tests/test_phase_1442_werner_diagnostic_wiring.py` | 3 | 2 | materialize Werner diagnostic TESTS, local-credit metric coverage, and review-lane-only default-off edges |
| `tests/test_phase_1443_agpl_license_header_audit_allowlist.py` | 3 | 2 | materialize AGPL header audit and source allowlist gate TESTS plus public-RC-not-published edges |
| `tests/test_phase_1444_cla_text_finalization.py` | 3 | 2 | materialize CLA text/governance status TESTS and Gap 7 external-action deferral edges |
| `tests/test_phase_1445_gap_7_partial_closure.py` | 2 | 2 | materialize Gap 7 partial-closure status TESTS and explicit patent/trademark deferred-action edges |
| `tests/test_phase_1446_v03_genesis_root_signing_ceremony.py` | 3 | 2 | materialize v0.3 root signing ceremony TESTS, candidate attestation trace, and no-publication/no-secret edges |
| `tests/test_phase_1447_release_artifact_signing_manifest.py` | 4 | 3 | materialize release artifact manifest TESTS, Phase 1446 derivation, candidate attestation, and no-publication/no-epoch-transition edges |
| `tests/test_phase_1460p_provider_usage_adapter.py` | 3 | 1 | materialize provider-usage adapter TESTS and classify as private operational-only support, not protocol truth |
| `tests/test_phase_1461p_local_node_capture_consent_gate.py` | 5 | 1 | materialize consent-gated local capture TESTS and private/no-production-graph-write classification edges |
| `tests/test_phase_1462p_idle_capacity_scheduler.py` | 4 | 1 | materialize idle-capacity scheduler TESTS and private_fixture_only anti-gaming classification edges |
| `tests/test_phase_1464p_co_attestation_receipt.py` | 4 | 1 | materialize co-attestation receipt TESTS, deterministic receipt coverage, and private-fixture classification |
| `tests/test_phase_1464p_maintenance_task_executor.py` | 5 | 1 | materialize maintenance executor TESTS, truth-primitive artifact coverage, and private/not-activated classification |
| `tests/test_phase_1465p_harness_integration.py` | 5 | 1 | materialize private harness full-stack integration TESTS and public-RC-exclude classification edges |
| `tests/test_phase_1466p_layer0_protocol_bundle.py` | 4 | 2 | materialize ADR-0009 Layer 0 bundle TESTS, private-distribution classification, and deterministic/frozen-container edges |
| `tests/test_phase_1475p_layer1_genesis_bundle.py` | 4 | 2 | materialize ADR-0009 Layer 1 bundle TESTS, layer0 digest dependency, and private canonical bundle edges |
| `tests/test_phase_1476p_adr0009_cross_layer.py` | 5 | 1 | materialize ADR-0009 cross-layer chain TESTS and digest/schema-reference integrity edges |
| `tests/test_phase_1476p_adr0009_layers23.py` | 5 | 2 | materialize ADR-0009 Layers 2/3 TESTS, validation edges, and private distribution classification |
| `tests/test_phase_1477p_harness_kernel_integration.py` | 4 | 1 | materialize harness-kernel scheduler TESTS and Decimal-safe private ordering edges |
| `tests/test_phase_1483p_rust_p2p_bridge.py` | 3 | 2 | materialize Rust P2P bridge TESTS, CDL-078 trace, default-off guard, and bounded-subprocess edges |
| `tests/test_phase_1485p_consent_gate_local_write.py` | 6 | 2 | materialize consent-gated local immutable store TESTS and not-production/private-write classification edges |
| `tests/test_phase_1490p_cdl094_admission_wire.py` | 3 | 2 | materialize CDL-094 admission wire TESTS and fail-closed default-off transport-principal edges |
| `tests/test_phase_1494p_cdl095_runtime_completions.py` | 6 | 2 | materialize CDL-095 runtime completion TESTS, verdict/petition schema coverage, and not-production guard edges |
| `tests/test_phase_1502p_cdl031_dynamic_ranking_multiplier.py` | 5 | 3 | materialize CDL-031 dynamic-ranking TESTS, Decimal safety, anti-dominance, CDL-019 authority, and not-activated guard edges |
| `tests/test_phase_1508p_werner_sim_fetch_rerun.py` | 4 | 2 | materialize Werner SIM-FETCH rerun TESTS, simulation evidence, and no-CDL096/no-flow-governor activation edges |
| `tests/test_phase_1509p_cdl096_eligibility_checkpoint.py` | 3 | 2 | materialize CDL-096 eligibility checkpoint TESTS/evidence and explicit not-opened/nonauthorization edges |
| `tests/test_phase_1512p_genesis_governance_node_frameworks.py` | 3 | 3 | materialize governance framework TESTS and future-anchor/reference edges while preserving no-runtime/no-graph-mutation boundaries |
| `tests/test_phase_1513p_window_coherence_capsule.py` | 3 | 2 | materialize Window 1505p coherence/capsule TESTS and guard-retention/carry-forward edges |
| `tests/test_phase_1514p_window_1505p_closure_gate.py` | 3 | 2 | materialize Window 1505p closure-gate TESTS and broad nonauthorization/carry-forward edges |
| `tests/test_phase_1516p_adr_0009_layer0_layer1_integration.py` | 6 | 2 | materialize ADR-0009 Layer 0/1 integration TESTS, CID/DAG-CBOR/COSE edges, and private selftest classification |
| `tests/test_phase_1517p_adr_0009_layer2_layer3_integration.py` | 6 | 2 | materialize ADR-0009 Layer 2/3 integration TESTS, four-layer CID-chain, COSE verification, and tamper-detection edges |
| `tests/test_phase_1518p_adr_0009_bundle_verifier.py` | 6 | 2 | materialize independent ADR-0009 verifier TESTS, fixture-vector evidence, and size/signature/linkage rejection edges |
| `tests/test_phase_1524p_adr0035_dependency_reconciliation.py` | 3 | 3 | materialize ADR-0035 dependency reconciliation TESTS and distinction between content metadata, type governance, and bundle integrity edges |
| `tests/test_phase_1525p_adr0035_definition_node_schema.py` | 3 | 2 | materialize ADR-0035 definition-node schema TESTS, verifier error-token edges, and no-authority-mutation boundaries |
| `tests/test_phase_1526p_adr0035_type_system_cdl_opening.py` | 3 | 2 | materialize CDL-097 opening TESTS, ADR-0035 authority-reference edges, and CDL-096/type-registry non-activation boundaries |
| `tests/test_phase_1527p_adr0035_cdl_prelock.py` | 4 | 2 | materialize CDL-097 prelock TESTS, locked-scope regression edges, and parse-support/non-activation boundary edges |
| `tests/test_phase_1528p_adr0035_cdl_ratification.py` | 6 | 2 | materialize CDL-097 ratification TESTS, ADR-0030/ADR-0035 linkage edges, and production-write/non-activation boundaries |
| `tests/test_phase_1529p_adr0035_type_registry_scaffold.py` | 10 | 2 | materialize type-registry scaffold TESTS, symbol coverage, CDL-097 authority-ref validation, and default-off classification edges |
| `tests/test_phase_1532p_obl020_emission_production_path.py` | 6 | 6 | materialize guarded OBL-020 emission production-path TESTS, authority dependency traces, and default-off/no-write boundaries |
| `tests/test_phase_1533p_obl020_settlement_roots.py` | 5 | 2 | materialize settlement-root replay TESTS, canonical SHA-256/anti-circularity symbol coverage, and default-off boundary edges |
| `tests/test_phase_1534p_obl020_canonical_economic_events.py` | 7 | 6 | materialize canonical economic event TESTS, event-payload/root-commitment symbol coverage, CDL authority traces, and default-off numeric-safety boundaries |
| `tests/test_phase_1535p_obl020_economic_round_trip.py` | 6 | 2 | materialize OBL-020 round-trip integration TESTS and replay-identical economic event/root coverage edges |
| `tests/test_phase_1539p_obl021_validator_admission_ejection.py` | 8 | 2 | materialize OBL-021 validator transition TESTS, CDL-017/default-off traces, event-batch root coverage, and stale-root/numeric rejection edges |
| `tests/test_phase_1540p_obl022_treasury_validator_reward.py` | 8 | 3 | materialize OBL-022 treasury/validator-reward TESTS, CDL-047/CDL-054/default-off traces, and event-batch root coverage edges |
| `tests/test_phase_1541p_obl022_ejected_stake.py` | 6 | 2 | materialize OBL-022 ejected-stake distribution TESTS, CDL-083/default-off traces, H-CON-02 quorum and event-batch root coverage edges |
| `tests/test_phase_1542p_obl027_expansion_bounty.py` | 6 | 3 | materialize OBL-027 bounty scaffold TESTS, ADR-0016/CDL-047/default-off traces, and proposed-status event-batch coverage edges |
| `tests/test_phase_1543p_block4b_round_trip.py` | 5 | 1 | materialize Block 4B cross-runtime round-trip TESTS and shared default-off replay invariant edges |
| `tests/test_phase_1545p_fix13_agentic_graph_grammar_axiom_inventory.py` | 4 | 2 | materialize Fix13 graph-grammar inventory TESTS, research-only classification, and governance-routing/non-activation edges |
| `tests/test_phase_1545p_fix19_atlas_axiomatic_calibration.py` | 4 | 1 | materialize Fix19 Atlas calibration SIM TESTS, truth-primitive recipe evidence, and research-only non-promotion edges |
| `tests/test_phase_1545p_fix20_atlas_precision_replay.py` | 4 | 1 | materialize Fix20 precision replay SIM TESTS, negative-control evidence, and review-only non-promotion boundaries |
| `tests/test_phase_1545p_fix22_full_repo_genesis_atlas.py` | 7 | 1 | materialize Fix22 full-repo candidate TESTS, preimage/candidate/report coverage, and unsigned support-only boundary edges |
| `tests/test_phase_1545p_fix23_genesis_atlas_lmdb_materialization.py` | 7 | 1 | materialize Fix23 LMDB adapter/materialization TESTS, candidate-store symbol coverage, digest round-trip evidence, and noncanonical projection boundaries |
| `tests/test_phase_1545p_fix24_whole_graph_atlas_objective_contract.py` | 5 | 2 | materialize Fix24 objective-contract TESTS, Genesis-rootedness standard evidence, and signing-gate/scope-mismatch boundary edges |
| `tests/test_phase_1545p_fix25_whole_graph_baseline_diagnostic.py` | 6 | 1 | materialize Fix25 baseline diagnostic TESTS, five-dimensional coverage evidence, and directed-view-gap classification edges |
| `tests/test_phase_1545p_fix26_axiomatic_extraction_replay.py` | 6 | 1 | materialize Fix26 axiomatic extraction replay TESTS, atom-candidate queue evidence, and no-promotion classification edges |
| `tests/test_phase_1545p_fix27_rewrite_candidate_generation.py` | 5 | 1 | materialize Fix27 rewrite-generation TESTS, runner/candidate evidence, and B10-B12 fallback reclassification boundaries |
| `tests/test_phase_1545p_fix28_projection_hydration_sim.py` | 5 | 1 | materialize Fix28 projection/hydration SIM TESTS, slice/redaction evidence, and non-serving classification edges |
| `tests/test_phase_1545p_fix29_spectral_non_excisability_sim.py` | 5 | 1 | materialize Fix29 spectral SIM TESTS, Laplacian/non-excisability evidence, and authority-firewall classification edges |
| `tests/test_phase_1545p_fix2_historical_snapshot_policy.py` | 3 | 1 | materialize Fix2 pytest policy TESTS and default-off executor-profile classification edges |
| `tests/test_phase_1545p_fix30_long_autoresearch_optimization.py` | 5 | 1 | materialize Fix30 AutoResearch TESTS, iteration/checkpoint evidence, and optimized-candidate research-only boundary edges |
| `tests/test_phase_1545p_fix31_candidate_reducer_v04_v05.py` | 5 | 2 | materialize Fix31 candidate reducer TESTS, variant/batch-plan evidence, and human-scope gate boundary edges |
| `tests/test_phase_1545p_fix32_homoiconic_test_registry_contract.py` | 5 | 1 | materialize Fix32 homoiconic test registry contract TESTS and non-executor/authority non-claim classification edges |
| `tests/test_phase_1545p_fix33_test_graph_coverage.py` | 5 | 1 | materialize Fix33 coverage-checker TESTS, enriched-graph coverage evidence, and report-only non-execution classification edges |
| `tests/test_phase_1545p_fix4_patent_delivery_status.py` | 6 | 1 | materialize Fix4 patent-delivery status TESTS, canonical status symbol coverage, and public-path-blocker classification edges |
| `tests/test_phase_1545p_fix5_public_disclosure_patent_coverage.py` | 5 | 1 | materialize Fix5 patent coverage audit TESTS and human-risk/final-publication-gate boundary edges |
| `tests/test_phase_1545p_fix6_genesis_v03_methodology_preservation.py` | 4 | 2 | materialize Fix6 methodology-preservation TESTS and v0.3 baseline/non-mutation trace edges |
| `tests/test_phase_1545p_fix7_genesis_common_registry_node_candidates.py` | 4 | 2 | materialize Fix7 common-registry candidate audit TESTS and support-only/non-activation trace edges |
| `tests/test_phase_1546p_block5_sequence_lock_gap_refresh.py` | 4 | 2 | materialize Phase 1546p Block 5 sequence-lock TESTS and CDL-096/public-RC-gate trace edges |
| `tests/test_phase_1546p_idea_descent_rehearsal_sidecar.py` | 4 | 1 | materialize idea-descent sidecar TESTS, symbol coverage, local-only guard, and canonical trace invariants |
| `tests/test_phase_1549p_obl028_adaptive_fee_burn.py` | 4 | 2 | materialize OBL-028 adaptive-fee-burn spec/SIM TESTS and fixed-CDL-028 runtime boundary edges |
| `tests/test_phase_1550p_obl029_peer_funded_bounty.py` | 4 | 2 | materialize OBL-029 peer-funded bounty spec TESTS, CDL-047 boundary, and no-runtime/no-payout activation edges |
| `tests/test_phase_1552p_cdl096_prelock.py` | 4 | 2 | materialize CDL-096 prelock TESTS, Werner/global-tier constant traces, and runtime-not-authorized boundary edges |
| `tests/test_phase_1556_pre_rc_completion_gap_refresh.py` | 4 | 1 | materialize Phase 1556 pre-RC sequence/gap/census TESTS and public-path-blocked boundary edges |
| `tests/test_phase_1557_hb001_genesis_authority_assertion.py` | 5 | 2 | materialize HB-001 genesis authority assertion TESTS, schema/builder symbol coverage, and Genesis authority trace edges |
| `tests/test_phase_1558_hb003_layer0_truth_primitive_schemas.py` | 6 | 2 | materialize HB-003 Layer 0 schema embedding TESTS, CDL-073 trace, and private selftest classification |
| `tests/test_phase_1559_hb002_serving_receipt.py` | 7 | 1 | materialize HB-002 serving receipt TESTS, transport safety symbol coverage, and private no-live-call classification |
| `tests/test_phase_1560_agent_init_live.py` | 3 | 2 | materialize Phase 1560 live ceremony evidence TESTS and private evidence/non-public activation boundaries |
| `tests/test_phase_1560_genesis_serving_receiver.py` | 6 | 1 | materialize private serving receiver TESTS, helper symbol coverage, and no-public-activation classification |
| `tests/test_phase_1560_preflight_blocker.py` | 4 | 1 | materialize Phase 1560 preflight blocker TESTS and blocker/remediation/live-history trace edges |
| `tests/test_phase_1561_ecu_live_smoke.py` | 4 | 1 | materialize Phase 1561 ECU smoke evidence TESTS and no-settlement/no-ledger-write classification |
| `tests/test_phase_1561_fix1_balance_report_cli.py` | 3 | 1 | materialize Phase 1561-Fix1 balance CLI TESTS and smoke-report/no-ledger balance classification |
| `tests/test_phase_1562_invitation_provenance_chain.py` | 5 | 2 | materialize Phase 1562 invitation provenance TESTS, depth-one provenance edges, node6 boundary, and no-economics classification |
| `tests/test_phase_226_security_triage_artifacts.py` | 4 | 2 | materialize Phase 226 security triage TESTS and backlog/non-ratification classification edges |
| `tests/test_phase_236_preflight.py` | 2 | 1 | materialize Phase 236 preflight CLI TESTS and composed-gate classification edge |
| `tests/test_phase_396_cdl_v3_v7_governance_authorization_lock.py` | 3 | 3 | materialize Phase 396 governance authorization-lock TESTS edges and candidate CDL-V3/CDL-V7 dependency traces |
| `tests/test_phase_428_cdl_049_bounded_existential_alignment_ratification.py` | 5 | 2 | materialize Phase 428 CDL-049 ratification and bounded-existential runtime/documentation TESTS edges |
| `tests/test_phase_429_sim_009_pe_stabilization_commissioning.py` | 5 | 2 | materialize Phase 429 SIM-009 commissioning TESTS/EVIDENCES edges and sim-only non-ratification classification |
| `tests/test_phase_430_sim_009_results_synthesis_and_disposition.py` | 4 | 1 | materialize Phase 430 SIM-009 synthesis/disposition edges and non-lock-ready classification |
| `tests/test_phase_431_pe_stabilization_carry_forward_decision.py` | 4 | 1 | materialize Phase 431 P_e carry-forward decision edges and non-ratifying planning-anchor classification |
| `tests/test_phase_436_runtime_tranche_benchmark_harness_and_tranche_completion.py` | 4 | 1 | materialize Phase 436 runtime-baseline harness TESTS and frozen-source DERIVED_FROM edges |
| `tests/test_phase_437_runtime_tranche_findings_memo_and_regression_hardening.py` | 4 | 1 | materialize Phase 437 findings-memo TESTS and Phase 435/436 handoff DERIVED_FROM edges |
| `tests/test_phase_438_treasury_pe_prerequisite_satisfaction_review.py` | 4 | 1 | materialize Phase 438 Treasury P_e review TESTS and CDL-050 non-opening classification |
| `tests/test_phase_439_coherence_and_capsule_v1_8.py` | 5 | 1 | materialize Phase 439 coherence/capsule TESTS and prior-phase DERIVED_FROM edges |
| `tests/test_phase_446_consensus_runtime_iii_harness_integration.py` | 6 | 2 | materialize Phase 446 consensus runtime harness TESTS edges and CDL-051/classification traces |
| `tests/test_phase_447_consensus_adversarial_regression.py` | 5 | 3 | materialize Phase 447 consensus findings TESTS edges and adversarial-regression evidence trace |
| `tests/test_phase_448_coherence_and_capsule_v1_9.py` | 4 | 2 | materialize Phase 448 coherence/capsule TESTS and CDL-051 settlement trace |
| `tests/test_phase_450_window_sequence_lock_and_lane_identity_freeze.py` | 3 | 3 | materialize Phase 450 sequence-lock/lane-freeze TESTS and candidate CDL-050 lane trace |
| `tests/test_phase_452_l1_l2_prerequisite_disposition.py` | 2 | 3 | materialize Phase 452 L1/L2 disposition TESTS and ADR-0018/CDL-050 candidate traces |
| `tests/test_phase_454_sim_t_evidence_package.py` | 5 | 2 | materialize Phase 454 SIM-T evidence TESTS/EVIDENCES edges and sim-only classification |
| `tests/test_phase_455_sim_t_comparative_synthesis.py` | 5 | 2 | materialize Phase 455 SIM-T synthesis/ranking edges and no-opening classification |
| `tests/test_phase_456_cdl_050_blocker_clearance_gate.py` | 3 | 2 | materialize Phase 456 blocker-clearance gate TESTS and fail/no-opening classification |
| `tests/test_phase_456_fix_10_nonlinear_control_mechanism_implementation.py` | 4 | 2 | materialize Phase 456 Fix10 nonlinear-control simulation TESTS/EVIDENCES edges and no-execution classification |
| `tests/test_phase_456_fix_13_post_nonlinear_control_blocker_disposition_review.py` | 4 | 2 | materialize Phase 456 Fix13 blocker-disposition TESTS and remains-open classification |
| `tests/test_phase_456_fix_14_cdl_050_blocker_clearance_gate_rerun.py` | 4 | 2 | materialize Phase 456 Fix14 gate-rerun TESTS and pass/next-opening-path classification |
| `tests/test_phase_456_fix_2_recovery_rule_execution_and_blocker_1_reassessment.py` | 5 | 2 | materialize Phase 456 Fix2 recovery-rule evidence/synthesis TESTS edges and remains-open classification |
| `tests/test_phase_456_fix_3_recovery_rule_mechanism_implementation.py` | 4 | 2 | materialize Phase 456 Fix3 recovery-rule simulation-surface TESTS and no-execution classification |
| `tests/test_phase_456_fix_6_oscillator_mechanism_implementation.py` | 4 | 2 | materialize Phase 456 Fix6 oscillator simulation-surface TESTS and implemented/no-execution classification |
| `tests/test_phase_456_fix_8_oscillator_execution_and_blocker_1_reassessment.py` | 5 | 2 | materialize Phase 456 Fix8 oscillator execution/synthesis TESTS edges and blocker-cleared classification |
| `tests/test_phase_456_fix_9_post_oscillator_blocker_disposition_review.py` | 4 | 2 | materialize Phase 456 Fix9 post-oscillator disposition TESTS and rerun-admissible classification |
| `tests/test_phase_456_post_fix_5_blocker_disposition_review.py` | 4 | 2 | materialize Phase 456 post-Fix5 blocker-disposition TESTS and paused/failed-window classification |
| `tests/test_phase_456_waggle_dance_wide_field_surface.py` | 4 | 1 | materialize Waggle Dance wide-field simulation/research TESTS edges and support-only classification |
| `tests/test_phase_459_post1_waggle_oscillator_hybrid_intake_and_admissibility_lock.py` | 4 | 2 | materialize Phase 459 Post1 hybrid intake TESTS and future-scheduling/non-authority classification |
| `tests/test_phase_459_post2_waggle_oscillator_hybrid_contrast_field_attestation_and_brief_freeze.py` | 4 | 2 | materialize Phase 459 Post2 hybrid contrast TESTS and support/no-authority classification |
| `tests/test_phase_460_window_sequence_lock.py` | 2 | 2 | materialize Phase 460 sequence-lock TESTS and CDL-052 scope-freeze candidate trace |
| `tests/test_phase_461_adr_0021_epistemic_finality_claims.py` | 2 | 3 | materialize Phase 461 ADR-0021 boundary TESTS and no-CDL052-opening classification |
| `tests/test_phase_462_refutation_criterion_schema_specification.py` | 2 | 3 | materialize Phase 462 refutation-schema TESTS and deferred-runtime/no-opening classification |
| `tests/test_phase_467_tla_plus_cdl_051_shell_specification.py` | 3 | 2 | materialize Phase 467 TLA+ shell TESTS and CDL-051 spec-only trace |
| `tests/test_phase_470_consensus_diversity_floor_finality_runtime.py` | 4 | 2 | materialize Phase 470 diversity-aware finality runtime TESTS and candidate CDL-V3 IMPLEMENTS trace |
| `tests/test_phase_473_consensus_adversarial_hardening_and_findings.py` | 4 | 3 | materialize Phase 473 consensus findings TESTS/EVIDENCES and governance-priority classification |
| `tests/test_phase_475_window_sequence_lock.py` | 2 | 2 | materialize Phase 475 sequence-lock TESTS and CDL-052/genesis-validator-bootstrap window classification |
| `tests/test_phase_479_genesis_validator_bootstrap_specification.py` | 3 | 2 | materialize Phase 479 validator-bootstrap spec TESTS and CDL-042 identity trace |
| `tests/test_phase_483_coherence_and_capsule_v2_2.py` | 4 | 3 | materialize Phase 483 coherence/capsule TESTS and ADR-0022/CDL-052 boundary traces |
| `tests/test_phase_485_window_sequence_lock.py` | 2 | 3 | materialize Phase 485 sequence-lock TESTS and validator economics/staking lane candidate traces |
| `tests/test_phase_487_sim_010_validator_incentive_economics_execution_and_evidence.py` | 5 | 3 | materialize Phase 487 SIM-010 validator economics TESTS/EVIDENCES and follow-on authorization classification |
| `tests/test_phase_489_validator_economic_incentive_framework_opening_stub.py` | 4 | 2 | materialize Phase 489 CDL-054 opening TESTS and SIM-010 evidence-gate trace |
| `tests/test_phase_493_validator_staking_and_liveness_enforcement_prelock_hardening.py` | 2 | 2 | materialize Phase 493 CDL-055 prelock TESTS and liveness/equivocation boundary trace |
| `tests/test_phase_495_sequence_lock_and_cdl_055_disposition.py` | 2 | 3 | materialize Phase 495 sequence-lock TESTS and CDL-055/CDL-056 lane traces |
| `tests/test_phase_497_validator_trust_tier_governance_boundary_analysis.py` | 3 | 4 | materialize Phase 497 trust-tier boundary TESTS and CDL-056/CDL-V3/CDL-055 traces |
| `tests/test_phase_498_epoch_boundary_enforcement_architectural_scoping.py` | 3 | 1 | materialize Phase 498 epoch-boundary scoping TESTS and Window 505+ deferral classification |
| `tests/test_phase_499_validator_trust_tier_elevation_opening_stub.py` | 4 | 3 | materialize Phase 499 CDL-056 opening TESTS and evidence-gate traces |
| `tests/test_phase_503_coherence_report_and_capsule_v2_3.py` | 4 | 3 | materialize Phase 503 coherence/capsule TESTS and validator/ADR-0022 boundary traces |
| `tests/test_phase_508_epoch_boundary_cdl_vehicle_selection.py` | 3 | 3 | materialize Phase 508 vehicle-selection TESTS and candidate CDL-057/CDL-030 protection traces |
| `tests/test_phase_509_epoch_boundary_cdl_opening_stub.py` | 5 | 2 | materialize Phase 509 CDL-057 opening TESTS and provenance-scope/deferred-blocking classification |
| `tests/test_phase_515_sequence_lock_and_carry_forward_intake.py` | 2 | 2 | materialize Phase 515 sequence-lock TESTS and CDL-057 runtime/SIM-011 gate trace |
| `tests/test_phase_522_adr_0023_cdl_scoping_analysis.py` | 2 | 2 | materialize Phase 522 ADR-0023 scoping TESTS and no-CDL059-opening classification |
| `tests/test_phase_528_adr_0023_simulation_synthesis.py` | 3 | 2 | materialize Phase 528 ADR-0023 synthesis TESTS/EVIDENCES and CDL-059 non-opening classification |
| `tests/test_phase_533_coherence_report_and_capsule_v2_6.py` | 3 | 3 | materialize Phase 533 coherence/capsule TESTS and CDL-059/carry-forward traces |
| `tests/test_phase_551_passive_ecu_attribution_hardening.py` | 2 | 2 | materialize Phase 551 passive ECU runtime TESTS and candidate quality-signal implementation trace |
| `tests/test_phase_555_window_555_564_sequence_lock.py` | 2 | 3 | materialize Phase 555 sequence-lock TESTS and CDL-061/ADR-0023 transport traces |
| `tests/test_phase_556_adr_023_signal_floor_invariant.py` | 4 | 2 | materialize Phase 556 ADR-0023 invariant TESTS and ADM-only classification |
| `tests/test_phase_559_gossip_transport_hardening.py` | 3 | 3 | materialize Phase 559 gossip transport hardening TESTS and topology-privacy/hop-count traces |
| `tests/test_phase_563_coherence_report_and_capsule.py` | 3 | 3 | materialize Phase 563 coherence/capsule TESTS and CDL-061/ADR-0025 traces |
| `tests/test_phase_565_window_565_574_sequence_lock.py` | 2 | 3 | materialize Phase 565 sequence-lock TESTS and CDL-061/ADR-0025 transport traces |
| `tests/test_phase_566_transport_operationalization_boundary_lock.py` | 3 | 3 | materialize Phase 566 boundary-lock TESTS and explicit transport-kind traces |
| `tests/test_phase_575_window_575_584_sequence_lock.py` | 4 | 2 | materialize Phase 575 sequence-lock TESTS and RC0.1 no-public-release classification traces |
| `tests/test_phase_576_rc0_1_settlement_wallet_boundary_lock.py` | 3 | 2 | materialize Phase 576 wallet-boundary TESTS and read-only settlement classification |
| `tests/test_phase_577_rc0_1_persisted_graph_contract_lock.py` | 3 | 3 | materialize Phase 577 persisted-graph TESTS and quorum/provenance traces |
| `tests/test_phase_578_rc0_1_curated_genesis_bootstrap_lineage_lock.py` | 3 | 3 | materialize Phase 578 curated-lineage TESTS and compromise/identity-boundary traces |
| `tests/test_phase_581_settlement_wallet_query_integration.py` | 9 | 4 | materialize Phase 581 integration TESTS over settlement/wallet runtime and predecessor lock dependencies |
| `tests/test_phase_585_window_585_594_sequence_lock.py` | 3 | 3 | materialize Phase 585 public-release sequence-lock TESTS and Genesis-rooted lineage traces |
| `tests/test_phase_587_public_identity_activation_and_namespace_boundary_lock.py` | 4 | 4 | materialize Phase 587 public identity/namespace TESTS and CDL-001/CDL-040/CDL-042 traces |
| `tests/test_phase_588_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock.py` | 4 | 4 | materialize Phase 588 public quorum boundary TESTS and diversity/quorum/lineage traces |
| `tests/test_phase_589_settlement_linked_public_legitimacy_and_payout_traceability_lock.py` | 7 | 4 | materialize Phase 589 public settlement-legitimacy TESTS and receipt/promotion/validation traces |
| `tests/test_phase_590_genesis_authority_sunset_and_fork_legitimacy_coherence_lock.py` | 7 | 4 | materialize Phase 590 Genesis-sunset/fork-legitimacy TESTS and extraordinary-authority boundary traces |
| `tests/test_phase_591_public_runtime_integration_over_receipt_boundary.py` | 7 | 3 | materialize Phase 591 runtime-integration TESTS and bounded bridge classification |
| `tests/test_phase_595_rc0_1_strike_force_consolidation_and_runtime_hardening.py` | 5 | 4 | materialize Phase 595 checker/runner TESTS and bounded RC0.1 consolidation traces |
| `tests/test_phase_596_window_596_605_sequence_lock.py` | 4 | 3 | materialize Phase 596 sequence-lock TESTS and Genesis carry-forward closure traces |
| `tests/test_phase_597_genesis_governance_dilution_and_brake_semantics_closure.py` | 4 | 3 | materialize Phase 597 governance-dilution closure TESTS and CDL-013 traces |
| `tests/test_phase_598_freshness_gate_provenance_and_genesis_exemption_closure.py` | 5 | 3 | materialize Phase 598 freshness-closure TESTS and decay/reuse boundary traces |
| `tests/test_phase_601_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary.py` | 5 | 2 | materialize Phase 601 capability-lane TESTS and snapshot/provenance traces |
| `tests/test_phase_602_topological_exemption_boundary_and_public_tokenomics_statement.py` | 4 | 3 | materialize Phase 602 tokenomics-statement TESTS and topological-exemption boundary traces |
| `tests/test_phase_603_genesis_carry_forward_synthesis_and_readiness_delta_addendum.py` | 9 | 1 | materialize Phase 603 synthesis TESTS and six-artifact derived-from closure edges |
| `tests/test_phase_604_coherence_report_and_capsule_v3_2.py` | 5 | 1 | materialize Phase 604 coherence/capsule TESTS and Phase 605-only next-step classification |
| `tests/test_phase_606_mempalace_internal_retrieval_adoption.py` | 7 | 1 | materialize Phase 606 MemPalace retrieval-only TESTS and non-authority classification |
| `tests/test_phase_607_window_607_612_sequence_lock.py` | 4 | 3 | materialize Phase 607 settlement-substrate sequence-lock TESTS and reconciliation classification |
| `tests/test_phase_609_ecu_ilc_runtime_boundary_reconciliation.py` | 4 | 2 | materialize Phase 609 ECU/ILC layer-separation TESTS and substrate non-closure traces |
| `tests/test_phase_612_settlement_substrate_closure_and_mvp_gated_replan.py` | 4 | 2 | materialize Phase 612 closure handoff TESTS and MVP-gate/ADR-0028 traces |
| `tests/test_phase_613_window_613_619_sequence_lock.py` | 4 | 3 | materialize Phase 613 MVP spec-lane TESTS and post-612 priority traces |
| `tests/test_phase_620_window_620_622_sequence_lock.py` | 3 | 3 | materialize Phase 620 Agent Skills planning-lane TESTS and ADR-0024 deferral traces |
| `tests/test_phase_624_window_624_630_sequence_lock.py` | 3 | 4 | materialize Phase 624 CDL-063 sequence-lock TESTS and commission vehicle traces |
| `tests/test_phase_626_cdl_063_ecu_directed_commission_prelock.py` | 4 | 4 | materialize Phase 626 CDL-063 prelock/SIM TESTS and non-inflation traces |
| `tests/test_phase_630_window_624_630_coherence_and_closure.py` | 6 | 2 | materialize Phase 630 closure/coherence TESTS and CDL-063 consumed traces |
| `tests/test_phase_631_window_631_636_sequence_lock.py` | 6 | 2 | materialize Phase 631 Tier-0 exact-numeric sequence-lock TESTS and CDL-064 traces |
| `tests/test_phase_632_tier0_numeric_inventory_and_cdl_064_opening.py` | 8 | 2 | materialize Phase 632 numeric-inventory TESTS and CDL-064 opening traces |
| `tests/test_phase_635_tier0_exact_numeric_runtime_migration.py` | 5 | 2 | materialize Phase 635 exact-numeric runtime migration TESTS and CDL-064 consumed traces |
| `tests/test_phase_636_tier0_numeric_hardening_and_closure.py` | 5 | 2 | materialize Phase 636 numeric hardening/closure TESTS and exact numeric foundation traces |
| `tests/test_phase_637_window_637_641_sequence_lock.py` | 5 | 2 | materialize Phase 637 residual numeric sequence-lock TESTS and CDL-064 consumed traces |
| `tests/test_phase_641_residual_numeric_cleanup_and_closure.py` | 5 | 2 | materialize Phase 641 residual numeric closure TESTS and Window 623+ resumption traces |
| `tests/test_phase_642_window_642_648_sequence_lock.py` | 5 | 1 | materialize Phase 642 security strike-force sequence-lock TESTS and guardrail classification |
| `tests/test_phase_644_canonical_json_and_signature_boundary_hardening.py` | 5 | 1 | materialize Phase 644 canonical JSON/signature TESTS and machine-verifiable JSON guardrail traces |
| `tests/test_phase_647_security_hardening_gate_and_fix_induced_regression_audit.py` | 5 | 1 | materialize Phase 647 security gate TESTS and regression-audit traces |
| `tests/test_phase_648_window_642_648_closure_and_handoff.py` | 5 | 1 | materialize Phase 648 closure/handoff TESTS and security-window closure traces |
| `tests/test_phase_649_window_649_654_sequence_lock.py` | 4 | 2 | materialize Phase 649 public runtime lane TESTS and Window 623+ touchpoint traces |
| `tests/test_phase_651_public_receipt_runtime.py` | 6 | 2 | materialize Phase 651 public receipt runtime TESTS and receipt-schema/read-only traces |
| `tests/test_phase_653_public_wallet_runtime_integration.py` | 5 | 3 | materialize Phase 653 public wallet runtime TESTS plus read-only settlement-wallet authority traces |
| `tests/test_phase_654_window_649_654_closure_and_handoff.py` | 6 | 2 | materialize Phase 654 closure-gate TESTS and row-state closure traces |
| `tests/test_phase_655_window_655_658_sequence_lock.py` | 3 | 1 | materialize Phase 655 sequence-lock TESTS and maintenance-lane classification |
| `tests/test_phase_656_canon_export_and_registry_signature_reproducibility.py` | 6 | 1 | materialize Phase 656 signing reproducibility TESTS and deterministic timestamp invariant |
| `tests/test_phase_657_registry_channel_promotion_sync_reproducibility.py` | 7 | 1 | materialize Phase 657 registry helper TESTS and signed-identity boundary invariant |
| `tests/test_phase_658_window_655_658_hardening_and_handoff.py` | 5 | 2 | materialize Phase 658 closure-gate TESTS and signing/export lane closure traces |
| `tests/test_phase_659_window_659_664_sequence_lock.py` | 2 | 2 | materialize Phase 659 sequence-lock TESTS and CDL-065/row-6 scope traces |
| `tests/test_phase_662_cdl_065_opening_and_admissibility_matrix.py` | 4 | 2 | materialize Phase 662 CDL-065 opening and CDL-062 admissibility split TESTS |
| `tests/test_phase_665_window_665_670_sequence_lock.py` | 3 | 2 | materialize Phase 665 row-9 transport sequence-lock TESTS and static-registry maturity traces |
| `tests/test_phase_669_transport_hardening_and_maturity_decision.py` | 2 | 1 | materialize Phase 669 transport maturity decision TESTS and closure-candidate trace |
| `tests/test_phase_670_window_665_670_closure_and_handoff.py` | 6 | 2 | materialize Phase 670 closure TESTS and row-9 transport closure traces |
| `tests/test_phase_676_window_671_676_closure_and_handoff.py` | 9 | 2 | materialize Phase 676 rows-7/8 closure TESTS and criteria-lock authority traces |
| `tests/test_phase_677_window_677_682_sequence_lock.py` | 5 | 2 | materialize Phase 677 sequence-lock TESTS and row-5 privacy lane classification |
| `tests/test_phase_682_window_677_682_closure_and_handoff.py` | 10 | 2 | materialize Phase 682 row-5 privacy closure TESTS and partial-state traces |
| `tests/test_phase_697_row_5_mechanism_proof_mysticeti.py` | 4 | 2 | materialize Phase 697 Mysticeti row-5 proof TESTS and evidence trace |
| `tests/test_phase_698_row_7_tlc_evidence_mysticeti.py` | 5 | 2 | materialize Phase 698 row-7 TLC evidence TESTS and model-evidence traces |
| `tests/test_phase_699_row_8_mysticeti_sovereign_config.py` | 4 | 2 | materialize Phase 699 row-8 sovereign configuration TESTS and external-center exclusion trace |
| `tests/test_phase_700_coherence_capsule_v4_4_and_window_693_700_closure_gate.py` | 4 | 4 | materialize Phase 700 closure-gate TESTS and open-CDL carry-forward traces |
| `tests/test_phase_701_window_701_706_sequence_lock.py` | 3 | 2 | materialize Phase 701 sequence-lock TESTS and BAL calibration lane traces |
| `tests/test_phase_703_bal_profile_kernel_calibration_and_replay_contract.py` | 4 | 2 | materialize Phase 703 BAL calibration TESTS and unratified-default evidence trace |
| `tests/test_phase_704_post_banking_doctrine_lock.py` | 4 | 1 | materialize Phase 704 doctrine TESTS and doctrine-not-law classification trace |
| `tests/test_phase_705_inverted_ecu_runtime_traceability_and_doctrine_preservation.py` | 4 | 3 | materialize Phase 705 inverted-ECU TESTS and CDL-V1/CDL-048 traceability edges |
| `tests/test_phase_706_coherence_capsule_v4_5_and_window_701_706_closure_gate.py` | 4 | 2 | materialize Phase 706 closure TESTS and economic-doctrine lane traces |
| `tests/test_phase_707_window_707_712_sequence_lock.py` | 3 | 4 | materialize Phase 707 sequence-lock TESTS and open-CDL/ratification-boundary traces |
| `tests/test_phase_711_validator_sim_commissioning_and_cdl_039_scope_note.py` | 5 | 3 | materialize Phase 711 SIM commissioning TESTS and CDL-039 scope-note trace |
| `tests/test_phase_712_coherence_report_capsule_v4_6_and_window_707_712_closure_gate.py` | 4 | 3 | materialize Phase 712 closure TESTS and ratified-CDL carry-forward traces |
| `tests/test_phase_713_window_713_716_sequence_lock.py` | 3 | 3 | materialize Phase 713 sequence-lock TESTS and CDL-060/CDL-061 inherited-anchor traces |
| `tests/test_phase_714_adaptive_gossip_contract_and_law_vs_freedom_classification.py` | 3 | 3 | materialize Phase 714 adaptive-gossip TESTS and law/freedom classification traces |
| `tests/test_phase_715_partition_repair_benchmark_pack_and_missing_signal_doctrine.py` | 4 | 3 | materialize Phase 715 partition-repair TESTS and commissioning-only doctrine traces |
| `tests/test_phase_716_coherence_report_capsule_v4_7_and_window_713_716_closure_gate.py` | 4 | 3 | materialize Phase 716 closure TESTS and adaptive-gossip carry-forward traces |
| `tests/test_phase_717_window_717_722_sequence_lock.py` | 3 | 2 | materialize Phase 717 sequence-lock TESTS and ADR-0015 family scope traces |
| `tests/test_phase_718_adr_0015_inventory_and_scoping.py` | 3 | 3 | materialize Phase 718 ADR-0015 inventory TESTS and treasury/attribution boundary traces |
| `tests/test_phase_720_commons_dedication_and_leasehold_reversion_calibration.py` | 4 | 3 | materialize Phase 720 commons/leasehold TESTS and CDL-047/ADR-0015 traces |
| `tests/test_phase_722_coherence_report_capsule_v4_8_and_window_717_722_closure_gate.py` | 4 | 2 | materialize Phase 722 closure TESTS and final ADR-0015 family disposition traces |
| `tests/test_phase_723_window_723_726_sequence_lock.py` | 3 | 3 | materialize Phase 723 sequence-lock TESTS and financial-shard separation traces |
| `tests/test_phase_724_financial_shard_eligibility_prefilter_and_lane_separation.py` | 3 | 3 | materialize Phase 724 prefilter TESTS and financial-shard separation traces |
| `tests/test_phase_726_coherence_report_capsule_v4_9_and_window_723_726_closure_gate.py` | 4 | 2 | materialize Phase 726 closure TESTS and financial-shard no-activation traces |
| `tests/test_phase_727_window_727_732_sequence_lock.py` | 3 | 3 | materialize Phase 727 sequence-lock TESTS and adjacent-gated-economy separation traces |
| `tests/test_phase_732_capsule_v5_0_and_window_727_732_closure_gate.py` | 5 | 2 | materialize Phase 732 frontier/capsule TESTS and post-732 planning traces |
| `tests/test_phase_733_window_733_738_sequence_lock.py` | 3 | 3 | materialize Phase 733 sequence-lock TESTS and CDL-017/CDL-068 prelock traces |
| `tests/test_phase_734_sim_validator_01_results.py` | 5 | 2 | materialize Phase 734 SIM-VALIDATOR result TESTS and CDL-017 evidence trace |
| `tests/test_phase_735_sim_topology_01_results.py` | 5 | 2 | materialize Phase 735 SIM-TOPOLOGY result TESTS and CDL-068 evidence trace |
| `tests/test_phase_736_cdl_068_opening.py` | 4 | 3 | materialize Phase 736 CDL-068 opening TESTS and boundary traces |
| `tests/test_phase_737_cdl_017_prelock_evidence_and_adr_0019_disposition.py` | 5 | 3 | materialize Phase 737 prelock/ADR-0019 TESTS and evidence traces |
| `tests/test_phase_738_window_733_738_closure_gate.py` | 5 | 2 | materialize Phase 738 closure TESTS and CDL-017 prelock completion traces |
| `tests/test_phase_739_window_739_744_sequence_lock.py` | 4 | 3 | materialize Phase 739 sequence-lock TESTS and CDL-068/rows-5-7 boundary traces |
| `tests/test_phase_745_window_745_748_sequence_lock.py` | 3 | 3 | materialize Phase 745 sequence-lock TESTS and convergence/ADR-0031 boundary traces |
| `tests/test_phase_749_window_749_752_sequence_lock.py` | 4 | 2 | materialize Phase 749 sequence-lock TESTS and planning-consolidation boundary traces |
| `tests/test_phase_750_master_completion_roadmap_and_m_series_lane_update.py` | 4 | 2 | materialize Phase 750 roadmap/M-series TESTS and planning route traces |
| `tests/test_phase_751_stale_planning_doc_archival_and_planning_index_advance.py` | 6 | 2 | materialize Phase 751 archival/index TESTS and successor-planning traces |
| `tests/test_phase_755_cdl_017_ratification_readiness_dossier.py` | 3 | 2 | materialize Phase 755 CDL-017 readiness TESTS and prework-only boundary trace |
| `tests/test_phase_764_cdl_017_interaction_synthesis_and_activation_boundary_record.py` | 4 | 4 | materialize Phase 764 activation-boundary TESTS and CDL carry-forward traces |
| `tests/test_phase_765_cdl_017_ratification_evidence.py` | 4 | 3 | materialize Phase 765 ratification TESTS and CDL-017 single-row mutation trace |
| `tests/test_phase_768_sec_004_acceptance.py` | 3 | 3 | materialize Phase 768 Rust runtime TESTS and SEC-004 acceptance trace |
| `tests/test_phase_769_m007_hook_activation.py` | 2 | 2 | materialize Phase 769 Rust validator hook TESTS and CDL-017 activation trace |
| `tests/test_phase_770_codex_audit.py` | 5 | 3 | materialize Phase 770 audit TESTS and runtime-evidence traces |
| `tests/test_phase_771_lane_doc_update.py` | 2 | 2 | materialize Phase 771 lane-doc TESTS and post-M-022 activation record trace |
| `tests/test_phase_773_coherence_and_capsule.py` | 3 | 2 | materialize Phase 773 coherence/capsule TESTS and non-conflation traces |
| `tests/test_phase_776_layer1_log_hygiene.py` | 3 | 1 | materialize Phase 776 log-hygiene TESTS and redaction-policy trace |
| `tests/test_phase_777_sim_run1.py` | 3 | 2 | materialize Phase 777 SIM result TESTS and row-5 privacy evidence trace |
| `tests/test_phase_779_sim_run2.py` | 3 | 3 | materialize Phase 779 SIM run-2 TESTS and row-5 privacy evidence traces |
| `tests/test_phase_780_row5_evaluation.py` | 2 | 3 | materialize Phase 780 row-5 evaluation TESTS and honest-nonclosure trace |
| `tests/test_phase_781_coherence_and_capsule.py` | 3 | 2 | materialize Phase 781 coherence/capsule TESTS and row-5 nonclosure carry-forward trace |
| `tests/test_phase_813_checklist_v0_2.py` | 2 | 2 | materialize Phase 813 checklist TESTS and Option B state trace |
| `tests/test_phase_830_settlement_path_gate.py` | 5 | 2 | materialize Phase 830 settlement-gate runtime TESTS and predeployment boundary trace |
| `tests/test_phase_831_row5_b_impl_obligations_1_3.py` | 3 | 2 | materialize Phase 831 privacy-lane runtime TESTS and row-5 B-Impl obligation trace |
| `tests/test_phase_832_row5_b_impl_obligations_4_5.py` | 4 | 2 | materialize Phase 832 monitor/notification TESTS and row-5 B-Impl obligation trace |
| `tests/test_phase_833_row5_b_impl_obligation_6_sim_leakage_03.py` | 4 | 2 | materialize Phase 833 leakage-metrics TESTS and SIM-LEAKAGE-03 instrumentation trace |
| `tests/test_phase_834_row5_b_impl_strike_force_closure_gate.py` | 6 | 2 | materialize Phase 834 closure-gate TESTS and honest-nonclosure boundary traces |
| `tests/test_phase_835_settlement_gate_preflight.py` | 4 | 2 | materialize Phase 835 preflight-tool TESTS and settlement-gate dry-run trace |
| `tests/test_phase_836_first_validator_entry_conditions_check.py` | 3 | 3 | materialize Phase 836 entry-condition harness TESTS and operator-boundary trace |
| `tests/test_phase_837_track1_coherence_and_capsule.py` | 3 | 2 | materialize Phase 837 coherence/capsule TESTS and first-validator gate boundary trace |
| `tests/test_phase_838a_genesis_agent1_keygen.py` | 3 | 3 | materialize Phase 838a keygen TESTS and CDL-069 public-record boundary trace |
| `tests/test_phase_838b_sphincs_shamir_split.py` | 4 | 2 | materialize Phase 838b Shamir wrapper/binary TESTS and CDL-069 recovery trace |
| `tests/test_phase_838c_epoch_endorsement_runtime.py` | 2 | 2 | materialize Phase 838c epoch endorsement runtime TESTS and CDL-069 trace |
| `tests/test_phase_838d_agent_id_runtime_v2.py` | 2 | 3 | materialize Phase 838d agent-id runtime TESTS and CDL-069/CDL-042 compatibility trace |
| `tests/test_phase_838e_genesis_record_schema.py` | 2 | 2 | materialize Phase 838e genesis-record schema TESTS and CDL-069 trace |
| `tests/test_phase_838f_endorsement_packet_schema.py` | 2 | 2 | materialize Phase 838f endorsement-packet schema TESTS and CDL-069 trace |
| `tests/test_phase_844_row5_rust_routing_instrumentation.py` | 3 | 3 | materialize Phase 844 Rust routing instrumentation TESTS and row-5 trace |
| `tests/test_phase_845_sim_leakage_03_live_run.py` | 4 | 3 | materialize Phase 845 live SIM evidence TESTS and row-5 honest nonclosure trace |
| `tests/test_phase_846_cdl_072_bound_b_and_row5_closure.py` | 5 | 3 | materialize Phase 846 CDL-072 and Row-5 closure TESTS with ratification trace |
| `tests/test_phase_847_window_844_847_closure_gate.py` | 5 | 2 | materialize Phase 847 closure-gate TESTS and row5/CDL-072 carry-forward trace |
| `tests/test_phase_849_graduation_checklist_v0_3.py` | 3 | 3 | materialize Phase 849 checklist TESTS and Option B graduation trace |
| `tests/test_phase_850_851_cdl_071_temporal_tier.py` | 3 | 3 | materialize Phase 850-851 CDL-071 TESTS and temporal-tier authority trace |
| `tests/test_phase_852_window_848_852_closure_gate.py` | 4 | 3 | materialize Phase 852 closure-gate TESTS and checklist/CDL-071 carry-forward trace |
| `tests/test_phase_858_hb_001_genesis_assertion_schema.py` | 3 | 2 | materialize Phase 858 HB-001 runtime TESTS and CDL-073 trace |
| `tests/test_phase_859_hb_003_layer_0_bundle_schema_section.py` | 2 | 2 | materialize Phase 859 HB-003 schema TESTS and CDL-073 trace |
| `tests/test_phase_865_872_cdl_074_truth_primitive_runtime.py` | 4 | 4 | materialize Phase 865-872 truth primitive runtime TESTS and CDL-074/CDL-073/CDL-052 traces |
| `tests/test_phase_879_886_truth_primitive_graph_store.py` | 4 | 3 | materialize Phase 879-886 graph-store TESTS and CDL-075 persistence trace |
| `tests/test_phase_888_891_query_truth_cli.py` | 4 | 2 | materialize Phase 888-891 query CLI TESTS and CDL-075 read-path trace |
| `tests/test_phase_921_929_cdl_080_star_map.py` | 3 | 3 | materialize Phase 921-929 star-map TESTS and CDL-080/ADR-0033 traces |
| `tests/test_phase_932_933_h013_spectral_beacon.py` | 4 | 3 | materialize Phase 932-933 H013 spectral beacon TESTS and crypto-surface trace |
| `tests/test_phase_942_cdl_081_hyperedge_ecu_attribution.py` | 4 | 3 | materialize Phase 942 CDL-081 attribution TESTS and SIM-REUSE evidence trace |
| `tests/test_phase_M009_mysticeti_testnet_setup.py` | 4 | 2 | materialize M-009 setup TESTS and testnet-only trace |
| `tests/test_phase_M012_full_bft_transfer.py` | 4 | 2 | materialize M-012 BFT transfer TESTS and Mysticeti testnet trace |
| `tests/test_phase_M013_workload_a_results.py` | 3 | 2 | materialize M-013 workload evidence TESTS and Mysticeti trace |
| `tests/test_phase_M014_workload_b_results.py` | 3 | 2 | materialize M-014 workload evidence TESTS and censorship-resistance trace |
| `tests/test_phase_M015_workload_c_results.py` | 5 | 3 | materialize M-015 workload recovery TESTS and SEC-008 trace |
| `tests/test_phase_M016_workload_d_results.py` | 5 | 3 | materialize M-016 replayability TESTS and row-7/state-extraction trace |
| `tests/test_phase_M017_workload_e_results.py` | 4 | 2 | materialize M-017 operability TESTS and workload E trace |
| `tests/test_phase_M018_workload_f_results.py` | 4 | 4 | materialize M-018 auditability TESTS and SEC-009/ADR-0031 trace |
| `tests/test_phase_M019_adversarial_hardening_results.py` | 4 | 4 | materialize M-019 adversarial hardening TESTS and safety/liveness trace |
| `tests/test_phase_commit_manifest_296.py` | 3 | 2 | materialize Phase 296 commit-manifest resolver TESTS and phase-history trace |
| `tests/test_phase_high002_phase_b_closure_gate.py` | 5 | 3 | materialize HIGH-002 closure TESTS and quorum/safety trace |
| `tests/test_problem_space_kpis.py` | 4 | 0 | materialize problem-space KPI runtime TESTS without authority promotion |
| `tests/test_protocol_event_export.py` | 3 | 0 | materialize protocol event export runtime TESTS without authority promotion |
| `tests/test_protocol_event_log.py` | 4 | 0 | materialize protocol event log runtime TESTS without authority promotion |
| `tests/test_protocol_params.py` | 6 | 0 | materialize ProtocolParams runtime TESTS without authority promotion |
| `tests/test_public_rc_drift_reconciliation_successor_manifest_plan.py` | 4 | 3 | materialize public RC drift reconciliation TESTS and successor-manifest route trace |
| `tests/test_public_rc_general_go_live_forward_plan.py` | 3 | 3 | materialize public RC go-live forward-plan TESTS and no-activation gate trace |
| `tests/test_public_rc_package_profiles.py` | 4 | 3 | materialize public RC package profile TESTS and profile-contract trace |
| `tests/test_quickstart_parity_phase_998.py` | 4 | 2 | materialize Phase 998 quickstart parity TESTS and docs-accuracy trace |
| `tests/test_ratification_sequence_250.py` | 3 | 2 | materialize Phase 250 sequence-lock TESTS and ratification-protocol trace |
| `tests/test_ratification_sequence_270.py` | 4 | 2 | materialize Phase 270 sequence-lock TESTS and dependency-ordering trace |
| `tests/test_rc0_1_benchmark_runner.py` | 3 | 0 | materialize RC benchmark runner support TESTS without authority promotion |
| `tests/test_rc_dredge_stack_tools.py` | 4 | 0 | materialize RC dredge support-tool TESTS without authority promotion |
| `tests/test_refutation_profitability_invariant_gate_phase_212.py` | 4 | 2 | materialize Phase 212 gate-script TESTS and invariant-gate trace |
| `tests/test_refutation_profitability_invariant_phase_212.py` | 5 | 2 | materialize Phase 212 refutation-profitability runtime TESTS and economic-invariant trace |
| `tests/test_release_readiness_package_238.py` | 3 | 2 | materialize Phase 238 release-readiness TESTS and carry-forward trace |
| `tests/test_replay_proof_schema_parity.py` | 6 | 0 | materialize replay-proof schema parity TESTS without authority promotion |
| `tests/test_reuse_diversity_invariants_gate_phase_216.py` | 4 | 3 | materialize Phase 216 reuse-diversity gate TESTS and anti-Sybil invariant trace |
| `tests/test_reuse_diversity_invariants_phase_216.py` | 5 | 3 | materialize Phase 216 reuse-diversity runtime TESTS and anti-Sybil invariant trace |
| `tests/test_reward_loop.py` | 5 | 0 | materialize early reward-loop runtime TESTS without authority promotion |
| `tests/test_rl_bandit_sim.py` | 3 | 0 | materialize RL bandit simulation TESTS as support-only evidence |
| `tests/test_routed_tasks_export.py` | 4 | 0 | materialize routed-task export runtime TESTS without authority promotion |
| `tests/test_runtime_logging_closure_gate.py` | 5 | 2 | materialize runtime logging closure-gate TESTS and closure trace |
| `tests/test_security_ratification_gate_252.py` | 5 | 4 | materialize Phase 252 security ratification gate TESTS and security-CDL trace |
| `tests/test_security_runtime_closure_gate_phase_249.py` | 4 | 5 | materialize Phase 249 security closure TESTS and window-handoff trace |
| `tests/test_security_runtime_cross_cdl_interactions_244.py` | 4 | 4 | materialize Phase 244 security runtime TESTS and cross-CDL trace |
| `tests/test_security_runtime_implementation_plan_232.py` | 3 | 5 | materialize Phase 232 security implementation-plan TESTS and planning-lock trace |
| `tests/test_security_runtime_sequence_240.py` | 2 | 5 | materialize Phase 240 security sequence TESTS and sequence-lock trace |
| `tests/test_sensitive_runtime_coding_taboos.py` | 3 | 0 | materialize sensitive-runtime taboo guardrail TESTS as support-only evidence |
| `tests/test_server_app_factory_phase_1001.py` | 5 | 2 | materialize Phase 1001 app-factory TESTS and server import-side-effect trace |
| `tests/test_server_instance_isolation_phase_199.py` | 4 | 2 | materialize Phase 199 server isolation TESTS and app-state trace |
| `tests/test_server_lifecycle_phase_198.py` | 4 | 2 | materialize Phase 198 server lifecycle TESTS and app-state boundary trace |
| `tests/test_settlement_metrics.py` | 5 | 0 | materialize settlement metrics runtime TESTS without authority promotion |
| `tests/test_settlement_stability.py` | 4 | 0 | materialize settlement stability runtime TESTS without authority promotion |
| `tests/test_settlement_verification.py` | 4 | 0 | materialize settlement verification runtime TESTS without authority promotion |
| `tests/test_sidecar_ccss_cli_public_ux.py` | 7 | 0 | materialize CCSS sidecar CLI TESTS as local-bootstrap support evidence |
| `tests/test_sidecar_query_completeness_1379.py` | 7 | 2 | materialize ADR-0031 sidecar query TESTS and no-authority trace |
| `tests/test_signing_provider_interface_262.py` | 5 | 3 | materialize Phase 262 signing-provider document TESTS and privacy-boundary trace |
| `tests/test_silent_exception_logging_guardrail.py` | 6 | 0 | materialize silent-exception logging guardrail TESTS as support-only evidence |
| `tests/test_sim_closed_loop_backlog_control.py` | 4 | 0 | materialize closed-loop backlog simulation TESTS as support-only evidence |
| `tests/test_sim_embed_01_results.py` | 5 | 2 | materialize SIM-EMBED-01 evidence TESTS and ADR-0030 evidence-boundary trace |
| `tests/test_sim_harnesses.py` | 4 | 0 | materialize SIM harness normalization TESTS without authority promotion |
| `tests/test_sim_leakage_02_autoresearch.py` | 3 | 1 | materialize SIM-LEAKAGE-02 AutoResearch evidence TESTS as research-only support |
| `tests/test_sim_routing_01_results.py` | 5 | 1 | materialize SIM-ROUTING-01 evidence TESTS as bounded research support |
| `tests/test_stress_response_kpis.py` | 5 | 0 | materialize stress-response KPI runtime TESTS without authority promotion |
| `tests/test_task_primitive.py` | 3 | 0 | materialize task primitive TESTS without authority promotion |
| `tests/test_task_queue.py` | 4 | 0 | materialize TaskQueue runtime TESTS without authority promotion |
| `tests/test_task_queue_reward_flow.py` | 4 | 0 | materialize task queue reward-flow simulation TESTS without authority promotion |
| `tests/test_task_routing_suggestions.py` | 7 | 0 | materialize task routing runtime TESTS without authority promotion |
| `tests/test_telemetry_rlhook.py` | 6 | 0 | materialize economic telemetry TESTS without authority promotion |
| `tests/test_track1_closure_guardrail_gate_ops.py` | 7 | 3 | materialize Track-1 guardrail gate TESTS with candidate policy traces |
| `tests/test_utility_flow_rewards_phase_208.py` | 5 | 3 | materialize utility-flow reward TESTS with candidate Phase 208 policy traces |
| `tests/test_validate_phase_prompt_alpha_subphase.py` | 4 | 2 | materialize alpha-subphase prompt validator TESTS with candidate prompt-schema traces |
| `tests/test_window_1257_1264_prompt_drafts.py` | 4 | 3 | materialize Window 1257-1264 prompt package TESTS with candidate window policy traces |
| `tests/test_window_1265_1272_prompt_drafts.py` | 4 | 3 | materialize Window 1265-1272 prompt package TESTS with candidate window policy traces |
| `tests/test_window_1273_1280_prompt_drafts.py` | 4 | 3 | materialize Window 1273-1280 prompt package TESTS with candidate window policy traces |
| `tests/test_window_1289_1302_prompt_drafts.py` | 4 | 4 | materialize Window 1289-1302 prompt package TESTS with candidate window policy traces |
| `tests/test_window_1303_1316_deep_code_audit_hardening.py` | 5 | 2 | materialize Window 1303-1316 audit hardening TESTS with candidate guardrail traces |
| `tests/test_window_1303_1316_prompt_drafts.py` | 4 | 3 | materialize Window 1303-1316 prompt package TESTS with candidate window policy traces |
| `tests/test_window_1317_1329_prompt_drafts.py` | 4 | 4 | materialize Window 1317-1329 prompt package TESTS with candidate release/CCSS policy traces |
| `tests/test_window_1330_1342_prompt_drafts.py` | 4 | 4 | materialize Window 1330-1342 prompt package TESTS with candidate high-authority gate traces |
| `tests/test_window_1343_1368_prompt_drafts.py` | 4 | 5 | materialize Window 1343-1368 prompt package TESTS with candidate issuance/CDL traces |
| `tests/test_window_1369_1390_public_economics_gap_planning.py` | 4 | 3 | materialize public-economics gap planning TESTS with candidate firewall traces |
| `tests/test_window_545_554_audit_regressions.py` | 3 | 2 | materialize Window 545-554 runtime audit TESTS with candidate guardrail traces |
| `tests/test_window_555_560_transport_audit_regressions.py` | 5 | 2 | materialize Window 555-560 transport audit TESTS with candidate guardrail traces |
| `tests/test_window_555_562_peer_registry_audit_regressions.py` | 2 | 2 | materialize Window 555-562 peer registry audit TESTS with candidate guardrail traces |
| `tests/test_window_767_774_closure_gate.py` | 8 | 4 | materialize Window 767-774 closure gate TESTS with candidate closure/activation traces |
| `tests/test_window_767_774_integration_gate_772.py` | 4 | 3 | materialize Window 767-774 integration gate TESTS with candidate activation-boundary traces |
| `tests/test_window_775_782_closure_gate.py` | 9 | 3 | materialize Window 775-782 closure gate TESTS with candidate Row-5 privacy traces |
| `tests/test_window_811_822_option_b_selection_and_pre_rc_hardening.py` | 7 | 3 | materialize Window 811-822 Option B hardening TESTS with candidate ADR/policy traces |
| `tests/test_window_823_829_sequence_lock.py` | 6 | 4 | materialize Window 823-829 sequence-lock TESTS with candidate CDL-017 and gate traces |
| `tests/test_window_b_scope_b1_b4_holdpoint.py` | 8 | 2 | materialize Row-5 B1-B4 holdpoint TESTS with candidate research-policy traces |
| `tests/test_window_b_scope_b5_lock_and_commissioning.py` | 7 | 3 | materialize Row-5 B5 lock and commissioning TESTS with candidate mechanism-lock traces |

## Non-Authority Boundary

Manual annotations are review-queue records, not canonical graph edges.
This report does not grant authority, activation, eligibility, claimability, governance effect, or economic effect.
The enriched graph input remains unsigned support-only and not canonical.

No canonical graph mutation, edge promotion, signing, upload, publication, runtime activation, sidecar activation, ADR mutation, or CDL mutation occurred.

## Output Tokens

- `graph_derived_test_frontier_report_committed_phase_1545p_fix38`
- `test_frontier_gap_categories_recorded_phase_1545p_fix38`
- `test_evidence_frontier_compared_phase_1545p_fix38`
- `manual_test_connectivity_annotations_recorded_phase_1545p_fix38`
- `stale_and_gated_test_frontier_recorded_phase_1545p_fix38`
- `test_frontier_report_no_authority_overclaim_phase_1545p_fix38`
- `public_path_remains_blocked_phase_1545p_fix38`
