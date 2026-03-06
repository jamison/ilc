# ILC CDL-039 Prelock Finalization 374 v0.1

Status: Phase-374 prelock finalization artifact  
Date: 2026-03-06  
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

Modeled outputs are non-ratifying evidence inputs.

This artifact finalizes CDL-039 prelock evidence in Window 368-377 without ratifying CDL-039.

Phase 374 freezes prelock text and calibration dispositions but does not ratify CDL-039.

No decision-log mutation occurred. No ilc_core runtime files were changed.

## 2. Prelock evidence continuity and consolidation

Primary evidence chain:
- `docs/specs/ilc_cdl_039_p2p_transport_baseline_and_topology_privacy_evidence_prelock_359_v0.1.md`
- `docs/specs/ilc_cdl_039_topology_privacy_hardening_prelock_372_v0.1.md`
- `docs/specs/ilc_cdl_039_adversarial_review_and_evidence_freeze_373_v0.1.md`
- `docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md`

This artifact extends the Phase-359, Phase-372, and Phase-373 prelock artifacts additively as a consolidated prelock package.

## 3. Finalized invariant set for CDL-039 prelock

Transport Envelope routing headers MUST NOT carry creator_agent_id; authorship attribution is resolved from Authored Payload and protocol interpretation.

Transport channel routing field MUST be an opaque identifier (CID or uniformly random bytes); human-readable channel labels are UI-layer concerns only.

Partition-state assertion requires bounded cross-cluster reference limiting and release hysteresis.

Cluster membership non-inferrability remains a passive-observer resistance invariant.

Private-visibility expiry remains mandatory with explicit recovery-boundary treatment in this finalized prelock package.

## 4. Two-timescale protocol closure

short-timescale CDL-039 context: validation epoch liveness and Levin stress-cascade reconnection handling.

long-timescale CDL-039 context: issuance epoch partition divergence and highest_ecu_wins reconciliation.

Both timescales are mandatory in prelock text and remain mandatory for ratification-lane interpretation.

## 5. Final calibration dispositions for prelock

| Parameter group | Disposition | Finalized prelock note |
| --- | --- | --- |
| `R_partition_cross_ref` | `bounded_range` | Bounded range retained for Phase-373 flapping-risk suppression with calibration deferred to ratification lane. |
| `H_release` | `bounded_range` | Hysteresis release kept bounded away from assertion threshold to prevent state flapping. |
| `retention_epochs` | `deferred_with_reason` | Final value remains open pending ratification-lane confirmation of fairness and recovery semantics. |
| `timeout_policy` / `stake_recovery_policy` | `bounded_range` | Validation-epoch liveness and recovery fairness remain coupled and bounded for ratification-lane final calibration. |
| `cdl_038_recovery_scope` | `requires_explicit_cdl_039_clause` | Phase-373 disposition is frozen and closed by explicit clause text in Section 6. |

## 6. CDL-038 scope boundary disposition

cdl_038_recovery_scope disposition: requires_explicit_cdl_039_clause.

Proposed CDL-039 prelock clause text for post-expiry recovery semantics:

`Post-expiry recovery semantics are governed by CDL-039 as follows: a private-visibility node that expires without promotion_receipt is ineligible for direct promotion and must re-enter via a successor-node re-assertion path that preserves provenance linkage while re-running current-lane validation and policy checks; no automatic carry-forward of expired-node promotion eligibility is permitted.`

This clause closes the scope boundary in prelock text while preserving non-ratifying status in Phase 374.

## 7. Phase 374 frozen prelock package

Frozen package contents:
- consolidated invariant text,
- two-timescale closure framing,
- calibration dispositions for all five parameter groups,
- explicit post-expiry recovery clause text.

Phase 374 freezes prelock text and calibration dispositions but does not ratify CDL-039.

## 8. Carry-forward constraints for ratification lane

Carry-forward constraints:
- ratification lane must preserve non-authorship transport header boundary,
- ratification lane must preserve opaque channel identifier requirement,
- ratification lane must resolve bounded ranges into constitutional constants where required,
- ratification lane must preserve the Section-6 post-expiry clause intent unless formally superseded by explicit constitutional amendment language.

## 9. Non-goals and residual risk

Non-goals:
- no decision-log change,
- no runtime implementation,
- no CDL-039 ratification.

Residual risks:
- bounded-range constants still require ratification-lane calibration closure,
- analytical/model-based evidence should be followed by empirical runtime validation once D2d implementation is authorized,
- transport metadata privacy assumptions depend on correct Window 378+ runtime enforcement.
