#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
ILC RC Gap Dredge Extractor
Matches mentions of missing/future RC Testnet and RC Mainnet features,
including Genesis Governance and Knowledge Nodes.
"""

import re
import json
import argparse
import hashlib
from pathlib import Path

# Important query terms
GAP_PATTERNS = {
    "genesis_concessions": [r"\bgenesis node", r"\bgenesis agent", r"\bconcession", r"\bfounder\b", r"\bbootstrap\b", r"\bgovernance structure\b"],
    "knowledge_nodes": [r"\bknowledge node", r"\bself-compiling\b", r"\bparameter node\b", r"\bhard coded\b", r"\bhard-coded\b"],
    "minting_economics": [r"\bILC mint\b", r"\bILC minting\b", r"\bcoin generation\b", r"\bclearing\b", r"\btokenomics\b", r"\bemission\b", r"\breward\b"],
    "network_privacy": [r"\bpublic release\b", r"\bdynamic discovery\b", r"\bhostile\b", r"\btopology privacy\b", r"\bmulti-hop\b", r"anonymously"],
    "agent_integration": [r"\bagent loop\b", r"\bharness\b", r"scrapbook\b", r"private memory", r"inward-memory"],
    "rc_gaps": [r"\bdeferred\b", r"\bmissing\b", r"\bfuture phase\b", r"\bnot included\b", r"\bpost-RC\b", r"testnet"],
}

def classify_topic(text: str) -> str:
    scores = {}
    for topic, patterns in GAP_PATTERNS.items():
        count = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
        scores[topic] = count
    
    if not scores: return "unclassified"
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unclassified"

def extract_candidates(text: str, source_file: str) -> list[dict]:
    candidates = []
    # split by paragraphs
    blocks = re.split(r'\n\s*\n', text)

    for i, block in enumerate(blocks):
        block_stripped = block.strip()
        if len(block_stripped) < 40: continue
        if block_stripped.startswith(("#", "|", "```", "---", "{")): continue

        topic = classify_topic(block_stripped)
        if topic == "unclassified":
            continue

        content_hash = hashlib.md5(block_stripped.encode()).hexdigest()[:6]

        candidates.append({
            "id": f"gap-{content_hash}",
            "source_file": source_file,
            "feature_topic": topic,
            "claim": block_stripped.replace('\n', ' ')[:400],
            "context": block_stripped,
            "strength": "target_feature",
        })
    return candidates

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("search_dirs", nargs='+', default=["docs", "tools"])
    parser.add_argument("--output", default="docs/research/rc_gap_dredge_raw.jsonl")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    all_entries = []
    seen = set()

    for dir_name in args.search_dirs:
        search_dir = Path(dir_name)
        if not search_dir.exists(): continue
        for file_path in search_dir.rglob("*.*"):
            if file_path.suffix not in [".md", ".txt"]: continue
        if "rc_gap_dredge" in file_path.name: continue # skip self outputs
        
        text = file_path.read_text(encoding="utf-8", errors="replace")
        candidates = extract_candidates(text, str(file_path))
        
        for c in candidates:
            key = c["claim"][:80]
            if key not in seen:
                seen.add(key)
                all_entries.append(c)

    # Sort to prioritize "must" and specific known missing topics
    all_entries.sort(key=lambda x: (x["strength"] == "idea", x["feature_topic"]))

    with open(output_path, "w") as f:
        for e in all_entries:
            f.write(json.dumps(e) + "\n")
            
    # Markdown summary
    md_path = output_path.with_suffix(".md")
    with open(md_path, "w") as f:
        f.write("# RC Gap Dredge Raw Extraction\n\n")
        f.write("| ID | Topic | Strength | Source | Claim |\n")
        f.write("|---|---|---|---|---|\n")
        for e in all_entries:
            src = Path(e["source_file"]).name
            claim = e["claim"].replace("|", "/").replace("\n", " ")[:100]
            f.write(f"| {e['id']} | {e['feature_topic']} | {e['strength']} | {src} | {claim} |\n")

    print(f"Extracted {len(all_entries)} potential missing feature gaps to {output_path}")

if __name__ == "__main__":
    main()
