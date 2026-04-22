# ILC Phase 767-774 Sequence Lock v0.1

**Phase:** 767  
**Window:** 767-774  
**Date:** 2026-04-22  
**Author:** Local architectural reviewer (Sonnet)

`window_767_774_sequence_lock_active`
`sec_004_post_ratification_activation_window`
`m007_hook_activation_window`
`cdl_017_ratified_phase_765_activation_work_begins`
`first_non_genesis_validator_deployment_remains_separate_human_gate`
`no_row_5_row_8_option_b_work_in_window_767_774`

## 1. Baseline and authority order

CDL-017 ratified Phase 765. Capsule `v5.5` is the current frontier anchor.
Window `763-766` is closed. The live `STATUS.md` tail at sequence-lock time
records:

- M-022 complete; convergence window closed; CDL-017 ratification window closed
- Phase 766 closed Window 763-766 honestly
- No new main-lane window opened by Phase 766; post-ratification activation
  work, row-5 privacy remediation, row-8 substrate evaluation, and hypergraph
  carry-forward remain pending explicit guidance

Security gate summary at sequence-lock time:

- `SEC-004`: OPEN partial — historical ValidatorSet resolution and the named
  acceptance test already exist in `fast_path.rs`; testnet client epoch
  stamping still uses a hardcoded epoch and closure evidence is not yet
  published for this window
- `M-007` hooks (`admit_validator`, `eject_validator`): `unimplemented!`
- `SEC-007a`: DEFERRED — protoc vendoring (does not block this window)
- `HIGH-002`, `HIGH-001`: DOCUMENTED LIMITATIONS (do not block this window)
- All SEC-001 through SEC-010 (excluding 004 and 007a): CLOSED

Authority order for this window:

1. live `STATUS.md` tail and `docs/PLANNING_INDEX.md`
2. capsule `v5.5`
3. CDL-017 ratification evidence (`ilc_cdl_017_validator_governance_framework_ratification_evidence_765_v0.1.md`)
4. CDL-017 interaction synthesis and activation-boundary record (`ilc_cdl_017_interaction_synthesis_and_activation_boundary_record_764_v0.1.md`)
5. M-series lane (`docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`)
6. M-022 Gemini handoff package
7. live constitutional decision log
8. post-766 continuation program guide (`docs/research/ilc_post_766_continuation_program_guide_2026_04_22_v0.1.md`)

## 2. Pre-window scope correction (decided 2026-04-22)

Before opening this window, the reviewer conducted a code audit of the
SEC-004 implementation state. Three corrections to the inherited framing apply:

**Correction 1 — TransferCertificate wire format is already complete.**
`TransferCertificate` carries `pub epoch: EpochSeq` at
`ilc_consensus/src/types.rs:135`. The field exists. It is not a design
question for this window.

**Correction 2 — Historical ValidatorSet resolution is already implemented.**
`execute_certificate` in `ilc_consensus/src/fast_path.rs` already resolves
the historically active `ValidatorSet` using:

```rust
let sets = self.epoch_sets.read().unwrap();
let vs = sets
    .range(..=cert.epoch)
    .next_back()
    .map(|(_, vs)| vs)
    .ok_or(ILCConsensusError::InvalidEpoch)?;
```

All cert signatures are verified against that historical set. The verification
logic is correct.

**Correction 3 — The named SEC-004 acceptance test already exists.**
`test_ejected_validator_sig_rejected_after_epoch_boundary` is already present
in `ilc_consensus/src/fast_path.rs`. It covers four cases:

1. epoch-1 cert accepted before rotation
2. epoch-1 cert accepted after the epoch-2 rotation because historical
   resolution still selects the epoch-1 set
3. epoch-2 cert with ejected validator `V3` rejected
4. epoch-2 cert with only still-active validators accepted

The test is load-bearing evidence for this window and must be preserved.

**What remains for SEC-004 in this window:**
1. The existing acceptance test must remain present, passing, and referenced in
   the phase gate and M-series lane update. No duplicate alternative SEC-004
   test scenario is required for this window.
2. The testnet client (`testnet_client_main.rs`) hardcodes `epoch: EpochSeq(1)`
   on all assembled certs (Audit Finding D, M-015 audit). This must be
   corrected to stamp the current epoch from the client's known state.
3. `rotate_validator_set` must be callable and tested in isolation for the
   acceptance test; live wiring into the epoch settlement event is deferred
   until the CDL-017 payload design is resolved (out of scope for this window).

**M-007 scope — constitutional basis now present:**
CDL-017 ratification removes the `unimplemented!` gate. The live M-007 hook
surface in this repo is `ValidatorSet::admit_validator` and
`ValidatorSet::eject_validator` in `ilc_consensus/src/validator.rs`, not
`node.rs`. The activation work in this window means: replace those
`unimplemented!()` stubs with working `ValidatorSet` mutation logic under
CDL-017 constitutional authority.

For testnet-path scope, the hooks are pure set-transform helpers:

- `admit_validator(id, key)` appends the new validator if absent
- `eject_validator(id)` removes the validator if present
- both rebuild the set through `ValidatorSet::new(...)` with
  `f = (N - 1) / 3` computed from the resulting validator count so the set
  remains internally valid after membership changes

These hooks do **not** live-wire `rotate_validator_set` into the epoch
settlement path. Production-grade governance delivery (transaction carrier,
CDL-017 payload carrier, operator ceremony) remains out of scope and behind
the separate human gate before any first non-Genesis deployment.

## 3. Window meaning

Window `767-774` is the SEC-004 wiring and M-007 activation window.

`sec_004_acceptance_test_required`
`m007_hooks_activatable_under_cdl_017_authority`
`rotate_validator_set_testable_in_isolation`
`live_settlement_wiring_deferred_pending_cdl_017_payload_design`
`testnet_client_epoch_stamp_must_be_corrected`
`first_non_genesis_validator_deployment_requires_human_gate_after_this_window`

This window exists to:

1. preserve and pass `test_ejected_validator_sig_rejected_after_epoch_boundary`,
   which is the named SEC-004 acceptance condition from the CDL-017
   ratification evidence
2. correct testnet client epoch stamping (remove hardcoded `EpochSeq(1)`)
3. activate M-007 `ValidatorSet::admit_validator` and
   `ValidatorSet::eject_validator` under CDL-017 constitutional authority
   (testnet-path implementation)
4. update the M-series lane document to record SEC-004 and M-007 activation
   as complete
5. produce a Codex audit artifact confirming constitutional compliance of the
   activation work
6. explicitly name the human gate for the first non-Genesis validator
   deployment as the remaining step after this window

This window does not deploy a validator. It does not perform live
`rotate_validator_set` wiring into the epoch settlement event path. It does
not close row `5`. It does not evaluate a row `8` candidate. It does not
claim Option B graduation.

## 4. Implementation scope and constraints

### 4.1 SEC-004 acceptance test

File: `ilc_consensus/src/fast_path.rs`.

The named SEC-004 acceptance test already exists and must remain the
authoritative scenario:

```
1. Build an epoch-1 validator set with validators V1, V2, V3, V4 (N=4, f=1)
2. Assemble an epoch-1 cert signed by V1/V2/V3 → PASS before rotation
3. Rotate at EpochSeq(2) to eject V3, producing validators V1, V2, V4 (N=3, f=0)
4. Re-submit an epoch-1 cert signed by V1/V2/V3 → still PASS because the
   historically active epoch-1 set governs that cert
5. Submit an epoch-2 cert signed by V1/V2/V3 → FAIL because V3 is not in the
   epoch-2 set
6. Submit an epoch-2 cert signed only by still-active validators → PASS
```

No duplicate disjoint-membership variant is required. The closure gate must
assert that this exact named test remains present and passes in CI.

### 4.2 Testnet client epoch stamping

File: `ilc_consensus/src/testnet_client_main.rs`.

Replace hardcoded `epoch: EpochSeq(1)` with the current epoch derived from
the client's tracking state (query current epoch from the node, or stamp
from the cert assembly context). The exact query path is an implementation
detail; the requirement is that no test or runner that submits epoch-N certs
will stamp a hardcoded epoch-1 after this window.

### 4.3 M-007 hook activation

Files: `ilc_consensus/src/validator.rs` and its companion unit-test module.

Replace `unimplemented!()` with working `ValidatorSet` mutation logic. For
testnet-path scope:
- `admit_validator(id, key)`: reject duplicate `ValidatorID`, append the new
  validator, recompute `f = (N - 1) / 3` from the resulting cardinality, then
  rebuild through `ValidatorSet::new(...)`
- `eject_validator(id)`: reject missing `ValidatorID`, remove the validator,
  recompute `f = (N - 1) / 3`, then rebuild through `ValidatorSet::new(...)`

These hooks are pure membership-transform helpers; they do **not** call
`rotate_validator_set`, do **not** carry an epoch parameter, and do **not**
constitute live governance delivery. Production governance delivery and
settlement-path activation remain explicitly deferred.

### 4.4 Concurrency constraint

`epoch_sets` is `Arc<RwLock<BTreeMap<EpochSeq, ValidatorSet>>>`. Write access
via `rotate_validator_set` must acquire the write lock and release it before
any subsequent read in `execute_certificate`. The monotonicity guard (already
implemented: stale-epoch calls are a no-op with a log line) must remain in
place. No new unsafe concurrency surface may be introduced.

### 4.5 What must not be implied

- No sentence in this window may imply that live `rotate_validator_set` wiring
  into the epoch settlement event path is complete.
- No sentence may imply that first non-Genesis validator deployment is
  automatically authorized by this window's completion.
- No sentence may imply that HIGH-002 (all-N quorum) is resolved.
- No sentence may imply that SEC-007a (protoc vendoring) is resolved.

## 5. Phase table and sequencing

| Order | Phase | Topic | Character |
|---|---:|---|---|
| 1 | 767 | sequence lock | gate / planning |
| 2 | 768 | SEC-004 acceptance-test verification + testnet client epoch fix | M-track Rust implementation |
| 3 | 769 | M-007 hook activation in `validator.rs` | M-track Rust implementation |
| 4 | 770 | Codex audit artifact: constitutional compliance review | audit |
| 5 | 771 | M-series lane doc update: SEC-004 and M-007 recorded as complete | documentation |
| 6 | 772 | integration review: all existing tests pass; no regression from activation | gate |
| 7 | 773 | coherence report + capsule v5.6 | coherence |
| 8 | 774 | closure gate | gate / handoff |

Sequencing rules:

- Phase `767` opens the window and does not mutate `ilc_consensus/` or
  `ilc_core/` runtime code
- Phase `768` is the first Rust mutation phase; it preserves the existing
  SEC-004 acceptance evidence and fixes the client-side epoch stamp; the
  acceptance test must pass before Phase 769
- Phase `769` activates the M-007 hooks in `validator.rs`; it may not be
  executed before Phase 768's acceptance test passes
- Phase `770` is the Codex audit; it reads the Phase 768 and 769 outputs
  without introducing new mutations unless a specific bug is found
- Phase `771` updates the M-series lane doc; it may not claim SEC-004 or M-007
  complete until Phase 770's audit artifact records no blocking findings
- Phase `772` is an integration verification gate; all `cargo test` targets
  must pass including the new acceptance test and the existing M-series regression suite
- Phase `773` is the coherence and capsule phase; capsule `v5.6` replaces `v5.5`
- Phase `774` is the closure gate and produces the handoff note for Window 6
  (`803+`); it must name the human gate for first non-Genesis validator
  deployment explicitly

## 6. Explicit non-conflation obligations

This window must preserve the following non-conflation boundaries:

1. SEC-004 acceptance test passing is not proof that live `rotate_validator_set`
   is wired into the epoch settlement path.
2. M-007 hook activation is not first non-Genesis validator admission.
3. First non-Genesis validator deployment requires a separate human gate after
   this window; this window does not cross that gate.
4. `rotate_validator_set` isolation in a test is not the same as live wiring
   at epoch boundary.
5. CDL-017 ratification constitutionally grounds the hook activation; it does
   not specify the production governance delivery mechanism — that remains out
   of scope until CDL-017 payload design is ratified.
6. Row 5, row 8, and Option B are unaffected by this window.

## 7. Pass conditions for closure gate (Phase 774)

The closure gate must assert:

- `test_ejected_validator_sig_rejected_after_epoch_boundary` exists, passes in
  CI, and is referenced in the M-series lane doc
- testnet client no longer hardcodes `epoch: EpochSeq(1)`
- `admit_validator` and `eject_validator` are no longer `unimplemented!()` in
  any build target
- Codex audit artifact records no unresolved blocking findings
- M-series lane doc records SEC-004 and M-007 as activated in this window
- capsule `v5.6` supersedes `v5.5`
- human gate for first non-Genesis validator deployment is named explicitly in
  the handoff and is not claimed to be crossed

## 8. Non-goals

This window does not include:

- live wiring of `rotate_validator_set` into the epoch settlement event path
- production governance delivery mechanism for validator admission/ejection
- any first non-Genesis validator deployment or key provisioning
- row-5 privacy remediation
- row-8 substrate evaluation
- CDL-062 admissibility determination
- Option B graduation
- H-010, H-014, H-013, or any other hypergraph work
- SEC-007a (protoc vendoring) resolution
- HIGH-002 (all-N quorum) resolution

## 9. Source inputs

- `docs/PLANNING_INDEX.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.5.md`
- `docs/specs/ilc_window_763_766_closure_gate_766_v0.1.md`
- `docs/specs/ilc_cdl_017_validator_governance_framework_ratification_evidence_765_v0.1.md`
- `docs/specs/ilc_cdl_017_interaction_synthesis_and_activation_boundary_record_764_v0.1.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `ilc_consensus/src/types.rs` (confirmed: TransferCertificate.epoch exists at line 135)
- `ilc_consensus/src/fast_path.rs` (confirmed: historical ValidatorSet resolution implemented at lines 77-82)
- `docs/research/ilc_post_766_continuation_program_guide_2026_04_22_v0.1.md`
- `docs/research/ilc_mysticeti_workload_c_results_M015_v0.1.md` (Audit Finding D: hardcoded epoch)

This sequence lock remains active until Phase `774` closes Window `767-774`.
