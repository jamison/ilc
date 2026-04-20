# ILC SIM-LEAKAGE-01 Commissioning Spec 740 v0.1

Status: commissioning spec
Date: 2026-04-20
Phase: 740
Owner lane: G8 MVP-gate runtime-form lane
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`sim_leakage_01_commissioned_phase_740`
`sim_leakage_01_is_dedicated_measurement_not_m019_default_verdict`
`sim_leakage_01_attacker_variants_operator_hosted_query_repeated_contributor`
`sim_leakage_01_commissioning_only_not_execution`

## 1. Commission purpose and non-conflation

`SIM-LEAKAGE-01` is the dedicated traffic-capture and leakage-measurement pass
for row `5`.

Its purpose is:

- measure runtime contributor-linkage leakage over a live multi-machine
  validator testbed,
- publish artifact-backed findings for the three inherited Phase `681`
  attacker variants,
- determine whether row `5` can move from `spec_closed_runtime_pending` to
  `runtime_closed`.

This SIM is distinct from Gemini `M-019`.

Gemini `M-019` is a fault-simulation and adversarial-hardening workload.
`SIM-LEAKAGE-01` may reuse the same multi-machine environment, deployment, or
capture substrate, but the default `M-019` pass/fail verdict is not the row-5
artifact. A successful `M-019` run alone is insufficient to satisfy row `5`.

`sim_leakage_01_not_satisfied_by_m019_pass_fail_alone`

## 2. Attacker variants and required evidence channels

The commissioned run must cover all three attacker variants fixed in Phase
`681`.

### 2.1 Operator-path attacker

Required evidence channels:

- validator-host traffic timing,
- validator-host message-size buckets,
- per-host ordering around epoch-boundary settlement events,
- contributor-script schedule needed to estimate same-contributor linkage.

Required output:

- measured same-contributor linkage estimate from validator-host vantage,
- explanation of whether the result stays within or exceeds the `0.60`
  operator-path closure band.

### 2.2 Hosted-query attacker

Required evidence channels:

- query timing traces,
- repeated identifier or handle access patterns,
- aggregation view across epochs,
- or an explicit hosted-query surface-absence record when the selected testbed
  exposes no hosted-query surface,
- linkage estimate using hosted-query metadata alone and with receipt-lineage
  context.

Required output:

- measured same-contributor linkage estimate for the hosted-query attacker, or
  an explicit absent-at-runtime disposition with supporting surface audit,
- explanation of whether the result stays within or exceeds the `0.45`
  ordinary-observer closure band.

### 2.3 Repeated-contributor attacker

Required evidence channels:

- public receipt and lineage corpus for repeated scripted contributors,
- epoch-by-epoch submission sequence,
- optional combined view with hosted-query traces if both are present.

Required output:

- measured same-contributor linkage estimate from the ordinary public
  legitimacy surface,
- explanation of whether the result stays within or exceeds the `0.45`
  materially-harder band.

## 3. Testbed and instrumentation requirements

The commissioned run requires:

1. a live multi-machine validator testbed,
2. at least one repeated-contributor script spanning multiple epochs,
3. timestamped traffic capture or equivalent event logs from validator-host
   vantage points,
4. query-trace capture for any hosted-query surface under test, or an explicit
   surface-absence record if no hosted-query surface exists on the selected
   runtime,
5. retained public receipt and lineage artifacts for the same workload window,
6. a manifest tying captures, query traces, and public receipts to the same run.

The candidate substrate for this run may be the Gemini multi-machine
environment being prepared around `M-019`, but the leakage run must still emit
its own artifacts and verdict table. Reusing the environment is acceptable.
Reusing only the `M-019` pass/fail summary is not.

## 4. Measurement protocol

The commissioned protocol is:

1. run repeated scripted contributors over multiple epochs,
2. capture validator-host timing and message-size-bucket data,
3. capture hosted-query traces if a hosted-query surface is part of the run,
4. collect the corresponding public receipts and lineage traces,
5. compute same-contributor linkage estimates for:
   - ordinary public-receipt / lineage observer,
   - hosted-query observer,
   - operator-path observer,
6. publish an artifact bundle with:
   - capture manifest,
   - analysis note,
   - linkage estimates,
   - observability-floor check,
   - explicit verdict.

The run must also publish a short boundary note stating:

- receipts remained discoverable,
- lineage remained legible,
- challengeability was preserved,
- bounded human auditability was preserved.

If any of those statements cannot be made honestly, the run fails regardless of
its linkage numbers.

## 5. Verdict criteria

`sim_leakage_01_verdict=pass` requires all of the following:

1. all three attacker variants were exercised,
2. required artifacts for traffic capture, query traces where applicable,
   receipts, and lineage were published,
3. ordinary-observer same-contributor linkage estimate is at or below `0.45`,
4. hosted-query same-contributor linkage estimate is at or below `0.45` when a
   hosted-query surface exists, or a hosted-query surface-absence record is
   published when it does not,
5. operator-path same-contributor linkage estimate is published and is not
   worse than the inherited `0.60` stretch target from Phase `681`,
6. no observability-floor violation occurred,
7. the analysis does not rely on blanket secrecy, hidden receipts, broken
   lineage, or one privileged verification portal.

`sim_leakage_01_verdict=fail` if any of the following occurs:

- one or more attacker variants are unmeasured,
- one or more required artifacts are missing,
- ordinary-observer linkage exceeds `0.45`,
- hosted-query linkage exceeds `0.45` where a hosted-query surface exists, or
  the hosted-query surface-absence record is missing where it does not,
- operator-path linkage exceeds the inherited `0.60` stretch target,
- the observability floor is violated,
- the report attempts to substitute an `M-019` default verdict for the
  dedicated leakage-measurement artifact.

`sim_leakage_01_verdict=incomplete` if the run was started but the artifact
bundle is insufficient to support a pass/fail judgment.

## 6. Commissioning posture and non-goals

This document commissions a future measurement run. It does not claim that the
run has already occurred.

`sim_leakage_01_execution_not_yet_performed`

Non-goals of this commissioning spec:

- closing row `5` by documentation alone,
- treating `M-019` fault-simulation pass/fail output as row-5 evidence,
- demanding blanket secrecy or passive-global-adversary proof,
- reopening the Phase `682` narrowing,
- mutating `ilc_core/` or `ilc_consensus/`.

Row `5` remains `spec_closed_runtime_pending` until a future execution of
`SIM-LEAKAGE-01` satisfies the commissioned artifact and verdict contract.
