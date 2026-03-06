# ILC SIM-005 Agent Death and Graph Orphaning Commissioning Results 370 v0.1

Status: Phase-370 simulation commissioning artifact  
Date: 2026-03-06  
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

This artifact records the implementation and output interpretation of SIM-005 for Window 368-377 governance-first work.

Modeled outputs are non-ratifying evidence inputs.

## 2. Implemented simulation modules

Implemented modules:
- `simulations/sim_005_agent_death_orphaning_370.py`
- `simulations/run_phase_370_sim_005.py`

Output root:
- `out/simulations/sim_005_agent_death_orphaning/`

## 3. Output artifacts and reproducibility

Generated artifacts:
- `out/simulations/sim_005_agent_death_orphaning/results.csv`
- `out/simulations/sim_005_agent_death_orphaning/results.tsv`
- `out/simulations/sim_005_agent_death_orphaning/summary_table.md`
- `out/simulations/sim_005_agent_death_orphaning/requirements_summary.md`
- `out/simulations/sim_005_agent_death_orphaning/run_manifest.json`

Deterministic run parameters:
- `seed=370005`
- `model_version=sim_005_agent_death_orphaning_370.v0.1`
- result digest: `391b0c97c26444d8b8d47a262e5edf91a1796bfe52a54c88a08bd1127983f069`

## 4. SIM-005 result summary

Primary modeled outputs:
- recommended timeout policy minimizing weighted orphan pollution and fairness loss: `timeout_epochs=2`
- recommended stake recovery policy from policy sweep: `full`
- maximum modeled orphaned-claim rate: `0.34`
- maximum modeled unresolved orphan backlog rate: `0.338368`

Observed trend:
- orphan backlog rises with longer timeout horizons and lower liveness probe cadence,
- death-rate and claim-pressure increases amplify orphan accumulation,
- fairness loss is strongly reduced by recovery policy support.

## 5. Explicit CDL-039 design requirements derived from modeled outputs

Derived requirements for CDL-039 prelock hardening:
- agent-death semantics must include deterministic claim-timeout event handling
- orphaned claims require explicit timed_out transition semantics after timeout horizon
- stake recovery for orphaned claims must be policy-defined and auditable

## 6. Carry-forward constraints for Phase 372

Carry-forward constraints:
- Phase 372 must treat this output as design evidence for liveness and timeout semantics, not as ratification.
- liveness probe cadence remains a candidate design input for Phase 372 CDL-039 topology/privacy hardening.
- Recommended timeout baseline for adversarial evaluation is `timeout_epochs=2`.

## 7. Non-goals

Out of scope for Phase 370:
- CDL mutation or ratification actions,
- D2d runtime implementation,
- protocol-constant locking for timeout and stake recovery policy.

No decision-log mutation occurred. No ilc_core runtime files were changed.
