#!/usr/bin/env python3
"""Composed security runtime gate for phases 240-243 runtime surfaces.

Contract:
- --dry-run: print commands only, exit 0
- --help/-h: print usage, exit 0
- unknown args: explicit exit code 2
- full execution: run commands in order, stop on first failure, exit 0 if all pass, else 1
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class GateCommand:
    name: str
    cmd: list[str]


def build_commands() -> list[GateCommand]:
    py = sys.executable
    return [
        GateCommand(
            name="phase 240 lineage schema tests",
            cmd=[py, "-m", "pytest", "tests/test_lineage_event_schema_phase_240.py", "-q"],
        ),
        GateCommand(
            name="phase 240 sequence lock tests",
            cmd=[py, "-m", "pytest", "tests/test_security_runtime_sequence_240.py", "-q"],
        ),
        GateCommand(
            name="phase 241 CDL-001 runtime tests",
            cmd=[py, "-m", "pytest", "tests/test_cdl_001_signer_lineage_runtime.py", "-q"],
        ),
        GateCommand(
            name="phase 242 CDL-002 runtime tests",
            cmd=[py, "-m", "pytest", "tests/test_cdl_002_key_compromise_runtime.py", "-q"],
        ),
        GateCommand(
            name="phase 243 CDL-007 runtime tests",
            cmd=[py, "-m", "pytest", "tests/test_cdl_007_rollback_resistance_runtime.py", "-q"],
        ),
        GateCommand(
            name="phase 244 cross-CDL interaction tests",
            cmd=[py, "-m", "pytest", "tests/test_security_runtime_cross_cdl_interactions_244.py", "-q"],
        ),
        GateCommand(
            name="phase 236 preflight regression",
            cmd=[py, "tools/run_phase_236_preflight.py"],
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run phase 244 composed security runtime gate")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    args, unknown = parser.parse_known_args(argv)

    if unknown:
        print(f"Unknown argument(s): {' '.join(unknown)}", file=sys.stderr)
        return 2

    commands = build_commands()

    if args.dry_run:
        print("Phase 244 security runtime gate dry-run:")
        for idx, item in enumerate(commands, start=1):
            print(f"{idx}. {item.name}: {shlex.join(item.cmd)}")
        return 0

    print("Phase 244 security runtime gate execution:")
    for idx, item in enumerate(commands, start=1):
        print(f"\n[{idx}/{len(commands)}] {item.name}")
        print(f"$ {shlex.join(item.cmd)}")
        result = subprocess.run(item.cmd, cwd=ROOT, check=False)
        if result.returncode != 0:
            print(f"-> FAIL (exit {result.returncode})")
            print("\nPhase 244 security runtime gate: FAIL")
            return 1
        print("-> PASS")

    print("\nPhase 244 security runtime gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
