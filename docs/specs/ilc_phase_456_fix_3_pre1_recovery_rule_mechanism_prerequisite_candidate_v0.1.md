# ILC Phase 456 Fix 3 Pre1 Recovery-Rule Mechanism Prerequisite Candidate v0.1

Status: planning candidate only. Not executed. Does not reopen `CDL-050` or authorize later fixes.
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

## 1. Why this prerequisite exists

Phase 456 Fix 2 strengthened the evidence record but left `Blocker 1` open.

The resulting repo-grounded diagnosis is now stricter than the original Fix-1 diagnosis:

- the current Scenario-5 family still fails the registered separation thresholds on
  `organic ECU production rate` and `P_e clamp-respect rate`,
- the current candidate family is expressed in briefs and evidence artifacts,
- but the repo does not currently expose a reusable `ilc_core/` Treasury recovery-rule mechanism
  surface for Scenario 5 candidate classes,
- therefore Fix 3 cannot honestly begin as "just freeze a new brief and run oscillator variants."

A prerequisite lane is needed first.

## 2. Repo-grounded findings that force the prerequisite

Current findings from the local repo state:

- `mixed_queue_and_production` is present in the Phase-454 Scenario-5 baseline at
  `out/treasury_sim/phase_454/scenario_results.csv:18`.
- no oscillator-style Treasury recovery-rule implementation is present in `ilc_core/`.
- no `production_band`, `clamp_floor`, or `mixed_queue_and_production` Treasury mechanism is
  implemented in `ilc_core/`.
- the only `recovery` surfaces in `ilc_core/` are unrelated claim-timeout or security recovery
  paths, not Scenario-5 Treasury recovery logic.

Practical implication:

- any future oscillator family is currently a design hypothesis, not a runnable mechanism.

## 3. Recommended next sequence

The cleanest continuation after Fix 2 is:

1. `Phase 456 Fix 3 Pre1` — define and lock the executable Scenario-5 mechanism surface
2. `Phase 456 Fix 3` — implement the approved runnable mechanism surface in `ilc_core/` and/or
   the simulation lane
3. `Phase 456 Fix 4` — freeze the next commission brief only after the mechanism surface exists
4. `Phase 456 Fix 5` — execute the expanded family, publish synthesis, and reassess `Blocker 1`

This keeps planning, implementation, and evidence separate.

## 4. Purpose of Fix 3 Pre1

Fix 3 Pre1 should do exactly four things:

1. document what Scenario-5 mechanism surfaces are actually missing,
2. define the minimal executable abstraction needed for future recovery-rule families,
3. decide which candidate classes are admissible for the next brief,
4. define the implementation exit criteria that must be satisfied before any Fix-4 brief freeze.

## 5. Candidate mechanism classes to evaluate

Fix 3 Pre1 should evaluate the following candidate classes without yet freezing any one as the
next winner:

### A. Uniform production-band family

Carry-forward baseline from Fix 2:

- `production_band_5_epoch`
- `production_band_6_epoch`
- `production_band_7_epoch`
- `production_band_8_epoch`
- `production_band_10_epoch`

Purpose:

- preserve a continuity baseline against which future alternatives are measured.

### B. Clamp-floor family

Carry-forward structural challenger from Fix 2:

- `production_band_5_epoch_with_clamp_floor_low`
- `production_band_5_epoch_with_clamp_floor_high`

Purpose:

- preserve the current non-uniform structural alternative already tested in Fix 2.

### C. Oscillating recovery-rule family

Candidate future class, not yet implemented:

- `oscillating_production_band_short_period`
- `oscillating_production_band_long_period`

Required parameter surfaces to define before any execution brief:

- `oscillation_period`
- `oscillation_amplitude`
- `phase_offset`
- evaluation-window interaction rules

### D. Fixed weak-field challenger

Keep `mixed_queue_and_production` available as a fixed architectural contrast anchor unless a later
brief explicitly removes it with justification.

Purpose:

- preserve a stable weak-field baseline so future threshold comparisons do not become artificially
  easy through family narrowing alone.

## 6. Required Fix 3 Pre1 outputs

The prerequisite phase should publish at minimum:

- a mechanism-surface definition for Scenario-5 candidate classes,
- an admissibility boundary for future recovery-rule families,
- an implementation-prerequisite artifact stating what must exist in `ilc_core/` or the simulation
  lane before Fix 4 may freeze a new brief,
- a test file guarding the docs-only contract and non-widening rule,
- a walkthrough and `STATUS.md` entry.

## 7. Non-goals

Fix 3 Pre1 should not:

- run new Scenario-5 simulations,
- reopen `CDL-050`,
- revise Phase-453 thresholds,
- reinterpret Window `450-459` as passed,
- widen into pressure-flow, `CDL-052`, `CDL-053`, or long-tail work,
- or silently implement oscillator logic without first locking the mechanism boundary.

## 8. Exit criteria before Fix 4 can exist

Fix 4 should not be authorized unless Fix 3 Pre1 and Fix 3 jointly establish:

- a named executable Scenario-5 mechanism surface,
- explicit parameter surfaces for each admissible family,
- a decision on whether oscillators are in scope,
- measurement-window rules that prevent phase-cancel averaging,
- a stable weak-field baseline policy for `mixed_queue_and_production`,
- and an explicit Fix-5 field composition decision stating whether strong production-band
  carry-forwards remain in the comparison field.

That field-composition decision must also state whether retaining strong production-band
carry-forwards makes the registered `10` percentage-point organic-production threshold
structurally unachievable for any future oscillator family.

## 9. Working rule

Do not treat the oscillator idea as automatically approved.

Treat it as a candidate mechanism class that must first pass:

- implementation-feasibility review,
- mechanism-surface definition,
- and explicit brief admissibility locking.
