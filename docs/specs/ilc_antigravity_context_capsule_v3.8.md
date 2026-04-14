# ILC Antigravity Context Capsule v3.8

Supersedes: docs/specs/ilc_antigravity_context_capsule_v3.7.md
Date: 2026-04-14
Owner lane: G8 MVP runtime closure

This capsule is self-contained.

## 1. Current frontier state

Capsule v3.8 supersedes v3.7.
Window 613-619 remains closed as the MVP gate spec lane.
Window 624-630 remains closed as the bounded ECU active-layer lane.
Window 631-636 remains closed as the Tier-0 exact-numeric lane.
Window 637-641 remains closed as the bounded residual numeric cleanup lane.
Window 642-648 remains closed as the bounded security boundary lane.
Window 649-654 is now closed as the concrete runtime/interface closure of the
former Window 623+ lane.

The current frontier result is:
- rows 1-4 of the Phase 611 Option-B graduation checklist are now
  `runtime_closed`
- rows 5-9 remain open
- bounded public init/admission runtime is live
- bounded public receipt runtime is live
- bounded ECU/ILC lifecycle runtime is live
- bounded public wallet runtime is live
- `Option D` remains active
- coupling-invariants governance lock is now the next constitutional target

## 2. Frozen inherited boundary state

The following inherited boundaries remain frozen:
- Phase 576 and Phase 581 read-only wallet boundary
- Phase 587-589 receipt, identity, and settlement-linked legitimacy boundary
  stack
- Phase 609 ECU / ILC / bounded-runtime separation
- Phase 612 two-form MVP gate requirement
- ADR-0028 `Option D` bounded-bridge posture

Capsule v3.8 does not reopen sovereign substrate selection, public
claimability, wallet widening, or ILC transferability.

## 3. Window 649-654 runtime closure state

Window 649-654 is now fixed as:
- Phase 650 public init/admission runtime live
- Phase 651 public receipt issuance/query runtime live
- Phase 652 ECU/ILC lifecycle runtime live
- Phase 653 public wallet runtime integration live
- machine-legible checklist-state artifact published
- rows 1-4 now `runtime_closed`

This window does not claim that rows 5-9 are closed.

## 4. Remaining later-lane blockers

The surviving later-lane blockers now include:
- privacy-preserving public legitimacy mechanism
- coupling-invariants governance lock
- censorship-resistance for public legitimacy surfaces
- independence from external constitutional centers
- transport and discovery operational maturity
- sovereign substrate governance and later `CDL-062` work
- broader public RC activation that depends on rows 5-9

## 5. Next authorized continuation

The next constitutional target is the coupling-invariants governance lock.

Window 649-654 does not select Option B. It removes the runtime-form blocker
under rows 1-4 while preserving the later governance, privacy, independence,
and substrate blockers honestly.
