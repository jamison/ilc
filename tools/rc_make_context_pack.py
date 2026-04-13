#!/usr/bin/env python3
"""
RC Gap Context Pack Generator
=============================
Builds a compact handoff bundle from a triage matrix.

This version is honest about the source material: the pack is a heuristic
candidate backlog, not a ratified closure artifact.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def parse_triage_matrix(matrix_path: Path):
    if not matrix_path.exists():
        raise SystemExit(f"Error: {matrix_path} not found.")

    lines = matrix_path.read_text(encoding="utf-8").split("\n")
    candidates = []
    in_table = False
    for line in lines:
        if line.startswith("| rank |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and not line.startswith("|"):
            in_table = False
            continue
        if in_table and line.strip():
            parts = [part.strip() for part in line.split("|") if part.strip()]
            if len(parts) >= 9:
                lane = parts[6]
                if lane in {"Now", "Near"}:
                    candidates.append(
                        {
                            "rank": parts[0],
                            "id": parts[1],
                            "topic": parts[2],
                            "score": parts[5],
                            "lane": lane,
                            "source": parts[7].strip(),
                            "claim": parts[8].strip(),
                        }
                    )
    return candidates


def generate_context_pack(output_path: Path, matrix_path: Path, raw_path: Path, candidates: list[dict]):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    content = "# RC Gap Handoff Context Pack v0.1\n\n"
    content += f"**Generated:** {now}\n"
    content += f"**Triage Matrix Source:** `{matrix_path}`\n"
    content += f"**Raw Data Lake Source:** `{raw_path}`\n"
    content += "**Status:** HEURISTIC CANDIDATE PACK FOR REVIEW\n\n"
    content += "---\n\n"

    content += "## 1. Context and Objective\n\n"
    content += (
        "This context pack summarizes the highest-ranked `Now`/`Near` claims from the triage matrix. "
        "These are heuristic candidate backlog items, not ratified findings. Use them to accelerate human review, "
        "prompt drafting, and sequence planning.\n\n"
    )

    content += "## 2. Candidate Backlog\n\n"
    content += (
        "Below are the highest-ranked candidate items carried forward from the triage matrix. "
        "You may re-sequence them, drop them, or split them after checking the underlying sources.\n\n"
    )

    for candidate in sorted(candidates, key=lambda item: int(item["rank"])):
        content += (
            f"### {candidate['rank']}. [{candidate['lane']}] Topic: `{candidate['topic']}` "
            f"(ID: {candidate['id']}, Score: {candidate['score']})\n"
        )
        content += f"**Provenance Path:** `{candidate['source']}`\n"
        content += f"> {candidate['claim']}\n\n"

    content += "---\n\n"
    content += "## 3. Strict Development Bounds\n\n"
    content += "- Treat every item here as a candidate requiring source review before implementation.\n"
    content += "- Do not infer ratification status from dredge score alone.\n"
    content += "- Do not collapse wallet/signing interoperability into transfer/escrow authority without explicit boundary work.\n"
    content += "- Keep RC runtime boundaries, public-release boundaries, and later-lane market infrastructure separate in planning.\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"Generated RC Context Pack with {len(candidates)} candidate requirements at {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", default="docs/research/rc_gap_triage_matrix_v0.1.md")
    parser.add_argument("--raw", default="docs/research/rc_gap_dredge_raw_v0.2.jsonl")
    parser.add_argument("--output", default="docs/context_packs/ilc_rc_gap_context_pack_v0.1.md")
    args = parser.parse_args()

    matrix_path = Path(args.matrix)
    raw_path = Path(args.raw)
    output_path = Path(args.output)
    candidates = parse_triage_matrix(matrix_path)
    if candidates:
        generate_context_pack(output_path, matrix_path, raw_path, candidates)
