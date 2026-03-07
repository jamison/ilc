# ILC CDL-043 Storage Economics Prelock 385 v0.1

Status: prelock evidence (open, non-ratifying)  
Date: 2026-03-07  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact opens CDL-043 and records prelock evidence for storage economics, graph pruning policy, and active-graph retention constraints with constitutional and documentation boundaries only.

## 2. CDL-043 opening state

- decision id: `CDL-043`
- status: open
- phase: 385
- ratification: deferred

No runtime implementation occurs in Phase 385.

## 3. Non-centralization constraint basis

CDL-043 storage economics must not create resource-concentration incentives incompatible with CDL-V3's cluster diversity floor or CDL-V2's sybil resistance requirements; pruning parameters that could systematically advantage large-stake clusters over small-stake clusters require explicit justification against these ratified constraints.

## 4. CDL-042 deferral and sequencing note

CDL-043 is opened directly after CDL-041; CDL-042 (agent identity namespace) is deferred to Window 392+ pending CDL-039/040 scope resolution.

## 5. Calibration constants and exclusivity boundary

CDL-043 storage economics prelock treats SIM-003 outputs as authoritative calibration evidence: ecu_score_floor=0.5, retention_epochs=1, snapshot_interval=50.

Prelock calibration parameters for CDL-043 are tracked in this section only:
- `ecu_score_floor` - evidence-aligned baseline and candidate bounded range under ratification review
- `retention_epochs` - evidence-aligned baseline and forward constitutional action dependency under ratification review
- `snapshot_interval` - evidence-aligned baseline and candidate bounded range under ratification review

## 6. Ratification-lane carry-forward notes

- Ratification may lock constants directly or preserve bounded candidates with explicit rationale.
- Any retained retention-window ambiguity must be surfaced as a named constitutional follow-up action.
- No computational/runtime enforcement is authorized in this phase.

## 7. Deferral and phase-boundary constraints

- Phase 385 is opening/prelock only.
- No CDL-043 ratification action occurs in this phase.
- No CDL-042 opening action occurs in this phase.
- Any runtime implementation is deferred to a later authorized runtime window.

## 8. Canonical anchors

- `docs/specs/ilc_sim_001_002_003_commissioning_results_365_v0.1.md`
- `docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md`
- `docs/specs/ilc_cdl_041_shard_lifecycle_prelock_384_v0.1.md`
- `docs/specs/ilc_phase_378_391_sequence_lock_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
