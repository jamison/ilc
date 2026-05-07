# ILC Launch Roadmap: Three Computers, Seven Agents

**Version:** v1.0
**Produced:** 2026-05-05
**Session context:** Window 1191-1199 closed at Phase 1199. Window
1183-1190 closed with CDL-085 ratified, `EDGE_MINT_PHI_BOUND = Decimal("0.60")`
active in runtime, and all three SIM-SPECTRAL-05 observer slices complete. Capsule v5.44
is current until Phase 1198 publishes v5.45.
**Supersedes:** `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.9.md`
**Purpose:** Refresh the public-RC and RC2 planning surface after CDL-085 ratification,
runtime activation, gossip-slice completion, and the Phase 1188 correction that routes the
public-launch packaging blocker to a fresh CDL number rather than CDL-001.

`launch_roadmap_v1_0_published_phase_1192`

**Post-Phase-1238 addendum:** Roadmap v1.0 remains the active gap inventory, but parts of
its early RC2 status table are stale relative to later canon. A pre-sequence runway
addendum now records the required Roadmap v1.1 refresh, public-RC blocker classes,
and candidate Window 1241+ bands:
`docs/specs/ilc_public_rc_runway_pre_sequence_plan_1241_plus_v0.1.md`.

`launch_roadmap_v1_1_refresh_required_after_phase_1240`
`public_rc_runway_pre_sequence_plan_1241_plus_recorded_phase_1238`

---

## 1. What Has Changed Since v0.9

| Item | v0.9 state | Current v1.0 state |
|------|------------|--------------------|
| CDL-085 | Open / not ratified | **Ratified** in Phase 1185 (`cdl_085_ratified_phase_1185`) |
| EDGE_MINT_PHI_BOUND | Unset planning candidate | **Active runtime value:** `EDGE_MINT_PHI_BOUND = Decimal("0.60")` |
| Attribution runtime | `epoch_attribution_settle_runtime_1129_fix1.v0.5` | **`epoch_attribution_settle_runtime_1185.v0.6`** |
| Runtime dependency | CDL-084 only | `CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"` |
| SIM-SPECTRAL-05 runtime-binding slice | Deferred | **Passed** (`sim_spectral_05_runtime_binding_slice_pass`) |
| SIM-SPECTRAL-05 economic-flow slice | Deferred | **Passed** (`sim_spectral_05_economic_flow_slice_pass`) |
| SIM-SPECTRAL-05 gossip slice | Deferred | **Passed** (`sim_spectral_05_gossip_slice_pass`) |
| SIM-SPECTRAL-05 framework | Partial | **Complete:** `sim_spectral_05_three_slice_observer_framework_complete` |
| Public-launch packaging blocker | Label drift around CDL-001 | **CDL-086 is OPEN** (`cdl_086_public_launch_packaging_blocker_opened_phase_1194`); CDL-001 is a dependency |
| v0.2 signing | Prerequisites met, unsigned | Still unsigned; explicit signing authorization absent |
| Window state | Pre-1183 planning | Window 1191-1199 active through Phase 1192 |

---

## 2. Current State Summary

| Surface | Status |
|---------|--------|
| Option B selection | **SELECTED** (`adr_0028_posture=option_b`, Phase 814) |
| Row 5 privacy lane | **`runtime_closed`** (Phase 846, CDL-072) |
| Row 7 | **`runtime_closed`** |
| Row 8 | **`pass`** |
| Truth primitive stack | **OPERATIONAL** — submit → persist → gossip → fetch → spectral routing loop |
| RC0.1 substrate | **`satisfied_for_testbed`** |
| RC1 | **`satisfied`** — CDL-073 through CDL-084 ratified; HB-002 closed |
| CDL-084 | **RATIFIED** — `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`; `PROVENANCE_MAX_DEPTH = 3` |
| CDL-085 | **RATIFIED** — Werner φ-bound provenance equivalence limit |
| EDGE_MINT_PHI_BOUND | **ACTIVE** — `Decimal("0.60")` |
| Runtime | **`epoch_attribution_settle_runtime_1185.v0.6`** |
| SIM-SPECTRAL-05 observer slices | **COMPLETE** — runtime-binding, economic-flow, and gossip all passed |
| ADR-0037 Genesis Canonical Lineage Contract | **ACCEPTED** |
| ADR-0036 Operational Release Key | **ACCEPTED** |
| Genesis Atlas v0.1 signed | **IMMUTABLE** — 32 nodes, 55 edges, hash `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Genesis Atlas v0.2 candidate | **41 nodes, 73 edges, unsigned** — signing prerequisites met; explicit human authorization required |
| Public-launch packaging blocker | **OPEN** — CDL-086 opened in Phase 1194; not ratified |
| Tier-3 runtime linkage | Scope committed in Phase 1195; runtime lane not yet implemented |
| Persistent rate limiter | Scope committed in Phase 1196; implementation remains open |
| Canon bundle signing repair | **SATISFIED** — `canon_bundle_signing_repair_pass_phase_1197` |

---

## 3. RC Milestone Map

| Milestone | Gate criteria | Current status |
|-----------|---------------|----------------|
| RC0.1 | Three-node substrate; 7-agent scenario; reproducible substrate | **`satisfied_for_testbed`** |
| RC1 | CDL-073 bootstrap schema; truth primitive stack operational; CDL-078 relay incentives; HB-002 closed | **`satisfied`** |
| RC2 | CDL-085 ratified; v0.2 signed; Tier-3 linkage; public-launch packaging blocker evaluated/progressed; persistent rate limiter; truth-primitive permanence governance | **In progress** — gate 1 satisfied |
| RC3 / Launch | L4 privacy wired; CDL-070 PQ ceremony; compaction CDL; multi-hop attribution CDL; counsel track complete | Long-range |

### RC2 Gate Status

| # | Gate | Status |
|---|------|--------|
| 1 | CDL-085 ratified and active | **SATISFIED** |
| 2 | v0.2 signing ceremony executed | **OPEN** — authorization absent |
| 3 | Tier-3 runtime linkage | **SCOPED** — `tier3_runtime_linkage_scope_committed_phase_1195`; implementation remains open |
| 4 | Public-launch packaging blocker evaluated/progressed | **IN PROGRESS** — CDL-086 is open, not ratified |
| 5 | Persistent rate limiter | **SCOPED** — `persistent_rate_limiter_scope_committed_phase_1196`; implementation remains open |
| 6 | Truth-primitive permanence community ratification | **ROUTED** — ratification packet required (`truth_primitive_permanence_governance_routed_phase_1206`) |

---

## 4. Gap Inventory

### Gap 1 — v0.2 Signing Ceremony

**Status:** Prerequisites met; explicit signing authorization absent.

ADR-0036 and ADR-0037 satisfy the governance prerequisites for signing the 41-node /
73-edge v0.2 candidate. The signing act still requires:

```text
v0_2_signing_ceremony_authorized_phase_1193
GO Phase 1193
```

If those tokens are not issued, Phase 1193 must use the skip path and preserve:

```text
v0_2_signing_ceremony_deferred_pending_signing_authorization
```

### Gap 2 — Public-Launch Packaging Blocker

**Status:** CDL-086 is open; ratification remains future work.

Phase 1188 corrected the roadmap label drift. CDL-001 is ratified signer-lineage canon and
is a dependency, not the public-launch packaging blocker target. The packaging blocker
opened under fresh number CDL-086 in Phase 1194.

`cdl_086_public_launch_packaging_blocker_opened_phase_1194`

Opening scope should cover:

- public release artifact definition;
- launch trigger conditions;
- release packaging and distribution governance;
- relationship to RC2, RC3, and public launch;
- dependency on CDL-001, ADR-0036, ADR-0037, and CDL-085;
- counsel track as a ratification condition.

### Gap 3 — Tier-3 Runtime Linkage

**Status:** Tier-3 runtime linkage scope committed; runtime implementation remains open.

ADR-0020 is accepted. Phase 1195 should remain scope-first, with bounded implementation
only if inspection shows a small, unambiguous, testable first tranche.

Phase 1195 published:

`tier3_runtime_linkage_scope_committed_phase_1195`

No Tier-3 runtime token was introduced.

### Gap 4 — Persistent Rate Limiter

**Status:** Persistent rate limiter scope committed; implementation remains open.

Phase 1196 should inspect the existing limiter surface and either implement a bounded,
testable persistence hardening change or publish a concrete implementation plan. It must
not introduce wall-clock protocol logic, predictable PRNG use, or unbounded input handling.

Phase 1196 published:

`persistent_rate_limiter_scope_committed_phase_1196`

No runtime token was introduced.

### Gap 5 — Truth-Primitive Permanence Community Ratification

**Status:** Governance carry-forward.

`truth_primitive_permanence_requires_community_ratification_before_genesis_sunset`

This remains a pre-public-RC governance requirement and is not assigned to Window
1191-1199.

### Gap 6 — Canon Bundle Signing Repair

**Status:** Satisfied in Phase 1197.

The known failing fixtures were repaired:

- `test_canon_bundle_audit_artifact.py`
- `test_canon_bundle_pipeline_report.py`

Phase 1197 added a deterministic valid v0.1 testing snapshot and an explicit test-only
toggle in both fixture files so the bundle pipeline reaches the intended sign/verify/report
/audit path without weakening production validation.

`canon_bundle_signing_repair_pass_phase_1197`

### Gap 7 — Counsel Track and IP Track

**Status:** Parallel lane. Self-counsel model adopted 2026-05-07 (no budget for
external legal counsel; tokens close via internal decision + committed artifact).

**Counsel track closure conditions (revised for self-counsel):**
- `counsel_license_instrument_selection_required_before_public_rc` → closes when
  AGPL-3.0 root LICENSE + LICENSING.md zone table committed as an internal decision.
- `counsel_cla_text_approved_before_external_contributors` → closes when DCO or CLA
  choice committed to repo.
- `counsel_trademark_policy_published_required_before_public_launch` → closes when
  a trademark policy stub committed.
- `genesis_canonical_lineage_contract_required_before_public_rc` → closes through
  normal CDL/ADR process (ADR opening and acceptance route not yet assigned to a
  window; planning spec drafted Phase 1153).

These are internal decision points, not blocked on external legal review. Self-counsel
basis must be recorded explicitly in the commit and walkthrough for future auditors.

**IP track — US Provisional Patent Application:**

A US Provisional Patent Application for the Merkle-Laplacian dual commitment
construction must be filed before any public repository publication. This is a
**hard prerequisite on the same gate as the license work**, running in parallel.

Decision (2026-05-07): self-file the provisional (~$320 USPTO small entity fee).
Follow within 12 months with PCT application to preserve all international rights.
See `docs/research/ilc_genesis_lineage_fork_resistance_and_license_strategy_v0.1.md`
§7b for full filing plan, jurisdiction list, cost table, and gate details.

**Why this is time-critical:** once the repository is made public, EU, JP, and most
international patent rights are permanently destroyed unless the provisional has
already been filed (US has a 1-year grace period; international jurisdictions require
absolute novelty pre-disclosure). The `docs/research/patent_pending/` folder must be
excluded from the public repo until the patent is filed.

Open carry-forward tokens (all must close before public RC / public launch):
- `us_provisional_patent_application_filed` ← NEW hard gate
- `counsel_license_instrument_selection_required_before_public_rc`
- `counsel_cla_text_approved_before_external_contributors`
- `counsel_trademark_policy_published_required_before_public_launch`
- `genesis_canonical_lineage_contract_required_before_public_rc`

### Gap 9 — Sidecar Projection Endpoint

**Status:** Carry-forward; gated on CDL-087 ratification.

Carry-forward token: `sidecar_projection_endpoint_required_post_cdl_087_ratification`

Phase 1237 Fix1–Fix7 delivered a complete, tested sidecar query library
(`ilc_core/graph/sidecar_query_runtime.py`, 100+ tests). The library operates
in-process over projection dicts. A running ILC node already has a FastAPI HTTP
server (`ilc_core/server.py`, uvicorn on port 8000) and two ThreadingHTTPServer
transport layers (gossip Phase 568, fetch Phase 1212). **None of these currently
expose a projection endpoint.** No `/projection`, `/graph`, or `/sidecar` route
exists in `server.py` as of Phase 1237.

The missing piece is:

```text
GET /v1/graph/projection/{projection_type}
```

This endpoint calls `project_graph()` and returns canonical JSON. The sidecar
query runtime then operates on that output client-side or in-process.

**Why gated on CDL-087:** CDL-087 (Canonical Fetch Distribution Policy) governs
how canonical graph content is distributed to consumers. Wiring a projection
endpoint before ratification bypasses the governance process. CDL-087 ratification
requires SIM-FETCH-01 evidence (Phase 1238) and is Window 1241+ at earliest.

**Additional prerequisites before implementation:**
- CDL-087 ratified
- Authentication policy authorized (not yet)
- TransportPrincipal public-path authentication defined; projection serving must not rely on raw IP
  or JSON/body requester identifiers
- Rate limiting plan confirmed (can reuse `persistent_fetch_rate_limiter_runtime`
  pattern)
- Privacy filter for serving-peer identity aggregation (sidecar spec §3)

**Implementation prompt:** `docs/antigravity_tasks/antigravity_prompt__phase_1237_fix8_g8_sidecar_projection_endpoint_planning.md`

This is a **SENSITIVE** implementation phase when it executes — `server.py` is a
protocol surface. Phase number to be assigned in the window guidance doc for the
window in which CDL-087 ratification lands.

Additional token:
- `sidecar_projection_endpoint_public_path_requires_transport_principal_auth`

### Gap 10 — Transport Principal Identity Layer

**Status:** Not yet started. Pre-public-P2P hard requirement.
**Recorded:** Phase 1238 (2026-05-07 Codex synthesis + Gemini review).

The repo currently lacks a dedicated `TransportPrincipal` identity layer. The four-level key
ladder (`AgentID` / BLS validator / Ed25519 enrollment / `TransportPrincipal`) has the
transport layer missing. Consequences:

- `PersistentFetchRateLimiter` keys on `client_ip` (fetch) — IP addresses are shared, dynamic,
  and cheap to rotate. Not sufficient for a public adversarial network.
- Gossip envelope `peer_id` is `ValidatorID(u32)` — no cryptographic authentication at the
  D2D message level.
- There is no mechanism to locally ban a spamming/adversarial peer by cryptographic identity
  costing reputation/stake.

`TransportPrincipal` requirements:
- Short-lived or rotating; cannot be freely rotated at zero cost (must be bounded by admission or
  stake)
- Does not reveal agent economic position at connection time (sealed-sender/privacy requirement)
- Not equal to AgentID — `agent_id_must_not_be_default_transport_rate_limit_key`
- Has explicit issuance, epoch rotation, revocation, local-ban persistence, replay prevention, and
  privacy-preserving admission/stake binding semantics
- CDL required before runtime implementation

The Rust QUIC layer (`ilc_consensus/src/network.rs`) already uses Quinn + rustls/TLS 1.3 with
pinned cert verification. The Python `ThreadingHTTPServer` layers should be formally downgraded
to devnet/test classification once the Rust P2P transport lane covers D2D.
An ADR must decide whether the public P2P substrate extends Quinn/rustls, adopts libp2p, or
defines an adapter boundary supporting both.

Carry-forward tokens (all open):
- `transport_principal_identity_required_before_public_p2p`
- `d2d_rate_limiter_key_must_be_authenticated_transport_principal`
- `agent_id_must_not_be_default_transport_rate_limit_key`
- `json_requester_id_rate_limit_fallback_forbidden_public_p2p`
- `transport_principal_cdl_required_before_runtime_implementation`
- `transport_principal_lifecycle_and_revocation_spec_required`
- `python_http_transport_formally_downgraded_to_devnet_test_only_required`
- `rust_public_p2p_transport_lane_required_before_public_p2p`
- `rust_p2p_substrate_decision_adr_required_quinn_vs_libp2p`

Forward-planning spec: `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` §2.

### Gap 11 — Werner Topological Flow Governor

**Status:** Forward planning recorded. Not yet in simulation. No CDL open. Pre-public-P2P item.
**Recorded:** Phase 1238 (2026-05-07 Codex synthesis).

The Werner φ-bound (CDL-085) already governs provenance-edge mint suppression. The
`routing_reputation_runtime.py` (CDL-078) already rewards useful serving. These are the
building blocks. What does not yet exist is a bidirectional topology-aware control layer that:
- Constructs a heat vector over shard/peer topology from serve pressure, cache miss rate, and
  circuit breaker activations
- Runs primal/dual Laplacian smoothing over the network topology graph
- Produces cooling signals (suppress unproductive amplification) AND heating signals (attract
  capacity to underconnected high-demand regions)
- Feeds ECU bounties and credit budgets where productive work demand is verified

This is NOT a per-request ECU micropayment system. `no_per_hop_ecu_micropayment_for_fetch_relay_preserved`.
The CDL-078 reputation-implicit relay incentive is preserved.

Sequencing: SIM-FETCH-01 overlay first (Phase 1238 Fix series), then CDL, then runtime.
The existing `laplacian_analytics.py` provides the Laplacian infrastructure. The dual graph
extension (flows/edges as dual nodes: fetch streams, provenance paths, cache-mirror
relationships) requires a new analysis module.

Carry-forward tokens (all open):
- `werner_topological_flow_governor_forward_planning_recorded_phase_1238`
- `werner_flow_governor_overlay_required_for_sim_fetch_01`
- `server_shard_credit_flow_governor_required_pre_public_p2p`
- `flow_governor_cdl_required_before_runtime_policy_deployment`
- `beta_decomposition_required_before_policy_use`
- `flow_governor_spectral_trust_threshold_required_before_policy_use`
- `heat_signal_must_not_directly_mint_ecu`

Forward-planning spec: `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` §3.

### Gap 12 — ECU Credit Creation in Agentic Wallet

**Status:** Wallet is read-only (Phase 576 boundary). Pre-public-launch hard requirement.
**Recorded:** Phase 1238 (2026-05-07 Codex synthesis).

The current wallet (`economic_cycle_runtime.py`) provides visibility and accounting only. It
cannot originate credit creation, accept a Werner work advance, sign spend or escrow actions, or
manage active productive-credit lifecycle state.

The complete ECU credit creation path requires:
- `ECUCreditCreationIntent` — wallet-side request object with work commitment, demand signal,
  authorization evidence, and repayment path
- Werner productive credit authorization CDL — governing rules for what work justifies credit
- Exposure ceilings — per-agent, per-shard, per-epoch, global outstanding credit cap
- Escrow and clawback mechanics — failed commitments cancel credit without socializing loss
- Separate wallet signing keys — identity / transfer / productive-credit-intent / recovery
- Consensus-epoch-settled creation — ECU creation through Rust epoch authority, not Python
  wallet mutation

**Hard invariant:** the wallet requests or signs ECU creation; it does not create ECU itself.

Carry-forward tokens (all open):
- `agentic_wallet_ecu_credit_creation_runtime_required_pre_public_launch`
- `ecu_credit_creation_intent_cdl_required`
- `werner_productive_credit_authorization_cdl_required`
- `ecu_credit_creation_must_be_consensus_epoch_settled_not_wallet_mutation`
- `wallet_signing_spend_transfer_claimability_boundary_required`

Forward-planning spec: `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` §4.

### Gap 13 — ECU-to-ILC Settlement Execution Runtime

**Status:** CDL-048 ratified mandatory conversion; no production conversion runtime exists.
Pre-public-launch hard requirement.
**Recorded:** Phase 1238 (2026-05-07 Codex synthesis).

CDL-048 ratifies a mandatory ECU conversion deadline of 4 issuance epochs. The `balance_ilc`
field exists in RC wallet state but is internal bookkeeping only. No production conversion
runtime, P_e fixed-point governor, mandatory sweeper, or public claimability state machine exists.

**Scope split (important):** Two components must NOT be conflated:

1. **Conversion mechanism** (internal bookkeeping) — eligible ECU → ILC at `P_e`, epoch-settled.
   Can be built pre-launch without resolving public substrate. Should be on testnet before launch
   to prove the economic model.

2. **Public claimability substrate** (governance decision) — what chain/mechanism allows humans
   to withdraw/claim ILC. Requires separate deliberation. Blocks public launch but NOT internal
   testnet readiness.

Required for conversion mechanism:
- Production conversion runtime (Rust epoch-settled, Decimal/fixed-point `P_e`)
- Mandatory conversion sweeper enforcing CDL-048 deadline
- ECU lot accounting for issue epoch, origin, funding provenance, deadline, and conversion status
- ILC issuance budget accounting (total budget, emitted per epoch, taper/long-tail)
- Claimability state machine with machine-verifiable receipts

Carry-forward tokens (all open):
- `ecu_to_ilc_conversion_execution_runtime_required_pre_public_launch`
- `pe_governor_fixed_point_runtime_required_pre_public_launch`
- `mandatory_conversion_sweeper_required_for_cdl_048_runtime`
- `ecu_lot_accounting_required_for_cdl_048_conversion_sweeper`
- `ilc_public_claimability_substrate_required_pre_public_launch`
- `ilc_public_claimability_substrate_does_not_block_internal_conversion_runtime`

Forward-planning spec: `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` §4.

### Gap 14 — OpenClaw/NemoClaw Package Modularity and CLI/Sidecar Boundary

**Status:** Forward planning recorded. Required if ILC Core launches first as an agentic
harness package/skill.
**Recorded:** Phase 1238 (2026-05-07 Codex synthesis + Gemini follow-up).

OpenClaw/NemoClaw is best treated as an onboarding/orchestration harness, not ILC's base protocol
transport. If ILC Core ships as a skill/package inside such a harness, the monorepo must expose
clean package boundaries:

- Rust consensus core: cryptography, quorum/finality verification, fixed-point ECU primitives,
  settlement math.
- Rust node transport lane: public P2P/admission/rate limiting where hostile-network exposure
  exists.
- Python `ilc_logic`: epistemic rules, projections, attribution logic, `commit.epoch`
  projection/adaptation surfaces; no public transport/storage dependency.
- Python `ilc_cli`: terminal UX and subprocess-compatible entrypoint; no protocol law.
- Harness adapters: OpenClaw/NemoClaw skills and sidecar apps implementing explicit
  `TransportHarness` and `StorageHarness` interfaces.

`commit.epoch` remains split: canonical event/projection semantics live in Python logic, while
quorum/finality verification and epoch settlement authority remain Rust. The CLI or node runtime
may trigger commit execution, but may not redefine event semantics. Any trigger path must use
ratified epoch/sequence inputs, not OS wall clock time, for protocol liveness or settlement
semantics.

The Rust/Python boundary requires an explicit binding plan before OpenClaw/NemoClaw skill launch.
If Python imports Rust consensus primitives directly, the implementing phase must document the PyO3
or equivalent FFI surface separately from the public P2P substrate decision. Harness adapters must
also remain generic and dependency-isolated: OpenClaw/NemoClaw are first target harnesses, not the
only acceptable harnesses, and their dependency graph must not leak into pure `ilc_logic` or Rust
consensus core packages.

Measured LOC baseline as of 2026-05-07: tracked repository files are approximately 852k lines;
tracked Python+Rust are approximately 276k lines. Public launch package size must be measured from
the selected packaging profile, not inferred from monorepo LOC.

Carry-forward tokens (all open):
- `ilc_package_modularity_split_required_before_openclaw_skill_launch`
- `ilc_logic_pure_protocol_interfaces_required`
- `ilc_logic_must_not_require_http_lmdb_or_harness_transport`
- `ilc_cli_package_boundary_required`
- `pyo3_binding_plan_required_for_ilc_consensus_core`
- `commit_epoch_boundary_split_python_projection_rust_finality_required`
- `commit_epoch_trigger_must_use_epoch_sequence_not_wall_clock`
- `openclaw_nemoclaw_adapter_must_be_sidecar_or_cli_not_protocol_substrate`
- `harness_adapter_transport_storage_protocols_required`
- `generic_agent_harness_adapter_contract_required`
- `localhost_sidecar_api_must_remain_loopback_or_transport_principal_auth`
- `sidecar_dependency_isolation_required_for_harness_adapters`
- `line_count_baseline_must_be_measured_not_estimated_before_public_rc`
- `public_package_size_audit_required_before_openclaw_skill_launch`

Forward-planning spec: `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` §2.7.

---

### Gap 8 — Long-Range Economic and Scale Work

**Status:** Deferred.

- Multi-hop centrality attribution CDL — research evidence exists; CDL not opened.
- Cross-epoch compaction / snapshot export — required before network-scale operation.
- CDL-070 PQ migration ceremony — SIM-MONETARY-01 prerequisite.
- **Reputation/centrality float surface migration** — `temporal_decay_runtime.py`,
  `centrality_delta_gossip_runtime.py`, and `routing_reputation_runtime.py` use `float`
  internally for score arithmetic. Not on critical economic settlement path but should
  migrate to `Decimal` before public RC. No window assigned.
- **Dynamic Epistemic Traversal Engine** — versioned path-activation runtime composing
  decay, centrality, refutation, reputation, and projection context. Biologically-inspired
  nonlinear dynamics layer. Forward-planning spec recorded Phase 1233-1240; earliest
  implementation Window 1241+. See
  `docs/specs/ilc_dynamic_epistemic_traversal_engine_forward_planning_1241_v0.1.md`.
  Token: `dynamic_epistemic_traversal_engine_forward_planning_recorded_phase_1233_1240`.
  Must not precede Phase 1236/1237/1238. v0.1 is read-only evaluation only; routing and
  settlement wiring require separate CDL openings.
- **TLA+/TLC formal verification track** — three specs already verified (Spec A DAG
  Liveness MaxRound=12, Spec B `SafetyNoDualCert` ECU transfer, Spec C partition/heal
  Phase 818). One pre-RC item: TLA+ refinement notes bridging abstract model to Rust
  implementation (`tla_refinement_notes_pre_rc`; NON-SENSITIVE, hours, Window 1241+
  tail slot). Post-launch items: Spec D EpochSettlementTx shared-object model
  (`tla_spec_d_epoch_settlement_complete`), TLAPS unbounded liveness proof
  (`tla_tlaps_unbounded_liveness_post_launch`), economic protocol specs
  (`tla_economic_protocol_specs_post_launch`). Forward-planning doc recorded Phase
  1233-1240: `docs/specs/ilc_tla_plus_formal_verification_forward_planning_v0.1.md`.
  Token: `tla_formal_verification_forward_planning_recorded_phase_1233_1240`.

---

## 5. Window 1191-1199 Execution Policy

The following policy answers the open decisions raised during Phase 1192:

| Question | Default for this window |
|----------|-------------------------|
| v0.2 signing authorization | Not issued as of Phase 1192; Phase 1193 skips unless the explicit token is provided before execution |
| Phase 1195 scope vs implementation | Scope-first; bounded implementation allowed only if small, unambiguous, and testable |
| Phase 1197 conditionality | Treat as firm-if-reached; defer only if prior phases expand unexpectedly |

Sensitive gates remain unchanged:

- Phase 1193 requires signing authorization and `GO Phase 1193`.
- Phase 1194 requires `GO Phase 1194` plus CDL mutation environment.
- Phase 1199 requires `GO Phase 1199`.

---

## 6. Layered Network Delivery Architecture

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| L1 | Announcement gossip — soft push-signal | CDL-076 | **Ratified** |
| L2 | WANT-HAVE/WANT-BLOCK two-phase fetch; rate limiting | CDL-077 | **Ratified** |
| L3 | star.map N-gram route index; spectral routing | CDL-079, CDL-080 | **Ratified** |
| L4 | Onion routing + SURB reply envelopes | Future CDL | H-series designed; not wired |
| L5 | Relay incentives; centrality attribution; provenance attribution | CDL-078, CDL-081, CDL-084, CDL-085 | **Ratified where opened** |

---

## 7. Relationship to Current Canon

| Artifact | Path | Role |
|----------|------|------|
| Capsule v5.44 | `docs/specs/ilc_antigravity_context_capsule_v5.44.md` | Current frontier capsule until Phase 1198 |
| Window 1183-1190 handoff | `docs/specs/ilc_window_1183_1190_handoff_1190_v0.1.md` | Incoming handoff for Window 1191-1199 |
| Window 1191-1199 sequence lock | `docs/specs/ilc_phase_1191_1199_sequence_lock_v0.1.md` | Active sequence lock |
| CDL master log | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | Authoritative CDL status |
| ADR-0037 | `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` | Accepted; lineage/equivalence/merge governance |
| ADR-0036 | `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md` | Accepted; release key mechanism |
| SIM-SPECTRAL-05 disposition | `docs/sims/sim_spectral_05/disposition_1171_v0.1.md` | Gate pass evidence |
| SIM runtime-binding slice | `docs/sims/sim_spectral_05/runtime_binding_slice_disposition_1179_v0.1.md` | Observer slice pass |
| SIM economic-flow slice | `docs/sims/sim_spectral_05/economic_flow_slice_disposition_1180_v0.1.md` | Observer slice pass |
| SIM gossip slice | `docs/sims/sim_spectral_05/gossip_slice_disposition_1187_v0.1.md` | Observer slice pass |
| Phase 1188 scoping | `docs/specs/ilc_cdl_001_genesis_blocker_scoping_1188_v0.1.md` | Fresh-CDL packaging-blocker routing |

---

## 8. What This Roadmap Does NOT Claim

- v0.2 Atlas signing ceremony executed.
- Any release key generated or registered in Window 1191-1199 so far.
- CDL-086 ratified.
- Any public launch claim.
- Any public repository publication.
- Counsel track completion.
- Tier-3 runtime linkage implemented.
- Persistent rate limiter completed.
- Truth-primitive permanence ratified by community governance.
