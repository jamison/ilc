# ILC CDL-V3/V7 Governance Authorization Lock v0.1

Status: authorization lock artifact
Date: 2026-03-10
Decision lane: G8 Constitution Cluster A

## 1. Scope and authority boundary

This is the single source of truth for CDL-V3/V7 runtime implementation authorization for phases 397/398.

Phase 396 is authorization-only and non-ratifying.

No decision-log mutation occurred. No ilc_core runtime files were changed.

## 2. Inputs and constitutional carry-forward

Authoritative inputs:
- `docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_392_413_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_sim_006_007_commissioning_results_386_v0.1.md`
- `docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_ratification_evidence_393_v0.1.md`
- `docs/specs/ilc_cdl_041_shard_lifecycle_ratification_evidence_394_v0.1.md`
- `docs/specs/ilc_cdl_043_storage_economics_ratification_evidence_395_v0.1.md`
- `docs/specs/ilc_cdl_044_retention_epochs_amendment_open_prelock_392_v0.1.md`

Carry-forward constitutional state confirms:
- CDL-039, CDL-040, CDL-041, CDL-043 are ratified,
- CDL-044 remains open,
- CDL-042 is not opened in this phase.

## 3. Branch resolution and governance stance

SIM-006 favorable branch is locked: recommended_panel_assignment_policy: diversity_weighted.

No unfavorable SIM-006 fallback branch is authorized in this artifact.

SIM-006 capability-vector tiers are directionally valid but were commissioned with placeholder vocabulary; this limitation is acknowledged and bounded to governance authorization framing in Phase 396.

Phases 397/398 implement ratified CDL-V3/V7 constitutional text; SIM-006 placeholder capability-vector tiers are not runtime specification inputs.

## 4. Authorized runtime target paths for phases 397/398

Authorized runtime targets:
- Phase 397 (CDL-V3):
  - `ilc_core/consensus/__init__.py`
  - `ilc_core/consensus/diversity_floor_runtime.py`
- Phase 398 (CDL-V7):
  - `ilc_core/consensus/popperian_gate_runtime.py`

`ilc_core/consensus/` does not exist in Phase 396 and is explicitly authorized as a creation target package for phases 397/398.

## 5. Dependency token and version lock

Dependency lock constants:
- `CDL_V3_DEPENDENCY = "cdl_v3_diversity_floor_397.v0.1"`
- `CDL_V7_DEPENDENCY = "cdl_v7_popperian_gate_398.v0.1"`

These values are fixed authorization outputs for implementation in phases 397/398.

## 6. Mutation scope restrictions for runtime phases

Phase 396 mutation restrictions:
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no mutation under `ilc_core/`,
- no CDL ratification,
- no opening of CDL-042,
- no ratification of CDL-044,
- no runtime implementation work.

## 7. Placeholder-vocabulary limitation and guardrails

The SIM-006 vocabulary limitation is a governance-input quality note only.

Runtime authorization in phases 397/398 must be interpreted exclusively through ratified CDL-V3 and CDL-V7 constitutional clauses plus this authorization lock's path and dependency constraints.

No placeholder capability tier labels from SIM-006 are authorized as executable runtime policy terms.

## 8. Conflict resolution and forward boundary

If downstream planning artifacts conflict with this document on Phase-397/398 runtime targets or dependency values, this artifact governs.

Phase 397 and Phase 398 are authorized runtime implementation phases. Phase 396 does not execute runtime work.

## 9. Non-goals and immutable boundaries

Non-goals in Phase 396:
- no decision-log edits,
- no runtime edits,
- no constitutional ratification action,
- no CDI/CDL expansion outside the locked window sequence.
