# ILC Phase 763-766 Sequence Lock v0.1

**Phase:** 763  
**Window:** 763-766  
**Date:** 2026-04-21  
**Author:** Codex

`window_763_766_sequence_lock_active`
`cdl_017_ratification_window_active`
`cdl_017_ratification_window_open_approved_by_reviewer`
`track_b_m022_complete_convergence_closed_cdl_017_window_open`
`row_5_spec_closed_runtime_pending_at_window_open`
`row_7_runtime_closed_at_window_open`
`row_8_inherited_candidate_evaluation_pending_at_window_open`
`sec_004_activation_scope_post_ratification_only`
`first_non_genesis_validator_deployment_requires_separate_human_gate`
`no_m007_hook_activation_in_window_763_766`

## 1. Baseline and authority order

The convergence window is closed. Capsule `v5.4` is the latest published
main-lane capsule at sequence-lock time. `CDL-017` remains open and
unratified. Row `5` remains `spec_closed_runtime_pending` with an honest fail
record. Row `7` is `runtime_closed`. Row `8` remains inherited as a
criteria-locked surface with no candidate evaluation. ADR-0028 still leaves
Option D as the active settlement posture.

Track B was re-read from `docs/phases/STATUS.md` tail at execution time rather
than copied from memory or from capsule `v5.4`. The live tail states:

- `M-022 complete; convergence window closed; later CDL-017 ratification window pending reviewer approval`

Reviewer approval has now been supplied explicitly, so this phase opens the
later `CDL-017` ratification window against that inherited frontier rather than
inventing a new frontier by prose.

Authority order for this window is:

1. live `STATUS.md` tail and `docs/PLANNING_INDEX.md`,
2. capsule `v5.4` and the convergence closure gate,
3. the Phase `755` ratification-readiness dossier,
4. the Phase `695` CDL-017 opening stub,
5. the live constitutional decision log,
6. ratified carry-forward surfaces for `CDL-055`, `CDL-056`, and `CDL-068`,
7. the M-series lane and M-022 handoff package for activation-bound
   implementation scope.

## 2. Inherited ratification constraints

This window inherits the closed-state boundary from Phase `762`, the later
ratification route from Phase `755`, and the reviewer-approved constraints now
fixed for execution:

- validator admission and ejection must be treated as governed protocol actions,
- Genesis-only authority remains operative for the near-term testnet at window
  open,
- ratification must state the activation boundary explicitly rather than
  implying automatic deployment,
- SEC-004 remains post-ratification M-track activation work and must be named
  with its acceptance condition,
- `CDL-055` and `CDL-056` may not be silently superseded; carry-forward versus
  amendment must be explicit,
- first authorized non-Genesis validator deployment remains a separate human
  gate after ratification,
- the M-007 `admit_validator` / `eject_validator` hooks remain
  `unimplemented!` and may not be activated in this window,
- no `ilc_core/` or `ilc_consensus/` mutation is authorized in the Codex main
  lane for this packet.

This window is therefore constitutional ratification work only. It is not a
runtime-activation lane.

## 3. Window meaning

Window `763-766` is the later `CDL-017` ratification window.

`cdl_017_open_at_window_entry`
`cdl_017_ratification_authorized_in_window_763_766`
`cdl_017_ratification_window_consumes_convergence_outputs`
`cdl_017_ratification_does_not_activate_runtime_hooks`
`sec_004_post_ratification_activation_scope_named`

This window exists to:

1. lock the ratification sequence against the now-complete convergence inputs,
2. synthesize the explicit interaction matrix for `CDL-017`, `CDL-055`,
   `CDL-056`, `CDL-068`, and SEC-004,
3. ratify `CDL-017` as the constitutional validator-governance lane for
   bootstrap transition, Genesis sunset, and dynamic validator-set activation
   boundary,
4. preserve the separate explicit human gate for first authorized non-Genesis
   validator deployment,
5. close the window with coherence, capsule `v5.5`, and a closure gate.

This window does not deploy a validator. It does not activate dynamic
validator-set hooks. It does not claim Option B graduation. It does not close
row `5` by rhetoric. It does not reopen row `7`. It does not evaluate a row
`8` substrate candidate.

## 4. Constitutional interaction boundaries at open

### 4.1 CDL-017 scope at ratification time

At this window open, `CDL-017` is the constitutional home for:

- validator admission and ejection as governed protocol actions,
- bootstrap-transition criteria,
- Genesis-sunset trigger design as it applies to validator authority,
- the activation boundary for dynamic validator-set operation.

The window must preserve the narrow truth fixed in the opening stub:

- Genesis-only authority remains operative for the near-term testnet,
- ratification is not deployment,
- ratification is not hook activation,
- ratification is not first-validator authorization by itself.

### 4.2 SEC-004 interaction

SEC-004 remains activation-bound and post-ratification:

- `TransferCertificate` must gain `epoch: EpochSeq`,
- certificate verification must resolve the historically active
  `ValidatorSet` for that epoch,
- the named acceptance condition is
  `test_ejected_validator_sig_rejected_after_epoch_boundary`,
- this implementation work begins only after `CDL-017` ratifies,
- no sentence in this window may imply that SEC-004 is already implemented.

### 4.3 CDL-055 / CDL-056 interaction

`CDL-055` and `CDL-056` remain ratified and live. This window must preserve
their boundaries unless it states otherwise explicitly.

The required ratification discipline is:

- Phase `764` must publish an explicit carry-forward / amendment matrix for
  `CDL-055` and `CDL-056`,
- Phase `765` must restate that matrix in the ratification artifact,
- silent supersession is prohibited.

The inherited baseline is:

- validator participation stake, liveness penalties, equivocation slash, and
  re-admission separation remain anchored to `CDL-055`,
- validator trust-tier elevation remains non-inheritable and tied to the
  ratified `CDL-055` liveness threshold per `CDL-056`,
- `CDL-017` governs validator-governance activation, not a hidden rewrite of
  staking or trust-tier law.

### 4.4 M-007 hook and deployment boundary

The M-007 hook points exist, but they remain disabled:

- `admit_validator` is still `unimplemented!`,
- `eject_validator` is still `unimplemented!`,
- that disabled state remains correct throughout this window.

The first non-Genesis validator remains a later operator decision after
ratification and after post-ratification implementation work begins. This
window may name that gate. It may not cross it.

## 5. Phase table and sequencing

| Order | Phase | Topic | Character |
|---|---:|---|---|
| 1 | 763 | sequence lock | gate / constitutional planning |
| 2 | 764 | CDL-017 interaction synthesis and activation-boundary record | constitutional evidence synthesis |
| 3 | 765 | CDL-017 ratification and decision-log mutation | constitutional ratification |
| 4 | 766 | coherence report + capsule v5.5 + closure gate | gate / handoff |

Sequencing rules:

- Phase `763` opens the window and does not mutate the decision log,
- Phase `764` may publish synthesis and evidence-packaging material but does
  not mutate the decision log,
- only Phase `765` may mutate the decision log,
- Phase `765` must follow the two-commit ratification discipline:
  commit 1 publishes the ratification artifact, tests, and ratification
  backfill; commit 2 mutates exactly the `CDL-017` row in
  `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- the Phase `765` second commit may touch only the `CDL-017` row and no other
  file,
- Phase `766` is the closure gate for the window and must summarize only what
  Phases `763-765` actually established.

Phase `766` is the closure gate for the window.

## 6. Explicit non-conflation obligations

This window must preserve seven non-conflation boundaries:

1. `CDL-017` ratification is not runtime hook activation.
2. `CDL-017` ratification is not first non-Genesis validator deployment.
3. SEC-004 activation scope is not proof that SEC-004 is already implemented.
4. `CDL-017` activation law is not silent supersession of `CDL-055`.
5. `CDL-017` activation law is not silent supersession of `CDL-056`.
6. row `7` runtime closure is inherited evidence, not a new ratification claim.
7. row `5` honest fail record remains true and is not erased by validator-law
   ratification.

No hidden runtime activation is authorized by ratification rhetoric in this
window.

## 7. Non-goals

This window does not include:

- any `ilc_core/` or `ilc_consensus/` mutation,
- any activation of `admit_validator` or `eject_validator`,
- any claim that first non-Genesis validator deployment is now authorized
  automatically,
- any claim that SEC-004 is already closed,
- any silent amendment of `CDL-055` or `CDL-056`,
- any row `5` runtime closure claim,
- any row `8` candidate evaluation,
- any Option B graduation claim,
- any sovereign-substrate selection.

## 8. Source inputs

The authoritative source set for this sequence lock is:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.4.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_mysticeti_convergence_window_closure_gate_762_v0.1.md`
- `docs/specs/ilc_row_5_runtime_closure_evaluation_cw2_v0.1.md`
- `docs/specs/ilc_row_7_censorship_runtime_closure_evaluation_cw3_v0.1.md`
- `docs/specs/ilc_row_7_exitability_closure_evaluation_cw4_v0.1.md`
- `docs/specs/ilc_row_8_disposition_and_option_b_gate_synthesis_cw5_v0.1.md`
- `docs/specs/ilc_cdl_017_ratification_readiness_dossier_v0.1.md`
- `docs/specs/ilc_cdl_017_opening_stub_695_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_ratification_evidence_496_v0.1.md`
- `docs/specs/ilc_cdl_056_validator_trust_tier_elevation_ratification_evidence_501_v0.1.md`
- `docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md`
- `docs/research/ilc_validator_agent_design_evidence_v0.1.md`
- `docs/research/ilc_validator_agent_q1_q6_prewindow_resolution_v0.1.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`
- `docs/specs/ilc_master_completion_roadmap_v0.1.md`

This sequence lock remains active until Phase `766` closes Window `763-766`.
