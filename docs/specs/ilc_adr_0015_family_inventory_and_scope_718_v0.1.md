# ILC ADR-0015 Family Inventory And Scope 718 v0.1

**Phase:** 718  
**Window:** 717-722  
**Date:** 2026-04-18  
**Author:** Codex

`adr_0015_family_inventory_complete`

## 1. Baseline

Window `717-722` is active under the Phase `717` sequence lock. This phase does
not publish the final ADR-0015 verdict. It inventories the four linked
mechanisms that still require explicit closure in-window:

- transfer tax,
- cooling period,
- commons dedication,
- leasehold / reversion.

Final ADR-0015 verdicts are deferred to a later phase in this window.
`final_disposition_deferred_to_later_phase`

## 2. Family inventory

The inventory covers transfer tax, cooling period, commons dedication, and
leasehold / reversion.

**Transfer tax**

ADR-0015 permits protocol-visible node transfers because otherwise the market
routes around the protocol through agent-identity sales. Transfer moves income rights only, never creator attribution. The current documented form is a progressive, time-sensitive tax payable at transfer time, with numeric
calibration still open.

**Cooling period**

ADR-0015 defines a post-transfer cooling window in which reuse ECU generation
is suspended or reduced for `N` epochs and the node remains especially open to
refutation challenge. The mechanism exists as an anti-speculation and
knowledge-quality guardrail, but the duration class is still calibration
dependent.

**Commons dedication**

ADR-0015 and the economic architecture both preserve a voluntary, irrevocable
commons-dedication path for income rights, while keeping authorship permanent.
The documented exception is a validated IP-dispute reversal that transfers
income rights to the true owner without rewriting authorship.

**Leasehold / reversion**

ADR-0015 treats leasehold / reversion as a proposed model rather than a settled
activation. Node income rights would have a constitutional lifespan, after
which income reverts to the commons. reset-on-transfer is described as a model option, not as a settled live rule. `leasehold_still_simulation_dependent`

## 3. Inherited governing constraints

The family does not start from zero. The inherited constraints are:

- creator attribution permanence remains locked by the authored payload model,
- transfer moves income rights only and not creator attribution,
- economic concentration does not convert into protocol governance influence,
- commons routing cannot silently bypass the existing `CDL-047` treasury lane,
- ECU-time and mandatory-conversion discipline remain inherited from `CDL-048`,
- leasehold / reversion remains evidence-bearing rather than silently active.

`creator_attribution_permanence_preserved`
`governance_decoupling_preserved`

## 4. Launch-bound versus deferred decision inputs

This phase does not make the final launch-bound decision, but it records the
decision inputs honestly.

Transfer tax is already grounded as a protocol-visible anti-circumvention
mechanism, yet its numeric rates remain open. Cooling period is grounded as a
quality and anti-speculation mechanism, yet its exact duration and suspension
profile remain open. Commons dedication is grounded as a routing and dedication
boundary, but its live closure must remain inside the existing treasury /
public-goods lane. Leasehold / reversion is the least mature mechanism because
duration class, reversion trigger shape, and reset-on-transfer posture still
depend on evidence.

## 5. Simulation and evidence dependencies

The remaining evidence dependencies are:

- transfer-tax calibration under realistic transfer-volume and anti-speculation
  scenarios,
- cooling-period duration and whether full suspension or reduced reuse better
  preserves quality without freezing legitimate transfers,
- leasehold duration class and reversion timing under long-run reuse patterns,
- reset-on-transfer versus non-reset lease behavior,
- the replay / simulation contract needed to close the family honestly in later
  phases.

Leasehold / reversion remains evidence-bearing and is not honest launch law
without that evidence.

## 6. Non-goals

This phase does not:

- mutate the constitutional decision log,
- ratify any new CDL,
- publish the final ADR-0015 disposition,
- mutate `ilc_core/` or `ilc_consensus/`,
- claim that leasehold / reversion is already activated,
- expand commons routing beyond the inherited treasury-governance boundary.
