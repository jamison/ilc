# ILC Forward Planning — Windows 906–929

Status: planning (pre-sequence-lock)
Date: 2026-04-27
Produced: End of Window 899–905 (CDL-077 ratified)
Superseded by: individual sequence locks for each window

---

## 1. Purpose

This document captures the proposed phase groupings, scope rationale, and key
open questions for the next three windows. It is a planning artifact, not a
sequence lock. Each window's sequence lock supersedes the relevant section here.

The three windows are:
- **Window 906–912**: CDL-078 — Relay incentive constitutional lock
- **Window 913–920**: HB-002 — P2P bootstrap distribution
- **Window 921–929**: CDL-079 — star.map L3 groundwork (N-gram route index opening)

---

## 2. Architectural Context

As of capsule v5.28, the 5-layer delivery architecture is:

| Layer | CDL | Status | Next obligation |
|-------|-----|--------|----------------|
| L1 — Announcement gossip | CDL-076 | **Ratified** | — |
| L2 — WANT-HAVE/WANT-BLOCK fetch | CDL-077 | **Ratified** | — |
| L3 — star.map N-gram routing | CDL-079 | Not opened | Window 921–929 |
| L4 — Onion routing + SURB | Future | Designed (H-series) | Post-L3 |
| L5 — Relay incentives + ECU fees | CDL-078 | Not opened | **Window 906–912 (next)** |

**Key locked design decisions** (not to be re-opened in these windows):
- Relay incentive model: reputation-implicit, not per-hop ECU micro-payment
- Star.map dissemination: CDL-076/077 pipeline — no separate Merkle sync
- Rate limiting: in-process per-identity token bucket (CDL-077)
- CDL-036 pull-dominant contract: governing across all layers

---

## 3. Window 906–912 — CDL-078: Relay Incentive Constitutional Lock

### 3.1 Authorization

Authorized by capsule v5.28 §8:
*"CDL-078: Relay fee CDL — reputation-implicit model, not per-hop ECU — Phase 906+ — Design intent locked; CDL not yet opened"*

Window 899–905 closure gate token: `relay_fee_cdl_is_next_l5_obligation`

### 3.2 Scope

**What this window ratifies:** The constitutional definition of how WANT-BLOCK serve
events translate into routing reputation, and how routing reputation feeds the
existing CDL-060 centrality delta gossip pipeline → passive ECU formula.

**What this window does NOT do:**
- No per-hop ECU micro-payment mechanism
- No new CDL beyond CDL-078
- No star.map wiring
- No onion routing

### 3.3 Phase sketch

| Phase | Topic |
|-------|-------|
| 906 | Sequence lock |
| 907 | CDL-078 opening — relay incentive constitutional scope |
| 908 | SIM-RELAY-01 (serve-rate → centrality delta calibration) OR analytic lock |
| 909 | Routing reputation signal wiring: `handle_want_block_request()` success → `centrality_delta_gossip_runtime.record_serve_event()` |
| 910 | Tests |
| 911 | CDL-078 ratification + coherence + capsule v5.29 |
| 912 | Closure gate |

### 3.4 Key implementation question for Phase 907

The CDL-078 opening must answer: what is the routing reputation signal?

**Option A**: WANT-BLOCK serve success fires a `serve_event` directly into
`centrality_delta_gossip_runtime` (CDL-060 pipeline), contributing to the node's
centrality score for the served node.

**Option B**: WANT-BLOCK serve success is recorded in a local `routing_serve_log`
and batched into centrality delta updates at validation epoch boundaries.

**Recommendation:** Option A is simpler and doesn't require a new persistence surface.
The CDL-060 centrality delta gossip already handles incremental centrality updates.
The serve event maps to a small positive `centrality_delta` for the served node_id.
No per-request gossip needed — batch at reasonable frequency (e.g., per 10 serves).

### 3.5 Open questions (to resolve at sequence lock Phase 906)

1. Does SIM-RELAY-01 need to run before CDL-078 ratifies, or can the signal be locked
   analytically (e.g., `serve_centrality_delta = 0.01 × base_centrality_unit`)?
2. Is there a maximum centrality contribution per-node per-epoch to prevent gaming?
3. Should drop/refusal of WANT-BLOCK requests produce a negative centrality signal,
   or is the absence of a positive signal sufficient?

### 3.6 Hard pass conditions (preview)

| # | Condition |
|---|-----------|
| 1 | `CDL_078_DEPENDENCY` token declared in routing reputation runtime |
| 2 | WANT-BLOCK serve success → centrality delta signal emitted |
| 3 | Centrality delta feeds CDL-060 gossip pipeline |
| 4 | No per-hop ECU micro-payment introduced |
| 5 | `serve_centrality_delta` constant declared and calibrated |
| 6 | CDL-078 ratified in CDL master log |

### 3.7 Estimated test count

~18–22 new tests. Projected total: ~383–387.

---

## 4. Window 913–920 — HB-002: P2P Bootstrap Distribution

### 4.1 Authorization

Authorized by:
- Capsule v5.28 §8: *"HB-002 P2P bootstrap distribution — re-evaluate each closure — HB-001 closed"*
- HB-001 closed Phase 860. CDL-076/077 now provide the fetch infrastructure HB-002 can leverage.

### 4.2 Scope decision — key pre-window question

The most important question for this window is architectural:

**Can new nodes bootstrap using CDL-076/077 + truth primitive graph?**

If bootstrap peer records are modeled as truth primitive nodes (a new primitive type like
`register.peer`), then:
- A new node announces itself via CDL-076
- Existing nodes fetch the new node's peer record via CDL-077
- No separate bootstrap gossip channel is needed

If bootstrap requires a separate channel:
- A dedicated gossip type (`"peer_announced"`) on a separate CDL-061 channel
- Separate routing from truth primitive gossip
- More infrastructure to implement and maintain

**Recommendation:** Evaluate at Phase 913 sequence lock. If CDL-073's homoiconic bootstrap
schema already covers peer records, the first option is cleaner. The decision must not be
made before reading the existing HB-001/003 schema carefully.

### 4.3 Phase sketch

| Phase | Topic |
|-------|-------|
| 913 | Sequence lock + HB-002 architectural decision (CDL-076/077 pipeline vs. separate channel) |
| 914 | HB-002 opening document + bootstrap peer record schema |
| 915 | Bootstrap peer discovery runtime (`bootstrap_peer_runtime.py`) |
| 916 | Integration with `node_startup_runtime.py` (Phase 570) — dynamic peer discovery on startup |
| 917 | Tests |
| 918 | HB-002 ratification + coherence + capsule v5.30 |
| 919 | Closure gate |

*Phase 920 is a spare / overflow phase if the architectural decision introduces complexity.*

### 4.4 Hard pass conditions (preview)

| # | Condition |
|---|-----------|
| 1 | Bootstrap peer record schema locked (compatible with CDL-073 or separate) |
| 2 | A new node can discover peers without a hardcoded peer list |
| 3 | Peer discovery is integrated into `node_startup_runtime.py` |
| 4 | `ILC_BOOTSTRAP_PEERS` env var (or equivalent) activates dynamic discovery |
| 5 | Static peer list fallback preserved (existing `gossip_peer_registry.py`) |
| 6 | HB-002 ratified in CDL master log |

### 4.5 Estimated test count

~20–24 new tests. Projected total: ~403–411.

---

## 5. Window 921–929 — CDL-079: star.map L3 Groundwork

### 5.1 Authorization

Authorized by:
- Capsule v5.28 §8: *"star.map L3 routing layer — Post-RC1 — H-series designed; CDL-076/077 serve star.map updates"*
- Closure gate 905 token: `layer_map_5_layers_is_canonical`
- `star.map.ngram.route_index.v1.md` is a complete, implementable spec

### 5.2 What this window covers

**N-gram route index only.** Spectral routing (`spectral_distance()`) is explicitly
deferred to CDL-080+. The reason: spectral routing requires H-014 SIM-ROUTING-01
evidence to be retrieved and reviewed before any implementation is locked.

**This window:**
- Open CDL-079 (N-gram route index constitutional scope)
- Implement `star_map_route_index_runtime.py` (producer + consumer)
- Wire star.map dissemination via CDL-076/077 pipeline
- Wire producer weighting (reputation-weighted route selection)

**Deferred to later windows:**
- Spectral routing (`spectral_distance()` as routing metric) — CDL-080+
- Onion routing + SURB (L4) — CDL-081+
- de Bruijn coverage harness — spec §15.1 "not implemented in v1"
- Geometry overlays — spec §15.2 "no geometry computation in v1"

### 5.3 Phase sketch

| Phase | Topic |
|-------|-------|
| 921 | Sequence lock + MemPalace retrieval (H-014, H-015, star.map geometry overlay spec) |
| 922 | CDL-079 opening — N-gram route index constitutional scope; options |
| 923 | `star_map_route_index_runtime.py` — N-gram extraction, multi-head hashing, canonicalization |
| 924 | Indexer producer: route index payload assembly, DAG-CBOR serialization, CIDv1 derivation |
| 925 | Indexer consumer: route lookup, target weighting, producer reputation integration |
| 926 | Dissemination wiring: producer announces route index CID via CDL-076; consumer fetches via CDL-077 |
| 927 | Tests |
| 928 | CDL-079 ratification + coherence + capsule v5.31 |
| 929 | Closure gate |

### 5.4 Pre-phase research requirement (Phase 921)

**MUST retrieve before writing sequence lock:**
- H-014 SIM-ROUTING-01 full simulation design (greedy spectral descent vs. random walk vs. DHT)
- H-015 spectral routing integration plan (how `spectral_distance()` gates on H-014)
- `star.map.geometry_overlay_placeholders.md` (understand placeholder scope)
- Any MemPalace entries on the pluralistic indexer competition design

Do NOT start Phase 922+ without this retrieval.

### 5.5 Hard pass conditions (preview)

| # | Condition |
|---|-----------|
| 1 | `star_map_route_index_runtime.py` exists with version + CDL-079 dep tokens |
| 2 | N-gram extraction produces deterministic bucket keys (matches test vectors in spec §16) |
| 3 | Producer assembles and signs a valid `@v1` route index payload |
| 4 | Consumer retrieves route targets from index by n-gram hash query |
| 5 | Route index CID is announced via CDL-076 gossip |
| 6 | Route index content is fetchable via CDL-077 WANT-BLOCK |
| 7 | No spectral routing (`spectral_distance()`) implemented in this window |
| 8 | CDL-079 ratified in CDL master log |

### 5.6 Estimated test count

~24–28 new tests. Projected total: ~427–439.

---

## 6. Forward Obligations Inventory (all open)

| Obligation | Window | Priority | Blocker |
|------------|--------|----------|---------|
| CDL-078: relay incentive lock | 906–912 | **HIGH** | CDL-077 ✅ done |
| HB-002: P2P bootstrap distribution | 913–920 | **HIGH** | HB-001 ✅ done |
| CDL-079: star.map N-gram route index | 921–929 | MEDIUM | CDL-078, HB-002 |
| CDL-080: spectral routing (`spectral_distance()`) | 930+ | MEDIUM | H-014 retrieval + CDL-079 |
| CDL-081: onion routing + SURB | Post-L3 | LOW | CDL-080 |
| Multi-hop centrality attribution CDL | Future | LOW | SIM-MULTI-HOP-01 Phase 552 evidence available |
| Persistent rate limiter (cross-restart) | Future | LOW | CDL-077 ✅ done |
| Cross-epoch compaction / snapshot export | Pre-RC2 | MEDIUM | CDL-077 ✅ done |
| CDL-001 packaging track | Pre-launch | **HIGH** | RC1 readiness |
| CDL-070 PQ migration ceremony | Pre-launch | MEDIUM | SIM-MONETARY-01 |
| HB-002 re-evaluation | Each closure | **HIGH** | HB-001 ✅ done |

---

## 7. Sequencing Rationale

**Why CDL-078 first?** The relay incentive model is already constitutionally blocked as
design intent. Leaving it unratified means the network operates with an unresolved question
about what routing behavior is rewarded. CDL-077 (L2) is the prerequisite — it is now done.
CDL-078 is a short window and closes L5's constitutional ambiguity.

**Why HB-002 second?** Once L1+L2+L5 are ratified, the bootstrap problem becomes tractable
using the existing infrastructure. A new node can announce itself and be fetched. Formalizing
this into HB-002 closes the last homoiconic bootstrap obligation before RC2.

**Why star.map third?** The N-gram route index is the largest new surface in the three-window
plan. It requires a dedicated pre-phase research retrieval from MemPalace and H-series. It
cannot be rushed. Placing it third ensures CDL-078 and HB-002 are constitutionally clean
before introducing L3 routing complexity.

**L4 (onion/SURB) and spectral routing (CDL-080)** are explicitly deferred beyond this
planning horizon. Enough work exists to occupy the next 3 windows without overloading
any single window.
