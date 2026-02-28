# ILC CDL-V Ratification Sequencing 326 v0.1

Status: Phase-326 sequencing artifact  
Date: 2026-02-28  
Owner lane: G8 Constitution Cluster A

## 1. Scope

This artifact formalizes the ratification-ordering and boundary-coupling rules for `CDL-V1` through `CDL-V7`.

The purpose is to prevent future ratification prompts from treating the V-series as seven unrelated policy lanes.

## 2. Ordering constraints

Exact sequencing rules:
- `CDL-V2 -> CDL-V3 -> CDL-V4`
- `CDL-V5 -> CDL-V7`
- `CDL-V1 has no V-series ordering constraint`

Interpretation:
- `CDL-V2` must be ratified before `CDL-V3` because quorum diversity depends on identity validity and anti-sybil semantics,
- `CDL-V3` must be ratified before `CDL-V4` because reopening and re-ratification quorum composition must already be constitutionally defined,
- `CDL-V5` must be ratified before `CDL-V7` because cross-agent reproducibility across decomposition workloads requires explicit schema-epoch and translation semantics,
- `CDL-V1` is relatively independent of the identity, quorum, reopening, and decomposition ordering chain.

## 3. Boundary-coupling rules

Exact coupling rule:
- `CDL-V4 <-> CDL-V6`

Boundary semantics:
- `CDL-V4` ratification must define when ordinary reopening escalates into `CDL-V6`, if at all,
- `CDL-V6` ratification must define whether Genesis intervention is exhausted-governance-only or a parallel path,
- if `CDL-V6` remains a parallel path, the ratification must state how circumvention of `CDL-V4` is prevented,
- ratifying one of `CDL-V4` or `CDL-V6` without the other for an extended period creates a governance-gap risk and requires explicit justification.

## 4. Explicit non-dependencies

Explicit non-dependency statement:
- `CDL-V1 has no V-series ordering constraint`

Clarification:
- `CDL-V1` may still interact economically with other V-series mechanisms,
- but there is no required ratification precedence among `CDL-V1` and the other CDL-V entries.

## 5. Carry-forward ratification requirements

Future ratification prompts must carry forward the following requirements:
- `CDL-V5` ratification must include explicit `non-comparable by design` handling for cross-epoch cases,
- `CDL-V7` ratification must include tested graph-entry and reuse-value tie-back requirements,
- `CDL-V7` reproducibility must use a concrete evaluation protocol with explicit tolerance bounds for acceptable disagreement,
- future CDL-V ratification prompts must treat Section 3 of the corresponding evidence-prelock artifact as authoritative when more specific than the CDL-row `required_artifacts` shorthand.

## 6. Non-goals

This artifact does not:
- ratify any CDL-V entry,
- set numerical quorum thresholds,
- define the final Genesis intervention trigger matrix,
- replace the evidence-prelock artifacts themselves.
