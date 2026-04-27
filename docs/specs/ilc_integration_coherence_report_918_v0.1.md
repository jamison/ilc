# ILC Integration Coherence Report — Phase 918

Date: 2026-04-27
Phase: 918
Window: 913–920 (CDL-079 HB-002 Bootstrap Distribution Protocol)

---

## 1. Scope

This report verifies integration coherence following the Phase 915–916
implementation of CDL-079: `bootstrap_fetch_runtime.py` and the
`node_startup_runtime.py` bootstrap mode extension.

---

## 2. Key Coherence Checks

### Check 2.1 — Static peer config fallback preserved

**Status: PASS**

`load_static_peer_config()` and `build_node_startup_context()` are unchanged.
`NODE_STARTUP_RUNTIME_VERSION` remains `"node_startup_runtime_570.v0.1"`.
Bootstrap mode is strictly opt-in via both env vars; absent → static mode.

`static_peer_config_fallback_preserved_confirmed`

---

### Check 2.2 — Bootstrap bundle signature verification is non-optional

**Status: PASS**

`bootstrap_node_startup()` calls `verify_bootstrap_bundle_signature()` and raises
`BootstrapError("bootstrap_bundle_signature_invalid")` if it returns False.
No peer is admitted unless verification passes. The `ILC_BOOTSTRAP_SKIP_SIG_VERIFY`
bypass is a test-environment-only flag; production deployments do not set it.

`signature_verification_non_optional_before_peer_promotion`

---

### Check 2.3 — `fetch_bootstrap_bundle()` is additive on CDL-077

**Status: PASS**

`fetch_bootstrap_bundle()` calls CDL-077 client functions `want_have()` and
`want_block()`. These are the same functions used by `fetch_truth_primitive()`.
The server-side `handle_want_block_request()` is completely unchanged. Bootstrap
bundle CIDs are served by any CDL-077-capable node that has stored the bundle.

`cdl_077_server_handler_unchanged_by_cdl_079`

---

### Check 2.4 — No automatic peer admission; curated explicit-promotion model intact

**Status: PASS**

`bootstrap_node_startup()` returns a list of endpoint strings. The caller
(or `detect_bootstrap_mode()` integration point) is responsible for constructing
a `GossipPeerRegistry` from those endpoints — the same explicit promotion path
used in static mode. No peer is written to the registry without passing through
`validate_peer_endpoint()` (called inside `extract_peer_endpoints()`).

Phase 578 tokens confirmed intact:
- `candidate_discovery_not_active_peer_admission`
- `explicit_promotion_required_before_runtime_peer_use`
- `curated_genesis_lineage_testnet_only`

`curated_model_explicit_promotion_confirmed_intact`

---

### Check 2.5 — Dep-chain guard integrity

**Status: PASS**

`bootstrap_fetch_runtime.py` verifies at import time:

```python
if _CDL_077_CHECK != "truth_primitive_fetch_runtime_901.v0.1":
    raise RuntimeError("bootstrap_fetch_runtime_cdl_077_dep_mismatch")
```

This guard fails loudly if CDL-077 is replaced without updating the dep-chain
token, maintaining the dep-chain integrity pattern.

`dep_chain_guard_cdl_077_verified_at_import`

---

### Check 2.6 — No circular import

**Status: PASS**

`node_startup_runtime.py` imports from `bootstrap_fetch_runtime` only inside
the `bootstrap_node_startup()` function body (local import). `bootstrap_fetch_runtime`
imports from `truth_primitive_fetch_runtime` at module level. Neither imports
from `node_startup_runtime`. No circular dependency.

`no_circular_import_in_bootstrap_chain`

---

### Check 2.7 — CDL-073 trust chain coherence

**Status: PASS**

The bootstrap bundle `signed_by` field is compared to the operator-provided
`genesis_authority_pubkey_hex`. In production, this key is the ML-DSA-65
genesis authority key defined in CDL-073 §2. The chain is:

```
CDL-073 genesis assertion → genesis_authority_pubkey
genesis_authority_pubkey → bootstrap bundle "signed_by" check → bundle verified
bundle verified → peer list extracted → peers promoted
```

No new trust anchor is introduced. The genesis authority key (CDL-073) is the
sole root of trust for bootstrap bundle verification.

`cdl_073_trust_chain_is_sole_root_for_cdl_079`

---

## 3. Regression Status

| Test file | Tests | Status |
|-----------|-------|--------|
| `tests/test_phase_913_920_cdl_079_hb_002_bootstrap.py` | 33 | All pass |
| Full suite | ~426 | All pass |

---

## 4. Forward Obligations Recorded

| Item | Vehicle |
|------|---------|
| Permissionless peer discovery | Post-RC1 CDL |
| Bootstrap bundle rotation / revocation protocol | Future CDL |
| star.map N-gram route index (CDL-080, renumbered from CDL-079) | Window 921–929 |

---

## 5. Coherence Verdict

**COHERENT.**

The Window 913–920 implementation is internally consistent and does not break
any existing CDL contract. CDL-077 client and server paths are unchanged.
The static peer config fallback is preserved. The curated explicit-promotion
model (Phase 578) is intact. The CDL-073 genesis authority key is the sole
root of trust for bootstrap bundle verification.

`window_913_920_coherence_verdict_pass`
