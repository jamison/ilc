# ILC CDL-V1 Temporal Decay Runtime Handoff 388 v0.1

Status: runtime tranche handoff  
Date: 2026-03-09  
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 388 implements CDL-V1 temporal-decay helpers in the Phase-387 authorized V1 target path only.

## 2. Dependency/version lock section

- `CDL_V1_RUNTIME_VERSION = "cdl_v1_temporal_decay_runtime_388.v0.1"`
- `CDL_V1_DEPENDENCY = "cdl_v1_temporal_decay_388.v0.1"`

## 3. Issuance-epoch temporal-decay model statement

CDL-V1 temporal decay enforcement is issuance-epoch scoped.

The runtime computes a deterministic exponential multiplier from elapsed issuance epochs, clamps the multiplier to `[floor_multiplier, 1.0]`, and applies it to base ECU score.

## 4. Deterministic failure-token catalog

Validation errors use deterministic tokens:
- `cdl_v1_temporal_decay_invalid_numeric`
- `cdl_v1_temporal_decay_negative_elapsed`
- `cdl_v1_temporal_decay_half_life_non_positive`
- `cdl_v1_temporal_decay_floor_out_of_range`
- `cdl_v1_temporal_decay_negative_base_score`
- `cdl_v1_temporal_decay_epoch_context_invalid`

## 5. Mutation-scope boundary statement

Phase 388 uses Phase-387 authorization targets as binding scope.

Touched runtime targets:
- `ilc_core/reputation/__init__.py`
- `ilc_core/reputation/temporal_decay_runtime.py`

Forbidden prefixes from Phase-387 remain unchanged.

## 6. Carry-forward constraints for Phase 389

- Phase 389 must import and lock `CDL_V1_DEPENDENCY` for chain continuity.
- Phase 389 must use custom runtime mutation-scope assertions and preserve forbidden-prefix boundaries.
- Phase 389 must not mutate decision-log state.

## 7. Non-goals

- no decision-log edits,
- no constitutional ratification action,
- no network or consensus module mutation,
- no governance-procedural V-series implementation in this phase.

No decision-log mutation occurred in Phase 388.
