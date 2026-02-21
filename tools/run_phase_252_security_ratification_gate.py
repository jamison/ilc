#!/usr/bin/env python3
"""Composed security ratification verification gate for Phase 252.

Verifies Phase-251 ratification integrity and regresses security-runtime behavior.

Contract:
- --dry-run: print commands only, exit 0
- --help/-h: print usage, exit 0
- unknown args: exit 2
- full execution: run commands in order, stop on first failure, exit 0 if all pass, else 1

Composed commands (must run in this exact order):
1. pytest tests/test_security_cdl_ratification_251.py -q
2. pytest tests/test_security_runtime_cross_cdl_interactions_244.py -q
3. python3 tools/run_phase_244_security_runtime_gate.py
4. python3 tools/run_phase_236_preflight.py
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
            name="phase 251 security CDL ratification tests",
            cmd=[py, "-m", "pytest", "tests/test_security_cdl_ratification_251.py", "-q"],
        ),
        GateCommand(
            name="phase 244 cross-CDL interaction tests",
            cmd=[py, "-m", "pytest", "tests/test_security_runtime_cross_cdl_interactions_244.py", "-q"],
        ),
        GateCommand(
            name="phase 244 security runtime gate",
            cmd=[py, "tools/run_phase_244_security_runtime_gate.py"],
        ),
        GateCommand(
            name="phase 236 preflight regression",
            cmd=[py, "tools/run_phase_236_preflight.py"],
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run phase 252 composed security ratification verification gate"
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    args, unknown = parser.parse_known_args(argv)

    if unknown:
        print(f"Unknown argument(s): {' '.join(unknown)}", file=sys.stderr)
        return 2

    commands = build_commands()

    if args.dry_run:
        print("Phase 252 security ratification gate dry-run:")
        for idx, item in enumerate(commands, start=1):
            print(f"{idx}. {item.name}: {shlex.join(item.cmd)}")
        return 0

    print("Phase 252 security ratification gate execution:")
    for idx, item in enumerate(commands, start=1):
        print(f"\n[{idx}/{len(commands)}] {item.name}")
        print(f"$ {shlex.join(item.cmd)}")
        result = subprocess.run(item.cmd, cwd=ROOT, check=False)
        if result.returncode != 0:
            print(f"-> FAIL (exit {result.returncode})")
            print("\nPhase 252 security ratification gate: FAIL")
            return 1
        print("-> PASS")

    print("\nPhase 252 security ratification gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
