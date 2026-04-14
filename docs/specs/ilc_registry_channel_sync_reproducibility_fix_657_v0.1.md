# ILC Registry Channel Sync Reproducibility Fix 657 v0.1

Status: implemented
Date: 2026-04-14
Phase: 657
Window: 655-658

## 1. Remaining helper-level bug class

`registry_channel_helper_reproducibility_fixed_in_657`
`promotion_and_sync_timestamp_discipline_fixed_in_657`

Phase 657 closes the remaining helper-level wall-clock drift in:
- `ilc_core/ledger/canon_bundle_key_registry_bundle.py`
- `ilc_core/ledger/canon_bundle_key_registry_channel.py`
- `ilc_core/ledger/canon_bundle_key_registry_channel_signing.py`
- `ilc_core/ledger/canon_bundle_key_registry_promotion.py`
- `ilc_core/ledger/canon_bundle_key_registry_sync.py`

The remaining bug class after Phase 656 was helper-generated timestamp mutation
inside bundle manifests, channel state, channel signature sidecars, promotion
metadata, and sync bookkeeping records.

## 2. Deterministic and explicit timestamp contracts

Phase 657 adopts the bounded rule:
- identity-adjacent helpers accept explicit timestamps from the caller
- when explicit timestamps are absent, they derive timestamps deterministically
  from existing registry or channel state
- touched helper functions must not synthesize signed or canonical timestamp
  values from local wall clock

The concrete contracts are:
- `build_registry_bundle(...)` may accept explicit `created_at`; otherwise the
  bundle manifest falls back deterministically to detached registry
  `signed_at`, then registry `updated_at`, then `1970-01-01T00:00:00Z`
- `create_channel_file(...)` and `set_current_channel(...)` may accept explicit
  `updated_at`; otherwise they reuse existing deterministic state or fall back
  to `1970-01-01T00:00:00Z`
- `sign_channel_file(...)` may accept explicit `signed_at`; otherwise it falls
  back deterministically to channel `published_at`, then `updated_at`, then
  `1970-01-01T00:00:00Z`
- `promote_bundle(...)` may accept explicit `timestamp`; otherwise promotion
  metadata falls back deterministically to channel `updated_at`, then
  `1970-01-01T00:00:00Z`
- `SyncContext.metadata_timestamp` may supply explicit sync bookkeeping time;
  otherwise sync bookkeeping falls back deterministically to channel
  `published_at`, then `updated_at`, then `1970-01-01T00:00:00Z`

## 3. Diagnostic metadata versus signed identity

`diagnostic_metadata_separated_from_signed_identity_in_657`
`filename_uniqueness_preserved_without_signed_state_pollution`

Phase 657 keeps a hard separation between:
- signed or canonical identity surfaces such as bundle manifests, channel
  files, and detached channel signatures
- diagnostic bookkeeping sidecars such as `.last_sync.json` and local sync
  state files

The rule is:
- bookkeeping timestamps may exist for operator visibility
- those bookkeeping writes must remain outside channel signed identity
- no backup, sync, or bookkeeping uniqueness behavior may change the signed
  payload truth of registry bundles or channel signatures

## 4. Verification compatibility and preserved boundaries

Phase 657 preserves:
- strict ISO timestamp validation on touched helper contracts
- detached channel-signature verification compatibility
- bounded scope with no decision-log mutation, no ADR mutation, and no wider
  report/rendering timestamp cleanup outside the assigned helper lane

Phase 657 therefore closes the remaining helper-level reproducibility defects
inside the bounded signing/export maintenance window without reopening any
constitutional or Option-B scope.
