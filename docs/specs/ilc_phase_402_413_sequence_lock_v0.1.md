# ILC Phase 402-413 Sequence Lock v0.1

Status: Phase-402 sequence lock artifact
Date: 2026-03-13
Owner lane: G8 Constitution Cluster A

## 1. Window identity and scope

Window 402-413 is the Constitutional Expansion and D2e First Block.

This sequence lock binds the first constitutional expansion lane after Window 392-401 closure: CDL-042 opening, CDL-045 opening, CDL-035 timed_out amendment planning, SIM-008 commissioning, the D2e first runtime block, and the closure obligations for the next synthesis and gate phases.

## 2. Inputs and closure inheritance

Inherited closure state from Phase 401:
- CDL-039 is ratified.
- CDL-040 is ratified.
- CDL-041 is ratified.
- CDL-043 is ratified.
- CDL-044 is ratified.
- Window 392-401 closure verified the node-schema ratification track, the retention-epochs amendment closure, and the ADM-003 signing-interface carry-forward.

CDL-040, CDL-041, CDL-043, and CDL-044 are ratified; the node-schema ratification track and retention-epochs amendment are closed as of Window 392-401.

## 3. V-series carry-forward and SIM carry-forward

CDL-V1, CDL-V2, CDL-V3, and CDL-V7 runtime lanes are implemented and carry forward without further V-series governance action in this window.

Phase 406 is SIM-008 commissioning and is not a V-series governance or runtime slot.

SIM-007 calibration is carried to Phase 405 for the CDL-035 timed_out amendment lane: recommended_orphan_timeout_epochs: 4; recommended_recovery_policy: stake_full_release.

SIM-005 remains the primary evidence anchor for CDL-045 opening and later prelock hardening.

## 4. Locked phase table (402-413)

| Order | Phase | Scope | Character |
| --- | --- | --- | --- |
| 1 | Phase 402 | Window sequence lock + CDL-042 opening + CDL-045 opening | sensitive constitutional |
| 2 | Phase 403 | CDL-042 prelock hardening | constitutional |
| 3 | Phase 404 | CDL-045 prelock hardening | constitutional |
| 4 | Phase 405 | CDL-035 timed_out amendment opening + prelock | constitutional |
| 5 | Phase 406 | SIM-008 commissioning | simulation |
| 6 | Phase 407 | CDL-042 ratification | constitutional |
| 7 | Phase 408 | CDL-045 ratification | constitutional |
| 8 | Phase 409 | CDL-035 timed_out amendment ratification | constitutional |
| 9 | Phase 410 | D2e Agent SDK - Part 1 | runtime |
| 10 | Phase 411 | D2e Agent SDK - Part 2 | runtime |
| 11 | Phase 412 | Coherence + capsule v1.5 | synthesis |
| 12 | Phase 413 | Window closure gate | sensitive gate |

## 5. Constitutional first-action: two-CDL opening batch

Phase 402 opens CDL-042 and CDL-045 as a two-CDL opening batch.

The two-CDL batch is additive to the constitutional register and does not ratify either lane in this phase.

CDL-042 is the agent identity namespace lane and CDL-045 is the operational emergency response lane.

## 6. Sequencing constraints and dependency ordering

D2e Agent SDK implementation is gated on CDL-042 ratification in Phase 407 and begins in Phase 410.

CDL-045 opening in Phase 402 depends on SIM-005 evidence already available since Phase 370, while detailed calibration and threshold hardening are deferred to Phase 404.

The CDL-035 timed_out amendment is structurally downstream of Phase 402 and uses the SIM-007 carry-forward already locked in this artifact.

Runtime implementation remains out of scope until the dedicated runtime phases later in the window.

## 7. D2e deferral, CDL-035 amendment convention, and SIM-008 gate

The CDL-035 timed_out amendment is opened in Phase 405 as a dedicated amendment row with a new sequential CDL identifier; it references CDL-035 in its related_clause and does not modify the base CDL-035 ratified row.

Under this register convention, Phase 405 must consume the next fresh numbered CDL row rather than suffix notation or in-place mutation of CDL-035.

Treasury governance CDL cluster and mandatory ECU conversion deadline CDL are explicitly deferred to Window 414+ and gated on SIM-008 commissioning in Phase 406.

No Treasury Governance CDL opening or ECU mandatory conversion deadline CDL opening is authorized anywhere in Window 402-413.

## 8. Canonical anchors and non-goals

Canonical anchors:
- `docs/specs/ilc_window_392_401_handoff_401_v0.1.md`
- `docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_392_413_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`
- `docs/specs/ilc_sim_005_agent_death_orphaning_commissioning_results_370_v0.1.md`
- `docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v1.4.md`

Non-goals in Phase 402:
- no ratification of CDL-042,
- no ratification of CDL-045,
- no opening of the CDL-035 timed_out amendment,
- no runtime mutation under `ilc_core/`,
- no D2e implementation.
