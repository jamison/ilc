# ILC Window 642-648 Handoff 648 v0.1

Status: handoff artifact
Date: 2026-04-14
Classification: closure and carry-forward handoff
Phase: 648
Owner lane: G8 security boundary and remaining-float strike force

## 1. Window identity and closure basis

Window 642-648 closes on the basis of:
- the Phase 642 sequence lock
- the Phase 643 remaining-float and security follow-on inventory
- the Phase 644 canonical JSON and signature boundary hardening
- the Phase 645 PRNG, timeout, and invariant enforcement hardening
- the Phase 646 NDJSON ingress and operational boundary hardening
- the Phase 647 security hardening gate PASS
- this handoff and capsule update

`window_642_648_handoff_648_closed`
`window_642_648_closed_without_new_constitutional_vehicle`
`option_d_posture_active_after_648`

## 2. Security issue summary

The bounded live security boundary issues touched in this window are closed to
the extent promised by Window 642-648.

Closed in this window:
- canonical JSON/signature drift on the touched bundle, report, and CLI
  surfaces
- compact canonical JSON enforcement on the touched machine-verifiable and
  machine-consumed JSON paths
- non-finite JSON numeric ingress rejection on the touched canonical export and
  bundle paths
- predictable PRNG usage on the touched runtime/security-sensitive selection
  paths
- flat timeout defaults on the touched HTTP wrappers
- production invariant enforcement via `assert` on the touched passive ECU
  runtime
- unbounded NDJSON bundle aggregation on the touched ingress path
- broad exception swallowing on the touched hardened boundaries

`live_security_boundary_issues_touched_in_642_648_closed`

## 3. Fix-induced regression summary

The window also checked the expected second-order regressions rather than
assuming the first-order fixes were automatically safe.

Verified in Phase 647:
- canonical JSON fixes did not leave whitespace or separator drift on the
  touched canonical bytes path
- deterministic selection fixes did not simply replace predictable PRNG with a
  new entropy-heavy runtime dependency
- explicit invariant enforcement fixes did not introduce new broad exception swallowing
  on the touched boundaries
- bounded NDJSON ingress did not shift the attack from RAM to temporary-disk spooling
- the hardening gate itself was corrected after a real recursive self-invocation
  bug was found during execution

## 4. Remaining-float carry-forward state

Window 642-648 does not claim repo-wide numeric or security closure.

Still active after this handoff:
- `docs/specs/ilc_remaining_float_and_security_follow_on_inventory_643_v0.1.md`
  remains the authoritative remaining-float and bounded security carry-forward
  inventory
- `TODO.txt` still contains the top-level Post-641 remaining-float/security
  follow-on block
- shared/public contract float cleanup remains open in later lanes
- runtime-adjacent protocol and consensus float cleanup remains open in later
  lanes
- lower-tier sim, analysis, and devnet float cleanup remains open in later
  lanes
- any future runtime/public numeric surface still requires exact-numeric and
  non-finite ingress review before activation

`remaining_float_follow_on_inventory_persists_after_648`

## 5. Routing after closure

Routing after this window:
- Window 642-648 is a bounded security boundary lane, not a new constitutional
  vehicle
- Window 623+ remains the broader runtime/interface priority after this window
- this lane does not select Option B
- this lane does not widen wallet authority
- this lane does not authorize ILC transferability
- this lane does not reopen sovereign substrate selection

`window_623_plus_priority_preserved_after_648`

## 6. MemPalace refresh disposition

Disposition: required
Active working set impacted: yes
Basis: capsule advanced to v3.7; Window 642-648 closed; remaining-float and
security carry-forward routing updated beneath the resumed broader runtime
roadmap
Rebuild command: bash tools/mempalace/build_active_working_set.sh
