# Phase 1331 Fix2 - Economics Numeric and Canon Export Hardening

**Date:** 2026-05-14
**Status:** Complete
**Scope:** Scoped hardening before Phase 1332. This is not Phase 1332 execution.

```text
phase_1331_fix2_economics_numeric_canon_export.v0.1
economics_entropy_decimal_only_phase_1331_fix2
epoch_ledger_clearing_price_decimal_phase_1331_fix2
exact_numeric_float_boundary_rejected_phase_1331_fix2
proportional_payout_round_down_residual_phase_1331_fix2
settlement_verification_quantum_aligned_phase_1331_fix2
canon_export_atomic_write_phase_1331_fix2
phase_1332_final_deterministic_code_security_audit_still_next_after_fix2
public_rc_remains_blocked_after_phase_1331_fix2
```

## 1. Finding Disposition

| Audit item | Disposition |
|------------|-------------|
| C3/H1 entropy-to-reward float chain | Fixed. `entropy.py` and `reward.py` now use `Decimal` and reject float inputs at the helper boundary. |
| C4 clearing price float cast | Fixed. `SimpleEpochLedger.clearing_price()` now returns `Decimal` and no longer casts ECU/reward ratios to `float`. |
| H2/H3 payout rounding gaps | Fixed. Ejected-stake and co-authorship proportional payouts round down to `0.000000001` for computed shares and assign deterministic residual to the final sorted participant. |
| H4 settlement verification mismatch | Fixed. Settlement verification now uses the same rounded/residual distribution shape and quantum-aligned tolerance. |
| M1 exact numeric float acceptance | Fixed. `ExactNumberish` excludes `float`, and `to_decimal()` rejects finite and non-finite float input. |
| M15 canon export direct write | Fixed. `export_canon_state_json()` writes via same-directory `mkstemp` and publishes with `os.replace`. |

## 2. Deferred Items

The following audit findings remain out of this Fix2 scope:

- network DoS/SSRF-adjacent hardening: fetch rate-limiter eviction, chunked
  request body bounds, NDJSON `read_bundle` memory profile, gossip header length
  bound, private-address endpoint denial, and CBOR pre-load size caps;
- `reputation.py` Decimal/version-token/mutation-boundary rewrite;
- CCSS style/consistency cleanup not required for the economics/canon export
  path.

These remain inputs for Phase 1332 and later Fix routing.

## 3. Non-Authorization Boundary

This fix does not authorize Phase 1332 execution, public RC, public launch,
source allowlist export execution, source publication, public repository
publication, public package publication, clean public tree production, release
artifact production, release-key generation, release envelope production,
release signing material generation, signature production, release signing,
Genesis Atlas mutation/regeneration/signing, v0.2 signing, ATLAS-G-007,
ATLAS-G-008, ATLAS-G-009, ATLAS-G-010, CDL mutation, CDL-088 opening, identity
artifact creation, genesis record creation, seed commitment artifact creation,
dummy Agent Birth artifact creation, identity-seed generation, mnemonic
generation, private-key generation, secret-store write, public claimability
activation, public verifier service, public claim endpoint, public P2P, public
fetch serving, public ILC listener, peer discovery, non-loopback bind, public
sidecar/projection serving, public confidential messaging, public confidential
coordination serving, wallet-facing withdrawal request, wallet-facing transfer
request, wallet-facing spend request, wallet-provider signing,
wallet-provider ledger-write, wallet write, withdrawal runtime, ECU minting,
ILC settlement activation, value-path activation, counsel approval, patent
filing, CLA approval, trademark-policy publication, or legal conclusion.

## 4. Verification

```bash
.venv/bin/python -m pytest \
  tests/test_phase_1331_fix2_economics_numeric_and_canon_export.py \
  tests/test_entropy_reward.py \
  tests/test_reward_loop.py \
  tests/test_epoch_ledger.py \
  tests/test_exact_numeric.py \
  tests/test_settlement_verification.py \
  tests/test_canon_export.py \
  tests/test_canon_loader.py \
  tests/test_ledger_backend.py \
  tests/test_ledger_persistence.py \
  tests/test_lmdb_public_runtime_store.py \
  tests/test_phase_0947_h012_epoch_attribution_settle.py \
  tests/test_phase_1107_h_con_02_panel_quorum_settle.py

.venv/bin/python -m pytest \
  tests/test_tier0_numeric_hardening.py \
  tests/test_phase_635_tier0_exact_numeric_runtime_migration.py \
  tests/test_settlement_stability.py \
  tests/test_ledger_export.py \
  tests/test_settlement_metrics.py \
  tests/test_canon_export_validate.py \
  tests/test_canon_export_format.py \
  tests/test_canon_export_bundle.py \
  tests/test_canon_export_bundle_validate.py \
  tests/test_canon_export_cli.py \
  tests/test_devnet_multi_epoch.py \
  tests/test_protocol_mapper.py \
  tests/test_protocol_event_export.py \
  tests/test_event_log.py

python3 -m py_compile \
  ilc_core/economics/entropy.py \
  ilc_core/economics/reward.py \
  ilc_core/economics/epoch_ledger.py \
  ilc_core/economics/epoch_attribution_settle_runtime.py \
  ilc_core/ledger/settlement_verification.py \
  ilc_core/ledger/exact_numeric.py \
  ilc_core/ledger/canon_export.py \
  ilc_core/ledger/backend.py

python3 tools/check_sensitive_runtime_coding_taboos.py
```
