# ILC SIM-010 Validator Incentive Economics Contract v0.1

Status: commissioning contract only. Not constitutional evidence by itself.
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. Scenarios

SIM-010 executes exactly these four scenarios:

1. Reward fraction scan: 0.5%-5.0% of per-epoch write-fee-burn routed to the validator pool.
2. Staking sizing: stake amount = K x expected_epoch_reward for K in {10, 25, 50, 100}.
3. Liveness threshold sensitivity: miss-streak thresholds in {4, 8, 16} epochs.
4. Participation equilibrium: 7, 25, and 100 active validators at minimum viable and larger network sizes.

## 2. Required outputs

Phase 487 must publish these exact outputs:

- `recommended_validator_reward_fraction`
- `recommended_genesis_stake_amount`
- `recommended_liveness_miss_threshold`

## 3. Pass and fail criteria

SIM-010 passes only if all three required outputs can be recommended from executed evidence and at
least one scenario shows reward remains meaningful at `N_agents = 10,000`.

SIM-010 fails or blocks the constitutional lane if:

- any required output is absent,
- the reward remains non-meaningful at minimum viable scale,
- the stake sizing and liveness thresholds cannot be bounded honestly from the evidence.

SIM-010 does not authorize a CDL opening by itself.

## 4. Execution artifact contract

Phase 487 must emit its execution artifacts under `out/sim_010/phase_487/` at minimum as:

- `run_manifest.json`
- `results.csv`
- `summary_table.md`

## 5. Constitutional non-authorizations

This commissioning contract does not:

- ratify any validator economics parameter,
- open a validator CDL,
- amend CDL-046 or CDL-047,
- authorize `ilc_core/` mutation.

No `ilc_core/` implementation occurs in Phase 486.
No decision-log mutation occurs in Phase 486.
Phase 487 is the next authorized phase.
