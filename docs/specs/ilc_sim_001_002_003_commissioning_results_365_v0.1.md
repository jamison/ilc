# ILC SIM-001/002/003 Commissioning Results 365 v0.1

Status: Phase-365 simulation commissioning artifact
Date: 2026-03-05
Phase: 365

## 1. Scope and non-ratifying boundary

Phase 365 commissions deterministic simulation execution for `SIM-001`, `SIM-002`, and `SIM-003` as specified in `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`.

This artifact is non-ratifying and non-runtime. No decision-log mutation occurred. No `ilc_core/` runtime files were changed.

## 2. Implemented simulation modules

Implemented scripts:
- `simulations/sim_001_bootstrap_threshold_365.py`
- `simulations/sim_002_micro_agent_cost_floor_365.py`
- `simulations/sim_003_graph_growth_storage_pressure_365.py`
- `simulations/run_phase_365_simulations.py`

Deterministic seeds:
- `SIM-001`: `365001`
- `SIM-002`: `365002`
- `SIM-003`: `365003`

## 3. Output artifacts and reproducibility

Output roots:
- `out/simulations/sim_001_bootstrap_threshold/`
- `out/simulations/sim_002_micro_agent_economics/`
- `out/simulations/sim_003_graph_growth/`

Each output root contains:
- `results.csv`
- `results.tsv`
- `summary_table.md`
- `run_manifest.json`

Each `run_manifest.json` contains deterministic parameter grid declarations, key metrics, artifact hashes, and a stable result digest.

## 4. SIM-001 result summary (bootstrap threshold)

Key outputs:
- minimum viable `N_agents` under thresholds (`signal>=0.65`, `TP>=0.95`, `FP<=0.05`): `10000`
- qualifying claim rate for the canonical lane: `claims_per_epoch=3`
- evaluated rows: `275`

Interpretation boundary:
- this result is a launch-readiness modeling signal for planning only,
- it does not by itself authorize constitutional threshold changes.

## 5. SIM-002 result summary (micro-agent cost floor)

Key outputs:
- participation cliff ratio across modeled profiles: `0.977778`
- recommended upper bound for `write_fee_multiplier` (within tested sweep): `<= 0.5`
- evaluated rows: `810`

Interpretation boundary:
- this result is evidence input for future write-fee constitutional bound discussion,
- it does not mutate existing fee CDLs.

## 6. SIM-003 result summary (graph growth and storage pressure)

Key outputs:
- claim-rate lanes derived from SIM-001: `[10000, 30000, 100000]`
- recommended pruning policy (within tested sweep):
  - `ecu_score_floor=0.5`
  - `retention_epochs=1`
  - `snapshot_interval=50`
- recommended annual storage cost under selected policy (modeled): `0.273702` USD
- evaluated rows: `576`

Interpretation boundary:
- this result is evidence input for future pruning/storage CDL work,
- it does not authorize pruning-policy runtime changes in this phase.

## 7. Carry-forward constraints for phase 366

Phase 366 coherence and capsule work must:
- interpret these simulation results explicitly against the three planning questions:
  - launch threshold from SIM-001,
  - write-fee bound direction from SIM-002,
  - pruning policy direction from SIM-003,
- preserve non-ratifying boundaries,
- keep `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md` as an open planning anchor.

## 8. Non-goals

This phase did not:
- change `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- change `ilc_core/` runtime modules,
- produce notebook artifacts,
- produce binary outputs,
- ratify any CDL rows.
