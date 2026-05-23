# Window 1429–1458: Public RC Activation Forward Plan

**Version:** v0.1
**Drafted:** Phase 1407 fix series (2026-05-20)
**Status:** SUPERSEDED-BY-SEQUENCE-LOCK — window-level `GO Window 1429` recorded 2026-05-22; executable authority now lives in `docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md`; Phase 1429 still requires explicit `GO Phase 1429`
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
| E — ADR-0035 CDL + runtime | **REMOVED** — deferred to Window 1459+ per §8 Q4 resolution | |
| F — Gap 7 internal-executable counsel milestones | ~1443–~1445 | License headers, CLA text, public-source allowlist audit |
| G — v0.3 signing + public RC publication | ~1446–~1450 | Release signing; source publication; public RC claim |
| H1 — Werner diagnostic wiring (default-off) | ~1442 | Single NON-SENSITIVE phase; accumulates data for Window 1459+ flow-governor CDL |
| H2/H3 — Werner flow-governor CDL | **REMOVED** — deferred to Window 1459+ per §8 Q5 resolution | |
| Z — Window coherence + closure | ~1451–~1452 | Window closure gate |

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

**Phase 1436 — Non-loopback sidecar/projection + public fetch serving activation (SENSITIVE)**

> **Updated 2026-05-21:** Reclassified SENSITIVE. This phase opens a non-loopback public network surface; human GO required regardless of CDL status.
> **Completed 2026-05-23:** Runtime activation gate implemented after explicit `GO Phase 1436`. See `docs/phases/phase_1436_public_fetch_serving_activation_walkthrough.md`.

- Explicit human `GO Phase 1436` required.
- Patch `ilc_core/` sidecar/projection runtimes to allow non-loopback binding, gated on `TRANSPORT_PRINCIPAL_CDL_RATIFIED`.
- Activate public fetch serving per CDL-087 ratification carry-forward: serving is now authorized behind TransportPrincipal policy.
- Token: `non_loopback_sidecar_projection_activated_phase_1436`.
- Public fetch public-path mode uses TransportPrincipal-derived `rate_limit_key`; requester-id fallback and client-IP identity remain forbidden.
- Phase 1436 did not activate OpenClaw P2P at the time. That boundary is superseded for the OpenClaw harness path only by Phase 1437; native Rust public P2P remains false.
- No native Rust public P2P, wallet mutation, ECU distribution, ILC settlement, signing, public RC publication, or epoch transition.

**Phase 1437 — OpenClaw harness-assisted P2P activation (SENSITIVE)**

> **Updated 2026-05-21:** Reclassified from "conditional SENSITIVE" to SENSITIVE. Activating any externally reachable P2P endpoint requires explicit human GO. Native Rust P2P substrate decision fully deferred to Window 1459+ per Q3 resolution.
> **Completed 2026-05-23:** OpenClaw `TransportHarness` relay path activated after explicit `GO Phase 1437`. See `docs/phases/phase_1437_openclaw_p2p_activation_walkthrough.md`.

- Explicit human `GO Phase 1437` required.
- Activate OpenClaw harness-assisted P2P using existing CDL-078 relay path; Phase 1432 must have validated this path.
- CDL coverage check: verify CDL-078 + CDL-094 cover this activation surface before proceeding.
- Token: `openclaw_p2p_activated_phase_1437`; `native_rust_p2p_deferred_window_1459_plus_phase_1437`.
- Native Rust P2P substrate (PersistentQuicSessionManager, CDL-078 relay routing in Rust, peer discovery) deferred to Window 1459+.
- `PUBLIC_P2P_ACTIVATED` remains `False`; no OpenClaw gateway process/listener is started by this phase.

**Track C status:** complete after Phase 1437. Stale CDL-088 historical-test cleanup is routed to separate NON-SENSITIVE task `phase_1437a_stale_cdl_088_test_cleanup` and is not part of Track C activation.

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

### Track E — ADR-0035 CDL + runtime ~~(Phases 1442–1444)~~ — REMOVED

> **SUPERSEDED 2026-05-21:** Track E is removed from Window 1429-1458. Per §8 Q4 resolution,
> ADR-0035 is not a public RC blocker. All three phases (CDL opening, ratification, runtime)
> are deferred to Window 1459+. Token locked: `q4_adr_0035_deferred_window_1459_plus_not_rc_blocker`.
> Do not use phase numbers 1442-1444 for ADR-0035 work. See §5 candidate phase table and §8 Q4
> for the locked decision and Window 1459+ assignment.

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

### Track H1 — Werner diagnostic wiring (~Phase 1442, NON-SENSITIVE)

> **Updated 2026-05-21:** Track H replaced with Track H1 only. The Werner flow-governor CDL
> (Phases 1453–1455 in the prior draft) is removed from this window. Per §8 Q5 resolution,
> the flow-governor CDL is deferred to Window 1459+ (Track C there) pending Werner diagnostic
> trace data collected by this Track H1 phase. Token locked:
> `q5_werner_diagnostic_h1_only_flow_governor_cdl_deferred_window_1459_plus`.

**Context:** CDL-053 was ratified in the Window 1399-1428 fix series with a narrow
maintenance-equivalent productive-credit scope. The broader Werner flow-governor architecture
(systolic/diastolic/pulse-pressure → admission priority) requires diagnostic trace data before
a CDL can be opened. Track H1 wires default-off Werner diagnostic instrumentation to accumulate
data during the public RC window. The flow-governor CDL opens in Window 1459+ once the
diagnostic data supports it.

**Phase ~1442 — Werner diagnostic wiring (NON-SENSITIVE)**

- Wire default-off systolic/diastolic/pulse-pressure pressure metrics for jury/review lanes only.
- Metrics accumulate diagnostic data; they do not affect ECU, wallet, or admission decisions.
- No CDL amendment required — diagnostic instrumentation only.
- Token: `werner_diagnostic_wired_phase_h1`.
- Record explicit non-claim: `werner_flow_governor_cdl_deferred_window_1459_plus_phase_h1`.
- Can run in parallel with D and F tracks.

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

**Note:** Updated 2026-05-21 to reflect §8 Q1-Q5 resolutions. Changes from v0.1 draft:
- Track E (ADR-0035, phases 1442-1444) REMOVED — deferred to Window 1459+
- Track H restructured: H1 = single Werner diagnostic wiring phase (NON-SENSITIVE); old H2/H3 conditional CDL phases REMOVED — flow-governor CDL deferred to Window 1459+
- Phase 1437 updated: OpenClaw harness-assisted P2P (not full Rust P2P substrate decision)
- Gap 14 phases added between C2 and C3 (phases ~1436a-1436b, run parallel with C governance)
- Phase numbers for D, F, G, Z tracks shift slightly; approximate numbers used

| Order | Phase (approx) | Topic | Character | Sensitivity |
|-------|----------------|-------|-----------|-------------|
| A1 | 1429 | Production assignment activation — flip `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED = False` | Runtime | **SENSITIVE** |
| A2 | 1430 | CDL-053 Werner local credit first wire to maintenance lottery stub | Runtime | NON-SENSITIVE |
| B1 | 1431 | Rehearsal agent identity ceremony (3 machines × 7 agents, production keypairs, preserved off-machine) | Identity | **SENSITIVE** |
| B2 | 1432 | Private rehearsal — infrastructure validation (scripted agents, Phase 1 dataset, OpenClaw P2P path tested) | Rehearsal | NON-SENSITIVE |
| B3 | 1433 | Private rehearsal verdict + Phase 2 dataset (Lean Mathlib); wipe right after PASS | Rehearsal | conditional |
| C1 | 1434 | TransportPrincipal CDL opening (public path governance, Gap 10) | Constitutional | **SENSITIVE** |
| C2 | 1435 | TransportPrincipal CDL prelock + ratification | Constitutional | **SENSITIVE** |
| G14a | ~1436a | Gap 14 package modularity — Phase 1 (modular package profile definition, parallel with C governance) | Runtime | NON-SENSITIVE |
| G14b | ~1436b | Gap 14 package modularity — Phase 2 (public RC profile, OpenClaw/NemoClaw hosted profile) | Runtime | NON-SENSITIVE |
| C3 | 1436 | Non-loopback sidecar/projection + public fetch serving activation (requires Gap 14 complete + Phase 1435) | Runtime | **SENSITIVE** |
| C4 | 1437 | OpenClaw harness-assisted P2P activation (CDL-078 relay path; validated in Phase 1432) | Runtime | **SENSITIVE** |
| D1 | 1438 | ECU-to-ILC conversion runtime + CDL-088 activation | Runtime | **SENSITIVE** |
| D2 | 1439 | Public verifier API activation | Runtime | NON-SENSITIVE |
| D3 | 1440 | Claimability integration tests + security review | Testing | NON-SENSITIVE |
| D4 | 1441 | Gap 13 closure verdict | Gate | NON-SENSITIVE |
| H1 | ~1442 | Werner diagnostic wiring — default-off pressure diagnostics (systolic/diastolic/pulse-pressure; review lane only; no CDL, no ECU, no wallet) | Runtime | NON-SENSITIVE |
| F1 | ~1443 | AGPL license header audit + public-source allowlist execution | Compliance | NON-SENSITIVE |
| F2 | ~1444 | CLA text finalization | Governance | **SENSITIVE** |
| F3 | ~1445 | Gap 7 partial closure + external-action carry-forward record | Gate | NON-SENSITIVE |
| G1 | ~1446 | v0.3 Genesis root envelope signing ceremony | Identity / Release | **SENSITIVE** |
| G2 | ~1447 | Release artifact signing + manifest finalization | Release | **SENSITIVE** |
| G3 | ~1448 | Public repository publication | Publication | **SENSITIVE** |
| G4 | ~1449 | External operator bootstrap guide publication | Documentation | NON-SENSITIVE |
| G5 | ~1450 | Public RC activation certificate + epoch 1 trigger | **Launch** | **SENSITIVE** |
| Z1 | ~1451 | Window coherence + capsule + ADR housekeeping | Synthesis | NON-SENSITIVE |
| Z2 | ~1452 | Window 1429–1458 closure gate | Gate | **SENSITIVE** |

**Removed from this window:**
- Track E (ADR-0035): deferred to Window 1459+ per Q4 resolution
- Track H2 (CDL-053 amendment opening): deferred to Window 1459+ per Q5 resolution
- Track H3 (Werner flow-governor CDL ratification): deferred to Window 1459+ per Q5 resolution
- Native Rust P2P substrate phases: deferred to Window 1459+ per Q3 resolution

Total: ~26 planned phases plus up to 2 Gap 14 phases and contingency slots (rehearsal remediation phases 1433a–1433n if needed). Exact phase number assignments finalized in the sequence lock.

---

## 6. Dependency tree

```
Phase 1427 (J-008 PASS) — inherits from Window 1399-1428
  └── 1429 (production assignment activation)
       └── 1430 (CDL-053 local credit wire)
            └── 1431 (rehearsal identity ceremony)  [SENSITIVE]
                 └── 1432 (rehearsal infra validation — OpenClaw P2P path tested)
                      └── 1433 (rehearsal verdict + wipe right)
                           ├── C track: 1434 (TransportPrincipal CDL opening)
                           │            └── 1435 (TransportPrincipal CDL ratification)
                           │                 ├── [parallel] Gap 14: ~1436a → ~1436b (package modularity)
                           │                 └── 1436 (sidecar/projection + public fetch serving)  ← requires Gap 14 complete  [SENSITIVE]
                           │                      └── 1437 (OpenClaw harness-assisted P2P)  [SENSITIVE]
                           ├── D track: 1438 (CDL-088 activation + ECU-to-ILC conversion)
                           │            └── 1439 (public verifier API)
                           │                 └── 1440 (claimability integration tests + security review)
                           │                      └── 1441 (Gap 13 closure)
                           ├── H1: ~1442 (Werner diagnostic wiring)  [parallel, NON-SENSITIVE, before ~1446]
                           └── F track: ~1443 (license header audit)
                                        └── ~1444 (CLA text finalization)
                                             └── ~1445 (Gap 7 partial closure)
                                                  └── ALL tracks (C+D+F complete, H1 wired)
                                                       └── ~1446 (v0.3 signing)  [SENSITIVE]
                                                            └── ~1447 (release artifact signing)  [SENSITIVE]
                                                                 └── ~1448 (public repository publication)  [SENSITIVE]
                                                                      └── ~1449 (operator bootstrap guide)
                                                                           └── ~1450 (epoch 1 trigger)  ← PUBLIC RC  [SENSITIVE]
                                                                                └── ~1451 (window coherence)
                                                                                     └── ~1452 (window closure gate)  [SENSITIVE]
```

**Critical path:** A → B (rehearsal) → C (TransportPrincipal + Gap 14) → D (claimability) → F (Gap 7) → G (signing + publication + epoch 1 trigger) → Z (closure)

**Parallel lanes:** H1 (Werner diagnostic, NON-SENSITIVE) runs during D/F execution; Gap 14 runs during C governance (1434-1435)

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

## 8. Open questions — RESOLVED 2026-05-21

All five open questions from the initial draft have been resolved by the human reviewer. Decisions are locked and carried forward to the formal sequence lock (`docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md`).

---

**Q1 — Rehearsal identity continuity: RESOLVED — fresh start with preserved keys**

Phase 1431 generates the 7 real production keypairs. Key material is saved off-machine by the human operator. After rehearsal completes and the wipe right is exercised, public RC re-initializes these same 7 agents via fresh ADR-0038/ADR-0041 ceremonies using the preserved keys. The rehearsal state is wiped; the cryptographic identities are continuous. Each agent will subsequently connect their respective LLM harness (OpenClaw, etc.) and operator tooling.

Token locked: `q1_rehearsal_identity_continuity_resolved_keys_preserved_rc_fresh_start`

---

**Q2 — Gap 14 timing: RESOLVED — parallel with Track C governance, required before Phase 1436**

Gap 14 (package modularity) runs in parallel with Track C phases 1434-1435 (TransportPrincipal CDL governance). Gap 14 must be complete before Phase 1436 (non-loopback sidecar/projection + public fetch serving activation). Gap 14 phases are inserted between Phase 1435 and Phase 1436 in the candidate phase table.

Token locked: `q2_gap_14_parallel_with_c_governance_required_before_1436`

---

**Q3 — P2P substrate: RESOLVED — OpenClaw harness-assisted P2P for Phase 1437; native Rust P2P deferred to Window 1459+**

Phase 1437 targets OpenClaw harness-assisted P2P as the public RC connection path. This is mediated P2P via the OpenClaw gateway layer using the existing CDL-078 relay path. Track B rehearsal (Phase 1432-1433) must explicitly test the OpenClaw connection path. Native Rust P2P substrate (PersistentQuicSessionManager completion, CDL-078 relay routing in Rust, peer discovery, Python/Rust cross-stack integration) is deferred to Window 1459+ with concrete phases assigned there.

Token locked: `q3_openclaw_harness_p2p_phase_1437_native_rust_deferred_window_1459_plus`

---

**Q4 — ADR-0035: RESOLVED — fully deferred to Window 1459+**

ADR-0035 (homoiconic type definition system) is not a public RC blocker. Track E is removed from Window 1429-1458 critical path entirely. Concrete assignment in Window 1459+:
- Phase 1459+1: ADR-0035 CDL opening (type_definition NodeType governance) — SENSITIVE
- Phase 1459+2: ADR-0035 CDL ratification — SENSITIVE
- Phase 1459+3: ADR-0035 runtime (migrate hardcoded type strings to graph-native type_definition nodes) — NON-SENSITIVE

Token locked: `q4_adr_0035_deferred_window_1459_plus_not_rc_blocker`

---

**Q5 — Werner flow-governor: RESOLVED — Werner diagnostic wiring in Window 1429-1458 (Track H1), flow-governor CDL deferred to Window 1459+**

Werner diagnostic wiring is a single NON-SENSITIVE phase added to Window 1429-1458 as Track H1. It wires default-off pressure diagnostics (systolic/diastolic/pulse-pressure metrics) for jury/review lane only against existing review-lane evidence. No CDL amendment, no settlement, no ECU, no wallet mutation. This accumulates diagnostic data during rehearsal and early public RC epochs. Werner flow-governor CDL (CDL-053 amendment or successor) is deferred to Window 1459+ pending diagnostic trace data. The old Track H2/H3 conditional CDL phases are removed from this window.

Token locked: `q5_werner_diagnostic_wiring_track_h1_nons_flow_governor_cdl_deferred_1459_plus`

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

## 10. Long-range governance obligations (post-public-RC)

These items are not blockers for Window 1429–1458. They are named architectural
obligations that must be addressed in a post-public-RC window. They are recorded
here because they emerged from the Phase 1410 audit and governance review; they
must not be forgotten between context sessions.

### 10.1 Genesis authority sunset and three-mode governance architecture

**Status:** Architecture fully specified in original design conversation (Oct 11 2025,
`Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt` lines 16094–16288);
no standalone spec; not implemented; SUBSTANTIVE gap recorded against CDL-004 in
`docs/specs/ilc_constitutional_context_audit_v0.1.md`; cited as raw-012616/646/647/660
in `docs/specs/ilc_governance_conflict_set_ratification_v0.1.md`.

**Background:** On October 11, 2025, Jamison proposed the three-branch model directly
("a system of three checks and balances similar to US constitutional system..."), motivated
by his university thesis that both two-party and three-party power systems are stable —
three being the last stable number. The design was elaborated in detail in that conversation.
CDL-004 was ratified at the principle level with the mechanism deferred. The constitutional
context audit records this as a SUBSTANTIVE gap.

**Three-phase, three-branch model (from Oct 11 2025 conversation):**

**Phase A — Boot (~2 years / Genesis constitutional period):**

| Branch | Role | Constraints |
|--------|------|-------------|
| Executive (Genesis) | May propose and enact bounded toggles; publishes signed proposal nodes | Annual quota (≤3/year); bounded: decoy bump ≤3%, 1-epoch pause, stake mult ≤1.5 |
| Court (7+1 VRF panel) | Must certify each Executive proposal as "objective and within bounds" before activation | k-by-sponsor_cluster; outsider seat; contestable like any claim |
| Legislature (House) | Advisory only during Boot; passes non-binding resolutions to rehearse the flow | Does not block Executive yet |

**Phase B — Transition:**

| Branch | Role |
|--------|------|
| Executive (Genesis) | Proposer + suspensive veto only (no direct enactment); ≤3 vetoes per 1000 epochs; 2/3 House override defeats veto |
| Court (7+1) | Certifies both (i) proposal is objective/within bounds and (ii) vote tally rules were met |
| House | Binding vote: passes by seat majority + cluster supermajority (≥⅔ sponsor_clusters) |

**Phase C — Mature (target: Genesis authority fully receded):**

| Branch | Role |
|--------|------|
| Executive (Genesis) | No veto; retains attention ballot power (100% reach to call a vote) + evidence packets only — pure soft power |
| Court | Same certification; all proposals contestable |
| House | Full authority; size = `clamp(101, floor(0.002 × active_wallets), 501)`, recomputed every 200 epochs |

**Key House parameters from original design:**
- Seat allocation: proportional to sponsor_cluster share of recent honest work (vested audits, decoys, low refutes)
- Per-cluster cap: ≤25% of House seats
- Eligibility: rep ≥0.80, ≥M recent audits, ≥99% decoy pass rate, no active slashes
- Voting: seat majority (>50%) AND cluster supermajority (≥⅔ of sponsor_clusters voting YES)
- Optional rep-capped weighting (quadratic cap) inside clusters
- Re-proposal cooldown: same measure cannot be resubmitted for X epochs unless evidence hash changed

**Autopilot note:** Autopilot (objective metrics triggering parameter flips) is NOT a
fourth branch — it is "the thermostat: physics, not party," preserving the three-party
stability balance.

**Mapping to existing ratified mechanisms:**

| Branch | Ratified mechanisms already in place |
|--------|--------------------------------------|
| Court | CDL-V4 (reopening), CDL-V7 (Popperian gate), CDL-091 (jury incentives), J-series activation; panel architecture directly reuses 7+1 VRF selection |
| House | CDL-004 (procedural governance); ordinary CDL ratification cycle provides the foundation; cluster-majority quorum **not yet enforced** |
| Executive sunset | CDL-003 (fade-out), CDL-004 (caps), CDL-013 (normalized voting), CDL-V6 (Genesis sunset trigger), CDL-045 (emergency sunset) |

**Named obligation:** A post-public-RC window must produce a standalone spec that:

1. Formalizes the court/house/executive model as a named ILC governance spec, citing the
   Oct 11 2025 design conversation (`Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:16094`)
   and raw-012616/646/647/660.
2. States observable Phase B and Phase C transition triggers (participation threshold,
   Genesis ECU share threshold) — exact numbers require SIM evidence against the
   Boot → Transition → Mature phase table.
3. Closes the CDL-004 SUBSTANTIVE gap by adding a forward pointer to the corpus sources.
4. Addresses `TODO-P585-02` (Genesis governance dilution closure) from
   `ilc_epistemological_foundations_canonical_v0.1.md`.
5. Routes through a SENSITIVE CDL phase when ready — this is a constitutional surface.

**Why recorded here:** The Z_Past_Chats search found the full design in the original Oct
11 2025 conversation; prior MemPalace searches had only reached the downstream ratification
artifacts. This is the authoritative source. No standalone spec formalizing it exists yet.

---

### 10.2 Delegated constitutional authority mechanism

**Status:** Named gap — no CDL, no spec.

**Background:** The CDL ratification cycle requires explicit human GO tokens for every
SENSITIVE step. This is the correct discipline for the current small-team bootstrap
context. As the network matures toward production with many operators, requiring Genesis-
mediated human authorization for every constitutional decision will become the primary
governance throughput bottleneck.

**Named obligation:** A post-public-RC window must:

1. Design a delegated constitutional authority mechanism — a CDL that defines how
   ratification authority for non-bootstrap CDLs can transfer from Genesis-mediated
   to operator-quorum-mediated over time.
2. Gate this design on observable conditions: J-008 PASS, public RC live, ≥10
   independent operators connected to the network.
3. This must NOT be activated before those conditions are met. Premature delegation
   of constitutional authority before community quorum is established replicates
   the same bootstrap-permanence problem CDL-V6 is meant to solve.

**Prerequisite for this window:** None. Record only. Do not design prematurely.

---

### 10.3 CDL falsification criterion field

**Status:** Gap noted in `ilc_epistemological_foundations_canonical_v0.1.md`; no CDL row carries this field.

**Background:** The epistemological foundations canonical states: "every ratified CDL
row should carry an explicit falsification criterion — a specific observable outcome
that would trigger reopening." Currently no CDL row carries such a field. This gap
means CDL entries can accumulate indefinitely without a structured path for the network
to signal that a ratified decision is no longer supported by evidence.

**Named obligation:** A coherence task in the first post-public-RC window must:

1. Define a `falsification_criterion` field for CDL rows (or an equivalent annotation
   attached to ratified CDL sections).
2. Apply retroactively to all currently-ratified CDLs in scope (CDL-001 through
   whatever CDL number is current at that time) as part of a coherence phase.
3. The field is non-blocking — no CDL is reopened simply by adding this field. Its
   purpose is to make reopening conditions explicit and auditable.

**Why recorded here:** The CDL review during the Phase 1410 audit found this gap was
previously noted but has no assigned resolution phase. It is assigned here to the first
post-public-RC window coherence phase.

---

### 10.4 CDL-091 inviter-chaining incentive extension (candidate, deliberation required)

**Status:** Candidate — not yet opened; no prelock; requires human deliberation.

**Background:** CDL-091 (jury incentive economics, ratified Phase 1400) governs jury
panel composition incentives. An inviter-chaining extension — economic incentives for
agents to onboard new participants via the ADR-0038 provenance edge — was identified
as a candidate CDL-091 follow-on during Phase 1410 governance review.

**Refined candidate scope:** The preferred model is not an immediate referral bounty.
It is a backward attribution stream over an agent-init service chain. A serving agent
may receive attribution only when a downstream agent that it helped initialize later
produces accepted, non-refuted work. The init service edge should record verifiable
bootstrap service: content-addressed software or protocol-bundle serving, epoch-snapshot
or Genesis-lineage serving, successful ADR-0038/ADR-0041 init evidence, and later
downstream survival/productivity evidence. Raw downloads, raw invitations, or unsigned
claims of "I onboarded this agent" are not sufficient payout evidence.

**Censorship-resilience motivation:** Distributed agent-init serving is a resilience
surface. Centralized hosting for initial software downloads or Genesis/snapshot
material is an institutional takedown risk in restrictive jurisdictions. This candidate
therefore includes P2P bootstrap relay, signed software/package mirror service, Genesis
graph/snapshot serving, and new-agent support services as potentially rewardable
surfaces, but only through self-verifying receipts and delayed downstream outcomes.

**ADR-0009 bundle dependency:** This incentive lane must absorb the remaining
protocol-native bundle work rather than treating "download serving" as an ordinary
file-hosting reward. ADR-0009 defines four bootstrap layers:

1. Layer 0 protocol rules bundle.
2. Layer 1 Genesis state bundle.
3. Layer 2 epoch state snapshots.
4. Layer 3 live wire messages.

A new agent should eventually be able to receive the protocol bundle plus a recent
snapshot from any serving peer, verify the hash/signature chain back to Genesis, and
begin participation without trusting a website, app store, centralized package host,
or the serving agent. Until that exists, Python remains the reference implementation
and agent-init serving can only be rewarded as best-effort mirror/bootstrap support,
not as a completed protocol-native self-compilation path.

**Required bundle work before this incentive can become protocol-native:**

1. Close Layer 0 schema scope: protocol object schemas, governance constants,
   scoring constants, version/predecessor semantics, and canonical encoding rules.
2. Implement ADR-0035 graph-native `type_definition` nodes, or explicitly document
   why the first public bundle still uses a transitional hardcoded type table.
3. Build a deterministic bundle generator that emits content-addressed signed
   protocol bundles.
4. Build an independent verifier for bundle CID, signature, schema completeness,
   version lineage, and canonical encoding.
5. Define the Layer 1 Genesis state bundle and Layer 2 epoch snapshot schemas with
   explicit references to the verified Layer 0 bundle CID.
6. Bind Layer 3 D2D bootstrap messages to content-addressed bundle/snapshot fetch and
   verification, so serving peers can be credited for delivering verifiable artifacts
   rather than opaque files.
7. Produce cross-implementation test vectors proving that a non-Python verifier can
   validate the same bundle and snapshot chain.

**Key constraints:**

1. Inviter chain references must bind to the ADR-0038 `identity_lineage_ref` provenance
   edge — NOT encoded in the `agent_id` itself (CDL-042 flat namespace, ratified Phase
   407, prohibits inviter encoding in agent_id derivation).
2. The attribution edge must bind to ADR-0041's permissionless INIT semantics: the
   downstream agent remains permissionless and zero-weight until attested; the serving
   agent earns no authority over the downstream agent.
3. Payout must be delayed, decayed, and capped. The unit of success is downstream
   accepted work or verified survival, not a download count, invite count, or wallet
   creation event.
4. Upstream slashing of inviters (slashing agents whose invitees misbehave) is
   dangerous — it would suppress legitimate agent onboarding due to tail-risk aversion.
   This must be explicitly reviewed and likely rejected. A narrower clawback or
   withheld-reward model for fraudulent bootstrap receipts remains in scope.
5. This is an incentive surface change. Requires SIM evidence before CDL opening.

**Named obligation:** Before opening any CDL for inviter-chaining incentives:

1. Produce a SIM showing the bootstrapping incentive effect without upstream slashing.
2. Produce a SIM showing delayed downstream-work attribution over the agent-init
   service chain, including Sybil-tree, same-cluster mirror farm, and artificial
   downstream productivity attacks.
3. Confirm that ADR-0038 provenance edge plus ADR-0041 INIT attestation semantics are
   sufficient as the binding mechanism.
4. Define a self-verifying bootstrap service receipt format for content-addressed
   software/protocol-bundle serving and epoch-snapshot/Genesis-lineage serving.
5. Define the ADR-0009 Layer 0/1/2/3 bundle/snapshot completion track that makes
   those receipts independently verifiable rather than trust-based download claims.
6. Bring to human deliberation with a specific CDL scope proposal.
7. Do not open this CDL in any window before public RC is live.

---

### 10.5 Post-public-RC provenance depth and hub relay CDL candidate

**Status:** Research-only (SIM-PROVENANCE-02 complete, commits `4f389de9`, `e7ff15b4`);
no CDL, no spec, no PROVENANCE_MAX_DEPTH amendment, no hub relay activation.

**Route:** Window 1459+ / Track I candidate. Not Track H (Werner flow-governor).
Not a blocker for Phase 1424 or any phase in this window.

**Background:** SIM-PROVENANCE-02 establishes the empirical basis for the lost-middle
concern and proposes hub relay as the best candidate architecture:

- `PROVENANCE_MAX_DEPTH = 3` is a safety truncation, not a Popperian principle.
  At `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`, depth-3 captures 90.9% of the
  infinite geometric sum but pays zero to hops 4+. Long epistemological chains have
  a creditor middle region that is systematically excluded.
- **Hub relay candidate model:** Attribution received by a hub is redistributed
  upstream. Conservation invariant: `sum(all_recipients) ≤ original_attribution_budget`
  — no new ECU is minted at any relay step.
  `retain = min(hub_maintenance_cap, B_in × retain_rate)`; `passed = B_in − retain`.
  Simulation parameters (not policy): `retain_rate = 0.15`, `hub_maintenance_cap = 0.05 ECU`.
- **Three hub types:** (1) Genuine load-bearing: high cross-cluster inflow, has parents,
  `pass_through_ratio ≥ 0.15`. (2) Parasitic: `parent_count > 0` AND `pass_through_ratio < 0.15`
  — flag for review. (3) Terminal (Genesis primitive): `parent_count == 0`, any pass-through
  ratio — acceptable.
- **Convergence-as-centrality:** Multiple independent backwards attribution chains
  converging at a node is hub-candidate evidence, not payout authority. Manufactured
  convergence remains possible; cross-cluster Laplacian filtering is the anti-ring
  guard, but FP/FN calibration is still missing.

**Key economic intent:** The protocol's historical intent is that new frontier claims
are valued tentatively while old, central, refutation-resistant nodes accumulate
economic value over time — the opposite of the depth-3 frontier-biased gradient.
Hub relay is the proposed mechanism to realize this intent without requiring each
claiming artifact to enumerate the full ancestor chain.

**Non-claims (all preserved from SIM-PROVENANCE-02):**

```
no_provenance_depth_amendment_from_sim_02
no_hub_relay_activation_from_sim_02
provenance_max_depth_3_not_changed_by_sim_02
```

**Blocking gates before any CDL opening:**

1. **SIM-PRESSURE-SPECTRAL-02** — calibrate Laplacian concentration threshold
   against real false-positive/false-negative data. Until this SIM runs, the
   cross-cluster filter is an architectural spec, not a production control.
   Laplacian flags "suspicious topology," not "confirmed abuse."
2. **Live network topology data** — hub identification requires real cross-cluster
   inflow observations from post-public-RC epochs. Simulation hub topology is
   synthetic.
3. **CDL deliberation questions before any opening:**
   - Who can assert hub status on a canonical node? What is the authority surface?
   - How is `retain_rate = 0.15` / `hub_maintenance_cap = 0.05 ECU` calibrated
     against live data and the Genesis 5% governor?
   - How does hub relay compose with the Genesis 5% governor? Governor limits
     total Genesis accrual; does it apply before or after relay redistribution?
   - What is the cross-cluster filter's enforcement path? Review trigger only,
     or automatic exclusion?
   - Can depth remain at 3 with hub relay layered on top, or does hub relay
     replace the depth parameter entirely?

**Named forward obligation:**

```
SIM-PRESSURE-SPECTRAL-02
  → CDL deliberation (canonical hub identification + retain/cap calibration)
    → CDL-PROVENANCE-DEPTH-01 opening (Window 1459+ / Track I candidate)
```

This is a post-public-RC architectural obligation. No action required in Window
1429–1458 beyond preserving this record.

---

### 10.6 Post-public-RC ADR-0029 Merkle-Laplacian / PoSK hardening lane

**Status:** Research-positive after v0.2 paper intake, first-pass SIM strike force,
and follow-on SIM hardening; not activated; no CDL; no epoch-commitment mutation;
no PoSK admission gate; IP-gated and `PUBLIC_RC_EXCLUDE`.

**Evidence now in repo:**

- `docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.2.md`
- `docs/research/ilc_merkle_laplacian_dual_commitment_v0.2_intake_review_2026_05_22.md`
- `docs/sims/sim_merkle_laplacian_v02/strike_force_results_2026_05_22_v0.1.md`
- `docs/sims/sim_merkle_laplacian_v02/followon_results_2026_05_22_v0.1.md`
- `docs/specs/ilc_merkle_laplacian_v02_canonicalization_and_posk_transcript_spec_v0.1.md`

**SIM strike-force tokens:**

```
sim_spectral_01_rerun_quantized_smallest_k_viable=true
sim_spectral_cost_01_dense_10k_fast_path_viable=false
sim_posk_01_copy_attack_blocked=true
sim_dualcommit_01_layer_separation_confirmed=true
sim_directed_closure_01_direction_lost_in_s=true
sim_reuse_stability_01_linear_unsafe_log_capped_preferred=true
sim_posk_param_02_multiple_nonce_calibration_complete=true
sim_spectral_crossimpl_02_python_vector_conformance=true
sim_cospectral_01_bounded_random_k8_distinct_m_collision_found=false
sim_directed_spectral_02_extension_required=true
```

**Key findings to preserve:**

1. The candidate `S(t)` encoding is smallest-k eigenvalues, fixed-point int64
   little-endian, `q=1_000_000` as a research parameter only.
2. Dense full eigendecomposition is not the 10k-node fast path; sparse/iterative
   low-end extraction is required.
3. PoSK must bind sampled edge-set root `R_c` plus challenge-subgraph spectrum;
   spectrum-only is insufficient against stale/partial graph views.
4. PoSK still needs challenge timeout or local-storage attestation controls.
5. Undirected closure loses directed-flow information; directed claims require a
   directed spectral extension.
6. Linear `reuse_count` weighting is unsafe; log/capped-log remains the safer
   candidate family pending CDL.
7. Follow-on PoSK parameter sweep supports `sample_size=64` and `nonce_count=4`
   as internal research evidence only; these are not activation constants.
8. Python-only cross-implementation conformance is positive, but non-Python
   reproduction remains required before activation.
9. Bounded random cospectral search found no distinct-content `k=8` collision,
   but found distinct-content weakness at `k=2` and does not replace formal or
   curated adversarial cospectral work.

**Named obligation:** Route to Window 1459+ Track G:

```
ADR-0029 Merkle-Laplacian hardening
  → canonical vector review
  → PoSK parameter / ceremony-control review
  → cross-implementation + cospectral review
  → IP/counsel/publication disposition
  → CDL readiness verdict or explicit deferral
```

**Non-claims:**

```
no_merkle_laplacian_epoch_commitment_activation_from_v0_2
no_posk_admission_activation_from_v0_2
no_publication_authorization_from_v0_2
public_rc_exclude_retained_for_merkle_laplacian_artifacts
```

This is a post-public-RC architectural obligation. No action required in Window
1429–1458 beyond preserving this record and ensuring public-RC export profiles
exclude the paper/SIM artifacts unless later IP/counsel authorization removes
the exclusion markers.

---

## 11. This document's authority and next steps

This is a **draft forward plan** — it does not constitute an authorized sequence lock. Before any phase in this window executes:

1. Human reviews this document (including §9 deferred findings routing table and §10 long-range governance obligations) and approves the overall structure.
2. A formal **Window 1429–1458 sequence lock** is produced (following the schema at `docs/specs/ilc_window_guidance_doc_schema_v0.1.md`) as the authoritative execution contract.
3. Phase prompts are drafted per the approved sequence lock. Phase prompts for Phase 1413, 1431, 1440, and 1456 must explicitly include the deferred findings assigned to them.

`window_1429_1458_public_rc_activation_forward_plan_v0.1`
