# ILC CDL-088 Public Claimability Authority Opening 1374 v0.1

**CDL number:** CDL-088
**Title:** Public Claimability Authority
**Status:** OPEN
**Phase:** 1374
**Date:** 2026-05-18
**Human authorization:** `GO Phase 1374` plus `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1374`

```text
cdl_088_public_claimability_opened_phase_1374
cdl_088_not_ratified_phase_1374
cdl_088_bounded_claimability_candidate_scope_phase_1374
```

---

## 1. Opening Statement

CDL-088 is opened in Phase 1374 as the public claimability authority CDL.

This opening creates the constitutional deliberation lane for any future public
claimability endpoint, public verifier API, or user-facing ILC claim path. It
does not ratify CDL-088, does not lock final scope, and does not activate public
claimability.

Phase 1375 must produce the deliberation/prelock record before Phase 1376 may
ratify CDL-088.

---

## 2. Predecessor Authority

| Source | Use in CDL-088 opening |
| --- | --- |
| `docs/specs/ilc_cdl_086_public_launch_packaging_blocker_opening_1194_v0.1.md` | Public launch, public release, counsel, packaging, signing, and distribution authority remain separately gated. |
| `docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md` | Fetch distribution is ratified, but public fetch serving, public sidecar/projection serving, reciprocal scoring, ECU-escrow admission, and CDL-088 remained separately gated. |
| `docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md` | Identity bootstrap governance is ratified, but public identity activation and public claimability remain separately gated. |
| `docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md` | Records CDL-088 as pre-reserved for public claimability authority and requires explicit `GO Phase 1374`. |
| Phase 1388 counsel clearance prerequisite | Public value-path and public verifier API activation require later counsel-clearance handling before any activation gate may pass. |
| Phase 1389 public claimability gate | Public claimability activation remains a future explicit-GO gate; this opening does not produce `result=public_claimability_activated`. |

---

## 3. Candidate Scope For Phase 1375 Deliberation

CDL-088 opens these candidate scope areas for Phase 1375:

1. **Bounded public claimability authority**
   - Define the exact condition-bounded or time-bounded authority needed before
     a public claim endpoint or public verifier API can be opened.
   - Determine what proof bundle must exist before any public claimability gate
     can pass.

2. **Reciprocal scoring, if included**
   - Determine whether contributor-identity scoring and claim scoring must be
     interlocked before public claimability can activate.
   - Determine whether reciprocal scoring is a CDL-088 requirement, a Phase
     1389 gate input, or an explicitly deferred post-RC item.

3. **ECU-escrow admission, if included**
   - Determine whether ECU escrow is a prerequisite for public claim admission.
   - Determine what escrow proof, custody boundary, and non-custodial user flow
     would be required if this path remains in scope.

4. **Public verifier API boundary**
   - Confirm whether CDL-088 governs only constitutional claimability authority
     or also locks minimum public-verifier API acceptance prerequisites.
   - Keep public serving, route activation, listeners, wallet-facing actions,
     ECU minting, ILC settlement, and value-path activation out of Phase 1374.

---

## 4. Open Questions For Phase 1375

Phase 1375 must resolve at least these questions:

| Question | Phase 1374 posture |
| --- | --- |
| Is reciprocal scoring in CDL-088 scope? | Open for deliberation. |
| Is ECU-escrow admission in CDL-088 scope? | Open for deliberation. |
| What exactly constitutes bounded public claimability? | Open for deliberation. |
| What proof bundle must exist before a public claim endpoint can activate? | Open for deliberation. |
| Does CDL-088 impose a condition-bounded window, epoch-bounded window, operator quorum, counsel precondition, or all of these? | Open for deliberation. |
| Which items are CDL-088 ratification requirements versus Phase 1389 activation-gate requirements? | Open for deliberation. |

---

## 5. Rejected Candidates

The following candidates are rejected at opening:

1. Unbounded public claimability with no conditions.
2. Claimability before Phase 1389 gate passes.
3. Treating CDL-088 opening as claim endpoint activation.
4. Treating CDL-088 opening as public verifier API activation.
5. Treating CDL-088 opening as wallet-facing withdrawal, transfer, or spend
   authority.
6. Treating identity bootstrap ratification as sufficient for public
   claimability.
7. Treating public fetch distribution ratification as sufficient for public
   claimability.

---

## 6. Non-Goals And Non-Authorization Boundary

This opening does not authorize:

1. CDL-088 prelock.
2. CDL-088 ratification.
3. Public claimability activation.
4. Public verifier API activation.
5. Claim endpoint activation.
6. Public HTTP route activation.
7. Public socket listener or non-loopback bind.
8. Wallet-facing withdrawal, transfer, or spend behavior.
9. Wallet-provider signing.
10. Wallet-provider ledger writes.
11. ECU minting.
12. ILC settlement.
13. Value-path activation.
14. Public RC publication.
15. Public launch.
16. Source publication.
17. Release artifact production.
18. Release signing.
19. Production validator deployment.
20. Production governance execution.
21. Production minting or production-minted ILC.
22. Runtime mutation in `ilc_core/`.

Non-ratification token:

```text
cdl_088_not_ratified_phase_1374
```

---

## 7. Register Mutation

Phase 1374 adds the pre-reserved CDL-088 row to the CDL register with status
`open`.

The CDL-088 row records:

```text
opened_phase: 1374
opened_date: 2026-05-18
opening_token: cdl_088_public_claimability_opened_phase_1374
historical_non_ratification_token: cdl_088_not_ratified_phase_1374
candidate_scope_token: cdl_088_bounded_claimability_candidate_scope_phase_1374
prelock_status: deferred_to_phase_1375
ratification_status: not_ratified_phase_1374
public_claimability_activation_status: not_enabled
claim_endpoint_status: not_enabled
runtime_activation_status: not_authorized
```

---

## 8. Phase 1375 Handoff

Phase 1375 must deliberate and prelock the candidate scope rather than treating
this opening as final scope closure.

Carry-forward:

```text
phase_1375_cdl_088_deliberation_prelock_next
```
