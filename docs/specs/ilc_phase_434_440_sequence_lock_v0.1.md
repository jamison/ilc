# ILC Phase 434-440 Sequence Lock v0.1

Status: Phase-434 sequence lock artifact
Date: 2026-03-17
Owner lane: G8 Constitution Cluster A

## 1. Window identity and scope

Window 434+ is the Runtime Tranche and Treasury P_e Prerequisite Review Block.

This baseline locks a 7-phase window: 434-440.

The scope of this baseline is limited to the numbered main-track runtime tranche, a non-ratifying Treasury `P_e` prerequisite review, synthesis, and a closure gate.

## 2. Inputs and closure inheritance

This sequence lock inherits the settled closure state from Window 424-433:
- `CDL-049` is ratified.
- CDL-050 is not pre-authorized at Phase 434 entry.
- Window 434+ may advance the Treasury P_e constitutional lane only after satisfying at least one Phase 431 prerequisite.
- The SIM-009 pair `0.2 / 0.02` remains a provisional planning anchor only.
- Release engineering packaging/bootstrap remains a parallel administrative track and does not consume numbered phases in this baseline.

## 3. Runtime tranche authorization and release-engineering separation

Window 434+ must cherry-pick the release-track runtime tranche before any public repo packaging commits are merged.

The numbered main-track lane in this baseline is authorized to plan around the runtime tranche only. Packaging/bootstrap work remains outside the numbered window unless a later governance decision rewrites that policy.
In operational terms, packaging/bootstrap remains outside numbered phases unless a later governance decision rewrites that policy.

## 4. Locked phase table (434-440 baseline)

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 434 | Sequence lock + runtime tranche intake freeze | Foundation / Control | SENSITIVE |
| 2 | 435 | Runtime tranche I: peer fanout integration | Runtime | SENSITIVE |
| 3 | 436 | Runtime tranche II: benchmark harness + tranche completion | Runtime / Tooling | SENSITIVE |
| 4 | 437 | Runtime tranche findings memo and regression hardening | Review / Stabilization | NON-SENSITIVE |
| 5 | 438 | Treasury P_e prerequisite-satisfaction review | Governance review | NON-SENSITIVE |
| 6 | 439 | Coherence + capsule v1.8 | Synthesis | NON-SENSITIVE |
| 7 | 440 | Closure gate + next-window handoff | Gate | SENSITIVE |

## 5. Treasury P_e prerequisite-review boundary

Phase 438 is a non-ratifying Treasury P_e prerequisite-satisfaction review.

Phase 438 may assess whether `CDL-050` can be opened in a later window or whether the Treasury `P_e` lane remains a carry-forward item. It does not itself open, amend, or ratify any CDL row in this baseline.

## 6. Extension rule for 441+

Any move to Phases 441+ requires an explicit sequence-lock amendment after Phase 438.

If such an amendment is justified, it must explain why the Treasury `P_e` evidence state has improved enough to support a future `CDL-050` opening and whether the current window should be extended or a new window should begin.

## 7. Sensitivity mapping and merge-timing rule

Sensitivity mapping for the 434-440 baseline:
- SENSITIVE: Phases 434, 435, 436, 440.
- NON-SENSITIVE: Phases 437, 438, 439.

Merge-timing rule:
- runtime tranche first,
- packaging/bootstrap later and outside the numbered baseline unless explicitly changed,
- do not let packaging commits arrive on `main` ahead of the runtime tranche.

## 8. Canonical anchors and non-goals

Canonical anchors:
- `docs/specs/ilc_window_424_433_handoff_433_v0.1.md`
- `docs/specs/ilc_pe_stabilization_carry_forward_decision_431_v0.1.md`
- `docs/specs/ilc_sim_009_results_synthesis_and_pe_stabilization_disposition_430_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v1.7.md`
- `../ILC_release_track/docs/handoffs/main_track_handoff_window_434_runtime_tranche_v0.1.md`

Non-goals in Phase 434:
- no runtime import execution,
- no packaging/bootstrap merge,
- no `CDL-050` opening,
- no decision-log mutation,
- no `ilc_core/` mutation.
