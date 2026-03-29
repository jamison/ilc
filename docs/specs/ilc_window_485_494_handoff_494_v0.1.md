# ILC Window 485-494 Handoff 494 v0.1

Status: closure gate and handoff
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. Window summary

Window 485-494 is closed.

This window completed the validator economics evidence lane, implemented the already-ratified
CDL-045 validator circuit-breaker runtime surface, ratified the validator economic incentive
framework as CDL-054, and carried CDL-055 forward as an open staking-and-liveness lane.

CDL-053 remains reserved and unopened.
CDL-054 is ratified at window close.
CDL-055 remains status: open at window close.

## 2. Deliverable matrix

| Phase | Deliverable | Status |
| --- | --- | --- |
| 485 | `docs/specs/ilc_phase_485_494_sequence_lock_v0.1.md` | complete |
| 486 | `docs/specs/ilc_sim_010_validator_incentive_economics_contract_486_v0.1.md` | complete |
| 487 | `tools/run_sim_010_validator_incentive_economics.py`, `out/sim_010/phase_487/`, `docs/specs/ilc_sim_010_validator_incentive_economics_evidence_package_487_v0.1.md`, `docs/specs/ilc_sim_010_validator_incentive_economics_synthesis_487_v0.1.md` | complete |
| 488 | `ilc_core/consensus/circuit_breaker_interface.py`, `docs/specs/ilc_cdl_045_validator_circuit_breaker_surface_handoff_488_v0.1.md` | complete |
| 489 | `docs/specs/ilc_cdl_054_validator_economic_incentive_framework_opening_stub_489_v0.1.md` | complete |
| 490 | `docs/specs/ilc_cdl_054_validator_economic_incentive_framework_prelock_hardening_490_v0.1.md` | complete |
| 491 | `docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md` | complete |
| 492 | `docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_opening_stub_492_v0.1.md` | complete |
| 493 | `docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_prelock_hardening_493_v0.1.md` | complete |

## 3. SIM-010 summary

SIM-010 passed in Phase 487 and published the required evidence-sized recommendations:
- `recommended_validator_reward_fraction = 0.02`
- `recommended_genesis_stake_amount = 400.0`
- `recommended_liveness_miss_threshold = 8`

Those outputs were the required opening gate for the validator constitutional lanes in this
window.

## 4. Validator economic lane summary

The validator economic lane opened in Phase 489, hardened in Phase 490, and ratified in Phase 491
as CDL-054.

CDL-054 keeps validator rewards inside the existing CDL-047 treasury framework. It does not create
any new treasury primitive, detached fee-burn ledger, or validator-only issuance source.

## 5. Validator staking carry-forward summary

The validator staking and liveness lane opened in Phase 492 and was prelock-hardened in Phase 493.

CDL-055 remains open at window close because this window intentionally stopped at lane opening and
prelock hardening. The ratification boundary for validator stake amount, liveness penalties,
equivocation slash behavior, and re-admission remains deferred beyond Window 485-494.

## 6. Next-window controls

Phase 494 does not ratify CDL-055.
Phase 495+ requires a new sequence lock or amendment.

Carry-forward controls:
- preserve the CDL-053 reservation boundary;
- treat CDL-055 as the next validator constitutional lane if a later sequence lock authorizes it;
- keep validator trust-tier, epoch-boundary enforcement scoping, and co-location policy out of
  this handoff.
