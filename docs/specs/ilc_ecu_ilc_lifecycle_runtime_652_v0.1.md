# ILC ECU/ILC Lifecycle Runtime 652 v0.1

Status: implemented
Date: 2026-04-14
Phase: 652
Owner lane: G8 MVP runtime closure

`ecu_ilc_lifecycle_runtime_652_live`

## 1. Runtime target and inherited lifecycle law

Phase 652 implements the bounded runtime/interface form of the Phase 615
ECU-to-ILC lifecycle contract.

Inherited lifecycle law remains controlling:
- ECU remains the bounded productive-credit visibility layer
- delayed visible ILC remains post-epoch-commit settled internal balance only
- Phase 609 ECU/ILC separation remains binding
- claimability remains deferred
- no spend, transfer, withdrawal, signing, or wallet-write authority is opened

## 2. Visible ECU runtime surface

`ecu_visibility_read_only_runtime_live`

The runtime exposes read-only visible ECU through
`GET /v1/public/lifecycle/{agent_id}`.

The response includes:
- `balance_ecu`
- `balance_ilc`
- `last_settled_epoch_id`
- `reward_status`
- `history_digest`
- `latest_balance_receipt`
- `claimability_state`

`balance_ecu` is read-only visibility sourced from the bounded ECU active-layer
runtime. It is not spend authority, not transfer authority, and not wallet
write authority.

## 3. Delayed visible ILC settlement runtime surface

`delayed_ilc_visibility_post_epoch_commit_runtime_live`

Delayed visible ILC remains absent until the bounded epoch-settled lifecycle
runtime applies an epoch commit.

Before epoch commit:
- `balance_ilc` remains `0`
- `last_settled_epoch_id` remains `null`
- `latest_balance_receipt` remains `null`

After epoch commit:
- `balance_ilc` becomes the settled internal balance
- `last_settled_epoch_id` records the commit epoch
- `latest_balance_receipt` records the commit receipt payload
- `history_digest` reflects the persisted balance-history state

The epoch commit helper uses exact-numeric canonical-string balance handling and
does not open public transferability, withdrawal, or claimability semantics.

## 4. Coupling-invariants diagnostic surface

`coupling_invariants_diagnostic_surface_present_in_652`
`coupling_diagnostic_is_read_only_and_not_governance_lock_claim`

The runtime exposes a bounded read-only diagnostic through
`GET /v1/public/lifecycle/coupling-invariants`.

The diagnostic makes visible:
- graph truth remains the upstream source
- ECU accounting remains downstream of graph truth
- delayed visible ILC remains downstream of ECU accounting and requires epoch
  commit
- `governance_lock_closed` remains `false`
- `diagnostic_only` remains `true`

This diagnostic is runtime evidence only. It is not a claim that the
coupling-invariants governance lock is already closed.

## 5. Exact-numeric, non-finite, and fail-closed discipline

`exact_numeric_and_non_finite_rules_apply_to_lifecycle_runtime`

The lifecycle runtime preserves:
- exact-numeric parsing for any touched balance delta
- canonical string rendering for visible balance fields
- non-finite rejection on lifecycle commit inputs
- canonical compact JSON with `allow_nan=False` for persisted machine payloads

`claimability_state_remains_deferred_in_652`

`claimability_state` remains `deferred` throughout the runtime surface.

## 6. Explicit exclusions and preserved boundaries

`no_spend_transfer_withdrawal_or_wallet_write_in_652`

Phase 652 preserves these exclusions:
- no wallet write authority
- no spend authority
- no transfer authority
- no withdrawal authority
- no public claimability widening
- no generalized ECU transfer
- no ILC transferability
- no constitutional mutation

The lifecycle runtime is therefore limited to bounded visibility, epoch-settled
internal balance materialization, and read-only coupling diagnostics.
