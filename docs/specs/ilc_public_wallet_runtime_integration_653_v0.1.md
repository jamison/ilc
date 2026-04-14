# ILC Public Wallet Runtime Integration 653 v0.1

Status: implemented
Date: 2026-04-14
Phase: 653
Owner lane: G8 MVP runtime closure

`public_wallet_runtime_653_live`

## 1. Runtime target and inherited wallet boundary

Phase 653 implements the bounded runtime/interface form of the Phase 617
public wallet surface contract.

Inherited wallet law remains controlling:
- wallet visibility remains read-only and accounting only
- the Phase 576 and Phase 581 wallet/query boundary remains binding
- delayed visible ILC remains settled internal balance only
- visible ECU remains advisory accounting visibility only
- `claimability_state` remains `deferred`
- no write, spend, transfer, withdrawal, minting, or signing authority is
  opened

## 2. Live wallet query operations

`wallet_status_history_export_ledger_summary_live`
`wallet_surface_read_only_and_accounting_only_in_runtime`

The runtime exposes exactly four live read-only operations:
- `GET /v1/public/wallet/{agent_id}/status`
- `GET /v1/public/wallet/{agent_id}/history`
- `GET /v1/public/wallet/{agent_id}/export`
- `GET /v1/public/wallet/{agent_id}/ledger-summary`

`wallet_status` returns:
- `agent_id`
- `balance_ilc`
- `ecu_accrual`
- `claimability_state`
- `last_settled_epoch_id`
- `history_digest`
- `latest_balance_receipt`
- `latest_balance_receipt_ref`
- `settled_runtime_root_ref`

`wallet_history` returns a read-only array of settled epoch records. Each record
includes:
- `epoch_id`
- `settled_amount_ilc`
- `attribution_snapshot_ref`

`wallet_export` returns a machine-legible accounting export for one agent and
includes:
- `agent_id`
- `export_epoch`
- `settled_balance_ilc`
- `ecu_accrual`
- `history_digest`
- `latest_balance_receipt_ref`
- `settled_runtime_root_ref`

`ledger_summary` returns a bounded participant-scoped settlement summary and
includes:
- `agent_id`
- `settled_balance_ilc`
- `reward_total_ilc`
- `epoch_record_count`
- `latest_epoch_id`
- `history_digest`
- `latest_balance_receipt_ref`
- `settled_runtime_root_ref`

## 3. Settled-root linkage and receipt-backed accounting visibility

`wallet_history_and_export_bind_to_settled_runtime_root`

The four wallet operations bind visibility to the settled runtime root and not
to speculative operator state.

The runtime therefore exposes:
- `settled_runtime_root_ref` as a deterministic hash-derived reference to the
  LMDB-backed wallet runtime root
- `latest_balance_receipt_ref` as a deterministic hash-derived reference to the
  latest settled balance receipt payload when such a receipt exists
- `history_digest` as the durable balance-history digest carried by the settled
  wallet row and wallet history state

History and export payloads are derived from the same settled LMDB-backed
wallet row and wallet history structures that Phase 652 updates at epoch
commit. They do not read projection-only helper state and they do not infer
wallet truth from operator-local process memory.

## 4. Failure-token and read-only enforcement discipline

The wallet runtime remains GET-only and fail-closed.

Machine-token failure discipline includes:
- `wallet_agent_id_required`
- `wallet_history_invalid`

Invalid or structurally corrupted wallet history is rejected rather than
silently projected into a speculative export.

`claimability_state_deferred_in_wallet_runtime`

`claimability_state` remains `deferred` in all four wallet operations.

## 5. Explicit exclusions and preserved boundaries

`no_wallet_write_spend_transfer_withdrawal_in_653`

Phase 653 preserves these exclusions:
- no wallet write authority
- no spend authority
- no transfer authority
- no withdrawal authority
- no minting authority
- no public claimability widening
- no external chain, blockchain, or rollup interaction
- no constitutional mutation

The public wallet runtime therefore remains a bounded read-only accounting and
visibility surface only.
