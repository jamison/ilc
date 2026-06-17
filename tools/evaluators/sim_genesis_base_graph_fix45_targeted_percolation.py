#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Run Phase 1545p-Fix45 targeted percolation annotation tranche 1.

PUBLIC_RC_EXCLUDE: genesis_base_graph_fix45_targeted_percolation_research_only
PUBLIC_RC_EXCLUDE_REASON: Unsigned candidate support-edge annotation over a
research Atlas candidate; no Genesis signing, canonical graph mutation, public
graph publication, public RC activation, runtime activation, minting,
settlement, or ADR/CDL mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE = "1545p-Fix45"
SCHEMA_VERSION = "genesis_base_graph_fix45_targeted_percolation.v0.1"

CANDIDATE_IN = REPO_ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json"
QUEUE_IN = REPO_ROOT / "out/genesis_base_graph_fix44_target_queue.json"
CANDIDATE_OUT = REPO_ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix45.json"
ANALYSIS_JSON_OUT = REPO_ROOT / "out/genesis_base_graph_fix45_target_queue_analysis.json"
ANALYSIS_MD_OUT = REPO_ROOT / "docs/specs/ilc_fix45_target_queue_analysis_v0.1.md"
LEDGER_OUT = REPO_ROOT / "docs/specs/ilc_fix45_algorithmic_percolation_ledger_v0.1.json"
REPORT_OUT = REPO_ROOT / "docs/specs/ilc_fix45_algorithmic_percolation_report_v0.1.md"
MANUAL_QUEUE_OUT = REPO_ROOT / "docs/specs/ilc_fix46_manual_semantic_annotation_queue_v0.1.json"
WALKTHROUGH_OUT = REPO_ROOT / "docs/phases/phase_1545p_fix45_targeted_percolation_annotation_walkthrough.md"

SOURCE_TREE_TARGET = "artifact:genesis_source_tree_manifest_candidate_1545p_fix38"
FIX41A_SHA256 = "3bcf8cdf248ea44248e72dce0c8209c92302826399b42524235cf8ee59936e52"

NEW_DOC_PATHS = [
    "docs/specs/ilc_fix45_target_queue_analysis_v0.1.md",
    "docs/specs/ilc_fix45_algorithmic_percolation_ledger_v0.1.json",
    "docs/specs/ilc_fix45_algorithmic_percolation_report_v0.1.md",
    "docs/specs/ilc_fix46_manual_semantic_annotation_queue_v0.1.json",
]

TOKENS = [
    "fix45_target_queue_algorithmic_annotation_complete",
    "fix45_enriched_candidate_produced",
    "fix45_manual_semantic_tranche_deferred",
    "fix45_complete",
    "public_path_remains_blocked_phase_1545p_fix45",
]

NON_CLAIMS = [
    "No Genesis signing occurred.",
    "No signed genesis_base_graph_v0.4.json artifact was produced.",
    "No canonical Atlas mutation occurred.",
    "No public graph publication occurred.",
    "No public repository push occurred.",
    "No public RC activation occurred.",
    "No runtime, economic, sidecar, network, ADR, or CDL activation occurred.",
    "No Fix45 edge is authority-bearing or promoted to canonical state.",
]


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _pretty_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        raise ValueError(f"fix45_json_object_required:{path}")
    return payload


def _node_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id") or node.get("node_id") or node.get("id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix45_node_missing_id")
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


def _fix45_edge_id(source: str, edge_type: str, target: str, rule: str) -> str:
    return "edge:fix45:" + hashlib.sha256(
        _canonical_json({"edge_type": edge_type, "rule": rule, "source": source, "target": target}).encode("utf-8")
    ).hexdigest()[:32]


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


def _extract_cdl_key(path: str) -> str | None:
    lowered = path.lower()
    match = re.search(r"cdl[_-]0*(v\d+|\d{1,3})", lowered)
    if not match:
        return None
    token = match.group(1)
    if token.startswith("v"):
        return token
    return token.zfill(3)


def _extract_adr_key(path: str) -> str | None:
    lowered = path.lower()
    match = re.search(r"adr[_-]0*(\d{1,4})", lowered)
    if not match:
        return None
    return match.group(1).zfill(4)


def _semantic_indexes(nodes: list[dict[str, Any]]) -> tuple[dict[str, list[str]], dict[str, list[str]], set[str]]:
    cdl: dict[str, list[str]] = defaultdict(list)
    adr: dict[str, list[str]] = defaultdict(list)
    node_ids = {_node_id(node) for node in nodes}
    for node_id in sorted(node_ids):
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
    return {k: sorted(v) for k, v in cdl.items()}, {k: sorted(v) for k, v in adr.items()}, node_ids


def _resolve_cdl_target(key: str, cdl_index: dict[str, list[str]], node_ids: set[str]) -> tuple[str | None, str]:
    exact = f"cdl:{key}" if not key.startswith("v") else f"cdl:{key}"
    if exact in node_ids:
        return exact, "exact_id"
    candidates = cdl_index.get(key, [])
    if len(candidates) == 1:
        return candidates[0], "unique_numeric_or_version_match"
    if not candidates:
        return None, "no_existing_cdl_target"
    return None, "multiple_existing_cdl_targets"


def _resolve_adr_target(key: str, adr_index: dict[str, list[str]], node_ids: set[str]) -> tuple[str | None, str]:
    exact = f"adr:{key}"
    if exact in node_ids:
        return exact, "exact_id"
    candidates = adr_index.get(key, [])
    if len(candidates) == 1:
        return candidates[0], "unique_numeric_match"
    if not candidates:
        return None, "no_existing_adr_target"
    return None, "multiple_existing_adr_targets"


def _new_edge(source: str, target: str, edge_type: str, repo_path: str, rule: str, rationale: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix45_algorithmic_percolation",
        "candidate_status": "fix45_support_only",
        "confidence": 0.82 if edge_type == "SOURCE_TREE_MEMBER" else 0.74,
        "edge_id": _fix45_edge_id(source, edge_type, target, rule),
        "edge_type": edge_type,
        "origin_repo_path": repo_path,
        "rationale": rationale,
        "review_status": "candidate_only_not_authority_promotion",
        "source": source,
        "source_phase": PHASE,
        "target": target,
    }


def _existing_edge_keys(edges: list[dict[str, Any]]) -> set[tuple[str, str, str]]:
    return {(_edge_source(edge), _edge_type(edge), _edge_target(edge)) for edge in edges}


def _queue_analysis(queue_entries: list[dict[str, Any]]) -> dict[str, Any]:
    prefix_counts = Counter(_repo_prefix(str(entry.get("repo_path", ""))) for entry in queue_entries)
    edge_type_counts = Counter(edge_type for entry in queue_entries for edge_type in entry.get("current_edge_types", []))
    degree_counts = Counter(int(entry.get("in_degree", 0)) + int(entry.get("out_degree", 0)) for entry in queue_entries)
    already_semantic = sum(
        1
        for entry in queue_entries
        if set(entry.get("current_edge_types", []))
        & {"REFERENCES_AUTHORITY", "IMPLEMENTS", "SOURCE_TREE_MEMBER", "CLASSIFIED_BY"}
    )
    return {
        "already_semantic_or_membership_count": already_semantic,
        "adr_filename_hint_count": sum(1 for entry in queue_entries if _extract_adr_key(str(entry.get("repo_path", "")))),
        "cdl_filename_hint_count": sum(1 for entry in queue_entries if _extract_cdl_key(str(entry.get("repo_path", "")))),
        "degree_counts": dict(sorted(degree_counts.items())),
        "edge_type_counts": dict(edge_type_counts.most_common()),
        "excluded_authority_targets": ["repo:group:out", "out/", "out/viz_exports/", "out/monitoring/"],
        "init_py_count": sum(1 for entry in queue_entries if str(entry.get("repo_path", "")).endswith("/__init__.py")),
        "node_prefix_counts": dict(Counter(str(entry.get("node_id", "")).split(":", 1)[0] for entry in queue_entries).most_common()),
        "repo_prefix_counts": dict(prefix_counts.most_common()),
        "target_node_count": sum(1 for entry in queue_entries if str(entry.get("node_id", "")).startswith("target:")),
        "tools_contains_file_only_count": sum(
            1
            for entry in queue_entries
            if str(entry.get("repo_path", "")).startswith("tools/")
            and set(entry.get("current_edge_types", [])) == {"CONTAINS_FILE"}
        ),
        "total_queue_count": len(queue_entries),
    }


def _classify_entry(
    entry: dict[str, Any],
    *,
    cdl_index: dict[str, list[str]],
    adr_index: dict[str, list[str]],
    node_ids: set[str],
    existing_keys: set[tuple[str, str, str]],
    new_keys: set[tuple[str, str, str]],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    source = str(entry.get("node_id", ""))
    repo_path = str(entry.get("repo_path", ""))
    current_edge_types = set(entry.get("current_edge_types", []))

    base = {
        "current_edge_types": sorted(current_edge_types),
        "node_id": source,
        "repo_path": repo_path,
    }

    if source.startswith("target:"):
        return {
            **base,
            "decision": "deferred_manual_semantic_review",
            "reason": "target_nodes_have_no_deterministic_authority_rule_in_fix45",
        }, None

    if repo_path.startswith("tests/fixtures/"):
        return {
            **base,
            "decision": "deferred_low_value_fixture",
            "reason": "fixture_file_low_semantic_value_for_algorithmic_authority_targeting",
        }, None

    if "REFERENCES_AUTHORITY" in current_edge_types or "IMPLEMENTS" in current_edge_types or "CLASSIFIED_BY" in current_edge_types:
        return {
            **base,
            "decision": "deferred_existing_semantic_edge_present",
            "reason": "entry_already_has_semantic_or_classification_edge",
        }, None

    cdl_key = _extract_cdl_key(repo_path)
    if cdl_key:
        target, resolution = _resolve_cdl_target(cdl_key, cdl_index, node_ids)
        if target is None:
            return {
                **base,
                "decision": "unresolved_no_unique_target",
                "pattern": f"cdl:{cdl_key}",
                "reason": resolution,
            }, None
        key = (source, "REFERENCES_AUTHORITY", target)
        if key in existing_keys or key in new_keys:
            return {
                **base,
                "decision": "skipped_duplicate",
                "target": target,
                "edge_type": "REFERENCES_AUTHORITY",
                "reason": "exact_source_type_target_edge_already_exists",
            }, None
        edge = _new_edge(
            source,
            target,
            "REFERENCES_AUTHORITY",
            repo_path,
            f"cdl_filename_rule:{cdl_key}",
            f"Filename contains CDL-{cdl_key}; resolved to existing semantic target {target}.",
        )
        return {**base, "decision": "added_edge", "edge_id": edge["edge_id"], "edge_type": "REFERENCES_AUTHORITY", "target": target}, edge

    adr_key = _extract_adr_key(repo_path)
    if adr_key:
        target, resolution = _resolve_adr_target(adr_key, adr_index, node_ids)
        if target is None:
            return {
                **base,
                "decision": "unresolved_no_unique_target",
                "pattern": f"adr:{adr_key}",
                "reason": resolution,
            }, None
        key = (source, "REFERENCES_AUTHORITY", target)
        if key in existing_keys or key in new_keys:
            return {
                **base,
                "decision": "skipped_duplicate",
                "target": target,
                "edge_type": "REFERENCES_AUTHORITY",
                "reason": "exact_source_type_target_edge_already_exists",
            }, None
        edge = _new_edge(
            source,
            target,
            "REFERENCES_AUTHORITY",
            repo_path,
            f"adr_filename_rule:{adr_key}",
            f"Filename contains ADR-{adr_key}; resolved to existing semantic target {target}.",
        )
        return {**base, "decision": "added_edge", "edge_id": edge["edge_id"], "edge_type": "REFERENCES_AUTHORITY", "target": target}, edge

    if repo_path.endswith("/__init__.py"):
        key = (source, "SOURCE_TREE_MEMBER", SOURCE_TREE_TARGET)
        if key in existing_keys or key in new_keys:
            return {
                **base,
                "decision": "skipped_duplicate",
                "target": SOURCE_TREE_TARGET,
                "edge_type": "SOURCE_TREE_MEMBER",
                "reason": "exact_source_tree_member_edge_already_exists",
            }, None
        edge = _new_edge(
            source,
            SOURCE_TREE_TARGET,
            "SOURCE_TREE_MEMBER",
            repo_path,
            "package_membership_rule",
            "Package initializer belongs to the candidate Genesis-governed source tree.",
        )
        return {**base, "decision": "added_edge", "edge_id": edge["edge_id"], "edge_type": "SOURCE_TREE_MEMBER", "target": SOURCE_TREE_TARGET}, edge

    if repo_path.startswith("tools/") and current_edge_types == {"CONTAINS_FILE"}:
        key = (source, "SOURCE_TREE_MEMBER", SOURCE_TREE_TARGET)
        if key in existing_keys or key in new_keys:
            return {
                **base,
                "decision": "skipped_duplicate",
                "target": SOURCE_TREE_TARGET,
                "edge_type": "SOURCE_TREE_MEMBER",
                "reason": "exact_source_tree_member_edge_already_exists",
            }, None
        edge = _new_edge(
            source,
            SOURCE_TREE_TARGET,
            "SOURCE_TREE_MEMBER",
            repo_path,
            "tools_containment_only_rule",
            "Tools file has only containment evidence; Fix45 adds source-tree membership only, not authority.",
        )
        return {**base, "decision": "added_edge", "edge_id": edge["edge_id"], "edge_type": "SOURCE_TREE_MEMBER", "target": SOURCE_TREE_TARGET}, edge

    return {
        **base,
        "decision": "deferred_manual_semantic_review",
        "reason": "no_deterministic_filename_or_membership_rule_matched",
    }, None


def _graph_intake_node(path: str) -> dict[str, Any]:
    return {
        "candidate_id": _repo_file_node_id(path),
        "candidate_status": "fix45_support_only",
        "category": "fix45_support_document",
        "confidence": 0.8,
        "inclusion_status": "support_only",
        "label": path,
        "node_kind": "repo_support_doc_node",
        "phase": PHASE,
        "public_path": "blocked",
        "rationale": "Fix45 graph intake record for a newly produced support artifact.",
        "sensitivity": "NON-SENSITIVE",
        "signature_status": "unsigned_candidate",
        "source_path": path,
        "source_phase": PHASE,
        "tier": "public_release_candidate_material",
    }


def _graph_intake_edge(node_id: str, path: str) -> dict[str, Any]:
    return _new_edge(
        node_id,
        SOURCE_TREE_TARGET,
        "SOURCE_TREE_MEMBER",
        path,
        "fix45_graph_intake_support_doc",
        "New Fix45 support artifact belongs to the candidate Genesis-governed source tree.",
    )


def _analysis_markdown(analysis: dict[str, Any]) -> str:
    lines = [
        "# Fix45 Target Queue Analysis",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: fix45_target_queue_analysis_support_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Research-only target queue analysis; no public RC or graph publication is authorized. -->",
        "",
        "## Summary",
        "",
        f"- Total queue entries: `{analysis['total_queue_count']}`",
        f"- CDL filename hints: `{analysis['cdl_filename_hint_count']}`",
        f"- ADR filename hints: `{analysis['adr_filename_hint_count']}`",
        f"- `__init__.py` entries: `{analysis['init_py_count']}`",
        f"- `target:*` entries: `{analysis['target_node_count']}`",
        f"- Tools containment-only entries: `{analysis['tools_contains_file_only_count']}`",
        f"- Entries already carrying semantic or classification edges: `{analysis['already_semantic_or_membership_count']}`",
        "",
        "## Repo Prefix Counts",
        "",
        "| Prefix | Count |",
        "|---|---:|",
    ]
    for key, value in analysis["repo_prefix_counts"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Edge Type Counts In Queue",
            "",
            "| Edge type | Count |",
            "|---|---:|",
        ]
    )
    for key, value in analysis["edge_type_counts"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Excluded Authority Targets",
            "",
            "`repo:group:out`, generated `out/` files, view exports, and monitoring artifacts are excluded as authority targets.",
        ]
    )
    return "\n".join(lines) + "\n"


def _manual_queue(rows: list[dict[str, Any]]) -> dict[str, Any]:
    entries = [
        row
        for row in rows
        if row["decision"]
        in {
            "deferred_manual_semantic_review",
            "deferred_low_value_fixture",
            "unresolved_no_unique_target",
        }
    ]
    return {
        "entry_count": len(entries),
        "entries": entries,
        "non_claims": NON_CLAIMS,
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
    }


def _ledger_payload(rows: list[dict[str, Any]], graph_intake_nodes: list[dict[str, Any]], new_edges: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "decision_counts": dict(Counter(row["decision"] for row in rows).most_common()),
        "edge_type_counts_added": dict(Counter(edge["edge_type"] for edge in new_edges).most_common()),
        "graph_intake_nodes": graph_intake_nodes,
        "non_claims": NON_CLAIMS,
        "phase": PHASE,
        "queue_entry_count": len(rows),
        "rows": rows,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
    }


def _report_markdown(ledger: dict[str, Any], manual_queue: dict[str, Any]) -> str:
    lines = [
        "# Fix45 Algorithmic Percolation Report",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: fix45_algorithmic_percolation_report_support_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: Research-only support-edge annotation report; no public RC or graph publication is authorized. -->",
        "",
        "## Summary",
        "",
        f"- Queue entries considered: `{ledger['queue_entry_count']}`",
        f"- Candidate edges added: `{sum(ledger['edge_type_counts_added'].values())}`",
        f"- Manual semantic carry-forward entries: `{manual_queue['entry_count']}`",
        "",
        "## Decision Counts",
        "",
        "| Decision | Count |",
        "|---|---:|",
    ]
    for key, value in ledger["decision_counts"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Added Edge Types", "", "| Edge type | Count |", "|---|---:|"])
    for key, value in ledger["edge_type_counts_added"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
        ]
    )
    for claim in NON_CLAIMS:
        lines.append(f"- {claim}")
    return "\n".join(lines) + "\n"


def _walkthrough(analysis: dict[str, Any], ledger: dict[str, Any], manual_queue: dict[str, Any], candidate: dict[str, Any]) -> str:
    edge_type_counts = ledger["edge_type_counts_added"]
    duplicate_count = ledger["decision_counts"].get("skipped_duplicate", 0)
    unresolved_count = ledger["decision_counts"].get("unresolved_no_unique_target", 0)
    return f"""# Phase 1545p-Fix45: Targeted Percolation Annotation Walkthrough

## Status

COMPLETE.

Fix45 consumed the Fix43 low-PageRank target queue and applied only bounded
algorithmic annotation rules. It did not perform the manual semantic tranche,
sign any artifact, mutate the canonical Atlas, publish a graph, activate public
RC, or mutate ADR/CDL state.

## Queue Breakdown

- Total queue entries: `{analysis['total_queue_count']}`
- Repo prefix counts: `{json.dumps(analysis['repo_prefix_counts'], sort_keys=True, allow_nan=False)}`
- CDL filename hints: `{analysis['cdl_filename_hint_count']}`
- ADR filename hints: `{analysis['adr_filename_hint_count']}`
- `__init__.py` entries: `{analysis['init_py_count']}`
- `target:*` entries: `{analysis['target_node_count']}`
- Tools containment-only entries: `{analysis['tools_contains_file_only_count']}`

## Annotation Results

- Deterministic candidate edges added: `{sum(edge_type_counts.values())}`
- Edge type counts: `{json.dumps(edge_type_counts, sort_keys=True, allow_nan=False)}`
- Duplicate edges skipped: `{duplicate_count}`
- Unresolved filename targets: `{unresolved_count}`
- Manual semantic review carry-forward entries: `{manual_queue['entry_count']}`
- New graph-intake support nodes: `{len(ledger['graph_intake_nodes'])}`

## Enriched Candidate

- Output: `out/atlas_research/genesis_atlas_enriched_candidate_fix45.json`
- Nodes: `{len(candidate['nodes'])}`
- Edges: `{len(candidate['edges'])}`
- New candidate status: `{candidate['candidate_status']}`

## Authority Target Guard

Fix45 did not use `repo:group:out`, generated `out/` files, view exports, or
generated monitoring artifacts as authority targets. Fix45 did not add
`GOVERNS` edges. `target:*` nodes were deferred to manual semantic review.

## Tokens

{chr(10).join(f'- `{token}`' for token in TOKENS)}

## Non-Claims

{chr(10).join(f'- {claim}' for claim in NON_CLAIMS)}
"""


def run(
    *,
    candidate_in: Path = CANDIDATE_IN,
    queue_in: Path = QUEUE_IN,
    candidate_out: Path = CANDIDATE_OUT,
    analysis_json_out: Path = ANALYSIS_JSON_OUT,
    analysis_md_out: Path = ANALYSIS_MD_OUT,
    ledger_out: Path = LEDGER_OUT,
    report_out: Path = REPORT_OUT,
    manual_queue_out: Path = MANUAL_QUEUE_OUT,
    walkthrough_out: Path = WALKTHROUGH_OUT,
) -> dict[str, Any]:
    source_candidate = _load_json(candidate_in)
    queue = _load_json(queue_in)
    if _sha256_file(candidate_in) != FIX41A_SHA256:
        raise ValueError("fix45_source_candidate_sha_mismatch")
    entries = queue.get("entries")
    if not isinstance(entries, list) or queue.get("entry_count") != 500:
        raise ValueError("fix45_queue_entry_count_mismatch")

    nodes: list[dict[str, Any]] = list(source_candidate["nodes"])
    edges: list[dict[str, Any]] = list(source_candidate["edges"])
    cdl_index, adr_index, node_ids = _semantic_indexes(nodes)
    existing_keys = _existing_edge_keys(edges)
    new_keys: set[tuple[str, str, str]] = set()
    ledger_rows: list[dict[str, Any]] = []
    new_edges: list[dict[str, Any]] = []

    for entry in entries:
        row, edge = _classify_entry(
            entry,
            cdl_index=cdl_index,
            adr_index=adr_index,
            node_ids=node_ids,
            existing_keys=existing_keys,
            new_keys=new_keys,
        )
        ledger_rows.append(row)
        if edge is not None:
            key = (_edge_source(edge), _edge_type(edge), _edge_target(edge))
            new_keys.add(key)
            new_edges.append(edge)

    graph_intake_nodes = [_graph_intake_node(path) for path in NEW_DOC_PATHS]
    graph_intake_edges = [_graph_intake_edge(_node_id(node), str(node["source_path"])) for node in graph_intake_nodes]
    for node in graph_intake_nodes:
        if _node_id(node) not in node_ids:
            nodes.append(node)
            node_ids.add(_node_id(node))
    for edge in graph_intake_edges:
        key = (_edge_source(edge), _edge_type(edge), _edge_target(edge))
        if key not in existing_keys and key not in new_keys:
            new_keys.add(key)
            new_edges.append(edge)

    analysis = _queue_analysis(entries)
    manual_queue = _manual_queue(ledger_rows)
    ledger = _ledger_payload(ledger_rows, graph_intake_nodes, new_edges)
    candidate = dict(source_candidate)
    candidate["nodes"] = nodes
    candidate["edges"] = edges + new_edges
    candidate["candidate_status"] = "unsigned_support_only_not_canonical_fix45_percolation_candidate"
    candidate["phase"] = PHASE
    candidate["fix45_merge_summary"] = {
        "added_candidate_edges": len(new_edges),
        "added_candidate_nodes": len(graph_intake_nodes),
        "decision_counts": ledger["decision_counts"],
        "edge_type_counts_added": ledger["edge_type_counts_added"],
        "input_base_graph": "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json",
        "input_queue": "out/genesis_base_graph_fix44_target_queue.json",
        "manual_semantic_queue_count": manual_queue["entry_count"],
        "phase": PHASE,
    }
    candidate.pop("candidate_digest", None)
    candidate["non_claims"] = NON_CLAIMS
    candidate["candidate_digest"] = "fix45_candidate:" + _sha256_text(_canonical_json(candidate))

    _atomic_write(analysis_json_out, _pretty_json(analysis))
    _atomic_write(analysis_md_out, _analysis_markdown(analysis))
    _atomic_write(manual_queue_out, _pretty_json(manual_queue))
    _atomic_write(ledger_out, _pretty_json(ledger))
    _atomic_write(report_out, _report_markdown(ledger, manual_queue))
    _atomic_write(candidate_out, _pretty_json(candidate))
    _atomic_write(walkthrough_out, _walkthrough(analysis, ledger, manual_queue, candidate))

    return {
        "analysis": analysis,
        "candidate_edge_count": len(candidate["edges"]),
        "candidate_node_count": len(candidate["nodes"]),
        "candidate_sha256": _sha256_file(candidate_out),
        "ledger": {
            "decision_counts": ledger["decision_counts"],
            "edge_type_counts_added": ledger["edge_type_counts_added"],
        },
        "manual_queue_entry_count": manual_queue["entry_count"],
        "non_claims": NON_CLAIMS,
        "status": "PASS",
        "tokens": TOKENS,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Fix45 targeted percolation annotation.")
    parser.add_argument("--candidate", type=Path, default=CANDIDATE_IN)
    parser.add_argument("--queue", type=Path, default=QUEUE_IN)
    args = parser.parse_args()
    payload = run(candidate_in=args.candidate, queue_in=args.queue)
    print(_canonical_json(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
