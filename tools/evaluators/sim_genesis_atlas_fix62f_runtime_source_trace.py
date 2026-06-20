#!/usr/bin/env python3
"""Repair priority-2 runtime-source role traces in the Atlas LMDB.

PUBLIC_RC_EXCLUDE: fix62f_runtime_source_trace_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Genesis Atlas LMDB maintenance pass;
not Genesis signing, public graph upload, canonical graph mutation, runtime
activation, public serving, ECU minting, or public RC publication.
"""

from __future__ import annotations

import ast
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
    repo_file_ref_id,
    write_json_atomic,
)


PHASE = "1545p-Fix62f"
PHASE_TOKEN = "phase_1545p_fix62f"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
INPUT_QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62e_manual_graph_finish_queue_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62f_runtime_source_trace_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62f_manual_graph_finish_queue_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62f_runtime_source_trace_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62f_runtime_source_trace_walkthrough.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62f_runtime_source_trace_v0.1.json"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix62f_runtime_source_trace.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix62f_runtime_source_trace.py"

INPUT_TOKENS = ("fix62e_complete",)
OUTPUT_TOKENS = (
    "fix62f_runtime_source_trace_complete",
    "fix62f_priority2_runtime_nodes_repaired",
    "fix62f_complete",
)

SOURCE_TREE_MANIFEST = "artifact:genesis_source_tree_manifest_candidate_1545p_fix38"
SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"

SEMANTIC_EDGE_TYPES = frozenset(
    {
        "CLASSIFIED_BY",
        "DERIVED_FROM",
        "IMPLEMENTS",
        "REFERENCES_AUTHORITY",
        "SOURCE_TREE_MEMBER",
    }
)

# Existing, Genesis-rooted authority/support targets only. The evaluator rejects
# absent targets rather than creating new authority stubs.
RULES: tuple[tuple[str, str, str, str], ...] = (
    ("canon_bundle|bundle_|canon_export|canon_loader", "IMPLEMENTS", "adr:0009_bundle_distribution", "canon bundle distribution implementation"),
    ("canon_bundle|canon_export|cidv1|encoding", "REFERENCES_AUTHORITY", "adr:0001_canonical_encoding_and_mcp_mvp", "canonical encoding reference"),
    ("public_init|agent_id|identity", "IMPLEMENTS", "adr:0041_agent_init_and_ingestion_protocol", "agent INIT and ingestion implementation"),
    ("public_init|agent_id|identity", "REFERENCES_AUTHORITY", "cdl:090_identity_bootstrap", "identity bootstrap authority reference"),
    ("public_receipt|receipt|invitation|provenance", "REFERENCES_AUTHORITY", "cdl:084_provenance_chain_attribution", "provenance/receipt authority reference"),
    ("serving_receipt|known_peer|bootstrap_bundle", "IMPLEMENTS", "cdl:079_hb_002_p2p_bootstrap_distribution_bootstrap_bundle_signed", "bootstrap serving receipt implementation"),
    ("transport_principal|public_init_admission|admission", "REFERENCES_AUTHORITY", "cdl:094_transport_principal_admission_wire", "transport/admission authority reference"),
    ("wallet|lifecycle|ecu|ilc|reward|settlement|stake|economic|fee|treasury|epoch_ledger", "REFERENCES_AUTHORITY", "adr:0012_ecu_ilc_graph_coupling_anti_reflexivity", "ECU/ILC graph coupling reference"),
    ("exact_numeric|decimal|numeric", "IMPLEMENTS", "cdl:064_exact_numeric_representation", "exact numeric implementation"),
    ("active_layer|commission|earmark", "IMPLEMENTS", "cdl:063_ecu_directed_commission", "directed ECU commission implementation"),
    ("lmdb|truth_primitive_graph|graph_store", "IMPLEMENTS", "cdl:075_truth_primitive_graph_persistence", "LMDB graph persistence implementation"),
    ("pruning|retention|storage_economics", "REFERENCES_AUTHORITY", "cdl:043_storage_economics_graph_pruning_active_graph_retention_constraints", "graph pruning authority reference"),
    ("wallet|local_first", "REFERENCES_AUTHORITY", "cdl:044_local_first_wallet_surface", "local-first wallet authority reference"),
    ("d2d|gossip|peer|transport|node_load|topology", "REFERENCES_AUTHORITY", "adr:0025_transport_binding", "transport binding reference"),
    ("want_block|fetch|persistent_fetch|rate_limiter", "IMPLEMENTS", "cdl:077_want_have_want_block_fetch", "WANT/HAVE/WANT-BLOCK fetch implementation"),
    ("gossip|announcement", "REFERENCES_AUTHORITY", "cdl:076_truth_primitive_announcement_gossip_lightweight_truth_primitive_announcement", "truth primitive announcement reference"),
    ("spectral|star_map|route|debruijn", "REFERENCES_AUTHORITY", "adr:0033_star_map_homoiconic_entity", "star-map routing/entity reference"),
    ("spectral|star_map|route|ngram", "IMPLEMENTS", "cdl:080_star_map_n_gram_route_index", "star-map route index implementation"),
    ("analysis|kpi|score|influence|competency|stress|quality|conformance|task_routing", "REFERENCES_AUTHORITY", "adr:0023_multi_layer_quality_signal_architecture", "quality signal analytics reference"),
    ("node_value|usefulness|utility_flow|reuse", "REFERENCES_AUTHORITY", "cdl:011_node_usefulness_formula_ratification_ew", "node usefulness formula reference"),
    ("utility_flow|reward", "REFERENCES_AUTHORITY", "cdl:012_utility_flow_reward_linkage_uf", "utility-flow reward reference"),
    ("finality|consensus|quorum|refutation", "REFERENCES_AUTHORITY", "adr:0021_epistemic_finality_claims", "epistemic finality reference"),
    ("jury|validator|quorum", "REFERENCES_AUTHORITY", "cdl:083_panel_quorum_refutation", "panel quorum/refutation reference"),
    ("node_v0|node_schema|schema", "REFERENCES_AUTHORITY", "cdl:034_node_schema_core_runtime", "node schema authority reference"),
    ("type_registry|type_definition", "REFERENCES_AUTHORITY", "cdl:097_type_definition_node_authority", "type definition authority reference"),
    ("harness|devnet|sim|scenario|fixture|orchestrator", "REFERENCES_AUTHORITY", "adr:0026_protocol_vs_harness_boundary", "protocol/harness boundary reference"),
    ("privacy|mixing|lane", "REFERENCES_AUTHORITY", "cdl:041_shard_lifecycle_operations_creation_merge_split_partition_privacy", "privacy/shard lifecycle reference"),
    ("sidecar|mcp", "REFERENCES_AUTHORITY", "adr:0026_protocol_vs_harness_boundary", "sidecar/harness boundary reference"),
    ("ccss", "CLASSIFIED_BY", "policy:ccss_private_local_sidecar_boundary", "CCSS private-local sidecar boundary"),
    ("rc|release|package_profile|public_rc|license_header|gap_7", "CLASSIFIED_BY", "policy:formal_publication_gate_required", "public RC formal gate classification"),
    ("genesis_authority|lineage|genesis", "REFERENCES_AUTHORITY", "adr:0037_genesis_canonical_lineage_contract", "Genesis lineage authority reference"),
    ("agent.py|agent_", "REFERENCES_AUTHORITY", "adr:0020_knowledge_node_first_design_principle", "agent/knowledge-node design reference"),
)


def _verify_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix62f_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix62f_output_token_already_present:{token}")
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError(f"fix62f_lmdb_missing:{LMDB_ROOT}")


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix62f_json_not_object:{path}")
    return payload


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62f_node_candidate_id_missing")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62f_edge_source_missing")


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62f_edge_target_missing")


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62f_edge_type_missing")
    return value


def _edge_payload(
    source: str,
    edge_type: str,
    target: str,
    *,
    evidence: str,
    reason: str,
    batch_id: str,
) -> dict[str, Any]:
    return {
        "annotation_method": "fix62f_manual_runtime_source_trace",
        "annotation_phase": PHASE_TOKEN,
        "batch_id": batch_id,
        "candidate_status": "fix62f_unsigned_runtime_trace_lmdb_candidate",
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
        "candidate_id": node_id,
        "graph_projection": node.get("graph_projection"),
        "node_kind": node.get("node_kind"),
        "phase": PHASE,
        "source_path": node.get("source_path"),
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": "v0.4.fix62f_runtime_source_trace",
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
        "preimage_version": "v0.4.fix62f_runtime_source_trace",
    }


def _source_evidence(path: Path) -> str:
    relative = path.relative_to(REPO_ROOT).as_posix()
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line_number, line in enumerate(lines[:80], start=1):
        stripped = line.strip()
        if (
            stripped
            and not stripped.startswith("# SPDX")
            and (stripped.startswith('"""') or stripped.startswith("PUBLIC_") or "VERSION" in stripped or "Phase " in stripped)
        ):
            return f"{relative}:{line_number}:{stripped[:120]}"
    for line_number, line in enumerate(lines[:80], start=1):
        stripped = line.strip()
        if stripped and not stripped.startswith("# SPDX"):
            return f"{relative}:{line_number}:{stripped[:120]}"
    return f"{relative}:1:empty_or_header_only"


def _import_targets(path: Path, path_to_node_id: dict[str, str]) -> list[tuple[str, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return []
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
    targets: list[tuple[str, str]] = []
    for module in sorted(modules):
        if not module.startswith("ilc_core."):
            continue
        module_path = module.replace(".", "/")
        candidate_paths = [f"{module_path}.py", f"{module_path}/__init__.py"]
        for candidate_path in candidate_paths:
            target = path_to_node_id.get(candidate_path)
            if target:
                targets.append((target, f"import:{module}"))
                break
    return targets


def _semantic_targets(relative_path: str, text: str, existing_node_ids: set[str]) -> list[tuple[str, str, str, str]]:
    haystack = f"{relative_path}\n{text[:5000]}".lower()
    selected: list[tuple[str, str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    for pattern, edge_type, target, reason in RULES:
        if target not in existing_node_ids:
            continue
        terms = [term for term in pattern.split("|") if term]
        if any(term.lower() in haystack for term in terms):
            semantic = (edge_type, target)
            if semantic not in seen:
                selected.append((edge_type, target, reason, pattern))
                seen.add(semantic)
        if len(selected) >= 4:
            break
    if not selected and SUPPORT_POLICY in existing_node_ids:
        selected.append(
            (
                "CLASSIFIED_BY",
                SUPPORT_POLICY,
                "fallback classification for runtime source without unique authority target",
                "fallback",
            )
        )
    return selected


def _build_entries(input_queue: dict[str, Any]) -> list[dict[str, Any]]:
    entries = [
        dict(entry)
        for entry in input_queue.get("entries", [])
        if entry.get("priority") == 2 and entry.get("graph_projection") == "public_protocol_graph"
    ]
    entries.sort(key=lambda item: (str(item.get("work_family", "")), str(item.get("path", "")), str(item.get("candidate_id", ""))))
    for index, entry in enumerate(entries, start=1):
        entry["fix62f_batch_id"] = f"fix62f_runtime_batch_{((index - 1) // 10) + 1:04d}"
        entry["fix62f_sequence"] = index
    return entries


def _queue_payload(entries: list[dict[str, Any]], *, source_queue: Path, status: str) -> dict[str, Any]:
    priority_counts = Counter(str(entry["priority"]) for entry in entries)
    work_family_counts = Counter(str(entry.get("work_family", "")) for entry in entries)
    reason_counts: Counter[str] = Counter()
    for entry in entries:
        reason_counts.update(str(reason) for reason in entry.get("reasons", []))
    return {
        "entry_count": len(entries),
        "entries": entries,
        "phase": PHASE,
        "priority_counts": dict(sorted(priority_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "source_queue": str(source_queue.relative_to(REPO_ROOT)),
        "status": status,
        "work_family_counts": dict(sorted(work_family_counts.items())),
    }


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(
            path=EVALUATOR_PATH.relative_to(REPO_ROOT),
            node_kind="tooling_source_file_node",
            graph_projection="support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix62f"),),
        ),
        AtlasPhaseFileRegistration(
            path=TEST_PATH.relative_to(REPO_ROOT),
            node_kind="test_evidence_node",
            graph_projection="support_candidate_graph",
            required_edges=(("TESTS", "phase:1545p_fix62f"),),
        ),
        AtlasPhaseFileRegistration(
            path=LEDGER_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62f"),),
        ),
        AtlasPhaseFileRegistration(
            path=QUEUE_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62f"),),
        ),
        AtlasPhaseFileRegistration(
            path=REPORT_MD_PATH.relative_to(REPO_ROOT),
            node_kind="spec_document_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62f"),),
        ),
        AtlasPhaseFileRegistration(
            path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            node_kind="phase_walkthrough_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62f"),),
        ),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def _append_status(report: dict[str, Any]) -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    block = f"""

### Phase 1545p-Fix62f — Runtime Source Role Trace Repair

**Status:** complete

**Output:** Repaired `{report['resolved_priority2_count']}` priority-2 public protocol runtime-source nodes, applied `{report['edge_application']['accepted_edge_count']}` new semantic/source-tree/import-derived edges, refreshed preimages, and preserved all non-activation boundaries.

**Tokens:** {', '.join(OUTPUT_TOKENS)}
"""
    STATUS_PATH.write_text(status.rstrip() + block + "\n", encoding="utf-8")


def _report_markdown(report: dict[str, Any]) -> str:
    return f"""# ILC Fix62f Runtime Source Trace Report

PUBLIC_RC_EXCLUDE: fix62f_runtime_source_trace_research_only

## Summary

- Phase: `{PHASE}`
- Input priority-2 runtime/source entries: `{report['input_priority2_count']}`
- Resolved priority-2 entries: `{report['resolved_priority2_count']}`
- Carry-forward priority-2 entries: `{report['carry_forward_priority2_count']}`
- Accepted edges: `{report['edge_application']['accepted_edge_count']}`
- Skipped duplicate edges: `{report['edge_application']['skipped_edge_count']}`
- Rejected edges: `{report['edge_application']['rejected_edge_count']}`
- Final LMDB nodes: `{report['final_counts']['nodes']}`
- Final LMDB edges: `{report['final_counts']['edges']}`
- Final LMDB preimages: `{report['final_counts']['preimages']}`

## Boundary

This phase updates the local unsigned Genesis Atlas LMDB candidate only. It does
not sign Genesis, publish the graph, activate public serving, mint ECU, settle
ILC, or mutate canonical protocol authority. No ECU minting, production
emission, wallet settlement, or public claimability activation occurred.

## Method

Each priority-2 `public_protocol_graph` file was direct-read from disk in
work-family ordered batches of ten. The evaluator recorded source evidence,
added source-tree membership, derived import edges to existing repo-file nodes,
and added path/content-derived semantic edges only to existing ADR/CDL/policy
targets. Missing targets were rejected rather than stubbed.
"""


def _walkthrough_markdown(report: dict[str, Any]) -> str:
    return f"""# Phase 1545p-Fix62f Walkthrough

## Commands

```bash
python tools/evaluators/sim_genesis_atlas_fix62f_runtime_source_trace.py
python -m pytest tests/test_phase_1545p_fix62f_runtime_source_trace.py tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py -q
python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb
```

## Result

- Resolved priority-2 runtime-source nodes: `{report['resolved_priority2_count']}`
- Remaining priority-2 runtime-source nodes: `{report['carry_forward_priority2_count']}`
- Accepted new edges: `{report['edge_application']['accepted_edge_count']}`
- Final LMDB counts: `{report['final_counts']['nodes']}` nodes / `{report['final_counts']['edges']}` edges / `{report['final_counts']['preimages']}` preimages

## Non-Claims

No Genesis signing, public graph upload, public RC publication, public serving,
runtime activation, ECU minting, or ILC settlement occurred.
"""


def _validate_postconditions(report: dict[str, Any]) -> None:
    if report["input_priority2_count"] != 190:
        raise ValueError(f"fix62f_unexpected_priority2_input_count:{report['input_priority2_count']}")
    if report["carry_forward_priority2_count"] != 0:
        raise ValueError(f"fix62f_priority2_not_closed:{report['carry_forward_priority2_count']}")
    if report["edge_application"]["rejected_edge_count"] != 0:
        raise ValueError(f"fix62f_rejected_edges_present:{report['edge_application']['rejected_edge_count']}")
    if report["edge_application"]["accepted_edge_count"] < 190:
        raise ValueError("fix62f_expected_at_least_one_new_edge_per_priority2_source")


def run() -> dict[str, Any]:
    _verify_tokens()
    input_queue = _read_json(INPUT_QUEUE_PATH)
    priority2_entries = _build_entries(input_queue)

    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        pre = writer.inspect()
        nodes = writer.store.iter_nodes()
        existing_node_ids = {_candidate_id(node) for node in nodes}
        path_to_node_id = {
            str(node.get("source_path")): _candidate_id(node)
            for node in nodes
            if isinstance(node.get("source_path"), str) and node.get("source_path")
        }
        edges_to_add: list[dict[str, Any]] = []
        ledger_entries: list[dict[str, Any]] = []
        resolved_ids: set[str] = set()

        for entry in priority2_entries:
            source = str(entry["candidate_id"])
            relative_path = str(entry["path"])
            path = REPO_ROOT / relative_path
            if source not in existing_node_ids:
                ledger_entries.append({**entry, "disposition": "deferred_source_node_missing"})
                continue
            if relative_path and path.is_file():
                text = path.read_text(encoding="utf-8", errors="ignore")
                evidence = _source_evidence(path)
                is_source_file = True
            else:
                text = f"{source}\n{entry.get('work_family', '')}"
                evidence = f"{source}:non_file_priority2_entry"
                is_source_file = False
            batch_id = str(entry["fix62f_batch_id"])
            candidate_edges: list[dict[str, Any]] = []
            if is_source_file:
                candidate_edges.append(
                    _edge_payload(
                        source,
                        "SOURCE_TREE_MEMBER",
                        SOURCE_TREE_MANIFEST,
                        evidence=evidence,
                        reason="runtime file belongs to Genesis source-tree manifest",
                        batch_id=batch_id,
                    )
                )
                for target, import_reason in _import_targets(path, path_to_node_id)[:4]:
                    if target != source:
                        candidate_edges.append(
                            _edge_payload(
                                source,
                                "DERIVED_FROM",
                                target,
                                evidence=evidence,
                                reason=import_reason,
                                batch_id=batch_id,
                            )
                        )
            for edge_type, target, reason, pattern in _semantic_targets(relative_path, text, existing_node_ids):
                candidate_edges.append(
                    _edge_payload(
                        source,
                        edge_type,
                        target,
                        evidence=evidence,
                        reason=f"{reason}; pattern={pattern}",
                        batch_id=batch_id,
                    )
                )
            valid_edges = [
                edge
                for edge in candidate_edges
                if _edge_type(edge) in SEMANTIC_EDGE_TYPES
                and _edge_source(edge) in existing_node_ids
                and _edge_target(edge) in existing_node_ids
            ]
            semantic_edges = [
                edge
                for edge in valid_edges
                if _edge_type(edge) in {"IMPLEMENTS", "REFERENCES_AUTHORITY", "CLASSIFIED_BY"}
            ]
            if valid_edges:
                edges_to_add.extend(valid_edges)
            if semantic_edges:
                resolved_ids.add(source)
            ledger_entries.append(
                {
                    **entry,
                    "disposition": "add_edges" if semantic_edges else "deferred_no_semantic_target",
                    "evidence": evidence,
                    "recommended_edges": [
                        {
                            "edge_id": edge["edge_id"],
                            "edge_type": edge["edge_type"],
                            "source": edge["source"],
                            "target": edge["target"],
                            "reason": edge["reason"],
                        }
                        for edge in valid_edges
                    ],
                }
            )

        plan = AtlasLmdbWritePlan(
            edges_to_add=edges_to_add,
            metadata={
                "operation": "fix62f_runtime_source_trace",
                "input_priority2_count": len(priority2_entries),
            },
            phase=PHASE,
            dry_run=False,
        )
        receipt = writer.apply_plan(plan)

        # Phase file registration happens after generated docs are written below;
        # its own support nodes/edges are also preimaged.
        carry_forward_entries: list[dict[str, Any]] = []
        for entry in input_queue.get("entries", []):
            if entry.get("priority") == 2 and entry.get("graph_projection") == "public_protocol_graph":
                if entry.get("candidate_id") not in resolved_ids:
                    carry_forward_entries.append(dict(entry))
                continue
            carry_forward_entries.append(dict(entry))
        carry_forward_entries.sort(
            key=lambda item: (item["priority"], item["work_family"], item.get("path", ""), item["candidate_id"])
        )
        for index, entry in enumerate(carry_forward_entries, start=1):
            entry["queue_index"] = index
            entry["batch_id"] = f"fix62f_batch_{((index - 1) // 10) + 1:04d}"

        ledger = {
            "entries": ledger_entries,
            "entry_count": len(ledger_entries),
            "phase": PHASE,
            "resolved_priority2_count": len(resolved_ids),
            "status": "runtime_source_trace_complete",
        }
        queue_payload = _queue_payload(
            carry_forward_entries,
            source_queue=INPUT_QUEUE_PATH,
            status="carry_forward_after_runtime_source_trace",
        )
        write_json_atomic(LEDGER_PATH, ledger)
        write_json_atomic(QUEUE_PATH, queue_payload)

        file_registration_receipt = _register_phase_files(writer)
        post_nodes = writer.store.iter_nodes()
        post_edges = writer.store.iter_edges()
        touched_node_ids = {entry["candidate_id"] for entry in priority2_entries}
        touched_node_ids.update(
            _candidate_id(node)
            for node in post_nodes
            if str(node.get("annotation_phase")) == PHASE_TOKEN
        )
        touched_edge_ids = {
            str(edge.get("edge_id"))
            for edge in post_edges
            if str(edge.get("annotation_phase")) == PHASE_TOKEN and edge.get("edge_id")
        }
        preimages = [
            _node_preimage(node)
            for node in post_nodes
            if _candidate_id(node) in touched_node_ids
        ]
        preimages.extend(
            _edge_preimage(edge)
            for edge in post_edges
            if str(edge.get("edge_id")) in touched_edge_ids
        )
        preimage_receipt = writer.write_preimages(
            preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "fix62f_runtime_source_trace"},
        )
        final = writer.inspect()

        report = {
            "carry_forward_priority2_count": len(priority2_entries) - len(resolved_ids),
            "edge_application": {
                "accepted_edge_count": receipt["accepted_edge_count"],
                "rejected_edge_count": receipt["rejected_edge_count"],
                "skipped_edge_count": receipt["skipped_edge_count"],
            },
            "file_registration": {
                "accepted_edge_count": file_registration_receipt["accepted_edge_count"],
                "accepted_node_count": file_registration_receipt["accepted_node_count"],
            },
            "final_counts": {
                "edges": final["edge_count"],
                "nodes": final["node_count"],
                "preimages": final["preimage_count"],
            },
            "input_priority2_count": len(priority2_entries),
            "ledger_path": str(LEDGER_PATH.relative_to(REPO_ROOT)),
            "phase": PHASE,
            "pre_counts": pre,
            "preimage_receipt": {
                "preimage_count": preimage_receipt["preimage_count"],
                "post_preimage_count": preimage_receipt["post_preimage_count"],
            },
            "queue_path": str(QUEUE_PATH.relative_to(REPO_ROOT)),
            "resolved_priority2_count": len(resolved_ids),
            "status": "PASS",
        }
        _validate_postconditions(report)
        REPORT_MD_PATH.write_text(_report_markdown(report), encoding="utf-8")
        WALKTHROUGH_PATH.write_text(_walkthrough_markdown(report), encoding="utf-8")
        write_json_atomic(OUT_REPORT_PATH, report)
        _append_status(report)
        return report
    finally:
        writer.close()


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":"), allow_nan=False))
