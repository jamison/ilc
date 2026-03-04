# CDL-037 Executable Node Descriptor and Safety Contract Ratification Evidence 352 v0.1

Status: Phase-352 ratification evidence artifact  
Date: 2026-03-04  
Owner lane: Constitution Cluster A / Node Schema Ratification Window

## 1. Purpose and scope

This artifact ratifies `CDL-037` and records the selected executable-node descriptor answer for Window 348-357.

This phase ratifies `CDL-037` only.

No runtime implementation of executable-node logic is ratified in Phase 352.

## 2. Ratified decision

`CDL-037` ratifies `structured descriptor with sandboxed runtime binding`.

Rejected options:
- `raw executable payload embedded in authored envelope`
- `structured descriptor without sandboxing`

The ratified answer preserves structured descriptors in authored content, binds execution to agent-side sandboxing, and keeps runtime implementation deferred to a later window.

## 3. Evidence basis

Evidence-chain anchors:
- `docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_evidence_prelock_343_v0.1.md`
- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md`
- `docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_ratification_evidence_351_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_346_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md`

Section 6 of the Phase-343 prelock artifact is authoritative for this ratification lane when it is more specific than the compressed CDL row shorthand.

## 4. Section-6 authoritative evidence checklist satisfaction

The artifact satisfies all five authoritative Phase-343 Section-6 evidence items:

1. `executable descriptor candidate field set`
   - `structured descriptor with sandboxed runtime binding`
   - `The executable descriptor is Authored Payload content.`
   - `declared inputs`
   - `declared outputs`
   - `declared side effects`
   - `safety assertions`
   - `determinism guarantees`
   - `bounded resource guarantees`

2. `sandboxed runtime binding contract`
   - `Nodes recommend logic; they do not self-authorize execution.`
   - `Execution context belongs to the Transport/Runtime layer, not the Authored Payload Envelope.`
   - `agent-side sandboxing is a safety-contract obligation`

3. `safety contract model and genesis-trust boundary`
   - `genesis-trusted executable descriptor`
   - `non-genesis executable descriptor`
   - `Genesis-trusted descriptors carry bootstrap authority that non-genesis descriptors cannot claim.`

4. `CDL-V7 decomposition gate for executable descriptors`
   - `A proposed executable descriptor is an objective graph object challengeable under CDL-V7.`
   - `The executable descriptor must satisfy the CDL-V7 Popperian basic-statement gate before acquiring protocol effect.`
   - `CDL-035 remains authoritative for validation_state semantics and is not weakened here.`

5. `CDL-034 authored-envelope boundary preservation note`
   - `The three-envelope boundary established in Phase 340 must not be weakened here.`
   - `CDL-036 remains authoritative for transport boundary semantics and is not weakened here.`
   - `Phase 353 must keep promotion continuity subordinate to the ratified CDL-037 executable-node contract.`

## 5. Governance tokens

- `structured descriptor with sandboxed runtime binding`
- `Nodes recommend logic; they do not self-authorize execution.`
- `The executable descriptor is Authored Payload content.`
- `Execution context belongs to the Transport/Runtime layer, not the Authored Payload Envelope.`
- `The three-envelope boundary established in Phase 340 must not be weakened here.`
- `agent-side sandboxing is a safety-contract obligation`
- `genesis-trusted executable descriptor`
- `non-genesis executable descriptor`
- `Genesis-trusted descriptors carry bootstrap authority that non-genesis descriptors cannot claim.`
- `A proposed executable descriptor is an objective graph object challengeable under CDL-V7.`
- `The executable descriptor must satisfy the CDL-V7 Popperian basic-statement gate before acquiring protocol effect.`
- `declared inputs`
- `declared outputs`
- `declared side effects`
- `safety assertions`
- `determinism guarantees`
- `bounded resource guarantees`
- `CDL-035 remains authoritative for validation_state semantics and is not weakened here.`
- `CDL-036 remains authoritative for transport boundary semantics and is not weakened here.`
- `Phase 353 must keep promotion continuity subordinate to the ratified CDL-037 executable-node contract.`

## 6. Carry-forward constraints

- `CDL-038` remains open and is not ratified in this phase.
- `CDL-035 remains authoritative for validation_state semantics and is not weakened here.`
- `CDL-036 remains authoritative for transport boundary semantics and is not weakened here.`
- `Phase 353 must keep promotion continuity subordinate to the ratified CDL-037 executable-node contract.`
- Phase-347 closure assets remain unchanged in this ratification lane.
- Runtime implementation remains deferred until later ratification windows authorize it.
- `tests/test_node_schema_coherence_and_ratification_readiness_346.py` remains a historical readiness artifact and must not be patched to chase live ratified state in this phase.

## 7. Prelock hardening requirement

The historical Phase-343 prelock test must remain valid after ratification.

`tests/test_cdl_037_open_and_executable_node_safety_contract_prelock_343.py` is hardened so the Phase-343 `CDL-037` row is checked against historical Phase-343 state, not the live ratified decision log.

`tests/test_cdl_038_open_and_promotion_continuity_prelock_344.py` is hardened only for the known live `CDL-037` dependency in its mutation-scope test, preserving the historical Phase-344 opening contract without broadening patch scope.

## 8. Runtime deferral boundary

No runtime implementation of executable-node logic is ratified in Phase 352.

No `ilc_core/` runtime behavior is changed in this phase.

## 9. Canonical anchors

- `docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_evidence_prelock_343_v0.1.md`
- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md`
- `docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_ratification_evidence_351_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_346_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
