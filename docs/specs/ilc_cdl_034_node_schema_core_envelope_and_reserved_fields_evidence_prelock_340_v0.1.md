# CDL-034 Node Schema Core Envelope and Reserved Fields Evidence Prelock v0.1

Status: Phase-340 evidence prelock artifact  
Date: 2026-03-03  
Owner lane: Constitution Cluster A / Node Schema Window

## 1. Purpose and scope

This artifact defines the pre-ratification contract surface for `CDL-034`.

Scope in this phase:
- open `CDL-034` and record `status: open`,
- lock the authored/protocol/transport envelope split as the core model under review,
- lock the reserved-field and extension-namespace boundary,
- lock the primitive/core field taxonomy candidate set,
- formally disposition `confidence`, `uncertainty_note`, and the `epistemic_type` / `gate_routing` boundary.

This phase does not ratify the node schema.

## 2. CDL-034 state and option inventory

Decision id: `CDL-034`

Current state: `status: open`

Option inventory:
- `single-envelope flat schema`
- `two-envelope authored/runtime split`
- `three-envelope authored/protocol/transport split`

Selected working candidate for prelock: `three-envelope authored/protocol/transport split`

The three-envelope model is the anchor invariant for CDL-034.

## 3. Three-envelope model and authored payload boundary

The unified schema is evaluated under three envelopes:
- `Authored Payload Envelope`
- `Protocol Interpretation Envelope`
- `Transport Envelope`

`Node is the canonical graph-object term.`

`Agent Profile is distinct from Node and is not a synonym for a graph claim object.`

`Quorum Record is distinct from Node and records evaluation outcomes by reference.`

`confidence` and `uncertainty_note` remain authored metadata pending ratification.

confidence and uncertainty_note remain authored metadata pending ratification.

`confidence and uncertainty_note provisionally belong to Authored Payload Envelope.`

`confidence and uncertainty_note are non-routing and non-economic pre-ratification authored metadata.`

`visibility` provisionally belongs to Authored Payload Envelope.

visibility provisionally belongs to Authored Payload Envelope.

`gate_routing is protocol-derived and not submitter-controlled authored payload.`

`gate_routing provisionally belongs to Protocol Interpretation Envelope if materialized at all.`

`no in-place historical payload mutation is authorized.`

## 4. Reserved fields, extension namespace, and collision rules

Reserved fields may not be shadowed by `meta` keys or `user_tags`.

`reserved fields may not be shadowed by meta keys or user tags.`

`custom-extension namespace uses meta plus namespaced user_tags and has no routing authority.`

The reserved/core boundary remains constitutional. Extension material is informational only until later ratified otherwise.

## 5. Primitive/core field taxonomy and epistemic-lane boundary

Candidate `primitive_type` family under review:
- `assertion`
- `observation`
- `citation`
- `executable_descriptor`
- `governance_proposal`

`refutation is not a default primitive_type.`

Refutation remains primarily an edge/relational semantic until later ratification says otherwise.

`single-primary-epistemic-lane rule`

The authored payload must not carry multiple routing-authoritative epistemic lanes at once. Mixed semantics must be decomposed rather than hidden in one claim object.

## 6. Evidence prelock requirements for CDL-034

Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.

Authoritative evidence-prelock items:
- `three-envelope comparison and boundary rationale`
- `reserved-field set and collision matrix`
- `primitive_type candidate taxonomy and edge-boundary note`
- `confidence and uncertainty_note disposition note`
- `gate_routing derivation and placement note`

These five items govern later ratification if they are more specific than the compressed CDL row shorthand in `docs/specs/ilc_constitutional_decision_log_v0.1.md`.

## 7. Carry-forward constraints for later node-schema lanes

`Schema changes still require CDL opening, evidence prelock, ratification, and closure-gate process.`

`Phase 339 role split remains authoritative for schema-evolution monitoring and may not be weakened here.`

`Phase 341 must treat validation_state and gate verdicts as Protocol Interpretation Envelope attachments by reference, not mutations of Authored Payload Envelope.`

`Phase 344 must treat promotion as successor public node plus promotion_receipt, never in-place visibility mutation.`

`Phase 344 must cross-reference the CDL-034 reserved-field and custom-extension model.`

## 8. Non-goals and canonical anchors

Non-goals in this phase:
- no ratification of `CDL-034`,
- no runtime implementation in `ilc_core/`,
- no opening of `CDL-035` through `CDL-038`,
- no custom-field elevation execution,
- no promotion mechanics beyond carry-forward constraints.

Canonical anchors:
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`
- `docs/specs/ilc_node_schema_concretization_proposals_v0.1.md`
- `docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
