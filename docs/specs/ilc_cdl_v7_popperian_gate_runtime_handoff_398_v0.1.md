# ILC CDL-V7 Popperian Gate Runtime Handoff 398 v0.1

Status: runtime handoff artifact
Date: 2026-03-11
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 398 implements the CDL-V7 Popperian-gate runtime surface under Phase-396 authorization boundaries.

Implemented runtime targets:
- `ilc_core/consensus/popperian_gate_runtime.py`
- `ilc_core/consensus/__init__.py` (export-surface update)

## 2. Dependency/version lock section

Dependency and version locks:
- `CDL_V7_RUNTIME_VERSION = "cdl_v7_popperian_gate_runtime_398.v0.1"`
- `CDL_V7_DEPENDENCY = "cdl_v7_popperian_gate_398.v0.1"`
- import-time dependency continuity to `CDL_V3_DEPENDENCY`

## 3. Popperian-gate computational model statement

CDL-V7 Popperian-gate enforcement is computational and deterministic.

Model components:
- claim-form admissibility check for ratified basic-statement forms,
- falsifiability-required predicate,
- inadmissible-counterexample rejection,
- cross-agent reproducibility threshold check,
- top-level decomposition admissibility verdict helper.

Phase 398 implements ratified CDL-V7 constitutional text and does not treat SIM-006 placeholder capability tiers as runtime policy terms.

## 4. Deterministic failure-token catalog

Runtime tokenized validation failures:
- `cdl_v7_popperian_invalid_string`
- `cdl_v7_popperian_empty_string`
- `cdl_v7_popperian_invalid_bool`
- `cdl_v7_popperian_invalid_numeric`
- `cdl_v7_popperian_out_of_range`

## 5. Mutation-scope boundary statement

Phase 398 uses Phase-396 authorization targets as binding scope.

Boundary confirmations:
- no decision-log mutation,
- no mutation outside authorized Phase-398 runtime targets,
- no mutation to `ilc_core/consensus/diversity_floor_runtime.py`.

No decision-log mutation occurred in Phase 398.

## 6. Carry-forward constraints for Phase 399

Phase 399 remains constitutional and must not mutate CDL-V3/V7 runtime dependency tokens.

CDL-044 retention-epochs amendment closure in Phase 399 must consume existing runtime evidence as non-ratifying computational context only.

## 7. Non-goals

Non-goals in Phase 398:
- no CDL ratification action,
- no decision-log edits,
- no reinterpretation of CDL-V3 runtime behavior,
- no governance reinterpretation of SIM-006 placeholder capability tiers.
