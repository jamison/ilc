# CDL-036 Node Dissemination Header and Fetch Contract Evidence Prelock v0.1

Status: prelock artifact for constitutional opening lane only  
Phase: 342  
Decision row: `CDL-036`

## 1. Purpose and scope

This artifact records the pre-ratification contract for `CDL-036`.

`CDL-036`
`status: open`

The phase evaluates three options:

- `full-payload push broadcast`
- `header-first dissemination with fixed orderer`
- `header-first dissemination with CID-addressed pull fetch`

The selected prelock direction is `header-first dissemination with CID-addressed pull fetch`.

This artifact does not ratify a permanent orderer, does not ratify transport bindings, and does not authorize runtime implementation.

## 2. CDL-036 state and option inventory

The governing dissemination conclusions are:

- `header-first dissemination`
- `CID-addressed pull fetch`
- `content-addressed verification before interpretation`
- `ILC leans pull, not push.`
- `pull-dominant with soft push-signals`

The rejected directions remain:

- `full-payload push broadcast`
- `header-first dissemination with fixed orderer`

## 3. Header-first dissemination and transport-envelope boundary

`Transport Envelope remains separate from Authored Payload Envelope and Protocol Interpretation Envelope.`

The candidate `header schema` is the minimal dissemination surface.

`candidate header field set: node_id, creator_agent_id, epistemic_type, visibility, channel, epoch_created, payload_cid, signature`

The intended split is:

- authored payload remains signed content,
- protocol interpretation remains lifecycle/governance attachment space,
- transport header remains the fast dissemination and fetch-trigger surface only.

`header-first dissemination does not authorize full-payload push as the default transport rule.`

## 4. Fetch contract, payload reference, and signature scope

`payload_cid`

`The header signature must commit to the payload reference.`

`signature scope covers header fields plus payload_cid.`

`retry and idempotence remain fetch-contract obligations, not authored-payload semantics.`

The fetch contract therefore requires:

- deterministic fetch by content address,
- safe retry semantics,
- idempotent payload retrieval,
- reject-on-mismatch behavior if the fetched payload does not satisfy the header commitment.

## 5. Visibility, channel interaction, and orderer-agnostic boundary

`visibility and channel remain routing inputs, not authored-payload mutability permissions.`

`visibility/channel interaction belongs to Transport Envelope routing semantics only insofar as dissemination policy is concerned.`

`Narwhal/Tusk/Bullshark remains a reference pattern, not a locked constitutional choice.`

`No permanent validator-core orderer is ratified in Phase 342.`

`No transport binding implementation is ratified in Phase 342.`

`CDL-024 remains authoritative for transport-agnostic wire bindings and is not weakened here.`

`Phase 341 remains authoritative for validation-lifecycle attachments and may not be collapsed into transport semantics.`

## 6. Evidence prelock requirements for CDL-036

Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.

Later ratification must treat the following six evidence items as authoritative:

- `transport header field set`
- `push/pull dissemination conclusion and fetch-boundary note`
- `fetch API and idempotence note`
- `signature scope and payload-reference integrity note`
- `visibility/channel dissemination rule note`
- `orderer-agnostic boundary note`

These evidence items are the minimum ratification basis for `CDL-036`.

## 7. Carry-forward constraints for later node-schema lanes

`Phase 343 must keep executable-node transport concerns subordinate to the CDL-036 header/fetch contract.`

Later phases may not:

- collapse Transport Envelope semantics into authored payload,
- treat header routing as a hidden lifecycle state machine,
- treat reference-orderer examples as constitutional orderer ratification.

## 8. Non-goals and canonical anchors

Non-goals:

- no ratification of `CDL-036`,
- no orderer selection,
- no transport binding implementation,
- no `ilc_core/` runtime implementation.

Canonical anchors:

- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md`
- `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`
- `docs/specs/ilc_node_schema_concretization_proposals_v0.1.md`
- `docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
