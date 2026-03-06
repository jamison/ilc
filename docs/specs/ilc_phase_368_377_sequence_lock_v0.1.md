# ILC Phase 368-377 Sequence Lock v0.1

Status: Phase-368 sequence lock artifact  
Date: 2026-03-06  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and window character

Window 368-377 is a governance-first window that hardens constitutional boundaries before any expanded runtime authorization.

Governance-first track: phases 368-374.
Implementation-boundary track: phases 375-377, bounded by V-series runtime enforcement authorization only.

## 2. Entry state from phase-367 closure

Entry assumptions:
- Window 358-367 closure passed with `phase_367_verdict=pass`.
- `CDL-034` through `CDL-038` runtime implementation tranches completed in phases 360-364.
- `CDL-039` remains open and implementation-barred.
- Phase 368 is non-ratifying and non-runtime.

## 3. Constitutional inventory and open lanes

Constitutional carry-forward inventory:
- `CDL-034`: ratified
- `CDL-035`: ratified
- `CDL-036`: ratified
- `CDL-037`: ratified
- `CDL-038`: ratified
- `CDL-039`: open

Open-lane constraints:
- CDL-039 remains open in Window 368-377; prelock finalization target is Phase 374.
- No CDL-039 ratification action is authorized in Window 368-377.

## 4. Locked phase table (368-377)

| Order | Phase | Scope | Sensitivity |
| --- | --- | --- | --- |
| 1 | Phase 368 | sequence lock + governance/runtime boundary lock | non-sensitive |
| 2 | Phase 369 | SIM-004 commissioning | non-sensitive |
| 3 | Phase 370 | SIM-005 commissioning | non-sensitive |
| 4 | Phase 371 | SIM-004/005 interpretation and risk closure | non-sensitive |
| 5 | Phase 372 | CDL-039 prelock topology/privacy hardening | sensitive |
| 6 | Phase 373 | CDL-039 prelock adversarial review and evidence freeze | sensitive |
| 7 | Phase 374 | CDL-039 prelock finalization (sensitive, non-ratifying) | sensitive |
| 8 | Phase 375 | V-series implementation window sequence lock (non-sensitive, no runtime) | non-sensitive |
| 9 | Phase 376 | coherence + capsule v1.2 | non-sensitive |
| 10 | Phase 377 | closure gate and 378+ handoff | sensitive |

## 5. Phase sensitivity classification

- `Phase 368`: non-sensitive
- `Phase 369`: non-sensitive
- `Phase 370`: non-sensitive
- `Phase 371`: non-sensitive
- `Phase 372`: sensitive
- `Phase 373`: sensitive
- `Phase 374`: sensitive
- `Phase 375`: non-sensitive
- `Phase 376`: non-sensitive
- `Phase 377`: sensitive

## 6. Governance-first track (368-374)

Governance-first first-half objectives:
- lock sequence and constitutional boundary behavior,
- commission and interpret simulation evidence for CDL-039 prelock hardening,
- finalize CDL-039 prelock structure without ratification.

Scope anchors:
- SIM-004 models network partition resilience and CDL-039 connectivity failure modes.
- SIM-005 models agent death and graph orphaning behavior under protocol conditions.

## 7. Implementation track boundary (375-377)

Second-half boundary:
- no D2d runtime implementation work is authorized in this window,
- any implementation-boundary work is limited to V-series runtime enforcement authorization planning,
- coherence and closure complete the window with carry-forward bounded to Window 378.

## 8. CDL-039 prelock finalization boundary

CDL-039 lane boundaries:
- prelock hardening and adversarial review occur in phases 372-373,
- prelock finalization target is phase 374,
- ratification is explicitly deferred beyond Window 368-377.

## 9. V-series runtime activation boundary

V-series activation policy for this window:
- CDL-V1 through CDL-V7 runtime activation decision is bounded to computational enforcement surfaces only.
- CDL-V4, CDL-V5, CDL-V6 remain governance-procedural and are implementation-barred unless explicitly reclassified.

## 10. D2d deferral and Levin-evaluation boundary

D2d carry-forward rules:
- D2d runtime implementation remains deferred to Window 378+.
- No P2P peering loop, routing loop, or gossip runtime implementation is authorized in Window 368-377.
- Window 368 sequence-lock drafting must evaluate Levin gossip + coordinate mechanism proposals as D2d wire-protocol inputs.
- Phase 368 records Levin proposals as carry-forward design inputs; detailed mechanism evaluation is scheduled for Phase 372 topology/privacy hardening.

## 11. Non-goals and explicit exclusions

Out of scope for Window 368-377 sequence lock:
- any decision-log mutation in Phase 368,
- any `ilc_core/` runtime mutation in Phase 368,
- CDL-039 ratification actions,
- D2d runtime implementation (peering/routing/gossip loop code).

## 12. Forward pointer

Window 378 begins with D2d runtime implementation authorization review.
