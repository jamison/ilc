# ILC CDL-046 timed_out Amendment Ratification Evidence 409 v0.1

Status: Phase-409 ratification evidence artifact
Date: 2026-03-14
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact records ratification closure for CDL-046, the CDL-035 timed_out amendment lane opened in Phase 405 for churn and orphan recovery semantics.

Scope boundary:
- ratify only CDL-046,
- lock the fixed timeout and recovery constants,
- preserve the CDL-035 base row unchanged,
- keep runtime implementation out of scope in this constitutional phase.

## 2. Ratified decision

CDL-046 is ratified as the CDL-035 timed_out amendment for churn and orphan recovery semantics.

The ratified candidate is the dedicated amendment row with fixed timeout and recovery constants, attached to the existing CDL-035 lifecycle envelope without reopening unrelated lifecycle states.

## 3. Evidence basis

Evidence basis for ratification:
- Phase 405 opened CDL-046 as a dedicated amendment row rather than mutating the CDL-035 base row,
- the Phase-405 prelock artifact locked the fixed constants and the explicit timed_out transition rule,
- SIM-007 provided direct issuance-epoch recommendations for orphan timeout and recovery policy,
- the Phase 402 sequence lock reserved this amendment lane and its dedicated identifier convention ahead of ratification.

## 4. Section-7 ratification readiness evidence checklist satisfaction

1. Open dedicated amendment row with fixed timeout and recovery constants prelock is confirmed as the ratified option.
2. orphan_timeout_epochs = 4 (issuance epochs) and recovery_policy = stake_full_release are locked as ratified constants.
3. timed_out transition remains bounded by the CDL-035 lifecycle envelope with bounded operational relevance.
4. SIM-007 calibration evidence is accepted for fixed-constant derivation at issuance_epoch scale.
5. Both rejected candidates (retain CDL-035 without amendment and bounded-range prelock) remain constitutionally excluded.

## 5. Ratified amendment constants: orphan timeout and recovery policy

SIM-007 calibrated the amendment basis at issuance_epoch scale: recommended_orphan_timeout_epochs: 4; recommended_recovery_policy: stake_full_release.

SIM-007 epoch context is issuance_epoch; orphan_timeout_epochs = 4 means a 4-month timeout horizon under the canonical 1-month issuance epoch.

Claims remaining orphaned after orphan_timeout_epochs = 4 issuance epochs transition to timed_out and apply recovery_policy = stake_full_release.

## 6. CDL-035 amendment boundary and timed_out transition scope

timed_out transition semantics remain bounded by CDL-035's attached lifecycle envelope with bounded operational relevance.

The ratified amendment attaches explicit orphan-timeout and recovery semantics without reopening unrelated CDL-035 lifecycle states, verdict attachment rules, or quarantine semantics.

Bounded timeout-and-recovery prelock is rejected because SIM-007 already provides direct fixed-constant recommendations at issuance_epoch scale.

Retaining CDL-035 without timed_out amendment is rejected because agent-churn and orphan accumulation evidence now requires explicit timed_out semantics and recovery policy to avoid undefined orphan-state handling.

## 7. D2e Agent SDK implementation carry-forward

The constitutional ratification in Phase 409 authorizes later D2e Agent SDK implementation to consume the locked constants and transition semantics without reopening the amendment lane.

Runtime implementation of the timed_out transition remains deferred to D2e Agent SDK implementation work and is not authorized in Phase 409 itself.

## 8. Out-of-scope and deferred tracks

Out of scope in Phase 409:
- no mutation to the CDL-035 base row,
- no further amendment-row numbering changes,
- no D2e Agent SDK runtime implementation,
- no ilc_core runtime mutation,
- no additional CDL lane openings or ratifications.

## 9. Canonical anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_cdl_046_timed_out_amendment_open_prelock_405_v0.1.md`
- `docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md`
- `docs/specs/ilc_sim_006_007_commissioning_results_386_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md`
