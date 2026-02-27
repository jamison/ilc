# ILC CDL-V3 Quorum Diversity Evidence Prelock 324 v0.1

Status: Phase-324 evidence prelock artifact  
Date: 2026-02-27  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Open `CDL-V3` as a constitutional decision-log entry and lock the initial evidence-prelock boundary for future quorum-diversity ratification.

This phase does not ratify quorum diversity policy. It opens the row and fixes the evidence package that future ratification must satisfy.

## 2. CDL-V3 option inventory and working candidate

Decision id: `CDL-V3`

Status in this phase: `open`

Option inventory:
- `cluster diversity floor`
- `weighted diversity quorum`
- `supermajority-only governance`

Selected working candidate for future ratification: `cluster diversity floor`

Rejected-for-now options in this prelock:
- `weighted diversity quorum`
- `supermajority-only governance`

Working rationale:
- a cluster diversity floor directly addresses monoculture/capture risk at quorum formation time,
- weighted diversity is more complex and may be harder to audit constitutionally,
- supermajority alone does not guarantee epistemic diversity and can still permit coordinated monoculture.

## 3. Evidence required before ratification

Future ratification evidence must include all of the following:
- quorum composition simulation across varying diversity-floor settings,
- coordinated voting adversarial tests showing capture resistance under clustered validator behavior,
- governance wording that defines cluster diversity in an auditable and implementable way,
- explicit review of appeal and minority-dissent interaction with the diversity rule.

## 4. Non-ratifying boundary confirmation

This phase opens `CDL-V3` but does not:
- ratify a quorum-diversity threshold,
- mutate any pre-existing CDL row,
- introduce runtime behavior changes in `ilc_core/`.

## 5. Canonical anchors

Primary anchors:
- `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md`

Supporting interpretation:
- quorum diversity is the constitutional mechanism for reducing epistemic monoculture in ratification,
- this phase opens the decision slot and locks the future evidence standard only.
