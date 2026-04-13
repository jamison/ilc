# ILC Tier-0 Numeric Surface Inventory and Risk Classification 632 v0.1

Status: scoped
Date: 2026-04-13
Window: 631-636
Phase: 632
Owner lane: G8 tier-0 economic numeric determinism strike force

## 1. Authorization basis and inventory scope

This document inventories the Tier-0 float-bearing runtime-critical economic,
ledger, staking, and directly coupled export surfaces named by the Phase 631
sequence lock. The inventory basis is code-derived rather than memo-derived:
the target surface was rescanned directly for `float`, epsilon tolerances, and
rounding-based replay logic before classification.

The scope is bounded to the Tier-0 strike-force surface:
- `ilc_core/ledger/`
- `ilc_core/rc/economic_cycle_runtime.py`
- `ilc_core/validator/staking_liveness_runtime.py`
- `ilc_core/types.py`
- directly coupled runtime/export/validation files required to keep those
  surfaces coherent once exact numeric representation is ratified

This phase does not choose the final representation direction. It opens
`CDL-064` and records why float retention is no longer acceptable for Tier-0.

`tier0_numeric_inventory_632_locked`
`cdl_064_opened_as_stub`
`tier0_float_surface_inventory_complete`

## 2. Tier-0 surface inventory

The inventory rows below cover every currently identified Tier-0 float-bearing
surface or directly coupled float-admitting export/validation companion within
the sequence-lock target surface.

| File path | Numeric role | Current primitive | Risk class | Migration class |
|---|---|---|---|---|
| `ilc_core/ledger/backend.py` | in-memory ledger balances, reward totals, stake-share settlement, epoch reward application | float state, float reward extraction, float settlement share math | R1 | M1+M3 |
| `ilc_core/ledger/stake_snapshot.py` | snapshot stake map and `total_stake` integrity check | float stakes, float total, `1e-9` epsilon validation | R1 | M1+M3 |
| `ilc_core/ledger/settlement_verification.py` | settlement replay verification, deltas, error bounds, hash inputs | float balances, float reward totals, epsilon-based equality/error checks | R1 | M3 |
| `ilc_core/ledger/lmdb_backend.py` | persisted balance and stake snapshot loading/storage for LMDB backend | float balance casts, float snapshot casts, float JSON payloads | R1 | M1+M2 |
| `ilc_core/ledger/persistent_backend.py` | persisted balance and stake snapshot loading/storage for file backend | float balance casts, float snapshot casts, float JSON payloads | R1 | M1+M2 |
| `ilc_core/rc/economic_cycle_runtime.py` | economic-cycle claim totals, reward reconciliation, wallet payload export, node stake coercion | float aggregation, `round(..., 12)`, `1e-9` replay check, float export fields | R1 | M1+M2+M3 |
| `ilc_core/validator/staking_liveness_runtime.py` | validator stake validation and penalty-return surface | float stake input and float penalty fractions/constants | R2 | M1 |
| `ilc_core/types.py` | protocol-level `net_stake` fields on `Node` and `ClaimRecord` | float-typed protocol/runtime fields | R2 | M1+M2 |
| `ilc_core/ledger/ledger_export.py` | ledger state export and distribution-check CSV/JSON surfaces | float-typed balances and verification totals in machine output | R2 | M2 |
| `ilc_core/ledger/canon_export.py` | canonical ledger-state export payload and hash input surface | float balances inside canonical export payload | R2 | M2 |
| `ilc_core/ledger/ecu_active_layer_runtime.py` | bounded active-layer runtime compatibility surface | exact internal `Decimal`, but float ingress/egress compatibility at public methods | R2 | M2 |
| `ilc_core/ledger/settlement_metrics.py` | aggregate settlement metrics for runtime summaries | float reward aggregates and typed output | R3 | M2 |
| `ilc_core/ledger/canon_export_bundle.py` | bundle-export scalar contract | `JsonScalar` explicitly admits float in bundle payloads | R3 | M2 |
| `ilc_core/ledger/canon_export_format.py` | canon-export format scalar contract | `JsonScalar` explicitly admits float in export format | R3 | M2 |
| `ilc_core/ledger/canon_export_validate.py` | canon-export validation boundary | validator explicitly accepts `int` or `float` numeric values | R3 | M3 |
| `ilc_core/ledger/canon_export_bundle_validate.py` | bundle-export validation boundary | bundle validator permits float-bearing JSON scalar values | R3 | M3 |
| `ilc_core/ledger/canon_bundle_audit_artifact.py` | canon-bundle audit artifact surface | `JsonScalar` admits float in audit/export companion payloads | R3 | M2 |

The minimum required Tier-0 path classes are therefore present:
- balance and reward-bearing ledger runtime
- stake snapshot and settlement verification runtime
- persistent backends that serialize/load those values
- RC economic-cycle runtime
- validator staking/liveness runtime
- direct type contract surfaces
- directly coupled runtime export and validation companions

## 3. Risk classification

Risk classes for this strike-force lane are:

- `R1`: consensus/settlement/economic replay critical
  - applies where float arithmetic or epsilon logic can alter balance state,
    settlement share distribution, reward reconciliation, or replay verdicts
- `R2`: runtime-export or validator-state critical
  - applies where runtime-facing or validator-facing surfaces publish or accept
    numeric values whose representation must match the Tier-0 exact contract
- `R3`: adjacent or lower-risk Tier-0 companion
  - applies where the surface is not the primary state machine but still must be
    kept coherent with the exact representation contract

`tier0_risk_classes_defined`

The inventory classification above treats `backend.py`,
`stake_snapshot.py`, `settlement_verification.py`, LMDB/file persistence, and
`economic_cycle_runtime.py` as `R1` because they can directly change or verify
settled balances and reward totals. `staking_liveness_runtime.py`, `types.py`,
`ledger_export.py`, `canon_export.py`, and `ecu_active_layer_runtime.py` are
`R2` because they shape validator/runtime-facing state or public machine output.
The remaining export and audit companions are `R3`.

## 4. Migration-class grouping

Migration classes for this strike-force lane are:

- `M1`: internal state primitive replacement
  - replace float-bearing in-memory or persisted state primitives with the
    ratified exact representation
- `M2`: serialization/export contract update
  - update machine-legible payloads, export surfaces, and persistence contracts
    so they no longer canonically emit or assume float
- `M3`: validation/tolerance logic replacement
  - remove epsilon/rounding-based correctness checks and replace them with exact
    arithmetic or exact serialization rules

`tier0_migration_classes_defined`

Rows may carry more than one migration class when state, serialization, and
verification all need coordinated change. The highest-load-bearing group is:
- `backend.py`, `stake_snapshot.py`, `settlement_verification.py`,
  `lmdb_backend.py`, `persistent_backend.py`, and
  `economic_cycle_runtime.py`

That group proves this is not an export-only cleanup. Tier-0 contains all three
migration classes simultaneously.

## 5. CDL-064 opening rationale

`CDL-064` is required because the exact numeric boundary is not implementation-
local cleanup.

Changing Tier-0 numeric representation affects:
- machine-legible protocol outputs
- replay and settlement verification expectations
- persistence and export shapes
- cross-language implementation assumptions
- future public runtime surfaces that would otherwise inherit float-bearing
  contracts by accident

If this were treated as implementation-only cleanup, the repo would still have
no ratified answer for:
- what exact representation is canonical for Tier-0 economic values
- whether export surfaces may continue to emit float
- whether epsilon/rounding replay checks remain allowed
- what compatibility contract later runtimes and non-Python implementations must
  honor

That is why the constitutional vehicle is narrow but necessary.

`float_retention_not_acceptable_tier0_inventory_conclusion`

## 6. Forward pointer to prelock and simulation

Phase 633 must do three things:
- evaluate the representation options recorded in `CDL-064`
- convert the selected direction into prelock migration invariants
- run SIM-NUMERIC-01 so the representation choice is selected on evidence, not
  on habit or convenience

The prelock phase must explicitly evaluate and reject or select:
- `retain-float-rounding-and-tolerance`
- `exact-decimal-runtime-contract`
- `fixed-point-minor-unit-contract`

The Phase 632 conclusion is only that float retention is no longer acceptable
for Tier-0. The final representation choice remains open until prelock.

`window_631_636_moves_to_cdl_064_prelock`
