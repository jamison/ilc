# ILC Genesis 5% Long-Horizon Production-Path SIM 1575c-Fix3g v0.1

Status: complete
Date: 2026-07-16
Phase: 1575c-Fix3g
Owner lane: Block 6 / Genesis 5% economics hardening

## 1. Purpose

This artifact records a deterministic 480-epoch Genesis 5% simulation that extends the Phase 1575c-Fix3f retained rehearsal surface beyond three epochs while using the current production-candidate economics path.

The simulation is not a live settlement, not production minting, and not a future fee-volume prediction. It is a current-code replay over a bounded gross-fee scenario grid.

## 2. Current Code Surfaces Exercised

The SIM drives the following current repo surfaces:

| Surface | Path | Role |
|---|---|---|
| Production-candidate emission path | `ilc_core/epoch/epoch_emission_production_path.py` | Computes emission quote, fee burn, allocation quote, governor report, and settlement root |
| CDL-028 fee burn | `ilc_core/epoch/fee_burn_split_runtime.py` | Applies 10% fee burn |
| CDL-029 allocation | `ilc_core/epoch/allocation_distributor_runtime.py` | Applies 80/15/5 post-burn allocation split |
| Genesis governor | `ilc_core/analysis/genesis_accrual_governor.py` | Computes Cmax-based ratio, taper report, and cap block |
| Genesis destination binding | `ilc_core/epoch/genesis_settlement_destination.py` | Verifies Genesis Agent 1 binding and default-off write guards |
| Genesis tranche reconciliation | `ilc_core/epoch/genesis_tranche_reconciliation_runtime.py` | Verifies CDL-048 treatment and destination token flow |

## 3. Scenario Grid

| Field | Value |
|---|---:|
| Horizon | `480` monthly epochs |
| Scenario count | `101` |
| Gross epoch fee minimum | `600,000 ILC` |
| Gross epoch fee maximum | `2,400,000 ILC` |
| Scenario type | Constant gross epoch fee sweep |
| Genesis target | `1,296,000 ILC` |
| Denominator | `C_max = 25,920,000 ILC` |

The grid is intentionally simple: it isolates current-code economics mechanics from market forecasting.

## 4. Results

Committed machine-readable evidence:

`docs/specs/ilc_genesis_5pct_long_horizon_production_path_sim_1575c_fix3g_v0.1.json`

Local replay output:

`out/genesis_5pct_long_horizon_production_path_sim_1575c_fix3g/sim_evidence.json`

Evidence SHA-256:

```text
86770147cc780da5be5ed902c8a812d80ed7ca3ad2757b8f1daced5c7407e1f1
```

Reach summary:

| Metric | Epoch |
|---|---:|
| Reach count | `101 / 101` |
| Not reached | `0 / 101` |
| p10 reach `G_max` | `13` |
| p50 reach `G_max` | `20` |
| p90 reach `G_max` | `37` |

Representative scenarios:

| Scenario | Gross fees / epoch | Reach epoch | Final Genesis cumulative |
|---:|---:|---:|---:|
| 0 | `600,000 ILC` | `48` | `1,296,000 ILC` |
| 50 | `1,500,000 ILC` | `20` | `1,296,000 ILC` |
| 100 | `2,400,000 ILC` | `12` | `1,296,000 ILC` |

## 5. Current-Code Findings

The SIM records two important implementation facts after Phase 1575c-Fix3h:

| Finding | Result | Disposition |
|---|---:|---|
| `taper_multiplier_is_reported_but_not_applied_to_pre_cap_allocation` | `true` | The current production path uses the governor for `cap_blocked`, but the taper multiplier does not reduce the Genesis overhead allocation before cap |
| `partial_cap_epoch_requires_residual_routing` | `false` | Closed by Phase 1575c-Fix3h. The cap-reaching epoch now clamps Genesis to the remaining fixed-tranche allowance |
| `partial_cap_excess_to_performer_pool_scenario_count` | `98` | The `98 / 101` scenarios that previously over-quoted Genesis now route the partial-cap excess to the performer pool fallback |

These are not SIM failures. They separate the closed partial-cap routing rule from the remaining design observation: whether the intended model is "5% until hard cap" or "sigmoid taper applied to the allocation amount before hard cap." The current runtime implements the former: Genesis accrues the 5% overhead until the hard cap, the final epoch is clamped exactly to the remaining allowance, and any excess routes to the performer pool fallback.

## 6. Cap Probe

Every scenario performs a zero-fee cap probe immediately after reaching `G_max`.

The cap probe verifies:

- `cap_blocked = true`
- `genesis_overhead_pool_ilc = 0`
- settlement root construction remains deterministic
- no wallet, minting, treasury, or settlement write guard is cleared

## 7. Non-Claims

This phase does not activate production minting, wallet writes, treasury writes, live settlement, public RC, public P2P, or an epoch transition.

This phase does not predict real public-RC fee volume.

This phase does not close the taper-design question. It makes the current-code behavior explicit so the next decision can be made on evidence.

## 8. Verification

Focused tests:

```text
.venv/bin/python -m pytest tests/test_phase_1575c_fix3g_genesis_long_horizon_sim.py -q
```

Adjacent economics tests:

```text
.venv/bin/python -m pytest \
  tests/test_phase_1573ac_canonical_genesis_accumulation_sim.py \
  tests/test_phase_600_deterministic_genesis_economics_evidence_and_parameter_closure.py \
  tests/test_phase_1573ab_genesis_accrual_governor_cmax_fix.py \
  tests/test_phase_1575c_fix3c_genesis_governor_decimal_migration.py \
  tests/test_phase_1575c_fix3d_genesis_governor_wiring.py \
  tests/test_phase_1575c_fix3e_genesis_destination_binding.py \
  tests/test_phase_1575c_fix3f_genesis_retained_rehearsal.py \
  -q
```

Required output tokens:

- `genesis_5pct_long_horizon_production_path_sim_committed_phase_1575c_fix3g`
- `genesis_5pct_current_code_reaches_cap_in_all_scenarios_phase_1575c_fix3g`
- `genesis_taper_reported_not_applied_recorded_phase_1575c_fix3g`
- `genesis_partial_cap_residual_routing_gap_closed_phase_1575c_fix3h`
