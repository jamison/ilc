# ILC Antigravity Context Capsule v5.30

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.29.md
Date: 2026-04-27
Owner lane: Window 913–920 — CDL-079 HB-002 P2P Bootstrap Distribution Protocol

`capsule_v5_30_supersedes_v5_29`
`window_913_920_closed_recorded_in_capsule_v5_30`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 913–920 — COMPLETE.**

| Phase | Topic | Key outcome |
|-------|-------|-------------|
| 913 | Sequence lock | Window 913–920 commissioned; CDL-077 reuse confirmed; CDL-079 assigned to HB-002 |
| 914 | CDL-079 opening | Bootstrap distribution protocol opened; Option C selected |
| 915 | `bootstrap_fetch_runtime.py` | fetch_bootstrap_bundle(); verify_bootstrap_bundle_signature(); extract_peer_endpoints() |
| 916 | `node_startup_runtime.py` patch | bootstrap_node_startup(); detect_bootstrap_mode(); BootstrapError; CDL_079_DEPENDENCY |
| 917 | Tests | 33 tests; all pass |
| 918 | CDL-079 ratification + coherence + capsule | This phase |
| 919 | Closure gate | Gate document; window closed |

**Previous windows:**
- Window 906–912 COMPLETE. CDL-078 ratified (Phase 911). 393 tests.
- Window 899–905 COMPLETE. CDL-077 ratified (Phase 904). 365 tests.
- Window 892–898 COMPLETE. CDL-076 ratified (Phase 897). 331 tests.
- Window 887–891 COMPLETE. Truth primitive read-path query. 305 tests.
- Window 877–886 COMPLETE. CDL-075 ratified (Phase 884). 282 tests.

---

## 2. Option B Status (unchanged)

`option_b_selected_by_human_authorization_2026_04_23`
`adr_0028_posture=option_b`

---

## 3. CDL Status

| CDL | Status | Phase | Note |
|-----|--------|-------|------|
| CDL-001 | Open (genesis_blocker) | — | Packaging track |
| CDL-042 | Ratified | 407 | CLI framework |
| CDL-052 | Ratified | 466 | Popperian gate |
| CDL-060 | Ratified | 541 | Centrality delta gossip |
| CDL-073 | Ratified | 860 | RC1 homoiconic bootstrap schema |
| CDL-074 | Ratified | 870 | Truth primitive runtime |
| CDL-075 | Ratified | 884 | Truth primitive graph persistence |
| CDL-076 | Ratified | 897 | Truth primitive announcement gossip (L1) |
| CDL-077 | Ratified | 904 | WANT-HAVE/WANT-BLOCK fetch (L2) |
| CDL-078 | Ratified | 911 | Relay incentive constitutional lock (L5) |
| CDL-079 | **Ratified** | **918** | **HB-002 P2P bootstrap distribution protocol** |
| CDL-070 | Deferred | — | PQ migration |
| CDL-080 | Not yet opened | — | star.map N-gram route index (L3) — Window 921–929 |

---

## 4. Window 913–920 Deliverables

### 4.1 New module: `bootstrap_fetch_runtime.py`

```python
# ilc_core/network/d2d/bootstrap_fetch_runtime.py

BOOTSTRAP_FETCH_RUNTIME_VERSION = "bootstrap_fetch_runtime_915.v0.1"
CDL_079_DEPENDENCY = "cdl_079_hb_002_bootstrap_distribution.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"

BOOTSTRAP_BUNDLE_SCHEMA_VERSION = "bootstrap_bundle_v1"
BOOTSTRAP_BUNDLE_CDL_VERSION = "cdl_079_bootstrap_bundle_v1"

def fetch_bootstrap_bundle(seed_peer_endpoint, bundle_cid) -> dict | None
def verify_bootstrap_bundle_signature(bundle, genesis_authority_pubkey_hex) -> bool
def extract_peer_endpoints(bundle) -> list[str]
def validate_bootstrap_bundle_schema(bundle) -> bool
```

### 4.2 Patch: `node_startup_runtime.py` (Phase 916)

```python
CDL_079_DEPENDENCY = "cdl_079_hb_002_bootstrap_distribution.v0.1"

class BootstrapError(Exception):
    def __init__(self, token: str, detail: str = "") -> None: ...

def bootstrap_node_startup(seed_peer, bundle_cid, genesis_pubkey_hex) -> list[str]:
    """Fetch, verify, extract → list of peer endpoints."""

def detect_bootstrap_mode() -> tuple[str, str] | None:
    """Read ILC_BOOTSTRAP_SEED_PEER + ILC_BOOTSTRAP_BUNDLE_CID from env."""
```

### 4.3 Bootstrap bundle schema

```json
{
  "schema_version": "bootstrap_bundle_v1",
  "bundle_cid": "<CIDv1>",
  "genesis_cid": "<CIDv1>",
  "peers": [{"endpoint": "https://...", "node_id": "<CIDv1>"}, ...],
  "signed_by": "<ML-DSA-65 genesis authority pubkey hex>",
  "signature": "<ML-DSA-65 signature hex>",
  "cdl_version": "cdl_079_bootstrap_bundle_v1"
}
```

### 4.4 Test coverage

**33 tests** in `tests/test_phase_913_920_cdl_079_hb_002_bootstrap.py`

---

## 5. P2P Bootstrap Model (CDL-079)

```
Operator provisions new node with:
    ILC_BOOTSTRAP_SEED_PEER = "https://seed1.ilc.example"
    ILC_BOOTSTRAP_BUNDLE_CID = "bafyreiabc..."

New node startup:
    detect_bootstrap_mode() → (seed_peer, bundle_cid)
    bootstrap_node_startup(seed_peer, bundle_cid, genesis_authority_pubkey)
        → fetch_bootstrap_bundle(seed_peer, bundle_cid)   [CDL-077 WANT-BLOCK]
        → verify_bootstrap_bundle_signature(bundle, pubkey)  [CDL-073 key]
        → extract_peer_endpoints(bundle)
        → GossipPeerRegistry(endpoints)   [explicit promotion]
```

**No GitHub required. One seed peer is sufficient. Curated model preserved.**

`hb_002_bootstrap_distribution_protocol_locked`
`bootstrap_bundle_trust_chain_via_cdl_073_genesis_authority_key`
`static_peer_config_fallback_preserved`

---

## 6. 5-Layer Network Delivery Architecture (canonical, unchanged)

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| **L1** | Announcement gossip | CDL-076 | **Ratified (Phase 897)** |
| **L2** | WANT-HAVE/WANT-BLOCK fetch | CDL-077 | **Ratified (Phase 904)** |
| **L5** | Relay incentives — serve → centrality → passive ECU | CDL-078 | **Ratified (Phase 911)** |
| L3 | star.map N-gram route index | CDL-080 | Window 921–929 |
| L4 | Onion routing + SURB | Future CDL | Post-L3 |

**Note:** CDL-079 is assigned to HB-002 (this window). Star.map is renumbered CDL-080.

`cdl_079_assigned_to_hb_002_star_map_renumbered_cdl_080`

---

## 7. Test Count

| Scope | Tests |
|-------|-------|
| Window 913–920 (CDL-079 HB-002 bootstrap) | 33 |
| Window 906–912 (CDL-078 relay incentive) | 28 |
| Window 899–905 (CDL-077 fetch) | 34 |
| Window 892–898 (CDL-076 gossip) | 26 |
| Window 887–891 (query CLI) | 23 |
| Window 877–886 (CDL-075 graph store) | 31 |
| Window 873–876 (CLI submit) | 22 |
| Window 863–872 (CDL-074 runtime) | 67 |
| Prior windows | 162 |
| **Total** | **426** |

---

## 8. Forward Obligations

| Item | Priority | Status |
|------|----------|--------|
| CDL-080: star.map N-gram route index (L3) | Window 921–929 | **Next primary obligation** |
| Permissionless peer discovery | Post-RC1 | HB-002 RC1 scope complete |
| Bootstrap bundle rotation / revocation | Future CDL | Deferred |
| SIM-RELAY-01: serve-rate → centrality delta calibration | Post-RC1 | CDL-078 forward obligation |
| CDL-001 packaging track | Pre-launch | genesis_blocker |
| CDL-070 PQ migration ceremony | Deep audit | SIM-MONETARY-01 prerequisite |
| Onion routing + SURB (L4 privacy) | Post-L3 | H-series designed |

---

## 9. RC1 Remaining Gates

| Gate | Status |
|------|--------|
| CDL-077 (L2 fetch) | Ratified (Phase 904) |
| CDL-078 (L5 relay incentive) | Ratified (Phase 911) |
| CDL-079 (HB-002 bootstrap) | **Ratified (Phase 918)** |
| CDL-001 (packaging track) | Pending |

---

## 10. Historical State Anchors

- Full CDL ratification history: v5.27 §3 (unchanged through v5.29)
- Full window history: v5.29 §1
- Passive ECU formula: `passive_ecu = min(base_reward × 0.20 × centrality_score × m_i, base_reward × 0.15)`
- Phase 578 curated lineage lock: `curated_genesis_lineage_testnet_only`
- star.map primitive: `docs/specs/star.map.ngram.route_index.v1.md`
- MemPalace retrieval required before Window 921–929 sequence lock (H-014, H-015)
