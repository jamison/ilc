# CDL-034 Node Schema Core Envelope and Reserved Fields Ratification Evidence 349 v0.1

Status: Phase-349 ratification evidence artifact  
Date: 2026-03-04  
Owner lane: Constitution Cluster A / Node Schema Window

## 1. Purpose and scope

This artifact ratifies `CDL-034` and records the selected node-schema core answer for Window 348-357.

This phase ratifies `CDL-034` only.

No runtime implementation of CDL-034 node schema logic is ratified in Phase 349.

## 2. Ratified decision

`CDL-034` ratifies `three-envelope authored/protocol/transport split`.

Rejected options:
- `single-envelope flat schema`
- `two-envelope authored/runtime split`

The ratified answer keeps authored content, protocol interpretation, and transport semantics as distinct constitutional surfaces.

## 3. Evidence basis

Evidence-chain anchors:
- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_346_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`

Section 6 of the Phase-340 prelock artifact is authoritative for this ratification lane when it is more specific than the compressed CDL row shorthand.

## 4. Section-6 authoritative evidence checklist satisfaction

The artifact satisfies all five authoritative Phase-340 Section-6 evidence items:

1. `three-envelope comparison and boundary rationale`
   - Ratified answer: `three-envelope authored/protocol/transport split`.
   - `Authored Payload Envelope`, `Protocol Interpretation Envelope`, and `Transport Envelope` remain distinct constitutional surfaces.

2. `reserved-field set and collision matrix`
   - `reserved fields may not be shadowed by meta keys or user tags.`
   - `custom-extension namespace uses meta plus namespaced user_tags and has no routing authority.`

3. `primitive_type candidate taxonomy and edge-boundary note`
   - `refutation is not a default primitive_type.`
   - Refutation remains primarily a relational/edge semantic unless a later CDL ratifies otherwise.

4. `confidence and uncertainty_note disposition note`
   - `confidence and uncertainty_note belong to Authored Payload Envelope.`
   - `confidence and uncertainty_note remain non-routing and non-economic metadata unless a later CDL ratifies otherwise.`

5. `gate_routing derivation and placement note`
   - `gate_routing is protocol-derived and not submitter-controlled authored payload.`
   - `gate_routing belongs to Protocol Interpretation Envelope if materialized at all.`

## 5. Governance tokens

- `The three-envelope model is the anchor invariant for CDL-034.`
- `Authored Payload Envelope`
- `Protocol Interpretation Envelope`
- `Transport Envelope`
- `Node is the canonical graph-object term.`
- `Agent Profile is distinct from Node and is not a synonym for a graph claim object.`
- `Quorum Record is distinct from Node and records evaluation outcomes by reference.`
- `reserved fields may not be shadowed by meta keys or user tags.`
- `custom-extension namespace uses meta plus namespaced user_tags and has no routing authority.`
- `confidence and uncertainty_note belong to Authored Payload Envelope.`
- `confidence and uncertainty_note remain non-routing and non-economic metadata unless a later CDL ratifies otherwise.`
- `visibility belongs to Authored Payload Envelope.`
- `gate_routing is protocol-derived and not submitter-controlled authored payload.`
- `gate_routing belongs to Protocol Interpretation Envelope if materialized at all.`
- `refutation is not a default primitive_type.`
- `no in-place historical payload mutation is authorized.`

## 6. Carry-forward constraints

- `CDL-035` through `CDL-038` remain open and are not ratified in this phase.
- `CDL-035` remains the next ratification dependency because lifecycle semantics constrain later executable and promotion lanes.
- Runtime implementation remains deferred until the ratified Window-357 boundary authorizes implementation work.
- `tests/test_node_schema_coherence_and_ratification_readiness_346.py` remains a historical readiness artifact and must not be patched to chase live ratified state in this phase.

## 7. Prelock hardening requirement

The historical Phase-340 prelock test must remain valid after ratification.

`tests/test_cdl_034_open_and_node_schema_core_prelock_340.py` is hardened so the Phase-340 `CDL-034` row is checked against historical Phase-340 state, not against the live ratified decision log.

## 8. Runtime deferral boundary

No runtime implementation of CDL-034 node schema logic is ratified in Phase 349.

No `ilc_core/` runtime behavior is changed in this phase.

## 9. Canonical anchors

- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_346_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
