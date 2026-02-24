#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


USAGE = (
    "Usage: run_mutation_canary_phase_297.py [--dry-run] [--help]\n"
    "\n"
    "Run deterministic mutation canary probes and verify that targeted tests kill each mutant.\n"
    "\n"
    "Options:\n"
    "  --dry-run  Print probe plan without mutating files.\n"
    "  --help     Show this help message.\n"
)


@dataclass(frozen=True)
class Probe:
    name: str
    path: Path
    old_token: str
    new_token: str
    command: tuple[str, ...]


PROBES = (
    Probe(
        name="lineage_rotated_authority_guard",
        path=Path("ilc_core/security/signer_lineage_runtime.py"),
        old_token="if entry.state not in {ACTIVE, RECOVERED}:",
        new_token="if entry.state not in {ACTIVE, RECOVERED, ROTATED}:",
        command=(
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_cdl_001_signer_lineage_runtime.py::"
            "TestVerifyCanonicalAuthorityStateGating::"
            "test_verify_canonical_authority_rejects_rotated_state",
        ),
    ),
    Probe(
        name="compromise_containment_sequence_order_guard",
        path=Path("ilc_core/security/key_compromise_runtime.py"),
        old_token=(
            "REQUIRED_CONTAINMENT_SEQUENCE: Tuple[str, str, str] = (\n"
            "    FREEZE_AUTHORITY,\n"
            "    QUARANTINE_LINEAGE,\n"
            "    SUSPEND_NEW_CANONICAL_SIGNATURES,\n"
            ")"
        ),
        new_token=(
            "REQUIRED_CONTAINMENT_SEQUENCE: Tuple[str, str, str] = (\n"
            "    QUARANTINE_LINEAGE,\n"
            "    FREEZE_AUTHORITY,\n"
            "    SUSPEND_NEW_CANONICAL_SIGNATURES,\n"
            ")"
        ),
        command=(
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_cdl_002_key_compromise_runtime.py::"
            "TestContainmentActionSequencing::test_containment_sequence_is_strict_and_ordered",
        ),
    ),
    Probe(
        name="non_target_phase_stamp_poisoning_guard",
        path=Path("docs/specs/ilc_constitutional_decision_log_v0.1.md"),
        old_token="ratified_phase: 273",
        new_token="ratified_phase: 277",
        command=(
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_cdl_030_ratification_277.py::test_non_target_rows_not_ratified_in_phase_277",
        ),
    ),
)


def _run_probe(probe: Probe) -> bool:
    original = probe.path.read_text(encoding="utf-8")
    if probe.old_token not in original:
        print(f"[{probe.name}] setup_error: token_not_found", file=sys.stderr)
        return False

    mutated = original.replace(probe.old_token, probe.new_token, 1)
    if mutated == original:
        print(f"[{probe.name}] setup_error: mutation_noop", file=sys.stderr)
        return False

    restored = False
    try:
        probe.path.write_text(mutated, encoding="utf-8")
        result = subprocess.run(
            list(probe.command),
            check=False,
            capture_output=True,
            text=True,
        )
        killed = result.returncode != 0
        status = "MUTATION_KILLED" if killed else "MUTATION_SURVIVED"
        print(f"[{probe.name}] {status} exit_code={result.returncode}")
        return killed
    finally:
        try:
            probe.path.write_text(original, encoding="utf-8")
            restored = True
        finally:
            if not restored:
                print(f"[{probe.name}] restore_error", file=sys.stderr)


def _run_dry() -> int:
    print("Dry run: mutation canary probe plan")
    for idx, probe in enumerate(PROBES, start=1):
        command_display = " ".join(probe.command)
        print(f"[{idx}/{len(PROBES)}] {probe.name}")
        print(f"  mutate: {probe.path}")
        print(f"  test:   {command_display}")
    return 0


def _run_full() -> int:
    print("Running mutation canary probes")
    results: list[bool] = []
    for idx, probe in enumerate(PROBES, start=1):
        print(f"[{idx}/{len(PROBES)}] {probe.name}")
        results.append(_run_probe(probe))

    if all(results):
        print("PASS: all mutation canary probes were killed by target tests")
        return 0

    failed = [probe.name for probe, ok in zip(PROBES, results) if not ok]
    print(f"FAIL: mutation canary probe failure(s): {', '.join(failed)}", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    args = argv[1:]
    if not args:
        return _run_full()
    if args == ["--help"]:
        print(USAGE, end="")
        return 0
    if args == ["--dry-run"]:
        return _run_dry()
    print(f"Unknown argument: {' '.join(args)}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
