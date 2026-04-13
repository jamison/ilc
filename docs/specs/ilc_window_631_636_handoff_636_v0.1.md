# ILC Window 631-636 Handoff 636 v0.1

Status: handoff artifact
Date: 2026-04-13
Classification: closure and carry-forward handoff
Phase: 636
Owner lane: G8 tier-0 economic numeric determinism strike force

## 1. Window identity and closure basis

Window 631-636 closes on the basis of:
- the Phase 631 sequence lock
- the Phase 634 `CDL-064` ratification evidence
- the Phase 635 Tier-0 runtime migration
- the Phase 636 hardening gate PASS
- this handoff and capsule update

`window_631_636_handoff_636_v0_1_closed`
`option_d_posture_active_after_636`

## 2. Inputs and inherited boundary state

Window 631-636 inherits and confirms:
- the Phase 609 ECU / ILC / bounded-runtime separation
- the Phase 576 and Phase 581 wallet boundary
- the Phase 612 two-form MVP gate rule
- ADR-0028 `Option D` active posture
- Window 624-630 as inherited bounded active-layer runtime context

This window consumed directly:
- `docs/specs/ilc_phase_631_636_sequence_lock_v0.1.md`
- `docs/specs/ilc_tier0_numeric_surface_inventory_and_risk_classification_632_v0.1.md`
- `docs/specs/ilc_cdl_064_exact_numeric_representation_prelock_633_v0.1.md`
- `docs/specs/ilc_sim_numeric_01_representation_evaluation_633_v0.1.md`
- `docs/specs/ilc_cdl_064_exact_numeric_representation_ratification_evidence_634_v0.1.md`
- `docs/specs/ilc_tier0_exact_numeric_runtime_migration_635_v0.1.md`
- `docs/specs/ilc_tier0_numeric_hardening_and_window_631_636_closure_636_v0.1.md`

## 3. Closure verdict summary

`CDL-064` ratified and consumed.
Tier-0 exact numeric runtime migration passed.
Tier-0 numeric hardening gate passed.

Active after this window:
- exact Tier-0 internal balances
- exact Tier-0 stake totals
- exact Tier-0 reward totals and settlement deltas
- canonical decimal-string serialization on the migrated Tier-0 machine surfaces

Still out of scope after this window:
- wallet widening
- generalized ECU transfer
- ILC transferability
- Option-B selection
- sovereign substrate selection

`cdl_064_runtime_migration_and_hardening_pass`
`tier0_exact_numeric_foundation_live`

## 4. Carry-forward items and residual blockers

Closed in this window:
- constitutional vehicle for exact numeric Tier-0 representation
- bounded Tier-0 runtime migration away from float-backed internal accounting
- hardening proof against replay/tolerance regression in the migrated set

Residual blockers or later-lane items:
- Window 623+ MVP runtime/interface closure
- broader public RC activation after both MVP forms close
- coupling-invariants governance lock
- privacy-preserving public legitimacy mechanism
- censorship-resistance and independence criteria for later Option-B graduation
- transport/discovery maturity
- broader non-Tier-0 float cleanup outside the bounded migrated set
- `CDL-053`, still deferred
- `CDL-062`, still not authorized

## 5. Next-window routing

Window 623+ may resume on the exact numeric Tier-0 foundation.

Routing after this handoff:
- the MVP touchpoints still require runtime/interface closure
- this window removes the Tier-0 numeric determinism blocker beneath that lane
- this window does not select Option B or advance wallet/payment authority
- `CDL-062` remains not authorized

`window_623_plus_may_resume_on_exact_numeric_tier0_foundation`

## 6. MemPalace refresh disposition

Disposition: required
Active working set impacted: yes
Basis: `CDL-064` ratified and consumed; capsule advanced to v3.5; Tier-0
runtime foundation and next-lane routing updated
Rebuild command: bash tools/mempalace/build_active_working_set.sh
