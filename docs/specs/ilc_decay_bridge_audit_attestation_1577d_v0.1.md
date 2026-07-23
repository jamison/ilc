# ILC Decay Bridge Audit Attestation 1577d v0.1

Status: locked
Date: 2026-07-23
Phase: 1577d / GAP-DECAY-BRIDGE-01

`decay_bridge_audit_complete_phase_1577d`

## 1. Purpose

This attestation closes GAP-DECAY-BRIDGE-01 by tracing the actual Python-to-Rust
ECU balance path and resolving the ambiguity in the phrase "temporal decay
bridge." The result is a boundary clarification, not an economic activation.

## 2. Audit Question

The original planning question was whether Python temporal decay is applied to
outstanding ECU balances before Rust LMDB commitment, or whether Rust stores raw
pre-decay balances without a required decay step.

The question as written is overbroad. The code and canon use three distinct
decay/anti-hoarding surfaces:

1. CDL-V1 temporal decay: exponential half-life decay over Tier-2 reputation and
   reuse-centrality data.
2. CDL-084 provenance decay: `PROVENANCE_DECAY_ALPHA` geometric decay over
   provenance-chain payouts.
3. CDL-048 anti-hoarding pressure: mandatory ECU-to-ILC conversion cadence and
   deadline, not raw Rust balance demurrage.

## 3. Source Trace

| Layer | Source | Finding |
|-------|--------|---------|
| CDL-V1 runtime | `ilc_core/reputation/temporal_decay_runtime.py` | Implements `compute_decay_multiplier()` and `apply_temporal_decay()` with exact Decimal arithmetic and `epoch_type="issuance_epoch"` validation. |
| CDL-V1 canon | `docs/specs/ilc_cdl_071_temporal_tier_reconciliation_opening_850_v0.1.md` | States that CDL-V1 governs reputation scores and reuse centrality, assigned to Tier 2. |
| Python read bridge | `ilc_core/consensus/production_bridge.py` | Exposes read-only gRPC balance and epoch queries; `PRODUCTION_BRIDGE_ACTIVE = False`; no write path applies decay or mutates consensus balances. |
| Python attribution bridge | `ilc_core/consensus/attribution_batch_bridge.py` | Converts accepted claim amounts to integer micro-ECU attribution deltas for Rust ingest. It performs exact Decimal validation and micro-ECU flooring, not temporal balance decay. |
| Rust ingest CLI | `ilc_consensus/src/attribution_batch_ingest_main.rs` | Validates JSON attribution batches and calls `BalanceStore.apply_attribution()`. It does not perform claim review, conversion, settlement, or decay. |
| Rust balance store | `ilc_consensus/src/balance_store.rs` | Stores `ECUBalance` and applies transfers or additive attribution batches with replay guards. It is a commitment/application layer, not an economics engine. |
| ECU lifecycle | `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md` | Defines ECU as local productive credit and states anti-hoarding is handled by conversion cadence/deadline, not by silently decaying raw balances in LMDB. |

## 4. Disposition

Hypothesis A is correct only with a refined interpretation: Python computes the
economic quantities that Rust commits, and Rust is intentionally a narrow
commitment/application layer. However, CDL-V1 is not currently a raw outstanding
balance decay rule. Therefore, there is no missing Rust-side balance-demurrage
implementation to add in this phase.

Hypothesis B is rejected as a required pre-RC implementation patch because it
assumes a raw balance decay obligation that the source canon does not ratify.
Adding such a rule here would silently alter protocol economics and would need a
separate governance decision.

`cdl_v1_reputation_decay_not_raw_balance_decay_confirmed_phase_1577d`

`rust_balance_store_commit_layer_confirmed_phase_1577d`

`no_balance_demurrage_rule_added_phase_1577d`

## 5. Correct Boundary

The correct pre-RC boundary is:

1. Reputation/reuse-centrality decay remains CDL-V1 and is computed in Python.
2. Provenance payout decay remains CDL-084 and uses `PROVENANCE_DECAY_ALPHA`.
3. Rust consensus commits exact attribution and transfer state supplied to it;
   it does not infer economic policy from reputation constants.
4. ECU anti-hoarding for balances is the CDL-048 conversion/deadline lane.

This means a future "outstanding balance decay" rule, if desired, must be opened
as an explicit economics/governance phase. It must not be introduced by reusing
`PROVENANCE_DECAY_ALPHA` or by treating CDL-V1 reputation decay as balance
demurrage.

## 6. Non-Claims

This phase does not:

- activate production economics,
- clear CDL-048, treasury, validator, Genesis minting, or settlement guards,
- mutate validator LMDBs,
- send epoch checkpoints,
- add Rust-side balance demurrage,
- assert that raw ECU balances decay automatically,
- publish a public mirror or make a public-RC claim.

## 7. Carry-Forward

If ILC later wants spend-to-keep or explicit outstanding ECU balance demurrage,
the next phase must be a governance/spec phase that defines:

1. whether decay affects ECU, ILC, reputation, or conversion eligibility,
2. the exact decay formula and constants,
3. where conservation loss is routed,
4. how the resulting state root commits the rule,
5. migration rules for existing balances.
