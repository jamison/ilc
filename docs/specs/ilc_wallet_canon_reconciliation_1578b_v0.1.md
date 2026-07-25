# ILC Wallet Canon Reconciliation 1578b v0.1

**Phase:** 1578b / GAP-WALLET-01  
**Date:** 2026-07-25  
**Status:** committed reconciliation / no runtime activation  
**Sensitivity:** NON-SENSITIVE

## 1. Purpose

This report reconciles wallet-adjacent ILC canon against the six wallet-lane architecture decisions recorded in `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md`. The result is a compatibility and gap inventory only. It does not open, amend, or ratify any CDL; it does not activate signer binding, transfer, spend, withdrawal, public claimability, minting, settlement, or wallet writes.

## 2. Six Canonical Wallet Decisions

| Decision | Source | Reconciliation verdict |
|----------|--------|------------------------|
| ILC-native first: `agent_id` is the account anchor; external wallets are delegated adapters | `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:14-28` | Compatible with CDL-042/CDL-069 identity canon and Phase 576 wallet boundary |
| Operator delegation accepted as an on-graph service-account design target | `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:29-48`; `docs/specs/ilc_agent_identity_enrollment_spec_1578a_v0.1.md:61-76` | Compatible, but runtime authority remains deferred to signer-binding and delegation phases |
| Public RC default is visibility/proof-claimability only; transfer-enabled RC needs exact `TRANSFER-ENABLED RC AUTHORIZED` | `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:50-58` | Compatible with Phase 1314 and wallet action preflight flags |
| Option C2: balances are canonical settled account state bound to `agent_id`; `GENESIS_WALLET_WRITE_AUTHORIZED=False` means no spend/transfer/withdraw authority, not invisibility | `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:60-72` | Compatible with Phase 576 settled-balance visibility and current public wallet runtime |
| Replay architecture: per-`agent_id` nonce for wallet-facing actions, object-version certificates for Rust consensus, nullifiers for proof claimability | `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:74-84`; `docs/specs/ilc_agent_identity_enrollment_spec_1578a_v0.1.md:53-59` | Compatible; nonce runtime surface is not yet implemented |
| Canonical ILC intent object with EIP-712/COSE adapter projections | `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:86-120` | Compatible with wallet-agnostic signing strategy; canonical envelope remains 1578c work |

## 3. CDL / ADR / Runtime Inventory

| Canon item | Status | Source | Wallet relevance | Verdict |
|------------|--------|--------|------------------|---------|
| CDL-001 signer lineage trust root | Implemented / full in map | `docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md:204` | Establishes signer lineage context for future wallet signer binding | No conflict |
| CDL-040 admission control | Implemented / full in map | `docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md:114` | Existing admission machinery is validator-oriented, not general wallet enrollment | No conflict |
| CDL-042 agent identity namespace | Implemented / full in map | `docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md:115` | Supports key-derived globally flat `agent_id` account anchors | No conflict |
| CDL-066 sender authorization | Implemented / full in map | `docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md:116` | Future wallet signer binding must not bypass existing sender authorization semantics | No conflict |
| CDL-069 PQ identity / epoch endorsement | Implemented / full in map | `docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md:117`; `ilc_core/genesis/invitation_provenance_record.py:235-237` | Supports ILC-native identity derivation independent of external wallet address | No conflict |
| CDL-V2 sybil resistance | Implemented / full in map | `docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md:118`; `ilc_core/identity/sybil_resistance_runtime.py:70-77` | Provides advisory sybil scoring; not a wallet balance or settlement weight authority | No conflict |
| CDL-048 mandatory ECU-to-ILC conversion | Partial in map; production activation still gated | `docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md:188`; `docs/phases/STATUS.md` Phase 1575q entry | Governs conversion and Genesis accounting; does not create transfer authority | No conflict |
| CDL-088 public claimability authority | Ratified authority only; activation gated | `docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md:189`; `ilc_core/sidecars/claimability_receipt_verifier.py:48-50`; `ilc_core/sidecars/claimability_receipt_verifier.py:599-616` | Local proof-bound claimability exists; public claimability and wallet ops remain false | No conflict; display reconciliation routed to 1578f |
| ADR-0015 node transfer economics | Proposed / no runtime activation | `docs/specs/ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md:156-177` | Future transfer-tax/cooling rules; does not authorize RC transfers | No conflict |
| ADR-0027 bootstrap receipt boundary | Implemented boundary | `docs/specs/ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md:40-67` | Supports proof-local claimability verification without mint/settlement/wallet write authority | No conflict |
| Wallet-agnostic signing strategy | Approved handoff / non-consensus strategy | `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:12-20`; `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:62-70`; `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:99-107` | Supports Coinbase, Bitcoin, Ethereum, hardware, and local key providers while keeping ILC independent of any external chain | No conflict |
| Phase 576 settlement-wallet boundary | Locked boundary | `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md:17-24`; `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md:58-81`; `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md:83-108` | Wallet is read-only visibility/accounting; ledger writes, transfer, spend, and withdrawal are deferred | No conflict |
| Phase 1314 wallet action preflight | Preflight-only / no activation | `docs/specs/ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md:31-38`; `docs/specs/ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md:89-103`; `docs/specs/ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md:130-154`; `docs/specs/ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md:179-190` | Confirms transfer/spend/withdraw/provider signing are blocked at pre-RC | No conflict |
| Wallet action sidecar flags | Runtime preflight guard inventory | `ilc_core/sidecars/wallet_action_semantics_preflight.py:54-71`; `ilc_core/sidecars/wallet_action_semantics_preflight.py:138-155` | Machine-readable false flags for wallet transfer, spend, withdrawal, signer binding, and public claimability | No conflict |
| Public wallet runtime | Current read-only display runtime | `ilc_core/protocol/public_wallet_runtime.py:36-42`; `ilc_core/protocol/public_wallet_runtime.py:44-60`; `ilc_core/protocol/public_wallet_runtime.py:62-82`; `ilc_core/protocol/public_wallet_runtime.py:111-142` | Displays settled balances and `claimability_state="deferred"`; no signing envelope or submit path | No conflict; claimability display routed to 1578f |

## 4. Conflict Scan

| Wallet decision | Potential conflict checked | Verdict | Evidence |
|-----------------|----------------------------|---------|----------|
| ILC-native first | External wallet canon might make wallet address the account anchor | No conflict | Wallet-agnostic signing strategy treats external wallets as key providers (`docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:62-70`); Phase 576 defines wallet as read-only surface (`docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md:58-81`) |
| Operator delegation | Existing identity canon might require one human-wallet ceremony per agent | No conflict | CDL-042/CDL-069 provide key-derived `agent_id` anchors (`docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md:115-117`); 1578a records separate controlled-agent enrollment and future delegation edge (`docs/specs/ilc_agent_identity_enrollment_spec_1578a_v0.1.md:28-32`) |
| Visibility-only RC default | Claimability sidecar might already activate public claim or wallet writes | No conflict | Claimability verifier keeps mint, settlement, public API, and wallet flags false (`ilc_core/sidecars/claimability_receipt_verifier.py:599-616`) |
| Option C2 settled balances | `GENESIS_WALLET_WRITE_AUTHORIZED=False` might imply invisible balances | No conflict | Phase 576 defines settled internal balance as visible accounting state (`docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md:41-56`); public wallet runtime exposes `balance_ilc` and `balance_ecu` (`ilc_core/protocol/public_wallet_runtime.py:111-142`) |
| Replay architecture | Existing canon might require nullifiers for all wallet actions | No conflict | Wallet plan separates per-agent nonce, object-version certificates, and nullifiers by use (`docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:74-84`); Phase 1314 records future idempotent requests without activating transfers (`docs/specs/ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md:156-177`) |
| Canonical ILC intent object | Existing wallet-agnostic signing might force COSE-only and reject EIP-712 | No conflict | Wallet-agnostic strategy allows external providers and treats wallet integration as provider selection (`docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:62-70`); wallet plan requires adapter projections from one canonical object (`docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:86-120`) |

## 5. Open Tensions and Resolution Paths

| Tension | Why it matters | Blocking phase | Resolution path |
|---------|----------------|----------------|-----------------|
| General enrollment has no live runtime | Agents and human users need a canonical enrollment surface before live signer binding | 1578d | 1578a defined the spec; 1578d may bind signer authority only to already enrolled `agent_id` records or must halt |
| Proof-claimability and wallet display state are not yet reconciled | Sidecar has proof-bound local claimability while public wallet runtime still displays `deferred` | 1578f | Rerun proof-claimability gate and update display semantics only after checking `PUBLIC_CLAIMABILITY_ACTIVATED_PHASE_1438_TOKEN` |
| Signer binding authority is not ratified | External wallet signatures must not become spend/claim authority by adapter convention alone | 1578d | SENSITIVE signer-binding authority phase must ratify allowed binding records and non-claims |
| Value transfer remains blocked | A wallet that can display balance is not yet a wallet that can spend or transfer balance | 1578h / 1579a / 1579b | Public RC remains visibility/proof-claimability-only unless `TRANSFER-ENABLED RC AUTHORIZED` is given at 1578h |
| Invite enforcement remains a pre-RC lane | Human public enrollment must respect the invite chain once live | 1576m-1576r | Complete CDL-102 invite chain before public RC; do not use wallet lane to bypass invite enforcement |

No ratified CDL/ADR conflict was found against the six wallet decisions. The open items are implementation or activation gaps, not contradictions in canon.

## 6. Non-Activation Statement

This phase activates nothing. It does not mutate `ilc_core/`, clear any guard, open or amend any CDL, publish a public mirror, write a wallet balance, create a signer binding, enable transfers, enable spends, enable withdrawals, enable wallet-provider signing, mint ECU or ILC, or activate public RC.

## 7. Output Tokens

- `wallet_canon_reconciliation_committed_phase_1578b`
- `cdl_adr_wallet_surface_inventory_complete_phase_1578b`
- `no_conflict_with_six_canonical_wallet_decisions_phase_1578b`
