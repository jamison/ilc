# ILC Treasury SIM-T Commission Brief 453 v0.1

Status: Phase-453 SIM-T commission brief and measurement contract
Date: 2026-03-21
Owner lane: G8 Constitution Cluster A

This commission brief is pre-registered against `docs/specs/ilc_treasury_objective_function_and_observables_contract_451_v0.1.md` and the Phase-452 prerequisite disposition. SIM-T is the planning label for the Treasury adversarial simulation lane in Window 450-459.

## 1. Scenario matrix

The following five scenario families are frozen for SIM-T. Each family is registered before execution and maps directly to one or more Phase-451 observables.

- `Scenario 1 - Escrow multiplier discrimination`
  - Primary blocker coverage: `Blocker 2`
  - Primary observables: `productive backlog / queue-clearance behavior`, `organic ECU production rate`, `intervention duration and intervention cost`
  - Purpose: compare candidate escrow ceilings under overheating conditions to identify the lowest effective ceiling that constrains abuse without collapsing productive throughput.

- `Scenario 2 - Vesting lock duration discrimination`
  - Primary blocker coverage: `Blocker 2`
  - Primary observables: `release-shock amplitude after time-lock expiry`, `P_e clamp-respect rate`, `intervention duration and intervention cost`
  - Purpose: compare candidate lock durations and measure whether stability during intervention is purchased at the cost of a later destabilizing release shock.

- `Scenario 3 - L1/L2 contagion isolation test`
  - Primary blocker coverage: `Blocker 2`
  - Primary observables: `P_e clamp-respect rate`, `organic ECU production rate`
  - Purpose: test whether the Phase-452 prerequisite boundary keeps L2 collapse or liquidation pressure from becoming a direct L1 Treasury input.

- `Scenario 4 - Long-tail zero-issuance stress test`
  - Primary blocker coverage: `Blocker 3`
  - Primary observables: `P_e clamp-respect rate`, `productive backlog / queue-clearance behavior`, `intervention duration and intervention cost`
  - Purpose: test whether ECU-side levers remain discriminating under terminal-issuance conditions without relying on fresh ILC issuance subsidy.

- `Scenario 5 - Recovery criterion exit validation`
  - Primary blocker coverage: `Blocker 1`
  - Primary observables: `organic ECU production rate`, `P_e clamp-respect rate`, `intervention duration and intervention cost`
  - Purpose: compare decoupled recovery-rule candidates and determine whether they can exit intervention cleanly without trigger-coupling or Treasury-self-satisfaction.

`Blocker 1`, `Blocker 2`, and `Blocker 3` are all covered in the registered scenario matrix.

## 2. Parameter families

The following parameter families are frozen for SIM-T execution. Phase 454 may instantiate only values inside these registered families unless a later constitutional amendment explicitly expands them.

- Escrow multiplier family: `2x`, `5x`, `10x`, `20x`
- Vesting-extension family: `10`, `25`, `50`, `100` additional epochs
- Stress-load family: nominal load, elevated load, and `300%` verification-request spike
- Recovery-rule family: at least three candidate decoupled recovery rules, each using an organic-production observable distinct from the trigger observable
- Shock-shape family: single-pulse shock, sustained shock, and delayed-release shock
- Cost-accounting family: lever-specific cost tables that make intervention duration and intervention cost reproducible across runs

No parameter family may be narrowed or widened after simulation execution begins without invalidating the commission brief and carrying the blocker forward.

## 3. Seed and manifest policy

SIM-T execution must be reproducible.

The seed and manifest policy for Phase 454 is:
- each scenario family receives a manifest identifier,
- each concrete run receives a fixed seed or seed-generation record recorded in the manifest,
- manifests must include scenario family, parameter family selection, seed material, observable bindings, and output file locations,
- any tie-break or exclusion decision must point back to the originating manifest,
- comparative synthesis in Phase 455 must cite the exact manifest set used.

Seed generation is frozen by policy in Phase 453 even though no simulation is executed yet.

## 4. Success criteria

Success criteria are frozen before execution and must be evaluated only against the observables registered in the Phase-451 contract.

- `Scenario 1 - Escrow multiplier discrimination`
  - success means at least one escrow ceiling materially suppresses overload behavior while preserving stronger queue-clearance and organic ECU production than the harsher alternatives.

- `Scenario 2 - Vesting lock duration discrimination`
  - success means at least one duration improves clamp-respect behavior without producing a larger release-shock amplitude than the next-best candidate by a non-trivial margin.

- `Scenario 3 - L1/L2 contagion isolation test`
  - success means L2 collapse does not become a direct L1 Treasury signal and the resulting L1 observables remain materially separated from a contagion-coupled model.

- `Scenario 4 - Long-tail zero-issuance stress test`
  - success means at least one ECU-side configuration maintains acceptable clamp-respect and backlog behavior without hidden dependence on fresh issuance.

- `Scenario 5 - Recovery criterion exit validation`
  - success means at least one recovery rule exits only when organic ECU production normalizes, resists trigger-coupling, and outperforms weaker candidates on intervention duration and false-exit behavior.

No retroactive rewriting of success criteria after Phase 453.

## 5. Discriminating thresholds

A scenario family is discriminating only if the leading candidate clears the next-best candidate by a pre-registered margin on the governing observables.

The registered thresholds are:
- clamp-respect separation: at least `5` percentage points unless all candidates remain outside the clamp at materially similar rates,
- organic-production separation: at least `10` percentage points relative difference between candidate outcomes,
- backlog or queue-clearance separation: at least `10` percentage points on the governing queue metric,
- release-shock separation: at least `10` percentage points on the registered shock metric,
- intervention duration or cost separation: at least `10` percentage points unless a stronger separation is needed to break a practical tie.

If the leading candidate does not clear the applicable threshold, the result is ambiguous rather than provisionally decisive.

## 6. Tie-break logic

Tie-break logic applies only after the registered discriminating thresholds are checked.

The tie-break order is:
1. prefer the candidate with stronger performance on the scenario's primary observable,
2. if still tied, prefer the candidate with lower intervention duration and intervention cost,
3. if still tied, prefer the candidate with lower architectural complexity and fewer assumptions carried into later phases,
4. if still tied, declare the scenario family ambiguous rather than force a winner.

Tie-break logic does not override the discriminating-threshold requirement. It resolves only residual ties inside an already valid comparison set.

## 7. Ambiguous-outcome policy

Ambiguous simulation outcomes preserve the blocker rather than forcing closure.

Window 450-459 therefore treats ambiguity as a carry-forward condition, not as permission to choose a favorite narrative. If a scenario family fails to clear its registered threshold, the result stays open and the downstream blocker-clearance gate must reflect that ambiguity explicitly.

No CDL-050 opening or ratification occurs in Phase 453.
