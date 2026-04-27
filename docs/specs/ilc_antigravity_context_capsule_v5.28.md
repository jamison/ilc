# ILC Antigravity Context Capsule v5.28

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.27.md
Date: 2026-04-27
Owner lane: Window 899–905 — CDL-077 WANT-HAVE/WANT-BLOCK fetch (Layer 2 network delivery)

`capsule_v5_28_supersedes_v5_27`
`window_899_905_closed_recorded_in_capsule_v5_28`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 899–905 — COMPLETE.**

| Phase | Topic | Key outcome |
|-------|-------|-------------|
| 899 | Sequence lock | Window 899–905 commissioned; 5-layer architecture corrected; relay incentive model locked |
| 900 | CDL-077 opening | WANT-HAVE/WANT-BLOCK protocol opened; Option C selected |
| 901 | `truth_primitive_fetch_runtime.py` | want_have(); want_block(); fetch_truth_primitive(); server handlers; FetchRateLimiter |
| 902 | `http_fetch_transport_runtime.py` | Dedicated fetch HTTP server (separate from gossip transport) |
| 903 | Tests | 34 tests; all pass |
| 904 | CDL-077 ratification + coherence + capsule | This phase |
| 905 | Closure gate | Gate document; window closed |

**Previous windows:**
- Window 892–898 COMPLETE. CDL-076 ratified (Phase 897). 331 tests.
- Window 887–891 COMPLETE. Truth primitive read-path query. 305 tests.
- Window 877–886 COMPLETE. CDL-075 ratified (Phase 884). 282 tests.
- Window 873–876 COMPLETE. CLI `submit` command. 251 tests.
- Window 863–872 COMPLETE. CDL-074 ratified (Phase 870). 229 tests.

---

## 2. Option B Status (unchanged)

`option_b_selected_by_human_authorization_2026_04_23`
`adr_0028_posture=option_b`

---

## 3. CDL Status

| CDL | Status | Phase | Note |
|-----|--------|-------|------|
| CDL-001 | Open (genesis_blocker) | — | Packaging track |
| CDL-042 | Ratified | 407 | CLI framework — extended by Windows 873–905 |
| CDL-052 | Ratified | 466 | Popperian gate — intact |
| CDL-073 | Ratified | 860 | RC1 homoiconic bootstrap schema |
| CDL-074 | Ratified | 870 | Truth primitive runtime |
| CDL-075 | Ratified | 884 | Truth primitive graph persistence |
| CDL-076 | Ratified | 897 | Truth primitive announcement gossip (Layer 1) |
| CDL-077 | Ratified | 904 | WANT-HAVE/WANT-BLOCK fetch (Layer 2) |
| CDL-078 | Not yet opened | — | Relay fee CDL (reputation-implicit) — Phase 906+ |
| CDL-070 | Deferred | — | PQ migration |

(Full CDL table in v5.27 — unchanged except CDL-077 ratified and CDL-078 noted.)

---

## 4. Window 899–905 Deliverables

**New module:** `ilc_core/network/d2d/truth_primitive_fetch_runtime.py`

```python
TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION = "truth_primitive_fetch_runtime_901.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
WANT_HAVE_PATH = "/fetch/want-have"
WANT_BLOCK_PATH = "/fetch/want-block"
WANT_BLOCK_RATE_LIMIT_PER_MINUTE = 10

def want_have(node_id, peer_endpoint) -> dict:        # {have: bool, node_id: str}
def want_block(node_id, peer_endpoint) -> bytes|None  # full record or None
def fetch_truth_primitive(node_id) -> bytes|None       # tries all ILC_D2D_GOSSIP_PEERS
def handle_want_have_request(body, store) -> (int, bytes)
def handle_want_block_request(body, store, rate_limiter) -> (int, bytes)
class FetchRateLimiter                                 # in-process per-identity token bucket
```

**New module:** `ilc_core/network/d2d/http_fetch_transport_runtime.py`

```python
HTTP_FETCH_TRANSPORT_RUNTIME_VERSION = "http_fetch_transport_runtime_902.v0.1"
class HttpFetchTransportRuntime   # threaded HTTP server for /fetch/want-have + /fetch/want-block
```

**Test coverage:** 34 tests in `tests/test_phase_901_905_cdl_077_fetch.py`

---

## 5. Full Submit → Persist → Announce → Fetch Loop

The full CDL-036 pull-dominant cycle is now operational locally:

```
# Publisher node:
ilc submit --primitive assert.truth --payload-json '...' \
           --agent-id agent-001 --epoch 1
# → node_id: bafyreicbeey...
# → graph_persistence: persisted
# → gossip_delivery: announced to N/N peers  (if ILC_D2D_GOSSIP_PEERS set)

# Subscriber node — receives CDL-076 gossip: "bafyreicbeey... exists"
# Then fetches via CDL-077:
fetch_truth_primitive("bafyreicbeey...")
# → WANT-HAVE → {have: true}
# → WANT-BLOCK → full node record bytes

# Query local store (CDL-075 + Phase 890 query CLI):
ilc query truth-node --node-id bafyreicbeey...
# → node_record: {primitive: "assert.truth", ...}
```

Both `ILC_TRUTH_GRAPH_STORE_PATH` and `ILC_D2D_GOSSIP_PEERS` must be set for the full loop.

---

## 6. Corrected 5-Layer Network Delivery Architecture

Capsule v5.27 recorded a 4-layer map. This capsule establishes the corrected 5-layer map:

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| **L1** | Announcement gossip — soft push-signal | CDL-076 | **Ratified** |
| **L2** | WANT-HAVE/WANT-BLOCK two-phase fetch; DoS rate limiting | CDL-077 | **Ratified** |
| L3 | star.map N-gram route index; pluralistic indexers; spectral routing | Future CDL | H-series designed, not wired |
| L4 | Onion routing + SURB reply envelopes (privacy) | Future CDL | H-series designed, not wired |
| L5 | Two-sided ECU routing fees; relay incentives; centrality attribution | CDL-078+ | Partially ratified (CDL-060, passive ECU); full wiring Phase 906+ |

`layer_map_5_layers_is_canonical`

**Star map dissemination:** Route index updates propagate via L1 (CDL-076 announces new route
index CID) + L2 (CDL-077 fetches the index). No separate Merkle sync protocol required —
star.map payloads are DAG-CBOR → CIDv1 natively.

`star_map_dissemination_uses_cdl_076_cdl_077_pipeline_no_separate_protocol`

**Relay incentive model:** ECU is the long-run consequence of routing behavior (serving →
centrality rises → passive ECU via ratified formula), not a per-hop micro-payment.

`relay_incentive_model_is_reputation_implicit_not_per_hop_ecu`

Historical canon anchors:
- `star.map` primitive: `docs/specs/star.map.ngram.route_index.v1.md`
- Spectral routing: H-014 SIM-ROUTING-01 (Window 791–800)
- Passive ECU formula: `passive_ecu = min(base_reward × 0.20 × centrality_score × m_i, base_reward × 0.15)`
- Two-sided ECU ledger: MemPalace `2026_03_15_21` / `2026_03_22_31` session records
- Onion routing + SURB: H-series, Window 791–800

---

## 7. Test Count

| Scope | Tests |
|-------|-------|
| Window 899–905 (CDL-077 fetch) | 34 |
| Window 892–898 (CDL-076 gossip) | 26 |
| Window 887–891 (query CLI) | 23 |
| Window 877–886 (CDL-075 graph store) | 31 |
| Window 873–876 (CLI submit) | 22 |
| Window 863–872 (CDL-074 runtime) | 67 |
| Prior windows | 162 |
| **Total** | **365** |

---

## 8. Forward Obligations

| Item | Priority | Status |
|------|----------|--------|
| CDL-078: Relay fee CDL — reputation-implicit model, not per-hop ECU | Phase 906+ | Design intent locked; CDL not yet opened |
| star.map L3 routing layer | Post-RC1 | H-series designed; CDL-076/077 serve star.map updates |
| Onion routing + SURB reply envelopes (L4 privacy) | Post-L3 | H-series designed, not wired |
| Multi-hop centrality attribution CDL | Future | SIM-MULTI-HOP-01 evidence available (Phase 552) |
| HB-002 (P2P bootstrap distribution) | Re-evaluate each closure | HB-001 closed; RC1 readiness watch |
| CDL-070 (PQ migration ceremony) | Deep audit window | SIM-MONETARY-01 prerequisite |
| Persistent rate limiter (cross-restart) | Future CDL | In-process only in CDL-077 |
| Cross-epoch compaction / snapshot export | Deferred | — |
