# Phase 1224 Fix1 Post-Closure Code Audit Hardening v0.1

**Phase:** 1224 Fix1
**Window:** 1218-1224 post-closure audit
**Date:** 2026-05-06
**Status:** implemented

## 1. Scope

This fix1 record captures the deterministic post-closure code audit performed after
Window 1218-1224 closed. The audit reviewed recent runtime/security work against the
repo-local guardrails for protocol time, bounded remote input, canonical JSON, TLS
posture, and static guardrail coverage.

No CDL mutation, runtime economic parameter change, Genesis Atlas mutation, signing
ceremony, release-key generation, public repository publication, public release
distribution, public RC claim, or public launch claim occurred.

## 2. Findings Fixed

| Finding | Fix |
|---------|-----|
| D2D fetch/gossip clients disabled TLS verification by default | Restored verified TLS as the default. Self-signed/local testbed behavior now requires explicit opt-out: `ILC_D2D_INSECURE_SKIP_TLS_VERIFY=1` for truth-primitive fetch/gossip helpers or `TransportRuntimeConfig.verify_peer_tls=False` for the HTTP gossip runtime. |
| `want_block()` could silently return a truncated peer response | Added bounded response read that reads one byte beyond the cap and raises `FetchTransportError("fetch_response_too_large")` if exceeded. |
| Remote registry-bundle download and archive extraction were unbounded | Added download byte cap, archive member-count cap, and total extracted regular-file byte cap. |
| `handle_want_block_request()` derived serve-reputation epoch from wall clock | Replaced `int(time.time() // 60)` path with caller-supplied `serve_epoch`; HTTP fetch transport forwards `FetchTransportConfig.rate_limit_window_id`. |
| `FileLedgerBackend._atomic_write()` wrote non-canonical JSON | Added `sort_keys=True` and `allow_nan=False` to persistent ledger JSON writes. |
| Sensitive-runtime guardrail failed to detect `opener.open(..., timeout=...)` | Extended the checker to recognize URL opener instances and added relevant fetch/gossip files to the scanned timeout surface. |

## 3. Test Coverage

Added:

- `tests/test_phase_1224_fix1_post_closure_audit_hardening.py`

The new tests cover:

- verified TLS defaults and explicit insecure opt-outs;
- oversized `want_block()` response rejection;
- bounded registry download copy;
- bounded archive extraction;
- canonical ledger JSON writes and NaN rejection;
- removal of wall-clock serve-reputation epoch derivation;
- sensitive-runtime guardrail pass.

## 4. Verification Commands

```bash
.venv/bin/python -m pytest \
  tests/test_phase_1224_fix1_post_closure_audit_hardening.py \
  tests/test_sensitive_runtime_coding_taboos.py \
  -q
```

```bash
.venv/bin/python -m pytest \
  tests/test_phase_568_real_http_transport_wrapper_runtime.py \
  tests/test_phase_569_transport_hardening_and_http2_fallback.py \
  tests/test_phase_901_905_cdl_077_fetch.py \
  tests/test_phase_1218b_security_hardening.py \
  -q
```

```bash
.venv/bin/python -m pytest \
  tests/test_canon_bundle_key_registry_fetch.py \
  tests/test_canon_bundle_key_registry_channel_rollback.py \
  tests/test_ledger_persistence.py \
  tests/test_phase_1224_fix1_post_closure_audit_hardening.py \
  tests/test_sensitive_runtime_coding_taboos.py \
  -q
```

```bash
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
```

## 5. Tokens

`phase_1224_fix1_post_closure_code_audit_hardening_committed`
`phase_1224_fix1_sensitive_runtime_guardrail_restored`
