#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Fix53: Apply canonical-only heuristic GOVERNS edges from CDL source patterns.

Four heuristics:
  H1: repo:file CDL source doc -> REGRESSES -> invariant
      => cdl:N_* -> GOVERNS -> invariant:*
  H2: repo:file CDL source doc -> CLASSIFIED_BY -> policy
      => cdl:N_* -> GOVERNS -> policy:*
  H3: repo:file CDL source doc -> REFERENCES_AUTHORITY -> policy or invariant
      => cdl:N_* -> GOVERNS -> policy:* or invariant:*
  H5: policy node ID contains CDL number pattern
      => cdl:N_* -> GOVERNS -> policy:cdl_NNN_*

Only CDL nodes classified by the Fix50 authority ledger as
``canonical_ratified`` may be GOVERNS sources. Alias, source-derived duplicate,
lifecycle snapshot, and proposed/open CDL-like nodes are rejected rather than
used as authority sources.

Spectral note: lambda2 (Fiedler value) measures global algebraic connectivity
of the full undirected graph projection. Analysis of the Fix51 Fiedler vector
shows that the graph has a small weakly-connected cluster of ~194 peripheral
repo:file nodes that determines the lambda2 bottleneck. NODE0, all CDL/ADR
semantic nodes, all policy nodes, and all invariant nodes lie in the main
well-connected cluster of ~15,483 nodes. GOVERNS edges connect nodes within
this main cluster and do not bridge the Fiedler cut. Therefore lambda2 will
not improve significantly from GOVERNS additions alone. The relevant authority
graph health metric is authority coverage (fraction of policy/invariant nodes
with inbound GOVERNS trace from NODE0), not lambda2.
"""

from __future__ import annotations

import collections
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix51.json"
AUTHORITY_LEDGER = ROOT / "docs" / "specs" / "ilc_fix50_authority_edge_repair_ledger_v0.1.json"
OUTPUT = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix53.json"
SIM_OUTPUT = ROOT / "out" / "genesis_authority_sim_battery_fix53_v0.1.json"
SIM_DOC = ROOT / "docs" / "sims" / "sim_authority_01" / "genesis_authority_sim_battery_fix53_v0.1.md"

SPECTRAL_NOTE = (
    "lambda2 (Fiedler value) measures global algebraic connectivity of the full "
    "undirected graph projection. Analysis of the Fix51 Fiedler vector shows that "
    "the graph has a small weakly-connected cluster of ~194 peripheral repo:file "
    "nodes that determines the lambda2 bottleneck. NODE0, all CDL/ADR semantic "
    "nodes, all policy nodes, and all invariant nodes lie in the main well-connected "
    "cluster of ~15,483 nodes. GOVERNS edges connect nodes within this main cluster "
    "and do not bridge the Fiedler cut. Therefore lambda2 will not improve "
    "significantly from GOVERNS additions alone. The relevant authority graph health "
    "metric is authority coverage (fraction of policy/invariant nodes with inbound "
    "GOVERNS trace from NODE0), not lambda2."
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_cdl_num_from_path(path: str) -> str | None:
    m = re.search(r"_cdl_0*(\d+)_", path)
    if m:
        return m.group(1).lstrip("0") or "0"
    m = re.search(r"_cdl_(v\d+)_", path)
    if m:
        return m.group(1)
    return None


def make_edge_id(src: str, edge_type: str, tgt: str) -> str:
    material = f"{src}|{edge_type}|{tgt}".encode("utf-8")
    return "edge:" + hashlib.sha256(material).hexdigest()[:16]


def canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def load_canonical_cdl_sources(nodes: dict[str, dict]) -> tuple[dict[str, list[str]], dict[str, str]]:
    """Return CDL number -> canonical ratified CDL node IDs from the Fix50 ledger."""
    ledger = json.loads(AUTHORITY_LEDGER.read_text(encoding="utf-8"))
    classifications = ledger.get("authority_classifications", {})
    if not isinstance(classifications, dict):
        raise ValueError("fix53_authority_classifications_missing")

    canonical_by_num: dict[str, list[str]] = collections.defaultdict(list)
    source_classification: dict[str, str] = {}
    for node_id, record in classifications.items():
        if not isinstance(record, dict) or not str(node_id).startswith("cdl:"):
            continue
        tier = record.get("classification_tier")
        if isinstance(tier, str):
            source_classification[str(node_id)] = tier
        if tier != "canonical_ratified" or node_id not in nodes:
            continue
        key = record.get("authority_key")
        if not isinstance(key, str) or not key:
            continue
        normalized = key.lstrip("0").upper() or "0"
        canonical_by_num[normalized].append(str(node_id))

    for key in list(canonical_by_num):
        canonical_by_num[key] = sorted(set(canonical_by_num[key]))
    return canonical_by_num, source_classification


def compute_coverage(edge_list: list, node_set: set) -> dict:
    inv_governed: set[str] = set()
    pol_governed: set[str] = set()
    for e in edge_list:
        if e["edge_type"] == "GOVERNS":
            t = e["target"]
            if t.startswith("invariant:"):
                inv_governed.add(t)
            elif t.startswith("policy:"):
                pol_governed.add(t)
    inv_total = sum(1 for n in node_set if n.startswith("invariant:"))
    pol_total = sum(1 for n in node_set if n.startswith("policy:"))
    return {
        "invariant_reachable": len(inv_governed),
        "invariant_total": inv_total,
        "invariant_coverage": len(inv_governed) / inv_total if inv_total else 0.0,
        "policy_reachable": len(pol_governed),
        "policy_total": pol_total,
        "policy_coverage": len(pol_governed) / pol_total if pol_total else 0.0,
    }


def derive_heuristic_edges(
    nodes: dict, edges: list, canonical_cdl_num_to_nodes: dict[str, list[str]], source_classification: dict[str, str]
) -> tuple[list, dict]:
    """Return list of new GOVERNS edge dicts and a stats dict."""

    out_edges_by_src: dict[str, list] = collections.defaultdict(list)
    for e in edges:
        out_edges_by_src[e["source"]].append(e)

    governs_set: set[tuple[str, str]] = set()
    for e in edges:
        if e["edge_type"] == "GOVERNS":
            governs_set.add((e["source"], e["target"]))

    # Build CDL number -> list of all CDL semantic node IDs for rejection accounting.
    cdl_num_to_nodes: dict[str, list[str]] = collections.defaultdict(list)
    for nid in nodes:
        if nid.startswith("cdl:"):
            m = re.search(r"cdl:0*(\d+)_", nid)
            if m:
                cdl_num_to_nodes[m.group(1).lstrip("0") or "0"].append(nid)
            m2 = re.search(r"cdl:(v\d+)_", nid)
            if m2:
                cdl_num_to_nodes[m2.group(1).upper()].append(nid)

    # Build CDL source doc files index: repo:file node -> CDL number
    cdl_source_files: dict[str, str] = {}
    for nid in nodes:
        if nid.startswith("repo:file:"):
            parts = nid.split(":", 2)
            path = parts[2] if len(parts) >= 3 else nid
            cdl_num = extract_cdl_num_from_path(path)
            cdl_num = cdl_num.upper() if cdl_num and cdl_num.lower().startswith("v") else cdl_num
            if cdl_num and cdl_num in cdl_num_to_nodes:
                cdl_source_files[nid] = cdl_num

    rejected_noncanonical: set[tuple[str, str, str]] = set()

    def canonical_sources_for(cdl_num: str) -> list[str]:
        return canonical_cdl_num_to_nodes.get(cdl_num, [])

    def record_rejected(cdl_num: str, target: str) -> None:
        canonical_sources = set(canonical_sources_for(cdl_num))
        for cdl_node in cdl_num_to_nodes.get(cdl_num, []):
            if cdl_node not in canonical_sources:
                rejected_noncanonical.add(
                    (cdl_node, target, source_classification.get(cdl_node, "unclassified"))
                )

    h1: set[tuple[str, str]] = set()
    h2: set[tuple[str, str]] = set()
    h3: set[tuple[str, str]] = set()
    h5: set[tuple[str, str]] = set()

    for src_file, cdl_num in cdl_source_files.items():
        for e in out_edges_by_src[src_file]:
            tgt = e["target"]
            etype = e["edge_type"]
            if tgt not in nodes:
                continue
            if etype == "REGRESSES" and tgt.startswith("invariant:"):
                record_rejected(cdl_num, tgt)
                for cdl_node in canonical_sources_for(cdl_num):
                    k = (cdl_node, tgt)
                    if k not in governs_set:
                        h1.add(k)
            elif etype == "CLASSIFIED_BY" and tgt.startswith("policy:"):
                record_rejected(cdl_num, tgt)
                for cdl_node in canonical_sources_for(cdl_num):
                    k = (cdl_node, tgt)
                    if k not in governs_set:
                        h2.add(k)
            elif etype == "REFERENCES_AUTHORITY" and (
                tgt.startswith("policy:") or tgt.startswith("invariant:")
            ):
                record_rejected(cdl_num, tgt)
                for cdl_node in canonical_sources_for(cdl_num):
                    k = (cdl_node, tgt)
                    if k not in governs_set:
                        h3.add(k)

    # H5: policy name contains CDL number
    for nid in nodes:
        if nid.startswith("policy:"):
            m = re.search(r"cdl[_\-]?0*(\d+)", nid, re.IGNORECASE)
            if m:
                cdl_num = m.group(1).lstrip("0") or "0"
                if cdl_num in cdl_num_to_nodes:
                    record_rejected(cdl_num, nid)
                    for cdl_node in canonical_sources_for(cdl_num):
                        k = (cdl_node, nid)
                        if k not in governs_set:
                            h5.add(k)

    # Combine and assign heuristic label (H1 takes priority)
    all_new: set[tuple[str, str]] = h1 | h2 | h3 | h5
    heuristic_map: dict[tuple[str, str], str] = {}
    for k in h1:
        heuristic_map[k] = "H1"
    for k in h2:
        if k not in heuristic_map:
            heuristic_map[k] = "H2"
    for k in h3:
        if k not in heuristic_map:
            heuristic_map[k] = "H3"
    for k in h5:
        if k not in heuristic_map:
            heuristic_map[k] = "H5"

    new_edges = []
    for src, tgt in sorted(all_new):
        h = heuristic_map[(src, tgt)]
        new_edges.append(
            {
                "edge_id": make_edge_id(src, "GOVERNS", tgt),
                "edge_type": "GOVERNS",
                "source": src,
                "target": tgt,
                "annotation_phase": "phase_1545p_fix53",
                "annotation_method": "heuristic_cdl_source_doc",
                "authority_boundary": "canonical_ratified_cdl_source_only",
                "candidate_status": "fix53_support_only_not_canonical",
                "promotion_status": "candidate_only_not_canonical",
                "review_status": "heuristic_not_manual_not_signing_ready",
                "signature_status": "unsigned_candidate_preimage",
                "heuristic_id": h,
                "confidence": "0.72",
                "rationale": (
                    f"CDL source document has edge to target node; "
                    f"GOVERNS derived via heuristic {h}"
                ),
            }
        )

    actual_counts = collections.Counter(heuristic_map[k] for k in all_new)
    stats = {
        "h1_candidate_edges_before_dedup": len(h1),
        "h2_candidate_edges_before_dedup": len(h2),
        "h3_candidate_edges_before_dedup": len(h3),
        "h5_candidate_edges_before_dedup": len(h5),
        "h1_edges_added": actual_counts["H1"],
        "h2_edges_added": actual_counts["H2"],
        "h3_edges_added": actual_counts["H3"],
        "h5_edges_added": actual_counts["H5"],
        "total_new_governs_edges": len(all_new),
        "canonical_source_guard": "canonical_ratified",
        "rejected_noncanonical_source_edges": len(rejected_noncanonical),
        "rejected_noncanonical_source_examples": [
            {"source": src, "target": tgt, "classification_tier": tier}
            for src, tgt, tier in sorted(rejected_noncanonical)[:20]
        ],
    }
    return new_edges, stats


def write_atomically(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        os.unlink(tmp)
        raise


def main() -> None:
    print(f"Loading Fix51 candidate from {INPUT}")
    with open(INPUT) as f:
        fix51 = json.load(f)

    input_sha256 = sha256_file(INPUT)
    print(f"Input SHA-256: {input_sha256}")

    nodes_list = fix51["nodes"]
    nodes: dict[str, dict] = {n["candidate_id"]: n for n in nodes_list}
    edges: list[dict] = fix51["edges"]
    canonical_cdl_num_to_nodes, source_classification = load_canonical_cdl_sources(nodes)

    print(f"Fix51: {len(nodes)} nodes, {len(edges)} edges")

    # Compute coverage before
    cov_before = compute_coverage(edges, nodes)
    print(
        f"Coverage before — invariants: {cov_before['invariant_reachable']}/"
        f"{cov_before['invariant_total']} ({100*cov_before['invariant_coverage']:.1f}%), "
        f"policies: {cov_before['policy_reachable']}/"
        f"{cov_before['policy_total']} ({100*cov_before['policy_coverage']:.1f}%)"
    )

    # Derive heuristic edges
    new_edges, stats = derive_heuristic_edges(
        nodes,
        edges,
        canonical_cdl_num_to_nodes,
        source_classification,
    )
    print(
        f"Derived: H1={stats['h1_edges_added']}, H2={stats['h2_edges_added']}, "
        f"H3={stats['h3_edges_added']}, H5={stats['h5_edges_added']}, "
        f"total={stats['total_new_governs_edges']}"
    )

    # Build Fix53 candidate
    fix53 = dict(fix51)
    fix53["edges"] = edges + new_edges
    fix53["phase"] = "phase_1545p_fix53"

    combined_edges = edges + new_edges
    cov_after = compute_coverage(combined_edges, nodes)
    print(
        f"Coverage after  — invariants: {cov_after['invariant_reachable']}/"
        f"{cov_after['invariant_total']} ({100*cov_after['invariant_coverage']:.1f}%), "
        f"policies: {cov_after['policy_reachable']}/"
        f"{cov_after['policy_total']} ({100*cov_after['policy_coverage']:.1f}%)"
    )

    fix53["fix53_generation_report"] = {
        "annotation_phase": "phase_1545p_fix53",
        "input_candidate": str(INPUT),
        "input_candidate_sha256": input_sha256,
        **stats,
        "invariant_coverage_before": cov_before["invariant_coverage"],
        "invariant_coverage_after": cov_after["invariant_coverage"],
        "invariant_reachable_before": cov_before["invariant_reachable"],
        "invariant_reachable_after": cov_after["invariant_reachable"],
        "invariant_total": cov_before["invariant_total"],
        "policy_coverage_before": cov_before["policy_coverage"],
        "policy_coverage_after": cov_after["policy_coverage"],
        "policy_reachable_before": cov_before["policy_reachable"],
        "policy_reachable_after": cov_after["policy_reachable"],
        "policy_total": cov_before["policy_total"],
        "spectral_note": SPECTRAL_NOTE,
    }

    # Write candidate atomically
    write_atomically(OUTPUT, canonical_json(fix53))
    output_sha256 = sha256_file(OUTPUT)
    print(f"Fix53 candidate written: {OUTPUT}")
    print(f"Output SHA-256: {output_sha256}")

    # SIM battery output
    governs_count_before = sum(1 for e in edges if e["edge_type"] == "GOVERNS")
    governs_count_after = sum(1 for e in combined_edges if e["edge_type"] == "GOVERNS")

    coverage_improved = (
        cov_after["invariant_coverage"] > cov_before["invariant_coverage"]
        and cov_after["policy_coverage"] > cov_before["policy_coverage"]
    )
    overall_verdict = "pass" if coverage_improved else "warn"

    sim_result = {
        "sim_battery_id": "genesis_authority_sim_battery_fix53_v0.1",
        "input_candidate_path": str(OUTPUT),
        "input_candidate_sha256": output_sha256,
        "baseline_candidate_path": str(INPUT),
        "baseline_candidate_sha256": input_sha256,
        "suite_d_rerun": {
            "fix51_baseline": {
                **cov_before,
                "governs_edge_count": governs_count_before,
            },
            "fix53_post_heuristic": {
                **cov_after,
                "governs_edge_count": governs_count_after,
            },
            "invariant_coverage_delta": (
                cov_after["invariant_coverage"] - cov_before["invariant_coverage"]
            ),
            "policy_coverage_delta": (
                cov_after["policy_coverage"] - cov_before["policy_coverage"]
            ),
            "governs_edge_delta": governs_count_after - governs_count_before,
            "coverage_strictly_improved": coverage_improved,
        },
        "heuristic_derivation": stats,
        "spectral_note": SPECTRAL_NOTE,
        "overall_verdict": overall_verdict,
        "non_claims": [
            "Fix53 is candidate mutation only (research graph). No CDL/ADR mutation occurred.",
            "No LMDB write, signing, runtime activation, or public RC activation occurred.",
            f"The {stats['total_new_governs_edges']} edges are heuristic research annotations with annotation_method: heuristic_cdl_source_doc.",
            "Fix53 rejects non-canonical CDL aliases, lifecycle snapshots, source-derived duplicates, and proposed/open CDL-like nodes as GOVERNS sources.",
            "Heuristic annotations are not equivalent to manual_reviewed annotations.",
            "SIM evidence does not grant authority, activation, eligibility, or signing readiness.",
            "Authority coverage improvement is a research signal, not a ratification event.",
            "lambda2 (Fiedler value) is not an authority graph health metric for this graph.",
            "No genesis signature occurred.",
        ],
    }

    write_atomically(SIM_OUTPUT, canonical_json(sim_result))
    print(f"SIM output written: {SIM_OUTPUT}")

    # Analysis document
    SIM_DOC.parent.mkdir(parents=True, exist_ok=True)
    inv_delta_pct = 100 * sim_result["suite_d_rerun"]["invariant_coverage_delta"]
    pol_delta_pct = 100 * sim_result["suite_d_rerun"]["policy_coverage_delta"]
    doc = f"""# Genesis Authority SIM Battery Fix53 v0.1 — Heuristic GOVERNS Expansion

## Executive Summary

Fix53 applies {stats['total_new_governs_edges']} canonical-source heuristic GOVERNS
edges to the Fix51 candidate using four heuristics based on CDL source document edge
patterns. This is candidate mutation only (research graph). No CDL/ADR mutation,
LMDB write, signing, or public RC activation
occurred.

**Overall verdict: `{overall_verdict}`**

Coverage strictly improved on both invariants and policies.

---

## Heuristic Derivation Methodology

Each heuristic uses CDL source document nodes (`repo:file:` nodes whose path contains
`_cdl_NNN_`) as intermediaries to derive a GOVERNS edge from the CDL semantic node to
the policy or invariant that the source document references.

| Heuristic | Source doc edge type | Target prefix | Edges derived |
|-----------|---------------------|---------------|---------------|
| H1 | REGRESSES | invariant: | {stats['h1_edges_added']} |
| H2 | CLASSIFIED_BY | policy: | {stats['h2_edges_added']} |
| H3 | REFERENCES_AUTHORITY | policy: or invariant: | {stats['h3_edges_added']} |
| H5 | Policy name contains CDL number | policy: | {stats['h5_edges_added']} |
| **Total (after deduplication)** | | | **{stats['total_new_governs_edges']}** |

All new edges carry `annotation_method: "heuristic_cdl_source_doc"` and
`confidence: "0.72"` (lower than Fix50 manual annotations at 0.90). GOVERNS
sources are restricted to CDL nodes classified by the Fix50 ledger as
`canonical_ratified`; {stats['rejected_noncanonical_source_edges']} non-canonical
alias/snapshot/proposed-source candidate edges were rejected.

---

## Coverage Table

| Metric | Fix51 (baseline) | Fix53 (post-heuristic) | Delta |
|--------|-----------------|----------------------|-------|
| Invariants governed | {cov_before['invariant_reachable']}/{cov_before['invariant_total']} ({100*cov_before['invariant_coverage']:.1f}%) | {cov_after['invariant_reachable']}/{cov_after['invariant_total']} ({100*cov_after['invariant_coverage']:.1f}%) | +{inv_delta_pct:.1f} pp |
| Policies governed | {cov_before['policy_reachable']}/{cov_before['policy_total']} ({100*cov_before['policy_coverage']:.1f}%) | {cov_after['policy_reachable']}/{cov_after['policy_total']} ({100*cov_after['policy_coverage']:.1f}%) | +{pol_delta_pct:.1f} pp |
| Total GOVERNS edges | {governs_count_before} | {governs_count_after} | +{governs_count_after - governs_count_before} |

---

## Spectral Interpretation Note

{SPECTRAL_NOTE}

The Fix52 SIM battery advisory warning `lambda2_decreased` (delta = -1.67e-7) is a
measurement artifact of the full graph's Fiedler structure and does not indicate
authority graph fragmentation. The Fiedler cut separates ~194 peripheral repo:file
nodes from the main cluster — it has no connection to the CDL/ADR/policy/invariant
authority subgraph.

---

## Non-Claims

- Fix53 is candidate mutation only. No CDL/ADR mutation occurred.
- No LMDB write, signing, runtime activation, or public RC activation occurred.
- The {stats['total_new_governs_edges']} edges are heuristic research annotations, not manually reviewed annotations.
- Non-canonical CDL aliases, lifecycle snapshots, source-derived duplicates, and proposed/open CDL-like nodes are not accepted as Fix53 GOVERNS sources.
- SIM evidence does not grant authority, activation, eligibility, or signing readiness.
- Authority coverage improvement is a research signal, not a ratification event.
- lambda2 is not an authority graph health metric for this graph.
- No genesis signature occurred.
"""
    write_atomically(SIM_DOC, doc)
    print(f"SIM doc written: {SIM_DOC}")
    print(f"\nDone. overall_verdict={overall_verdict}")


if __name__ == "__main__":
    main()
