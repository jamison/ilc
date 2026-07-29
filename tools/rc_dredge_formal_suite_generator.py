#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
RC Formal Protocol Suite Generator
==================================
Reads raw dredge output and emits the formal markdown suite.

This version is hardened for post-605 use:
- configurable input, matrix, and output directory
- exact source-path provenance when available
- honest placeholder marking for unimplemented gates
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

LEVERAGE_PRIMARY_TOPICS = {
    "minting_economics",
    "genesis_governance",
    "wallet_authority",
    "ecu_circulation",
}
LEVERAGE_SECONDARY_TOPICS = {
    "node_market_structure",
    "market_liquidity",
}
AGENT_PULL_PRIMARY_TOPICS = {
    "agent_memory",
    "knowledge_nodes",
    "network_privacy",
    "node_market_structure",
}


def evaluate_gates(claim_text: str, strength: str, topic: str, mainnet_req: str, g1_mode: str):
    text = claim_text.lower()
    if g1_mode == "off":
        g1 = True
    elif g1_mode == "relaxed":
        g1 = mainnet_req != "No" and ("invariant" in text or strength == "must")
    else:
        g1 = mainnet_req == "Yes" and ("invariant" in text or strength == "must")
    g2 = strength == "must"

    g7 = 0
    if topic in LEVERAGE_PRIMARY_TOPICS:
        g7 += 2
    elif topic in LEVERAGE_SECONDARY_TOPICS:
        g7 += 1
    if any(token in text for token in ("canonical", "wire spec", "contract", "boundary", "authority")):
        g7 += 1

    g8 = 0
    if topic in AGENT_PULL_PRIMARY_TOPICS:
        g8 += 2
    if any(token in text for token in ("privacy", "private", "hostile", "market", "liquidity")):
        g8 += 1

    novelty = 10 if any(token in text for token in ("new", "miss", "missing", "gap", "deferred")) else 5
    return g1, g2, min(g7, 3), min(g8, 3), novelty


def resolve_source_path(candidate: dict) -> tuple[str, Path | None]:
    source_path = candidate.get("source_path")
    if source_path:
        actual = Path(source_path)
        if actual.exists():
            return source_path, actual

    src_file = candidate.get("source_file") or candidate.get("source", "").split(":")[0]
    if not src_file:
        return "", None

    for parent in (Path("docs"), Path("Z_Past_Chats"), Path(".")):
        matches = list(parent.rglob(src_file))
        if matches:
            return str(matches[0]), matches[0]
    return src_file, None


def generate_suite(input_path: Path, matrix_path: Path, output_dir: Path, g1_mode: str):
    if not input_path.exists():
        raise SystemExit(f"Run rc_dredge_v2.py first. Missing: {input_path}")
    if not matrix_path.exists():
        raise SystemExit(f"Missing matrix file: {matrix_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    candidates = [json.loads(line) for line in input_path.open(encoding="utf-8")]

    sources: dict[str, Path | None] = {}
    for candidate in candidates:
        source_label, resolved = resolve_source_path(candidate)
        if source_label:
            sources[source_label] = resolved

    inventory_path = output_dir / "ilc_rc_dredge_inventory_v0.1.md"
    with inventory_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# RC Dredge Inventory v0.1\n\nGenerated: {now}\n\n")
        handle.write("| file | ext | bytes | sha256 |\n|---|---:|---:|---|\n")
        for source_label in sorted(sources):
            actual = sources[source_label]
            if actual and actual.exists():
                size = actual.stat().st_size
                digest = hashlib.sha256(actual.read_bytes()).hexdigest()
                handle.write(f"| {actual} | {actual.suffix} | {size} | {digest} |\n")
            else:
                handle.write(f"| {source_label} | .unknown | 0 | 000...000 |\n")

    shutil.copy(input_path, output_dir / "ilc_rc_dredge_raw_v0.1.jsonl")
    shutil.copy(matrix_path, output_dir / "ilc_rc_dredge_matrix_v0.1.md")

    scored = []
    dropped = []
    for candidate in candidates:
        g1, g2, g7, g8, novelty = evaluate_gates(
            candidate["claim"],
            candidate["strength"],
            candidate["topic"],
            candidate.get("mainnet_req", "Review"),
            g1_mode,
        )
        if g1 and g2:
            candidate["g7"] = g7
            candidate["g8"] = g8
            candidate["novelty"] = novelty
            candidate["total"] = g7 + g8 + novelty
            scored.append(candidate)
        else:
            dropped.append(candidate)

    scored.sort(key=lambda item: (item["total"], item["g7"], item.get("source", "")), reverse=True)

    prerank_path = output_dir / "ilc_rc_preranking_v0.1.md"
    with prerank_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# ILC RC Dredge — Pre-Triage Ranking v0.1\n\nGenerated: {now}\n\n")
        handle.write("## Top 20 by Total Score\n\n")
        handle.write("| rank | id | topic | total | novelty | agent | claim |\n")
        handle.write("|---|---|---|---:|---:|---:|---|\n")
        for index, candidate in enumerate(scored[:20], 1):
            claim_trunc = candidate["claim"][:150].replace("\n", " ")
            handle.write(
                f"| {index} | {candidate['id']} | {candidate['topic']} | {candidate['total']} | "
                f"{candidate['novelty']} | {candidate['g8']} | {claim_trunc}... |\n"
            )

    triage_path = output_dir / "ilc_rc_clause_triage_v0.1.md"
    with triage_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# RC Clause Triage v0.1\n\nGenerated: {now}\n\n")
        handle.write("## Logic Gates\n")
        handle.write("1. `G1 rc_scope`\n2. `G2 evidence_strength`\n3. `G3 conflict_check`\n4. `G4 architecture_alignment`\n5. `G5 implementation_alignment`\n6. `G6 ratifiability`\n\n")
        handle.write("G3-G6 remain human-review placeholders in this generated suite.\n\n")
        handle.write("## Clause-by-Clause Results\n\n")
        handle.write("| clause | G1 | G2 | G3 | G4 | G5 | G6 | disposition | notes |\n")
        handle.write("|---|---|---|---|---|---|---|---|---|\n")
        for candidate in scored[:30]:
            disposition = "KEEP-NOW" if candidate["g7"] > 1 else "KEEP-DEFER"
            handle.write(
                f"| {candidate['id']} | pass | pass | needs_review | needs_review | needs_review | needs_review | "
                f"{disposition} | Candidate mapped from {candidate.get('source', '')} |\n"
            )

    leverage_path = output_dir / "ilc_rc_leverage_agent_pull_ranking_v0.1.md"
    with leverage_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# RC Leverage + Agent Pull Ranking v0.1\n\nGenerated: {now}\n\n")
        handle.write("## Top-15 Priority Ranking\n\n")
        handle.write("| rank | clause_id | topic | current_action | G7 | G8 | total | lane | why this matters |\n")
        handle.write("|---|---|---|---|---:|---:|---:|---|---|\n")
        for index, candidate in enumerate(scored[:15], 1):
            lane = "Now" if candidate["g7"] + candidate["g8"] >= 4 else "Near"
            handle.write(
                f"| {index} | `{candidate['id']}` | {candidate['topic']} | `promote_guardrail` | {candidate['g7']} | "
                f"{candidate['g8']} | {candidate['g7'] + candidate['g8']} | {lane} | High-leverage candidate in {candidate['topic']}. |\n"
            )

    crit_path = output_dir / "ilc_rc_criticality_v0.1.md"
    with crit_path.open("w", encoding="utf-8") as handle:
        handle.write("# RC Criticality Guardrails Matrix v0.1\n\n")
        handle.write("## Matrix\n\n| Domain | Criticality | Target State | Source |\n|---|---|---|---|\n")
        for candidate in scored[:10]:
            handle.write(f"| {candidate['topic']} | RC-Blocker | Review and sequence | {candidate.get('source', '')} |\n")

    drop_path = output_dir / "ilc_rc_drop_ledger_v0.1.md"
    with drop_path.open("w", encoding="utf-8") as handle:
        handle.write("# RC Drop Ledger v0.1\n\n")
        handle.write("Captures items that failed G1 or G2 gating under the selected mode.\n\n")
        for candidate in dropped[:20]:
            handle.write(
                f"- Topic: `{candidate['topic']}`\n"
                f"- Strength: `{candidate['strength']}`\n"
                f"- Matrix Status: `discarded` / `out_of_scope`\n"
                f"- Citation: `{candidate.get('source', '')}`\n"
                f"> {candidate['claim'][:200]}...\n\n"
            )

    breakthrough_path = output_dir / "ilc_rc_breakthrough_shortlist_v0.1.md"
    with breakthrough_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# RC Breakthrough Shortlist v0.1\n\nGenerated: {now}\n\n")
        handle.write("## Top 10 (Ranked, Curated)\n\n")
        handle.write("| rank | idea | canonical anchors | representative evidence rows | classification | rationale |\n")
        handle.write("|---|---|---|---|---|---|\n")
        for index, candidate in enumerate(scored[:10], 1):
            handle.write(
                f"| {index} | {candidate['topic']} stabilization | `{candidate['id']}` | `{candidate.get('source', '')}` | "
                f"`review-now` | High-signal candidate for post-605 backlog review. |\n"
            )

    meta_path = output_dir / "ilc_rc_dredge_meta_v0.1.md"
    with meta_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# RC Dredge Metadata v0.1\n\nGenerated: {now}\n\n")
        handle.write(f"Input raw file: `{input_path}`\n")
        handle.write(f"Input matrix file: `{matrix_path}`\n")
        handle.write(f"Output directory: `{output_dir}`\n")
        handle.write(f"G1 mode: `{g1_mode}`\n")
        handle.write(f"Text corpus files scanned: {len(sources)}\n")
        handle.write(f"Raw entries captured: {len(candidates)}\n")
        handle.write(f"Gated-in entries: {len(scored)}\n")
        handle.write(f"Dropped entries: {len(dropped)}\n\n")
        handle.write("## Dredge Outputs\n\n")
        for name in (
            "ilc_rc_dredge_raw_v0.1.jsonl",
            "ilc_rc_dredge_matrix_v0.1.md",
            "ilc_rc_preranking_v0.1.md",
            "ilc_rc_clause_triage_v0.1.md",
            "ilc_rc_leverage_agent_pull_ranking_v0.1.md",
            "ilc_rc_criticality_v0.1.md",
            "ilc_rc_drop_ledger_v0.1.md",
            "ilc_rc_breakthrough_shortlist_v0.1.md",
        ):
            handle.write(f"- `{output_dir / name}`\n")

    print(f"Successfully generated RC dredge suite at {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="docs/research/rc_gap_dredge_raw_v0.2.jsonl")
    parser.add_argument("--matrix", default="docs/research/rc_gap_matrix_v0.2.md")
    parser.add_argument("--output-dir", default="docs/research")
    parser.add_argument("--g1-mode", choices=["strict", "relaxed", "off"], default="strict")
    args = parser.parse_args()
    generate_suite(Path(args.input), Path(args.matrix), Path(args.output_dir), args.g1_mode)
