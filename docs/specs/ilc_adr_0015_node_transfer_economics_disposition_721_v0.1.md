# ILC ADR-0015 Node Transfer Economics Disposition 721 v0.1

**Phase:** 721  
**Window:** 717-722  
**Date:** 2026-04-18  
**Author:** Codex

## 1. Baseline

Window `717-722` required explicit closure of the ADR-0015 family. Phases
`718-720` established the inventory, the transfer-tax and cooling package, and
the commons / leasehold boundary. This phase now records the final family
disposition without ratifying a new CDL.

`adr_0015_family_disposition_explicit`

## 2. Per-mechanism verdicts

The explicit verdicts are:

- transfer tax: amended_accept,
- cooling period: amended_accept,
- commons dedication: amended_accept,
- leasehold / reversion: deferred.

Transfer tax is accepted in visible, taxed, anti-speculation form with numeric
calibration deferred. Cooling period is accepted as an epoch-based challenge
window with exact duration deferred. Commons dedication is accepted as a
voluntary mechanism under bounded `CDL-047` routing. Leasehold / reversion is
deferred because activation still depends on missing simulation evidence.

`per_mechanism_verdicts_recorded`

## 3. Launch-bound versus deferred matrix

The launch-bound versus deferred matrix is:

- transfer tax -> `launch_bound`,
- cooling period -> `launch_bound`,
- commons dedication -> `launch_bound`,
- leasehold / reversion -> `deferred`.

No `post_launch_bound` mechanism is created in this family close. The window
either binds the mechanism now or explicitly defers it.

`launch_bound_post_launch_bound_and_deferred_matrix_recorded`

## 4. Required follow-on evidence

The required follow-on evidence remains:

- numeric transfer-tax range calibration,
- exact cooling-period epoch count,
- leasehold duration-class and reversion trigger calibration,
- reset-on-transfer versus continuity evidence,
- replay evidence showing how the deferred leasehold branch behaves under
  realistic transfer and reuse conditions.

## 5. Non-ratification boundary

No CDL ratification occurs in Phase 721.

This disposition is a spec / contract closure for the ADR-0015 family. It does
not mutate the constitutional decision log, and it does not claim runtime
implementation or evidence results.

`no_cdl_ratification_occurs_in_phase_721`
