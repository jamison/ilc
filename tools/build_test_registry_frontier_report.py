#!/usr/bin/env python3
"""Build the Phase 1545p-Fix38 graph-derived test frontier report.

PUBLIC_RC_EXCLUDE: homoiconic_test_frontier_report_research_runner
PUBLIC_RC_EXCLUDE_REASON: Research-only report generator for graph-derived test
frontier gaps and manual connectivity annotations. It does not mutate graph
state, execute tests, sign nodes, upload nodes, or activate runtime/public RC
paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_FIX33 = Path("out/test_graph_coverage_1545p_fix33.json")
DEFAULT_FIX34 = Path("out/test_function_nodes_1545p_fix34.json")
DEFAULT_FIX35 = Path("out/test_registry_sidecar_plan_1545p_fix35.json")
DEFAULT_FIX36 = Path("out/test_registry_evidence_envelopes_1545p_fix36.json")
DEFAULT_FIX37 = Path("out/test_registry_hydrated_workspace_1545p_fix37.json")
DEFAULT_GRAPH = Path("out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json")
DEFAULT_INVENTORY = Path("docs/testing/test_inventory.md")
DEFAULT_STATUS = Path("docs/phases/STATUS.md")
DEFAULT_PLANNING = Path("docs/PLANNING_INDEX.md")
DEFAULT_MANUAL_LEDGER = Path("docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json")
DEFAULT_JSON_OUT = Path("out/test_registry_frontier_report_1545p_fix38.json")
DEFAULT_REPORT = Path("docs/specs/ilc_test_registry_frontier_report_1545p_fix38_v0.1.md")
DEFAULT_CANDIDATE_OUT = Path(
    "out/atlas_research/genesis_atlas_test_frontier_unified_candidate_1545p_fix38.json"
)

PHASE = "1545p-Fix38"

OUTPUT_TOKENS = [
    "graph_derived_test_frontier_report_committed_phase_1545p_fix38",
    "test_frontier_gap_categories_recorded_phase_1545p_fix38",
    "test_evidence_frontier_compared_phase_1545p_fix38",
    "manual_test_connectivity_annotations_recorded_phase_1545p_fix38",
    "stale_and_gated_test_frontier_recorded_phase_1545p_fix38",
    "test_frontier_report_no_authority_overclaim_phase_1545p_fix38",
    "public_path_remains_blocked_phase_1545p_fix38",
]

NON_CLAIMS = [
    "no_test_execution",
    "no_canonical_graph_mutation",
    "no_edge_promotion",
    "no_canonical_atlas_mutation",
    "no_genesis_signing",
    "no_node_upload",
    "no_public_graph_publication",
    "no_public_rc_activation",
    "no_runtime_activation",
    "no_sidecar_activation",
    "no_adr_cdl_mutation",
    "manual_annotations_are_review_queue_not_canonical_edges",
]

MANUAL_ANNOTATION_SOURCE = "direct_read_by_codex_phase_1545p_fix38"
CURATED_EDGE_BATCH_SOURCE = "manual_best_effort_direct_read_edge_batch_phase_1545p_fix38"
PATH_LITERAL_RE = re.compile(
    r"(?P<quote>[\"'`])(?P<path>(?:docs|tests|ilc_core|tools|out)/[A-Za-z0-9_./:@+=,-]+)(?P=quote)"
)
IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+(?P<module>(?:ilc_core|tools|tests|simulations)(?:\.[A-Za-z0-9_]+)*)",
    re.MULTILINE,
)
PHASE_TOKEN_RE = re.compile(r"phase[_-](?P<phase>\d{3,4}p?(?:[_-]fix\d+)?)", re.IGNORECASE)
PHASE_PATH_RE = re.compile(r"phase[_-](?P<phase>\d{3,4}p?)(?:[_-]fix(?P<fix>\d+))?", re.IGNORECASE)
FIX38_EXCLUDED_GENERATED_TARGETS = {
    "out/atlas_research/genesis_atlas_test_frontier_unified_candidate_1545p_fix38_digest.json",
}

CURATED_TARGET_OVERRIDES: dict[str, list[str]] = {
    "tests/test_canon_bundle_key_registry_cli.py": [
        "ilc_core/cli/canon_bundle_key_registry.py",
    ],
    "tests/test_canon_bundle_sign_cli.py": [
        "ilc_core/cli/canon_bundle_sign.py",
    ],
    "tests/test_canon_export_cli.py": [
        "ilc_core/cli/canon_export.py",
    ],
    "tests/test_claim_lifecycle_playground.py": [
        "simulations/claim_lifecycle_playground.py",
    ],
    "tests/test_claim_reward_flow.py": [
        "simulations/claim_reward_flow.py",
    ],
    "tests/test_code_health.py": [
        "repo_dir:ilc_core",
        "tests/test_code_health.py",
    ],
    "tests/test_dag_audit_cli.py": [
        "ilc_consensus/src/dag_audit_main.rs",
        "ilc_consensus/Cargo.toml",
    ],
    "tests/test_data_center_ballast.py": [
        "simulations/data_center_ballast.py",
    ],
    "tests/test_data_center_controller.py": [
        "simulations/data_center_ballast.py",
    ],
    "tests/test_docs_links_resolve.py": [
        "repo_dir:docs/phases",
        "repo_dir:docs/context_packs",
        "repo_dir:docs/adr",
        "repo_dir:docs/mcp",
    ],
    "tests/test_domain_sigmoid_sim.py": [
        "simulations/domain_sigmoid_allocation.py",
    ],
    "tests/test_epistemic_work_task_playground.py": [
        "simulations/epistemic_work_task_playground.py",
    ],
    "tests/test_epoch_playground_sim.py": [
        "simulations/end_to_end_epoch_playground.py",
    ],
    "tests/test_mcp_cli_adapter.py": [
        "ilc_core/cli/mcp_cli.py",
    ],
    "tests/test_meta_test_integrity_controls.py": [
        "repo_dir:tests",
        "tests/test_meta_test_integrity_controls.py",
    ],
    "tests/test_phase_768_sec_004_acceptance.py": [
        "ilc_consensus/src/fast_path.rs",
        "ilc_consensus/src/testnet_client_main.rs",
    ],
    "tests/test_phase_769_m007_hook_activation.py": [
        "ilc_consensus/src/validator.rs",
    ],
    "tests/test_phase_776_layer1_log_hygiene.py": [
        "ilc_consensus/src/node.rs",
        "ilc_consensus/Cargo.toml",
    ],
    "tests/test_phase_830_settlement_path_gate.py": [
        "ilc_consensus/src/config.rs",
        "ilc_consensus/src/main.rs",
        "docs/specs/ilc_settlement_path_rotation_wiring_design_825_v0.1.md",
    ],
    "tests/test_phase_844_row5_rust_routing_instrumentation.py": [
        "ilc_consensus/src/node.rs",
    ],
    "tests/test_phase_849_graduation_checklist_v0_3.py": [
        "docs/specs/ilc_option_b_graduation_checklist_state_849_v0.3.json",
        "docs/specs/ilc_option_b_graduation_checklist_state_682_v0.1.json",
        "docs/specs/ilc_constitutional_decision_log_v0.1.md",
    ],
    "tests/test_rc0_1_benchmark_runner.py": [
        "tools/testbed/run_rc0_1_benchmarks.py",
    ],
    "tests/test_rl_bandit_sim.py": [
        "simulations/rl_bandit_domain_allocation.py",
    ],
    "tests/test_task_queue_reward_flow.py": [
        "simulations/task_queue_reward_flow.py",
    ],
}

CURATED_FRONTIER_EDGE_ANNOTATIONS: dict[str, dict[str, Any]] = {
    "tests/test_event_log_retention_rotation_gate_phase_196.py": {
        "manual_read_summary": (
            "Validates the Phase 196 event-log retention and rotation gate shell "
            "contract: dry-run output, help text, unknown-argument failure, and "
            "normal PASS execution."
        ),
        "proposed_trace_roles": [
            "TESTS",
            "REFERENCES_TEST",
            "COVERS_COMMAND_CONTRACT",
            "EVIDENCES",
            "REQUIRES_PROFILE",
            "SOURCE_TREE_MEMBER",
        ],
        "proposed_semantic_edges": [
            {"edge_type": "TESTS", "target": "tools/check_event_log_retention_rotation.sh"},
            {
                "edge_type": "REFERENCES_TEST",
                "target": "tests/test_event_log_retention_rotation_phase_196.py",
            },
            {
                "edge_type": "COVERS_COMMAND_CONTRACT",
                "target": "command:tools/check_event_log_retention_rotation.sh",
            },
            {
                "edge_type": "EVIDENCES",
                "target": "phase:196_event_log_retention_rotation_gate",
            },
            {"edge_type": "REQUIRES_PROFILE", "target": "executor_profile:bash_plus_pytest"},
        ],
        "proposed_authority_trace_edges": [
            {
                "edge_type": "REFERENCES_AUTHORITY",
                "target": "docs/antigravity_tasks/antigravity_prompt__phase_196_g8_constitution_cluster_a_event_log_retention_rotation_ops_contract.md",
                "review_status": "candidate_role_specific_authority_trace",
            }
        ],
        "recommended_graph_action": (
            "materialize TESTS edge to the gate script and candidate authority trace "
            "to the Phase 196 ops-contract prompt"
        ),
    },
    "tests/test_node_id_runtime_bridge_phase_1003.py": {
        "manual_read_summary": (
            "Validates the Phase 1003 node-ID runtime bridge by exercising "
            "legacy ID acceptance, canonical ID acceptance, and mismatched ID "
            "rejection through the FastAPI gossip receive route."
        ),
        "proposed_trace_roles": [
            "TESTS",
            "COVERS_SYMBOL",
            "TESTS_ROUTE",
            "EVIDENCES",
            "REGRESSES",
            "REQUIRES_PROFILE",
            "SOURCE_TREE_MEMBER",
        ],
        "proposed_semantic_edges": [
            {"edge_type": "TESTS", "target": "ilc_core/server.py"},
            {"edge_type": "TESTS", "target": "ilc_core/types.py"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.server.create_app"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.types.Node.compute_legacy_id"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.types.Node.compute_canonical_id"},
            {"edge_type": "TESTS_ROUTE", "target": "api_route:/gossip/receive"},
            {"edge_type": "EVIDENCES", "target": "phase:1003_node_id_runtime_bridge"},
            {"edge_type": "REGRESSES", "target": "invariant:canonical_node_id_mismatch_rejected"},
        ],
        "proposed_authority_trace_edges": [
            {
                "edge_type": "REFERENCES_AUTHORITY",
                "target": "docs/phases/phase_1003_g8_constitution_cluster_a_nodeid_migration_phase2_runtime_boundary_compatibility_bridge_walkthrough.md",
                "review_status": "candidate_role_specific_authority_trace",
            }
        ],
        "recommended_graph_action": (
            "materialize runtime TESTS and COVERS_SYMBOL edges plus authority "
            "trace through the Phase 1003 walkthrough"
        ),
    },
    "tests/test_phase_1135_sim_spectral_02_run02.py": {
        "manual_read_summary": (
            "Validates SIM-SPECTRAL-02 run02 output shape, scenario coverage, "
            "run01 preservation, and Phase 1135 completion evidence."
        ),
        "proposed_trace_roles": [
            "TESTS",
            "EVIDENCES",
            "REGRESSES",
            "REQUIRES_PROFILE",
            "SOURCE_TREE_MEMBER",
        ],
        "proposed_semantic_edges": [
            {"edge_type": "TESTS", "target": "out/sim_spectral_02_run02_summary.json"},
            {"edge_type": "TESTS", "target": "out/sim_spectral_02_run01_summary.json"},
            {"edge_type": "TESTS", "target": "docs/sims/sim_spectral_02/run02_raw_notes_1135.md"},
            {"edge_type": "EVIDENCES", "target": "sim:SIM-SPECTRAL-02-run02"},
            {"edge_type": "REGRESSES", "target": "invariant:sim_spectral_02_run01_summary_preserved"},
        ],
        "proposed_authority_trace_edges": [
            {
                "edge_type": "EVIDENCES",
                "target": "docs/phases/phase_1135_sim_spectral_02_run02_walkthrough.md",
                "review_status": "candidate_phase_evidence_trace",
            }
        ],
        "recommended_graph_action": "materialize SIM artifact TESTS edges and Phase 1135 evidence trace",
    },
    "tests/test_phase_1137_coherence_capsule_v5_38.py": {
        "manual_read_summary": (
            "Validates the Phase 1137 coherence capsule, integration report, "
            "SIM-SPECTRAL-02 disposition, Genesis star-map output, and CDL-084 "
            "runtime constant preservation."
        ),
        "proposed_trace_roles": [
            "TESTS",
            "COVERS_SYMBOL",
            "EVIDENCES",
            "REGRESSES",
            "REFERENCES_AUTHORITY",
            "REQUIRES_PROFILE",
            "SOURCE_TREE_MEMBER",
        ],
        "proposed_semantic_edges": [
            {"edge_type": "TESTS", "target": "docs/specs/ilc_antigravity_context_capsule_v5.38.md"},
            {"edge_type": "TESTS", "target": "docs/specs/ilc_integration_coherence_report_1137_v0.1.md"},
            {"edge_type": "TESTS", "target": "docs/sims/sim_spectral_02/run02_disposition_1136_v0.1.md"},
            {"edge_type": "TESTS", "target": "out/genesis_core_star_map_v0.1.json"},
            {"edge_type": "TESTS", "target": "ilc_core/types.py"},
            {"edge_type": "TESTS", "target": "ilc_core/economics/epoch_attribution_settle_runtime.py"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.types.PROVENANCE_DECAY_ALPHA"},
            {"edge_type": "EVIDENCES", "target": "phase:1137_coherence_capsule"},
            {"edge_type": "REGRESSES", "target": "invariant:cdl_084_provenance_decay_constant_preserved"},
        ],
        "proposed_authority_trace_edges": [
            {
                "edge_type": "REFERENCES_AUTHORITY",
                "target": "cdl:084_provenance_chain",
                "review_status": "candidate_role_specific_authority_trace",
            }
        ],
        "recommended_graph_action": "materialize coherence, SIM, star-map, and CDL-084 preservation edges",
    },
    "tests/test_phase_1215_v0_2_signing_skip.py": {
        "manual_read_summary": (
            "Validates that Phase 1215 records v0.2 signing as deferred and "
            "that no signing evidence file exists without signing authorization."
        ),
        "proposed_trace_roles": [
            "TESTS",
            "NEGATIVE_ASSERTS_ABSENCE",
            "EVIDENCES",
            "REGRESSES",
            "REQUIRES_PROFILE",
            "SOURCE_TREE_MEMBER",
        ],
        "proposed_semantic_edges": [
            {"edge_type": "TESTS", "target": "docs/phases/phase_1215_v0_2_signing_ceremony_walkthrough.md"},
            {"edge_type": "TESTS", "target": "docs/phases/STATUS.md"},
            {
                "edge_type": "NEGATIVE_ASSERTS_ABSENCE",
                "target": "docs/specs/ilc_genesis_v0_2_signing_evidence_1215_v0.1.md",
            },
            {"edge_type": "EVIDENCES", "target": "phase:1215_v0_2_signing_deferred_boundary"},
            {"edge_type": "REGRESSES", "target": "invariant:no_signing_evidence_without_authorization"},
        ],
        "proposed_authority_trace_edges": [
            {
                "edge_type": "REFERENCES_AUTHORITY",
                "target": "policy:genesis_signing_authorization_gate",
                "review_status": "candidate_policy_terminal_requires_review",
            }
        ],
        "recommended_graph_action": "materialize negative signing-gate evidence edges",
    },
    "tests/test_phase_1350_cdl_083_ejected_stake_treasury_distribution.py": {
        "manual_read_summary": (
            "Validates the CDL-083 ejected-stake treasury distribution runtime "
            "surface, H-CON-02 quorum guard, Decimal arithmetic, activation "
            "fail-closed guard, and Phase 1350 evidence/docs."
        ),
        "proposed_trace_roles": [
            "TESTS",
            "COVERS_SYMBOL",
            "EVIDENCES",
            "REGRESSES",
            "REFERENCES_AUTHORITY",
            "REQUIRES_PROFILE",
            "SOURCE_TREE_MEMBER",
        ],
        "proposed_semantic_edges": [
            {"edge_type": "TESTS", "target": "ilc_core/economics/epoch_attribution_settle_runtime.py"},
            {"edge_type": "TESTS", "target": "ilc_core/types.py"},
            {"edge_type": "TESTS", "target": "docs/phases/phase_1350_cdl_083_ejected_stake_treasury_distribution_walkthrough.md"},
            {
                "edge_type": "COVERS_SYMBOL",
                "target": "ilc_core.economics.epoch_attribution_settle_runtime.build_ejected_stake_treasury_distribution_quote",
            },
            {
                "edge_type": "COVERS_SYMBOL",
                "target": "ilc_core.economics.epoch_attribution_settle_runtime.evaluate_ejected_stake_vote",
            },
            {
                "edge_type": "COVERS_SYMBOL",
                "target": "ilc_core.economics.epoch_attribution_settle_runtime.require_h_con_02_quorum_guard",
            },
            {
                "edge_type": "COVERS_SYMBOL",
                "target": "ilc_core.economics.epoch_attribution_settle_runtime.require_production_ejected_stake_distribution_activation",
            },
            {"edge_type": "EVIDENCES", "target": "phase:1350_cdl_083_runtime_boundary"},
            {"edge_type": "REGRESSES", "target": "invariant:ejected_stake_distribution_default_off"},
        ],
        "proposed_authority_trace_edges": [
            {
                "edge_type": "REFERENCES_AUTHORITY",
                "target": "cdl:083_panel_quorum",
                "review_status": "candidate_role_specific_authority_trace",
            }
        ],
        "recommended_graph_action": "materialize CDL-083 runtime TESTS and COVERS_SYMBOL edges",
    },
    "tests/test_phase_1388a_cdl_048_self_counsel_clearance.py": {
        "manual_read_summary": (
            "Validates Phase 1388a self-counsel clearance for CDL-048 activation, "
            "including the no-external-legal-advice boundary, licensing/CDL-086 "
            "references, and no public claimability activation."
        ),
        "proposed_trace_roles": [
            "TESTS",
            "NEGATIVE_ASSERTS",
            "EVIDENCES",
            "REGRESSES",
            "REFERENCES_AUTHORITY",
            "REQUIRES_PROFILE",
            "SOURCE_TREE_MEMBER",
        ],
        "proposed_semantic_edges": [
            {"edge_type": "TESTS", "target": "docs/specs/ilc_counsel_clearance_cdl_048_activation_1388a_v0.1.md"},
            {"edge_type": "TESTS", "target": "docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md"},
            {"edge_type": "TESTS", "target": "LICENSING.md"},
            {"edge_type": "TESTS", "target": "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"},
            {"edge_type": "NEGATIVE_ASSERTS", "target": "claim:external_legal_advice"},
            {"edge_type": "REGRESSES", "target": "invariant:no_public_claimability_activation"},
            {"edge_type": "EVIDENCES", "target": "phase:1388a_self_counsel_clearance"},
        ],
        "proposed_authority_trace_edges": [
            {
                "edge_type": "REFERENCES_AUTHORITY",
                "target": "cdl:048_activation_counsel_clearance",
                "review_status": "candidate_policy_terminal_requires_review",
            },
            {
                "edge_type": "REFERENCES_AUTHORITY",
                "target": "docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md",
                "review_status": "candidate_role_specific_authority_trace",
            },
        ],
        "recommended_graph_action": "materialize CDL-048 clearance and negative-claim edges",
    },
    "tests/test_phase_447_consensus_adversarial_regression.py": {
        "manual_read_summary": (
            "Validates Phase 447 consensus adversarial regression findings, "
            "epoch-state and finality-evaluator runtime surfaces, quorum/fork "
            "failure cases, and historical non-mutation boundaries."
        ),
        "proposed_trace_roles": [
            "TESTS",
            "COVERS_SYMBOL",
            "EVIDENCES",
            "REGRESSES",
            "REFERENCES_AUTHORITY",
            "REQUIRES_PROFILE",
            "SOURCE_TREE_MEMBER",
        ],
        "proposed_semantic_edges": [
            {"edge_type": "TESTS", "target": "ilc_core/consensus/epoch_state_runtime.py"},
            {"edge_type": "TESTS", "target": "ilc_core/consensus/finality_evaluator.py"},
            {"edge_type": "TESTS", "target": "docs/specs/ilc_consensus_findings_memo_447_v0.1.md"},
            {"edge_type": "TESTS", "target": "out/runtime_baseline/phase_446_report.json"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.consensus.epoch_state_runtime.generate_epoch_state_record"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.consensus.epoch_state_runtime.generate_quorum_record"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.consensus.epoch_state_runtime.verify_quorum_record"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.consensus.finality_evaluator.evaluate_epoch_finality"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.consensus.finality_evaluator.resolve_fork"},
            {"edge_type": "EVIDENCES", "target": "phase:447_consensus_adversarial_regression"},
            {"edge_type": "REGRESSES", "target": "invariant:adversarial_consensus_fail_closed"},
            {"edge_type": "REQUIRES_PROFILE", "target": "executor_profile:git_history_available"},
        ],
        "proposed_authority_trace_edges": [
            {
                "edge_type": "REFERENCES_AUTHORITY",
                "target": "cdl:051_epoch_state_quorum",
                "review_status": "candidate_role_specific_authority_trace",
            }
        ],
        "recommended_graph_action": "materialize consensus runtime TESTS, COVERS_SYMBOL, and CDL-051 trace edges",
    },
    "tests/test_phase_676_window_671_676_closure_and_handoff.py": {
        "manual_read_summary": (
            "Validates Window 671-676 closure and handoff: threat model, "
            "exclusion matrix, exitability threshold, rows 7-8 criteria/decision, "
            "checklist state, context capsule, historical planning notes, and "
            "commit path-scope constraints."
        ),
        "proposed_trace_roles": [
            "TESTS",
            "EVIDENCES",
            "REGRESSES",
            "REFERENCES_AUTHORITY",
            "REQUIRES_PROFILE",
            "SOURCE_TREE_MEMBER",
        ],
        "proposed_semantic_edges": [
            {"edge_type": "TESTS", "target": "docs/specs/ilc_censorship_resistance_threat_model_672_v0.1.md"},
            {"edge_type": "TESTS", "target": "docs/specs/ilc_external_constitutional_center_and_exclusion_matrix_673_v0.1.md"},
            {"edge_type": "TESTS", "target": "docs/specs/ilc_exitability_and_replayability_threshold_674_v0.1.md"},
            {"edge_type": "TESTS", "target": "docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md"},
            {"edge_type": "TESTS", "target": "docs/specs/ilc_rows_7_8_ratification_or_threshold_decision_675_v0.1.md"},
            {"edge_type": "TESTS", "target": "docs/specs/ilc_window_671_676_handoff_676_v0.1.md"},
            {"edge_type": "TESTS", "target": "docs/specs/ilc_option_b_graduation_checklist_state_676_v0.1.json"},
            {"edge_type": "EVIDENCES", "target": "phase_window:671_676_closure_and_handoff"},
            {"edge_type": "REGRESSES", "target": "invariant:rows_7_8_closed_row_5_open"},
            {"edge_type": "REQUIRES_PROFILE", "target": "executor_profile:git_history_available"},
        ],
        "proposed_authority_trace_edges": [
            {
                "edge_type": "REFERENCES_AUTHORITY",
                "target": "docs/specs/ilc_rows_7_8_ratification_or_threshold_decision_675_v0.1.md",
                "review_status": "candidate_role_specific_authority_trace",
            }
        ],
        "recommended_graph_action": "materialize window-closure TESTS and rows 7-8 authority trace edges",
    },
    "tests/test_sidecar_query_completeness_1379.py": {
        "manual_read_summary": (
            "Validates ADR-0031 sidecar query completeness by testing all locked "
            "query types, unsupported query fail-closed behavior, ego-graph "
            "response structure, and no mutation/network/serving authority."
        ),
        "proposed_trace_roles": [
            "TESTS",
            "COVERS_SYMBOL",
            "NEGATIVE_ASSERTS",
            "EVIDENCES",
            "REFERENCES_AUTHORITY",
            "REQUIRES_PROFILE",
            "SOURCE_TREE_MEMBER",
        ],
        "proposed_semantic_edges": [
            {"edge_type": "TESTS", "target": "ilc_core/graph/sidecar_query_runtime.py"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.graph.sidecar_query_runtime.QUERY_TYPES"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.graph.sidecar_query_runtime.SidecarQuery"},
            {"edge_type": "COVERS_SYMBOL", "target": "ilc_core.graph.sidecar_query_runtime.execute_sidecar_query"},
            {"edge_type": "NEGATIVE_ASSERTS", "target": "claim:sidecar_mutation_or_network_serving_authority"},
            {"edge_type": "REGRESSES", "target": "invariant:unsupported_sidecar_query_fails_closed"},
            {"edge_type": "EVIDENCES", "target": "phase:1379_adr_0031_sidecar_query_completeness"},
        ],
        "proposed_authority_trace_edges": [
            {
                "edge_type": "REFERENCES_AUTHORITY",
                "target": "adr:0031_subgraph_homomorphism",
                "review_status": "candidate_role_specific_authority_trace",
            }
        ],
        "recommended_graph_action": "materialize sidecar runtime TESTS, COVERS_SYMBOL, and ADR-0031 trace edges",
    },
}

MANUAL_CONNECTIVITY_ANNOTATIONS: list[dict[str, Any]] = [
    {
        "repo_path": "tests/test_homoiconic_test_registry_forward_plan.py",
        "annotation_tranche": "tranche_001_missing_candidate_nodes_01_10",
        "connectivity_class": "forward_plan_document_validation",
        "proposed_tests_targets": [
            "docs/specs/ilc_homoiconic_test_registry_forward_plan_v0.1.md",
            "docs/testing/test_inventory.md",
            "docs/PLANNING_INDEX.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "support_plan_validation_no_direct_authority_claim",
        "manual_read_summary": "Validates that the homoiconic test registry forward plan exists, preserves pytest as executor, declares file/function/evidence node kinds, records role-specific test edge vocabulary, preserves non-authorizing boundaries, and is linked from inventory and planning.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_forward_plan_inventory_planning",
    },
    {
        "repo_path": "tests/test_homoiconic_test_registry_implementation_guidance.py",
        "annotation_tranche": "tranche_001_missing_candidate_nodes_01_10",
        "connectivity_class": "implementation_guidance_and_window_validation",
        "proposed_tests_targets": [
            "docs/specs/ilc_homoiconic_test_registry_implementation_guidance_v0.1.md",
            "docs/specs/ilc_homoiconic_test_registry_forward_plan_v0.1.md",
            "docs/specs/ilc_window_1576_1584_homoiconic_test_registry_candidate_phase_grouping_v0.1.md",
            "docs/testing/test_inventory.md",
            "docs/PLANNING_INDEX.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "support_plan_validation_no_direct_authority_claim",
        "manual_read_summary": "Validates guidance pushback, concrete Fix32-Fix38 route, enriched-artifact checker input, lower-information fallback, registry/hydration/plugin sidecar sequencing, and Window 1576-1584 tokens and non-claims.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_guidance_forward_plan_window_inventory_planning",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix22_full_repo_genesis_atlas.py",
        "annotation_tranche": "tranche_001_missing_candidate_nodes_01_10",
        "connectivity_class": "full_repo_atlas_candidate_artifact_validation",
        "proposed_tests_targets": [
            "out/sim_full_repo_genesis_atlas_1545p_fix22.json",
            "out/genesis_atlas_full_repo_candidate_1545p_fix22.json",
            "out/genesis_atlas_full_repo_node_preimages_1545p_fix22.jsonl",
            "docs/sims/sim_full_repo_genesis_atlas_1545p_fix22_v0.1.md",
            "docs/specs/ilc_full_repo_genesis_atlas_candidate_review_packet_1545p_fix22_v0.1.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "generated_candidate_artifact_validation_unsigned_support_only",
        "manual_read_summary": "Validates full-repo candidate outputs, tracked-file coverage, public/private/generated tiers, deterministic unsigned preimages, endpoint safety, reachability, and non-claim boundaries.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_fix22_sim_graph_preimages_report_review",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix23_genesis_atlas_lmdb_materialization.py",
        "annotation_tranche": "tranche_001_missing_candidate_nodes_01_10",
        "connectivity_class": "lmdb_materialization_adapter_and_sim_validation",
        "proposed_tests_targets": [
            "ilc_core/storage/genesis_atlas_candidate_lmdb_adapter.py",
            "out/sim_genesis_atlas_lmdb_materialization_1545p_fix23.json",
            "docs/sims/sim_genesis_atlas_lmdb_materialization_1545p_fix23_v0.1.md",
            "docs/specs/ilc_genesis_atlas_lmdb_materialization_review_1545p_fix23_v0.1.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "runtime_adapter_test_plus_unsigned_materialization_evidence",
        "manual_read_summary": "Validates LMDB adapter version, materialization round trip, Fix22 source counts, digest identity, node/tier/source-path indexes, fail-closed missing-ID checks, and non-claim boundary docs.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_lmdb_adapter_and_fix23_artifacts",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix24_whole_graph_atlas_objective_contract.py",
        "annotation_tranche": "tranche_001_missing_candidate_nodes_01_10",
        "connectivity_class": "whole_graph_objective_contract_validation",
        "proposed_tests_targets": [
            "docs/specs/ilc_whole_graph_atlas_objective_contract_1545p_fix24_v0.1.md",
            "out/atlas_research/whole_graph_atlas_objective_contract_1545p_fix24.json",
            "docs/phases/phase_1545p_fix24_whole_graph_atlas_objective_contract_walkthrough.md",
            "docs/phases/STATUS.md",
            "docs/PLANNING_INDEX.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "contract_validation_with_explicit_no_authority_overclaim",
        "manual_read_summary": "Validates Fix24 tokens, genesis-rootedness standard, Phase 1573 scope mismatch, objective-vector field completeness, Tier 1/Tier 2 separation, conditional anti-gaming boundary, and non-claim language.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_fix24_contract_json_walkthrough_status_planning",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix25_whole_graph_baseline_diagnostic.py",
        "annotation_tranche": "tranche_001_missing_candidate_nodes_01_10",
        "connectivity_class": "whole_graph_baseline_diagnostic_validation",
        "proposed_tests_targets": [
            "out/sim_atlas_whole_graph_baseline_diagnostic_1545p_fix25.json",
            "docs/sims/sim_atlas_whole_graph_baseline_diagnostic_1545p_fix25_v0.1.md",
            "docs/specs/ilc_atlas_whole_graph_baseline_diagnostic_review_1545p_fix25_v0.1.md",
            "docs/phases/phase_1545p_fix25_whole_graph_baseline_diagnostic_walkthrough.md",
            "docs/phases/STATUS.md",
            "docs/PLANNING_INDEX.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "diagnostic_validation_not_authority_proof",
        "manual_read_summary": "Validates five separate coverage dimensions, directed-view gap counts, LMDB cross-checks, review queue schema, transition-envelope not-yet-implemented status, and Merkle/lambda2 non-overclaim boundaries.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_fix25_diagnostic_report_review_walkthrough_status_planning",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix26_axiomatic_extraction_replay.py",
        "annotation_tranche": "tranche_001_missing_candidate_nodes_01_10",
        "connectivity_class": "axiomatic_extraction_replay_validation",
        "proposed_tests_targets": [
            "out/sim_atlas_axiomatic_extraction_replay_1545p_fix26.json",
            "out/atlas_research/genesis_atlas_atom_candidates_1545p_fix26.jsonl",
            "out/genesis_atlas_full_repo_candidate_1545p_fix22.json",
            "docs/sims/sim_atlas_axiomatic_extraction_replay_1545p_fix26_v0.1.md",
            "docs/specs/ilc_atlas_axiomatic_extraction_replay_review_1545p_fix26_v0.1.md",
            "docs/phases/phase_1545p_fix26_axiomatic_extraction_replay_walkthrough.md",
            "docs/phases/STATUS.md",
            "docs/PLANNING_INDEX.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "atom_candidate_queue_validation_no_promotion",
        "manual_read_summary": "Validates Fix26 queue counts and schema, non-promotional candidate classes, calibration gates, accepted terminal constraints, denominator lock, trace orientation, AST/text method counts, deferred carry-forward fields, and non-claim docs.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_fix26_sim_atom_queue_graph_report_review_walkthrough_status_planning",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix27_rewrite_candidate_generation.py",
        "annotation_tranche": "tranche_001_missing_candidate_nodes_01_10",
        "connectivity_class": "rewrite_candidate_generation_validation",
        "proposed_tests_targets": [
            "out/sim_atlas_rewrite_candidate_generation_1545p_fix27.json",
            "out/atlas_research/genesis_atlas_rewrite_candidates_1545p_fix27.jsonl",
            "out/genesis_atlas_full_repo_candidate_1545p_fix22.json",
            "tools/evaluators/sim_atlas_rewrite_candidate_generation_1545p_fix27.py",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "rewrite_candidate_validation_no_promotion",
        "manual_read_summary": "Validates Fix27 candidate counts, DPO invariant summary, rule families, record fields, proof-class deltas, B10-B12 fallback reclassification, and preservation of Fix22 baseline counts.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_fix27_summary_candidates_fix22_graph_runner",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix28_projection_hydration_sim.py",
        "annotation_tranche": "tranche_001_missing_candidate_nodes_01_10",
        "connectivity_class": "projection_hydration_sim_validation",
        "proposed_tests_targets": [
            "tools/evaluators/sim_atlas_projection_hydration_1545p_fix28.py",
            "out/sim_atlas_projection_hydration_1545p_fix28.json",
            "out/atlas_research/genesis_atlas_projection_hydration_slices_1545p_fix28.json",
            "docs/sims/sim_atlas_projection_hydration_1545p_fix28_v0.1.md",
            "docs/specs/ilc_atlas_projection_hydration_review_1545p_fix28_v0.1.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "projection_hydration_validation_not_public_serving",
        "manual_read_summary": "Validates fallback filter application, projection slice schema, privacy redaction, reachability loss annotations, permission denial slice, and public-serving/non-authority boundaries.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_fix28_runner_summary_slices_report_review",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix29_spectral_non_excisability_sim.py",
        "annotation_tranche": "tranche_001_missing_candidate_nodes_01_10",
        "connectivity_class": "spectral_non_excisability_sim_validation",
        "proposed_tests_targets": [
            "tools/evaluators/sim_atlas_spectral_non_excisability_1545p_fix29.py",
            "out/sim_atlas_spectral_non_excisability_1545p_fix29.json",
            "docs/sims/sim_atlas_spectral_non_excisability_1545p_fix29_v0.1.md",
            "docs/specs/ilc_atlas_spectral_non_excisability_review_1545p_fix29_v0.1.md",
            "docs/phases/phase_1545p_fix29_spectral_non_excisability_sim_walkthrough.md",
            "docs/phases/STATUS.md",
            "docs/PLANNING_INDEX.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "spectral_structural_validation_not_authority_proof",
        "manual_read_summary": "Validates Fix29 tokens, clique and star Laplacian method disclosure, Fiedler export scope, authority-semantics firewall, non-excisability probe families, negative controls, and non-claim docs.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_fix29_runner_summary_report_review_walkthrough_status_planning",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix30_long_autoresearch_optimization.py",
        "annotation_tranche": "tranche_002_missing_candidate_nodes_tail_11_14",
        "connectivity_class": "long_autoresearch_optimization_validation",
        "proposed_tests_targets": [
            "out/sim_atlas_long_autoresearch_optimization_1545p_fix30.json",
            "out/atlas_research/genesis_atlas_autoresearch_iterations_1545p_fix30.jsonl",
            "out/atlas_research/genesis_atlas_optimized_candidate_1545p_fix30.json",
            "docs/sims/sim_atlas_long_autoresearch_optimization_1545p_fix30_v0.1.md",
            "docs/specs/ilc_atlas_long_autoresearch_optimization_review_1545p_fix30_v0.1.md",
            "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix30_g10_long_autoresearch_optimization_run.md",
            "out/atlas_research/fix30_checkpoints",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "autoresearch_candidate_validation_research_only",
        "manual_read_summary": "Validates Fix30 output tokens, 200-iteration budget, KEEP counts, checkpoints, hard invariants, Fiedler firewall, optimized candidate research-only status, added-edge boundaries, and no placeholder/non-claim language.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_fix30_summary_iterations_candidate_report_review_prompt_checkpoints",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix31_candidate_reducer_v04_v05.py",
        "annotation_tranche": "tranche_002_missing_candidate_nodes_tail_11_14",
        "connectivity_class": "candidate_reducer_decision_packet_validation",
        "proposed_tests_targets": [
            "out/sim_atlas_candidate_reducer_v04_v05_1545p_fix31.json",
            "out/atlas_research/genesis_atlas_v04_v05_candidate_variants_1545p_fix31.json",
            "out/atlas_research/genesis_atlas_public_private_batch_plan_1545p_fix31.json",
            "docs/sims/sim_atlas_candidate_reducer_v04_v05_1545p_fix31_v0.1.md",
            "docs/specs/ilc_genesis_atlas_v04_v05_candidate_decision_packet_1545p_fix31_v0.1.md",
            "docs/phases/phase_1545p_fix31_candidate_reducer_v04_v05_walkthrough.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "decision_packet_validation_not_signing_decision",
        "manual_read_summary": "Validates Fix31 variant boundaries, Phase 1573 scope compatibility, proof classes, signing-batch records, source context stability, human scope gate, decision packet non-claims, and no placeholder text.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_fix31_summary_variants_batch_plan_report_packet_walkthrough",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix32_homoiconic_test_registry_contract.py",
        "annotation_tranche": "tranche_002_missing_candidate_nodes_tail_11_14",
        "connectivity_class": "homoiconic_test_registry_contract_validation",
        "proposed_tests_targets": [
            "docs/specs/ilc_homoiconic_test_registry_contract_1545p_fix32_v0.1.md",
            "docs/specs/ilc_homoiconic_test_registry_implementation_route_1545p_fix32_v0.1.md",
            "docs/phases/phase_1545p_fix32_homoiconic_test_registry_contract_walkthrough.md",
            "docs/phases/STATUS.md",
            "docs/PLANNING_INDEX.md",
            "docs/testing/test_inventory.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "test_registry_contract_validation_no_runtime_executor_activation",
        "manual_read_summary": "Validates Fix32 contract tokens, test node schemas, pytest nodeid identity boundary, edge vocabulary, executor gating, non-authorization boundaries, successor route, section numbering, and planning/inventory references.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_fix32_contract_route_walkthrough_status_planning_inventory",
    },
    {
        "repo_path": "tests/test_phase_1545p_fix33_test_graph_coverage.py",
        "annotation_tranche": "tranche_002_missing_candidate_nodes_tail_11_14",
        "connectivity_class": "test_graph_coverage_checker_validation",
        "proposed_tests_targets": [
            "out/test_graph_coverage_1545p_fix33.json",
            "docs/specs/ilc_test_graph_coverage_report_1545p_fix33_v0.1.md",
            "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix33_g10_test_node_atlas_smoke_audit.md",
            "tools/check_test_graph_coverage.py",
            "docs/phases/phase_1545p_fix33_test_node_atlas_smoke_audit_walkthrough.md",
            "docs/phases/STATUS.md",
            "docs/PLANNING_INDEX.md",
        ],
        "proposed_trace_roles": ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
        "executor_profile": "default_local_pytest",
        "authority_trace_expectation": "checker_validation_report_first_no_execution",
        "manual_read_summary": "Validates Fix33 enriched graph scope, report-first mode, file mapping, gap classes, executor profiles, ordinary runtime test authority boundary, non-claims, fallback boundary, and deterministic JSON requirements.",
        "recommended_graph_action": "create_test_file_node_and_TESTS_edges_to_fix33_summary_report_prompt_tool_walkthrough_status_planning",
    },
]


class FrontierReportError(ValueError):
    pass


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def report_digest(payload: dict[str, Any]) -> str:
    """Digest semantic report content, not caller-specific output paths."""
    normalized = json.loads(json.dumps(payload, sort_keys=True, allow_nan=False))
    normalized.pop("report_digest", None)
    candidate_summary = normalized.get("unified_candidate_summary")
    if isinstance(candidate_summary, dict):
        candidate_summary["candidate_path"] = "<candidate_out>"
    return "test_frontier_report:" + sha256_bytes(canonical_bytes(normalized))[:32]


def atomic_canonical_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(canonical_bytes(payload))
            handle.write(b"\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manual_edge_ledger(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = load_json(path)
    if payload.get("phase") != PHASE:
        raise FrontierReportError("manual_edge_ledger_phase_mismatch")
    annotations = payload.get("annotations", [])
    if not isinstance(annotations, list):
        raise FrontierReportError("manual_edge_ledger_annotations_not_list")
    by_path: dict[str, dict[str, Any]] = {}
    for annotation in annotations:
        repo_path = annotation.get("repo_path")
        if not repo_path:
            # Later phases may append carry-forward graph annotations with a
            # different schema (for example `path` plus `proposed_edges`).
            # Fix38 regeneration consumes only the original repo_path-indexed
            # manual-read rows, so ignore non-Fix38 rows deterministically.
            continue
        by_path[str(repo_path)] = {
            "manual_read_summary": annotation["manual_read_summary"],
            "proposed_trace_roles": annotation["proposed_trace_roles"],
            "proposed_semantic_edges": annotation["proposed_semantic_edges"],
            "proposed_authority_trace_edges": annotation["proposed_authority_trace_edges"],
            "recommended_graph_action": annotation["recommended_graph_action"],
        }
    return by_path


def sample(items: list[Any], limit: int = 20) -> list[Any]:
    return items[:limit]


def path_to_candidate_id(repo_path: str, source_sha256: str) -> str:
    safe = repo_path.replace("/", "_").replace(".", "_").replace("-", "_")
    return f"repo:file:{source_sha256[:16]}:{safe}"


def require_file(path: Path) -> None:
    if not path.exists():
        raise FrontierReportError(f"required_input_missing:{path}")


def load_graph(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise FrontierReportError("graph_payload_not_object")
    return payload


def graph_test_target_gap(graph: dict[str, Any] | None) -> dict[str, Any]:
    if graph is None:
        return {
            "status": "not_measured_graph_missing",
            "runtime_source_node_count": 0,
            "runtime_source_without_tests_edge_count": 0,
            "authority_document_node_count": 0,
            "authority_document_without_tests_edge_count": 0,
            "runtime_source_without_tests_edge_sample": [],
            "authority_document_without_tests_edge_sample": [],
        }

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise FrontierReportError("graph_nodes_or_edges_not_list")

    tests_targets = {
        str(edge.get("target"))
        for edge in edges
        if isinstance(edge, dict) and edge.get("edge_type") == "TESTS"
    }
    runtime_nodes = [
        node
        for node in nodes
        if isinstance(node, dict)
        and (
            str(node.get("source_path", "")).startswith("ilc_core/")
            or str(node.get("label", "")).startswith("ilc_core/")
        )
    ]
    authority_nodes = [
        node
        for node in nodes
        if isinstance(node, dict)
        and (
            str(node.get("source_path", "")).startswith("docs/adr/")
            or str(node.get("source_path", "")).startswith("docs/specs/ilc_cdl")
            or str(node.get("node_kind", "")).lower() in {"adr", "cdl", "policy"}
            or str(node.get("candidate_id", "")).startswith(("adr:", "cdl:", "policy:"))
        )
    ]

    runtime_without = [
        {
            "candidate_id": node.get("candidate_id"),
            "source_path": node.get("source_path") or node.get("label"),
        }
        for node in runtime_nodes
        if node.get("candidate_id") not in tests_targets
    ]
    authority_without = [
        {
            "candidate_id": node.get("candidate_id"),
            "source_path": node.get("source_path") or node.get("label"),
        }
        for node in authority_nodes
        if node.get("candidate_id") not in tests_targets
    ]
    return {
        "status": "approximate_graph_TESTS_target_metric",
        "runtime_source_node_count": len(runtime_nodes),
        "runtime_source_without_tests_edge_count": len(runtime_without),
        "authority_document_node_count": len(authority_nodes),
        "authority_document_without_tests_edge_count": len(authority_without),
        "runtime_source_without_tests_edge_sample": sample(runtime_without, 20),
        "authority_document_without_tests_edge_sample": sample(authority_without, 20),
    }


def resolve_import_target(module: str, repo_root: Path) -> str | None:
    rel = module.replace(".", "/")
    for candidate in (Path(f"{rel}.py"), Path(rel) / "__init__.py"):
        if (repo_root / candidate).is_file():
            return candidate.as_posix()
    return None


def existing_phase_targets(text: str, repo_path: str, repo_root: Path) -> list[str]:
    tokens = {
        match.group("phase").lower().replace("-", "_")
        for match in PHASE_TOKEN_RE.finditer(text + "\n" + repo_path)
    }
    targets: set[str] = set()
    def allowed_target(path: str) -> bool:
        if path in FIX38_EXCLUDED_GENERATED_TARGETS:
            return False
        match = PHASE_PATH_RE.search(path)
        if match is None:
            return True
        phase = match.group("phase").lower()
        fix = match.group("fix")
        if phase == "1545p" and fix is not None and int(fix) > 38:
            return False
        return True

    for token in tokens:
        for pattern in (
            f"docs/phases/phase_{token}*.md",
            f"docs/antigravity_tasks/antigravity_prompt__phase_{token}*.md",
            f"docs/specs/*{token}*.md",
            f"docs/sims/*{token}*.md",
            f"out/*{token}*.json",
            f"out/atlas_research/*{token}*.json",
            f"out/atlas_research/*{token}*.jsonl",
        ):
            targets.update(
                path.relative_to(repo_root).as_posix()
                for path in repo_root.glob(pattern)
                if path.is_file() and allowed_target(path.relative_to(repo_root).as_posix())
            )
    return sorted(targets)


def extract_targets_from_source(
    repo_path: str,
    source_text: str,
    repo_root: Path,
    existing_graph_targets: list[str],
) -> dict[str, Any]:
    path_targets: set[str] = set()
    import_targets: set[str] = set()
    graph_targets = {f"graph_node:{target}" for target in existing_graph_targets}

    for match in PATH_LITERAL_RE.finditer(source_text):
        target = match.group("path")
        if target != repo_path and (repo_root / target).exists():
            path_targets.add(target)

    for match in IMPORT_RE.finditer(source_text):
        target = resolve_import_target(match.group("module"), repo_root)
        if target is not None:
            import_targets.add(target)

    phase_targets = set(existing_phase_targets(source_text, repo_path, repo_root))
    all_targets = sorted(graph_targets | path_targets | import_targets | phase_targets)
    if not all_targets:
        all_targets = ["manual_review_required_no_target_extracted"]

    return {
        "existing_graph_targets": sorted(graph_targets),
        "path_literal_targets": sorted(path_targets),
        "import_targets": sorted(import_targets),
        "phase_token_targets": sorted(phase_targets),
        "proposed_tests_targets": all_targets,
    }


def classify_gap_record(repo_path: str, source_text: str, gap_classes: list[str]) -> str:
    lower = (repo_path + "\n" + source_text[:2000]).lower()
    if "adr" in lower:
        return "adr_or_governance_validation"
    if "cdl" in lower:
        return "cdl_or_constitutional_validation"
    if "phase_" in lower or "phase-" in lower:
        return "phase_artifact_validation"
    if "ilc_core" in lower:
        return "runtime_or_protocol_module_validation"
    if "homoiconic" in lower or "test_registry" in lower:
        return "homoiconic_test_registry_validation"
    if "missing_expected_authority_trace" in gap_classes:
        return "authority_trace_review_required"
    return "general_test_frontier_validation"


def build_frontier_gap_annotations(
    records: list[dict[str, Any]],
    repo_root: Path,
    curated_annotations: dict[str, dict[str, Any]],
    curated_edge_annotations: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    frontier_records = [
        record
        for record in records
        if set(record.get("gap_classes", []))
        & {"missing_candidate_node", "missing_tests_edge", "missing_expected_authority_trace"}
    ]
    annotations: list[dict[str, Any]] = []
    for index, record in enumerate(sorted(frontier_records, key=lambda row: row["repo_path"]), start=1):
        repo_path = record["repo_path"]
        path = repo_root / repo_path
        if not path.is_file():
            raise FrontierReportError(f"frontier_gap_source_missing:{repo_path}")
        source_text = path.read_text(encoding="utf-8")
        source_sha256 = sha256_file(path)
        target_evidence = extract_targets_from_source(
            repo_path,
            source_text,
            repo_root,
            list(record.get("tests_targets", [])),
        )
        gap_classes = list(record.get("gap_classes", []))
        batch_start = ((index - 1) // 10) * 10 + 1
        batch_end = min(batch_start + 9, len(frontier_records))
        curated = {
            **curated_annotations.get(repo_path, {}),
            **curated_edge_annotations.get(repo_path, {}),
        }
        authority_expected = "missing_expected_authority_trace" in gap_classes
        missing_tests = "missing_tests_edge" in gap_classes
        missing_candidate = "missing_candidate_node" in gap_classes
        annotation = {
            "annotation_batch": f"batch_{((index - 1) // 10) + 1:03d}_frontier_files_{batch_start:04d}_{batch_end:04d}",
            "annotation_index": index,
            "annotation_source": "direct_file_read_phase_1545p_fix38",
            "repo_path": repo_path,
            "source_sha256": source_sha256,
            "gap_classes_before_annotation": gap_classes,
            "candidate_node_status_before_annotation": record.get("candidate_node_status"),
            "connectivity_class": curated.get(
                "connectivity_class",
                classify_gap_record(repo_path, source_text, gap_classes),
            ),
            "executor_profiles": record.get("executor_profiles", []),
            "environment_gates": record.get("environment_gates", []),
            "default_query_visibility": record.get("default_query_visibility"),
            "proposed_candidate_node_id": path_to_candidate_id(repo_path, source_sha256),
            "proposed_node_kind": "test_file",
            "proposed_trace_roles": curated.get(
                "proposed_trace_roles",
                ["TESTS", "REQUIRES_PROFILE", "SOURCE_TREE_MEMBER"],
            ),
            "target_extraction": target_evidence,
            "proposed_tests_targets": target_evidence["proposed_tests_targets"],
            "authority_trace_expectation": (
                "role_specific_authority_trace_review_required_not_auto_closed"
                if authority_expected
                else "ordinary_test_trace_no_authority_claim"
            ),
            "tests_edge_annotation_status": (
                "candidate_TESTS_targets_extracted_for_review"
                if missing_tests or missing_candidate
                else "existing_TESTS_edges_retained"
            ),
            "authority_trace_annotation_status": (
                "candidate_authority_trace_requires_role_specific_review"
                if authority_expected
                else "authority_trace_not_expected_for_this_gap"
            ),
            "manual_read_summary": curated.get(
                "manual_read_summary",
                (
                    "Direct-read extraction recorded existing graph targets, path literals, "
                    "imports, and phase-token targets for later graph refresh review."
                ),
            ),
            "recommended_graph_action": curated.get(
                "recommended_graph_action",
                "review_extracted_targets_then_materialize_candidate_TESTS_or_authority_trace_edges",
            ),
            "gap_annotation_status": "manual_annotation_complete_graph_not_mutated",
        }
        if repo_path in curated_edge_annotations:
            annotation["curated_edge_batch_source"] = CURATED_EDGE_BATCH_SOURCE
            annotation["proposed_semantic_edges"] = curated["proposed_semantic_edges"]
            annotation["proposed_authority_trace_edges"] = curated[
                "proposed_authority_trace_edges"
            ]
            annotation["curated_edge_annotation_status"] = (
                "best_effort_manual_edges_recorded_for_graph_refresh_review"
            )
        annotations.append(annotation)

    batches: dict[str, int] = {}
    for annotation in annotations:
        batches[annotation["annotation_batch"]] = batches.get(annotation["annotation_batch"], 0) + 1

    return {
        "annotation_mode": "manual_direct_read_batches_all_fix33_frontier_gaps",
        "batch_size_policy": "batches_of_10",
        "frontier_gap_file_count": len(frontier_records),
        "frontier_gap_annotation_count": len(annotations),
        "frontier_gap_annotation_coverage": f"{len(annotations)}/{len(frontier_records)}",
        "batch_count": len(batches),
        "batch_record_counts": dict(sorted(batches.items())),
        "annotations": annotations,
    }


def _git_chronology(repo_root: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            "git",
            "log",
            "--reverse",
            "--date=iso-strict",
            "--format=@@@%ct\t%cI\t%H\t%s",
            "--name-only",
            "--",
            "tests",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return {"status": "unavailable", "reason": result.stderr.strip()[:200]}

    current: dict[str, Any] | None = None
    by_path: dict[str, dict[str, Any]] = {}
    by_commit: dict[str, set[str]] = {}
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("@@@"):
            epoch, iso, commit, subject = line[3:].split("\t", 3)
            current = {
                "epoch": int(epoch),
                "committed_at": iso,
                "commit": commit[:12],
                "subject": subject,
            }
            by_commit.setdefault(current["commit"], set())
            continue
        if current is None or not line.startswith("tests/") or not line.endswith(".py"):
            continue
        by_commit.setdefault(current["commit"], set()).add(line)
        entry = by_path.setdefault(line, {"path": line, "earliest": current, "latest": current})
        entry["latest"] = current

    ordered = sorted(
        by_path.values(),
        key=lambda item: (item["earliest"]["epoch"], item["path"]),
    )
    return {"status": "available", "ordered": ordered, "by_commit": by_commit}


def build_curated_edge_batch(
    records: list[dict[str, Any]],
    repo_root: Path,
    curated_edge_annotations: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    record_by_path = {record["repo_path"]: record for record in records}
    chronology = _git_chronology(repo_root)
    ordered = chronology.get("ordered", []) if chronology.get("status") == "available" else []
    by_commit = chronology.get("by_commit", {}) if chronology.get("status") == "available" else {}
    ordered_index = {item["path"]: index for index, item in enumerate(ordered)}

    annotations: list[dict[str, Any]] = []
    for repo_path, curated in sorted(curated_edge_annotations.items()):
        path = repo_root / repo_path
        if not path.is_file():
            raise FrontierReportError(f"curated_edge_source_missing:{repo_path}")
        source_sha256 = sha256_file(path)
        record = record_by_path.get(repo_path, {})
        chronological_context: dict[str, Any] = {"status": chronology.get("status")}
        if repo_path in ordered_index:
            index = ordered_index[repo_path]
            current = ordered[index]
            same_commit_paths = sorted(
                path
                for path in by_commit.get(current["earliest"]["commit"], set())
                if path != repo_path
            )
            chronological_context.update(
                {
                    "earliest_commit": current["earliest"],
                    "latest_commit": current["latest"],
                    "chronological_neighbor_before": (
                        ordered[index - 1] if index > 0 else None
                    ),
                    "chronological_neighbor_after": (
                        ordered[index + 1] if index + 1 < len(ordered) else None
                    ),
                    "same_earliest_commit_test_files": same_commit_paths[:20],
                    "same_earliest_commit_test_file_count": len(same_commit_paths),
                    "chronology_use": (
                        "supporting_cluster_evidence_only_direct_read_edges_remain_primary"
                    ),
                }
            )
        annotations.append(
            {
                "annotation_source": CURATED_EDGE_BATCH_SOURCE,
                "repo_path": repo_path,
                "source_sha256": source_sha256,
                "candidate_node_status_before_annotation": record.get(
                    "candidate_node_status", "not_in_fix33_record"
                ),
                "gap_classes_before_annotation": record.get("gap_classes", []),
                "proposed_candidate_node_id": path_to_candidate_id(repo_path, source_sha256),
                "proposed_node_kind": "test_file",
                "proposed_trace_roles": curated["proposed_trace_roles"],
                "proposed_semantic_edges": curated["proposed_semantic_edges"],
                "proposed_authority_trace_edges": curated["proposed_authority_trace_edges"],
                "manual_read_summary": curated["manual_read_summary"],
                "recommended_graph_action": curated["recommended_graph_action"],
                "git_chronology_context": chronological_context,
                "promotion_status": "candidate_edge_overlay_for_graph_refresh_only",
                "canonical_mutation_status": "not_mutated",
                "edge_annotation_status": (
                    "best_effort_manual_edges_recorded_for_later_agent_review"
                ),
            }
        )

    semantic_edge_count = sum(
        len(item["proposed_semantic_edges"]) for item in annotations
    )
    authority_edge_count = sum(
        len(item["proposed_authority_trace_edges"]) for item in annotations
    )
    return {
        "annotation_mode": "curated_best_effort_direct_read_edge_overlay",
        "annotation_source": CURATED_EDGE_BATCH_SOURCE,
        "chronology_source": "git_log_reverse_tests_path_supporting_evidence",
        "manual_edge_annotation_count": len(annotations),
        "semantic_edge_count": semantic_edge_count,
        "authority_trace_edge_count": authority_edge_count,
        "edge_overlay_scope": "candidate_graph_refresh_review_not_canonical",
        "annotations": annotations,
    }


def _safe_node_suffix(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_").lower()[:160]


def _edge_id(source: str, edge_type: str, target: str, provenance: str) -> str:
    payload = {
        "edge_type": edge_type,
        "provenance": provenance,
        "source": source,
        "target": target,
    }
    return "edge:fix38:" + sha256_bytes(canonical_bytes(payload))[:32]


def _target_node_kind(target: str) -> str:
    if target.startswith("adr:"):
        return "authority_terminal_adr"
    if target.startswith("cdl:"):
        return "authority_terminal_cdl"
    if target.startswith("policy:"):
        return "authority_terminal_policy"
    if target.startswith("phase:") or target.startswith("phase_window:"):
        return "phase_terminal"
    if target.startswith("sim:"):
        return "sim_terminal"
    if target.startswith("invariant:"):
        return "invariant_terminal"
    if target.startswith("claim:"):
        return "claim_terminal"
    if target.startswith("command:"):
        return "command_terminal"
    if target.startswith("api_route:"):
        return "api_route_terminal"
    if target.startswith("executor_profile:"):
        return "executor_profile_terminal"
    if target.startswith("repo_dir:"):
        return "repo_directory_terminal"
    if target.startswith("graph_node:"):
        return "existing_graph_node_reference"
    return "support_artifact"


def _target_to_candidate_id(
    target: str,
    repo_root: Path,
    path_node_cache: dict[str, str],
) -> str:
    if target.startswith("graph_node:"):
        return target.removeprefix("graph_node:")
    if target.startswith(("adr:", "cdl:", "policy:", "phase:", "phase_window:", "sim:", "invariant:", "claim:", "command:", "api_route:", "executor_profile:", "repo_dir:")):
        return target
    if target in path_node_cache:
        return path_node_cache[target]
    path = repo_root / target
    if path.is_file():
        # Target artifacts can include generated reports from this same phase.
        # Use path-stable reference IDs to avoid recursive digest churn when a
        # report is regenerated while preserving content-hashed source test IDs.
        node_id = f"repo:file_ref:{_safe_node_suffix(target)}"
    else:
        node_id = f"target:{_safe_node_suffix(target)}"
    path_node_cache[target] = node_id
    return node_id


def _authority_edge_targets(annotation: dict[str, Any]) -> list[dict[str, Any]]:
    explicit = annotation.get("proposed_authority_trace_edges")
    if explicit:
        return list(explicit)
    if "missing_expected_authority_trace" not in annotation.get("gap_classes_before_annotation", []):
        return []
    targets: list[dict[str, Any]] = []
    for target in annotation.get("proposed_tests_targets", []):
        lower = str(target).lower()
        if (
            "/adr_" in lower
            or "docs/adr/" in lower
            or "ilc_cdl_" in lower
            or "constitutional_decision_log" in lower
            or "decision" in lower
            or "ratification" in lower
            or "counsel_clearance" in lower
        ):
            targets.append(
                {
                    "edge_type": "REFERENCES_AUTHORITY",
                    "target": target,
                    "review_status": "candidate_inferred_from_frontier_direct_read_targets",
                }
            )
    return targets[:5]


def build_unified_candidate(
    graph: dict[str, Any] | None,
    all_frontier_annotations: dict[str, Any],
    curated_edge_batch: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    base = graph or {
        "schema_version": "genesis_atlas_candidate.v0",
        "phase": PHASE,
        "candidate_status": "lower_information_fallback_no_base_graph",
        "nodes": [],
        "edges": [],
        "non_claims": [],
    }
    nodes = [dict(node) for node in base.get("nodes", [])]
    edges = [dict(edge) for edge in base.get("edges", [])]
    node_ids = {node.get("candidate_id") for node in nodes if node.get("candidate_id")}
    edge_ids = {edge.get("edge_id") for edge in edges if edge.get("edge_id")}
    path_node_cache: dict[str, str] = {}

    def ensure_node(node_id: str, node_kind: str, label: str, provenance: str) -> None:
        if node_id in node_ids:
            return
        nodes.append(
            {
                "candidate_id": node_id,
                "label": label,
                "category": node_kind,
                "canonicality_tier": "fix38_candidate_overlay",
                "confidence": 0.72 if provenance == CURATED_EDGE_BATCH_SOURCE else 0.55,
                "inclusion_status": "candidate_overlay",
                "genesis_attested": False,
                "authority_status": "candidate_review_required",
                "promotion_status": "candidate_only_not_canonical",
                "source_phase": PHASE,
                "provenance": provenance,
            }
        )
        node_ids.add(node_id)

    def add_edge(
        source: str,
        edge_type: str,
        target: str,
        provenance: str,
        confidence: float,
        rationale: str,
        review_status: str = "candidate_review_required",
    ) -> None:
        eid = _edge_id(source, edge_type, target, provenance)
        if eid in edge_ids:
            return
        edges.append(
            {
                "edge_id": eid,
                "source": source,
                "target": target,
                "edge_type": edge_type,
                "relation": edge_type.lower(),
                "confidence": confidence,
                "rationale": rationale,
                "provenance": provenance,
                "review_status": review_status,
                "source_phase": PHASE,
                "promotion_status": "candidate_only_not_canonical",
            }
        )
        edge_ids.add(eid)

    manifest_id = "artifact:genesis_source_tree_manifest_candidate_1545p_fix38"
    ensure_node(
        manifest_id,
        "source_tree_manifest_candidate",
        "Fix38 candidate source-tree manifest terminal",
        "fix38_unified_candidate_builder",
    )

    curated_by_path = {
        annotation["repo_path"]: annotation
        for annotation in curated_edge_batch.get("annotations", [])
    }
    annotations = all_frontier_annotations.get("annotations", [])
    for annotation in annotations:
        repo_path = annotation["repo_path"]
        source_id = annotation["proposed_candidate_node_id"]
        ensure_node(source_id, "test_file", repo_path, annotation["annotation_source"])
        add_edge(
            source_id,
            "SOURCE_TREE_MEMBER",
            manifest_id,
            annotation["annotation_source"],
            0.8,
            "Test file belongs to the candidate Genesis-governed source tree.",
            "membership_only_not_authority_trace",
        )
        for profile in annotation.get("executor_profiles", []):
            target_id = f"executor_profile:{_safe_node_suffix(str(profile))}"
            ensure_node(target_id, "executor_profile_terminal", str(profile), annotation["annotation_source"])
            add_edge(
                source_id,
                "REQUIRES_PROFILE",
                target_id,
                annotation["annotation_source"],
                0.8,
                "Executor profile recorded by Fix33 coverage analysis.",
                "candidate_execution_metadata",
            )
        for target in annotation.get("proposed_tests_targets", []):
            target_id = _target_to_candidate_id(str(target), repo_root, path_node_cache)
            ensure_node(
                target_id,
                _target_node_kind(str(target)),
                str(target),
                annotation["annotation_source"],
            )
            add_edge(
                source_id,
                "TESTS",
                target_id,
                annotation["annotation_source"],
                0.65,
                "Candidate TESTS edge extracted from direct file read targets.",
                "candidate_tests_edge_needs_review",
            )
        for authority_edge in _authority_edge_targets(annotation):
            target = str(authority_edge["target"])
            target_id = _target_to_candidate_id(target, repo_root, path_node_cache)
            ensure_node(
                target_id,
                _target_node_kind(target),
                target,
                annotation["annotation_source"],
            )
            add_edge(
                source_id,
                str(authority_edge.get("edge_type", "REFERENCES_AUTHORITY")),
                target_id,
                annotation["annotation_source"],
                0.55,
                "Candidate role-specific authority trace recorded for review.",
                str(authority_edge.get("review_status", "candidate_authority_trace_review_required")),
            )

        curated = curated_by_path.get(repo_path)
        if not curated:
            continue
        for semantic_edge in curated["proposed_semantic_edges"]:
            target = str(semantic_edge["target"])
            target_id = _target_to_candidate_id(target, repo_root, path_node_cache)
            ensure_node(
                target_id,
                _target_node_kind(target),
                target,
                CURATED_EDGE_BATCH_SOURCE,
            )
            add_edge(
                source_id,
                str(semantic_edge["edge_type"]),
                target_id,
                CURATED_EDGE_BATCH_SOURCE,
                0.86,
                curated["manual_read_summary"],
                "best_effort_curated_direct_read_edge",
            )
        for authority_edge in curated["proposed_authority_trace_edges"]:
            target = str(authority_edge["target"])
            target_id = _target_to_candidate_id(target, repo_root, path_node_cache)
            ensure_node(
                target_id,
                _target_node_kind(target),
                target,
                CURATED_EDGE_BATCH_SOURCE,
            )
            add_edge(
                source_id,
                str(authority_edge["edge_type"]),
                target_id,
                CURATED_EDGE_BATCH_SOURCE,
                0.78,
                "Best-effort role-specific authority trace from manual direct read.",
                str(authority_edge["review_status"]),
            )

    added_nodes = len(nodes) - len(base.get("nodes", []))
    added_edges = len(edges) - len(base.get("edges", []))
    candidate = {
        **base,
        "phase": PHASE,
        "candidate_status": "unsigned_support_only_not_canonical_fix38_unified_candidate",
        "source_base_graph_status": base.get("candidate_status", "unknown"),
        "fix38_overlay_summary": {
            "frontier_file_count": all_frontier_annotations["frontier_gap_file_count"],
            "frontier_annotation_coverage": all_frontier_annotations[
                "frontier_gap_annotation_coverage"
            ],
            "curated_manual_edge_file_count": curated_edge_batch["manual_edge_annotation_count"],
            "curated_semantic_edge_count": curated_edge_batch["semantic_edge_count"],
            "curated_authority_trace_edge_count": curated_edge_batch[
                "authority_trace_edge_count"
            ],
            "added_node_count": added_nodes,
            "added_edge_count": added_edges,
            "authority_edge_policy": (
                "candidate role-specific traces only; no GOVERNS edges from tests; "
                "no direct test-to-Genesis authority shortcut"
            ),
        },
        "nodes": nodes,
        "edges": edges,
        "non_claims": sorted(
            set(base.get("non_claims", []))
            | set(NON_CLAIMS)
            | {
                "fix38_unified_candidate_unsigned",
                "candidate_edges_not_promoted",
                "authority_trace_edges_require_later_review",
            }
        ),
    }
    candidate["candidate_digest"] = "fix38_unified_candidate:" + sha256_bytes(
        canonical_bytes(
            {
                "edges": candidate["edges"],
                "nodes": candidate["nodes"],
                "phase": candidate["phase"],
                "status": candidate["candidate_status"],
            }
        )
    )[:32]
    return candidate


def summarize_fix33(fix33: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    summary = fix33["summary"]
    records = fix33["file_records"]
    if summary.get("phase") != "1545p-Fix33" or summary.get("status") != "pass":
        raise FrontierReportError("fix33_not_pass")
    missing_candidates = [
        record for record in records if record.get("candidate_node_status") == "missing_candidate_node"
    ]
    missing_tests_edges = [
        record for record in records if "missing_tests_edge" in record.get("gap_classes", [])
    ]
    missing_authority = [
        record
        for record in records
        if "missing_expected_authority_trace" in record.get("gap_classes", [])
    ]
    return (
        {
            "coverage_input_scope": summary["coverage_input_scope"],
            "local_test_python_file_count": summary["local_test_python_file_count"],
            "mapped_test_file_count": summary["mapped_test_file_count"],
            "files_with_tests_edge_count": summary["files_with_tests_edge_count"],
            "missing_candidate_node_count": summary["missing_candidate_node_count"],
            "missing_tests_edge_count": summary["missing_tests_edge_count"],
            "dangling_tests_target_count": summary["dangling_tests_target_count"],
            "authority_trace_expected_file_count": summary["authority_trace_expected_file_count"],
            "authority_trace_satisfied_file_count": summary["authority_trace_satisfied_file_count"],
            "gap_class_counts": summary["gap_class_counts"],
            "executor_profile_counts": summary["executor_profile_counts"],
            "supplemental_tests_edge_count": summary["supplemental_tests_edge_count"],
            "missing_candidate_node_sample": [row["repo_path"] for row in missing_candidates],
            "missing_tests_edge_sample": [row["repo_path"] for row in sample(missing_tests_edges)],
            "missing_expected_authority_trace_sample": [
                row["repo_path"] for row in sample(missing_authority)
            ],
        },
        records,
    )


def summarize_fix34(fix34: dict[str, Any]) -> dict[str, Any]:
    summary = fix34["summary"]
    if summary.get("phase") != "1545p-Fix34" or summary.get("status") != "pass":
        raise FrontierReportError("fix34_not_pass")
    zero_inherited = [
        node
        for node in fix34["test_function_nodes"]
        if int(node.get("inherited_tests_target_count", 0)) == 0
    ]
    return {
        "collected_test_function_count": summary["collected_test_function_count"],
        "candidate_edge_count": summary["candidate_edge_count"],
        "deferred_record_count": summary["deferred_record_count"],
        "executor_profile_counts": summary["executor_profile_counts"],
        "environment_gate_counts": summary["environment_gate_counts"],
        "function_nodes_with_inherited_tests_targets_count": summary[
            "function_nodes_with_inherited_tests_targets_count"
        ],
        "function_nodes_without_inherited_tests_targets_count": len(zero_inherited),
        "function_nodes_without_inherited_tests_targets_sample": [
            {
                "pytest_nodeid": node["pytest_nodeid"],
                "repo_path": node["repo_path"],
            }
            for node in sample(zero_inherited, 20)
        ],
    }


def summarize_fix35(fix35: dict[str, Any]) -> dict[str, Any]:
    if fix35.get("phase") != "1545p-Fix35" or fix35.get("status") != "pass":
        raise FrontierReportError("fix35_not_pass")
    return {
        "sidecar_mode": fix35["sidecar_mode"],
        "selected_count": fix35["selected_count"],
        "selected_profile_counts": fix35["selected_profile_counts"],
        "selected_environment_gate_counts": fix35["selected_environment_gate_counts"],
        "execute_requested": fix35["execute_requested"],
        "default_dry_run": fix35["default_dry_run"],
    }


def summarize_fix36(fix36: dict[str, Any]) -> dict[str, Any]:
    if fix36.get("phase") != "1545p-Fix36" or fix36.get("status") != "pass":
        raise FrontierReportError("fix36_not_pass")
    return {
        "batch_id": fix36["batch_id"],
        "selected_count": fix36["selected_count"],
        "result_status_counts": fix36["result_status_counts"],
        "execution_scope": fix36["execution_scope"],
        "evidence_run_count": len(fix36["evidence_runs"]),
    }


def summarize_fix37(fix37: dict[str, Any]) -> dict[str, Any]:
    if fix37.get("phase") != "1545p-Fix37" or fix37.get("status") != "pass":
        raise FrontierReportError("fix37_not_pass")
    return {
        "batch_id": fix37["batch_id"],
        "selected_count": fix37["selected_count"],
        "excluded_count": fix37["excluded_count"],
        "hydrated_file_count": fix37["hydrated_file_count"],
        "result_status_counts": fix37["result_status_counts"],
        "execution_scope": fix37["execution_scope"],
        "excluded_commands": fix37["excluded_commands"],
    }


def enrich_manual_annotations(
    records: list[dict[str, Any]],
    repo_root: Path,
) -> dict[str, Any]:
    missing = {
        record["repo_path"]: record
        for record in records
        if record.get("candidate_node_status") == "missing_candidate_node"
    }
    annotations: list[dict[str, Any]] = []
    for annotation in MANUAL_CONNECTIVITY_ANNOTATIONS:
        repo_path = annotation["repo_path"]
        if repo_path not in missing:
            raise FrontierReportError(f"manual_annotation_not_in_fix33_missing_candidates:{repo_path}")
        path = repo_root / repo_path
        if not path.is_file():
            raise FrontierReportError(f"manual_annotation_source_missing:{repo_path}")
        source_sha256 = sha256_file(path)
        missing_record = missing[repo_path]
        annotated = {
            **annotation,
            "annotation_source": MANUAL_ANNOTATION_SOURCE,
            "candidate_node_status_before_annotation": missing_record["candidate_node_status"],
            "gap_classes_before_annotation": missing_record["gap_classes"],
            "proposed_candidate_node_id": path_to_candidate_id(repo_path, source_sha256),
            "source_sha256": source_sha256,
            "proposed_node_kind": "test_file",
            "promotion_status": "manual_annotation_for_graph_refresh_only",
            "canonical_mutation_status": "not_mutated",
        }
        annotations.append(annotated)

    annotated_paths = {row["repo_path"] for row in annotations}
    missing_unannotated = sorted(set(missing) - annotated_paths)
    return {
        "annotation_mode": "manual_direct_read_batches",
        "annotation_source": MANUAL_ANNOTATION_SOURCE,
        "batch_size_policy": "batches_of_10_plus_tail_batch",
        "fix33_missing_candidate_node_count": len(missing),
        "manual_annotation_count": len(annotations),
        "manual_annotation_coverage": f"{len(annotations)}/{len(missing)}",
        "graph_refresh_ready_count": len(annotations),
        "missing_candidate_nodes_remaining_unannotated_count": len(missing_unannotated),
        "missing_candidate_nodes_remaining_unannotated": missing_unannotated,
        "annotations": annotations,
    }


def docs_cross_check(inventory: Path, status: Path, planning: Path) -> dict[str, Any]:
    inventory_text = inventory.read_text(encoding="utf-8")
    status_text = status.read_text(encoding="utf-8")
    planning_text = planning.read_text(encoding="utf-8")
    return {
        "test_inventory_records_future_homoiconic_registry": (
            "Future Homoiconic Test Registry" in inventory_text
            or "homoiconic test registry" in inventory_text
        ),
        "status_records_fix37": "pytest_sidecar_graph_hydrated_workspace_committed_phase_1545p_fix37"
        in status_text,
        "planning_records_fix37": "pytest_sidecar_graph_hydrated_workspace_committed_phase_1545p_fix37"
        in planning_text,
        "planning_records_block6_not_superseded": "does not supersede Block 6" in planning_text,
    }


def build_payload(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    for path in [
        args.fix33,
        args.fix34,
        args.fix35,
        args.fix36,
        args.fix37,
        args.inventory,
        args.status,
        args.planning,
    ]:
        require_file(path)

    fix33 = load_json(args.fix33)
    fix34 = load_json(args.fix34)
    fix35 = load_json(args.fix35)
    fix36 = load_json(args.fix36)
    fix37 = load_json(args.fix37)
    graph = load_graph(args.graph)
    ledger_annotations = load_manual_edge_ledger(args.manual_ledger)
    curated_edge_annotations = {
        **CURATED_FRONTIER_EDGE_ANNOTATIONS,
        **ledger_annotations,
    }

    fix33_summary, fix33_records = summarize_fix33(fix33)
    manual_annotations = enrich_manual_annotations(fix33_records, repo_root)
    curated_by_path = {
        annotation["repo_path"]: annotation
        for annotation in manual_annotations["annotations"]
    }
    all_frontier_annotations = build_frontier_gap_annotations(
        fix33_records,
        repo_root,
        curated_by_path,
        curated_edge_annotations,
    )
    curated_edge_batch = build_curated_edge_batch(
        fix33_records,
        repo_root,
        curated_edge_annotations,
    )
    unified_candidate = build_unified_candidate(
        graph,
        all_frontier_annotations,
        curated_edge_batch,
        repo_root,
    )
    atomic_canonical_write(args.candidate_out, unified_candidate)
    graph_gap = graph_test_target_gap(graph)
    graph_status = (
        "unsigned_support_only_not_canonical"
        if graph is not None
        else "graph_missing_lower_information_frontier_only"
    )
    graph_counts = {
        "graph_path": str(args.graph) if args.graph is not None else None,
        "graph_present": graph is not None,
        "graph_candidate_status": graph_status,
        "graph_node_count": len(graph.get("nodes", [])) if graph is not None else 0,
        "graph_edge_count": len(graph.get("edges", [])) if graph is not None else 0,
    }

    frontier_categories = {
        "missing_candidate_nodes": {
            "count": fix33_summary["missing_candidate_node_count"],
            "manual_annotation_coverage": manual_annotations["manual_annotation_coverage"],
            "action": "refresh_atlas_candidate_with_manual_test_file_nodes_and_TESTS_edges",
        },
        "missing_tests_edges": {
            "count": fix33_summary["missing_tests_edge_count"],
            "sample": fix33_summary["missing_tests_edge_sample"],
            "action": "manual_or_extractor_TESTS_edge_review",
        },
        "missing_expected_authority_traces": {
            "count": fix33_summary["gap_class_counts"].get("missing_expected_authority_trace", 0),
            "sample": fix33_summary["missing_expected_authority_trace_sample"],
            "action": "role_specific_authority_trace_review_not_REFERENCES_AUTHORITY_by_default",
        },
        "function_nodes_without_inherited_targets": {
            "count": summarize_fix34(fix34)["function_nodes_without_inherited_tests_targets_count"],
            "action": "function_level_COVERS_SYMBOL_or_TESTS_inheritance_review",
        },
        "gated_or_non_default_tests": {
            "count": sum(
                count
                for profile, count in fix33_summary["executor_profile_counts"].items()
                if profile not in {"default_local_pytest", "pytest_support_file"}
            ),
            "profile_counts": {
                profile: count
                for profile, count in fix33_summary["executor_profile_counts"].items()
                if profile not in {"default_local_pytest", "pytest_support_file"}
            },
            "action": "preserve_executor_gates_before_default_graph_runner_queries",
        },
        "git_history_dependent_hydration_exclusions": {
            "count": summarize_fix37(fix37)["excluded_count"],
            "excluded_commands": summarize_fix37(fix37)["excluded_commands"],
            "action": "decide_git_history_hydration_or_persistent_repo_executor_mode",
        },
        "bounded_execution_evidence": {
            "fix36_selected_default_local_count": summarize_fix36(fix36)["selected_count"],
            "fix37_graph_hydrated_selected_count": summarize_fix37(fix37)["selected_count"],
            "action": "expand_evidence_batches_only_after_frontier_gap_triage",
        },
        "dangling_tests_targets": {
            "count": fix33_summary["dangling_tests_target_count"],
            "action": "no_action_required_when_zero",
        },
        "approximate_graph_TESTS_target_gap": graph_gap,
    }

    payload = {
        "phase": PHASE,
        "status": "pass",
        "report_kind": "graph_derived_test_frontier_report",
        "execution_scope": "report_only_no_test_execution_no_canonical_graph_mutation_candidate_overlay_only",
        "input_scope": "fix33_fix34_fix35_fix36_fix37_plus_enriched_graph_if_present",
        "graph_summary": graph_counts,
        "fix33_file_frontier": fix33_summary,
        "fix34_function_frontier": summarize_fix34(fix34),
        "fix35_sidecar_plan_summary": summarize_fix35(fix35),
        "fix36_evidence_summary": summarize_fix36(fix36),
        "fix37_hydration_summary": summarize_fix37(fix37),
        "frontier_categories": frontier_categories,
        "manual_connectivity_annotations": manual_annotations,
        "manual_connectivity_annotations_all_frontier_gaps": all_frontier_annotations,
        "curated_frontier_edge_batch": curated_edge_batch,
        "unified_candidate_summary": {
            "candidate_path": str(args.candidate_out),
            "candidate_digest": unified_candidate["candidate_digest"],
            "candidate_status": unified_candidate["candidate_status"],
            "node_count": len(unified_candidate["nodes"]),
            "edge_count": len(unified_candidate["edges"]),
            "fix38_overlay_summary": unified_candidate["fix38_overlay_summary"],
        },
        "manual_edge_ledger_summary": {
            "ledger_path": str(args.manual_ledger),
            "ledger_present": args.manual_ledger.exists(),
            "ledger_annotation_count": len(ledger_annotations),
            "combined_curated_edge_annotation_count": len(curated_edge_annotations),
        },
        "documentation_cross_check": docs_cross_check(args.inventory, args.status, args.planning),
        "next_actions": [
            "materialize_manual_annotation_batch_as_candidate_test_file_nodes_in_next_graph_refresh",
            "review_all_frontier_gap_annotations_and_materialize_candidate_edges_in_next_graph_refresh",
            "review_fix38_unified_candidate_before_any_graph_promotion",
            "preserve executor gates before expanding registry-mode execution",
            "decide git-history-dependent test execution strategy before broader graph-hydrated mode",
            "do not treat this report as canonical graph mutation or authority proof",
        ],
        "non_claims": NON_CLAIMS,
        "output_tokens": OUTPUT_TOKENS,
    }
    payload["report_digest"] = report_digest(payload)
    return payload


def render_report(payload: dict[str, Any], path: Path) -> None:
    fix33 = payload["fix33_file_frontier"]
    fix34 = payload["fix34_function_frontier"]
    fix36 = payload["fix36_evidence_summary"]
    fix37 = payload["fix37_hydration_summary"]
    annotations = payload["manual_connectivity_annotations"]
    all_annotations = payload["manual_connectivity_annotations_all_frontier_gaps"]
    curated_batch = payload["curated_frontier_edge_batch"]
    candidate_summary = payload["unified_candidate_summary"]

    lines = [
        "# ILC Test Registry Frontier Report - Phase 1545p-Fix38",
        "",
        "## Summary",
        "",
        f"- Phase: `{payload['phase']}`",
        f"- Status: `{payload['status']}`",
        f"- Report digest: `{payload['report_digest']}`",
        f"- Graph candidate status: `{payload['graph_summary']['graph_candidate_status']}`",
        "- Scope: report-only support evidence; no test execution and no canonical graph mutation.",
        f"- Unified candidate file: `{candidate_summary['candidate_path']}`",
        f"- Unified candidate digest: `{candidate_summary['candidate_digest']}`",
        "",
        "## File-Level Frontier",
        "",
        f"- Local test Python files: `{fix33['local_test_python_file_count']}`",
        f"- Mapped test files: `{fix33['mapped_test_file_count']}`",
        f"- Files with TESTS edges: `{fix33['files_with_tests_edge_count']}`",
        f"- Missing candidate node count: `{fix33['missing_candidate_node_count']}`",
        f"- Missing TESTS edge count: `{fix33['missing_tests_edge_count']}`",
        f"- Missing expected authority trace count: `{fix33['gap_class_counts'].get('missing_expected_authority_trace', 0)}`",
        f"- Dangling TESTS target count: `{fix33['dangling_tests_target_count']}`",
        "",
        "## Function-Level Frontier",
        "",
        f"- Collected test function nodes: `{fix34['collected_test_function_count']}`",
        f"- Candidate edge count: `{fix34['candidate_edge_count']}`",
        f"- Deferred record count: `{fix34['deferred_record_count']}`",
        f"- Function nodes without inherited TESTS targets: `{fix34['function_nodes_without_inherited_tests_targets_count']}`",
        "",
        "## Unified Candidate Overlay",
        "",
        f"- Candidate status: `{candidate_summary['candidate_status']}`",
        f"- Unified node count: `{candidate_summary['node_count']}`",
        f"- Unified edge count: `{candidate_summary['edge_count']}`",
        f"- Overlay frontier files: `{candidate_summary['fix38_overlay_summary']['frontier_file_count']}`",
        f"- Overlay added nodes: `{candidate_summary['fix38_overlay_summary']['added_node_count']}`",
        f"- Overlay added edges: `{candidate_summary['fix38_overlay_summary']['added_edge_count']}`",
        f"- Curated manual-edge files: `{candidate_summary['fix38_overlay_summary']['curated_manual_edge_file_count']}`",
        f"- Curated semantic edges: `{candidate_summary['fix38_overlay_summary']['curated_semantic_edge_count']}`",
        f"- Curated authority-trace edges: `{candidate_summary['fix38_overlay_summary']['curated_authority_trace_edge_count']}`",
        "- Authority edge policy: candidate role-specific traces only; no `GOVERNS` edges from tests and no direct test-to-Genesis authority shortcut.",
        "",
        "## Evidence Frontier",
        "",
        f"- Fix36 default-local evidence commands: `{fix36['selected_count']}`",
        f"- Fix36 result statuses: `{json.dumps(fix36['result_status_counts'], sort_keys=True)}`",
        f"- Fix37 graph-hydrated commands: `{fix37['selected_count']}`",
        f"- Fix37 excluded git-history-dependent commands: `{fix37['excluded_count']}`",
        f"- Fix37 hydrated files: `{fix37['hydrated_file_count']}`",
        "",
        "## Manual Connectivity Annotation Batches",
        "",
        f"- Annotation mode: `{annotations['annotation_mode']}`",
        f"- Batch size policy: `{annotations['batch_size_policy']}`",
        f"- Manual annotation coverage for Fix33 missing candidate nodes: `{annotations['manual_annotation_coverage']}`",
        f"- Remaining missing candidate nodes after this pass: `{annotations['missing_candidate_nodes_remaining_unannotated_count']}`",
        f"- All Fix33 frontier gap files annotated: `{all_annotations['frontier_gap_annotation_coverage']}`",
        f"- All-frontier annotation batches: `{all_annotations['batch_count']}`",
        "",
        "| Tranche | Test file | Connectivity class | Proposed target count | Recommended action |",
        "|---|---:|---|---:|---|",
    ]

    for row in annotations["annotations"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["annotation_tranche"],
                    f"`{row['repo_path']}`",
                    row["connectivity_class"],
                    str(len(row["proposed_tests_targets"])),
                    row["recommended_graph_action"],
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Frontier Categories",
            "",
        ]
    )
    for name, category in payload["frontier_categories"].items():
        lines.append(f"- `{name}`: `{category.get('count', category.get('status', 'recorded'))}`")

    lines.extend(
        [
            "",
            "## All-Frontier Batch Annotation Summary",
            "",
            "Every Fix33 file in `missing_candidate_node`, `missing_tests_edge`, or `missing_expected_authority_trace` was direct-read and assigned a batch annotation record.",
            "",
            "| Batch | Annotated files |",
            "|---|---:|",
        ]
    )
    for batch, count in all_annotations["batch_record_counts"].items():
        lines.append(f"| `{batch}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Curated Manual Edge Batch",
            "",
            f"- Annotation source: `{curated_batch['annotation_source']}`",
            f"- Curated files: `{curated_batch['manual_edge_annotation_count']}`",
            f"- Curated semantic edges: `{curated_batch['semantic_edge_count']}`",
            f"- Curated authority-trace edges: `{curated_batch['authority_trace_edge_count']}`",
            "- Git chronology is supporting cluster evidence only; direct-read semantics remain primary.",
            "",
            "| Test file | Semantic edges | Authority trace edges | Recommended action |",
            "|---|---:|---:|---|",
        ]
    )
    for row in curated_batch["annotations"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['repo_path']}`",
                    str(len(row["proposed_semantic_edges"])),
                    str(len(row["proposed_authority_trace_edges"])),
                    row["recommended_graph_action"],
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Non-Authority Boundary",
            "",
            "Manual annotations are review-queue records, not canonical graph edges.",
            "This report does not grant authority, activation, eligibility, claimability, governance effect, or economic effect.",
            "The enriched graph input remains unsigned support-only and not canonical.",
            "",
            "No canonical graph mutation, edge promotion, signing, upload, publication, runtime activation, sidecar activation, ADR mutation, or CDL mutation occurred.",
            "",
            "## Output Tokens",
            "",
        ]
    )
    lines.extend(f"- `{token}`" for token in OUTPUT_TOKENS)
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix33", type=Path, default=DEFAULT_FIX33)
    parser.add_argument("--fix34", type=Path, default=DEFAULT_FIX34)
    parser.add_argument("--fix35", type=Path, default=DEFAULT_FIX35)
    parser.add_argument("--fix36", type=Path, default=DEFAULT_FIX36)
    parser.add_argument("--fix37", type=Path, default=DEFAULT_FIX37)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--status", type=Path, default=DEFAULT_STATUS)
    parser.add_argument("--planning", type=Path, default=DEFAULT_PLANNING)
    parser.add_argument("--manual-ledger", type=Path, default=DEFAULT_MANUAL_LEDGER)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--candidate-out", type=Path, default=DEFAULT_CANDIDATE_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    payload = build_payload(args, repo_root)
    atomic_canonical_write(args.json_out, payload)
    render_report(payload, args.report)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "report_digest": payload["report_digest"],
                "candidate_digest": payload["unified_candidate_summary"]["candidate_digest"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
