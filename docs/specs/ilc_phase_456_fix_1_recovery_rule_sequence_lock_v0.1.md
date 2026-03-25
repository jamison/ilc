# ILC Phase 456 Fix 1 Recovery-Rule Sequence Lock v0.1

Status: Phase-456 Fix-1 sequence lock artifact
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

## 1. Window identity and non-reopening rule

Phase 456 Fix 1 opens a narrow carry-forward lane after the failed Phase-456 gate.

Window 450-459 remains failed and closed.

CDL-050 remains unopened.

Phases 457-459 remain unauthorized.

This sequence lock does not revive the failed Window 450-459 path. It opens only the
recovery-rule carry-forward mini-window consisting of:

- `Phase 456 Fix 1`
- `Phase 456 Fix 2`

Any future CDL-050 reopening still requires a new explicit sequence lock.

## 2. Inherited Blocker-1 diagnosis

The inherited failure surface from Phase 456 is unchanged:

- the recovery-rule problem remains primary-observable separation on `organic ECU production rate`
  and `P_e clamp-respect rate`,
- `production_band_5_epoch` remains the lead candidate in the original Scenario-5 family,
- the lead candidate improves organic ECU production and clamp-respect only narrowly against the
  registered challengers,
- Duration and cost do separate inside the family.

Therefore the carry-forward lane must target stronger separation on the primary observables
rather than a generic duration/cost search.

## 3. Authorized recovery-rule lane

The authorized carry-forward lane is limited to recovery-rule evidence only.

Blockers 2, 3, and the L1/L2 prerequisite remain cleared from Phase 456.

Blockers 2, 3, and the L1/L2 prerequisite are not reopened in Fix 1 or Fix 2.

The lane is authorized to:

- freeze a narrow recovery-rule commission brief,
- run only the registered recovery-rule family in Fix 2,
- publish comparative synthesis for the registered subfamilies,
- publish a standalone Blocker-1 reassessment artifact.

The lane is not authorized to:

- amend Phase 453,
- widen Window 460-468,
- or open CDL-050.

## 4. Scope and non-goals

In scope:

- preserve the inherited Blocker-1 diagnosis,
- freeze the candidate family and subfamily structure,
- preserve the registered threshold values from Phase 453,
- preserve the rule that duration/cost remain secondary observables,
- carry Fix 2 forward as an evidence-only reassessment lane.

Non-goals:

- no new trigger observable,
- no new Treasury lever family,
- no threshold change,
- no Scenario-5 objective change,
- no pressure-flow, CDL-052, CDL-053, or long-tail scope expansion,
- no decision-log mutation,
- no `ilc_core/` runtime changes.

## 5. Fix-2 required outputs

Fix 2 must publish the following outputs:

- `docs/specs/ilc_treasury_sim_t_recovery_rule_evidence_package_456_fix_2_v0.1.md`
- `docs/specs/ilc_treasury_sim_t_recovery_rule_comparative_synthesis_456_fix_2_v0.1.md`
- `docs/specs/ilc_cdl_050_blocker_1_reassessment_456_fix_2_v0.1.md`

The standalone Blocker-1 reassessment artifact must contain at minimum:

- lead candidate identifier,
- explicit threshold-clearance statement for both `organic ECU production rate` and
  `P_e clamp-respect rate`,
- exact verdict token `blocker_1_fix_2_verdict=` followed by `cleared` or `remains_open`.

Fix 2 must also preserve the distinction between:

- Subfamily A - epoch-window variants
- Subfamily B - clamp-floor variants

## 6. Non-authorization statement

Phase 456 Fix 1 does not authorize CDL-050 opening.

No CDL-050 opening or ratification occurs in Phase 456 Fix 1.

If Fix 2 later produces a threshold-clearing winner, that result closes only the recovery-rule
evidence question. It does not automatically reopen CDL-050 or reauthorize Phases 457-459.
