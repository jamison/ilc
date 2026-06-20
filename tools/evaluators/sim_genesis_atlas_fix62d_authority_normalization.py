#!/usr/bin/env python3
"""Normalize accepted ADR / ratified CDL authority targets in the Atlas LMDB.

PUBLIC_RC_EXCLUDE: fix62d_authority_normalization_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Genesis Atlas LMDB maintenance pass;
not Genesis signing, public graph upload, canonical graph mutation, runtime
activation, public serving, ECU minting, or public RC publication.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict, deque
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
import tools.evaluators.sim_genesis_atlas_fix62b_priority0_authority_trace as fix62b  # noqa: E402


PHASE = "1545p-Fix62d"
PHASE_TOKEN = "phase_1545p_fix62d"
ROOT = "artifact:genesis_intent_attestation_init_authority_map"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
CDL_REGISTER_PATH = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
ADR_DIR = REPO_ROOT / "docs/adr"
INPUT_QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62c_manual_graph_finish_queue_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62d_authority_normalization_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62d_manual_graph_finish_queue_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62d_authority_normalization_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62d_authority_normalization_walkthrough.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62d_authority_normalization_v0.1.json"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix62d_authority_normalization.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix62d_authority_normalization.py"

INPUT_TOKENS = ("fix62c_complete",)
OUTPUT_TOKENS = (
    "fix62d_authority_normalization_complete",
    "fix62d_accepted_adr_ratified_cdl_targets_rooted",
    "fix62d_priority1_token_refs_applied",
    "fix62d_complete",
)

AUTH_FORWARD_EDGE_TYPES = frozenset({"GOVERNS", "ATTESTATION"})
TYPED_TRACE_EDGE_TYPES = frozenset(
    {
        "GOVERNS",
        "ATTESTATION",
        "SAME_AUTHORITY",
        "DERIVED_FROM",
        "REFERENCES_AUTHORITY",
        "EVIDENCES",
        "CLASSIFIED_BY",
        "CARRIES_FORWARD",
        "PROVENANCE",
        "SUPERSEDED_BY",
    }
)
STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "any",
        "architecture",
        "authority",
        "boundary",
        "contract",
        "for",
        "framework",
        "from",
        "governance",
        "into",
        "lane",
        "later",
        "only",
        "policy",
        "protocol",
        "runtime",
        "the",
        "under",
        "with",
    }
)


def _verify_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix62d_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix62d_output_token_already_present:{token}")
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError(f"fix62d_lmdb_missing:{LMDB_ROOT}")


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _slug(value: str, *, limit: int = 8) -> str:
    words = [
        word
        for word in re.findall(r"[a-z0-9]+", value.lower())
        if word not in STOP_WORDS
    ]
    return "_".join(words[:limit]) or "authority"


def _edge_payload(
    source: str,
    edge_type: str,
    target: str,
    *,
    candidate_status: str,
    evidence: str,
    method: str,
) -> dict[str, Any]:
    return {
        "annotation_method": method,
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": candidate_status,
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "evidence": evidence,
        "source": source,
        "target": target,
    }


def _node_preimage(node: dict[str, Any]) -> dict[str, Any]:
    node_id = fix62b._candidate_id(node)
    if not node_id:
        raise ValueError("fix62d_node_preimage_candidate_id_missing")
    fields = {
        "authority_normalization_phase": node.get("authority_normalization_phase"),
        "authority_status": node.get("authority_status"),
        "candidate_id": node_id,
        "canonicality_tier": node.get("canonicality_tier"),
        "creator_agent_id": node.get("creator_agent_id"),
        "graph_projection": node.get("graph_projection"),
        "node_kind": node.get("node_kind"),
        "phase": PHASE,
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": "v0.4.fix62d_authority_normalization",
    }


def _edge_preimage(edge: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "edge_id": edge.get("edge_id")
        or deterministic_edge_id(
            fix62b._edge_source(edge),
            fix62b._edge_type(edge),
            fix62b._edge_target(edge),
        ),
        "edge_type": fix62b._edge_type(edge),
        "phase": PHASE,
        "source": fix62b._edge_source(edge),
        "target": fix62b._edge_target(edge),
    }
    edge_id = fields["edge_id"]
    if not isinstance(edge_id, str) or not edge_id:
        raise ValueError("fix62d_edge_preimage_edge_id_missing")
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "edge_id": edge_id,
        "fields": fields,
        "preimage_version": "v0.4.fix62d_authority_normalization",
    }


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix62d_json_not_object:{path}")
    return payload


def _parse_cdl_register() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(CDL_REGISTER_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.startswith("| CDL-") or "| ratified |" not in line:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 4 or parts[3].lower() != "ratified":
            continue
        decision_id = parts[0].replace("CDL-", "")
        rows.append(
            {
                "decision_id": decision_id,
                "evidence": f"{CDL_REGISTER_PATH.relative_to(REPO_ROOT)}:{line_number}",
                "related_clause": parts[1],
                "source_line": line_number,
                "topic": parts[2],
            }
        )
    return rows


def _parse_accepted_adrs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(ADR_DIR.glob("ADR_*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        status = re.search(r"\*\*Status:\*\*\s*([^\n]+)", text)
        if not status or not status.group(1).strip().lower().startswith("accepted"):
            continue
        filename = re.match(r"ADR_([0-9]{4})_(.*)\.md", path.name)
        if not filename:
            continue
        title = filename.group(2).replace("_", " ")
        h1 = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        rows.append(
            {
                "decision_id": filename.group(1),
                "evidence": str(path.relative_to(REPO_ROOT)),
                "status": status.group(1).strip(),
                "title": h1.group(1).strip() if h1 else title,
                "topic": title,
            }
        )
    return rows


def _candidate_number(node_id: str, prefix: str) -> int | str | None:
    if prefix == "cdl":
        match = re.match(r"cdl:(?:v([0-9]+)|0*([0-9]{1,4})(?:\b|_|$))", node_id, re.IGNORECASE)
        if not match:
            return None
        if match.group(1):
            return f"v{int(match.group(1))}"
        return int(match.group(2))
    match = re.match(r"adr:(?:ADR_)?0*([0-9]{1,4})(?:\b|_|$)", node_id, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _candidate_score(node_id: str, topic: str, direct_rooted: bool) -> float:
    node_lc = node_id.lower()
    score = 100.0 if direct_rooted else 0.0
    tokens = set(re.findall(r"[a-z0-9]+", topic.lower())) - STOP_WORDS
    for token in tokens:
        if len(token) > 2 and token in node_lc:
            score += 3.0
    if re.match(r"^(cdl|adr):0*[0-9]+$", node_lc):
        score -= 8.0
    for bad in ("opening", "prelock", "ratification_phase", "historical", "draft"):
        if bad in node_lc:
            score -= 20.0
    for good in (
        "architecture",
        "attribution",
        "bundle",
        "contract",
        "finality",
        "governance",
        "identity",
        "lineage",
        "policy",
        "schema",
        "transport",
    ):
        if good in node_lc:
            score += 1.0
    score += min(len(node_lc), 80) / 100.0
    return score


def _new_cdl_id(decision_id: str, topic: str) -> str:
    if decision_id.startswith("V"):
        return f"cdl:{decision_id.lower()}_{_slug(topic)}"
    return f"cdl:{int(decision_id):03d}_{_slug(topic)}"


def _new_adr_id(decision_id: str, topic: str) -> str:
    return f"adr:{int(decision_id):04d}_{_slug(topic)}"


def _choose_canonical(
    *,
    prefix: str,
    decision_id: str,
    topic: str,
    nodes: dict[str, dict[str, Any]],
    directly_rooted: set[str],
) -> tuple[str, str, float, list[str]]:
    number: int | str = f"v{int(decision_id[1:])}" if decision_id.startswith("V") else int(decision_id)
    candidates = [
        node_id
        for node_id in nodes
        if _candidate_number(node_id, prefix) == number
    ]
    if not candidates:
        return (
            _new_cdl_id(decision_id, topic) if prefix == "cdl" else _new_adr_id(decision_id, topic),
            "create_missing_authority_node",
            0.0,
            [],
        )
    ranked = sorted(
        (
            (
                _candidate_score(candidate, topic, candidate in directly_rooted),
                candidate,
            )
            for candidate in candidates
        ),
        reverse=True,
    )
    best_score, best_id = ranked[0]
    # Accepted ADR files are direct evidence; use the best existing ADR node when
    # present. For CDLs, create a clean canonical node when only weak/generic
    # aliases exist and no current root authority edge selected the node.
    if prefix == "adr" or best_score >= 5.0 or best_id in directly_rooted:
        return best_id, "normalize_existing_authority_node", best_score, candidates
    return _new_cdl_id(decision_id, topic), "create_low_confidence_canonical_cdl_node", best_score, candidates


def _authority_patch(kind: str, row: dict[str, Any], node_id: str) -> dict[str, Any]:
    if kind == "cdl":
        decision_id = row["decision_id"]
        return {
            "authority_evidence_ref": row["evidence"],
            "authority_normalization_phase": PHASE_TOKEN,
            "authority_status": f"ratified_CDL_{decision_id}",
            "canonicality_tier": "ratified_cdl",
            "genesis_attested": True,
            "genesis_attested_by": "genesis_agent:01",
            "graph_projection": "genesis_core_star_map",
            "inclusion_status": "must_include",
            "label": f"CDL-{decision_id} {row['topic']}",
            "node_kind": "cdl_artifact",
            "promotion_status": "canonical_authority_normalized_fix62d",
            "sensitivity": "NON-SENSITIVE",
            "tier": "genesis_core",
        }
    decision_id = row["decision_id"]
    return {
        "authority_evidence_ref": row["evidence"],
        "authority_normalization_phase": PHASE_TOKEN,
        "authority_status": f"accepted_ADR_{decision_id}",
        "canonicality_tier": "accepted_adr",
        "genesis_attested": True,
        "genesis_attested_by": "genesis_agent:01",
        "graph_projection": "genesis_core_star_map",
        "inclusion_status": "must_include",
        "label": row["title"],
        "node_kind": "adr_artifact",
        "promotion_status": "canonical_authority_normalized_fix62d",
        "sensitivity": "NON-SENSITIVE",
        "tier": "genesis_core",
    }


def _new_authority_node(node_id: str, kind: str, row: dict[str, Any]) -> dict[str, Any]:
    node = {
        "annotation_method": "fix62d_authority_normalization",
        "annotation_phase": PHASE_TOKEN,
        "candidate_id": node_id,
        "creator_agent_id": "genesis_agent:01",
        "creator_attribution_basis": "genesis_canonical_authority_register",
        "creator_attribution_phase": PHASE_TOKEN,
        "creator_attribution_scope": "accepted_adr_or_ratified_cdl_authority_node",
        "creator_attribution_status": "resolved_by_fix62d_authority_normalization",
        "graph_delta": "authority_normalization_node_materialized",
    }
    node.update(_authority_patch(kind, row, node_id))
    return node


def _directly_rooted(edges: list[dict[str, Any]]) -> set[str]:
    return {
        fix62b._edge_target(edge)
        for edge in edges
        if fix62b._edge_source(edge) == ROOT
        and fix62b._edge_type(edge) in AUTH_FORWARD_EDGE_TYPES
    }


def _build_authority_plan(
    nodes: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
) -> tuple[
    dict[tuple[str, int | str], str],
    dict[str, dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    direct_rooted = _directly_rooted(edges)
    canonical_map: dict[tuple[str, int | str], str] = {}
    updates: dict[str, dict[str, Any]] = {}
    nodes_to_add: list[dict[str, Any]] = []
    selections: list[dict[str, Any]] = []

    for row in _parse_cdl_register():
        decision_id = row["decision_id"]
        key: tuple[str, int | str] = (
            "cdl",
            f"v{int(decision_id[1:])}" if decision_id.startswith("V") else int(decision_id),
        )
        node_id, disposition, score, candidates = _choose_canonical(
            prefix="cdl",
            decision_id=decision_id,
            topic=row["topic"],
            nodes=nodes,
            directly_rooted=direct_rooted,
        )
        canonical_map[key] = node_id
        patch = _authority_patch("cdl", row, node_id)
        if node_id in nodes:
            updates[node_id] = patch
        else:
            nodes_to_add.append(_new_authority_node(node_id, "cdl", row))
        selections.append(
            {
                "canonical_node_id": node_id,
                "candidates": sorted(candidates),
                "decision_id": f"CDL-{decision_id}",
                "disposition": disposition,
                "evidence": row["evidence"],
                "kind": "cdl",
                "score": score,
                "topic": row["topic"],
            }
        )

    for row in _parse_accepted_adrs():
        decision_id = row["decision_id"]
        key = ("adr", int(decision_id))
        node_id, disposition, score, candidates = _choose_canonical(
            prefix="adr",
            decision_id=decision_id,
            topic=row["topic"],
            nodes=nodes,
            directly_rooted=direct_rooted,
        )
        canonical_map[key] = node_id
        patch = _authority_patch("adr", row, node_id)
        if node_id in nodes:
            updates[node_id] = patch
        else:
            nodes_to_add.append(_new_authority_node(node_id, "adr", row))
        selections.append(
            {
                "canonical_node_id": node_id,
                "candidates": sorted(candidates),
                "decision_id": f"ADR-{decision_id}",
                "disposition": disposition,
                "evidence": row["evidence"],
                "kind": "adr",
                "score": score,
                "topic": row["title"],
            }
        )

    authority_edges = [
        _edge_payload(
            ROOT,
            "GOVERNS",
            item["canonical_node_id"],
            candidate_status="fix62d_root_authority_edge_unsigned_lmdb_candidate",
            evidence=item["evidence"],
            method="fix62d_accepted_adr_ratified_cdl_rooting",
        )
        for item in selections
    ]
    return canonical_map, updates, nodes_to_add, selections, authority_edges


def _trace_rooted_sets(edges: list[dict[str, Any]]) -> tuple[set[str], set[str]]:
    authority_adj: dict[str, list[str]] = defaultdict(list)
    trace_adj: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        source = fix62b._edge_source(edge)
        target = fix62b._edge_target(edge)
        edge_type = fix62b._edge_type(edge)
        if edge_type in AUTH_FORWARD_EDGE_TYPES:
            authority_adj[source].append(target)
        if edge_type in TYPED_TRACE_EDGE_TYPES:
            trace_adj[source].append(target)
    authority_rooted = {ROOT}
    queue: deque[str] = deque([ROOT])
    while queue:
        node_id = queue.popleft()
        for target in authority_adj.get(node_id, []):
            if target not in authority_rooted:
                authority_rooted.add(target)
                queue.append(target)

    memo: dict[str, bool] = {}

    def can_trace(node_id: str, seen: frozenset[str] = frozenset()) -> bool:
        if node_id in authority_rooted:
            return True
        if node_id in memo:
            return memo[node_id]
        if node_id in seen:
            return False
        next_seen = frozenset((*seen, node_id))
        result = any(can_trace(target, next_seen) for target in trace_adj.get(node_id, []))
        memo[node_id] = result
        return result

    all_trace_rooted = {node_id for node_id in trace_adj if can_trace(node_id)}
    all_trace_rooted.update(authority_rooted)
    return authority_rooted, all_trace_rooted


def _tokens_from_node_id(node_id: str) -> list[tuple[str, int]]:
    tokens: list[tuple[str, int]] = []
    for match in re.finditer(r"(?:cdl|adr)[_-]?0*([0-9]{1,4})", node_id.lower()):
        raw = match.group(0)
        prefix = "cdl" if raw.startswith("cdl") else "adr"
        token = (prefix, int(match.group(1)))
        if token not in tokens:
            tokens.append(token)
    return tokens


def _priority1_token_edges(
    queue_entries: list[dict[str, Any]],
    trace_rooted: set[str],
    canonical_map: dict[tuple[str, int | str], str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    edges: list[dict[str, Any]] = []
    ledger_rows: list[dict[str, Any]] = []
    for entry in queue_entries:
        if entry.get("priority") != 1:
            continue
        source = str(entry["candidate_id"])
        if source in trace_rooted:
            ledger_rows.append(
                {
                    "candidate_id": source,
                    "disposition": "already_trace_rooted_before_token_repair",
                    "queue_index": entry.get("queue_index"),
                }
            )
            continue
        tokens = _tokens_from_node_id(source)
        matched_targets: list[str] = []
        missing_tokens: list[str] = []
        for prefix, number in tokens:
            target = canonical_map.get((prefix, number))
            if target:
                matched_targets.append(target)
            else:
                missing_tokens.append(f"{prefix}:{number:04d}")
        if not matched_targets:
            ledger_rows.append(
                {
                    "candidate_id": source,
                    "disposition": "no_accepted_or_ratified_token_target",
                    "missing_tokens": missing_tokens,
                    "queue_index": entry.get("queue_index"),
                }
            )
            continue
        for target in sorted(set(matched_targets)):
            edges.append(
                _edge_payload(
                    source,
                    "REFERENCES_AUTHORITY",
                    target,
                    candidate_status="fix62d_deterministic_semantic_token_reference_unsigned_lmdb_candidate",
                    evidence=f"candidate_id_token:{source}",
                    method="fix62d_priority1_token_authority_reference",
                )
            )
        ledger_rows.append(
            {
                "candidate_id": source,
                "disposition": "token_reference_edge_planned",
                "missing_tokens": missing_tokens,
                "planned_targets": sorted(set(matched_targets)),
                "queue_index": entry.get("queue_index"),
            }
        )
    return edges, ledger_rows


def _queue_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    priority_counts = Counter(str(entry["priority"]) for entry in entries)
    reason_counts: Counter[str] = Counter()
    work_family_counts = Counter(str(entry["work_family"]) for entry in entries)
    for entry in entries:
        reason_counts.update(str(reason) for reason in entry.get("reasons", []))
    return {
        "entry_count": len(entries),
        "entries": entries,
        "phase": PHASE,
        "priority_counts": dict(sorted(priority_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "source_queue": str(INPUT_QUEUE_PATH.relative_to(REPO_ROOT)),
        "status": "carry_forward_after_authority_normalization",
        "work_family_counts": dict(sorted(work_family_counts.items())),
    }


def _carry_forward_queue(source_entries: list[dict[str, Any]], trace_rooted: set[str]) -> dict[str, Any]:
    entries = [dict(entry) for entry in source_entries if entry.get("candidate_id") not in trace_rooted]
    entries.sort(key=lambda item: (item["priority"], item["work_family"], item.get("path", ""), item["candidate_id"]))
    for index, entry in enumerate(entries, start=1):
        entry["queue_index"] = index
        entry["batch_id"] = f"fix62d_batch_{((index - 1) // 10) + 1:04d}"
    return _queue_payload(entries)


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(
            path=EVALUATOR_PATH.relative_to(REPO_ROOT),
            node_kind="tooling_source_file_node",
            graph_projection="support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix62d"),),
        ),
        AtlasPhaseFileRegistration(
            path=TEST_PATH.relative_to(REPO_ROOT),
            node_kind="test_evidence_node",
            graph_projection="support_candidate_graph",
            required_edges=(("TESTS", "phase:1545p_fix62d"),),
        ),
        AtlasPhaseFileRegistration(
            path=LEDGER_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62d"),),
        ),
        AtlasPhaseFileRegistration(
            path=QUEUE_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62d"),),
        ),
        AtlasPhaseFileRegistration(
            path=REPORT_MD_PATH.relative_to(REPO_ROOT),
            node_kind="spec_document_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62d"),),
        ),
        AtlasPhaseFileRegistration(
            path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            node_kind="phase_walkthrough_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62d"),),
        ),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def _report_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ILC Fix62d Authority Normalization Report v0.1",
            "",
            "## Summary",
            "",
            f"- Phase: `{PHASE}`",
            f"- Canonical authority selections: `{report['authority_selection_count']}`",
            f"- New authority nodes materialized: `{report['new_authority_node_count']}`",
            f"- Existing authority nodes updated: `{report['node_update_receipt']['accepted_update_count']}`",
            f"- Root authority semantics present: `{report['root_authority_semantics_present_count']}`",
            f"- Priority-1 token reference semantics present: `{report['token_reference_semantics_present_count']}`",
            f"- Next queue entries: `{report['next_queue']['entry_count']}`",
            f"- Next queue priority counts: `{json.dumps(report['next_queue']['priority_counts'], sort_keys=True)}`",
            f"- Final LMDB nodes: `{report['final_counts']['nodes']}`",
            f"- Final LMDB edges: `{report['final_counts']['edges']}`",
            f"- Final preimages: `{report['final_counts']['preimages']}`",
            "",
            "## Interpretation",
            "",
            "Fix62d normalizes accepted ADR and ratified CDL authority targets from",
            "source canon, then applies deterministic semantic references only where a",
            "priority-1 invariant/policy node explicitly names one of those accepted or",
            "ratified identifiers. Open/proposed rows are not promoted.",
            "",
            "## Non-Claims",
            "",
            "- No Genesis signing occurred.",
            "- No public graph upload occurred.",
            "- No public RC activation occurred.",
            "- No ECU minting, settlement, or entitlement was authorized.",
            "- No proposed/open ADR or CDL was promoted.",
            "",
        ]
    )


def _walkthrough_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Phase 1545p-Fix62d Authority Normalization Walkthrough",
            "",
            "## Commands",
            "",
            "- `python tools/evaluators/sim_genesis_atlas_fix62d_authority_normalization.py`",
            "- `python -m pytest tests/test_phase_1545p_fix62d_authority_normalization.py -q`",
            "- `python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb`",
            "",
            "## Results",
            "",
            f"- Canonical authority selections: `{report['authority_selection_count']}`",
            f"- New authority nodes materialized: `{report['new_authority_node_count']}`",
            f"- Node updates accepted/rejected: `{report['node_update_receipt']['accepted_update_count']}` / `{report['node_update_receipt']['rejected_update_count']}`",
            f"- Edge additions accepted/skipped/rejected: `{report['edge_receipt']['accepted_edge_count']}` / `{report['edge_receipt']['skipped_edge_count']}` / `{report['edge_receipt']['rejected_edge_count']}`",
            f"- Root authority semantics present: `{report['root_authority_semantics_present_count']}`",
            f"- Token reference semantics present: `{report['token_reference_semantics_present_count']}`",
            f"- Next queue priority counts: `{json.dumps(report['next_queue']['priority_counts'], sort_keys=True)}`",
            f"- LMDB nodes: `{report['final_counts']['nodes']}`",
            f"- LMDB edges: `{report['final_counts']['edges']}`",
            f"- Preimages: `{report['final_counts']['preimages']}`",
            "",
            "## Boundary",
            "",
            "Fix62d is local unsigned Atlas LMDB maintenance. It does not sign, publish,",
            "activate, mint ECU, settle economics, mutate ADR/CDL text, or authorize",
            "public RC.",
            "",
        ]
    )


def _append_status(report: dict[str, Any]) -> None:
    block = "\n".join(
        [
            "",
            "### Phase 1545p-Fix62d — Authority Normalization Strike Force",
            "",
            "**Status:** complete",
            "",
            f"**Output:** Normalized `{report['authority_selection_count']}` accepted ADR / ratified CDL authority targets, materialized `{report['new_authority_node_count']}` missing authority nodes, verified `{report['root_authority_semantics_present_count']}` root authority semantics and `{report['token_reference_semantics_present_count']}` priority-1 token-reference semantics, reduced the graph-finish queue to `{report['next_queue']['entry_count']}` entries, refreshed preimages, and preserved all non-activation boundaries.",
            "",
            "**Tokens:** fix62d_authority_normalization_complete, fix62d_accepted_adr_ratified_cdl_targets_rooted, fix62d_priority1_token_refs_applied, fix62d_complete",
            "",
        ]
    )
    with STATUS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(block)


def run() -> dict[str, Any]:
    _verify_tokens()
    source_queue = _read_json(INPUT_QUEUE_PATH)
    source_entries = source_queue.get("entries", [])
    if not isinstance(source_entries, list):
        raise ValueError("fix62d_source_queue_entries_missing")

    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        nodes_before = {fix62b._candidate_id(node): node for node in writer.store.iter_nodes()}
        edges_before = writer.store.iter_edges()
        canonical_map, updates, nodes_to_add, selections, authority_edges = _build_authority_plan(
            nodes_before,
            edges_before,
        )
        node_update_receipt = writer.update_node_fields(
            updates,
            phase=PHASE,
            dry_run=False,
            metadata={"scope": "accepted_adr_ratified_cdl_authority_normalization"},
        )
        if node_update_receipt.get("status") != "PASS":
            raise ValueError("fix62d_node_update_failed")

        # Recompute trace after authority updates but before new root/token edges.
        _, trace_rooted_before_token = _trace_rooted_sets(writer.store.iter_edges())
        token_edges, token_ledger_rows = _priority1_token_edges(
            source_entries,
            trace_rooted_before_token,
            canonical_map,
        )
        edge_receipt = writer.apply_plan(
            AtlasLmdbWritePlan(
                nodes_to_add=nodes_to_add,
                edges_to_add=[*authority_edges, *token_edges],
                metadata={"operation": "authority_normalization_and_priority1_token_refs"},
                phase=PHASE,
                dry_run=False,
            )
        )
        if edge_receipt.get("status") != "PASS":
            raise ValueError("fix62d_edge_application_failed")

        edges_after = writer.store.iter_edges()
        _, trace_rooted_after = _trace_rooted_sets(edges_after)
        next_queue = _carry_forward_queue(source_entries, trace_rooted_after)
        ledger = {
            "authority_edges_planned_count": len(authority_edges),
            "authority_selections": selections,
            "canonical_map_size": len(canonical_map),
            "new_authority_node_count": len(nodes_to_add),
            "new_authority_nodes": [node["candidate_id"] for node in nodes_to_add],
            "node_update_count": len(updates),
            "phase": PHASE,
            "priority1_token_edge_count": len(token_edges),
            "priority1_token_ledger_rows": token_ledger_rows,
            "status": "PASS",
        }
        write_json_atomic(LEDGER_PATH, ledger)
        write_json_atomic(QUEUE_PATH, next_queue)

        expected_root_semantics = {
            (ROOT, "GOVERNS", item["canonical_node_id"]) for item in selections
        }
        expected_token_semantics = {
            (edge["source"], edge["edge_type"], edge["target"]) for edge in token_edges
        }
        observed_semantics = {
            (fix62b._edge_source(edge), fix62b._edge_type(edge), fix62b._edge_target(edge))
            for edge in edges_after
        }
        provisional_report: dict[str, Any] = {
            "authority_selection_count": len(selections),
            "edge_receipt": edge_receipt,
            "final_counts": {"edges": 0, "nodes": 0, "preimages": 0},
            "ledger": {
                "authority_selection_count": len(selections),
                "new_authority_node_count": len(nodes_to_add),
                "priority1_token_edge_count": len(token_edges),
            },
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "new_authority_node_count": len(nodes_to_add),
            "next_queue": {
                "entry_count": next_queue["entry_count"],
                "priority_counts": next_queue["priority_counts"],
                "reason_counts": next_queue["reason_counts"],
                "work_family_counts": next_queue["work_family_counts"],
            },
            "node_update_receipt": node_update_receipt,
            "non_claims": [
                "fix62d_does_not_authorize_ecu_minting_or_settlement",
                "fix62d_does_not_sign_or_publish_the_genesis_atlas",
                "fix62d_does_not_mutate_adr_or_cdl_text",
                "fix62d_does_not_promote_open_or_proposed_authority",
            ],
            "phase": PHASE,
            "root_authority_semantics_present_count": len(expected_root_semantics & observed_semantics),
            "status": "PASS",
            "token_reference_semantics_present_count": len(expected_token_semantics & observed_semantics),
        }
        fix62b._write_text_atomic(REPORT_MD_PATH, _report_markdown(provisional_report))
        fix62b._write_text_atomic(WALKTHROUGH_PATH, _walkthrough_markdown(provisional_report))

        registration_receipt = _register_phase_files(writer)
        if registration_receipt.get("status") != "PASS":
            raise ValueError("fix62d_phase_file_registration_failed")

        final_nodes = writer.store.iter_nodes()
        final_edges = writer.store.iter_edges()
        preimages = [_node_preimage(node) for node in final_nodes]
        preimages.extend(_edge_preimage(edge) for edge in final_edges)
        preimage_receipt = writer.write_preimages(
            preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "full_lmdb_after_fix62d"},
        )
        if preimage_receipt.get("status") != "PASS":
            raise ValueError("fix62d_preimage_write_failed")

        report = dict(provisional_report)
        report["file_registration_receipt"] = registration_receipt
        report["final_counts"] = {
            "edges": len(writer.store.iter_edges()),
            "nodes": len(writer.store.iter_nodes()),
            "preimages": len(writer.store.iter_preimages()),
        }
        report["preimage_receipt"] = preimage_receipt
        write_json_atomic(OUT_REPORT_PATH, report)
        fix62b._write_text_atomic(REPORT_MD_PATH, _report_markdown(report))
        fix62b._write_text_atomic(WALKTHROUGH_PATH, _walkthrough_markdown(report))
        writer.write_metadata(
            "fix62d_authority_normalization_report",
            {
                "final_counts": report["final_counts"],
                "ledger_path": str(LEDGER_PATH.relative_to(REPO_ROOT)),
                "out_report_path": str(OUT_REPORT_PATH.relative_to(REPO_ROOT)),
                "phase": PHASE,
                "status": "PASS",
            },
            phase=PHASE,
            dry_run=False,
        )
        _append_status(report)
        return report
    finally:
        writer.close()


def main() -> int:
    report = run()
    print(
        json.dumps(
            {
                "final_counts": report["final_counts"],
                "next_queue": report["next_queue"],
                "phase": PHASE,
                "status": report["status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
