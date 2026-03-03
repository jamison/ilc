# CDL-037 Executable Node Descriptor and Safety Contract Evidence Prelock v0.1

Status: prelock artifact for constitutional opening lane only  
Phase: 343  
Decision row: `CDL-037`

## 1. Purpose and scope

This artifact records the pre-ratification contract for `CDL-037`.

`CDL-037`
`status: open`

The phase evaluates three options:

- `raw executable payload embedded in authored envelope`
- `structured descriptor without sandboxing`
- `structured descriptor with sandboxed runtime binding`

The selected prelock direction is `structured descriptor with sandboxed runtime binding`.

This artifact does not ratify runtime implementation, does not authorize unsandboxed execution, and does not weaken the three-envelope model.

## 2. CDL-037 state and option inventory

The governing executable-node conclusions are:

- `Nodes recommend logic; they do not self-authorize execution.`
- `The executable descriptor is Authored Payload content.`
- `Execution context belongs to the Transport/Runtime layer, not the Authored Payload Envelope.`
- `The three-envelope boundary established in Phase 340 must not be weakened here.`
- `agent-side sandboxing is a safety-contract obligation`
- `genesis-trusted executable descriptor`
- `non-genesis executable descriptor`

The rejected directions remain:

- `raw executable payload embedded in authored envelope`
- `structured descriptor without sandboxing`

## 3. Executable descriptor boundary and authored-envelope placement

`The executable descriptor is Authored Payload content.`

`Execution context belongs to the Transport/Runtime layer, not the Authored Payload Envelope.`

`The three-envelope boundary established in Phase 340 must not be weakened here.`

The descriptor is the authored claim about executable behavior, not the runtime authorization surface itself.

The descriptor candidate field set must remain claim-like and decomposable under `CDL-V7`, including:

- `declared inputs`
- `declared outputs`
- `declared side effects`
- `safety assertions`
- `determinism guarantees`
- `bounded resource guarantees`

## 4. Safety contract model and agent-side sandboxing

`Nodes recommend logic; they do not self-authorize execution.`

`agent-side sandboxing is a safety-contract obligation`

`A proposed executable descriptor is an objective graph object challengeable under CDL-V7.`

`The executable descriptor must satisfy the CDL-V7 Popperian basic-statement gate before acquiring protocol effect.`

The runtime-binding model therefore requires:

- a structured descriptor, not raw executable payload,
- agent-side sandbox enforcement,
- explicit safety-contract interpretation by the consuming runtime,
- reject-on-boundary-violation behavior if descriptor claims exceed the safety contract.

## 5. Genesis-trusted vs non-genesis executable descriptors

`genesis-trusted executable descriptor`

`non-genesis executable descriptor`

`Genesis-trusted descriptors carry bootstrap authority that non-genesis descriptors cannot claim.`

Bootstrap authority does not erase challengeability. A genesis-trusted descriptor may still be challenged at the claim level and does not authorize arbitrary unsandboxed execution.

## 6. Evidence prelock requirements for CDL-037

Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.

Later ratification must treat the following five evidence items as authoritative:

- `executable descriptor candidate field set`
- `sandboxed runtime binding contract`
- `safety contract model and genesis-trust boundary`
- `CDL-V7 decomposition gate for executable descriptors`
- `CDL-034 authored-envelope boundary preservation note`

These evidence items are the minimum ratification basis for `CDL-037`.

## 7. Carry-forward constraints for later node-schema lanes

`Phase 344 must cross-reference CDL-037 for the executable-node promotion case.`

`Phase 345 must not treat executable-node trust levels as reputation defaults.`

Later phases may not:

- collapse executable descriptor claims into runtime authorization,
- treat sandboxing as optional or merely advisory,
- reuse genesis-trusted status as a shortcut for reputation,
- bypass `CDL-V7` decomposition requirements for executable descriptors.

## 8. Non-goals and canonical anchors

Non-goals:

- no ratification of `CDL-037`,
- no runtime implementation of executable-node logic,
- no weakening of the three-envelope model,
- no promotion or reputation mechanics beyond carry-forward notes.

`No runtime implementation of executable-node logic is ratified in Phase 343.`

Canonical anchors:

- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md`
- `docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_evidence_prelock_342_v0.1.md`
- `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`
- `docs/specs/ilc_node_schema_concretization_proposals_v0.1.md`
- `docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
