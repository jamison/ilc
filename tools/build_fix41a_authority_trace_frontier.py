#!/usr/bin/env python3
"""Build Phase 1545p-Fix41a authority-trace frontier outputs.

PUBLIC_RC_EXCLUDE: fix41a_authority_trace_frontier_runner
PUBLIC_RC_EXCLUDE_REASON: Internal research-only Atlas candidate overlay and
coverage diagnostic runner. It does not mutate canonical graph state, sign
nodes, upload nodes, execute tests, activate runtime, or authorize public RC.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PHASE = "1545p-Fix41a"
DEFAULT_BASE_GRAPH = Path("out/atlas_research/genesis_atlas_enriched_candidate_fix40.json")
DEFAULT_CANDIDATE_OUT = Path("out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json")
DEFAULT_LEDGER_OUT = Path("docs/specs/ilc_fix41a_authority_trace_frontier_ledger_v0.1.json")
DEFAULT_REPORT_OUT = Path("docs/specs/ilc_fix41a_authority_trace_frontier_report_v0.1.md")
DEFAULT_COVERAGE_JSON = Path("out/test_graph_coverage_1545p_fix41a.json")
DEFAULT_COVERAGE_REPORT = Path(
    "docs/specs/ilc_test_graph_coverage_report_1545p_fix41a_v0.1.md"
)
FIX40_COVERAGE_BASELINE = Path("out/test_graph_coverage_1545p_fix40.json")

OUTPUT_TOKENS = [
    "fix41a_authority_trace_frontier_manual_audit_complete",
    "fix41a_role_specific_checker_hardening_committed",
    "fix41a_authority_trace_overlay_produced",
    "fix41a_coverage_rerun_complete",
    "fix41a_complete",
    "public_path_remains_blocked_phase_1545p_fix41a",
]

TERMINAL_PREFIXES = (
    "adr:",
    "cdl:",
    "phase:",
    "phase_window:",
    "policy:",
    "sim:",
)


class Fix41aError(RuntimeError):
    """Stable phase-runner error."""


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )


def canonical_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_bytes(payload).decode("utf-8") + "\n", encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_short(payload: Any, length: int = 32) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()[:length]


def safe_suffix(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")[:180] or "unknown"


def node_id(node: dict[str, Any]) -> str | None:
    for key in ("candidate_id", "node_id", "id", "vertex_id"):
        value = node.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def edge_source(edge: dict[str, Any]) -> str | None:
    value = edge.get("source") or edge.get("from") or edge.get("source_id")
    return value if isinstance(value, str) and value else None


def edge_target(edge: dict[str, Any]) -> str | None:
    value = edge.get("target") or edge.get("to") or edge.get("target_id")
    return value if isinstance(value, str) and value else None


def edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type") or edge.get("relation") or "UNKNOWN"
    return str(value)


def build_path_index(nodes: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for node in nodes:
        nid = node_id(node)
        if not nid:
            continue
        for key in ("source_path", "repo_path", "path", "label"):
            value = node.get(key)
            if isinstance(value, str) and value:
                index[value].append(nid)
    return {key: sorted(set(value)) for key, value in index.items()}


def prefer_node(candidates: list[str]) -> str:
    def score(value: str) -> tuple[int, str]:
        if value.startswith("repo:file:"):
            return (0, value)
        if value.startswith("repo:file_ref:"):
            return (1, value)
        return (2, value)

    return sorted(candidates, key=score)[0]


def target_category(target: str) -> str:
    if target.startswith("phase:") or target.startswith("phase_window:"):
        return "phase_terminal"
    if target.startswith("policy:"):
        return "authority_terminal_policy"
    if target.startswith("sim:"):
        return "sim_terminal"
    if target.startswith("adr:"):
        return "authority_terminal_adr"
    if target.startswith("cdl:"):
        return "authority_terminal_cdl"
    return "support_terminal"


def ensure_node(
    nodes: list[dict[str, Any]],
    node_ids: set[str],
    nid: str,
    label: str,
    category: str,
    provenance: str,
) -> None:
    if nid in node_ids:
        return
    nodes.append(
        {
            "authority_status": "candidate_review_required",
            "candidate_id": nid,
            "canonicality_tier": "fix41a_candidate_terminal",
            "category": category,
            "confidence": "0.700",
            "genesis_attested": False,
            "inclusion_status": "candidate_overlay",
            "label": label,
            "promotion_status": "candidate_only_not_canonical",
            "provenance": provenance,
            "source_phase": PHASE,
        }
    )
    node_ids.add(nid)


def resolve_target(
    target: str,
    nodes: list[dict[str, Any]],
    node_ids: set[str],
    path_index: dict[str, list[str]],
    repo_root: Path,
) -> str:
    if target in node_ids:
        return target
    if target in path_index:
        return prefer_node(path_index[target])
    if target.startswith(TERMINAL_PREFIXES):
        ensure_node(nodes, node_ids, target, target, target_category(target), "fix41a_target_resolution")
        return target
    if (repo_root / target).exists():
        nid = f"repo:file_ref:{safe_suffix(target)}"
        ensure_node(nodes, node_ids, nid, target, "support_artifact", "fix41a_target_resolution")
        return nid
    nid = f"target:{safe_suffix(target)}"
    ensure_node(nodes, node_ids, nid, target, "unresolved_candidate_terminal", "fix41a_target_resolution")
    return nid


def source_for_path(path_index: dict[str, list[str]], repo_path: str) -> str:
    candidates = path_index.get(repo_path)
    if not candidates:
        raise Fix41aError(f"source_node_not_found:{repo_path}")
    return prefer_node(candidates)


def fix41a_edge_id(source: str, etype: str, target: str, repo_path: str, index: int) -> str:
    payload = {
        "index": index,
        "phase": PHASE,
        "repo_path": repo_path,
        "source": source,
        "target": target,
        "type": etype,
    }
    return "edge:fix41a:" + sha256_short(payload)


def edge_record(etype: str, target: str, rationale: str) -> dict[str, str]:
    return {
        "edge_type": etype,
        "target": target,
        "rationale": rationale,
        "review_status": "candidate_role_specific_authority_trace",
    }


def batch_id(index: int) -> str:
    start = ((index - 1) // 10) * 10 + 1
    end = min(start + 9, 57)
    return f"manual_batch_{((index - 1) // 10) + 1:03d}_authority_files_{start:04d}_{end:04d}"


def existing(path: str, summary: str) -> dict[str, Any]:
    return {
        "manual_read_summary": summary,
        "new_candidate_trace_edges": [],
        "repo_path": path,
        "trace_status": "existing_role_trace_checker_hardening_only",
    }


def missing(path: str, summary: str, edges: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "manual_read_summary": summary,
        "new_candidate_trace_edges": edges,
        "repo_path": path,
        "trace_status": "new_candidate_trace_required",
    }


FRONTIER_RECORDS: list[dict[str, Any]] = [
    existing(
        "tests/test_cdl_001_signer_lineage_runtime.py",
        "CDL-001 signer-lineage runtime regression evidence for the security signer-lineage path.",
    ),
    existing(
        "tests/test_cdl_002_key_compromise_runtime.py",
        "CDL-002 key-compromise runtime regression evidence with signer-lineage dependency.",
    ),
    existing(
        "tests/test_cdl_007_rollback_resistance_runtime.py",
        "CDL-007 rollback-resistance runtime regression evidence for security-lineage boundaries.",
    ),
    existing(
        "tests/test_cdl_011_015_ratification_evidence_gate_phase_215.py",
        "Phase 215 CDL-011 through CDL-015 ratification evidence gate regression.",
    ),
    missing(
        "tests/test_cli_key_loader_dedupe_phase_999.py",
        "Phase 999 CLI key-loader dedupe and contract narrowing test; existing role traces target runtime files and an invariant but not an authority terminal.",
        [
            edge_record(
                "REFERENCES_AUTHORITY",
                "phase:999_cli_key_loader_dedupe_contract_narrowing",
                "Manual read ties the test to the Phase 999 CLI key-loader dedupe contract.",
            ),
            edge_record(
                "CLASSIFIED_BY",
                "policy:phase999_cli_key_loader_dedupe",
                "Classifies the test as CLI key-registry dedupe support evidence.",
            ),
            edge_record(
                "EVIDENCES",
                "phase:999_cli_key_loader_dedupe_contract_narrowing",
                "Records the test as Phase 999 evidence, not authority.",
            ),
        ],
    ),
    existing(
        "tests/test_domain_exception_migration_closure_gate.py",
        "Domain-exception migration closure-gate regression for Phase 181 migration work.",
    ),
    existing(
        "tests/test_edge_removal_phase1_guardrails.py",
        "Track-1 edge-removal guardrail regression evidence for safe pruning controls.",
    ),
    missing(
        "tests/test_genesis_node_candidate_crawl.py",
        "Genesis node-candidate crawl test over star-map artifacts, review queues, and crawl diagnostics; existing traces use target terminals that are not authority terminals.",
        [
            edge_record(
                "REFERENCES_AUTHORITY",
                "policy:genesis_star_map_candidate_methodology",
                "Manual read ties the crawl to the Genesis star-map candidate methodology.",
            ),
            edge_record(
                "CLASSIFIED_BY",
                "policy:genesis_node_candidate_crawl_review_queue",
                "Classifies the crawl output as review-queue support evidence.",
            ),
            edge_record(
                "EVIDENCES",
                "sim:genesis_node_candidate_crawl",
                "Records the crawl as simulation/diagnostic evidence, not authority.",
            ),
        ],
    ),
    missing(
        "tests/test_genesis_star_map_gap_analysis.py",
        "Genesis star-map gap-analysis regression over observed hypergraph shape and gap categories; existing traces use diagnostic target terminals.",
        [
            edge_record(
                "REFERENCES_AUTHORITY",
                "policy:genesis_core_star_map_gap_analysis",
                "Manual read ties the test to the Genesis core star-map gap-analysis policy.",
            ),
            edge_record(
                "CLASSIFIED_BY",
                "policy:genesis_star_map_gap_analysis_support_only",
                "Classifies the test as support-only gap-analysis evidence.",
            ),
            edge_record(
                "EVIDENCES",
                "sim:spectral_02_genesis_core_star_map_gap_analysis",
                "Records the gap-analysis test as SIM evidence, not authority.",
            ),
        ],
    ),
    missing(
        "tests/test_genesis_work_task_model.py",
        "Genesis work-task model regression for epistemic task descriptors and task-queue bridge behavior.",
        [
            edge_record(
                "REFERENCES_AUTHORITY",
                "policy:genesis_epistemic_work_task_model",
                "Manual read ties the model to Genesis epistemic work-task semantics.",
            ),
            edge_record(
                "CLASSIFIED_BY",
                "policy:genesis_work_task_task_queue_bridge",
                "Classifies the test as task-model/task-queue bridge evidence.",
            ),
            edge_record(
                "EVIDENCES",
                "phase:1119_float_kill_01_ilc_core_float_prng_hardening",
                "Records the test as hardening evidence for the work-task surface.",
            ),
        ],
    ),
    missing(
        "tests/test_governance_config.py",
        "Governance config loader and consensus-engine propagation regression; existing traces target artifact terminals rather than accepted authority terminals.",
        [
            edge_record(
                "REFERENCES_AUTHORITY",
                "policy:governance_config_mvp_runtime_contract",
                "Manual read ties governance config behavior to the MVP runtime contract.",
            ),
            edge_record(
                "REFERENCES_AUTHORITY",
                "phase:983_typed_return_contract_rollout_ledger_config_foundation",
                "Routes the typed config contract to Phase 983 follow-on authority evidence.",
            ),
            edge_record(
                "CLASSIFIED_BY",
                "policy:governance_config_default_runtime_contract",
                "Classifies the test as governance config default-runtime support evidence.",
            ),
        ],
    ),
    existing(
        "tests/test_governance_config_diagnostics.py",
        "Governance config diagnostic regression for Phase 166 diagnostic behavior.",
    ),
    missing(
        "tests/test_governance_engine.py",
        "Governance engine dynamic pricing, congestion, and hardware scaling regression; existing traces target an artifact terminal.",
        [
            edge_record(
                "REFERENCES_AUTHORITY",
                "policy:governance_dynamic_pricing_runtime",
                "Manual read ties the test to dynamic governance-pricing runtime semantics.",
            ),
            edge_record(
                "CLASSIFIED_BY",
                "policy:governance_engine_mvp_config_pricing",
                "Classifies the test as MVP governance-engine pricing evidence.",
            ),
            edge_record(
                "EVIDENCES",
                "phase:951_crosscut_core_hygiene_and_operability",
                "Records the test as cross-cutting operability/hygiene evidence.",
            ),
        ],
    ),
    existing(
        "tests/test_governance_ingest_helper_domain_exceptions.py",
        "Governance ingest helper domain-exception migration regression for Phase 184.",
    ),
    missing(
        "tests/test_idea_descent_genesis_star_map_loop.py",
        "Idea-descent Genesis star-map loop regression for refutation-loop traces and evaluator outputs.",
        [
            edge_record(
                "REFERENCES_AUTHORITY",
                "policy:idea_descent_genesis_star_map_autoresearch",
                "Manual read ties the test to the idea-descent Genesis star-map AutoResearch policy.",
            ),
            edge_record(
                "EVIDENCES",
                "phase:1545p_fix3_idea_descent_genesis_rework",
                "Records the test as evidence for Phase 1545p-Fix3 idea-descent rework.",
            ),
            edge_record(
                "TESTS",
                "docs/specs/ilc_idea_descent_genesis_star_map_objective_v0.1.md",
                "Connects the test to the objective spec it operationalizes.",
            ),
        ],
    ),
    existing(
        "tests/test_ilc_cluster_a_governance_apply.py",
        "Cluster-A governance application and signature verification regression.",
    ),
    existing(
        "tests/test_ilc_governance_record_schema.py",
        "Governance record schema regression for constitutional Cluster-A foundation records.",
    ),
    existing(
        "tests/test_ledger_config_typed_contract_guardrails_phase1.py",
        "Phase 983 ledger/config typed-contract guardrail tranche one.",
    ),
    existing(
        "tests/test_ledger_typed_contract_guardrails_phase2.py",
        "Ledger typed-contract guardrail tranche two.",
    ),
    existing(
        "tests/test_ledger_typed_contract_guardrails_phase3.py",
        "Ledger typed-contract guardrail tranche three.",
    ),
    existing(
        "tests/test_ledger_typed_contract_guardrails_phase4.py",
        "Ledger typed-contract guardrail tranche four.",
    ),
    existing(
        "tests/test_license_presence_phase_997.py",
        "Phase 997 release/legal layered license-presence regression.",
    ),
    existing(
        "tests/test_node_value_kernel_phase_205.py",
        "Phase 205 node-value kernel regression evidence.",
    ),
    existing(
        "tests/test_non_replay_domain_exception_migration_closure_gate.py",
        "Non-replay domain-exception migration closure gate regression for Phase 191.",
    ),
    existing(
        "tests/test_patent_application_numbers_status.py",
        "Patent application-number status regression already traces to patent delivery and RC status artifacts.",
    ),
    existing(
        "tests/test_path_lift_counterfactual_phase_214.py",
        "Phase 214 path-lift counterfactual regression evidence.",
    ),
    existing(
        "tests/test_phase_768_sec_004_acceptance.py",
        "Phase 768 SEC-004/CDL-017 validator acceptance regression.",
    ),
    existing(
        "tests/test_phase_769_m007_hook_activation.py",
        "Phase 769 validator-hook activation regression under CDL-017 boundaries.",
    ),
    existing(
        "tests/test_phase_776_layer1_log_hygiene.py",
        "Phase 776 Layer-1 agent-id log hygiene regression.",
    ),
    existing(
        "tests/test_phase_777_sim_run1.py",
        "Phase 777 SIM leakage run-one regression evidence.",
    ),
    existing(
        "tests/test_phase_779_sim_run2.py",
        "Phase 779 SIM leakage run-two regression evidence.",
    ),
    existing(
        "tests/test_phase_831_row5_b_impl_obligations_1_3.py",
        "Phase 831 Row-5 B privacy obligations one through three regression evidence.",
    ),
    existing(
        "tests/test_phase_832_row5_b_impl_obligations_4_5.py",
        "Phase 832 Row-5 B privacy obligations four and five regression evidence.",
    ),
    existing(
        "tests/test_phase_833_row5_b_impl_obligation_6_sim_leakage_03.py",
        "Phase 833 Row-5 B obligation six and SIM-LEAKAGE-03 regression evidence.",
    ),
    existing(
        "tests/test_phase_835_settlement_gate_preflight.py",
        "Phase 835 settlement-gate preflight regression evidence.",
    ),
    existing(
        "tests/test_phase_845_sim_leakage_03_live_run.py",
        "Phase 845 SIM-LEAKAGE-03 live-run evidence regression.",
    ),
    existing(
        "tests/test_phase_858_hb_001_genesis_assertion_schema.py",
        "Phase 858 HB-001/CDL-073 Genesis assertion-schema regression.",
    ),
    existing(
        "tests/test_phase_932_933_h013_spectral_beacon.py",
        "Phase 932/933 H-013/CDL-080 spectral-beacon regression.",
    ),
    existing(
        "tests/test_phase_M012_full_bft_transfer.py",
        "Mysticeti M-012 full BFT transfer artifact regression evidence.",
    ),
    existing(
        "tests/test_phase_M013_workload_a_results.py",
        "Mysticeti M-013 workload-A result regression evidence.",
    ),
    existing(
        "tests/test_phase_M014_workload_b_results.py",
        "Mysticeti M-014 workload-B result regression evidence.",
    ),
    existing(
        "tests/test_phase_M015_workload_c_results.py",
        "Mysticeti M-015 workload-C result regression evidence.",
    ),
    existing(
        "tests/test_phase_M016_workload_d_results.py",
        "Mysticeti M-016 replayability/state-extraction regression evidence.",
    ),
    existing(
        "tests/test_phase_M017_workload_e_results.py",
        "Mysticeti M-017 operability regression evidence.",
    ),
    existing(
        "tests/test_phase_M018_workload_f_results.py",
        "Mysticeti M-018 auditability, SEC-009, and BLS regression evidence.",
    ),
    existing(
        "tests/test_phase_M019_adversarial_hardening_results.py",
        "Mysticeti M-019 adversarial-hardening regression evidence.",
    ),
    existing(
        "tests/test_phase_high002_phase_b_closure_gate.py",
        "HIGH-002 Phase-B closure-gate regression evidence.",
    ),
    existing(
        "tests/test_public_rc_package_profiles.py",
        "Public RC package-profile policy regression evidence.",
    ),
    existing(
        "tests/test_quickstart_parity_phase_998.py",
        "Phase 998 README and Genesis boot quickstart parity regression.",
    ),
    existing(
        "tests/test_refutation_profitability_invariant_gate_phase_212.py",
        "Phase 212 refutation-profitability invariant gate regression.",
    ),
    existing(
        "tests/test_refutation_profitability_invariant_phase_212.py",
        "Phase 212 refutation-profitability invariant runtime regression.",
    ),
    existing(
        "tests/test_runtime_logging_closure_gate.py",
        "Runtime logging closure-gate regression evidence.",
    ),
    existing(
        "tests/test_security_runtime_cross_cdl_interactions_244.py",
        "Phase 244 cross-CDL security interaction regression for CDL-001/002/007.",
    ),
    existing(
        "tests/test_track1_closure_guardrail_gate_ops.py",
        "Track-1 closure and replay-proof gate orchestration regression.",
    ),
    existing(
        "tests/test_window_545_554_audit_regressions.py",
        "Window 545-554 audit regression bundle.",
    ),
    existing(
        "tests/test_window_555_560_transport_audit_regressions.py",
        "Window 555-560 transport/gossip audit regression bundle.",
    ),
    existing(
        "tests/test_window_555_562_peer_registry_audit_regressions.py",
        "Window 555-562 peer-registry audit regression bundle.",
    ),
]


def validate_frontier_records() -> None:
    if len(FRONTIER_RECORDS) != 57:
        raise Fix41aError(f"frontier_record_count_mismatch:{len(FRONTIER_RECORDS)}")
    paths = [row["repo_path"] for row in FRONTIER_RECORDS]
    duplicate_paths = [path for path, count in Counter(paths).items() if count > 1]
    if duplicate_paths:
        raise Fix41aError(f"duplicate_frontier_paths:{duplicate_paths}")


def existing_role_traces(
    repo_path: str,
    path_index: dict[str, list[str]],
    edges_by_source: dict[str, list[dict[str, Any]]],
) -> list[dict[str, str]]:
    traces: list[dict[str, str]] = []
    for source in path_index.get(repo_path, []):
        for edge in edges_by_source.get(source, []):
            etype = edge_type(edge)
            if etype not in {
                "CLASSIFIED_BY",
                "DERIVED_FROM",
                "EVIDENCES",
                "IMPLEMENTS",
                "REFERENCES_AUTHORITY",
                "REGRESSES",
                "TESTS",
            }:
                continue
            target = edge_target(edge)
            if not target:
                continue
            traces.append({"edge_type": etype, "target": target})
    return sorted({json.dumps(t, sort_keys=True): t for t in traces}.values(), key=lambda t: (t["edge_type"], t["target"]))[:20]


def build_ledger(base_graph: dict[str, Any]) -> dict[str, Any]:
    validate_frontier_records()
    nodes = [node for node in base_graph.get("nodes", []) if isinstance(node, dict)]
    edges = [edge for edge in base_graph.get("edges", []) if isinstance(edge, dict)]
    path_index = build_path_index(nodes)
    edges_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        source = edge_source(edge)
        if source:
            edges_by_source[source].append(edge)

    annotations = []
    for index, row in enumerate(FRONTIER_RECORDS, start=1):
        repo_path = row["repo_path"]
        annotations.append(
            {
                "annotation_method": "direct_read_manual_semantic_audit",
                "annotation_phase": PHASE,
                "batch_id": batch_id(index),
                "frontier_index": index,
                "manual_read_summary": row["manual_read_summary"],
                "new_candidate_trace_edges": row["new_candidate_trace_edges"],
                "observed_existing_role_traces": existing_role_traces(
                    repo_path, path_index, edges_by_source
                ),
                "repo_path": repo_path,
                "trace_status": row["trace_status"],
            }
        )

    counts = Counter(row["trace_status"] for row in annotations)
    return {
        "annotations": annotations,
        "metadata": {
            "base_graph": str(DEFAULT_BASE_GRAPH),
            "frontier_file_count": len(annotations),
            "manual_batch_policy": "batches_of_10_plus_tail",
            "new_candidate_trace_required_count": counts["new_candidate_trace_required"],
            "phase": PHASE,
            "status": "research_only_manual_audit_ledger",
        },
        "non_claims": [
            "no_canonical_graph_mutation",
            "no_edge_promotion",
            "no_genesis_signing",
            "no_node_upload",
            "no_public_rc_activation",
            "no_runtime_activation",
            "no_adr_cdl_mutation",
        ],
        "output_tokens": OUTPUT_TOKENS,
    }


def merge_new_edges(
    base_graph: dict[str, Any],
    ledger: dict[str, Any],
    repo_root: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    nodes = [dict(node) for node in base_graph.get("nodes", []) if isinstance(node, dict)]
    edges = [dict(edge) for edge in base_graph.get("edges", []) if isinstance(edge, dict)]
    node_ids = {nid for node in nodes if (nid := node_id(node))}
    path_index = build_path_index(nodes)
    existing_signatures = {
        (edge_source(edge), edge_type(edge), edge_target(edge))
        for edge in edges
        if edge_source(edge) and edge_target(edge)
    }
    added_edges = 0
    added_by_type: Counter[str] = Counter()
    considered = 0
    created_target_nodes_before = len(node_ids)

    for annotation in ledger["annotations"]:
        repo_path = annotation["repo_path"]
        source = source_for_path(path_index, repo_path)
        for index, item in enumerate(annotation["new_candidate_trace_edges"]):
            considered += 1
            etype = item["edge_type"]
            target = resolve_target(item["target"], nodes, node_ids, path_index, repo_root)
            signature = (source, etype, target)
            if signature in existing_signatures:
                continue
            edge = {
                "annotation_method": "direct_read_manual_semantic_audit",
                "annotation_phase": PHASE,
                "annotation_reviewer": "codex",
                "candidate_status": "fix41a_proposed",
                "confidence": "0.820",
                "edge_id": fix41a_edge_id(source, etype, target, repo_path, index),
                "edge_type": etype,
                "origin_edge_index": index,
                "origin_phase": PHASE,
                "origin_repo_path": repo_path,
                "promotion_status": "candidate_only_not_canonical",
                "provenance": "fix41a_authority_trace_frontier_ledger",
                "rationale": item["rationale"],
                "relation": etype.lower(),
                "review_status": item["review_status"],
                "source": source,
                "source_phase": PHASE,
                "target": target,
                "target_original": item["target"],
            }
            edges.append(edge)
            existing_signatures.add(signature)
            added_edges += 1
            added_by_type[etype] += 1

    result = {
        **base_graph,
        "candidate_status": "unsigned_support_only_not_canonical_fix41a_authority_trace_candidate",
        "edges": edges,
        "fix41a_merge_summary": {
            "added_candidate_edges": added_edges,
            "added_edges_by_type": dict(sorted(added_by_type.items())),
            "base_edge_count": len(base_graph.get("edges", [])),
            "base_node_count": len(base_graph.get("nodes", [])),
            "considered_new_candidate_trace_edges": considered,
            "created_target_nodes": len(node_ids) - created_target_nodes_before,
            "input_base_graph": str(DEFAULT_BASE_GRAPH),
            "input_ledger": str(DEFAULT_LEDGER_OUT),
            "phase": PHASE,
        },
        "nodes": nodes,
        "phase": PHASE,
    }
    result["candidate_digest"] = "fix41a_candidate:" + hashlib.sha256(
        canonical_bytes(
            {
                "edges": result["edges"],
                "nodes": result["nodes"],
                "phase": result["phase"],
                "status": result["candidate_status"],
            }
        )
    ).hexdigest()[:32]
    return result, result["fix41a_merge_summary"]


def integrity_checks(candidate: dict[str, Any]) -> dict[str, Any]:
    nodes = [node for node in candidate.get("nodes", []) if isinstance(node, dict)]
    edges = [edge for edge in candidate.get("edges", []) if isinstance(edge, dict)]
    ids = [nid for node in nodes if (nid := node_id(node))]
    id_counts = Counter(ids)
    node_id_set = set(ids)
    duplicates = sorted(nid for nid, count in id_counts.items() if count > 1)
    dangling = []
    for edge in edges:
        source = edge_source(edge)
        target = edge_target(edge)
        if source not in node_id_set or target not in node_id_set:
            dangling.append(
                {
                    "edge_id": str(edge.get("edge_id", "")),
                    "source": source,
                    "source_present": source in node_id_set,
                    "target": target,
                    "target_present": target in node_id_set,
                }
            )
    fix41a_edges = [edge for edge in edges if edge.get("source_phase") == PHASE]
    forbidden_governs = [
        str(edge.get("edge_id", "")) for edge in fix41a_edges if edge_type(edge) == "GOVERNS"
    ]
    return {
        "duplicate_node_id_count": len(duplicates),
        "duplicate_node_ids_sample": duplicates[:50],
        "endpoint_dangling_edge_count": len(dangling),
        "endpoint_dangling_edges_sample": dangling[:50],
        "fix41a_edge_count": len(fix41a_edges),
        "fix41a_governs_edge_count": len(forbidden_governs),
        "fix41a_governs_edge_sample": forbidden_governs[:50],
        "hard_stop": bool(dangling or duplicates or forbidden_governs),
        "status": "failed_hard_stop" if dangling or duplicates or forbidden_governs else "pass",
    }


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def run_coverage_checker(
    repo_root: Path,
    graph_path: Path,
    json_out: Path,
    report: Path,
) -> dict[str, Any]:
    command = [
        sys.executable,
        "tools/check_test_graph_coverage.py",
        "--graph",
        str(graph_path),
        "--json-out",
        str(json_out),
        "--report",
        str(report),
    ]
    result = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise Fix41aError(
            "coverage_checker_failed:" + result.stdout.strip() + result.stderr.strip()
        )
    payload = load_json(json_out)
    summary = payload["summary"]
    summary["coverage_checker_origin_phase"] = summary.get("phase", "1545p-Fix33")
    summary["phase"] = PHASE
    summary["graph_path"] = display_path(graph_path, repo_root)
    summary["output_tokens"] = OUTPUT_TOKENS
    summary["non_claims"] = sorted(
        set(summary.get("non_claims", []))
        | {
            "no_graph_promotion",
            "no_canonical_atlas_mutation",
            "no_genesis_signing",
            "no_node_upload",
            "no_public_graph_publication",
        }
    )
    canonical_write(json_out, payload)
    write_coverage_report(report, payload)
    return payload


def coverage_delta(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    b = baseline["summary"]
    c = current["summary"]
    return {
        "authority_trace_satisfied_file_count": {
            "baseline": b["authority_trace_satisfied_file_count"],
            "current": c["authority_trace_satisfied_file_count"],
            "delta": c["authority_trace_satisfied_file_count"]
            - b["authority_trace_satisfied_file_count"],
        },
        "missing_expected_authority_trace_count": {
            "baseline": b["gap_class_counts"].get("missing_expected_authority_trace", 0),
            "current": c["gap_class_counts"].get("missing_expected_authority_trace", 0),
            "delta": c["gap_class_counts"].get("missing_expected_authority_trace", 0)
            - b["gap_class_counts"].get("missing_expected_authority_trace", 0),
        },
        "role_trace_checker_delta_note": (
            "Fix41a baseline comparison is against the original Fix40 persisted coverage. "
            "The checker-hardening effect accounts for 50 of 57 authority-trace files; "
            "the overlay adds reviewed candidate traces for the remaining 7."
        ),
    }


def write_coverage_report(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    records = payload["file_records"]
    gap_counts = summary["gap_class_counts"]
    examples = {
        gap: [record["repo_path"] for record in records if gap in record["gap_classes"]][:10]
        for gap in sorted(gap_counts)
    }
    lines = [
        "<!-- PUBLIC_RC_EXCLUDE: fix41a_homoiconic_test_graph_coverage_report -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Phase 1545p-Fix41a diagnostic report; no graph mutation, test execution, signing, public RC activation, or runtime activation. -->",
        "",
        "# ILC Test Graph Coverage Report 1545p-Fix41a v0.1",
        "",
        "Phase: 1545p-Fix41a",
        "Status: report-first diagnostic rerun over Fix41a candidate",
        "Sensitivity: NON-SENSITIVE",
        "",
        "## Summary",
        "",
        f"- Coverage checker origin phase: `{summary['coverage_checker_origin_phase']}`",
        f"- Coverage input scope: `{summary['coverage_input_scope']}`",
        f"- Graph input: `{summary['graph_path']}`",
        f"- Graph nodes: `{summary['graph_node_count']}`",
        f"- Graph edges: `{summary['graph_edge_count']}`",
        f"- Graph TESTS edges: `{summary['graph_tests_edge_count']}`",
        f"- Local test/support Python files: `{summary['local_test_python_file_count']}`",
        f"- Mapped files: `{summary['mapped_test_file_count']}`",
        f"- Files with valid TESTS edge: `{summary['files_with_tests_edge_count']}`",
        f"- Missing candidate nodes: `{summary['missing_candidate_node_count']}`",
        f"- Missing TESTS edges: `{summary['missing_tests_edge_count']}`",
        f"- Missing expected authority traces: `{gap_counts.get('missing_expected_authority_trace', 0)}`",
        f"- Dangling TESTS targets: `{summary['dangling_tests_target_count']}`",
        "",
        "## Gap Class Counts",
        "",
        "| Gap class | Count |",
        "|---|---:|",
    ]
    for gap, count in gap_counts.items():
        lines.append(f"| `{gap}` | `{count}` |")
    lines.extend(["", "## Gap Examples", ""])
    for gap, paths in examples.items():
        lines.append(f"### `{gap}`")
        if paths:
            lines.extend(f"- `{item}`" for item in paths)
        else:
            lines.append("None recorded.")
        lines.append("")
    lines.extend(
        [
            "## Non-Claims",
            "",
            "- No graph-selected tests were executed.",
            "- No function-level pytest collection was performed.",
            "- No canonical Atlas mutation occurred.",
            "- No edge promotion occurred.",
            "- No Genesis signing occurred.",
            "- No node upload occurred.",
            "- No public graph publication occurred.",
            "- No public RC activation occurred.",
            "- No runtime, economic, sidecar, ADR, or CDL mutation occurred.",
            "",
            "## Output Tokens",
            "",
        ]
    )
    lines.extend(f"- `{token}`" for token in OUTPUT_TOKENS)
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_frontier_report(
    path: Path,
    ledger: dict[str, Any],
    merge_summary: dict[str, Any],
    integrity: dict[str, Any],
    coverage: dict[str, Any],
    baseline: dict[str, Any],
) -> None:
    counts = Counter(row["trace_status"] for row in ledger["annotations"])
    delta = coverage_delta(baseline, coverage)
    lines = [
        "<!-- PUBLIC_RC_EXCLUDE: fix41a_authority_trace_frontier_report -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Phase 1545p-Fix41a manual audit report; research-only candidate overlay, no signing, activation, publication, or canonical graph mutation. -->",
        "",
        "# ILC Fix41a Authority-Trace Frontier Report v0.1",
        "",
        "Phase: 1545p-Fix41a",
        "Status: complete research addendum",
        "Sensitivity: NON-SENSITIVE",
        "",
        "## Summary",
        "",
        f"- Manually audited files: `{len(ledger['annotations'])}`",
        f"- Files already covered by existing role-specific traces after checker hardening: `{counts['existing_role_trace_checker_hardening_only']}`",
        f"- Files requiring new candidate authority traces: `{counts['new_candidate_trace_required']}`",
        f"- New candidate trace edges added: `{merge_summary['added_candidate_edges']}`",
        f"- Created terminal nodes: `{merge_summary['created_target_nodes']}`",
        f"- Integrity status: `{integrity['status']}`",
        f"- Missing expected authority traces after Fix41a: `{coverage['summary']['gap_class_counts'].get('missing_expected_authority_trace', 0)}`",
        "",
        "## Coverage Delta",
        "",
        f"- Authority-trace satisfied files: `{delta['authority_trace_satisfied_file_count']['baseline']}` -> `{delta['authority_trace_satisfied_file_count']['current']}`",
        f"- Missing expected authority traces: `{delta['missing_expected_authority_trace_count']['baseline']}` -> `{delta['missing_expected_authority_trace_count']['current']}`",
        "",
        "## New Candidate Trace Files",
        "",
    ]
    for row in ledger["annotations"]:
        if row["trace_status"] != "new_candidate_trace_required":
            continue
        lines.append(f"### `{row['repo_path']}`")
        lines.append(row["manual_read_summary"])
        for edge in row["new_candidate_trace_edges"]:
            lines.append(
                f"- `{edge['edge_type']}` -> `{edge['target']}`: {edge['rationale']}"
            )
        lines.append("")
    lines.extend(
        [
            "## Boundary",
            "",
            "Fix41a records candidate-only role-specific authority traces. It does not promote candidate edges, mutate the canonical Atlas, sign graph artifacts, materialize LMDB, upload nodes, publish a public repository or graph, activate public RC, activate runtime/economics/sidecars, or mutate ADR/CDL state.",
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-graph", type=Path, default=DEFAULT_BASE_GRAPH)
    parser.add_argument("--candidate-out", type=Path, default=DEFAULT_CANDIDATE_OUT)
    parser.add_argument("--ledger-out", type=Path, default=DEFAULT_LEDGER_OUT)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT_OUT)
    parser.add_argument("--coverage-json", type=Path, default=DEFAULT_COVERAGE_JSON)
    parser.add_argument("--coverage-report", type=Path, default=DEFAULT_COVERAGE_REPORT)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    base_graph = load_json(args.base_graph)
    baseline = load_json(FIX40_COVERAGE_BASELINE)
    ledger = build_ledger(base_graph)
    canonical_write(args.ledger_out, ledger)
    candidate, merge_summary = merge_new_edges(base_graph, ledger, repo_root)
    canonical_write(args.candidate_out, candidate)
    integrity = integrity_checks(candidate)
    if integrity["hard_stop"]:
        raise Fix41aError(f"integrity_hard_stop:{integrity}")
    coverage = run_coverage_checker(repo_root, args.candidate_out, args.coverage_json, args.coverage_report)
    write_frontier_report(args.report_out, ledger, merge_summary, integrity, coverage, baseline)
    result = {
        "added_candidate_edges": merge_summary["added_candidate_edges"],
        "coverage_missing_expected_authority_trace": coverage["summary"]["gap_class_counts"].get(
            "missing_expected_authority_trace", 0
        ),
        "frontier_file_count": len(ledger["annotations"]),
        "integrity": integrity["status"],
        "new_candidate_trace_required_count": ledger["metadata"][
            "new_candidate_trace_required_count"
        ],
        "output_tokens": OUTPUT_TOKENS,
        "phase": PHASE,
    }
    print(canonical_bytes(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
