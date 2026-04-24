# ILC Antigravity Context Capsule v5.13

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.12.md
Date: 2026-04-24
Owner lane: G8 Row-5 B-Scope closure / B-Impl commissioning

`capsule_v5_13_supersedes_v5_12`
`option_b_selected_by_human_authorization_2026_04_23`
`adr_0028_posture=option_b`
`cdl_017_remains_ratified`
`row5_b_scope_window_closed`
`row5_mechanism_selection_human_gate_closed`
`row5_k_anonymity_jitter3_primary_locked`
`row5_k_anonymity_jitter3_k20_fallback_locked`
`row5_b_impl_commissioned_local_reviewer`
`transfer_class_groundwork_present`
`row5_still_spec_closed_runtime_pending`
`no_cdl_mutation_in_phase_b5`

This capsule is self-contained.

## 1. Current Frontier State

Window B-Scope is now closed.

The corrected Row-5 outcome is:

- the original B-4 mixing recommendation is superseded,
- the locked primary mechanism is `k=30`, `rolling_threshold`,
  `release_jitter_epochs=3`, `bounded_hold`,
- the locked fallback is `k=20` with the same jitter policy,
- the intended B-Impl target remains the simulation-derived recommendation
  `A<=0.15`, `B<=0.15`, `C<=0.05`,
- Row 5 remains `spec_closed_runtime_pending`.

## 2. Carry-Forward Runtime Posture

The runtime groundwork already present in the worktree and code surface is:

- `TransferClass`
- `ExpressConsent`
- `ECUTransfer.transfer_class`

The implementation lane commissioned from this point is:

- rolling group construction in the submission path,
- deferred jitter queue,
- bounded-hold enforcement,
- automatic fallback activation,
- degraded-anonymity notification,
- live instrumentation for `SIM-LEAKAGE-03`.

This implementation is commissioned to the local reviewer. B-5 does not claim
that the runtime work is complete.

## 3. Preserved Constitutional and Governance Boundaries

This capsule preserves:

- `option_b_selected_by_human_authorization_2026_04_23`,
- `adr_0028_posture=option_b`,
- `CDL-017` remains ratified,
- row 7 remains `runtime_closed`,
- row 8 remains `pass`.

This capsule does not claim:

- Row 5 runtime closure,
- Option B graduation,
- any new CDL ratification or mutation,
- first non-Genesis validator deployment,
- `SIM-LEAKAGE-03` completion.

## 4. Immediate Carry-Forward

The next meaningful Row-5 proof step is not another scoping pass.

It is:

1. B-Impl delivery in the runtime, and then
2. `SIM-LEAKAGE-03` against the M-009 testbed.

Only after those steps can the Row-5 runtime closure window open honestly.
