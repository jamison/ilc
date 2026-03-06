# ILC Phase 378-391 Sequence Lock v0.1

Status: Phase-378 sequence lock artifact  
Date: 2026-03-06  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and runtime transition character

Window 378-391 is the Runtime Transition Block.

This sequence lock defines the constitutional/runtime transition from Window 368-377 outputs into ratification, network runtime implementation, V-series authorization, and closure-gate delivery for Window 392+ handoff.

Phase 378 is a scope declaration, not the implementation authorization source of truth for V-series runtime work.

## 2. Entry state from window 368-377 closure

Entry assumptions from closure:
- `phase_377_verdict=pass` and Window 368-377 is closed.
- `CDL-034` through `CDL-038` are ratified.
- `CDL-039` is open and prelock-finalized, not ratified.
- Phase 378 is non-sensitive and non-ratifying.

## 3. Constitutional inventory and unresolved lanes

Constitutional carry-forward inventory:
- `CDL-034`: ratified
- `CDL-035`: ratified
- `CDL-036`: ratified
- `CDL-037`: ratified
- `CDL-038`: ratified
- `CDL-039`: open

Unresolved/open lanes for this window:
- `CDL-040`: not opened yet
- `CDL-041`: not opened yet
- `CDL-042`: deferred by scope boundary
- `CDL-043`: not opened yet

CDL-039 ratification is authorized in Phase 379 based on the Phase 374 prelock finalization package.

The Phase 379 ratification artifact must contain a dedicated section headed with a ## heading containing the word calibration (case-insensitive). Calibration constants resolution text must appear within that section and not in prose outside it. This structural requirement enables section-scoped parsing by the Phase 391 closure gate.

## 4. Locked phase table (378-391)

| Order | Phase | Scope | Sensitivity |
| --- | --- | --- | --- |
| 1 | Phase 378 | window + V-series scope declaration sequence lock | non-sensitive |
| 2 | Phase 379 | CDL-039 ratification | sensitive |
| 3 | Phase 380 | D2d abstract interface + dependency token | sensitive |
| 4 | Phase 381 | D2d peering loop | sensitive |
| 5 | Phase 382 | D2d gossip state machine + CDL-039 invariant enforcement | sensitive |
| 6 | Phase 383 | CDL-040 prelock (admission control + identity envelope) | sensitive |
| 7 | Phase 384 | CDL-041 prelock (shard lifecycle) | sensitive |
| 8 | Phase 385 | CDL-043 prelock (storage economics) | sensitive |
| 9 | Phase 386 | SIM-006/007 commissioning | non-sensitive |
| 10 | Phase 387 | V-series implementation authorization lock | non-sensitive |
| 11 | Phase 388 | CDL-V1 temporal decay runtime | sensitive |
| 12 | Phase 389 | CDL-V2 sybil resistance runtime | sensitive |
| 13 | Phase 390 | coherence + capsule v1.3 | non-sensitive |
| 14 | Phase 391 | closure gate + 392+ handoff | sensitive |

## 5. Phase sensitivity and execution policy

Sensitivity policy:
- non-sensitive: phases 378, 386, 387, 390
- sensitive: phases 379, 380, 381, 382, 383, 384, 385, 388, 389, 391

Operational policy:
- non-sensitive phases may proceed under standard execution path,
- sensitive phases require prompt hardening and review hold/GO flow before execution.

## 6. D2d runtime track (380-382) and enforcement boundaries

D2d wire protocol implementation lives in ilc_core/network/d2d/.

Declared package boundary for this window:
- `ilc_core/network/d2d/__init__.py`
- `ilc_core/network/d2d/interface.py`
- `ilc_core/network/d2d/peer.py`
- `ilc_core/network/d2d/gossip.py`

D2d implementation phases may use asyncio. Abstract interfaces (Phase 380) must contain no asyncio.

Peering loop (Phase 381) and gossip state machine (Phase 382) may use asyncio.run() with deterministic mock event loops.

Real socket binds, real DNS lookups, and wall-clock timeouts are prohibited in test code.

## 7. Constitutional prelock track (383-385)

Prelock lane scope:
- Phase 383: `CDL-040` prelock (admission control + identity envelope)
- Phase 384: `CDL-041` prelock (shard lifecycle)
- Phase 385: `CDL-043` prelock (storage economics)

Cross-lane constraints:
- CDL-mutation phases 379, 383, 384, and 385 require ILC_CDL_MUTATION_AUTHORIZED=1, ILC_CDL_MUTATION_PHASE=<NNN>, and a clean git diff HEAD -- ilc_core/ preflight.
- Phase 379 must harden all four CDL-039 prelock tests before commit and use a seven-path commit resolver that includes tests 359, 372, 373, and 374 hardening targets.

## 8. Simulation and authorization track (386-387)

Simulation scope:
- SIM-006 capability_vector vocabulary precondition is declared in this sequence lock and must be verified in Phase 386.
- SIM-006 models panel effectiveness under capability heterogeneity.
- SIM-007 models agent churn and orphan accumulation for CDL-035 timed_out extension and D2d wire-spec planning.

Authorization ownership:
- Phase 387 is the single source of truth for V-series implementation authorization.
- If Phase 378 and Phase 387 conflict on exact target paths or dependency token values, Phase 387 governs.

## 9. V-series runtime enforcement track (388-389)

V-series window-level declaration:
- CDL-V1 and CDL-V2 are authorized for Window 378+ implementation, with exact runtime targets and dependency token values declared in Phase 387.
- CDL-V3 and CDL-V7 remain requires_additional_governance_input pending SIM-006 results and Window 392+ governance resolution.
- CDL-V4, CDL-V5, CDL-V6 remain governance-procedural and implementation-barred.

Runtime-phase guardrail:
- Runtime phases 380, 381, 382, 388, and 389 must use custom runtime mutation-scope asserters and must not use assert_head_commit_touched_no_runtime_files.

## 10. Coherence and closure track (390-391)

Phase 390 obligations:
- coherence report and capsule v1.3 synthesis,
- explicit statement that CDL-039 is ratified in phase 379 with calibration lock,
- explicit V-series enforcement and D2d state declaration.

Phase 391 obligations:
- closure gate and 392+ handoff,
- section-scoped calibration parsing across the phase-379 ratification artifact,
- ratification/implementation boundary assertions for opened and deferred CDLs.

## 11. Explicit deferrals and non-goals

Explicit deferrals:
- CDL-042 (agent identity namespace) is deferred to Window 392+ pending CDL-039/040 scope resolution.

Non-goals in Phase 378:
- no decision-log mutation,
- no `ilc_core/` runtime mutation,
- no runtime implementation execution,
- no ratification action.

## 12. Forward pointer to window 392+

Window 392+ starts with:
- CDL-040/041/043 ratification planning,
- CDL-042 opening,
- CDL-V3/V7 governance resolution,
- runtime follow-through from Phase 387 authorization outputs.

No decision-log mutation occurred. No ilc_core runtime files were changed.
