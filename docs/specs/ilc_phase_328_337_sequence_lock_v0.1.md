# ILC Phase 328-337 Sequence Lock v0.1

Status: Phase-328 sequence lock artifact  
Date: 2026-02-28  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and sequence scope

Lock execution order, dependency edges, sensitivity boundaries, and closure-gate carry-forward rules for the Phase 328-337 window.

This artifact is non-ratifying. It does not mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md` and does not implement runtime behavior in `ilc_core/`.

## 2. Entry state from phase-327 closure controls

Entry assumptions:
- Window 318-327 is closed and handed off (`docs/specs/ilc_window_318_327_handoff_327_v0.1.md`).
- Closure-gate contracts enforce deterministic dry-run formatting, recursion-safe selftest behavior, verdict-exit semantics, and snapshot-override isolation (`tools/check_window_318_327_closure_gate_phase_327.sh`).
- Phase-326 coherence artifacts remain authoritative for CDL-V sequencing, Section-3 evidence authority, and Phase-317 snapshot-isolation remediation (`docs/specs/ilc_integration_coherence_report_326_v0.1.md`, `docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md`, `docs/specs/ilc_antigravity_context_capsule_v0.7.md`).

## 3. Open constitutional inventory and window intent

Open constitutional inventory relevant to this window:
- `CDL-021`: rust kernel port and WASM distribution.
- `CDL-024`: wire protocol specification and transport bindings.
- `CDL-V1`: temporal decay for reuse-centrality weighting.
- `CDL-V2`: sybil-resistance requirements for identity and reuse validation.
- `CDL-V3`: quorum-diversity constraints for constitutional ratification.
- `CDL-V4`: minority dissent, appeal, and reopening protocol.
- `CDL-V5`: schema-epoch translation protocol and cross-version handling.
- `CDL-V6`: Genesis intervention protocol.
- `CDL-V7`: agent decomposition criteria.

Window 328-337 intent:
- ratify `CDL-024` after the deferred historical-prelock hardening patch in Phase 329,
- ratify the V-series in dependency-respecting order,
- keep `CDL-021` open but milestone-triggered and out of active execution in this window,
- execute Phase 334 as a coupled dual-row constitutional ratification lane for `CDL-V4` and `CDL-V6`,
- consolidate window state and carry-forward obligations in Phase 336,
- close the window with a composed closure gate and 338+ handoff in Phase 337.

## 4. Locked phase table (328-337)

| Order | Phase | Track | Scope | Sensitivity |
| --- | --- | --- | --- | --- |
| 1 | Phase 328 | Sequence lock lane | Lock 328-337 ordering, dependencies, sensitivity, closure skeleton | Non-sensitive |
| 2 | Phase 329 | Ratification lane | CDL-024 ratification + deferred historical-prelock hardening | Sensitive |
| 3 | Phase 330 | Ratification lane | CDL-V1 ratification | Sensitive |
| 4 | Phase 331 | Ratification lane | CDL-V2 ratification | Sensitive |
| 5 | Phase 332 | Ratification lane | CDL-V3 ratification | Sensitive |
| 6 | Phase 333 | Ratification lane | CDL-V5 ratification | Sensitive |
| 7 | Phase 334 | Ratification lane | CDL-V4 + CDL-V6 coupled dual-row ratification | Sensitive |
| 8 | Phase 335 | Ratification lane | CDL-V7 ratification | Sensitive |
| 9 | Phase 336 | Coherence/capsule lane | Integration coherence, capsule v0.8, and carry-forward consolidation | Non-sensitive |
| 10 | Phase 337 | Closure/handoff lane | 328-337 closure verification gate and 338+ handoff | Sensitive |

## 5. Per-phase sensitivity classification

| Phase | Sensitivity |
| --- | --- |
| Phase 328 | Non-sensitive |
| Phase 329 | Sensitive |
| Phase 330 | Sensitive |
| Phase 331 | Sensitive |
| Phase 332 | Sensitive |
| Phase 333 | Sensitive |
| Phase 334 | Sensitive |
| Phase 335 | Sensitive |
| Phase 336 | Non-sensitive |
| Phase 337 | Sensitive |

Sensitivity rationale highlights:
- phases `329` through `335` are sensitive because they ratify constitutional rows,
- phase `334` is sensitive as a dual-row constitutional mutation lane rather than the standard one-row ratification pattern,
- phase `337` remains sensitive as the closure gate and 338+ handoff authority lane.

## 6. Dependency map and synchronization rules

Track model:
- Ratification track phases: `329`, `330`, `331`, `332`, `333`, `334`, `335`.
- Coherence/capsule lane phase: `336`.
- Closure/handoff lane phase: `337`.

Synchronization rules:
1. `329` requires the completed Phase-322 contract/evidence artifact and Phase-323 runtime handoff.
2. `330` requires Phase-328 sequence lock completion and no additional dependency from the V-series.
3. `331` requires Phase-330 completion only as optional sequencing hygiene; its mandatory dependency is the published sequence lock.
4. `332` requires `331` because `CDL-V2 -> CDL-V3 -> CDL-V4`.
5. `333` requires the published sequence lock and no dependency on the `CDL-V2 -> CDL-V3 -> CDL-V4` chain.
6. `334` requires `332` and remains coupled to `CDL-V6` because `CDL-V4 <-> CDL-V6`.
7. `335` requires `333` because `CDL-V5 -> CDL-V7`.
8. `336` requires completion evidence from `329` through `335`.
9. `337` requires `336` completion evidence plus green closure prerequisites.

## 7. Mandatory entry and exit gates per phase

| Phase | Mandatory entry gate | Mandatory exit gate |
| --- | --- | --- |
| Phase 328 | Phase-327 closure gate and handoff are present. | Sequence lock artifact, tests, walkthrough, and STATUS entry are complete. |
| Phase 329 | Phase-328 sequence lock is complete; Phase-322/323 evidence chain is green; historical-prelock test hardening is included. | CDL-024 ratification evidence and mutation guardrails are complete. |
| Phase 330 | Phase-328 sequence lock is complete. | CDL-V1 ratification evidence and mutation guardrails are complete. |
| Phase 331 | Phase-328 sequence lock is complete. | CDL-V2 ratification evidence and mutation guardrails are complete. |
| Phase 332 | Phase-331 is complete. | CDL-V3 ratification evidence and mutation guardrails are complete, with the ordering-anchor break handled explicitly. |
| Phase 333 | Phase-328 sequence lock is complete. | CDL-V5 ratification evidence and mutation guardrails are complete. |
| Phase 334 | Phase-332 and Phase-333 are complete. | CDL-V4 and CDL-V6 ratify together with dual-row mutation guardrails enforced. |
| Phase 335 | Phase-333 is complete. | CDL-V7 ratification evidence and mutation guardrails are complete. |
| Phase 336 | Phases 329-335 are complete and green. | Coherence artifact, capsule update, and carry-forward consolidation are complete. |
| Phase 337 | Phase-336 is complete and green. | Closure gate passes all required categories and 338+ handoff is published. |

## 8. No-ratification-before-lock and authorization boundaries

Window-level guard:
- no ratification lane may execute in the 328-337 window unless this sequence lock is published first,
- authorized ratification lanes in this window are limited to phases `329`, `330`, `331`, `332`, `333`, `334`, and `335`.

Authorization boundaries:
- `CDL-021` remains `open`, milestone-triggered, and out-of-window for active execution in this sequence,
- Phase 334 is the only authorized dual-row constitutional mutation lane in this window,
- Phase 336 is coherence-only and does not ratify new constitutional rows.

## 9. V-series sequencing and special lane constraints

Locked sequencing rules:
- `CDL-V2 -> CDL-V3 -> CDL-V4`
- `CDL-V5 -> CDL-V7`
- `CDL-V4 <-> CDL-V6`
- `CDL-V1 has no V-series ordering constraint`

Special lane constraints:
- Phase 329 includes the deferred historical-prelock hardening patch for `tests/test_wire_transport_contract_and_cdl_024_evidence_prelock_322.py`, replacing the live-CDL status assertion with the historical `status: open` pattern.
- Phase 332 must handle the known structural risk that ratifying `CDL-V3` will break the raw-row anchor used by `tests/test_cdl_v_batch_a_open_and_evidence_prelock_324.py`.
- Phase 334 is a dual-row constitutional mutation lane. Exactly `CDL-V4` and `CDL-V6` may change, all other rows remain unchanged, and both rows transition `open -> ratified` in the same commit.
- Phase 335 must treat Section 3 of `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_evidence_prelock_325_v0.1.md` as authoritative, including the tested graph-entry and reuse-value tie-back requirement.

## 10. Closure-gate skeleton requirements for phase 337

Phase 337 must implement a composed closure gate with these command categories:
1. Prompt contract validation category.
2. Lane-specific contract tests category.
3. Cross-phase regression category.
4. Mutation canary category.
5. CLI contract category.
6. Walkthrough hygiene category.

Snapshot isolation/testing standard (mandatory carry-forward):
- closure gate script must accept `ILC_PHASE_<PHASE>_SNAPSHOT_PATH` as snapshot override input,
- closure-gate category execution that invokes the Phase-316 regression suite must isolate the snapshot via `ILC_PHASE_316_SNAPSHOT_PATH`,
- direct execution of `tests/test_infrastructure_composed_preflight_316.py` is a known residual on any direct execution path,
- entry-criteria or verification-command execution outside a gate category must immediately `git restore out/monitoring/infrastructure_risk_snapshot_phase_316.json`,
- tests must not mutate canonical snapshot files under `out/monitoring/`.

## 11. Non-goals and explicit boundaries

This Phase-328 sequence lock does not:
- ratify, open, or modify any CDL row,
- modify `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- implement runtime behavior in `ilc_core/`,
- authorize `CDL-021` execution without milestone trigger.

Boundary statement:
- no decision-log mutation in Phase 328,
- no `ilc_core/` runtime implementation in Phase 328.

## 12. Forward pointer

Phase 329 opens as the first sensitive ratification lane for `CDL-024`, followed by the ordered V-series ratification lanes, coherence consolidation in Phase 336, and the 328-337 closure gate in Phase 337.
