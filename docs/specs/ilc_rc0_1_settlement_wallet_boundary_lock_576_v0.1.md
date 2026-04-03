# ILC RC0.1 Settlement + Wallet Boundary Lock 576 v0.1

Status: locked
Date: 2026-04-03
Phase: 576
Owner lane: G8 implementation cluster

## 1. Bounded RC target

Phase 576 locks the settlement and wallet boundary for the RC0.1 curated
testnet.

This packet authorizes bounded economic visibility for the operator-managed
three-machine RC lane without claiming public minting closure, withdrawal, or
transfer semantics.

Required governance tokens:
- `rc0_1_balance_visibility_does_not_imply_public_claimability`
- `ecu_accrual_reaches_ilc_balance_only_through_epoch_commit`
- `wallet_visibility_and_accounting_only`
- `wallet_has_no_ledger_write_authority`
- `wallet_signing_spend_transfer_deferred_post_rc0_1`
- `settlement_replay_must_fail_closed_or_noop_without_balance_drift`
- `founder_and_genesis_reward_split_deferred_to_public_rc_packet`

## 2. Settlement meaning in RC0.1

RC0.1 ILC balance means a settled internal ledger balance produced by the
bounded epoch-commit path on the curated testnet.

`ecu_accrual_reaches_ilc_balance_only_through_epoch_commit`.

A visible RC0.1 balance is operator-queryable and machine-queryable through the
bounded wallet and query surfaces.

`rc0_1_balance_visibility_does_not_imply_public_claimability`.

A visible RC0.1 balance does not, by itself, imply public withdrawal,
transferability, or finalized public minting semantics.

## 3. Balance-state classification

The minimum RC0.1 balance-state classes are:
- submitted ECU claim record
- epoch-attribution candidate included in the current bounded settlement path
- settled internal balance
- deferred public-claimability state

Interpretation rule:
- a submitted ECU claim record is not yet a balance
- an epoch-attribution candidate is eligible for bounded settlement processing
  but is not yet a settled balance
- settled internal balance is the only balance class the wallet may expose as
  `balance_ilc`
- deferred public-claimability state remains outside the RC0.1 testnet claim
  surface

## 4. Wallet boundary and authority split

`wallet_visibility_and_accounting_only`.

Wallet status, history, and export are read-only visibility and accounting
surfaces.

`wallet_has_no_ledger_write_authority`.

Wallet queries must read settled ledger state deterministically.
Wallet queries must not mutate ledger, graph, or settlement state.

The RC0.1 wallet visibility surface must expose stable equivalents for the
currently surfaced runtime fields:
- `balance_ilc`
- `last_settled_epoch_id`
- `reward_status`
- settled history receipts

`wallet_signing_spend_transfer_deferred_post_rc0_1`.

Signing, spend, transfer, and withdrawal semantics are deferred.

## 5. Replay and idempotency rule

`settlement_replay_must_fail_closed_or_noop_without_balance_drift`.

Settlement replay handling must reject or no-op repeated application without
balance drift.

Epoch commit identity and replay-safety rules must remain machine-auditable.

Current runtime-equivalent settlement outcomes must preserve stable
machine-legible status values for:
- applied settlement
- idempotent replay

Wallet history must reflect settled state only, never speculative pre-settle
balances.

## 6. Explicit deferrals to RC0.1+

Deferred beyond RC0.1:
- public claimability and withdrawal semantics
- founder/genesis vs steward/downstream payout stabilization
- broader minting and governance semantics
- spend/transfer wallet functionality

`founder_and_genesis_reward_split_deferred_to_public_rc_packet`.
