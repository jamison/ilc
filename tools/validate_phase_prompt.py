#!/usr/bin/env python3
"""
Validate markdown phase prompt schema for Antigravity execution.

Usage:
  python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_141_g8_....md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FILENAME_RE = re.compile(
    r"^antigravity_prompt__phase_(?P<phase>\d+[a-z]{0,2}(?:_fix\d+[a-z]{0,2})?)_g(?P<group>\d+)_(?P<slug>[a-z0-9_]+)\.md$"
)
H1_RE = re.compile(r"^#\s+Phase\s+(?P<phase>\d+[a-z]{0,2}(?:[_-]Fix\d+[a-z]{0,2})?)-G(?P<group>\d+)\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^#{2,3}\s+(.+?)\s*$")
UNKNOWN_UNKNOWN_DISCOVERY_PHASE_FLOOR = 1249
UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS = (
    "### §0a — Known-token audit",
    "### §0b — Concept-discovery search",
    "### §0c — Contradiction and non-claim search",
    "### §0d — Source expansion and newly discovered tokens",
)

# Every phase at or above this number must include an explicit LMDB node
# registration section declaring graph node records for all new files
# created in docs/specs/, docs/antigravity_tasks/, ilc_core/, tools/, tests/.
# Enforces the Graph Intake Protocol (CLAUDE.md) — prevents coverage deficit.
LMDB_NODE_REGISTRATION_PHASE_FLOOR = 1545


def _norm_heading(s: str) -> str:
    s = s.strip().lower().rstrip(":")
    s = re.sub(r"\s+", " ", s)
    return s


def _extract_h1(text: str) -> str | None:
    for line in text.splitlines():
        if line.strip().startswith("# "):
            return line.strip()
    return None


def _extract_headings(text: str) -> set[str]:
    out: set[str] = set()
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if not m:
            continue
        out.add(_norm_heading(m.group(1)))
    return out


def _require_any(headings: set[str], choices: tuple[str, ...]) -> bool:
    return any(c in headings for c in choices)


def _require_prefix_any(headings: set[str], prefixes: tuple[str, ...]) -> bool:
    for h in headings:
        for p in prefixes:
            if h.startswith(p):
                return True
    return False


def validate(path: Path) -> list[str]:
    errors: list[str] = []

    if not path.exists():
        return [f"file_not_found: {path}"]

    name_m = FILENAME_RE.match(path.name)
    if not name_m:
        errors.append("invalid_filename_pattern")
        return errors

    expected_phase = name_m.group("phase")
    expected_group = name_m.group("group")

    text = path.read_text(encoding="utf-8")

    h1 = _extract_h1(text)
    if not h1:
        errors.append("missing_h1_title")
    else:
        h1_m = H1_RE.match(h1)
        if not h1_m:
            errors.append("invalid_h1_pattern")
        else:
            if h1_m.group("phase").replace("-", "_").lower() != expected_phase.lower():
                errors.append(
                    f"h1_phase_mismatch: expected={expected_phase} got={h1_m.group('phase')}"
                )
            if h1_m.group("group") != expected_group:
                errors.append(
                    f"h1_group_mismatch: expected={expected_group} got={h1_m.group('group')}"
                )

    headings = _extract_headings(text)

    required_exact = (
        "mission",
        "scope",
        "deliverables",
        "walkthrough requirements",
        "status update requirements",
    )
    for req in required_exact:
        if req not in headings:
            errors.append(f"missing_section:{req}")

    if not (
        _require_any(headings, ("required inputs", "inputs to read first", "inputs"))
        or _require_prefix_any(headings, ("required inputs", "inputs to read first"))
    ):
        errors.append("missing_section:inputs")

    if not _require_any(
        headings, ("commands to run", "test commands", "verification commands")
    ):
        errors.append("missing_section:commands")

    if not _require_any(headings, ("commit", "commit message")):
        errors.append("missing_section:commit")

    # Soft content checks that materially reduce drift.
    if "No ellipses in walkthrough." not in text and "No ellipses in walkthrough" not in text:
        errors.append("missing_rule:no_ellipses_in_walkthrough")

    if "STATUS.md" not in text:
        errors.append("missing_reference:STATUS.md")

    expected_phase_number = int(re.match(r"\d+", expected_phase).group(0))
    if expected_phase_number >= UNKNOWN_UNKNOWN_DISCOVERY_PHASE_FLOOR:
        for section in UNKNOWN_UNKNOWN_DISCOVERY_SECTIONS:
            if section not in text:
                errors.append(f"missing_unknown_unknown_discovery_section:{section}")

    if expected_phase_number >= LMDB_NODE_REGISTRATION_PHASE_FLOOR:
        # Require a dedicated LMDB node registration section.
        # This enforces the Graph Intake Protocol: every new file in
        # docs/specs/, docs/antigravity_tasks/, ilc_core/, tools/, tests/
        # must be declared as a candidate LMDB node in the same commit.
        if "lmdb node registration" not in headings:
            errors.append("missing_section:lmdb_node_registration")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt_path", type=Path)
    args = parser.parse_args()

    errors = validate(args.prompt_path)
    if errors:
        print(f"INVALID: {args.prompt_path}")
        for e in errors:
            print(f"- {e}")
        return 1

    print(f"VALID: {args.prompt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
