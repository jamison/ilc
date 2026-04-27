# ILC Window 921–929 Sequence Lock

Status: locked
Date: 2026-04-28
Window: 921–929
Topic: CDL-080 — Star.Map N-Gram Route Index (L3 Routing Layer)

`window_921_929_commissioned`
`cdl_080_star_map_n_gram_route_index_l3`

---

## 1. Authorization Basis

This window is authorized by:

- Window 913–920 closure gate `08ebdd3e`:
  `star_map_cdl_080_is_next_l3_obligation`
- H-003 complete: `docs/adr/ADR_0033_Star_Map_Homoiconic_Epistemiological_Entity.md`
  — star-map results are first-class nodes; publication boundary enforced
- H-014 complete: `docs/research/ilc_sim_routing_01_results_v0.1.md`
  — spectral two-phase routing validated across all four topology classes
- H-015 complete: `ilc_core/network/d2d/spectral_routing_runtime.py`
  — greedy spectral descent primitive with random-walk fallback; gossip activation
  deferred to H-013 (sealed sender)
- ADR-0003: signed, versioned N-gram route index as advisory routing prefilter
- ADR-0029 + ADR-0032: hypergraph substrate and temporal Laplacian — provides
  spectral_distance() as the L3 routing metric

Pre-window open questions resolved before this sequence lock:

**Q1: Does CDL-080 re-do ADR-0033, or constitute the protocol layer above it?**

Answer: **Protocol layer above it.** ADR-0033 is already accepted — it sets the
node-identity and claim-form contract for published star-map results. CDL-080
constitutionalizes the L3 *operational behavior*: how route index results
circulate, how and when they are promoted to first-class nodes, and what
protocol guarantees they carry. CDL-080 depends on ADR-0033; it does not repeat it.

`cdl_080_depends_on_adr_0033_does_not_repeat_it`

**Q2: Is spectral routing (H-015) wired in this window?**

Answer: **Yes — as a read-only L3 routing prefilter only.** H-015 primitive is
complete and bounded. CDL-080 authorizes `spectral_distance()` as the routing
metric for L3 star.map queries. This does not require gossip activation (H-013)
or beacon emission — only local spectral fingerprint comparison against a target
fingerprint. The full sealed-sender spectral beacon is H-013 scope (post-window).

`spectral_routing_h015_wired_as_l3_prefilter_no_gossip_activation`

**Q3: Does CDL-080 cover ECU attribution for star-map results?**

Answer: **No.** ADR-0033 §2.6 explicitly defers the ECU split rule to H-CON-01
and adjacent downstream CDLs. CDL-080 does not define or imply any ECU formula.
Star-map nodes may sit on an attribution chain (per ADR-0033) but no ECU flows
in this window.

`cdl_080_no_ecu_attribution_deferred_to_h_con_01`

**Q4: What is the L3 → L2 interaction contract?**

Answer: **L3 is advisory; L2 is authoritative.** A route hint produced by L3
tells a node where to look. The actual fetch uses L2 (CDL-077 WANT-HAVE/WANT-BLOCK).
Content that does not match the L2 fetch response is rejected regardless of the
L3 hint. CDL-080 must specify this priority explicitly: L3 prefilter → L2 fetch
→ content truth. No L3 route hint can override CDL-077 fetch semantics.

`l3_advisory_l2_authoritative_l3_does_not_override_cdl_077`

---

## 2. Architectural Grounding

### 2.1 The five-layer network architecture

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| L1 | Announcement gossip | CDL-076 | Ratified Phase 897 |
| L2 | WANT-HAVE / WANT-BLOCK fetch | CDL-077 | Ratified Phase 904 |
| L5 | Relay incentive | CDL-078 | Ratified Phase 911 |
| **L3** | **Star.map N-gram route index** | **CDL-080** | **This window** |
| L4 | Onion routing + SURB | Future CDL | Post-L3 |

CDL-080 fills the L3 slot. L3 sits between L2 (content fetch) and L4 (privacy
routing). Its role: given a query, produce an advisory route hint specifying which
nodes are likely to hold relevant content, so L2 can direct its WANT-HAVE to the
right peers rather than flooding.

### 2.2 Star.map N-gram route index (ADR-0003 constitutionalization)

ADR-0003 defines the route index artifact: hashed N-gram buckets, signed by the
generating agent, versioned, advisory only. CDL-080 constitutionalizes:

1. The **route index update protocol** — how a validator publishes and
   distributes a new route index version
2. The **query interface** — how an agent submits an L3 route query and receives
   advisory hints
3. The **publication boundary** — when a route index computation result crosses
   the ADR-0033 threshold and is promoted to a first-class `Node(type="star_map")`
4. The **spectral routing integration** — how `spectral_distance()` is used
   as the routing metric within L3

### 2.3 Spectral routing integration (H-015)

SIM-ROUTING-01 results (H-014):

| Algorithm | T1 | T2 | T3 | T4 (stress) |
|-----------|----|----|----|----|
| Greedy convergence | 0.9740 | 0.8705 | 0.8615 | 0.6605 |
| Two-phase convergence | 1.0000 | 0.9800 | 0.9815 | 0.8195 |

The two-phase algorithm (greedy descent → random-walk fallback on cycle) clears
the convergence floor in every topology class. Implementation rule:

- L3 route resolution uses `spectral_greedy` first
- On cycle detection: immediate random-walk fallback for remaining hop budget
- Max hops: `3 * ceil(log2(N))` per SIM-ROUTING-01
- Fingerprint noise: sigma=0.005 per SIM-BEACON-01

**What this window does NOT wire:** gossip emission of spectral beacons (H-013
scope). Spectral routing in this window operates only on locally-cached
fingerprints. Agents query the route index; spectral distance narrows the target
peer set; WANT-HAVE/WANT-BLOCK completes the fetch.

### 2.4 ADR-0033 publication boundary enforcement

A star-map computation result becomes a first-class node when it is:
- published, shared across agents, relied upon for routing, OR referenced by
  later claims

CDL-080 must define the protocol signal that marks this boundary. Proposal:
**explicit `publish_star_map_result` call** by the generating agent. Results
remain ephemeral until `publish_star_map_result()` is called. After publication,
the result is gossip-eligible and can receive claims, refutations, and Popperian
review.

`star_map_publication_boundary_explicit_not_automatic`

### 2.5 Scope constraints

```
no_ecu_attribution_for_star_map_results_in_this_window
no_gossip_beacon_activation_in_this_window
no_sealed_sender_wiring_in_this_window
no_l4_onion_routing_in_this_window
no_posk_gate_in_this_window
no_panel_hyperedge_quorum_cdl_in_this_window
no_cdl_081_or_higher_in_this_window
l3_prefilter_is_advisory_l2_fetch_is_authoritative
```

---

## 3. Window Scope

### 3.1 In scope

| Phase | Topic |
|-------|-------|
| 921 | Sequence lock (this document) |
| 922 | CDL-080 opening document — scope, options, selected design |
| 923 | `star_map_route_index_runtime.py` — N-gram index computation and query |
| 924 | ADR-0033 publication boundary: `publish_star_map_result()` and node promotion |
| 925 | Spectral routing integration: H-015 wired as L3 prefilter |
| 926 | Tests |
| 927 | CDL-080 ratification + coherence report + capsule v5.31 |
| 928 | Closure gate |
| 929 | Spare / overflow |

### 3.2 Explicit exclusions

```
no_ecu_attribution_formula
no_gossip_beacon_emission
no_sealed_sender_activation
no_l4_routing
no_posk_admission_gate
no_star_expansion_of_hyperedges
no_panel_hyperedge_quorum_rules
no_cdl_081_or_higher
```

---

## 4. Hard Pass Conditions

The Phase 928 closure gate must verify all 8 conditions:

| # | Condition |
|---|-----------|
| 1 | `ilc_core/network/star_map/star_map_route_index_runtime.py` exists |
| 2 | `STAR_MAP_RUNTIME_VERSION` and `CDL_080_DEPENDENCY` tokens present |
| 3 | N-gram route index computation is deterministic and sort_keys=True serializable |
| 4 | `publish_star_map_result()` exists and promotes result to `Node(type="star_map")` |
| 5 | Spectral routing primitive (H-015 `spectral_routing_runtime.py`) wired as L3 prefilter |
| 6 | L3 advisory / L2 authoritative contract enforced: no L3 hint overrides CDL-077 fetch |
| 7 | No ECU attribution, no gossip beacon activation, no sealed sender in this window |
| 8 | CDL-080 opened (Phase 922) and ratified (Phase 927) in CDL master log |

---

## 5. Phase Detail

### Phase 922 — CDL-080 Opening

**Deliverables:**
- CDL-080 row inserted in `docs/specs/ilc_constitutional_decision_log_v0.1.md` as `open`
- `docs/specs/ilc_cdl_080_star_map_n_gram_route_index_opening_922_v0.1.md`

**Options to evaluate:**
- Option A: Route index as pure gossip artifact (no node promotion) — ruled out by ADR-0033
- Option B: Route index as first-class node from creation — too permissive; creates
  ephemeral scratch nodes with governance overhead
- **Option C (proposed):** Dual mode — results are ephemeral until `publish_star_map_result()`;
  publication triggers ADR-0033 node promotion; spectral routing operates on ephemeral
  fingerprints without requiring promotion first

**Parent CDLs:** CDL-077 (L2 fetch) / CDL-079 (bootstrap — route index distributable
as a bootstrap bundle component in future windows)

---

### Phase 923 — Star Map Route Index Runtime

**File:** `ilc_core/network/star_map/star_map_route_index_runtime.py`

**Required tokens:**
```python
STAR_MAP_RUNTIME_VERSION = "star_map_route_index_runtime_923.v0.1"
CDL_080_DEPENDENCY = "cdl_080_star_map_n_gram_route_index.v0.1"
ADR_0003_DEPENDENCY = "adr_0003_star_map_route_index"
ADR_0033_DEPENDENCY = "adr_0033_star_map_homoiconic_entity"
```

**Core functions:**
```python
def compute_route_index(
    nodes: list[Node],
    epoch: int,
    agent_id: str,
) -> RouteIndex:
    """Compute N-gram route index from a node set.
    Deterministic. sort_keys=True serialization.
    Returns RouteIndex(buckets, epoch, generator_ref, parameter_digest).
    """

def query_route_index(
    route_index: RouteIndex,
    query: str,
    top_k: int = 16,
) -> list[RouteHint]:
    """Return advisory route hints (peer endpoints) matching query N-grams.
    Purely advisory — hints must be validated by L2 WANT-HAVE before use.
    """

def publish_star_map_result(
    route_index: RouteIndex,
    source_node_set_digest: str,
    agent_id: str,
    epoch: int,
) -> Node:
    """Promote a route index result to a first-class Node(type='star_map').
    Enforces ADR-0033 claim-form contract: entity_kind, generator_ref,
    source_artifact_refs, source_node_set_digest, method, parameter_digest,
    result_payload, epoch, agent_id all present.
    """
```

---

### Phase 924 — ADR-0033 Publication Boundary

**Scope:** Verify ADR-0033 claim-form contract is enforced at publication boundary.
Write tests confirming:
- Ephemeral results cannot receive claims before `publish_star_map_result()` is called
- Published nodes carry all required ADR-0033 fields
- Node ID is content-addressed from canonical payload

**No new runtime files** — this is a test + contract verification phase.

---

### Phase 925 — Spectral Routing Integration

**Scope:** Wire H-015 `spectral_routing_runtime.py` as L3 prefilter.

**Integration contract:**
```python
# L3 route resolution sequence:
# 1. Compute spectral fingerprint of query neighborhood (local, no gossip)
# 2. Spectral greedy descent to find peer(s) closest to target fingerprint
# 3. On cycle: random-walk fallback for remaining hop budget
# 4. Return ranked list of candidate peers (advisory)
# 5. Caller submits WANT-HAVE (CDL-077 L2) to candidates in order
# 6. L2 response is authoritative; L3 hint has no override authority

def l3_route_and_fetch(
    query: str,
    local_fingerprint: list[float],
    peer_registry: GossipPeerRegistry,
    cdl_077_fetch_fn: Callable,
) -> dict | None:
    """Advisory L3 routing → authoritative L2 fetch.
    Returns fetched content dict or None if not found.
    """
```

**H-015 boundary preserved:** gossip activation NOT wired. Spectral routing
operates on locally-cached peer fingerprints only (from `SpectralBeacon` stubs).
Beacon gossip emission requires H-013 (sealed sender) — not this window.

---

### Phase 926 — Tests

**File:** `tests/test_phase_921_929_cdl_080_star_map.py`

**Minimum 28 tests:**

| Group | Tests |
|-------|-------|
| 1. Module tokens | runtime exists; version token; CDL-080/ADR-0003/ADR-0033 dep tokens |
| 2. compute_route_index | deterministic output; sort_keys canonical; epoch-stamped |
| 3. query_route_index | returns route hints; top_k respected; empty index → [] |
| 4. publish_star_map_result | returns Node(type="star_map"); ADR-0033 fields present; content-addressed ID |
| 5. ADR-0033 boundary | ephemeral result has no node ID before publish; publish promotes correctly |
| 6. Spectral routing integration | greedy descent + fallback path exercised; cycle triggers fallback |
| 7. L3 advisory contract | L3 hint does not override L2 result; L2 None → not found |
| 8. No ECU / no gossip | no ECU call in source; no beacon gossip call in source |
| 9. CDL-080 in master log | CDL master log contains CDL-080 row with opened_phase: 922 |
| 10. Commit scope guard | commit touches only allowed paths |

---

### Phase 927 — CDL-080 Ratification + Coherence + Capsule v5.31

**CDL-080 ratification:**
- CDL master log row updated from `open` → `ratified`
- Ratification evidence: `docs/specs/ilc_cdl_080_star_map_n_gram_route_index_ratification_evidence_927_v0.1.md`
- Atomic commit with `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=927`

**Coherence report:** `docs/specs/ilc_integration_coherence_report_927_v0.1.md`

Key checks:
- L2 fetch semantics (CDL-077) unchanged by L3 wiring
- CDL-079 bootstrap bundle distribution unaffected by star.map layer
- ADR-0033 claim-form contract fully enforced at publication boundary
- No ECU attribution introduced
- H-015 gossip boundary respected

**Capsule:** `docs/specs/ilc_antigravity_context_capsule_v5.31.md` — supersedes v5.30

**Estimated test count:**

| Scope | Tests |
|-------|-------|
| Window 921–929 (CDL-080) | ~28 |
| Prior windows | 426 |
| **Total (estimated)** | **~454** |

---

### Phase 928 — Closure Gate

**File:** `docs/specs/ilc_window_921_929_closure_gate_928_v0.1.md`

On PASS emits:
```
window_921_929_closed
capsule_v5_31_is_current_frontier
cdl_080_ratified
l3_star_map_route_index_constitutionally_locked
spectral_routing_h015_wired_as_l3_prefilter
adr_0033_publication_boundary_enforced
h_con_01_cdl_hyperedge_ecu_attribution_is_next_governance_obligation
h_013_sealed_sender_remains_blocked_pending_human_authorization
```

---

## 6. Forward Obligations After This Window

| Obligation | Next step | Evidence basis |
|------------|-----------|----------------|
| H-CON-01: CDL hyperedge ECU attribution | Next governance CDL | H-series doc; star expansion blocked on this |
| H-CON-02: CDL panel quorum and diversity rules | After H-CON-01 | H-series doc |
| H-CON-03: CDL epoch KPI temporal spectral fields | Deliberate planning | H-006b + H-005 complete |
| H-007: CDL spectral hash in epoch commitment | Deliberate planning | H-005 complete |
| H-013: Sealed sender implementation | Human authorization | ADR-0034 accepted |
| H-011: Patent assessment | Human action | H-005 complete |
| CDL-001: Packaging track | Pre-launch | genesis_blocker |
| SIM-REUSE-01: Reuse signal in W calibration | Post-ADR-0029 impl | New — hypergraph v0.3 |
| Hypergraph v0.3 NOW items (proto schema, EdgeType, WeightParams) | Pre-M-018 | Planning doc v0.3 §1.4 |

---

## 7. Sequence Constraints

1. Phase 922 (CDL-080 open) must precede Phase 923 (runtime)
2. Phase 923 (runtime) must precede Phase 924 (publication boundary)
3. Phase 924 must precede Phase 925 (spectral routing integration)
4. Phase 925 must precede Phase 926 (tests)
5. Phase 926 (tests passing) must precede Phase 927 (ratification)
6. Phase 927 (ratification) must precede Phase 928 (closure gate)
7. No ECU attribution, gossip beacon activation, or sealed sender in this window
8. L3 advisory contract enforced throughout: L2 is always authoritative

---

## 8. Governing Tokens

```
window_921_929_commissioned
cdl_080_star_map_n_gram_route_index_l3
cdl_080_depends_on_adr_0033_does_not_repeat_it
spectral_routing_h015_wired_as_l3_prefilter_no_gossip_activation
cdl_080_no_ecu_attribution_deferred_to_h_con_01
l3_advisory_l2_authoritative_l3_does_not_override_cdl_077
star_map_publication_boundary_explicit_not_automatic
no_ecu_attribution_for_star_map_results_in_this_window
no_gossip_beacon_activation_in_this_window
```
