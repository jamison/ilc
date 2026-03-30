# ILC CDL-058 re_admission_boundary Opening Stub 518 v0.1

Status: opening stub
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

## 1. Lane identity

cdl_058_governs_re_admission_boundary

CDL-058 opens in Phase 518 as the numbered re_admission boundary lane for validator return after
bounded exit or fault events.

## 2. Problem statement

The validator runtime now separates:
- liveness enforcement (`CDL-055`),
- trust-tier elevation (`CDL-056`),
- epoch-boundary witness provenance (`CDL-057`),
- and validator re-entry after exit or fault (`CDL-058`).

The open question narrowed in Phase 512 is the constitutional boundary for return after:
- `liveness_miss`,
- `equivocation`,
- `voluntary_exit`.

This lane does not absorb `CDL-046 timed_out` recovery semantics and does not alter validator
bootstrap or Genesis key custody artifacts.

## 3. Candidate options

Candidate options carried forward from Phase 512:
- cooldown period in epochs before validator re-entry,
- stake re-deposit requirement before re-admission,
- reputation floor before re-admission,
- sponsor attestation for validator return.

## 4. Selected option

selected_option: cooldown_period_per_exit_reason
re_admission_cooldown_epoch_type: issuance_epoch

The selected option is cooldown period per exit-reason type (`liveness_miss`, `equivocation`,
`voluntary_exit`), anchored to SIM-011 recommended constants:
- `recommended_cooldown_epochs_liveness_miss: 2`
- `recommended_cooldown_epochs_equivocation: 12`
- `recommended_cooldown_epochs_voluntary_exit: 1`

Cooldown epochs are issuance epochs (1 month each). The validator monitoring and penalty layer
continues to operate on validation epochs independently through `CDL-055`.

## 5. Evidence anchors

Required anchors:
- `docs/specs/ilc_cdl_058_re_admission_boundary_scoping_512_v0.1.md`
- `docs/specs/ilc_sim_011_re_admission_boundary_calibration_517_v0.1.md`
- `docs/specs/ilc_phase_515_524_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_ratification_evidence_496_v0.1.md`

## 6. Governance tokens

sim_011_calibrated_constants_required
cdl_046_timed_out_orthogonal
re_admission_cooldown_epoch_type: issuance_epoch

CDL-058 remains status: open in Phase 518.

## 7. Forward obligations

Phase 519 prelock hardening is required.
Phase 520 ratification is required.
Phase 521 runtime implementation is required.
