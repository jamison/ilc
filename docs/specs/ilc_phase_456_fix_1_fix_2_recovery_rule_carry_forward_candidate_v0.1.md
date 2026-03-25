# ILC Phase 456 Fix 1 / Fix 2 Recovery-Rule Carry-Forward Candidate v0.1

Status: planning candidate only. Not a sequence lock. Not a commission brief. Does not reopen
`CDL-050` or authorize Phases `457-459`.
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

Purpose: define the narrow carry-forward shape recommended after the failed Phase-456 gate so the
project can strengthen `Blocker 1` evidence without widening Window `460-468`, retroactively
rewriting Phase `453`, or silently reactivating the failed Window `450-459` path.

---

## 1. Why this candidate exists

Phase `456` failed because `Blocker 1` remained open while `Blocker 2`, `Blocker 3`, and the
L1/L2 prerequisite cleared.

The corrected Phase-456 diagnosis is specific:

- the failure surface is insufficient separation on the primary Scenario-5 observables,
  `organic ECU production rate` and `P_e clamp-respect rate`,
- duration and intervention cost already separate inside the registered family,
- therefore the next evidence lane must target stronger separation on the primary observables,
  not generic duration/cost optimization.

Primary anchors:

- `docs/specs/ilc_treasury_sim_t_commission_brief_453_v0.1.md`
- `docs/specs/ilc_treasury_sim_t_comparative_synthesis_455_v0.1.md`
- `docs/specs/ilc_cdl_050_blocker_clearance_gate_456_v0.1.md`
- `docs/phases/STATUS.md`

---

## 2. Inherited failure diagnosis that must stay frozen

The carry-forward lane should inherit the corrected Blocker-1 diagnosis from Phase `456`
verbatim in substance:

- `production_band_5_epoch` remains the lead candidate in the registered family,
- but it does not materially separate itself from the field on the registered primary
  observables,
- against `production_band_3_epoch`, the lead candidate improves organic ECU production only from
  `0.88` to `0.91` (`3.4` percentage points) and clamp-respect only from `0.84` to `0.86`
  (`2.4` percentage points),
- against `mixed_queue_and_production`, the lead candidate improves organic ECU production only
  from `0.83` to `0.91` (`9.6` percentage points) and clamp-respect only from `0.82` to `0.86`
  (`4.9` percentage points),
- the registered thresholds remain `10` percentage points on organic production and `5`
  percentage points on clamp-respect,
- duration and cost separate; they are not the blocker-preserving failure surface.

Planning rule:

- no Fix-1 brief may describe the carry-forward target as "duration/cost ambiguity";
- it must describe the target as "primary-observable separation on organic production and
  clamp-respect".

---

## 3. Recommended dedicated carry-forward shape

The cleanest response is a dedicated two-step carry-forward mini-window:

| Order | Phase label | Topic | Character | Sensitivity |
|-------|-------------|-------|-----------|-------------|
| 1 | Phase 456 Fix 1 | recovery-rule carry-forward sequence lock + narrow commission brief freeze | planning / constitutional | SENSITIVE |
| 2 | Phase 456 Fix 2 | recovery-rule execution, comparative synthesis, and refreshed Blocker-1 reassessment | simulation / evidence / gate | SENSITIVE |

Design rule:

- this mini-window is dedicated to recovery-rule evidence only,
- it does not amend Phase `453`,
- it does not reopen Window `450-459`,
- and it does not authorize Phases `457-459` by implication.

If Fix `2` succeeds, the output is only:

- a stronger recovery-rule evidence record, and
- a refreshed carry-forward verdict on whether `Blocker 1` is now evidentially closed.

Any future `CDL-050` reopening still requires a new explicit sequence lock outside the failed
Window `450-459` path.

---

## 4. Phase 456 Fix 1 candidate scope

Fix `1` should do exactly four things:

1. authorize a narrow post-Phase-456 recovery-rule evidence lane,
2. freeze the candidate family and subfamily structure before any new run begins,
3. freeze success criteria and thresholds without lowering them post hoc,
4. declare the outputs that Fix `2` must publish.

Fix `1` should not:

- reopen `CDL-050`,
- revise the Phase-453 thresholds,
- widen the work into general Treasury redesign,
- absorb `CDL-052`, pressure-flow, `CDL-053`, or long-tail research,
- or backflow this work into Window `460-468`.

Recommended Fix-1 outputs:

- a dedicated recovery-rule sequence-lock artifact,
- a dedicated narrow commission brief artifact for the recovery-rule lane,
- a test file that verifies the narrow family, fixed thresholds, and non-widening constraints,
- a walkthrough and `STATUS.md` entry.

---

## 5. Candidate recovery-rule family for Fix 1

Fix `1` should pre-register a narrow family centered on the already-identified strong region plus
one distinct structural challenger subfamily.

### 5.1 Subfamily A - epoch-window variants

Recommended baseline family:

- `production_band_5_epoch`
- `production_band_6_epoch`
- `production_band_7_epoch`
- `production_band_8_epoch`
- `production_band_10_epoch`

Rationale:

- this is a granular search around the current lead candidate,
- it stays inside the same architectural model family,
- and it directly tests whether the currently narrow margin failures can be turned into clear
  primary-observable separation without changing the underlying exit-rule logic.

### 5.2 Subfamily B - clamp-floor variants

Recommended distinct structural subfamily:

- `production_band_5_epoch_with_clamp_floor_low` with `clamp_floor=0.87`
- `production_band_5_epoch_with_clamp_floor_high` with `clamp_floor=0.90`

Both clamp-floor variants should be anchored to the current `5_epoch` lead region.

Planning rule:

- `clamp_floor_low=0.87` is justified because it matches the Phase-454
  `boundary_enforced` clamp-respect operating point and is the minimum floor value that sits
  above the registered `5` percentage-point separation bar against the weakest Scenario-5
  challenger,
- `clamp_floor_high=0.90` is justified because it matches the Phase-454
  `vesting_50_epoch` and `escrow_10x` clamp-respect operating points and tests whether a
  materially stronger clamp gate produces separation against both Scenario-5 challengers,
- the values are evidence-motivated parameters, not assumed measured outcomes,
- the actual Fix-2 verdict must still be based on measured Scenario-5 outcomes under the
  registered threshold rules,
- and the subfamily size must remain exactly the two named candidates above,
- clamp-floor variants must be registered as their own subfamily with their own blocker-coverage
  label in the brief,
- they must not be mixed into a single undifferentiated ranking with pure epoch-window variants,
- and comparative synthesis in Fix `2` must report intra-subfamily ranking before any
  cross-subfamily recommendation.

This keeps "finer search inside the same model" separate from "new recovery-rule condition".

### 5.3 Family boundary

Fix `1` should freeze the family narrowly enough that the lane cannot silently expand after
execution begins.

Recommended boundary:

- no new trigger observable,
- no threshold change,
- no new Treasury lever family,
- no new Scenario-5 objective,
- no family widening after execution begins without invalidating the brief.

---

## 6. Success criteria and thresholds that should remain unchanged

The Fix-1 brief should inherit the Phase-453 Scenario-5 structure rather than rewriting it.

Primary observables:

- `organic ECU production rate`
- `P_e clamp-respect rate`

Secondary observables:

- `intervention duration`
- `intervention cost`

Required discipline:

- the lead candidate must clear the registered primary-observable thresholds,
- threshold evaluation must be against the best remaining alternative in the full registered
  candidate set for the same blocker-coverage objective, not merely against the nearest family
  neighbor,
- duration and cost may break ties only after the threshold requirement is met,
- threshold revision is out of scope for Fix `1`,
- any move to revise the thresholds would require a separate constitutional argument and should
  be treated as a later fallback, not the default response to the failed gate.

This preserves the epistemic discipline of Phase `453` and avoids retrofitting the bar to the
evidence.

---

## 7. Phase 456 Fix 2 candidate scope

Fix `2` should execute the narrow recovery-rule lane frozen in Fix `1` and publish:

1. a reproducible evidence package,
2. a comparative synthesis artifact that distinguishes Subfamily A from Subfamily B,
3. a standalone refreshed Blocker-1 reassessment artifact,
4. a walkthrough and `STATUS.md` update.

Fix `2` should answer exactly three questions:

1. does any epoch-window candidate now materially separate on organic production and
   clamp-respect,
2. does any clamp-floor candidate materially separate on those same primary observables,
3. if both families produce viable leaders, which leader is preferred under the registered
   tie-break logic without collapsing the subfamily distinction.

Cross-subfamily reporting rule:

- if exactly one subfamily produces a threshold-clearing leader, that leader is the Fix-2
  recommendation without requiring cross-subfamily tie-break,
- cross-subfamily tie-break applies only when both subfamilies produce threshold-clearing leaders,
- if neither subfamily produces a threshold-clearing leader, `Blocker 1` remains open.

Fix `2` should not:

- open `CDL-050`,
- mutate the decision log,
- reactivate Phases `457-459`,
- or reinterpret the failed Window `450-459` gate as retroactively passed.

---

## 8. Expected post-Fix-2 outcomes

There are only three legitimate post-Fix-2 outcomes:

### Outcome A - Blocker 1 remains open

No candidate clears the registered primary-observable thresholds.

Result:

- `CDL-050` remains unopened,
- the recovery-rule lane remains a carry-forward item,
- any future work must either widen the evidence family again or explicitly revisit the
  threshold question under a new constitutional argument.

### Outcome B - Blocker 1 evidence closes

A candidate materially clears the registered thresholds on the primary observables.

Result:

- the recovery-rule blocker is evidentially closed,
- but `CDL-050` still does not automatically reopen,
- a separate future sequence lock is still required to decide whether and how to reopen the
  Treasury constitutional lane.

### Outcome C - Cross-subfamily recommendation remains ambiguous

One candidate leads Subfamily A and one candidate leads Subfamily B, but the cross-subfamily
recommendation is still practically ambiguous.

Result:

- the evidence lane succeeded at narrowing the field,
- but constitutional reopening remains deferred until the ambiguity is resolved explicitly rather
  than hand-waved away.

---

## 9. Review disposition before any pre-registration

The current review disposition is:

1. include `production_band_10_epoch` in Subfamily A rather than truncating the epoch-window
   search at `8_epoch`,
2. register exactly two clamp-floor variants in Subfamily B,
3. keep the refreshed Blocker-1 reassessment as a standalone artifact rather than embedding it as
   a section inside the comparative synthesis output,
4. evaluate threshold clearance against the best remaining alternative in the full registered
   candidate set,
5. apply cross-subfamily tie-break only when both subfamilies produce threshold-clearing leaders.
6. freeze `clamp_floor_low=0.87` and `clamp_floor_high=0.90` with explicit justification from
   the Phase-454 observed operating points.

This candidate is now ready to be translated into the actual Fix-1 sequence-lock and commission-
brief artifacts without further family-shape changes.
