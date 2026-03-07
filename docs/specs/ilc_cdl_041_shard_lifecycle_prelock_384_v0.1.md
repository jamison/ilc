# ILC CDL-041 Shard Lifecycle Prelock 384 v0.1

Status: prelock evidence (open, non-ratifying)  
Date: 2026-03-07  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact opens CDL-041 and records prelock evidence for shard lifecycle operations (creation, merge, split) with constitutional and documentation boundaries only.

## 2. CDL-041 opening state

- decision id: `CDL-041`
- status: open
- phase: 384
- ratification: deferred

No runtime implementation occurs in Phase 384.

## 3. SIM-004 reconciliation and partition-window anchor

Shard merge semantics are constrained by SIM-004's highest_ecu_wins reconciliation rule for issuance-epoch partition divergence; shard splits must not create irreconcilable divergence paths in the T=34-month partition threshold window established by SIM-004.

## 4. Shard lifecycle diversity and privacy constraints

Shard creation requires satisfaction of CDL-V3 cluster diversity floor; V-series enforcement runtime authorization determines when this requirement is computationally enforced.

Shard lifecycle operations (creation, merge, split) must not allow passive observers to infer cluster membership in violation of CDL-039's cluster membership non-inferrability invariant.

## 5. Calibration constants and exclusivity boundary

Prelock calibration parameters for CDL-041 are tracked in this section only:
- `merge_conflict_window_months` - candidate window under review
- `split_divergence_guard_months` - candidate guard horizon under review
- `shard_creation_diversity_floor` - candidate floor alignment under review

## 6. CDL-042 forward pointer and deferral boundary

CDL-042 (agent identity namespace) addresses per-agent identity within shard contexts; CDL-042 is deferred to Window 392+ pending CDL-039/040 scope resolution.

## 7. Deferral and phase-boundary constraints

- Phase 384 is opening/prelock only.
- No CDL-041 ratification action occurs in this phase.
- No CDL-042 opening action occurs in this phase.
- Any runtime implementation is deferred to a later authorized runtime window.

## 8. Canonical anchors

- `docs/specs/ilc_sim_004_partition_resilience_commissioning_results_369_v0.1.md`
- `docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md`
- `docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_prelock_383_v0.1.md`
- `docs/specs/ilc_phase_378_391_sequence_lock_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
