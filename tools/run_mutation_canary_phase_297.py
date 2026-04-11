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

# Probe 4 — centrality_delta_gossip_version_guard
# Mutation: changes the ratified Phase 548 runtime version constant.
_CDL060_GOSSIP_VERSION_LINE = (
    'CDL_060_GOSSIP_RUNTIME_VERSION = "cdl_060_gossip_runtime_548.v0.1"'
)
_CDL060_GOSSIP_VERSION_MUTANT = (
    'CDL_060_GOSSIP_RUNTIME_VERSION = "cdl_060_gossip_runtime_548.v9.9"'
)

# Probe 5 — centrality_delta_gossip_d2d_dependency_guard
# Mutation: changes the D2d dependency constant away from the ratified Phase 382 token.
_CDL060_D2D_DEPENDENCY_LINE = 'D2D_GOSSIP_DEPENDENCY = "d2d_gossip_382.v0.1"'
_CDL060_D2D_DEPENDENCY_MUTANT = 'D2D_GOSSIP_DEPENDENCY = "d2d_gossip_999.v0.1"'

# Probe 6 — gossip_transport_cdl_039_forbidden_key_guard
# Mutation: removes "creator_agent_id" from FORBIDDEN_HEADER_KEYS set.
_TRANSPORT_FORBIDDEN_PREFIX = 'FORBIDDEN_HEADER_KEYS = frozenset({\n    "'
_TRANSPORT_FORBIDDEN_OLD = 'creator_agent_id",'
_TRANSPORT_FORBIDDEN_NEW = 'REMOVED_FOR_MUTATION",'

# Probe 7 — gossip_transport_version_guard
# Mutation: changes the Phase 558 transport runtime version constant.
_TRANSPORT_VERSION_LINE = (
    'GOSSIP_TRANSPORT_RUNTIME_VERSION = "gossip_transport_runtime_558.v0.1"'
)
_TRANSPORT_VERSION_MUTANT = (
    'GOSSIP_TRANSPORT_RUNTIME_VERSION = "gossip_transport_runtime_558.v9.9"'
)

# Probe 8 — gossip_transport_cdl_061_dep_guard
# Mutation: changes CDL-061 dep constant away from the ratified Phase 561 token.
_TRANSPORT_CDL061_DEP_LINE = 'CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"'
_TRANSPORT_CDL061_DEP_MUTANT = 'CDL_061_DEPENDENCY = "cdl_061_ratified_999.v0.1"'

# Probe 9 — http_gossip_transport_runtime_version_guard
# Mutation: changes the Phase 568 real HTTP transport runtime version constant.
_HTTP_GOSSIP_RUNTIME_VERSION_LINE = (
    'HTTP_GOSSIP_TRANSPORT_RUNTIME_VERSION = "http_gossip_transport_runtime_568.v0.1"'
)
_HTTP_GOSSIP_RUNTIME_VERSION_MUTANT = (
    'HTTP_GOSSIP_TRANSPORT_RUNTIME_VERSION = "http_gossip_transport_runtime_568.v9.9"'
)

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
    Probe(
        name="centrality_delta_gossip_version_guard",
        path=Path("ilc_core/network/d2d/centrality_delta_gossip_runtime.py"),
        old_token=_CDL060_GOSSIP_VERSION_LINE,
        new_token=_CDL060_GOSSIP_VERSION_MUTANT,
        command=(
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_phase_548_centrality_delta_gossip_runtime.py::test_exact_constant_values_are_locked",
        ),
    ),
    Probe(
        name="centrality_delta_gossip_d2d_dependency_guard",
        path=Path("ilc_core/network/d2d/centrality_delta_gossip_runtime.py"),
        old_token=_CDL060_D2D_DEPENDENCY_LINE,
        new_token=_CDL060_D2D_DEPENDENCY_MUTANT,
        command=(
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_phase_548_centrality_delta_gossip_runtime.py::test_exact_constant_values_are_locked",
        ),
    ),
    Probe(
        name="gossip_transport_cdl_039_forbidden_key_guard",
        path=Path("ilc_core/network/d2d/gossip_transport.py"),
        old_token=_TRANSPORT_FORBIDDEN_PREFIX + _TRANSPORT_FORBIDDEN_OLD,
        new_token=_TRANSPORT_FORBIDDEN_PREFIX + _TRANSPORT_FORBIDDEN_NEW,
        command=(
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_phase_559_gossip_transport_hardening.py::test_cdl_039_creator_agent_id_is_in_forbidden_set",
        ),
    ),
    Probe(
        name="gossip_transport_version_guard",
        path=Path("ilc_core/network/d2d/gossip_transport.py"),
        old_token=_TRANSPORT_VERSION_LINE,
        new_token=_TRANSPORT_VERSION_MUTANT,
        command=(
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_phase_558_gossip_transport_adapter.py::test_all_constants_have_exact_expected_values",
        ),
    ),
    Probe(
        name="gossip_transport_cdl_061_dep_guard",
        path=Path("ilc_core/network/d2d/gossip_transport.py"),
        old_token=_TRANSPORT_CDL061_DEP_LINE,
        new_token=_TRANSPORT_CDL061_DEP_MUTANT,
        command=(
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_phase_558_gossip_transport_adapter.py::test_all_constants_have_exact_expected_values",
        ),
    ),
    Probe(
        name="http_gossip_transport_runtime_version_guard",
        path=Path("ilc_core/network/d2d/http_gossip_transport_runtime.py"),
        old_token=_HTTP_GOSSIP_RUNTIME_VERSION_LINE,
        new_token=_HTTP_GOSSIP_RUNTIME_VERSION_MUTANT,
        command=(
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_phase_568_real_http_transport_wrapper_runtime.py::"
            "test_module_imports_and_exposes_exact_constants",
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
            subprocess.run(
                ["git", "checkout", "HEAD", "--", str(probe.path)],
                check=False,
                capture_output=True,
                text=True,
            )
            os.utime(probe.path, ns=original_times_ns)
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


def _reset_all_probe_targets() -> None:
    """Hard-reset all probe target files to HEAD after the run completes."""
    seen: set[Path] = set()
    for probe in PROBES:
        if probe.path not in seen:
            seen.add(probe.path)
            subprocess.run(
                ["git", "checkout", "HEAD", "--", str(probe.path)],
                check=False,
                capture_output=True,
                text=True,
            )


def _run_full() -> int:
    print("Running mutation canary probes")
    results: list[bool] = []
    try:
        for idx, probe in enumerate(PROBES, start=1):
            print(f"[{idx}/{len(PROBES)}] {probe.name}")
            results.append(_run_probe(probe))
    finally:
        _reset_all_probe_targets()

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
