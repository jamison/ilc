# ILC SEC-004 / M-007 Activation Codex Audit v0.1

## 1. Constitutional compliance

Phase `768` and Phase `769` remain inside the authority boundary created by
`CDL-017` ratification in Phase `765`. The landed work does not mutate the
constitutional decision log, does not authorize first non-Genesis validator
deployment, and does not claim live governance delivery or settlement-path
activation. The work is constitutionally narrow:

- Phase `768` preserves the named SEC-004 acceptance condition and removes the
  hardcoded client certificate epoch from `full_transfer`
- Phase `769` activates the live `ValidatorSet` admission/ejection hook surface
  that was still `unimplemented!()` after ratification

Required token:

`phase_770_audit_cdl_017_constitutional_compliance=confirmed`

## 2. SEC-004 implementation review

The SEC-004 implementation state is coherent.

Status:

- `test_ejected_validator_sig_rejected_after_epoch_boundary` exists in
  `ilc_consensus/src/fast_path.rs`
- the test passes under
  `~/.cargo/bin/cargo test --features testnet_fault_sim test_ejected_validator_sig_rejected_after_epoch_boundary -- --nocapture`
- `execute_certificate` resolves the governing `ValidatorSet` from
  `epoch_sets.range(..=cert.epoch).next_back()`, which is the correct
  historical lookup
- `rotate_validator_set` remains exercised only in isolation; it is not wired
  into the live epoch-settlement path
- `ilc_consensus/src/testnet_client_main.rs` no longer hardcodes
  `epoch: EpochSeq(1)` in `full_transfer`

Evidence-backed conclusion:

The named acceptance condition from the CDL-017 ratification packet is now
present and passing on the live tree, and the M-015 audit finding about the
hardcoded client epoch stamp is resolved.

Required token:

`phase_770_audit_sec_004_acceptance_test=confirmed`

## 3. M-007 implementation review

The M-007 implementation state is coherent.

Status:

- `ValidatorSet::admit_validator` and `ValidatorSet::eject_validator` in
  `ilc_consensus/src/validator.rs` are no longer `unimplemented!()`
- both hooks are implemented as pure `ValidatorSet` mutation helpers
- both hooks route through `rebuild_with(...)`, which recomputes
  `f = (N - 1) / 3` from the resulting cardinality and then rebuilds through
  `ValidatorSet::new(...)`
- duplicate admit, missing-validator eject, and invalid-collapse paths all
  return explicit `ILCConsensusError::Other(...)` values rather than panicking
- the Rust validator test set covers success plus all three edge conditions

Evidence-backed conclusion:

The activation work landed on the correct API surface and preserved the
constitutional non-conflation boundary: these hooks are active as local set
transforms, not as live governance delivery.

Required token:

`phase_770_audit_m007_hooks_activated=confirmed`

## 4. Concurrency hazard review

`epoch_sets` remains the only new concurrency-bearing SEC-004 surface in this
window. The current state is acceptable.

Review points:

- `rotate_validator_set` acquires the write lock on `epoch_sets`, updates the
  map, drops that guard, then updates the compatibility view in
  `validator_set`
- `execute_certificate` acquires the read lock on `epoch_sets` and performs the
  historical set resolution before quorum and signature verification
- Phase `769` introduces no new shared-state surface because `ValidatorSet`
  admission/ejection is implemented as local mutation methods on `&mut self`
  rather than as a new `Arc<RwLock<...>>` path

Verdict:

`CLEAR` — no new blocking concurrency hazard was introduced by Phase `768` or
Phase `769`.

## 5. Non-conflation verification

All seven non-conflation obligations from the sequence lock remain satisfied:

1. The SEC-004 acceptance test passing is not treated as proof of live
   settlement-path wiring.
2. M-007 hook activation is not treated as first non-Genesis validator
   admission.
3. The first non-Genesis validator remains behind a separate human gate.
4. `rotate_validator_set` isolation in a test is not treated as live epoch
   boundary wiring.
5. CDL-017 remains the constitutional authority only; production governance
   delivery remains deferred.
6. Row `5`, row `8`, and Option B remain untouched by this window.
7. No CDL row was mutated in Phase `768` or Phase `769`.

Required tokens:

`phase_770_audit_live_settlement_wiring_deferred=confirmed`
`phase_770_audit_first_validator_deployment_gate_preserved=confirmed`

## 6. Unresolved findings (if any)

No unresolved BLOCKING findings.

Non-blocking note:

- `full_transfer` now stamps the certificate epoch from the existing `--epoch`
  CLI context with a floor-to-1 fallback, rather than performing a direct
  read-service query at runtime. This is acceptable for current testnet scope
  because the sequence lock explicitly allowed stamping from cert assembly
  context, but it remains an operational limitation rather than a dynamic epoch
  discovery path.

## 7. Audit verdict

Audit verdict: `CLEAR`.

Phase `768` and Phase `769` are consistent with the live codebase, satisfy the
window’s constitutional and technical constraints, and introduce no blocking
defect. The window may proceed to the M-series lane documentation update.
