#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PATH=.venv/bin:$PATH .venv/bin/pytest \
  tests/test_phase_656_canon_export_and_registry_signature_reproducibility.py \
  tests/test_phase_657_registry_channel_promotion_sync_reproducibility.py \
  tests/test_phase_658_window_655_658_hardening_and_handoff.py \
  tests/test_canon_export_bundle_sign.py \
  tests/test_canon_bundle_key_registry_signing.py \
  tests/test_canon_bundle_key_registry.py \
  tests/test_canon_bundle_key_registry_bundle.py \
  tests/test_canon_bundle_key_registry_channel.py \
  tests/test_canon_bundle_key_registry_channel_signing.py \
  tests/test_canon_bundle_key_registry_promotion.py \
  tests/test_canon_bundle_key_registry_sync.py \
  tests/test_canon_bundle_key_registry_integration.py \
  tests/test_canon_bundle_key_registry_channel_rollback.py \
  -q

if rg -n 'datetime\.now|time\.time' \
  ilc_core/ledger/canon_export_bundle_sign.py \
  ilc_core/ledger/canon_bundle_key_registry.py \
  ilc_core/ledger/canon_bundle_key_registry_bundle.py \
  ilc_core/ledger/canon_bundle_key_registry_channel.py \
  ilc_core/ledger/canon_bundle_key_registry_channel_signing.py \
  ilc_core/ledger/canon_bundle_key_registry_promotion.py \
  ilc_core/ledger/canon_bundle_key_registry_sync.py
then
  echo "forbidden wall-clock call remains in touched signing/export lane" >&2
  exit 1
fi
