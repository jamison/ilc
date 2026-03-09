# ILC Phase 392-401 Sequence Lock v0.1

Status: Phase-392 sequence lock artifact
Date: 2026-03-09
Owner lane: G8 Constitution Cluster A

## 1. Window identity and scope

Window 392-401 is the Ratification Settlement and V-series Resolution Block.

This sequence lock binds the constitutional ratification track for CDL-040/CDL-041/CDL-043, the retention_epochs amendment lane, and the V-series governance/runtime continuation from Window 378-391 outputs.

## 2. Inputs and closure inheritance

Inherited closure state from Phase 391:
- CDL-039 is ratified.
- CDL-040, CDL-041, and CDL-043 are open prelock lanes.
- Window 392+ starts with a named forward obligation for retention_epochs amendment opening.

The first constitutional action of Window 392+ is opening the retention_epochs amendment required by CDL-039 ratification evidence and carried through Phase 391 handoff.

## 3. SIM-006/007 branch resolution

SIM-006 favorable branch is locked: recommended_panel_assignment_policy: diversity_weighted.

Phase 396 remains the CDL-V3/V7 governance authorization lock under the favorable SIM-006 branch; no unfavorable fallback branch is authorized in this artifact.

SIM-007 carry-forward to CDL-035 amendment lane is locked: recommended_orphan_timeout_epochs: 4; recommended_recovery_policy: stake_full_release.

## 4. Locked phase table (392-401)

| Order | Phase | Scope | Character |
| --- | --- | --- | --- |
| 1 | Phase 392 | Window sequence lock + retention_epochs amendment opening (CDL-044) | sensitive constitutional |
| 2 | Phase 393 | CDL-040 ratification | constitutional |
| 3 | Phase 394 | CDL-041 ratification | constitutional |
| 4 | Phase 395 | CDL-043 ratification | constitutional |
| 5 | Phase 396 | CDL-V3/V7 governance authorization lock (SIM-006 synthesis) | authorization |
| 6 | Phase 397 | CDL-V3 runtime implementation | runtime |
| 7 | Phase 398 | CDL-V7 runtime implementation | runtime |
| 8 | Phase 399 | CDL-044 retention_epochs evidence closure + ratification lane | constitutional |
| 9 | Phase 400 | Coherence + capsule v1.4 | synthesis |
| 10 | Phase 401 | Window closure gate + 402+ handoff | sensitive gate |

## 5. Constitutional first-action requirement

The first constitutional action of Window 392+ is opening the retention_epochs amendment required by CDL-039 ratification evidence and carried through Phase 391 handoff.

CDL-044 is opened in Phase 392 as a dedicated amendment row with bounded-range prelock framing; this window does not ratify the retention_epochs operational constant until evidence closes in the targeted Phase 399 lane.

## 6. Sequencing constraints and dependency ordering

CDL-040/041/043 ratifications must complete before CDL-042 opening.

D2e implementation remains deferred to Window 402+ pending CDL-042 opening.

CDL-044 remains additive to the existing constitutional register and does not authorize runtime mutation in this phase.

## 7. Deferred tracks and SIM-008 gate

Treasury governance CDL cluster and mandatory ECU conversion deadline CDL are explicitly deferred to Window 402+ and gated on SIM-008.

Window 392-401 is not authorized to open or ratify those economics CDLs.

## 8. Canonical anchors and non-goals

Canonical anchors:
- `docs/specs/ilc_window_378_391_handoff_391_v0.1.md`
- `docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md`
- `docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md`
- `docs/specs/ilc_sim_006_007_commissioning_results_386_v0.1.md`
- `docs/specs/ilc_window_392_413_candidate_phase_grouping_v0.1.md`

Non-goals in Phase 392:
- no ratification of CDL-044,
- no opening of CDL-042,
- no runtime mutation under `ilc_core/`.
