# ILC CDL-043 Ratification Evidence v0.1

Status: ratification evidence artifact
Date: 2026-03-10
Decision lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact ratifies CDL-043 for storage economics, graph pruning policy, and active-graph retention constraints using the Phase-385 prelock and Phase-392 sequence-lock constraints.

## 2. Ratified decision

Ratified option:
- adaptive pruning with bounded retention windows

CDL-043 ratifies adaptive pruning with bounded retention windows under SIM-003 calibration evidence constraints.

## 3. Evidence basis

Canonical evidence anchors:
- `docs/specs/ilc_cdl_043_storage_economics_prelock_385_v0.1.md`
- `docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_041_shard_lifecycle_ratification_evidence_394_v0.1.md`
- `docs/specs/ilc_cdl_044_retention_epochs_amendment_open_prelock_392_v0.1.md`
- `docs/specs/ilc_sim_001_002_003_commissioning_results_365_v0.1.md`
- `docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md`

## 4. Section-3 authoritative evidence checklist satisfaction

Checklist satisfaction statements:
1. SIM-003 calibration anchors are preserved as the ratification basis,
2. non-centralization constraints remain explicitly bound to CDL-V2 and CDL-V3,
3. retention_epochs remains bounded by the open CDL-044 amendment lane and is not finalized here,
4. CDL-042 opening sequencing remains deferred until the Phase-392 ratification sequence completes,
5. runtime implementation remains deferred.

## 5. Calibration constants resolution

Ratification calibration dispositions:
- `ecu_score_floor`: constitutional floor `ecu_score_floor >= 0.5`.
- `retention_epochs`: formal amendment deferral; closure target is `docs/specs/ilc_cdl_044_retention_epochs_ratification_evidence_399_v0.1.md`.
- `snapshot_interval`: concrete constant `snapshot_interval = 50`.

## 6. Non-centralization constitutional closure

Storage economics must not create resource-concentration incentives incompatible with CDL-V3 diversity-floor and CDL-V2 sybil-resistance constraints.

## 7. Carry-forward constraints

retention_epochs remains governed by the CDL-044 amendment lane and is not constitutionally finalized by CDL-043 ratification in Phase 395.

CDL-042 opening remains sequenced after CDL-043 ratification completion.

No standing compatibility profile dual-mode is introduced as a protocol feature.

## 8. Runtime deferral boundary

No runtime implementation of CDL-043 is ratified in Phase 395.

Runtime implementation remains deferred to a later authorized runtime window.

## 9. Canonical anchors

Constitutional anchors:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_043_storage_economics_prelock_385_v0.1.md`
- `docs/specs/ilc_cdl_044_retention_epochs_amendment_open_prelock_392_v0.1.md`
