#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Run Phase 1545p-Fix46 manual semantic annotation tranche.

PUBLIC_RC_EXCLUDE: genesis_base_graph_fix46_manual_semantic_annotation_research_only
PUBLIC_RC_EXCLUDE_REASON: Unsigned candidate support-edge annotation over a
research Atlas candidate; no Genesis signing, canonical graph mutation, public
graph publication, public RC activation, runtime activation, minting,
settlement, or ADR/CDL mutation.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE = "1545p-Fix46"
SCHEMA_VERSION = "genesis_base_graph_fix46_manual_semantic_annotation.v0.1"

CANDIDATE_IN = REPO_ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix45.json"
QUEUE_IN = REPO_ROOT / "docs/specs/ilc_fix46_manual_semantic_annotation_queue_v0.1.json"
CANDIDATE_OUT = REPO_ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix46.json"
LEDGER_OUT = REPO_ROOT / "docs/specs/ilc_fix46_manual_semantic_annotation_ledger_v0.1.json"
REPORT_OUT = REPO_ROOT / "docs/specs/ilc_fix46_manual_semantic_annotation_report_v0.1.md"
RESIDUAL_QUEUE_OUT = REPO_ROOT / "docs/specs/ilc_fix47_residual_semantic_annotation_queue_v0.1.json"
WALKTHROUGH_OUT = REPO_ROOT / "docs/phases/phase_1545p_fix46_manual_semantic_annotation_walkthrough.md"

SOURCE_TREE_TARGET = "artifact:genesis_source_tree_manifest_candidate_1545p_fix38"
BATCH_SIZE = 10

NEW_DOC_PATHS = [
    "docs/specs/ilc_fix46_manual_semantic_annotation_ledger_v0.1.json",
    "docs/specs/ilc_fix46_manual_semantic_annotation_report_v0.1.md",
    "docs/specs/ilc_fix47_residual_semantic_annotation_queue_v0.1.json",
]

TOKENS = [
    "fix46_manual_semantic_annotation_complete",
    "fix46_enriched_candidate_produced",
    "fix46_residual_queue_produced",
    "fix46_complete",
    "public_path_remains_blocked_phase_1545p_fix46",
]

NON_CLAIMS = [
    "No Genesis signing occurred.",
    "No signed genesis_base_graph_v0.4.json artifact was produced.",
    "No canonical Atlas mutation occurred.",
    "No public graph publication occurred.",
    "No public repository push occurred.",
    "No public RC activation occurred.",
    "No runtime, economic, sidecar, network, ADR, or CDL activation occurred.",
    "No Fix46 edge is authority-bearing or promoted to canonical state.",
]


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _pretty_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix46_json_object_required:{path}")
    return payload


def _node_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id") or node.get("node_id") or node.get("id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix46_node_missing_id")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    value = edge.get("source_candidate_id") or edge.get("source") or edge.get("from")
    return value if isinstance(value, str) else ""


def _edge_target(edge: dict[str, Any]) -> str:
    value = edge.get("target_candidate_id") or edge.get("target") or edge.get("to")
    return value if isinstance(value, str) else ""


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type") or edge.get("type")
    return value if isinstance(value, str) and value else "UNKNOWN"


def _path_key(path: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", path).strip("_").lower()


def _repo_file_node_id(path: str) -> str:
    return f"repo:file:{hashlib.sha256(path.encode('utf-8')).hexdigest()[:16]}:{_path_key(path)}"


def _repo_prefix(path: str) -> str:
    if path.startswith("docs/specs/"):
        return "docs/specs"
    if path.startswith("tools/"):
        return "tools"
    if path.startswith("ilc_core/"):
        return "ilc_core"
    if path.startswith("tests/"):
        return "tests"
    return path.split("/", 1)[0] if "/" in path else path


def _edge_id(source: str, edge_type: str, target: str, repo_path: str, evidence_hash: str) -> str:
    return "edge:fix46:" + hashlib.sha256(
        _canonical_json(
            {
                "edge_type": edge_type,
                "evidence_hash": evidence_hash,
                "origin_repo_path": repo_path,
                "source": source,
                "target": target,
            }
        ).encode("utf-8")
    ).hexdigest()[:32]


def _existing_edge_keys(edges: list[dict[str, Any]]) -> set[tuple[str, str, str]]:
    return {(_edge_source(edge), _edge_type(edge), _edge_target(edge)) for edge in edges}


def _node_indexes(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    node_ids = {_node_id(node) for node in nodes}
    path_to_node: dict[str, str] = {}
    cdl: dict[str, list[str]] = defaultdict(list)
    adr: dict[str, list[str]] = defaultdict(list)

    for node in nodes:
        node_id = _node_id(node)
        for key in ("source_path", "label"):
            value = node.get(key)
            if isinstance(value, str) and value and "/" in value:
                path_to_node.setdefault(value.rstrip("/"), node_id)
        if node_id.startswith("cdl:"):
            rest = node_id.split(":", 1)[1].lower()
            number = re.match(r"0*(\d{1,3})(?:_|$)", rest)
            version = re.match(r"(v\d+)(?:_|$)", rest)
            if number:
                cdl[number.group(1).zfill(3)].append(node_id)
            if version:
                cdl[version.group(1)].append(node_id)
        if node_id.startswith("adr:"):
            rest = node_id.split(":", 1)[1].lower()
            number = re.match(r"0*(\d{1,4})(?:_|$)", rest)
            if number:
                adr[number.group(1).zfill(4)].append(node_id)
    return {
        "adr": {key: sorted(value) for key, value in adr.items()},
        "cdl": {key: sorted(value) for key, value in cdl.items()},
        "node_ids": node_ids,
        "path_to_node": path_to_node,
    }


def _resolve_numbered(kind: str, key: str, indexes: dict[str, Any]) -> tuple[str | None, str, list[str]]:
    exact = f"{kind}:{key}"
    node_ids: set[str] = indexes["node_ids"]
    if exact in node_ids:
        return exact, "exact_id", [exact]
    candidates = indexes[kind].get(key, [])
    if len(candidates) == 1:
        return candidates[0], "unique_numeric_or_version_match", candidates
    if not candidates:
        return None, f"no_existing_{kind}_target", []
    return None, f"multiple_existing_{kind}_targets", candidates


def _read_source(repo_path: str) -> tuple[str, str, list[str]]:
    path = REPO_ROOT / repo_path
    if path.is_dir():
        return "directory_target", "", []
    if not path.exists():
        return "missing_source", "", []
    if not path.is_file():
        return "not_regular_file", "", []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "read_error", "", []
    return "read_text", text, text.splitlines()


def _line_evidence(repo_path: str, line_number: int, line: str, evidence_type: str) -> dict[str, Any]:
    text = line.strip()
    if len(text) > 240:
        text = text[:237] + "..."
    return {
        "evidence_hash": _sha256_text(f"{repo_path}:{line_number}:{text}"),
        "evidence_text": text,
        "evidence_type": evidence_type,
        "source_line": line_number,
        "source_path": repo_path,
    }


def _extract_authority_refs(repo_path: str, lines: list[str], indexes: dict[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int]] = set()
    scan_pairs = [(0, repo_path)] + list(enumerate(lines, start=1))
    for line_number, line in scan_pairs:
        for match in re.finditer(r"\bCDL[-_\s]0*(v\d+|\d{1,3})\b", line, re.IGNORECASE):
            token = match.group(1).lower()
            key = token if token.startswith("v") else token.zfill(3)
            target, resolution, candidates = _resolve_numbered("cdl", key, indexes)
            dedupe = ("cdl", key, line_number)
            if dedupe in seen:
                continue
            seen.add(dedupe)
            refs.append(
                {
                    "kind": "cdl",
                    "key": key,
                    "target": target,
                    "resolution": resolution,
                    "candidates": candidates,
                    "evidence": _line_evidence(repo_path, line_number, line, "explicit_cdl_reference"),
                }
            )
        for match in re.finditer(r"\bADR[-_\s]0*(\d{1,4})\b", line, re.IGNORECASE):
            key = match.group(1).zfill(4)
            target, resolution, candidates = _resolve_numbered("adr", key, indexes)
            dedupe = ("adr", key, line_number)
            if dedupe in seen:
                continue
            seen.add(dedupe)
            refs.append(
                {
                    "kind": "adr",
                    "key": key,
                    "target": target,
                    "resolution": resolution,
                    "candidates": candidates,
                    "evidence": _line_evidence(repo_path, line_number, line, "explicit_adr_reference"),
                }
            )
        for match in re.finditer(r"\b(policy|artifact):[a-zA-Z0-9_:\-.]+", line):
            node_id = match.group(0).rstrip(".,;)`]")
            dedupe = ("node", node_id, line_number)
            if dedupe in seen:
                continue
            seen.add(dedupe)
            refs.append(
                {
                    "kind": node_id.split(":", 1)[0],
                    "key": node_id,
                    "target": node_id if node_id in indexes["node_ids"] else None,
                    "resolution": "exact_id" if node_id in indexes["node_ids"] else "no_existing_exact_node_target",
                    "candidates": [node_id] if node_id in indexes["node_ids"] else [],
                    "evidence": _line_evidence(repo_path, line_number, line, "explicit_node_id_reference"),
                }
            )
    return refs


def _module_to_paths(module: str) -> list[str]:
    parts = module.split(".")
    paths: list[str] = []
    while len(parts) >= 2:
        rel = "/".join(parts)
        paths.append(f"{rel}.py")
        paths.append(f"{rel}/__init__.py")
        parts = parts[:-1]
    return paths


def _extract_imports(repo_path: str, text: str, indexes: dict[str, Any]) -> list[dict[str, Any]]:
    if not repo_path.endswith(".py") or not text.strip():
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    imports: list[dict[str, Any]] = []
    seen: set[str] = set()
    for node in ast.walk(tree):
        names: list[str] = []
        line_number = getattr(node, "lineno", 0) or 0
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
            for alias in node.names:
                if alias.name != "*":
                    names.append(f"{node.module}.{alias.name}")
        for name in names:
            if not name.startswith(("ilc_core", "tools", "tests")):
                continue
            for path in _module_to_paths(name):
                target = indexes["path_to_node"].get(path)
                if target and target not in seen:
                    seen.add(target)
                    imports.append(
                        {
                            "module": name,
                            "target": target,
                            "target_path": path,
                            "evidence": _line_evidence(
                                repo_path,
                                line_number,
                                f"import {name}",
                                "python_import_reference",
                            ),
                        }
                    )
                    break
    return imports


def _edge_type_for_authority(repo_path: str) -> str:
    if repo_path.startswith("ilc_core/"):
        return "IMPLEMENTS"
    return "REFERENCES_AUTHORITY"


def _is_test_like(repo_path: str) -> bool:
    name = Path(repo_path).name
    return (
        repo_path.startswith("tests/")
        or "/testbed/" in repo_path
        or name.startswith(("test_", "check_"))
        or name.endswith("_test.py")
    )


def _new_edge(
    source: str,
    target: str,
    edge_type: str,
    repo_path: str,
    rationale: str,
    evidence: list[dict[str, Any]],
    confidence: float,
) -> dict[str, Any]:
    evidence_hash = _sha256_text(_canonical_json(evidence))
    return {
        "annotation_method": "fix46_manual_semantic_batch_read",
        "candidate_status": "fix46_support_only",
        "confidence": confidence,
        "edge_id": _edge_id(source, edge_type, target, repo_path, evidence_hash),
        "edge_type": edge_type,
        "evidence": evidence,
        "origin_repo_path": repo_path,
        "rationale": rationale,
        "review_status": "candidate_only_not_authority_promotion",
        "source": source,
        "source_phase": PHASE,
        "target": target,
    }


def _maybe_add_edge(
    *,
    source: str,
    target: str,
    edge_type: str,
    repo_path: str,
    rationale: str,
    evidence: list[dict[str, Any]],
    confidence: float,
    existing_keys: set[tuple[str, str, str]],
    new_keys: set[tuple[str, str, str]],
) -> tuple[dict[str, Any] | None, str]:
    key = (source, edge_type, target)
    if key in existing_keys or key in new_keys:
        return None, "skipped_duplicate"
    edge = _new_edge(source, target, edge_type, repo_path, rationale, evidence, confidence)
    new_keys.add(key)
    return edge, "added_edge"


def _graph_intake_node(path: str) -> dict[str, Any]:
    return {
        "candidate_id": _repo_file_node_id(path),
        "candidate_status": "fix46_support_only",
        "category": "fix46_support_document",
        "confidence": 0.8,
        "inclusion_status": "support_only",
        "label": path,
        "node_kind": "repo_support_doc_node",
        "phase": PHASE,
        "public_path": "blocked",
        "rationale": "Fix46 graph intake record for a newly produced support artifact.",
        "sensitivity": "NON-SENSITIVE",
        "signature_status": "unsigned_candidate",
        "source_path": path,
        "source_phase": PHASE,
        "tier": "public_release_candidate_material",
    }


def _process_entry(
    entry: dict[str, Any],
    *,
    batch_id: str,
    batch_index: int,
    indexes: dict[str, Any],
    existing_keys: set[tuple[str, str, str]],
    new_keys: set[tuple[str, str, str]],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
    source = str(entry.get("node_id", ""))
    repo_path = str(entry.get("repo_path", ""))
    disposition, text, lines = _read_source(repo_path)
    refs = _extract_authority_refs(repo_path, lines, indexes) if disposition == "read_text" else []
    imports = _extract_imports(repo_path, text, indexes) if disposition == "read_text" else []
    edges: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    unresolved_refs = [ref for ref in refs if ref["target"] is None]

    for ref in refs:
        if ref["target"] is None:
            continue
        edge_type = _edge_type_for_authority(repo_path)
        edge, decision = _maybe_add_edge(
            source=source,
            target=ref["target"],
            edge_type=edge_type,
            repo_path=repo_path,
            rationale=f"Direct-read explicit {ref['kind'].upper()} reference resolved to existing target {ref['target']}.",
            evidence=[ref["evidence"]],
            confidence=0.78 if edge_type == "REFERENCES_AUTHORITY" else 0.72,
            existing_keys=existing_keys,
            new_keys=new_keys,
        )
        decisions.append({"decision": decision, "edge_type": edge_type, "target": ref["target"], "reason": ref["resolution"]})
        if edge:
            edges.append(edge)

    for item in imports:
        target = item["target"]
        if target == source:
            continue
        edge_type = "TESTS" if _is_test_like(repo_path) else "IMPORTS_MODULE"
        edge, decision = _maybe_add_edge(
            source=source,
            target=target,
            edge_type=edge_type,
            repo_path=repo_path,
            rationale=f"Direct-read Python import `{item['module']}` resolved to existing graph node {target}.",
            evidence=[item["evidence"]],
            confidence=0.7 if edge_type == "TESTS" else 0.64,
            existing_keys=existing_keys,
            new_keys=new_keys,
        )
        decisions.append({"decision": decision, "edge_type": edge_type, "target": target, "reason": "python_import_resolved"})
        if edge:
            edges.append(edge)

    support_only = (
        source.startswith("target:")
        or repo_path.startswith("tests/fixtures/")
        or disposition == "directory_target"
    )
    if support_only:
        edge, decision = _maybe_add_edge(
            source=source,
            target=SOURCE_TREE_TARGET,
            edge_type="SOURCE_TREE_MEMBER",
            repo_path=repo_path,
            rationale="Direct-read support object classified as source-tree member only; not authority promotion.",
            evidence=[
                _line_evidence(
                    repo_path,
                    0,
                    repo_path,
                    "source_tree_membership_support_classification",
                )
            ],
            confidence=0.68,
            existing_keys=existing_keys,
            new_keys=new_keys,
        )
        decisions.append(
            {
                "decision": decision,
                "edge_type": "SOURCE_TREE_MEMBER",
                "target": SOURCE_TREE_TARGET,
                "reason": "support_object_source_tree_membership",
            }
        )
        if edge:
            edges.append(edge)

    residual: dict[str, Any] | None = None
    if not edges:
        residual = {
            "batch_id": batch_id,
            "batch_index": batch_index,
            "candidate_authority_refs": [
                {
                    "candidates": ref["candidates"],
                    "key": ref["key"],
                    "kind": ref["kind"],
                    "resolution": ref["resolution"],
                }
                for ref in unresolved_refs
            ],
            "current_edge_types": entry.get("current_edge_types", []),
            "node_id": source,
            "prior_decision": entry.get("decision"),
            "reason": "no_unique_evidence_backed_edge_added",
            "repo_path": repo_path,
            "source_read_disposition": disposition,
        }

    row = {
        "added_edge_ids": [edge["edge_id"] for edge in edges],
        "batch_id": batch_id,
        "batch_index": batch_index,
        "decisions": decisions or [{"decision": "deferred_residual_review", "reason": "no_edge_added"}],
        "explicit_authority_reference_count": len(refs),
        "import_reference_count": len(imports),
        "node_id": source,
        "prior_decision": entry.get("decision"),
        "repo_path": repo_path,
        "source_read_disposition": disposition,
        "source_sha256": _sha256_text(text) if disposition == "read_text" else None,
    }
    return row, edges, residual


def _report_markdown(ledger: dict[str, Any], residual_queue: dict[str, Any], candidate: dict[str, Any]) -> str:
    lines = [
        "# Fix46 Manual Semantic Annotation Report",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: fix46_manual_semantic_annotation_report_support_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Research-only support-edge annotation report; no public RC or graph publication is authorized. -->",
        "",
        "## Summary",
        "",
        f"- Queue entries considered: `{ledger['queue_entry_count']}`",
        f"- Batch count: `{ledger['batch_count']}`",
        f"- Candidate edges added: `{sum(ledger['edge_type_counts_added'].values())}`",
        f"- Residual Fix47 entries: `{residual_queue['entry_count']}`",
        f"- Candidate nodes: `{len(candidate['nodes'])}`",
        f"- Candidate edges: `{len(candidate['edges'])}`",
        "",
        "## Edge Type Counts Added",
        "",
        "| Edge type | Count |",
        "|---|---:|",
    ]
    for key, value in ledger["edge_type_counts_added"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Source Read Dispositions", "", "| Disposition | Count |", "|---|---:|"])
    for key, value in ledger["source_read_disposition_counts"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Non-Claims", ""])
    for claim in NON_CLAIMS:
        lines.append(f"- {claim}")
    return "\n".join(lines) + "\n"


def _walkthrough(ledger: dict[str, Any], residual_queue: dict[str, Any], candidate: dict[str, Any]) -> str:
    return f"""# Phase 1545p-Fix46: Manual Semantic Annotation Walkthrough

## Status

COMPLETE.

Fix46 consumed the Fix45 manual semantic queue in deterministic batches of ten
entries, direct-read available local files, and added only evidence-backed
candidate support edges. It did not sign, publish, promote, activate, or mutate
canonical graph authority.

## Batch Summary

- Queue entries considered: `{ledger['queue_entry_count']}`
- Batch count: `{ledger['batch_count']}`
- Non-tail batch size: `{BATCH_SIZE}`
- Source-read dispositions: `{json.dumps(ledger['source_read_disposition_counts'], sort_keys=True, allow_nan=False)}`

## Annotation Results

- Candidate edges added: `{sum(ledger['edge_type_counts_added'].values())}`
- Edge type counts: `{json.dumps(ledger['edge_type_counts_added'], sort_keys=True, allow_nan=False)}`
- Residual Fix47 entries: `{residual_queue['entry_count']}`
- Graph-intake support nodes: `{len(ledger['graph_intake_nodes'])}`

## Enriched Candidate

- Output: `out/atlas_research/genesis_atlas_enriched_candidate_fix46.json`
- Nodes: `{len(candidate['nodes'])}`
- Edges: `{len(candidate['edges'])}`
- New candidate status: `{candidate['candidate_status']}`

## Boundary

Fix46 did not add `GOVERNS` edges and did not use generated `out/` artifacts as
authority targets. Every Fix46 edge remains candidate-only and unsigned.

## Tokens

{chr(10).join(f'- `{token}`' for token in TOKENS)}

## Non-Claims

{chr(10).join(f'- {claim}' for claim in NON_CLAIMS)}
"""


def _graph_intake_edge(node_id: str, path: str) -> dict[str, Any]:
    return _new_edge(
        node_id,
        SOURCE_TREE_TARGET,
        "SOURCE_TREE_MEMBER",
        path,
        "New Fix46/Fix47 support artifact belongs to the candidate Genesis-governed source tree.",
        [_line_evidence(path, 0, path, "fix46_graph_intake_support_doc")],
        0.8,
    )


def run(
    *,
    candidate_in: Path = CANDIDATE_IN,
    queue_in: Path = QUEUE_IN,
    candidate_out: Path = CANDIDATE_OUT,
    ledger_out: Path = LEDGER_OUT,
    report_out: Path = REPORT_OUT,
    residual_queue_out: Path = RESIDUAL_QUEUE_OUT,
    walkthrough_out: Path = WALKTHROUGH_OUT,
) -> dict[str, Any]:
    source_candidate = _load_json(candidate_in)
    queue = _load_json(queue_in)
    entries = queue.get("entries")
    if not isinstance(entries, list) or queue.get("entry_count") != 382:
        raise ValueError("fix46_queue_entry_count_mismatch")

    nodes: list[dict[str, Any]] = list(source_candidate["nodes"])
    edges: list[dict[str, Any]] = list(source_candidate["edges"])
    indexes = _node_indexes(nodes)
    existing_keys = _existing_edge_keys(edges)
    new_keys: set[tuple[str, str, str]] = set()
    rows: list[dict[str, Any]] = []
    residual_entries: list[dict[str, Any]] = []
    new_edges: list[dict[str, Any]] = []

    for offset, entry in enumerate(entries):
        batch_number = offset // BATCH_SIZE + 1
        batch_id = f"fix46_batch_{batch_number:03d}"
        batch_index = offset % BATCH_SIZE + 1
        row, entry_edges, residual = _process_entry(
            entry,
            batch_id=batch_id,
            batch_index=batch_index,
            indexes=indexes,
            existing_keys=existing_keys,
            new_keys=new_keys,
        )
        rows.append(row)
        new_edges.extend(entry_edges)
        if residual:
            residual_entries.append(residual)

    graph_intake_nodes = [_graph_intake_node(path) for path in NEW_DOC_PATHS]
    for node in graph_intake_nodes:
        node_id = _node_id(node)
        if node_id not in indexes["node_ids"]:
            nodes.append(node)
            indexes["node_ids"].add(node_id)
    for node in graph_intake_nodes:
        edge = _graph_intake_edge(_node_id(node), str(node["source_path"]))
        key = (_edge_source(edge), _edge_type(edge), _edge_target(edge))
        if key not in existing_keys and key not in new_keys:
            new_keys.add(key)
            new_edges.append(edge)

    batch_counts = Counter(row["batch_id"] for row in rows)
    ledger = {
        "batch_count": len(batch_counts),
        "batch_counts": dict(sorted(batch_counts.items())),
        "decision_counts": dict(Counter(decision["decision"] for row in rows for decision in row["decisions"]).most_common()),
        "edge_type_counts_added": dict(Counter(edge["edge_type"] for edge in new_edges).most_common()),
        "graph_intake_nodes": graph_intake_nodes,
        "non_claims": NON_CLAIMS,
        "phase": PHASE,
        "queue_entry_count": len(rows),
        "repo_prefix_counts": dict(Counter(_repo_prefix(row["repo_path"]) for row in rows).most_common()),
        "rows": rows,
        "schema_version": SCHEMA_VERSION,
        "source_read_disposition_counts": dict(Counter(row["source_read_disposition"] for row in rows).most_common()),
        "status": "PASS",
    }
    residual_queue = {
        "entry_count": len(residual_entries),
        "entries": residual_entries,
        "non_claims": NON_CLAIMS,
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
    }

    candidate = dict(source_candidate)
    candidate["nodes"] = nodes
    candidate["edges"] = edges + new_edges
    candidate["candidate_status"] = "unsigned_support_only_not_canonical_fix46_manual_semantic_candidate"
    candidate["phase"] = PHASE
    candidate["fix46_merge_summary"] = {
        "added_candidate_edges": len(new_edges),
        "added_candidate_nodes": len(graph_intake_nodes),
        "batch_count": len(batch_counts),
        "edge_type_counts_added": ledger["edge_type_counts_added"],
        "input_candidate": "out/atlas_research/genesis_atlas_enriched_candidate_fix45.json",
        "input_queue": "docs/specs/ilc_fix46_manual_semantic_annotation_queue_v0.1.json",
        "phase": PHASE,
        "queue_entry_count": len(rows),
        "residual_queue_count": len(residual_entries),
    }
    candidate.pop("candidate_digest", None)
    candidate["non_claims"] = NON_CLAIMS
    candidate["candidate_digest"] = "fix46_candidate:" + _sha256_text(_canonical_json(candidate))

    _atomic_write(ledger_out, _pretty_json(ledger))
    _atomic_write(residual_queue_out, _pretty_json(residual_queue))
    _atomic_write(candidate_out, _pretty_json(candidate))
    _atomic_write(report_out, _report_markdown(ledger, residual_queue, candidate))
    _atomic_write(walkthrough_out, _walkthrough(ledger, residual_queue, candidate))

    return {
        "candidate_edge_count": len(candidate["edges"]),
        "candidate_node_count": len(candidate["nodes"]),
        "edge_type_counts_added": ledger["edge_type_counts_added"],
        "residual_queue_entry_count": residual_queue["entry_count"],
        "status": "PASS",
        "tokens": TOKENS,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Fix46 manual semantic annotation.")
    parser.add_argument("--candidate", type=Path, default=CANDIDATE_IN)
    parser.add_argument("--queue", type=Path, default=QUEUE_IN)
    args = parser.parse_args()
    payload = run(candidate_in=args.candidate, queue_in=args.queue)
    print(_canonical_json(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
