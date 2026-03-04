# ILC Phase 348-357 Sequence Lock v0.1

Status: Phase-348 sequence lock artifact  
Date: 2026-03-04  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and window character

Lock execution order, ratification dependency edges, sensitivity boundaries, and implementation-deferral rules for the Window 348-357 node-schema ratification program.

This artifact is non-ratifying. It does not mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md` and does not implement runtime behavior in `ilc_core/`.

Window 348-357 is the ratification window for `CDL-034` through `CDL-038`.

## 2. Entry state from phase-347 closure

Entry assumptions:
- Window 338-347 is closed and handed off (`docs/specs/ilc_window_338_347_handoff_347_v0.1.md`).
- Phase-347 closure-gate contracts enforce deterministic dry-run formatting, recursion-safe selftest behavior, verdict/exit semantics, Phase-316 snapshot override isolation, and the corrected prior-window closure-gate chain through `tests/test_window_328_337_closure_gate_337.py` (`tools/check_window_338_347_closure_gate_phase_347.sh`).
- Phase-346 readiness artifacts remain authoritative for the ratification queue, the coherence state, and the ratification-first boundary (`docs/specs/ilc_integration_coherence_report_346_v0.1.md`, `docs/specs/ilc_antigravity_context_capsule_v0.9.md`, `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`).
- ADM-003 role-split groundwork exists, but the 7+1 evaluation panel behavioral-role gap still requires explicit resolution before implementation authorization (`docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`).

## 3. Current constitutional baseline and ratification intent

Current constitutional baseline relevant to this window:
- `CDL-034` through `CDL-038` are open and unratified at entry.
- Window 338-347 closure is complete.
- `CDL-024` and `CDL-V1` through `CDL-V7` remain ratified.
- `CDL-021` remains open and deferred.

Window 348-357 intent:
- ratify `CDL-034` through `CDL-038` in dependency order,
- resolve the ADM-003 7+1 panel behavioral-role gap in Phase 354,
- publish a self-contained capsule `v1.0` in Phase 355,
- publish implementation-readiness boundaries in Phase 356,
- end Window 357 with implementation authorization handed forward to Window 358+ for ratified surfaces only.

## 4. Locked phase table (348-357)

| Order | Phase | Track | Scope | Sensitivity |
| --- | --- | --- | --- | --- |
| 1 | Phase 348 | Sequence lock lane | Lock 348-357 ordering, ratification queue, and implementation-deferral boundary | Non-sensitive |
| 2 | Phase 349 | Ratification lane | `CDL-034` ratification | Sensitive |
| 3 | Phase 350 | Ratification lane | `CDL-035` ratification | Sensitive |
| 4 | Phase 351 | Ratification lane | `CDL-036` ratification | Sensitive |
| 5 | Phase 352 | Ratification lane | `CDL-037` ratification | Sensitive |
| 6 | Phase 353 | Ratification lane | `CDL-038` ratification | Sensitive |
| 7 | Phase 354 | ADM-003 lane | 7+1 panel behavioral-role resolution | Sensitive |
| 8 | Phase 355 | Coherence lane | coherence report, self-contained capsule `v1.0`, implementation-authorization scope | Non-sensitive |
| 9 | Phase 356 | Readiness lane | node-schema implementation readiness | Non-sensitive |
| 10 | Phase 357 | Closure/handoff lane | 348-357 closure gate and 358+ implementation handoff | Sensitive |

## 5. Per-phase sensitivity classification

| Phase | Sensitivity |
| --- | --- |
| Phase 348 | Non-sensitive |
| Phase 349 | Sensitive |
| Phase 350 | Sensitive |
| Phase 351 | Sensitive |
| Phase 352 | Sensitive |
| Phase 353 | Sensitive |
| Phase 354 | Sensitive |
| Phase 355 | Non-sensitive |
| Phase 356 | Non-sensitive |
| Phase 357 | Sensitive |

Sensitivity rationale highlights:
- phases `349` through `353` are sensitive because they ratify constitutional decision-log rows,
- phase `354` is sensitive because it modifies a core architectural reference document with direct governance-boundary implications,
- phase `355` is non-sensitive because it carries forward ratified state into coherence and implementation-scope artifacts without mutating the decision log,
- phase `357` is sensitive because it closes the window and authorizes Window 358+ implementation of ratified surfaces.

## 6. Ratification dependency order

Ratification dependency order is non-negotiable:
1. `CDL-034` must be ratified before `CDL-035`, `CDL-036`, `CDL-037`, and `CDL-038`.
2. `CDL-035` must be ratified before `CDL-037` and `CDL-038` because lifecycle semantics constrain executable-node and promotion continuity behavior.
3. `CDL-036`, `CDL-037`, and `CDL-038` ratify in that order after `CDL-034` and `CDL-035` are complete.
4. Phase 354 follows the CDL stack and resolves the ADM-003 7+1 panel behavioral-role gap before any implementation authorization is granted.
5. Phase 355 may summarize ratified state only after Phases 349-354 are complete.
6. Phase 356 may publish implementation readiness only after Phase 355 completes.
7. Window 358+ implementation begins only after Phase 357 closure confirms the ratified state and implementation boundary.

## 7. Mandatory entry and exit gates per phase

| Phase | Mandatory entry gate | Mandatory exit gate |
| --- | --- | --- |
| Phase 348 | Phase-347 closure gate and handoff are present and green. | Sequence lock artifact, tests, walkthrough, and STATUS entry are complete. |
| Phase 349 | Phase-348 sequence lock is complete. | `CDL-034` is ratified and the ratification artifact is published. |
| Phase 350 | Phase 349 is complete. | `CDL-035` is ratified and the ratification artifact is published. |
| Phase 351 | Phases 349-350 are complete. | `CDL-036` is ratified and the ratification artifact is published. |
| Phase 352 | Phases 349-351 are complete. | `CDL-037` is ratified and the ratification artifact is published. |
| Phase 353 | Phases 349-352 are complete. | `CDL-038` is ratified and the ratification artifact is published. |
| Phase 354 | Phases 349-353 are complete. | ADM-003 explicitly documents the 7+1 panel behavioral role and governance boundary. |
| Phase 355 | Phases 349-354 are complete. | coherence report, self-contained capsule `v1.0`, and implementation-authorization scope are published. |
| Phase 356 | Phase 355 is complete. | implementation-readiness artifact is published without `ilc_core/` work. |
| Phase 357 | Phases 349-356 are complete and closure prerequisites are green. | Closure gate passes and 358+ handoff authorizes implementation of ratified surfaces only. |

## 8. No-runtime-implementation-before-authorization

Window-level guards:
- no runtime implementation may begin in `ilc_core/` during Window 348-357,
- no CDL ratification in this window implicitly authorizes implementation before Window 357 closure,
- no implementation authorization may be inferred from readiness artifacts alone,
- Window 358+ is authorized only for implementation of ratified surfaces.

Authorization boundaries:
- `CDL-034` through `CDL-038` are the only ratification surfaces in this window,
- Phase 355 defines implementation-authorization scope but does not itself authorize `ilc_core/` work,
- Phase 356 maps implementation prerequisites but still does not permit `ilc_core/` changes,
- implementation authorization becomes active only after Phase 357 closure.

## 9. Phase-specific forward constraints (349-357)

Phase-349 through Phase-353 constraints:
- each ratification hardens exactly one corresponding prelock test,
- each ratification uses a 4-file content-qualified commit resolver,
- no V-series style cascade hardening is introduced between `CDL-034` through `CDL-038`,
- each ratification artifact must include a self-contained Section-6 authoritative evidence satisfaction block,
- no runtime implementation of the ratified topic is authorized in the ratification phase itself.

Phase-354 constraints:
- ADM-003 must explicitly add the 7+1 evaluation panel as a named agent behavioral role,
- the governance boundary must remain explicit: the panel governs knowledge-claim evaluation, not constitutional or genesis-layer changes,
- L-tier disambiguation must remain explicit,
- CDL-V7 remains the test specification; the 7+1 panel remains the testing mechanism.

Phase-355 constraints:
- capsule `v1.0` must be self-contained, not delta-only,
- capsule `v1.0` must carry forward the full v0.9 context where still applicable,
- implementation-authorization scope must name only ratified surfaces.

Phase-356 constraints:
- implementation readiness maps prerequisites and module targets only,
- implementation readiness does not permit `ilc_core/` work,
- ADM-003 integration remains a Window 358+ implementation prerequisite.

Phase-357 constraints:
- category 3 must use `tests/test_window_338_347_closure_gate_347.py`,
- closure must verify `CDL-034` through `CDL-038` are ratified,
- closure must verify ADM-003 role resolution is complete,
- closure must verify no `ilc_core/` implementation occurred in Window 348-357,
- Phase 357 prompt must not be drafted until Phases 348-356 are approved.

## 10. Closure condition and 358+ boundary

Window 357 closure must verify:
- `CDL-034` through `CDL-038` are all ratified,
- ADM-003 7+1 panel role resolution is complete,
- no `ilc_core/` implementation occurred in Window 348-357,
- the implementation-authorization scope from Phase 355 is complete and bounded,
- the implementation-readiness document from Phase 356 is complete,
- Window 358+ is authorized to begin runtime implementation of ratified CDL-034 through CDL-038 surfaces.

Window 358+ boundary:
- Window 358+ is authorized only for implementation of ratified surfaces.
- Unratified surfaces remain implementation-barred.
- Implementation ordering in Window 358+ must mirror the ratified dependency order where technically required.

## 11. Non-goals and explicit boundaries

This Phase-348 sequence lock does not:
- ratify any CDL row,
- modify `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- implement runtime behavior in `ilc_core/`,
- resolve ADM-003 itself,
- authorize runtime work merely because a plan exists.

Boundary statement:
- no decision-log mutation in Phase 348,
- no `ilc_core/` runtime implementation in Phase 348.

## 12. Forward pointer

Phase 349 begins the ratification lane for `CDL-034`, with `CDL-035` and the remainder of the stack following in dependency order. ADM-003 resolution remains mandatory before implementation authorization can be granted.
