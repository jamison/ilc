# ILC CDL-V2 Sybil Resistance Runtime Handoff 389 v0.1

Status: runtime tranche handoff  
Date: 2026-03-09  
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 389 implements CDL-V2 sybil-resistance helpers in the Phase-387 authorized V2 target path only.

## 2. Dependency/version lock section

- `CDL_V2_RUNTIME_VERSION = "cdl_v2_sybil_resistance_runtime_389.v0.1"`
- `CDL_V2_DEPENDENCY = "cdl_v2_sybil_resistance_389.v0.1"`
- `CDL_V1_DEPENDENCY` is imported and locked for runtime-chain continuity.

## 3. Heuristic calibration and deterministic-boundary statement

CDL-V2 sybil-resistance enforcement is computational and deterministic.

Runtime heuristics cover:
- identity-cluster overlap risk,
- burst-write anomaly penalty,
- diversity-floor contribution,
- bounded risk-to-penalty mapping.

## 4. Deterministic failure-token catalog

Validation errors use deterministic tokens:
- `cdl_v2_sybil_invalid_numeric`
- `cdl_v2_sybil_out_of_range`
- `cdl_v2_sybil_rate_non_positive`
- `cdl_v2_sybil_burst_sensitivity_out_of_range`
- `cdl_v2_sybil_diversity_floor_invalid`

## 5. Mutation-scope boundary statement

Phase 389 uses Phase-387 authorization targets as binding scope.

Touched runtime targets:
- `ilc_core/identity/__init__.py`
- `ilc_core/identity/sybil_resistance_runtime.py`

Forbidden prefixes from Phase-387 remain unchanged.

## 6. Carry-forward constraints for Phase 390

- Phase 390 coherence must record V1/V2 runtime implementation completion and token-lock continuity.
- Phase 390 must preserve the decision-log non-mutation boundary for runtime-phase summaries.
- Closure-gate Phase 391 should verify V1/V2 dependency exports are importable.

## 7. Non-goals

- no decision-log edits,
- no constitutional ratification action,
- no mutation outside authorized V2 runtime targets,
- no governance-procedural V-series implementation in this phase.

No decision-log mutation occurred in Phase 389.
