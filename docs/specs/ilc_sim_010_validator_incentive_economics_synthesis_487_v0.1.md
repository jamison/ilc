# ILC SIM-010 Validator Incentive Economics Synthesis 487 v0.1

Status: synthesis and recommendation output
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

SIM-010 verdict: pass

recommended_validator_reward_fraction: 0.02
recommended_genesis_stake_amount: 400.0
recommended_liveness_miss_threshold: 8

Key findings:

- Reward remains meaningful at `N_agents = 10,000` with `fraction = 0.02` and `validators = 7`.
- A `K = 50` staking multiple yields `stake_amount = 400.0` with a partial-slash payback window
  of `12.5` epochs.
- `miss_threshold = 8` is the balanced liveness point across false-slash risk, deterrence, and
  availability.
- SIM-010 therefore authorizes the validator economic and staking lanes to proceed to their
  constitutional openings.
