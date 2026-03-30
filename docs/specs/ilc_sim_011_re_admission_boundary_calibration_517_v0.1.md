# ILC SIM-011 re_admission_boundary Calibration 517 v0.1

Status: completed simulation synthesis
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

## 1. Simulation purpose and scope

SIM-011 narrows the validator re_admission boundary for Window 515-524. The simulation models
three scenarios only: liveness-miss recovery, equivocation recovery, and voluntary exit.
The output is a bounded set of cooldown-epoch constants for CDL-058 runtime implementation.

## 2. SIM-010 baseline constants

SIM-010 baseline constants consumed in this synthesis:
- `recommended_genesis_stake_amount: 400.0`
- `recommended_liveness_miss_threshold: 8`
- `recommended_validator_reward_fraction: 0.02`
- `equivocation_full_slash = 1.0` remains the severity anchor from CDL-055 runtime.

These constants establish the validator stake and liveness baseline; SIM-011 only narrows the
post-exit or post-penalty re-admission cooldown boundary.

## 3. Re-admission scenario modeling

Scenario A — liveness-miss recovery:
- validator breached the `liveness_miss_threshold = 8`
- validator did not equivocate
- objective: allow return after short cooling-off and operator remediation
- chosen policy basis: short cooldown to avoid permanent exclusion for recoverable downtime

Scenario B — equivocation recovery:
- validator triggered the equivocation slash boundary
- objective: preserve deterrence and governance clarity before re-entry
- chosen policy basis: materially longer cooldown than liveness recovery

Scenario C — voluntary exit:
- validator exited without slash or consensus fault
- objective: allow orderly churn without zero-friction validator flapping
- chosen policy basis: minimal but non-zero cooldown

## 4. Recommended cooldown constants

recommended_cooldown_epochs_liveness_miss: 2
recommended_cooldown_epochs_equivocation: 12
recommended_cooldown_epochs_voluntary_exit: 1

Calibration rationale:
- `recommended_cooldown_epochs_liveness_miss = 2` gives a short remediation window after a
  recoverable liveness failure without collapsing validator continuity.
- `recommended_cooldown_epochs_equivocation = 12` is deliberately stricter because equivocation
  is a consensus fault with full-slash severity and requires a visibly separate re-entry lane.
- `recommended_cooldown_epochs_voluntary_exit = 1` prevents immediate validator churn cycling
  while keeping orderly exit and later return low-friction.

## 5. CDL-046 timed_out orthogonality

cdl_046_timed_out_orthogonal

CDL-046 governs orphan timeout and node lifecycle re-attachment with
`orphan_timeout_epochs = 4` and `recovery_policy = stake_full_release`.
CDL-058 governs validator re-admission after validator exit or validator fault.
These are separate lanes: node lifecycle recovery does not determine validator re-entry.

## 6. Simulation sufficiency declaration

sim_011_sufficient

SIM-011 is sufficient to open CDL-058 on the narrow option `cooldown_period_per_exit_reason`.
The synthesis is intentionally limited to cooldown constants and does not authorize sponsor
attestation, reputation-floor gating, or stake re-deposit requirements in this window.
