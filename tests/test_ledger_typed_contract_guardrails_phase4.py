from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "ilc_core/ledger/canon_bundle_key_registry_sync.py",
    ROOT / "ilc_core/ledger/ledger_export.py",
]

BANNED_PATTERNS = [
    re.compile(r"\bAny\b"),
    re.compile(r"Dict\[str,\s*Any\]"),
    re.compile(r"->\s*Any\b"),
]

REQUIRED_TYPED_MARKERS = [
    re.compile(r"\bTypeAlias\b"),
    re.compile(r"\bTypedDict\b"),
    re.compile(r"\bSourceAttempt\b"),
    re.compile(r"\bSyncResult\b"),
    re.compile(r"\bLedgerDistributionCheck\b"),
    re.compile(r"\bLedgerStateExport\b"),
]


def test_no_loose_any_contracts_in_ledger_phase4_targets() -> None:
    offenders: list[str] = []
    for path in TARGETS:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        for idx, line in enumerate(text.splitlines(), start=1):
            for pattern in BANNED_PATTERNS:
                if pattern.search(line):
                    offenders.append(f"{rel}:{idx}: {line.strip()}")

    if offenders:
        raise AssertionError(
            "Loose Any-based contracts found in phase4 ledger targets:\n"
            + "\n".join(offenders)
        )


def test_phase4_targets_define_explicit_typed_contract_markers() -> None:
    missing: list[str] = []
    for path in TARGETS:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if not any(pattern.search(text) for pattern in REQUIRED_TYPED_MARKERS):
            missing.append(rel)

    if missing:
        raise AssertionError("Missing typed-contract markers in:\n" + "\n".join(missing))
