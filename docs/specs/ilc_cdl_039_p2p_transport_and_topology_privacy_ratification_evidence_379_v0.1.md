# ILC CDL-039 Ratification Evidence v0.1

Status: ratification evidence artifact  
Date: 2026-03-06  
Decision lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact ratifies CDL-039 for P2P transport baseline, no-central-broker invariants, and topology privacy constraints using the additive prelock evidence chain from phases 359, 372, 373, and 374.

## 2. Ratified decision

Ratified option:
- brokerless peer-to-peer gossip baseline

Ratification scope:
- no-central-broker transport baseline is constitutional,
- transport metadata/privacy constraints are constitutional,
- calibration constants are constitutionally resolved in this artifact under Section 5.

## 3. Evidence basis

Canonical evidence anchors:
- `docs/specs/ilc_cdl_039_open_and_p2p_transport_baseline_prelock_359_v0.1.md`
- `docs/specs/ilc_cdl_039_topology_privacy_hardening_prelock_372_v0.1.md`
- `docs/specs/ilc_cdl_039_adversarial_review_and_evidence_freeze_373_v0.1.md`
- `docs/specs/ilc_cdl_039_prelock_finalization_374_v0.1.md`
- `docs/specs/ilc_phase_378_391_sequence_lock_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v1.2.md`

## 4. Section-3 authoritative evidence checklist satisfaction

Checklist satisfaction statements:
1. finalized invariant set from Phase 374 is carried unchanged,
2. two-timescale closure (validation epoch short-timescale, issuance epoch long-timescale) is carried unchanged,
3. calibration dispositions from Phase 374 are resolved in Section 5,
4. CDL-038 scope boundary clause from Phase 374 Section 6 is carried as ratification-lane constraint,
5. adversarial evidence-freeze continuity from Phase 373 is preserved.

All CDL-039 prelock artifacts remain historical-open references after ratification.

## 5. Calibration constants resolution

Calibration constants section is authoritative for Phase-391 section-scoped parsing.

Ratification resolution:
- `R_partition_cross_ref`: ratified as constitutional bound `0.05 <= R_partition_cross_ref <= 0.20` (validation of exact operational value remains implementation-lane tuning within bound).
- `H_release`: ratified as constitutional bound `1 <= H_release <= 3` consecutive clean epochs before partition-state release.
- `timeout_policy / stake_recovery_policy`: ratified as constitutional policy pair:
  - timeout trigger baseline = `2` validation epochs,
  - stake recovery requires successful post-timeout recovery attestation before payout lane reactivation.
- `retention_epochs`: retention_epochs operational value requires a named subsequent CDL amendment before deployment.

## 6. CDL-036 reconciliation clause

CDL-039 ratification removes creator_agent_id from the CDL-036 Transport Envelope candidate header field set; authorship attribution is resolved exclusively from the Authored Payload envelope and Protocol Interpretation envelope.

## 7. Carry-forward constraints

Ratification carry-forward constraints:
- no standing compatibility/profile dual-mode is introduced as a protocol feature,
- runtime enforcement remains bounded to implementation phases 380-382,
- Section-6 reconciliation clause governs transport header interpretation at implementation boundary,
- Phase-391 closure gate must verify calibration parsing against Section 5 only.

## 8. Runtime deferral boundary

No runtime implementation of CDL-039 transport invariants is ratified in Phase 379.

D2d runtime enforcement remains implementation work in phases 380-382.

## 9. Canonical anchors

Constitutional anchors:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_phase_378_391_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_039_prelock_finalization_374_v0.1.md`
- `docs/specs/ilc_window_368_377_handoff_377_v0.1.md`
