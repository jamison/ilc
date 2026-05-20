# Window 1429–1458: Public RC Activation Forward Plan

**Version:** v0.1
**Drafted:** Phase 1407 fix series (2026-05-20)
**Status:** DRAFT — requires human review and GO before any phase executes
**Objective:** Close all remaining gaps for full public RC from a clean J-008 PASS at Phase 1427

---

## 1. Baseline inherited from Window 1399–1428

At Phase 1428 close, the following are in force:

| Item | State after 1428 |
|------|-----------------|
| J-008 gate | PASS — `production_jury_activation_gate_pass_phase_1427` |
| `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED` | **Still True** — explicit activation commit required post-gate |
| Soft RC eligible | `soft_rc_eligible=true` first recorded (Phase 1426) |
| CDL-001, CDL-002, CDL-007 | Ratified Phase 251 — no obligations remaining |
| CDL-053 (Werner local productive credit) | Ratified in fix series (fix2) — narrow maintenance scope only; flow-governor deferred |
| CDL-091 (jury incentive economics) | Ratified Phase 1400 |
| CDL-092 (CapProof) | Ratified Phase 1405 |
| CDL-093 (maintenance lottery pool) | Ratified Phase 1408 (Werner source, fix3-amended) |
| CDL-085 Werner φ-bound | Ratified Phase 1185 — `EDGE_MINT_PHI_BOUND = Decimal("0.60")` |
| CDL-086 public launch packaging | Ratified Phase 1220 — governance preconditions only |
| CDL-087 canonical fetch distribution | Ratified Phase 1278 Fix1 — public fetch/sidecar still blocked |
| CDL-088 public claimability authority | Ratified Phase 1376 — activation still blocked |
| CDL-089 blocking authority | Ratified Phase 1364 |
| CDL-090 identity bootstrap | Ratified Phase 1373 |
| VRF verifier | Implemented and integrated (Phases 1411–1413) |
| Review lane wiring | Complete (Phases 1414–1417) |
| Public economics firewall | Active (Phase 1387a) |
| Copyright counsel disposition | Genesis self-counsel recorded (Phase 1420) |
| ADR-0035 homoiconic type system | Direction accepted; implementation deferred pending CDL |
| v0.3 candidate signing | Forward obligation from Phase 1387j — deferred |
| Private soft-RC rehearsal | Entry criteria documented (Phase 1423) — execution deferred to this window |
| Public fetch serving | Blocked — TransportPrincipal policy (Gap 10) |
| Public P2P | Blocked — TransportPrincipal + Rust P2P substrate decision |
| Public claimability API | Blocked — CDL-088 activation gated (Gap 13) |
| Public repository publication | Blocked — Gap 7 (provisional patent, CLA, trademark, allowlist) |
| Production minting | Deferred post-public-RC |

**Remaining gap inventory (from roadmap v1.1):**

| Gap | Title | Blocking for |
|-----|-------|-------------|
| Gap 7 | Counsel / license / CLA / trademark / IP | Public repository publication, release signing |
| Gap 10 | TransportPrincipal + Rust P2P substrate | Public P2P, non-loopback sidecar, public fetch serving |
| Gap 13 | ECU-to-ILC claimability runtime | Public claimability API, withdrawal path |
| Gap 14 | Package modularity | OpenClaw/NemoClaw hosted public RC profile (parallel to Gap 10) |

---

## 2. Window objective

**Primary objective:** Achieve the first publicly-accessible, constitutionally-sound RC publication — an ILC node that external operators can connect to, an agent-identity ceremony that operators can run, and a claimability path that functions end-to-end.

**Three concrete deliverables that define window success:**

1. A signed, published release artifact at a public URL or repository.
2. A published `activation_certificate_v1` signed by Genesis Agent 01 triggering epoch 1.
3. At least one external operator completing the identity init ceremony and connecting to the network.

**What this window does NOT attempt:**

- Mainnet production minting or production ILC settlement (long-range).
- Full Werner flow-governor CDL (deferred — Phase 1263 decision preserved; requires additional SIM evidence).
- Resolving all of Gap 7 (US provisional patent and trademark require external counsel; this window does what is internally executable).
- CDL-031 dynamic ranking runtime (long-range; requires CDL-019 prerequisite).

---

## 3. Track inventory

| Track | Phases (approx) | Gate conditions closed |
|-------|----------------|----------------------|
| A — Production assignment activation | 1429–1430 | Flip `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED` after J-008 PASS |
| B — Private rehearsal execution | 1431–1433 | Validate 3-machine 7-agent topology before any public claim |
| C — TransportPrincipal + public path (Gap 10) | 1434–1437 | Non-loopback sidecar/projection, public fetch serving |
| D — Public claimability activation (Gap 13) | 1438–1441 | CDL-088 activation; ECU-to-ILC conversion live |
| E — ADR-0035 CDL + runtime | 1442–1444 | Homoiconic type definition system; deferred from Phase 1387d |
| F — Gap 7 internal-executable counsel milestones | 1445–1447 | License headers, CLA text, public-source allowlist audit |
| G — v0.3 signing + public RC publication | 1448–1452 | Release signing; source publication; public RC claim |
| H — Werner credit broader scope (CDL-053 follow-on) | 1453–1455 | Flow-governor CDL (conditional on SIM evidence) |
| Z — Window coherence + closure | 1456–1458 | Window closure gate |

---

## 4. Phase-level plan

### Track A — Production assignment activation (Phases 1429–1430)

**Context:** J-008 PASS at Phase 1427 is a gate verdict. Two separate source commits are required to turn production assignment on: (1) patch `jury_assignment_runtime.py` to set `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED = False`, and (2) patch `jury_activation_gate.py` if hardcoded NOT_MET conditions were not already updated in Phase 1425/1425a. These commits require explicit production activation GO tokens.

**Phase 1429 — Production assignment activation commit (SENSITIVE)**

- Explicit human `GO Phase 1429` required.
- Patch `ilc_core/epistemic/jury_assignment_runtime.py`: `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED = False`.
- Patch `ilc_core/epistemic/jury_activation_gate.py`: remove hardcoded NOT_MET tokens for conditions that Phase 1427 confirmed MET; verify verdict returns PASS after patch.
- Add production activation token: `production_assignment_activated_phase_1429`.
- Tests: gate still returns PASS; `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED = False` asserted; no epoch-hash shadow path used for high-value slots when VRF is available.
- **Pre-condition:** Phase 1427 must have returned `verdict="PASS"`.

**Phase 1430 — CDL-053 Werner local credit first wire (NON-SENSITIVE)**

- Wire `maintenance_lottery_runtime.py` (Phase 1409 stub) to the CDL-053 local credit eligibility path: eligible maintenance tasks now accumulate local credit.
- `MAINTENANCE_LOTTERY_NOT_ACTIVATED` remains `True` in the stub; this phase wires the *eligibility accounting path* only (local credit tracking), not live ECU distribution.
- Token: `cdl_053_local_credit_wired_maintenance_lottery_phase_1430`.
- ICSS §3 enforced: Decimal only; no float.
- No wallet mutation, no ECU settlement, no live draw.

---

### Track B — Private rehearsal execution (Phases 1431–1433)

**Context:** Phase 1423 (in current window) documents entry criteria. This window executes the rehearsal. This is the prerequisite validation step before any public RC claim. It is the operational proof that the 3-machine 7-agent topology cycles epochs, submits truth primitives, runs review lanes, and produces VRF-assigned jury panels correctly.

**Phase 1431 — Rehearsal agent identity ceremony (SENSITIVE)**

- Each VPS node generates its own keypair locally via ADR-0038 + ADR-0041 INIT path.
- Public identity bundles exported to Genesis. Genesis does NOT generate or distribute private keys.
- Commit: identity bundle manifest for 3 machines × 7 agents.
- Token: `rehearsal_agent_identity_ceremony_complete_phase_1431`.
- Sensitive because it creates protocol identity artifacts.
- Open question from Phase 1423 resolved here: record whether these 7 identities carry to public RC or public RC begins fresh.

**Phase 1432 — Private rehearsal execution: infrastructure validation (NON-SENSITIVE)**

- Bring up 3-machine topology: QUIC networking live, epoch cycling confirmed, L1 gossip propagation confirmed.
- Submit ~50–100 synthetic mathematical truth primitive nodes (Phase 1 dataset from Phase 1423 plan).
- T0→T0.5→T2 progression with deterministic expected outcomes.
- Run review lane: VRF-assigned jury panel for at least one T0.5 node.
- Record: epoch count, node submission count, review lane assignments, VRF proof roundtrip.
- Token: `rehearsal_infrastructure_validation_complete_phase_1432`.
- **No live LLM API during this phase.** Deterministic scripted agents only.

**Phase 1433 — Private rehearsal verdict and Phase 2 dataset (NON-SENSITIVE or conditional)**

- Introduce Phase 2 dataset: Lean Mathlib subset (PFR formalization chain or Lean 4 Mathlib ancestry). Apache 2.0 licensed.
- Run scripted agents against real-world content. Record taxonomy variety (T2/T5/T6).
- Produce rehearsal verdict: PASS (proceed to public RC track) or FAIL (remediation phases inserted before public RC claim).
- Token: `rehearsal_phase_2_complete_phase_1433`; `rehearsal_verdict=pass` or `rehearsal_verdict=remediation_required`.
- If verdict = FAIL: insert 1433a–1433n remediation phases before Track G; do not proceed to public RC claim.

---

### Track C — TransportPrincipal + public path activation (Phases 1434–1437)

**Context:** Gap 10 is the blocking condition for public P2P, non-loopback sidecar/projection, and public fetch serving. Phase 1267 implemented a pre-public TransportPrincipal helper; Phase 1277 completed a preflight. The activation CDL and runtime are not yet written.

**Phase 1434 — TransportPrincipal CDL opening and ADR (SENSITIVE)**

- Open CDL for TransportPrincipal public-path governance: defines the authenticated principal abstraction binding public HTTP/P2P/sidecar paths to agent identity (not IP, not JSON body).
- ADR: select the CDL number (next available after CDL-093 + any fix-series CDLs); defines the policy boundary between loopback-only (default) and public-path (CDL-gated).
- CDL-appropriate sensitivity: SENSITIVE because it opens a new constitutional lane.
- Token: `transport_principal_cdl_opened_phase_1434`.

**Phase 1435 — TransportPrincipal CDL prelock + ratification (SENSITIVE)**

- Deliberate and ratify the TransportPrincipal public-path governance CDL.
- Scope constants: authenticated principal required for non-loopback binding; rate-limit policy; ban/revocation integration; no IP-only authentication.
- Token: `transport_principal_cdl_ratified_phase_1435`.
- Two-commit pattern per CDL mutation protocol.

**Phase 1436 — Non-loopback sidecar/projection serving activation (NON-SENSITIVE)**

- Patch `ilc_core/` sidecar/projection runtimes to allow non-loopback binding, gated on `TRANSPORT_PRINCIPAL_CDL_RATIFIED`.
- Activate public fetch serving per CDL-087 ratification carry-forward: serving is now authorized behind TransportPrincipal policy.
- Token: `non_loopback_sidecar_projection_activated_phase_1436`.
- No wallet mutation, no ECU settlement.

**Phase 1437 — Rust P2P substrate decision and public P2P activation (SENSITIVE, conditional)**

- Resolve the deferred Quinn vs. libp2p P2P substrate decision.
- If decision is made: implement the CDL-gated Rust P2P substrate binding.
- Token: `rust_p2p_substrate_decision_recorded_phase_1437`.
- Sensitivity: conditional — constitutional if a new CDL is required for P2P governance.
- **Note:** Public P2P may be deferred beyond this window if Rust substrate work requires a separate full window. Record the deferral explicitly if so.

---

### Track D — Public claimability activation (Phases 1438–1441)

**Context:** CDL-088 (public claimability authority) was ratified Phase 1376, but activation was not authorized. Phase 1389 re-ran the claimability gate (`result=public_claimability_activated` at the governance level), but the live API is still blocked. Gap 13 requires the ECU-to-ILC conversion runtime and public verifier API to be live.

**Phase 1438 — ECU-to-ILC conversion runtime activation (SENSITIVE)**

- Activate the ECU-to-ILC conversion runtime (Phase 1274 skeleton exists as a default-off stub).
- CDL-088 activation commit: flip `PUBLIC_CLAIMABILITY_ACTIVATED = True`.
- Token: `public_claimability_activated_phase_1438`.
- Sensitive: activates a live value path.
- **Pre-condition:** CDL-088 ratified (Phase 1376 ✓), Phase 1389 gate PASS, rehearsal PASS (Phase 1433), TransportPrincipal CDL ratified (Phase 1435).

**Phase 1439 — Public verifier API activation (NON-SENSITIVE)**

- Activate the public verifier API endpoint (proof verification, ECU balance query, claim proof submission).
- Bound to TransportPrincipal authenticated principal.
- No wallet widening: claim submission accepted but wallet settlement still gated at CDL-047 treasury path.
- Token: `public_verifier_api_activated_phase_1439`.

**Phase 1440 — Claim endpoint integration tests and security review (NON-SENSITIVE)**

- Integration tests covering: valid proof → accepted; invalid proof → rejected; replay attack → rejected (nullifier); rate-limit enforcement.
- Security review: ICSS §6 (socket timeouts), ICSS §10 (bounded fetch), ICSS §2 (no PRNG), TLS verification not disabled.
- Token: `claimability_integration_tests_complete_phase_1440`.

**Phase 1441 — Gap 13 closure verdict (NON-SENSITIVE)**

- Record formal Gap 13 closure: public claimability path live, verifier API active, conversion runtime active.
- Token: `gap_13_closed_phase_1441`.

---

### Track E — ADR-0035 CDL + runtime (Phases 1442–1444)

**Context:** ADR-0035 (homoiconic type definition system) was accepted as direction in Phase 1387d but implementation was deferred pending a CDL to introduce `type="type_definition"` as a new NodeType. This is a graph-layer architectural feature, not a security-critical RC blocker — it is included here because it was a named carry-forward obligation from Phase 1387d.

**Phase 1442 — ADR-0035 CDL opening and prelock (SENSITIVE)**

- Open and prelock the CDL for `type="type_definition"` NodeType introduction.
- Scope: introduces the homoiconic type definition node; type regress stops at `type="type_definition"` (hardcoded); complements ADR-0030 content typing.
- Token: `adr_0035_cdl_opened_prelock_committed_phase_1442`.

**Phase 1443 — ADR-0035 CDL ratification (SENSITIVE)**

- Ratify the ADR-0035 CDL.
- Token: `adr_0035_cdl_ratified_phase_1443`.
- Two-commit pattern.

**Phase 1444 — ADR-0035 runtime implementation (NON-SENSITIVE)**

- Implement `type="type_definition"` NodeType in the graph store and validation layer.
- Integrate with ADR-0030 content typing.
- Token: `adr_0035_type_definition_runtime_implemented_phase_1444`.

---

### Track F — Gap 7 internal-executable counsel milestones (Phases 1445–1447)

**Context:** Gap 7 has four components. Two require external counsel or government action (US provisional patent application, trademark registration) and cannot be completed internally. Two can be completed with Genesis-authority internal action: (1) license header audit and public-source allowlist execution, (2) CLA text finalization.

This window does only the internally executable portions. External actions (provisional patent filing, trademark registration) are recorded as named carry-forward obligations for the next window, flagged to human.

**Phase 1445 — AGPL license header audit and public-source allowlist (NON-SENSITIVE)**

- Audit all source files for correct AGPL-3.0-only headers per Phase 1323 Fix3 layered license posture.
- Execute the public-source allowlist: tag every file as in-scope for publication or excluded.
- Token: `license_header_audit_complete_phase_1445`.

**Phase 1446 — CLA text finalization (SENSITIVE)**

- Finalize the Contributor License Agreement text (Genesis-authority governance document).
- Record as Genesis-authority policy; does not constitute external legal opinion.
- Token: `cla_text_finalized_phase_1446`.
- Sensitive: governance policy publication.

**Phase 1447 — Gap 7 partial closure and remaining blockers (NON-SENSITIVE)**

- Record Gap 7 partial closure: AGPL headers complete, CLA ready, allowlist executed.
- Record explicit carry-forward: US provisional patent application (external counsel required — not executable internally); trademark registration (external action required).
- Token: `gap_7_internal_milestones_complete_phase_1447`.
- **Important:** Do not claim Gap 7 is fully closed — the external-action items remain open.

---

### Track G — v0.3 signing + public RC publication (Phases 1448–1452)

**Context:** All previous tracks must be complete and PASS before this track executes. Phase 1387j recorded a v0.3 signing ceremony as a forward obligation. Public RC publication requires: v0.3 signed root envelope, signed release artifact, source publication.

**Phase 1448 — v0.3 Genesis root envelope signing ceremony (SENSITIVE)**

- Requires explicit `GO Phase 1448` + signing authorization token from human.
- Genesis Agent 01 signs the v0.3 candidate root envelope per ADR-0037 + ADR-0038.
- Token: `v0_3_signing_ceremony_complete_phase_1448`.
- Sensitive: produces the canonical Genesis-signed artifact chain for public RC.
- **Pre-conditions:** All Tracks A–F complete; rehearsal PASS; claimability active; J-008 PASS; Gap 7 internal milestones done.

**Phase 1449 — Release artifact signing and manifest finalization (SENSITIVE)**

- Sign release artifacts (binary packages, source tarball, genesis snapshot) with the v0.3 root envelope key chain.
- Finalize `public_rc_launch_readiness_manifest_v1` (defined Phase 1422) with actual gate verdict hashes.
- Token: `release_artifacts_signed_phase_1449`.

**Phase 1450 — Public repository publication (SENSITIVE)**

- Requires explicit `GO Phase 1450` + publication authorization token.
- Execute public-source allowlist (Phase 1445).
- Publish source repository and release artifacts to public URL.
- Token: `public_repository_published_phase_1450`.
- Record: no production minting, no production ILC settlement, no mainnet deployment.

**Phase 1451 — External operator bootstrap guide publication (NON-SENSITIVE)**

- Publish operator bootstrap guide: keypair ceremony (ADR-0038 + ADR-0041 INIT), peer connection (CDL-079), genesis snapshot fetch (CDL-087).
- Token: `operator_bootstrap_guide_published_phase_1451`.

**Phase 1452 — Public RC activation certificate publication and epoch 1 trigger (SENSITIVE)**

- Genesis Agent 01 signs and publishes `activation_certificate_v1` (defined Phase 1424).
- Validators accept certificate as epoch 0→1 transition trigger.
- Genesis publishes T6 "hello world" node citing manifest + certificate hashes — records activation after the fact, does not cause it.
- Token: `activation_certificate_published_phase_1452`, `epoch_1_transition_authorized_phase_1452`.
- **This is the public RC launch commit.**

---

### Track H — CDL-053 Werner broader scope (Phases 1453–1455, conditional)

**Context:** CDL-053 was ratified in this window's fix series with a narrow maintenance-equivalent productive-credit scope. The broader Werner flow-governor architecture (heat/pressure → expanded capacity signals → economic policy) was rejected in Phase 1263 due to insufficient evidence. This track opens it only if post-rehearsal SIM evidence supports it. It is conditional on: (a) Phase 1433 rehearsal producing Werner credit trace data, and (b) human decision to proceed.

**Phase 1453 — Werner flow-governor evidence review (NON-SENSITIVE, conditional)**

- Review Werner overlay data from rehearsal (Phase 1432–1433) against Phase 1263 remaining open conditions:
  - Default SIM-FETCH evidence profile
  - Beta/noise decomposition
  - Spectral trust threshold discipline
  - TransportPrincipal/admission binding
  - Productive-credit authorization
- Record: do evidence gaps close, partially close, or remain open?
- Token: `werner_flow_governor_evidence_review_complete_phase_1453`.
- If conditions not met: record explicit deferral. Do not open CDL.

**Phase 1454 — CDL-053 amendment or flow-governor CDL opening (SENSITIVE, conditional)**

- If Phase 1453 verdict = conditions met: open the flow-governor CDL (CDL-053 amendment or successor CDL).
- Scope: Werner heat signal → topology pressure → admission priority (NOT direct ECU minting).
- Token: `werner_flow_governor_cdl_opened_phase_1454` (conditional).
- If Phase 1453 verdict = deferred: skip this phase; record `werner_flow_governor_cdl_deferred_phase_1454`.

**Phase 1455 — Werner flow-governor CDL prelock + ratification (SENSITIVE, conditional)**

- If Phase 1454 proceeded: ratify the Werner flow-governor CDL with full prelock/ratification cycle.
- Token: `werner_flow_governor_cdl_ratified_phase_1455` (conditional).

---

### Track Z — Window coherence and closure (Phases 1456–1458)

**Phase 1456 — Window coherence, capsule update, and ADR housekeeping (NON-SENSITIVE)**

- Update context capsule.
- Review all open ADR obligations: ADR-0008 (node usefulness), ADR-0019 (graph-native governance), ADR-0024 (agent skills Tier 3), ADR-0025 (dynamic peer discovery), ADR-0028 (settlement substrate graduation), ADR-0029 (hypergraph spectral hash epoch commitment) — record which are still deferred and which have implicit closure by this window's work.
- Token: `window_1429_1458_coherence_complete_phase_1456`.

**Phase 1457 — Window 1429–1458 closure gate (SENSITIVE)**

- Requires explicit `GO Phase 1457`.
- Closure verdict against window objective: public RC published, epoch 1 triggered, at least one external operator connected.
- Handoff doc per `docs/specs/ilc_window_closure_handoff_doc_schema_v0.1.md`.
- Record MemPalace refresh disposition.
- Token: `window_1429_1458_closed_phase_1457`.

---

## 5. Candidate phase table

| Order | Phase (approx) | Topic | Character | Sensitivity |
|-------|----------------|-------|-----------|-------------|
| A1 | 1429 | Production assignment activation — flip `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED = False` | Runtime | **SENSITIVE** |
| A2 | 1430 | CDL-053 Werner local credit first wire to maintenance lottery stub | Runtime | NON-SENSITIVE |
| B1 | 1431 | Rehearsal agent identity ceremony (3 machines × 7 agents) | Identity | **SENSITIVE** |
| B2 | 1432 | Private rehearsal execution — infrastructure validation (scripted agents, Phase 1 dataset) | Rehearsal | NON-SENSITIVE |
| B3 | 1433 | Private rehearsal verdict + Phase 2 dataset (Lean Mathlib) | Rehearsal | conditional |
| C1 | 1434 | TransportPrincipal CDL opening (public path governance) | Constitutional | **SENSITIVE** |
| C2 | 1435 | TransportPrincipal CDL prelock + ratification | Constitutional | **SENSITIVE** |
| C3 | 1436 | Non-loopback sidecar/projection + public fetch serving activation | Runtime | NON-SENSITIVE |
| C4 | 1437 | Rust P2P substrate decision + public P2P activation | Runtime/Constitutional | **conditional SENSITIVE** |
| D1 | 1438 | ECU-to-ILC conversion runtime + CDL-088 activation | Runtime | **SENSITIVE** |
| D2 | 1439 | Public verifier API activation | Runtime | NON-SENSITIVE |
| D3 | 1440 | Claimability integration tests + security review | Testing | NON-SENSITIVE |
| D4 | 1441 | Gap 13 closure verdict | Gate | NON-SENSITIVE |
| E1 | 1442 | ADR-0035 CDL opening + prelock (`type_definition` NodeType) | Constitutional | **SENSITIVE** |
| E2 | 1443 | ADR-0035 CDL ratification | Constitutional | **SENSITIVE** |
| E3 | 1444 | ADR-0035 runtime implementation | Runtime | NON-SENSITIVE |
| F1 | 1445 | AGPL license header audit + public-source allowlist execution | Compliance | NON-SENSITIVE |
| F2 | 1446 | CLA text finalization | Governance | **SENSITIVE** |
| F3 | 1447 | Gap 7 partial closure + external-action carry-forward record | Gate | NON-SENSITIVE |
| G1 | 1448 | v0.3 Genesis root envelope signing ceremony | Identity / Release | **SENSITIVE** |
| G2 | 1449 | Release artifact signing + manifest finalization | Release | **SENSITIVE** |
| G3 | 1450 | Public repository publication | Publication | **SENSITIVE** |
| G4 | 1451 | External operator bootstrap guide publication | Documentation | NON-SENSITIVE |
| G5 | 1452 | Public RC activation certificate + epoch 1 trigger | **Launch** | **SENSITIVE** |
| H1 | 1453 | Werner flow-governor evidence review (conditional on rehearsal data) | Research | NON-SENSITIVE |
| H2 | 1454 | CDL-053 amendment / flow-governor CDL opening (conditional) | Constitutional | **conditional SENSITIVE** |
| H3 | 1455 | Werner flow-governor CDL ratification (conditional) | Constitutional | **conditional SENSITIVE** |
| Z1 | 1456 | Window coherence + capsule + ADR housekeeping | Synthesis | NON-SENSITIVE |
| Z2 | 1457 | Window 1429–1458 closure gate | Gate | **SENSITIVE** |

Total: 28 planned phases (phases 1429–1457) plus up to 2 contingency slots (1458 + rehearsal remediation phases 1433a–1433n if needed).

---

## 6. Dependency tree

```
Phase 1427 (J-008 PASS) — inherits from Window 1399-1428
  └── 1429 (production assignment activation)
       └── 1430 (CDL-053 local credit wire)
            └── 1431 (rehearsal identity ceremony)
                 └── 1432 (rehearsal infra validation)
                      └── 1433 (rehearsal verdict)
                           └── C track (TransportPrincipal 1434-1437)
                           └── D track (claimability 1438-1441)
                           └── E track (ADR-0035 1442-1444) [parallel]
                           └── F track (Gap 7 1445-1447) [parallel]
                                └── 1448 (v0.3 signing) ← ALL tracks must pass
                                     └── 1449 (release artifact signing)
                                          └── 1450 (public publication)
                                               └── 1451 (operator guide)
                                                    └── 1452 (epoch 1 trigger) ← PUBLIC RC
```

---

## 7. Named carry-forward items not closeable in this window

These items are real obligations but require external action or long-range architectural work:

| Item | Why deferred | External dependency |
|------|-------------|---------------------|
| US provisional patent application | Requires external patent counsel filing | External legal |
| Trademark registration | Government action required | External |
| Mainnet split-custody ceremony | Requires multi-party coordination; pre-mainnet only | Future window |
| Production minting activation | Deferred from Phase 1368; post-public-RC only | Future window |
| CDL-031 dynamic ranking runtime | Requires CDL-019 prerequisite chain first | Long-range |
| Full Werner flow-governor CDL | Conditional on evidence; Phase 1453 decides | Evidence-gated |
| ADR-0008 node usefulness/governance weight | Requires live network data | Post-public-RC |
| ADR-0028 settlement substrate graduation | Requires live network data | Post-public-RC |

---

## 8. Open questions for human review before window GO

1. **Rehearsal identity continuity:** Do the 7 rehearsal agent identities (Phase 1431) carry forward to public RC, or does public RC start with fresh agent identities? This decision must be made at or before Phase 1431.

2. **Gap 14 (package modularity) timing:** The roadmap records `gap_14_package_modularity_executes_before_gap_10_public_p2p`. Is Gap 14 a prerequisite for Track C in this window, or does it run in parallel/after? If Gap 14 is a hard prerequisite, insert it before Phase 1434.

3. **Rust P2P substrate (Phase 1437):** Is public P2P a hard prerequisite for epoch 1 trigger, or is a loopback-accessible public RC acceptable as the first version? If loopback-only is acceptable, Phase 1437 can be deferred past Phase 1452.

4. **ADR-0035 priority:** Is ADR-0035 (homoiconic type definition system) a blocking requirement for public RC, or can it run as a parallel non-blocking track? If non-blocking, it can be deferred to post-1452.

5. **Werner flow-governor track (H):** Given the Phase 1263 decision is preserved, is there a specific SIM result or evidence threshold you want to define before authorizing Phase 1453 evidence review?

---

## 9. Deferred code audit findings — resolution routing

The Phase 1410 code audit produced 15 findings. Six are fixed by Phase 1410-Fix1.
The remaining nine are deferred and must be resolved before or during the phases
listed below. They are **not optional** — each must be closed before the phase
that depends on the affected module can proceed to production activation.

| Finding | Severity | File | Issue summary | Resolution phase | Rationale |
|---------|----------|------|---------------|-----------------|-----------|
| FINDING-1 | MEDIUM | `epoch/allocation_distributor_runtime.py` | `rounding_residual` unrouted when `cap_blocked=True` with refutation recipients — recorded in conservation check but has no delivery path | **Phase 1440** (claimability integration tests + security review) | Must be resolved before CDL-029 allocation distributor is connected to any live settlement path; Phase 1440 is the pre-activation integration gate |
| FINDING-3 | LOW | `epoch/ecu_price_clamp_runtime.py` | `PRICE_CLAMP_WIDTH = Decimal("0.55")` hardcoded instead of derived from `P_MAX - P_MIN` | **Phase 1440** | Cosmetic but must not persist into the live price-clamp activation path; bundle with security review |
| FINDING-5 | LOW | `economics/epoch_attribution_settle_runtime.py` | Dead `total_members == 0` branch in quorum check (already handled earlier in the function) | **Phase 1456** (window coherence) | Harmless dead code; no activation dependency; bundle with coherence cleanup |
| FINDING-7 | LOW | `epistemic/jury_assignment_runtime.py` | `_select_outsider` operator-domain filter is O(n) over full eligible pool; should use a set | **Phase 1413** (VRF integration tests + security review) | Jury assignment is on the production path; O(n) filter must be fixed before production activation; Phase 1413 is the integration-level review of this module |
| FINDING-9 | LOW | `identity/agent_id_runtime.py` | v1 and v2 domain separators are identical bytes (`b"ilc-agent-id-v1:"`); defense-in-depth requires distinct values | **Phase 1431** (rehearsal agent identity ceremony) | Identity code is live at Phase 1431; domain separator collision is defense-in-depth but must be audited before protocol identities are created for rehearsal |
| FINDING-11 | LOW | `sidecars/claim_nullifier_registry_v1.py` | No `expire_stale_records()` method — expired entries accumulate in memory indefinitely | **Phase 1440** (claimability integration tests + security review) | Memory growth would occur under long-running public RC serving; must have a cleanup path before Phase 1439 activates the public verifier API |
| FINDING-13 | LOW | `sidecars/claimability_receipt_verifier.py` | `_reject_unsafe_json_tree` rejects negative integers — implicit constraint that all integer payload values must be non-negative is undocumented | **Phase 1440** | Documentation-only fix; bundle with the claimability security review gate |
| FINDING-14 | MEDIUM | `protocol/event_log_retention.py` | `apply_event_log_retention_plan` uses `shutil.rmtree` without verifying the plan was produced by the trusted internal builder (not from deserialized external input) | **Phase 1440** | MEDIUM pre-activation; `_is_within_root` provides partial mitigation, but provenance guard must be added before any public-facing path can trigger pruning |
| FINDING-15 | LOW | `protocol/event_log_retention.py` | `discover_epoch_event_dirs` has no `MAX_RECORDS` cap over local filesystem entries | **Phase 1456** (window coherence) | Local filesystem only; no network data; low risk; bundle with coherence cleanup |

**Execution rule:** Each finding in this table must be fixed (code change + regression test) in the phase listed, or in a Fix sub-phase committed immediately before it. A finding may not be deferred past the phase listed here without explicit human authorization and a new deferral record in PLANNING_INDEX.

---

## 10. This document's authority and next steps

This is a **draft forward plan** — it does not constitute an authorized sequence lock. Before any phase in this window executes:

1. Human reviews this document (including §9 deferred findings routing table) and approves the overall structure.
2. A formal **Window 1429–1458 sequence lock** is produced (following the schema at `docs/specs/ilc_window_guidance_doc_schema_v0.1.md`) as the authoritative execution contract.
3. Phase prompts are drafted per the approved sequence lock. Phase prompts for Phase 1413, 1431, 1440, and 1456 must explicitly include the deferred findings assigned to them.

`window_1429_1458_public_rc_activation_forward_plan_v0.1`
