# ILC Window 655-658 Candidate Phase Grouping v0.1

Status: candidate grouping
Date: 2026-04-14
Classification: bounded signing/export reproducibility maintenance lane
Owner lane: G8 signing/export reproducibility strike force

## 1. Window intent

Window 655-658 is a short bounded maintenance lane that follows Window 649-654.

Its purpose is to remove wall-clock and nondeterministic signing/export behavior
from the canon-export and canon-bundle key-registry surfaces before those
surfaces are relied on for production signing workflows.

This window is not a constitutional lane.
It does not reopen the coupling-invariants governance lock as the next
constitutional target. It simply prevents signing/export reproducibility debt
from leaking forward into later operator and substrate-facing work.

`window_655_658_candidate_grouping_present`
`window_655_658_is_bounded_signing_export_reproducibility_lane`
`window_655_658_non_constitutional_maintenance_lane`

## 2. Why this lane exists now

Post-649-654 security auditing identified a bounded but real class of remaining
issues:
- wall-clock timestamps embedded into signed manifest payloads
- wall-clock timestamps embedded into detached registry signature sidecars
- helper timestamp generators used by bundle/channel/promotion/sync flows
- operator-facing backup naming that should remain unique without contaminating
  signed state contracts

The objective is not to make every audit artifact reproducible.
The objective is to ensure that:
- signed payload identity is deterministic unless an explicit caller-provided
  timestamp contract says otherwise
- filename churn does not become part of signature or canonical-hash truth
- helper modules stop silently reintroducing `datetime.now(...)` into signed or
  canonicalized content

`signed_manifest_reproducibility_needed_before_operator_signing`
`registry_signature_sidecar_reproducibility_needed_before_production_signing`
`filename_uniqueness_must_not_pollute_signed_payload_identity`

## 3. Proposed phase map

Proposed four-phase shape:
- Phase 655: sequence lock for the bounded signing/export reproducibility lane
- Phase 656: canon-export manifest and detached-signature reproducibility fixes
- Phase 657: registry/channel/promotion/sync helper reproducibility fixes
- Phase 658: hardening gate, closure report, capsule update, and handoff

`phase_655_sequence_lock_for_signing_export_reproducibility`
`phase_656_manifest_and_signature_reproducibility_scope`
`phase_657_registry_channel_promotion_sync_reproducibility_scope`
`phase_658_hardening_and_closure_scope`

## 4. Scope boundaries

In scope:
- `ilc_core/ledger/canon_export_bundle_sign.py`
- `ilc_core/ledger/canon_bundle_key_registry.py`
- `ilc_core/ledger/canon_bundle_key_registry_bundle.py`
- `ilc_core/ledger/canon_bundle_key_registry_channel.py`
- `ilc_core/ledger/canon_bundle_key_registry_channel_signing.py`
- `ilc_core/ledger/canon_bundle_key_registry_promotion.py`
- `ilc_core/ledger/canon_bundle_key_registry_sync.py`
- narrowly related validation or helper tests required to prove the fixes

Out of scope:
- any decision-log mutation
- any ADR mutation
- coupling-invariants governance lock work
- `CDL-062`
- wallet/runtime/public-touchpoint widening
- broad audit/report timestamp cleanup outside the touched signing/export lane

`no_decision_log_or_adr_scope_in_window_655_658`
`no_coupling_invariants_governance_lock_execution_in_655_658`
`no_cdl_062_or_option_b_selection_in_655_658`

## 5. Intended closure standard

This window should close only if:
- signed export manifests no longer derive signed identity from local wall clock
- registry signature sidecars no longer require local wall clock for their
  signed metadata path
- helper modules touched in this lane use explicit caller-supplied timestamps or
  deterministic bounded fallbacks for signed/canonical content
- operator backup naming remains unique without altering signed state contracts
- targeted hardening tests and the final gate pass

`window_655_658_requires_signed_payload_time_determinism`
`window_655_658_requires_registry_signature_reproducibility`
`window_655_658_requires_helper_level_timestamp_discipline`

## 6. Routing after closure

If Window 655-658 closes successfully:
- the coupling-invariants governance lock remains the next constitutional target
- the signing/export surfaces stop carrying known wall-clock reproducibility debt
- later substrate or operator-signing work inherits a cleaner boundary

This window does not alter the broader post-654 roadmap beyond removing this
bounded maintenance blocker.

`coupling_invariants_lock_remains_next_constitutional_target_after_658`
