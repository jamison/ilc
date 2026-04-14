#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PATH=.venv/bin:$PATH .venv/bin/pytest \
  tests/test_phase_650_public_init_admission_runtime.py \
  tests/test_phase_651_public_receipt_runtime.py \
  tests/test_phase_652_ecu_ilc_lifecycle_runtime.py \
  tests/test_phase_653_public_wallet_runtime_integration.py \
  tests/test_phase_654_window_649_654_closure_and_handoff.py \
  -q
