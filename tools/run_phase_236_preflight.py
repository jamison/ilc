#!/usr/bin/env python3
"""Composed preflight gate for phases 230-235.

Contract:
- --dry-run: print commands only, exit 0
- --help: print usage, exit 0
- unknown args: argparse exit code 2
- full execution: exit 0 iff all commands pass; else exit 1
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
            name="validate phase 234 prompt",
            cmd=[
                py,
                "tools/validate_phase_prompt.py",
                "docs/antigravity_tasks/antigravity_prompt__phase_234_g8_constitution_cluster_a_sdk_boundary_contract_lock.md",
            ],
        ),
        GateCommand(
            name="phase 234 sdk boundary tests",
            cmd=[py, "-m", "pytest", "tests/test_sdk_boundary_contract_234.py", "-q"],
        ),
        GateCommand(
            name="phase 235 bootstrap runbook tests",
            cmd=[py, "-m", "pytest", "tests/test_bootstrap_operations_runbook_235.py", "-q"],
        ),
        GateCommand(
            name="phase 233 issuance governance tests",
            cmd=[py, "-m", "pytest", "tests/test_issuance_governance_plan_233.py", "-q"],
        ),
        GateCommand(
            name="no ellipses guardrail",
            cmd=[py, "-m", "pytest", "tests/test_no_ellipses_in_walkthroughs.py", "-q"],
        ),
        GateCommand(
            name="phase 230 reproducible build regression tests",
            cmd=[py, "-m", "pytest", "tests/test_reproducible_build_phase_230.py", "-q"],
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run composed preflight checks for phases 230-235")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    args = parser.parse_args()

    commands = build_commands()

    if args.dry_run:
        print("Phase 236 preflight dry-run:")
        for i, item in enumerate(commands, start=1):
            print(f"{i}. {item.name}: {shlex.join(item.cmd)}")
        return 0

    print("Phase 236 preflight execution:")
    failures: list[str] = []
    for i, item in enumerate(commands, start=1):
        print(f"\n[{i}/{len(commands)}] {item.name}")
        print(f"$ {shlex.join(item.cmd)}")
        result = subprocess.run(item.cmd, cwd=ROOT, check=False)
        if result.returncode == 0:
            print("-> PASS")
        else:
            print(f"-> FAIL (exit {result.returncode})")
            failures.append(f"{item.name} (exit {result.returncode})")

    if failures:
        print("\nPhase 236 preflight: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nPhase 236 preflight: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
