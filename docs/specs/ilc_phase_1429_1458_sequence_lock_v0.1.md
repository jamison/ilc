# ILC Phase 1429-1458 Sequence Lock v0.1

**Status:** DRAFT — requires human review and explicit GO before any phase executes
**Date:** 2026-05-21
**Owner lane:** G8 Jury Economy / Launch Readiness / Public RC Activation
**GO authority:** Human reviewer (explicit `GO window_1429_1458` required before Phase 1429)

```text
window_1429_1458_sequence_lock_committed
go_window_1429_1458_authorized_PENDING_HUMAN_GO
phase_1429_is_first_phase_this_window
```

---

## 1. Window Identity and Scope

**Window:** 1429-1458
**Objective:** Achieve the first publicly-accessible, constitutionally-sound RC publication — a signed published release artifact, a published `activation_certificate_v1` triggering epoch 0-to-1, and at least one external operator completing the identity init ceremony.

**Baseline at lock time:**
- Window 1399-1428 CLOSED PASS (`0876cae8`) — `window_1399_1428_closed_phase_1428`
- J-008 gate: PASS — `production_jury_activation_gate_pass_phase_1427`
- `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED` = True (explicit activation commit required)
- `PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED` = False (set Phase 1427)
- `soft_rc_eligible=true` — recorded Phase 1426
- Last ratified CDL: CDL-093 (Phase 1408)
- Active capsule: v5.59 (Phase 1421)
- Current commit: `0876cae8`

---

## 2. Inputs and Closure Inheritance

| Item | State inherited from Window 1399-1428 |
|------|--------------------------------------|
| J-008 gate | PASS — all 10 conditions MET |
| `PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED` | False (set Phase 1427) |
| `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED` | True — activation commit required this window |
| CDL-053 Werner local productive credit | Ratified Phase 1407-Fix2 — narrow maintenance scope only |
| CDL-087 canonical fetch distribution | Ratified Phase 1278 Fix1 — public fetch/sidecar still blocked pending TransportPrincipal CDL |
| CDL-088 public claimability authority | Ratified Phase 1376 — activation gated |
| CDL-091 jury incentive economics | Ratified Phase 1400 |
| CDL-092 CapProof | Ratified Phase 1405 |
| CDL-093 maintenance lottery pool | Ratified Phase 1408 |
| Review lane wiring | Complete Phase 1417 — `review_lane_wiring_complete_phase_1417` |
| VRF verifier | Implemented Phase 1411; integrated Phase 1412 |
| Anti-capture diversity | Verified Phase 1419 |
| Copyright counsel disposition | Complete Phase 1420 |
| `soft_rc_eligible=true` | Phase 1426 |
| Activation certificate v1 design | Phase 1424 |
| Launch readiness manifest schema | Phase 1422 |
| Private soft-RC rehearsal entry criteria | Phase 1423 |
| Werner diagnostic wiring | Not yet started |
| Gap 10 (TransportPrincipal) | Open |
| Gap 13 (ECU-to-ILC claimability) | Open |
| Gap 14 (package modularity) | Open |
| ADR-0035 homoiconic type system | Deferred to Window 1459+ (Q4 resolution) |
| Native Rust P2P substrate completion | Deferred to Window 1459+ (Q3 resolution) |
| Werner flow-governor CDL | Deferred to Window 1459+ (Q5 resolution) |

---

## 3. Resolved §8 Decisions — Locked

All five open questions from the Window 1429-1458 forward plan have been resolved by the human reviewer and are locked here.

| Token | Decision summary |
|-------|-----------------|
| `q1_rehearsal_identity_continuity_resolved_keys_preserved_rc_fresh_start` | Phase 1431 generates 7 production keypairs; keys saved off-machine; rehearsal state wiped; public RC re-initializes via fresh ADR-0038/ADR-0041 using the same preserved keys |
| `q2_gap_14_parallel_with_c_governance_required_before_1436` | Gap 14 runs parallel with Track C phases 1434-1435; must complete before Phase 1436 |
| `q3_openclaw_harness_p2p_phase_1437_native_rust_deferred_window_1459_plus` | Phase 1437 = OpenClaw harness-assisted P2P via CDL-078 relay; native Rust P2P substrate deferred to Window 1459+ |
| `q4_adr_0035_deferred_window_1459_plus_not_rc_blocker` | ADR-0035 fully deferred to Window 1459+; Track E removed from Window 1429-1458 critical path |
| `q5_werner_diagnostic_wiring_track_h1_nons_flow_governor_cdl_deferred_1459_plus` | Single NON-SENSITIVE Werner diagnostic wiring phase added (Track H1); flow-governor CDL deferred to Window 1459+ |

---

## 4. Locked Phase Table (1429-1458)

Approximate phase numbers for tracks after C4. Exact number assignments are confirmed as each phase prompt is approved. Gap 14 phases run in parallel with Track C governance and use letter suffixes.

| Order | Phase | Scope | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| A1 | 1429 | Production assignment activation — flip `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED = False`; verify J-008 gate still PASS | Runtime | **SENSITIVE** |
| A2 | 1430 | CDL-053 Werner local credit first wire to maintenance lottery stub | Runtime | NON-SENSITIVE |
| B1 | 1431 | Rehearsal agent identity ceremony — 7 production keypairs via ADR-0038/ADR-0041 INIT; keys off-machine; FINDING-9 domain separator fix before ceremony | Identity | **SENSITIVE** |
| B2 | 1432 | Private rehearsal infrastructure validation — 3-machine 7-agent topology; scripted agents; Phase 1 synthetic dataset; OpenClaw P2P path tested | Rehearsal | NON-SENSITIVE |
| B3 | 1433 | Private rehearsal verdict — Phase 2 Lean Mathlib dataset; PASS/FAIL verdict; wipe right exercised after PASS | Rehearsal | conditional |
| C1 | 1434 | TransportPrincipal CDL opening (Gap 10) | Constitutional | **SENSITIVE** |
| C2 | 1435 | TransportPrincipal CDL prelock + ratification | Constitutional | **SENSITIVE** |
| G14a | ~1436a | Gap 14 Phase 1 — modular package profile definition (parallel with C governance) | Runtime | NON-SENSITIVE |
| G14b | ~1436b | Gap 14 Phase 2 — public RC profile, OpenClaw/NemoClaw hosted profile | Runtime | NON-SENSITIVE |
| C3 | 1436 | Non-loopback sidecar/projection + public fetch serving activation (requires Gap 14 complete + Phase 1435) | Runtime | NON-SENSITIVE |
| C4 | 1437 | OpenClaw harness-assisted P2P activation (CDL-078 relay; validated Phase 1432; native Rust P2P deferred to Window 1459+) | Runtime | **conditional SENSITIVE** |
| D1 | ~1438 | ECU-to-ILC conversion runtime activation + CDL-088 activation | Runtime | **SENSITIVE** |
| D2 | ~1439 | Public verifier API activation | Runtime | NON-SENSITIVE |
| D3 | ~1440 | Claimability integration tests + security review (FINDING-1, FINDING-11, FINDING-13, FINDING-14) | Testing | NON-SENSITIVE |
| D4 | ~1441 | Gap 13 closure verdict | Gate | NON-SENSITIVE |
| H1 | ~1442 | Werner diagnostic wiring — default-off systolic/diastolic/pulse-pressure metrics; review lane only; no CDL, no ECU, no wallet | Runtime | NON-SENSITIVE |
| F1 | ~1443 | AGPL license header audit + public-source allowlist execution | Compliance | NON-SENSITIVE |
| F2 | ~1444 | CLA text finalization | Governance | **SENSITIVE** |
| F3 | ~1445 | Gap 7 partial closure + external-action carry-forward record | Gate | NON-SENSITIVE |
| G1 | ~1446 | v0.3 Genesis root envelope signing ceremony | Identity / Release | **SENSITIVE** |
| G2 | ~1447 | Release artifact signing + manifest finalization | Release | **SENSITIVE** |
| G3 | ~1448 | Public repository publication | Publication | **SENSITIVE** |
| G4 | ~1449 | External operator bootstrap guide publication | Documentation | NON-SENSITIVE |
| G5 | ~1450 | Public RC activation certificate + epoch 1 trigger | **Launch** | **SENSITIVE** |
| Z1 | ~1451 | Window coherence + capsule update + ADR housekeeping (FINDING-5, FINDING-15) | Synthesis | NON-SENSITIVE |
| Z2 | ~1452 | Window 1429-1458 closure gate | Gate | **SENSITIVE** |

**Contingency:** Phases 1453-1458 are held as contingency slots for rehearsal remediation (if verdict=FAIL at Phase 1433), P2P fallback work, or other unforeseeable blockers.

---

## 5. Dependency Tree

```
Phase 1427 (J-008 PASS, Window 1399-1428 commit 0876cae8)
  └── 1429 (production assignment activation)  [SENSITIVE]
       └── 1430 (CDL-053 local credit wire)  [NON-SENSITIVE]
            └── 1431 (rehearsal identity ceremony)  [SENSITIVE — GO required]
                 └── 1432 (rehearsal infra validation + OpenClaw P2P test)  [NON-SENSITIVE]
                      └── 1433 (rehearsal verdict + wipe right)  [conditional]
                           |
                           ├── C track (sequential, on critical path):
                           |    1434 (TransportPrincipal CDL opening)  [SENSITIVE — GO required]
                           |    └── 1435 (TransportPrincipal CDL ratification)  [SENSITIVE — GO required]
                           |         ├── [parallel] Gap 14: ~1436a -> ~1436b  [NON-SENSITIVE]
                           |         └── 1436 (sidecar/projection + public fetch)  ← requires Gap 14 complete
                           |              └── 1437 (OpenClaw P2P)  [conditional SENSITIVE — GO required if CDL needed]
                           |
                           ├── D track (after rehearsal verdict):
                           |    ~1438 (CDL-088 activation)  [SENSITIVE — GO required]
                           |    └── ~1439 (public verifier API)
                           |         └── ~1440 (claimability tests + security review)
                           |              └── ~1441 (Gap 13 closure)
                           |
                           ├── H1 track (~1442, parallel, NON-SENSITIVE, before ~1446):
                           |    Werner diagnostic wiring
                           |
                           └── F track (after rehearsal verdict):
                                ~1443 (license audit) -> ~1444 (CLA) -> ~1445 (Gap 7 partial)
                                     |
                                     └── ALL tracks must complete before Track G:
                                          ~1446 (v0.3 signing)  [SENSITIVE — GO required]
                                          └── ~1447 (release signing)  [SENSITIVE — GO required]
                                               └── ~1448 (public publication)  [SENSITIVE — GO required]
                                                    └── ~1449 (operator guide)
                                                         └── ~1450 (epoch 1 trigger)  ← PUBLIC RC  [SENSITIVE — GO required]
                                                              └── ~1451 (coherence)
                                                                   └── ~1452 (closure gate)  [SENSITIVE — GO required]
```

---

## 6. SENSITIVE Phases — GO Token Required

These phases require explicit human `GO Phase NNNN` before execution:

| Phase | Sensitivity basis |
|-------|------------------|
| 1429 | Activates production jury assignment machinery |
| 1431 | Creates protocol cryptographic identities (production keypairs) |
| 1434 | Opens new constitutional CDL lane (TransportPrincipal) |
| 1435 | Ratifies TransportPrincipal CDL |
| 1437 | Conditional: SENSITIVE if new CDL governance required for OpenClaw P2P binding |
| ~1438 | Activates live value path (CDL-088, ECU-to-ILC conversion) |
| ~1444 | CLA text is Genesis-authority governance policy publication |
| ~1446 | Genesis signing ceremony — canonical artifact chain |
| ~1447 | Signs release artifacts against v0.3 root envelope |
| ~1448 | Public source publication |
| ~1450 | Epoch 0-to-1 transition trigger — PUBLIC RC LAUNCH |
| ~1452 | Window closure gate |

CDL mutation phases (1434, 1435, and any CDL-governing subphase) require:
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<phase>
```

---

## 7. CDL Number Assignments

| CDL | Scope | Register opening | Ratification |
|-----|-------|-----------------|--------------|
| CDL-094 | TransportPrincipal public-path governance (Gap 10) | Phase 1434 | Phase 1435 |

Next fresh CDL number after this window: **CDL-095** (subject to fix-series openings)

**Note:** ADR-0035 CDL was planned as CDL-094 in earlier drafts. That assignment is released; CDL-094 is reassigned to TransportPrincipal governance. ADR-0035 CDL number is assigned in Window 1459+ sequence lock.

---

## 8. Non-Authorizations

This sequence lock does not authorize:

- Production jury assignment execution beyond Phase 1429 activation (activation itself authorized, execution gated by gate machinery)
- Live ECU distribution via maintenance lottery (MAINTENANCE_LOTTERY_NOT_ACTIVATED remains True until separate GO)
- VRF production key generation or proof generation (Phase 1431 generates agent identity keypairs, not VRF signing keys; these are distinct)
- Public RC publication or source repository publication (gated on Track G)
- Epoch 0-to-1 transition (gated on ~1450 GO token)
- Native Rust P2P substrate work (deferred to Window 1459+)
- ADR-0035 homoiconic type system implementation (deferred to Window 1459+)
- Werner flow-governor CDL (deferred to Window 1459+)
- Production minting, production ILC settlement
- Any CDL mutation beyond CDL-094 TransportPrincipal

---

## 9. Deferred Finding Resolution Schedule

From Phase 1410 audit (inherited from forward plan §9):

| Finding | Phase assigned | Rule |
|---------|---------------|------|
| FINDING-9 | Before Phase 1431 (identity ceremony) | Must fix domain separator v1/v2 collision before any identity creation |
| FINDING-7 | Phase 1413 (assigned and closed — retroactive closure record added to Phase 1413 walkthrough) | O(n) filter in `_select_outsider`; set-based implementation confirmed present in `jury_assignment_runtime.py`; formal closure record was absent from Phase 1413 walkthrough; added retroactively |
| FINDING-1 | Phase ~1440 (claimability integration tests) | Rounding residual unrouted path |
| FINDING-3 | Phase ~1440 (claimability integration tests) | PRICE_CLAMP_WIDTH hardcoded |
| FINDING-11 | Phase ~1440 (claimability integration tests) | No expire_stale_records() in claim nullifier registry |
| FINDING-13 | Phase ~1440 (claimability integration tests) | Negative integer documentation |
| FINDING-14 | Phase ~1440 (claimability integration tests) | shutil.rmtree provenance guard |
| FINDING-5 | Phase ~1451 (coherence) | Dead branch cleanup |
| FINDING-15 | Phase ~1451 (coherence) | discover_epoch_event_dirs MAX_RECORDS cap |

**Execution rule:** No finding may be deferred past its assigned phase without explicit human authorization and a new deferral record.

---

## 10. Canonical Anchors

- `docs/specs/ilc_window_1429_1458_public_rc_activation_forward_plan_v0.1.md` — forward plan (updated 2026-05-21 with Q1-Q5 resolutions)
- `docs/specs/ilc_window_1399_1428_handoff_1428_v0.1.md` — prior window handoff
- `docs/specs/ilc_phase_1399_1428_sequence_lock_v0.1.md` — prior sequence lock
- `ilc_core/epistemic/jury_activation_gate.py` — J-008 gate (PASS, `PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED=False`)
- `ilc_core/epistemic/jury_assignment_runtime.py` — `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED=True` until Phase 1429
- `docs/specs/ilc_private_soft_rc_rehearsal_criteria_1423_v0.1.md` — rehearsal entry criteria
- `docs/specs/ilc_activation_certificate_v1_design_1424_v0.1.md` — epoch 1 trigger design
- `docs/specs/ilc_launch_readiness_manifest_schema_1422_v0.1.md` — launch readiness manifest schema
- `docs/specs/ilc_production_jury_activation_gate_pass_1427_v0.1.md` — J-008 PASS evidence

---

## 11. Final Closure Routing (anticipated)

Window 1429-1458 will be closed by:

```text
docs/specs/ilc_window_1429_1458_handoff_<closing_phase>_v0.1.md
window_1429_1458_closed_phase_<closing_phase>
window_1429_1458_closure_verdict_recorded
mempalace_refresh_disposition_recorded
public_rc_activated_epoch_1_triggered   (if Track G completes)
go_window_1459_plus_required_next
```

No phase after this window's closing phase is authorized by this sequence lock. Window 1459+ requires a new formal sequence lock and explicit human GO.
