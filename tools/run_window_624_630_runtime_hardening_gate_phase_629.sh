#!/usr/bin/env bash
set -euo pipefail

PATH=.venv/bin:$PATH .venv/bin/pytest \
  tests/test_phase_628_ecu_active_layer_runtime_and_accounting_spec.py \
  tests/test_ecu_active_layer_runtime.py \
  tests/test_ecu_active_layer_runtime_hardening.py \
  tests/test_phase_629_ecu_active_layer_runtime_hardening_gate.py \
  -q

echo "PASS: window_624_630_runtime_hardening_gate_phase_629"
