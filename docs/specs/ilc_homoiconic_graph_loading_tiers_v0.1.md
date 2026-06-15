# ILC Homoiconic Graph Loading Tiers v0.1

**Status:** pre-canon synthesis artifact — input for future ratification lane(s)
**Date:** 2026-06-13
**Owner lane:** Atlas Research / Genesis Compile
**Authority:** non-normative synthesis; does not override ratified CDL, accepted ADR,
  or live runtime. Companion to `ilc_node_schema_architectural_synthesis_v0.1.md`.

`homoiconic_graph_loading_tiers_v0_1_published`
`load_tier_property_pre_canon_phase_genesis_atlas`
`three_tier_loading_model_synthesis_artifact`
`any_agent_can_serve_content_addressed_content`
`invitation_attribution_chain_synthesis_recorded`

---

## 1. Purpose

This document defines a three-tier **priority classification** for vertices in
the ILC hypergraph. The tiers are not download batches — they are a statement
about when content must be locally available versus when it can be fetched
on demand from any peer.

The model is motivated by three converging requirements:

1. **Homoiconic completeness.** If a file is in the RC repo, it must be
   representable as a vertex in the hypergraph. A graph that cannot represent
   files it has not pre-processed has a hidden class of objects outside its own
   description — it is not fully homoiconic.

2. **Bootstrap tractability.** A new agent receiving the graph for the first
   time (ADR-0009, CDL-073) should not be required to download thousands of
   spec documents to function. The governance spine must be immediately
   available; everything else is held as pointers and fetched when traversed.

3. **Permissionless content serving.** Because all content is content-addressed
   and cryptographically signed back to Genesis (ADR-0009 §hash-chain), any
   agent can serve any content to any other agent. The receiver verifies the
   hash chain independently — server identity is irrelevant. This means the
   graph can grow without central distribution authority.

This spec introduces the `load_tier` vertex property, currently used as a
candidate annotation in the Atlas research lane. It is not yet ratified.
A CDL is required before `load_tier` becomes a canonical field of the vertex
schema.

---

## 2. Relationship to Existing Canon

| Document | Relationship |
|----------|-------------|
| ADR-0009 (four-layer content-addressed bundle distribution) | Foundational. All content is DAG-CBOR encoded, COSE Sign1 signed, and CIDv1 identified, forming a verifiable chain back to Genesis. This makes any peer a valid server for any content. |
| CDL-073 (homoiconic bootstrap schema) | Governs the wire format and genesis-authority assertion schema for Tier 0 content. This spec classifies which vertices are Tier 0. |
| `ilc_node_schema_architectural_synthesis_v0.1.md` | Canonical node schema input; `load_tier` is an additional property on that schema's vertex envelope. |
| `ilc_agent_onboarding_organic_graph_hydration_spec_1545p_fix10_v0.1.md` | The onboarding hydration path is a Tier 1 pointer → Tier 2 fetch traversal in this model's terms. Invitation provenance established there (Phase 1493p) is the basis for the attribution chain described in §5. |
| `ilc_agent_subgraph_hydration_contract_1545p_fix16_v0.1.md` | Defines the permissioned hydration boundary; this spec defines the `load_tier` property those boundaries operate on. |
| ADR-0035 (homoiconic type definition system) | Type definitions are Tier 0 — they must be loadable before any typed vertex can be interpreted. |

---

## 3. The Three Tiers

The tiers describe **when** content must be available, not **who** serves it or
**how much** is downloaded at once. An agent always holds the complete star map
(all vertex IDs and all edges) but holds zero Tier 1 content until explicitly
requested. Content is fetched per-node from any willing peer, not per-tier in
bulk.

---

### Tier 0 — Genesis Core (eager, always materialized locally)

**Definition:** The minimal set of vertices and edges required for a new
participant to verify protocol identity, interpret truth primitives, locate
governance decisions, and produce or verify signed protocol artifacts — without
fetching any additional content from any peer.

**What belongs in Tier 0:**
- All `truth_primitive:*` vertices (seven truth primitives, CDL-073)
- All `cdl:*` vertices (CDL register)
- All `adr:*` vertices (ADR register)
- All `artifact:genesis_*` vertices (genesis state bundle, bootstrap boundary,
  genesis intent attestation, etc.)
- All `policy:*` vertices (theta_hard, theta_soft, accrual_governor, sunset, etc.)
- Edges between these vertices (governance and implementation relationships)
- The canonical type registry (ADR-0035)
- Key architectural synthesis documents whose definitions are prerequisite for
  interpreting any other vertex (e.g., node_schema_architectural_synthesis,
  sdk_boundary_contract, adm_001/002/003 v0.2, this document)

**Property value:** `"load_tier": 0`

**Loading behaviour:** Fully materialized at graph open. No remote fetch
required. An agent that has only Tier 0 content can still participate in the
protocol — it knows all governance decisions, all truth primitive definitions,
and can verify any signed object it subsequently receives.

**Approximate size (current canon):** ~300–400 vertices, ~7,000 edges.

---

### Tier 1 — Star Map (pointer only, content never held unless requested)

**Definition:** Every other vertex in the graph. An agent holds the complete
star map — every Tier 1 vertex ID and its full edge list — but holds no content
for any of them. The star map is the graph's self-description at pointer
resolution: you know everything that exists and how it connects, without holding
any of it.

**What belongs in Tier 1:**
- All `source:*` vertices (every file in the RC repo not in Tier 0)
- All `spec:*` vertices (spec documents, research memos, phase prompts)
- All `test:*` vertices
- All `tool:*` and `sidecar:*` vertices
- Candidate vertices added by the Atlas research lane

**Property value:** `"load_tier": 1`

**What an agent holds for a Tier 1 vertex:**
`vertex_id`, `vertex_type`, `source_path`, `label`, `load_tier`, adjacency
list (edge references with types and roles). No source content. No hydrated
fields.

**Key property:** PageRank, BFS, reachability, and path-finding all work on
the star map alone. An agent can answer "does a path exist from this governance
vertex to that source file?" without fetching any content. Only when it needs
to read, reason about, or re-attest the content of a specific vertex does it
request hydration.

**Approximate size (full RC repo):** ~2,000–3,000 additional vertices.

---

### Tier 2 — On-Demand Hydration (content fetched when traversal reaches the node)

**Definition:** The full source content of a Tier 1 stub, fetched when an agent
or traversal algorithm explicitly needs it.

**What triggers hydration:**
- An agent navigating to a specific vertex and requesting its content
- A traversal algorithm that needs content for semantic matching or attestation
- The Atlas research agent processing a batch containing this vertex

**Serving model:** Any agent that holds a hydrated copy of a vertex can serve
it to any requesting agent. The receiving agent verifies the hash chain
independently (ADR-0009): content hash → commit.epoch → genesis-authority
assertion → genesis key. The server's identity is not part of the trust model.
A vertex served by an unknown peer is as trustworthy as one served by Genesis
itself, provided the chain verifies.

**Local behaviour:** The hydrated content is cached in the agent's local LMDB
store. It does not automatically propagate back to the canonical graph. Only
an Atlas KEEP decision (via the evaluator gain gate) can promote new
relationships into the research baseline, and only an explicit manual gate can
promote research candidates into canon.

---

## 4. The `load_tier` Property

```json
{
  "vertex_id": "spec:docs/specs/ilc_node_schema_architectural_synthesis_v0.1",
  "vertex_type": "spec_document",
  "label": "ILC Node Schema: Architectural Synthesis v0.1",
  "properties": {
    "load_tier": 0,
    "source_path": "docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md",
    "candidate": true
  }
}
```

**Allowed values:** `0`, `1` (integer; `2` is a runtime state, not a stored
property — a vertex transitions to hydrated locally but remains `load_tier: 1`
in the canonical record)

**Default:** `1` — if `load_tier` is absent, the vertex is treated as a Tier 1
stub.

**Tier 0 assignment rules (pre-ratification guidance):**
A vertex receives `load_tier: 0` if and only if:
- Its `vertex_type` is one of: `truth_primitive`, `cdl`, `adr`, `artifact`,
  `policy`
- It is a canonical architectural synthesis document defining terms prerequisite
  for interpreting other vertices
- It is an ADM document at v0.2 or later

All other vertices default to `load_tier: 1`.

---

## 5. Permissionless Serving and the Verification Chain

Because all ILC content is content-addressed and COSE Sign1 signed (ADR-0009),
the identity of the serving peer is protocol-irrelevant:

```
received_content
    → CID matches vertex's content_digest
    → DAG-CBOR canonical encoding verified
    → COSE Sign1 signature traces to commit.epoch
    → commit.epoch traces to genesis-authority assertion (CDL-073)
    → genesis-authority assertion signed by genesis key (Tier 0, already held)
    → VERIFIED
```

Any agent in the network can serve any content at any tier. A new agent with
only Tier 0 locally can request any Tier 1 vertex from any peer it discovers,
verify the chain independently, and accept or reject the content on its own
authority. No trusted distribution server is required. This is the homoiconic
serving property: the graph distributes itself.

**Practical consequence:** When an agent wants to read
`spec:docs/specs/ilc_node_schema_architectural_synthesis_v0.1`, it broadcasts
a content request (or queries known peers), receives the blob from whoever
responds first, verifies the hash chain against its local Tier 0, and accepts
or discards. The star map tells it this vertex exists and what it connects to
before the content arrives.

---

## 6. Invitation Attribution and Growth Incentives

When agent A invites agent B into the network, a `link.claim` edge is created:

```
A --[link.claim, role="inviter"]--> B
```

This edge is a provenance record. It is not a minting event, not a reward
issuance, and not a validator admission path (consistent with Phase 1493p canon,
`ilc_agent_onboarding_organic_graph_hydration_spec_1545p_fix10_v0.1.md §2`).

**Attribution chain mechanics (pre-canon direction):**

B's subsequent contributions — new vertices attested via `assert.truth`,
new agents B invites, new `commit.epoch` objects referencing B's nodes — create
a growing provenance subgraph. When a future ECU attribution sweep evaluates
B's contribution to the graph, the `link.claim` edge from A is evidence that
A initiated the chain. Attribution flows:

```
B's verified contribution
    → ECU credit proposed for B (via standard epistemic credit rules)
    → link.claim edge to A detected
    → portion of credit attributed to A as inviter
    → if A invited B who invited C who contributed verified nodes:
      → chain attribution carries forward (with decay per hop, TBD by CDL)
```

**Why this is architecturally sound:** Because every node is content-addressed
and attribution is graph-native (recorded as `link.claim` edges, not in a
separate referral registry), the attribution chain is itself a verifiable part
of the graph. It is auditable, refutable, and carries the same epistemic weight
as any other claim. A false attribution claim can be challenged via
`refute.claim`.

**Current status:** The invitation provenance edge is established canon
(Phase 1493p). The ECU attribution mechanics described here are pre-canon
direction — a CDL is required before any runtime credit distribution operates
on this chain.

---

## 7. The Genesis Graph as Verification Object

The Tier 0 graph is not merely the starting state — it is the trust anchor for
all subsequent verification. This is the homoiconic property stated precisely:

> The ILC hypergraph contains, within itself, all the information required to
> verify any artifact produced according to the ILC protocol.

Concretely:
- The genesis key (held in `artifact:genesis_state_bundle`, Tier 0) is the
  root of the COSE signing chain
- The seven truth primitives (Tier 0) are the complete vocabulary for all
  protocol interactions
- The CDL/ADR register (Tier 0) contains all governance decisions
- Any signed object received from any peer can be verified by walking from that
  object's signature back to genesis — using only Tier 0 content

This means: **a new agent that has only Tier 0 can safely accept, verify, and
build on any Tier 1 or Tier 2 content without trusting the peer that served
it.** The graph bootstraps its own trust.

For the Atlas research lane specifically: candidate vertices and edges added by
the agent are proposed as `assert.truth` objects, evaluated against the
existing graph structure (the gain function measures improvement in
connectivity and authority reachability), and committed or reverted. The
research baseline is itself a verifiable graph object — its provenance traces
back through the commit history to the canonical graph, which traces to Genesis.

---

## 8. Homoiconic Completeness Invariant

> For every file F in the RC repo that is not excluded by policy
> (`.venv/`, `__pycache__/`, `build/`, `Z_Past_Chats/`, `out/`), there exists
> a vertex V in the hypergraph such that `V.source_path == relative_path(F)`.
> V may be a Tier 1 stub — its content need not be held locally — but it must
> exist in the star map and its edges to governance vertices must be indexed.

This invariant makes the graph a complete self-index. A traversal starting from
any governance vertex can reach any file in the repo via Tier 1 stub vertices.
Any of those stubs can be hydrated on demand from any peer. The graph describes
the entire codebase without materializing it.

The Atlas research loop builds this index. Level 1 passes emit Tier 1 stubs
and edges. The manual citation pass emits Tier 0 vertices for governance-spine
documents. Level 2 (Popperian) deepens edge density around highest-PageRank
nodes. Together they satisfy the invariant over the full RC repo.

---

## 9. Relationship to Atlas Research Lane

- **Atlas loop:** all emitted candidate vertices are implicitly `load_tier: 1`
  (stubs with edges; content not held in the graph record)
- **Manual citer:** emits `load_tier: 0` for governance-spine specs per §4;
  `load_tier: 1` for all others
- **After ratification:** the compiler pass assigns `load_tier` at compile time
  based on vertex type, making it a first-class canonical field

---

## 10. Open Questions for Future Ratification Lane

1. **Stub mandatory fields.** What fields must a Tier 1 stub include at minimum?
   Proposal: `vertex_id`, `vertex_type`, `source_path`, `label`, `load_tier`,
   `content_digest` (hash of source content, for integrity verification without
   full hydration). The content digest lets an agent confirm it received the
   right content without having fetched it before.

2. **Attribution chain decay rate.** How does ECU credit decay per hop in the
   invitation chain? Proposal: geometric decay at a rate defined by a CDL
   parameter (e.g., 50% per hop, configurable). Must not create infinite-chain
   gaming incentives.

3. **Tier 0 size limit.** Soft cap at 500 vertices; CDL must explicitly grant
   Tier 0 status for additions beyond that cap, to bound the mandatory bootstrap
   footprint.

4. **Tier 0 bundle section in ADR-0009.** A follow-on CDL should define the
   Tier 0 bundle section format so bundles self-describe their loading tier
   classification, enabling a new agent to identify Tier 0 content without
   prior graph knowledge.

5. **`load_tier` field placement.** Current pre-canon placement is
   `properties.load_tier`. The ratification lane should decide whether it
   belongs in the top-level vertex envelope or remains in `properties`.

6. **Content request protocol.** The mechanism by which an agent broadcasts a
   content request for a specific `vertex_id` / CID and receives a response
   from any willing peer is not yet specified. This is ADR-0009 territory but
   needs a concrete sub-protocol for Tier 1 → Tier 2 demand-fetch.

---

## 11. Non-Goals

- This spec does not define the content request sub-protocol (ADR-0009
  territory).
- This spec does not define which vertices are excluded from the RC repo index.
- This spec does not activate public-facing content serving. Serving requires
  independent CDL authorization.
- This spec does not change the canonical hypergraph
  (`out/genesis_observed_repo_hypergraph_v0.1.json`). `load_tier` is currently
  a candidate-only property in the Atlas research lane.
- The invitation attribution chain described in §6 is pre-canon direction. No
  ECU credit distributes on this chain until a ratifying CDL authorizes it.

---

## 12. Supersession Note

If a CDL ratifies a loading tier model that differs from this spec, add the
standard supersession tombstone:

> **SUPERSEDED.** This draft pre-dates [superseding CDL]. It is not a governing
> source. Canonical authority: [CDL reference].
