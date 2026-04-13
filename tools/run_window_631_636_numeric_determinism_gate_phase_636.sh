#!/usr/bin/env bash
set -euo pipefail

PATH=.venv/bin:$PATH

.venv/bin/pytest \
  tests/test_tier0_numeric_hardening.py \
  tests/test_phase_636_tier0_numeric_hardening_and_closure.py \
  -q

.venv/bin/pytest \
  tests/test_exact_numeric.py \
  tests/test_phase_628_ecu_active_layer_runtime_and_accounting_spec.py \
  tests/test_ecu_active_layer_runtime.py \
  tests/test_ecu_active_layer_runtime_hardening.py \
  tests/test_phase_635_tier0_exact_numeric_runtime_migration.py \
  tests/test_ledger_backend.py \
  tests/test_settlement_verification.py \
  tests/test_ledger_export.py \
  tests/test_canon_export.py \
  tests/test_canon_loader.py \
  tests/test_phase_506_validator_staking_liveness_runtime.py \
  tests/test_lmdb_public_runtime_store.py \
  tests/test_ledger_persistence.py \
  tests/test_rc0_1_economic_cycle_runtime.py \
  -q
