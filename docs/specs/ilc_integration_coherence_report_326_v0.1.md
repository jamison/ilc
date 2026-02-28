# ILC Integration Coherence Report 326 v0.1

Status: Phase-326 integration coherence artifact  
Date: 2026-02-28  
Owner lane: G8 Constitution Cluster A

## 1. Scope

This artifact closes the non-sensitive coherence lane for window 318-327 through Phase 325 completion.

It does three things:
- confirms the constitutional and implementation state reached by Phases 319-325,
- formalizes the evidence-authority rule for future CDL-V ratification prompts,
- records the Phase-317 closure-gate snapshot isolation remediation as a coherence-level project invariant.

## 2. Window 318-325 completion alignment

Window-alignment statements:
- `CDL-020` is `ratified`.
- `CDL-022` is `ratified`.
- `CDL-023` is `ratified`.
- `CDL-024` remains `open`.
- `CDL-V1` through `CDL-V7` are `open`.
- no additional constitutional mutations occurred in Phase 326.

Phase alignment summary:
- Phase 319 ratified `CDL-020`.
- Phase 320 ratified `CDL-022`.
- Phase 321 ratified `CDL-023`.
- Phase 322 and Phase 323 established the `CDL-024` contract/runtime boundary while leaving it open.
- Phase 324 opened `CDL-V1`, `CDL-V2`, and `CDL-V3` with evidence-prelock artifacts.
- Phase 325 opened `CDL-V4`, `CDL-V5`, `CDL-V6`, and `CDL-V7` with evidence-prelock artifacts.

## 3. Snapshot isolation remediation

Phase 326 fixes the known closure-gate side effect in `tools/check_window_308_317_closure_gate_phase_317.sh`.

Normative remediation statements:
- ordinary Phase-317 closure-gate execution is no-write by default for `out/monitoring/infrastructure_risk_snapshot_phase_316.json`,
- explicit snapshot regeneration, if ever needed, requires opt-in via `ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE=1`,
- ordinary validation runs must not mutate canonical snapshot files under `out/monitoring/`,
- Phase-327 is closure only and is not the place to repair closure-gate mechanics.

## 4. Evidence-authority rule

Normative rule:
- future CDL-V ratification prompts must treat Section 3 of the corresponding evidence-prelock artifact as authoritative when it is more specific than the compressed `required_artifacts` column in the CDL row,
- the CDL row `required_artifacts` field is shorthand and does not override more specific Section-3 evidence obligations.

Implication:
- future ratification prompts for `CDL-V1` through `CDL-V7` must cite both the decision-log row and the paired evidence-prelock artifact,
- where a Section-3 list contains additional procedural or boundary evidence items, those items are part of the ratification contract and are not optional.

## 5. V-series ratification implications

The V-series no longer consists of seven independent ratification questions. Phase 326 locks the coherence-level dependency map that later ratification prompts must respect.

Coherence implications:
- `CDL-V2 -> CDL-V3 -> CDL-V4` is the governing identity/quorum/reopening chain,
- `CDL-V4 <-> CDL-V6` is a coupled governance boundary that must be specified from both directions,
- `CDL-V5 -> CDL-V7` is required so cross-agent decomposition reproducibility can be evaluated with explicit epoch/translation semantics,
- `CDL-V1 has no V-series ordering constraint` and may be ratified independently.

Carry-forward ratification implications:
- `CDL-V5` ratification must include explicit `non-comparable by design` handling,
- `CDL-V7` ratification must include tested graph-entry and reuse-value tie-back requirements,
- `CDL-V7` reproducibility must use a concrete evaluation protocol with explicit tolerance bounds for acceptable disagreement.

## 6. Non-goals and explicit boundaries

This phase does not:
- mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- ratify any additional CDL or CDL-V entry,
- modify `ilc_core/` runtime files,
- change the archived dry-run/output contract of the Phase-317 closure gate.

Boundary statement:
- Phase 326 is coherence and remediation only,
- Phase 327 inherits a stabilized closure foundation and remains a closure gate, not a repair lane.
