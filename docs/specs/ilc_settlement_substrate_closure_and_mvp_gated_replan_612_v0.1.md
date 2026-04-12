# ILC Settlement-Substrate Closure and MVP-Gated Replan 612 v0.1

Status: locked
Date: 2026-04-12
Phase: 612
Owner lane: G8 settlement substrate reconciliation

`phase_612_closes_window_607_612_without_reopening_substrate_selection`
`phase_612_uses_phase_611_memo_plus_adr_route_as_governing_input`

## 1. Closure target and inherited route

Window 607-612 is being closed on the basis of the actual Phase 611 memo-plus-ADR route. That route is the sole governing input for this closure memo. Phase 612
does not reopen the `Option A / B / C / D` evaluation that Phases 608-610
completed. Phase 612 does not revisit the Phase 611 governance vehicle choice.
This closure memo exists to synthesize the lane and route downstream work only.

The inherited route is:
- Phase 607 established the sequence lock and framed the reconciliation target,
- Phase 608 classified the historical lineage and authority tiers for all
  relevant source material,
- Phase 609 separated `ECU`, `ILC`, and the current RC/runtime posture without
  selecting a final substrate,
- Phase 610 evaluated the four substrate paths and kept `Option D` as the
  near-term posture while deferring `Option B` and `Option C` as later viable
  paths,
- Phase 611 selected the memo-plus-ADR governance vehicle and published
  `ADR-0028` as the durable carry-forward rule for the graduation checklist and
  blocker-routing contract.

No substrate option is re-evaluated here. No governance vehicle is re-selected
here. The Phase 611 memo and `ADR-0028` are the controlling governing inputs and
this phase consumes them.

## 2. Locked conclusions from Phases 607-611

The following conclusions are locked by this closure memo and may not be quietly
reopened in downstream work.

The current RC/runtime internal epoch-settled ledger posture remains bounded current truth rather than forever-substrate closure. It is a disciplined bridge
to a later explicit decision, not a permanent final substrate by implication.

`Option D` remains the active near-term posture. The deferred-substrate
ledger-interface architecture is the controlling design path until the
`Option B` graduation checklist is explicitly satisfied.

`Option B` remains the likely sovereign later path but is not yet selected.
`Option B` becomes selectable only through the published graduation checklist in
Phase 611 Section 5 and the rules in `ADR-0028`. Checklist completion is the
gate, not project momentum or design iteration.

The locked conclusion is that public auditability remains distinct from public identity exposure. These two
concerns may not be collapsed together in downstream planning, RC claims, or
public participant-facing work.

The locked criteria are that censorship-resistance and independence from external constitutional centers
remain live substrate criteria. They are named selection requirements for any
later sovereign public settlement substrate. They are not satisfied by the
current bounded posture and must be carried forward explicitly.

The Phase 609 ECU/ILC layer separation is locked. ECU is the local
protocol-internal productive-credit layer. ILC is the hard settlement asset. The
current runtime internal ledger is neither. These layers may not silently
recollapse in subsequent phases.

## 3. MVP gate and minimum participant-touch package

`minimum_participant_touch_package_is_required_before_broader_public_rc_claims`

The MVP gate requires the minimum participant-touch package to be closed in spec
and interface/runtime form before any broader public RC claims are made. The
minimum participant-touch package defines the smallest set of surfaces that allows
a real participant to enter and complete a bounded economic loop without requiring
final sovereign substrate selection.

The minimum participant-touch package includes exactly the following touchpoints:

**init/admission touchpoint**: a bounded public init and admission flow tied to
canonical receipts, derived from the boundary locks in Phases 587-589 and
`ADR-0027`.

**receipt issuance and query touchpoint**: a machine-legible public receipt
issuance and query surface. Receipt-bound legitimacy must be consolidated into a
published public machine contract before the MVP gate is considered satisfied.

**ECU visibility touchpoint**: a participant-visible `ECU` balance and
attribution surface. The conversion cadence and deadline are locked; the
participant-facing lifecycle contract must now be written end-to-end.

**delayed ILC visibility touchpoint**: a participant-accessible delayed `ILC`
visibility surface that is consistent with the current locked wallet boundary
from Phase 576 and Phase 581. This surface is read-only and may not carry write
or transfer authority in this window.

**wallet/query touchpoint**: a public wallet query surface, bounded to the
accounting and visibility semantics already locked in Phase 576 and Phase 581.
No wallet widening is authorized by this package.

This five-touchpoint package is sufficient for public learning without forcing immediate sovereign-chain implementation because every touchpoint is bounded to
the current read-only, receipt-anchored, and epoch-settled posture, which is
already implemented and does not require new substrate infrastructure to operate.

## 4. Downstream lane openings and sequencing

`downstream_replan_must_follow_mvp_gate_before_sovereign_substrate_execution`

Downstream work is sequenced by the MVP gate. No sovereign substrate execution
lane opens before the minimum participant-touch package is closed in both spec
and interface/runtime form.

**First post-612 spec lane**: public init/admission contract and visible
ECU-to-ILC lifecycle contract. Owner lane: economics/interface spec lane.
Dependency: Phase 612 handoff, Phases 576, 581, 587-589, `ADR-0027`, and
Phase 423 handoff. This lane is a blocker-class A item from the Phase 611
blocker matrix.

**First post-612 interface/runtime lane**: machine-legible public receipt schema
and query runtime, public wallet surface contract within the existing read-only
boundary, and transport/discovery operationalization packet. Owner lane:
receipt/runtime lane and wallet/harness lane. Dependency: first post-612 spec
lane outputs and Phase 611 route. These are blocker-class B items.

**Later public-legitimacy mechanism lane**: privacy-preserving public legitimacy
mechanism at the settlement layer. Owner lane: public legitimacy and settlement
lane. Dependency: Phase 611 route and later substrate decision. This lane is a
blocker-class C item and does not open until the first two post-612 lanes have
materially advanced. The rule is locked; the mechanism is not yet designed.

**Later sovereign substrate selection lane**: final selection of the sovereign
public settlement substrate for ILC. Owner lane: settlement substrate lane.
Dependency: completion of the `Option B` graduation checklist from Phase 611
Section 5 as governed by `ADR-0028`. This lane does not open and is not
authorized until the graduation checklist is explicitly satisfied and the human
authorizes the opening.

Downstream work must satisfy the MVP gate before sovereign substrate execution is
opened. This is a strict sequencing requirement and not advisory. Any phase that
attempts to open sovereign substrate execution before the MVP gate passes must be
rejected.

`option_b_remains_later_selectable_only_via_published_graduation_checklist`
`public_rc_package_coherence_does_not_require_immediate_option_b_selection`

Public RC package coherence is achievable under the current `Option D` posture.
Coherence in the RC package does not require `Option B` to be selected now.

`post_612_work_must_prioritize_receipts_lifecycle_wallet_touchpoints_and_init`

Post-612 work must prioritize the receipt, lifecycle, wallet touchpoints, and the
init/admission contract before opening new planning sub-lanes or widening
authority surfaces.

## 5. Explicit exclusions and unresolved later closures

`phase_612_does_not_open_new_sub_lanes_inside_the_closure_phase`

Phase 612 is a closure gate. It does not open new planning sub-lanes, governance
sub-lanes, or deliberation sub-lanes inside the phase.

The following exclusions are explicit and carry forward:

No final substrate ratification occurs in Phase 612. The public settlement
substrate for ILC remains unratified and the unresolved final-substrate posture
is preserved intentionally.

No wallet widening occurs in Phase 612. The wallet boundary from Phase 576 and
Phase 581 is the controlling boundary and is not expanded.

No payment runtime is implemented or authorized in Phase 612. Outbound and
inbound payment implementation work remain out of scope beyond this phase.

No chain implementation occurs in Phase 612. No L1, L2, or rollup work is
authorized or scoped.

No new planning sub-lanes are opened in Phase 612. The minimum participant-touch
package and downstream lane sequencing in this memo are the only planning outputs
of this phase.

Unresolved items that remain deliberately deferred beyond this window:

The privacy-preserving public legitimacy mechanism remains unresolved. The rule
is locked in Phase 611 and `ADR-0028` but the concrete mechanism awaits the
later public-legitimacy mechanism lane.

The sovereign substrate selection and the associated final constitutional
treatment remain deferred. The graduation checklist and the `ADR-0028` rules
govern when this item becomes unblocked.

The `CDL-062` opening remains unauthorized. It is not authorized by `ADR-0028`
or this closure memo. A future constitutional opening requires explicit human
authorization and prior satisfaction of the ADR-0028 conditions.

Coupling invariants between protocol truth, graph legitimacy, and settlement
backend choice remain a partial-state carry-forward item. A final governance lock
is still required in a later window.

## 6. Closure verdict and carry-forward handoff

Window 607-612 is closed. The settlement-substrate reconciliation lane is
complete.

Broader post-605 planning may resume under the following substrate assumptions:
the current RC/runtime posture is `Option D` bounded current truth, not
final-substrate closure; `Option B` is not selected; `CDL-062` is not open; no
wallet widening has been authorized; no payment runtime has been authorized; and
no chain implementation work is in scope. Planning that assumes any of these
conditions have changed may not proceed.

The Phase 611 graduation checklist in Phase 611 Section 5, carried forward and
governed by `ADR-0028`, remains the controlling gate for any later `Option B`
selection. No executive decision, accumulated momentum, or individual phase
output may substitute for the explicit satisfaction of that checklist plus
explicit human authorization.

The immediate carry-forward handoff for the RC lane is:
- resume the RC0.1 work at Phase 581 (ECU attribution, settlement, and wallet
  query integration) which was deferred for the Window 607-612 reconciliation
  lane,
- open the first post-612 spec lane for the public init/admission contract and
  the visible ECU-to-ILC lifecycle contract,
- do not open or widen any surface beyond the minimum participant-touch package
  until the MVP gate is satisfied.

The handoff assumptions for any later `Option B` selection are:
- the graduation checklist from Phase 611 Section 5 must be fully satisfied,
- the blocker matrix from Phase 611 Section 6 must be materially closed at the
  class-A and class-B levels,
- human explicit authorization and GO-token handling are required before any
  decision-log mutation related to sovereign substrate selection,
- `ADR-0028` Section 4 conditions must be demonstrated before a future
  `CDL-062` opening becomes admissible.
