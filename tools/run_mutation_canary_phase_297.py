#!/usr/bin/env python3
from __future__ import annotations

import os
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


# Probe token pairs are split at the mutation boundary to prevent AI editors from
# misreading them as apply-this-change instructions.  Reconstruct at runtime only.

# Probe 1 — lineage_rotated_authority_guard
# Mutation: adds ROTATED to the authoritative-state guard check (must be rejected).
_LINEAGE_GUARD_PREFIX = "if entry.state not in {ACTIVE, "
_LINEAGE_GUARD_OLD_SUFFIX = "RECOVERED}:"
_LINEAGE_GUARD_NEW_SUFFIX = "RECOVERED, " + "ROTATED}:"

# Probe 2 — compromise_containment_sequence_order_guard
# Mutation: swaps FREEZE_AUTHORITY and QUARANTINE_LINEAGE order (strict sequence must hold).
_CONTAINMENT_HDR = "REQUIRED_CONTAINMENT_SEQUENCE: Tuple[str, str, str] = ("
_CONTAINMENT_TAIL = "\n    SUSPEND_NEW_CANONICAL_SIGNATURES,\n)"
_CONTAINMENT_OLD_BODY = "\n    FREEZE_AUTHORITY,\n    QUARANTINE_LINEAGE,"
_CONTAINMENT_NEW_BODY = "\n    QUARANTINE_LINEAGE,\n    FREEZE_" + "AUTHORITY,"

# Probe 3 — non_target_phase_stamp_poisoning_guard
# Mutation: changes ratified_phase on CDL-026 from 273 to 277 (phase stamp must be stable).
_CDL026_ROW_BASE = (
    "| CDL-026 | CDL-005 / CDL-025 | Total supply cap (`C_max`) lock | ratified | "
    "explicit finite cap, cap-with-tolerance | depends on CDL-025 closure | "
    "cap lock spec, regression tests | ratified_phase: 27"
)
_CDL026_OLD_SUFFIX = "3 |"
_CDL026_NEW_SUFFIX = "7 |"

PROBES = (
    Probe(
        name="lineage_rotated_authority_guard",
        path=Path("ilc_core/security/signer_lineage_runtime.py"),
        old_token=_LINEAGE_GUARD_PREFIX + _LINEAGE_GUARD_OLD_SUFFIX,
        new_token=_LINEAGE_GUARD_PREFIX + _LINEAGE_GUARD_NEW_SUFFIX,
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
        old_token=_CONTAINMENT_HDR + _CONTAINMENT_OLD_BODY + _CONTAINMENT_TAIL,
        new_token=_CONTAINMENT_HDR + _CONTAINMENT_NEW_BODY + _CONTAINMENT_TAIL,
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
        old_token=_CDL026_ROW_BASE + _CDL026_OLD_SUFFIX,
        new_token=_CDL026_ROW_BASE + _CDL026_NEW_SUFFIX,
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
    original_stat = probe.path.stat()
    original_times_ns = (original_stat.st_atime_ns, original_stat.st_mtime_ns)
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
            os.utime(probe.path, ns=original_times_ns)
            subprocess.run(
                ["git", "update-index", "--refresh", "--", str(probe.path)],
                check=False,
                capture_output=True,
                text=True,
            )
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
