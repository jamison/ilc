# ILC Antigravity Context Capsule v5.31

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.30.md
Date: 2026-04-27
Owner lane: Window 921–929 — CDL-080 Star.Map N-Gram Route Index (L3)

`capsule_v5_31_supersedes_v5_30`
`window_921_929_near_closed_recorded_in_capsule_v5_31`
`cdl_080_ratified_phase_927`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 921–929 — Phase 927 (ratification). Closure at Phase 928.**

| Phase | Topic | Key outcome |
|-------|-------|-------------|
| 921 | Sequence lock | Window 921–929 commissioned; L3 slot confirmed; H-015 as prefilter |
| 922 | CDL-080 opening | N-gram route index opened; Option C selected (ephemeral-until-published) |
| 922 | CDL log mutation | CDL-080 inserted as open |
| 923–926 | Runtime + tests | `star_map_route_index_runtime.py`; 36 tests; all pass |
| 927 | CDL-080 ratification | Evidence + coherence + capsule v5.31; CDL log → ratified |
| 928 | Closure gate | Window 921–929 closed |
| 929 | Spare | — |

**Previous windows:**
- Window 913–920 COMPLETE. CDL-079 ratified (Phase 918). 426 tests.
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
| CDL-079 | Ratified | 918 | HB-002 P2P bootstrap distribution protocol |
| CDL-080 | **Ratified** | **927** | **star.map N-gram route index (L3)** |
| CDL-070 | Deferred | — | PQ migration |

---

## 4. Window 921–929 Deliverables

### 4.1 New module: `star_map_route_index_runtime.py`

```python
# ilc_core/network/star_map/star_map_route_index_runtime.py
# Phase 923-926 — committed 3180dc78

STAR_MAP_RUNTIME_VERSION = "star_map_route_index_runtime_923.v0.1"
CDL_080_DEPENDENCY = "cdl_080_star_map_n_gram_route_index.v0.1"
ADR_0003_DEPENDENCY = "adr_0003_star_map_route_index"
ADR_0033_DEPENDENCY = "adr_0033_star_map_homoiconic_entity"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
H015_DEPENDENCY = "spectral_routing_runtime_h015.v0.1"

L3_ADVISORY_L2_AUTHORITATIVE = (
    "l3_advisory_l2_authoritative_l3_does_not_override_cdl_077"
)

ROUTE_INDEX_SCHEMA_VERSION = "route_index_v1"
NGRAM_SIZE = 3
NODE_TYPE_STAR_MAP = "star_map"
STAR_MAP_ENTITY_KINDS = frozenset({"route_cluster", "panel_result", "navigation_overlay"})

def compute_route_index(node_endpoints: dict[str, list[str]], epoch: int,
                        generator_agent_id: str) -> RouteIndex
def query_route_index(route_index: RouteIndex, query: str, top_k: int = 16) -> list[RouteHint]
def query_route_index_spectral(route_index, query, local_fingerprint,
                               peer_fingerprints, top_k=16) -> list[RouteHint]
def publish_star_map_result(route_index, source_node_set_digest, agent_id,
                            epoch, entity_kind="route_cluster") -> dict
def l3_route_and_fetch(query, route_index, local_fingerprint, peer_fingerprints,
                       cdl_077_fetch_fn, top_k=16) -> Optional[dict]
```

Dep-chain guard verifies H-015 `SPECTRAL_ROUTING_RUNTIME_VERSION` at import.

### 4.2 Route index schema (route_index_v1)

```json
{
  "schema_version": "route_index_v1",
  "epoch": "<int>",
  "generator_agent_id": "<agent CID>",
  "buckets": {
    "<sha256(ngram)[:16]>": ["<endpoint1>", "<endpoint2>", ...]
  },
  "parameter_digest": "<sha256 of bucket construction parameters>"
}
```

Canonical form: `json.dumps(index, sort_keys=True).encode()`

### 4.3 L3 routing sequence (CDL-080 §4.1)

```
Agent query (semantic string)
  → L3: compute route hints via N-gram route index + spectral prefilter
  → L3 returns: ordered list of candidate peer endpoints (advisory)
  → L2: agent submits WANT-HAVE to candidates (CDL-077)
  → L2 returns: content or WANT-BLOCK CID (authoritative)
  → L2 authoritative result is truth; L3 hint has no override authority
```

`l3_advisory_l2_authoritative`
`l2_non_match_is_not_l3_error`

### 4.4 ADR-0033 publication boundary

Ephemeral `RouteIndex` → promoted to `Node(type="star_map")` via explicit
`publish_star_map_result()` call. Node is content-addressed. No private scratch
work produces a first-class node. ECU attribution deferred to H-CON-01.

### 4.5 Spectral routing (H-015)

`query_route_index_spectral()` uses `spectral_distance` from
`ilc_core.analysis.spectral_utils` (the H-015 kernel). Greedy descent + random-
walk fallback on cycle detection per SIM-ROUTING-01. Operates on locally-cached
peer fingerprints only — no gossip beacon emission (H-013 scope).

`spectral_routing_local_fingerprints_only_no_beacon_gossip`

### 4.6 Test coverage

**36 tests** in `tests/test_phase_921_929_cdl_080_star_map.py`, 36/36 pass.

---

## 5. 5-Layer Network Delivery Architecture (now L1–L3 complete)

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| **L1** | Announcement gossip | CDL-076 | **Ratified (Phase 897)** |
| **L2** | WANT-HAVE/WANT-BLOCK fetch | CDL-077 | **Ratified (Phase 904)** |
| **L3** | star.map N-gram route index | CDL-080 | **Ratified (Phase 927)** |
| L4 | Onion routing + SURB | Future CDL | Post-L3 |
| **L5** | Relay incentives | CDL-078 | **Ratified (Phase 911)** |

`l1_l2_l3_l5_constitutional_stack_complete`

---

## 6. P2P Bootstrap Model (CDL-079, unchanged)

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

`hb_002_bootstrap_distribution_protocol_locked`

---

## 7. Test Count

| Scope | Tests |
|-------|-------|
| Window 921–929 (CDL-080 star.map L3) | **36** |
| Window 913–920 (CDL-079 HB-002 bootstrap) | 33 |
| Window 906–912 (CDL-078 relay incentive) | 28 |
| Window 899–905 (CDL-077 fetch) | 34 |
| Window 892–898 (CDL-076 gossip) | 26 |
| Window 887–891 (query CLI) | 23 |
| Window 877–886 (CDL-075 graph store) | 31 |
| Window 873–876 (CLI submit) | 22 |
| Window 863–872 (CDL-074 runtime) | 67 |
| Prior windows | 162 |
| **Total** | **462** |

---

## 8. Forward Obligations

| Item | Priority | Status |
|------|----------|--------|
| Window 921–929 closure gate | Phase 928 | Immediate next |
| ECU attribution for star-map nodes | H-CON-01 CDL | Deferred |
| Gossip beacon activation | H-013 | Blocked on ADR-0034 + sealed sender |
| PoSK admission gate | H-008 CDL | Blocked on H-011 patent assessment |
| Panel hyperedge quorum rules | H-CON-02 CDL | Blocked on H-CON-01 |
| Star expansion implementation | H-012 | Blocked on H-CON-01 |
| `node_startup_runtime.py` L3 wiring | Post-H-013 | Blocked on live peer fingerprints |
| SIM-REUSE-01 reuse signal calibration in W | Planning | New SIM entry |
| Hypergraph NOW items (EdgeType enum, WeightParams, EdgeRecord proto) | Pre-M-018 | H-CON-01 design |
| CDL-001 packaging track | Pre-launch | genesis_blocker |
| CDL-070 PQ migration ceremony | Deep audit | SIM-MONETARY-01 prerequisite |
| Onion routing + SURB (L4 privacy) | Post-L3 | H-series designed |

---

## 9. RC1 Remaining Gates

| Gate | Status |
|------|--------|
| CDL-077 (L2 fetch) | Ratified (Phase 904) |
| CDL-078 (L5 relay incentive) | Ratified (Phase 911) |
| CDL-079 (HB-002 bootstrap) | Ratified (Phase 918) |
| CDL-080 (L3 star.map route index) | **Ratified (Phase 927)** |
| CDL-001 (packaging track) | Pending |

---

## 10. Historical State Anchors

- Full CDL ratification history: v5.27 §3 (unchanged through v5.30)
- Full window history: v5.30 §1
- Passive ECU formula: `passive_ecu = min(base_reward × 0.20 × centrality_score × m_i, base_reward × 0.15)`
- Phase 578 curated lineage lock: `curated_genesis_lineage_testnet_only`
- star.map primitive: `docs/specs/star.map.ngram.route_index.v1.md`
- H-014 SIM-ROUTING-01 result: P50=1-2 hops, two-phase ≥0.80 in all four topology classes
- H-015 spectral routing primitive: `spectral_routing_runtime_h015.v0.1`
