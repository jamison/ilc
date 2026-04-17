# ILC ECU Kernel Profile Calibration Note v0.1

**Status:** Phase 703 calibration and replay contract
**Date:** 2026-04-17
**Window:** 701-706
**Disposition token:** `bal_profile_phase_703_disposition=spec_or_contract_lock`

`phase_703_calibration_contract_complete`
`ecu_kernel_four_component_scope_locked`
`bal_profile_active_default_unratified`
`phase_703_fixed_vector_profiles=EVEN|BAL|ROBUST|REFINE`
`phase_703_adapt_status=excluded_from_fixed_vector_sweep`
`phase_703_replay_tiers=100_agent_preflight|10000_agent_evidence`
`bal_profile_phase_703_disposition=spec_or_contract_lock`

## 1. Kernel under test

Phase 703 calibrates the current four-component ECU scoring kernel only.

The scored slots under test are:

- `reuse`
- `contradiction_resilience`
- `validation_integrity`
- `path_uplift`

These are the only Phase 703 weight-vector slots.

The following are explicitly not Phase 703 weight-vector slots:

- `freshness_gate`
- `CDL-V3` diversity floor
- stake
- generic recency

Those surfaces still matter economically, but they operate as adjacent guards,
constraints, or downstream modifiers rather than as entries in the four-slot ECU
weight vector.

The present repo/runtime baseline remains the BAL-weight default in
`DEFAULT_EW_WEIGHTS`, but this note does not ratify BAL as constitutional law.
The correct state after this phase is: BAL is active default and operationally
real, but still unratified as a final constitutional profile lock.

## 2. Fixed-vector candidate profile set

The fixed-vector candidate family for Phase 703 is:

- `EVEN = 0.25 / 0.25 / 0.25 / 0.25`
- `BAL = 0.35 / 0.25 / 0.20 / 0.20`
- `ROBUST = 0.20 / 0.45 / 0.20 / 0.15`
- `REFINE = 0.45 / 0.15 / 0.20 / 0.20`

Purpose of each profile in the calibration sweep:

- `EVEN`: null baseline with no intentional preference across the four kernel
  slots.
- `BAL`: current active default and the live planning assumption used in the
  kernel today.
- `ROBUST`: adversarial / regulated candidate that intentionally increases
  contradiction-resilience emphasis.
- `REFINE`: throughput / iteration candidate that intentionally increases reuse
  emphasis.

`ADAPT` is excluded from the fixed-vector sweep in this phase. It is not a
weight vector. It is a proposed adjustment algorithm that requires its own
formal specification and later governance treatment before any executable
profile-selection role can be assigned to it.

## 3. Deterministic replay tiers and inputs

Phase 703 defines two replay tiers and one common simulation posture.

Common posture:

- `40-epoch` simulation posture for every evidence-bearing replay in this phase
- deterministic input bundle with fixed seed, fixed agent population template,
  fixed protocol-parameter bundle, fixed adversarial share, and fixed ordering
  of claim / validation / refutation event generation
- same metric extraction contract for every profile under comparison

Tier A: `100-agent` deterministic preflight

- purpose: smoke-test the harness, metric extraction, and profile-difference
  logic before the large run
- population: synthetic `100-agent` replay population
- role: preflight only, not constitutional-grade evidence by itself

Tier B: `10,000-agent` deterministic evidence-bearing tier

- purpose: evidence-bearing comparison for any future stronger lock move
- population: synthetic `10,000-agent` replay population
- role: this is the minimum scale for profile-comparison evidence in this lane

Replay inputs must include, at minimum:

- the exact profile vector under test
- the deterministic seed value or replay-bundle identifier
- the fixed epoch count (`40`)
- the agent-population definition
- the adversarial-agent ratio and behavior mix
- the fixed scoring and payout parameter bundle used for the run
- the metric outputs captured per epoch and at terminal summary

The `7-agent` testnet is not the calibration evidence lane for Phase 703. It is
too small for this question and may be used only as an implementation sanity
surface, not as the main calibration evidence base.

## 4. Sensitivity dimensions and evaluation criteria

The Phase 703 calibration harness must report at least these evaluation
dimensions for each fixed-vector profile:

1. Intended profile-behavior differentiation
   - `ROBUST` should materially outperform `BAL` on contradiction-heavy or
     contested-node scenarios.
   - `REFINE` should materially outperform `BAL` on reuse-heavy or
     throughput-oriented scenarios.
   - `EVEN` serves as the null baseline for checking whether the active default
     and alternatives produce real, interpretable differences.

2. Honest-agent profitability
   - honest participants must remain economically viable across the replay
     window
   - no candidate profile should be eligible for stronger lock if its replay
     posture collapses honest-agent profitability relative to the current BAL
     baseline without an explicitly justified policy reason

3. Error / refutation behavior
   - the comparison must capture whether a candidate profile materially improves
     or degrades error detection, refutation profitability, or wrong-claim
     persistence over the `40-epoch` run

4. Reward concentration or inequality pressure
   - the comparison must report whether a candidate profile produces stronger
     reward concentration, higher inequality pressure, or more concentrated
     payout capture than the active BAL default

5. Throughput and scoring posture
   - the comparison should report claims scored above threshold, congestion
     effects, and whether profile differences are merely cosmetic or actually
     alter useful network behavior

A Phase 703 pass requires the harness contract to name these dimensions and
bind them to deterministic replay. It does not require selecting a winner.

## 5. Disposition and forward evidence threshold

Phase 703 closes the calibration ambiguity by locking the contract, not by
ratifying a profile.

Disposition:

- BAL remains the active default / planning assumption in the running kernel.
- BAL does not become ratified constitutional law in this phase.
- `bal_profile_phase_703_disposition=spec_or_contract_lock`

Forward evidence threshold for any later stronger lock:

1. the `100-agent` preflight tier must run cleanly and reproduce the expected
   directionality of the candidate profiles;
2. the `10,000-agent` evidence-bearing tier must complete under the declared
   deterministic replay bundle and `40-epoch` posture;
3. the results must publish a comparative metrics table covering intended
   differentiation, honest-agent profitability, error / refutation behavior,
   and reward concentration or inequality pressure;
4. the chosen recommendation, if any, must be reproducible from the published
   replay inputs without hidden tuning;
5. if those conditions are not met, no later constitutional-lock move is
   justified, and BAL remains only the active default / unratified assumption.

This phase therefore prevents the ambiguous middle state where BAL is treated as
real for planning but left without an explicit evidence contract. Calibration is
no longer "plan it later" work. The replay tiers, candidate set, and evidence
threshold are now named and locked.
