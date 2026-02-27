# ILC CDL-V2 Sybil Resistance Evidence Prelock 324 v0.1

Status: Phase-324 evidence prelock artifact  
Date: 2026-02-27  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Open `CDL-V2` as a constitutional decision-log entry and lock the initial evidence-prelock boundary for future anti-sybil ratification.

This phase does not ratify the anti-sybil mechanism. It opens the row and defines the required evidence package only.

## 2. CDL-V2 option inventory and working candidate

Decision id: `CDL-V2`

Status in this phase: `open`

Option inventory:
- `proof-of-personhood gate`
- `stake-based participation cost`
- `hybrid heuristic resistance`

Selected working candidate for future ratification: `hybrid heuristic resistance`

Rejected-for-now options in this prelock:
- `proof-of-personhood gate`
- `stake-based participation cost`

Working rationale:
- a hybrid heuristic path preserves lower-friction participation while still allowing layered anti-gaming controls,
- a single hard gate may over-constrain participation too early,
- the ratification phase must still show that heuristic resistance is measurable, testable, and governable.

## 3. Evidence required before ratification

Future ratification evidence must include all of the following:
- a sybil threat model covering reuse-event inflation and coordinated cluster gaming,
- synthetic graph simulation demonstrating expected containment effectiveness,
- monitoring/operator threshold proposal for suspicious reuse velocity, burst patterns, or isolated cluster anomalies,
- clear identity-surface integration notes describing how the chosen mechanism interacts with participant identity validation.

## 4. Non-ratifying boundary confirmation

This phase opens `CDL-V2` but does not:
- ratify an anti-sybil runtime mechanism,
- mutate any pre-existing CDL row,
- introduce runtime behavior changes in `ilc_core/`.

## 5. Canonical anchors

Primary anchors:
- `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
- `docs/specs/ilc_d2e_04_identity_subsystem_handoff_294_v0.1.md`

Supporting interpretation:
- anti-sybil policy must stay consistent with the identity subsystem boundary,
- constitutional opening occurs here; implementation and ratification are deferred.
