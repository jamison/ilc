# ILC CDL-039 Adversarial Review and Evidence Freeze 373 v0.1

Status: Phase-373 adversarial evidence-freeze artifact  
Date: 2026-03-06  
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

This artifact records adversarial review outputs for CDL-039 prelock hardening and freezes calibration evidence for Phase 374 prelock finalization.

Modeled outputs are non-ratifying evidence inputs.

Phase 373 freezes evidence and calibration outcomes but does not ratify CDL-039.

No decision-log mutation occurred. No ilc_core runtime files were changed.

## 2. Evidence inputs and prelock continuity

Primary evidence chain:
- `docs/specs/ilc_cdl_039_p2p_transport_baseline_and_topology_privacy_evidence_prelock_359_v0.1.md`
- `docs/specs/ilc_cdl_039_topology_privacy_hardening_prelock_372_v0.1.md`
- `docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md`

This artifact extends the Phase-359 and Phase-372 prelock artifacts additively as CDL-039 prelock evidence.

Phase 374 consumes this evidence-freeze package for prelock finalization.

## 3. Adversarial method and threat matrix

Adversarial method is analytical/model-based and constrained by phase boundary (no live network attack execution).

Threat matrix coverage:
- partition-state flapping attacks targeting rate-limit oscillation,
- passive observer membership reconstruction attempts,
- expiry-path abuse attempts around promotion timing,
- channel semantic inference from identifier surface,
- timeout false-positive/false-negative tradeoff pressure under validation-epoch assumptions.

## 4. Partition-state flapping adversarial findings (R_partition_cross_ref, H_release)

Adversarial review required partition-state flapping stress for R_partition_cross_ref and H_release.

Findings:
- flapping risk increases sharply when release hysteresis is too close to assertion threshold,
- reference-cap pressure is manageable in bounded windows but unstable when cap and hysteresis are jointly under-constrained,
- bounded-range calibration is safer than single-point lock in this phase.

## 5. Cluster membership reconstruction adversarial findings

Adversarial review required passive-observer cluster-membership reconstruction attempts.

Findings:
- current invariant framing is sufficient for prelock if enforced with explicit passive-observer test anchors,
- leakage risk remains concentrated in correlation of repeated routing metadata patterns,
- no evidence supports weakening non-inferrability invariant.

## 6. Private-visibility expiry and promotion-boundary adversarial findings

Adversarial review required expiry-path abuse tests around promotion_receipt timing.

Findings:
- expiry semantics reduce indefinite orphan accumulation risk,
- adversarial timing windows exist around near-expiry promotion attempts and must be normalized by deterministic cutover semantics,
- CDL-038 scope boundary for post-expiry recovery receives explicit disposition in this phase.

## 7. Channel identifier leakage adversarial findings

Adversarial review required channel-identifier semantic inference probes.

Findings:
- opaque-identifier invariant remains necessary; enum-like channel surfaces amplify semantic leakage,
- enforcement remains deferred to authorized runtime implementation window,
- prelock text should retain strict prohibition on human-readable routing-channel identifiers.

## 8. Timeout and recovery policy adversarial calibration findings

Adversarial review required timeout false-positive and false-negative tradeoff analysis under validation-epoch assumptions.

Findings:
- `timeout_epochs=2` provides a sharp liveness signal but can over-trigger under jitter-heavy conditions without robust probe cadence,
- recovery-policy choices materially alter fairness outcomes during transient outages,
- bounded-range treatment is appropriate before final prelock binding.

## 9. Calibration outcomes and frozen evidence set

Calibration dispositions (one per required parameter group):

| Parameter group | Disposition | Frozen evidence note |
| --- | --- | --- |
| `R_partition_cross_ref` | `bounded_range` | Keep bounded range for Phase-374 text; single-point constant deferred until additional adversarial sensitivity review. |
| `H_release` | `bounded_range` | Maintain separation from assertion threshold to suppress flapping. |
| `retention_epochs` | `deferred_with_reason` | Defer final value pending combined CDL-038 scope closure and fairness pressure analysis in Phase 374. |
| `timeout_policy` / `stake_recovery_policy` | `bounded_range` | Treat timeout and recovery as coupled policy surface under validation-epoch assumptions. |
| `cdl_038_recovery_scope` | `requires_explicit_cdl_039_clause` | Post-expiry recovery semantics require explicit CDL-039 clause text for prelock completeness. |

Evidence freeze statement:
- all above dispositions are frozen as Phase-373 evidence inputs for Phase-374 prelock finalization,
- no ratification effect is produced in this phase.

## 10. Carry-forward package for Phase 374

Phase 374 carry-forward package includes:
- adversarially reviewed invariant integrity outcomes,
- frozen calibration dispositions for all five parameter groups,
- explicit requirement to close `cdl_038_recovery_scope` in prelock text,
- explicit two-timescale discipline retention (validation-epoch liveness vs issuance-epoch partition consensus).

## 11. Non-goals and unresolved residual risk

Non-goals:
- no decision-log updates,
- no runtime implementation,
- no CDL-039 ratification.

Residual risks carried forward:
- bounded-range parameters may still require tighter constraints before final ratification lane,
- model-based adversarial analysis requires future empirical validation once runtime transport implementation is authorized,
- privacy leakage probes remain sensitive to future routing metadata design decisions.
