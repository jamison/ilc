# ILC CDL-046 timed_out Amendment Open Prelock v0.1

Status: Phase-405 constitutional opening prelock
Date: 2026-03-13
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact opens the constitutional amendment lane for `CDL-035` `timed_out` semantics under the amendment convention locked in Phase 402.

The opening is additive, non-ratifying, and restricted to constitutional prelock evidence.

## 2. CDL-046 opening state

status: open

CDL-046 opens as the CDL-035 timed_out amendment lane for churn and orphan recovery semantics.

This amendment uses a dedicated new sequential CDL identifier referencing CDL-035 and does not mutate the base CDL-035 ratified row.

## 3. CDL-035 amendment boundary and constitutional anchors

The base CDL-035 row remains the ratified lifecycle envelope for validation-state handling.

The amendment surface is limited to explicit `timed_out` transition semantics and recovery-policy handling for orphaned claims under churn conditions.

`timed_out` transition semantics remain bounded by CDL-035's attached lifecycle envelope with bounded operational relevance.

## 4. SIM-007 calibration anchor and issuance-epoch interpretation

SIM-007 calibrated the amendment basis at issuance_epoch scale: recommended_orphan_timeout_epochs: 4; recommended_recovery_policy: stake_full_release.

SIM-007 epoch context is issuance_epoch; orphan_timeout_epochs = 4 means a 4-month timeout horizon under the canonical 1-month issuance epoch.

## 5. Candidate discrimination and proposed fixed-constant prelock

The proposed candidate is open dedicated amendment row with fixed timeout and recovery constants prelock.

The prelock candidate binds orphan_timeout_epochs = 4 and recovery_policy = stake_full_release as the proposed fixed constants for later ratification.

Bounded timeout-and-recovery prelock is rejected because SIM-007 already provides direct fixed-constant recommendations at issuance_epoch scale.

Retaining CDL-035 without timed_out amendment is rejected because agent-churn and orphan accumulation evidence now requires explicit timed_out semantics and recovery policy to avoid undefined orphan-state handling.

## 6. Proposed amendment surface: timed_out transition and recovery policy

Claims remaining orphaned after orphan_timeout_epochs = 4 issuance epochs transition to timed_out and apply recovery_policy = stake_full_release.

timed_out transition semantics remain bounded by CDL-035's attached lifecycle envelope with bounded operational relevance.

The amendment surface attaches explicit orphan-timeout and recovery semantics without reopening unrelated CDL-035 lifecycle states.

## 7. Sequencing and ratification readiness plan

Phase 409 is the targeted ratification lane for CDL-046; this opening artifact constitutes the primary prelock evidence.

The opening remains constitutional only and prepares the amendment for later ratification evidence assembly.

## 8. Out-of-scope and deferred tracks

No runtime implementation occurs in Phase 405.

No mutation to the base CDL-035 ratified row occurs in this phase.

## 9. Canonical anchors

- `docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md`
- `docs/specs/ilc_sim_006_007_commissioning_results_386_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
