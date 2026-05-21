# Window 1459+: Post-Public-RC Architecture Forward Plan

**Version:** v0.1
**Drafted:** 2026-05-21 (based on Q3/Q4/Q5 resolutions from Window 1429-1458 §8)
**Status:** DRAFT — not an authorized sequence lock; requires human review and GO before any phase executes
**Context:** This forward plan covers the first post-public-RC window. It assumes Window 1429-1458 closes with `public_rc_activated_epoch_1_triggered`. Entry into this window is conditioned on that closure verdict.

---

## 1. Baseline Inherited from Window 1429-1458

At Window 1429-1458 close (anticipated), the following are in force:

| Item | Anticipated state |
|------|------------------|
| Public RC | Published — signed release artifact at public URL |
| `activation_certificate_v1` | Published — epoch 0-to-1 triggered |
| At least one external operator | Connected — identity ceremony complete |
| `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED` | False (Phase 1429) |
| CDL-094 TransportPrincipal | Ratified (Phase 1435) |
| OpenClaw harness-assisted P2P | Active (Phase 1437) |
| Werner diagnostic wiring | Active (Track H1, default-off pressure metrics) |
| Gap 13 (claimability) | Closed (Phase ~1441) |
| Gap 14 (package modularity) | Closed (Phases ~1436a-1436b) |
| ADR-0035 (homoiconic type system) | Deferred — direction accepted, CDL not yet opened |
| Native Rust P2P substrate | Deferred — OpenClaw harness-assisted P2P only |
| Werner flow-governor CDL | Deferred — diagnostic trace data accumulating |
| Gap 7 (counsel, CLA, trademark) | Partially closed — external items (patent, trademark) remain |

---

## 2. Window Objective

**Primary objective:** Deepen the architectural foundation of the live network — closing the three most consequential deferred architectural items (ADR-0035 type system, Rust P2P substrate, and Werner flow-governor CDL) and hardening the governance model (Genesis authority sunset spec, CDL falsification criterion, CDL-091 inviter-chaining candidate deliberation).

**What this window does NOT attempt:**
- Production minting or live ILC settlement (long-range post-public-RC only)
- CDL-031 dynamic ranking runtime (requires CDL-019 prerequisite chain first)
- Mainnet split-custody ceremony (multi-party coordination, future window)
- CDL-091 inviter-chaining CDL opening (requires SIM evidence and ADR-0009 bundle work first)

---

## 3. Entry Conditions

This window may not open until all of the following are confirmed:

| Condition | Evidence required |
|-----------|------------------|
| Public RC published | `public_repository_published` token committed |
| Epoch 1 triggered | `activation_certificate_published` + `epoch_1_transition_authorized` committed |
| At least one external operator connected | Documented in window 1429-1458 closure gate handoff |
| Window 1429-1458 closure gate PASS | `window_1429_1458_closed_phase_<N>` committed |
| Werner diagnostic trace data available | At least one epoch of pressure-diagnostic data from Track H1 |

---

## 4. Track Inventory

| Track | Phases (approx) | Gate conditions closed |
|-------|----------------|----------------------|
| A — ADR-0035 homoiconic type definition system | 1459–1461 | type_definition NodeType CDL + runtime |
| B — Native Rust P2P substrate completion | 1462–1466 | PersistentQuicSessionManager, CDL-078 Rust routing, peer discovery ADR, Python/Rust bridge, end-to-end tests |
| C — Werner flow-governor CDL | 1467–1469 | CDL-053 amendment / successor CDL (conditional on diagnostic data) |
| D — CDL falsification criterion field | ~1470 | Retroactive falsification_criterion annotation on all ratified CDLs |
| E — Genesis authority sunset spec | ~1471 | Standalone spec formalizing court/house/executive model; closes CDL-004 SUBSTANTIVE gap |
| F — ADR-0009 protocol-native bundle | 1472–1477 | Layer 0-3 bundle schemas, deterministic generator, independent verifier |
| Z — Window coherence + closure | 1478–1480 | Window closure gate |

---

## 5. Phase-Level Plan

### Track A — ADR-0035 Homoiconic Type Definition System (Phases 1459-1461)

**Context:** ADR-0035 was accepted as direction in Phase 1387d. Implementation was deferred pending a CDL to introduce `type="type_definition"` as a new NodeType. This is a graph-layer architectural feature complementing ADR-0030 content typing. Not a public RC blocker; assigned to the first post-public-RC window per Q4 resolution.

**Phase 1459 — ADR-0035 CDL opening (type_definition NodeType governance) (SENSITIVE)**

- Open CDL for `type="type_definition"` NodeType introduction.
- Scope: introduces the homoiconic type definition node; type regress stops at `type="type_definition"` (hardcoded); complements ADR-0030 content typing.
- CDL number: next available after CDL-094 (anticipated CDL-095; confirm at execution).
- Token: `adr_0035_cdl_opened_phase_1459`.
- Required GO token: `GO Phase 1459`.

**Phase 1460 — ADR-0035 CDL ratification (SENSITIVE)**

- Deliberate and ratify the ADR-0035 CDL.
- Two-commit pattern per CDL mutation protocol.
- Token: `adr_0035_cdl_ratified_phase_1460`.
- Required GO token: `GO Phase 1460`.

**Phase 1461 — ADR-0035 runtime implementation (NON-SENSITIVE)**

- Implement `type="type_definition"` NodeType in the graph store and validation layer.
- Migrate hardcoded type strings to graph-native type_definition nodes.
- Integrate with ADR-0030 content typing.
- Token: `adr_0035_type_definition_runtime_implemented_phase_1461`.

---

### Track B — Native Rust P2P Substrate Completion (Phases 1462-1466)

**Context:** The current Rust P2P baseline (from Phase 1387g audit):
- Already complete: QUIC transport (`ilc_consensus/src/network.rs`), endpoint projection (`persistent_quic.rs`), D2d gossip (Python `ilc_core/network/d2d/`)
- OpenClaw harness-assisted P2P is the live path as of Window 1429-1458 Phase 1437
- Still needed for full protocol-native P2P: PersistentQuicSessionManager, CDL-078 relay routing in Rust, peer discovery design, Python/Rust cross-stack integration, end-to-end tests

**Phase 1462 — PersistentQuicSessionManager implementation (NON-SENSITIVE)**

- Implement `PersistentQuicSessionManager` in `ilc_consensus/src/`:
  - Connection pool with session lifecycle management
  - Relay fallback path on connection failure
  - CDL-078 relay path integration (next-hop selection)
- Token: `persistent_quic_session_manager_implemented_phase_1462`.
- ICSS §8 enforced: TLS verification must not be disabled.
- ICSS §6 enforced: socket timeouts on all outbound connections.

**Phase 1463 — CDL-078 relay routing in Rust (NON-SENSITIVE)**

- Implement CDL-078 relay routing in Rust:
  - Next-hop selection algorithm per CDL-078 relay fee ratification
  - Relay forwarding path in `ilc_consensus/src/`
  - Integration with Phase 1462 `PersistentQuicSessionManager`
- Token: `cdl_078_relay_routing_rust_implemented_phase_1463`.

**Phase 1464 — Peer discovery ADR (NON-SENSITIVE)**

- Produce ADR for dynamic peer discovery beyond static endpoint projection:
  - Evaluate DHT-based, gossip-based, and introducer-based approaches
  - Define discovery bounds (privacy, Sybil resistance, CDL-V3 diversity constraints)
  - Define ADR-0025 resolution (dynamic peer discovery was deferred in prior windows)
  - Output: accepted ADR (not yet implemented)
- Token: `peer_discovery_adr_accepted_phase_1464`.

**Phase 1465 — Python/Rust cross-stack integration (NON-SENSITIVE)**

- Bridge D2d gossip layer (`ilc_core/network/d2d/`) to Rust QUIC validators:
  - Python-side serialization for Rust QUIC transport
  - Rust-side deserialization and forwarding to D2d gossip
  - subprocess bridge contracts (building on existing patterns from `ilc_consensus/`)
- Token: `python_rust_cross_stack_bridge_implemented_phase_1465`.

**Phase 1466 — End-to-end Rust P2P integration tests (NON-SENSITIVE)**

- Full end-to-end tests spanning Rust QUIC validators and Python agents:
  - Epoch cycling with Rust validator participation
  - D2d gossip propagation through Rust QUIC layer
  - CDL-078 relay path exercised
  - OpenClaw harness-assisted P2P remains the fallback (not removed)
- Token: `rust_p2p_integration_tests_complete_phase_1466`.

---

### Track C — Werner Flow-Governor CDL (Phases 1467-1469, conditional)

**Context:** CDL-053 was ratified with a narrow maintenance-equivalent productive-credit scope. The broader Werner flow-governor architecture (heat/pressure signals → expanded capacity → economic policy) was deferred from Phase 1263 pending SIM evidence. Track H1 in Window 1429-1458 wires default-off diagnostic metrics during rehearsal and early public RC epochs. This track opens only if diagnostic data meets the deliberation threshold.

**Entry gate for Track C:** Werner diagnostic trace data from at least 10 epochs of live public RC network operation. Human deliberation required before Phase 1467 authorized.

**Phase 1467 — Werner diagnostic data review and CDL deliberation (NON-SENSITIVE)**

- Review Werner overlay data (systolic/diastolic/pulse-pressure metrics) from Track H1 diagnostic wiring against Phase 1263 remaining open conditions:
  - Default SIM-FETCH evidence profile
  - Beta/noise decomposition
  - Spectral trust threshold discipline
  - TransportPrincipal/admission binding
  - Productive-credit authorization boundary
- Produce: CDL deliberation document proposing scope for CDL-053 amendment or successor CDL.
- Token: `werner_flow_governor_deliberation_complete_phase_1467`.
- If conditions not met: record explicit deferral. Do not open CDL. Assign to next review window.

**Phase 1468 — Werner flow-governor CDL opening (SENSITIVE, conditional on Phase 1467 verdict)**

- If Phase 1467 verdict = conditions met: open the CDL.
- Scope: Werner heat signal → topology pressure → admission priority (NOT direct ECU minting); must not widen CDL-053 narrow scope without explicit CDL amendment.
- Token: `werner_flow_governor_cdl_opened_phase_1468` (conditional).
- Required GO token: `GO Phase 1468`.
- If Phase 1467 verdict = deferred: skip. Record `werner_flow_governor_cdl_deferred_phase_1468`.

**Phase 1469 — Werner flow-governor CDL ratification (SENSITIVE, conditional)**

- If Phase 1468 proceeded: full prelock/ratification cycle.
- Token: `werner_flow_governor_cdl_ratified_phase_1469` (conditional).
- Required GO token: `GO Phase 1469`.

---

### Track D — CDL Falsification Criterion Field (~Phase 1470)

**Context:** The epistemological foundations canonical states every ratified CDL row should carry an explicit falsification criterion. No CDL row currently carries this field. Assigned to first post-public-RC window coherence in §10.3 of the forward plan.

**Phase ~1470 — CDL falsification criterion annotation (NON-SENSITIVE)**

- Define `falsification_criterion` field annotation schema for CDL rows.
- Apply retroactively to all currently-ratified CDLs in scope (CDL-001 through CDL-094+).
- The field is non-blocking — no CDL is reopened by adding it; purpose is to make reopening conditions explicit and auditable.
- Token: `cdl_falsification_criterion_field_applied_phase_1470`.

---

### Track E — Genesis Authority Sunset Spec (~Phase 1471)

**Context:** The three-branch governance model (court/house/executive) was fully designed in the Oct 11 2025 conversation (`Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:16094`) and cited at raw-012616/646/647/660. No standalone spec formalizing it exists. CDL-004 SUBSTANTIVE gap recorded against it. Assigned here per §10.1 of the forward plan.

**Phase ~1471 — Genesis authority sunset standalone spec (SENSITIVE)**

- Produce standalone spec formalizing the three-phase, three-branch governance model:
  - Phase A (Boot): Executive proposer, Court certifier, House advisory
  - Phase B (Transition): Executive suspensive veto, Court certifier, House binding vote
  - Phase C (Mature): Executive soft-power only, Court certifier, House full authority
- Spec must cite the Oct 11 2025 design conversation and raw-012616/646/647/660 as authoritative sources.
- Observable Phase B and Phase C transition triggers (participation threshold, Genesis ECU share threshold) — exact numbers require SIM evidence; record as forward-deliberation items if not yet settled.
- Close CDL-004 SUBSTANTIVE gap by adding a forward pointer from CDL-004 to the spec.
- Address `TODO-P585-02` (Genesis governance dilution closure).
- Token: `genesis_authority_sunset_spec_committed_phase_1471`.
- Required GO token: `GO Phase 1471` (SENSITIVE: constitutional surface).

---

### Track F — ADR-0009 Protocol-Native Bundle (Phases 1472-1477)

**Context:** ADR-0009 defines four bootstrap layers. Currently no implemented bundle generator or verifier exists. This track is a prerequisite for CDL-091 inviter-chaining incentive extension (§10.4 of the forward plan). Must close before any bootstrap-serving incentive CDL can be opened.

**Phase 1472 — Layer 0 protocol bundle schema definition (NON-SENSITIVE)**

- Define Layer 0 schema: protocol object schemas, governance constants, scoring constants, version/predecessor semantics, canonical encoding rules.
- Integration point: ADR-0035 `type_definition` nodes (Track A) — either required or explicitly scoped out with a transitional hardcoded type table noted.
- Token: `layer_0_protocol_bundle_schema_defined_phase_1472`.

**Phase 1473 — Deterministic bundle generator (NON-SENSITIVE)**

- Implement deterministic bundle generator:
  - Emits content-addressed signed protocol bundles from Layer 0 schema
  - Reproducible across implementations: same schema → same content hash
- Token: `deterministic_bundle_generator_implemented_phase_1473`.

**Phase 1474 — Independent bundle verifier (NON-SENSITIVE)**

- Implement independent verifier:
  - Verifies bundle CID, signature, schema completeness, version lineage, canonical encoding
  - Must work without trusting the source (verify hash chain back to Genesis root)
- Token: `independent_bundle_verifier_implemented_phase_1474`.

**Phase 1475 — Layer 1 Genesis state bundle schema (NON-SENSITIVE)**

- Define Layer 1 Genesis state bundle schema:
  - Explicit reference to verified Layer 0 bundle CID
  - Genesis graph snapshot format
- Token: `layer_1_genesis_state_bundle_schema_defined_phase_1475`.

**Phase 1476 — Layer 2 epoch snapshot schema (NON-SENSITIVE)**

- Define Layer 2 epoch snapshot schema:
  - Epoch state snapshots with explicit references to Layer 1 Genesis bundle CID
  - Serving peer verification receipts
- Token: `layer_2_epoch_snapshot_schema_defined_phase_1476`.

**Phase 1477 — Layer 3 D2D wire-message binding (NON-SENSITIVE)**

- Bind Layer 3 D2D bootstrap messages to content-addressed bundle/snapshot fetch and verification:
  - Serving peers credited for delivering verifiable artifacts, not opaque files
  - Self-verifying bootstrap service receipt format
- Token: `layer_3_d2d_bundle_binding_implemented_phase_1477`.

---

### Track Z — Window Coherence + Closure

**Phase ~1478 — Window coherence, capsule update, ADR housekeeping (NON-SENSITIVE)**

- Update context capsule.
- Review open ADR obligations: ADR-0008 (node usefulness), ADR-0019 (graph-native governance), ADR-0024 (agent skills Tier 3), ADR-0025 (dynamic peer discovery — if Phase 1464 closed this, record closure), ADR-0028 (settlement substrate graduation), ADR-0029 (hypergraph spectral hash epoch commitment).
- Record CDL-091 inviter-chaining candidate deliberation status (CDL opening requires SIM evidence; record gate conditions still outstanding if applicable).
- Token: `window_1459_plus_coherence_complete`.

**Phase ~1479 — Window closure gate (SENSITIVE)**

- Closure verdict against window objective.
- Required GO token: `GO Phase 1479`.
- Token: `window_1459_plus_closed`.

---

## 6. Candidate Phase Table

| Order | Phase (approx) | Topic | Character | Sensitivity |
|-------|----------------|-------|-----------|-------------|
| A1 | 1459 | ADR-0035 CDL opening — type_definition NodeType | Constitutional | **SENSITIVE** |
| A2 | 1460 | ADR-0035 CDL ratification | Constitutional | **SENSITIVE** |
| A3 | 1461 | ADR-0035 runtime — migrate hardcoded type strings to type_definition nodes | Runtime | NON-SENSITIVE |
| B1 | 1462 | PersistentQuicSessionManager — connection pool, session lifecycle, relay fallback | Runtime (Rust) | NON-SENSITIVE |
| B2 | 1463 | CDL-078 relay routing in Rust — next-hop selection, relay forwarding | Runtime (Rust) | NON-SENSITIVE |
| B3 | 1464 | Peer discovery ADR — dynamic discovery beyond static endpoint projection | Spec/ADR | NON-SENSITIVE |
| B4 | 1465 | Python/Rust cross-stack bridge — D2d gossip to Rust QUIC validators | Runtime | NON-SENSITIVE |
| B5 | 1466 | End-to-end Rust P2P integration tests | Testing | NON-SENSITIVE |
| C1 | 1467 | Werner diagnostic data review + flow-governor CDL deliberation | Research | NON-SENSITIVE |
| C2 | 1468 | Werner flow-governor CDL opening (conditional) | Constitutional | **conditional SENSITIVE** |
| C3 | 1469 | Werner flow-governor CDL ratification (conditional) | Constitutional | **conditional SENSITIVE** |
| D1 | ~1470 | CDL falsification criterion field — retroactive annotation on all ratified CDLs | Coherence | NON-SENSITIVE |
| E1 | ~1471 | Genesis authority sunset spec — court/house/executive three-branch model | Constitutional | **SENSITIVE** |
| F1 | ~1472 | ADR-0009 Layer 0 protocol bundle schema | Spec | NON-SENSITIVE |
| F2 | ~1473 | Deterministic bundle generator | Runtime | NON-SENSITIVE |
| F3 | ~1474 | Independent bundle verifier | Runtime | NON-SENSITIVE |
| F4 | ~1475 | Layer 1 Genesis state bundle schema | Spec | NON-SENSITIVE |
| F5 | ~1476 | Layer 2 epoch snapshot schema | Spec | NON-SENSITIVE |
| F6 | ~1477 | Layer 3 D2D wire-message binding | Runtime | NON-SENSITIVE |
| Z1 | ~1478 | Window coherence + capsule + ADR housekeeping | Synthesis | NON-SENSITIVE |
| Z2 | ~1479 | Window closure gate | Gate | **SENSITIVE** |

Total: ~21 planned phases plus contingency slots. Exact phase number assignments depend on Window 1429-1458 closing phase number.

---

## 7. Dependency Tree

```
Window 1429-1458 closure (public RC active, epoch 1 triggered)
  |
  ├── A track (ADR-0035, can open immediately):
  |    1459 (CDL opening)  [SENSITIVE]
  |    └── 1460 (CDL ratification)  [SENSITIVE]
  |         └── 1461 (runtime)  [NON-SENSITIVE]
  |
  ├── B track (Rust P2P, can open after entry conditions met):
  |    1462 (PersistentQuicSessionManager)
  |    └── 1463 (CDL-078 Rust relay routing)
  |         └── 1464 (peer discovery ADR)
  |              └── 1465 (Python/Rust bridge)
  |                   └── 1466 (end-to-end tests)
  |
  ├── C track (Werner flow-governor, conditional on diagnostic data):
  |    1467 (diagnostic review + deliberation)
  |    └── 1468 (CDL opening, conditional)  [SENSITIVE if proceeds]
  |         └── 1469 (CDL ratification, conditional)  [SENSITIVE if proceeds]
  |
  ├── D track: ~1470 (CDL falsification criterion, parallel)
  |
  ├── E track: ~1471 (Genesis authority sunset spec)  [SENSITIVE — after C track or parallel]
  |
  └── F track (ADR-0009, can begin after ADR-0035 scope is resolved):
       1472 (Layer 0 schema)
       └── 1473 (bundle generator)
            └── 1474 (independent verifier)
                 └── 1475 (Layer 1 schema)
                      └── 1476 (Layer 2 schema)
                           └── 1477 (Layer 3 binding)
                                └── ~1478 (coherence)
                                     └── ~1479 (closure gate)  [SENSITIVE]
```

---

## 8. Named Carry-Forward Items Not Closeable in This Window

| Item | Why deferred | Gate condition |
|------|-------------|---------------|
| CDL-091 inviter-chaining CDL | Requires SIM evidence + ADR-0009 bundle completion (Tracks B5+F6 done) | Post-F-track window |
| SIM-PRESSURE-SPECTRAL-02 | Requires live network topology data from post-public-RC epochs | Post-public-RC real data |
| CDL-PROVENANCE-DEPTH-01 (hub relay) | Blocked on SIM-PRESSURE-SPECTRAL-02 + live topology data | Post-SIM |
| Mainnet split-custody ceremony | Requires multi-party coordination | Future |
| Production minting activation | Post-public-RC; requires separate deliberation | Future |
| ADR-0008 node usefulness/governance weight | Requires live network data | Post-public-RC data |
| ADR-0028 settlement substrate graduation | Requires live network data | Post-public-RC data |
| Delegated constitutional authority CDL | Gated on J-008 PASS + public RC + 10 independent operators | Window 1480+ |
| Phase B/C governance transition triggers (exact numbers) | Require SIM evidence against Boot/Transition/Mature phase table | Post-E track |

---

## 9. Non-Activation Invariants

This forward plan does not authorize:
- CDL mutation of any currently-ratified CDL
- Production minting or ILC settlement
- Any CDL opening before the Window 1459+ sequence lock is formalized and human-approved
- Track C (Werner CDL) opening before Phase 1467 diagnostic review verdict
- ADR-0009 CDL-091 inviter-chaining deliberation (requires Track F completion first)

---

## 10. This Document's Authority and Next Steps

This is a **draft forward plan** — it does not constitute an authorized sequence lock. Before any phase in this window executes:

1. Window 1429-1458 must close PASS with `public_rc_activated_epoch_1_triggered`.
2. Human reviews this document and approves the overall structure.
3. A formal **Window 1459+ sequence lock** is produced following the schema at `docs/specs/ilc_window_guidance_doc_schema_v0.1.md`.
4. Phase prompts are drafted per the approved sequence lock.

`window_1459_plus_forward_plan_v0.1`
