#!/usr/bin/env bash
set -euo pipefail

PATH=.venv/bin:$PATH

.venv/bin/pytest \
  tests/test_residual_numeric_hardening.py \
  tests/test_phase_641_residual_numeric_cleanup_and_closure.py \
  -q

.venv/bin/pytest \
  tests/test_phase_638_r2_shared_numeric_contract_cleanup.py \
  tests/test_protocol_mapper.py \
  tests/test_api.py \
  tests/test_phase_639_r2_protocol_runtime_adjacent_numeric_cleanup.py \
  tests/test_event_log_validators.py \
  tests/test_settlement_metrics.py \
  tests/test_ecu_active_layer_runtime.py \
  tests/test_ecu_active_layer_runtime_hardening.py \
  tests/test_phase_640_r3_numeric_companion_cleanup.py \
  tests/test_canon_export_validate.py \
  tests/test_canon_export_bundle_validate.py \
  tests/test_canon_export_bundle.py \
  tests/test_canon_export_format.py \
  -q
