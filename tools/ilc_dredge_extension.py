#!/usr/bin/env python3
"""
ILC Constitutional Dredge Extension Tool
=========================================
Extends the original constitutional dredge corpus (docs/research/constitution_dredge_raw_v0.1.jsonl,
Feb 2026, 41 files, 22194 entries) with new source material.

Scoring model is reverse-engineered from the original outputs:
  docs/research/constitution_idea_amazement_scores_v0.1.csv
  docs/research/constitution_leverage_agent_pull_ranking_v0.1.md

Usage:
  # Process specific files:
  python3 tools/ilc_dredge_extension.py \
      docs/adr/ADR_0015_Node_Transfer_Economics.md \
      docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md \
      docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md \
      docs/specs/ilc_economic_architecture_comprehensive_v0.1.md \
      Z_Past_Chats/2026_03_05_Opus_Conversation_Werner_Political_Economy_Phase358_Review.md \
      Z_Past_Chats/2026_03_05_Opus_Conversation_Economic_Architecture_Deep_Dive.md

  # With custom output directory:
  python3 tools/ilc_dredge_extension.py --output-dir docs/research/ FILE [FILE ...]

Outputs (written to --output-dir, default docs/research/):
  ilc_dredge_extension_raw_v0.1.jsonl       -- raw extracted entries (unreviewed)
  ilc_dredge_extension_matrix_v0.1.md       -- triage matrix (needs human/AI review pass)
  ilc_dredge_extension_preranking_v0.1.md   -- content-scored pre-ranking (before triage)
"""

import re
import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Topic classification
# ---------------------------------------------------------------------------

TOPIC_PATTERNS = {
    "economics": [
        r"\bECU\b", r"\bissuance\b", r"\breward\b", r"\bfee\b", r"\bmining\b",
        r"\beconomic\b", r"\btoken\b", r"\bprice\b", r"\bpay\b", r"\bincentive\b",
        r"\bWerner\b", r"\bcredit.creation\b", r"\bproductive.credit\b",
        r"\bmonetary\b", r"\bbounty\b", r"\btransfer.tax\b", r"\bleasehold\b",
        r"\bpost.issuance\b", r"\bSector [AB]\b", r"\bP_e\b", r"\bB_e\b",
        r"\bdual.token\b", r"\bECU.*lifespan\b", r"\bvault\b", r"\bfee.burn\b",
        r"\bSparkasse\b", r"\bCBDC\b", r"\bMittelstand\b", r"\btreasury\b",
        r"\bconversion.rate\b", r"\bfunding.request\b",
    ],
    "governance": [
        r"\bgovernance\b", r"\bcommittee\b", r"\bpanel\b", r"\bvote\b",
        r"\bquorum\b", r"\bratif", r"\bpolicy\b", r"\bCDL\b", r"\bADM\b",
        r"\bconstitutional\b", r"\bclause\b", r"\bdecision.log\b",
        r"\bminority.dissent\b", r"\bVRF\b", r"\boutside.*seat\b",
        r"\bauditor\b", r"\breopening\b", r"\bcapture\b", r"\banti.capture\b",
        r"\bsunset.fuse\b", r"\bgovernance.*bug\b",
    ],
    "canonicality": [
        r"\bcanonical\b", r"\bcanon\b", r"\bsignature\b", r"\bsigned\b",
        r"\bCID\b", r"\bCOSE\b", r"\bcommit\b", r"\bhash\b", r"\bimmutab\b",
        r"\bcontent.address\b", r"\bDAG.CBOR\b", r"\blineage\b",
        r"\brollback\b", r"\bcanonicity\b", r"\bsigner\b", r"\bkey.isolat\b",
        r"\bwallet.agnostic\b", r"\bsigning.provider\b", r"\bsecp256k1\b",
    ],
    "fork_policy": [
        r"\bfork\b", r"\bshard\b", r"\bupgrade\b", r"\brollback\b",
        r"\bversion\b", r"\bmigration\b", r"\bcanary\b", r"\bsplit\b",
        r"\bmerge\b",
    ],
    "founder_role": [
        r"\bgenesis\b", r"\bfounder\b", r"\badmin\b", r"\bprivilege\b",
        r"\bbootstrap\b", r"\bfade.out\b", r"\bsunset\b", r"\banonymous\b",
        r"\bSatoshi\b",
    ],
    "security": [
        r"\battack\b", r"\bexploit\b", r"\bvulnerab\b", r"\badversar\b",
        r"\btamper\b", r"\bfake\b", r"\bsybil\b",
        r"\bkey.compromise\b", r"\brotate\b", r"\bOPSEC\b",
    ],
    "epistemic_graph": [
        r"\bepistemic\b", r"\bclaim\b", r"\bvalidat\b", r"\brefut\b",
        r"\bcontradict\b", r"\bgraph\b", r"\bknowledge\b", r"\bPopper\b",
        r"\bfalsif\b", r"\bbasic.statement\b", r"\bD2\b", r"\bnode\b",
    ],
    "policy_loading": [
        r"\bL0\b", r"\bL1\b", r"\bL2\b", r"\bL3\b",
        r"\bpolicy.load\b", r"\bwire.protocol\b",
        r"\bgossip\b", r"\bD2d\b", r"\bLevin\b", r"\badaptive\b",
        r"\bgossip.coordinate\b", r"\btopology\b", r"\bforward.comparable\b",
        r"\bbackward.private\b",
    ],
}

# Topic base scores (reverse-engineered from constitution_idea_amazement_scores_v0.1.csv)
TOPIC_BASE = {
    "canonicality":    11,
    "governance":      10,
    "economics":        9,
    "epistemic_graph":  9,
    "security":         8,
    "policy_loading":   8,
    "fork_policy":      7,
    "founder_role":     6,
}

# G7 leverage multiplier and G8 agent pull defaults per topic
# (from constitution_leverage_agent_pull_ranking_v0.1.md rubric)
TOPIC_G7_DEFAULT = {
    "canonicality":    3,
    "governance":      3,
    "economics":       2,
    "epistemic_graph": 2,
    "policy_loading":  3,
    "fork_policy":     2,
    "security":        2,
    "founder_role":    2,
}
TOPIC_G8_DEFAULT = {
    "canonicality":    2,
    "governance":      2,
    "economics":       3,
    "epistemic_graph": 3,
    "policy_loading":  2,
    "fork_policy":     2,
    "security":        2,
    "founder_role":    1,
}


# ---------------------------------------------------------------------------
# Normative strength detection
# ---------------------------------------------------------------------------

MUST_RE = re.compile(
    r"\b(must|cannot|must not|never|always|required|shall|critical|mandatory|"
    r"prohibited|invariant|hard constraint|non-negotiable|is not permitted|"
    r"is required)\b",
    re.IGNORECASE,
)
SHOULD_RE = re.compile(
    r"\b(should|ought|recommended|prefer|ideally|designed to|intended to|"
    r"needs to|is expected to)\b",
    re.IGNORECASE,
)


def normative_strength(text: str) -> tuple[str, float]:
    """Return (strength, confidence) for a text chunk."""
    if MUST_RE.search(text):
        return "must", 0.85
    if SHOULD_RE.search(text):
        return "should", 0.70
    return "idea", 0.55


# ---------------------------------------------------------------------------
# Topic classification
# ---------------------------------------------------------------------------

def classify_topic(text: str) -> str:
    """Return the best-matching topic for a text chunk."""
    scores = {}
    for topic, patterns in TOPIC_PATTERNS.items():
        count = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
        scores[topic] = count
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "epistemic_graph"


# ---------------------------------------------------------------------------
# Candidate extraction
# ---------------------------------------------------------------------------

# Sentences/bullets that are likely normative architectural statements
CANDIDATE_RE = re.compile(
    r"(?:^|\n)"                          # start of line
    r"[ \t]*[-*•]?[ \t]*"               # optional bullet
    r"([A-Z][^\n]{40,300})"             # sentence: capital start, 40-300 chars
    r"(?=\n|$)",
    re.MULTILINE,
)

# Skip lines that are clearly metadata / formatting
SKIP_RE = re.compile(
    r"^(#|\*\*Date|\*\*From|\*\*To|\*\*Status|\|---|^---$|\s*$|"
    r"Co-Authored-By|^\s*\*\s*$)",
    re.MULTILINE,
)


def extract_candidates(text: str, source_file: str) -> list[dict]:
    """Extract normative candidate entries from text."""
    candidates = []
    lines = text.splitlines()

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Skip short lines, markdown headers, table rows, code fences
        if len(line_stripped) < 40:
            continue
        if line_stripped.startswith(("#", "|", "```", "---", "**Date", "**From")):
            continue
        if line_stripped.startswith(("Co-Authored", "Generated:", "Input:", "Output:")):
            continue

        strength, confidence = normative_strength(line_stripped)

        # For "idea" strength, only keep lines with at least one topic keyword match
        if strength == "idea":
            topic = classify_topic(line_stripped)
            if sum(
                1 for p in TOPIC_PATTERNS[topic]
                if re.search(p, line_stripped, re.IGNORECASE)
            ) < 2:
                continue  # too weak a signal

        topic = classify_topic(line_stripped)

        # Build a stable ID from content hash
        content_hash = hashlib.md5(line_stripped.encode()).hexdigest()[:6]
        entry_id = f"ext-{content_hash}"

        # Context: surrounding lines
        ctx_start = max(0, i - 1)
        ctx_end = min(len(lines), i + 3)
        context = " ".join(lines[ctx_start:ctx_end]).strip()[:300]

        candidates.append({
            "id": entry_id,
            "source_file": source_file,
            "line_number": i + 1,
            "topic": topic,
            "claim_statement": line_stripped[:300],
            "context_excerpt": context,
            "normative_strength": strength,
            "confidence": confidence,
            "status": "unreviewed",
        })

    # Deduplicate by claim content (first occurrence wins)
    seen = set()
    unique = []
    for c in candidates:
        key = c["claim_statement"][:80]
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

# Impact signals in claim text (protocol/system impact)
IMPACT_HIGH_RE = re.compile(
    r"\b(protocol.critical|constitutionally|must.*sign|canonical.*boundar|"
    r"invariant|hard.*constraint|Werner|productive.credit|post.issuance|"
    r"dual.token|gossip.coordinate|Levin.*adaptive|forward.comparable|"
    r"backward.private)\b",
    re.IGNORECASE,
)
IMPACT_MED_RE = re.compile(
    r"\b(CDL|ADM|epoch|governance|policy|shard|lifecycle|issuance|"
    r"ratif|prelock|treasury|bounty)\b",
    re.IGNORECASE,
)

# Agent pull signals
AGENT_HIGH_RE = re.compile(
    r"\b(agent|autonomous|digital.*agent|automation|OpenClaw|"
    r"agent.*operator|agent.*pull|mining.agent)\b",
    re.IGNORECASE,
)
AGENT_MED_RE = re.compile(
    r"\b(protocol|peer|API|interface|CLI|verification|node)\b",
    re.IGNORECASE,
)

# Novelty signals
NOVELTY_HIGH_RE = re.compile(
    r"\b(VRF|gossip.coordinate|Levin|Werner|policy.load|dual.token|"
    r"post.issuance|forward.comparable|backward.private|productive.credit|"
    r"CBDC|Sparkasse|Mittelstand|leasehold|transfer.tax|bounty.mechanism|"
    r"adaptive.gossip|topology.privacy|wallet.agnostic|secp256k1.*COSE|"
    r"organic.*resilience)\b",
    re.IGNORECASE,
)
NOVELTY_MED_RE = re.compile(
    r"\b(content.address|epoch|canonical|CDL|signer.lineage|"
    r"reputation.adjoint|node.schema)\b",
    re.IGNORECASE,
)


def score_impact(claim: str) -> int:
    high = len(IMPACT_HIGH_RE.findall(claim))
    med = len(IMPACT_MED_RE.findall(claim))
    return min(30, high * 6 + med * 2)


def score_agent(claim: str) -> int:
    high = len(AGENT_HIGH_RE.findall(claim))
    med = len(AGENT_MED_RE.findall(claim))
    return min(20, high * 5 + med * 2)


def score_novelty(claim: str) -> int:
    high = len(NOVELTY_HIGH_RE.findall(claim))
    med = len(NOVELTY_MED_RE.findall(claim))
    return min(20, high * 5 + med * 2)


def base_score(topic: str, strength: str) -> int:
    """
    Approximate base score using reverse-engineered formula.
    For unreviewed entries, we use conservative defaults:
      review=unreviewed (8), action=unset (0), alignment=unknown (3)
    to avoid inflating scores before triage.
    """
    return (
        TOPIC_BASE.get(topic, 6)
        + {"must": 30, "should": 20, "idea": 10}[strength]
        + 8   # review: unreviewed
        + 0   # action: not yet assigned
        + 3   # alignment: unknown
    )


def score_entry(entry: dict) -> dict:
    claim = entry["claim_statement"]
    topic = entry["topic"]
    strength = entry["normative_strength"]

    bs = base_score(topic, strength)
    impact = score_impact(claim)
    agent = score_agent(claim)
    novelty = score_novelty(claim)
    total = bs + impact + agent + novelty

    g7 = TOPIC_G7_DEFAULT.get(topic, 2)
    g8 = TOPIC_G8_DEFAULT.get(topic, 2)

    return {
        **entry,
        "base_score": bs,
        "impact_score": impact,
        "agent_score": agent,
        "novelty_score": novelty,
        "total_score": total,
        "g7_leverage": g7,
        "g8_agent_pull": g8,
        "g7g8_total": g7 + g8,
    }


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def write_jsonl(entries: list[dict], path: Path) -> None:
    with open(path, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    print(f"  Wrote {len(entries)} entries → {path}")


def write_matrix(entries: list[dict], path: Path, source_files: list[str]) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# ILC Constitutional Dredge Extension Matrix v0.1",
        f"",
        f"Generated: {now}",
        f"Source files: {len(source_files)}",
        f"Entries extracted: {len(entries)}",
        f"",
        f"## Source Files",
    ]
    for f in source_files:
        lines.append(f"- `{f}`")
    lines += [
        "",
        "## Status Note",
        "",
        "All entries have `status: unreviewed`. Run a triage pass to assign:",
        "`review_status` (reviewed/deferred/discarded), `alignment_status` (partial/missing/implemented/conflict),",
        "`action` (promote_clause/promote_guardrail/decision_log/todo/drop).",
        "After triage, re-run scoring to get final base_score including action/review/alignment components.",
        "",
        "## Entries (sorted by pre-triage total_score)",
        "",
        "| id | topic | strength | total | impact | agent | novelty | g7 | g8 | claim |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    sorted_entries = sorted(entries, key=lambda e: e["total_score"], reverse=True)
    for e in sorted_entries:
        claim_short = e["claim_statement"][:100].replace("|", "/")
        lines.append(
            f"| {e['id']} | {e['topic']} | {e['normative_strength']} "
            f"| {e['total_score']} | {e['impact_score']} | {e['agent_score']} "
            f"| {e['novelty_score']} | {e['g7_leverage']} | {e['g8_agent_pull']} "
            f"| {claim_short}... |"
        )
    path.write_text("\n".join(lines) + "\n")
    print(f"  Wrote matrix ({len(entries)} rows) → {path}")


def write_preranking(entries: list[dict], path: Path) -> None:
    """
    Pre-ranking focused on novelty + agent pull — highlights ideas not in original corpus.
    Useful before triage to find the highest-value new concepts.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Cluster by topic
    by_topic: dict[str, list[dict]] = {}
    for e in entries:
        by_topic.setdefault(e["topic"], []).append(e)

    lines = [
        f"# ILC Constitutional Dredge Extension — Pre-Triage Ranking v0.1",
        f"",
        f"Generated: {now}",
        f"Purpose: identify highest-novelty + highest-agent-pull concepts in new source material.",
        f"Note: base_score uses conservative unreviewed defaults. Re-score after triage.",
        f"",
        "## Top 20 by Total Score (pre-triage)",
        "",
        "| rank | id | topic | total | novelty | agent | claim |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    top20 = sorted(entries, key=lambda e: e["total_score"], reverse=True)[:20]
    for i, e in enumerate(top20, 1):
        claim_short = e["claim_statement"][:120].replace("|", "/")
        lines.append(
            f"| {i} | {e['id']} | {e['topic']} | {e['total_score']} "
            f"| {e['novelty_score']} | {e['agent_score']} | {claim_short}... |"
        )

    lines += [
        "",
        "## Top 10 by Novelty Score",
        "",
        "| rank | id | topic | novelty | claim |",
        "|---|---|---|---:|---|",
    ]
    top_novelty = sorted(entries, key=lambda e: e["novelty_score"], reverse=True)[:10]
    for i, e in enumerate(top_novelty, 1):
        claim_short = e["claim_statement"][:120].replace("|", "/")
        lines.append(
            f"| {i} | {e['id']} | {e['topic']} | {e['novelty_score']} | {claim_short}... |"
        )

    lines += [
        "",
        "## Top 10 by G7+G8 (Leverage + Agent Pull)",
        "",
        "| rank | id | topic | g7 | g8 | total_g7g8 | claim |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    top_leverage = sorted(
        entries, key=lambda e: (e["g7g8_total"], e["total_score"]), reverse=True
    )[:10]
    for i, e in enumerate(top_leverage, 1):
        claim_short = e["claim_statement"][:120].replace("|", "/")
        lines.append(
            f"| {i} | {e['id']} | {e['topic']} | {e['g7_leverage']} "
            f"| {e['g8_agent_pull']} | {e['g7g8_total']} | {claim_short}... |"
        )

    lines += [
        "",
        "## By Topic",
        "",
    ]
    for topic in sorted(by_topic, key=lambda t: TOPIC_BASE.get(t, 0), reverse=True):
        topic_entries = sorted(
            by_topic[topic], key=lambda e: e["total_score"], reverse=True
        )
        lines.append(f"### {topic} ({len(topic_entries)} entries)")
        lines.append("")
        lines.append("| id | total | novelty | claim |")
        lines.append("|---|---:|---:|---|")
        for e in topic_entries[:8]:
            claim_short = e["claim_statement"][:100].replace("|", "/")
            lines.append(
                f"| {e['id']} | {e['total_score']} | {e['novelty_score']} | {claim_short}... |"
            )
        lines.append("")

    path.write_text("\n".join(lines) + "\n")
    print(f"  Wrote pre-ranking → {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="ILC Constitutional Dredge Extension")
    parser.add_argument(
        "files",
        nargs="+",
        help="Source files to process (.md, .txt)",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/research",
        help="Output directory for generated files (default: docs/research)",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.55,
        help="Minimum confidence threshold for inclusion (default: 0.55)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_entries: list[dict] = []
    processed_files: list[str] = []

    for file_path_str in args.files:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"  WARNING: file not found, skipping: {file_path}")
            continue

        print(f"  Processing: {file_path.name}")
        text = file_path.read_text(encoding="utf-8", errors="replace")
        candidates = extract_candidates(text, str(file_path))
        scored = [score_entry(c) for c in candidates]
        filtered = [e for e in scored if e["confidence"] >= args.min_confidence]

        print(f"    Extracted {len(candidates)} candidates → {len(filtered)} after filter")
        all_entries.extend(filtered)
        processed_files.append(str(file_path))

    if not all_entries:
        print("No entries extracted. Check input files.")
        return

    # Global dedup across all files (same claim in multiple docs)
    seen_claims: set[str] = set()
    deduped: list[dict] = []
    for e in all_entries:
        key = e["claim_statement"][:80]
        if key not in seen_claims:
            seen_claims.add(key)
            deduped.append(e)

    print(f"\n  Total: {len(all_entries)} entries → {len(deduped)} after cross-file dedup\n")

    # Write outputs
    jsonl_path = output_dir / "ilc_dredge_extension_raw_v0.1.jsonl"
    matrix_path = output_dir / "ilc_dredge_extension_matrix_v0.1.md"
    prerank_path = output_dir / "ilc_dredge_extension_preranking_v0.1.md"

    write_jsonl(deduped, jsonl_path)
    write_matrix(deduped, matrix_path, processed_files)
    write_preranking(deduped, prerank_path)

    print(f"\nDone. {len(deduped)} entries across {len(processed_files)} files.")
    print(f"Next step: run triage pass on {matrix_path.name} to assign action/review/alignment,")
    print(f"then re-score to get final breakthrough shortlist additions.")


if __name__ == "__main__":
    main()
