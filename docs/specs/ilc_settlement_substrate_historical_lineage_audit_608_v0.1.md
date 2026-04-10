# ILC Settlement Substrate Historical Lineage Audit 608 v0.1

Status: locked
Date: 2026-04-10
Phase: 608
Owner lane: G8 settlement substrate reconciliation

## 1. Audit target and inherited lock

Phase 608 classifies the settlement-substrate source stack for Window 607-612
without deciding the final `ILC` substrate.

`phase_608_historical_lineage_audit_classifies_source_layers_without_settling_final_substrate`.

This audit inherits the Phase 607 sequence lock and its rule that current
RC/runtime truth, historical strategy, and drift-carrier language must be
separated before Phase 609 reconciliation or Phase 610 options analysis.

The audit therefore sorts the record into four layers only:
- June 2025 exploratory option space,
- December 2025 off-chain-first / later-chain strategic direction,
- February 2026 drift-carrier and boundary language,
- current runtime and current-authority posture.

## 2. June 2025 exploratory option space

`june_2025_blockchain_and_settlement_discussion_is_exploratory_option_space`.

The June 2025 record is exploratory architecture work, not current closure.

Direct source classification:
- `Z_Past_Chats/2025_06_03_ILC - Higher Dimensional Geometry in DS.txt`
  explores ERC-20, rollup, L1, and L2 variants for ILC settlement and wallet
  compatibility.
- `Z_Past_Chats/2025_06_05_ILC - AI Job Impact and Advancement.txt` frames ILC
  as building on blockchain credibility while also discussing off-chain or
  rollup-based economic layers and Bitcoin-key compatibility.

The June option space includes:
- ILC as ERC-20 or similar token on Ethereum or other chains,
- ILC as sovereign L2 rollup,
- ILC as standalone L1,
- Bitcoin-style key compatibility regardless of where settlement lives.

These materials are historically useful because they show that chain-backed
settlement was openly considered early. They are not current law because they
were exploratory design conversations without later ratified closure.

## 3. December 2025 off-chain-first / later-chain strategic direction

`december_2025_off_chain_first_later_chain_direction_is_historical_strategy_not_current_closure`.

The December 2025 record is materially stronger than the June exploratory set,
but it still remains historical strategy rather than current closure.

The strongest December sources are:
- `whitepaper/2025_12_03_ILC_whitepaper_v5_2.md`, which declares an off-chain
  MVP with forward-compatible hooks for on-chain settlement and later concrete
  L2 or rollup binding.
- `Z_Past_Chats/OLD_2025_12_07_ILC - ILC project status update.txt`, which
  states that the core protocol should talk to a ledger interface rather than a
  hard-bound chain implementation.
- `Z_Past_Chats/OLD_2025_12_25_ILC - ILC project status update.txt`, which
  explicitly recommends off-chain first and later custom minimal L1 or other
  chain-backed settlement.

The December strategy is coherent on four points:
- real nodes, real agents, and real economics should run before any permanent
  public chain commitment,
- the protocol should preserve a ledger-backend abstraction,
- later chain-backed settlement remains a valid intended direction,
- the off-chain MVP is a bootstrap posture rather than a final constitutional
  statement that `ILC` can never settle on a public ledger.

That strategy is historically authoritative enough to survive as a Phase 608
input, but it is not current closure because no later accepted ADR or ratified
CDL explicitly locks a final public substrate choice.

## 4. February 2026 drift-carrier and boundary language

`february_2026_capsule_v0_4_v0_5_language_is_historical_drift_carrier_not_final_substrate_law`.

The February 2026 record contains the main drift carriers for this window.

Verified chronology:
- commit `eaf6d0e3ac5024112a4e3ae054da6da439f9f472` on 2026-02-20 introduced the
  phrase `ILC is NOT a blockchain` into
  `docs/specs/ilc_antigravity_context_capsule_v0.4.md`.
- commit `db8627d64203e2f6d82f0e5005161e931307554d` on 2026-02-22 carried that
  same framing forward into `docs/specs/ilc_antigravity_context_capsule_v0.5.md`.
- commit `48a2b042c671289adf01798cc81ca1e24077e361` on 2026-02-21 introduced both
  the line-12 sentence `The ILC coin (ECU) is protocol-native.` and the line-105
  sentence `ILC's native coin remains independent of any blockchain` into
  `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`.

`wallet_handoff_ilc_ecu_conflation_and_overbroad_anti_blockchain_language_are_phase_609_reconciliation_inputs`.

Phase 608 classification of these February materials is:
- capsule `v0.4` and `v0.5` correctly describe the current executable emphasis on
  epistemic-graph protocol work, but they overgeneralize that runtime emphasis
  into a broader anti-blockchain identity claim,
- the wallet handoff correctly argues for wallet-agnostic signing and key-layer
  compatibility, but line 12 conflates `ILC` and `ECU` and line 105 overstates
  the anti-blockchain conclusion,
- none of these February formulations by themselves close the long-run public
  settlement-substrate question for `ILC`.

Therefore the February wording is not discarded, but it must be treated as
historical drift-carrier and boundary-input material rather than as silent final
substrate law. This is historical drift-carrier language rather than silently inherited closure.

## 5. Current runtime and current-authority posture

`phase_602_public_tokenomics_statement_is_bounded_current_public_claims_surface_not_final_substrate_closure`.

`current_rc_runtime_internal_epoch_settled_ledger_truth_is_current_implementation_not_final_substrate_by_implication`.

The current accepted and locked runtime truth is narrower than the February
anti-blockchain rhetoric.

Current executable/runtime truth:
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md` locks a
  read-only wallet visibility and accounting surface with no ledger write,
  spend, transfer, or withdrawal authority.
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`
  proves that the authoritative RC0.1 balance is a settled internal ledger
  balance over the LMDB-backed epoch-commit path.
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md` is Accepted and
  preserves the narrow wallet and product boundary.

Current bounded surface classification:
- Phase 600 is a bounded evidence surface for Genesis economics and parameter
  closure. It does not decide final public-ledger substrate.
- Phase 602 is a bounded current public-claims surface rather than final substrate closure.
  It narrows what may be said publicly now; it does not decide final public
  substrate.
- capsule `v3.2` is the current context surface for the 596-605 closure state,
  and it does not repeat the blunt `ILC is NOT a blockchain` phrase.

Current design-input context that remains below accepted authority:
- `docs/adr/ADR_0012_ECU_ILC_Graph_Coupling_and_Anti_Reflexivity.md` and
  `docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md`
  are Proposed, not accepted,
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md` is valuable but
  remains a non-normative economics synthesis rather than final substrate law.

## 6. Audit conclusions and carry-forward constraints

`historical_chat_and_whitepaper_material_must_not_outrank_current_canon`.

Phase 608 conclusions are:
- June 2025 proves that chain-backed settlement and rollup-style deployment
  were early exploratory options.
- December 2025 preserves the strongest historical strategic direction:
  off-chain first, ledger-interface in the middle, later chain-backed settlement
  still open.
- February 2026 introduced the main drift-carrier phrasing that overgeneralized
  current RC/runtime truth into a broader anti-blockchain architectural claim.
- current runtime truth is an internal epoch-settled ledger with read-only
  wallet/query surfaces, but that current implementation reality does not settle
  the forever substrate for `ILC` by implication.
- Phase 600 and Phase 602 are bounded current surfaces only. They constrain
  evidence language and public claims; they do not close the long-run
  settlement-substrate question.
- the wallet handoff line-12 `ILC coin (ECU)` wording is a known inconsistency
  and must remain an explicit Phase 609 reconciliation input.

Carry-forward constraints into Phase 609 and Phase 610:
- use current accepted and locked runtime surfaces as present-tense truth,
- use December 2025 material only as labeled historical strategy,
- use June 2025 only as exploratory option space,
- treat capsule `v0.4` / `v0.5` and the wallet-handoff inconsistency as known
  reconciliation targets rather than stable final-substrate authority.
