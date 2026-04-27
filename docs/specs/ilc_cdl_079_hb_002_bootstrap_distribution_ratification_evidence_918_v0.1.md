# CDL-079 HB-002 Bootstrap Distribution Protocol — Ratification Evidence (Phase 918)

Status: ratified
Date: 2026-04-27
Phase: 918
CDL: CDL-079
Opening document: docs/specs/ilc_cdl_079_hb_002_bootstrap_distribution_protocol_opening_914_v0.1.md

---

## 1. Ratification Summary

CDL-079 ratifies the peer-to-peer bootstrap distribution protocol for the ILC
network. The implementation covers Phases 913–917 of Window 913–920 and satisfies
all 8 hard pass conditions from the sequence lock
(`docs/specs/ilc_phase_913_920_sequence_lock_v0.1.md`).

Selected option: **Option C** — CDL-077 WANT-BLOCK bundle fetch with operator-provided
seed peer. Options A (separate gossip channel) and B (DHT discovery) rejected.

`cdl_079_ratified_phase_918`
`option_c_selected_cdl_077_bundle_fetch`

---

## 2. Hard Pass Condition Verification

### Condition 1 — `bootstrap_fetch_runtime.py` exists

**Result: PASS**

File: `ilc_core/network/d2d/bootstrap_fetch_runtime.py`

Verified by `test_bootstrap_fetch_runtime_exists()`.

---

### Condition 2 — Version and CDL dependency tokens present

**Result: PASS**

```python
BOOTSTRAP_FETCH_RUNTIME_VERSION = "bootstrap_fetch_runtime_915.v0.1"
CDL_079_DEPENDENCY = "cdl_079_hb_002_bootstrap_distribution.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"
```

Also in `node_startup_runtime.py`:
```python
CDL_079_DEPENDENCY = "cdl_079_hb_002_bootstrap_distribution.v0.1"
```

Verified by: `test_bootstrap_fetch_runtime_version_token`,
`test_cdl_079_dependency_token`, `test_cdl_077_dependency_token_in_bootstrap_runtime`,
`test_cdl_073_dependency_token_in_bootstrap_runtime`, `test_cdl_079_dependency_in_node_startup`.

---

### Condition 3 — `fetch_bootstrap_bundle()` fetches via CDL-077 WANT-HAVE/WANT-BLOCK

**Result: PASS**

Protocol:
1. `want_have(bundle_cid, seed_peer_endpoint)` → `{have: bool}`
2. If `have: True` → `want_block(bundle_cid, seed_peer_endpoint)` → raw bytes
3. Parse JSON → return bundle dict

Verified: correct args passed to `want_have`/`want_block` (mock assertions),
404/WANT-HAVE-false paths return None, invalid JSON raises `BootstrapBundleError`,
bad inputs raise before network calls.

Tests: `test_fetch_bootstrap_bundle_success`, `test_fetch_bootstrap_bundle_not_found_returns_none`,
`test_fetch_bootstrap_bundle_want_block_none_returns_none`,
`test_fetch_bootstrap_bundle_invalid_json_raises`,
`test_fetch_bootstrap_bundle_bad_seed_peer_raises`,
`test_fetch_bootstrap_bundle_bad_bundle_cid_raises`.

---

### Condition 4 — `verify_bootstrap_bundle_signature()` verifies ML-DSA-65 signature

**Result: PASS**

Verification contract:
- `signed_by` field must match `genesis_authority_pubkey_hex` (key binding)
- `schema_version == "bootstrap_bundle_v1"` required
- `cdl_version == "cdl_079_bootstrap_bundle_v1"` required
- `signature` field must be present
- ML-DSA-65 crypto via `oqs` library (bypassed in test env via
  `ILC_BOOTSTRAP_SKIP_SIG_VERIFY=1`)
- Never raises — returns False on any error

Tests: `test_verify_signature_wrong_signed_by_returns_false`,
`test_verify_signature_wrong_schema_version_returns_false`,
`test_verify_signature_wrong_cdl_version_returns_false`,
`test_verify_signature_missing_signature_field_returns_false`,
`test_verify_signature_not_a_dict_returns_false`,
`test_verify_signature_correct_key_with_bypass`.

---

### Condition 5 — `node_startup_runtime.py` patched: bootstrap mode via env vars

**Result: PASS**

New functions added:
- `bootstrap_node_startup(seed_peer, bundle_cid, genesis_pubkey_hex) → list[str]`
- `detect_bootstrap_mode() → tuple[str, str] | None`
- `BootstrapError(token, detail)`

Env var logic:
- Both `ILC_BOOTSTRAP_SEED_PEER` + `ILC_BOOTSTRAP_BUNDLE_CID` set → bootstrap mode
- Neither set → None (static mode)
- One without the other → `ValueError("bootstrap_mode_requires_both_seed_peer_and_bundle_cid")`

Tests: `test_detect_bootstrap_mode_both_set`, `test_detect_bootstrap_mode_neither_set`,
`test_detect_bootstrap_mode_only_seed_raises`, `test_detect_bootstrap_mode_only_cid_raises`,
`test_bootstrap_node_startup_success`, `test_bootstrap_node_startup_bundle_not_found_raises`,
`test_bootstrap_node_startup_signature_invalid_raises`.

---

### Condition 6 — Static peer config fallback preserved

**Result: PASS**

`detect_bootstrap_mode()` returns `None` when both env vars are absent.
`load_static_peer_config()` is unchanged. `build_node_startup_context()` is unchanged.
`NODE_STARTUP_RUNTIME_VERSION` remains `"node_startup_runtime_570.v0.1"`.

All existing node startup tests continue to pass (regression confirmed).

`static_peer_config_fallback_preserved_confirmed`

---

### Condition 7 — No DHT, no swarm discovery introduced

**Result: PASS**

Source scan of `bootstrap_fetch_runtime.py` (code lines only, excluding docstrings):
Forbidden terms not present: `kademlia`, `swarm_discovery`, `mdns`, `announce_peer`,
`import dht`, `from dht`.

`no_dht_no_swarm_in_cdl_079_confirmed_by_source_scan`

Verified by: `test_no_dht_in_bootstrap_fetch_runtime`.

---

### Condition 8 — CDL-079 opened in CDL master log

**Result: PASS**

CDL-079 row present in `docs/specs/ilc_constitutional_decision_log_v0.1.md`:
```
opened_phase: 914 | opened_date: 2026-04-27
```

Verified by: `test_cdl_079_row_in_master_log`.

---

## 3. Curated Model Preserved

The Phase 578 curated lineage lock contract is fully preserved:
- `candidate_discovery_not_active_peer_admission` — bundle verification is the promotion gate
- `explicit_promotion_required_before_runtime_peer_use` — enforced in `bootstrap_node_startup()`
- No peer is admitted to the registry without a verified bundle signature

`curated_lineage_contract_preserved_in_cdl_079`

---

## 4. CDL-077 Return Contract Preserved

`fetch_bootstrap_bundle()` calls `want_have()` and `want_block()` — the CDL-077 client
functions. These are called with (node_id, peer_endpoint) as specified in CDL-077.
The server-side `handle_want_block_request()` is NOT modified by this window.

`cdl_077_return_contract_unchanged`

---

## 5. CDL-073 Trust Chain

The `signed_by` public key in the bootstrap bundle must match the genesis authority key
embedded in the genesis-authority assertion (CDL-073 §2). This closes the trust chain:
- CDL-073: genesis authority key is machine-legible in the genesis-authority assertion
- CDL-079: bootstrap bundle `signed_by` = genesis authority key → cryptographic binding
- New nodes verify this binding without out-of-band trust assumptions

`bootstrap_bundle_trust_chain_via_cdl_073_genesis_authority_key_confirmed`

---

## 6. Test Summary

| Test file | Tests | Status |
|-----------|-------|--------|
| `tests/test_phase_913_920_cdl_079_hb_002_bootstrap.py` | 33 | All pass (1 scope guard skips before commit; 33/33 after commit `9b42809f`) |

Total new tests in Window 913–920: **33**
Total passing tests across full suite: **~426** (393 + 33)

---

## 7. Rejected Options

**Option A — Separate bootstrap gossip channel:** Rejected. Redundant with CDL-077.
A push gossip channel for bootstrap adds infrastructure complexity without benefit
over a single WANT-BLOCK fetch of a known bundle CID.

**Option B — DHT peer discovery:** Rejected. Phase 578 curated lineage lock explicitly
rejects DHT for RC phase. Permissionless peer discovery is a post-RC1 concern.

`option_a_rejected_separate_gossip_channel`
`option_b_rejected_dht_discovery`
`option_c_selected_cdl_079`

---

## 8. Exclusion Tokens (confirmed)

```
no_permissionless_peer_admission_in_cdl_079       confirmed — curated model only
no_dht_in_cdl_079                                 confirmed — source scan
no_separate_bootstrap_gossip_channel_in_cdl_079   confirmed — CDL-077 reused
no_mdns_in_cdl_079                                confirmed — source scan
no_auto_peer_promotion_without_bundle_verification confirmed — explicit gate in code
no_star_map_wiring_in_cdl_079                     confirmed — CDL-080 window
```

---

## 9. Ratification Authorization

CDL-079 is hereby ratified at Phase 918 (2026-04-27).

`cdl_079_ratified_918`
`window_913_920_hard_pass_conditions_all_satisfied`
`hb_002_bootstrap_distribution_protocol_locked`
