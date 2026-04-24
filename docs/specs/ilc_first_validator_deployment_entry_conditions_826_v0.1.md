# ILC First-Validator Deployment Entry Conditions 826 v0.1

**Phase:** 826
**Date:** 2026-04-24
**Status:** operator checklist, gate not pulled

`first_validator_entry_conditions_record_826_published`
`first_validator_deployment_human_gated_no_trigger_this_window`

## 1. Constitutional Prerequisites

CDL-017 is ratified, but Phase 765 preserves the activation boundary:

- Genesis-only validator authority remains operative until a later deployment
  decision,
- ratification opens validator-governance law only,
- first non-Genesis validator deployment still requires a later human gate,
- CDL-055, CDL-056, and CDL-068 remain carried forward unchanged.

The operator authorization must therefore be explicit. No artifact in Window
823-829 pulls that gate.

## 2. Implementation Prerequisites

Before the gate can be considered satisfiable, the operator must verify:

- SEC-004 historical validator-set binding remains closed,
- M-007 local `ValidatorSet` mutation helpers remain available under CDL-017
  authority,
- M-019 adversarial hardening is complete,
- M-021 genesis BLS fix is complete,
- SEC-007a vendored `protoc` build path remains green,
- the Phase 825 settlement-path rotation wiring design has been consumed by an
  implementation window,
- validator keys, TLS material, genesis state, network ID, and rollback plan are
  recorded,
- the three-machine smoke proof described in Phase 825 has passed.

## 3. Row-5 Gating

Row 5 runtime closure is not a prerequisite for first-validator deployment at
controlled testnet scale.

Rationale: Row 5 is a pre-public-RC privacy obligation. First-validator
deployment is a controlled validator-governance activation step, not a public
RC graduation claim. Row 5 remains `spec_closed_runtime_pending` until B-Impl
and `SIM-LEAKAGE-03` complete.

## 4. HIGH-002 Gating

HIGH-002 hardening is not a prerequisite for first-validator deployment at
controlled testnet scale.

Rationale: HIGH-002 is a liveness limitation, not a safety break. It becomes
mandatory before independently operated production validator sets or no later
than `N >= 4`, `F >= 1` production hardening, as recorded in Phase 824.

## 5. Smoke Proof Requirement

A post-rotation three-machine smoke proof must pass before deployment can be
accepted as successful. The proof must show:

- validator peering,
- live ECU transfer finalization,
- exact-once balance update,
- extractable epoch state,
- audit replayability,
- rollback readiness.

## 6. Human Gate Form

The human authorization record must state at minimum:

- date and operator identity,
- validator IDs and machine identities,
- network ID and chain ID,
- genesis hash or validator-set snapshot,
- exact deployment command or runbook reference,
- rollback command or runbook reference,
- acknowledgement that Row 5 remains runtime-pending,
- acknowledgement that HIGH-002 remains production-hardening debt,
- explicit statement that the first non-Genesis validator deployment gate is
  being pulled.
