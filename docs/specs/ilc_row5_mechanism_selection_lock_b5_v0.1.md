# ILC Row-5 Mechanism Selection Lock B5 v0.1

**Phase:** B-5
**Window:** B-Scope
**Date:** 2026-04-24
**Status:** locked after human hold-point closure
**Supersedes:** `docs/specs/ilc_row5_mechanism_selection_recommendation_b4_v0.1.md`, `docs/specs/ilc_row5_mechanism_selection_recommendation_b4_fix1_v0.1.md`, `docs/specs/ilc_row5_mechanism_selection_recommendation_b4_fix2_v0.1.md`, `docs/specs/ilc_row5_mechanism_selection_recommendation_b4_fix3_v0.1.md`

`row5_mechanism_selection_human_gate_closed`
`row5_mechanism_selection_lock_b5_published`
`row5_k_anonymity_jitter3_primary_locked`
`row5_k_anonymity_jitter3_k20_fallback_locked`
`row5_still_spec_closed_runtime_pending`

## 1. Hold-Point Closure Record

The B-4 hold point is closed.

Q1. Adopt `k=30`, `rolling_threshold`, `release_jitter_epochs=3`, `bounded_hold`?

- Yes. Adopted as the primary mechanism.

Q2. Is `p95<=3 minutes` acceptable, or is `1 minute` required?

- `3 minutes` is acceptable.
- The selected mechanism is therefore the `k=30 + jitter=3` k-anonymity lane.
- Mixing remains documented only as the alternative if a later operator decision
  makes `1-minute p95` a hard requirement.

Q3. Confirm the simulation-derived B-Impl target?

- Yes.
- The locked simulation-derived recommendation, pending live confirmation via
  `SIM-LEAKAGE-03`, is:
  - `A<=0.15`
  - `B<=0.15`
  - `C<=0.05`

Q4. Was the `k=20 + jitter=3` fallback explored and accepted?

- Yes.
- FIX-4 confirmed `k=20 + jitter=3` as a viable fallback with
  `A=0.050`, `B=0.050`, `C=0.045`, `p95=3 epochs`.

## 2. Locked Primary Mechanism

The locked primary mechanism is:

- family: `k-anonymity`
- `k_value=30`
- `release_mode=rolling_threshold`
- `release_jitter_epochs=3`
- `carry_over_policy=bounded_hold`
- `max_wait=3..5 epochs`

Expected behavior from the FIX-3 evidence:

- best observed recall: `A=0.033`, `B=0.033`, `C=0.030`
- `p50≈1.5 epochs`
- `p95≈3 epochs`

The important architectural property is the one surfaced by FIX-3: at higher
network volume, settlement converges to the jitter-dominated floor rather than
remaining throughput-limited. The privacy budget is the fixed `0..3 epoch`
decorrelation window, not an ever-growing queue delay.

## 3. Locked Fallback

The locked fallback is:

- family: `k-anonymity`
- `k_value=20`
- `release_mode=rolling_threshold`
- `release_jitter_epochs=3`
- `carry_over_policy=bounded_hold`
- `max_wait=3 epochs`

Fallback activation criterion:

- if `k=30` group-fill failure exceeds `5%` of windows within `1.5x max_wait`,
  activate `k=20` with no other parameter change.

Fallback evidence from FIX-4:

- `A=0.050`
- `B=0.050`
- `C=0.045`
- `p95=3 epochs`

## 4. Locked B-Impl Target

The selected mechanism does not set a runtime bar by itself. It sets the
intended B-Impl target.

The locked target is:

- `A<=0.15`
- `B<=0.15`
- `C<=0.05`

This is a simulation-derived recommendation only. It becomes a live runtime
claim only if:

1. B-Impl lands in the runtime, and
2. `SIM-LEAKAGE-03` confirms the live system meets it.

## 5. Two-Tier Privacy Lanes

Two transfer classes are now adopted at the mechanism-lock level.

### 5.1 Contribution transfers

`Contribution` transfers use the privacy lane mandatorily.

- no opt-out
- k-group queue participation is required
- the anonymity set is collective; one opt-out would degrade the batch for all
  members, so no individual opt-out is allowed here

### 5.2 Payment transfers

`Payment` transfers default to the same privacy lane, but may opt into express
immediate settlement on a per-transfer basis.

The express path requires:

- `ExpressConsent { agent_acknowledged_timing_disclosure: bool, consent_epoch: EpochSeq }`
- explicit acknowledgment of timing-disclosure risk
- epoch-scoped consent, not a permanent account-level flag

The implementation groundwork for this contract is already present in
[`types.rs`](/Users/jamstar/Documents/ILC_Main/01_Current/ilc_consensus/src/types.rs):

- `TransferClass`
- `ExpressConsent`
- `ECUTransfer.transfer_class`

This groundwork is carried forward into B-Impl. It is not a B-5 reimplementation
target.

## 6. Alternative Retained but Not Selected

The mixing family remains documented as the alternative if a later operator
decision makes `1-minute p95` settlement a hard requirement.

The retained reference configuration is:

- `pool=32`
- `delay=1 epoch`
- best observed model result `A≈0.091`, `B≈0.084`, `C≈0.005`, `p95=1 epoch`

That mechanism is not selected here because the accepted UX budget is
`p95<=3 minutes`, and the `k=30 + jitter=3` lane materially outperforms mixing
on Variants A and B while remaining inside the selected target.

## 7. Non-Claims

This lock does not claim:

- Row 5 `runtime_closed`
- `SIM-LEAKAGE-03` completed
- live runtime confirmation of the selected target
- Option B graduation
- any CDL mutation
- any Rust implementation delivery by Codex in B-5
