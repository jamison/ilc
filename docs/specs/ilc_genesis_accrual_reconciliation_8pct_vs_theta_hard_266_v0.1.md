# ILC Genesis Accrual Reconciliation 8% vs theta_hard 266 v0.1

Status: Phase-266 reconciliation artifact (non-ratifying)
Date: 2026-02-22
Owner lane: G8 Constitution Cluster A

## 1. Problem statement

Historical simulation framing cites an `8%` Genesis accrual notion, while implemented governor framing uses issuance-share bounds (`theta_hard = 1/20`, `theta_soft = exp(-3)`).

Without explicit reconciliation, these surfaces can be misread as contradictory policy definitions.

## 2. Metric-surface distinction

The two framings operate on different measurement surfaces:
- simulation framing (`8%`) references task-level value flow in modeled task contexts,
- governor framing (`theta_hard = 1/20`, `theta_soft = exp(-3)`) constrains issuance-share behavior at policy-governor layer.

These are related but not numerically identical observables.

## 3. Compatibility framing and assumptions

Compatibility assumptions for interpretation:
- task-level flow share and issuance-share cap can coexist as different normalization surfaces,
- policy cap constants control issuance envelope independent of local task composition,
- simulation percentages remain historical calibration signals rather than direct constitutional constants.

This reconciliation artifact clarifies interpretation and does not itself pick or ratify policy values.

## 4. Open questions and next ratification-lane requirements

Open questions for sensitive lanes:
- what evidence threshold is required to claim practical consistency under multi-epoch stress,
- what tolerance band should be accepted between task-flow and issuance-share observables,
- whether additional telemetry should be mandated before ratification closure.

Required next steps:
- lane-local evidence package tying model assumptions to observed metrics,
- explicit ratification-lane decision text if constants or interpretation rules are locked.

## 5. Canonical anchors

- `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- `docs/specs/ilc_phase_260_269_sequence_lock_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
