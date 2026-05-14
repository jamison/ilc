# Phase 1331 Fix3 - Network DoS Hardening

**Date:** 2026-05-14
**Status:** Complete
**Scope:** Scoped hardening before Phase 1332. This is not Phase 1332 execution.

```text
phase_1331_fix3_network_dos_hardening.v0.1
fetch_rate_limiter_bucket_cap_phase_1331_fix3
http_gossip_chunked_transfer_rejected_phase_1331_fix3
ndjson_read_bundle_materialization_cap_phase_1331_fix3
gossip_type_header_length_bound_phase_1331_fix3
phase_1332_final_deterministic_code_security_audit_still_next_after_fix3
public_rc_remains_blocked_after_phase_1331_fix3
```

## 1. Finding Disposition

| Audit item | Disposition |
|------------|-------------|
| H6 fetch rate limiter bucket growth | Fixed. In-memory `FetchRateLimiter` now uses bounded `OrderedDict` buckets with configurable `max_buckets`, expired-window pruning, and FIFO eviction. |
| H7 chunked HTTP gossip body without content length | Fixed. HTTP gossip runtime rejects any `Transfer-Encoding` header fail-closed before body drain. |
| H8 `read_bundle()` materializes all streaming records | Fixed. `read_bundle()` now has a stricter `max_materialized_records` cap separate from `iter_bundle()` streaming caps and documents `iter_bundle()` as the large/untrusted path. |
| H9 gossip type header length unbounded | Fixed. `ILC-Gossip-Type` values are bounded by `MAX_GOSSIP_TYPE_BYTES` in path construction, header construction, and header validation. |

## 2. Deferred Items

This Fix3 does not resolve private-address endpoint denial, CBOR pre-load size
caps, `reputation.py` Decimal/version-token/mutation-boundary rewrite, or
low-urgency CCSS style/consistency cleanup. Those remain Phase 1332 audit
inputs and later fix-routing candidates.

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
  tests/test_phase_1331_fix3_network_dos_hardening.py \
  tests/test_phase_901_905_cdl_077_fetch.py \
  tests/test_phase_568_real_http_transport_wrapper_runtime.py \
  tests/test_phase_558_gossip_transport_adapter.py \
  tests/test_ndjson_bundle.py

.venv/bin/python -m pytest \
  tests/test_phase_1218b_security_hardening.py \
  tests/test_phase_1217_post_closure_audit_hardening.py \
  tests/test_phase_1212_rate_limiter_wiring.py \
  tests/test_phase_894_898_truth_primitive_gossip.py \
  tests/test_sensitive_runtime_coding_taboos.py \
  tests/test_window_1330_1342_prompt_drafts.py

python3 -m py_compile \
  ilc_core/network/d2d/truth_primitive_fetch_runtime.py \
  ilc_core/network/d2d/http_gossip_transport_runtime.py \
  ilc_core/network/d2d/gossip_transport.py \
  ilc_core/protocol/ndjson_bundle.py

python3 tools/check_sensitive_runtime_coding_taboos.py
```
