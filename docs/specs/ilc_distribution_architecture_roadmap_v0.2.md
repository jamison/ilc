# ILC Distribution Architecture Roadmap v0.2

Status: **non-normative planning artifact** — subject to decision-log ratification  
Date: 2026-02-19  
Author: Claude Opus 4.6 (Strategic Architectural Reviewer)  
Supersedes: `ilc_distribution_architecture_roadmap_v0.1.md`  
Depends on: ADM-001 v0.2 (Four-Layer Protocol-Native Bundle Distribution Architecture)  
Amendment reason: v0.1 covered Layer 0 (protocol rules) only. v0.2 adds task groups for Layer 1 (Genesis state bundle), Layer 2 (epoch snapshots), Layer 3 (wire protocol), and the full object schema catalog.

---

## 1. Strategic Summary

ILC adopts a four-layer content-addressed distribution architecture. Layer 0 carries the protocol's complete type system and rules. Layer 1 carries the Genesis starting state. Layer 2 provides periodic graph state snapshots. Layer 3 defines the live wire protocol for agent communication. All layers use DAG-CBOR + COSE Sign1 + CIDv1.

---

## 2. Distribution Architecture Phases

### Phase D1: Genesis Tactical Reproducibility (Target: Phase 230 scope)

Unchanged from v0.1.

| Task ID | Task | Deliverable | Acceptance criteria |
|---------|------|-------------|-------------------|
| D1-01 | Pin `SOURCE_DATE_EPOCH=0` in build pipeline | Updated build config | Two consecutive builds produce identical SHA-256 |
| D1-02 | Evaluate deterministic build backend | Decision note | Backend selected, rationale documented |
| D1-03 | Add deterministic rebuild gate to CI | `tools/check_reproducible_build.sh` | Builds twice, compares checksums, emits PASS/FAIL |
| D1-04 | Update provenance contract | Provenance artifact amendment | States reproducibility scope explicitly |

**Exit criteria:** Python builds reproducible on same platform. Provenance honest about scope.

---

### Phase D2: Protocol Bundle — Complete Type System (Target: post-Genesis Phase 1)

**Expanded from v0.1.** The bundle now includes the full protocol ontology — every object schema in the glossary — not just parameters.

| Task ID | Task | Deliverable | Acceptance criteria |
|---------|------|-------------|-------------------|
| **D2-01** | **Define Node schema** | Section in bundle schema spec | DAG-CBOR schema for nodes: CIDv1 node_id, payload, primitive_type, creator_agent_id, epoch_created, parent_edges, signature. Canonical field ordering. Round-trip test: encode → decode → re-encode = identical bytes |
| **D2-02** | **Define Edge schema** | Section in bundle schema spec | DAG-CBOR schema for edges: edge_id, source/target node_ids, edge_type, weight, epoch_created, creator_agent_id |
| **D2-03** | **Define Shard schema** | Section in bundle schema spec | DAG-CBOR schema for shards: shard_id, knowledge_domain, governance_parameters, membership_rules, fee_structure, visibility_mode, creator_agent_id |
| **D2-04** | **Define Agent Profile schema** | Section in bundle schema spec | DAG-CBOR schema: agent_id, operator_id, functional_scope, capability_vector, model_family, reputation_history_ref, registered_shards |
| **D2-05** | **Define Star Map Entry schema** | Section in bundle schema spec | DAG-CBOR schema: source_shard_id, target_shard_id, routing_weight, freshness_timestamp, contributing_agents. Forward-compatible (included in Genesis bundle, expressed when star maps emerge) |
| **D2-06** | **Define Subscription schema** | Section in bundle schema spec | DAG-CBOR schema: agent_id, shard_id, subscription_type, duration, stake_commitment, epoch_start/end |
| **D2-07** | **Define Inter-Agent Contract schema** | Section in bundle schema spec | DAG-CBOR schema: contract_id (CIDv1), parties[], terms, duration, dispute_resolution_ref, stake_escrow, epoch_created, signatures[] |
| **D2-08** | **Define Epoch Record schema** | Section in bundle schema spec | DAG-CBOR schema: epoch_id, participating_agents[], scoring_results[], reward_distribution[], finalization_hash, previous_epoch_hash, timestamp |
| **D2-09** | **Define CapProof Bundle schema** | Section in bundle schema spec | DAG-CBOR schema: epoch_id, agent_id, probe_results (5 probes), hardware_attestation_blob (optional), signature |
| **D2-10** | **Define Governance Proposal schema** | Section in bundle schema spec | DAG-CBOR schema: proposal_id, proposer, parameter_path, current/proposed values, rationale, voting_record, status |
| **D2-11** | **Define Quorum Record schema** | Section in bundle schema spec | DAG-CBOR schema: epoch_id, target_node_id, panel_members[], votes[], outsider_seat_agent_id, verdict, confidence_score |
| **D2-12** | **Define scoring parameters block** | Section in bundle schema spec | Four-component ECU weights, freshness gate, refutation-profitability multiplier, share caps, cluster damping, diversity weighting, vesting parameters |
| **D2-13** | **Define governance configuration block** | Section in bundle schema spec | Quorum rules, Autopilot thresholds, sunset fuses, Genesis accrual governor schedule |
| **D2-14** | **Define canonical encoding rules block** | Section in bundle schema spec | DAG-CBOR field ordering, CIDv1 derivation, COSE Sign1 requirements, NDJSON log format |
| **D2-15** | **Define bundle metadata headers** | Section in bundle schema spec | Protocol version, schema catalog version, epoch timing summary, capability requirements summary, scoring weight summary. Parseable by orchestrators without full decode |
| **D2-16** | **Define bundle signing contract** | `ilc_protocol_bundle_signing_contract_v0.1.md` | COSE Sign1 signing requirements, key hierarchy, CIDv1 derivation from canonical bytes |
| **D2-17** | **Define bundle verification contract** | `ilc_protocol_bundle_verification_v0.1.md` | CID check, COSE verification, parameter constraint validation, constitutional invariant checks |
| **D2-18** | **Define bundle versioning scheme** | Section in bundle schema spec | Version field, compatibility rules, breaking vs non-breaking change classification, upgrade path |
| **D2-19** | **Build reference bundle generator** | `tools/generate_protocol_bundle.py` | Reads protocol config from repo, serializes full type system + parameters to DAG-CBOR, signs, produces CIDv1-identified bundle |
| **D2-20** | **Build reference bundle verifier** | `tools/verify_protocol_bundle.py` | Verifies CID, signature, constitutional constraints. Emits detailed report |
| **D2-21** | **Add bundle generation to release pipeline** | Integration with release process | Release produces: wheel, sdist, protocol bundle. All with provenance |
| **D2-22** | **Write bundle consumer guide** | `docs/guides/consuming_protocol_bundle.md` | Language-agnostic guide with examples in Python, Rust, JavaScript |
| **D2-23** | **Cross-implementation schema test vectors** | `tests/bundle_schema_test_vectors/` | For each schema: golden DAG-CBOR bytes + expected CIDv1. Any implementation can verify conformance |

**Exit criteria:** Complete protocol ontology encoded in DAG-CBOR. Bundle can be generated, verified, and consumed by a non-Python program. Test vectors pass across implementations.

**CDL routing:** CDL-020 "Protocol-native bundle schema and type system."

---

### Phase D2b: Genesis State Bundle (Target: post-Genesis Phase 1)

**NEW in v0.2.** This is the Layer 1 specification.

| Task ID | Task | Deliverable | Acceptance criteria |
|---------|------|-------------|-------------------|
| D2b-01 | Define Genesis state bundle format | `ilc_genesis_state_bundle_schema_v0.1.md` | DAG-CBOR schema for: genesis nodes, shard topology, agent roster, parameter registry, protocol bundle CID reference, signing keys |
| D2b-02 | Define Genesis node seed set | Genesis node content specification | Minimum viable seed claims across ≥3 knowledge domains. Content, structure, and scoring targets for each |
| D2b-03 | Define Genesis shard topology | Initial shard specification | Which shards exist at launch, boundaries, governance parameters, membership rules |
| D2b-04 | Define Genesis agent roster requirements | Seed fleet specification | ≥3 model families, ≥5 operator identities, 20% adversarial, ≥3 knowledge domains. Identity provisioning workflow |
| D2b-05 | Define Genesis parameter registry snapshot | Complete parameter listing | ALL governable parameters with initial values. Cross-referenced to scoring kernel, governance config, and epoch rules |
| D2b-06 | Build Genesis state bundle generator | `tools/generate_genesis_state_bundle.py` | Reads seed data, serializes to DAG-CBOR, signs with Genesis authority key, produces CIDv1-identified bundle. Includes protocol bundle CID reference |
| D2b-07 | Build Genesis state bundle verifier | `tools/verify_genesis_state_bundle.py` | Verifies CID, signature, cross-reference to protocol bundle CID, parameter completeness, seed fleet requirements |
| D2b-08 | Define fork semantics | Section in Genesis state spec | How forking works: same rules + different state (state fork), same state + different rules (protocol fork), different both (full fork). CID references make this explicit |

**Exit criteria:** Genesis state bundle can be generated, verified, and consumed. Fork semantics are explicit and testable.

**CDL routing:** CDL-022 "Genesis state bundle specification and signing ceremony."

---

### Phase D3: OpenClaw Integration Surface (Target: post-Genesis Phase 1-2)

Enhanced from v0.1 with Layer awareness.

| Task ID | Task | Deliverable | Acceptance criteria |
|---------|------|-------------|-------------------|
| D3-01 | Define OpenClaw bundle ingestion contract | Integration spec | How OpenClaw fetches, pins, distributes Layer 0 and Layer 1 bundles. CID-based version pinning |
| D3-02 | Define protocol-aware scheduling interface | Section in integration spec | Layer 0 metadata headers → scheduling decisions. Capability requirements → node selection, epoch timing → windows, scoring weights → specialization routing |
| D3-03 | Define minimal agent container contract | Container spec | What container MUST contain (CBOR parser, COSE verifier, schema-driven encoder/decoder, bundle consumer logic). What it MUST NOT require (Python, pip, ilc_core) |
| D3-04 | Build reference minimal container | `containers/ilc-agent-minimal/Dockerfile` | Fetches protocol bundle by CID, verifies, extracts schemas, logs "ready." No Python |
| D3-05 | Define bundle-based protocol upgrade flow | Section in integration spec | New bundle CID propagation, staged rollout, verification at each node, rollback on failure |
| D3-06 | Prototype protocol-aware scheduling | Proof-of-concept | OpenClaw reads metadata headers, makes at least one scheduling decision |
| **D3-07** | **Define snapshot-based fleet health monitoring** | Section in integration spec | OpenClaw reads Layer 2 snapshots for agent state, shard topology, graph growth. Triggers scaling, alerts, rebalancing |
| **D3-08** | **Define Genesis state bootstrap flow** | Section in integration spec | How OpenClaw uses Layer 1 to bootstrap initial agent fleet. Shard assignment, agent role allocation, initial subscription setup |

**Exit criteria:** OpenClaw-managed fleet can receive, verify, and consume all layers. Protocol-aware scheduling operational.

---

### Phase D2c: Epoch State Snapshot Mechanism (Target: post-Genesis Phase 2)

**NEW in v0.2.** This is the Layer 2 specification.

| Task ID | Task | Deliverable | Acceptance criteria |
|---------|------|-------------|-------------------|
| D2c-01 | Define snapshot format | `ilc_epoch_snapshot_schema_v0.1.md` | DAG-CBOR schema for: full graph state, shard topology, agent state, star map, active contracts, epoch chain, protocol bundle CID ref, previous snapshot CID |
| D2c-02 | Define snapshot generation protocol | Section in snapshot spec | Deterministic generation: same epoch state → same bytes → same CID. Consensus-checkable |
| D2c-03 | Define snapshot verification protocol | Section in snapshot spec | CID check, signature check, hash chain verification back to Genesis, protocol bundle CID cross-reference |
| D2c-04 | Define snapshot frequency governance | Section in snapshot spec | Default interval (every N epochs), governance-adjustable, triggered vs periodic |
| D2c-05 | Define fast-bootstrap protocol | Section in snapshot spec | New agent receives snapshot + protocol bundle → verifies → begins participating. No full replay required |
| D2c-06 | Build reference snapshot generator | `tools/generate_epoch_snapshot.py` | Given epoch state, produces deterministic DAG-CBOR snapshot, signs, computes CID |
| D2c-07 | Build reference snapshot verifier | `tools/verify_epoch_snapshot.py` | Full verification: CID, signature, hash chain, cross-references, constraint checks |
| D2c-08 | Define snapshot pruning policy | Section in snapshot spec | How old snapshots are managed. Archival vs deletion. Minimum retention. Hash chain integrity preservation |

**Exit criteria:** Epoch snapshots are deterministic, verifiable, and support fast agent bootstrap without full replay.

**CDL routing:** CDL-023 "Epoch snapshot mechanism and fast-bootstrap protocol."

---

### Phase D2d: Wire Protocol Specification (Target: post-Genesis Phase 1-2)

**NEW in v0.2.** This is the Layer 3 specification. Aligns with SDK boundary contract.

| Task ID | Task | Deliverable | Acceptance criteria |
|---------|------|-------------|-------------------|
| D2d-01 | Define claim submission protocol | Wire protocol spec section | How agents encode and submit assert.truth nodes. Message format, transport, acknowledgment, error handling |
| D2d-02 | Define validation/refutation protocol | Wire protocol spec section | How agents produce and submit validation/refutation edges. Quorum formation, panel assignment, verdict reporting |
| D2d-03 | Define subscription management protocol | Wire protocol spec section | Join/leave shards, update stake, subscription lifecycle |
| D2d-04 | Define contract negotiation protocol | Wire protocol spec section | Propose, accept, dispute inter-agent contracts. Multi-party signing |
| D2d-05 | Define epoch participation protocol | Wire protocol spec section | Submit work within windows, receive scoring results, handle vesting |
| D2d-06 | Define star map propagation protocol | Wire protocol spec section | How L2 routing entries are published, consumed, and weighted. Forward-compatible with Phase B/C emergence |
| D2d-07 | Define CapProof submission protocol | Wire protocol spec section | How agents submit per-epoch capability proofs. Verification flow, challenge-response |
| D2d-08 | Define error handling and retry semantics | Wire protocol spec section | Message failure modes, retry policies, idempotency, deduplication |
| D2d-09 | Define transport requirements | Wire protocol spec section | Transport-agnostic message format. Reference bindings for common transports (HTTP, gRPC, libp2p). Content-type negotiation |

**Exit criteria:** Complete wire protocol specification. Reference binding for at least one transport. All messages conform to Layer 0 schemas.

**CDL routing:** CDL-024 "Wire protocol specification and transport bindings."

---

### Phase D4: Rust Kernel Port (Target: Phase B transition, milestone-triggered)

Unchanged from v0.1. Trigger criteria, tasks D4-01 through D4-09 all remain as specified.

---

### Phase D5: Python Retirement Planning (Target: Phase C, stability-triggered)

Unchanged from v0.1. Tasks D5-01 through D5-04 remain as specified.

---

## 3. Dependency Graph (amended)

```
D1 (Genesis reproducibility)
  |
  v
D2 (Protocol Bundle + full type system) ─────────────────┐
  |                                                        |
  +──> D2b (Genesis State Bundle)                          |
  |       |                                                |
  |       +──> D3 (OpenClaw integration)                   |
  |                                                        |
  +──> D2d (Wire Protocol) ←── depends on D2 schemas      |
  |                                                        |
  +──> D2c (Epoch Snapshots) ←── depends on D2 schemas     |
  |           and running network                          |
  v                                                        |
D4 (Rust kernel) ── triggered by Phase B milestones ───────┘
  |
  v
D5 (Python retirement) ── triggered by Phase C stability
```

**Critical path:** D1 → D2 → D2b (enables Genesis launch with protocol-native distribution)
**Parallel work:** D2d and D3 can proceed alongside D2b once D2 schemas are stable
**Deferred:** D2c requires a running network; D4 requires Phase B milestones

---

## 4. TODO.txt Routing (amended)

```
# Distribution Architecture Roadmap v0.2 (from ADM-001 v0.2)

## Immediate (Phase 230 scope)
- [ ] D1-01: Pin SOURCE_DATE_EPOCH=0 in build pipeline
- [ ] D1-02: Evaluate deterministic build backend
- [ ] D1-03: Add deterministic rebuild gate script
- [ ] D1-04: Update provenance contract with reproducibility scope statement

## Post-Genesis Phase 1 — Layer 0 Protocol Bundle (23 tasks)
- [ ] D2-01 through D2-23: Full protocol ontology schema catalog + tooling

## Post-Genesis Phase 1 — Layer 1 Genesis State Bundle (8 tasks)
- [ ] D2b-01 through D2b-08: Genesis state format, content, tooling, fork semantics

## Post-Genesis Phase 1-2 — Layer 3 Wire Protocol (9 tasks)
- [ ] D2d-01 through D2d-09: Complete wire protocol specification

## Post-Genesis Phase 1-2 — OpenClaw Integration (8 tasks)
- [ ] D3-01 through D3-08: OpenClaw integration with all layers

## Post-Genesis Phase 2 — Layer 2 Epoch Snapshots (8 tasks)
- [ ] D2c-01 through D2c-08: Snapshot mechanism and fast-bootstrap

## Phase B (milestone-triggered) — Rust Kernel (9 tasks)
- [ ] D4-01 through D4-09: Rust port + WASM + cross-validation

## Phase C (stability-triggered) — Python Retirement (4 tasks)
- [ ] D5-01 through D5-04: Retirement assessment and decision
```

**Total tasks:** 4 + 23 + 8 + 9 + 8 + 8 + 9 + 4 = **73 tasks**

---

## 5. CDL Routing Summary (amended)

| Proposed CDL | Subject | Layer | Trigger |
|---|---|---|---|
| CDL-019 | Multiplier-governance surface unification | 0 | Before Phase 230 scope lock |
| CDL-020 | Protocol-native bundle schema and complete type system | 0 | When D2 phase complete |
| CDL-021 | Rust kernel port and WASM distribution | 0 | When D4 trigger criteria met |
| CDL-022 | Genesis state bundle specification and signing ceremony | 1 | When D2b phase complete |
| CDL-023 | Epoch snapshot mechanism and fast-bootstrap protocol | 2 | When D2c phase complete |
| CDL-024 | Wire protocol specification and transport bindings | 3 | When D2d phase complete |

---

## 6. Risk Register (amended)

All v0.1 risks remain. Additional v0.2 risks:

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Schema catalog is too large for practical bundle size | Low | Medium | Compress schemas. Split into required (Genesis) and optional (post-Genesis) catalogs. Metadata headers always small |
| Epoch snapshots grow prohibitively large | Medium | High | Incremental snapshots (delta from previous). Pruning policy. Sharded snapshots |
| Wire protocol specification is premature before real agent workloads | Medium | Medium | Spec is minimal and extensible. Version field allows non-breaking additions. Real workload data informs v0.2 spec |
| Genesis state bundle signing ceremony logistics | Low | High | Ceremony protocol specified in advance. Multi-party signing. Rehearsal on testnet |
| Star map schema evolves significantly before Phase B | Medium | Low | Schema is forward-compatible by design. Version field. Non-breaking extensions |

---

## 7. Success Metrics (amended)

| Metric | D1 | D2 | D2b | D2c | D2d | D3 | D4 |
|---|---|---|---|---|---|---|---|
| Build reproducibility | 100% same-platform | N/A | N/A | N/A | N/A | N/A | 100% cross-platform |
| Bundle verification time | N/A | <1s | <1s | <5s | N/A | N/A | <100ms (WASM) |
| Schema count in bundle | N/A | ≥11 types | N/A | N/A | N/A | N/A | N/A |
| Min agent container size | N/A | N/A | N/A | N/A | N/A | <50MB | <20MB (WASM) |
| Bootstrap time (new agent) | N/A | N/A | N/A | <30s from snapshot | N/A | N/A | <10s |
| Wire protocol message types | N/A | N/A | N/A | N/A | ≥7 (one per primitive + subscriptions + contracts) | N/A | N/A |
| Cross-impl parity | N/A | Test vectors pass | N/A | N/A | N/A | N/A | 100% deterministic |

---

*End of roadmap v0.2. 73 tasks across 8 phases. All items non-normative until routed through CDL.*
