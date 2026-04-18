# ILC Leasehold Duration And Reversion Calibration Note 720 v0.1

**Phase:** 720  
**Window:** 717-722  
**Date:** 2026-04-18  
**Author:** Codex

## 1. Baseline

Leasehold / reversion remains the least mature member of the ADR-0015 family.
ADR-0015 and the economic architecture describe it as a proposed model whose
activation still depends on simulation rather than an already settled launch
rule. `leasehold_remains_simulation_dependent`

## 2. Candidate duration classes

The candidate duration classes are:

- long epoch-count lease,
- issuance-era or epoch-band lease,
- adaptive lease tuned by later evidence.

This phase does not choose a final numeric duration. It only records the class
space that later evidence must evaluate.

## 3. Reversion trigger taxonomy

The explicit reversion trigger taxonomy is:

- time-expiry reversion after the lease horizon,
- validated IP-dispute correction,
- transfer-followed continuation or reset depending on later policy choice.

`reversion_trigger_taxonomy_explicit`

## 4. Transfer-reset question

Reset-on-transfer is still open.

The repo documents resettable-on-transfer as a model option, but this phase
does not accept it, reject it, or silently activate it. The honest current
state is that transfer-reset remains unresolved until evidence compares reset
versus continuity behavior.

## 5. Evidence boundary and deferment options

Leasehold activation is deferred rather than launch-authorized in this window.
`leasehold_activation_not_silently_authorized_here`

The evidence boundary still includes:

- duration-class calibration,
- reversion timing effects on late-economy revenue,
- reset-on-transfer versus continuity,
- interaction with reuse incentives and transfer frequency.

The honest current posture is `deferred`, not `launch_bound`.
