# ILC ECU / ILC / Runtime-Boundary Reconciliation 609 v0.1

Status: locked
Date: 2026-04-10
Phase: 609
Owner lane: G8 settlement substrate reconciliation

## 1. Reconciliation target and inherited authority stack

Phase 609 reconciles `ECU`, `ILC`, and the current RC/runtime internal-ledger
posture without selecting a final long-run public settlement substrate.

`phase_609_reconciliation_separates_ecu_ilc_and_current_runtime_without_selecting_final_substrate`.

This packet inherits the Phase 607 sequence lock and the Phase 608 authority
classification.

Present-tense authority order for this reconciliation is:
- Tier A runtime and accepted-boundary sources control present-tense truth,
- Tier B bounded current surfaces constrain evidence and public claims only,
- Tier C and Tier D sources may inform interpretation only when explicitly
  labeled,
- `ADR-0026` is the operative accepted boundary surface while `ADR-0012` and
  `ADR-0013` remain lower-authority proposed inputs.

This phase reconciles layers and boundaries but does not pick a public-ledger path.

## 2. ECU layer and local/protocol-internal semantics

`ecu_is_local_protocol_internal_productive_credit_layer`.

`ECU` is the local/protocol-internal productive-credit layer.

Phase 609 keeps the ECU layer narrow:
- the current runtime and economic-design corpus may describe ECU circulation without implying public-chain settlement,
- ECU semantics may inform later settlement design, but ECU is not itself the
  final public-ledger decision,
- ECU discussion in this memo does not reopen transfer or write-authority boundaries fixed by Phases 576 and 581.

The controlling runtime meaning remains the locked RC0.1 posture:
- Phase 576 fixes wallet visibility and accounting only, with no ledger write
  authority,
- Phase 581 proves settled LMDB-backed wallet/query surfaces while keeping the
  same read-only meaning,
- any discussion of ECU circulation or sector-level economic behavior remains
  subordinate to those locked runtime boundaries.

Therefore ECU may circulate inside the protocol and economic-design discourse
without collapsing into a claim that ECU is the final public settlement asset.

## 3. ILC layer and hard-settlement semantics

`ilc_is_hard_settlement_asset_with_final_substrate_still_unresolved`.

`wallet_handoff_line_12_ilc_ecu_conflation_rejected_as_stable_authority`.

`wallet_agnostic_signing_is_signing_provider_compatibility_not_substrate_closure`.

`ILC` is the hard settlement asset in the design corpus.

Phase 609 fixes the ILC layer as follows:
- the final long-run public settlement substrate for `ILC` remains unresolved in
  current authority,
- December 2025 later-chain direction remains legitimate historical strategy,
  not current closure,
- the line-12 `ILC coin (ECU)` sentence in the wallet handoff is rejected as
  stable authority for this reconciliation,
- the line-105 anti-blockchain sentence in the wallet handoff is not sufficient
  by itself to close the final substrate question.

The wallet/signing handoff remains useful only on the narrower point it actually
supports: wallet-agnostic signing is about signing keys and provider
compatibility, not token substrate, transfer authority, or final-settlement
closure.

## 4. Current RC/runtime posture versus final-substrate non-closure

`current_rc_runtime_internal_ledger_is_bounded_current_posture_not_forever_substrate`.

The current RC/runtime is an internal epoch-settled ledger with read-only
wallet/query surfaces.

That posture is a bounded current implementation truth, not forever-substrate closure by implication.

The locked current-runtime boundary is:
- Phase 576 defines RC0.1 balance as settled internal ledger balance only,
- Phase 581 proves the authoritative live runtime path over LMDB-backed
  settlement roots,
- no current runtime artifact authorizes payment runtime, public withdrawal, or
  wallet write authority.

Phase-boundary carry-forward in this section remains explicit:
- Phase 600 remains a bounded evidence surface only,
- Phase 602 remains a bounded current public-claims surface only,
- neither Phase 600 nor Phase 602 settles the final public-ledger substrate for
  `ILC`.

## 5. Public auditability versus identity/privacy boundary

`public_auditability_is_not_public_identity_exposure`.

Public auditability is not identical to public identity exposure.

Any later public-ledger substrate must preserve the privacy boundary already
established by the wallet/signing and transport/privacy work.

Phase 609 therefore locks all of the following:
- directly correlatable public identity artifacts are not assumed by default,
- a later public-ledger substrate may need auditable settlement state without
  exposing raw or easily correlatable identity-linked artifacts,
- this memo does not pre-decide the exact auditability/privacy mechanism; it
  preserves the distinction as mandatory input to Phase 610.

## 6. Carry-forward constraints into Phase 610 and Phase 611

`phase_609_reconciliation_does_not_authorize_payment_lane_or_wallet_widening`.

`phase_610_options_matrix_must_consume_phase_609_layer_separation`.

Phase 610 must consume the `ECU` / `ILC` / runtime separation from this memo.

Phase 610 must not collapse current runtime truth into final substrate closure.

Phase 611 remains conditional and may not be pre-opened here.

No payment-lane progress or wallet-authority widening is authorized by Phase
609.
