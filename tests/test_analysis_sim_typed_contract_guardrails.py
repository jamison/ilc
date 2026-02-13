from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = [ROOT / "ilc_core" / "analysis", ROOT / "ilc_core" / "sim"]

BANNED_PATTERNS = [
    re.compile(r"Mapping\[str,\s*Any\]"),
    re.compile(r"Dict\[str,\s*Any\]"),
    re.compile(r"List\[Dict\[str,\s*Any\]\]"),
    re.compile(r"\b_to_(float|int)\(value:\s*Any\b"),
]

ALLOWLIST: dict[str, set[str]] = {}


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for base in TARGET_DIRS:
        files.extend(sorted(base.rglob("*.py")))
    return files


def test_no_loose_any_contracts_in_analysis_and_sim() -> None:
    offenders: list[str] = []
    for path in _iter_python_files():
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
            "Loose Any-based contracts found in analysis/sim:\n"
            + "\n".join(offenders)
        )
