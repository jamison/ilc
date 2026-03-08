# ILC SIM-006/007 Commissioning Results 386 v0.1

Status: commissioned (non-ratifying evidence)  
Date: 2026-03-08  
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

Phase 386 commissions SIM-006 and SIM-007 as deterministic planning evidence for downstream governance and wire-spec work.

Modeled outputs are non-ratifying evidence inputs.

No decision-log mutation occurred. No ilc_core runtime files were changed.

## 2. Capability-vector vocabulary assessment and parameterization decision

SIM-006 capability_vector vocabulary precondition was evaluated during commissioning; placeholder tiers are used only when canonical vocabulary remains undefined.

Canonical sources checked:
- `docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md`
- `docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_prelock_383_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`

Result:
- explicit Tier-0/Tier-1/Tier-2 vocabulary was not defined in canonical inputs,
- SIM-006 used placeholder tiers:
  - Tier-0 = unclassified
  - Tier-1 = moderate
  - Tier-2 = expert
- this decision is captured in `out/simulations/sim_006_panel_effectiveness/run_manifest.json`.

## 3. Implemented simulation modules

- `simulations/sim_006_panel_effectiveness_386.py`
- `simulations/sim_007_agent_churn_orphan_accumulation_386.py`
- `simulations/run_phase_386_sim_006_007.py`

## 4. Output artifacts and reproducibility

Outputs are written under:
- `out/simulations/sim_006_panel_effectiveness/`
- `out/simulations/sim_007_agent_churn_orphan_accumulation/`

Each root includes:
- `results.csv`
- `results.tsv`
- `summary_table.md`
- `requirements_summary.md`
- `run_manifest.json`

Determinism properties:
- fixed seeds (`386006`, `386007`),
- fixed parameter grids,
- stable sorted output ordering,
- hash-stable artifacts on rerun.

## 5. SIM-006 result summary

SIM-006 evaluates panel effectiveness under capability heterogeneity across profile mixes, claim-complexity tiers, outsider evidence quality, and review-window lengths.

Primary output:
- `recommended_panel_assignment_policy: diversity_weighted`

Interpretation:
- diversity-weighted assignment balances false-accept suppression and convergence rounds across heterogeneous capability profiles,
- outsider evidence quality materially shifts false-accept rates,
- capability-tier conditioning is useful even under placeholder vocabulary.

## 6. SIM-007 result summary

SIM-007 evaluates churn-driven orphan accumulation across monthly churn rates, timeout windows, reconnect windows, replication factors, and stake-recovery policies.

Primary outputs:
- `recommended_orphan_timeout_epochs: 4`
- `recommended_recovery_policy: stake_full_release`

Interpretation:
- longer issuance-epoch timeout windows reduce spurious timed_out transitions under churn,
- recovery-policy choice affects backlog pressure and reconnect stability,
- churn controls are load-bearing inputs for timed_out extension planning.

## 7. Carry-forward constraints for Phase 387 and Phase 390

SIM-006 and SIM-007 outputs feed CDL-V7 extension planning, D2d-10/11 wire-spec planning, and CDL-035 timed_out extension planning.

SIM-006 epoch context is validation_epoch and SIM-007 epoch context is issuance_epoch.

Carry-forward boundaries:
- SIM outputs do not mutate constitutional state,
- SIM outputs do not calibrate CDL-040, CDL-041, or CDL-043 prelocks,
- Phase 387 should cite these results as governance/planning evidence only,
- Phase 390 capsule v1.3 should record SIM-006/007 readiness and unresolved governance items for CDL-V3/V7.

## 8. Non-goals

- no CDL ratification,
- no runtime module implementation,
- no decision-log edits,
- no `ilc_core/` changes.
