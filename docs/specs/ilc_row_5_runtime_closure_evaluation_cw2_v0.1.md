# ILC Row-5 Runtime Closure Evaluation CW-2 v0.1

**Phase:** 758  
**Window:** Mysticeti convergence window  
**Date:** 2026-04-21  
**Author:** Codex

`row_5_runtime_closure_verdict=fail`
`row_5_status=spec_closed_runtime_pending`
`row_5_observability_floor_verdict=pass`
`row_5_fail_expected_pre_constitutional_no_privacy_layer`
`row_5_two_layer_defence_required_before_runtime_closure`

## 1. Evaluation target and inherited bar

`CW-1` passed, so row `5` may now be evaluated against the live runtime-closure
bar fixed by Phase `740`.

That inherited bar requires:

- ordinary-observer / hosted-query same-contributor linkage recall `<= 0.45`,
- operator-path same-contributor linkage recall `<= 0.60`,
- observability-floor preservation per Phase `679`.

This phase evaluates the committed `SIM-LEAKAGE-01` results artifact directly.
It does not restate those results from memory and it does not reopen the Phase
`740` methodology.

## 2. Raw committed results and threshold comparison

### 2.1 Variant A — Operator-path attacker

Quoted committed result from
`docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`:

- `Recall = 1.0`
- threshold: `<= 0.60`

Comparison:

- `1.0 > 0.60`
- verdict: `FAIL`

The committed artifact also states why this is direct rather than inferential:

- validator logs expose sender `AgentID` bytes in plaintext,
- no timing inference or statistical reconstruction is required.

### 2.2 Variant B — Hosted-query attacker

Quoted committed result:

- `Recall (observed) = 0.0`
- `Recall (structural) = 1.0`
- threshold: `<= 0.45`

Comparison:

- structural value controls because the hosted-query surface is present,
- `1.0 > 0.45`
- verdict: `FAIL`

The committed artifact states explicitly:

- `gRPC surface live = true`
- `Structural linkage bound: ... structural recall = 1.0`

### 2.3 Variant C — Repeated-contributor attacker

Quoted committed result:

- `structural recall = 1.0`
- threshold: `<= 0.45`

Comparison:

- `1.0 > 0.45`
- verdict: `FAIL`

The committed artifact ties this to epoch-boundary and balance-surface
correlation rather than to a missing-measurement gap.

### 2.4 Consolidated result table

| Variant | Raw committed recall | Closure threshold | Result |
|---|---:|---:|---|
| Operator-path | `1.0` | `<= 0.60` | fail |
| Hosted-query (structural) | `1.0` | `<= 0.45` | fail |
| Repeated-contributor (structural) | `1.0` | `<= 0.45` | fail |

Both inherited closure bands are exceeded by the committed runtime artifact.

## 3. Observability-floor verdict

The committed `SIM-LEAKAGE-01` results artifact records all four observability
requirements as present:

- receipts discoverable: `PASS`
- lineage legible: `PASS`
- challengeability preserved: `PASS`
- bounded human auditability preserved: `PASS`

This means row `5` does **not** fail because the measurement surface was
inadmissible. It fails because the measured linkage numbers are materially too
high while the public-legitimacy surface remains intact.

Observability-floor verdict:

- `row_5_observability_floor_verdict=pass`

## 4. Honest row-5 verdict

Overall row-5 runtime-closure verdict:

- `row_5_runtime_closure_verdict=fail`

Status after evaluation:

- `row_5_status=spec_closed_runtime_pending`

This fail is expected and must be stated plainly.

The committed artifact itself explains why:

- no privacy layer exists,
- validator logs expose sender identity directly,
- the hosted-query surface remains structurally linkable,
- epoch-lineage correlation remains structurally linkable.

This is therefore a pre-constitutional failure of the closure bar, not a test
artifact or a documentation defect.

## 5. Required carry-forward before row 5 can close

The committed evidence supports a specific two-layer carry-forward rather than
a generic privacy aspiration.

Required before row `5` can close:

1. log hygiene:
   AgentID redaction or equivalent removal of direct sender identity from the
   validator operational log surface,
2. transfer privacy:
   a real privacy layer for contribution flow, such as mixing or
   k-anonymity-style protection, sufficient to drive the linkage numbers below
   the inherited closure bands.

The fail verdict should not be softened into “partial closure.” The current
runtime does not satisfy the Phase `740` closure bar.

## 6. Non-claims

This phase does **not** claim:

- row `5` closure,
- convergence-window failure as a whole,
- any row-7 or row-8 result,
- any `CDL-017` action,
- any Option B implication.

The honest effect of `CW-2` is narrower:

- row `5` remains pending,
- the convergence window continues to `CW-3` and `CW-4`.
