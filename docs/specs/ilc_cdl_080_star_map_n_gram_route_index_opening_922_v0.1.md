# CDL-080: Star.Map N-Gram Route Index — Opening Document

**Phase:** 922
**Date:** 2026-04-28
**Status:** open
**Window:** 921–929
**Topic:** L3 routing layer — star.map N-gram route index as constitutional routing prefilter

---

## 1. Problem Statement

As of capsule v5.30, ILC has two ratified transport layers:

- **L1** (CDL-076): announcement gossip — nodes announce their existence
- **L2** (CDL-077): WANT-HAVE / WANT-BLOCK fetch — nodes fetch specific content by CID

The missing layer is **L3**: given a semantic query (not a known CID), which peers
are most likely to hold relevant content? Without L3, agents must either:
1. Broadcast WANT-HAVE to all known peers (flooding — scales poorly), or
2. Know the CID in advance (requires out-of-band discovery)

CDL-080 constitutionalizes the star.map N-gram route index as the L3 routing
prefilter that fills this gap.

---

## 2. Architectural Context

### 2.1 Prior work this CDL depends on

| Document | Status | Contribution |
|---|---|---|
| ADR-0003 | Accepted | Defines the route index artifact: signed N-gram bucket map, advisory hints |
| ADR-0033 (H-003) | Accepted | Star-map results are first-class nodes at the publication boundary |
| H-014 SIM-ROUTING-01 | Complete | Spectral two-phase routing validated: P50 = 1–2 hops, ≥ 0.80 convergence in all topologies |
| H-015 spectral routing primitive | Complete | `spectral_routing_runtime.py` — greedy descent + random-walk fallback |
| CDL-077 | Ratified Phase 904 | L2 fetch — the authoritative content retrieval layer that L3 feeds |

### 2.2 What CDL-080 does NOT cover

- ECU attribution for star-map results → deferred to H-CON-01
- Gossip beacon emission → deferred to H-013 (sealed sender)
- Onion routing (L4) → future CDL
- PoSK admission gate → H-008, blocked on H-011 patent assessment
- Panel hyperedge quorum rules → H-CON-02

---

## 3. Options Considered

### Option A — Route index as pure gossip artifact (no node promotion)

Each validator maintains a local route index and shares it over gossip. Results
are ephemeral query responses only — never promoted to first-class graph nodes.

**Rejected.** Violates ADR-0033 (accepted): published star-map results that are
relied upon for routing MUST be first-class nodes with a claim-form contract,
challengeable by other agents, and enterable into the Popperian evaluation
apparatus. Ephemeral-only results cannot be audited, refuted, or attributed.

`option_a_rejected_violates_adr_0033`

### Option B — Route index as first-class node from creation

Every route index computation immediately creates a `Node(type="star_map")`,
whether or not it is published or relied upon.

**Rejected.** Creates governance overhead for private scratch work. Every local
experimentation event would produce a claimable, refutable, stake-bearing node.
ADR-0033 §2.1 explicitly scopes the promotion trigger to the
publication/reliance boundary, not the computation moment.

`option_b_rejected_premature_promotion`

### Option C — Dual mode: ephemeral until published (SELECTED)

Route index results are ephemeral by default. Spectral routing operates on
ephemeral fingerprints without requiring promotion. When a result crosses the
ADR-0033 publication boundary (shared, relied upon, or referenced by later
claims), `publish_star_map_result()` is called explicitly, promoting the result
to a first-class `Node(type="star_map")` with the full ADR-0033 claim-form
contract.

**Selected.** Preserves the ADR-0033 node identity scheme, keeps private scratch
work ephemeral, and allows spectral routing to operate pre-publication.

`option_c_selected_dual_mode_ephemeral_until_published`

---

## 4. CDL-080 Constitutional Definition

### 4.1 Layer definition

The star.map N-gram route index is hereby constitutionally defined as **Layer 3
(L3)** of the ILC network stack — the advisory routing prefilter between L1
announcement gossip and L2 content fetch.

**L3 routing sequence:**

```
Agent query (semantic string or content_type filter)
  → L3: compute route hints via N-gram route index + spectral routing prefilter
  → L3 returns: ordered list of candidate peer endpoints (advisory)
  → L2: agent submits WANT-HAVE to candidates (CDL-077)
  → L2 returns: content or WANT-BLOCK CID (authoritative)
  → L2 authoritative result is the truth; L3 hint has no override authority
```

`l3_advisory_l2_authoritative`

### 4.2 Route index artifact (from ADR-0003)

A route index is a signed, versioned map from N-gram hashes to peer endpoint
sets. Format:

```json
{
  "schema_version": "route_index_v1",
  "epoch": <int>,
  "generator_agent_id": "<agent CID>",
  "buckets": {
    "<sha256(ngram)[:16]>": ["<endpoint1>", "<endpoint2>", ...],
    ...
  },
  "parameter_digest": "<sha256 of bucket construction parameters>",
  "signed_by": "<agent pubkey hex>",
  "signature": "<ML-DSA-65 signature over canonical JSON excluding signature>"
}
```

Canonical form: `json.dumps(index_without_signature, sort_keys=True).encode()`

### 4.3 Spectral routing prefilter

Within L3 route resolution, `spectral_distance(λ_A, λ_B) = ||λ_A − λ_B||₂`
(from `ilc_core/network/d2d/spectral_routing_runtime.py`) is the routing metric
for ordering candidate peers by epistemic proximity to the query neighborhood.

Algorithm (per SIM-ROUTING-01 H-014):
1. Greedy descent: hop toward peer with minimum spectral distance to target fingerprint
2. On cycle detection: immediate random-walk fallback for remaining hop budget
3. Max hops: `3 × ⌈log₂(N)⌉` where N = peer count

Spectral routing in this window operates on **locally-cached peer fingerprints**
only. Gossip emission of spectral beacons is H-013 scope.

`spectral_routing_local_fingerprints_only_no_beacon_gossip`

### 4.4 Publication boundary (ADR-0033 enforcement)

A route index computation result is promoted to a first-class `Node(type="star_map")`
via explicit `publish_star_map_result()` call. The published node carries:

| Field | Required | Source |
|---|---|---|
| `entity_kind` | Yes | `"route_cluster"` \| `"panel_result"` \| `"navigation_overlay"` |
| `generator_ref` | Yes | Agent CID of generating agent |
| `source_artifact_refs` | Yes | CIDs of source nodes used in computation |
| `source_node_set_digest` | Yes | SHA-256 of sorted source node CID list |
| `method` | Yes | `"n_gram_route_index_v1"` |
| `parameter_digest` | Yes | SHA-256 of construction parameters |
| `result_payload` | Yes | Serialized route index artifact |
| `epoch` | Yes | Publication epoch |
| `agent_id` | Yes | Publishing agent CID |

Node ID: content-addressed from canonical JSON of all required fields (sort_keys=True).

### 4.5 L3 / L2 priority rule (non-negotiable)

CDL-077 fetch semantics are authoritative. A WANT-HAVE/WANT-BLOCK response that
does not match the L3 hint is **not** an error — it is the correct behavior. L3
hints are routing optimizations, not content guarantees. Any implementation that
treats a non-matching L2 response as an error on the basis of L3 expectation is
non-conforming.

`l2_non_match_is_not_l3_error`

---

## 5. Implementation Scope

| File | Phase | Change |
|---|---|---|
| `ilc_core/network/star_map/star_map_route_index_runtime.py` | 923 | NEW: route index computation and query |
| `ilc_core/network/star_map/__init__.py` | 923 | NEW: module init |
| `ilc_core/node/node_startup_runtime.py` | 925 | PATCH: L3 route resolution wired alongside static peer config |
| `tests/test_phase_921_929_cdl_080_star_map.py` | 926 | NEW: ≥28 tests |

---

## 6. Dep-Chain Tokens

```python
STAR_MAP_RUNTIME_VERSION = "star_map_route_index_runtime_923.v0.1"
CDL_080_DEPENDENCY = "cdl_080_star_map_n_gram_route_index.v0.1"
ADR_0003_DEPENDENCY = "adr_0003_star_map_route_index"
ADR_0033_DEPENDENCY = "adr_0033_star_map_homoiconic_entity"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
H015_DEPENDENCY = "spectral_routing_runtime_h015.v0.1"
```

---

## 7. Forward Obligations

| Item | Window | Prerequisite |
|---|---|---|
| ECU attribution for star-map nodes | H-CON-01 CDL | ADR-0029 + H-001 |
| Gossip beacon activation | H-013 | ADR-0034 + sealed sender impl |
| PoSK admission gate | H-008 CDL | H-011 patent assessment |
| Panel hyperedge quorum rules | H-CON-02 CDL | H-CON-01 |
| Star expansion implementation | H-012 | H-CON-01 |

---

## 8. Ratification Readiness Evidence Checklist

At Phase 927, ratification evidence must confirm:

- [ ] 1. `star_map_route_index_runtime.py` exists; version + dep tokens present
- [ ] 2. Route index computation is deterministic (same inputs → same output)
- [ ] 3. `publish_star_map_result()` produces ADR-0033 compliant `Node(type="star_map")`
- [ ] 4. Spectral routing (H-015) wired as L3 prefilter; gossip boundary preserved
- [ ] 5. L3 advisory / L2 authoritative contract verified by test
- [ ] 6. No ECU call, no gossip beacon call in star_map source
- [ ] 7. ≥28 tests passing, zero regressions
- [ ] 8. CDL-080 row in master log: `opened_phase: 922`, `ratified_phase: 927`
