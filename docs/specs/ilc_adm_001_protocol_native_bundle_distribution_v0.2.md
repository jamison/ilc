# ADM-001: Protocol-Native Bundle Distribution Architecture (v0.2)

**Type:** Architectural Decision Memo  
**Status:** Proposed (awaiting decision-log ratification)  
**Date:** 2026-02-18 (v0.2 amended 2026-02-19)  
**Author:** Claude Opus 4.6 (Strategic Architectural Reviewer)  
**Supersedes:** ADM-001 v0.1 (which covered Layer 0 only)  
**Amendment reason:** v0.1 addressed protocol rules and parameters but was silent on the epistemic graph's living state — its nodes, edges, shards, star maps, subscriptions, contracts, and agent connectivity. v0.2 introduces a four-layer content-addressed architecture that covers the full protocol ontology from type system through live operations.

---

## 1. Decision (amended)

ILC adopts a **four-layer content-addressed distribution architecture**:

| Layer | Name | Contents | Lifecycle |
|---|---|---|---|
| Layer 0 | Protocol Bundle | Rules, type system, schemas, parameters, invariants | Changes at protocol upgrades only |
| Layer 1 | Genesis State Bundle | Initial graph state, seed claims, shard topology, agent roster | Created once at launch, immutable thereafter |
| Layer 2 | Epoch State Snapshots | Periodic checkpoints of full graph state | Created every N epochs, allows fast bootstrap |
| Layer 3 | Wire Protocol | Live agent-to-agent and agent-to-network operations | Real-time, not bundled |

All layers (0-2) use DAG-CBOR encoding, COSE Sign1 signatures, and CIDv1 identification. Each layer references the layer above it by CID, creating a verifiable chain from live operations back to the protocol rules.

The Python package (wheel + sdist) remains as a reference implementation distribution channel for human developers.

---

## 2. Context (amended from v0.1)

### 2.1 — 2.4: Unchanged from v0.1

(Reproducibility tension, agent heterogeneity requirement, self-verification principle, OpenClaw integration opportunity — see v0.1 for full text.)

### 2.5 The graph connectivity gap (NEW in v0.2)

The v0.1 bundle specification addressed protocol parameters (scoring weights, invariants, epoch timing) but omitted the protocol's complete type system — the schemas that define what objects can exist in the epistemic graph and how they relate to each other. An agent needs more than rules; it needs to know the structure of every object type it will encounter: nodes, edges, shards, agent profiles, star maps, subscriptions, contracts, epoch records, and capability proofs.

Additionally, v0.1 did not address how an agent joins an already-running network. It needs the current graph state — a snapshot — not just the rules. And it needs to know how to communicate with other agents — the wire protocol.

The four-layer architecture addresses all of these: Layer 0 carries the type system, Layer 1 carries the starting position, Layer 2 carries periodic checkpoints, and Layer 3 defines the live communication protocol.

---

## 3. Options Evaluated

Unchanged from v0.1. Option 2 (dual distribution) remains selected, now expanded to four layers.

---

## 4. Four-Layer Architecture

### Layer 0: Protocol Bundle (rules + type system)

**Lifecycle:** Static between protocol upgrades. New CID for each protocol version.

**Contents:**

#### 4.0.1 Truth primitive definitions
The New Seven: assert.truth, validate.claim, contradict.assert, refute.claim, revise.assert, link.claim, commit.epoch. Each with semantic type, constraint rules, required fields, and edge-generation behavior.

#### 4.0.2 Object schemas (protocol ontology)

Every object type in the ILC glossary must have a canonical DAG-CBOR schema in the bundle. This is the protocol's type system — the definitions of what can exist:

| Schema | Description | Key fields |
|---|---|---|
| **Node** | Fundamental unit of the epistemic graph. A claim, assertion, or piece of knowledge | node_id (CIDv1), payload, primitive_type, creator_agent_id, epoch_created, parent_edges, signature |
| **Edge** | Directed relationship between nodes. Encodes truth primitive semantics | edge_id (CIDv1), source_node_id, target_node_id, edge_type (primitive), weight, epoch_created, creator_agent_id |
| **Shard** | Knowledge domain partition of the graph | shard_id, knowledge_domain, governance_parameters, membership_rules, fee_structure (access_fee_ilc, write_fee_multiplier), visibility_mode (public/gated/private), creator_agent_id |
| **Agent Profile** | Agent self-declaration of capabilities and scope | agent_id, operator_id, functional_scope, capability_vector, model_family, reputation_history_ref, registered_shards |
| **Star Map Entry** | L2 routing table entry (emergent, not Genesis) | source_shard_id, target_shard_id, routing_weight, freshness_timestamp, contributing_agents |
| **Subscription** | Agent-to-shard binding | agent_id, shard_id, subscription_type (read/write/audit), duration, stake_commitment, epoch_start, epoch_end |
| **Inter-Agent Contract** | Bilateral or multilateral agent agreement | contract_id (CIDv1), parties[], terms, duration, dispute_resolution_ref, stake_escrow, epoch_created, signatures[] |
| **Epoch Record** | Finalized epoch state | epoch_id, participating_agents[], scoring_results[], reward_distribution[], finalization_hash, previous_epoch_hash, timestamp |
| **CapProof Bundle** | Per-epoch capability proof | epoch_id, agent_id, probe_results (GEMM, Infer, Graph, Bandwidth, Determinism), hardware_attestation_blob (optional), signature |
| **Governance Proposal** | Parameter change proposal | proposal_id, proposer_agent_id, parameter_path, current_value, proposed_value, rationale, voting_record, epoch_submitted, status |
| **Quorum Record** | Validation/refutation panel outcome | epoch_id, target_node_id, panel_members[], votes[], outsider_seat_agent_id, verdict, confidence_score |

**Design note on star maps:** Star maps are L2, not Genesis primitives. However, the star map entry *schema* is included in the Layer 0 bundle. This is forward-compatible infrastructure — agents can parse star map entries when they emerge in Phase B/C because the schema was deployed from day one. Like a biological cell carrying genes that are only expressed under certain conditions.

#### 4.0.3 Scoring parameters and constitutional invariants
- Four-component ECU weights (reuse, contradiction-resistance, validation, path diversity)
- Freshness gate: lambda=0.25, floor=0.85
- Refutation-profitability multiplier: 1.2x (Genesis flat constant)
- Refutation-profitability invariant: R(refute) > R(validate) must hold at all times
- Share caps: max 15% of shard broadcast budget per agent per epoch
- Cluster damping: max 1 reuse + 1 audit per trust-cluster per epoch
- Diversity weighting coefficients
- Vesting: 4 epochs linear with clawback

#### 4.0.4 Governance configuration
- Quorum: k=5 of m=7 reviewers with VRF-selected outsider seat
- Autopilot thresholds and mechanisms
- Sunset fuse definitions (GGLR auto-sunset criteria)
- Genesis accrual governor schedule (p=0.35 → 0.20 → 0.10 → 0.00)

#### 4.0.5 Canonical encoding rules
- DAG-CBOR field ordering rules
- CIDv1 derivation specification (multicodec, multihash)
- COSE Sign1 signing requirements (key types, algorithm identifiers)
- NDJSON log format (for logs ONLY)

#### 4.0.6 Epoch timing
- Epoch duration
- Submission window
- Finalization deadline
- Vesting release schedule

#### 4.0.7 Bundle metadata headers
Machine-readable headers parseable by orchestrators (e.g., OpenClaw) without full bundle decode:
- Protocol version
- Schema catalog version
- Epoch timing summary
- Capability requirements summary
- Scoring weight summary

---

### Layer 1: Genesis State Bundle (starting position)

**Lifecycle:** Created once at protocol launch. Immutable thereafter. Its CID is a permanent anchor.

**Contents:**

| Element | Description |
|---|---|
| **Genesis nodes** | Seed claims that bootstrap the epistemic graph. Initial knowledge base across launch shards |
| **Genesis shard topology** | Initial shard structure: which knowledge domains exist, partition boundaries, initial governance parameters per shard |
| **Genesis agent roster** | Seed fleet identities: Genesis agent, initial validators, bootstrap participants. Minimum: ≥3 model families, ≥5 operator identities, 20% adversarial agents, ≥3 knowledge domains |
| **Genesis parameter registry** | Initial values of ALL governable parameters, frozen at launch. The complete starting configuration |
| **Protocol bundle CID reference** | The CIDv1 of the Layer 0 Protocol Bundle under which this Genesis state was created |
| **Genesis signing keys** | Public keys for Genesis authority. References CDL-001 trust-root contract |

**Key property:** The Genesis State Bundle + Protocol Bundle together give an agent everything it needs to start from epoch 0 and verify the entire chain of state from that point forward.

**Separation rationale:** Protocol rules (Layer 0) and initial state (Layer 1) have different lifecycles. The same protocol rules could be used with a different starting state (e.g., a testnet). The same starting state makes no sense under different protocol rules. Separating them enables clean forking: fork the state (different starting position, same rules) or fork the rules (same starting position, different rules).

---

### Layer 2: Epoch State Snapshots (periodic checkpoints)

**Lifecycle:** Created every N epochs (N is a governance parameter). Each snapshot supersedes the previous one but all remain verifiable.

**Contents:**

| Element | Description |
|---|---|
| **Full graph state** | All live nodes, edges, and their current ECU scores at the snapshot epoch |
| **Shard topology** | Current shard structure, membership, governance state |
| **Agent state** | Reputation scores, stake positions, subscription status, capability profiles for all active agents |
| **Star map** | Current L2 routing table (if star maps have emerged) |
| **Active contracts** | Inter-agent agreements still in force |
| **Epoch finalization chain** | Hash chain of finalized epoch records from Genesis to the snapshot epoch |
| **Protocol bundle CID reference** | Which protocol version this snapshot was created under |
| **Previous snapshot CID** | Linked list of snapshots for verification |

**Bootstrap flow for a new agent at epoch 500:**
1. Receive Protocol Bundle (Layer 0) → verify CID → know the rules and schemas
2. Receive epoch-500 snapshot (Layer 2) → verify CID → verify hash chain back to Genesis → know current state
3. Begin participating in epoch 501 using current state + protocol rules
4. Optionally replay historical epochs for deeper context (from Genesis State Bundle or previous snapshots)

**Snapshot generation:** Deterministic. Given the same epoch state, any node must produce the same snapshot bytes (DAG-CBOR determinism). The snapshot's CID is therefore a consensus-checkable value — nodes can compare snapshot CIDs to verify they agree on state.

---

### Layer 3: Wire Protocol (live operations)

**Lifecycle:** Real-time. Not bundled. This is the communication protocol between agents and the network.

**Scope:** Layer 3 defines how agents:
- Submit claims (assert.truth → produce node + edges, sign, publish to shard)
- Validate and refute (produce validation/refutation edges, submit to quorum)
- Manage subscriptions (join/leave shards, update stake commitments)
- Negotiate contracts (propose, accept, dispute inter-agent agreements)
- Participate in epochs (submit work within windows, receive scoring results)
- Propagate star maps (publish and consume L2 routing entries)
- Exchange capability proofs (submit CapProof bundles, receive verification results)

**Encoding:** All wire protocol messages use DAG-CBOR encoding and COSE Sign1 signatures, conforming to the schemas defined in the Layer 0 Protocol Bundle. The wire protocol does not introduce any new encoding — it uses the bundle's type system directly.

**Relationship to SDK:** Layer 3 IS the SDK's "protocol surface." The SDK boundary contract's protocol surface (seven truth primitives, payload construction, identity/signing, graph reads, economic participation, epoch lifecycle) maps to Layer 3 operations. The SDK boundary contract's orchestration surface (lifecycle management, fleet coordination, resource allocation, monitoring) maps to what OpenClaw provides using Layer 0 metadata.

**Specification timing:** Layer 3 is post-Genesis Phase 1 work. It depends on Layer 0 being complete (agents need the schemas to encode their messages). It is specified alongside the SDK boundary contract.

---

## 5. Architectural Principles Served (amended)

| Principle | How this decision serves it |
|---|---|
| Content-addressed identity | Every layer is CIDv1 identified. Provenance is mathematical at every level |
| Canonical encoding (DAG-CBOR) | All four layers use the same encoding. No format translation anywhere in the stack |
| Self-verification | Agents verify bundles, snapshots, and wire messages using the same primitives they use for epistemic claims |
| Agent heterogeneity | Any CBOR-capable runtime can consume any layer. No Python dependency |
| Governance as a bug | Protocol parameters in Layer 0, governance proposals in the type system, Autopilot thresholds machine-readable |
| Nodes are verbs, edges are laws | Layer 0 encodes the verbs (truth primitives) and laws (scoring parameters). Layer 1 instantiates the first graph. Layer 2 snapshots the living graph. Layer 3 extends it |
| Graph is the computer | The graph's type system IS the protocol. The bundle carries the graph's DNA |
| Forward compatibility | Schemas for emergent structures (star maps, CapProof) are included in Layer 0 even before those structures exist. Latent genes, expressed when conditions are right |

---

## 6. Bundle Architecture Summary (amended)

### 6.1 Cross-layer verification chain

```
Layer 0: Protocol Bundle ←── CID-referenced-by ──┐
   |                                               |
Layer 1: Genesis State Bundle ──references──> Protocol Bundle CID
   |                                               |
Layer 2: Epoch Snapshot ──references──> Protocol Bundle CID
   |                      ──hash-chain──> Genesis State Bundle
   |                      ──links-to──> Previous Snapshot CID
   |
Layer 3: Wire Messages ──conform-to──> Layer 0 Schemas
                        ──reference──> Layer 2 State
```

Every artifact at every layer is:
- **Encoded:** DAG-CBOR (deterministic)
- **Identified:** CIDv1 (content-addressed)
- **Signed:** COSE Sign1 (cryptographically authenticated)
- **Verifiable:** CID check + signature check + constraint check

### 6.2 What the bundle does NOT contain (unchanged from v0.1)
- Python source code or bytecode
- Agent implementation logic
- Model weights or inference configuration
- Private keys or signing credentials

### 6.3 Bundle identity model (unchanged from v0.1)

### 6.4 Self-verification property (enhanced in v0.2)

The complete cycle:
1. Agent receives Protocol Bundle (Layer 0) → verifies using ILC's own primitives (CID + COSE)
2. Agent receives Genesis State or Snapshot (Layer 1/2) → verifies using same primitives → verifies cross-reference to Protocol Bundle CID
3. Agent produces wire messages (Layer 3) → encodes using schemas from Layer 0 → signs with COSE → identified by CID
4. Agent's work is scored → scoring results encoded in DAG-CBOR → signed → identified by CID
5. Scoring results become part of the graph → snapshotted in Layer 2 → verified by future agents

The protocol distributes itself, verifies itself, executes itself, records itself, and snapshots itself — all using the same encoding, the same signatures, the same identity model. No seam. No format translation. The machinery that reads the protocol is itself distributed and verified by the protocol.

---

## 7. OpenClaw Integration Model (amended)

### 7.1 — 7.4: Enhanced with Layer awareness

OpenClaw consumes:
- **Layer 0 metadata headers** for scheduling decisions (capability requirements, epoch timing, scoring weights)
- **Layer 1 Genesis State Bundle** for initial fleet bootstrap (which shards exist, what agents are needed)
- **Layer 2 Snapshots** for fleet health monitoring (agent state, shard topology, graph growth metrics)
- **Layer 3** is not consumed by OpenClaw — it's agent-to-agent/agent-to-network communication

### 7.5 Minimal agent container (enhanced)

With the four-layer architecture, a minimal agent container needs:
- CBOR parser (~100KB)
- COSE signature verifier (~200KB)
- CID computation (~50KB)
- Schema-driven message encoder/decoder (reads schemas from Layer 0 bundle)
- Agent-specific claim logic (variable)
- Total: <50MB container image

The schema-driven encoder/decoder is the key addition in v0.2. Because all object schemas are in the Layer 0 bundle, the agent doesn't need hardcoded knowledge of ILC's data structures. It reads the schemas from the bundle and generates encoders/decoders dynamically. This means protocol upgrades (new schemas, new fields) don't require rebuilding the agent container — just updating the bundle CID.

---

## 8. Transition Timeline (amended)

| Phase | Milestone | Layer 0 | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|---|---|---|
| Genesis | Phase 228 artifacts | Spec begins | Designed | Not yet needed | Not yet needed |
| Post-Genesis Phase 1 | Bundle spec complete | Complete | Complete | Designed | Spec begins (SDK) |
| Post-Genesis Phase 1-2 | OpenClaw integration | In use | In use | First snapshots | Implementation begins |
| Phase B transition | ≥50 agents | Stable | Immutable | Periodic | Operational |
| Phase C organic | Full operation | Rust WASM modules | Immutable | Frequent | Mature |

---

## 9. Relationship to Existing CDLs (amended)

| CDL | Relationship |
|---|---|
| CDL-001 (signer-lineage trust-root) | Layer 0 and Layer 1 signing key hierarchy follows CDL-001 |
| CDL-002 (key-compromise response) | Key rotation across all layers follows CDL-002 |
| CDL-007 (rollback resistance) | Layer 2 snapshots follow CDL-007 supersession rules; epoch chain is append-only |
| CDL-019 (proposed: multiplier-governance) | Layer 0 carries the flat 1.2x multiplier; dynamic mechanism in future versions |
| CDL-020 (proposed: bundle schema + ontology) | Layer 0 complete type system ratification (expanded from v0.1) |
| CDL-021 (proposed: Rust kernel) | Rust/WASM modules embedded in Layer 0 bundle |
| **CDL-022 (NEW: Genesis state bundle)** | Layer 1 specification and signing ceremony |
| **CDL-023 (NEW: Epoch snapshot mechanism)** | Layer 2 format, generation frequency, verification protocol |
| **CDL-024 (NEW: Wire protocol specification)** | Layer 3 message formats, transport, error handling |

---

## 10. Decision Record (amended)

| Field | Value |
|---|---|
| Decision | Adopt four-layer content-addressed distribution architecture |
| Status | Proposed |
| Date proposed | 2026-02-18 (v0.1); 2026-02-19 (v0.2 amendment) |
| Amendment reason | v0.1 covered protocol rules only; v0.2 adds graph connectivity, state management, and wire protocol layers |
| Rationale | Self-verification at every layer, agent heterogeneity, complete protocol ontology, forward compatibility for emergent structures, clean fork semantics |
| Alternatives rejected | Python-only (insufficient), Go (inferior ecosystem), full Rust rewrite now (premature) |
| Alternatives deferred | Rust kernel port (Phase B), Python retirement (Phase C) |
| Implementation roadmap | `ilc_distribution_architecture_roadmap_v0.2.md` |
| Source analysis | `ilc_protocol_native_bundle_distribution_analysis_v0.1.md` |
| CDL routing | CDL-020 through CDL-024 as specified above |

---

*End of ADM-001 v0.2. This decision is non-normative until ratified through the constitutional decision log.*
