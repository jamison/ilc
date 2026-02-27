# ILC Crypto Asymmetric Dual-Verify Cutoff Handoff 285 v0.1

Status: Phase-285 implementation handoff artifact  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Tranche scope and touched surfaces

Phase 285 adds explicit verification-mode controls on migrated signing surfaces:
- `ilc_core/ledger/canon_export_bundle_verify_sig.py`,
- `ilc_core/ledger/canon_bundle_key_registry.py`,
- `ilc_core/ledger/canon_bundle_key_registry_channel_signing.py`,
- regression tests for bundle/registry/channel verification behavior.

No decision-log files were modified in this tranche.

## 2. Implemented cutoff behavior

Implemented behavior:
1. Verification paths now accept explicit mode values:
   - `compatibility`,
   - `asymmetric_required`.
2. `compatibility` mode preserves bounded legacy acceptance for artifacts missing canonical fingerprint.
3. `asymmetric_required` mode fails closed when canonical fingerprint metadata is missing.
4. Invalid mode values are rejected deterministically.

## 3. No-silent-fallback guarantee

No-silent-fallback guarantee is enforced by contract tests:
- asymmetric-required mode does not fallback to compatibility acceptance,
- compatibility behavior is available only when explicitly requested.

## 4. Verification summary

Executed checks:
- `tests/test_crypto_migration_bundle_registry_completion_284.py`,
- `tests/test_canon_export_bundle_verify_sig.py`,
- `tests/test_canon_bundle_key_registry_signing.py`,
- `tests/test_canon_bundle_key_registry_channel_signing.py`,
- `tests/test_crypto_asymmetric_dual_verify_cutoff_285.py`.

All listed checks passed for this tranche.

## 5. Rollback boundary

Rollback boundary:
- rollback to compatibility mode is explicit mode selection,
- no implicit runtime downgrade from asymmetric-required mode is allowed.

## 6. Non-goals

This phase does not:
- mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- replace HMAC with asymmetric signatures,
- remove compatibility fields from artifacts.

## 7. Canonical anchors and next-step recommendation

Canonical anchors:
- `docs/specs/ilc_ledger_signature_migration_contract_282_v0.1.md`
- `docs/specs/ilc_crypto_migration_initial_tranche_handoff_283_v0.1.md`
- `docs/specs/ilc_crypto_bundle_registry_completion_handoff_284_v0.1.md`

Next-step recommendation:
- open Phase 286 sequence lock for 286-295 window, with `280-pre1` prerequisite placement before CDL-031 evidence closure.
