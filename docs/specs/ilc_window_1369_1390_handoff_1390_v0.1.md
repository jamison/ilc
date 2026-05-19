# ILC Window 1369-1390 Handoff 1390 v0.1

Status: handoff artifact
Date: 2026-05-19
Classification: closure and carry-forward handoff

```text
window_1369_1390_closed_phase_1390.v0.1
window_1369_1390_closure_verdict_recorded_phase_1390
mempalace_refresh_disposition_recorded_phase_1390
window_1391_not_open_phase_1390
go_window_1391_required_next
```

## 1. Window identity and closure basis

Window 1369-1390 is closed by Phase 1390 after explicit human authorization:

```text
GO Phase 1390
```

Closure basis:

| Basis | Artifact | Result |
|-------|----------|--------|
| Window sequence lock | `docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md` | confirmed |
| Candidate grouping | `docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md` | confirmed |
| Closure schema | `docs/specs/ilc_window_closure_handoff_doc_schema_v0.1.md` | followed |
| Final public-claimability gate verdict | `docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md` | `result=public_claimability_activated` |
| STATUS frontier | `docs/phases/STATUS.md` | confirmed through Phase 1389 rerun |

The closure is an honest handoff artifact. It does not open Window 1391, mutate
the CDL register, mutate runtime code, publish public RC artifacts, start public
serving, sign releases, mint ECU, settle ILC, launch mainnet, claim external
legal advice, or record a legal conclusion.

## 2. Inputs and closure inheritance

| Input | Closure inheritance |
|-------|---------------------|
| `docs/specs/ilc_window_1343_1368_handoff_1368_v0.1.md` | Prior window closed; production minting remained deferred. |
| `docs/specs/ilc_antigravity_context_capsule_v5.58.md` | Active capsule at Window 1369 entry; not superseded by Phase 1390. |
| `docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md` | Locked order and public claimability gate discipline for this window. |
| `docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md` | Phase inventory, tail-slot policy, and Phase 1390 closure routing. |
| `docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md` | CDL-090 identity bootstrap ratified. |
| `docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md` | CDL-088 public claimability authority ratified. |
| `docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md` | Phase 1387 hardening gate passed after the 1387-Fix chain. |
| `docs/specs/ilc_accepted_adr_cdl_public_rc_coverage_matrix_1387a_v0.1.md` | Accepted ADR/CDL public-RC coverage matrix complete. |
| `docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md` | Public-only economics admission firewall complete. |
| `docs/specs/ilc_counsel_clearance_1388_v0.1.md` | CDL-048 activation and internal self-counsel prerequisite closed for testnet/pre-production scope. |
| `docs/specs/ilc_public_claimability_activation_gate_report_1389_v0.1.md` | Historical failed-closed Phase 1389 report retained as evidence. |
| `docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md` | Current Phase 1389 routing verdict: `result=public_claimability_activated`. |

CDL chain inherited at closure:

| CDL | Window 1369-1390 status |
|-----|--------------------------|
| CDL-088 | Opened in Phase 1374, prelocked in Phase 1375, ratified in Phase 1376; later consumed by Phase 1389a and Phase 1389 rerun. |
| CDL-089 | Inherited ratified from Window 1343-1368. |
| CDL-090 | Opened in Phase 1371, prelocked in Phase 1372, ratified in Phase 1373; consumed by Phase 1389 prerequisite checks. |

## 3. Closure verdict summary

Overall verdict:

```text
window_1369_1390_closure_verdict=closed_with_carry_forward
phase_1389_public_claimability_result=result=public_claimability_activated
```

Main locked sequence:

| Phase | Topic | Status | Commit hash |
|-------|-------|--------|-------------|
| 1369 | Sequence lock + Capsule v5.58 | complete | `4a918075` |
| 1369 Fix1 | Numeric/runtime hardening | complete | `65531719` |
| 1370 | ADR-0038 agent birth attestation | complete | `794df06e` |
| 1371 | CDL-090 identity bootstrap opening | complete | `580bf148`; walkthrough `ef1aebb9` |
| 1372 | CDL-090 prelock | complete | `9b62237f` |
| 1373 | CDL-090 ratification | complete | `ff841ad2`; walkthrough `d93a1009` |
| 1374 | CDL-088 opening | complete | `43bcddc0`; walkthrough `801c8b98` |
| 1375 | CDL-088 prelock | complete | `287cbcf5` |
| 1376 | CDL-088 ratification | complete | `3d8ce11e`; walkthrough `4a37f379` |
| 1377 | Replay/nullifier and duplicate-claim policy | complete | `4f9715c6` |
| 1378 | Legacy `/v1/public/*` FastAPI route cleanup | complete | `29f11571` |
| 1379 | ADR-0031 sidecar query runtime completeness | complete | `014f4664` |
| 1380 | CDL-048 dry-run wiring | complete | `2c7a32ed` |
| 1381 | CDL-006 challenge-node spec and stub | complete | `ad1a7c50` |
| 1382 | CDL-006 challenge-node runtime | complete | `b46496bf` |
| 1383 | CDL-009 fork-legitimacy UX | complete | `1992111e` |
| 1384 | Security review scope | complete | `a51f8599` |
| 1385 | TLA+ SafetyNoDualCert disposition | complete; deferral later closed | `109112a4`; backfill `b8f2dd5c` |
| 1385a | Spec D epoch-checkpoint SafetyNoDualCert Strike Force | complete | `bd3cd896` |
| 1386 | Genesis validator bootstrap exception record | complete | `9dc5cd1d` |
| 1386a | Production TLS gRPC proof | complete | `858cc8b2` |
| 1386b | Validator endpoint registry ADR-0039 | complete | `ffd7dd88` |
| 1386c | Persistent QUIC connectivity proof | complete | `020ae5b8` |
| 1387 | Pre-activation hardening gate | failed closed, then rerun pass | v0.1 `c3521636`; rerun `df18e921`; fix chain `4ebf12f5`, `fd99b5be`, `daea0626`, `5f5a6d7e`, `38787d6b` |
| 1387a | Accepted ADR/CDL coverage and public-economics firewall | complete | `290f5a70` |
| 1388 | CDL-048 activation and counsel clearance | failed closed, then rerun complete | blocked `9b5e9b7c`; rerun `17b844a6` |
| 1388a | CDL-048 self-counsel clearance | complete | `3829890e` |
| 1389 | Public claimability/API activation gate | v0.1 failed closed; v0.2 rerun pass | v0.1 `7cd16204`; rerun `449f0e95`; backfill `65896516` |
| 1389a | Claimability public-mode governance decisions | complete | `2f48c1fc`; backfill `cabe2616` |
| 1389b | Claimability public-mode runtime | complete | runtime `aed33474`; docs `dcdb9543`; backfill `fdda9b7a` |
| 1390 | Window closure handoff | complete by this artifact | `43401835` |

Additional support-lane work observed inside the same frontier:

| Phase | Topic | Status | Commit hash |
|-------|-------|--------|-------------|
| 1387b | SIM-GENESIS-COMPILE-02 | complete; walkthrough exists | `3b6b7fef`; `6e478f23` |
| 1387c | Compiler transition basis expansion | complete by STATUS; incomplete — no walkthrough file found | `ecca6b9b` |
| 1387d | ADR-0035 formal spec | complete; walkthrough exists | `6b88e034` |
| 1387e | Star map expansion | complete; walkthrough exists | `8fbcf6b7` |
| 1387f | SIM-GRAPHOPT-01 graph structure analysis | complete by STATUS; incomplete — no walkthrough file found | `504d46a8` |
| 1387g | SIM-GRAPHOPT-02 epistemic leverage analysis | complete by STATUS; incomplete — no walkthrough file found | `3ed04fed` |
| 1387h | SIM-GRAPHOPT-03 edge recipe canonicalization | complete by STATUS; incomplete — no walkthrough file found | `afb46c44` |
| 1387i | SIM-GRAPHOPT synthesis report | complete by STATUS; incomplete — no walkthrough file found | `976ae6e9` |
| 1387j | Signed-artifact hygiene restoration | complete by STATUS; incomplete — no walkthrough file found | `4750b00b` |

Phase 1389 result, verbatim:

```text
result=public_claimability_activated
```

The Phase 1389 v0.2 gate report explicitly preserves the boundary that the
rerun does not start a public HTTP server, add a public claim endpoint, publish
public RC artifacts, perform wallet actions, mint ECU, settle ILC, or launch
mainnet.

## 4. Carry-forward items and residual blockers

Closed and not carried forward:

| Item | Closure evidence |
|------|------------------|
| CDL-090 identity bootstrap governance | Ratified in Phase 1373. |
| CDL-088 public claimability authority | Ratified in Phase 1376 and consumed by Phase 1389a/v0.2. |
| Legacy `/v1/public/*` FastAPI route cleanup | Closed by Phase 1378. |
| ADR-0031 sidecar query completeness | Closed by Phase 1379. |
| CDL-006 challenge-node spec/runtime | Closed by Phases 1381-1382. |
| CDL-009 fork legitimacy UX | Closed by Phase 1383. |
| Epoch-checkpoint SafetyNoDualCert formal proof | Closed by Phase 1385a Spec D exhaustive TLC result. |
| Phase 1387 hardening gate | Closed by rerun after 1387-Fix chain. |
| Phase 1389 public-mode blockers | Closed by Phases 1389a, 1389b, and 1389 rerun v0.2. |

Carried forward to Window 1391+ or later:

| Item | Phase origin | Window 1391+ obligation |
|------|--------------|--------------------------|
| Public RC publication, source export, package upload, OpenClaw/ClawHub listing, and release signing | Phase 1389/1390 boundary | Requires separate publication/release/signing authorization. Phase 1390 does not publish or sign anything. |
| Public HTTP verifier/claim endpoint serving | Phase 1389 rerun non-authorization | Define and activate serving separately if desired; Phase 1389 activated the gate verdict, not a live HTTP route. |
| Soft-RC full gate rerun | Phase 1366/1367 inheritance | Phase 1367 fixed the named treasury-budget blocker, but no later full soft-RC gate recorded `soft_rc_eligible=true`. |
| Production minting | Phase 1368 inheritance | Remains deferred; no production minting activation in Window 1369-1390. |
| Mainnet split-custody ceremony | Phase 1386 | `production_split_custody_ceremony_required_before_mainnet_launch` remains a mainnet-launch obligation. |
| MEDIUM-007 anti-equivocation tombstones | Phase 1387-Fix | Accepted carry-forward; LMDB execution-level safety remains maintained, but tombstone design is future work. |
| MEDIUM-008 endpoint edge crypto | Phase 1387-Fix | Accepted carry-forward; endpoint-edge cryptographic hardening remains future work. |
| v0.3 candidate signing ceremony | Phase 1387j | Required before making signed Genesis graph coverage claims over the 54-node/v0.3 candidate state. |
| 1387c/f/g/h/i/j walkthrough backfill | Phase 1390 discovery | STATUS and commits exist, but no matching walkthrough files were found; backfill or explicitly waive before relying on them as walkthrough-complete support phases. |
| J-series jury/epoch-work continuation | Phase 1391+ pre-work | J-001/J-002/J-003/J-003a/J-004 already exist as side-lane artifacts; Phase 1390 does not open or close Window 1391+. Continue only under explicit future GO. |
| J-007 ingestion shadow harness prerequisite | ADR-0041 | ADR-0041 must be consumed before J-007 shadow ingestion harness execution. |
| Mode-2 refutation settlement details | J-series planning | Stake calibration, CDL-029 allocation wiring, novelty spec, and Mode-3 escalation remain visible J-series obligations. |

Blocked items requiring future routing:

| Blocked item | Required future routing |
|--------------|-------------------------|
| Public RC publication claim | Needs explicit publication/release/signing gate. |
| Mainnet launch | Needs mainnet-specific launch planning, split custody, production deployment, and any then-required legal/governance dispositions. |
| Public wallet/value operations beyond the committed pre-production activation path | Needs separate wallet/value-path activation authority and tests. |

## 5. Next-window entry criteria and routing

```text
window_1391_not_open_phase_1390
go_window_1391_required_next
```

Window 1391+ may assume:

| Assumption | Basis |
|------------|-------|
| Window 1369-1390 is closed with carry-forward | This handoff. |
| Phase 1389 public claimability gate verdict is pass | `docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md`. |
| CDL-088 and CDL-090 are ratified | Phase 1376 and Phase 1373 evidence. |
| Phase 1387/1387a/1388 prerequisites are closed | Rerun reports and runtime/docs artifacts. |
| Spec D epoch-checkpoint SafetyNoDualCert exists | Phase 1385a TLA/TLC artifacts. |

Window 1391+ must not assume:

| Non-assumption | Reason |
|----------------|--------|
| Public RC is published | No publication, source export, package upload, OpenClaw/ClawHub listing, or release signing occurred. |
| Public HTTP claimability serving is live | Phase 1389 rerun explicitly did not start serving or add public routes. |
| Mainnet is launched | No mainnet launch or production validator deployment occurred. |
| Production minting is active | Production minting remains deferred. |
| External legal advice exists | The project uses self-counsel artifacts in this scope; no external legal opinion was claimed. |

Next routing:

| Route | Condition |
|-------|-----------|
| Open Window 1391+ | Requires explicit human `GO Window 1391` or equivalent next-window authorization. |
| Continue J-series | Requires explicit phase-level GO and should reconcile side-lane J artifacts already committed before this closure. |
| Public RC publication/release | Requires separate publication, release signing, and packaging authorization. |
| Mainnet launch | Requires separate mainnet launch planning, split custody resolution, and production-deployment authority. |

## 6. MemPalace refresh disposition

- `Disposition:` `required`
- `Active working set impacted:` `yes`
- `Basis:` Window 1369-1390 closed, the Phase 1389 public claimability gate verdict changed from historical failed-closed to v0.2 pass, and Window 1391+ routing now has explicit carry-forward obligations. The authoritative frontier and retrieval surface changed enough to justify rebuilding the active MemPalace working set after this closure commit.
- `Working-set descriptor:` `docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json`
- `Manifest:` `docs/tools/mempalace/ilc_mempalace_current_frontier_manifest_v0.1.json`
- `Rebuild command:` `bash tools/mempalace/build_active_working_set.sh`

MemPalace remains advisory retrieval only. This handoff is based on direct repo
reads of the schema, STATUS, planning docs, gate reports, and walkthrough files.
