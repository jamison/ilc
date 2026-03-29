# ILC CDL-055 Validator Staking and Liveness Enforcement Ratification Evidence 496 v0.1

Status: ratified evidence
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. Ratified lane identity

CDL-055 is ratified in Phase 496.

## 2. Evidence anchors

Ratification anchors:
- `docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_prelock_hardening_493_v0.1.md`
- `docs/specs/ilc_sim_010_validator_incentive_economics_synthesis_487_v0.1.md`
- `docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md`
- `docs/specs/ilc_cdl_046_timed_out_amendment_ratification_evidence_409_v0.1.md`

## 3. Rejected alternatives

Rejected at ratification:
- leave validator staking and liveness unopened indefinitely,
- renegotiate `recommended_genesis_stake_amount` or `recommended_liveness_miss_threshold`,
- overload the timed-out orphan policy directly into validator participation without a separate lane.

## 4. Constitutional boundary after ratification

CDL-053 remains reserved and unopened.
No ilc_core/ mutation occurs in Phase 496.
Validator participation stake, liveness penalties, equivocation slash boundary, and the separate
re-admission boundary now sit inside CDL-055 rather than inside CDL-046.

## 5. Governance tokens

Governance tokens locked by this ratification:
- `genesis_stake_amount` remains anchored to SIM-010,
- `liveness_miss_threshold` remains anchored to SIM-010,
- `equivocation_full_slash` remains in-scope,
- `re_admission_boundary` remains constitutionally separate from this ratification window.

## 6. Section-5 ratification readiness evidence checklist satisfaction

Section-5 readiness is satisfied because:
- Phase 493 prelock hardening fixed the validator-participation liveness boundary,
- SIM-010 passed and supplied the bounded staking and liveness inputs,
- CDL-054 ratified the reward-routing prerequisite before staking ratification,
- no new staking calibration is introduced at ratification time.
