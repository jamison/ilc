# ILC Row-7 Censorship Runtime Closure Evaluation CW-3 v0.1

**Phase:** 759  
**Window:** Mysticeti convergence window  
**Date:** 2026-04-21  
**Author:** Codex

`row_7_censorship_resistance_runtime_closure_verdict=pass`
`row_7_censorship_side_closed_only`
`row_7_exitability_obligation_still_pending_until_cw4`
`epochcheckpointmsg_carries_row_7_censorship_evidence_weight_post_crit_001`
`row_7_phase_698_mapping_reverified`

## 1. Evaluation target and inherited contract

`CW-1` re-verified the committed row-7 runtime bundle, so the censorship side
of row `7` may now be evaluated against the Phase `741` Section `3.2` contract.

This phase evaluates only the censorship-resistance obligation.
Row `7` contains two runtime obligations:

1. censorship resistance,
2. strong exitability.

`CW-3` can close only the first of those two obligations.

## 2. Requirement-by-requirement check against Phase 741 Section 3.2

### 2.1 Requirement 1 — live censoring-validator scenario

Committed bundle evidence:

- `Validators: [V1, V2, V3, V4]`
- `Byzantine/Censoring Actor: V4`
- `Configuration Params: CENSOR_VALIDATOR=4, CENSOR_TARGET=1`

Verdict:

- satisfied

This is a live censoring-validator scenario, not a prose-only scenario sketch.

### 2.2 Requirement 2 — not weaker than the Phase 698 proof basis

Committed mapping note:

- `N=4`
- `F=1`
- `MaxRound=5`
- `Liveness property (Row7_Liveness)`

Phase `698` formal evidence confirms the same checked basis:

- `N=4`
- `F=1`
- `MaxRound=5`
- temporal property: `Liveness`

Verdict:

- satisfied

### 2.3 Requirement 3 — practical inclusion not suppressed permanently

Committed bundle evidence:

- `V1 logs: [m019_censoring] epoch_record_committed:epoch=1`
- `V2 logs: [m019_censoring] epoch_record_committed:epoch=1`
- `V3 logs: [m019_censoring] epoch_record_committed:epoch=1`
- `V4 logs: [m019_censoring] epoch_record_committed:epoch=1`

The committed artifact also states:

- `The honest path was confirmed not permanently suppressed`

Verdict:

- satisfied

### 2.4 Requirement 4 — eventual commit under bounded censoring quorum

Committed runtime evidence:

- all four validators reached `epoch_record_committed:epoch=1`,
- the censoring validator `V4` still integrated payloads arriving through
  non-censored routes,
- redundant propagation through `V2` and `V3` completed the path.

Verdict:

- satisfied

### 2.5 Requirement 5 — explicit mapping note to Phase 698 proof basis

The committed bundle includes an explicit section:

- `## 3. Explicit Phase 698 Formal Model Mapping`

That section maps the live run directly back to:

- `N=4`
- `F=1`
- `MaxRound=5`
- `Liveness property (Row7_Liveness)`

Verdict:

- satisfied

## 3. Post-CRIT-001 framing

This framing is mandatory and load-bearing.

The M-020 censorship evidence bundle was gathered before CRIT-001 closed the
`EpochSettlementTx` production path. The committed bundle still describes
censoring of both `EpochSettlementTx` and `EpochCheckpointMsg` traffic.

The governing post-CRIT-001 interpretation is:

- the row-7 censorship evidence weight is carried by the
  `EpochCheckpointMsg` redundant-path liveness property,
- the `EpochSettlementTx` path is now gated to `testnet_fault_sim` only and
  cannot carry production evidence weight,
- the live row-7 claim survives because the remaining honest validators still
  complete the checkpoint path under bounded censoring.

Post-CRIT-001 framing token:

- `epochcheckpointmsg_carries_row_7_censorship_evidence_weight_post_crit_001`

## 4. Verdict and remaining boundary

All five Phase `741` Section `3.2` requirements are satisfied by the committed
runtime bundle.

Verdict:

- `row_7_censorship_resistance_runtime_closure_verdict=pass`

This closes only the censorship-resistance side of row `7`.

Remaining boundary after `CW-3`:

- strong exitability still requires `CW-4`,
- full row-7 closure cannot be claimed until both sub-verdicts pass,
- no row-8 or Option B claim is authorized here.

## 5. Non-claims

This phase does **not** claim:

- full row-7 closure by itself,
- any row-5 result,
- any row-8 disposition,
- any Option B gate synthesis,
- any `CDL-017` ratification act.
