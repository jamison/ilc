# ILC Node-Value + Governance Conformance Telemetry Contract v0.1

Status: Draft
Date: 2026-02-18
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Define a single typed telemetry/report surface for node-value and governance conformance checks so operators can consume one coherent status artifact instead of stitching multiple invariant outputs manually.

## 2. Scope

This contract is compositional only:
- it aggregates outputs from existing evaluators,
- it does not redefine or mutate underlying economic/governance formulas.

## 3. Report Root Contract

Type: `NodeValueGovernanceConformanceReport`

Required fields:
- `contract_version: "v0.1"`
- `score_row_count: int`
- `score_rows_sha256: str`
- `checks: NodeValueGovernanceConformanceChecks`
- `overall_ok: bool`

## 4. Check Contract

Each check field uses:

`ConformanceInvariantCheck`:
- `ok: bool`
- `skipped: bool`
- `errors: list[str]`
- `detail: dict[str, object]`

Required check keys:
- `score_vector_schema`
- `anti_sybil`
- `reuse_diversity_policy`
- `freshness_policy`
- `refutation_profitability`
- `genesis_accrual_governor`

## 5. Delegation Rules

The consolidated report must delegate to existing evaluators:
- anti-Sybil flags from phase-206 surfaces,
- refutation profitability from phase-212 evaluator,
- reuse-diversity policy validation from phase-216 policy validator,
- freshness policy validation from phase-217 policy validator,
- Genesis accrual governor evaluation from phase-218 evaluator.

No manual recomputation or alternate logic is allowed in this contract.

## 6. Score Vector Schema Lock

`score_vector_schema` check enforces exact key set for each score row:
- `node_id`
- `reuse_component`
- `contradiction_component`
- `validation_component`
- `path_component`
- `reuse_diversity_multiplier`
- `epistemic_weight`
- `freshness_gate`
- `utility_flow`

Any key drift is a schema mismatch and must be reported.

## 7. Optional-Surface Semantics

Two check surfaces are optional-input aware:
- `refutation_profitability` may be skipped when reward allocations are absent,
- `genesis_accrual_governor` may be skipped when Genesis signal input is absent.

Skip reasons must be emitted in `detail.reason`.

## 8. Stability Guarantees

Genesis-facing consumers may rely on:
- root field names and check-key names in this contract,
- semantics of `ok`, `skipped`, and `errors`,
- score-vector required key set listed above.

Any future schema expansion must be additive or versioned.
