# ILC Window 655-658 Handoff 658 v0.1

Status: handoff artifact
Date: 2026-04-14
Classification: closure and carry-forward handoff
Phase: 658
Owner lane: G8 signing/export reproducibility strike force

## 1. Window identity and closure basis

Window 655-658 closes on the basis of:
- the Phase 655 sequence lock
- the Phase 656 canon-export and registry-signature reproducibility fix
- the Phase 657 helper-level registry/channel/promotion/sync reproducibility fix
- the Phase 658 signing/export gate PASS
- this handoff and the capsule v3.9 update

`window_655_658_handoff_658_closed`
`window_655_658_signing_export_lane_status_pass`
`signed_manifest_and_registry_signature_reproducibility_closed_after_658`
`helper_level_registry_channel_sync_reproducibility_closed_after_658`
`option_d_posture_still_active_after_658`
`no_option_b_or_cdl_062_selection_in_658`

## 2. Signing/export reproducibility closure summary

The bounded signing/export maintenance lane is now closed in the scope it
promised.

Closed in this window:
- signed canon-export manifest metadata no longer depends on implicit local wall
  clock
- detached registry signature sidecars no longer depend on implicit local wall
  clock
- bundle/channel/promotion/sync helper metadata now uses explicit input or
  deterministic fallback where identity-adjacent behavior is involved
- sync bookkeeping remains clearly separated from channel signed identity

## 3. What this window fixed

This window fixed the specific bug class of implicit wall-clock signed-identity
drift on the touched signing/export lane.

The touched lane now has:
- explicit timestamp input where callers need control
- deterministic fallback from existing registry or channel state where callers
  do not provide timestamps
- canonical JSON discipline preserved on the touched machine-consumed signing
  artifacts
- no known remaining `datetime.now(...)` or `time.time()` usage in the touched
  lane files

## 4. What this window did not claim

This window did not claim:
- closure of Phase 611 rows 5-9
- broader substrate readiness
- `CDL-062` opening
- Option-B selection
- any new constitutional vehicle

Window 655-658 is maintenance only. It closes a bounded reproducibility debt
without altering the broader post-654 constitutional frontier.

## 5. Routing after closure

`coupling_invariants_lock_remains_next_constitutional_target_after_658`

Routing after this window:
- Window 649-654 remains the concrete runtime/interface closure of the former
  Window 623+ lane
- rows 1-4 remain `runtime_closed`
- rows 5-9 remain open
- `Option D` remains active
- the coupling-invariants governance lock remains the next constitutional
  target
- no `CDL-062` opening is authorized here
- no Option-B selection is authorized here

## 6. MemPalace refresh disposition

Disposition: required
Active working set impacted: yes
Basis: capsule advanced to v3.9; Window 655-658 closed; the bounded
signing/export maintenance state is now carry-forward complete beneath the
post-654 frontier; the next constitutional target remains the
coupling-invariants governance lock
Rebuild command: bash tools/mempalace/build_active_working_set.sh
