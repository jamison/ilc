from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "ilc_core/cli/canon_cluster_a_replay_proof.py",
    ROOT / "ilc_core/protocol/ilc_cluster_a_replay_proof_package.py",
    ROOT / "ilc_core/protocol/ilc_cluster_a_replay_proof_batch.py",
    ROOT / "ilc_core/protocol/ilc_cluster_a_replay_proof_batch_compare.py",
    ROOT / "ilc_core/protocol/ilc_cluster_a_replay_proof_batch_ops.py",
    ROOT / "ilc_core/protocol/ilc_cluster_a_replay_proof_ci_gate.py",
]

BANNED_PATTERNS = [
    re.compile(r"Mapping\[str,\s*Any\]"),
    re.compile(r"Dict\[str,\s*Any\]"),
    re.compile(r"dict\[str,\s*Any\]"),
    re.compile(r"->\s*Any\b"),
]

ALLOWLIST: dict[str, set[str]] = {}


def test_no_loose_any_contracts_in_replay_proof_surfaces() -> None:
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
            "Loose Any-based contracts found in replay-proof surfaces:\n"
            + "\n".join(offenders)
        )
