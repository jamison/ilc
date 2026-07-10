# ILC Genesis Accumulation Canonical SIM 1573ac v0.1

Status: locked
Date: 2026-07-10
Phase: 1573ac
Owner lane: Block 6 / issuance economics SIM

## 1. Purpose

This artifact records the Phase 1573ac canonical Genesis accumulation simulation package. It converts the Phase 305 checklist into committed, reproducible evidence using the corrected C_max denominator from CDL-029 Amendment 2 and the Phase 1573ab governor runtime.

## 2. Canonical Constants

| Constant | Value | Class | Anchor |
|---|---:|---|---|
| `C_max` | `25,920,000 ILC` | Canonical | CDL-026 |
| `theta_hard` | `0.05` | Canonical | CDL-029 |
| `G_max` | `1,296,000 ILC` | Derived | `0.05 * C_max` |
| Halving schedule `H` | `48` issuance epochs | Canonical | CDL-027 |
| Issuance epoch duration | `1 month` | Canonical | CDL-027 |
| Allocation split | `80 / 15 / 5` | Canonical | CDL-029 |
| Governor runtime | `genesis_accrual_governor_runtime_1573ab.v0.1` | Implemented | Phase 1573ab |

## 3. Derived Arithmetic

- `G_max = theta_hard * C_max = 0.05 * 25,920,000 = 1,296,000 ILC`.
- The H=48 monthly issuance schedule is modeled over 480 epochs.
- The epoch-zero finite-horizon issuance budget is derived from the geometric series with `q = 2^(-1/48)` and finite horizon sum equal to `C_max`.

## 4. Mode Declaration

This simulation uses `theoretical_cap_cmax_denominator`: the Genesis share ratio denominator is `C_max` per CDL-029 Amendment 2 and Phase 1573ab.

The older `issued_to_date` denominator mode is explicitly superseded for this canonical SIM. It remains historical sensitivity context only and must not be used as the current Genesis share-ratio denominator.

## 5. Deterministic Output Summary

Script: `simulations/sim_genesis_accumulation_canonical_1573ac.py`

Committed machine-readable output: `docs/specs/ilc_genesis_accumulation_canonical_sim_1573ac_v0.1.json`

Local replay output: `out/phase_1573ac_genesis_accumulation_canonical_sim.json`

Fixed seed declaration: `phase_1573ac_grid_v1_no_prng`

Scenario grid:

| Field | Value |
|---|---:|
| Scenario count | `101` |
| Genesis subsidy factor min | `1.85` |
| Genesis subsidy factor max | `5.30` |
| Genesis subsidy factor step | `0.0345` |

Reach summary:

| Metric | Epoch | Wall-clock interpretation |
|---|---:|---|
| p10 reach `G_max` | `15` | approximately 15 months |
| p50 reach `G_max` | `22` | approximately 22 months |
| p90 reach `G_max` | `42` | approximately 42 months |

All `101 / 101` scenarios reached `G_max` within the 480-epoch horizon.

Canonical output hash:

```text
47b4efc5db83916a00b1ec71e86412613b9f5801212312eaa76a333b2ecd6d2f
```

## 6. Assumption Registry

| Label | Assumption | Value | Anchor |
|---|---|---:|---|
| Canonical | `C_max` | `25,920,000` | CDL-026 |
| Canonical | `H` | `48` | CDL-027 |
| Canonical | allocation split | `80/15/5` | CDL-029 |
| Derived | `G_max` | `1,296,000` | `0.05 * C_max` |
| Exploratory | Genesis subsidy factor grid | `1.85..5.30` | Phase 1573ac deterministic sensitivity grid |

## 7. External-Communication-Safe Claims

It is safe to say that Phase 1573ac produced a committed, deterministic Genesis accumulation SIM using the corrected C_max denominator and that the bounded scenario grid reaches the fixed Genesis tranche with p10/p50/p90 epochs of `15 / 22 / 42`.

It is not safe to present the p10/p50/p90 values as guaranteed production timelines, active settlement behavior, public-tokenomics law, or a promise that production issuance is live.

## 8. Phase 305 Checklist Disposition

- Canonical simulation script: satisfied by `simulations/sim_genesis_accumulation_canonical_1573ac.py`.
- Reproducible output package: satisfied by `out/phase_1573ac_genesis_accumulation_canonical_sim.json` and the hash above.
- Contract tests: satisfied by `tests/test_phase_1573ac_canonical_genesis_accumulation_sim.py`.
- Walkthrough and STATUS update: satisfied by the Phase 1573ac walkthrough and STATUS tokens.
- Mode-qualified trajectory table: satisfied by the C_max mode declaration and reach summary above.
- Assumption registry: satisfied by Section 6.

## 9. Residual Open Questions

- The Genesis subsidy factor grid is exploratory and is not a ratified protocol constant.
- This phase does not implement a Genesis-only ECU realization controller.
- This phase does not activate production issuance, minting, wallet writes, settlement, public RC, Genesis signing, or public P2P.
- Any external public-tokenomics statement must retain denominator mode, assumption labels, and non-activation boundaries.
