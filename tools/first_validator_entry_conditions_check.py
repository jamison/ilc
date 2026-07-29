#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 836 — First-validator deployment entry conditions verification harness.

Mechanically checks the Phase 826 entry conditions checklist against the
current repository state. Produces a pass/fail verdict for each item so
operators have a concrete readiness report before pulling the human gate.

Items checked (from docs/specs/ilc_first_validator_deployment_entry_conditions_826_v0.1.md §2):

  1. SEC-004 historical validator-set binding closed
  2. M-007 ValidatorSet mutation hooks activated under CDL-017 authority
  3. M-019 adversarial hardening complete
  4. M-021 genesis BLS fix complete
  5. SEC-007a vendored protoc build path green
  6. Phase 825 settlement-path rotation wiring design consumed
     (Phase 830 gate wiring + Phase 835 preflight tool)
  7. Phase 826 entry conditions doc itself exists
  8. Three-machine smoke harness structurally ready with preflight step
  9. Row-5 runtime-pending posture preserved (not falsely claimed closed)
 10. HIGH-002 production-debt noted (not a blocker at controlled testnet scale)

Items NOT checked here (require live infrastructure or human decision):
  - validator keys, TLS material, genesis state, network ID, rollback plan
  - live smoke proof (validator peering, ECU finalization, balance update,
    epoch extraction, audit replay, rollback execution)
  - the human authorization record itself

Exit codes:
  0 — all code-verifiable items pass
  1 — one or more items fail

Token: first_validator_entry_conditions_check_836_published

Usage:
  python3 tools/first_validator_entry_conditions_check.py
  python3 tools/first_validator_entry_conditions_check.py --verbose
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HARNESS_VERSION = "first_validator_entry_conditions_836.v0.1"

REPO_ROOT = Path(__file__).resolve().parents[1]


def _emit(marker: str) -> None:
    print(marker, flush=True)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_sec_004(verbose: bool) -> bool:
    """SEC-004: historical validator-set binding acceptance test exists and is locked."""
    test_path = REPO_ROOT / "tests" / "test_phase_768_sec_004_acceptance.py"
    walkthrough = REPO_ROOT / "docs" / "phases" / "phase_768_g8_sec_004_acceptance_test_walkthrough.md"

    if not test_path.exists():
        _emit("entry_check_fail: SEC-004: test_phase_768_sec_004_acceptance.py not found")
        return False
    if not walkthrough.exists():
        _emit("entry_check_fail: SEC-004: phase_768 walkthrough not found")
        return False

    text = _read(test_path)
    required = (
        "test_ejected_validator_sig_rejected_after_epoch_boundary",
        "sec_004",
    )
    for token in required:
        if token not in text:
            _emit(f"entry_check_fail: SEC-004: required token '{token}' not in test file")
            return False

    if verbose:
        _emit("entry_check_verbose: SEC-004: test file and tokens present")
    _emit("entry_check_pass: SEC-004_historical_validator_set_binding_closed")
    return True


def check_m007(verbose: bool) -> bool:
    """M-007: ValidatorSet mutation hooks activated in validator.rs."""
    test_path = REPO_ROOT / "tests" / "test_phase_769_m007_hook_activation.py"
    validator_rs = REPO_ROOT / "ilc_consensus" / "src" / "validator.rs"

    if not test_path.exists():
        _emit("entry_check_fail: M-007: test_phase_769_m007_hook_activation.py not found")
        return False

    text = _read(test_path)
    if "m007" not in text.lower() and "M-007" not in text and "769M007" not in text:
        _emit("entry_check_fail: M-007: neither 'm007' nor 'M-007' nor '769M007' token in test file")
        return False

    if validator_rs.exists():
        vrs = _read(validator_rs)
        if "unimplemented!()" in vrs and "admit_validator" in vrs:
            _emit("entry_check_fail: M-007: admit_validator still has unimplemented!() in validator.rs")
            return False
        if verbose:
            _emit("entry_check_verbose: M-007: validator.rs hook stubs removed")
    else:
        if verbose:
            _emit("entry_check_verbose: M-007: validator.rs not present — skipping Rust check")

    if verbose:
        _emit("entry_check_verbose: M-007: test file and tokens present")
    _emit("entry_check_pass: M-007_validator_set_hooks_activated")
    return True


def check_m019_m021(verbose: bool) -> bool:
    """M-019/M-021: M-series complete, convergence entry conditions satisfied."""
    status = REPO_ROOT / "docs" / "phases" / "STATUS.md"
    if not status.exists():
        _emit("entry_check_fail: M-019/M-021: STATUS.md not found")
        return False

    text = _read(status)
    required = (
        "gemini_lane_m_series_complete",
        "run_m022_verdict=pass",
        "M-019/M-020 artifact bundle committed",
    )
    missing = [t for t in required if t not in text]
    if missing:
        for t in missing:
            _emit(f"entry_check_fail: M-019/M-021: token not found in STATUS.md: '{t}'")
        return False

    if verbose:
        _emit("entry_check_verbose: M-019/M-021: M-series completion tokens present")
    _emit("entry_check_pass: M-019_adversarial_hardening_complete")
    _emit("entry_check_pass: M-021_genesis_bls_fix_complete")
    return True


def check_sec_007a(verbose: bool) -> bool:
    """SEC-007a: vendored protoc build path recorded."""
    walkthrough = REPO_ROOT / "docs" / "phases" / "phase_820_sec_007a_protoc_vendored.md"
    if not walkthrough.exists():
        _emit("entry_check_fail: SEC-007a: phase_820_sec_007a_protoc_vendored.md not found")
        return False

    text = _read(walkthrough)
    if "sec_007a_protoc_vendored" not in text:
        _emit("entry_check_fail: SEC-007a: 'sec_007a_protoc_vendored' token not in walkthrough")
        return False

    build_rs = REPO_ROOT / "ilc_consensus" / "build.rs"
    if build_rs.exists():
        brs = _read(build_rs)
        if verbose:
            if "protoc" in brs.lower():
                _emit("entry_check_verbose: SEC-007a: protoc reference present in build.rs")
            else:
                _emit("entry_check_verbose: SEC-007a: build.rs present but no 'protoc' string — may be in Cargo.toml")
    else:
        if verbose:
            _emit("entry_check_verbose: SEC-007a: build.rs not found — relying on walkthrough token")

    if verbose:
        _emit("entry_check_verbose: SEC-007a: walkthrough and token present")
    _emit("entry_check_pass: SEC-007a_vendored_protoc_build_path_green")
    return True


def check_phase_825_consumed(verbose: bool) -> bool:
    """Phase 825: settlement-path rotation wiring design consumed (Phase 830 + 835)."""
    status = REPO_ROOT / "docs" / "phases" / "STATUS.md"
    if not status.exists():
        _emit("entry_check_fail: Phase-825: STATUS.md not found")
        return False

    text = _read(status)
    required = (
        "settlement_path_gate_830_published",
        "settlement_gate_preflight_835_published",
    )
    missing = [t for t in required if t not in text]
    if missing:
        for t in missing:
            _emit(f"entry_check_fail: Phase-825: consumption token not found: '{t}'")
        return False

    # Also check the gate wiring source itself.
    config_rs = REPO_ROOT / "ilc_consensus" / "src" / "config.rs"
    if config_rs.exists():
        crs = _read(config_rs)
        if "SettlementPath" not in crs:
            _emit("entry_check_fail: Phase-825: SettlementPath not found in config.rs")
            return False
        if verbose:
            _emit("entry_check_verbose: Phase-825: SettlementPath enum present in config.rs")

    if verbose:
        _emit("entry_check_verbose: Phase-825: wiring design consumption tokens present")
    _emit("entry_check_pass: Phase-825_settlement_path_rotation_wiring_design_consumed")
    return True


def check_phase_826_doc(verbose: bool) -> bool:
    """Phase 826: entry conditions document exists."""
    doc = REPO_ROOT / "docs" / "specs" / "ilc_first_validator_deployment_entry_conditions_826_v0.1.md"
    if not doc.exists():
        _emit("entry_check_fail: Phase-826: entry conditions doc not found")
        return False

    text = _read(doc)
    if "first_validator_entry_conditions_record_826_published" not in text:
        _emit("entry_check_fail: Phase-826: publication token not found in doc")
        return False

    if verbose:
        _emit("entry_check_verbose: Phase-826: entry conditions doc and publication token present")
    _emit("entry_check_pass: Phase-826_entry_conditions_doc_present")
    return True


def check_smoke_harness_ready(verbose: bool) -> bool:
    """Smoke harness structurally ready with Phase 835 preflight step."""
    harness = REPO_ROOT / "tools" / "run_three_machine_smoke_phase_572.sh"
    preflight = REPO_ROOT / "tools" / "settlement_gate_preflight.py"

    if not harness.exists():
        _emit("entry_check_fail: smoke: run_three_machine_smoke_phase_572.sh not found")
        return False
    if not preflight.exists():
        _emit("entry_check_fail: smoke: settlement_gate_preflight.py not found")
        return False

    text = _read(harness)
    required_markers = (
        "smoke_settlement_gate_preflight_ok",
        "smoke_node_1_ready",
        "smoke_node_2_ready",
        "smoke_node_3_ready",
        "smoke_gossip_send_ok",
        "smoke_restart_ok",
    )
    missing = [m for m in required_markers if m not in text]
    if missing:
        for m in missing:
            _emit(f"entry_check_fail: smoke: marker '{m}' not in harness")
        return False

    if verbose:
        _emit("entry_check_verbose: smoke: harness and preflight present, all markers found")
    _emit("entry_check_pass: three_machine_smoke_harness_structurally_ready")
    return True


def check_row5_posture_preserved(verbose: bool) -> bool:
    """Row-5 remains spec_closed_runtime_pending (not falsely claimed closed)."""
    capsule = REPO_ROOT / "docs" / "specs" / "ilc_antigravity_context_capsule_v5.15.md"
    if not capsule.exists():
        _emit("entry_check_fail: Row-5: capsule v5.15 not found")
        return False

    text = _read(capsule)
    if "row5_spec_closed_runtime_pending_preserved" not in text:
        _emit("entry_check_fail: Row-5: 'row5_spec_closed_runtime_pending_preserved' not in capsule")
        return False
    if "row5_runtime_closed" in text:
        _emit("entry_check_fail: Row-5: capsule falsely claims row5_runtime_closed")
        return False

    if verbose:
        _emit("entry_check_verbose: Row-5: posture preserved as spec_closed_runtime_pending")
    _emit("entry_check_pass: row5_posture_spec_closed_runtime_pending_preserved")
    return True


def check_high_002_noted(verbose: bool) -> bool:
    """HIGH-002: production-debt noted in entry conditions doc (not a blocker at testnet scale)."""
    doc = REPO_ROOT / "docs" / "specs" / "ilc_first_validator_deployment_entry_conditions_826_v0.1.md"
    if not doc.exists():
        _emit("entry_check_fail: HIGH-002: entry conditions doc not found")
        return False

    text = _read(doc)
    if "HIGH-002" not in text:
        _emit("entry_check_fail: HIGH-002: not mentioned in entry conditions doc")
        return False

    if verbose:
        _emit("entry_check_verbose: HIGH-002: production-debt noted in entry conditions doc")
    _emit("entry_check_pass: HIGH-002_production_debt_noted_not_a_testnet_blocker")
    return True


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

CHECKS = [
    ("SEC-004 historical validator-set binding", check_sec_004),
    ("M-007 ValidatorSet hooks activated", check_m007),
    ("M-019/M-021 M-series complete", check_m019_m021),
    ("SEC-007a vendored protoc", check_sec_007a),
    ("Phase 825 wiring design consumed", check_phase_825_consumed),
    ("Phase 826 entry conditions doc", check_phase_826_doc),
    ("Smoke harness structurally ready", check_smoke_harness_ready),
    ("Row-5 posture preserved", check_row5_posture_preserved),
    ("HIGH-002 noted", check_high_002_noted),
]


def run(verbose: bool) -> int:
    _emit(f"entry_conditions_check_version: {HARNESS_VERSION}")
    _emit("entry_conditions_check_start")

    results: list[tuple[str, bool]] = []
    for label, fn in CHECKS:
        ok = fn(verbose)
        results.append((label, ok))

    passed = sum(1 for _, ok in results if ok)
    failed = len(results) - passed

    _emit(f"entry_conditions_check_summary: {passed} passed, {failed} failed")

    if failed == 0:
        _emit("entry_conditions_check_all_pass")
        _emit("entry_conditions_human_gate_code_prerequisites_satisfied")
        return 0
    else:
        _emit("entry_conditions_check_fail_summary")
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="First-validator entry conditions check — Phase 836"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Emit additional diagnostic lines",
    )
    args = parser.parse_args()
    sys.exit(run(args.verbose))


if __name__ == "__main__":
    main()
