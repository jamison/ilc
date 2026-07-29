#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_MANIFEST = Path("docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json")
ACTIVE_WORKING_SET = Path("docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json")
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKTICK_RE = re.compile(r"`([^`]+)`")
PHASE_PREFIX_RE = re.compile(r"^Phase\s+\d+(?:-G\d+)?(?:\s+Fix\s+\d+)?[:\-]?\s*", re.IGNORECASE)
LOGIC_GATES = (
    ("G1", "Start from the highest relevant authority tier before descending."),
    ("G2", "Read retrieved files directly before relying on them."),
    ("G3", "Classify each source as canonical, planning, evidence, or historical."),
    ("G4", "Check alignment with the current capsule, handoff, and STATUS frontier."),
    ("G5", "Treat any wallet/payment/runtime boundary implication as a direct-read stop sign."),
    ("G6", "If higher-authority sources conflict, the higher-authority source wins."),
    ("G7", "Require execution evidence before treating runtime claims as settled."),
    ("G8", "Confirm whether an item is closed, carried forward, or still deferred."),
    ("G9", "Label planning or historical material as non-canonical provenance support."),
    ("G10", "Route boundary changes to the right governance/planning lane instead of smuggling them in."),
)


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_repo_paths(text: str, repo_root: Path) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for match in BACKTICK_RE.findall(text):
        candidate = match.strip()
        if not candidate:
            continue
        if "://" in candidate or candidate.startswith("/"):
            continue
        if "/" not in candidate:
            continue
        normalized = str(Path(candidate).as_posix())
        resolved = (repo_root / normalized).resolve()
        try:
            resolved.relative_to(repo_root.resolve())
        except ValueError:
            continue
        if resolved.is_file() and normalized not in seen:
            seen.add(normalized)
            paths.append(normalized)
    return paths


def classify_path_tier(path: str, manifest: dict) -> str | None:
    for tier_name, tier in manifest["tiers"].items():
        for entry in tier.get("include", []):
            if isinstance(entry, str) and path == entry:
                return tier_name
            if isinstance(entry, dict) and path == entry.get("path"):
                return tier_name
    return None


def suggest_queries(title: str, paths: list[str]) -> list[str]:
    queries: list[str] = []
    cleaned_title = PHASE_PREFIX_RE.sub("", title).strip()
    if cleaned_title:
        queries.append(cleaned_title)
    for path in paths[:5]:
        stem = Path(path).stem.replace("_", " ")
        if stem not in queries:
            queries.append(stem)
    return queries[:6]


def render_brief(doc_path: Path, manifest: dict, repo_root: Path) -> str:
    text = doc_path.read_text(encoding="utf-8")
    title = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), doc_path.name)
    paths = extract_repo_paths(text, repo_root)
    queries = suggest_queries(title, paths)

    lines = [
        f"# MemPalace Retrieval Brief - {doc_path.name}",
        "",
        "Advisory only. Direct repo reads remain authoritative.",
        "",
        "## Direct reads",
    ]
    if paths:
        for path in paths:
            tier = classify_path_tier(path, manifest) or "unclassified"
            lines.append(f"- `{path}` ({tier})")
    else:
        lines.append("- No direct repo paths extracted.")

    lines.extend(["", "## Suggested MemPalace queries"])
    if queries:
        for query in queries:
            lines.append(f"- `{query}`")
    else:
        lines.append("- No query suggestions generated.")

    lines.extend(["", "## Reviewer logic gates"])
    lines.append(
        "- Apply `docs/tools/mempalace/ilc_mempalace_logic_gate_profile_v0.1.md`"
        " before elevating retrieval output into planning or boundary claims."
    )
    for gate, text in LOGIC_GATES:
        lines.append(f"- `{gate}` - {text}")

    lines.extend([
        "",
        "## Standard follow-up checks",
        "- Provenance question: compare a tier-A current-frontier read with the lower-tier lineage hit before drafting.",
        "- Carry-forward question: confirm current `STATUS.md` plus the relevant handoff or sequence-lock file after retrieval.",
        "- Contradiction question: compare higher- and lower-tier hits explicitly and let the higher-authority source win.",
        "- If this brief influenced prompt drafting, window guidance, or an audit note, record the brief path as advisory provenance support.",
        "",
        "## Usage note",
        f"- Default current-frontier working set: `{ACTIVE_WORKING_SET.as_posix()}`.",
        "- Use tiered queries for provenance support.",
        "- Read returned repo files directly before drafting or answering.",
    ])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render an advisory MemPalace retrieval brief from a markdown document.")
    parser.add_argument("doc", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    manifest = load_manifest(args.manifest)
    brief = render_brief(args.doc, manifest, args.repo_root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(brief, encoding="utf-8")
    else:
        sys.stdout.write(brief)
    return 0


if __name__ == "__main__":
    sys.exit(main())
