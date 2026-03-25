# ILC Phase 456 Fix 3 Recovery-Rule Mechanism Surface Attestation v0.1

Status: Phase-456 Fix-3 mechanism surface attestation
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

## 1. Implemented module boundary

`simulations/sim_treasury_scenario5_recovery_rule.py` is the named executable Scenario-5 recovery-rule abstraction for the current carry-forward lane.

The module exposes a callable `(candidate_id, parameters)` surface, preserves the non-constitutional implementation boundary in `simulations/`, and satisfies the Pre1 exit criteria for a runnable uniform production-band surface and a runnable clamp-floor surface.

## 2. Runnable carry-forward candidates

The implemented candidate registry now makes the seven Fix-2 registered candidates callable together with `mixed_queue_and_production` as the weak-field anchor.

Runnable carry-forward candidates include the five epoch-window variants, the two clamp-floor variants, and `mixed_queue_and_production` as the fixed contrast anchor carried forward from the original Scenario-5 baseline.

## 3. Oscillator mechanism status

`oscillator_mechanism_status=stubbed`

The oscillator parameter interface now exists with `oscillation_period`, `oscillation_amplitude`, and `phase_offset`, but runnable oscillator logic is not implemented in Phase 456 Fix 3. Fix 4 may not freeze oscillator candidates unless oscillator_mechanism_status=implemented.

## 4. Non-execution statement

No Scenario-5 execution occurs in Phase 456 Fix 3.

This phase implements the callable mechanism surface only. It does not run a new commission brief, does not publish new Scenario-5 raw outputs, and does not claim that oscillator candidates have been executed.

## 5. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 456 Fix 3.

The implemented surface is simulation scaffolding only. It does not reopen Blocker 1, does not revise thresholds, and does not authorize Phase 456 Fix 5 execution without a later Fix 4 brief freeze.
