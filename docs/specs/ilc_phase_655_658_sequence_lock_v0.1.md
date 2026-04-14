# ILC Phase 655-658 Sequence Lock v0.1

Status: locked
Date: 2026-04-14
Phase: 655
Owner lane: G8 signing/export reproducibility strike force

## 1. Window identity and authorization basis

`window_655_658_sequence_lock_primary_gate`
`window_655_658_signing_export_reproducibility_lane_locked`
`window_655_658_non_constitutional_maintenance_lane`
`coupling_invariants_lock_remains_next_constitutional_target_after_655`
`no_cdl_062_or_option_b_selection_in_655_658`

Window 655-658 is a bounded post-654 maintenance lane for signing/export
reproducibility only.

Human direction 2026-04-14: after closing Window 649-654, the next immediate
maintenance detour should be a short bounded lane to remove wall-clock drift
from signing/export surfaces before later operator-signing and substrate-facing
work continues.

Window 655-658 is not a constitutional lane and does not displace the
coupling-invariants governance lock as the next constitutional target.

No decision-log opening, ADR opening, `CDL-062` opening, or `Option B`
selection is authorized here.

## 2. Bug-class map and target surfaces

The bug class in this window is:
- implicit local wall clock inside signed manifests
- implicit local wall clock inside detached registry signature sidecars
- helper-level timestamp generation inside touched bundle, channel, promotion,
  and sync paths
- uniqueness behavior that is valid for filenames or operator bookkeeping but
  must not pollute signed payload identity

The target surfaces are:
- `ilc_core/ledger/canon_export_bundle_sign.py`
- `ilc_core/ledger/canon_bundle_key_registry.py`
- `ilc_core/ledger/canon_bundle_key_registry_bundle.py`
- `ilc_core/ledger/canon_bundle_key_registry_channel.py`
- `ilc_core/ledger/canon_bundle_key_registry_channel_signing.py`
- `ilc_core/ledger/canon_bundle_key_registry_promotion.py`
- `ilc_core/ledger/canon_bundle_key_registry_sync.py`

## 3. Inherited boundary state

Window 649-654 remains closed.
Rows 1-4 are `runtime_closed`.
Rows 5-9 remain open.
`Option D` remains active.
The coupling-invariants governance lock remains the next constitutional target.

This window preserves:
- post-654 runtime/interface closure as already achieved
- the exact-numeric and non-finite rules already locked for runtime-critical
  numeric boundaries
- canonical compact JSON discipline on touched machine-consumed artifacts
- no wallet widening, no claimability widening, and no transferability opening

This window is maintenance only. It does not reopen public-runtime touchpoints
or claim broader Option-B readiness.

## 4. Per-phase scope constraints

Per-phase scope is fixed as:
- Phase 655: sequence lock only
- Phase 656: canon-export manifest and detached registry-signature
  reproducibility only
- Phase 657: registry/channel/promotion/sync helper reproducibility only
- Phase 658: hardening, closure, capsule, and handoff only

Each phase must remain within the signing/export lane and must not be used to
clean up unrelated diagnostic/report timestamp surfaces.

## 5. Deterministic signing/export rules

`signed_payload_timestamps_must_be_explicit_or_deterministic`
`diagnostic_timestamps_must_not_pollute_signed_identity`
`backup_filename_uniqueness_must_not_change_signed_payload_identity`

Every touched signing/export surface in this window must follow:
- signed payload timestamps must be explicit caller inputs or deterministic
  bounded fallbacks
- diagnostic timestamps may remain local only when they are excluded from signed
  or canonical identity
- canonical JSON for touched machine-consumed artifacts must remain
  sorted-key, compact-separator, `allow_nan=False` JSON
- backup filename uniqueness may remain operationally unique, but that
  uniqueness must not change signed payload identity or canonical digest truth

No phase in this window may silently rely on `datetime.now(...)`, `time.time()`,
or equivalent wall-clock generation inside touched signed/canonical payload
paths.

## 6. Routing and exclusions

`no_decision_log_or_adr_scope_in_window_655_658`

After this window:
- the signing/export reproducibility debt in the touched lane may be treated as
  closed if the hardening gate passes
- the coupling-invariants governance lock still remains the next constitutional
  target
- `Option D` remains active
- no `CDL-062` opening is authorized
- no `Option B` selection is authorized

Window 655-658 is therefore a bounded hardening detour, not a roadmap reset.
