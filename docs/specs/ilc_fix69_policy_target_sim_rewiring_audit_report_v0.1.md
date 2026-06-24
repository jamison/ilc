# Fix69 Policy, Target, and Sim Rewiring Audit Report v0.1

PUBLIC_RC_EXCLUDE: local unsigned Atlas LMDB maintenance report.

## Summary

- Phase: `phase_1545p_fix69`
- LMDB: `out/genesis_base_graph_v0.4_unified.lmdb`
- Pre-repair orphan counts: policy=267, target=786, sim=39
- Post-repair orphan counts: policy=93, target=786, sim=0
- Safe-writer status: `PASS`
- Support phase nodes added: 127
- Semantic edges accepted: 213
- Phase-lineage hygiene edges accepted: 14
- Rejected edges: 0
- Skipped duplicate edges: 0
- Projected dangling edges: 0

## Edge-Type Breakdown

{
  "CARRIES_FORWARD": 207,
  "EVIDENCES": 5,
  "REFERENCES_AUTHORITY": 1
}

## Disposition Breakdown

{
  "edge_added": 213,
  "support_only_unresolved": 93,
  "tier1_build_critical_review_required": 383,
  "tier2_support_leaf_no_wiring_required": 403
}

## Applied Edge Records

| candidate_id | track | disposition | edge_type | target | evidence | reason |
|---|---|---|---|---|---|---|
| `policy:agpl_license_header_audit_complete_phase_1443` | policy | edge_added | CARRIES_FORWARD | `phase:1443` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:anti_capture_diversity_verified_phase_1419` | policy | edge_added | CARRIES_FORWARD | `phase:1419` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:atlas_atoms_not_promoted_phase_1545p_fix26` | policy | edge_added | CARRIES_FORWARD | `phase:1545p_fix26` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:atlas_optimized_candidate_not_signed_phase_1545p_fix30` | policy | edge_added | CARRIES_FORWARD | `phase:1545p_fix30` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:atlas_rewrite_candidates_not_promoted_phase_1545p_fix27` | policy | edge_added | CARRIES_FORWARD | `phase:1545p_fix27` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:atlas_signing_gate_not_reached_phase_1545p_fix24` | policy | edge_added | CARRIES_FORWARD | `phase:1545p_fix24` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:block4b_runtime_paths_not_activated_phase_1543p` | policy | edge_added | CARRIES_FORWARD | `phase:1543p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:cdl062_unopened_optionb_selection_deferred` | policy | edge_added | REFERENCES_AUTHORITY | `cdl:062_sovereign_substrate_research_lane` | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | policy_candidate_id_embeds_existing_cdl_token |
| `policy:cla_governance_policy_committed_phase_1444` | policy | edge_added | CARRIES_FORWARD | `phase:1444` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:co_attestation_receipt_private_fixture_phase_1464p` | policy | edge_added | CARRIES_FORWARD | `phase:1464p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:consent_gate_local_write_private_phase_1485p` | policy | edge_added | CARRIES_FORWARD | `phase:1485p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:directed_view_not_yet_contractualized_gap_phase_1545p_fix25` | policy | edge_added | CARRIES_FORWARD | `phase:1545p_fix25` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:dynamic_ranking_multiplier_not_activated_phase_1502p` | policy | edge_added | CARRIES_FORWARD | `phase:1502p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:ejected_stake_distribution_not_activated_phase_1541p` | policy | edge_added | CARRIES_FORWARD | `phase:1541p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:fee_burn_runtime_unchanged_phase_1549p` | policy | edge_added | CARRIES_FORWARD | `phase:1549p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:gap_13_closure_verdict_pass_phase_1441` | policy | edge_added | CARRIES_FORWARD | `phase:1441` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:gap_7_cla_milestone_complete_phase_1444` | policy | edge_added | CARRIES_FORWARD | `phase:1444` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:gap_7_not_fully_closed_phase_1445` | policy | edge_added | CARRIES_FORWARD | `phase:1445` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:gap_7_partially_closed_phase_1445` | policy | edge_added | CARRIES_FORWARD | `phase:1445` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:governance_config_mvp_runtime_contract` | policy | edge_added | CARRIES_FORWARD | `phase:983_typed_return_contract_rollout_ledger_config_foundation` | `docs/specs/ilc_fix41a_authority_trace_frontier_report_v0.1.md` | known_policy_phase_anchor_from_fix41a_manual_read_report |
| `policy:governance_dynamic_pricing_runtime` | policy | edge_added | CARRIES_FORWARD | `phase:983_typed_return_contract_rollout_ledger_config_foundation` | `docs/specs/ilc_fix41a_authority_trace_frontier_report_v0.1.md` | known_policy_phase_anchor_from_fix41a_manual_read_report |
| `policy:governance_engine_mvp_config_pricing` | policy | edge_added | CARRIES_FORWARD | `phase:983_typed_return_contract_rollout_ledger_config_foundation` | `docs/specs/ilc_fix41a_authority_trace_frontier_report_v0.1.md` | known_policy_phase_anchor_from_fix41a_manual_read_report |
| `policy:h11_reputation_governance_weight_float_kill_phase_1357` | policy | edge_added | CARRIES_FORWARD | `phase:1357` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:harness_kernel_integration_private_not_activated_phase_1477p` | policy | edge_added | CARRIES_FORWARD | `phase:1477p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:historical_phase_snapshot_tests_default_off_phase_1545p_fix2` | policy | edge_added | CARRIES_FORWARD | `phase:1545p_fix2` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:homoiconic_test_graph_checker_report_only_phase_1545p_fix33` | policy | edge_added | CARRIES_FORWARD | `phase:1545p_fix33` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:human_risk_authorization_relying_on_fedex_delivery_pending_uspto_receipts_phase_1545p_fix5` | policy | edge_added | CARRIES_FORWARD | `phase:1545p_fix5` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:idle_capacity_scheduler_not_activated_phase_1462p` | policy | edge_added | CARRIES_FORWARD | `phase:1462p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:issuance_economics_integration_gate_phase_1352` | policy | edge_added | CARRIES_FORWARD | `phase:1352` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:j008_pre_gate_verification_phase_1425` | policy | edge_added | CARRIES_FORWARD | `phase:1425` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:j008_vrf_verifier_not_implemented_phase_1410` | policy | edge_added | CARRIES_FORWARD | `phase:1410` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:local_immutable_store_not_production_phase_1485p` | policy | edge_added | CARRIES_FORWARD | `phase:1485p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:local_node_capture_private_consent_gate_phase_1461p` | policy | edge_added | CARRIES_FORWARD | `phase:1461p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:multi_operator_mysticeti_testnet_phase_1360` | policy | edge_added | CARRIES_FORWARD | `phase:1360` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:peer_funded_bounty_runtime_not_activated_phase_1550p` | policy | edge_added | CARRIES_FORWARD | `phase:1550p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase1001_server_app_factory_import_side_effect_boundary` | policy | edge_added | CARRIES_FORWARD | `phase:1001` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase1516p_private_runtime_selftest` | policy | edge_added | CARRIES_FORWARD | `phase:1516p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase1517p_private_runtime_selftest` | policy | edge_added | CARRIES_FORWARD | `phase:1517p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase1518p_private_runtime_selftest` | policy | edge_added | CARRIES_FORWARD | `phase:1518p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase1573_signing_input_requires_human_scope_selection_phase_1545p_fix31` | policy | edge_added | CARRIES_FORWARD | `phase:1545p_fix31` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase171_runtime_logging_hardening_closure` | policy | edge_added | CARRIES_FORWARD | `phase:171` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase198_server_lifecycle_app_state_boundary` | policy | edge_added | CARRIES_FORWARD | `phase:198` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase199_server_instance_state_isolation` | policy | edge_added | CARRIES_FORWARD | `phase:199` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase208_utility_flow_reward_governor` | policy | edge_added | CARRIES_FORWARD | `phase:208` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase212_refutation_profitability_invariant_gate` | policy | edge_added | CARRIES_FORWARD | `phase:212_refutation_profitability_invariant` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase216_reuse_diversity_anti_sybil_contract` | policy | edge_added | CARRIES_FORWARD | `phase:216` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase216_reuse_diversity_invariant_gate` | policy | edge_added | CARRIES_FORWARD | `phase:216` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase226_decision_log_backlog_not_entered_into_ratified_register` | policy | edge_added | CARRIES_FORWARD | `phase:226` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase236_composed_preflight_gate` | policy | edge_added | CARRIES_FORWARD | `phase:236` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase250_259_sequence_lock_no_runtime_mutation` | policy | edge_added | CARRIES_FORWARD | `phase:250` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase262_signing_provider_interface` | policy | edge_added | CARRIES_FORWARD | `phase:262` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase270_279_cdl_dependency_ordering_no_mutation` | policy | edge_added | CARRIES_FORWARD | `phase:270` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase270_279_issuance_governance_closure_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:270` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase296_commit_manifest_resolver_hardening` | policy | edge_added | CARRIES_FORWARD | `phase:296` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase429_sim009_non_ratifying_no_decision_log_no_runtime_mutation` | policy | edge_added | CARRIES_FORWARD | `phase:429` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase430_sim009_insufficient_for_constitutional_lock` | policy | edge_added | CARRIES_FORWARD | `phase:430` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase431_non_ratifying_pe_stabilization_carry_forward` | policy | edge_added | CARRIES_FORWARD | `phase:431` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase436_runtime_tranche_completion_no_cdl_mutation` | policy | edge_added | CARRIES_FORWARD | `phase:436` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase437_runtime_tranche_findings_doc_only` | policy | edge_added | CARRIES_FORWARD | `phase:437` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase446_consensus_runtime_harness_no_transport_or_storage_cutover` | policy | edge_added | CARRIES_FORWARD | `phase:446` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase447_consensus_findings_adversarial_regression_no_new_runtime_surface` | policy | edge_added | CARRIES_FORWARD | `phase:447` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase450_window450_459_sequence_lock_lane_identity_freeze_no_opening` | policy | edge_added | CARRIES_FORWARD | `phase:450` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase456_fix13_post_nonlinear_control_blocker1_remains_open_no_opening` | policy | edge_added | CARRIES_FORWARD | `phase:456_fix13` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase456_fix2_recovery_rule_blocker1_remains_open_no_opening` | policy | edge_added | CARRIES_FORWARD | `phase:456_fix2_recovery_rule_execution` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase456_fix8_oscillator_blocker1_cleared_no_opening` | policy | edge_added | CARRIES_FORWARD | `phase:456_fix8` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase456_fix9_post_oscillator_blocker1_cleared_rerun_admissible_no_opening` | policy | edge_added | CARRIES_FORWARD | `phase:456_fix9` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase456_post_fix5_blocker1_remains_open_treasury_closure_paused` | policy | edge_added | CARRIES_FORWARD | `phase:456` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase475_window475_484_sequence_lock_scope_freeze` | policy | edge_added | CARRIES_FORWARD | `phase:475` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase483_window475_484_coherence_capsule_v2_2` | policy | edge_added | CARRIES_FORWARD | `phase:483` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase485_window485_494_sequence_lock_sim010_gate` | policy | edge_added | CARRIES_FORWARD | `phase:485` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase498_epoch_boundary_cdl_amendment_deferred_to_window505_plus` | policy | edge_added | CARRIES_FORWARD | `phase:498` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase503_window495_504_coherence_capsule_v2_3` | policy | edge_added | CARRIES_FORWARD | `phase:503` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase533_window525_534_coherence_capsule_v2_6` | policy | edge_added | CARRIES_FORWARD | `phase:533` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase556_signal_floor_governance_adm_only` | policy | edge_added | CARRIES_FORWARD | `phase:556` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase559_gossip_transport_hardening_test_only` | policy | edge_added | CARRIES_FORWARD | `phase:559` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase563_window555_564_coherence_capsule_v2_9` | policy | edge_added | CARRIES_FORWARD | `phase:563` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase565_window565_574_sequence_lock_three_machine_http_transport` | policy | edge_added | CARRIES_FORWARD | `phase:565` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase566_transport_operationalization_boundary_lock_explicit_http_testbed` | policy | edge_added | CARRIES_FORWARD | `phase:566` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase604_window596_605_coherence_report_capsule_v3_2` | policy | edge_added | CARRIES_FORWARD | `phase:604` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase613_window613_619_mvp_spec_lane_no_runtime_widening` | policy | edge_added | CARRIES_FORWARD | `phase:613` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase620_window620_622_agent_skills_planning_lane_spec_only` | policy | edge_added | CARRIES_FORWARD | `phase:620` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase635_tier0_exact_numeric_runtime_migration` | policy | edge_added | CARRIES_FORWARD | `phase:635` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase636_tier0_numeric_hardening_closure` | policy | edge_added | CARRIES_FORWARD | `phase:636` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase637_window637_641_residual_r2_r3_numeric_cleanup` | policy | edge_added | CARRIES_FORWARD | `phase:637` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase641_residual_numeric_cleanup_closure` | policy | edge_added | CARRIES_FORWARD | `phase:641` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase654_window649_654_runtime_closure_rows1_4` | policy | edge_added | CARRIES_FORWARD | `phase:654` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase655_window655_658_signing_export_reproducibility_lane` | policy | edge_added | CARRIES_FORWARD | `phase:655` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase657_registry_channel_promotion_sync_reproducibility` | policy | edge_added | CARRIES_FORWARD | `phase:657` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase658_signing_export_hardening_closure` | policy | edge_added | CARRIES_FORWARD | `phase:658` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase659_row6_coupling_invariants_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:659` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase665_row9_transport_maturity_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:665` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase669_transport_maturity_decision_closure_candidate` | policy | edge_added | CARRIES_FORWARD | `phase:669` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase670_window665_670_row9_transport_closure` | policy | edge_added | CARRIES_FORWARD | `phase:670` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase676_rows7_8_censorship_independence_criteria_closure` | policy | edge_added | CARRIES_FORWARD | `phase:676` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase690_mysticeti_workload_suite` | policy | edge_added | CARRIES_FORWARD | `phase:690` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase697_mysticeti_row5_mechanism_proof` | policy | edge_added | CARRIES_FORWARD | `phase:697` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase698_mysticeti_row7_tlc_evidence` | policy | edge_added | CARRIES_FORWARD | `phase:698` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase699_mysticeti_row8_sovereign_configuration_confirmation` | policy | edge_added | CARRIES_FORWARD | `phase:699` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase700_window693_700_substrate_legitimacy_closure_gate` | policy | edge_added | CARRIES_FORWARD | `phase:700` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase701_window701_706_bal_kernel_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:701` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase703_bal_profile_kernel_calibration_contract` | policy | edge_added | CARRIES_FORWARD | `phase:703` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase704_post_banking_doctrine_lock_not_binding_law` | policy | edge_added | CARRIES_FORWARD | `phase:704` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase706_window701_706_economic_doctrine_closure` | policy | edge_added | CARRIES_FORWARD | `phase:706` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase707_window707_712_ratification_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:707` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase712_window707_712_ratification_closure` | policy | edge_added | CARRIES_FORWARD | `phase:712` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase713_window713_716_adaptive_gossip_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:713` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase714_adaptive_gossip_law_vs_freedom_contract` | policy | edge_added | CARRIES_FORWARD | `phase:714` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase715_partition_repair_commissioning_missing_signal_doctrine` | policy | edge_added | CARRIES_FORWARD | `phase:715` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase716_window713_716_adaptive_gossip_closure` | policy | edge_added | CARRIES_FORWARD | `phase:716` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase717_window717_722_adr0015_family_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:717` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase718_adr0015_family_inventory_and_scope` | policy | edge_added | CARRIES_FORWARD | `phase:718` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase720_commons_dedication_launch_bound_leasehold_deferred` | policy | edge_added | CARRIES_FORWARD | `phase:720` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase722_window717_722_adr0015_family_closure` | policy | edge_added | CARRIES_FORWARD | `phase:722` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase727_window727_732_adjacent_gated_economy_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:727` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase732_window727_732_adjacent_gated_economy_closure` | policy | edge_added | CARRIES_FORWARD | `phase:732` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase735_sim_topology_01_topology_shuffle_results` | policy | edge_added | CARRIES_FORWARD | `phase:735` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase739_window739_744_rows5_7_runtime_packaging_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:739` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase745_window745_748_convergence_commissioning_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:745` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase749_window749_752_planning_consolidation_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:749` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase750_master_completion_roadmap_m_series_update` | policy | edge_added | CARRIES_FORWARD | `phase:750` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase768_sec004_acceptance_testnet_client_epoch_fix` | policy | edge_added | CARRIES_FORWARD | `phase:768` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase770_sec004_m007_activation_audit_clear` | policy | edge_added | CARRIES_FORWARD | `phase:770` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase771_m_series_lane_doc_update_sec004_m007` | policy | edge_added | CARRIES_FORWARD | `phase:771` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase773_coherence_capsule_v56_sec004_m007` | policy | edge_added | CARRIES_FORWARD | `phase:773` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase776_layer1_agentid_log_hygiene` | policy | edge_added | CARRIES_FORWARD | `phase:776` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase777_sim_leakage_01_post_layer1_results` | policy | edge_added | CARRIES_FORWARD | `phase:777` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase778_layer2_relay_forwarding_testnet_only` | policy | edge_added | CARRIES_FORWARD | `phase:778` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase779_sim_leakage_01_run2_post_both_layers` | policy | edge_added | CARRIES_FORWARD | `phase:779` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase780_row5_honest_nonclosure_bands_not_met` | policy | edge_added | CARRIES_FORWARD | `phase:780` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase781_coherence_capsule_v57_row5_nonclosure` | policy | edge_added | CARRIES_FORWARD | `phase:781` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase813_option_b_checklist_v02_state` | policy | edge_added | CARRIES_FORWARD | `phase:813` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase831_row5_b_impl_obligations_1_3_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:831` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase832_row5_b_impl_obligations_4_5_monitoring_notifications` | policy | edge_added | CARRIES_FORWARD | `phase:832` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase833_row5_b_impl_obligation_6_sim_leakage_03_metrics` | policy | edge_added | CARRIES_FORWARD | `phase:833` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase834_row5_b_impl_honest_nonclosure_closure_gate` | policy | edge_added | CARRIES_FORWARD | `phase:834` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase837_track1_predeployment_lane_coherence_human_gate_not_pulled` | policy | edge_added | CARRIES_FORWARD | `phase:837` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase838b_sphincs_recovery_seed_shamir_split_stdin_only` | policy | edge_added | CARRIES_FORWARD | `phase:838b` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase838d_agent_id_runtime_v2_identity_seed_sha384` | policy | edge_added | CARRIES_FORWARD | `phase:838d` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase838f_endorsement_packet_schema_cose_tbs` | policy | edge_added | CARRIES_FORWARD | `phase:838f` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase844_row5_rust_routing_instrumentation_sequence_lock` | policy | edge_added | CARRIES_FORWARD | `phase:844` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase845_sim_leakage_03_live_run_honest_nonclosure` | policy | edge_added | CARRIES_FORWARD | `phase:845` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase847_window_844_847_closure_row5_runtime_closed` | policy | edge_added | CARRIES_FORWARD | `phase:847` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase849_option_b_graduation_checklist_v03` | policy | edge_added | CARRIES_FORWARD | `phase:849` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase852_window_848_852_closure` | policy | edge_added | CARRIES_FORWARD | `phase:852` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase932_933_h013_spectral_beacon_tests` | policy | edge_added | CARRIES_FORWARD | `phase:932` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase_1213_artifact_manifest_shape` | policy | edge_added | CARRIES_FORWARD | `phase:1213` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase_1332_fix4_pre_1333_hardening` | policy | edge_added | CARRIES_FORWARD | `phase:1332_fix4` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase_1366_treasury_epoch_budget_binding_verified` | policy | edge_added | CARRIES_FORWARD | `phase:1366` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase_1369_fix1_authorized_numeric_hardening` | policy | edge_added | CARRIES_FORWARD | `phase:1369_fix1` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase_1558_private_runtime_selftest` | policy | edge_added | CARRIES_FORWARD | `phase:1558` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase_1559_private_runtime_selftest` | policy | edge_added | CARRIES_FORWARD | `phase:1559` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase_1560_preflight_blocker_recorded` | policy | edge_added | CARRIES_FORWARD | `phase:1560` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:phase_1560_private_receiver_selftest` | policy | edge_added | CARRIES_FORWARD | `phase:1560` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:pre_gate_fix_pass_phase_1367` | policy | edge_added | CARRIES_FORWARD | `phase:1367` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:pre_vrf_hardening_phase_1410_fix1` | policy | edge_added | CARRIES_FORWARD | `phase:1410_fix1` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:private_harness_integration_phase_1465p` | policy | edge_added | CARRIES_FORWARD | `phase:1465p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:production_emission_not_activated_phase_1532p` | policy | edge_added | CARRIES_FORWARD | `phase:1532p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:production_emission_not_activated_phase_1533p` | policy | edge_added | CARRIES_FORWARD | `phase:1533p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:production_emission_not_activated_phase_1534p` | policy | edge_added | CARRIES_FORWARD | `phase:1534p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:production_emission_not_activated_phase_1535p` | policy | edge_added | CARRIES_FORWARD | `phase:1535p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:release_artifacts_signed_phase_1447` | policy | edge_added | CARRIES_FORWARD | `phase:1447` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:release_dry_run_private_only_sequence_locked_phase_1317` | policy | edge_added | CARRIES_FORWARD | `phase:1317` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:review_lane_payment_not_activated_phase_1416` | policy | edge_added | CARRIES_FORWARD | `phase:1416` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:review_lane_production_not_activated_phase_1415` | policy | edge_added | CARRIES_FORWARD | `phase:1415` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:review_lane_wiring_complete_phase_1417` | policy | edge_added | CARRIES_FORWARD | `phase:1417` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:rust_p2p_bridge_not_activated_phase_1483p` | policy | edge_added | CARRIES_FORWARD | `phase:1483p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:sim_graphopt_01_forward_optimization_phase_1387i` | policy | edge_added | CARRIES_FORWARD | `phase:1387` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:transfer_mixing_k_anonymity_framework_phase_1359` | policy | edge_added | CARRIES_FORWARD | `phase:1359` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:transport_principal_cdl_ratified_gate_wired_phase_1436` | policy | edge_added | CARRIES_FORWARD | `phase:1436` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:treasury_distribution_not_activated_phase_1540p` | policy | edge_added | CARRIES_FORWARD | `phase:1540p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:vrf_integration_tests_complete_phase_1413` | policy | edge_added | CARRIES_FORWARD | `phase:1413` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:werner_condition_1_topology_pressure_covered_phase_1508p` | policy | edge_added | CARRIES_FORWARD | `phase:1508p` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:werner_diagnostic_wired_phase_1442` | policy | edge_added | CARRIES_FORWARD | `phase:1442` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `policy:window_1369_1390_closed_phase_1390` | policy | edge_added | CARRIES_FORWARD | `phase:1390` | `docs/phases/STATUS.md` | policy_candidate_id_embeds_phase_token |
| `sim:SIM-004_partition_resilience` | sim | edge_added | CARRIES_FORWARD | `phase:369_sim004_commissioning` | `tests/test_phase_369_sim_004_commissioning.py` |  |
| `sim:SIM-005_agent_death_orphaning` | sim | edge_added | CARRIES_FORWARD | `phase:370_sim005_commissioning` | `docs/phases/phase_0370_g8_constitution_cluster_a_sim_005_agent_death_and_graph_orphaning_commissioning_walkthrough.md` |  |
| `sim:SIM-006_panel_effectiveness` | sim | edge_added | CARRIES_FORWARD | `phase:386_sim_006_007_commissioning` | `tests/test_phase_386_sim_006_007_commissioning.py` |  |
| `sim:SIM-007_agent_churn_orphan_accumulation` | sim | edge_added | CARRIES_FORWARD | `phase:386_sim_006_007_commissioning` | `tests/test_phase_386_sim_006_007_commissioning.py` |  |
| `sim:SIM-008_post_issuance_transition` | sim | edge_added | CARRIES_FORWARD | `phase:406_sim_008_commissioning` | `tests/test_phase_406_sim_008_commissioning.py` |  |
| `sim:SIM-010_validator_incentive_economics` | sim | edge_added | CARRIES_FORWARD | `phase:487_sim_010_validator_incentive_economics` | `docs/phases/phase_0487_sim_010_validator_incentive_economics_execution_and_evidence_walkthrough.md` |  |
| `sim:SIM-EMBED-01` | sim | edge_added | EVIDENCES | `invariant:sim_embed_01_records_recommendations_staleness_thresholds_and_unexecuted_openai_candidate` | `docs/specs/ilc_phase_791_800_sequence_lock_v0.1.md` |  |
| `sim:claim_lifecycle_playground` | sim | edge_added | CARRIES_FORWARD | `phase:claim_lifecycle_playground_simulation` | `tests/test_claim_lifecycle_playground.py` |  |
| `sim:claim_reward_flow` | sim | edge_added | CARRIES_FORWARD | `phase:claim_reward_flow_simulation` | `tests/test_claim_reward_flow.py` |  |
| `sim:data_center_ballast` | sim | edge_added | EVIDENCES | `invariant:data_center_ballast_ilc_utilization_not_worse_than_baseline` | `tests/test_data_center_ballast.py` |  |
| `sim:data_center_ballast_controller` | sim | edge_added | EVIDENCES | `invariant:data_center_ballast_cli_prints_and_preserves_non_degradation` | `tests/test_data_center_ballast.py` |  |
| `sim:genesis_compile_02` | sim | edge_added | CARRIES_FORWARD | `phase:1387b` | `tests/test_phase_1387b_sim_genesis_compile_02.py` |  |
| `sim:merkle_laplacian_v02_followon_2026_05_22` | sim | edge_added | EVIDENCES | `invariant:merkle_laplacian_followon_does_not_authorize_publication_or_epoch_commitment_activation` | `tests/test_merkle_laplacian_v02_followon_sims.py` |  |
| `sim:merkle_laplacian_v02_strike_force_2026_05_22` | sim | edge_added | EVIDENCES | `invariant:merkle_laplacian_strike_force_is_research_positive_with_publication_gates_remaining` | `tests/test_merkle_laplacian_v02_strike_force_sim.py` |  |
| `sim:provenance_01` | sim | edge_added | CARRIES_FORWARD | `phase:1120_sim_provenance_01_commissioning` | `docs/sims/sim_spectral_02/sim_spectral_02_signal_definition_v0.1.md` |  |
| `sim:provenance_01_commissioning` | sim | edge_added | CARRIES_FORWARD | `phase:1120_sim_provenance_01_commissioning` | `docs/phases/phase_1120_sim_provenance_01_commissioning_walkthrough.md` |  |
| `sim:provenance_01_run02` | sim | edge_added | CARRIES_FORWARD | `phase:1121_sim_provenance_01_run02_disposition` | `docs/sims/sim_provenance_01/results_phase_1121_run_02.md` |  |
| `sim:spectral_02_genesis_candidate_crawl` | sim | edge_added | CARRIES_FORWARD | `phase:spectral_02_genesis_candidate_crawl` | `tests/test_genesis_node_candidate_crawl.py` |  |
| `sim:spectral_02_run01_disposition` | sim | edge_added | CARRIES_FORWARD | `phase:1134_sim_spectral_02_run01_disposition` | `docs/phases/phase_1134_sim_spectral_02_run01_disposition_walkthrough.md` |  |
| `sim:spectral_03_disposition` | sim | edge_added | CARRIES_FORWARD | `phase:1146_sim_spectral_03_disposition` | `docs/sims/sim_spectral_03/disposition_1146_v0.1.md` |  |
| `sim:spectral_03_harness` | sim | edge_added | CARRIES_FORWARD | `phase:1144_sim_spectral_03_harness` | `tests/test_phase_1144_sim_spectral_03_harness.py` |  |
| `sim:spectral_03_run01` | sim | edge_added | CARRIES_FORWARD | `phase:1145_sim_spectral_03_run01` | `docs/sims/sim_spectral_03/run01_raw_notes_1145.md` |  |
| `sim:spectral_03_topology_search` | sim | edge_added | CARRIES_FORWARD | `phase:1145a_sim_spectral_03_topology_search` | `docs/sims/sim_spectral_03/run01a_topology_search_notes.md` |  |
| `sim:spectral_04_claim_composition_projection` | sim | edge_added | CARRIES_FORWARD | `phase:1160_claim_composition_projection_build` | `tests/test_phase_1160_claim_composition_projection_build.py` |  |
| `sim:spectral_04_disposition_gate_fail` | sim | edge_added | CARRIES_FORWARD | `phase:1162_sim_spectral_04_disposition` | `tests/test_phase_1165_window_1156_1165_closure_gate.py` |  |
| `sim:spectral_04_program_spec` | sim | edge_added | CARRIES_FORWARD | `phase:1152_sim_spectral_04_program_spec` | `tests/test_phase_1152_sim_spectral_04_program_spec.py` |  |
| `sim:spectral_04_run01` | sim | edge_added | CARRIES_FORWARD | `phase:1161_sim_spectral_04_run01` | `docs/sims/sim_spectral_04/run01_raw_notes_1161.md` |  |
| `sim:spectral_05_disposition` | sim | edge_added | CARRIES_FORWARD | `phase:1171_sim_spectral_05_disposition` | `tests/test_phase_1171_sim_spectral_05_disposition.py` |  |
| `sim:spectral_05_economic_flow_slice` | sim | edge_added | CARRIES_FORWARD | `phase:1180_sim_spectral_05_economic_flow_slice` | `docs/sims/sim_spectral_05/economic_flow_slice_disposition_1180_v0.1.md` |  |
| `sim:spectral_05_gossip_slice` | sim | edge_added | CARRIES_FORWARD | `phase:1187_sim_spectral_05_gossip_slice` | `docs/sims/sim_spectral_05/gossip_slice_program_1187_v0.1.md` |  |
| `sim:spectral_05_runtime_binding_slice` | sim | edge_added | CARRIES_FORWARD | `phase:1179_sim_spectral_05_runtime_binding_slice` | `docs/sims/sim_spectral_05/runtime_binding_slice_program_1179_v0.1.md` |  |
| `sim:spectral_05_three_slice_observer_framework` | sim | edge_added | CARRIES_FORWARD | `phase:1192_roadmap_v1_0_rc2_status` | `docs/phases/phase_1192_roadmap_v1_0_rc2_status_walkthrough.md` |  |
| `sim:spectral_05_three_slice_observer_framework_complete` | sim | edge_added | CARRIES_FORWARD | `phase:1192_roadmap_v1_0_rc2_status` | `docs/phases/phase_1192_roadmap_v1_0_rc2_status_walkthrough.md` |  |
| `sim:spectral_05_track_a` | sim | edge_added | CARRIES_FORWARD | `phase:1169_sim_spectral_05_track_a_calibration` | `docs/sims/sim_spectral_05/track_a_calibration_notes_1169.md` |  |
| `sim:spectral_05_track_a_calibration` | sim | edge_added | CARRIES_FORWARD | `phase:1169_sim_spectral_05_track_a_calibration` | `docs/sims/sim_spectral_05/track_a_calibration_notes_1169.md` |  |
| `sim:spectral_05_track_b` | sim | edge_added | CARRIES_FORWARD | `phase:1170_sim_spectral_05_track_b_build` | `docs/sims/sim_spectral_05/branchial_projection_design_1170_v0.1.md` |  |
| `sim:spectral_05_track_b_projection` | sim | edge_added | CARRIES_FORWARD | `phase:1170_sim_spectral_05_track_b_build` | `docs/sims/sim_spectral_05/branchial_projection_design_1170_v0.1.md` |  |
| `sim:treasury_sim_t_nonlinear_control_phase_456_fix12` | sim | edge_added | CARRIES_FORWARD | `phase:456_fix12_nonlinear_control_execution` | `docs/specs/ilc_treasury_sim_t_nonlinear_control_evidence_package_456_fix_12_v0.1.md` |  |
| `sim:validator_incentive_economics_010` | sim | edge_added | CARRIES_FORWARD | `phase:487_sim_010_validator_incentive_economics` | `docs/specs/ilc_sim_010_validator_incentive_economics_evidence_package_487_v0.1.md` |  |

## Target Tier-1 Review Queue

These `target:*` nodes looked potentially build-critical from their ID, but Fix69 did not infer a semantic edge without a producing phase, module, or CDL direct read.

| candidate_id | track | disposition | edge_type | target | evidence | reason |
|---|---|---|---|---|---|---|
| `target:adr_0030` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_cdl086_open_not_ratified_no_public_launch_no_legal_conclusions_no_ilc_core_mutation` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_design_spec_only_no_float_constants_no_ilc_core_mutation_no_unbounded_graph_dump` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_ilc_core_storage_or_node_imports_in_pure_logic_no_forbidden_ilc_logic_imports` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_agent_eveagent_auto_mine_claim` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_agent_eveagent_decide_stake_for_claim` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_agent_eveagent_mine_thought` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_agent_eveagent_perform_pow_benchmark` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_agent_descriptors_agentdescriptor` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_agent_descriptors_build_agent_descriptors_from_task_rows` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_agent_dossier_export_export_agent_dossiers_to_csv` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_agent_dossier_export_export_agent_dossiers_to_json` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_agent_dossier_export_flatten_profile_for_csv` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_agent_profiles_agentprofile` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_agent_profiles_attach_competency_to_profiles` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_agent_profiles_attach_influence_to_profiles` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_agent_profiles_attach_light_cone_to_profiles` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_agent_profiles_build_agent_profiles` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_agent_profiles_compute_agent_influence_kpis` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_claim_scores_build_claim_influence_table` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_claim_scores_write_claim_influence_csv` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_competency_kpis_compute_agent_competency_kpis` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_competency_kpis_summarize_competency_for_profile` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_embedding_pipeline_is_embedding_stale` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_embedding_pipeline_prepare_text_payload` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_embedding_pipeline_select_model` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_embedding_pipeline_select_payload_family` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_epistemic_code_namespacestats` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_fairness_metrics_apply_beta_theta_payouts` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_fairness_metrics_apply_pb_farming_and_gating` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_fairness_metrics_compute_group_roi_ratio` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_fairness_metrics_summarize_fairness` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_freshness_gate_compute_freshness_gate` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_freshness_gate_validate_freshness_gate_policy` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_genesis_accrual_governor_compute_genesis_share_ratio` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_genesis_accrual_governor_compute_taper_multiplier` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_genesis_accrual_governor_evaluate_genesis_accrual_governor` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_genesis_accrual_governor_simulate_genesis_accrual_governor_trajectory` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_governance_weight_compute_governance_weights` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_graph_kpis_compute_claim_link_stats` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_graph_kpis_compute_local_influence_scores` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_graph_kpis_find_conflict_hotspots` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_graph_kpis_get_local_influence_scores` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_graph_kpis_rank_claims_by_influence` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_light_cone_kpis_compute_agent_light_cone_kpis` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_local_spectral_analytics_compute_local_lambda2` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_local_spectral_analytics_fiedler_centrality_delta` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_namespace_health_build_namespace_health_snapshot` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_namespace_health_build_namespace_health_timeseries` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_namespace_health_write_namespace_health_csv` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_conformance_build_node_value_conformance_report` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_conformance_verify_node_value_challenge` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_extraction_build_node_value_replay_fixture_from_ndjson` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_extraction_build_node_value_replay_fixture_from_rows` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_extraction_write_node_value_replay_fixture` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_input_canon_collect_node_value_input_events` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_input_canon_validate_node_value_input_event` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_kernel_build_node_evidence_vectors` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_kernel_compute_node_scores` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_kernel_compute_utility_flow` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_kernel_validate_ew_weights` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_node_value_policy_migration_normalize_node_value_policy_bundle` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_path_lift_counterfactual_compute_path_lift_counterfactual` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_path_lift_counterfactual_rank_path_lift_rows` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_problem_space_kpis_compute_problem_space_kpis` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_problem_space_kpis_infer_problem_space` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_reuse_diversity_invariants_compute_reuse_diversity_multiplier` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_reuse_diversity_invariants_validate_reuse_diversity_policy` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_routed_tasks_export_export_routed_tasks_to_json` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_stress_response_kpis_attach_stress_response_to_profiles` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_stress_response_kpis_compute_agent_stress_response` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_task_routing_suggestions_classify_namespace_stress` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_task_routing_suggestions_suggest_tasks_for_agents` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_task_routing_suggestions_taskroutingsuggestion` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_utility_flow_rewards_allocate_rewards_with_governor` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_utility_flow_rewards_assert_refutation_profitability_invariant` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_utility_flow_rewards_compute_reward_allocations` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_utility_flow_rewards_evaluate_refutation_profitability_invariant` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_analysis_utility_flow_rewards_evaluate_reward_governor` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_ccss_runtime_build_allow_reply_message` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_ccss_runtime_generate_identity` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_ccss_runtime_seal_message` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_ccss_runtime_unseal_message` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_cli__cli_error_build_cli_error_payload` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_cli__cli_error_emit_cli_error` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_cli__key_utils_load_key_bytes_with_b64_fallback` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_cli_balance_report` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_cli_canon_cluster_a_replay_proof_main` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_cli_mcp_cli__invoke_tool` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_engine_consensusengine_calculate_maintenance_tax` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_engine_consensusengine_calculate_refutation_bounty` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_finality_evaluator_evaluate_epoch_finality` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_governance_governance` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_governance_governance_get_task_fee_ecu` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_governance_governance_update_congestion` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_governance_governance_update_hardware_potential` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_production_bridge_build_quic_ecu_transfer_submission_path` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_production_bridge_build_secure_grpc_read_stub` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_production_bridge_ilcconsensusgrpcreadadapter` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_production_bridge_submit_ecu_transfer_via_quic` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_consensus_reputation_apply_atrophy` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_epoch_attribution_settle_runtime` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_epoch_attribution_settle_runtime_build_ejected_stake_treasury_distribution_quote` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_epoch_attribution_settle_runtime_evaluate_ejected_stake_vote` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_epoch_attribution_settle_runtime_require_h_con_02_quorum_guard` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_epoch_attribution_settle_runtime_settle_attribution_batch` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_epoch_ledger_simpleepochledger_clearing_price` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_epoch_ledger_simpleepochledger_get_epoch_stats` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_epoch_ledger_simpleepochledger_record_task` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_epoch_ledger_simpleepochledger_total_aggregate` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_outcome_outcomelogger` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_outcome_taskoutcome` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_reward_simple_claim_reward` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_telemetry_economictelemetry` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_economics_telemetry_rlhook` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_epoch` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:ilc_core_epoch_allocation_distributor_runtime_build_allocation_distribution_quote` | target | tier1_build_critical_review_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |

## Target Tier-2 Leaves

These targets are support/build-output leaves. Fix69 intentionally did not wire them to governance nodes.

| candidate_id | track | disposition | edge_type | target | evidence | reason |
|---|---|---|---|---|---|---|
| `target:agent_behavioral_loop_runtime_cutover_v1` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:agent_init_ceremony_1560` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_devnet_topology_and_load_metrics` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_dynamic_maintenance_tax_and_paradigm_shift_bounties` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_epistemic_light_cone_kpi_analytics` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_genesis_atlas_v0_2_root_envelope_signature_phase_1340` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_genesis_core_star_map_v0_3_candidate` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_genesis_epistemic_work_task_model` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_genesis_node_attestation_manifest_v0_1` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_governance_fee_scaling_runtime` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_governance_mvp_config` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_graph_conflict_support_kpis` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_hardware_archetype_strategy_sim` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_legacy_eve_agent_life_smoke` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_legacy_kernel_genesis_linking_smoke` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_namespace_health_analytics` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_phase1323_fix2_openclaw_vps_install_skill_discovery_report` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:artifact_phase1323_openclaw_nemoclaw_claimable_profile_full_dry_run_report` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:atlas_tier1_checkpoint_1_report` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:bash_tools_check_event_log_retention_rotation_sh` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:bash_tools_check_freshness_gate_invariants_phase_217_sh` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:bash_tools_check_genesis_accrual_governor_phase_218_sh` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:bash_tools_check_genesis_readiness_audit_reverification_1012_sh` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:bash_tools_check_genesis_readiness_remediation_closure_996_1008_sh` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:blocker_genesis_rooted_identity_origin` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:blocker_identity_seed_ux_public_bootstrap` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_adaptive_replication_disabled_by_default_no_invalid_controls_no_cdl087_ratification` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_adr0020_acceptance_does_not_immediately_migrate_all_governance_constants` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_adr0036_remains_proposed_and_does_not_define_lineage_contract` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_adr0036_scope_boundary_and_signed_v01_unchanged` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_cdl001_register_row_not_reused_for_genesis_blocker` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_cdl085_open_not_ratified_edge_mint_phi_bound_unset_no_runtime_mutation` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_cdl087_not_ratified_pull_first_not_universal_service_mandate_no_circuit_breaker_weakening` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_cdl087_not_ratified_v02_signing_deferred_mempalace_advisory_only` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_cdl088_not_ratified_no_public_claimability_activation_no_claim_endpoint_enabled_no_runtime_activation_no_runtime_mutation_no_cdl_register_mutation` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_cdl090_not_ratified_no_cdl088_opening_no_identity_artifact_creation_no_secret_generation_no_public_identity_activation_no_public_claimability_activatio` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_cdl090_not_ratified_no_cdl_register_mutation_no_cdl088_opening_no_runtime_mutation_no_secret_material` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_deliberation_does_not_authorize_phase1204_and_public_launch_blocks_remain` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_ejected_stake_distribution_not_activated_no_notimplemented_stub_no_float_economics` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_fail_closed_missing_corrupt_schema_mismatch_and_raw_requester_id_not_persisted` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_genesis_authority_attestation_not_multi_party_signer_roster` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_historical_pre_ratification_phi_bound_placeholder` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_inventory_only_no_counsel_legal_conclusion_no_ip_filing_no_paper_publication_no_public_repo_package_no_public_rc_claim` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_local_only_no_public_p2p_no_public_claimability_no_openclaw_nemoclaw_dependency_no_network_storage_imports` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_local_preview_not_final_public_rc_no_forbidden_imports_no_absolute_roots` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_m019_loopback_testbed_not_durable_not_formal_proof_spec_b_not_epoch_checkpoint_shared_object_proof` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_malformed_provenance_chain_input_rejected` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_activation_no_public_rc_no_release_export_no_genesis_atlas_signing_no_v02_signing_no_cdl088_no_ecu_mint_no_ilc_settlement` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_anonymity_claim_no_unlinkability_claim_no_signal_equivalent_guarantee_no_public_p2p_no_network_runtime_no_predictable_prng` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_artifact_only_credit_no_tier_c_cdl078_credit_by_default_no_cdl087_ratification` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_assert_no_random_requests_open_wall_clock_float_constants` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_blanket_mit_no_public_rc_authorization_no_counsel_finality_claim` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_bool_bounds_no_unbounded_results_no_unbounded_hops_no_float_centrality` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_bulk_legacy_backfill_no_public_rc_claim_no_v02_signing_no_genesis_atlas_regeneration` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_cdl087_ratification_no_public_fetch_no_public_p2p_no_werner_ecu_mint_no_ilc_settlement_no_v02_signing` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_cdl_mutation_authorization` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_cdl_open_no_adr_acceptance_no_phase1156_signing_authorization` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_cdl_register_mutation_no_phase1214_ratification_evidence` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_created_at_no_float_economic_summary_no_bool_integer_fields_no_wall_clock_commit_epoch` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_created_at_no_payload_source_no_epoch_zero_adapter_no_production_emission` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_created_at_no_wall_clock_no_legacy_constructor_no_random_no_network_no_file_io` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_final_runtime_retuning_accepted_by_phase1158_batch` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_float_centrality_results_no_malformed_metric_values_no_unbounded_top_k` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_float_no_nan_no_wall_clock_no_filesystem_io_no_network_io` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_float_profiles_no_unbounded_total_scenarios_no_cdl087_ratification` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_float_rates_no_cdl087_ratification_no_request_cap_overrun` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_float_reward_total_no_genesis_epoch_zero_no_wall_clock_random_io_network_legacy_constructor` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_float_staleness_no_invalid_exact_holder_count_no_claimed_cdl087_ratification` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_float_sweep_inputs_no_unbounded_scenarios_no_cdl087_ratification_no_werner_economic_activation` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_float_values_no_random_assert_wall_clock_protocol_calls_no_unsupported_projection` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_float_zipf_or_avg_requests_no_out_of_range_zipf` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_http_lmdb_socket_urllib_in_protocol_harness_interfaces_no_forbidden_runtime_imports` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_http_server_no_non_loopback_bind_no_public_sidecar_no_public_claimability_no_v02_signing` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_invalid_retry_hops_no_retry_depth_over_peer_count_no_cdl087_ratification` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_live_consensus_writes_no_python_write_authority_to_rust_consensus` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_openclaw_gateway_no_clawhub_public_install_no_public_rc_no_runtime_modification` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_phase1163_execution_no_cdl085_opening_authorized` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_phase1193_release_key_release_envelope_or_signing_artifact` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_phase1215_signing_ceremony_no_signing_evidence` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_phase1221_signing_ceremony_no_signing_evidence_unsigned_v02_candidate` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_phase1230_signing_ceremony_no_signing_evidence_unsigned_v02_candidate` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_phase1374_cdl088_prerequisite_before_execution_no_phase1389_public_claimability_gate_before_go` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_plaintext_agent_id_validator_logs_no_transfer_mixing_production_route_no_random_assert_wall_clock_or_float_patterns` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_private_peer_public_path_by_default_no_cbor_oversize_decode_no_release_artifact_authorization` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_production_issuance_implementation_no_production_minting_no_soft_rc_eligibility_without_phase1366_conditions` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_production_minting_no_fee_burn_activation_no_allocation_distribution_activation_no_treasury_activation_no_validator_reward_activation_no_ejected_sta` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_production_validation_weakening_no_cli_testing_bypass` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_claimability_api_no_public_verifier_service_no_public_claim_endpoint_no_wallet_value_actions` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_claimability_no_public_p2p_no_release_artifact_no_cdl_mutation_no_genesis_atlas_mutation_no_v02_signing_no_ecu_mint_no_ilc_settlement` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_claimability_no_public_p2p_no_release_export_no_genesis_atlas_mutation_no_v02_signing_no_cdl_mutation` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_claimability_no_public_p2p_no_serving_no_wallet_no_value_activation_no_skill_publication` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_fetch_serving_no_network_endpoint_no_float_payload_no_public_server_socket` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_launch_public_repo_v02_signing_or_cdl087_ratification` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_p2p_no_production_ecu_transfer_activation_no_durable_peer_to_peer_bft_claim_from_direct_injection_no_projection_write_path` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_p2p_no_public_claimability_no_final_public_rc_claim_from_roadmap_only` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_p2p_no_public_relay_no_confidential_messaging_claim_no_plaintext_or_route_metadata_leakage_no_unbounded_queue` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_rc_claim_no_v02_signing_claim_no_stale_gap_overclaim` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_rc_no_public_activation_no_cdl088_no_ecu_mint_no_ilc_settlement` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_rc_no_release_signing_no_public_activation_no_cdl_mutation_no_atlas_g_authority_substitution` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_rc_no_source_export_no_release_signing_no_claimability_no_public_p2p_no_wallet_no_ecu_mint_no_ilc_settlement_no_cdl088` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_public_rc_publication_claim_performed_no_public_repository_push_no_public_package_upload_no_release_signing_authorized_no_counsel_approval_no_wallet` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_publication_no_signing_no_allowlist_export_no_release_artifact_no_release_keys_no_genesis_atlas_mutation_no_v02_signing` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_publication_no_signing_no_identity_artifact_no_wallet_no_ecu_mint_no_ilc_settlement_no_public_ccss` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_publication_no_signing_no_public_activation_no_helper_stripping_execution_no_atlas_g_substitution_no_public_confidential_coordination` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_random_import_no_bool_rates_no_invalid_circuit_breaker_no_cdl087_ratification` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_raw_decimal_invalidoperation_escape_no_unbounded_governance_quality_score_no_lmdb_dry_run_write_transaction` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_release_signing_no_public_activation_no_identity_artifact_no_wallet_no_ecu_mint_no_ilc_settlement_no_counsel_approval` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_release_signing_no_public_claimability_no_public_verifier_service_no_wallet_withdrawal_no_ecu_minting_no_ilc_settlement_no_cdl088_opening_no_counsel` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_runtime_float_surface_no_nonfinite_float_no_routing_reputation_decimal_claim_before_cdl060_pipeline` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_runtime_mutation_no_signed_genesis_v01_mutation_phase1195` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_secret_material_in_committed_artifacts_no_public_rc_activation_despite_v02_signed_gate` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_secret_material_written_to_repo_no_private_material_path_recorded_no_release_signature_produced_no_unsigned_envelope_misclaimed_as_signed` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_soft_rc_eligible_true_recorded_no_new_scope_no_full_phase1366_gate_rerun` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_source_allowlist_export_no_release_artifact_no_keys_no_envelope_no_genesis_atlas_signing_no_public_rc_claim` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_source_publication_authorized_no_public_repository_publication_no_public_rc_claim` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_transport_principal_public_path_no_public_p2p_no_public_fetch_serving_no_public_sidecar_projection_no_public_confidential_coordination_no_public_lis` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_transport_principal_runtime_activation_no_public_p2p_no_public_sidecar_no_claimability_no_cdl_mutation` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_unknown_nodes_no_unbounded_hops_no_cycle_nontermination` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_unknown_root_no_unbounded_hops_no_overflow_node_result` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |
| `target:boundary_no_unsupported_query_type_no_missing_query_type_no_unimplemented_supported_query` | target | tier2_support_leaf_no_wiring_required |  | `` | `` | Fix69 did not infer semantic target edge without direct producing phase/CDL read |

## Unresolved Policy or Sim Records

These records had no exact non-speculative phase, CDL, ADR, or invariant anchor under the Fix69 rules.

| candidate_id | track | disposition | edge_type | target | evidence | reason |
|---|---|---|---|---|---|---|
| `policy:accepted_adr_cdl_runtime_coverage_matrix` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:adversarial_robustness_envelope_expansion` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:agent_graph_projection_interface` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:atlas_g_tail_unsigned_candidate_non_excisability_and_signing_gate` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:bal_profile_active_default_unratified` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:ccss_private_local_sidecar_boundary` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:cdl_ratification_ceremony_protocol` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:centrality_delta_gossip_bounded_fanout_and_score_cap` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:commit_epoch_production_emission_not_yet_authorized` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:confidential_coordination_local_preview_only` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:counsel_review_future_modification_expected` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:devnet_harness_not_production_emission` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:external_constitutional_center_exclusion_hard_gate` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:external_getting_started_docs_accuracy` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:fix6_fix7_required_before_successor_manifest_support_work` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:freshness_gate_contract` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:go_window_1429_required_next` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:go_window_1515p_required_next` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:gossip_peer_registry_endpoint_dedup_and_fanout_uniqueness` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:gossip_transport_header_epoch_and_forbidden_key_validation` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:h013_spectral_beacon_crypto_surface` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:high002_quorum_threshold_liveness_closure` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:issuance_stack_integration_and_not_activated_guard` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:j008_review_lane_condition` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:j008_vrf_verifier_condition` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:m007_mysticeti_hooks_activation_boundary` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:no_cdl_mutation_in_window_767_774` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:no_decision_log_mutation_window811_822` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:node_value_kernel` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:openclaw_nemoclaw_hosts_not_protocol_substrates` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:openclaw_private_vps_install_discovery_only` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:persistent_fetch_rate_limiter_scope` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:phase_commit_manifest_296_phase_history_stabilization` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:phase_high002_phase_b_closure_gate` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:phase_m009_mysticeti_testnet_setup` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:phase_m012_full_bft_transfer_binary_complete` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:phase_m014_workload_b_censorship_resistance_results` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:phase_m015_workload_c_tier2_partition_recovery` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:phase_m016_workload_d_replayability_state_extraction` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:phase_m019_adversarial_hardening` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:phase_prompt_schema_validation` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:refutation_profitability_gate_script_contract` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:refutation_profitability_runtime_invariant` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:replay_proof_schema_parity_gate` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:repo_hygiene_duplicate_definition_and_line_guardrail` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:reuse_diversity_gate_script_contract` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:reuse_diversity_runtime_invariant` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:row5_b_impl_commissioning` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:row5_b_scope_b1_b4_holdpoint` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:row5_b_scope_b5_lock_and_commissioning` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:row5_k_anonymity_jitter3_primary_lock` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:row7_liveness` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:row7_replayability_exitability` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:runtime_logging_closure_gate` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:safety_no_dual_cert` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:safetynodualcert_deferred_to_spec_d_epoch_checkpoint_scope` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:sdk_boundary_contract_signing_provider` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:sec008_missing_epoch_recovery_cursor` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:sec009_bls_epoch_auditability` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:sec_004_m007_activation_boundary` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:server_app_factory_runtime_boundary` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:server_lifecycle_runtime_boundary` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:simulation_only_deterministic_rng_allowed` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:static_peer_registry_v1` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:tier3_runtime_linkage` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:track1_ci_release_guardrail_presteps` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:track1_closure_guardrail_gate` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:transport_principal_required_before_non_loopback_projection` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:utility_flow_reward_runtime_invariant` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1257_1264_prompt_draft_validation` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1257_1264_sequence_lock_and_prompt_package` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1265_1272_prompt_draft_validation` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1265_1272_sequence_lock_and_prompt_package` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1273_1280_prompt_draft_validation` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1273_1280_sequence_lock_and_prompt_package` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1289_1302_prompt_draft_validation` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1289_1302_sequence_lock_and_prompt_package` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1303_1316_deep_code_audit_hardening` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1303_1316_prompt_draft_validation` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1303_1316_sequence_lock_and_prompt_package` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1317_1329_prompt_draft_validation` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1317_1329_sequence_lock_and_prompt_package` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1330_1342_prompt_draft_validation` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1330_1342_sequence_lock_and_prompt_package` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1343_1368_prompt_draft_validation` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window1343_1368_sequence_lock_and_prompt_package` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window545_554_runtime_audit_regression_hardening` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window555_560_gossip_transport_validation_guardrails` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window555_562_gossip_peer_registry_dedup_guardrails` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window767_774_closure_gate` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window767_774_integration_gate` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window775_782_closure_gate` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |
| `policy:window823_829_mysticeti_activation_sequence_lock` | policy | support_only_unresolved |  | `` | `` | no exact phase/cdl/adr token resolved without speculative edge |

## Non-Claims

- No Genesis signing.
- No public graph upload.
- No public RC activation.
- No runtime activation.
- No ECU minting.
- No ILC settlement.
- No `GOVERNS` edges added.
- No `SOURCE_TREE_MEMBER` edges added.
- `14` orphaned phase support nodes from the Fix-series registration lineage
  received `CARRIES_FORWARD -> phase:1545p` lineage edges after the main
  rewiring receipt, clearing phase-node non-repo orphan hygiene without adding
  authority edges.
