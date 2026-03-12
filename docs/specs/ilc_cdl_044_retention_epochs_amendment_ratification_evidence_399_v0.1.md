# ILC CDL-044 retention_epochs Amendment Ratification Evidence 399 v0.1

Status: Phase-399 ratification evidence artifact
Date: 2026-03-12
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact records ratification closure for CDL-044, the retention_epochs constitutional amendment lane opened in Phase 392.

Scope boundary:
- ratify only CDL-044,
- close the named CDL-039 forward obligation for deployment,
- preserve runtime deferral boundaries in this constitutional phase.

## 2. Ratified amendment decision

CDL-044 ratifies retention_epochs operational constant as 1 issuance_epoch (1 month) for CDL-039 deployment boundary enforcement.

Ratified candidate framing in decision-log row vocabulary remains:
- `open dedicated amendment row with fixed constant prelock`.

## 3. Evidence basis

Evidence basis for closure:
- Phase-392 opening prelock established the bounded-range opening and floor anchor,
- Phase-379 ratification evidence named the mandatory forward amendment obligation,
- SIM-003 and Phase-371 interpretation supply epoch context and deployability interpretation,
- Phase-395 storage-economics ratification keeps retention constant closure delegated to CDL-044.

## 4. CDL-039 forward-obligation closure statement

CDL-044 closes the CDL-039 forward obligation requiring a named subsequent CDL amendment before deployment.

Closure statement:
- the obligation named in Phase-379 is now constitutionally satisfied,
- CDL-039 deployment boundary no longer carries an unresolved retention_epochs amendment dependency,
- this closure does not authorize runtime mutation in Phase 399.

## 5. Calibration constants resolution

`retention_epochs` is resolved as a deployable constitutional constant:
- `retention_epochs = 1`
- `epoch_type = issuance_epoch`
- `epoch_duration = 1 month`
- `wall_clock_interpretation = 1 month retention window`

No bounded-range, deferred, or placeholder calibration language remains for this constant in CDL-044 closure.

## 6. Epoch-type interpretation closure

retention_epochs is issuance-epoch scoped and must not be interpreted on validation-epoch timescale.

Interpretation closure note:
- issuance-epoch interpretation aligns with SIM-003/371 graph-pruning context,
- validation-epoch interpretation is explicitly prohibited for CDL-044 deployment semantics.

## 7. Carry-forward constraints

Carry-forward constraints for immediate next phases:
- Phase-400 coherence and capsule v1.4 must carry forward a runtime-integrity note: CDL-V1/V2/V3/V7 validators reject non-finite numeric inputs (NaN/Inf).
- Phase-400 and Phase-401 must preserve the non-ratifying boundary for runtime implementation claims in constitutional synthesis/gate phases.
- CDL-042 opening remains out-of-scope in this phase and is handled by later window sequencing.

## 8. Runtime deferral boundary

No runtime implementation is ratified in Phase 399.

This phase ratifies constitutional parameter closure only; any runtime behavior changes require explicit runtime-phase authorization in a subsequent lane.

## 9. Canonical anchors

- `docs/specs/ilc_cdl_044_retention_epochs_amendment_open_prelock_392_v0.1.md`
- `docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md`
- `docs/specs/ilc_window_378_391_handoff_391_v0.1.md`
- `docs/specs/ilc_sim_001_002_003_commissioning_results_365_v0.1.md`
- `docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md`
- `docs/specs/ilc_cdl_043_storage_economics_ratification_evidence_395_v0.1.md`
- `docs/specs/ilc_cdl_v3_diversity_floor_runtime_handoff_397_v0.1.md`
- `docs/specs/ilc_cdl_v7_popperian_gate_runtime_handoff_398_v0.1.md`
