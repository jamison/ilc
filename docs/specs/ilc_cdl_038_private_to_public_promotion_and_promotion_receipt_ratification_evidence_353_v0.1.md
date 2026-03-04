# CDL-038 Private-to-Public Promotion and promotion_receipt Ratification Evidence 353 v0.1

Status: Phase-353 ratification evidence artifact  
Date: 2026-03-04  
Owner lane: Constitution Cluster A / Node Schema Ratification Window

## 1. Purpose and scope

This artifact ratifies `CDL-038` and records the selected promotion continuity answer for Window 348-357.

This phase ratifies `CDL-038` only.

No runtime implementation of promotion logic is ratified in Phase 353.

## 2. Ratified decision

`CDL-038` ratifies `successor-node plus promotion_receipt without automatic reputation carry-forward`.

Rejected options:
- `in-place visibility mutation on original node`
- `successor-node plus promotion_receipt with automatic reputation carry-forward`

The ratified answer preserves authored-payload immutability, requires explicit successor-node promotion via `promotion_receipt`, and rejects automatic public legitimacy, reward, or reputation carry-forward.

## 3. Evidence basis

Evidence-chain anchors:
- `docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_evidence_prelock_344_v0.1.md`
- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md`
- `docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_ratification_evidence_351_v0.1.md`
- `docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_ratification_evidence_352_v0.1.md`
- `docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_346_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`

Section 6 of the Phase-344 prelock artifact is authoritative for this ratification lane when it is more specific than the compressed CDL row shorthand.

## 4. Section-6 authoritative evidence checklist satisfaction

The artifact satisfies all five authoritative Phase-344 Section-6 evidence items:

1. `successor-node model and authored-payload immutability contract`
   - `successor-node plus promotion_receipt without automatic reputation carry-forward`
   - `Promotion changes visibility only by creating a successor public node plus a promotion_receipt, never by mutating the original node.`
   - `The original private node remains immutable after promotion.`

2. `promotion_receipt candidate schema`
   - `promotion_receipt`
   - `promotion_receipt must carry: original node CID, public successor node CID, disclosed lineage reference, epoch of promotion.`
   - `promotion_receipt is a reserved field under CDL-034; reserved-field collision rules apply.`
   - `CDL-034 remains authoritative for reserved-field collision rules and is not weakened here.`

3. `carry-forward restrictions (corroboration, reuse credit)`
   - `No automatic public corroboration or reuse credit carry-forward is allowed.`
   - `No automatic reputation carry-forward is allowed.`
   - `Promotion preserves provenance continuity, not public legitimacy or reward continuity.`

4. `disclosed lineage and audit history rules`
   - `Disclosed lineage is required; anonymous laundering of private work into public credit is not permitted.`
   - `Promotion is a one-way visibility transition.`

5. `CDL-034 reserved-field cross-reference and CDL-035 validation_state interaction`
   - `A promoted public successor node starts in proposed validation_state; it does not inherit the original node's validation_state.`
   - `CDL-035 remains authoritative for validation_state semantics and is not weakened here.`
   - `CDL-037 remains authoritative for executable-node safety constraints and is not weakened here.`
   - `Phase 345 must not treat a successfully promoted node as having automatic reputation advantage.`

## 5. Governance tokens

- `successor-node plus promotion_receipt without automatic reputation carry-forward`
- `Promotion changes visibility only by creating a successor public node plus a promotion_receipt, never by mutating the original node.`
- `The original private node remains immutable after promotion.`
- `promotion_receipt`
- `promotion_receipt must carry: original node CID, public successor node CID, disclosed lineage reference, epoch of promotion.`
- `No automatic public corroboration or reuse credit carry-forward is allowed.`
- `No automatic reputation carry-forward is allowed.`
- `Disclosed lineage is required; anonymous laundering of private work into public credit is not permitted.`
- `Promotion is a one-way visibility transition.`
- `A promoted public successor node starts in proposed validation_state; it does not inherit the original node's validation_state.`
- `promotion_receipt is a reserved field under CDL-034; reserved-field collision rules apply.`
- `CDL-034 remains authoritative for reserved-field collision rules and is not weakened here.`
- `CDL-035 remains authoritative for validation_state semantics and is not weakened here.`
- `Phase 345 must not treat a successfully promoted node as having automatic reputation advantage.`
- `CDL-037 remains authoritative for executable-node safety constraints and is not weakened here.`
- `Promotion preserves provenance continuity, not public legitimacy or reward continuity.`
- `No runtime implementation of promotion logic is ratified in Phase 353.`

## 6. Carry-forward constraints

- `CDL-038` is ratified in this phase and must not be reopened implicitly.
- `CDL-034 remains authoritative for reserved-field collision rules and is not weakened here.`
- `CDL-035 remains authoritative for validation_state semantics and is not weakened here.`
- `CDL-037 remains authoritative for executable-node safety constraints and is not weakened here.`
- `Phase 345 must not treat a successfully promoted node as having automatic reputation advantage.`
- Phase-347 closure assets remain unchanged in this ratification lane.
- Runtime implementation remains deferred until later windows authorize it.
- `tests/test_reputation_and_agent_profile_adjoint_contract_345.py` remains a locked adjoint contract artifact and must not be patched in this phase.

## 7. Prelock hardening requirement

The historical Phase-344 prelock test must remain valid after ratification.

`tests/test_cdl_038_open_and_promotion_continuity_prelock_344.py` is hardened so the Phase-344 `CDL-038` row is checked against historical Phase-344 state, not the live ratified decision log.

The Phase-344 historical `CDL-037` dependency remains preserved as historical Phase-344 state and is not broadened into new live checks.

## 8. Runtime deferral boundary

No runtime implementation of promotion logic is ratified in Phase 353.

No `ilc_core/` runtime behavior is changed in this phase.

## 9. Canonical anchors

- `docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_evidence_prelock_344_v0.1.md`
- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md`
- `docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_ratification_evidence_351_v0.1.md`
- `docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_ratification_evidence_352_v0.1.md`
- `docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_346_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
