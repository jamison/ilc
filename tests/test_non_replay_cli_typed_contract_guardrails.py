from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "ilc_core/cli/canon_consumer.py",
    ROOT / "ilc_core/cli/ep_task_cli.py",
]

BANNED_PATTERNS = [
    re.compile(r"\bAny\b"),
    re.compile(r"Dict\[str,\s*Any\]"),
    re.compile(r"->\s*Any\b"),
    re.compile(r"client:\s*Any\b"),
]

ALLOWLIST: dict[str, set[str]] = {}


def test_no_loose_any_contracts_in_non_replay_cli_surfaces() -> None:
    offenders: list[str] = []
    for path in TARGETS:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        for idx, line in enumerate(text.splitlines(), start=1):
            for pattern in BANNED_PATTERNS:
                if pattern.search(line):
                    if line.strip() in ALLOWLIST.get(rel, set()):
                        continue
                    offenders.append(f"{rel}:{idx}: {line.strip()}")

    if offenders:
        raise AssertionError(
            "Loose Any-based contracts found in non-replay CLI surfaces:\n"
            + "\n".join(offenders)
        )
