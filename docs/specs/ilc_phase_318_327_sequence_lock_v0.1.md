# ILC Phase 318-327 Sequence Lock v0.1

Status: Phase-318 sequence lock artifact  
Date: 2026-02-27  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and sequence scope

Lock execution order, dependency edges, and sensitivity boundaries for the Phase 318-327 window.

This artifact is non-ratifying. It does not mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md` and does not implement runtime behavior in `ilc_core/`.

## 2. Entry state from phase-317 closure controls

Entry assumptions:
- Window 308-317 is closed and handed off (`docs/specs/ilc_window_308_317_handoff_317_v0.1.md`).
- Closure gate contracts enforce deterministic dry-run formatting, recursion-safe selftest behavior, and explicit verdict-exit semantics (`tools/check_window_308_317_closure_gate_phase_317.sh`).
- Snapshot override isolation is a required testability standard for future closure gates.

## 3. Open CDL inventory and window intent

Open constitutional inventory relevant to this window:
- `CDL-020`: protocol-native bundle schema and complete type system.
- `CDL-021`: rust kernel port and WASM distribution.
- `CDL-022`: genesis state bundle specification and signing ceremony.
- `CDL-023`: epoch snapshot mechanism and fast-bootstrap protocol.
- `CDL-024`: wire protocol specification and transport bindings.

Window 318-327 intent:
- execute ratification lanes for foundational infrastructure CDLs (`319-321` for `CDL-020`, `CDL-022`, `CDL-023`) after prior evidence/runtime prerequisites,
- open wire transport contract/runtime lane (`322-323`) while keeping transport coupling constraints explicit,
- open vulnerability-governance CDL-V entries via constitutional-sensitive lanes (`324-325`),
- keep `CDL-021` milestone-triggered and out of active execution in this window,
- close window with composed closure gate + 328+ handoff in phase 327.

## 4. Locked phase table (318-327)

| Order | Phase | Track | Scope | Sensitivity |
| --- | --- | --- | --- | --- |
| 1 | Phase 318 | Sequence lock lane | Lock 318-327 ordering, dependencies, sensitivity, closure skeleton | Non-sensitive |
| 2 | Phase 319 | Ratification lane | CDL-020 ratification ceremony | Sensitive |
| 3 | Phase 320 | Ratification lane | CDL-022 ratification ceremony | Sensitive |
| 4 | Phase 321 | Ratification lane | CDL-023 ratification ceremony | Sensitive |
| 5 | Phase 322 | Schema/evidence lane | CDL-024 contract and evidence prelock | Non-sensitive |
| 6 | Phase 323 | Runtime/provider lane | CDL-024 implementation tranche | Sensitive |
| 7 | Phase 324 | Vulnerability governance lane | Open CDL-V1/V2/V3 entries + evidence prelock artifacts | Sensitive |
| 8 | Phase 325 | Vulnerability governance lane | Open CDL-V4/V5/V6/V7 entries + evidence prelock artifacts | Sensitive |
| 9 | Phase 326 | Coherence/capsule lane | Integration coherence + context capsule update | Non-sensitive |
| 10 | Phase 327 | Closure/handoff lane | 318-327 closure verification gate and 328+ handoff | Sensitive |

## 5. Per-phase sensitivity classification

| Phase | Sensitivity |
| --- | --- |
| Phase 318 | Non-sensitive |
| Phase 319 | Sensitive |
| Phase 320 | Sensitive |
| Phase 321 | Sensitive |
| Phase 322 | Non-sensitive |
| Phase 323 | Sensitive |
| Phase 324 | Sensitive |
| Phase 325 | Sensitive |
| Phase 326 | Non-sensitive |
| Phase 327 | Sensitive |

Sensitivity rationale highlights:
- phases `324` and `325` are sensitive because adding/opening new CDL-V entries mutates constitutional decision-log state,
- phase `327` remains sensitive as window closure gate and handoff authority lane.

## 6. Dependency map and synchronization rules

Track model:
- Ratification track phases: `319`, `320`, `321`.
- Transport track phases: `322`, `323`.
- Vulnerability governance track phases: `324`, `325`.
- Coherence/capsule lane phase: `326`.
- Closure/handoff lane phase: `327`.

Synchronization rules:
1. `319` requires Phase-310 runtime handoff and Phase-309 contract evidence.
2. `320` requires Phase-312 runtime handoff and Phase-311 contract evidence.
3. `321` requires Phase-314 runtime handoff and Phase-313 contract evidence.
4. `322` must complete before `323` begins.
5. `324` and `325` may execute after `318` but both must complete before `326`.
6. `326` requires completion evidence from `319` through `325`.
7. `327` requires `326` completion evidence plus green closure prerequisites.

## 7. Mandatory entry and exit gates per phase

| Phase | Mandatory entry gate | Mandatory exit gate |
| --- | --- | --- |
| Phase 318 | Phase-317 closure gate and handoff are present. | Sequence lock artifact, tests, walkthrough, and STATUS entry are complete. |
| Phase 319 | Phase-318 sequence lock is complete; Phase-309/310 evidence chain is green. | CDL-020 ratification evidence and mutation guardrails are complete. |
| Phase 320 | Phase-318 sequence lock is complete; Phase-311/312 evidence chain is green. | CDL-022 ratification evidence and mutation guardrails are complete. |
| Phase 321 | Phase-318 sequence lock is complete; Phase-313/314 evidence chain is green. | CDL-023 ratification evidence and mutation guardrails are complete. |
| Phase 322 | Phase-318 sequence lock is complete. | CDL-024 contract/evidence prelock artifact and tests are complete. |
| Phase 323 | Phase-322 contract/evidence lane is complete. | CDL-024 runtime tranche tests pass; no non-target mutations. |
| Phase 324 | Phase-318 sequence lock is complete. | CDL-V1/V2/V3 open-entry mutations + prelock artifacts are complete. |
| Phase 325 | Phase-318 sequence lock is complete. | CDL-V4/V5/V6/V7 open-entry mutations + prelock artifacts are complete. |
| Phase 326 | Phases 319-325 are complete and green. | Coherence artifact + capsule update are complete with boundary checks. |
| Phase 327 | Phase-326 is complete and green. | Closure gate passes all required categories and 328+ handoff is published. |

## 8. No-ratification-before-lock and authorization boundaries

Window-level guard:
- no ratification lane may execute in this 318-327 window unless this sequence lock is published first,
- authorized ratification lanes in this window are limited to phases `319`, `320`, and `321`.

Authorization boundaries:
- `CDL-021` remains milestone-triggered and is not authorized for execution in this window,
- CDL-V entry opening lanes (`324`, `325`) are authorized as sensitive constitutional mutation lanes only.

## 9. Closure-gate skeleton requirements for phase 327

Phase 327 must implement a composed closure gate with these command categories:
1. Prompt contract validation category.
2. Lane-specific contract tests category.
3. Cross-phase regression category.
4. Mutation canary category.
5. CLI contract category.
6. Walkthrough hygiene category.

Snapshot isolation/testing standard (mandatory carry-forward):
- closure gate script must accept `ILC_PHASE_<PHASE>_SNAPSHOT_PATH` as snapshot override input,
- closure-gate tests that simulate non-pass verdicts must use `tmp_path` snapshot copies plus env override,
- closure-gate tests must not mutate canonical snapshots under `out/monitoring/`.

## 10. Non-goals and explicit boundaries

This phase-318 sequence lock does not:
- ratify, open, or modify any CDL row,
- modify `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- implement runtime behavior in `ilc_core/`,
- authorize `CDL-021` execution without milestone trigger.

## 11. Forward pointer

Phase 319 opens as the first sensitive ratification lane for `CDL-020`, and Phase 320/321 follow as ratification lanes for `CDL-022` and `CDL-023` using already-completed evidence/runtime foundations.
