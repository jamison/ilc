# ILC ECU-to-ILC Lifecycle Contract Spec 615 v0.1

Status: locked
Date: 2026-04-13
Phase: 615
Owner lane: G8 MVP gate spec lane

`ecu_to_ilc_lifecycle_contract_spec_615_locked`

## 1. ECU-to-ILC lifecycle touchpoint target

Phase 615 locks the visible ECU-to-ILC lifecycle touchpoint for Window 613-619.
This touchpoint covers participant-visible ECU balance and attribution surfaces
plus delayed participant-visible ILC balance surfaces after epoch commit.

The Phase 609 ECU/ILC layer separation is controlling. ECU is the local
protocol-internal productive-credit layer. ILC is the hard settlement asset.
The current runtime internal ledger is neither and these layers may not silently
recollapse in this spec.

`spec_form_closure_necessary_but_not_sufficient_for_mvp_gate`.
`interface_runtime_form_required_window_623_plus`.
`broader_public_rc_claims_remain_blocked_until_spec_and_runtime_both_complete`.

This Phase 615 packet is a spec-form artifact only. Interface/runtime form is deferred to Window 623+. Spec-form closure here is necessary but not sufficient for the full MVP gate. Broader public RC claims remain blocked until both spec and runtime forms complete.

## 2. Dependency and inherited canon

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_phase_613_619_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_613_619_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`
- `docs/specs/ilc_topological_exemption_boundary_and_public_tokenomics_statement_602_v0.1.md`
- `docs/specs/ilc_ecu_ilc_runtime_boundary_reconciliation_609_v0.1.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`

Inherited canon that remains binding in this spec:
- ECU is the local protocol-internal productive-credit layer and not the final
  public settlement asset
- ILC is the hard settlement asset while final public substrate remains
  unresolved
- wallet visibility remains read-only accounting only
- a visible settled balance does not imply public claimability, spend,
  transfer, or withdrawal semantics
- broader public RC claims remain blocked until the MVP gate closes in both
  spec and interface/runtime form

## 3. ECU layer boundary and attribution surface

`ecu_is_local_productive_credit_ilc_is_hard_settlement_asset`.
`ecu_ilc_layers_must_not_recollapse`.
`participant_visible_ecu_balance_is_read_only_visibility_only`.

ECU is the local protocol-internal productive-credit layer. It is an
attribution and accounting layer inside the bounded runtime posture, not a
publicly claimable settlement balance and not a shortcut to hard-settlement
closure.

The current bounded testnet attribution proxy remains anchored to the passive
ECU attribution rate from Phase 550:
- `rate = 0.20`
- `decay_floor = 0.05`
- `attribution_cap = 0.15`

Those values are testnet context only. They are not public-release law, and
this phase does not reopen them as a new governance target.

Participant-visible ECU balance is read-only accounting only. It carries no write authority, no transfer authority, no spend authority, and no generalized signing authority.

## 4. Epoch-commit and ILC settlement lifecycle

`ecu_accrual_reaches_ilc_balance_only_through_epoch_commit`.
`delayed_ilc_visibility_is_read_only_not_transfer_authority`.

ECU accrual reaches ILC balance only through epoch commit. The lifecycle is:
1. ECU accrual is recorded in the bounded productive-credit layer.
2. The bounded settlement path closes an epoch commit.
3. The settled internal balance is materialized on the authoritative settled
   runtime root.
4. Only after that settled epoch-commit path may delayed ILC visibility surface
   a `balance_ilc` value to participants.

The settled internal balance is the only ILC balance class exposed as
`balance_ilc`.

Deferred public-claimability state remains outside the current testnet scope.
Delayed visible ILC balance is read-only evidence of settled internal balance,
not transfer authority, not withdrawal authority, and not proof of public
claimability.

## 5. Participant-visible surfaces

Participant-visible surfaces are limited to read-only accounting and visibility
surfaces consistent with the Phase 576 and Phase 581 boundary.

ECU balance visibility:
- read-only
- accounting only
- no write, transfer, or spend authority

ILC balance visibility:
- read-only
- delayed until post-epoch-commit settlement
- consistent with the Phase 576 and Phase 581 read-only boundary

Visible fields must include stable equivalents for:
- `balance_ilc`
- `last_settled_epoch_id`
- `reward_status`
- `history_digest`
- `latest_balance_receipt`

No spend, transfer, withdrawal, or signing authority is exposed through the
participant-visible lifecycle surface.

## 6. Conversion cadence and deadline

`issuance_epoch_cadence_cdl_027_one_month`.

The issuance epoch cadence is one month under the locked CDL-027 rule.
The ECU-to-ILC conversion deadline is locked by CDL-027 and carried forward by
the Phase 612 MVP gate packet.

No amendment to the issuance cadence or the conversion deadline is authorized by
this spec. This packet consumes those bounds; it does not reopen them.

## 7. Forbidden interpretations and exclusions

`no_public_claimability_or_spend_in_lifecycle_spec`.
`wallet_boundary_phase_576_and_581_preserved`.

The following interpretations are forbidden:
- collapsing ECU and ILC into one undifferentiated layer
- treating participant-visible balance as public claimability
- any wallet widening beyond the read-only boundary from Phases 576 and 581
- any payment runtime or chain implementation reference as if authorized here
- reopening the ECU attribution rate as a governance target in this spec
- treating delayed ILC visibility as spend, transfer, withdrawal, or signing
  authority

This phase preserves the Phase 576 and Phase 581 wallet boundary exactly and
does not authorize any broader public balance semantics.

## 8. Explicit deferrals to later phases

The following items are explicitly deferred:
- interface/runtime implementation of the lifecycle packet to Window 623+
- public claimability semantics
- spend, transfer, withdrawal, or signing semantics
- payment runtime
- chain implementation
- any final public settlement substrate selection

Phase 615 closes only the spec-form lifecycle contract. It does not bypass the
Phase 612 and Phase 613 carry-forward rule that the MVP gate remains incomplete
until spec and interface/runtime forms are both closed.
