# Window 1459+: Post-Public-RC Architecture Forward Plan

**Version:** v0.1
**Drafted:** 2026-05-21 (based on Q3/Q4/Q5 resolutions from Window 1429-1458 §8)
**Status:** DRAFT — not an authorized sequence lock; requires human review and GO before any phase executes
**Context:** This forward plan covers the first post-public-RC window. It assumes Window 1429-1458 closes with `public_rc_activated_epoch_1_triggered`. Entry into this window is conditioned on that closure verdict.
**Rehydration addendum (2026-05-27):** Patent-sidequest gaps are recorded in `docs/specs/ilc_patent_sidequest_gap_analysis_and_forward_plan_1448x_v0.1.md`. Filing 5 / agentic function endpoint concepts are routed to Track H compatibility constraints and Candidate Window 1490+ successor scope. Three additional sub-phases were added to Track C after repo verification: Phase ~1469a (W_e Decimal conversion — `node_value_kernel.py` float → Decimal, ICSS §3 compliance), Phase ~1469b (Filing 4 anti-gaming invariants wired into settlement dispatch), and Phase ~1469c (dual-unit ECU+ILC settlement CDL, SENSITIVE). None of these authorize Phase 1448a/1448b publication, runtime activation, CDL mutation, or public disclosure before patent filing/counsel disposition.

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

**Primary objective:** Deepen the architectural foundation of the live network — closing the most consequential deferred architectural items (ADR-0035 type system, Rust P2P substrate, Werner flow-governor CDL readiness, ADR-0009 protocol-native bundles, and ADR-0029 Merkle-Laplacian hardening) and hardening the governance model (Genesis authority sunset spec, CDL falsification criterion, CDL-091 inviter-chaining candidate deliberation).

**What this window does NOT attempt:**
- Production minting or live ILC settlement (long-range post-public-RC only)
- CDL-031 dynamic ranking runtime (requires CDL-019 prerequisite chain first)
- Mainnet split-custody ceremony (multi-party coordination, future window)
- CDL-091 inviter-chaining CDL opening (requires SIM evidence and ADR-0009 bundle work first)
- Merkle-Laplacian epoch-commitment activation or PoSK admission activation (requires ADR-0029 CDL, IP/counsel authorization, and additional SIM hardening)

---

## 3. Entry Conditions

This window may not open until all of the following are confirmed:

| Condition | Evidence required |
|-----------|------------------|
| Public RC published | `public_repository_published` token committed |
| Epoch 1 triggered | `activation_certificate_published` + `epoch_1_transition_authorized` committed |
| At least one external operator connected | `external_operator_identity_ceremony_complete` token committed in window 1429-1458 closure gate handoff |
| Window 1429-1458 closure gate PASS | `window_1429_1458_closed_phase_<N>` committed |
| Werner diagnostic trace data available | At least one epoch of systolic/diastolic/pulse-pressure metrics logged by Track H1 runtime with no false-positive pressure flags recorded |

---

## 4. Track Inventory

| Track | Phases (approx) | Gate conditions closed |
|-------|----------------|----------------------|
| A — ADR-0035 homoiconic type definition system | 1459–1461 | type_definition NodeType CDL + runtime |
| B — Native Rust P2P substrate completion | 1462–1466 | PersistentQuicSessionManager, CDL-078 Rust routing, peer discovery ADR, Python/Rust bridge, end-to-end tests |
| C — Werner flow-governor CDL + ECU pipeline hardening | 1467–1469c | CDL-053 amendment / successor CDL (conditional on diagnostic data); W_e Decimal conversion (~1469a); anti-gaming settlement wiring (~1469b); dual-unit CDL (~1469c, SENSITIVE) |
| D — CDL falsification criterion field | ~1470 | Retroactive falsification_criterion annotation on all ratified CDLs |
| E — Genesis authority sunset spec | ~1471 | Standalone spec formalizing court/house/executive model; closes CDL-004 SUBSTANTIVE gap |
| F — ADR-0009 protocol-native bundle | 1472–1477 | Layer 0-3 bundle schemas, deterministic generator, independent verifier |
| G — ADR-0029 Merkle-Laplacian hardening | 1478–1482 | canonical vectors, PoSK transcript controls, remaining SIM scoping, IP/publication disposition |
| H — ILC Skill / Harness Intelligence Layer | ~1483–1487 | ILC skill architecture spec, ProviderUsageAdapter, LocalNodeCapture + ConsentGate, IdleCapacityScheduler, MaintenanceTaskExecutor + anti-gaming; full crediting conditional on Track C |
| Z — Window coherence + closure | ~1488–1489 | Window closure gate |

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

**Context:** CDL-053 was ratified with a narrow maintenance-equivalent productive-credit scope. The broader Werner flow-governor architecture (heat/pressure signals -> expanded capacity -> economic policy) was deferred from Phase 1263 pending SIM evidence. Track H1 in Window 1429-1458 wires default-off diagnostic metrics during rehearsal and early public RC epochs. This track opens only if diagnostic data meets the deliberation threshold.

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
- Scope: Werner heat signal -> topology pressure -> admission priority (NOT direct ECU minting); must not widen CDL-053 narrow scope without explicit CDL amendment.
- Token: `werner_flow_governor_cdl_opened_phase_1468` (conditional).
- Required GO token: `GO Phase 1468`.
- If Phase 1467 verdict = deferred: skip. Record `werner_flow_governor_cdl_deferred_phase_1468`.

**Phase 1469 — Werner flow-governor CDL ratification (SENSITIVE, conditional)**

- If Phase 1468 proceeded: full prelock/ratification cycle.
- Token: `werner_flow_governor_cdl_ratified_phase_1469` (conditional).
- Required GO token: `GO Phase 1469`.

**Phase ~1469a — W_e Decimal conversion: ECU scoring pipeline (NON-SENSITIVE)**

- **Gap:** `ilc_core/analysis/node_value_kernel.py:109` returns `tuple[float, float, float, float, float]`. All intermediate computation is Python `float`, violating ICSS §3 (Float Ban) for any future settlement-grade use. `spectral_utils.py:59–70` marks `w(e,t)` `PROVISIONAL` and `UNRATIFIED`. Zero settlement-path imports confirmed.
- **What's needed:**
  - Port `node_value_kernel.py` weight and score computations to `decimal.Decimal` with `sort_keys=True` canonical serialization where applicable.
  - Apply `if not d.is_finite(): raise ValueError(...)` guard at all external input boundaries per ICSS §3 edge case.
  - Update the three analysis callers (`node_value_conformance.py`, `node_value_governance_conformance.py`, `node_value_policy_migration.py`) to accept `Decimal` outputs.
  - Update conformance tests.
  - Scope note: this phase makes the analysis module settlement-grade-capable; it does NOT activate settlement or wire the output into the epoch/ledger path (that is Phase ~1469b).
- **Sensitivity:** NON-SENSITIVE (no CDL mutation, no settlement activation, no ledger write).
- **Dependency:** May proceed independently of Phases 1467–1469 (does not require Werner CDL). Logically precedes Phase ~1469b.
- **Token:** `node_value_kernel_decimal_conversion_complete_phase_1469a`.

**Phase ~1469b — Filing 4 settlement dispatch wiring (NON-SENSITIVE)**

- **Gap:** `ilc_core/analysis/utility_flow_rewards.py` (refutation-profitability invariant), `ilc_core/analysis/reuse_diversity_invariants.py` (anti-Sybil weighting), and `ilc_core/analysis/freshness_gate.py` (freshness gate with permanent-axiom exemption) are fully implemented but have **zero imports in any non-analysis `ilc_core/` module** (confirmed grep: no settlement, epoch, or ledger path calls these functions). They are conformance-check tools only.
- **What's needed:**
  - Identify the correct settlement dispatch hook point (epoch processor or reward allocation path) in `ilc_core/`.
  - Import and invoke all three invariant checks before reward allocation is finalized in the epoch path.
  - Wrap with appropriate `Decimal`-safe guards (after Phase ~1469a Decimal conversion completes).
  - Add integration tests confirming invariant violations reject reward allocation, not just log a conformance failure.
  - Scope note: this wires the analysis-layer invariants into the runtime enforcement path; it does NOT alter the invariant logic itself.
- **Sensitivity:** NON-SENSITIVE (no CDL mutation; invariants already ratified via Filing 4 mechanisms).
- **Dependency:** Phase ~1469a (Decimal conversion) should precede or run concurrently. Does not require Werner CDL.
- **Token:** `anti_gaming_settlement_dispatch_wired_phase_1469b`.

**Phase ~1469c — Dual-unit ECU+ILC settlement CDL and pipeline (SENSITIVE)**

- **Gap:** `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py` tracks ECU and ILC as separate `Decimal` values with `ilc_settlement_authorized` as a boolean flag — there is no protocol-committed ECU+ILC pair at epoch boundary. Dual-unit settlement is currently spec-only; the Filing 3 provisional describes it as an embodiment.
- **What's needed:**
  - Open a new CDL scoping the paired `(ECU_delta, ILC_delta)` settlement commitment at epoch boundary: what the pair means, under what authority it is committed, and what the accounting invariants are.
  - Ratification cycle (prelock, two-commit pattern).
  - Runtime: implement the paired settlement pipeline so `ecu_ilc_lifecycle_runtime.py` produces and records a co-committed `(ECU, ILC)` settlement record rather than two independent entries.
  - This CDL must explicitly scope the relationship to CDL-047 treasury, CDL-050/051 economic governance, and CDL-088 claimability.
- **Sensitivity:** SENSITIVE — new CDL mutation; touches settlement economics surface; requires `ILC_CDL_MUTATION_AUTHORIZED=1`.
- **Dependency:** Phase ~1469a (Decimal pipeline), Phase 1469 (Werner CDL — settlement authority gating). Werner CDL ratification should precede or the dual-unit CDL must explicitly scope its relationship to Werner authority.
- **Required GO token:** `GO Phase 1469c`.
- **Token:** `dual_unit_ecu_ilc_settlement_cdl_ratified_phase_1469c`.

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
  - Reproducible across implementations: same schema -> same content hash
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

### Track G — ADR-0029 Merkle-Laplacian Hardening (Phases 1478-1482)

**Context:** The Merkle-Laplacian dual commitment v0.2 paper and strike-force SIM
results are research-positive but remain IP-gated, pre-CDL, and excluded from public
RC artifacts. Commit `5b98ee66` imported the v0.2 draft; commit `aca6241e` ran the
first-pass SIM strike force. The strike force produced:

- `sim_spectral_01_rerun_quantized_smallest_k_viable=true`
- `sim_spectral_cost_01_dense_10k_fast_path_viable=false`
- `sim_posk_01_copy_attack_blocked=true`
- `sim_dualcommit_01_layer_separation_confirmed=true`
- `sim_directed_closure_01_direction_lost_in_s=true`
- `sim_reuse_stability_01_linear_unsafe_log_capped_preferred=true`

Critical caveats:

- `S(t)` activation still requires a CDL and cross-implementation canonicalization proof.
- PoSK must bind sampled edge-set root `R_c` plus the challenge spectrum.
- PoSK still requires response-time or local-storage attestation controls.
- Undirected closure loses directed-flow information; directed-flow claims need a directed spectral extension.
- Linear `reuse_count` weighting is unsafe; log/capped-log remains the candidate family.
- All artifacts stay `PUBLIC_RC_EXCLUDE` until IP/counsel/publication authorization.

Follow-on internal SIM evidence recorded after the first-pass strike force:

- `sim_posk_param_02_multiple_nonce_calibration_complete=true`
- `sim_spectral_crossimpl_02_python_vector_conformance=true`
- `sim_cospectral_01_bounded_random_k8_distinct_m_collision_found=false`
- `sim_directed_spectral_02_extension_required=true`

These tokens support Track G review but do not close activation gates. They remain
internal-only and pre-CDL.

**Phase 1478 — Merkle-Laplacian canonical vectors + transcript readiness review (NON-SENSITIVE)**

- Review `docs/specs/ilc_merkle_laplacian_v02_canonicalization_and_posk_transcript_spec_v0.1.md`.
- Confirm fixed-point int64 little-endian vectors reproduce in Python.
- Confirm legacy `spectral_hash()` is not used for v0.2 epoch commitments.
- Token: `merkle_laplacian_v02_canonical_vectors_reviewed_phase_1478`.

**Phase 1479 — PoSK parameter and ceremony-control SIM scoping (NON-SENSITIVE)**

- Review `SIM-POSK-PARAM-02` evidence:
  - candidate sample size and multiple nonce count;
  - stale-cache and partial-graph pass rates;
  - response timeout / local-storage attestation requirement;
  - post-challenge full-fetch caveat.
- Output: parameter-readiness review, not activation.
- Token: `sim_posk_param_02_scoped_phase_1479`.

**Phase 1480 — Cross-implementation and cospectral SIM scoping (NON-SENSITIVE)**

- Review:
  - `SIM-SPECTRAL-CROSSIMPL-02` Python conformance and remaining non-Python port obligation;
  - `SIM-COSPECTRAL-01` bounded search results and formal/crafted cospectral-work obligation;
  - `SIM-DIRECTED-SPECTRAL-02` directed-flow extension requirement.
- Decide whether to commission deeper formal/crafted cospectral examples before
  any CDL opening proposal.
- Token: `merkle_laplacian_remaining_sims_scoped_phase_1480`.

**Phase 1481 — IP/counsel/publication disposition (SENSITIVE)**

- Decide whether the paper can move toward publication, patent filing, or continued internal hold.
- This phase may not remove `PUBLIC_RC_EXCLUDE` unless explicit IP/counsel/publication authorization is recorded.
- Token: `merkle_laplacian_ip_publication_disposition_phase_1481`.
- Required GO token: `GO Phase 1481`.

**Phase 1482 — ADR-0029 Merkle-Laplacian CDL readiness verdict (SENSITIVE if opening proceeds)**

- Review all SIM and IP/counsel evidence.
- If gates are not met, record explicit deferral.
- If gates are met, produce a CDL opening proposal for Merkle-Laplacian epoch commitments and/or PoSK admission.
- Any CDL opening requires explicit human GO and the two-commit CDL mutation discipline.
- Token if deferred: `adr_0029_merkle_laplacian_cdl_deferred_phase_1482`.
- Token if opened: `adr_0029_merkle_laplacian_cdl_opened_phase_1482`.

---

### Track H — ILC Skill / Harness Intelligence Layer (Phases ~1483-1487)

**Context:** Established during Window 1429-1458 architecture discussions (2026-05-23). The ILC skill interprets LLM turn outputs as ILC graph node submissions via a harness-side interpreter layer — not a protocol fork. The skill consumes stable `ilc_core/` surfaces (CLI commands, structured markers, content-addressed node framing) and adds operator-side intelligence on top.

This track provides the implementation substrate for the idle-capacity contribution mechanism: spare LLM API quota → maintenance lottery tasks → Werner/ECU credit path. Full crediting is conditional on Track C (Werner flow-governor CDL). Phases ~1483–1485 (spec, ProviderUsageAdapter, LocalNodeCapture) can proceed independently; Phases ~1486–1487 (IdleCapacityScheduler, MaintenanceTaskExecutor) depend on Track C ratification for Werner crediting but can be implemented and tested locally before it.

**Design invariants (from boundary doc §10 addendum and Codex review 2026-05-23):**
- TOON compression applies to outbound context packing only — captured model output preserves raw response bytes; the node envelope is added separately and is not part of the content hash
- The skill consumes stable `ilc_core/` surfaces; it does not redefine admission semantics or become the sole graph-writing path
- Provider quota headers are operational scheduling signals only — not protocol truth, economic proof, or inputs to Werner credit calculation
- Werner crediting is disabled until the Werner flow-governor CDL (Track C) explicitly authorizes the on-ramp; local scheduling and node capture may proceed before Track C

**Patent-sidequest compatibility note (2026-05-27):** Filing 5 discussions introduced future agentic-function endpoint concepts: graph-native function endpoints anchored to identity-seed-derived agent identities, query-response artifacts, co-attested inference receipts, processing-capacity tier metadata, model/capability substitution records, agent trust-state neighborhood projections, and invitation/provenance for peer-to-peer protocol bundle distribution. Track H may preserve compatibility with those concepts through local capture, LMDB storage, and consent-gated publication surfaces, but Track H must not implement or imply protocol activation of function endpoints, processing-capacity tiers, inference crediting, invitation economics, or executable graph payloads. These concepts are routed to Candidate Window 1490+ successor scope unless and until a later sequence lock authorizes them.

**Non-negotiable testing requirement for Phase ~1485 (LocalNodeCapture):**

Every test suite for LocalNodeCapture must include an explicit hash-separation test:

1. Execute a turn with a TOON-compressed outbound prompt.
2. Capture the raw model response bytes.
3. Assert: `content_hash == SHA-256(json.dumps(raw_response_payload, sort_keys=True))`.
4. Assert: `content_hash != SHA-256(json.dumps(toon_packed_prompt, sort_keys=True))`.
5. Assert: the node envelope fields (`epoch_id`, `agent_id`, `capture_timestamp_epoch_sequence`) are NOT included in the content hash input.

This prevents the skill from accidentally canonicalizing or compressing the actual claim content before content-addressing. The test must fail if TOON packing touches the captured output in any way.

**Anti-gaming requirements (must be scoped before MaintenanceTaskExecutor activates):**
- Diversity controls: per-operator slot cap per epoch prevents one operator from supplying all maintenance completions
- Duplicate suppression: task_id uniqueness enforced; completed task_ids recorded in LMDB
- Result-quality gate: Werner credit amount weighted by review-lane acceptance score, not raw submission count
- Attribution: task completion records bind `provider_id`, `operator_agent_id`, `task_id`, `epoch_id`

**Phase ~1483 — ILC skill architecture spec (NON-SENSITIVE)**

- Produce spec: `docs/specs/ilc_skill_harness_intelligence_layer_spec_v0.1.md`
- Covers: TOON outbound compression, raw response capture, content-addressed node framing, LMDB local store, consent-gated publication path, bootstrap via SOUL.md/AGENTS.md, `runAttempt` hook placement, `registerAgentToolResultMiddleware` capture point
- Constraint: raw captured output is the hashable content; node envelope (epoch_id, agent_id, capture_timestamp_epoch_sequence) is added separately
- Token: `ilc_skill_architecture_spec_committed_phase_1483`

**Phase ~1484 — ProviderUsageAdapter implementation (NON-SENSITIVE)**

- Implement `ProviderUsageAdapter` in harness adapter package (not `ilc_core/`):
  - Anthropic: reads `anthropic-ratelimit-tokens-remaining` + `anthropic-ratelimit-tokens-reset` from every API response header
  - OpenAI: reads `x-ratelimit-remaining-tokens` + `x-ratelimit-reset-tokens`
  - Gemini: reads `usage_metadata` from response body (no confirmed remaining-tokens header contract; falls back to local counter + configurable budget)
  - Local fallback: operator-configured monthly budget with local counter for providers without header-level remaining-quota exposure
- Constraint: provider quota signals are operational scheduling data only; must not feed into any Werner credit calculation, Werner diagnostic quote, or protocol proof
- Token: `provider_usage_adapter_implemented_phase_1484`

**Phase ~1485 — LocalNodeCapture + ConsentGate (NON-SENSITIVE)**

- Implement `LocalNodeCapture` via `registerAgentToolResultMiddleware`:
  - Intercepts tool results; wraps as content-addressed ILC nodes (`SHA-256(json.dumps(payload, sort_keys=True))`)
  - Writes to LMDB node store using stable `ilc_core/` graph surfaces — does not redefine node admission semantics
  - Raw response bytes are the hashable content; node envelope (epoch_id, agent_id) appended separately
- Implement `ConsentGate`:
  - Local-first: all captures go to LMDB immediately; no publication default
  - Human opt-in required for publication via `/v1/protocol/claim`
  - `AUTO_PUBLISH_REQUIRES_EXPLICIT_CONSENT = True` — no automatic public claim without policy flag set
- Token: `local_node_capture_consent_gate_implemented_phase_1485`

**Phase ~1486 — IdleCapacityScheduler (NON-SENSITIVE)**

- Implement `IdleCapacityScheduler`:
  - Reads `ProviderUsageAdapter` quota state after each API response
  - Configurable threshold: `remaining_tokens_threshold` (default: 50,000) and `idle_window_cron` (default: 22:00–06:00 local)
  - Session idle detection: reads JSONL session transcript last-active timestamp
  - If idle + above threshold: surfaces maintenance lottery task offer to human operator (does not auto-execute)
  - Human opt-in required before first task execution per session
- Crediting path: records completion locally with `werner_credit_pending_track_c_cdl` flag if Track C not yet ratified; no credit is minted until Track C CDL ratified
- Token: `idle_capacity_scheduler_implemented_phase_1486`

**Phase ~1487 — MaintenanceTaskExecutor + anti-gaming controls (NON-SENSITIVE)**

- Implement `MaintenanceTaskExecutor`:
  - Task types: `star.map.embedding`, `contradiction.sweep`, `graph.compression`, `stability.simulation` (review-lane / maintenance-lottery tasks only; no protocol mutations)
  - Each task execution passes through `runAttempt` with TOON-formatted task envelope
  - Results submitted via `LocalNodeCapture` → `ConsentGate` → Werner credit recording path
- Implement anti-gaming controls per the requirements above
- Constraint: `review_lane_only=True` flag from Phase 1442 `WernerDiagnosticQuote` governs all maintenance task completions; `settlement_grade=False` until Track C CDL ratified
- Token: `maintenance_task_executor_anti_gaming_implemented_phase_1487`

---

### Post-1489 Successor Scope — ILC-Native Harness MVP (Candidate Window 1490+)

**Status:** Planning scope only. This section does not add executable phases to
Window 1459+ and does not authorize work after Phase ~1489. It records the
expected next window shape if Track H closes cleanly.

**Goal:** Build a first-party ILC-native harness that is OpenClaw-style in user
experience but ILC-native in architecture: a plug-and-play sidecar recipe host,
not a protocol fork and not a monolithic app inside `ilc_core/`.

**Definition:** An ILC-native harness is a local operator runtime that composes
sidecar recipes over stable `ilc_core/` surfaces:

```text
human/operator policy
  -> harness recipe manifest
  -> agent loop orchestrator
  -> provider/tool adapters
  -> sidecar recipe modules
  -> local graph/LMDB capture
  -> consent-gated publication / verification
```

**Candidate Window 1490+ areas:**

| Area | Candidate scope | Sidecar recipe modules | Non-claim |
|------|-----------------|------------------------|-----------|
| I — Recipe manifest + loader | Define signed/local `ilc_harness_recipe_manifest` format, dependency isolation, enable/disable policy, and public/private recipe flags | recipe registry, loader, capability policy | Does not make any recipe protocol truth |
| J — Agent loop runtime | Implement resumable `runAttempt`, task queue, retry/resume, transcript capture, and tool-routing lifecycle | agent loop orchestrator, attempt journal, transcript store | Does not replace review lane or node admission |
| K — Provider runtime adapters | Normalize model calls, streaming, tool-call responses, cost accounting, timeout/backoff, and provider-specific usage metadata | OpenAI adapter, Anthropic adapter, Gemini/local fallback adapter | Provider usage is scheduling data only |
| L — Operator UX shell | Provide CLI/TUI/local web panel for budgets, pending captures, consent queue, task history, identity status, earned/pending credit | approval inbox, budget panel, identity panel, publication queue | No automatic publication without consent policy |
| M — Maintenance workbench | Turn Track H maintenance tasks into operator-visible queues with quality gates and replayable evidence | star-map embedding recipe, contradiction sweep recipe, graph compression recipe, stability simulation recipe | Credit remains gated by Werner CDL authority |
| N — Goal/function-set coordination recipes | Package harness coordination functions as sidecar recipes with explicit privacy and public-path gates | task offers, task reservations, result availability, receipt/claimability availability, peer health, sealed/private coordination | Does not activate native public Rust P2P or bypass TransportPrincipal |
| O — Distribution + update path | Package `ilc-harness` for pipx/Homebrew, signed recipe packs, local upgrade checks, and compatibility tests | installer recipe, recipe-pack verifier, conformance pack | No public package/release claim without release authority |
| P — Agentic function endpoint schema | Define sidecar-bounded function endpoint descriptors anchored to identity-seed-derived `agent_id`, with query interface, output schema, side-effect boundary, and provenance binding | function endpoint descriptor, endpoint registry projection, local endpoint verifier | Does not create independent endpoint identities or executable core graph payloads |
| Q — Query-response + co-attested inference artifacts | Define graph-native artifact schemas for query-response outputs and multi-agent co-attestation receipts | query-response artifact, co-attestation receipt, contributor signature bundle | Does not mint credit or bypass truth-primitive validation/refutation |
| R — Agent trust-state neighborhood projection | Define a read model where an agent identity is evaluated by its cryptographic root plus attributed graph actions, validations, refutations, substitutions, and artifacts | trust-state projector, identity-neighborhood view, refutation-survival summary | Does not replace `agent_id` derivation or create reputation scoring authority |
| S — Model/capability substitution continuity | Define recipes for capability updates, model substitution, identity-continuity claims, and identity-fork/refutation paths | substitution event artifact, continuity claim recipe, fork recommendation report | Does not permit silent identity mutation or unratified signer-lineage changes |
| T — Tier-aware routing and anti-capture simulation | Simulate processing-capacity tier declarations, tier-honesty checks, response novelty gates, and cluster-diverse endpoint routing | tier declaration stub, routing SIM, anti-capture harness | Processing tier is not economic proof or protocol truth before CDL authority |
| U — Invitation/provenance + protocol bundle serving path | Integrate Track F protocol bundle artifacts with invitation provenance and serving receipts as a prerequisite for any later inviter-attribution economics | bundle serving receipt, invitation provenance chain, ADR-0009 verifier bridge | No public bundle-serving incentive or CDL-091 successor activation in this window |

**Goal/function-set taxonomy (must be explicit in future prompts):**

| Function set | Purpose | Default visibility | Required gate |
|--------------|---------|--------------------|---------------|
| `task_offer_coordination` | Present available maintenance tasks to opted-in local harnesses | local/private or Tailscale-only | public path requires TransportPrincipal/public P2P authority |
| `task_reservation_coordination` | Reserve a maintenance task and suppress duplicate execution | local/private | public claim requires anti-gaming + review-lane policy |
| `task_result_availability` | Record that a local result exists and can be reviewed/fetched | local/private by default | publication requires ConsentGate |
| `receipt_claimability_availability` | Record verifier receipts, nullifier state, or claimability proof availability | local/private until public verifier authority | public serving requires activated verifier API |
| `peer_health_diagnostics` | Share bounded diagnostics, capacity, and reachability status | diagnostic only | no economic proof; no provider quota in protocol state |
| `sealed_private_coordination` | Private coordination payload announce/pull through CCSS recipes | private/gated | CCSS authority and privacy tests |
| `function_endpoint_query` | Route a bounded query to a sidecar-hosted function endpoint and capture a declarative response artifact | local/private by default | public graph artifact requires ConsentGate and later schema authority |
| `co_attestation_coordination` | Collect multiple agent signatures over a shared output or inference result | local/private until publication | no credit without Werner/ECU authority and review-lane policy |
| `trust_state_projection` | Compute an advisory identity-neighborhood summary from attributed graph actions and outcomes | local/diagnostic | no protocol reputation score or admission consequence |
| `identity_continuity_event` | Record capability/model substitution evidence and continuity/fork recommendations | local/diagnostic until schema ratified | no silent `agent_id` mutation |
| `bundle_invitation_provenance` | Relate protocol bundle serving receipts to invitation provenance chains | local/private until Track F evidence exists | no inviter economics without later CDL authority |

**Required carry-forward tokens:** `ilc_native_harness_mvp_successor_scope_recorded_window_1459_forward_plan`; `agentic_function_endpoint_successor_scope_recorded_window_1459_forward_plan`; `agent_trust_state_neighborhood_successor_scope_recorded_window_1459_forward_plan`.

---

### Track Z — Window Coherence + Closure

**Phase ~1488 — Window coherence, capsule update, ADR housekeeping (NON-SENSITIVE)**

- Update context capsule.
- Review open ADR obligations: ADR-0008 (node usefulness), ADR-0019 (graph-native governance), ADR-0024 (agent skills Tier 3), ADR-0025 (dynamic peer discovery — if Phase 1464 closed this, record closure), ADR-0028 (settlement substrate graduation), ADR-0029 (hypergraph spectral hash epoch commitment).
- Record CDL-091 inviter-chaining candidate deliberation status (CDL opening requires SIM evidence; record gate conditions still outstanding if applicable).
- Token: `window_1459_plus_coherence_complete_phase_1488`.

**Phase ~1489 — Window closure gate (SENSITIVE)**

- Closure verdict against window objective.
- Required GO token: `GO Phase 1489`.
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
| C4 | ~1469a | W_e Decimal conversion — port `node_value_kernel.py` from float to Decimal; ICSS §3 compliance | Runtime | NON-SENSITIVE |
| C5 | ~1469b | Filing 4 settlement dispatch wiring — import anti-gaming invariants into epoch/reward path | Runtime | NON-SENSITIVE |
| C6 | ~1469c | Dual-unit ECU+ILC settlement CDL + paired pipeline | Constitutional + Runtime | **SENSITIVE** |
| D1 | ~1470 | CDL falsification criterion field — retroactive annotation on all ratified CDLs | Coherence | NON-SENSITIVE |
| E1 | ~1471 | Genesis authority sunset spec — court/house/executive three-branch model | Constitutional | **SENSITIVE** |
| F1 | ~1472 | ADR-0009 Layer 0 protocol bundle schema | Spec | NON-SENSITIVE |
| F2 | ~1473 | Deterministic bundle generator | Runtime | NON-SENSITIVE |
| F3 | ~1474 | Independent bundle verifier | Runtime | NON-SENSITIVE |
| F4 | ~1475 | Layer 1 Genesis state bundle schema | Spec | NON-SENSITIVE |
| F5 | ~1476 | Layer 2 epoch snapshot schema | Spec | NON-SENSITIVE |
| F6 | ~1477 | Layer 3 D2D wire-message binding | Runtime | NON-SENSITIVE |
| G1 | ~1478 | Merkle-Laplacian canonical vectors + transcript readiness review | Research/spec | NON-SENSITIVE |
| G2 | ~1479 | PoSK parameter and ceremony-control SIM scoping | Research/SIM scoping | NON-SENSITIVE |
| G3 | ~1480 | Cross-implementation and cospectral SIM scoping | Research/SIM scoping | NON-SENSITIVE |
| G4 | ~1481 | Merkle-Laplacian IP/counsel/publication disposition | Legal/IP/publication | **SENSITIVE** |
| G5 | ~1482 | ADR-0029 Merkle-Laplacian CDL readiness verdict/opening decision | Constitutional | **conditional SENSITIVE** |
| H1 | ~1483 | ILC skill architecture spec — TOON, node capture, LMDB, consent gate | Spec | NON-SENSITIVE |
| H2 | ~1484 | ProviderUsageAdapter — Anthropic/OpenAI/Gemini/local fallback | Runtime (harness) | NON-SENSITIVE |
| H3 | ~1485 | LocalNodeCapture + ConsentGate — tool result middleware, LMDB write, opt-in publication | Runtime (harness) | NON-SENSITIVE |
| H4 | ~1486 | IdleCapacityScheduler — quota threshold, idle window, human opt-in | Runtime (harness) | NON-SENSITIVE |
| H5 | ~1487 | MaintenanceTaskExecutor + anti-gaming controls — diversity cap, dedup, quality gate, attribution | Runtime (harness) | NON-SENSITIVE |
| Z1 | ~1488 | Window coherence + capsule + ADR housekeeping | Synthesis | NON-SENSITIVE |
| Z2 | ~1489 | Window closure gate | Gate | **SENSITIVE** |

Total: ~31 planned phases plus contingency slots. Exact phase number assignments depend on Window 1429-1458 closing phase number.

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
  |
  ├── G track (ADR-0029 Merkle-Laplacian hardening, can run after F or parallel if IP hold permits):
  |    1478 (canonical vectors + transcript readiness)
  |    └── 1479 (PoSK parameter SIM scoping)
  |         └── 1480 (cross-implementation/cospectral SIM scoping)
  |              └── 1481 (IP/publication disposition)  [SENSITIVE]
  |                   └── 1482 (CDL readiness/opening decision)  [SENSITIVE if opening proceeds]
  |
  ├── H track (ILC Skill / Harness Intelligence Layer, can begin after entry conditions met):
  |    ~1483 (ILC skill architecture spec)
  |    └── ~1484 (ProviderUsageAdapter)
  |         └── ~1485 (LocalNodeCapture + ConsentGate)
  |              └── ~1486 (IdleCapacityScheduler)  [Werner crediting requires Track C]
  |                   └── ~1487 (MaintenanceTaskExecutor + anti-gaming)  [Werner crediting requires Track C]
  |
  └── Z track:
       ~1488 (coherence)
       └── ~1489 (closure gate)  [SENSITIVE]
```

---

## 8. Named Carry-Forward Items Not Closeable in This Window

| Item | Why deferred | Gate condition |
|------|-------------|---------------|
| CDL-091 inviter-chaining CDL | Requires SIM evidence + ADR-0009 bundle completion (Tracks B5+F6 done) | Post-F-track window |
| SIM-PRESSURE-SPECTRAL-02 | Requires live network topology data from post-public-RC epochs | Post-public-RC real data |
| CDL-PROVENANCE-DEPTH-01 (hub relay) | Blocked on SIM-PRESSURE-SPECTRAL-02 + live topology data | Post-SIM |
| ADR-0029 Merkle-Laplacian epoch commitment activation | Blocked on Track G, cross-implementation vectors, cospectral SIM, PoSK parameter SIM, IP/counsel disposition, and CDL opening/ratification | Post-Track-G and SENSITIVE CDL |
| PoSK admission-gate activation | Blocked on Track G, PoSK timeout/local-storage attestation design, multiple-nonce/sample-size calibration, and CDL authority | Post-SIM-POSK-PARAM-02 and SENSITIVE CDL |
| Merkle-Laplacian paper publication or `PUBLIC_RC_EXCLUDE` removal | Blocked on IP/counsel/publication authorization | SENSITIVE publication disposition |
| Mainnet split-custody ceremony | Requires multi-party coordination | Future |
| Production minting activation | Post-public-RC; requires separate deliberation | Future |
| ADR-0008 node usefulness/governance weight | Requires live network data | Post-public-RC data |
| ADR-0028 settlement substrate graduation | Requires live network data | Post-public-RC data |
| Delegated constitutional authority CDL | Gated on J-008 PASS + public RC + 10 independent operators | Window 1480+ |
| Phase B/C governance transition triggers (exact numbers) | Require SIM evidence against Boot/Transition/Mature phase table | Post-E track |
| ILC-native harness MVP | Requires Track H closure; should be a successor window, not a late insertion into Window 1459+ | Candidate Window 1490+ sequence lock |
| Filing 5 agentic function endpoint layer | Requires patent filing/counsel disposition, Track H local capture substrate, sidecar schema design, and successor sequence lock; economic parts also require Werner/ECU authority | Candidate Window 1490+ sequence lock and later CDL/SIM gates |
| Agent trust-state neighborhood projection | Requires direct schema work and careful separation from protocol reputation/admission authority | Candidate Window 1490+ advisory read-model scope |
| Invitation/provenance protocol bundle serving economics | Requires ADR-0009 Track F bundle generator/verifier evidence and later CDL-091 successor deliberation | Post-F-track window |

---

## 9. Non-Activation Invariants

This forward plan does not authorize:
- CDL mutation of any currently-ratified CDL
- Production minting or ILC settlement
- Any CDL opening before the Window 1459+ sequence lock is formalized and human-approved
- Track C (Werner CDL) opening before Phase 1467 diagnostic review verdict
- ADR-0009 CDL-091 inviter-chaining deliberation (requires Track F completion first)
- Merkle-Laplacian `S(t)` epoch-commitment activation without a SENSITIVE CDL
- PoSK admission-gate activation without a SENSITIVE CDL and ceremony-control spec
- Public release of Merkle-Laplacian paper/SIM artifacts or removal of `PUBLIC_RC_EXCLUDE` without IP/counsel/publication authorization
- Any Window 1490+ ILC-native harness MVP phase execution before a successor sequence lock and explicit human GO
- Automatic public publication of captured model/tool outputs without ConsentGate policy
- Public task coordination, public receipt coordination, or native public Rust P2P activation through Track H alone
- Function endpoint protocol activation, processing-capacity tier authority, co-attested inference crediting, or agent trust-state projection authority through Track H alone
- Executable payloads in core graph nodes or an eighth truth primitive for agentic coordination
- Invitation-based economic credit, public protocol bundle serving incentives, or CDL-091 successor activation before ADR-0009 Track F evidence and later CDL authority
- Public disclosure of patent-derived Filing 5 implementation details before Phase 1448a records patent filing/counsel disposition or explicit human deferral

---

## 10. This Document's Authority and Next Steps

This is a **draft forward plan** — it does not constitute an authorized sequence lock. Before any phase in this window executes:

1. Window 1429-1458 must close PASS with `public_rc_activated_epoch_1_triggered`.
2. Human reviews this document and approves the overall structure.
3. A formal **Window 1459+ sequence lock** is produced following the schema at `docs/specs/ilc_window_guidance_doc_schema_v0.1.md`.
4. Phase prompts are drafted per the approved sequence lock.

`window_1459_plus_forward_plan_v0.1`

Related internal support record: `docs/specs/ilc_patent_sidequest_gap_analysis_and_forward_plan_1448x_v0.1.md`.
