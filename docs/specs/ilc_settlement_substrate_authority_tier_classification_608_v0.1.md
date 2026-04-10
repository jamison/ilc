# ILC Settlement Substrate Authority-Tier Classification 608 v0.1

Status: locked
Date: 2026-04-10
Phase: 608
Owner lane: G8 settlement substrate reconciliation

## 1. Classification target

Phase 608 classifies the active source set for settlement-substrate reasoning so
that Phase 609 and Phase 610 consume the right materials in the right order.

`phase_608_authority_classification_enforces_current_canon_over_historical_strategy`.

The target is not to flatten every source into one canon tier. The target is to
separate accepted boundary law, bounded current evidence surfaces, proposed or
non-normative design inputs, and historical strategy or drift-carrier material.

## 2. Tier definitions and precedence rules

Tier definitions used in this packet:
- **Tier A — current accepted or locked authority:** accepted ADRs, locked phase
  specs, current runtime-boundary surfaces, and the ratified CDL surface.
- **Tier B — bounded current surface:** current evidence-limited or public-claim
  surfaces that are authoritative only to the scope they explicitly bound.
- **Tier C — proposed or non-normative design input:** useful design reasoning
  that is below accepted authority and cannot silently close the issue.
- **Tier D — historical strategy or exploratory lineage:** chats, old whitepaper
  strategy, and drift-carrier materials that remain informative only when
  labeled explicitly.

Precedence rules:
1. Tier A outranks every lower tier.
2. Tier B may constrain current claims but may not silently decide final
   substrate questions outside its bounded scope.
3. Tier C informs reconciliation but cannot override Tier A or Tier B.
4. Tier D may explain why the project got here, but it cannot close anything in
   the present tense.

## 3. Source-by-source classification

| Source | Current status | Tier | Phase 608 classification |
|---|---|---|---|
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | ratified rows | Tier A | Current constitutional surface; mechanism law outranks narrative history |
| `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md` | locked | Tier A | Current wallet and settlement-boundary authority |
| `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md` | locked | Tier A | Current runtime truth for settled internal-ledger balance |
| `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md` | Accepted | Tier A | Accepted boundary surface for wallet/product scope |
| `docs/specs/ilc_antigravity_context_capsule_v3.2.md` | active capsule | Tier A | Current context surface for the 596-605 closure state |
| `docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md` | locked | Tier B | Bounded evidence surface for Genesis economics |
| `docs/specs/ilc_topological_exemption_boundary_and_public_tokenomics_statement_602_v0.1.md` | locked | Tier B | Bounded current public-claims surface |
| `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md` | approved handoff | Tier B/C boundary | Current boundary input with a known wording inconsistency; usable only with explicit caution |
| `docs/adr/ADR_0012_ECU_ILC_Graph_Coupling_and_Anti_Reflexivity.md` | Proposed | Tier C | Useful design input, below accepted boundary authority |
| `docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md` | Proposed | Tier C | Useful perimeter-boundary input, below accepted boundary authority |
| `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md` | non-normative | Tier C | Valuable economics synthesis, not final substrate law |
| `whitepaper/2025_12_03_ILC_whitepaper_v5_2.md` | draft snapshot | Tier D | Historical strategy, not current closure |
| `docs/specs/ilc_antigravity_context_capsule_v0.4.md` | superseded | Tier D | Historical drift carrier |
| `docs/specs/ilc_antigravity_context_capsule_v0.5.md` | superseded | Tier D | Historical drift carrier carried forward from v0.4 |
| `Z_Past_Chats/2025_06_03_ILC - Higher Dimensional Geometry in DS.txt` | historical chat | Tier D | Exploratory option space |
| `Z_Past_Chats/2025_06_05_ILC - AI Job Impact and Advancement.txt` | historical chat | Tier D | Exploratory option space with blockchain-audience framing |
| `Z_Past_Chats/OLD_2025_12_07_ILC - ILC project status update.txt` | historical chat | Tier D | Historical strategy around ledger abstraction and later chain adapters |
| `Z_Past_Chats/OLD_2025_12_25_ILC - ILC project status update.txt` | historical chat | Tier D | Historical off-chain-first / later-chain strategic direction |

`capsule_v0_4_and_v0_5_classified_as_historical_drift_carriers`.

`capsule_v3_2_classified_as_current_context_surface_without_inheriting_v0_4_language`.

`wallet_agnostic_signing_handoff_classified_as_current_boundary_input_with_known_wording_inconsistency`.

`phase_600_classified_as_bounded_evidence_surface`.

`phase_602_classified_as_bounded_current_public_claims_surface`.

`adr_0026_classified_as_accepted_boundary_surface`.

`adr_0012_and_adr_0013_classified_below_accepted_boundary_authority`.

`whitepaper_v5_2_classified_as_historical_strategy_not_current_closure`.

## 4. Drift-carrier, bounded-claims, and safe-authority findings

Drift-carrier findings:
- `docs/specs/ilc_antigravity_context_capsule_v0.4.md` and `v0.5` carry the
  over-broad anti-blockchain phrase and must remain historical-only.
- `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`
  contains a known line-12 `ILC coin (ECU)` inconsistency and a line-105
  anti-blockchain sentence that cannot close the long-run substrate question on
  its own.

Bounded-claims findings:
- Phase 600 tells us what can be claimed about Genesis evidence now.
- Phase 602 tells us what can be said publicly about tokenomics now.
- Neither packet authorizes a permanent conclusion about where final `ILC`
  settlement must live.

Safe-authority findings:
- the current wallet and runtime boundary are governed by locked Phase 576 and
  Phase 581 surfaces,
- `ADR-0026` is the operative accepted boundary surface for product and wallet
  scope,
- the ratified CDL layer remains current mechanism law and is not itself the
  contamination source for this substrate question.

## 5. Phase 609 and 610 routing notes

`phase_609_must_consume_known_drift_carriers_and_safe_boundary_sources_separately`.

Phase 609 must:
- consume Tier A runtime and accepted-boundary sources as present-tense truth,
- consume Tier B bounded current surfaces only to the extent they constrain
  evidence and public claims,
- consume the wallet-handoff inconsistency and old capsule language as explicit reconciliation targets rather than inherited law,
- keep Tier D historical strategy and exploratory material labeled as history.

Phase 610 must:
- use the Tier A and Tier B outputs of Phase 609 as the basis for any options
  matrix,
- avoid using Tier D material as if it already picked the winner,
- preserve the distinction between public auditability and public identity
  exposure while evaluating future substrate options.
