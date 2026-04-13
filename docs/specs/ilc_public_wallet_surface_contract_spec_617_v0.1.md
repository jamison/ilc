# ILC Public Wallet Surface Contract Spec 617 v0.1

Status: locked
Date: 2026-04-13
Phase: 617
Owner lane: G8 MVP gate spec lane

`public_wallet_surface_contract_spec_locked`

## 1. Wallet surface contract target and inherited boundary

Phase 617 locks the wallet/query touchpoint of the Phase 612 minimum
participant-touch package.

This packet specifies the public wallet query surface that already exists
inside the current bounded posture. It does not create new wallet surfaces, and
it does not widen the read-only wallet authority boundary locked by Phase 576
and Phase 581.

`wallet_surface_is_read_only_and_accounting_only`.
`wallet_query_anchors_to_phase_576_and_phase_581`.
`wallet_surface_does_not_widen_phase_576_boundary`.
`phase_617_carries_phase_612_mvp_gate_dependency`.
`wallet_query_is_fifth_of_five_mvp_touchpoints`.
`no_cdl_062_opening_in_wallet_surface_contract`.

The governing inputs are:
- Phase 576 wallet boundary as the primary authority
- Phase 581 settlement integration and wallet-query proof
- Phase 615 lifecycle contract for delayed ILC visibility
- ADR-0026 for the protocol-vs-harness product boundary

CDL-062 is not opened by this spec.

## 2. Permitted wallet query operations

The permitted wallet query operations are exactly:
- `wallet_status`: returns the participant's current settled ILC balance and
  ECU accrual state
- `wallet_history`: returns the participant's settled balance history by epoch
- `wallet_export`: returns a machine-legible export of the participant's
  current wallet state covering settled balances and accrual records
- `ledger_summary`: returns a summary of the settlement ledger state for the
  participant's epoch records

No other operations are permitted. Any operation not in this list is prohibited
without explicit authorization.

## 3. Wallet status and balance visibility contract

`wallet_status_exposes_settled_ilc_balance_only`.

`wallet_status` returns a JSON object with fields:
- `agent_id` (key-derived)
- `balance_ilc` (settled internal balance)
- `ecu_accrual` (current-epoch ECU accrual, advisory)
- `claimability_state` (string: `deferred`)

`balance_ilc` is the only balance class exposed. No additional balance, token,
claim, withdrawal, or transfer field may be added without explicit
authorization.

`claimability_state` must always be `deferred` in the current bounded posture.
It must not be omitted and must not be set to any value implying public
claimability.

## 4. Wallet history and attribution query contract

`wallet_history` returns an array of epoch settlement records. Each record must
include:
- `epoch_id`
- `settled_amount_ilc`
- `attribution_snapshot_ref`

`wallet_history` is read-only.

History records must be anchored to the same settled LMDB-backed state as
`wallet_status`. The wallet history surface may expose settled attribution
history, but it may not expose speculative pre-settle balances or any write
authority.

## 5. Wallet export and accounting contract

`wallet_export` returns a machine-legible JSON object containing:
- `agent_id`
- `export_epoch`
- `settled_balance_ilc`
- `history_digest` (a deterministic hash of the wallet history array)

The export is advisory and accounting only. It carries no transfer authority,
signing authority, withdrawal authority, or public claimability.

`ledger_summary` returns a bounded summary for the participant's ledger scope.
It is a read-only accounting/query surface and not an authorization surface.

## 6. Prohibited wallet operations

`wallet_write_spend_transfer_withdrawal_explicitly_prohibited`.

The following operations are explicitly prohibited:
- wallet write operations of any kind
- spend operations
- transfer operations
- withdrawal operations
- minting operations
- any operation that implies public claimability
- any operation that interacts with an external chain, blockchain, or rollup
- any wallet UX flow that silently widens the bounded accounting surface

This phase does not authorize blockchain wallet bridging, rollup interactions,
chain settlement, or any generalized wallet-signing interface.

## 7. Explicit exclusions and deferred items

The following items remain explicitly deferred:
- wallet create/import/export UX flows as a harness-layer concern under
  ADR-0026
- runtime implementation of the wallet query surface
- public claimability posture resolution, which remains blocked on the
  downstream settlement route and ADR-0028 conditions
- any reputation portability or cross-epoch balance transfer mechanism

This spec is bounded to read-only visibility and accounting only. It does not
widen wallet authority, settlement authority, or participant claim rights.
