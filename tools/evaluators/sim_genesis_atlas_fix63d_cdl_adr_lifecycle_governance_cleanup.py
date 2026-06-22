# SPDX-License-Identifier: AGPL-3.0-only
"""Fix63d CDL/ADR lifecycle governance cleanup over the unified Atlas LMDB.

PUBLIC_RC_EXCLUDE: fix63d_unsigned_atlas_lmdb_maintenance
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas support maintenance only; not
Genesis signing, public graph publication, runtime activation, ECU minting, or
ILC settlement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    AtlasPhaseFileRegistration,
    deterministic_edge_id,
)


PHASE = "1545p-Fix63d"
PHASE_TOKEN = "phase_1545p_fix63d"
REPO_ROOT = Path(__file__).resolve().parents[2]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
ADR_DIR = REPO_ROOT / "docs/adr"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix63d_cdl_adr_no_outbound_governs_queue_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix63d_cdl_adr_lifecycle_governance_cleanup_ledger_v0.1.json"
REPORT_PATH = REPO_ROOT / "docs/specs/ilc_fix63d_cdl_adr_lifecycle_governance_cleanup_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix63d_cdl_adr_lifecycle_governance_cleanup_walkthrough.md"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix63d_cdl_adr_lifecycle_governance_cleanup.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix63d_cdl_adr_lifecycle_governance_cleanup.py"

AUTHORITY_PREFIXES = ("cdl:", "adr:", "artifact:", "policy:", "truth_primitive:", "invariant:", "phase:", "target:")
PROCEDURAL_EDGE_TYPES = {
    "SAME_AUTHORITY",
    "OPENED_FOR",
    "PRELOCK_FOR",
    "RATIFICATION_EVIDENCE_FOR",
    "PROPOSES_CHANGE_TO",
    "RESOLVED_BY",
    "DERIVED_FROM",
    "CLASSIFIED_BY",
    "GOVERNS",
}


@dataclass(frozen=True)
class SourceEvidence:
    path: str
    line_ref: str
    status: str
    summary: str

    @property
    def evidence(self) -> str:
        return f"{self.path}:{self.line_ref}"


def _canonical_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp", text=True)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False))
            handle.write("\n")
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp", text=True)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _load_graph(writer: AtlasLmdbSafeWriter) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    nodes = {node["candidate_id"]: node for node in writer.store.iter_nodes() if node.get("candidate_id")}
    edges = writer.store.iter_edges()
    return nodes, edges


def _edge_source(edge: dict[str, Any]) -> str:
    return str(edge.get("source") or edge.get("src") or "")


def _edge_target(edge: dict[str, Any]) -> str:
    return str(edge.get("target") or edge.get("tgt") or "")


def _edge_type(edge: dict[str, Any]) -> str:
    return str(edge.get("edge_type") or "")


def _live_queue(nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    outgoing: dict[str, list[dict[str, Any]]] = {node_id: [] for node_id in nodes}
    incoming: dict[str, list[dict[str, Any]]] = {node_id: [] for node_id in nodes}
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        if source in outgoing:
            outgoing[source].append(edge)
        if target in incoming:
            incoming[target].append(edge)

    queue: list[dict[str, Any]] = []
    for node_id, node in sorted(nodes.items()):
        if not (node_id.startswith("cdl:") or node_id.startswith("adr:")):
            continue
        has_outbound_non_repo_governs = any(
            _edge_type(edge) == "GOVERNS" and not _edge_target(edge).startswith("repo:")
            for edge in outgoing.get(node_id, [])
        )
        if has_outbound_non_repo_governs:
            continue
        queue.append(
            {
                "candidate_id": node_id,
                "candidate_status": node.get("candidate_status") or node.get("authority_status"),
                "graph_projection": node.get("graph_projection"),
                "incoming_edge_count": len(incoming.get(node_id, [])),
                "node_kind": node.get("node_kind"),
                "outgoing_edge_count": len(outgoing.get(node_id, [])),
                "source_path": node.get("source_path"),
            }
        )
    return queue


def _number_token(node_id: str) -> str:
    rest = node_id.split(":", 1)[1]
    if rest.startswith("ADR_"):
        return rest.split("_", 2)[1]
    if rest.startswith("v"):
        match = re.match(r"(v\d+)", rest, flags=re.IGNORECASE)
        return match.group(1).lower() if match else rest.split("_", 1)[0].lower()
    return rest.split("_", 1)[0]


def _authority_score(node_id: str, node: dict[str, Any]) -> tuple[int, str]:
    score = 0
    status = str(node.get("candidate_status") or node.get("authority_status") or "").lower()
    kind = str(node.get("node_kind") or "").lower()
    projection = str(node.get("graph_projection") or "")
    if "ratified" in status or "accepted" in status:
        score -= 30
    if kind in {"cdl_artifact", "adr_artifact"}:
        score -= 20
    if projection == "genesis_core_star_map":
        score -= 10
    if "support" in kind or "alias" in kind or "lifecycle" in kind or "proposal" in kind:
        score += 50
    if node_id.split(":", 1)[1] == _number_token(node_id):
        score += 25
    return (score, node_id)


def _canonical_index(nodes: dict[str, dict[str, Any]], prefix: str) -> dict[str, str]:
    grouped: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for node_id, node in nodes.items():
        if node_id.startswith(f"{prefix}:"):
            grouped.setdefault(_number_token(node_id), []).append((node_id, node))
    result: dict[str, str] = {}
    for token, values in grouped.items():
        values.sort(key=lambda item: _authority_score(item[0], item[1]))
        result[token] = values[0][0]
    return result


def _adr_files_by_number() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in sorted(ADR_DIR.glob("ADR_*.md")):
        match = re.search(r"ADR_(\d{4})", path.name)
        if match:
            files.setdefault(match.group(1), path)
    return files


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _line_ref_for_match(text: str, pattern: str, *, fallback_span: int = 20) -> str:
    lines = text.splitlines()
    regex = re.compile(pattern, flags=re.IGNORECASE)
    for index, line in enumerate(lines, start=1):
        if regex.search(line):
            return f"{index}-{min(len(lines), index + fallback_span)}"
    return f"1-{min(len(lines), fallback_span)}"


def _extract_line_range(text: str, line_ref: str) -> str:
    start_s, _, end_s = line_ref.partition("-")
    start = max(1, int(start_s or "1"))
    end = max(start, int(end_s or start_s or "1"))
    lines = text.splitlines()
    return "\n".join(lines[start - 1 : min(end, len(lines))])


def _cdl_evidence(node_id: str, node: dict[str, Any]) -> SourceEvidence:
    source_path = node.get("source_path")
    if isinstance(source_path, str) and source_path and source_path != "docs/phases/STATUS.md":
        path = REPO_ROOT / source_path
        if path.exists():
            text = _read_text(path)
            return SourceEvidence(source_path, f"1-{min(40, len(text.splitlines()))}", "source_path_read", _extract_line_range(text, f"1-{min(12, len(text.splitlines()))}"))

    text = _read_text(CDL_REGISTER)
    token = _number_token(node_id)
    if token.startswith("v"):
        pattern = rf"\\b{re.escape(token.upper())}\\b|\\b{re.escape(token)}\\b"
    elif token.isdigit():
        pattern = rf"CDL[- ]?0*{int(token):03d}\\b|\\b{node_id}\\b"
    else:
        pattern = re.escape(node_id)
    line_ref = _line_ref_for_match(text, pattern)
    return SourceEvidence(
        str(CDL_REGISTER.relative_to(REPO_ROOT)),
        line_ref,
        "cdl_register_direct_read",
        _extract_line_range(text, line_ref),
    )


def _adr_status(text: str) -> str:
    for line in text.splitlines()[:80]:
        if line.lower().startswith("status:"):
            return line.split(":", 1)[1].strip()
        if line.lower().startswith("**status:**"):
            return line.split("**", 2)[-1].strip()
    if re.search(r"\baccepted\b", text[:2000], flags=re.IGNORECASE):
        return "Accepted"
    if re.search(r"\bproposed\b", text[:2000], flags=re.IGNORECASE):
        return "Proposed"
    return "unknown"


def _adr_evidence(node_id: str, node: dict[str, Any], adr_files: dict[str, Path]) -> SourceEvidence:
    source_path = node.get("source_path")
    if isinstance(source_path, str) and source_path and source_path != "docs/phases/STATUS.md":
        path = REPO_ROOT / source_path
        if path.exists():
            text = _read_text(path)
            line_ref = _line_ref_for_match(text, r"^status:|accepted|proposed|decision|governance")
            return SourceEvidence(source_path, line_ref, "source_path_read", _extract_line_range(text, line_ref))
    token = _number_token(node_id)
    path = adr_files.get(token)
    if path and path.exists():
        text = _read_text(path)
        line_ref = _line_ref_for_match(text, r"^status:|accepted|proposed|decision|governance")
        return SourceEvidence(str(path.relative_to(REPO_ROOT)), line_ref, "adr_file_direct_read", _extract_line_range(text, line_ref))
    return SourceEvidence("", "0-0", "escalated_no_source", f"No ADR source file found for {node_id}")


def _edge(source: str, edge_type: str, target: str, evidence: str, status: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix63d_lifecycle_governance_cleanup",
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": status,
        "confidence": "high",
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "evidence": evidence,
        "source": source,
        "src": source,
        "target": target,
        "tgt": target,
    }


def _node_patch(disposition: str, evidence: SourceEvidence, *, graph_projection: str | None = None, node_kind: str | None = None, candidate_status: str | None = None) -> dict[str, Any]:
    patch: dict[str, Any] = {
        "fix63d_disposition": disposition,
        "fix63d_evidence": evidence.evidence if evidence.path else evidence.status,
        "fix63d_review_status": "direct_read_reviewed",
    }
    if graph_projection:
        patch["graph_projection"] = graph_projection
    if node_kind:
        patch["node_kind"] = node_kind
    if candidate_status:
        patch["candidate_status"] = candidate_status
    return patch


def _classify_cdl(node_id: str, node: dict[str, Any], canonical_cdl: dict[str, str], nodes: dict[str, dict[str, Any]]) -> tuple[str, list[dict[str, Any]], dict[str, Any], SourceEvidence]:
    evidence = _cdl_evidence(node_id, node)
    token = _number_token(node_id)
    canonical = canonical_cdl.get(token)
    kind = str(node.get("node_kind") or "").lower()
    status = str(node.get("candidate_status") or node.get("authority_status") or "").lower()
    edges: list[dict[str, Any]] = []

    if evidence.status == "escalated_no_source":
        return "escalated_no_source", edges, _node_patch("escalated_no_source", evidence), evidence

    if canonical and canonical != node_id and ("shadow" in status or "alias" in kind or "support" in kind):
        if "opening" in node_id:
            edge_type = "OPENED_FOR"
            disposition = "lifecycle_opening_record"
        elif "prelock" in node_id:
            edge_type = "PRELOCK_FOR"
            disposition = "lifecycle_prelock_record"
        elif "ratification" in node_id:
            edge_type = "RATIFICATION_EVIDENCE_FOR"
            disposition = "lifecycle_ratification_record"
        elif "open_cdl_stub" in status or "open" in status:
            edge_type = "DERIVED_FROM"
            disposition = "open_cdl_support_record"
        elif "candidate_review_required" in status:
            edge_type = "DERIVED_FROM"
            disposition = "candidate_review_overlay"
        else:
            edge_type = "SAME_AUTHORITY"
            disposition = "shadow_duplicate_same_authority"
        edges.append(_edge(node_id, edge_type, canonical, evidence.evidence, f"fix63d_{disposition}"))
        return (
            disposition,
            edges,
            _node_patch(
                disposition,
                evidence,
                graph_projection="support_candidate_graph",
                node_kind="cdl_alias_or_lifecycle_support_node",
                candidate_status=f"fix63d_{disposition}_not_independent_authority",
            ),
            evidence,
        )

    if "open_cdl_stub" in status or ("support" in kind and "ratified" not in status):
        disposition = "open_cdl_support_record"
        return (
            disposition,
            edges,
            _node_patch(
                disposition,
                evidence,
                graph_projection="support_candidate_graph",
                node_kind="cdl_support_candidate_overlay",
                candidate_status="fix63d_open_cdl_support_record_not_independent_authority",
            ),
            evidence,
        )

    if "ratified" in status or str(node.get("graph_projection")) == "genesis_core_star_map":
        disposition = "canonical_ratified_cdl_no_concrete_governed_target"
        return disposition, edges, _node_patch(disposition, evidence, candidate_status=str(node.get("candidate_status") or f"ratified_CDL_{token}")), evidence

    disposition = "cdl_support_record_reviewed"
    return disposition, edges, _node_patch(disposition, evidence, graph_projection="support_candidate_graph"), evidence


def _classify_adr(node_id: str, node: dict[str, Any], canonical_adr: dict[str, str], nodes: dict[str, dict[str, Any]], adr_files: dict[str, Path]) -> tuple[str, list[dict[str, Any]], dict[str, Any], SourceEvidence]:
    evidence = _adr_evidence(node_id, node, adr_files)
    token = _number_token(node_id)
    canonical = canonical_adr.get(token)
    kind = str(node.get("node_kind") or "").lower()
    status = str(node.get("candidate_status") or node.get("authority_status") or "").lower()
    source_text = ""
    if evidence.path:
        path = REPO_ROOT / evidence.path
        if path.exists():
            source_text = _read_text(path)
    adr_status = _adr_status(source_text) if source_text else "unknown"
    edges: list[dict[str, Any]] = []

    if evidence.status == "escalated_no_source":
        return "escalated_no_source", edges, _node_patch("escalated_no_source", evidence), evidence

    if canonical and canonical != node_id and ("alias" in kind or "support" in kind or "rooted_authority" in status):
        if "option_b" in node_id or "decision" in kind or "graduation" in node_id:
            edge_type = "RESOLVED_BY"
            disposition = "adr_decision_or_lifecycle_record"
        elif "proposed" in status or "proposal" in kind or adr_status.lower().startswith("proposed"):
            edge_type = "PROPOSES_CHANGE_TO"
            disposition = "adr_proposal_record"
        else:
            edge_type = "SAME_AUTHORITY"
            disposition = "shadow_duplicate_same_authority"
        edges.append(_edge(node_id, edge_type, canonical, evidence.evidence, f"fix63d_{disposition}"))
        return (
            disposition,
            edges,
            _node_patch(
                disposition,
                evidence,
                graph_projection="support_candidate_graph",
                node_kind="adr_alias_or_lifecycle_support_node",
                candidate_status=f"fix63d_{disposition}_not_independent_authority",
            ),
            evidence,
        )

    if "proposed" in status or "proposal" in kind or adr_status.lower().startswith("proposed"):
        disposition = "proposed_adr_record_no_governs"
        return (
            disposition,
            edges,
            _node_patch(
                disposition,
                evidence,
                graph_projection="support_candidate_graph",
                node_kind="adr_proposal_artifact",
                candidate_status="fix63d_proposed_adr_record_not_independent_authority",
            ),
            evidence,
        )

    if adr_status.lower().startswith("accepted") or "accepted" in status or str(node.get("graph_projection")) == "genesis_core_star_map":
        disposition = "canonical_accepted_adr_no_concrete_governed_target"
        return disposition, edges, _node_patch(disposition, evidence, candidate_status=str(node.get("candidate_status") or f"accepted_ADR_{token}")), evidence

    disposition = "adr_support_record_reviewed"
    return disposition, edges, _node_patch(disposition, evidence, graph_projection="support_candidate_graph"), evidence


def _build_outputs(batch_size: int) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        nodes, edges = _load_graph(writer)
    finally:
        writer.close()
    queue = _live_queue(nodes, edges)
    canonical_cdl = _canonical_index(nodes, "cdl")
    canonical_adr = _canonical_index(nodes, "adr")
    adr_files = _adr_files_by_number()

    entries: list[dict[str, Any]] = []
    edge_candidates: list[dict[str, Any]] = []
    node_updates: dict[str, dict[str, Any]] = {}
    disposition_counter: Counter[str] = Counter()
    edge_type_counter: Counter[str] = Counter()
    existing_semantics = {(_edge_source(edge), _edge_type(edge), _edge_target(edge)) for edge in edges}
    plan_semantics: set[tuple[str, str, str]] = set()

    for index, item in enumerate(queue):
        node_id = item["candidate_id"]
        node = nodes[node_id]
        if node_id.startswith("cdl:"):
            disposition, candidates, patch, evidence = _classify_cdl(node_id, node, canonical_cdl, nodes)
        else:
            disposition, candidates, patch, evidence = _classify_adr(node_id, node, canonical_adr, nodes, adr_files)

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
            edge_candidates.append(candidate)
            accepted_edges.append(candidate)
            edge_type_counter[candidate["edge_type"]] += 1

        node_updates[node_id] = patch
        disposition_counter[disposition] += 1
        entries.append(
            {
                "candidate_id": node_id,
                "direct_read": {
                    "line_refs": [evidence.line_ref],
                    "path": evidence.path,
                    "source_status": evidence.status,
                    "summary": evidence.summary[:2000],
                },
                "disposition": disposition,
                "duplicate_edges_observed": duplicate_edges,
                "node_update": patch,
                "recommended_edges": accepted_edges,
                "row_index": index,
            }
        )

    batches: list[dict[str, Any]] = []
    for batch_index in range(math.ceil(len(entries) / batch_size)):
        batch_entries = entries[batch_index * batch_size : (batch_index + 1) * batch_size]
        batches.append(
            {
                "batch_index": batch_index + 1,
                "candidate_ids": [entry["candidate_id"] for entry in batch_entries],
                "entry_count": len(batch_entries),
            }
        )

    queue_payload = {
        "description": "Live CDL/ADR nodes with no outbound non-repo GOVERNS at Fix63d execution time.",
        "generated_by": "tools/evaluators/sim_genesis_atlas_fix63d_cdl_adr_lifecycle_governance_cleanup.py",
        "lmdb_root": str(LMDB_ROOT.relative_to(REPO_ROOT)),
        "phase": PHASE,
        "queue": queue,
        "queue_counts": dict(Counter(item["candidate_id"].split(":", 1)[0] for item in queue)),
        "queue_count": len(queue),
        "schema_version": "fix63d_cdl_adr_no_outbound_governs_queue.v0.1",
    }
    ledger = {
        "batch_size": batch_size,
        "batches": batches,
        "disposition_counts": dict(sorted(disposition_counter.items())),
        "duplicate_procedural_edge_count": sum(
            len(entry.get("duplicate_edges_observed", [])) for entry in entries
        ),
        "edge_type_counts": dict(sorted(edge_type_counter.items())),
        "entries": entries,
        "escalated_no_source_count": sum(
            1 for entry in entries if entry["direct_read"]["source_status"] == "escalated_no_source"
        ),
        "lmdb_root": str(LMDB_ROOT.relative_to(REPO_ROOT)),
        "node_update_count": len(node_updates),
        "phase": PHASE,
        "pre_execution_queue_count": len(queue),
        "pre_execution_queue_counts": dict(Counter(item["candidate_id"].split(":", 1)[0] for item in queue)),
        "recommended_edge_count": len(edge_candidates),
        "schema_version": "fix63d_cdl_adr_lifecycle_governance_cleanup_ledger.v0.1",
        "source_backed_direct_read_count": sum(
            1 for entry in entries if entry["direct_read"]["source_status"] != "escalated_no_source"
        ),
    }
    report = {
        "disposition_counts": dict(sorted(disposition_counter.items())),
        "duplicate_procedural_edge_count": ledger["duplicate_procedural_edge_count"],
        "edge_type_counts": dict(sorted(edge_type_counter.items())),
        "escalated_no_source_count": ledger["escalated_no_source_count"],
        "lmdb_root": str(LMDB_ROOT.relative_to(REPO_ROOT)),
        "node_update_count": len(node_updates),
        "phase": PHASE,
        "pre_execution_queue_count": len(queue),
        "pre_execution_queue_counts": dict(Counter(item["candidate_id"].split(":", 1)[0] for item in queue)),
        "recommended_edge_count": len(edge_candidates),
        "schema_version": "fix63d_report.v0.1",
        "source_backed_direct_read_count": ledger["source_backed_direct_read_count"],
    }
    return queue_payload, ledger, edge_candidates, node_updates, report


def _status_entry(report: dict[str, Any], final_info: dict[str, Any]) -> str:
    return f"""
### Phase 1545p-Fix63d — CDL/ADR Lifecycle Governance Cleanup

**Status:** complete

**Output:** Recomputed the live CDL/ADR no-outbound-GOVERNS queue from the unified LMDB, reviewed `{{queue}}` CDL/ADR nodes, direct-read `{{source_backed}}` source-backed authority or lifecycle records with `{{escalated}}` no-source escalation, applied `{{edges}}` new procedural governance edges, confirmed `{{duplicates}}` pre-existing procedural edges, updated `{{updates}}` CDL/ADR node classifications, registered Fix63d files in LMDB, and preserved all non-activation boundaries. Post-run LMDB: `{{nodes}}` nodes / `{{edge_count}}` edges / `{{dangling}}` dangling / `{{debt}}` edge-id debt.

**Tokens:** fix63d_cdl_adr_lifecycle_governance_cleanup_complete, fix63d_no_blanket_governs_expansion, fix63d_complete
""".format(
        queue=report["pre_execution_queue_count"],
        source_backed=report["source_backed_direct_read_count"],
        escalated=report["escalated_no_source_count"],
        edges=report["edge_application"]["accepted_edge_count"],
        duplicates=report["duplicate_procedural_edge_count"],
        updates=report["node_update_receipt"]["accepted_update_count"],
        nodes=final_info["node_count"],
        edge_count=final_info["edge_count"],
        dangling=final_info["dangling_edge_count"],
        debt=final_info["edge_id_debt_count"],
    )


def _append_status(report: dict[str, Any], final_info: dict[str, Any]) -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    if "fix63d_complete" in status:
        return
    _write_text(STATUS_PATH, status.rstrip() + "\n\n" + _status_entry(report, final_info).lstrip())


def _markdown_report(report: dict[str, Any]) -> str:
    edge_lines = "\n".join(f"- `{key}`: `{value}`" for key, value in sorted(report["edge_type_counts"].items())) or "- none"
    disposition_lines = "\n".join(f"- `{key}`: `{value}`" for key, value in sorted(report["disposition_counts"].items()))
    return f"""# Fix63d CDL/ADR Lifecycle Governance Cleanup Report

- Phase: `{PHASE}`
- LMDB: `{report['lmdb_root']}`
- Pre-execution queue: `{report['pre_execution_queue_count']}`
- Queue counts: `{report['pre_execution_queue_counts']}`
- Node classifications updated: `{report['node_update_receipt']['accepted_update_count']}`
- Procedural edges written: `{report['edge_application']['accepted_edge_count']}`
- Pre-existing procedural edges observed/skipped before write plan: `{report['duplicate_procedural_edge_count']}`
- Edge-write duplicate skips inside safe writer: `{report['edge_application']['skipped_edge_count']}`
- Source-backed direct reads: `{report['source_backed_direct_read_count']}`
- Escalated no-source records: `{report['escalated_no_source_count']}`
- `GOVERNS` edges written: `{report['edge_type_counts'].get('GOVERNS', 0)}`
- Final LMDB nodes/edges: `{report['final_lmdb']['node_count']}` / `{report['final_lmdb']['edge_count']}`
- Dangling edges / edge-id debt: `{report['final_lmdb']['dangling_edge_count']}` / `{report['final_lmdb']['edge_id_debt_count']}`

## Edge Types

{edge_lines}

## Dispositions

{disposition_lines}

## Non-Claims

Fix63d is local unsigned Atlas LMDB maintenance only. It does not authorize public RC, publication, runtime activation, ECU minting, ILC settlement, CDL mutation, ADR mutation, Genesis signing, or public graph upload.
"""


def _walkthrough(report: dict[str, Any]) -> str:
    disposition_lines = "\n".join(f"- `{key}`: `{value}`" for key, value in sorted(report["disposition_counts"].items()))
    edge_lines = "\n".join(f"- `{key}`: `{value}`" for key, value in sorted(report["edge_type_counts"].items())) or "- none"
    return f"""# Phase 1545p-Fix63d CDL/ADR Lifecycle Governance Cleanup Walkthrough

## Summary

Fix63d recomputed the live CDL/ADR queue from `out/genesis_base_graph_v0.4_unified.lmdb`. It processed `{report['pre_execution_queue_count']}` nodes: `{report['pre_execution_queue_counts'].get('cdl', 0)}` CDL nodes and `{report['pre_execution_queue_counts'].get('adr', 0)}` ADR nodes. Direct source reads succeeded for `{report['source_backed_direct_read_count']}` records; `{report['escalated_no_source_count']}` record was escalated because no source file exists in the current repo.

The phase classified records rather than forcing blanket authority. Lifecycle, proposal, open, alias, and shadow records were not given false independent `GOVERNS` edges.

## LMDB Writes

- Node field updates accepted: `{report['node_update_receipt']['accepted_update_count']}`
- Procedural edges accepted: `{report['edge_application']['accepted_edge_count']}`
- Pre-existing procedural edges observed/skipped before write plan: `{report['duplicate_procedural_edge_count']}`
- Edge-write duplicate skips inside safe writer: `{report['edge_application']['skipped_edge_count']}`
- Final LMDB nodes: `{report['final_lmdb']['node_count']}`
- Final LMDB edges: `{report['final_lmdb']['edge_count']}`
- Dangling edges: `{report['final_lmdb']['dangling_edge_count']}`
- Edge-id debt: `{report['final_lmdb']['edge_id_debt_count']}`

## Edge Type Counts

{edge_lines}

## Disposition Counts

{disposition_lines}

## GOVERNS Boundary

`GOVERNS` edges written: `{report['edge_type_counts'].get('GOVERNS', 0)}`. No lifecycle, proposal, open, alias, or shadow record received a false independent `GOVERNS` edge.

## Verification

- `python -m py_compile tools/evaluators/sim_genesis_atlas_fix63d_cdl_adr_lifecycle_governance_cleanup.py tests/test_phase_1545p_fix63d_cdl_adr_lifecycle_governance_cleanup.py`
- `python tools/evaluators/sim_genesis_atlas_fix63d_cdl_adr_lifecycle_governance_cleanup.py --batch-size 10`
- `python -m pytest tests/test_phase_1545p_fix63d_cdl_adr_lifecycle_governance_cleanup.py tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py -q`
- `python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb`

## Non-Claims

Fix63d is local unsigned Atlas LMDB maintenance only. It does not authorize public RC, publication, runtime activation, ECU minting, ILC settlement, CDL mutation, ADR mutation, Genesis signing, or public graph upload.
"""


def _register_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = [
        AtlasPhaseFileRegistration(EVALUATOR_PATH.relative_to(REPO_ROOT), "atlas_lmdb_maintenance_tool", "support_candidate_graph"),
        AtlasPhaseFileRegistration(TEST_PATH.relative_to(REPO_ROOT), "phase_test", "support_candidate_graph", graph_delta="support_tests_added"),
        AtlasPhaseFileRegistration(QUEUE_PATH.relative_to(REPO_ROOT), "atlas_manual_audit_record", "support_candidate_graph"),
        AtlasPhaseFileRegistration(LEDGER_PATH.relative_to(REPO_ROOT), "atlas_manual_audit_record", "support_candidate_graph"),
        AtlasPhaseFileRegistration(REPORT_PATH.relative_to(REPO_ROOT), "atlas_manual_audit_report", "support_candidate_graph"),
        AtlasPhaseFileRegistration(WALKTHROUGH_PATH.relative_to(REPO_ROOT), "phase_walkthrough", "support_candidate_graph"),
        AtlasPhaseFileRegistration(STATUS_PATH.relative_to(REPO_ROOT), "phase_status_log", "support_candidate_graph"),
    ]
    return writer.register_phase_files(PHASE, files, dry_run=False)


def execute(batch_size: int) -> dict[str, Any]:
    for token in ("fix63_complete", "fix63a_complete", "fix63c_complete"):
        if token not in STATUS_PATH.read_text(encoding="utf-8"):
            raise ValueError(f"fix63d_missing_input_token:{token}")

    queue_payload, ledger, edge_candidates, node_updates, report = _build_outputs(batch_size)
    _canonical_json(QUEUE_PATH, queue_payload)
    _canonical_json(LEDGER_PATH, ledger)

    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        update_receipt = writer.update_node_fields(
            node_updates,
            phase=PHASE,
            dry_run=False,
            metadata={"operation": "fix63d_cdl_adr_lifecycle_node_classification"},
        )
        edge_receipt = writer.apply_plan(
            AtlasLmdbWritePlan(
                nodes_to_add=[],
                edges_to_add=edge_candidates,
                metadata={"operation": "fix63d_cdl_adr_lifecycle_procedural_edges"},
                phase=PHASE,
                dry_run=False,
            )
        )
        if edge_receipt["rejected_edge_count"]:
            raise ValueError(f"fix63d_edge_rejections:{edge_receipt['rejected_edges']}")
        final_info_before_files = writer.inspect()
        report["node_update_receipt"] = update_receipt
        report["edge_application"] = edge_receipt
        report["final_lmdb_before_file_registration"] = final_info_before_files
        _write_text(REPORT_PATH, _markdown_report({**report, "final_lmdb": final_info_before_files}))
        _write_text(WALKTHROUGH_PATH, _walkthrough({**report, "final_lmdb": final_info_before_files}))
        _append_status({**report, "final_lmdb": final_info_before_files}, final_info_before_files)
        file_registration = _register_files(writer)
        final_info = writer.inspect()
    finally:
        writer.close()

    report["file_registration"] = file_registration
    report["final_lmdb"] = final_info
    _write_text(REPORT_PATH, _markdown_report(report))
    _write_text(WALKTHROUGH_PATH, _walkthrough(report))
    _append_status(report, final_info)
    return {
        "edge_application": edge_receipt,
        "file_registration": file_registration,
        "final_lmdb": final_info,
        "node_update_receipt": update_receipt,
        "report": report,
        "status": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=10)
    args = parser.parse_args()
    result = execute(batch_size=args.batch_size)
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
