# ILC CDL-041 Ratification Evidence v0.1

Status: ratification evidence artifact
Date: 2026-03-10
Decision lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact ratifies CDL-041 for shard lifecycle operations (creation, merge, split) using the Phase-384 prelock evidence and the Phase-392 sequence-lock constraints.

## 2. Ratified decision

Ratified option:
- merge-first lifecycle with highest_ecu_wins reconciliation

CDL-041 ratifies merge-first shard lifecycle with highest_ecu_wins reconciliation under SIM-004 partition evidence constraints.

## 3. Evidence basis

Canonical evidence anchors:
- `docs/specs/ilc_cdl_041_shard_lifecycle_prelock_384_v0.1.md`
- `docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md`
- `docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_ratification_evidence_393_v0.1.md`
- `docs/specs/ilc_sim_004_partition_resilience_commissioning_results_369_v0.1.md`

## 4. Section-3 authoritative evidence checklist satisfaction

Checklist satisfaction statements:
1. Phase-384 Section-3 SIM-004 reconciliation constraints are preserved,
2. Phase-384 Section-4 CDL-V3 and CDL-039 boundaries are preserved,
3. calibration dispositions from the Phase-384 parameter set are resolved in Section 5,
4. sequencing boundary for CDL-042 remains enforced by the Phase-392 lock,
5. no runtime implementation is ratified in this phase.

## 5. Calibration constants resolution

Ratification calibration dispositions:
- `merge_conflict_window_months`: constitutional bound `3 <= merge_conflict_window_months <= 12`.
- `split_divergence_guard_months`: concrete constant `split_divergence_guard_months = 6`.
- `shard_creation_diversity_floor`: formal amendment deferral; closure target is `docs/specs/ilc_cdl_v3_v7_governance_authorization_lock_396_v0.1.md` and downstream constitutional lock text.

## 6. Shard-lifecycle constitutional closure

Shard creation remains constrained by CDL-V3 diversity-floor requirements.

Shard lifecycle operations remain bound by CDL-039 cluster membership non-inferrability requirements.

## 7. Carry-forward constraints

CDL-042 opening remains sequenced after CDL-041 and CDL-043 ratification completion.

No standing compatibility profile dual-mode is introduced as a protocol feature.

## 8. Runtime deferral boundary

No runtime implementation of CDL-041 is ratified in Phase 394.

Runtime implementation remains deferred to a later authorized runtime window.

## 9. Canonical anchors

Constitutional anchors:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_041_shard_lifecycle_prelock_384_v0.1.md`
- `docs/specs/ilc_sim_004_partition_resilience_commissioning_results_369_v0.1.md`
