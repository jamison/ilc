# ILC SIM-003/004/005 Interpretation and CDL-039 Risk Closure 371 v0.1

Status: Phase-371 interpretation artifact  
Date: 2026-03-06  
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

This artifact interprets Phase-365/369/370 simulation outputs for CDL-039 prelock drafting and closes interpretation-risk gaps required before Phase 372.

Modeled outputs are non-ratifying evidence inputs.

Boundary statements:
- no decision-log mutation,
- no runtime mutation,
- no simulation-output regeneration.

## 2. Input inventory and manifest provenance

Primary evidence inputs:
- `docs/specs/ilc_sim_001_002_003_commissioning_results_365_v0.1.md`
- `docs/specs/ilc_sim_004_partition_resilience_commissioning_results_369_v0.1.md`
- `docs/specs/ilc_sim_005_agent_death_orphaning_commissioning_results_370_v0.1.md`
- `out/simulations/sim_003_graph_growth/run_manifest.json`
- `out/simulations/sim_004_partition_resilience/run_manifest.json`
- `out/simulations/sim_005_agent_death_orphaning/run_manifest.json`

Manifest-level provenance anchors:
- SIM-003 digest: `37cc447f08bf51bab2e8ec2973435c026bd4718cee9c65b7491ea9c6b5d88dae`
- SIM-004 digest: `399e76966bcd786b9b93dddfdf2279031a04f99b6f271d9f28b10a0bb12e810a`
- SIM-005 digest: `391b0c97c26444d8b8d47a262e5edf91a1796bfe52a54c88a08bd1127983f069`

## 3. SIM taxonomy table (canonical numbering and scope)

SIM taxonomy resolved for current window: SIM-003 graph growth pressure, SIM-004 partition resilience, SIM-005 agent death and orphaning.

| SIM | Canonical scope used in Window 368-377 | Evidence source | Drift note |
| --- | --- | --- | --- |
| SIM-003 | Graph growth and storage-pressure pruning policy | Phase 365 outputs | No drift |
| SIM-004 | Network partition divergence and reconciliation behavior | Phase 369 outputs | No drift |
| SIM-005 | Agent death/orphaning timeout and recovery-policy behavior | Phase 370 outputs | Historical docs also used SIM-005 for epoch timing attack-surface; current window uses SIM-005 as orphaning model |

Canonical resolution for Phase 372 inputs:
- Phase 372 shall consume SIM-003/004/005 meanings from this table.
- Any legacy SIM numbering in older planning notes is superseded by this Phase-371 interpretation table for current-window prelock work.

## 4. Epoch-type interpretation table (SIM-003, SIM-004, SIM-005)

SIM-004 epoch context: issuance_epoch (1 month).

SIM-005 epoch context: validation_epoch (1 minute).

SIM-003 epoch interpretation is declared explicitly for retention and snapshot semantics.

| SIM | Epoch type | Epoch duration | Source basis | Parameter interpretation |
| --- | --- | --- | --- | --- |
| SIM-003 | issuance_epoch | 1 month | Issuance schedule canonicalization (`CDL-027`) and graph-pruning context across multi-epoch state growth | `retention_epochs=1` means 1 month retention; `snapshot_interval=50` means 50 months snapshot cadence |
| SIM-004 | issuance_epoch | 1 month | `run_manifest.json` epoch_context + partition divergence consensus framing | `minimum_divergence_partition_duration_epochs=34` means 34 months |
| SIM-005 | validation_epoch | 1 minute | `run_manifest.json` epoch_context and liveness-timeout semantics | `recommended_timeout_epochs=2` means 2-minute liveness timeout |

## 5. Wall-clock conversions and operational semantics

Wall-clock conversion anchors used for Phase 372 drafting:
- SIM-003: `retention_epochs=1` -> 1 month; `snapshot_interval=50` -> approximately 4.17 years.
- SIM-004: `T_safe=34` -> approximately 2.8 years; threshold exceedance first observed at `T=50` -> approximately 4.2 years.
- SIM-005: `timeout_epochs=2` -> 2 minutes under validation-epoch assumption.

Operational semantics:
- SIM-003 controls long-horizon storage/pruning pressure and should not be interpreted as minute-scale runtime tuning.
- SIM-004 constrains long-horizon partition reconciliation behavior and informs issuance-epoch consensus hardening.
- SIM-005 constrains short-horizon liveness semantics and informs timeout/fairness policy at validation timescale.

## 6. Constant lock/readiness flags for Phase 372 and Phase 373

### Interpretation-locked for Phase 372 drafting

| Constant / claim | Status | Rationale |
| --- | --- | --- |
| SIM-003 uses issuance-epoch interpretation | Locked | Required for coherent reading of retention and snapshot recommendations |
| SIM-004 uses issuance-epoch interpretation | Locked | Manifest-declared and consistent with partition-consensus semantics |
| SIM-005 uses validation-epoch interpretation | Locked | Manifest-declared and consistent with liveness timeout semantics |
| `highest_ecu_wins` as reconciliation baseline candidate | Locked for baseline evaluation | SIM-004 consistently ranks it as lowest-conflict reconciliation rule |
| Two-timescale CDL-039 framing | Locked | Required to separate liveness and long-horizon partition concerns |

### Calibration-required for Phase 373 adversarial review

| Parameter / question | Status | Phase-373 role |
| --- | --- | --- |
| `R_partition_cross_ref` cross-cluster reference cap | Calibration-required | Stress-test range and anti-flap behavior |
| `H_release` hysteresis release threshold | Calibration-required | Prevent partition-state flapping abuse |
| Private-node `retention_epochs` constant used for expiry invariants | Calibration-required | Must account for CDL-038 scope and operational fairness |
| Final timeout policy binding from SIM-005 (`timeout_epochs`, recovery policy) | Calibration-required | Validate false-positive/false-negative risk under adversarial network behavior |

## 7. CDL-039 two-timescale design closure

short-timescale CDL-039 context: validation epoch liveness and Levin stress-cascade reconnection handling.

long-timescale CDL-039 context: issuance epoch partition divergence and highest_ecu_wins reconciliation.

Closure statement:
- CDL-039 prelock must explicitly separate liveness-timeout controls (minute-scale) from partition-consensus reconciliation controls (month-scale).
- A single undifferentiated epoch assumption is prohibited for Phase 372 prelock text.

## 8. Carry-forward constraints for Phase 372

Phase 372 consumes invariant shape and interpretation-locked constants only.

Required Phase-372 carry-forward constraints:
- consume taxonomy table from Section 3 as canonical SIM meaning,
- consume epoch-interpretation table from Section 4 without redefining epoch types,
- include two-timescale CDL-039 closure from Section 7,
- maintain non-ratifying boundary.

## 9. Carry-forward constraints for Phase 373

Phase 373 calibrates unresolved parameter constants under adversarial review.

Required Phase-373 carry-forward constraints:
- quantify `R_partition_cross_ref` and `H_release` under noisy partition-state conditions,
- adversarially evaluate timeout/recovery parameter safety bounds from SIM-005,
- test cluster-membership non-inferrability and opaque-channel leakage risks,
- freeze only constants with successful adversarial evidence.

## 10. Non-goals and open questions

Non-goals:
- no CDL-039 ratification in Phase 371,
- no runtime changes,
- no simulation reruns.

Open questions carried forward:
- CDL-038 scope boundary for post-expiry promotion recovery semantics,
- whether SIM-004 crossover precision requires a narrower sweep before final CDL-039 constant binding,
- final timeout and recovery constants pending adversarial calibration.

No decision-log mutation occurred. No ilc_core runtime files were changed.
