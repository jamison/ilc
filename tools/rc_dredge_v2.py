#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
ILC RC Missing Feature Dredge V2
=========================================
Scans markdown/text corpora for candidate RC gaps and writes a raw JSONL plus
human-readable matrix.

This version is hardened for post-605 use:
- configurable topic profile
- safer self-skip rules
- exact-text deduplication instead of prefix-only dedup
- full relative source paths for provenance
- isolated output directories
- heuristic environment flags that can be inspected downstream
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

BASELINE_TOPIC_PATTERNS = {
    "genesis_governance": [
        r"\bgenesis node",
        r"\bgenesis agent",
        r"\bfounder",
        r"\bgovernance structure",
        r"\bbootstrap",
        r"\bgenesis",
    ],
    "knowledge_nodes": [
        r"\bknowledge node",
        r"\bself-compiling",
        r"\bparameter node",
        r"\bhard coded",
        r"\bhard-coded",
    ],
    "minting_economics": [
        r"\bILC mint",
        r"\bcoin generation",
        r"\bclearing",
        r"\btokenomics",
        r"\bemission",
        r"\breward",
    ],
    "network_privacy": [
        r"\bpublic release",
        r"\bdynamic discovery",
        r"\bhostile",
        r"\btopology privacy",
        r"\bmulti-hop",
        r"\banonymous",
    ],
    "agent_memory": [
        r"\bagent loop",
        r"\bharness",
        r"\bscrapbook",
        r"\bprivate memory",
        r"\binward-memory",
    ],
    "testnet_gap": [
        r"\bdeferred",
        r"\bmissing",
        r"\bfuture phase",
        r"\bnot included",
        r"\bpost-RC",
        r"\bTestnet",
        r"\bRelease Candidate",
    ],
}

POST_605_TOPIC_PATTERNS = {
    "wallet_authority": [
        r"\btransfer\b",
        r"\bsend\b",
        r"\bescrow\b",
        r"\bwrite[- ]authority\b",
        r"\bwallet[- ]write\b",
        r"\bsettlement[- ]path\b",
        r"\bwithdrawal\b",
        r"\bspend authority\b",
        r"\btransfer tax\b",
        r"\btransfer fee\b",
    ],
    "ecu_circulation": [
        r"\bsector b\b",
        r"\bagent-to-agent\b",
        r"\bagent to agent\b",
        r"\becu payment\b",
        r"\becu transfer\b",
        r"\becu spend\b",
        r"\becu circulation\b",
        r"\bproductive credit\b",
    ],
    "node_market_structure": [
        r"\bfractional\b",
        r"\bleasehold\b",
        r"\bnode lease\b",
        r"\bincome rights?\b",
        r"\bnode transfer\b",
        r"\bcreator attribution\b",
        r"\bcooling period\b",
    ],
    "market_liquidity": [
        r"\bmarket[- ]making\b",
        r"\bliquidity\b",
        r"\border book\b",
        r"\bbid[- ]ask\b",
        r"\bspread\b",
        r"\bamm\b",
        r"\bprice discovery\b",
        r"\bexchange listing\b",
    ],
}

TOPIC_PROFILES = {
    "baseline": BASELINE_TOPIC_PATTERNS,
    "post_605": {**BASELINE_TOPIC_PATTERNS, **POST_605_TOPIC_PATTERNS},
}

EXCLUDE_NAME_SUBSTRINGS = (
    "rc_gap_dredge",
    "rc_dredge_v2",
    "rc_gap_triage_v2",
    "rc_dredge_formal_suite_generator",
    "rc_make_context_pack",
)

MUST_RE = re.compile(
    r"\b(must|cannot|must not|never|always|required|shall|critical|mandatory|prohibited|invariant|hard constraint|non-negotiable)\b",
    re.IGNORECASE,
)
SHOULD_RE = re.compile(
    r"\b(should|ought|recommended|prefer|ideally|designed to|intended to|needs to|is expected to)\b",
    re.IGNORECASE,
)

MAINNET_YES_PATTERNS = [
    r"\bmainnet\b",
    r"\bproduction\b",
    r"\bpublic rc\b",
    r"\bpublic release\b",
    r"\brelease candidate\b",
    r"\bpublic launch\b",
    r"\bpost-rc\b",
]
MAINNET_NO_PATTERNS = [
    r"\btestnet\b",
    r"\brc0\.1\b",
    r"\bcurated testnet\b",
    r"\boperator-managed\b",
    r"\bthree-machine\b",
    r"\bprivate memory\b",
]
TESTNET_YES_PATTERNS = [
    r"\btestnet\b",
    r"\brc0\.1\b",
    r"\bcurated testnet\b",
    r"\boperator-managed\b",
    r"\bthree-machine\b",
]
TESTNET_NO_PATTERNS = [
    r"\bmainnet\b",
    r"\bproduction\b",
    r"\bpublic release\b",
    r"\brelease candidate\b",
    r"\bpublic launch\b",
]


def compile_topic_patterns(topic_patterns: dict[str, list[str]]) -> dict[str, list[re.Pattern[str]]]:
    return {
        topic: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        for topic, patterns in topic_patterns.items()
    }


def normative_strength(text: str) -> str:
    if MUST_RE.search(text):
        return "must"
    if SHOULD_RE.search(text):
        return "should"
    return "idea"


def classify_topic(text: str, topic_patterns: dict[str, list[re.Pattern[str]]]) -> str:
    scores: dict[str, int] = {}
    for topic, patterns in topic_patterns.items():
        scores[topic] = sum(1 for pattern in patterns if pattern.search(text))
    if not any(scores.values()):
        return "unclassified"
    return max(scores, key=scores.get)


def resolve_flag(text_lower: str, yes_patterns: list[str], no_patterns: list[str]) -> str:
    yes = any(re.search(pattern, text_lower) for pattern in yes_patterns)
    no = any(re.search(pattern, text_lower) for pattern in no_patterns)
    if yes and not no:
        return "Yes"
    if no and not yes:
        return "No"
    return "Review"


def heuristics_status(text: str) -> tuple[str, str, str]:
    text_lower = text.lower()
    testnet_req = resolve_flag(text_lower, TESTNET_YES_PATTERNS, TESTNET_NO_PATTERNS)
    mainnet_req = resolve_flag(text_lower, MAINNET_YES_PATTERNS, MAINNET_NO_PATTERNS)
    return ("heuristic", testnet_req, mainnet_req)


def normalize_block(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def should_skip_file(file_path: Path) -> bool:
    name = file_path.name.lower()
    return any(token in name for token in EXCLUDE_NAME_SUBSTRINGS)


def iter_corpus_files(search_dirs: list[str]) -> Iterable[Path]:
    for dir_name in search_dirs:
        root = Path(dir_name)
        if not root.exists():
            continue
        for file_path in root.rglob("*.*"):
            if file_path.suffix not in {".md", ".txt"}:
                continue
            if should_skip_file(file_path):
                continue
            yield file_path


def run_dredge(search_dirs: list[str], output_dir: str, topic_profile: str, min_chars: int) -> tuple[Path, Path, int]:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    topic_patterns = compile_topic_patterns(TOPIC_PROFILES[topic_profile])

    candidates = []
    seen: set[str] = set()

    for file_path in iter_corpus_files(search_dirs):
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            print(f"Skipping {file_path}: {exc}")
            continue

        blocks = re.split(r"\n\s*\n", text)
        for i, block in enumerate(blocks):
            block_stripped = block.strip()
            if len(block_stripped) < min_chars:
                continue
            if block_stripped.startswith(("#", "|", "```", "---")):
                continue

            topic = classify_topic(block_stripped, topic_patterns)
            if topic == "unclassified":
                continue

            normalized = normalize_block(block_stripped)
            if normalized.lower() in seen:
                continue
            seen.add(normalized.lower())

            strength = normative_strength(block_stripped)
            content_hash = hashlib.md5(normalized.encode()).hexdigest()[:6]
            review_status, t_req, m_req = heuristics_status(block_stripped)
            source_path = file_path.as_posix()

            candidates.append(
                {
                    "id": f"cap-{content_hash}",
                    "topic": topic,
                    "strength": strength,
                    "claim": normalized[:400],
                    "source": f"{source_path}:{i}",
                    "source_path": source_path,
                    "source_file": file_path.name,
                    "block_index": i,
                    "review_status": review_status,
                    "testnet_req": t_req,
                    "mainnet_req": m_req,
                }
            )

    jsonl_file = out_path / "rc_gap_dredge_raw_v0.2.jsonl"
    with open(jsonl_file, "w", encoding="utf-8") as handle:
        for candidate in candidates:
            handle.write(json.dumps(candidate) + "\n")

    matrix_file = out_path / "rc_gap_matrix_v0.2.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    candidates.sort(
        key=lambda item: (
            0 if item["strength"] == "must" else 1 if item["strength"] == "should" else 2,
            item["topic"],
            item["source_path"],
            item["block_index"],
        )
    )

    with open(matrix_file, "w", encoding="utf-8") as handle:
        handle.write("# RC Missing Feature Dredge Matrix v0.2 (Refined)\n\n")
        handle.write(f"- Generated: {now}\n")
        handle.write(f"- Topic profile: `{topic_profile}`\n")
        handle.write(f"- Search roots: {', '.join(f'`{root}`' for root in search_dirs)}\n")
        handle.write(f"- Min chars: {min_chars}\n")
        handle.write(f"- Inputs extracted: {len(candidates)}\n")
        handle.write("- Formalizing the delta between Testnet Sandbox and Public RC Release.\n\n")
        handle.write("## Topic Coverage\n")
        topics: dict[str, int] = {}
        for candidate in candidates:
            topics[candidate["topic"]] = topics.get(candidate["topic"], 0) + 1
        for topic, count in sorted(topics.items()):
            handle.write(f"- {topic}: {count}\n")
        handle.write("\n## The Dredge Ledger\n\n")
        handle.write(
            "| id | topic | strength | claim | source | status | testnet_req | mainnet_req |\n"
        )
        handle.write("|---|---|---|---|---|---|---|---|\n")
        for candidate in candidates:
            claim_trunc = candidate["claim"][:120].replace("|", "/")
            handle.write(
                f"| {candidate['id']} | {candidate['topic']} | {candidate['strength']} | "
                f"{claim_trunc}... | {candidate['source']} | {candidate['review_status']} | "
                f"{candidate['testnet_req']} | {candidate['mainnet_req']} |\n"
            )

    print(f"Pipeline complete: Extracted {len(candidates)} claims to {matrix_file}")
    return jsonl_file, matrix_file, len(candidates)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("search_dirs", nargs="+", default=["docs", "tools", "Z_Past_Chats"])
    parser.add_argument("--output", default="docs/research")
    parser.add_argument("--topic-profile", choices=sorted(TOPIC_PROFILES), default="baseline")
    parser.add_argument("--min-chars", type=int, default=40)
    args = parser.parse_args()

    run_dredge(args.search_dirs, args.output, args.topic_profile, args.min_chars)
