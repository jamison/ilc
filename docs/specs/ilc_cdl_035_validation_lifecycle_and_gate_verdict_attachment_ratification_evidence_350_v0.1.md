# CDL-035 Validation Lifecycle and Gate-Verdict Attachment Ratification Evidence 350 v0.1

Status: Phase-350 ratification evidence artifact  
Date: 2026-03-04  
Owner lane: Constitution Cluster A / Node Schema Ratification Window

## 1. Purpose and scope

This artifact ratifies `CDL-035` and records the selected validation-lifecycle answer for Window 348-357.

This phase ratifies `CDL-035` only.

No runtime implementation of CDL-035 validation lifecycle logic is ratified in Phase 350.

## 2. Ratified decision

`CDL-035` ratifies `attached lifecycle envelope with bounded operational relevance`.

Rejected options:
- `inline mutable lifecycle state`
- `attached lifecycle envelope with unbounded recursive verdict effects`

The ratified answer places lifecycle semantics in a protocol-attached envelope, keeps gate verdicts attached by reference, and constrains automatic protocol effect to a bounded operational window.

## 3. Evidence basis

Evidence-chain anchors:
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md`
- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_346_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md`

Section 6 of the Phase-341 prelock artifact is authoritative for this ratification lane when it is more specific than the compressed CDL row shorthand.

## 4. Section-6 authoritative evidence checklist satisfaction

The artifact satisfies all five authoritative Phase-341 Section-6 evidence items:

1. `validation_state state-machine table`
   - `validation_state is a state machine, not loose status vocabulary.`
   - `validation_state provisionally belongs to Protocol Interpretation Envelope.`
   - The ratified lifecycle retains the candidate state vocabulary: `proposed`, `under_review`, `corroborated`, `quarantined`, `finalized`, `diverged`.

2. `gate-verdict attachment-by-reference model`
   - `gate verdicts attach by reference and do not mutate Authored Payload Envelope.`
   - `gate verdict objects remain challengeable objective graph objects under CDL-V7.`
   - `gate_verdict_refs` remains the attachment surface.

3. `recursive challenge operational bound`
   - `operational_verdict_depth_max = 2`
   - `The operational bound constrains protocol effect, not graph expressibility.`
   - `deeper chains may exist on graph but do not automatically alter node status until collapsed back into first-order evidentiary claims.`

4. `quarantine semantics and payout-freeze note`
   - `quarantine freezes public corroboration and payout eligibility pending eligible verdict resolution.`
   - `quarantine freezes public reuse eligibility pending eligible verdict resolution.`
   - `quarantine does not rewrite authored payload history.`

5. `CDL-V1 / CDL-V3 / CDL-V7 dependency note`
   - `CDL-V1 temporal decay remains damping support, not the sole convergence mechanism.`
   - `CDL-V3 remains authoritative for diversity and anti-cluster constraints; this phase does not redefine them.`
   - `CDL-V7 remains authoritative for decomposition admissibility and challengeable gate-verdict objects.`

## 5. Governance tokens

- `validation_state is a state machine, not loose status vocabulary.`
- `validation_state provisionally belongs to Protocol Interpretation Envelope.`
- `quarantine_state provisionally belongs to Protocol Interpretation Envelope.`
- `gate verdicts attach by reference and do not mutate Authored Payload Envelope.`
- `gate verdict objects remain challengeable objective graph objects under CDL-V7.`
- `operational_verdict_depth_max = 2`
- `The operational bound constrains protocol effect, not graph expressibility.`
- `deeper chains may exist on graph but do not automatically alter node status until collapsed back into first-order evidentiary claims.`
- `quarantine freezes public corroboration and payout eligibility pending eligible verdict resolution.`
- `quarantine freezes public reuse eligibility pending eligible verdict resolution.`
- `No quorum thresholds are ratified in Phase 350.`
- `No reputation defaults are ratified in Phase 350.`
- `Phase 345 may not treat L-tier quorum levels as reputation tiers.`

## 6. Carry-forward constraints

- `CDL-036` through `CDL-038` remain open and are not ratified in this phase.
- Transport/header ratification remains deferred to `CDL-036`; lifecycle attachment semantics may not be collapsed into transport semantics.
- Reputation remains derived from lifecycle outputs and may not be materialized as mutable inline node-level reputation.
- Runtime implementation remains deferred until the post-ratification window authorizes it.
- `tests/test_node_schema_coherence_and_ratification_readiness_346.py` remains a historical readiness artifact and must not be patched to chase live ratified state in this phase.

## 7. Prelock hardening requirement

The historical Phase-341 prelock test must remain valid after ratification.

`tests/test_cdl_035_open_and_validation_lifecycle_prelock_341.py` is hardened so the Phase-341 `CDL-035` row is checked against historical Phase-341 state, not against the live ratified decision log.

`tests/test_cdl_036_open_and_node_dissemination_header_fetch_prelock_342.py` is hardened only for the known live `CDL-035` dependency in its mutation-scope test, preserving the historical Phase-342 opening contract without broadening patch scope.

## 8. Runtime deferral boundary

No runtime implementation of CDL-035 validation lifecycle logic is ratified in Phase 350.

No `ilc_core/` runtime behavior is changed in this phase.

## 9. Canonical anchors

- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md`
- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_346_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
