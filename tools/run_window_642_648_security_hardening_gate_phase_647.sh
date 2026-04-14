#!/usr/bin/env bash
set -euo pipefail

PATH=.venv/bin:$PATH .venv/bin/pytest \
  tests/test_phase_643_remaining_float_and_security_inventory.py \
  tests/test_canon_export_bundle_sign.py \
  tests/test_canon_bundle_pipeline.py \
  tests/test_phase_644_canonical_json_and_signature_boundary_hardening.py \
  tests/test_phase_532_aesthetic_panel_runtime.py \
  tests/test_phase_550_passive_ecu_attribution_runtime.py \
  tests/test_phase_551_passive_ecu_attribution_hardening.py \
  tests/test_phase_435_runtime_tranche_peer_fanout_integration.py \
  tests/test_phase_645_prng_timeout_and_invariant_enforcement_hardening.py \
  tests/test_ndjson_bundle.py \
  tests/test_ep_task_cli.py \
  tests/test_phase_646_ndjson_ingress_and_operational_boundary_hardening.py \
  -q
