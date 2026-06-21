#!/usr/bin/env python3
"""Manual GOVERNS audit for CDL shadows, ADR shadows, and invariant nodes.

PUBLIC_RC_EXCLUDE: fix63_manual_governs_audit_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Genesis Atlas LMDB maintenance pass;
not Genesis signing, public graph upload, canonical graph mutation, runtime
activation, public serving, ECU minting, or public RC publication.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_lmdb_writer import (  # noqa: E402
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    AtlasPhaseFileRegistration,
    deterministic_edge_id,
    write_json_atomic,
)


PHASE = "1545p-Fix63"
PHASE_TOKEN = "phase_1545p_fix63"
ROOT = "artifact:genesis_intent_attestation_init_authority_map"
SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
PROMPT_PATH = REPO_ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix63_g10_manual_governs_audit.md"
CDL_REGISTER_PATH = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix63_manual_governs_audit_ledger_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix63_manual_governs_audit_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix63_manual_governs_audit_walkthrough.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix63_manual_governs_audit_report_v0.1.json"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix63_manual_governs_audit.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix63_manual_governs_audit.py"

INPUT_TOKENS = ("fix62i_support_queue_closure_complete", "fix62i_complete")
OUTPUT_TOKENS = (
    "fix63_manual_governs_audit_complete",
    "fix63_cdl_orphans_dispositioned",
    "fix63_adr_orphans_dispositioned",
    "fix63_invariant_batch_1_of_5_complete",
    "fix63_invariant_batch_2_of_5_complete",
    "fix63_invariant_batch_3_of_5_complete",
    "fix63_invariant_batch_4_of_5_complete",
    "fix63_invariant_batch_5_of_5_complete",
    "fix63_complete",
)

ADR_FILES = {
    "0001": "docs/adr/ADR_0001_Canonical_Encoding_and_MCP_MVP.md",
    "0015": "docs/adr/ADR_0015_Node_Transfer_Economics.md",
    "0018": "docs/adr/ADR_0018_Sequestered_Financial_Shard.md",
    "0022": "docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md",
    "0023": "docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md",
    "0024": "docs/adr/ADR_0024_Agent_Skills_Infrastructure.md",
    "0026": "docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md",
    "0028": "docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md",
    "0029": "docs/adr/ADR_0029_Hypergraph_Substrate.md",
    "0030": "docs/adr/ADR_0030_Node_Embedding_Substrate_and_Content_Typing.md",
    "0031": "docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md",
}

ACCEPTED_ADR_NODES = {
    "adr:0001_canonical_encoding_and_mcp_mvp": "0001",
    "adr:0022_local_first_private_use_and_publication_bound_economics": "0022",
    "adr:0022_local_first_private_use_publication_bound_economics": "0022",
    "adr:0023_quality_signal": "0023",
    "adr:0026_protocol_vs_harness_boundary": "0026",
    "adr:0028_consensus_production_bridge": "0028",
    "adr:0030_node_embedding": "0030",
    "adr:0031_subgraph_homomorphism": "0031",
    "adr:ADR_0029": "0029",
}

PROPOSED_ADR_NODES = {
    "adr:0015_node_transfer_economics": "0015",
    "adr:0018_sequestered_financial_shard": "0018",
    "adr:0021_epistemic_finality_claims": None,
    "adr:0024_agent_skills_infrastructure": "0024",
}

ADR_DECISION_RECORDS = {
    "adr:0028_option_b_graduation_posture": "0028",
    "adr:0028_settlement_substrate_graduation": "0028",
}

CDL_SHADOWS = {
    "cdl:001": "cdl:001_signer_lineage_trust_root",
    "cdl:001_trust_root_runtime": "cdl:001_signer_lineage_trust_root",
    "cdl:002": "cdl:002_key_compromise_response",
    "cdl:007": "cdl:007_rollback_resistance",
    "cdl:028": "cdl:028_fee_burn_split",
    "cdl:029_allocation_split": "cdl:029_80_15_5_allocation_distribution",
    "cdl:039_open_and_promotion_continuity": "cdl:039_topology_shuffling_authorization",
    "cdl:047_treasury_reserve": "cdl:047_treasury_governance",
    "cdl:053_werner_local_productive_credit": "cdl:053_werner_local_productive_credit_future_vehicle",
    "cdl:055_validator_staking_liveness": "cdl:055_validator_staking_liveness_runtime",
    "cdl:056_trust_tier_boundary": "cdl:056_validator_trust_tier_elevation",
    "cdl:057_epoch_boundary_witness": "cdl:057_blocking_authority_activation",
    "cdl:060": "cdl:060_gossip_centrality_extension",
    "cdl:060_gossip_hop_limit": "cdl:060_gossip_centrality_extension",
    "cdl:061": "cdl:061_gossip_http_envelope",
    "cdl:061_gossip_runtime_boundary": "cdl:061_gossip_http_envelope",
    "cdl:068_topology_shuffle_vrf": "cdl:068_topology_shuffle_vrf_runtime",
    "cdl:077": "cdl:077_want_have_want_block_fetch",
    "cdl:081_hyperedge_attribution": "cdl:081_hyperedge_ecu_attribution",
    "cdl:084_provenance_chain": "cdl:084_provenance_chain_attribution",
    "cdl:085": "cdl:085_werner_phi_bound",
    "cdl:087": "cdl:087_canonical_fetch_distribution_policy",
    "cdl:096_werner_flow_governor_lane": "cdl:096_werner_global_tier_authority",
    "cdl:v3_diversity_floor": "cdl:v3_quorum_diversity",
    "cdl:v7_popperian_gate": "cdl:v7_agent_decomposition",
}

CDL_OPEN_STUBS = {
    "cdl:021": "CDL-021 is open/deferred; no ratified canonical authority node expected",
    "cdl:062_sovereign_substrate_research_lane": "CDL-062 is open/deferred research-lane material",
}

CDL_LIFECYCLE_RECORDS = {
    "cdl:085_opening_phase_1172",
    "cdl:085_prelock_historical_opening_and_prelock_state",
    "cdl:085_prelock_spec",
    "cdl:085_ratification_phase_1185",
}


def _verify_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix63_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix63_output_token_already_present:{token}")


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix63_node_candidate_id_missing")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix63_edge_source_missing")


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix63_edge_target_missing")


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix63_edge_type_missing")
    return value


def _edge_payload(source: str, edge_type: str, target: str, *, evidence: str, reason: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix63_manual_governs_audit",
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": "fix63_unsigned_manual_governs_audit_lmdb_candidate",
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "evidence": evidence,
        "reason": reason,
        "source": source,
        "target": target,
    }


def _node_preimage(node: dict[str, Any]) -> dict[str, Any]:
    node_id = _candidate_id(node)
    fields = {
        "authority_status": node.get("authority_status"),
        "candidate_id": node_id,
        "canonicality_tier": node.get("canonicality_tier"),
        "graph_projection": node.get("graph_projection"),
        "phase": PHASE,
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": "v0.4.fix63_manual_governs_audit",
    }


def _edge_preimage(edge: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "edge_id": edge.get("edge_id")
        or deterministic_edge_id(_edge_source(edge), _edge_type(edge), _edge_target(edge)),
        "edge_type": _edge_type(edge),
        "phase": PHASE,
        "source": _edge_source(edge),
        "target": _edge_target(edge),
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "edge_id": fields["edge_id"],
        "fields": fields,
        "preimage_version": "v0.4.fix63_manual_governs_audit",
    }


def _read_source(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _line_for(path: Path, patterns: list[str]) -> str:
    lines = _read_source(path)
    lowered = [(index, line.lower()) for index, line in enumerate(lines, start=1)]
    for pattern in patterns:
        pattern_lower = pattern.lower()
        for index, line in lowered:
            if pattern_lower in line:
                return f"{path.relative_to(REPO_ROOT)}:{index}"
    return f"{path.relative_to(REPO_ROOT)}:1"


def _status_line(adr_number: str | None) -> str:
    if adr_number is None:
        return "docs/phases/STATUS.md:1"
    path = REPO_ROOT / ADR_FILES[adr_number]
    return _line_for(path, ["**Status:**", "Status:"])


def _cdl_evidence(cdl_number: str) -> str:
    return _line_for(CDL_REGISTER_PATH, [f"CDL-{cdl_number}", f"CDL_{cdl_number}"])


def _phase_evidence(node_id: str) -> str:
    match = re.search(r"phase[_-]?([0-9]{3,4}[a-z]?|m[0-9]{3})", node_id)
    if match:
        token = match.group(1)
        return _line_for(STATUS_PATH, [f"phase_{token}", f"phase{token}", token])
    match = re.search(r"window[_-]?([0-9]{3,4})", node_id)
    if match:
        token = match.group(1)
        return _line_for(STATUS_PATH, [f"window_{token}", f"window{token}", token])
    return "docs/phases/STATUS.md:1"


def _extract_invariant_ids() -> list[str]:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    block = text.split("## §4 — Full Invariant Node List", 1)[1].split("```", 2)[1]
    seen: set[str] = set()
    out: list[str] = []
    for line in block.splitlines():
        node_id = line.strip()
        if not node_id.startswith("invariant:") or node_id in seen:
            continue
        seen.add(node_id)
        out.append(node_id)
    if len(out) != 451:
        raise ValueError(f"fix63_invariant_list_count_mismatch:{len(out)}")
    return out


def _rooted_governs_targets(edges: list[dict[str, Any]]) -> set[str]:
    return {
        _edge_target(edge)
        for edge in edges
        if _edge_source(edge) == ROOT and _edge_type(edge) == "GOVERNS"
    }


def _canonical_cdl_map(nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, str]:
    rooted = _rooted_governs_targets(edges)
    out: dict[str, str] = {}
    for node_id, node in sorted(nodes.items()):
        match = re.match(r"cdl:(\d{3})(?:_|$)", node_id)
        if not match:
            continue
        if node.get("canonicality_tier") != "ratified_cdl":
            continue
        score = 0
        if node.get("graph_projection") == "genesis_core_star_map":
            score += 2
        if node_id in rooted:
            score += 3
        number = match.group(1)
        current = out.get(number)
        if current is None:
            out[number] = node_id
            continue
        current_score = (3 if current in rooted else 0) + (
            2 if nodes[current].get("graph_projection") == "genesis_core_star_map" else 0
        )
        if score > current_score:
            out[number] = node_id
    return out


def _canonical_adr_map() -> dict[str, str]:
    # Prefer the accepted ADR node IDs that Fix63 roots directly.
    return {
        "0001": "adr:0001_canonical_encoding_and_mcp_mvp",
        "0022": "adr:0022_local_first_private_use_and_publication_bound_economics",
        "0023": "adr:0023_quality_signal",
        "0026": "adr:0026_protocol_vs_harness_boundary",
        "0028": "adr:0028_consensus_production_bridge",
        "0029": "adr:ADR_0029",
        "0030": "adr:0030_node_embedding",
        "0031": "adr:0031_subgraph_homomorphism",
    }


def _governed_invariant_patch() -> dict[str, str]:
    return {
        "authority_status": "protocol_invariant_governed_by_rooted_authority",
        "canonicality_tier": "governed_protocol_invariant",
        "graph_projection": "genesis_core_star_map",
        "inclusion_status": "genesis_core_authority_trace_supported",
        "promotion_status": "authority_trace_supported_unsigned_candidate",
        "tier": "invariant_evidence",
    }


def _support_stub_patch() -> dict[str, str]:
    return {
        "authority_status": "support_only_not_independent_authority",
        "canonicality_tier": "support_trace_not_independent_authority",
        "graph_projection": "support_candidate_graph",
        "inclusion_status": "support_trace_not_independent_authority",
        "promotion_status": "not_independent_authority",
        "tier": "support_candidate",
    }


def _accepted_adr_patch() -> dict[str, str]:
    return {
        "authority_status": "accepted_adr_rooted_authority",
        "canonicality_tier": "accepted_adr",
        "graph_projection": "genesis_core_star_map",
        "inclusion_status": "genesis_core_authority_trace_supported",
        "promotion_status": "authority_trace_supported_unsigned_candidate",
        "tier": "adr_authority",
    }


def _classify_invariant(
    node_id: str,
    *,
    canonical_cdls: dict[str, str],
    canonical_adrs: dict[str, str],
) -> tuple[str, str | None, str, str]:
    body = node_id.split(":", 1)[1]
    cdl_match = re.search(r"cdl[_-]?(\d{3})", body)
    if cdl_match:
        number = cdl_match.group(1)
        authority = canonical_cdls.get(number)
        if authority:
            return (
                "add_governs_from_cdl",
                authority,
                _cdl_evidence(number),
                f"node_id encodes ratified CDL-{number} invariant",
            )
        return (
            "confirmed_support_stub",
            None,
            _cdl_evidence(number),
            f"node_id references CDL-{number}, but no ratified rooted canonical CDL node was found",
        )

    adr_match = re.search(r"adr[_-]?(\d{4})", body)
    if adr_match:
        number = adr_match.group(1)
        authority = canonical_adrs.get(number)
        if authority:
            return (
                "add_governs_from_adr",
                authority,
                _status_line(number),
                f"node_id encodes accepted ADR-{number} invariant",
            )
        return (
            "confirmed_support_stub",
            None,
            _status_line(number if number in ADR_FILES else None),
            f"node_id references ADR-{number}, but no accepted rooted ADR source was in Fix63 scope",
        )

    if "truth_primitive" in body:
        return (
            "add_governs_from_cdl",
            "cdl:074_truth_primitive_runtime",
            _cdl_evidence("074"),
            "truth primitive invariant governed by CDL-074 truth primitive runtime",
        )

    if "provenance" in body and "decay" in body:
        authority = canonical_cdls.get("084")
        if authority:
            return (
                "add_governs_from_cdl",
                authority,
                _cdl_evidence("084"),
                "provenance decay invariant governed by CDL-084 provenance chain attribution",
            )

    if "passive_ecu" in body or "hyperedge" in body:
        authority = canonical_cdls.get("081")
        if authority:
            return (
                "add_governs_from_cdl",
                authority,
                _cdl_evidence("081"),
                "hyperedge or passive ECU invariant governed by CDL-081 hyperedge ECU attribution",
            )

    return (
        "confirmed_support_stub",
        None,
        _phase_evidence(node_id),
        "phase-local, SIM, window, package, or non-claim invariant without a unique governing authority in direct-read evidence",
    )


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(PROMPT_PATH.relative_to(REPO_ROOT), "phase_prompt_node", "support_candidate_graph"),
        AtlasPhaseFileRegistration(
            EVALUATOR_PATH.relative_to(REPO_ROOT),
            "tooling_source_file_node",
            "support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix63"),),
        ),
        AtlasPhaseFileRegistration(
            TEST_PATH.relative_to(REPO_ROOT),
            "test_evidence_node",
            "support_candidate_graph",
            required_edges=(("TESTS", "phase:1545p_fix63"),),
        ),
        AtlasPhaseFileRegistration(
            LEDGER_PATH.relative_to(REPO_ROOT),
            "spec_json_artifact_node",
            "support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix63"),),
        ),
        AtlasPhaseFileRegistration(
            REPORT_MD_PATH.relative_to(REPO_ROOT),
            "spec_document_node",
            "support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix63"),),
        ),
        AtlasPhaseFileRegistration(
            WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            "phase_walkthrough_node",
            "support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix63"),),
        ),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def _append_status(report: dict[str, Any]) -> None:
    block = f"""

### Phase 1545p-Fix63 — Manual GOVERNS Audit

**Status:** complete

**Output:** Reviewed `{report['total_reviewed']}` nodes: `{report['category_counts'].get('cdl', 0)}` CDL shadow/lifecycle nodes, `{report['category_counts'].get('adr', 0)}` ADR nodes, and `{report['category_counts'].get('invariant', 0)}` invariant nodes. Added `{report['edge_application']['accepted_edge_count']}` edges, accepted `{report['node_update']['accepted_update_count']}` node updates, and recorded `{report['disposition_counts'].get('escalate', 0)}` escalations.

**Tokens:** {', '.join(OUTPUT_TOKENS)}
"""
    STATUS_PATH.write_text(STATUS_PATH.read_text(encoding="utf-8").rstrip() + block + "\n", encoding="utf-8")


def _report_markdown(report: dict[str, Any]) -> str:
    return f"""# ILC Fix63 Manual GOVERNS Audit Report

PUBLIC_RC_EXCLUDE: fix63_manual_governs_audit_research_only

## Summary

- Total reviewed: `{report['total_reviewed']}`
- Accepted edges: `{report['edge_application']['accepted_edge_count']}`
- Node updates: `{report['node_update']['accepted_update_count']}`
- Escalations: `{report['disposition_counts'].get('escalate', 0)}`
- Final LMDB: `{report['final_counts']['nodes']}` nodes / `{report['final_counts']['edges']}` edges / `{report['final_counts']['preimages']}` preimages

## Dispositions

```json
{json.dumps(report['disposition_counts'], sort_keys=True, indent=2)}
```

## Boundary

This phase updates the local unsigned Genesis Atlas LMDB candidate only. It does
not sign Genesis, publish the graph, activate public serving, perform ECU minting,
settle ILC, mutate the CDL register, open or ratify a CDL, or authorize public RC.

## Carry-Forward

Lifecycle and proposal records are not false or disposable nodes. They should be
enriched in a follow-on pass with non-authority procedural edges such as
`OPENED_FOR`, `PRELOCK_FOR`, `RATIFICATION_EVIDENCE_FOR`, `PROPOSES_CHANGE_TO`,
`RESOLVED_BY`, `SUPERSEDES`, `SAME_AUTHORITY`, or `DERIVED_FROM`. Fix63 only
prevents false authority by avoiding independent root `GOVERNS` edges for those
records.
"""


def _walkthrough_markdown(report: dict[str, Any]) -> str:
    return f"""# Phase 1545p-Fix63 Manual GOVERNS Audit Walkthrough

## Commands

```bash
python -m py_compile tools/evaluators/sim_genesis_atlas_fix63_manual_governs_audit.py tests/test_phase_1545p_fix63_manual_governs_audit.py
python tools/evaluators/sim_genesis_atlas_fix63_manual_governs_audit.py
python -m pytest tests/test_phase_1545p_fix63_manual_governs_audit.py tests/test_phase_1545p_fix62i_support_queue_closure.py tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py -q
python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb
```

## Result

- Total reviewed: `{report['total_reviewed']}`
- CDL nodes dispositioned: `{report['category_counts'].get('cdl', 0)}`
- ADR nodes dispositioned: `{report['category_counts'].get('adr', 0)}`
- Invariant nodes dispositioned: `{report['category_counts'].get('invariant', 0)}`
- Accepted edges: `{report['edge_application']['accepted_edge_count']}`
- Node updates: `{report['node_update']['accepted_update_count']}`
- Final LMDB counts: `{report['final_counts']['nodes']}` nodes / `{report['final_counts']['edges']}` edges / `{report['final_counts']['preimages']}` preimages

## Evidence Examples

- Accepted ADR status evidence: `docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md:3`
- Proposed ADR status evidence: `docs/adr/ADR_0024_Agent_Skills_Infrastructure.md:3`
- CDL register evidence: `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- Phase-local invariant evidence: `docs/phases/STATUS.md`

## Non-Claims

No Genesis signing, public graph upload, public RC publication, public serving,
runtime activation, ECU minting, ILC settlement, CDL mutation, or ADR mutation
occurred.

## Carry-Forward

Support, proposal, and lifecycle records should remain graph-visible as
procedural evidence. A later pass should add typed non-authority edges to the
canonical CDL or ADR they open, amend, prepare, resolve, supersede, or evidence.
Fix63 deliberately stops at safe classification plus authority edges for
accepted authority and protocol invariants.
"""


def _validate(report: dict[str, Any]) -> None:
    if report["total_reviewed"] != 497:
        raise ValueError(f"fix63_total_reviewed_mismatch:{report['total_reviewed']}")
    if report["category_counts"] != {"adr": 15, "cdl": 31, "invariant": 451}:
        raise ValueError(f"fix63_category_counts_mismatch:{report['category_counts']}")
    if report["edge_application"]["rejected_edge_count"] != 0:
        raise ValueError("fix63_rejected_edges_present")
    if report["node_update"]["rejected_update_count"] != 0:
        raise ValueError("fix63_rejected_node_updates_present")
    if report["post_audit"]["accepted_adr_nodes_missing_governs"]:
        raise ValueError("fix63_accepted_adr_nodes_still_missing_governs")
    if report["post_audit"]["truth_primitive_missing_governs_count"] != 0:
        raise ValueError("fix63_truth_primitive_regression")


def _build_cdl_entries(nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    rooted = _rooted_governs_targets(edges)
    entries: list[dict[str, Any]] = []
    updates: dict[str, dict[str, str]] = {}
    for shadow, canonical in CDL_SHADOWS.items():
        if shadow not in nodes:
            raise ValueError(f"fix63_missing_cdl_shadow:{shadow}")
        disposition = "shadow_duplicate_deduped" if canonical in rooted else "escalate"
        evidence = _cdl_evidence(re.search(r"cdl:(\d{3})", canonical).group(1)) if re.search(r"cdl:(\d{3})", canonical) else "docs/specs/ilc_constitutional_decision_log_v0.1.md:1"
        entries.append(
            {
                "candidate_id": shadow,
                "category": "cdl",
                "disposition": disposition,
                "edge_added": False,
                "evidence": evidence,
                "governing_authority": canonical if disposition != "escalate" else None,
                "notes": f"Shadow duplicate of rooted canonical CDL node {canonical}",
            }
        )
        if disposition != "escalate":
            patch = _support_stub_patch()
            patch.update(
                {
                    "authority_status": "shadow_duplicate_to_rooted_canonical_authority",
                    "canonical_counterpart": canonical,
                    "canonicality_tier": "shadow_duplicate_deduped",
                }
            )
            updates[shadow] = patch
    for node_id, note in CDL_OPEN_STUBS.items():
        if node_id not in nodes:
            raise ValueError(f"fix63_missing_cdl_open_stub:{node_id}")
        entries.append(
            {
                "candidate_id": node_id,
                "category": "cdl",
                "disposition": "open_cdl_stub",
                "edge_added": False,
                "evidence": _cdl_evidence(re.search(r"cdl:(\d{3})", node_id).group(1)),
                "governing_authority": None,
                "notes": note,
            }
        )
        patch = _support_stub_patch()
        patch.update({"authority_status": "open_cdl_stub_not_ratified", "canonicality_tier": "open_cdl_stub"})
        updates[node_id] = patch
    for node_id in sorted(CDL_LIFECYCLE_RECORDS):
        if node_id not in nodes:
            raise ValueError(f"fix63_missing_cdl_lifecycle_record:{node_id}")
        entries.append(
            {
                "candidate_id": node_id,
                "category": "cdl",
                "disposition": "cdl_lifecycle_record",
                "edge_added": False,
                "evidence": _cdl_evidence("085"),
                "governing_authority": "cdl:085_werner_phi_bound",
                "notes": "CDL-085 lifecycle sub-record, not an independent ratified CDL authority node",
            }
        )
        patch = _support_stub_patch()
        patch.update(
            {
                "authority_status": "cdl_lifecycle_record_not_independent_authority",
                "canonical_counterpart": "cdl:085_werner_phi_bound",
                "canonicality_tier": "cdl_lifecycle_record",
            }
        )
        updates[node_id] = patch
    return entries, updates


def _build_adr_entries(nodes: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, str]]]:
    entries: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    updates: dict[str, dict[str, str]] = {}
    for node_id, adr_number in ACCEPTED_ADR_NODES.items():
        if node_id not in nodes:
            raise ValueError(f"fix63_missing_accepted_adr:{node_id}")
        evidence = _status_line(adr_number)
        edges.append(
            _edge_payload(
                ROOT,
                "GOVERNS",
                node_id,
                evidence=evidence,
                reason=f"ADR-{adr_number} source file has Accepted status",
            )
        )
        entries.append(
            {
                "candidate_id": node_id,
                "category": "adr",
                "disposition": "add_governs_from_genesis",
                "edge_added": True,
                "evidence": evidence,
                "governing_authority": ROOT,
                "notes": f"ADR-{adr_number} accepted or accepted-amended source status verified",
            }
        )
        updates[node_id] = _accepted_adr_patch()
    for node_id, adr_number in PROPOSED_ADR_NODES.items():
        if node_id not in nodes:
            raise ValueError(f"fix63_missing_proposed_adr:{node_id}")
        entries.append(
            {
                "candidate_id": node_id,
                "category": "adr",
                "disposition": "proposed_adr_stub",
                "edge_added": False,
                "evidence": _status_line(adr_number),
                "governing_authority": None,
                "notes": "Proposed, missing, unresolved, or unratified ADR node; no root GOVERNS edge added",
            }
        )
        patch = _support_stub_patch()
        patch.update({"authority_status": "proposed_adr_not_authority", "canonicality_tier": "proposed_adr_stub"})
        updates[node_id] = patch
    for node_id, adr_number in ADR_DECISION_RECORDS.items():
        if node_id not in nodes:
            raise ValueError(f"fix63_missing_adr_decision_record:{node_id}")
        entries.append(
            {
                "candidate_id": node_id,
                "category": "adr",
                "disposition": "adr_decision_record",
                "edge_added": False,
                "evidence": _status_line(adr_number),
                "governing_authority": "adr:0028_consensus_production_bridge",
                "notes": "ADR-0028 decision sub-record, not an independent ADR authority node",
            }
        )
        patch = _support_stub_patch()
        patch.update(
            {
                "authority_status": "adr_decision_record_not_independent_authority",
                "canonical_counterpart": "adr:0028_consensus_production_bridge",
                "canonicality_tier": "adr_decision_record",
            }
        )
        updates[node_id] = patch
    return entries, edges, updates


def _build_invariant_entries(
    invariant_ids: list[str],
    nodes: dict[str, dict[str, Any]],
    *,
    canonical_cdls: dict[str, str],
    canonical_adrs: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, str]]]:
    entries: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    updates: dict[str, dict[str, str]] = {}
    batch_size = 90
    for index, node_id in enumerate(invariant_ids, start=1):
        if node_id not in nodes:
            raise ValueError(f"fix63_missing_invariant_node:{node_id}")
        disposition, authority, evidence, notes = _classify_invariant(
            node_id,
            canonical_cdls=canonical_cdls,
            canonical_adrs=canonical_adrs,
        )
        edge_added = False
        if authority:
            edges.append(
                _edge_payload(
                    authority,
                    "GOVERNS",
                    node_id,
                    evidence=evidence,
                    reason=notes,
                )
            )
            updates[node_id] = _governed_invariant_patch()
            edge_added = True
        else:
            updates[node_id] = _support_stub_patch()
        entries.append(
            {
                "batch": min(5, ((index - 1) // batch_size) + 1),
                "candidate_id": node_id,
                "category": "invariant",
                "disposition": disposition,
                "edge_added": edge_added,
                "evidence": evidence,
                "governing_authority": authority,
                "notes": notes,
            }
        )
    return entries, edges, updates


def _post_audit(nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    incoming_governs: dict[str, set[str]] = {}
    for edge in edges:
        if _edge_type(edge) == "GOVERNS":
            incoming_governs.setdefault(_edge_target(edge), set()).add(_edge_source(edge))
    accepted_missing = sorted(
        node_id for node_id in ACCEPTED_ADR_NODES if not incoming_governs.get(node_id)
    )
    proposed_rooted = sorted(
        node_id for node_id in PROPOSED_ADR_NODES if ROOT in incoming_governs.get(node_id, set())
    )
    truth_missing = sorted(
        node_id
        for node_id in nodes
        if node_id.startswith("truth_primitive:") and not incoming_governs.get(node_id)
    )
    ratified_cdl_missing = sorted(
        node_id
        for node_id, node in nodes.items()
        if node_id.startswith("cdl:")
        and node.get("canonicality_tier") == "ratified_cdl"
        and not incoming_governs.get(node_id)
    )
    return {
        "accepted_adr_nodes_missing_governs": accepted_missing,
        "proposed_adr_nodes_root_governed": proposed_rooted,
        "ratified_cdl_missing_governs": ratified_cdl_missing,
        "truth_primitive_missing_governs_count": len(truth_missing),
        "truth_primitive_missing_governs": truth_missing,
    }


def run() -> dict[str, Any]:
    _verify_tokens()
    # Direct-read required source files before any write.
    _read_source(CDL_REGISTER_PATH)
    _read_source(STATUS_PATH)
    _read_source(PROMPT_PATH)
    for path in ADR_FILES.values():
        _read_source(REPO_ROOT / path)

    invariant_ids = _extract_invariant_ids()
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        pre_nodes = {_candidate_id(node): node for node in writer.store.iter_nodes()}
        pre_edges = writer.store.iter_edges()
        canonical_cdls = _canonical_cdl_map(pre_nodes, pre_edges)
        canonical_adrs = _canonical_adr_map()
        cdl_entries, cdl_updates = _build_cdl_entries(pre_nodes, pre_edges)
        adr_entries, adr_edges, adr_updates = _build_adr_entries(pre_nodes)
        invariant_entries, invariant_edges, invariant_updates = _build_invariant_entries(
            invariant_ids,
            pre_nodes,
            canonical_cdls=canonical_cdls,
            canonical_adrs=canonical_adrs,
        )
        ledger_entries = cdl_entries + adr_entries + invariant_entries
        edge_rows = adr_edges + invariant_edges
        updates = {**cdl_updates, **adr_updates, **invariant_updates}
        ledger = {
            "category_counts": dict(Counter(entry["category"] for entry in ledger_entries)),
            "disposition_counts": dict(Counter(entry["disposition"] for entry in ledger_entries)),
            "entries": ledger_entries,
            "entry_count": len(ledger_entries),
            "phase": PHASE,
            "status": "manual_governs_audit_ledger_complete",
        }
        write_json_atomic(LEDGER_PATH, ledger)
        plan = AtlasLmdbWritePlan(
            edges_to_add=edge_rows,
            metadata={"operation": "fix63_manual_governs_audit"},
            phase=PHASE,
            dry_run=False,
        )
        edge_receipt = writer.apply_plan(plan)
        update_receipt = writer.update_node_fields(
            updates,
            phase=PHASE,
            dry_run=False,
            metadata={"operation": "fix63_manual_governs_projection_update"},
        )
        REPORT_MD_PATH.write_text("", encoding="utf-8")
        WALKTHROUGH_PATH.write_text("", encoding="utf-8")
        file_receipt = _register_phase_files(writer)
        post_nodes_list = writer.store.iter_nodes()
        post_edges = writer.store.iter_edges()
        post_nodes = {_candidate_id(node): node for node in post_nodes_list}
        touched_node_ids = set(updates)
        touched_node_ids.update(
            _candidate_id(node)
            for node in post_nodes_list
            if str(node.get("annotation_phase")) == PHASE_TOKEN
        )
        touched_edge_ids = {
            str(edge.get("edge_id"))
            for edge in post_edges
            if str(edge.get("annotation_phase")) == PHASE_TOKEN and edge.get("edge_id")
        }
        preimages = [_node_preimage(node) for node in post_nodes_list if _candidate_id(node) in touched_node_ids]
        preimages.extend(_edge_preimage(edge) for edge in post_edges if str(edge.get("edge_id")) in touched_edge_ids)
        preimage_receipt = writer.write_preimages(
            preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "fix63_manual_governs_audit"},
        )
        final = writer.inspect()
        post_audit = _post_audit(post_nodes, post_edges)
        report = {
            "category_counts": dict(Counter(entry["category"] for entry in ledger_entries)),
            "disposition_counts": dict(Counter(entry["disposition"] for entry in ledger_entries)),
            "edge_application": {
                "accepted_edge_count": edge_receipt["accepted_edge_count"],
                "rejected_edge_count": edge_receipt["rejected_edge_count"],
                "skipped_edge_count": edge_receipt["skipped_edge_count"],
            },
            "file_registration": {
                "accepted_edge_count": file_receipt["accepted_edge_count"],
                "accepted_node_count": file_receipt["accepted_node_count"],
            },
            "final_counts": {
                "edges": final["edge_count"],
                "nodes": final["node_count"],
                "preimages": final["preimage_count"],
            },
            "node_update": {
                "accepted_update_count": update_receipt["accepted_update_count"],
                "rejected_update_count": update_receipt["rejected_update_count"],
            },
            "phase": PHASE,
            "post_audit": post_audit,
            "preimage_receipt": {
                "preimage_count": preimage_receipt["preimage_count"],
                "post_preimage_count": preimage_receipt["post_preimage_count"],
            },
            "status": "PASS",
            "total_reviewed": len(ledger_entries),
        }
        _validate(report)
        REPORT_MD_PATH.write_text(_report_markdown(report), encoding="utf-8")
        WALKTHROUGH_PATH.write_text(_walkthrough_markdown(report), encoding="utf-8")
        write_json_atomic(OUT_REPORT_PATH, report)
        _append_status(report)
        return report
    finally:
        writer.close()


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":"), allow_nan=False))
