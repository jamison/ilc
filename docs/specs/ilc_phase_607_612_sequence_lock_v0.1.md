# ILC Phase 607-612 Sequence Lock v0.1

Status: locked
Date: 2026-04-10
Phase: 607
Owner lane: G8 settlement substrate reconciliation

## 1. Window summary

Window 607-612 is the dedicated settlement-substrate reconciliation lane that
opens after the MemPalace enablement and pre-607 reconciliation groundwork.

It is not a generic continuation of post-605 work. It exists to reconcile the
current RC/runtime internal-ledger posture, the December 2025 off-chain-first /
later-chain historical direction, the ECU/ILC layer distinction, and the public
claims boundary before any broader payment, wallet-authority, or public-RC
planning continues.

Required lock tokens:
- `window_607_612_settlement_substrate_reconciliation_primary_gate`
- `current_rc_runtime_internal_epoch_settled_ledger_is_not_final_substrate_by_implication`
- `december_2025_off_chain_first_later_chain_direction_must_be_reconciled_against_current_authority`
- `ecu_and_ilc_layers_must_be_separated_before_public_settlement_claims`
- `public_auditability_and_identity_privacy_must_be_designed_together`
- `wallet_agnostic_signing_does_not_settle_final_token_substrate`
- `no_payment_lane_progress_before_settlement_substrate_issue_framing`
- `broader_window_607_615_is_superseded_pending_reconciliation_first_lane`
- `current_capsule_language_must_not_overgeneralize_rc_runtime_posture`
- `historical_chain_backed_settlement_option_must_be_classified_not_assumed`
- `no_wallet_authority_widening_inside_reconciliation_window`
- `phase_607_sequence_lock_sets_reconciliation_before_expansion`

## 2. Hard pass condition

Window 607-612 only passes if all of the following are true:
1. The current RC/runtime internal-ledger posture is described explicitly
   without treating it as the final long-run substrate by implication.
2. The December 2025 off-chain-first / later-chain direction is inventoried and
   authority-classified explicitly.
3. `ECU` and `ILC` are separated architecturally before public settlement
   claims are made.
4. Public auditability and public identity exposure are treated as distinct
   design questions.
5. Broader payment, wallet, and public RC planning remain blocked until this
   reconciliation lane closes.

`window_607_612_settlement_substrate_reconciliation_primary_gate`.
`current_rc_runtime_internal_epoch_settled_ledger_is_not_final_substrate_by_implication`.
`december_2025_off_chain_first_later_chain_direction_must_be_reconciled_against_current_authority`.
`ecu_and_ilc_layers_must_be_separated_before_public_settlement_claims`.
`public_auditability_and_identity_privacy_must_be_designed_together`.
`no_payment_lane_progress_before_settlement_substrate_issue_framing`.
`phase_607_sequence_lock_sets_reconciliation_before_expansion`.

## 3. Mandatory dependency bundle

Every Phase 607-612 artifact must carry the mandatory dependency bundle from
`docs/specs/ilc_window_607_612_candidate_phase_grouping_v0.1.md`.

Binding references for the window:
- `docs/specs/ilc_window_607_612_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_window_607_615_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_window_596_605_handoff_605_v0.1.md`
- `docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.4.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.5.md`
- `docs/specs/ilc_antigravity_context_capsule_v3.2.md`
- `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`
- `docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md`
- `docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md`
- `docs/specs/ilc_topological_exemption_boundary_and_public_tokenomics_statement_602_v0.1.md`
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`
- `docs/specs/ilc_agent_sdk_boundary_contract_draft_v0.1.md`
- `docs/specs/ilc_claude_extraction_brief_v0.1.md`
- `docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `whitepaper/2025_12_03_ILC_whitepaper_v5_2.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Minimum decision-log cluster for the window:
- `CDL-001`
- `CDL-003`
- `CDL-004`
- `CDL-013`
- `CDL-022`
- `CDL-023`
- `CDL-026`
- `CDL-027`
- `CDL-028`
- `CDL-029`
- `CDL-030`
- `CDL-031`
- `CDL-045`
- `CDL-V6`

Supporting context may inform this window only when it is explicitly labeled as
historical strategy, historical drift-carrier language, bounded current public
claims, or design input. No supporting-context source is equal canon with the
ratified CDL surface or accepted architectural boundary surfaces by silence.

## 4. Pre-lock blockers

The following blockers are mandatory before any settlement-substrate
reconciliation execution lock may pass:
- the 585-595 public and bounded-RC boundaries remain frozen inherited law
- the read-only wallet/query posture remains frozen inherited law
- the broader 607-615 continuation draft is superseded pending this narrower
  lane
- no historical whitepaper or chat material may be treated as current canon by
  silence
- the wording inconsistency in
  `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`
  (`The ILC coin (ECU) is protocol-native.`) must be flagged as unresolved and
  routed to Phase 609 rather than inherited as stable authority
- the older capsule phrase `ILC is NOT a blockchain` must be treated as
  historical drift-carrier language requiring explicit classification rather
  than inherited long-run substrate closure
- no payment lane, wallet authority, or public RC planning may advance inside
  this window
- public auditability must be distinguished from public identity exposure

`broader_window_607_615_is_superseded_pending_reconciliation_first_lane`.
`no_payment_lane_progress_before_settlement_substrate_issue_framing`.
`no_wallet_authority_widening_inside_reconciliation_window`.
`wallet_agnostic_signing_does_not_settle_final_token_substrate`.

## 5. Phase table

| Phase | Description | Primary output | Sensitive? |
|---|---|---|---|
| 607 | Window 607-612 sequence lock and issue framing | `ilc_phase_607_612_sequence_lock_v0.1.md` | No |
| 608 | Historical lineage and authority audit | historical lineage audit artifact | No |
| 609 | ECU / ILC / runtime-boundary reconciliation | reconciliation memo | No |
| 610 | Public-ledger substrate options and rejection matrix | substrate options matrix | No |
| 611 | Governance vehicle selection and prelock | governance vehicle selection artifact | **conditional** |
| 612 | Closure synthesis and downstream replan | closure handoff + downstream replan | YES |

## 6. Locked implementation decisions

The following decisions are locked for the full settlement-substrate
reconciliation window:
- Window 607-612 is a settlement-substrate reconciliation lane, not a generic
  continuation window.
- current RC/runtime implementation is an internal epoch-settled ledger with
  read-only wallet/query surfaces.
- that current posture does not settle the forever substrate for `ILC` by
  implication.
- the December 2025 off-chain-first / later-chain direction remains legitimate
  historical design lineage that must be reconciled explicitly.
- wallet-agnostic signing is about signing keys and provider compatibility, not
  token substrate or transfer authority.
- `ECU` and `ILC` must be treated as distinct layers in this reconciliation.
- no broader 607+ implementation planning resumes until this window closes.
- the Phase 610 options matrix must classify each substrate option with an
  explicit keep/defer/reject rationale rather than a presence-only listing.

`current_rc_runtime_internal_epoch_settled_ledger_is_not_final_substrate_by_implication`.
`december_2025_off_chain_first_later_chain_direction_must_be_reconciled_against_current_authority`.
`ecu_and_ilc_layers_must_be_separated_before_public_settlement_claims`.
`public_auditability_and_identity_privacy_must_be_designed_together`.
`wallet_agnostic_signing_does_not_settle_final_token_substrate`.
`historical_chain_backed_settlement_option_must_be_classified_not_assumed`.

## 7. Protected boundaries and anti-pattern exclusions

The following exclusions are mandatory for Window 607-612:
- treating the capsule phrase `ILC is not a blockchain` as fully settling the
  long-run `ILC` substrate
- treating older later-chain aspirations as if they are already current canon
- collapsing `ECU` and `ILC` into one undifferentiated substrate discussion
- assuming public identity-linked artifacts must automatically be fully visible
- pushing outbound or inbound payment implementation into this window
- any wallet write/transfer/withdrawal widening inside this window
- treating current RC/runtime implementation truth as if it automatically
  determines the final public settlement substrate

`current_capsule_language_must_not_overgeneralize_rc_runtime_posture`.
`historical_chain_backed_settlement_option_must_be_classified_not_assumed`.
`no_wallet_authority_widening_inside_reconciliation_window`.
`public_auditability_and_identity_privacy_must_be_designed_together`.

## 8. Sequence integrity rule

Window 607-612 must execute in this order:
1. Phase 607 sequence lock and issue framing.
2. Phase 608 historical lineage and authority audit.
3. Phase 609 ECU / ILC / runtime-boundary reconciliation.
4. Phase 610 public-ledger substrate options and rejection matrix.
5. Phase 611 governance vehicle selection and prelock.
6. Phase 612 closure synthesis and downstream replan.

This ordering prevents the current RC/runtime ledger posture, historical
blockchain aspirations, public tokenomics language, or wallet-signing framing
from hardening into silent final-substrate assumptions before the authority
stack has been explicitly reconciled.
