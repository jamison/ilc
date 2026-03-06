# ILC SIM-004 Partition Resilience Commissioning Results 369 v0.1

Status: Phase-369 simulation commissioning artifact  
Date: 2026-03-06  
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

This artifact records the implementation and output interpretation of SIM-004 for Window 368-377 governance-first work.

Modeled outputs are non-ratifying evidence inputs.

## 2. Implemented simulation modules

Implemented modules:
- `simulations/sim_004_partition_divergence_369.py`
- `simulations/run_phase_369_sim_004.py`

Output root:
- `out/simulations/sim_004_partition_resilience/`

## 3. Output artifacts and reproducibility

Generated artifacts:
- `out/simulations/sim_004_partition_resilience/results.csv`
- `out/simulations/sim_004_partition_resilience/results.tsv`
- `out/simulations/sim_004_partition_resilience/summary_table.md`
- `out/simulations/sim_004_partition_resilience/requirements_summary.md`
- `out/simulations/sim_004_partition_resilience/run_manifest.json`

Deterministic run parameters:
- `seed=369004`
- `model_version=sim_004_partition_divergence_369.v0.1`
- result digest: `399e76966bcd786b9b93dddfdf2279031a04f99b6f271d9f28b10a0bb12e810a`

## 4. SIM-004 result summary

Primary modeled outputs:
- minimum-divergence partition duration (under conflict threshold `0.18`): `34` epochs
- maximum modeled conflict rate in sweep: `0.569174`
- recommended reconciliation rule from model sweep: `highest_ecu_wins`

Observed trend:
- conflict rate increases monotonically with partition duration and cross-partition reference pressure,
- conflict remains tractable through medium partition durations but exceeds threshold at long durations (`T=50`).

## 5. Explicit CDL-039 design requirements derived from modeled outputs

Derived requirements for CDL-039 prelock hardening:
- partition-tolerant epoch consensus required
- reconnection policy must bound conflict-reconciliation load under partition duration T
- cross-partition reference reconciliation must be deterministic and auditable

## 6. Carry-forward constraints for Phase 372

Carry-forward constraints:
- Phase 372 must treat this output as design evidence for topology and reconnection policy hardening, not as ratification.
- Levin stress-cascade reconnection mechanism remains a candidate design input for Phase 372 CDL-039 topology/privacy hardening.
- Recommended reconciliation baseline for evaluation is `highest_ecu_wins`, with adversarial comparison against alternative rules preserved.

## 7. Non-goals

Out of scope for Phase 369:
- CDL mutation or ratification actions,
- D2d runtime implementation,
- protocol-constant locking for reconnection policy.

No decision-log mutation occurred. No ilc_core runtime files were changed.
