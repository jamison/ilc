# ILC ECU / ILC Semantic Boundary Spec - GAP-VALUE-ECU-00

**Phase:** 1581 / GAP-VALUE-ECU-00
**Date:** 2026-07-26
**Status:** Ratifiable specification
**Sensitivity:** NON-SENSITIVE

---

## 1. Purpose and Gate

This specification records the canonical boundary between ECU, ILC, Werner local productive credit, passive ECU, fast-path balance objects, wallet-visible balances, and future transfer actions.

This document is a sequencing gate. The token `ecu_ilc_semantic_boundary_gates_transfer_enabled_rc_phase_1581` must be present before any of the following proceeds:

- `TRANSFER-ENABLED RC AUTHORIZED`
- an `ILCValueAction` CDL
- production bridge activation for `ECUTransfer`
- wallet transfer, spend, or withdrawal implementation beyond query/proof claimability

This phase does not open a CDL, clear a guard, write a wallet, mint ECU or ILC, settle value, activate public RC, or push the public mirror.

## 2. Canonical Surface Classification Table

| Surface | Canonical name | CDL / ADR authority | Runtime status as of 2026-07-26 | Transferable? |
|---|---|---|---|---|
| Settlement-grade attribution ECU | `ProtocolECU` | CDL-052, CDL-081, CDL-084, CDL-085 | Live for REUSE, CO_AUTHORSHIP, PROVENANCE, and REFUTATION attribution paths in `epoch_attribution_settle_runtime.py` | No. Narrow coordination and sender-auth exceptions are listed separately. |
| Bounded directed commission | `ECUEarmark` | CDL-063 | Live in `ecu_active_layer_runtime.py` | No. Debit reduces the commissioning agent's accrued ECU; it does not credit the performer. |
| Authenticated fast-path balance object | `ECUTransfer` | CDL-066 sender authorization | Live in Rust consensus types and `balance_store.rs`; Python production bridge remains off with `PRODUCTION_BRIDGE_ACTIVE = False` | Scoped CDL-066 sender-auth only. This is not generalized ECU transfer. |
| CDL-048 mandatory conversion lot | `ECUConversionLot` | CDL-048, CDL-030 | Guard `CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED = False` after Phase 1575g; Phase 1575r rehearsal remains pending | Converts ECU to ILC. It is not a transfer surface. |
| Passive ECU / centrality attribution | Part of `ProtocolECU` when active | CDL-052, CDL-060, CDL-078 | Source is currently active with `PASSIVE_ECU_WIRING_NOT_ACTIVATED = False`, changed by commit `93773ef8a` for the private canonical soak. Public-RC disposition is not authorized yet. | No. |
| Werner local productive credit | `LocalProductiveCredit` | CDL-053 | Ratified but not activated for live distribution | No. It is explicitly not ECU, not settlement-grade, not wallet-visible, and not transferable. |
| Werner / pressure diagnostics | `PressureDiagnostics` | Research only; no constitutional activation | Research and pre-canon only | No. Heat or pressure does not mint ECU or settle ILC. |
| Settled ILC account balance | `ILCSettledBalance` | CDL-027, CDL-029, CDL-048 | Live LMDB wallet store uses `b"wallets"` and `b"wallet_history"`; claimability and action authority remain guarded | Query/display only. Transfer, spend, and withdrawal remain blocked. |
| Future ILC transfer / spend action | `ILCValueAction` | No CDL yet | Not built | Not authorized until a future CDL, signer binding runtime, value-action hyperedge, nonce enforcement, and settlement-root inclusion exist. |

## 3. Constitutionally Closed Paths

| Closed path | Decision | Source |
|---|---|---|
| Generalized ECU transfer | Rejected by Phase 625 / CDL-063 scoping. Option C was rejected because it exceeded CDL-063 scope and created a general payment surface incompatible with the current bounded canon. | `docs/specs/ilc_ecu_active_economic_layer_architecture_scoping_625_v0.1.md` |
| Direct Werner heat-to-ECU minting | Rejected at Phase 1263 and preserved by CDL-053. `direct_werner_ecu_creation_rejected_phase_1263` is the controlling token; CDL-053 records `WERNER_DIRECT_HEAT_TO_ECU_MINTING = not_authorized`. | `docs/specs/ilc_werner_flow_governor_cdl_decision_1263_v0.1.md`; `docs/specs/ilc_cdl_053_werner_local_productive_credit_ratification_evidence_1407_fix2_v0.1.md` |

These paths are closed, not merely deferred. Reopening either requires a new constitutional vehicle.

## 4. Terminology Precision Register

| Term | Binding | Prohibited conflation |
|---|---|---|
| `ProtocolECU` | Settlement-grade ECU produced by ratified attribution paths. | Werner local productive credit, pressure diagnostics, or arbitrary local credit. |
| `ECUEarmark` | Bounded directed commission reservation and debit machinery. | A fifth attribution path or a credit-side supplement for the performer. |
| `ECUTransfer` | CDL-066 authenticated sender-authorized Rust balance-object path. | Generalized ECU transfer or public wallet transfer authority. |
| `LocalProductiveCredit` | CDL-053 Werner local productive credit eligibility signal. | ECU, settlement-grade balance, wallet-visible value, or transferable asset. |
| `Inverted ECU` | Spend-to-keep / productive deployment posture. | Backward attribution or retroactive provenance credit propagation. |
| `ILCSettledBalance` | Epoch-settled ILC balance visible through wallet/accounting surfaces. | Wallet spend, transfer, withdrawal, or public claimability authority. |

## 5. Guard Constant Inventory

| Guard / field | Live value | Source |
|---|---:|---|
| `PASSIVE_ECU_WIRING_NOT_ACTIVATED` | `False` | `ilc_core/economics/epoch_attribution_settle_runtime.py` |
| `PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED` | `True` | `ilc_core/economics/productive_ecu_expansion_bounty_runtime.py` |
| `PRODUCTION_BRIDGE_ACTIVE` | `False` | `ilc_core/consensus/production_bridge.py` |
| `GENESIS_WALLET_WRITE_AUTHORIZED` | `False` | `ilc_core/epoch/genesis_settlement_destination.py` |
| `GENESIS_SETTLEMENT_WRITE_AUTHORIZED` | `False` | `ilc_core/epoch/genesis_settlement_destination.py` |
| `GENESIS_MINTING_AUTHORIZED` | `False` | `ilc_core/epoch/genesis_settlement_destination.py` |
| `CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED` | `False` | `ilc_core/ledger/conversion_candidate_runtime.py` |
| `ConversionReceipt.public_claimability_activated` | `False` | `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` |
| `ConversionReceipt.wallet_withdrawal_enabled` | `False` | `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` |
| `ConversionReceipt.wallet_transfer_enabled` | `False` | `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` |
| `ConversionReceipt.wallet_spend_enabled` | `False` | `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` |
| `ConversionReceipt.ecu_mint_authorized` | `False` | `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` |
| `ConversionReceipt.ilc_settlement_authorized` | `False` | `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` |

## 6. What Remains Open

### Passive ECU Public-RC Guard Disposition

The live source currently has `PASSIVE_ECU_WIRING_NOT_ACTIVATED = False`.

Token history:

- Phase 1577 / GAP-CDL060 installed the passive ECU hook behind `PASSIVE_ECU_WIRING_NOT_ACTIVATED = True` and recorded `passive_ecu_guard_installed_phase_GAP_CDL060`.
- Phase 1575h-Reset-Canonical changed the guard to `False` for canonical private-soak execution and recorded `passive_ecu_guard_cleared_canonical_phase_1575h_reset`.
- Phase 1575h-Canonical-Soak recorded `passive_ecu_active_canonical_soak_phase_1575h_canonical`.

The current `False` state is therefore a private-soak operational state. It is not an explicit public-RC economic authorization. No exact GO phrase `GO 1581 PASSIVE-ECU-PUBLIC-RC-AUTHORIZED` was received in this phase.

Default disposition: passive ECU must be re-guarded to `True` before public mirror unless a later SENSITIVE phase explicitly authorizes passive ECU for public RC. The named carry-forward phase is `GAP-CDL060-GUARD-CLEARANCE`. It must decide whether public RC ships passive ECU active, and it must set or verify `PASSIVE_ECU_WIRING_NOT_ACTIVATED` accordingly before mirror regeneration.

Output token for this default disposition: `passive_ecu_public_rc_disposition_requires_guard_clearance_phase_1581`.

### Other Open Surfaces

- `1575r` must rehearse CDL-048 production conversion.
- `1575s` must decide and execute Genesis minting/accounting authorization under its own sensitive gate.
- `1575t` must run end-to-end production economic soak.
- `1578e` may continue operator-delegation preflight, but it cannot activate value movement.
- `1578f` requires `1575t` and must rerun proof-claimability.
- `1578h` must gate public-RC wallet scope and requires a separate `TRANSFER-ENABLED RC AUTHORIZED` phrase for any transfer-enabled RC.
- `1579a` and `1579b` remain post-RC stubs unless transfer-enabled RC is explicitly authorized.

## 7. Non-Claims

This specification does not:

- open or mutate any CDL
- authorize generalized ECU transfer
- authorize Werner heat-to-ECU minting
- authorize passive ECU as public-RC economics
- change `PASSIVE_ECU_WIRING_NOT_ACTIVATED`
- activate `PRODUCTION_BRIDGE_ACTIVE`
- authorize wallet transfer, spend, withdrawal, signing, or ledger write
- mint ECU or ILC
- settle ILC
- write validator DBs or wallet LMDBs
- regenerate or push the public mirror
- activate public RC

## 8. Phase 1581 Tokens

```text
ecu_ilc_semantic_boundary_spec_committed_phase_1581
ecu_surface_classification_table_ratified_phase_1581
generalized_ecu_transfer_closed_confirmed_phase_1581
werner_heat_to_ecu_rejected_confirmed_phase_1581
ecu_ilc_semantic_boundary_gates_transfer_enabled_rc_phase_1581
ecu_earmark_debit_no_credit_supplement_confirmed_phase_1581
ecu_transfer_cdl066_sender_auth_only_confirmed_phase_1581
local_productive_credit_not_ecu_confirmed_phase_1581
inverted_ecu_backward_attribution_distinction_confirmed_phase_1581
passive_ecu_guard_state_recorded_phase_1581
passive_ecu_public_rc_disposition_requires_guard_clearance_phase_1581
production_bridge_guard_state_recorded_phase_1581
no_cdl_opened_phase_1581
no_guard_cleared_phase_1581
no_wallet_write_phase_1581
no_minting_no_settlement_phase_1581
no_public_mirror_push_phase_1581
```
