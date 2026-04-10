# ILC Settlement-Substrate Governance Vehicle Selection 611 v0.1

Status: locked
Date: 2026-04-11
Phase: 611
Owner lane: G8 settlement substrate reconciliation

## 1. Decision target and inherited state

Phase 611 chooses the governance vehicle that is sufficient to preserve the
Phase 607 through Phase 610 reconciliation results without ratifying the final
public settlement substrate.

`phase_611_selects_governance_vehicle_without_ratifying_final_substrate`.

Inherited state at Phase 611 entry is:
- Phases 607 through 610 are complete and this phase consumes their outputs
  rather than reopening them,
- `Option D` remains the kept near-term posture from Phase 610,
- `Option B` remains a legitimate later sovereign path but is not selected or
  ratified here,
- `Option C` remains deferred and dependency-heavy, not selected,
- this phase chooses a governance vehicle only and does not pick the final
  substrate.

## 2. Design lemma and prohibited failure modes

`design_lemma_local_graph_work_fast_settlement_hard_to_fake`.

Design lemma:
- local intelligence and graph work should be cheap, fast, and abundant,
- canonical legitimacy and settlement should be scarce, auditable, and hard to
  fake.

`waterfall_overbuild_and_protocol_first_paralysis_are_both_prohibited`.

The two prohibited failure modes are:
- waterfall overbuild, where the project delays all public learning until an
  oversized final package is attempted,
- protocol-first paralysis, where the project keeps extending design closure
  without opening a real participant-touch economic loop.

`phase_611_treats_censorship_resistance_as_named_substrate_constraint`.

Censorship-resistance and resistance to centralized memory/context rewriting are
named design constraints for future substrate choice.

Public auditability remains distinct from public identity exposure.

## 3. Governance vehicle options and decision rule

`default_route_must_be_lowest_authority_vehicle_sufficient_for_the_required_lock`.

Phase 611 evaluates three routes:
- memo-only,
- memo plus ADR,
- conditional CDL opening stub.

Decision rule:
- select the lowest-authority vehicle sufficient to lock the required rule set,
- do not open a CDL merely to preserve optionality,
- do not select a weaker vehicle if it cannot carry the graduation checklist,
  blocker routing, and failure-mode prohibitions forward reliably.

Route observations:
- memo-only is the lightest route but is too weak for a durable carry-forward
  rule on graduation criteria and blocker ownership,
- memo plus ADR is strong enough to preserve the design lemma, the graduation
  checklist, and the blocker-routing contract without constitutional mutation,
- conditional CDL opening remains available only if a constitutional boundary
  must be opened now, which Phase 610 did not establish.

## 4. Selected route and justification

`scenario_a_requires_no_decision_log_mutation`.

Selected route for Phase 611: memo plus ADR.

`selected_route_memo_plus_adr_is_sufficient_now`.

This route is sufficient now because:
- it locks the graduation rule and blocker-routing posture in a durable
  architectural form,
- it is stronger than memo-only for future execution windows,
- it still avoids constitutional mutation while the final substrate remains
  unratified.

Rejected routes:
- memo-only is unnecessary now because it is too soft to prevent `Option D`
  from drifting into inertia,
- conditional CDL opening is unnecessary now because memo and ADR are not both exhausted and no constitutional boundary requires opening in this window.

Censorship-resistance and independence from external constitutional centers push
this phase away from a dependency-light memo-only route and also do not yet
justify a constitutional opening. They support preserving a stronger sovereign
future direction without prematurely invoking `CDL-062`.

`scenario_b_requires_go_token_and_precommit_authorization`.

Scenario B remains conditional only. If it is ever selected later, it requires
explicit human authorization, GO-token handling, and precommit authorization
before any decision-log mutation.

## 5. Option-B graduation checklist

`option_b_graduation_requires_explicit_checklist_not_inertia`.

`Option B` may become selectable only after the following checklist is met. The
checklist is not discussion-only; it is a graduation gate.

| Criterion | Current state | Notes |
|---|---|---|
| public init/admission flow tied to canonical receipts | `partial` | Boundary rules exist in Phases 587-589 and ADR-0027, but the integrated public flow contract is not yet published |
| machine-legible public receipt issuance and query/runtime contract | `not_started` | Receipt-bound legitimacy exists conceptually but not yet as a consolidated public machine surface |
| user and agent visible `ECU` to `ILC` lifecycle contract | `partial` | Epoch cadence and conversion deadline exist, but the public lifecycle contract is not yet written end-to-end |
| public wallet surface contract sufficient for a first participant-touch economic loop | `partial` | Read-only wallet/accounting exists, but participant-touch public wallet semantics are not yet closed |
| privacy-preserving public legitimacy mechanism at the settlement layer | `not_started` | Rule is locked; mechanism remains unresolved |
| coupling invariants that keep protocol truth and graph legitimacy upstream of settlement backend choice | `partial` | High-value coupling surfaces exist in the coupling memo, but a final governance lock is still needed |
| censorship-resistance requirement for public legitimacy surfaces | `partial` | Named here as a criterion, but not yet implemented as a concrete public-settlement mechanism |
| independence from external constitutional centers as a future-substrate selection criterion | `partial` | Direction is strong, but future selection rules are not yet closed |
| transport and discovery operational maturity threshold for public participant use | `partial` | Transport direction is locked, but broader public operational maturity is not yet achieved |

Checklist labels used in this packet are `closed`, `partial`, and `not_started`.

## 6. Blocker matrix, owner lanes, and earliest phases

`blocker_matrix_assigns_owner_lane_required_artifact_dependency_and_earliest_phase`.

Blocker classes are:
- `A = closable now with governance/spec work`
- `B = follow-on interface or runtime work after governance selection`
- `C = dependent on prior closure, later substrate choice, or later public-legitimacy mechanism work`

| blocker | class | why blocked now | owner lane | required artifact | dependency | earliest phase |
|---|---|---|---|---|---|---|
| governance vehicle for D -> B graduation | `A` | Phase 610 kept `Option D` but did not choose the vehicle that governs later graduation | G8 governance | Phase 611 governance memo + ADR-0028 | Phase 610 matrix | Phase 611 |
| public init/admission flow contract | `A` | boundary locks exist but no integrated public init/admission contract exists | public legitimacy spec lane | public init/admission contract memo | Phases 587-589, ADR-0027 | Phase 612 handoff into first post-612 spec window |
| machine-legible public receipt runtime | `B` | legitimacy is receipt-bound in principle but no consolidated public receipt schema/query runtime exists | receipt/runtime lane | public receipt schema and query contract | Phase 611 route + Phase 612 MVP gate | first post-612 interface/runtime window |
| visible ECU -> ILC lifecycle contract | `A` | conversion cadence exists but participant-visible lifecycle semantics are not unified | economics/interface spec lane | ECU/ILC lifecycle contract | Phase 423 handoff, Phases 576/581 | Phase 612 handoff into first post-612 spec window |
| public wallet surface beyond read-only accounting | `B` | wallet remains intentionally narrow and cannot widen before governance-selected routing | wallet/harness lane | public wallet surface contract | Phase 611 route + lifecycle contract | first post-612 wallet/interface window |
| transport and discovery operational maturity | `B` | transport direction exists but public operational maturity and discovery remain incomplete | D2d transport lane | transport/discovery operationalization packet | ADR-0025 and later RC operations work | first post-612 runtime/ops window |
| privacy-preserving public legitimacy mechanism | `C` | rule is locked but final mechanism depends on later public settlement architecture | public legitimacy + settlement lane | privacy-preserving legitimacy design packet | Phase 611 route + later substrate decision | later public-legitimacy mechanism window |
| sovereign substrate selection and execution | `C` | future substrate cannot be selected before the graduation checklist closes | settlement substrate lane | later sovereign substrate selection packet | completion of Option-B graduation checklist | later substrate-selection window |

## 7. Carry-forward constraints into Phase 612

`phase_612_must_be_mvp_gated_and_may_not_open_new_sub_lanes`.

Phase 612 must be MVP-gated and may not open new sub-lanes.

Phase 612 must define the minimum participant-touch package rather than a broad
speculative roadmap.

That minimum participant-touch package must name, at minimum:
- init/admission,
- receipt issuance/query,
- ECU visibility,
- delayed ILC visibility,
- wallet/query touchpoints.

No implementation, wallet widening, payment runtime, or final substrate
ratification is authorized by Phase 611.

Because the selected route is memo plus ADR, Phase 612 must carry forward the
ADR-governed graduation rule and blocker matrix without opening `CDL-062` in
this window.
