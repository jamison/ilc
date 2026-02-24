# ILC Historical Simulation Recovery Index (Subjective/Objective + Sybil) v0.1

Status: non-normative recovery index  
Date: 2026-02-23  
Primary source corpus: `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt`

## 1. Purpose

Index simulation work from historical chats and map each item to:
- recovered script artifact,
- active simulation in current repo,
- current status (replayable now vs still needs reconstruction).

## 2. Historical simulation anchors from 2025_11_12 thread

| Theme | Historical line anchors | Historical artifact names in thread | Repo mapping | Status |
|---|---|---|---|---|
| A5 subjective-node gating policies (`OFF`, `CONSERVATIVE`, `HYBRID`) | `:8730-8767`, `:9119-9123` | `a5_subjective_gating_summary.csv`, `a5_off_epoch.csv`, `a5_conservative_epoch.csv`, `a5_hybrid_epoch.csv` | `simulations/sim_subjective_gating_pb_gaming.py` (conceptual successor) | partial (historical exact CSV set not yet replayed) |
| Broadcast/epistemic-type policy hooks | `:2701`, `:2710`, `:2796` | policy equations + schema additions | no single dedicated replay script yet | open |
| Controller telemetry 80-epoch run | `:6120-6132`, `:6137-6138`, `:6377`, `:6386` | `telemetry_80_epoch_trace.csv`, `telemetry_80_summary.csv` | `simulations/historical_recovered/sim_controller_telemetry_80_epoch_recovered_20251009.py` | recovered (path adaptation needed) |
| Kappa A/B normal + stressed | `:6993-6996`, `:7192-7194` | `kappa_*_epoch.csv`, `kappa_ab_summary.csv` | `simulations/historical_recovered/sim_kappa_ab_recovered_20251009.py` | recovered (path adaptation needed) |
| Cartel/Sybil stress continuation | `:10315`, `:10392`, `:13357` | stress-follow-up requests + sponsor-root logic intent | `tests/test_sybil_defense.py` + reuse-diversity suite | partial (core defense exists; stress sim lane not fully reconstructed) |

## 3. Active simulation and test assets already in repo

### 3.1 Subjective/objective and reward behavior

- `simulations/sim_subjective_gating_pb_gaming.py`
- `tests/test_sim_subjective_gating_pb_gaming.py`
- `simulations/sim_ecu_beta_theta_fairness.py`
- `tests/test_sim_ecu_beta_theta_fairness.py`
- `simulations/sim_burn_pb_grid.py`
- `tests/test_sim_burn_pb_grid.py`

Current generated outputs present locally:
- `out/phase_63b/subjective_gating_pb_gaming.csv`
- `out/phase_63a/ecu_beta_theta_fairness.csv`
- `out/phase_64e/burn_pb_grid.csv`

### 3.2 Sybil and anti-gaming protections

- `docs/specs/ilc_reuse_diversity_anti_sybil_contract_v0.1.md`
- `tests/test_sybil_defense.py`
- `tests/test_reuse_diversity_invariants_phase_216.py`
- `tests/test_reuse_diversity_invariants_gate_phase_216.py`

## 4. Recovery gaps (high-value)

1) Reconstruct exact A5 historical sweep outputs (`a5_*`) as deterministic local scripts + CSV outputs.
2) Add one dedicated simulation for sponsor-root Sybil swarm stress (independence collapse under shared sponsor roots).
3) Add one simulation for citation-loop/collusion ring reward extraction and diversity-penalty containment.

## 5. Recommended execution order

1. Path-adapt and replay recovered scripts under `simulations/historical_recovered/`.
2. Publish replay outputs under `out/recovered_20251009/` with checksums.
3. Implement missing A5 replay harness with deterministic seed and explicit policy variants.
4. Publish a consolidated evidence note linking:
- historical line anchors,
- replay scripts,
- output CSVs/JSON,
- pass/fail against Sybil-resilience acceptance criteria.
