# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.8
**Produced**: 2026-04-27
**Session context**: Window 899–905 closed; CDL-077 ratified; 365 tests; capsule v5.28.
G8 network delivery track L1+L2 complete. 5-layer delivery architecture established.
**Supersedes**: `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.7.md`
**Purpose**: First roadmap update to reflect the full G8 truth primitive stack (CDL-073
through CDL-077) and the 5-layer network delivery architecture. Corrects stale Row 5
and CDL status from v0.7.

---

## Postscript 2026-05-02 — Window 1130-1138 Closure

This roadmap remains the launch architecture reference, but its date-stamped test count and
immediate-next-window assumptions are superseded by the later Window 1130-1138 closure.

Current frontier after Phase 1138:

- SIM-SPECTRAL-02 is complete with Scenario B Advisory: useful directional bootstrap
  signal, not deployment-ready.
- CDL-085 remains SIM-gated and unopened; SIM-SPECTRAL-03 with the 31-node Genesis core
  star-map seed is the recommended evidence route before any CDL-085 authorization.
- GENESIS-COMPILE-01 baseline is `PARTIAL_WITH_STRUCTURAL_GAPS`; the gap is graph
  construction, not protocol failure.
- Genesis Atlas Tier-1 should precede SIM-SPECTRAL-03: add explicit authority-chain edges,
  rerun GENESIS-COMPILE-01 checkpoint #1, then proceed to SIM harness work if authorized.
- Runtime remains `epoch_attribution_settle_runtime_1129_fix1.v0.5`; no `ilc_core/`
  files changed in Window 1130-1138.

Authoritative closure reference:
`docs/specs/ilc_window_1130_1138_handoff_1138_v0.1.md`.

---

## 1. What Has Changed Since v0.7

| Item | v0.7 claim | Actual state (v0.8) |
|------|-----------|---------------------|
| Row 5 | `spec_closed_runtime_pending` | `runtime_closed` (Phase 846, CDL-072) |
| CDL-073 | Not yet in scope | Ratified (Phase 860) — RC1 homoiconic bootstrap schema |
| CDL-074 | Not yet in scope | Ratified (Phase 870) — truth primitive runtime, 6 primitives |
| CDL-075 | Not yet in scope | Ratified (Phase 884) — truth primitive graph persistence (LMDB) |
| CDL-076 | Not yet in scope | Ratified (Phase 897) — truth primitive announcement gossip (L1) |
| CDL-077 | Not yet in scope | Ratified (Phase 904) — WANT-HAVE/WANT-BLOCK fetch (L2) |
| HB-001 | Pending | CLOSED (Phase 860) |
| HB-003 | Pending | CLOSED (Phase 860) |
| Network delivery | Not addressed | 5-layer architecture established and L1+L2 ratified |
| Relay incentives | Not addressed | Design intent locked: reputation-implicit, not per-hop ECU |
| Test count | Not tracked | 365 tests passing |

---

## 2. Current State Summary (2026-04-27)

| Surface | Status |
|---------|--------|
| Option B selection | **SELECTED** (`adr_0028_posture=option_b`, Phase 814) |
| CDL-017 | **RATIFIED** (Phase 765) |
| Row 5 (privacy lane, k-anonymity) | **`runtime_closed`** (Phase 846, CDL-072 ratified) |
| Row 7 | **`runtime_closed`** |
| Row 8 | **`pass`** |
| H-013 (sealed spectral beacon) | **IMPLEMENTED** — post-audit hardened; no production gossip activation |
| H-015 (spectral routing) | **PRIMITIVE COMPLETE** — can consume H-013 |
| HIGH-002 | **DISPOSITIONED** — production-hardening item |
| Settlement-path rotation | **DESIGNED** — Rust implementation gated on first-validator authorization |
| First non-Genesis validator deployment | **GATE PULLED** (Phase 826) — first validator deployed to testbed |
| B-Impl obligations (Row 5) | **COMPLETE** (Phases 831–833, 844, 846) |
| SIM-LEAKAGE-03 | **COMPLETE** (Phase 846 — definitive pass) |
| HB-001 / HB-003 | **CLOSED** (Phase 860, CDL-073) |
| HB-002 | Not yet opened — re-evaluate each window closure |
| CDL-073 | **RATIFIED** (Phase 860) — RC1 homoiconic bootstrap schema |
| CDL-074 | **RATIFIED** (Phase 870) — truth primitive runtime |
| CDL-075 | **RATIFIED** (Phase 884) — truth primitive graph persistence |
| CDL-076 | **RATIFIED** (Phase 897) — truth primitive announcement gossip (L1) |
| CDL-077 | **RATIFIED** (Phase 904) — WANT-HAVE/WANT-BLOCK fetch (L2) |
| RC0.1 substrate | **`satisfied_for_testbed`** — all checklist rows satisfied |
| Truth primitive stack | **OPERATIONAL** — submit → persist → gossip → fetch loop complete |
| Test suite | **365 tests passing** |

---

## 3. Gap Inventory (Current)

### Gap 1 — L5 relay incentive CDL (CDL-078)

**Status: design intent locked, CDL not yet opened.**

The relay incentive model is constitutionally locked as reputation-implicit (not per-hop ECU
micro-payment). Serving WANT-BLOCK requests feeds centrality accumulation → passive ECU
via the ratified formula. Dropping requests degrades routing reputation → reduced ECU.

What remains:
- CDL-078 opening and ratification
- Routing reputation signal integration: WANT-BLOCK serves → centrality delta → CDL-060 gossip
- SIM-RELAY-01 (optional calibration for serve-rate thresholds)

**Urgency:** HIGH. This is the next-window primary obligation and closes L5 constitutional
ambiguity before the network grows.

### Gap 2 — HB-002 (P2P bootstrap distribution)

**Status: not yet opened — re-evaluate each window.**

HB-001 (genesis authority assertion schema) is closed. HB-002 covers how new nodes discover
bootstrap peers without a centralized directory. CDL-076/077 (announcement + fetch) now
provide the infrastructure for dynamic peer discovery via truth primitive announcements.

What remains:
- Decision on whether CDL-076/077 pipeline is sufficient for HB-002, or whether a separate
  bootstrap gossip mechanism is needed
- HB-002 formal scope definition and implementation

**Urgency:** MEDIUM. Needed before RC2. Can proceed in parallel with or after CDL-078.

### Gap 3 — L3 star.map routing (CDL-079+)

**Status: H-series designed, not wired.**

The star.map N-gram route index spec (`star.map.ngram.route_index.v1.md`) is complete.
H-014 (SIM-ROUTING-01) compared spectral descent vs. random walk vs. DHT. H-015 established
spectral routing as the ILC-native routing metric (`spectral_distance()`).

Star.map dissemination is now confirmed to use the CDL-076/077 pipeline — no separate
Merkle sync protocol required (DAG-CBOR → CIDv1 natively content-addressed).

What remains:
- MemPalace retrieval of H-014/H-015 full spec before any wiring
- CDL-079 opening (star.map L3 CDL)
- `star_map_route_index_runtime.py` wiring
- Pluralistic indexer protocol (competing indexers, producer weighting)

**Urgency:** LOW for immediate RC1. HIGH for network efficiency beyond testbed scale.

### Gap 4 — L4 onion routing / SURB reply envelopes

**Status: H-series designed, not wired.**

Onion routing within the peer gossip mesh with SURB-style reply envelopes is named in the
H-series. This provides privacy for fetch requests — the requester's identity is not revealed
to intermediate peers.

**Urgency:** LOW. Deferred until L3 (star.map) is wired. Not blocking any RC milestone.

### Gap 5 — CDL-070 (PQ migration ceremony)

**Status: deferred — SIM-MONETARY-01 prerequisite.**

CDL-069 ratified ML-DSA-65 as the identity root. CDL-070 covers the migration ceremony for
existing BLS keys. SIM-MONETARY-01 must run first to verify that the ceremony does not
create economic discontinuities.

**Urgency:** LOW. On the deep audit agenda. Not blocking any RC milestone.

### Gap 6 — Cross-epoch compaction / snapshot export

**Status: deferred.**

LMDB stores accumulate truth primitive nodes indefinitely. A compaction CDL is needed before
the network grows beyond testbed scale. Not yet opened.

**Urgency:** LOW. Needed before RC2 / public network.

### Gap 7 — Multi-hop centrality attribution CDL

**Status: SIM-MULTI-HOP-01 evidence available (Phase 552), CDL not opened.**

SIM-MULTI-HOP-01 studied compounding ECU streams across citation chains (A→B→C). Evidence
exists but was explicitly marked research-only — no CDL opened from it.

**Urgency:** LOW. Needed for L5 economics completeness.

### Gap 8 — CDL-001 (genesis_blocker / packaging track)

**Status: open genesis_blocker.**

CDL-001 must close before any public launch claim. Not yet opened for ratification.

**Urgency:** HIGH for any public RC claim. Not blocking internal testbed work.

---

## 4. Layered Network Delivery Architecture (canonical, v0.8)

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| L1 | Announcement gossip — soft push-signal (CDL-036) | CDL-076 | **Ratified** |
| L2 | WANT-HAVE/WANT-BLOCK two-phase fetch; rate limiting | CDL-077 | **Ratified** |
| L3 | star.map N-gram route index; spectral routing | CDL-079+ | H-series designed |
| L4 | Onion routing + SURB reply envelopes (privacy) | Future CDL | H-series designed |
| L5 | Relay incentives; ECU routing fees; centrality attribution | CDL-078 (opening) | Design intent locked |

---

## 5. Proposed Next Sequence (three windows)

### Window 906–912 — CDL-078: Relay Incentive Constitutional Lock

**Primary goal:** Ratify the reputation-implicit relay incentive model. Wire WANT-BLOCK serve
events into the CDL-060 centrality delta gossip pipeline. Close L5's constitutional ambiguity.

**Why now:** CDL-077 (L2) is ratified. The relay incentive model cannot be wired without L2.
The design intent is locked but not constitutionally ratified. Gap 1 closes here.

**Phase sketch:**
- 906: Sequence lock
- 907: CDL-078 opening
- 908: SIM-RELAY-01 (serve-rate → centrality delta calibration) — optional, may be analytic
- 909: Routing reputation signal wiring (`serve_event → centrality_delta_gossip_runtime`)
- 910: Tests
- 911: CDL-078 ratification + coherence + capsule v5.29
- 912: Closure gate

**Hard pass conditions (preview):**
- CDL-078 ratified
- `handle_want_block_request()` success → centrality delta signal emitted
- Centrality delta feeds CDL-060 gossip pipeline
- No per-hop ECU micro-payment mechanism introduced
- relay_incentive_model_is_reputation_implicit confirmed by implementation

### Window 913–920 — HB-002: P2P Bootstrap Distribution

**Primary goal:** Formally scope and implement HB-002. Determine whether CDL-076/077 pipeline
is sufficient for dynamic peer discovery or whether a separate bootstrap gossip mechanism is
needed. Close the last open homoiconic bootstrap obligation.

**Why now:** HB-001/003 are closed. CDL-076/077 infrastructure is now available. HB-002 can
leverage the truth primitive stack if bootstrap peer records are modeled as truth primitive
nodes. This is the decision to make at sequence lock time.

**Phase sketch:**
- 913: Sequence lock + HB-002 scope decision (CDL-076/077 pipeline vs. separate mechanism)
- 914: HB-002 opening document + bootstrap peer record schema
- 915: Bootstrap peer discovery runtime implementation
- 916: Integration with node_startup_runtime.py (Phase 570)
- 917: Tests
- 918: HB-002 ratification + coherence + capsule v5.30
- 920: Closure gate

**Key open question for sequence lock:**
Can a new node use CDL-076/077 (announce self as a truth primitive node, fetch peer list from
any known node) as its bootstrap mechanism? If yes, HB-002 is wired on top of existing
infrastructure. If no, a separate bootstrap gossip channel is required.

### Window 921–929 — CDL-079 Opening: star.map L3 Groundwork

**Primary goal:** Open CDL-079 for star.map N-gram route index. Do NOT attempt full wiring
in this window — the H-series design is extensive and must be fully retrieved before
committing to a runtime contract. This window establishes the constitutional scope lock
and implements the N-gram indexer runtime, deferring spectral routing wiring.

**Why now:** L1 and L2 are ratified. HB-002 is closed. The star.map is the next architectural
layer. Starting it now prevents the N-gram routing work from being re-derived from first
principles in a later window.

**Phase sketch:**
- 921: Sequence lock + MemPalace retrieval (H-014, H-015, star.map spec full review)
- 922: CDL-079 opening — star.map N-gram route index constitutional scope
- 923: `star_map_route_index_runtime.py` — N-gram extraction, hashing, indexer producer
- 924: Indexer consumer + producer weighting (reputation-weighted route selection)
- 925: star.map dissemination wiring (CDL-076 announces index CID, CDL-077 fetches it)
- 926: Tests
- 927: CDL-079 ratification + coherence + capsule v5.31
- 929: Closure gate

**Explicit deferral in this window:**
- Spectral routing (`spectral_distance()` routing metric) — deferred to CDL-080+
- Onion routing / SURB (L4 privacy) — deferred to CDL-081+
- de Bruijn coverage harness — deferred (defined as future hook in star.map spec §15.1)

---

## 6. RC Milestone Map

| Milestone | Gate criteria | Current status |
|-----------|---------------|----------------|
| RC0.1 | Three-node substrate; 7-agent scenario; reproducible substrate | **`satisfied_for_testbed`** |
| RC1 | + CDL-073 bootstrap schema; truth primitive stack operational | **In progress** — CDL-074/075/076/077 ratified; CDL-078 + HB-002 remaining |
| RC2 | + L3 routing; HB-002 closed; CDL-001 (packaging); persistent rate limiter | CDL-079+ required |
| Launch | + L4 privacy; CDL-070 PQ ceremony; compaction; multi-hop attribution CDL | Long-range |

**RC1 remaining gates (internal definition):**
1. CDL-078 ratified (relay incentives) ← Window 906-912
2. HB-002 closed (P2P bootstrap) ← Window 913-920
3. CDL-001 packaging track evaluated

---

## 7. Relationship to Current Canon

| Artifact | Path | Role |
|---------|------|------|
| Capsule v5.28 | `docs/specs/ilc_antigravity_context_capsule_v5.28.md` | Live G8 track frontier |
| CDL master log | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | Authoritative CDL status |
| RC0.1 checklist | `docs/specs/ilc_rc0_1_readiness_checklist_v0.1.md` | All rows `satisfied_for_testbed` |
| star.map spec | `docs/specs/star.map.ngram.route_index.v1.md` | L3 design source |
| Window 906-912 seq lock | (to be written) | CDL-078 authorization |
| Window 913-920 seq lock | (to be written) | HB-002 authorization |
| Window 921-929 seq lock | (to be written) | CDL-079 / star.map authorization |

---

## 8. What This Roadmap Does NOT Claim

- Row 5 privacy lane is deployed in production (it is `runtime_closed` on testbed only)
- CDL-076/077 gossip/fetch is deployed in production (testbed only)
- Any public launch claim (CDL-001 not yet resolved)
- Option B graduation (first-validator deployed to testbed; broader validator set not authorized)
- L3 routing is operational (H-series designed; not wired)
- CDL-070 PQ ceremony is scheduled (SIM-MONETARY-01 not run)

---

## Postscript 2026-05-04 — Window 1139-1147 Closure

Window 1139-1147 is closed via Phase 1147. The corrected Run 02 Fix2 baseline is now the
SIM-SPECTRAL comparison baseline, the signed 32-node Genesis star map v0.1 is the Atlas
Tier-1 authority baseline, and SIM-SPECTRAL-03 produced a Phase 1146
`CDL-085 recommendation: DEFER`.

Signed Genesis anchor:

- Star map: `out/genesis_core_star_map_v0.1.json`
- Shape: 32 nodes, 55 edges
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`

SIM-SPECTRAL-03 finding:

- The signed authority graph is valid, but raw authority topology is not the right direct
  spectral work graph.
- The next route is a claim-composition projection and 32-node composability audit before
  CDL-085 is reconsidered.
- `CDL-085` remains SIM-gated and unopened.

Runtime posture:

- Runtime semantics unchanged.
- Active runtime remains `epoch_attribution_settle_runtime_1129_fix1.v0.5`.
- One comment-only audit annotation touched `ilc_core/analysis/embedding_pipeline.py`;
  no settlement, QATPS, slashing, or CDL-084 constant changed.

New pre-public-RC obligations:

- Genesis Canonical Lineage Contract.
- Public RC envelope-hash transition policy.
- Truth-primitive permanence community ratification path before Genesis sunset.
- Contributor agreement before public repo.
- License/trademark/identity counsel track.
