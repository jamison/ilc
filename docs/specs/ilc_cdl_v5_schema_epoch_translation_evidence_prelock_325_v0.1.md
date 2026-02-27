# ILC CDL-V5 Schema Epoch Translation Evidence Prelock 325 v0.1

Status: Phase-325 evidence prelock artifact  
Date: 2026-02-27  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Open `CDL-V5` as a constitutional decision-log entry and lock the initial evidence-prelock boundary for future schema-epoch and cross-version translation ratification.

This phase opens the row but does not ratify the translation protocol. It creates the pre-ratification evidence contract only.

## 2. CDL-V5 option inventory and working candidate

Decision id: `CDL-V5`

Status in this phase: `open`

Option inventory:
- `no epoch markers`
- `schema epoch markers only`
- `schema epoch markers plus explicit cross-version translation`

Selected working candidate for future ratification: `schema epoch markers plus explicit cross-version translation`

Rejected-for-now options in this prelock:
- `no epoch markers`
- `schema epoch markers only`

Working rationale:
- epoch markers alone identify frame boundaries but do not solve comparability,
- explicit translation is needed for cross-version centrality claims to remain auditable,
- the ratification phase must still prove translation invariance and acceptable backward-compatibility thresholds.

## 3. Evidence required before ratification

Future ratification evidence must include all of the following:
- translation invariance test vectors covering representative schema-epoch transitions,
- epoch-marker serialization contract specifying how schema epoch identifiers enter canonical artifacts,
- backward-compatibility thresholds defining when translation is acceptable versus incommensurable,
- explicit tie-back to schema and snapshot runtime surfaces already ratified in the current window.

## 4. Non-ratifying boundary confirmation

This phase opens `CDL-V5` but does not:
- ratify the cross-version translation protocol,
- mutate any pre-existing CDL row,
- introduce runtime behavior changes in `ilc_core/`.

## 5. Canonical anchors

Primary anchors:
- `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
- `docs/specs/ilc_d2_schema_baseline_runtime_handoff_310_v0.1.md`
- `docs/specs/ilc_epoch_snapshot_runtime_handoff_314_v0.1.md`

Supporting interpretation:
- schema epoch markers must be paired with an explicit translation protocol for centrality comparability,
- this phase opens the constitutional decision slot and evidence boundary only.
