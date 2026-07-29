#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 835 — settlement-path dry-run preflight tool.

Reads one or more node config JSON files and validates the settlement_path
gate logic locally, without starting a node or requiring live validators.

Mirrors the Rust check_settlement_path_gate logic from ilc_consensus/src/main.rs
so operators can verify their config before deploying.

Exit codes:
  0 — all configs passed
  1 — one or more configs failed

Token: settlement_gate_preflight_835_published

Usage:
  python3 tools/settlement_gate_preflight.py --config node_config.json [--config n2.json ...]
  python3 tools/settlement_gate_preflight.py --config-dir tests/fixtures/phase_572_three_machine_smoke/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PREFLIGHT_VERSION = "settlement_gate_preflight_835.v0.1"

# Valid settlement_path values (must match Rust SettlementPath enum).
VALID_SETTLEMENT_PATH_VALUES = ("none", "", "mysticeti_fast_path")
MYSTICETI_VALUE = "mysticeti_fast_path"

# Minimum validator count required for MysticetiFastPath activation.
# f = (N-1) / 3; f >= 1 requires N >= 4.
MIN_VALIDATORS_FOR_FAST_PATH = 4


def _emit(marker: str) -> None:
    print(marker, flush=True)


def check_config(config_path: Path) -> bool:
    """Check one config file. Returns True on pass, False on fail.

    Token: settlement_gate_preflight_check_config
    """
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _emit(f"settlement_gate_preflight_config_read_error: {config_path.name}: {exc}")
        return False

    settlement_path = raw.get("settlement_path", "none") or "none"
    settlement_path = settlement_path.strip().lower()
    network_id = raw.get("network_id", "")
    node_id = raw.get("node_id", str(config_path.name))

    # Validate settlement_path value.
    if settlement_path not in VALID_SETTLEMENT_PATH_VALUES:
        _emit(
            f"settlement_gate_preflight_unknown_value: {node_id}: "
            f"settlement_path='{settlement_path}' — valid values are 'none' or 'mysticeti_fast_path'"
        )
        return False

    if settlement_path != MYSTICETI_VALUE:
        # None posture — always passes.
        _emit(f"settlement_gate_preflight_none_posture_preserved: {node_id}")
        return True

    # MysticetiFastPath — enforce prerequisites.
    errors: list[str] = []

    if not network_id:
        errors.append("non-empty network_id required for mysticeti_fast_path activation")

    # Validator-count check: count peers + self to estimate N.
    # Preflight uses the peer list as a proxy since the live validator set
    # is not available locally. Operators must confirm validator-set size
    # matches the live CDL-017-governed set.
    peers = raw.get("peers", [])
    n_estimated = len(peers) + 1  # peers + self
    f_estimated = (n_estimated - 1) // 3
    if f_estimated < 1:
        errors.append(
            f"sec_warn_settlement_gate_f_zero: estimated f={f_estimated} (N={n_estimated} from peer list) "
            f"— HIGH-002 applies; mysticeti_fast_path requires f>=1 (N>={MIN_VALIDATORS_FOR_FAST_PATH})"
        )

    if errors:
        for err in errors:
            _emit(f"settlement_gate_preflight_fail: {node_id}: {err}")
        return False

    _emit(
        f"settlement_gate_preflight_mysticeti_fast_path_ok: {node_id}: "
        f"network_id='{network_id}' estimated_f={f_estimated} "
        f"— Rollback: set settlement_path=none in config"
    )
    return True


def run(config_paths: list[Path]) -> int:
    """Run preflight on all configs. Returns exit code 0/1."""
    _emit(f"settlement_gate_preflight_version: {PREFLIGHT_VERSION}")
    results = []
    for path in config_paths:
        results.append(check_config(path))

    passed = sum(results)
    failed = len(results) - passed
    _emit(f"settlement_gate_preflight_summary: {passed} passed, {failed} failed")

    if failed == 0:
        _emit("settlement_gate_preflight_all_pass")
        return 0
    else:
        _emit("settlement_gate_preflight_fail_summary")
        return 1


def _collect_configs(args: argparse.Namespace) -> list[Path]:
    paths: list[Path] = []
    for c in args.config or []:
        p = Path(c)
        if not p.exists():
            print(f"settlement_gate_preflight_config_not_found: {c}", flush=True)
            sys.exit(1)
        paths.append(p)
    if args.config_dir:
        d = Path(args.config_dir)
        if not d.is_dir():
            print(f"settlement_gate_preflight_config_dir_not_found: {args.config_dir}", flush=True)
            sys.exit(1)
        paths.extend(sorted(d.glob("*_config.json")))
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Settlement-path dry-run preflight — Phase 835"
    )
    parser.add_argument(
        "--config",
        action="append",
        metavar="JSON",
        help="Path to a node config JSON file (may be repeated)",
    )
    parser.add_argument(
        "--config-dir",
        metavar="DIR",
        help="Directory containing *_config.json files",
    )
    args = parser.parse_args()

    if not args.config and not args.config_dir:
        parser.error("At least one --config or --config-dir is required")

    paths = _collect_configs(args)
    if not paths:
        print("settlement_gate_preflight_no_configs_found", flush=True)
        sys.exit(1)

    sys.exit(run(paths))


if __name__ == "__main__":
    main()
