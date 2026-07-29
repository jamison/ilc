#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
RC Gap Dredge Matrix Triage V2
==============================
Applies lightweight gates to dredge output and emits a ranked markdown matrix.

This version is hardened for post-605 work:
- configurable input and output paths
- configurable G1 behavior
- dynamic raw-entry counts
- leverage scoring for post-605 topic families
"""

from __future__ import annotations

import argparse
import json
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

    total = int(g1) + int(g2) + min(g7, 3) + min(g8, 3)
    return g1, g2, min(g7, 3), min(g8, 3), total


def generate_triage(input_path: Path, output_path: Path, g1_mode: str) -> int:
    if not input_path.exists():
        raise SystemExit(f"Run tools/rc_dredge_v2.py first. Missing: {input_path}")

    candidates = [json.loads(line) for line in input_path.open(encoding="utf-8")]

    scored = []
    dropped = 0
    for candidate in candidates:
        g1, g2, g7, g8, total = evaluate_gates(
            candidate["claim"],
            candidate["strength"],
            candidate["topic"],
            candidate.get("mainnet_req", "Review"),
            g1_mode,
        )
        if not g1 or not g2:
            dropped += 1
            continue
        candidate["g7"] = g7
        candidate["g8"] = g8
        candidate["total_score"] = total
        scored.append(candidate)

    scored.sort(
        key=lambda item: (item["total_score"], item["g7"], item.get("source_path", item.get("source", ""))),
        reverse=True,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("# RC Gap Triage + Leverage Ranking v0.1\n\n")
        handle.write(f"- Generated: {now}\n")
        handle.write(f"- Input: `{input_path}` ({len(candidates)} raw entries)\n")
        handle.write(f"- Surviving G1/G2 Cut: {len(scored)} entries\n")
        handle.write(f"- Dropped by gate: {dropped} entries\n")
        handle.write(f"- G1 mode: `{g1_mode}`\n")
        handle.write(
            "- Applied logic gates: `G1 rc_scope`, `G2 evidence_strength`, `G7 leverage_multiplier`, `G8 agent_market_pull`\n\n"
        )
        handle.write("## Expanded Priority Ranking (RC Mainnet Blockers)\n\n")
        handle.write("| rank | id | topic | G7 | G8 | total | lane | source | claim |\n")
        handle.write("|---|---|---|---:|---:|---:|---|---|---|\n")
        for index, candidate in enumerate(scored, 1):
            claim_trunc = candidate["claim"][:150].replace("|", "/")
            if candidate["total_score"] >= 6:
                lane = "Now"
            elif candidate["total_score"] >= 4:
                lane = "Near"
            else:
                lane = "Later"
            source_link = candidate.get("source", "unknown")
            handle.write(
                f"| {index} | {candidate['id']} | {candidate['topic']} | {candidate['g7']} | {candidate['g8']} | "
                f"{candidate['total_score']} | {lane} | {source_link} | {claim_trunc}... |\n"
            )
        handle.write("\n## Execution Recommendation\n\n")
        handle.write("### Cluster A (`Now`)\nHighest-leverage `must` claims under the selected gate mode.\n\n")
        handle.write("### Cluster B (`Near`)\nStrong `must` claims that need sequencing after Cluster A.\n\n")
        handle.write("### Cluster C (`Later`)\nStill in scope, but lower-ranked under the current scoring model.\n")

    print(f"Triage complete. Matrix generated at {output_path}")
    return len(scored)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="docs/research/rc_gap_dredge_raw_v0.2.jsonl")
    parser.add_argument("--output", default="docs/research/rc_gap_triage_matrix_v0.1.md")
    parser.add_argument("--g1-mode", choices=["strict", "relaxed", "off"], default="strict")
    args = parser.parse_args()
    generate_triage(Path(args.input), Path(args.output), args.g1_mode)
