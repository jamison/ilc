#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PATH=.venv/bin:$PATH .venv/bin/pytest \
  tests/test_phase_665_window_665_670_sequence_lock.py \
  tests/test_phase_666_transport_maturity_contract.py \
  tests/test_phase_667_transport_harness_and_vpn_canary_pack.py \
  tests/test_phase_668_transport_drill_execution.py \
  tests/test_phase_669_transport_hardening_and_maturity_decision.py \
  tests/test_phase_670_window_665_670_closure_and_handoff.py \
  -q
