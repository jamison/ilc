# ILC Phase 338-347 Sequence Lock v0.1

Status: Phase-338 sequence lock artifact  
Date: 2026-03-03  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and window character

Lock execution order, dependency edges, sensitivity boundaries, CDL-opening lanes, and forward constraints for the Window 338-347 node-schema contract program.

This artifact is non-ratifying. It does not mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md` and does not implement runtime behavior in `ilc_core/`.

Window 338-347 is a pre-ratification, pre-implementation contract window.

## 2. Entry state from phase-337 closure

Entry assumptions:
- Window 328-337 is closed and handed off (`docs/specs/ilc_window_328_337_handoff_337_v0.1.md`).
- Closure-gate contracts enforce deterministic dry-run formatting, recursion-safe selftest behavior, verdict/exit semantics, Phase-316 snapshot override isolation, and forced-verdict sanitization (`tools/check_window_328_337_closure_gate_phase_337.sh`).
- Phase-336 coherence artifacts remain authoritative for the 7+1 panel architecture, L-tier disambiguation, the ADM-003 gap, and the governance boundary between knowledge evaluation and constitutional change (`docs/specs/ilc_integration_coherence_report_336_v0.1.md`, `docs/specs/ilc_antigravity_context_capsule_v0.8.md`).
- The node-schema packet is committed and available as planning input (`docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`, `docs/specs/ilc_node_schema_concretization_proposals_v0.1.md`, `docs/specs/ilc_window_338_347_node_schema_program_plan_v0.1.md`).

## 3. Current constitutional baseline and window intent

Current constitutional baseline relevant to this window:
- `CDL-021` remains open and deferred.
- `CDL-024` and `CDL-V1` through `CDL-V7` are ratified.
- `CDL-034` through `CDL-038` are not yet opened in Phase 338.

Window 338-347 intent:
- resolve the `ADM-003` role gap first,
- open `CDL-034` through `CDL-038` in separate sensitive lanes,
- publish prelock artifacts for each node-schema surface,
- keep runtime implementation barred until the relevant CDL is ratified,
- end Window 347 with `CDL-034` through `CDL-038` still open and unratified,
- hand Window 348+ a ratification-first queue rather than an implementation authorization.

## 4. Locked phase table (338-347)

| Order | Phase | Track | Scope | Sensitivity |
| --- | --- | --- | --- | --- |
| 1 | Phase 338 | Sequence lock lane | Lock 338-347 ordering, sensitivity, opening map, and ratification-first boundary | Non-sensitive |
| 2 | Phase 339 | ADM-003 lane | Resolve panel role vs graph-observation/schema-evolution role | Non-sensitive |
| 3 | Phase 340 | Opening lane | `CDL-034` opening + node schema core prelock | Sensitive |
| 4 | Phase 341 | Opening lane | `CDL-035` opening + validation lifecycle prelock | Sensitive |
| 5 | Phase 342 | Opening lane | `CDL-036` opening + dissemination/header prelock | Sensitive |
| 6 | Phase 343 | Opening lane | `CDL-037` opening + executable node prelock | Sensitive |
| 7 | Phase 344 | Opening lane | `CDL-038` opening + promotion continuity prelock | Sensitive |
| 8 | Phase 345 | Adjoint contract lane | Reputation and agent-profile adjunct contract | Non-sensitive |
| 9 | Phase 346 | Coherence lane | Node schema coherence and ratification-readiness package | Non-sensitive |
| 10 | Phase 347 | Closure/handoff lane | 338-347 closure gate and 348+ ratification-first handoff | Sensitive |

## 5. Per-phase sensitivity classification

| Phase | Sensitivity |
| --- | --- |
| Phase 338 | Non-sensitive |
| Phase 339 | Non-sensitive |
| Phase 340 | Sensitive |
| Phase 341 | Sensitive |
| Phase 342 | Sensitive |
| Phase 343 | Sensitive |
| Phase 344 | Sensitive |
| Phase 345 | Non-sensitive |
| Phase 346 | Non-sensitive |
| Phase 347 | Sensitive |

Sensitivity rationale highlights:
- phases `340` through `344` are sensitive because they open new constitutional decision-log rows,
- phase `345` is non-sensitive because it constrains future reputation design without opening a CDL row,
- phase `347` is sensitive because it closes the window and authorizes the 348+ ratification-first handoff.

## 6. Opening-lane map and dependency order

Opening-lane map:
- `340 -> CDL-034`
- `341 -> CDL-035`
- `342 -> CDL-036`
- `343 -> CDL-037`
- `344 -> CDL-038`

Dependency order:
1. Phase 339 must complete before any schema-evolution monitoring or custom-field elevation work is authorized.
2. Phase 340 establishes the node-schema core boundary that later phases must reference.
3. Phase 341 depends on the Window-338 sequence lock and the Phase-339 role split.
4. Phase 342 depends on the Window-338 sequence lock and the Phase-340 authored/protocol/transport boundary.
5. Phase 343 depends on the Window-338 sequence lock and must respect the Phase-340 boundary model.
6. Phase 344 depends on the Window-338 sequence lock and must cross-reference the Phase-340 reserved-field/custom-extension model.
7. Phase 345 depends on the Window-338 sequence lock and the Phase-339 role split, but does not open a CDL row.
8. Phase 346 requires completion evidence from Phases 339 through 345.
9. Phase 347 requires Phase 346 completion evidence plus green closure prerequisites.
10. Window 348+ begins with ratification work rather than runtime implementation.

## 7. Mandatory entry and exit gates per phase

| Phase | Mandatory entry gate | Mandatory exit gate |
| --- | --- | --- |
| Phase 338 | Phase-337 closure gate and handoff are present and green. | Sequence lock artifact, tests, walkthrough, and STATUS entry are complete. |
| Phase 339 | Phase-338 sequence lock is complete. | `ADM-003` role split is published with tests and carry-forward authorization. |
| Phase 340 | Phases 338-339 are complete. | `CDL-034` is opened and the node-schema core prelock is published. |
| Phase 341 | Phases 338-339 are complete. | `CDL-035` is opened and the validation-lifecycle prelock is published. |
| Phase 342 | Phases 338-340 are complete. | `CDL-036` is opened and the dissemination/header prelock is published. |
| Phase 343 | Phases 338-340 are complete. | `CDL-037` is opened and the executable-node prelock is published. |
| Phase 344 | Phases 338-340 are complete. | `CDL-038` is opened and the promotion-continuity prelock is published. |
| Phase 345 | Phases 338-339 are complete. | Reputation adjunct contract is published without opening a CDL row. |
| Phase 346 | Phases 339-345 are complete. | Ratification-readiness report and capsule update are complete. |
| Phase 347 | Phase 346 is complete and closure prerequisites are green. | Closure gate passes and 348+ handoff confirms `CDL-034` through `CDL-038` remain open and unratified. |

## 8. No-ratification-before-lock and no-implementation-before-ratification

Window-level guards:
- no ratification or opening lane may execute in Window 338-347 unless this sequence lock is published first,
- no node-schema runtime implementation may begin in `ilc_core/` during Window 338-347,
- no node-schema surface becomes implementation-authorized merely because its CDL row was opened or its prelock was published,
- Window 348+ begins with ratification work rather than runtime implementation.

Authorization boundaries:
- `CDL-034` through `CDL-038` are the only authorized new constitutional topics in this window,
- `CDL-021` remains open, deferred, and out of active execution in this window,
- Phase 345 may constrain future reputation design but may not create a de facto reputation CDL.

## 9. Phase-specific forward constraints (340-345)

Phase-340 forward constraints:
- The three-envelope model is the anchor invariant for `CDL-034`.
- `confidence` and `uncertainty_note` must receive an explicit disposition.
- `gate_routing` is protocol-derived and not submitter-controlled authored payload.
- custom-extension namespace rules and reserved-field collision rules must be explicit.
- a single-primary-epistemic-lane rule must be stated explicitly.

Phase-341 forward constraints:
- `validation_state` must be specified as a state machine rather than loose status vocabulary.
- `gate_verdict` must attach by reference.
- bounded operational relevance for recursive verdict challenges must be explicit.

Phase-342 forward constraints:
- dissemination remains header-first with CID-addressed pull fetch.
- transport/header semantics must remain orderer-agnostic at this stage.
- Narwhal/Tusk/Bullshark may appear only as a reference pattern, not a locked constitutional choice.

Phase-343 forward constraints:
- nodes recommend logic; they do not self-authorize execution.
- executable-node descriptors remain structured descriptors, not raw executable code.
- agent-side sandboxing and safety-contract semantics must remain explicit.

Phase-344 forward constraints:
- promotion occurs by successor public node plus `promotion_receipt`, never by mutating the original node.
- promotion continuity must cross-reference the `CDL-034` reserved-field and custom-extension model.
- no automatic public corroboration or reuse credit carry-forward is allowed.

Phase-345 boundary constraints:
- do not lock quorum thresholds for reputation,
- do not treat L-tier quorum levels as reputation tiers,
- do not embed `CDL-V3` diversity criteria as implicit reputation defaults,
- do not create a de facto reputation CDL without opening one explicitly.

## 10. Closure condition and 348+ boundary

Window 347 closure must verify:
- `CDL-034` through `CDL-038` were opened in their designated lanes,
- `CDL-034` through `CDL-038` remain open and unratified,
- no runtime implementation was smuggled in under prelock or adjunct-contract work,
- the ratification-readiness package is complete.

Window 348+ boundary:
- Window 348+ begins with ratification work rather than runtime implementation.
- Runtime implementation remains barred until the relevant CDL is ratified.
- The first authorized Window-348+ work is controlled ratification of `CDL-034` through `CDL-038`.

## 11. Non-goals and explicit boundaries

This Phase-338 sequence lock does not:
- open or ratify any CDL row,
- modify `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- implement runtime behavior in `ilc_core/`,
- authorize reputation thresholds as if they were constitutional,
- authorize implementation merely because prelock artifacts exist.

Boundary statement:
- no decision-log mutation in Phase 338,
- no `ilc_core/` runtime implementation in Phase 338.

## 12. Forward pointer

Phase 339 resolves the `ADM-003` role split so that Window 340-344 schema-opening lanes can proceed without blurring evaluation-panel authority and schema-evolution monitoring.
