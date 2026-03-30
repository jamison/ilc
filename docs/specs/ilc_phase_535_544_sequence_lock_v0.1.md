# ILC Phase 535-544 Sequence Lock v0.1

Status: locked
Date: 2026-03-30
Window: 535-544
Owner lane: G8 Constitution Cluster A

## 1. Window identity

Window 535-544 is the single-hop reuse-centrality propagation and passive-attribution
calibration window. It inherits the Phase 534 handoff and freezes the ten-phase program below.

## 2. Carry-forward freeze

- SIM-CENTRALITY-02 is required before CDL-060 can be opened.
- CDL-060 opening requires Phase 538 simulation calibration gate.
- CDL-053 remains reserved and unopened throughout Window 535-544.
- CDL-060 gossip runtime is a Window 545+ carry-forward.
- Phase 544 is the closure gate.
- multi_hop_centrality_deferred

## 3. Non-goals

This sequence lock does not:
- mutate the constitutional decision log
- modify `ilc_core/`
- open CDL-060 before Phase 538 sufficiency is established
- reopen or repurpose CDL-053
- amend Genesis bootstrap, validator bootstrap, key-ceremony, or admission-control artifacts

## 4. Phase sequence and primary deliverables

| Phase | Primary deliverable |
|---|---|
| 535 | `docs/specs/ilc_phase_535_544_sequence_lock_v0.1.md` |
| 536 | `docs/specs/ilc_cdl_060_gossip_centrality_extension_scoping_536_v0.1.md` |
| 537 | `ilc_core/epistemic/reuse_centrality_runtime.py` |
| 538 | `docs/specs/ilc_sim_centrality_02_gossip_propagation_calibration_538_v0.1.md` |
| 539 | `docs/specs/ilc_cdl_060_gossip_centrality_extension_opening_stub_539_v0.1.md` |
| 540 | `docs/specs/ilc_cdl_060_gossip_centrality_extension_prelock_hardening_540_v0.1.md` |
| 541 | `docs/specs/ilc_cdl_060_gossip_centrality_extension_ratification_evidence_541_v0.1.md` |
| 542 | `docs/specs/ilc_sim_passive_ecu_01_attribution_formula_calibration_542_v0.1.md` |
| 543 | `docs/specs/ilc_integration_coherence_report_543_v0.1.md` and `docs/specs/ilc_antigravity_context_capsule_v2.7.md` |
| 544 | `tools/check_window_535_544_closure_gate_phase_544.sh` |

## 5. Entry conditions from Window 525-534

Window 525-534 is closed.
`CDL-059` is ratified at window entry.
`CDL-036`, `CDL-039`, and `CDL-052` are ratified.
`CDL-060` remains absent at Phase 535 entry.
`CDL-053` remains reserved and unopened.
`ilc_core/epistemic/reuse_centrality_runtime.py` remains in stub form at window entry.
