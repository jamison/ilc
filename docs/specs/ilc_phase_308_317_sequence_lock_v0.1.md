# ILC Phase 308-317 Sequence Lock v0.1

Status: Phase-308 sequence lock artifact  
Date: 2026-02-26  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and sequence scope

Lock execution order, dependency edges, and sensitivity boundaries for the Phase 308-317 window.

This artifact is non-ratifying. It does not mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md` and does not implement runtime behavior in `ilc_core/`.

## 2. Entry state from phase-307 closure controls

Entry assumptions:
- Window 298-307 is closed and handed off (`docs/specs/ilc_window_298_307_handoff_307_v0.1.md`).
- Closure gate contracts now enforce deterministic dry-run formatting and explicit verdict-exit semantics (`tools/check_window_298_307_closure_gate_phase_307.sh`).
- Snapshot override isolation is a required testability standard for future closure gates.

## 3. Open CDL inventory and window intent

Open constitutional inventory relevant to this window:
- `CDL-020`: protocol-native bundle schema and complete type system.
- `CDL-021`: rust kernel port and WASM distribution.
- `CDL-022`: genesis state bundle specification and signing ceremony.
- `CDL-023`: epoch snapshot mechanism and fast-bootstrap protocol.
- `CDL-024`: wire protocol specification and transport bindings.

Window 308-317 intent:
- prioritize infrastructure-tier D2 schema, genesis bundle, and epoch snapshot surfaces (`CDL-020`, `CDL-022`, `CDL-023`),
- keep `CDL-021` milestone-triggered and out of this window,
- defer `CDL-024` wire transport ratification lane to the next window once 309-316 prerequisites settle.

## 4. Locked phase table (308-317)

| Order | Phase | Track | Scope | Sensitivity |
| --- | --- | --- | --- | --- |
| 1 | Phase 308 | Sequence lock lane | Lock 308-317 ordering, dependencies, sensitivity, closure skeleton | Non-sensitive |
| 2 | Phase 309 | Schema/evidence track | D2 schema baseline contract + CDL-020 evidence prelock | Non-sensitive |
| 3 | Phase 310 | Runtime/provider track | D2 schema baseline implementation tranche | Sensitive |
| 4 | Phase 311 | Schema/evidence track | Genesis state bundle contract + CDL-022 evidence prelock | Non-sensitive |
| 5 | Phase 312 | Runtime/provider track | Genesis state bundle implementation tranche | Sensitive |
| 6 | Phase 313 | Schema/evidence track | Epoch snapshot contract + CDL-023 evidence prelock | Non-sensitive |
| 7 | Phase 314 | Runtime/provider track | Epoch snapshot implementation tranche | Sensitive |
| 8 | Phase 315 | Schema/evidence track | Economic risk monitoring update for D2 schema/genesis/epoch surfaces | Non-sensitive |
| 9 | Phase 316 | Runtime/provider track | Composed integration preflight across D2 schema, genesis, and epoch lanes | Sensitive |
| 10 | Phase 317 | Closure/handoff lane | 308-317 closure verification gate and 318+ handoff | Sensitive |

## 5. Per-phase sensitivity classification

| Phase | Sensitivity |
| --- | --- |
| Phase 308 | Non-sensitive |
| Phase 309 | Non-sensitive |
| Phase 310 | Sensitive |
| Phase 311 | Non-sensitive |
| Phase 312 | Sensitive |
| Phase 313 | Non-sensitive |
| Phase 314 | Sensitive |
| Phase 315 | Non-sensitive |
| Phase 316 | Sensitive |
| Phase 317 | Sensitive |

## 6. Parallel-track dependency and synchronization map

Track model:
- Runtime/provider track phases: `310`, `312`, `314`, `316`.
- Schema/evidence track phases: `309`, `311`, `313`, `315`.
- Closure/handoff lane phase: `317`.

Synchronization rules:
1. `309` is required before `310` begins.
2. `311` is required before `312` begins.
3. `313` is required before `314` begins.
4. `315` is required before `316` begins.
5. `316` completion evidence is required before closure in `317`.

## 7. Mandatory entry and exit gates per phase

| Phase | Mandatory entry gate | Mandatory exit gate |
| --- | --- | --- |
| Phase 308 | Phase 307 closure gate and handoff are present. | Sequence lock artifact, tests, walkthrough, and STATUS entry are complete. |
| Phase 309 | Phase 308 sequence lock is complete. | D2 schema baseline contract + CDL-020 prelock evidence artifact and tests are complete; no `ilc_core/` runtime mutation. |
| Phase 310 | Phase 309 contract tests pass and prelock boundaries are locked. | D2 schema runtime tranche tests pass; no decision-log mutation. |
| Phase 311 | Phase 310 runtime handoff is complete. | Genesis bundle contract + CDL-022 prelock evidence artifact and tests are complete; no `ilc_core/` runtime mutation. |
| Phase 312 | Phase 311 contract tests pass and prelock boundaries are locked. | Genesis runtime tranche tests pass; no decision-log mutation. |
| Phase 313 | Phase 312 runtime handoff is complete. | Epoch snapshot contract + CDL-023 prelock evidence artifact and tests are complete; no `ilc_core/` runtime mutation. |
| Phase 314 | Phase 313 contract tests pass and prelock boundaries are locked. | Epoch snapshot runtime tranche tests pass; no decision-log mutation. |
| Phase 315 | Phase 314 runtime handoff is complete. | Monitoring update artifact and tests are complete; no decision-log mutation. |
| Phase 316 | Phase 315 monitoring update and dependencies are complete. | Composed preflight tests pass with explicit runtime boundary statement. |
| Phase 317 | Phase 316 composed preflight is complete and green. | Closure gate passes all required command categories and handoff artifact is published. |

## 8. No-ratification-before-lock gate

Window-level ratification guard:
- no ratification lane may execute in this 308-317 window unless its prelock/evidence lane is explicitly listed in this sequence lock and completed first,
- this window is planned as infrastructure contract/runtime staging and closure work; no direct CDL mutation lane is authorized by Phase 308.

## 9. Closure-gate skeleton requirements for phase 317

Phase 317 must implement a composed closure gate with these command categories:
1. Prompt contract validation category.
2. Lane-specific contract tests category.
3. Cross-phase regression category.
4. Mutation canary category.
5. CLI contract category.
6. Walkthrough hygiene category.

Snapshot isolation/testing standard (mandatory carry-forward from Phase 307):
- closure gate script must accept `ILC_PHASE_<PHASE>_SNAPSHOT_PATH` as snapshot override input,
- closure-gate tests that simulate non-pass verdicts must use `tmp_path` snapshot copies plus the env override,
- closure-gate tests must not mutate canonical snapshots under `out/monitoring/`.

## 10. Non-goals and explicit boundaries

This phase-308 sequence lock does not:
- ratify or reopen any CDL row,
- modify `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- implement runtime behavior in `ilc_core/`,
- authorize `CDL-021` or `CDL-024` ratification execution in this window.

## 11. Forward pointer

Phase 309 starts the first schema/evidence lane (`D2 schema baseline contract + CDL-020 evidence prelock`), and Phase 310 remains blocked until Phase 309 completion evidence is present.
