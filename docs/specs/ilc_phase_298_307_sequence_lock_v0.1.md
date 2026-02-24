# ILC Phase 298-307 Sequence Lock v0.1

Status: Phase-298 sequence lock artifact  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and sequence scope

Lock execution order, dependency edges, and sensitivity boundaries for the Phase 298-307 window.

This artifact is non-ratifying. It does not mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md` and it does not implement runtime behavior in `ilc_core/`.

## 2. Entry state from phase-296 and phase-297 controls

Entry assumptions:
- Phase 296 established commit-manifest-backed resolver hardening (`docs/specs/ilc_phase_commit_manifest_296_v0.1.json`).
- Phase 297 established mutation-canary gate contract (`docs/specs/ilc_mutation_canary_gate_contract_297_v0.1.md`).
- Window 286-295 is closed and handed off (`docs/specs/ilc_window_286_295_handoff_295_v0.1.md`).

## 3. Locked phase table (298-307)

| Order | Phase | Track | Scope | Sensitivity |
| --- | --- | --- | --- | --- |
| 1 | Phase 298 | Sequence lock lane | Lock 298-307 ordering, dependencies, sensitivity, closure skeleton | Non-sensitive |
| 2 | Phase 299 | Schema/evidence track | D2e-05 query contract and schema boundary lock | Non-sensitive |
| 3 | Phase 300 | Runtime/provider track | D2e-05 query runtime implementation tranche | Sensitive |
| 4 | Phase 301 | Schema/evidence track | D2e-06 verify contract and schema boundary lock | Non-sensitive |
| 5 | Phase 302 | Runtime/provider track | D2e-06 verify runtime implementation tranche | Sensitive |
| 6 | Phase 303 | Schema/evidence track | D2e-07 bundle contract and provider-boundary lock | Non-sensitive |
| 7 | Phase 304 | Runtime/provider track | D2e-07 bundle runtime implementation tranche | Sensitive |
| 8 | Phase 305 | Schema/evidence track | Economic risk monitoring rollout baseline for D2e surfaces | Non-sensitive |
| 9 | Phase 306 | Runtime/provider track | Composed query/verify/bundle integration preflight lane | Sensitive |
| 10 | Phase 307 | Closure/handoff lane | 298-307 closure verification gate and 308+ handoff | Sensitive |

## 4. Per-phase sensitivity classification

| Phase | Sensitivity |
| --- | --- |
| Phase 298 | Non-sensitive |
| Phase 299 | Non-sensitive |
| Phase 300 | Sensitive |
| Phase 301 | Non-sensitive |
| Phase 302 | Sensitive |
| Phase 303 | Non-sensitive |
| Phase 304 | Sensitive |
| Phase 305 | Non-sensitive |
| Phase 306 | Sensitive |
| Phase 307 | Sensitive |

## 5. Parallel-track dependency and synchronization map

Track model:
- Runtime/provider track phases: `300`, `302`, `304`, `306`.
- Schema/evidence track phases: `299`, `301`, `303`, `305`, `307`.

Synchronization rules:
1. `299` is required before `300` begins.
2. `301` is required before `302` begins.
3. `303` is required before `304` begins.
4. `305` is required before `306` begins.
5. `306` completion evidence is required before closure in `307`.

## 6. Mandatory entry and exit gates per phase

| Phase | Mandatory entry gate | Mandatory exit gate |
| --- | --- | --- |
| Phase 298 | Phase 297 canary contract and handoff are present. | Sequence lock artifact, tests, walkthrough, and STATUS entry are complete. |
| Phase 299 | Phase 298 sequence lock is complete. | Query contract/schema artifact and tests are complete; no `ilc_core/` runtime mutation. |
| Phase 300 | Phase 299 contract tests pass and schema boundaries are locked. | Query runtime tranche tests pass; no decision-log mutation. |
| Phase 301 | Phase 300 runtime handoff is complete. | Verify contract/schema artifact and tests are complete; no `ilc_core/` runtime mutation. |
| Phase 302 | Phase 301 contract tests pass and schema boundaries are locked. | Verify runtime tranche tests pass; no decision-log mutation. |
| Phase 303 | Phase 302 runtime handoff is complete. | Bundle contract/provider-boundary artifact and tests are complete; no decision-log mutation. |
| Phase 304 | Phase 303 contract tests pass and provider boundaries are locked. | Bundle runtime tranche tests pass; no decision-log mutation. |
| Phase 305 | Phase 304 runtime handoff is complete. | Economic monitoring rollout artifact and tests are complete; no decision-log mutation. |
| Phase 306 | Phase 305 monitoring baseline and dependencies are complete. | Composed integration preflight tests pass with explicit runtime boundary statement. |
| Phase 307 | Phase 306 integration preflight is complete and green. | Closure gate passes all required command categories and handoff artifact is published. |

## 7. No-ratification-before-lock gate

Window-level ratification guard:
- No ratification lane may execute in this 298-307 window unless its prelock/evidence lane is explicitly listed in this sequence lock and completed first.
- This window is currently planned as implementation and closure work; no direct CDL mutation lane is authorized by Phase 298.

## 8. Closure-gate skeleton requirements for phase 307

Phase 307 must implement a composed closure gate that includes these command categories:
1. Prompt contract validation category (`tools/validate_phase_prompt.py` for Phase 307 prompt).
2. Lane-specific contract tests category (phase tests for 298-307 deliverables).
3. Cross-phase regression category (carry-forward tests from phases 296 and 297 plus D2e runtime regressions).
4. Mutation canary category (phase-297 runner invocation to prove mutation detection remains active).
5. CLI contract category (`--dry-run`, `--help`, unknown-arg exit 2 for any new gate scripts).
6. Walkthrough hygiene category (`tests/test_no_ellipses_in_walkthroughs.py`).

## 9. Non-goals and explicit boundaries

This phase-298 sequence lock does not:
- ratify or reopen any CDL row,
- modify `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- implement runtime behavior in `ilc_core/`,
- select policy values that require constitutional ratification.

## 10. Forward pointer

Phase 299 starts the first schema/evidence lane (`D2e-05 query contract and schema boundary lock`), and Phase 300 remains blocked until Phase 299 completion evidence is present.
