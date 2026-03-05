# ILC Phase 358-367 Sequence Lock v0.1

Status: Phase-358 sequence lock artifact  
Date: 2026-03-05  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and window character

Window 358-367 is the first implementation window after constitutional ratification for the node-schema stack.

This phase is non-ratifying and non-runtime. It publishes the planning lock, test contract, and roadmap only.

## 2. Entry state from phase-357 closure

Entry assumptions:
- Window 348-357 closure passed and handoff is published in `docs/specs/ilc_window_348_357_handoff_357_v0.1.md`.
- `CDL-034` through `CDL-038` are ratified and implementation-ready per Phase 355/356 artifacts.
- The decision log remains immutable in this phase.
- `ilc_core/` runtime implementation remains out of scope for this phase.

## 3. Implementation authorization and dependency chain

CDL dependency chain for implementation ordering:

`CDL-034 -> CDL-035 -> CDL-036 -> CDL-037 -> CDL-038`

Authorization boundary for this window:
- CDL-034 through CDL-038 runtime implementation is authorized for Window 358-367.
- V-series enforcement runtime implementation (CDL-V1 through CDL-V7) is NOT authorized in this window.
- V-series runtime work is deferred to Window 368-377.

## 4. Locked phase table (358-367)

| Order | Phase | Scope | Sensitivity |
| --- | --- | --- | --- |
| 1 | Phase 358 | sequence lock + roadmap v0.4 | non-sensitive |
| 2 | Phase 359 | CDL-039 opening | sensitive |
| 3 | Phase 360 | CDL-034 runtime implementation | sensitive |
| 4 | Phase 361 | CDL-035 runtime implementation | sensitive |
| 5 | Phase 362 | CDL-036 runtime implementation | sensitive |
| 6 | Phase 363 | CDL-037 runtime implementation | sensitive |
| 7 | Phase 364 | CDL-038 runtime implementation | sensitive |
| 8 | Phase 365 | SIM-001/002/003 commissioning | non-sensitive |
| 9 | Phase 366 | coherence + capsule v1.1 | non-sensitive |
| 10 | Phase 367 | closure gate and 368+ handoff | sensitive |

## 5. Per-phase sensitivity classification

- `Phase 358`: sequence lock + roadmap v0.4 (non-sensitive)
- `Phase 359`: CDL-039 opening (sensitive)
- `Phase 360`: CDL-034 runtime implementation (sensitive)
- `Phase 361`: CDL-035 runtime implementation (sensitive)
- `Phase 362`: CDL-036 runtime implementation (sensitive)
- `Phase 363`: CDL-037 runtime implementation (sensitive)
- `Phase 364`: CDL-038 runtime implementation (sensitive)
- `Phase 365`: SIM-001/002/003 commissioning (non-sensitive)
- `Phase 366`: coherence + capsule v1.1 (non-sensitive)
- `Phase 367`: closure gate and 368+ handoff (sensitive)

## 6. Runtime module naming convention

Runtime modules in phases 360-364 must use phase-qualified naming under stable subsystem roots so dependency edges remain explicit in review and test logs.

Required runtime-phase test policy:
- `_assert_runtime_mutation_scope(commit_ref)`
- `assert_head_commit_touched_no_runtime_files is an anti-pattern for runtime implementation phases`

## 7. Mandatory entry and exit gates per phase

- Every phase must start with explicit regression gate checks tied to prior-window closure contracts.
- Every sensitive phase must include commit-anchored mutation-scope tests.
- Every non-sensitive phase must prove no decision-log mutation and no `ilc_core/` runtime mutation.
- Every phase must end with walkthrough and STATUS backfill.

## 8. CDL-039 opening constraints (phase 359)

- Phase 359 opens CDL-039 as an additive-only row mutation.
- No finalized CDL-039 prelock invariants are locked in Phase 359.
- Phase 374 finalizes CDL-039 prelock design after SIM-004 and SIM-005 evidence.

Open constraints carried forward:
- topology-opaque
- cluster membership comparison must not be derivable from public protocol data
- COSE kid must be a protocol-internal opaque identifier

These constraints are carried as open requirements only and not converted into locked implementation choices in this window.

## 9. No-runtime-before-window-367-closure

Window 358 authorization is planning-only and does not itself perform implementation.

No runtime execution claims may be made before phase-specific implementation commits land in phases 360-364 and the window closes through Phase 367.

## 10. Phase-specific forward constraints (359-367)

- Phase 359 must remain additive-only on decision-log scope.
- Phases 360-364 must implement only ratified `CDL-034` through `CDL-038` surfaces.
- Phase 365 simulation outputs must remain deterministic and text-serializable for downstream coherence.
- Phase 366 capsule v1.1 must be self-contained.
- Window 368 sequence-lock drafting must evaluate Levin gossip + coordinate mechanism proposals as D2d wire-protocol inputs.

## 11. Non-goals and explicit boundaries

Out of scope for this window lock phase:
- legal/regulatory strategy document creation,
- any decision-log mutation in Phase 358,
- any `ilc_core/` runtime mutation in Phase 358,
- final prelock design closure for `CDL-039`,
- V-series runtime authorization or implementation in this window lock.

## 12. Forward pointer

Phase 359 executes the additive opening of CDL-039 under the constraints above, then phases 360-364 execute the bounded node-schema runtime implementation lane.
