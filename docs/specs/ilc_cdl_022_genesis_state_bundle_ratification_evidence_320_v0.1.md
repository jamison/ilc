# ILC CDL-022 Genesis State Bundle Ratification Evidence 320 v0.1

Status: Phase-320 ratification evidence artifact  
Date: 2026-02-27  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Record ratification evidence for `CDL-022` using the locked sequence:
- Phase 311 contract/evidence prelock,
- Phase 312 runtime/provider tranche.

Scope boundary:
- mutate only `CDL-022` ratification fields,
- do not mutate other decision-log rows,
- do not modify `ilc_core/` runtime behavior.

## 2. Evidence chain summary

Evidence chain:
1. `docs/specs/ilc_phase_318_327_sequence_lock_v0.1.md`
2. `docs/specs/ilc_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311_v0.1.md`
3. `docs/specs/ilc_genesis_state_bundle_runtime_handoff_312_v0.1.md`
4. `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 3. CDL-022 option inventory and selection statement

Option inventory:
- `genesis bundle only`,
- `genesis bundle + ceremony`,
- `ad hoc bootstrapping`.

Selection statement:
- selected option: `genesis bundle + ceremony`,
- rejected options: `genesis bundle only`, `ad hoc bootstrapping`,
- runtime dependency tokens confirmed from Phase 312:
  - `genesis_state_bundle_312.v0.1`,
  - `d2_schema_baseline_310.v0.1`.

## 4. Ratification record

| Field | Value |
| --- | --- |
| decision_id | `CDL-022` |
| status | `ratified` |
| ratified_phase | `320` |
| ratified_date | `2026-02-27` |
| evidence_document | `docs/specs/ilc_cdl_022_genesis_state_bundle_ratification_evidence_320_v0.1.md` |
| selected_option | `genesis bundle + ceremony` |
| dependency_token_runtime | `genesis_state_bundle_312.v0.1` |
| dependency_token_schema | `d2_schema_baseline_310.v0.1` |

## 5. Mutation protocol confirmation

Mutation protocol confirmation:
- only `status`, `ratified_phase`, `ratified_date`, and `evidence_document` changed for `CDL-022`,
- no other `CDL-*` row was mutated,
- no runtime files in `ilc_core/` were changed.

## 6. Non-goals

This phase does not:
- ratify `CDL-021`, `CDL-023`, or `CDL-024`,
- modify genesis runtime implementation behavior,
- introduce wire transport or rust/wasm scope.

## 7. Canonical anchors

- `docs/specs/ilc_phase_318_327_sequence_lock_v0.1.md`
- `docs/specs/ilc_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311_v0.1.md`
- `docs/specs/ilc_genesis_state_bundle_runtime_handoff_312_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_ratification_mutation_scope_guardrail_261_v0.1.md`
