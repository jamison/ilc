# ILC Phase 456 Fix 3 Pre1 Recovery-Rule Mechanism Surface Definition v0.1

Status: Phase-456 Fix-3-Pre1 mechanism-surface definition
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

## 1. Current repository state

No executable Treasury recovery-rule mechanism exists in ilc_core today.

Current repo-grounded state:

- `mixed_queue_and_production` remains present in the original Scenario-5 evidence field at
  `out/treasury_sim/phase_454/scenario_results.csv:18`,
- the current Scenario-5 candidate family exists in briefs and evidence artifacts,
- but the candidate families are not backed by a reusable executable Treasury mechanism surface in
  `ilc_core/`.

## 2. Missing mechanism surfaces

The repo is missing at least four surfaces needed before a later Fix-4 brief can honestly freeze an
expanded family:

- a named Scenario-5 recovery-rule abstraction,
- a uniform production-band mechanism surface,
- a clamp-floor mechanism surface,
- an oscillator-capable mechanism surface with explicit scheduling semantics.

These are prerequisite mechanism gaps, not evidence gaps.

## 3. Candidate mechanism classes

Candidate classes that later phases may implement and test:

- carry-forward baseline: `Subfamily A - epoch-window variants`
- carry-forward structural challenger: `Subfamily B - clamp-floor variants`
- candidate future class: `oscillating_production_band_short_period`
- candidate future class: `oscillating_production_band_long_period`
- fixed weak-field contrast anchor: `mixed_queue_and_production`

## 4. Measurement-window and parameterization requirements

Any later oscillator family must define:

- `oscillation_period`
- `oscillation_amplitude`
- `phase_offset`
- measurement-window rules that prevent phase-cancel averaging across the evaluation horizon

The mechanism surface must also preserve comparability to the existing production-band baseline
rather than redefining the Scenario-5 objective itself.

## 5. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 456 Fix 3 Pre1.

This phase defines prerequisite mechanism surfaces only.
