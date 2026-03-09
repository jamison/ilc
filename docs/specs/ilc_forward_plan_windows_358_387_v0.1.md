# ILC Forward Plan: Windows 358-387 v0.1

**Status:** Non-normative planning artifact — for review and operational feedback, not ratification
**Date:** 2026-03-05
**Phase:** 357 (post-Window 348-357 closure; pre-Window 358 sequence-lock drafting)
**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Purpose:** Provide a three-window forward plan covering runtime implementation of the ratified node-schema stack (CDL-034–038), V-series enforcement implementation, simulation commissioning, and the first wave of constitutional gap closures identified in `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`. This document is intended for review by both the local architectural reviewer (Sonnet) and the executor (Codex) before the Window 358 sequence lock is drafted.

**Companion documents:**
- `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md` — gap analysis, known unknowns, unknown unknowns, SIM-001 through SIM-007 proposals
- `docs/specs/ilc_cdl_dependency_graph_v0.1.md` — CDL ratification and dependency topology
- `docs/specs/ilc_window_348_357_handoff_357_v0.1.md` — Phase 357 handoff baseline
- `docs/specs/ilc_node_schema_implementation_readiness_356_v0.1.md` — per-CDL implementation prerequisites

---

## 1. Entry state and authorization baseline

This plan begins from the following confirmed state at Window 348-357 close (Phase 357):

- `CDL-034` through `CDL-038` are ratified (Phases 349-353).
- ADM-003 7+1 evaluation panel behavioral role is resolved (Phase 354).
- Capsule v1.0 is published and self-contained (Phase 355).
- Implementation-readiness prerequisites are mapped per CDL (Phase 356).
- Window 358+ is authorized to begin runtime implementation of ratified CDL-034 through CDL-038 surfaces.
- Unratified surfaces remain implementation-barred.
- Implementation ordering in Window 358+ must mirror the ratified dependency chain: `CDL-034 -> CDL-035 -> CDL-036 -> CDL-037 -> CDL-038`.

Implementation of V-series enforcement (CDL-V1 through CDL-V7) is not explicitly authorized by Phase 357. Whether V-series runtime work enters Window 358-367 must be decided explicitly in the Phase 358 sequence lock. Until that lock states otherwise, Window 358+ implementation authorization remains bounded to ratified `CDL-034` through `CDL-038` surfaces.

---

## 2. Planning horizon and structure

Three windows are planned here:

| Window | Phases | Primary theme | Planning confidence |
|---|---|---|---|
| 358-367 | 358–367 | Node schema runtime implementation + SIM commissioning | HIGH — concrete deliverables from ratified CDLs |
| 368-377 | 368–377 | V-series enforcement + P2P constitutional opening | MEDIUM — depends on Window 358-367 outcomes |
| 378-387 | 378–387 | P2P ratification + shard/storage CDL cluster + Agent SDK/CLI | LOW — depends on SIM results and CDL-039+ progress |

Windows 368+ are intentionally sketch-level. They will be hardened into sequence locks as each prior window closes and SIM results are available.

---

## 3. Window 358-367: Node schema runtime implementation and SIM commissioning

### 3.1 Window character

Window 358-367 is the first implementation window after the constitutional ratification program. It transitions from document-only phases to `ilc_core/` runtime work. The first five implementation phases (359-363) are structurally analogous to Phases 310/312/314 (schema/genesis/epoch runtimes) — each produces a standalone runtime module under `ilc_core/`, a full test suite, and a CDL dependency token.

Phases 364-366 are non-sensitive planning and analysis phases. Phase 365 is novel: it commissions Codex to implement Python simulations from fully specified briefs, using the executor role to reduce epistemic uncertainty rather than to implement protocol features.

### 3.2 Phase table

| Order | Phase | Track | Scope | Sensitivity |
|---|---|---|---|---|
| 1 | **Phase 358** | Sequence lock + roadmap | Lock 358-367 ordering, implementation authorization carry-forward, runtime module naming conventions, V-series enforcement authorization scope; produce roadmap v0.4 | Non-sensitive |
| 2 | **Phase 359** | CDL-039 opening | CDL-039 row opening (additive-only, no prelock): P2P transport baseline, no-central-broker invariant, gossip topology privacy design requirements carried as open constraints | Sensitive |
| 3 | **Phase 360** | Runtime implementation | CDL-034: node envelope parser, reserved-field enforcement, three-envelope split runtime | Sensitive |
| 4 | **Phase 361** | Runtime implementation | CDL-035: validation_state machine runtime, gate_verdict reference, quarantine-state handling | Sensitive |
| 5 | **Phase 362** | Runtime implementation | CDL-036: header-first dissemination runtime, CID pull fetch, signature scope enforcement | Sensitive |
| 6 | **Phase 363** | Runtime implementation | CDL-037: executable descriptor parsing, sandboxed runtime binding stub, safety-contract verification | Sensitive |
| 7 | **Phase 364** | Runtime implementation | CDL-038: promotion_receipt handler, successor-node flow, no-carry-forward enforcement | Sensitive |
| 8 | **Phase 365** | SIM commissioning | Codex implements SIM-001 + SIM-002 + SIM-003 per exact briefs in the gap analysis document; outputs committed as reproducible Python with deterministic seeds, CSV/TSV results, summary tables, and run manifests | Non-sensitive |
| 9 | **Phase 366** | Coherence + capsule v1.1 | Coherence report covering Phases 360-364 implementation status, SIM-001/002/003 results and their implications, gap analysis document carry-forward, capsule update | Non-sensitive |
| 10 | **Phase 367** | Closure | Window 358-367 closure gate and 368+ handoff | Sensitive |

### 3.3 Per-phase notes

**Phase 358 — Sequence lock + roadmap v0.4:**
- Must explicitly carry forward Phase 357's implementation authorization and dependency chain.
- Must define the runtime module naming convention for node-schema runtimes (e.g., `ilc_core/node/node_schema_runtime_360.py` or similar pattern consistent with `d2_schema_baseline_runtime.py`).
- Must address whether V-series enforcement implementations (CDL-V1 through CDL-V7) are authorized in this window or deferred to Window 368-377.
- Must address runtime mutation scope: the `_assert_runtime_mutation_scope` pattern (NOT `assert_head_commit_touched_no_runtime_files`) is required for all five implementation phases.
- Roadmap v0.4 is produced as part of this phase. Supersedes v0.3. Must add: node schema implementation track, V-series enforcement track, SIM track, P2P CDL cluster (CDL-039+), ADM-004 lane, 1000-series remediation phases (1000-1014 complete), and Phase 262 signing-provider interface. Must mark v0.3 items that are now complete (D1, D2, D2b, D2c) and items with only constitutional completion but no runtime (D2d, D2e). Must include a revised dependency graph reflecting Window 358+ implementation phases.

**Phase 359 — CDL-039 row opening:**
- Additive-only CDL action. Commits `CDL-039` row with `status: open`. Creates prelock artifact placeholder. No prelock design is finalized in this phase.
- The three gossip topology privacy constraints (from gap analysis KU-1 extension) must appear in the prelock artifact as open design requirements, not as locked invariants: (a) agent public identifiers must be topology-opaque; (b) cluster membership comparison must not be derivable from public protocol data; (c) COSE `kid` must be a protocol-internal opaque identifier (already captured in `ilc_signing_provider_interface_262_v0.1.md`; must be explicitly cross-referenced in the CDL-039 prelock artifact).
- Prelock design will be finalized in Phase 374 after SIM-004 (partition divergence) and SIM-005 (epoch timing attack surface) results are available.
- Uses three-path commit resolver: CDL + prelock artifact + new test file.
- Sensitivity: SENSITIVE (CDL status mutation).

**Phases 360-364 — Node schema runtimes:**
- Each follows the Phase 310/312/314 pattern: standalone `ilc_core/` module, CDL dependency token exported, version string, full test suite (target 8-14 tests each).
- Phase 360 = CDL-034, Phase 361 = CDL-035, Phase 362 = CDL-036, Phase 363 = CDL-037, Phase 364 = CDL-038.
- Each must assert the prior CDL dependency tokens from the phases below it in the dependency chain (`CDL-034 -> CDL-035 -> ... -> CDL-038`).
- The `assert_head_commit_touched_no_runtime_files` guardrail is an ANTI-PATTERN here. Use `_assert_runtime_mutation_scope(commit_ref)` instead.
- Forbidden `ilc_core/` prefixes (must not be modified): `consensus/`, `security/`, `ledger/`, `issuance/`, `genesis/`, `epoch/`, `d2e/`, `cli/`.
- Allowed `ilc_core/` targets per Phase 356: `node/node_v0.py`, `schema/d2_schema_baseline_runtime.py`, `protocol/schema.py`, `network/gossip.py`, `network/peer.py`, `network/wire_transport_runtime.py`, `analysis/agent_profiles.py`.

**Phase 365 — SIM commissioning:**
- This is a new phase type: Codex as simulation engineer rather than constitutional executor.
- Codex must implement three Python simulations per the exact briefs in Section 5 of `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`:
  - **SIM-001:** Bootstrap threshold analysis (CDL-V1/V2 effectiveness vs. network size).
  - **SIM-002:** Micro-agent cost-floor model (participation economics).
  - **SIM-003:** Graph growth and storage pressure.
- Each simulation: Python module with deterministic seed, parameterized inputs, CSV output, plain-text summary table.
- Output files committed under `out/simulations/sim_001_bootstrap_threshold/`, `out/simulations/sim_002_micro_agent_economics/`, `out/simulations/sim_003_graph_growth/`.
- Output constraints: text formats only (`.py`, `.md`, `.csv`, `.tsv`, `.json`), deterministic run manifest per simulation, no notebook artifacts, and no single result file larger than 10 MB.
- No `ilc_core/` changes. No CDL mutations. No ratification.
- Results are returned to the architectural reviewer (this conversation) for interpretation in Phase 366.

**Phase 366 — Coherence + capsule v1.1:**
- Coherence report covers the implementation status of CDL-034–038 runtimes.
- Must incorporate SIM-001/002/003 results with interpretation:
  - What threshold does SIM-001 establish for launch readiness?
  - What constitutional bound does SIM-002 recommend for write_fee_multiplier?
  - What pruning policy does SIM-003 recommend?
- Gap analysis document (`ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`) is carried forward as an open planning artifact.
- Capsule v1.1 is self-contained, not delta-only.
- Capsule v1.1 must explicitly state the wallet-agnostic strategic principle: "ILC co-opts existing wallet trust rather than building competing wallet infrastructure." This principle is implemented in `ilc_signing_provider_interface_262_v0.1.md` and the Phase 262 SDK boundary contract amendments, but does not appear in capsule v1.0. Capsule v1.1 should include it in the signing/identity section.

### 3.4 Pre-commit split expectations for Phases 360-364

Each implementation phase should follow the Phase 310/312/314 pre-commit split pattern:
- Before commit: non-commit-anchored tests pass; commit-anchored tests fail with `phase_NNN_commit_not_present_in_local_history`.
- After commit: all tests pass.
- Expected pre-commit split for each: approximately 7-9 passed / 2 failed (the two commit-anchored guard tests).

Phase 359 (CDL-039 row opening) follows the additive-only CDL pattern (Phases 340-344): 5+2 pre-commit split, three-path commit resolver, direct dict equality for pre-existing row shield.

---

## 4. Window 368-377: V-series enforcement and P2P constitutional opening (sketch)

### 4.1 Window character

Window 368-377 implements the enforcement runtimes for the four most technically tractable V-series CDLs and opens the P2P constitutional track. The P2P CDL opening (CDL-039) begins the process of constitutionally guarding the distributed architecture — the highest-priority known unknown from the gap analysis.

SIM-004 and SIM-005 are commissioned in this window, and their interpreted outputs must feed the CDL-039 prelock design before that prelock is finalized.

### 4.2 Phase table (sketch)

| Order | Phase | Track | Scope | Sensitivity |
|---|---|---|---|---|
| 1 | **Phase 368** | Sequence lock | Lock 368-377 ordering; carry forward from Phase 367 implementation authorization | Non-sensitive |
| 2 | **Phase 369** | Runtime implementation | CDL-V1: temporal decay enforcement runtime; half-life decay formula; integration with ECU scoring module | Sensitive |
| 3 | **Phase 370** | Runtime implementation | CDL-V2: sybil resistance enforcement runtime; hybrid heuristic resistance mechanism | Sensitive |
| 4 | **Phase 371** | Runtime implementation | CDL-V3: quorum diversity enforcement; cluster diversity floor; independence_k=3 enforcement | Sensitive |
| 5 | **Phase 372** | Runtime implementation | CDL-V7: Popperian gate enforcement; basic-statement falsifiability check integration | Sensitive |
| 6 | **Phase 373** | SIM commissioning | Codex implements SIM-004 (network partition divergence) + SIM-005 (epoch timing attack surface); results returned for interpretation | Non-sensitive |
| 7 | **Phase 374** | CDL-039 prelock | P2P transport baseline prelock: no-central-broker invariant; anchored to ADR-0011; evidence artifact drafted | Sensitive |
| 8 | **Phase 375** | ADM-004 draft | Software upgrade governance ADM: content-addressed upgrades, no trusted update server requirement, CDL-V7 gate for adoption | Non-sensitive |
| 9 | **Phase 376** | Coherence + capsule v1.2 | V-series enforcement status; P2P constitutional opening; SIM-004/005 results and CDL-039 prelock evidence | Non-sensitive |
| 10 | **Phase 377** | Closure | Window 368-377 closure gate and 378+ handoff | Sensitive |

### 4.3 Key decision points before drafting Window 368 sequence lock

1. **V-series enforcement scope:** CDL-V4 (reopening protocol) and CDL-V6 (Genesis intervention) have governance-process semantics, not purely computational semantics — their "enforcement" is procedural rather than a runtime module. The Window 368 sequence lock must decide which V-series CDLs get runtime modules vs. which are document-only governance enforcement. CDL-V1, CDL-V2, CDL-V3, CDL-V7 are computational and should have runtime modules. CDL-V4, CDL-V5, CDL-V6 may not.

2. **CDL-039 prelock design:** SIM-004 results (partition divergence) and SIM-005 results (epoch timing attack surface) should be available before the CDL-039 prelock is finalized, since those results inform the no-central-broker invariant's specific requirements. Window 368 should treat Phase 373 simulation output as a hard input to the Phase 374 prelock. If results are not usable by Phase 374, defer CDL-039 prelock by one phase rather than ratifying against incomplete evidence.

3. **ADM-004 scope:** Software upgrade governance is an architectural memo, not a CDL. It should define the content-addressed upgrade model but explicitly reserve constitutional ratification of specific upgrade mechanisms to a future CDL lane.

---

## 5. Window 378-387: P2P ratification, shard/storage CDL cluster, Agent SDK/CLI (sketch)

### 5.1 Window character

Window 378-387 ratifies the P2P transport CDL (CDL-039) based on the prelock from Phase 374, opens the shard lifecycle and storage economics CDLs (CDL-041 and CDL-043), and begins the long-deferred D2e Agent SDK/CLI implementation track. This window is the most speculative of the three — its exact shape depends heavily on SIM-001/002/003 results and Codex's operational review feedback.

SIM-006 and SIM-007 are commissioned here, with results feeding CDL-V7 capability extensions and wire protocol specs.

### 5.2 Phase table (sketch)

| Order | Phase | Track | Scope | Sensitivity |
|---|---|---|---|---|
| 1 | **Phase 378** | Sequence lock | Lock 378-387 ordering | Non-sensitive |
| 2 | **Phase 379** | Ratification | CDL-039: P2P transport baseline ratification (from Phase 374 prelock) | Sensitive |
| 3 | **Phase 380** | CDL prelock | CDL-040: admission control + identity envelope; anchored to ADR-0014 | Sensitive |
| 4 | **Phase 381** | CDL prelock | CDL-041: shard lifecycle operations; no-central-authority constraint; CDL-V3 diversity required for shard creation | Sensitive |
| 5 | **Phase 382** | CDL prelock | CDL-043: graph pruning and storage economics; SIM-003 outputs authoritative for prelock evidence | Sensitive |
| 6 | **Phase 383** | SIM commissioning | Codex implements SIM-006 (panel effectiveness under capability heterogeneity) + SIM-007 (agent churn and orphan accumulation); results returned | Non-sensitive |
| 7 | **Phase 384** | Runtime implementation | D2e Agent SDK/CLI — Part 1: D2e-01 through D2e-05 (identity, query, verify subsystems) | Sensitive |
| 8 | **Phase 385** | Runtime implementation | D2e Agent SDK/CLI — Part 2: D2e-06 through D2e-11 (bundle, epoch, balance, integration test) | Sensitive |
| 9 | **Phase 386** | Coherence + capsule v1.3 | P2P/shard CDL openings; SIM-006/007 results; D2e implementation status | Non-sensitive |
| 10 | **Phase 387** | Closure | Window 378-387 closure gate and 388+ handoff | Sensitive |

### 5.3 Key open questions for Window 378-387 design

1. **CDL-039 ratification prerequisites:** The Phase 379 ratification requires the full evidence prelock (Phase 374) plus validation that the no-central-broker invariant is testable against the existing `ilc_core/network/` stub. If the stub doesn't provide enough surface to test against, the ratification may need a companion runtime phase.

2. **D2e readiness:** The D2e Agent SDK/CLI (CDL-032, ratified Phase 253) has been deferred since Phase 253. The node schema runtimes (Phases 359-363) and wire transport runtime (Phase 323) are prerequisites before D2e can be meaningfully built. Phases 384-385 should be gated on Phases 359-363 being complete and stable.

3. **SIM-006 dependency:** SIM-006 (panel effectiveness under capability heterogeneity) requires the `capability_vector` vocabulary to be at least partially defined before meaningful simulation inputs can be set. If the vocabulary isn't defined by Window 378, SIM-006 may need to be deferred or parameterized with placeholder capability tiers.

---

## 6. Codex engagement strategy for planning review

### 6.1 Rationale

The architectural reviewer (Sonnet) designs plans and interprets results. Codex executes implementation. For planning documents, Codex's operational knowledge — what was hard, what was underspecified, what took unexpected effort — adds a dimension that pure architectural reasoning cannot. This section defines how to use Codex as a planning reviewer.

### 6.2 Phase 358 pre-lock review request

Before drafting the Phase 358 sequence lock, route this document and the gap analysis document (`ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`) to Codex with the following specific questions:

**Q1 — Implementation phase scoping:** Are the Phase 359-363 scopes (one CDL per phase) correctly sized, or should any be split across two phases? Which CDL runtime is likely to be most complex given the current `ilc_core/` module structure?

**Q2 — SIM-001/002/003 implementability:** Reading Section 5 of the gap analysis document, are the three High-ease simulations (SIM-001, SIM-002, SIM-003) implementable from the existing simulation infrastructure without requiring changes to `ilc_core/`? Flag any input parameter that does not have a ratified value source (e.g., `lambda` from CDL-V1 — where exactly is this value in the codebase?).

**Q3 — Module target correctness:** The Phase 356 readiness document lists `ilc_core/node/node_v0.py`, `ilc_core/schema/d2_schema_baseline_runtime.py`, `ilc_core/protocol/schema.py`, and network/security targets. Are these the correct module targets given the current `ilc_core/` layout? Are any targets stale or renamed since Phase 356 was written?

**Q4 — V-series enforcement authorization:** The gap analysis notes that CDL-V4, CDL-V5, and CDL-V6 have procedural rather than computational semantics. From an implementation standpoint, do CDL-V1, CDL-V2, CDL-V3, and CDL-V7 have clear enough computational definitions to produce runtime modules in Window 368-377, or do any require further constitutional specification before implementation?

**Q5 — Roadmap v0.4 scope:** What should be added or removed from the v0.3 roadmap task list to reflect the current state? Specifically: which of the 73 original tasks are complete, which are in progress, and which are not yet started? A rough task-status audit would allow the v0.4 roadmap to be accurate rather than a forward-only append.

### 6.3 Pre-Phase-373 SIM review

Before Codex implements SIM-004 and SIM-005 (Window 368-377, Phase 373), route the SIM-004/005 briefs from the gap analysis document with this question: given the forked graph state required for SIM-004 and the parameterized temporal decay model required for SIM-005, what existing simulation code can be reused and what needs to be written from scratch?

### 6.4 Ongoing pattern

Each window's sequence lock phase (358, 368, 378) should include a Codex review of the corresponding window sketch from this document before the sequence lock is finalized. This gives Codex a voice in the planning process and surfaces execution-level constraints before they become blocking issues mid-window.

---

## 7. Simulation result handling

When Codex completes SIM implementations and commits results, the architectural reviewer (Sonnet) performs interpretation in the following cohesion window:

| SIM batch | Commissioned | Results interpreted | Feeds |
|---|---|---|---|
| SIM-001, SIM-002, SIM-003 | Phase 365 | Phase 366 coherence report | CDL-017 opening; write_fee CDL; CDL-043 pruning prelock |
| SIM-004, SIM-005 | Phase 373 | Phase 374 prelock package (carried forward in Phase 376 coherence) | CDL-039 prelock evidence; clock sync CDL design |
| SIM-006, SIM-007 | Phase 383 | Phase 386 coherence report | CDL-V7 extension; D2d-10/11 wire spec; CDL-035 timed_out extension |

Results should be committed as CSV/TSV + summary table + deterministic run manifest (not Python notebooks) so they can be referenced from ratification evidence artifacts without requiring code execution.

---

## 8. Gap analysis items not yet mapped to phases

The following items from `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md` do not yet have a phase assignment. They are deferred pending SIM results and CDL-039+ progress:

| Item | Reason for deferral | Earliest viable window |
|---|---|---|
| CDL-042: agent identity namespace | Depends on CDL-039/040 admission control scope | Window 388+ |
| CDL-045: operational emergency response | Requires SIM-005 results to calibrate thresholds (renumbered after CDL-044 retention_epochs opening in Phase 392) | Window 392+ |
| UU-1 partition semantics (CDL specification) | Requires SIM-004 results | Window 378+ |
| UU-3 clock synchronization (CDL) | Requires SIM-005 results + external VDF evaluation | Window 388+ |
| UU-8 human-agent distinction | Low priority; purely mechanism-design | Not scheduled |
| UU-11 model version drift | External dependency; not schedulable until model versioning standards exist | Not scheduled |
| CDL-017 bootstrap transition criteria | Requires SIM-001 results | Window 378+ |
| ADM-004 software upgrade governance | Phase 375 draft; ratification CDL follows in Window 388+ | Window 388+ |

---

## 9. What this document is not

- This is not a sequence lock. It does not lock execution order or phase sensitivity.
- This is not a prompt contract. No Codex execution is authorized from this document.
- This is not a ratification request. No CDL rows are opened here.
- Windows 368-387 are intentional sketches. They will be replaced by proper sequence locks as each window closes.
- This document does not authorize implementation. Implementation authorization for Window 358+ is granted only by Phase 357 closure.

---

## 10. Canonical anchors

- `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`
- `docs/specs/ilc_cdl_dependency_graph_v0.1.md`
- `docs/specs/ilc_node_schema_implementation_readiness_356_v0.1.md`
- `docs/specs/ilc_node_schema_implementation_authorization_scope_355_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_window_348_357_handoff_357_v0.1.md`
- `docs/specs/ilc_phase_348_357_sequence_lock_v0.1.md`
- `docs/adr/ADR_0011_Native_P2P_Transport_Baseline_for_Agent_Communication.md`
- `docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md`

---

*End of document.*
