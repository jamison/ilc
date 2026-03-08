# ILC V-Series Implementation Authorization Lock 387 v0.1

Status: planning authorization lock (non-ratifying)  
Date: 2026-03-08  
Owner lane: G8 Constitution Cluster A

## 1. Scope and authority boundary

Phase 387 is non-sensitive and planning/authorization-only.

This artifact authorizes exact runtime targets and dependency-token values for Phases 388/389 and does not perform runtime implementation.

No decision-log mutation occurred. No ilc_core runtime files were changed.

## 2. Inputs and constitutional carry-forward

Canonical inputs:
- `docs/specs/ilc_phase_378_391_sequence_lock_v0.1.md`
- `docs/specs/ilc_sim_006_007_commissioning_results_386_v0.1.md`
- `docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md`
- `docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_prelock_383_v0.1.md`
- `docs/specs/ilc_cdl_041_shard_lifecycle_prelock_384_v0.1.md`
- `docs/specs/ilc_cdl_043_storage_economics_prelock_385_v0.1.md`

## 3. Single-source-of-truth declaration

This is the single source of truth for CDL-V1/V2 implementation authorization.

If Phase 378 and Phase 387 conflict on exact target paths or dependency token values, Phase 387 governs.

## 4. Authorized runtime target paths for phases 388/389

Authorized creation/mutation targets for Phase 388 (CDL-V1 temporal decay runtime):
- `ilc_core/reputation/__init__.py`
- `ilc_core/reputation/temporal_decay_runtime.py`

Authorized creation/mutation targets for Phase 389 (CDL-V2 sybil resistance runtime):
- `ilc_core/identity/__init__.py`
- `ilc_core/identity/sybil_resistance_runtime.py`

The two module roots above are authorized creation targets because these exact paths do not yet exist in the current repository layout.

## 5. Dependency token and version lock

CDL-V1 dependency token lock:
- `CDL_V1_DEPENDENCY = "cdl_v1_temporal_decay_388.v0.1"`

CDL-V2 dependency token lock:
- `CDL_V2_DEPENDENCY = "cdl_v2_sybil_resistance_389.v0.1"`

Phase-388/389 runtime modules must export these exact tokens.

## 6. Mutation scope restrictions for runtime phases

Mutation scope for Phases 388/389 forbids: ilc_core/consensus/, ilc_core/security/, ilc_core/ledger/, ilc_core/issuance/, ilc_core/schema/, ilc_core/genesis/, ilc_core/epoch/, ilc_core/network/, ilc_core/node/.

Additional runtime-phase constraints:
- Phases 388/389 must use custom runtime mutation-scope asserters.
- Phases 388/389 must not use `assert_head_commit_touched_no_runtime_files`.

## 7. CDL-V3/V7 deferral and SIM-006 evidence linkage

CDL-V3 and CDL-V7 remain requires_additional_governance_input. SIM-006 results (Phase 386) are available for governance review. CDL-V3/V7 governance resolution is deferred to Window 392+ where capsule v1.3 section on CDL-V3/V7 readiness provides the authoritative declaration.

## 8. Conflict resolution and forward boundary

Phase 387 governs exact path and token values for Phase-388/389 runtime implementation even when earlier planning artifacts use broader scope declarations.

Phases 388 and 389 remain sensitive and require prompt review/GO before execution.

## 9. Non-goals and immutable boundaries

- no decision-log mutation,
- no runtime implementation in this phase,
- no governance reopening for CDL-V3/CDL-V7,
- no modification of ratified CDL rows.
