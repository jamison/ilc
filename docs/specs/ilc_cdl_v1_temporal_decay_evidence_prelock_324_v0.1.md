# ILC CDL-V1 Temporal Decay Evidence Prelock 324 v0.1

Status: Phase-324 evidence prelock artifact  
Date: 2026-02-27  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Open `CDL-V1` as a constitutional decision-log entry and lock the initial evidence-prelock boundary for later ratification.

This phase does not ratify the decay parameter. It creates an open constitutional row plus a pre-ratification evidence contract only.

## 2. CDL-V1 option inventory and working candidate

Decision id: `CDL-V1`

Status in this phase: `open`

Option inventory:
- `no temporal decay`
- `epoch-step decay`
- `exponential half-life decay`

Selected working candidate for future ratification: `exponential half-life decay`

Rejected-for-now options in this prelock:
- `no temporal decay`
- `epoch-step decay`

Working rationale:
- temporal decay is needed to reduce lock-in from stale historical reuse,
- a half-life model is more continuous and tunable than hard epoch-step cliffs,
- the ratification phase must still prove acceptable stability under sensitivity analysis.

## 3. Evidence required before ratification

Future ratification evidence must include all of the following:
- decay sensitivity analysis across multiple half-life candidates,
- lock-in displacement simulation showing whether newer superior claims can overtake entrenched incumbents,
- monitoring threshold proposal that explains how decay interacts with risk-monitoring signals and governance review,
- explicit parameter-boundary discussion for governance control and rollback safety.

## 4. Non-ratifying boundary confirmation

This phase opens `CDL-V1` but does not:
- ratify a temporal decay constant,
- modify any pre-existing CDL row,
- introduce runtime behavior changes in `ilc_core/`.

## 5. Canonical anchors

Primary anchors:
- `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
- `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`

Supporting interpretation:
- temporal decay is carried as a governance-controlled vulnerability response surface,
- the constitutional role here is to formalize the decision slot before parameter ratification.
