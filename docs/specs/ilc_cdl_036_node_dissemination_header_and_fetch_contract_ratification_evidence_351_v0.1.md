# CDL-036 Node Dissemination Header and Fetch Contract Ratification Evidence 351 v0.1

Status: Phase-351 ratification evidence artifact  
Date: 2026-03-04  
Owner lane: Constitution Cluster A / Node Schema Ratification Window

## 1. Purpose and scope

This artifact ratifies `CDL-036` and records the selected node-dissemination contract answer for Window 348-357.

This phase ratifies `CDL-036` only.

No runtime implementation of CDL-036 dissemination or fetch logic is ratified in Phase 351.

## 2. Ratified decision

`CDL-036` ratifies `header-first dissemination with CID-addressed pull fetch`.

Rejected options:
- `full-payload push broadcast`
- `header-first dissemination with fixed orderer`

The ratified answer preserves header-first dissemination, keeps payload retrieval behind content-addressed pull fetch, and refuses to constitutionalize a permanent validator-core orderer or a transport-binding implementation in this phase.

## 3. Evidence basis

Evidence-chain anchors:
- `docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_evidence_prelock_342_v0.1.md`
- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_346_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`

Section 6 of the Phase-342 prelock artifact is authoritative for this ratification lane when it is more specific than the compressed CDL row shorthand.

## 4. Section-6 authoritative evidence checklist satisfaction

The artifact satisfies all six authoritative Phase-342 Section-6 evidence items:

1. `transport header field set`
   - `header-first dissemination`
   - `candidate header field set: node_id, creator_agent_id, epistemic_type, visibility, channel, epoch_created, payload_cid, signature`
   - `Transport Envelope remains separate from Authored Payload Envelope and Protocol Interpretation Envelope.`

2. `push/pull dissemination conclusion and fetch-boundary note`
   - `CID-addressed pull fetch`
   - `ILC leans pull, not push.`
   - `pull-dominant with soft push-signals`
   - `header-first dissemination does not authorize full-payload push as the default transport rule.`

3. `fetch API and idempotence note`
   - `content-addressed verification before interpretation`
   - `retry and idempotence remain fetch-contract obligations, not authored-payload semantics.`
   - fetch remains contract-driven and transport-envelope scoped.

4. `signature scope and payload-reference integrity note`
   - `payload_cid`
   - `The header signature must commit to the payload reference.`
   - `signature scope covers header fields plus payload_cid.`

5. `visibility/channel dissemination rule note`
   - `visibility and channel remain routing inputs, not authored-payload mutability permissions.`
   - `visibility/channel interaction belongs to Transport Envelope routing semantics only insofar as dissemination policy is concerned.`
   - dissemination policy does not authorize authored-payload mutation.

6. `orderer-agnostic boundary note`
   - `Narwhal/Tusk/Bullshark remains a reference pattern, not a locked constitutional choice.`
   - `No permanent validator-core orderer is ratified in Phase 351.`
   - `No transport binding implementation is ratified in Phase 351.`

## 5. Governance tokens

- `header-first dissemination`
- `CID-addressed pull fetch`
- `content-addressed verification before interpretation`
- `Transport Envelope remains separate from Authored Payload Envelope and Protocol Interpretation Envelope.`
- `candidate header field set: node_id, creator_agent_id, epistemic_type, visibility, channel, epoch_created, payload_cid, signature`
- `payload_cid`
- `The header signature must commit to the payload reference.`
- `signature scope covers header fields plus payload_cid.`
- `header-first dissemination does not authorize full-payload push as the default transport rule.`
- `ILC leans pull, not push.`
- `pull-dominant with soft push-signals`
- `retry and idempotence remain fetch-contract obligations, not authored-payload semantics.`
- `visibility and channel remain routing inputs, not authored-payload mutability permissions.`
- `visibility/channel interaction belongs to Transport Envelope routing semantics only insofar as dissemination policy is concerned.`
- `Narwhal/Tusk/Bullshark remains a reference pattern, not a locked constitutional choice.`
- `No permanent validator-core orderer is ratified in Phase 351.`
- `No transport binding implementation is ratified in Phase 351.`
- `CDL-024 remains authoritative for transport-agnostic wire bindings and is not weakened here.`
- `Phase 343 must keep executable-node transport concerns subordinate to the CDL-036 header/fetch contract.`

## 6. Carry-forward constraints

- `CDL-037` and `CDL-038` remain open and are not ratified in this phase.
- `CDL-024 remains authoritative for transport-agnostic wire bindings and is not weakened here.`
- `Phase 343 must keep executable-node transport concerns subordinate to the CDL-036 header/fetch contract.`
- `Phase 347` closure assets remain unchanged in this ratification lane.
- Runtime implementation remains deferred until later ratification windows authorize it.
- `tests/test_node_schema_coherence_and_ratification_readiness_346.py` remains a historical readiness artifact and must not be patched to chase live ratified state in this phase.

## 7. Prelock hardening requirement

The historical Phase-342 prelock test must remain valid after ratification.

`tests/test_cdl_036_open_and_node_dissemination_header_fetch_prelock_342.py` is hardened so the Phase-342 `CDL-036` row is checked against historical Phase-342 state, not the live ratified decision log.

`tests/test_cdl_037_open_and_executable_node_safety_contract_prelock_343.py` is hardened only for the known live `CDL-036` dependency in its mutation-scope test, preserving the historical Phase-343 opening contract without broadening patch scope.

## 8. Runtime deferral boundary

No runtime implementation of CDL-036 dissemination or fetch logic is ratified in Phase 351.

No `ilc_core/` runtime behavior is changed in this phase.

## 9. Canonical anchors

- `docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_evidence_prelock_342_v0.1.md`
- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_346_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
