#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Fix50 conservative authority-edge repair for unsigned Atlas candidates."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE = "phase_1545p_fix50"
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"

BASE_FIX49 = REPO_ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix49.json"
BASE_FIX48 = REPO_ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix48.json"
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
OUT_CANDIDATE = REPO_ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix50.json"
LEDGER_OUT = REPO_ROOT / "docs/specs/ilc_fix50_authority_edge_repair_ledger_v0.1.json"
REPORT_OUT = REPO_ROOT / "docs/specs/ilc_fix50_authority_edge_repair_report_v0.1.md"
QUEUE_OUT = REPO_ROOT / "docs/specs/ilc_fix50_unresolved_authority_repair_queue_v0.1.json"

NON_CLAIMS = [
    "Fix50 is an unsigned Atlas candidate repair pass.",
    "No Genesis signing occurred.",
    "No canonical Atlas mutation occurred.",
    "No public graph publication occurred.",
    "No public RC activation occurred.",
    "No runtime, economic, network, ADR, or CDL activation occurred.",
    "CDL-098 remains unconsumed; Phase 1573a is drafted but not ratified.",
]


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _pretty_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def _edge_id(source: str, edge_type: str, target: str) -> str:
    preimage = f"{source}|{edge_type}|{target}".encode("utf-8")
    return "edge:" + hashlib.sha256(preimage).hexdigest()[:16]


def _load_candidate() -> tuple[Path, dict[str, Any]]:
    path = BASE_FIX49 if BASE_FIX49.exists() else BASE_FIX48
    if not path.exists():
        raise FileNotFoundError("fix50_base_candidate_missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("fix50_candidate_object_required")
    return path, data


def _node_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id") or node.get("node_id") or node.get("id")
    return value if isinstance(value, str) else ""


def _parse_register() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    text = CDL_REGISTER.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.startswith("| CDL-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        raw = cells[0].upper().replace("CDL-", "")
        key = raw if raw.startswith("V") else raw.zfill(3)
        row_text = " | ".join(cells).lower()
        if "ratified" in row_text:
            status = "ratified"
        elif "accepted" in row_text:
            status = "accepted"
        elif "open" in row_text or "prelock" in row_text:
            status = "open"
        else:
            status = "unknown"
        rows[key] = {"status": status, "row": " | ".join(cells)}
    return rows


def _cdl_key(node_id: str) -> str | None:
    if not node_id.startswith("cdl:"):
        return None
    rest = node_id.split(":", 1)[1].lower()
    if rest.startswith("v"):
        match = re.match(r"v(\d+)", rest)
        return f"V{match.group(1)}" if match else None
    match = re.match(r"0*(\d{1,3})", rest)
    return match.group(1).zfill(3) if match else None


def _adr_key(node_id: str) -> str | None:
    if not node_id.startswith("adr:"):
        return None
    match = re.search(r"0*(\d{1,4})", node_id.split(":", 1)[1])
    return match.group(1).zfill(4) if match else None


def _is_lifecycle(node_id: str) -> bool:
    lowered = node_id.lower()
    return any(
        token in lowered
        for token in (
            "_opening_phase_",
            "_prelock_",
            "_ratification_phase_",
            "historical_opening",
        )
    )


def _canonical_score(node_id: str, node: dict[str, Any], existing_node0: set[str]) -> tuple[int, str]:
    score = 0
    lowered = node_id.lower()
    if node_id in existing_node0:
        score += 1000
    if node.get("core_star_map_candidate") is True:
        score += 100
    if str(node.get("canonicality_tier", "")).lower() in {"accepted_adr", "ratified_cdl", "constitutional"}:
        score += 50
    if _is_lifecycle(node_id):
        score -= 500
    if re.match(r"^(cdl|adr):0*\d+$", lowered):
        score -= 25
    if "runtime" in lowered:
        score -= 5
    score += min(len(node_id), 120)
    return (score, node_id)


def _classify_authorities(
    nodes: dict[str, dict[str, Any]],
    existing_node0_governs: set[str],
) -> tuple[dict[str, dict[str, str]], dict[str, str], dict[str, str]]:
    register = _parse_register()
    classifications: dict[str, dict[str, str]] = {}
    canonical_cdl_by_key: dict[str, str] = {}
    canonical_adr_by_key: dict[str, str] = {}

    cdl_groups: dict[str, list[str]] = defaultdict(list)
    adr_groups: dict[str, list[str]] = defaultdict(list)
    for nid in nodes:
        cdl = _cdl_key(nid)
        adr = _adr_key(nid)
        if cdl:
            cdl_groups[cdl].append(nid)
        elif adr:
            adr_groups[adr].append(nid)

    for key, ids in sorted(cdl_groups.items()):
        status = register.get(key, {}).get("status", "unknown")
        candidates = [nid for nid in ids if not _is_lifecycle(nid)]
        if status == "ratified" and candidates:
            canonical = max(candidates, key=lambda nid: _canonical_score(nid, nodes[nid], existing_node0_governs))
            canonical_cdl_by_key[key] = canonical
        else:
            canonical = ""
        for nid in sorted(ids):
            if _is_lifecycle(nid):
                tier = "lifecycle_snapshot"
            elif status != "ratified":
                tier = "proposed_open"
            elif nid == canonical:
                tier = "canonical_ratified"
            elif re.match(r"^cdl:0*\d+$", nid.lower()):
                tier = "source_derived_duplicate"
            else:
                tier = "canonical_alias"
            classifications[nid] = {
                "authority_family": "cdl",
                "authority_key": key,
                "classification_tier": tier,
                "canonical_target": canonical,
                "register_status": status,
            }

    adr_files = {p.name.split("_", 2)[1].zfill(4) for p in (REPO_ROOT / "docs/adr").glob("ADR_*.md")}
    for key, ids in sorted(adr_groups.items()):
        accepted = key in adr_files or any("accepted" in str(nodes[nid].get("canonicality_tier", "")).lower() for nid in ids)
        candidates = [nid for nid in ids if not _is_lifecycle(nid)]
        if accepted and candidates:
            canonical = max(candidates, key=lambda nid: _canonical_score(nid, nodes[nid], existing_node0_governs))
            canonical_adr_by_key[key] = canonical
        else:
            canonical = ""
        for nid in sorted(ids):
            if _is_lifecycle(nid):
                tier = "lifecycle_snapshot"
            elif not accepted:
                tier = "proposed_open"
            elif nid == canonical:
                tier = "canonical_accepted"
            elif re.match(r"^adr:0*\d+$", nid.lower()):
                tier = "source_derived_duplicate"
            else:
                tier = "canonical_alias"
            classifications[nid] = {
                "authority_family": "adr",
                "authority_key": key,
                "classification_tier": tier,
                "canonical_target": canonical,
                "register_status": "accepted" if accepted else "unknown",
            }

    return classifications, canonical_cdl_by_key, canonical_adr_by_key


def _new_edge(source: str, target: str, edge_type: str, method: str, rationale: str) -> dict[str, Any]:
    return {
        "annotation_method": method,
        "annotation_phase": PHASE,
        "candidate_status": "fix50_support_only_not_canonical",
        "confidence": 0.78,
        "edge_id": _edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "phase": PHASE,
        "rationale": rationale,
        "relation": edge_type.lower(),
        "review_status": "candidate_only_not_authority_promotion",
        "signature_status": "unsigned_candidate_preimage",
        "source": source,
        "target": target,
    }


def _add_edge(edges: list[dict[str, Any]], seen: set[tuple[str, str, str]], edge: dict[str, Any]) -> bool:
    key = (edge["source"], edge["edge_type"], edge["target"])
    if key in seen:
        return False
    seen.add(key)
    edges.append(edge)
    return True


def _authority_from_identifier(
    nid: str,
    canonical_cdls: dict[str, str],
    canonical_adrs: dict[str, str],
) -> str | None:
    lowered = nid.lower()
    cdl_matches = [m.zfill(3) for m in re.findall(r"cdl[_:-]0*(\d{1,3})", lowered)]
    cdl_v_matches = [f"V{m}" for m in re.findall(r"cdl[_:-]v(\d+)", lowered)]
    adr_matches = [m.zfill(4) for m in re.findall(r"adr[_:-]0*(\d{1,4})", lowered)]
    candidates = [canonical_cdls[k] for k in cdl_matches + cdl_v_matches if k in canonical_cdls]
    candidates += [canonical_adrs[k] for k in adr_matches if k in canonical_adrs]
    unique = sorted(set(candidates))
    if len(unique) == 1:
        return unique[0]
    return None


def _policy_authority(nid: str, canonical_cdls: dict[str, str], canonical_adrs: dict[str, str]) -> str | None:
    explicit = _authority_from_identifier(nid, canonical_cdls, canonical_adrs)
    if explicit:
        return explicit
    lowered = nid.lower()
    mappings = [
        ("genesis_theta", "029"),
        ("provenance_decay", "084"),
        ("reuse_attribution", "084"),
        ("edge_mint_phi", "085"),
        ("cmax", "026"),
        ("fee_burn", "028"),
        ("ecu_price_clamp", "030"),
    ]
    for token, key in mappings:
        if token in lowered and key in canonical_cdls:
            return canonical_cdls[key]
    if "node_embedding" in lowered and "0030" in canonical_adrs:
        return canonical_adrs["0030"]
    return None


def main() -> None:
    base_path, data = _load_candidate()
    base_sha = _sha256_file(base_path)
    nodes = {_node_id(node): node for node in data.get("nodes", []) if _node_id(node)}
    edges = list(data.get("edges", []))
    seen = {
        (edge.get("source", ""), edge.get("edge_type", ""), edge.get("target", ""))
        for edge in edges
    }
    existing_node0_governs = {
        edge.get("target", "")
        for edge in edges
        if edge.get("source") == NODE0 and edge.get("edge_type") == "GOVERNS"
    }

    classifications, canonical_cdls, canonical_adrs = _classify_authorities(nodes, existing_node0_governs)
    added_edges: list[dict[str, Any]] = []
    skipped_duplicates = 0

    def emit(edge: dict[str, Any]) -> None:
        nonlocal skipped_duplicates
        if _add_edge(added_edges, seen, edge):
            return
        skipped_duplicates += 1

    for nid, record in sorted(classifications.items()):
        tier = record["classification_tier"]
        canonical = record["canonical_target"]
        if nid == canonical or not canonical:
            continue
        if tier == "lifecycle_snapshot":
            emit(_new_edge(nid, canonical, "SUPERSEDED_BY", "fix50_duplicate_consolidation", "Lifecycle snapshot superseded by canonical ratified authority node."))
        elif tier == "canonical_alias":
            emit(_new_edge(nid, canonical, "SAME_AUTHORITY", "fix50_duplicate_consolidation", "Alias node refers to the same ratified or accepted authority object as the canonical target."))
        elif tier == "source_derived_duplicate":
            emit(_new_edge(nid, canonical, "DERIVED_FROM", "fix50_duplicate_consolidation", "Source-derived duplicate linked to canonical semantic authority node."))

    for canonical in sorted(set(canonical_cdls.values()) | set(canonical_adrs.values())):
        emit(_new_edge(NODE0, canonical, "GOVERNS", "fix50_authority_repair", "NODE0 is the genesis authority root; all ratified CDL and accepted ADR nodes descend from it under the ILC constitutional decision log chain."))

    unresolved_no_authority: list[str] = []
    multi_authority: list[str] = []
    for nid in sorted(nodes):
        if nid.startswith("invariant:"):
            authority = _authority_from_identifier(nid, canonical_cdls, canonical_adrs)
            if authority:
                emit(_new_edge(authority, nid, "GOVERNS", "fix50_invariant_authority_repair", "Governing authority identified from explicit CDL/ADR identifier in invariant node id."))
            else:
                unresolved_no_authority.append(nid)
        elif nid.startswith("policy:"):
            lowered = nid.lower()
            if "_phase_" in lowered or "_window_" in lowered or "_not_" in lowered or "_complete_phase_" in lowered:
                continue
            authority = _policy_authority(nid, canonical_cdls, canonical_adrs)
            if authority:
                emit(_new_edge(authority, nid, "GOVERNS", "fix50_authority_repair", "Governing authority identified from explicit policy family or CDL/ADR identifier."))
            else:
                unresolved_no_authority.append(nid)

    phase_fenceposts = [
        nid
        for nid in sorted(nodes)
        if nid.startswith("policy:")
        and any(token in nid.lower() for token in ("_phase_", "_window_", "_complete_phase_", "_not_"))
    ]

    edge_type_counts = Counter(edge["edge_type"] for edge in added_edges)
    method_counts = Counter(edge["annotation_method"] for edge in added_edges)
    classification_counts = Counter(record["classification_tier"] for record in classifications.values())

    queue = {
        "cdl_098_unconsumed_candidate_gap": True,
        "fix50_multi_authority_decisions": multi_authority,
        "fix50_phase_fencepost_no_source_node": phase_fenceposts,
        "fix50_unresolved_duplicate_groups": [],
        "fix50_unresolved_invariants_no_authority_trace": unresolved_no_authority,
        "fix50_unresolved_proposed_open_cdl": [
            nid for nid, record in sorted(classifications.items()) if record["classification_tier"] == "proposed_open"
        ],
        "residual_semantic_annotation_queue_status": "deferred_to_successor_lane",
    }

    report = {
        "base_candidate_path": str(base_path.relative_to(REPO_ROOT)),
        "base_candidate_sha256": base_sha,
        "base_edge_count": len(edges),
        "base_node_count": len(data.get("nodes", [])),
        "cdl_098_unconsumed_candidate_gap": True,
        "classification_counts": dict(sorted(classification_counts.items())),
        "edge_type_counts_added": dict(sorted(edge_type_counts.items())),
        "fix50_generation_report_version": "fix50_authority_edge_repair.v0.1",
        "method_counts_added": dict(sorted(method_counts.items())),
        "new_edge_count": len(added_edges),
        "non_claims": NON_CLAIMS,
        "output_candidate_path": str(OUT_CANDIDATE.relative_to(REPO_ROOT)),
        "output_edge_count": len(edges) + len(added_edges),
        "output_node_count": len(data.get("nodes", [])),
        "skipped_duplicate_edges": skipped_duplicates,
        "unresolved_counts": {
            key: len(value) if isinstance(value, list) else int(bool(value))
            for key, value in queue.items()
            if key != "residual_semantic_annotation_queue_status"
        },
    }

    output = dict(data)
    output["edges"] = edges + added_edges
    output["fix50_generation_report"] = report
    output["phase"] = "1545p-Fix50"
    output["schema_version"] = "genesis_atlas_enriched_candidate_fix50.v0.1"
    output["non_claims"] = sorted(set(output.get("non_claims", []) + NON_CLAIMS))
    output["sha256"] = hashlib.sha256(_canonical_json({"nodes": output["nodes"], "edges": output["edges"]}).encode("utf-8")).hexdigest()

    ledger = {
        "phase": "1545p-Fix50",
        "authority_classifications": classifications,
        "edges_added": added_edges,
        "generation_report": report,
    }

    report_md = f"""<!-- PUBLIC_RC_EXCLUDE: atlas_fix50_authority_edge_repair_report -->
<!-- PUBLIC_RC_EXCLUDE_REASON: Unsigned candidate graph repair report; no Genesis signing, canonical graph mutation, public graph publication, public RC activation, runtime activation, minting, settlement, or ADR/CDL mutation. -->

# Fix50 Authority Edge Repair Report

## Summary

- Base candidate: `{report['base_candidate_path']}`
- Base SHA-256: `{base_sha}`
- Nodes preserved: `{report['output_node_count']}`
- Base edges: `{report['base_edge_count']}`
- New Fix50 edges: `{report['new_edge_count']}`
- Output edges: `{report['output_edge_count']}`
- CDL-098 status: unconsumed; Phase 1573a drafted but not ratified.

## Classification Counts

{_markdown_counts(report['classification_counts'])}

## Added Edge Types

{_markdown_counts(report['edge_type_counts_added'])}

## Unresolved Carry-Forward

{_markdown_counts(report['unresolved_counts'])}

## Non-Claims

{chr(10).join(f'- {claim}' for claim in NON_CLAIMS)}
"""

    _atomic_write(OUT_CANDIDATE, _pretty_json(output))
    _atomic_write(LEDGER_OUT, _pretty_json(ledger))
    _atomic_write(QUEUE_OUT, _pretty_json(queue))
    _atomic_write(REPORT_OUT, report_md)
    print(_pretty_json(report), end="")


def _markdown_counts(counts: dict[str, int]) -> str:
    lines = ["| Item | Count |", "|---|---:|"]
    for key, value in sorted(counts.items()):
        lines.append(f"| `{key}` | {value} |")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
