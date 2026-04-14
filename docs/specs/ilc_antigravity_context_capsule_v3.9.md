# ILC Antigravity Context Capsule v3.9

Supersedes: docs/specs/ilc_antigravity_context_capsule_v3.8.md
Date: 2026-04-14
Owner lane: G8 signing/export reproducibility closure

This capsule is self-contained.

## 1. Current frontier state

Capsule v3.9 supersedes v3.8.
Window 613-619 remains closed as the MVP gate spec lane.
Window 624-630 remains closed as the bounded ECU active-layer lane.
Window 631-636 remains closed as the Tier-0 exact-numeric lane.
Window 637-641 remains closed as the bounded residual numeric cleanup lane.
Window 642-648 remains closed as the bounded security boundary lane.
Window 649-654 remains closed as the concrete runtime/interface closure of the
former Window 623+ lane.
Window 655-658 is now closed as a bounded post-654 signing/export maintenance
closure.

The current frontier result is:
- rows 1-4 of the Phase 611 Option-B graduation checklist remain
  `runtime_closed`
- rows 5-9 remain open
- `Option D` remains active
- the touched signing/export lane no longer carries known implicit wall-clock
  signed-identity drift
- coupling-invariants governance lock remains the next constitutional target

## 2. Frozen inherited boundary state

The following inherited boundaries remain frozen:
- Phase 576 and Phase 581 read-only wallet boundary
- Phase 587-589 receipt, identity, and settlement-linked legitimacy boundary
  stack
- Phase 609 ECU / ILC / bounded-runtime separation
- Phase 612 two-form MVP gate requirement
- ADR-0028 `Option D` bounded-bridge posture

Capsule v3.9 does not reopen sovereign substrate selection, public
claimability, wallet widening, or ILC transferability.

## 3. Window 655-658 maintenance closure state

Window 655-658 is now fixed as:
- Phase 655 sequence lock complete
- Phase 656 signed manifest and detached registry signature reproducibility
  complete
- Phase 657 helper-level registry/channel/promotion/sync reproducibility
  complete
- Phase 658 hardening gate and closure complete

This window closes known implicit wall-clock signed-identity drift on the
touched signing/export lane. It does not alter the Phase 611 checklist state
beyond preserving rows 1-4 as already `runtime_closed`.

## 4. Remaining later-lane blockers

The surviving later-lane blockers still include:
- privacy-preserving public legitimacy mechanism
- coupling-invariants governance lock
- censorship-resistance for public legitimacy surfaces
- independence from external constitutional centers
- transport and discovery operational maturity
- sovereign substrate governance and later `CDL-062` work
- broader public RC activation that depends on rows 5-9

## 5. Next authorized continuation

The next constitutional target remains the coupling-invariants governance lock.

Window 655-658 was a maintenance detour that removed a bounded signing/export
reproducibility blocker. It did not select Option B, did not close rows 5-9,
and did not change the post-654 constitutional routing.
