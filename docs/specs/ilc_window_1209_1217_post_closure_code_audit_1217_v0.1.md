# Window 1209-1217 Post-Closure Deterministic Code Audit 1217 v0.1

**Date:** 2026-05-05
**Scope:** Implementation surfaces changed in Window 1209-1217
**Status:** AUDIT COMPLETE - TWO FINDINGS FIXED

`post_closure_code_audit_1217_verdict=pass_after_fixes`
`persistent_rate_limiter_audit_hardened_phase_1217`

---

## 1. Files Reviewed

- `ilc_core/economics/epoch_attribution_settle_runtime.py`
- `ilc_core/types.py`
- `ilc_core/network/d2d/http_fetch_transport_runtime.py`
- `ilc_core/network/d2d/persistent_fetch_rate_limiter_runtime.py`
- Phase 1210-1217 focused tests

Review focus: mathematical correctness, edge cases, input validation, memory/resource
safeguards, Decimal/float discipline, protocol-token observability, and threaded runtime
behavior.

---

## 2. Findings Fixed

### Finding 1 - Persistent limiter backend was not thread-safe

`HttpFetchTransportRuntime` uses `ThreadingHTTPServer`, but
`PersistentFetchRateLimiter` mutated `_buckets` and `_sequence` without a lock. Under
concurrent WANT-BLOCK requests, two threads could race through `check_and_consume()`.

Fix:

- Added `threading.RLock()` to `PersistentFetchRateLimiter`.
- Wrapped `check_and_consume()` and `save()` in the lock.
- Returned a copied state snapshot for deterministic serialization.
- Added concurrent consumption regression coverage.

### Finding 2 - Persistent state save failure could escape handler path

The persistent adapter saved state immediately after successful rate admission. If the
filesystem write failed, `OSError` could propagate out of the limiter call instead of
returning a stable fail-closed fetch response.

Fix:

- Catch `OSError` in the persistent adapter.
- Emit `persistent_rate_limiter_state_save_failed`.
- Return `False` so the existing WANT-BLOCK handler emits the stable 429 token
  `fetch_rate_limit_exceeded`.
- Added regression coverage.

---

## 3. No-Finding Areas

φ-bound enforcement:

- `epoch_node_mint_count` rejects non-int/bool and negative values.
- Ratio computation uses `Decimal`, not float.
- Threshold behavior matches the Phase 1210 example: with 5 node mints, the fourth
  PROVENANCE event is stripped because `3 / 5 = 0.60`.
- `EpochAttributionBatch.settle()` forwards `epoch_node_mint_count`.
- Zero-count compatibility path emits
  `edge_mint_phi_bound_enforcement_skipped_no_node_mints` when `emitted_tokens` is supplied.

Fetch transport:

- In-memory limiter remains default.
- Persistent limiter remains opt-in.
- WANT-HAVE remains unrate-limited.
- Load failures remain fail-closed and observable through
  `persistent_rate_limiter_state_reset_on_load_failure`.

---

## 4. Residual Design Notes

- `epoch_node_mint_count=0` remains a backward-compatible skip path by design. Callers that
  care about enforcement must pass `emitted_tokens` and a real epoch node-mint count.
- The static limiter remains only an abuse circuit breaker. The carry-forward remains:
  `reciprocal_fetch_admission_model_required`.
- The persistent state schema version was not changed because the audit fix changes
  concurrency and error handling, not serialized state shape.

---

## 5. Verification

Added:

- `tests/test_phase_1217_post_closure_audit_hardening.py`
- Additional save-failure regression in `tests/test_phase_1212_rate_limiter_wiring.py`

Expected verification command:

```bash
.venv/bin/python -m pytest \
  tests/test_phase_1210_phi_bound_enforcement.py \
  tests/test_phase_1212_rate_limiter_wiring.py \
  tests/test_phase_1217_post_closure_audit_hardening.py \
  tests/test_sensitive_runtime_coding_taboos.py -q
```

`post_closure_code_audit_1217_verdict=pass_after_fixes`
