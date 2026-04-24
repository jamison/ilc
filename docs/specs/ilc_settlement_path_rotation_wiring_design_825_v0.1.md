# ILC Settlement-Path Rotation Wiring Design 825 v0.1

**Phase:** 825
**Date:** 2026-04-24
**Status:** design-only activation sequencing artifact

`settlement_path_rotation_wiring_design_825_published`

## 1. Current State

The Mysticeti fast path exists and has passed the M-series testnet lane.

Current relevant surfaces:

- `ilc_consensus/src/fast_path.rs` owns `execute_certificate` for transfer
  certificates and historical validator-set resolution.
- `ilc_consensus/src/node.rs` owns `handle_broadcast_honest`,
  `handle_full_transfer_honest`, and the BroadcastHonest -> AckFor ->
  Certificate -> execute path.
- `ilc_consensus/src/epoch_settlement.rs` owns BLS-verified epoch checkpoint
  settlement via `process_epoch_checkpoint`.
- `FastPathProtocol::rotate_validator_set` exists as a local helper and SEC-004
  historical binding is closed.
- M-019 and M-021 hardening items are closed; SEC-007a vendored `protoc` is in
  place.

What is not yet present is a production node switch that declares Mysticeti the
live ECU settlement path and routes live settlement submissions through that
path under an operator authorization record.

## 2. Required Wiring Changes

The later implementation window should make the following changes in order:

1. Add an explicit node configuration gate such as
   `settlement_path = "mysticeti_fast_path"` with a default that preserves the
   current non-activation posture.
2. Wire the live ECU submission ingress into the existing
   `handle_broadcast_honest` / `handle_full_transfer_honest` path only when the
   gate is enabled.
3. Require chain ID, network ID, epoch, and active validator-set context to be
   present before certificate execution.
4. Preserve SEC-004 historical validator-set resolution by ensuring every live
   `TransferCertificate` carries the epoch that will be verified.
5. Keep `rotate_validator_set` as a governed helper, not an automatic admission
   path; live invocation remains behind CDL-017 and the first-validator human
   gate.
6. Emit operator-visible activation logs that name the configured settlement
   path, network ID, validator set, and rollback path.
7. Add a three-machine smoke harness that submits a live ECU transfer, obtains
   quorum finalization, verifies LMDB state, and confirms state-extractor /
   `ilc_dag_audit` replayability.

## 3. Scope Boundary

This design does not include:

- Row-5 privacy queue implementation,
- B-Impl runtime work,
- first non-Genesis validator deployment,
- automatic validator admission or ejection,
- HIGH-002 signer-subset hardening,
- CDL mutation,
- public RC graduation.

## 4. Deployment Dependency Split

Pre-deployment work:

- add the configuration gate,
- add dry-run validation,
- add operator logging,
- add test harnesses against local or controlled multi-machine validators.

Deployment-dependent work:

- enabling the gate against a live non-Genesis validator set,
- proving live validator rotation behavior,
- accepting any first-validator deployment success claim.

The deployment-dependent portion requires separate human authorization.

## 5. Smoke Test Criteria

The post-rotation three-machine smoke proof must demonstrate:

- all configured validators start and peer,
- one live ECU transfer reaches certificate execution,
- balances update exactly once,
- epoch checkpoint state is extractable and auditable,
- restart/replay preserves the committed result,
- rollback instructions are executable without corrupting LMDB state.
