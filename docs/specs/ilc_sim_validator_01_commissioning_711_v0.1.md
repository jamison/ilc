# ILC SIM-VALIDATOR-01 Commissioning 711 v0.1

**Date:** 2026-04-17  
**Phase:** 711  
**Status:** Commissioned

Tokens:
- `sim_validator_01_commissioned`
- `stake_floor_not_yet_constitutional_numeric_law`
- `equivocation_must_be_economically_irrational`
- `sim_validator_01_results_required_before_cdl_017_numeric_floor`

## 1. Purpose and calibrated question

`SIM-VALIDATOR-01` is commissioned to answer one narrow question:

> What minimum ECU validator stake floor makes equivocation economically
> irrational across the intended validator operating envelope?

This simulation is not allowed to wander into generalized validator-economics
theory. Its purpose is the Q2 consequence from Phase `710`: `CDL-017` may name a
required floor class, but may not lock a numeric floor before evidence exists.

`equivocation_must_be_economically_irrational`

## 2. Inputs and parameter sweep

The simulation must sweep at minimum:

- validator population size `N`,
- tolerated Byzantine fraction `F`,
- expected transfer volume per epoch,
- `CDL-055` slash-rate assumptions,
- equivocation detection latency,
- reward / fee expectations for honest participation,
- adversary gain bounds from successful conflicting execution attempts.

The simulation should also include sensitivity sweeps for:

- lower-volume and higher-volume operating regimes,
- faster and slower detection assumptions,
- thinner and thicker slash policies inside the constitutionally admissible
  interpretation of the current validator-slash lane.

## 3. Required outputs and failure criteria

Required outputs:

- a candidate stake-floor interval rather than a conversation-picked constant,
- payoff curves showing adversary expected value under equivocation,
- a sensitivity table identifying which parameters move the floor most,
- a short explanation of what floor, if any, remains stable across the tested
  operating envelope.

Failure criteria:

- any modeled equivocation regime remains non-negative expected value at or
  above the proposed floor,
- the proposed floor changes materially under ordinary parameter shifts,
- the simulation cannot explain which assumptions dominate the floor result.

## 4. Constitutional consequence and evidence threshold

`stake_floor_not_yet_constitutional_numeric_law`

`sim_validator_01_results_required_before_cdl_017_numeric_floor`

The constitutional consequence is narrow:

- before `SIM-VALIDATOR-01`, `CDL-017` may state that a minimum ECU stake floor
  is required,
- after `SIM-VALIDATOR-01`, later `CDL-017` convergence text may select a
  numeric floor only if the simulation shows equivocation is economically
  irrational across the agreed operating envelope.

Evidence threshold before any numeric floor becomes stronger law:

- the payoff analysis must stay negative for equivocation across the accepted
  envelope,
- the result must identify the dominant sensitivity dimensions,
- the result must be reproducible from deterministic inputs,
- the chosen floor must be routed through later `CDL-017` convergence work
  rather than treated as auto-ratified by this commissioning note.
