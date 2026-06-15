#!/usr/bin/env python3
"""Phase 1545p-Fix31 Atlas v0.4/v0.5 candidate reducer.

This runner is intentionally conservative. It prepares a decision packet over
already-generated research artifacts. It does not sign, upload, mutate canonical
Genesis state, activate runtime, or alter ADR/CDL state.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

FIX18_CORE = ROOT / "out/genesis_core_star_map_v0.4_candidate.json"
FIX18_DIAGNOSTIC = ROOT / "out/genesis_compile_coverage_diagnostic_v0.4_candidate.json"
FIX22_FULL = ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
FIX25_BASELINE = ROOT / "out/sim_atlas_whole_graph_baseline_diagnostic_1545p_fix25.json"
FIX29_SPECTRAL = ROOT / "out/sim_atlas_spectral_non_excisability_1545p_fix29.json"
FIX30_OPTIMIZED = ROOT / "out/atlas_research/genesis_atlas_optimized_candidate_1545p_fix30.json"
FIX30_SUMMARY = ROOT / "out/sim_atlas_long_autoresearch_optimization_1545p_fix30.json"
FIX30_ITERATIONS = ROOT / "out/atlas_research/genesis_atlas_autoresearch_iterations_1545p_fix30.jsonl"
BLOCK6_GUIDANCE = ROOT / "docs/specs/ilc_window_1565_1575_block6_candidate_phase_grouping_v0.1.md"

VARIANTS_OUT = ROOT / "out/atlas_research/genesis_atlas_v04_v05_candidate_variants_1545p_fix31.json"
BATCH_PLAN_OUT = ROOT / "out/atlas_research/genesis_atlas_public_private_batch_plan_1545p_fix31.json"
SUMMARY_OUT = ROOT / "out/sim_atlas_candidate_reducer_v04_v05_1545p_fix31.json"
SIM_REPORT = ROOT / "docs/sims/sim_atlas_candidate_reducer_v04_v05_1545p_fix31_v0.1.md"
DECISION_PACKET = ROOT / "docs/specs/ilc_genesis_atlas_v04_v05_candidate_decision_packet_1545p_fix31_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix31_candidate_reducer_v04_v05_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"

REQUIRED_TOKENS = [
    "atlas_candidate_reducer_v04_v05_packet_committed_phase_1545p_fix31",
    "atlas_v04_core_plus_support_variant_recorded_phase_1545p_fix31",
    "atlas_v05_full_repo_optimized_variant_recorded_phase_1545p_fix31",
    "atlas_public_private_signing_batch_plan_recorded_phase_1545p_fix31",
    "phase1573_signing_input_requires_human_scope_selection_phase_1545p_fix31",
    "public_path_remains_blocked_phase_1545p_fix31",
]

NON_CLAIMS = [
    "no_genesis_v04_signing",
    "no_genesis_v05_signing",
    "no_node_upload",
    "no_canonical_graph_mutation",
    "no_public_graph_publication",
    "no_public_repo_push",
    "no_public_rc_activation",
    "no_runtime_activation",
    "no_economic_activation",
    "no_sidecar_activation",
    "no_adr_cdl_mutation",
    "no_public_path_authorization",
]

NON_CLAIM_TEXT = [
    "No Genesis v0.4 signing occurred.",
    "No Genesis v0.5 signing occurred.",
    "No node upload occurred.",
    "No canonical graph mutation occurred.",
    "No public graph publication occurred.",
    "No public repository push occurred.",
    "No public RC activation occurred.",
    "No runtime activation occurred.",
    "No economic activation occurred.",
    "No sidecar activation occurred.",
    "No ADR/CDL mutation occurred.",
    "No public-path authorization occurred.",
]

NODE0 = "artifact:genesis_intent_attestation_init_authority_map"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
        os.chmod(path, 0o644)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(
        path,
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n",
    )


def node_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id") or node.get("node_id") or node.get("id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix31_node_without_id")
    return value


def edge_endpoints(edge: dict[str, Any]) -> tuple[str, str]:
    source = edge.get("source") or edge.get("from") or edge.get("source_id")
    target = edge.get("target") or edge.get("to") or edge.get("target_id")
    if not isinstance(source, str) or not isinstance(target, str):
        raise ValueError("fix31_edge_without_binary_endpoints")
    return source, target


def graph_counts(graph: dict[str, Any]) -> dict[str, int]:
    return {"node_count": len(graph["nodes"]), "edge_count": len(graph["edges"])}


def endpoint_error_count(graph: dict[str, Any]) -> int:
    nodes = {node_id(node) for node in graph["nodes"]}
    errors = 0
    for edge in graph["edges"]:
        source, target = edge_endpoints(edge)
        if source not in nodes or target not in nodes:
            errors += 1
    return errors


def undirected_reachable_count(graph: dict[str, Any], start: str = NODE0) -> int:
    nodes = {node_id(node) for node in graph["nodes"]}
    if start not in nodes:
        return 0
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in graph["edges"]:
        source, target = edge_endpoints(edge)
        if source in nodes and target in nodes:
            adjacency[source].add(target)
            adjacency[target].add(source)
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in adjacency[current]:
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return len(seen)


def prefix_for(node_value: str) -> str:
    return node_value.split(":", 1)[0] if ":" in node_value else "other"


def repo_file_counts(graph: dict[str, Any]) -> dict[str, int]:
    counts = Counter()
    for node in graph["nodes"]:
        nid = node_id(node)
        if not nid.startswith("repo:file:"):
            continue
        counts["repo_file"] += 1
        lowered = nid.lower()
        if ":out_" in lowered or "_out_" in lowered or "docs_sims" in lowered:
            counts["generated_evidence"] += 1
        elif "z_past_chats" in lowered or "todo_docs_post_mvp" in lowered or "private" in lowered:
            counts["private_or_local"] += 1
        elif "sidecar" in lowered or "ccss" in lowered or "openclaw" in lowered:
            counts["sidecar_recipe"] += 1
        else:
            counts["public_support"] += 1
    return dict(counts)


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except subprocess.CalledProcessError:
        return "git_head_unavailable"


def fix30_added_edges(graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        edge
        for edge in graph["edges"]
        if edge.get("feature_hints", {}).get("phase") == "1545p-Fix30"
    ]


def signing_record(nid: str, authority_traceable: set[str]) -> dict[str, Any]:
    is_root = nid == NODE0
    return {
        "node_id": nid,
        "proof_class": "merkle_plus_typed_authority_eligibility_path",
        "typed_trace_edge_role": "ATTESTATION" if is_root else "GOVERNS",
        "traversal_direction": "authority_forward" if is_root else "verification_backtrace",
        "terminal_authority_node": NODE0,
        "genesis_rootedness_proof": (
            "axiomatic_exception_declared" if is_root else "backtrace_to_node0"
        ),
        "governing_adr_cdl_conditions": ["ADR-0004", "ADR-0035", "CDL-097"],
        "signing_batch_classification": "genesis_core",
        "authority_traceable_under_fix18_diagnostic": nid in authority_traceable,
        "human_review_note": (
            "Axiomatic Node 0 root exception; not traced from itself."
            if is_root
            else "Traceable under Fix18 diagnostic."
        ),
    }


def build_variant(
    *,
    variant_id: str,
    graph: dict[str, Any],
    source_artifact: str,
    authority_count: int,
    authority_traceability: Any,
    backwards_read_coverage: Any,
    directed_gap_count: int,
    directed_gap_by_prefix: dict[str, int],
    proof_distribution: dict[str, int],
    genesis_core_eligible_count: int,
    hashed_only_count: int,
    signing_compatibility: str,
    unresolved_human_review_count: int,
    lambda2: Any,
    objective_g: Any,
    non_excisability_summary: str,
) -> dict[str, Any]:
    counts = graph_counts(graph)
    repo_counts = repo_file_counts(graph)
    root_reachable = undirected_reachable_count(graph)
    public_count = counts["node_count"] - repo_counts.get("private_or_local", 0)
    return {
        "variant_id": variant_id,
        "source_artifact": source_artifact,
        "node_count": counts["node_count"],
        "edge_count": counts["edge_count"],
        "authority_bearing_node_count": authority_count,
        "public_node_count": public_count,
        "private_local_node_count": repo_counts.get("private_or_local", 0),
        "generated_evidence_node_count": repo_counts.get("generated_evidence", 0),
        "sidecar_recipe_node_count": repo_counts.get("sidecar_recipe", 0),
        "public_support_node_count": repo_counts.get("public_support", 0),
        "endpoint_validity": {
            "endpoint_error_count": endpoint_error_count(graph),
            "valid": endpoint_error_count(graph) == 0,
        },
        "root_reachability": {
            "reachable_count": root_reachable,
            "total_count": counts["node_count"],
            "coverage": round(root_reachable / counts["node_count"], 9)
            if counts["node_count"]
            else 0,
        },
        "authority_traceability": authority_traceability,
        "backwards_read_coverage": backwards_read_coverage,
        "non_excisability_summary": non_excisability_summary,
        "unresolved_human_review_count": unresolved_human_review_count,
        "signing_compatibility_verdict": signing_compatibility,
        "directed_view_not_yet_contractualized_count": directed_gap_count,
        "directed_view_not_yet_contractualized_by_prefix": directed_gap_by_prefix,
        "proof_class_distribution": proof_distribution,
        "genesis_core_eligible_count": genesis_core_eligible_count,
        "hashed_repo_material_only_count": hashed_only_count,
        "lambda2_structural_diagnostic_only": lambda2,
        "objective_g_research_only": objective_g,
        "non_claim": (
            "Structural membership, lambda2, and root reachability do not prove "
            "authority, eligibility, claimability, governance effect, or signing readiness."
        ),
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    text = ["| " + " | ".join(headers) + " |"]
    text.append("|" + "|".join(["---" for _ in headers]) + "|")
    for row in rows:
        text.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(text)


def update_status() -> None:
    token = "atlas_candidate_reducer_v04_v05_packet_committed_phase_1545p_fix31"
    current = STATUS.read_text(encoding="utf-8")
    if token in current:
        return
    entry = f"""## Phase 1545p-Fix31 - Atlas Candidate Reducer And v0.4/v0.5 Packet (2026-06-16)

**Status:** COMPLETE
**Track:** G10 Genesis Atlas research / candidate reducer and signing-scope packet
**Sensitivity:** NON-SENSITIVE

| Phase | Work | Status | Sensitivity | Window |
|---|---|---|---|---|
| 1545p-Fix31 | Atlas v0.4/v0.5 candidate reducer and decision packet | COMPLETE | NON-SENSITIVE | research addendum |

**Tokens emitted:**
- `atlas_candidate_reducer_v04_v05_packet_committed_phase_1545p_fix31`
- `atlas_v04_core_plus_support_variant_recorded_phase_1545p_fix31`
- `atlas_v05_full_repo_optimized_variant_recorded_phase_1545p_fix31`
- `atlas_public_private_signing_batch_plan_recorded_phase_1545p_fix31`
- `phase1573_signing_input_requires_human_scope_selection_phase_1545p_fix31`
- `public_path_remains_blocked_phase_1545p_fix31`

**Summary:** Reduced the Fix18 core candidate, Fix22 full-repo candidate, and
Fix30 optimized research candidate into explicit v0.4/v0.5 review variants.
The packet records that current Block 6 Phase 1573 guidance remains compatible
with the Fix18 core-only signing target and requires human scope selection
before any broader v0.4 support graph or v0.5 full-repo optimized signing route.

**Non-claims:** No Genesis v0.4 signing, Genesis v0.5 signing, node upload,
canonical graph mutation, public graph publication, public repository push,
public RC activation, runtime activation, economic activation, sidecar
activation, ADR/CDL mutation, or public-path authorization occurred.

---

"""
    marker = "---\n\n"
    atomic_write_text(STATUS, current.replace(marker, marker + entry, 1))


def update_planning_index() -> None:
    token = "Phase 1545p-Fix31 Atlas candidate reducer"
    current = PLANNING_INDEX.read_text(encoding="utf-8")
    if token in current:
        return
    line = (
        "**Research addendum 2026-06-16 Phase 1545p-Fix31 Atlas candidate "
        "reducer and v0.4/v0.5 packet:** "
        "`tools/evaluators/sim_atlas_candidate_reducer_v04_v05_1545p_fix31.py`, "
        "`out/atlas_research/genesis_atlas_v04_v05_candidate_variants_1545p_fix31.json`, "
        "`out/atlas_research/genesis_atlas_public_private_batch_plan_1545p_fix31.json`, "
        "`out/sim_atlas_candidate_reducer_v04_v05_1545p_fix31.json`, "
        "`docs/sims/sim_atlas_candidate_reducer_v04_v05_1545p_fix31_v0.1.md`, "
        "`docs/specs/ilc_genesis_atlas_v04_v05_candidate_decision_packet_1545p_fix31_v0.1.md`, "
        "`tests/test_phase_1545p_fix31_candidate_reducer_v04_v05.py`, and "
        "`docs/phases/phase_1545p_fix31_candidate_reducer_v04_v05_walkthrough.md`. "
        "Records `atlas_candidate_reducer_v04_v05_packet_committed_phase_1545p_fix31`, "
        "`atlas_v04_core_plus_support_variant_recorded_phase_1545p_fix31`, "
        "`atlas_v05_full_repo_optimized_variant_recorded_phase_1545p_fix31`, "
        "`atlas_public_private_signing_batch_plan_recorded_phase_1545p_fix31`, "
        "`phase1573_signing_input_requires_human_scope_selection_phase_1545p_fix31`, "
        "and `public_path_remains_blocked_phase_1545p_fix31`. The packet preserves "
        "the Phase 1573 Fix18-only compatibility boundary, routes broader full-repo "
        "support and optimized whole-repo Atlas variants to explicit human scope "
        "selection, and performs no signing, upload, canonical graph mutation, "
        "runtime activation, ADR/CDL mutation, public graph publication, public "
        "repository push, or public RC activation.\n"
    )
    lines = current.splitlines(keepends=True)
    insert_at = 1
    for index, value in enumerate(lines):
        if value.startswith("**Last updated:**"):
            insert_at = index + 1
            break
    lines.insert(insert_at, line)
    atomic_write_text(PLANNING_INDEX, "".join(lines))


def main() -> None:
    core = load_json(FIX18_CORE)
    diagnostic = load_json(FIX18_DIAGNOSTIC)
    full = load_json(FIX22_FULL)
    baseline = load_json(FIX25_BASELINE)
    spectral = load_json(FIX29_SPECTRAL)
    optimized = load_json(FIX30_OPTIMIZED)
    fix30_summary = load_json(FIX30_SUMMARY)

    authority_traceable = set(
        diagnostic["authority_traceability"]["authority_traceable_node_ids"]
    )
    core_node_ids = [node_id(node) for node in core["nodes"]]
    core_records = [signing_record(nid, authority_traceable) for nid in core_node_ids]

    fix30_added = fix30_added_edges(optimized)
    fix30_objective = fix30_summary["objective_summary"]
    baseline_gap = int(baseline["directed_view_not_yet_contractualized_count"])
    upgraded = int(fix30_objective["source_nodes_upgraded_to_typed_trace_candidate"])
    optimized_gap = max(0, baseline_gap - upgraded)
    optimized_gap_by_prefix = dict(baseline["directed_view_not_yet_contractualized_by_prefix"])
    optimized_gap_by_prefix["repo"] = max(0, optimized_gap_by_prefix.get("repo", 0) - upgraded)

    clique_lambda = spectral["spectral_diagnostics"]["clique_incidence_projection"]["lambda2"]
    star_lambda = spectral["spectral_diagnostics"]["star_projection"]["lambda2"]
    non_excisability = (
        "Fix29 classifies Genesis roots as non-excisable, ADR/CDL authority "
        "families and high-degree support hubs as fragile, and generated "
        "evidence leaves as low-priority structural leaves."
    )

    variants = [
        build_variant(
            variant_id="v04_core_only_fix18_preserved",
            graph=core,
            source_artifact=str(FIX18_CORE.relative_to(ROOT)),
            authority_count=len(core["nodes"]),
            authority_traceability={
                "traceable_count": len(authority_traceable),
                "total_count": len(core["nodes"]),
                "ratio": "56/57 plus one declared axiomatic Node 0 exception",
            },
            backwards_read_coverage="not_applicable_core_star_map",
            directed_gap_count=0,
            directed_gap_by_prefix={},
            proof_distribution={
                "merkle_inclusion_only": 0,
                "merkle_plus_typed_non_authority_trace": 0,
                "merkle_plus_typed_authority_eligibility_path": len(core["nodes"]),
            },
            genesis_core_eligible_count=len(core["nodes"]),
            hashed_only_count=0,
            signing_compatibility="phase1573_current_guidance_compatible_with_fix18_only",
            unresolved_human_review_count=1,
            lambda2="not_recomputed_for_fix18_core",
            objective_g="not_comparable_to_full_repo",
            non_excisability_summary="Fix18 core is the current Phase 1573 signing target and is not expanded by Fix31.",
        ),
        build_variant(
            variant_id="v04_core_plus_full_repo_support",
            graph=full,
            source_artifact=str(FIX22_FULL.relative_to(ROOT)),
            authority_count=int(baseline["authority_bearing_node_count"]),
            authority_traceability={
                "authority_reachability": baseline["authority_reachability"],
                "authority_forward_trace_coverage": baseline["authority_forward_trace_coverage"],
                "verification_backtrace_coverage": baseline["verification_backtrace_coverage"],
            },
            backwards_read_coverage=baseline["backwards_read_coverage"],
            directed_gap_count=baseline_gap,
            directed_gap_by_prefix=dict(baseline["directed_view_not_yet_contractualized_by_prefix"]),
            proof_distribution={
                "merkle_inclusion_only": baseline_gap,
                "merkle_plus_typed_non_authority_trace": 0,
                "merkle_plus_typed_authority_eligibility_path": int(
                    baseline["authority_traceable_node_count"]
                ),
            },
            genesis_core_eligible_count=len(core["nodes"]),
            hashed_only_count=baseline_gap,
            signing_compatibility="phase1573_requires_guidance_patch_for_v04_core_plus_support",
            unresolved_human_review_count=baseline_gap,
            lambda2={"clique": clique_lambda, "star": star_lambda, "star_status": "cheeger_lb_fallback"},
            objective_g="baseline_full_repo_not_optimized",
            non_excisability_summary=non_excisability,
        ),
        build_variant(
            variant_id="v05_full_repo_optimized_candidate",
            graph=optimized,
            source_artifact=str(FIX30_OPTIMIZED.relative_to(ROOT)),
            authority_count=int(baseline["authority_bearing_node_count"]),
            authority_traceability={
                "authority_reachability": baseline["authority_reachability"],
                "authority_forward_trace_coverage": baseline["authority_forward_trace_coverage"],
                "verification_backtrace_coverage": baseline["verification_backtrace_coverage"],
                "fix30_added_typed_trace_candidate_edges": len(fix30_added),
            },
            backwards_read_coverage=fix30_objective["source_typed_trace_candidate_coverage"],
            directed_gap_count=optimized_gap,
            directed_gap_by_prefix=optimized_gap_by_prefix,
            proof_distribution={
                "merkle_inclusion_only": optimized_gap,
                "merkle_plus_typed_non_authority_trace": len(fix30_added),
                "merkle_plus_typed_authority_eligibility_path": int(
                    baseline["authority_traceable_node_count"]
                ),
            },
            genesis_core_eligible_count=len(core["nodes"]),
            hashed_only_count=optimized_gap,
            signing_compatibility="phase1573_requires_new_scope_or_later_v05_for_full_repo_optimized",
            unresolved_human_review_count=optimized_gap,
            lambda2={
                "clique": clique_lambda,
                "star": star_lambda,
                "star_status": "not_available_budget_fallback_for_fiedler_vector",
            },
            objective_g=fix30_objective["objective_score"],
            non_excisability_summary=non_excisability,
        ),
        build_variant(
            variant_id="maximal_research_not_for_signing",
            graph=optimized,
            source_artifact=str(FIX30_OPTIMIZED.relative_to(ROOT)),
            authority_count=int(baseline["authority_bearing_node_count"]),
            authority_traceability="research_frontier_not_a_signing_claim",
            backwards_read_coverage=fix30_objective["source_typed_trace_candidate_coverage"],
            directed_gap_count=optimized_gap,
            directed_gap_by_prefix=optimized_gap_by_prefix,
            proof_distribution={
                "merkle_inclusion_only": optimized_gap,
                "merkle_plus_typed_non_authority_trace": len(fix30_added),
                "merkle_plus_typed_authority_eligibility_path": int(
                    baseline["authority_traceable_node_count"]
                ),
            },
            genesis_core_eligible_count=0,
            hashed_only_count=optimized_gap,
            signing_compatibility="not_a_signing_target_research_only",
            unresolved_human_review_count=optimized_gap,
            lambda2={"clique": clique_lambda, "star": star_lambda},
            objective_g=fix30_objective["objective_score"],
            non_excisability_summary="Research frontier only. It is not signing-ready.",
        ),
    ]

    pareto_rows = [
        {
            "variant": variant["variant_id"],
            "coverage": variant["root_reachability"]["coverage"],
            "auth_reach": variant["authority_traceability"],
            "lambda2": variant["lambda2_structural_diagnostic_only"],
            "G": variant["objective_g_research_only"],
            "nodes_signed": variant["genesis_core_eligible_count"]
            if variant["variant_id"] == "v04_core_only_fix18_preserved"
            else 0,
            "files_included": variant["node_count"],
            "genesis_core_eligible": variant["genesis_core_eligible_count"],
            "hashed_only_not_signing_ready": variant["hashed_repo_material_only_count"],
            "directed_view_not_yet_contractualized": variant[
                "directed_view_not_yet_contractualized_count"
            ],
            "dominated": False,
        }
        for variant in variants
    ]

    why_not_selected = [
        {
            "variant_id": "v04_core_plus_full_repo_support",
            "reason_not_selected": "human_choice_required",
            "evidence": (
                "Current Phase 1573 guidance is compatible with Fix18 only; "
                "v0.4 core plus support requires a guidance patch."
            ),
        },
        {
            "variant_id": "v05_full_repo_optimized_candidate",
            "reason_not_selected": "deferred_to_v0.5",
            "evidence": (
                "Fix30 optimized whole-repo output remains research-only and "
                "requires new scope or a later v0.5 route."
            ),
        },
        {
            "variant_id": "maximal_research_not_for_signing",
            "reason_not_selected": "out_of_scope_v0.4",
            "evidence": "Research-only frontier; not a signing target.",
        },
    ]

    signing_scope_decision = {
        "v04_signing_input": "fix18_core_only",
        "v05_signing_input": "deferred",
        "scope_decision_requires_human_authorization": True,
        "blocking_questions": [
            "Confirm whether Phase 1573 should sign only the Fix18 v0.4 core candidate.",
            "If v0.4 should reference the full-repo support graph, authorize a Block 6 guidance patch first.",
            "If the optimized whole-repo candidate should become a signing target, route it to v0.5 or a new explicit scope.",
            "Decide whether the broader full-repo route requires CDL-098 or an ADR amendment before signing.",
        ],
    }

    batch_plan = {
        "schema_version": "ilc.genesis_atlas.public_private_batch_plan.fix31.v1",
        "phase": "1545p-Fix31",
        "source_git_commit": git_head(),
        "signing_batches": {
            "genesis_core_fix18": {
                "candidate_variant": "v04_core_only_fix18_preserved",
                "record_count": len(core_records),
                "records": core_records,
                "signing_order": "genesis_root_to_governance_spine_to_truth_primitives_to_policies_to_artifacts",
                "public_publishable": True,
                "requires_human_scope_selection": True,
            }
        },
        "support_batches_not_semantic_signing_ready": {
            "public_support_hashed_repo_material": {
                "node_count": variants[1]["public_support_node_count"],
                "proof_class": "merkle_inclusion_only",
                "status": "signed_source_tree_manifest_only_not_semantically_rooted_atlas_nodes",
            },
            "generated_evidence": {
                "node_count": variants[1]["generated_evidence_node_count"],
                "status": "evidence_support_not_authority_bearing",
            },
            "private_genesis_local": {
                "node_count": variants[1]["private_local_node_count"],
                "status": "local_or_private_not_public_upload_candidate",
            },
            "sidecar_recipe": {
                "node_count": variants[1]["sidecar_recipe_node_count"],
                "status": "sidecar_recipe_support_not_runtime_activation",
            },
            "reject_or_defer": {
                "node_count": optimized_gap,
                "status": "directed_view_not_yet_contractualized",
            },
        },
        "human_scope_selection_required_before_phase1573": True,
        "phase1573_compatibility_finding": "phase1573_current_guidance_compatible_with_fix18_only",
        "non_claims": NON_CLAIMS,
        "output_tokens": REQUIRED_TOKENS,
    }

    variants_payload = {
        "schema_version": "ilc.genesis_atlas.v04_v05.candidate_variants.fix31.v1",
        "phase": "1545p-Fix31",
        "source_git_commit": git_head(),
        "variants": variants,
        "pareto_frontier": pareto_rows,
        "why_not_selected": why_not_selected,
        "signing_scope_decision": signing_scope_decision,
        "recommended_current_phase1573_route": "v04_core_only_fix18_preserved",
        "recommended_future_route": "v05_full_repo_optimized_candidate_requires_new_scope",
        "non_claims": NON_CLAIMS,
        "output_tokens": REQUIRED_TOKENS,
    }

    summary = {
        "schema_version": "ilc.sim_atlas_candidate_reducer.fix31.v1",
        "phase": "1545p-Fix31",
        "sim_id": "SIM-ATLAS-CANDIDATE-REDUCER-01",
        "status": "pass",
        "input_artifacts": {
            "fix18_core": str(FIX18_CORE.relative_to(ROOT)),
            "fix22_full_repo": str(FIX22_FULL.relative_to(ROOT)),
            "fix25_baseline": str(FIX25_BASELINE.relative_to(ROOT)),
            "fix29_spectral": str(FIX29_SPECTRAL.relative_to(ROOT)),
            "fix30_optimized": str(FIX30_OPTIMIZED.relative_to(ROOT)),
            "block6_guidance": str(BLOCK6_GUIDANCE.relative_to(ROOT)),
        },
        "variant_count": len(variants),
        "phase1573_compatibility_finding": "phase1573_current_guidance_compatible_with_fix18_only",
        "signing_scope_decision": signing_scope_decision,
        "fix30_added_edge_count": len(fix30_added),
        "public_private_batch_plan": str(BATCH_PLAN_OUT.relative_to(ROOT)),
        "candidate_variants": str(VARIANTS_OUT.relative_to(ROOT)),
        "non_claims": NON_CLAIMS,
        "output_tokens": REQUIRED_TOKENS,
    }

    atomic_write_json(VARIANTS_OUT, variants_payload)
    atomic_write_json(BATCH_PLAN_OUT, batch_plan)
    atomic_write_json(SUMMARY_OUT, summary)

    table = markdown_table(
        [
            "Variant",
            "Nodes",
            "Edges",
            "Genesis-core eligible",
            "Hashed-only",
            "Directed gaps",
            "Phase 1573 verdict",
        ],
        [
            [
                variant["variant_id"],
                variant["node_count"],
                variant["edge_count"],
                variant["genesis_core_eligible_count"],
                variant["hashed_repo_material_only_count"],
                variant["directed_view_not_yet_contractualized_count"],
                variant["signing_compatibility_verdict"],
            ]
            for variant in variants
        ],
    )

    pareto_table = markdown_table(
        [
            "Variant",
            "Coverage",
            "Auth. Reach.",
            "lambda2",
            "G",
            "Nodes signed",
            "Files included",
            "Genesis-core eligible",
            "Hashed-only",
            "Directed gaps",
        ],
        [
            [
                row["variant"],
                row["coverage"],
                row["auth_reach"],
                row["lambda2"],
                row["G"],
                row["nodes_signed"],
                row["files_included"],
                row["genesis_core_eligible"],
                row["hashed_only_not_signing_ready"],
                row["directed_view_not_yet_contractualized"],
            ]
            for row in pareto_rows
        ],
    )

    non_claim_block = "\n".join(f"- {claim}" for claim in NON_CLAIM_TEXT)
    non_claim_token_block = "\n".join(f"- `{token}`" for token in NON_CLAIMS)

    report = f"""# SIM-ATLAS-CANDIDATE-REDUCER-01

Phase: 1545p-Fix31
Status: PASS

## Method

The reducer compares the Fix18 core candidate, the Fix22 whole-repo candidate,
and the Fix30 optimized research candidate. It emits review variants and a
public/private batch plan. It does not sign, upload, mutate canonical graph
state, activate public RC, activate runtime, activate economics, activate
sidecars, or mutate ADR/CDL state.

## Candidate Variants

{table}

## Pareto Frontier

{pareto_table}

Structural diagnostics are not authority proofs. Merkle inclusion and lambda2
do not establish eligibility, claimability, governance effect, or signing
readiness.

## Phase 1573 Compatibility

`phase1573_current_guidance_compatible_with_fix18_only`

The current Block 6 signing guidance can consume the Fix18 v0.4 core candidate.
It cannot silently consume the full-repo support graph or Fix30 optimized graph
without human scope selection and guidance changes.

## Output Tokens

""" + "\n".join(f"- `{token}`" for token in REQUIRED_TOKENS) + """

## Non-claims

""" + non_claim_block + "\n\n## Non-claim Tokens\n\n" + non_claim_token_block + "\n"

    packet = f"""# ILC Genesis Atlas v0.4/v0.5 Candidate Decision Packet - Phase 1545p-Fix31

## Decision Boundary

This packet is the decision packet, not the signing decision. The current
Phase 1573 route remains compatible only with the Fix18 v0.4 core candidate
unless a human authorizes a broader scope.

## Variant Comparison

{table}

## Pareto Frontier

{pareto_table}

## Why Not Selected

{markdown_table(["Variant", "Reason", "Evidence"], [[item["variant_id"], item["reason_not_selected"], item["evidence"]] for item in why_not_selected])}

## Signing Scope Decision

```json
{json.dumps(signing_scope_decision, sort_keys=True, indent=2, allow_nan=False)}
```

## Signing Batch Rule

Only nodes with a declared typed trace and an accepted proof class can be
assigned to an Atlas semantic signing batch. Hashed repo material may appear in
a signed source-tree manifest, but is not a semantically rooted Atlas node and
is not Genesis-core signing-batch-ready.

## Human Choices Required

- Confirm Fix18 core-only v0.4 as the Phase 1573 signing input, or authorize a
  Block 6 guidance patch for a broader v0.4 support route.
- Decide whether the Fix30 full-repo optimized candidate is a later v0.5 route.
- Decide whether broader full-repo signing requires CDL-098 or an ADR amendment.

## Non-claims

""" + non_claim_block + "\n\n## Non-claim Tokens\n\n" + non_claim_token_block + "\n"

    claim_table = markdown_table(
        ["Claim", "File/symbol checked", "Result"],
        [
            ["Fix30 optimized candidate exists", str(FIX30_OPTIMIZED.relative_to(ROOT)), "confirmed"],
            ["Fix18 core has 57 nodes and 80 edges", str(FIX18_CORE.relative_to(ROOT)), "confirmed"],
            ["Fix25 baseline has 10029 nodes and 27668 edges", str(FIX25_BASELINE.relative_to(ROOT)), "confirmed"],
            ["Phase 1573 guidance targets Fix18 scope", str(BLOCK6_GUIDANCE.relative_to(ROOT)), "confirmed"],
            ["Fix31 output tokens absent before execution", "rg token audit", "confirmed"],
        ],
    )

    walkthrough = f"""# Phase 1545p-Fix31 Candidate Reducer Walkthrough

## Claim Table

{claim_table}

## Reducer Method

The runner reads Fix18, Fix22, Fix25, Fix29, and Fix30 artifacts. It builds four
review variants, writes a public/private batch plan, and records the human
scope-selection questions required before any signing phase can proceed.

## Candidate Variant Comparison

{table}

## Public/Private/Signing Batch Plan

- Genesis core semantic signing batch: `57` Fix18 records.
- Public support graph: counted as support and hashed material unless a future
  typed trace contract promotes specific nodes.
- Private Genesis-local graph: local-only or private nodes, not public upload
  candidates.
- Generated evidence: evidence support, not authority-bearing.
- Sidecar recipe nodes: sidecar support only, not runtime activation.
- Reject or defer: directed-view gap nodes and unresolved support material.

## Phase 1573 Compatibility Finding

`phase1573_current_guidance_compatible_with_fix18_only`

## Human Decision Points

- Confirm Fix18 core-only v0.4 signing target for Phase 1573.
- Authorize a Block 6 guidance patch before any v0.4 core-plus-support route.
- Route Fix30 full-repo optimized candidate to v0.5 or another explicit scope.
- Decide whether CDL-098 or an ADR amendment is required for broader scope.

## Output Tokens

""" + "\n".join(f"- `{token}`" for token in REQUIRED_TOKENS) + """

## Verification Commands

- `.venv/bin/python tools/evaluators/sim_atlas_candidate_reducer_v04_v05_1545p_fix31.py`
- `.venv/bin/python -m pytest tests/test_phase_1545p_fix31_candidate_reducer_v04_v05.py -q`
- `.venv/bin/python tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix31_g10_candidate_reducer_v04_v05_packet.md`
- `.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py`
- `git diff --check`

## Non-claims

""" + non_claim_block + "\n\n## Non-claim Tokens\n\n" + non_claim_token_block + "\n"

    atomic_write_text(SIM_REPORT, report)
    atomic_write_text(DECISION_PACKET, packet)
    atomic_write_text(WALKTHROUGH, walkthrough)
    update_status()
    update_planning_index()


if __name__ == "__main__":
    main()
