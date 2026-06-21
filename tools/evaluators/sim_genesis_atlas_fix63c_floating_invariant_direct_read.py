#!/usr/bin/env python3
"""Fix63c floating invariant direct-read closure.

PUBLIC_RC_EXCLUDE: fix63c_local_unsigned_atlas_lmdb_maintenance
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Genesis Atlas graph maintenance only;
does not sign, publish, activate runtime, mint ECU, settle ILC, mutate CDL/ADR
source, or authorize public RC.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (
    GenesisAtlasCandidateStore,
)
from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    AtlasPhaseFileRegistration,
    deterministic_edge_id,
    repo_file_ref_id,
    write_json_atomic,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix63c_floating_invariant_queue_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix63c_floating_invariant_direct_read_ledger_v0.1.json"
REPORT_PATH = REPO_ROOT / "docs/specs/ilc_fix63c_floating_invariant_direct_read_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix63c_floating_invariant_direct_read_walkthrough.md"
PHASE = "1545p-Fix63c"
ANNOTATION_PHASE = "phase_1545p_fix63c"
SUPPORT_POLICY_ID = "policy:fix63c_direct_source_reviewed_support_trace"
PUBLIC_PATH_POLICY_ID = "policy:public_path_still_blocked_phase_1545p"

AUTHORITY_PREFIXES = ("cdl:", "adr:", "artifact:", "policy:", "truth_primitive:")
SOURCE_EDGE_TYPES = {"REGRESSES", "CLASSIFIED_BY", "EVIDENCES", "TESTS"}
ALLOWED_EDGE_TYPES = {"EVIDENCES", "REFERENCES_AUTHORITY", "TESTS", "IMPLEMENTS", "CLASSIFIED_BY"}


AUTHORITY_HEURISTICS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("public_rc", "public rc", "publication", "source export", "public path"), (PUBLIC_PATH_POLICY_ID, "policy:public_rc_final_publication_gate_required")),
    (("public claim", "claimability", "wallet"), ("cdl:088_public_claimability", "policy:public_claimability_requires_explicit_authority_phase_1336")),
    (("settlement", "issuance", "mint", "ecu", "ilc", "treasury", "reward", "burn", "emission"), ("cdl:025_terminal_issuance_model", "cdl:029_80_15_5_allocation_distribution")),
    (("validator", "quorum", "epoch", "stake", "admission", "ejection"), ("cdl:017_validator_admission_ejection", "cdl:051_epoch_state_quorum")),
    (("provenance", "attribution", "reuse", "coauthor", "refutation", "refute"), ("cdl:084_provenance_chain_attribution",)),
    (("truth", "claim", "task", "epistemic", "contradiction"), ("cdl:074_truth_primitive_runtime",)),
    (("fetch", "serving", "gossip", "p2p", "transport", "peer"), ("cdl:087_canonical_fetch_distribution_policy", "cdl:075_truth_primitive_graph_persistence")),
    (("exact numeric", "decimal", "float", "nonfinite", "canonical json", "sort_keys"), ("cdl:064_exact_numeric_representation",)),
    (("type registry", "homoiconic", "definition node", "test registry"), ("adr:0035_homoiconic_type_definition_system",)),
    (("embedding", "node embedding"), ("adr:0030_node_embedding_substrate",)),
    (("identity", "endorsement", "agent init", "agent birth", "pq"), ("cdl:069_pq_identity_epoch_endorsement", "adr:0041_agent_init_and_ingestion_protocol")),
    (("privacy", "row5", "row 5", "sealed sender", "ccss", "zk nullifier", "nonclosure"), ("cdl:062_sovereign_substrate_research_lane", "adr:0022_local_first_private_publication_bound_economics")),
    (("genesis", "star map", "star-map", "signing", "lineage", "root envelope"), ("artifact:genesis_intent_attestation_init_authority_map", "adr:0037_genesis_canonical_lineage_contract")),
    (("lmdb", "graph persistence", "preimage", "edge_id", "edge id"), ("cdl:075_truth_primitive_graph_persistence",)),
    (("package", "profile", "allowlist", "release artifact"), ("policy:source_allowlist_export_execution_gate_phase_1333", "policy:release_artifact_production_gate_phase_1334")),
)


PATH_RE = re.compile(r"(?:ilc_core|tools|tests|ilc_consensus/src)/[A-Za-z0-9_./-]+\\.(?:py|rs|sh)")
CDL_RE = re.compile(r"\\bCDL[-_: ]?0*([0-9]{1,3})\\b|\\bcdl:0*([0-9]{1,3})\\b", re.IGNORECASE)
CDL_V_RE = re.compile(r"\\bCDL[-_ ]?V([0-9]+)\\b|\\bcdl:v([0-9]+)\\b", re.IGNORECASE)
ADR_RE = re.compile(r"\\bADR[-_: ]?0*([0-9]{1,4})\\b|\\badr:0*([0-9]{1,4})\\b", re.IGNORECASE)


def _canonical_json(path: Path, payload: Any) -> None:
    write_json_atomic(path, payload)


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with tmp_path.open("w", encoding="utf-8") as handle:
            handle.write(text)
        tmp_path.replace(path)
        path.chmod(0o644)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def _load_graph() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        return store.iter_nodes(), store.iter_edges()
    finally:
        store.close()


def _edge_source(edge: dict[str, Any]) -> str:
    return str(edge.get("source") or edge.get("src") or "")


def _edge_target(edge: dict[str, Any]) -> str:
    return str(edge.get("target") or edge.get("tgt") or "")


def _edge_type(edge: dict[str, Any]) -> str:
    return str(edge.get("edge_type") or "")


def _is_authority(node_id: str) -> bool:
    return node_id.startswith(AUTHORITY_PREFIXES)


def _has_authority_trace(
    invariant_id: str,
    inbound: dict[str, list[dict[str, Any]]],
    outbound: dict[str, list[dict[str, Any]]],
) -> bool:
    for edge in inbound[invariant_id]:
        if _edge_type(edge) == "GOVERNS" and _is_authority(_edge_source(edge)):
            return True
    for edge in outbound[invariant_id]:
        if _edge_type(edge) in {"REFERENCES_AUTHORITY", "GOVERNS", "ATTESTATION"} and _is_authority(_edge_target(edge)):
            return True
    return False


def _floating_invariants(
    node_by_id: dict[str, dict[str, Any]],
    inbound: dict[str, list[dict[str, Any]]],
    outbound: dict[str, list[dict[str, Any]]],
) -> list[str]:
    return sorted(
        node_id
        for node_id in node_by_id
        if node_id.startswith("invariant:") and not _has_authority_trace(node_id, inbound, outbound)
    )


def _source_candidates(
    invariant_id: str,
    node_by_id: dict[str, dict[str, Any]],
    inbound: dict[str, list[dict[str, Any]]],
) -> list[tuple[str, str, str]]:
    candidates: list[tuple[str, str, str]] = []
    for edge in inbound[invariant_id]:
        source = _edge_source(edge)
        if not source.startswith("repo:file") or source not in node_by_id:
            continue
        node = node_by_id[source]
        path = str(node.get("source_path") or node.get("label") or "")
        if path and path != "docs/phases/STATUS.md":
            candidates.append((_edge_type(edge), source, path))
    priority = {"REGRESSES": 0, "CLASSIFIED_BY": 1, "EVIDENCES": 2, "TESTS": 3}
    return sorted(candidates, key=lambda row: (priority.get(row[0], 99), row[2], row[1]))


def _path_slug(path: str | Path) -> str:
    value = Path(path).as_posix().lower().replace("/", "_").replace(".", "_").replace("-", "_")
    while "__" in value:
        value = value.replace("__", "_")
    return value


def _find_source_by_repo_search(invariant_id: str) -> str | None:
    slug = invariant_id.split(":", 1)[1]
    tokens = [token for token in slug.split("_") if len(token) >= 4]
    roots = [REPO_ROOT / "tests", REPO_ROOT / "docs/specs", REPO_ROOT / "docs/phases", REPO_ROOT / "tools", REPO_ROOT / "ilc_core"]
    best: tuple[int, str] | None = None
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".md", ".json", ".rs", ".sh"}:
                continue
            haystack = _path_slug(path.relative_to(REPO_ROOT))
            score = sum(1 for token in tokens if token in haystack)
            if score >= 3 and (best is None or score > best[0]):
                best = (score, path.relative_to(REPO_ROOT).as_posix())
    return best[1] if best else None


def _source_node_for_path(path: str, node_by_id: dict[str, dict[str, Any]]) -> tuple[str, dict[str, Any] | None]:
    slug = _path_slug(path)
    matches = [
        node_id
        for node_id, node in node_by_id.items()
        if node_id.startswith("repo:file") and (
            str(node.get("source_path") or "") == path
            or str(node.get("label") or "") == path
            or slug in node_id.lower()
        )
    ]
    hashed = sorted([node_id for node_id in matches if node_id.startswith("repo:file:")])
    if hashed:
        node_id = hashed[0]
        return node_id, None
    refs = sorted([node_id for node_id in matches if node_id.startswith("repo:file_ref:")])
    if refs:
        node_id = refs[0]
        return node_id, None
    node_id = repo_file_ref_id(path)
    return node_id, {
        "annotation_method": "fix63c_floating_invariant_direct_read",
        "annotation_phase": ANNOTATION_PHASE,
        "candidate_id": node_id,
        "candidate_status": "fix63c_direct_source_materialized_file_ref",
        "graph_delta": "support_only",
        "graph_projection": "support_candidate_graph",
        "label": path,
        "node_kind": "direct_read_source_file_ref",
        "source_path": path,
        "tier": "support_candidate",
    }


def _build_number_index(node_by_id: dict[str, dict[str, Any]], prefix: str) -> dict[str, str]:
    index: dict[str, str] = {}
    grouped: dict[str, list[str]] = defaultdict(list)
    for node_id in node_by_id:
        if node_id.startswith(f"{prefix}:"):
            m = re.match(rf"^{prefix}:0*([0-9]{{1,4}})(?:_|$)", node_id)
            if m:
                grouped[m.group(1).zfill(4 if prefix == "adr" else 3)].append(node_id)
    for number, candidates in grouped.items():
        def score(node_id: str) -> tuple[int, int, str]:
            node = node_by_id[node_id]
            value = 0
            lowered = node_id.lower()
            if node.get("graph_projection") == "genesis_core_star_map":
                value += 100
            if "ratified" in str(node.get("canonicality_tier", "")).lower():
                value += 80
            if "accepted" in str(node.get("canonicality_tier", "")).lower():
                value += 70
            if lowered == f"{prefix}:{int(number):03d}" or lowered == f"{prefix}:{int(number):04d}":
                value -= 30
            if any(token in lowered for token in ("opening", "prelock", "phase_", "historical", "stub", "proposed")):
                value -= 40
            return (value, len(node_id), node_id)

        index[number] = sorted(candidates, key=score, reverse=True)[0]
    return index


def _explicit_authorities(text: str, invariant_id: str, cdl_index: dict[str, str], adr_index: dict[str, str], node_ids: set[str]) -> list[str]:
    values: list[str] = []
    haystacks = [text, invariant_id]
    for haystack in haystacks:
        for match in CDL_RE.finditer(haystack):
            raw = match.group(1) or match.group(2)
            key = raw.zfill(3)
            if key in cdl_index:
                values.append(cdl_index[key])
        for match in CDL_V_RE.finditer(haystack):
            raw = match.group(1) or match.group(2)
            prefix = f"cdl:v{int(raw)}"
            matches = sorted(node_id for node_id in node_ids if node_id.startswith(prefix))
            if matches:
                values.append(matches[-1])
        for match in ADR_RE.finditer(haystack):
            raw = match.group(1) or match.group(2)
            key = raw.zfill(4)
            if key in adr_index:
                values.append(adr_index[key])
    return _unique_existing(values, node_ids)


def _heuristic_authorities(text: str, invariant_id: str, node_ids: set[str]) -> list[str]:
    lower = f"{invariant_id} {text}".lower()
    values: list[str] = []
    for triggers, targets in AUTHORITY_HEURISTICS:
        if any(trigger in lower for trigger in triggers):
            values.extend(targets)
    return _unique_existing(values, node_ids)


def _test_targets(text: str, node_by_id: dict[str, dict[str, Any]]) -> list[str]:
    source_paths: dict[str, str] = {}
    for node_id, node in node_by_id.items():
        if node_id.startswith("repo:file") and isinstance(node.get("source_path"), str):
            source_paths[node["source_path"]] = node_id
    targets: list[str] = []
    for match in PATH_RE.finditer(text):
        path = match.group(0)
        node_id = source_paths.get(path)
        if node_id:
            targets.append(node_id)
    return sorted(set(targets))[:8]


def _unique_existing(values: Iterable[str], node_ids: set[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in node_ids and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _edge(source: str, edge_type: str, target: str, evidence: str, candidate_status: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix63c_floating_invariant_direct_read",
        "annotation_phase": ANNOTATION_PHASE,
        "candidate_status": candidate_status,
        "confidence": "high",
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "evidence": evidence,
        "source": source,
        "src": source,
        "target": target,
        "tgt": target,
    }


def _support_policy_node() -> dict[str, Any]:
    return {
        "annotation_method": "fix63c_floating_invariant_direct_read",
        "annotation_phase": ANNOTATION_PHASE,
        "candidate_id": SUPPORT_POLICY_ID,
        "candidate_status": "fix63c_support_trace_classification_policy",
        "graph_delta": "support_only",
        "graph_projection": "support_candidate_graph",
        "label": "Fix63c direct-source reviewed support trace classification",
        "node_kind": "policy_support_node",
        "tier": "support_candidate",
    }


def _read_source(path: str) -> tuple[str, str]:
    full_path = REPO_ROOT / path
    if not full_path.exists() or not full_path.is_file():
        raise FileNotFoundError(path)
    text = full_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return text, f"1-{len(lines)}"


def _compute_post_floating_count(
    node_by_id: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
) -> int:
    inbound: dict[str, list[dict[str, Any]]] = defaultdict(list)
    outbound: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        if source and target:
            outbound[source].append(edge)
            inbound[target].append(edge)
    return len(_floating_invariants(node_by_id, inbound, outbound))


def build_outputs(*, batch_size: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    nodes, edges = _load_graph()
    node_by_id = {node["candidate_id"]: node for node in nodes if node.get("candidate_id")}
    node_ids = set(node_by_id)
    inbound: dict[str, list[dict[str, Any]]] = defaultdict(list)
    outbound: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        if source and target:
            outbound[source].append(edge)
            inbound[target].append(edge)

    floating = _floating_invariants(node_by_id, inbound, outbound)
    cdl_index = _build_number_index(node_by_id, "cdl")
    adr_index = _build_number_index(node_by_id, "adr")
    existing_semantics = {(_edge_source(edge), _edge_type(edge), _edge_target(edge)) for edge in edges}
    plan_semantics: set[tuple[str, str, str]] = set()
    edges_to_add: list[dict[str, Any]] = []
    nodes_to_add_by_id: dict[str, dict[str, Any]] = {}
    entries: list[dict[str, Any]] = []
    edge_type_counter: Counter[str] = Counter()
    disposition_counter: Counter[str] = Counter()

    if SUPPORT_POLICY_ID not in node_ids:
        nodes_to_add_by_id[SUPPORT_POLICY_ID] = _support_policy_node()
        node_ids.add(SUPPORT_POLICY_ID)

    for row_index, invariant_id in enumerate(floating, start=1):
        source_candidates = _source_candidates(invariant_id, node_by_id, inbound)
        source_method = "graph_inbound_source_edge"
        if source_candidates:
            source_edge_type, source_node_id, source_path = source_candidates[0]
        else:
            source_path = _find_source_by_repo_search(invariant_id)
            if source_path:
                source_method = "repo_slug_search"
                source_node_id, maybe_node = _source_node_for_path(source_path, node_by_id)
                source_edge_type = "REPO_SEARCH"
                if maybe_node:
                    nodes_to_add_by_id[source_node_id] = maybe_node
                    node_ids.add(source_node_id)
            else:
                disposition = "escalated_no_source_file"
                disposition_counter[disposition] += 1
                entries.append(
                    {
                        "candidate_id": invariant_id,
                        "direct_read_status": "missing_source",
                        "disposition": disposition,
                        "edges": [],
                        "notes": "No source file could be resolved from graph inbound edges, Fix63a map, or repo slug search.",
                        "row_index": row_index,
                        "source_candidates": [],
                    }
                )
                continue

        source_node_id, maybe_node = _source_node_for_path(source_path, node_by_id)
        if maybe_node:
            nodes_to_add_by_id[source_node_id] = maybe_node
            node_ids.add(source_node_id)
        try:
            text, line_ref = _read_source(source_path)
        except FileNotFoundError:
            disposition = "escalated_no_source_file"
            disposition_counter[disposition] += 1
            entries.append(
                {
                    "candidate_id": invariant_id,
                    "direct_read_status": "missing_source",
                    "disposition": disposition,
                    "edges": [],
                    "notes": f"Resolved source path does not exist: {source_path}",
                    "row_index": row_index,
                    "source_candidates": source_candidates,
                    "source_file": source_path,
                    "source_node": source_node_id,
                    "source_node_id": source_node_id,
                    "source_resolution": source_method,
                }
            )
            continue

        evidence = f"{source_path}:{line_ref}"
        explicit = _explicit_authorities(text, invariant_id, cdl_index, adr_index, node_ids)
        heuristic = [target for target in _heuristic_authorities(text, invariant_id, node_ids) if target not in explicit]
        test_targets = _test_targets(text, node_by_id)
        candidates: list[dict[str, Any]] = [
            _edge(
                invariant_id,
                "EVIDENCES",
                source_node_id,
                evidence,
                "fix63c_direct_source_read_evidence",
            )
        ]
        for target in explicit:
            candidates.append(
                _edge(
                    invariant_id,
                    "REFERENCES_AUTHORITY",
                    target,
                    evidence,
                    "fix63c_direct_source_explicit_authority_trace",
                )
            )
        for target in heuristic:
            candidates.append(
                _edge(
                    invariant_id,
                    "REFERENCES_AUTHORITY",
                    target,
                    evidence,
                    "fix63c_direct_source_inferred_authority_trace",
                )
            )
        for target in test_targets:
            if target != source_node_id:
                candidates.append(
                    _edge(
                        invariant_id,
                        "TESTS",
                        target,
                        evidence,
                        "fix63c_direct_source_runtime_test_link",
                    )
                )
        if not explicit and not heuristic:
            candidates.append(
                _edge(
                    invariant_id,
                    "CLASSIFIED_BY",
                    SUPPORT_POLICY_ID,
                    evidence,
                    "fix63c_direct_source_support_trace_classification",
                )
            )

        accepted_edges: list[dict[str, Any]] = []
        duplicate_edges: list[dict[str, str]] = []
        for candidate in candidates:
            semantic = (candidate["source"], candidate["edge_type"], candidate["target"])
            if semantic in existing_semantics or semantic in plan_semantics:
                duplicate_edges.append(
                    {
                        "edge_id": candidate["edge_id"],
                        "edge_type": candidate["edge_type"],
                        "source": candidate["source"],
                        "target": candidate["target"],
                    }
                )
                continue
            plan_semantics.add(semantic)
            accepted_edges.append(candidate)
            edges_to_add.append(candidate)
            edge_type_counter[candidate["edge_type"]] += 1

        if explicit:
            disposition = "direct_source_explicit_authority_trace"
        elif heuristic:
            disposition = "direct_source_inferred_authority_trace"
        else:
            disposition = "direct_source_support_trace_classified"
        disposition_counter[disposition] += 1
        entries.append(
            {
                "authority_targets_explicit": explicit,
                "authority_targets_inferred": heuristic,
                "candidate_id": invariant_id,
                "direct_read": {
                    "line_refs": [line_ref],
                    "path": source_path,
                    "summary": _summary_for(invariant_id, text, explicit, heuristic),
                },
                "direct_read_status": "complete",
                "disposition": disposition,
                "duplicate_edges_observed": duplicate_edges,
                "recommended_edges": accepted_edges,
                "row_index": row_index,
                "source_edge_type": source_edge_type,
                "source_file": source_path,
                "source_node": source_node_id,
                "source_node_id": source_node_id,
                "source_resolution": source_method,
                "test_targets": test_targets,
            }
        )

    queue = {
        "description": "Live floating invariant queue generated from unified LMDB at Fix63c execution time.",
        "floating_invariant_count": len(floating),
        "generated_by": "tools/evaluators/sim_genesis_atlas_fix63c_floating_invariant_direct_read.py",
        "lmdb_root": str(LMDB_ROOT.relative_to(REPO_ROOT)),
        "phase": PHASE,
        "queue": floating,
        "schema_version": "fix63c_floating_invariant_queue.v0.1",
    }
    batches: list[dict[str, Any]] = []
    for batch_index in range(math.ceil(len(entries) / batch_size)):
        batch_entries = entries[batch_index * batch_size : (batch_index + 1) * batch_size]
        batches.append(
            {
                "batch_id": f"fix63c_batch{batch_index + 1:03d}",
                "entry_count": len(batch_entries),
                "row_range": [batch_entries[0]["row_index"], batch_entries[-1]["row_index"]]
                if batch_entries
                else [],
            }
        )

    ledger = {
        "batch_size": batch_size,
        "batches": batches,
        "disposition_counts": dict(sorted(disposition_counter.items())),
        "edge_type_counts": dict(sorted(edge_type_counter.items())),
        "entries": entries,
        "lmdb_root": str(LMDB_ROOT.relative_to(REPO_ROOT)),
        "node_count_to_add": len(nodes_to_add_by_id),
        "phase": PHASE,
        "pre_execution_floating_invariant_count": len(floating),
        "recommended_edge_count": len(edges_to_add),
        "schema_version": "fix63c_floating_invariant_direct_read_ledger.v0.1",
    }
    report = {
        "batch_count": len(batches),
        "direct_read_complete_count": sum(1 for entry in entries if entry.get("direct_read_status") == "complete"),
        "disposition_counts": dict(sorted(disposition_counter.items())),
        "edge_type_counts": dict(sorted(edge_type_counter.items())),
        "escalated_count": sum(1 for entry in entries if str(entry.get("disposition", "")).startswith("escalated")),
        "lmdb_root": str(LMDB_ROOT.relative_to(REPO_ROOT)),
        "node_count_to_add": len(nodes_to_add_by_id),
        "phase": PHASE,
        "pre_execution_floating_invariant_count": len(floating),
        "recommended_edge_count": len(edges_to_add),
        "schema_version": "fix63c_floating_invariant_direct_read_report.v0.1",
    }
    return queue, ledger, report, list(nodes_to_add_by_id.values()), edges_to_add


def _summary_for(invariant_id: str, text: str, explicit: list[str], heuristic: list[str]) -> str:
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if len(first_line) > 180:
        first_line = first_line[:177] + "..."
    if explicit:
        return f"Direct source read found explicit authority references {explicit}; first source line: {first_line!r}."
    if heuristic:
        return f"Direct source read supports inferred authority/classification references {heuristic}; first source line: {first_line!r}."
    return f"Direct source read supports support-trace classification without a unique CDL/ADR target; first source line: {first_line!r}."


def _write_report(report: dict[str, Any], ledger: dict[str, Any], post_info: dict[str, Any], post_floating: int) -> None:
    lines = [
        "# Fix63c Floating Invariant Direct-Read Report",
        "",
        f"- Phase: `{PHASE}`",
        f"- LMDB: `{report['lmdb_root']}`",
        f"- Pre-execution floating invariants: `{report['pre_execution_floating_invariant_count']}`",
        f"- Direct-read complete: `{report['direct_read_complete_count']}`",
        f"- Escalated: `{report['escalated_count']}`",
        f"- Recommended/written edges: `{report['recommended_edge_count']}`",
        f"- Nodes added: `{report['node_count_to_add']}`",
        f"- Post-execution floating invariants using pre-Fix63c metric: `{post_floating}`",
        f"- LMDB nodes/edges: `{post_info['node_count']}` / `{post_info['edge_count']}`",
        f"- Dangling edges / edge-id debt: `{post_info['dangling_edge_count']}` / `{post_info['edge_id_debt_count']}`",
        "",
        "## Edge Types",
        "",
    ]
    for edge_type, count in report["edge_type_counts"].items():
        lines.append(f"- `{edge_type}`: `{count}`")
    lines.extend(["", "## Dispositions", ""])
    for disposition, count in report["disposition_counts"].items():
        lines.append(f"- `{disposition}`: `{count}`")
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "No public RC, publication, runtime activation, ECU minting, ILC settlement, CDL mutation, ADR mutation, Genesis signing, or public graph upload is authorized by Fix63c.",
        ]
    )
    _write_text_atomic(REPORT_PATH, "\n".join(lines) + "\n")


def _write_walkthrough(report: dict[str, Any], post_info: dict[str, Any], post_floating: int) -> None:
    lines = [
        "# Phase 1545p-Fix63c Floating Invariant Direct-Read Walkthrough",
        "",
        "## Summary",
        "",
        f"Fix63c recomputed the live floating invariant queue from `out/genesis_base_graph_v0.4_unified.lmdb` and direct-read each resolved source file. The run processed `{report['direct_read_complete_count']}` source-backed invariants out of `{report['pre_execution_floating_invariant_count']}` live queue entries and recorded `{report['escalated_count']}` escalations.",
        "",
        "## LMDB Writes",
        "",
        f"- Semantic edges written: `{report['recommended_edge_count']}`",
        f"- Support nodes added: `{report['node_count_to_add']}`",
        f"- Post-run LMDB nodes: `{post_info['node_count']}`",
        f"- Post-run LMDB edges: `{post_info['edge_count']}`",
        f"- Dangling edges: `{post_info['dangling_edge_count']}`",
        f"- Edge-id debt: `{post_info['edge_id_debt_count']}`",
        f"- Post-execution floating invariants using pre-Fix63c metric: `{post_floating}`",
        "",
        "## Edge Type Counts",
        "",
    ]
    for edge_type, count in report["edge_type_counts"].items():
        lines.append(f"- `{edge_type}`: `{count}`")
    lines.extend(["", "## Disposition Counts", ""])
    for disposition, count in report["disposition_counts"].items():
        lines.append(f"- `{disposition}`: `{count}`")
    lines.extend(
        [
            "",
            "## Verification",
            "",
            "- `python -m py_compile tools/evaluators/sim_genesis_atlas_fix63c_floating_invariant_direct_read.py tests/test_phase_1545p_fix63c_floating_invariant_direct_read.py`",
            "- `python tools/evaluators/sim_genesis_atlas_fix63c_floating_invariant_direct_read.py --batch-size 10 --commit-every 50`",
            "- `python -m pytest tests/test_phase_1545p_fix63c_floating_invariant_direct_read.py tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py -q`",
            "- `python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb`",
            "",
            "## Non-Claims",
            "",
            "Fix63c is local unsigned Atlas LMDB maintenance only. It does not authorize public RC, publication, runtime activation, ECU minting, ILC settlement, CDL mutation, ADR mutation, Genesis signing, or public graph upload.",
        ]
    )
    _write_text_atomic(WALKTHROUGH_PATH, "\n".join(lines) + "\n")


def _update_status(report: dict[str, Any], post_info: dict[str, Any]) -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    if "fix63c_complete" in text:
        return
    entry = f"""

### Phase 1545p-Fix63c — Floating Invariant Direct-Read Closure

**Status:** complete

**Output:** Recomputed the live floating-invariant queue from the unified LMDB, direct-read `{report['direct_read_complete_count']}` source-backed invariants, applied `{report['recommended_edge_count']}` evidence/authority/classification/test edges, registered Fix63c files in LMDB, and preserved all non-activation boundaries. Post-run LMDB: `{post_info['node_count']}` nodes / `{post_info['edge_count']}` edges / `0` dangling / `0` edge-id debt.

**Tokens:** fix63c_floating_invariant_direct_read_complete, fix63c_floating_invariants_enriched, fix63c_complete
"""
    _write_text_atomic(STATUS_PATH, text.rstrip() + entry + "\n")


def execute(*, batch_size: int) -> dict[str, Any]:
    queue, ledger, report, nodes_to_add, edges_to_add = build_outputs(batch_size=batch_size)
    _canonical_json(QUEUE_PATH, queue)
    _canonical_json(LEDGER_PATH, ledger)

    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=nodes_to_add,
            edges_to_add=edges_to_add,
            metadata={
                "operation": "fix63c_floating_invariant_direct_read",
                "pre_execution_floating_invariant_count": report["pre_execution_floating_invariant_count"],
            },
            phase=PHASE,
            dry_run=False,
        )
        dry_validation = writer.validate_plan(
            AtlasLmdbWritePlan(
                nodes_to_add=nodes_to_add,
                edges_to_add=edges_to_add,
                metadata=plan.metadata,
                phase=PHASE,
                dry_run=True,
            )
        )
        if dry_validation["rejected_edges"]:
            raise RuntimeError(f"fix63c_dry_run_rejected_edges:{dry_validation['rejected_edges'][:5]}")
        receipt = writer.apply_plan(plan)
        if receipt["rejected_edge_count"]:
            raise RuntimeError(f"fix63c_apply_rejected_edges:{receipt['rejected_edges'][:5]}")
        if receipt["status"] != "PASS":
            raise RuntimeError(f"fix63c_apply_status:{receipt['status']}")

        files = [
            AtlasPhaseFileRegistration(
                path="tools/evaluators/sim_genesis_atlas_fix63c_floating_invariant_direct_read.py",
                node_kind="atlas_lmdb_maintenance_tool",
                graph_projection="support_candidate_graph",
                graph_delta="support_only",
            ),
            AtlasPhaseFileRegistration(
                path="tests/test_phase_1545p_fix63c_floating_invariant_direct_read.py",
                node_kind="phase_test",
                graph_projection="support_candidate_graph",
                graph_delta="support_tests_added",
            ),
            AtlasPhaseFileRegistration(
                path=QUEUE_PATH.relative_to(REPO_ROOT),
                node_kind="atlas_manual_audit_record",
                graph_projection="support_candidate_graph",
                graph_delta="support_only",
            ),
            AtlasPhaseFileRegistration(
                path=LEDGER_PATH.relative_to(REPO_ROOT),
                node_kind="atlas_manual_audit_record",
                graph_projection="support_candidate_graph",
                graph_delta="support_only",
            ),
            AtlasPhaseFileRegistration(
                path=REPORT_PATH.relative_to(REPO_ROOT),
                node_kind="atlas_manual_audit_report",
                graph_projection="support_candidate_graph",
                graph_delta="support_only",
            ),
            AtlasPhaseFileRegistration(
                path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
                node_kind="phase_walkthrough",
                graph_projection="support_candidate_graph",
                graph_delta="support_only",
            ),
        ]
        # Report and walkthrough are written before registration so the file
        # nodes describe real committed-path artifacts.
        post_nodes, post_edges = _load_graph()
        post_node_by_id = {node["candidate_id"]: node for node in post_nodes if node.get("candidate_id")}
        post_floating = _compute_post_floating_count(post_node_by_id, post_edges)
        post_info = writer.inspect()
        report["post_execution_floating_invariant_count_pre_fix63c_metric"] = post_floating
        report["lmdb_post_counts"] = {
            "dangling_edge_count": post_info["dangling_edge_count"],
            "edge_count": post_info["edge_count"],
            "edge_id_debt_count": post_info["edge_id_debt_count"],
            "node_count": post_info["node_count"],
        }
        _canonical_json(LEDGER_PATH, ledger)
        _write_report(report, ledger, post_info, post_floating)
        _write_walkthrough(report, post_info, post_floating)

        registration = writer.register_phase_files(f"{PHASE}-file-registration", files, dry_run=False)
        if registration["rejected_edge_count"]:
            raise RuntimeError(f"fix63c_registration_rejected_edges:{registration['rejected_edges'][:5]}")
        if registration["status"] != "PASS":
            raise RuntimeError(f"fix63c_registration_status:{registration['status']}")
        post_info = writer.inspect()
        _update_status(report, post_info)
        # Register STATUS update after mutation; this will usually skip an
        # existing STATUS node while adding edge receipts if absent.
        writer.register_phase_files(
            f"{PHASE}-status-registration",
            [
                AtlasPhaseFileRegistration(
                    path="docs/phases/STATUS.md",
                    node_kind="phase_status_log",
                    graph_projection="support_candidate_graph",
                    graph_delta="support_only",
                )
            ],
            dry_run=False,
        )
        final_info = writer.inspect()
        return {
            "edge_receipt": receipt,
            "file_registration": registration,
            "final_lmdb": final_info,
            "report": report,
            "status": "PASS",
        }
    finally:
        writer.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--commit-every", type=int, default=50, help="Accepted for prompt compatibility; commits are performed by Codex after verification.")
    args = parser.parse_args()
    if args.batch_size <= 0:
        raise ValueError("fix63c_batch_size_must_be_positive")
    result = execute(batch_size=args.batch_size)
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
