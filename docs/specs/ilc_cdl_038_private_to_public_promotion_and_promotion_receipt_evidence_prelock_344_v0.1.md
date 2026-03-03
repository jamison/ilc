# CDL-038 Private-to-Public Promotion and promotion_receipt Evidence Prelock v0.1

Status: prelock artifact for constitutional opening lane only  
Phase: 344  
Decision row: `CDL-038`

## 1. Purpose and scope

This artifact records the pre-ratification contract for `CDL-038`.

`CDL-038`
`status: open`

The phase evaluates three options:

- `in-place visibility mutation on original node`
- `successor-node plus promotion_receipt`
- `successor-node plus promotion_receipt with automatic reputation carry-forward`

The selected prelock direction is `successor-node plus promotion_receipt without automatic reputation carry-forward`.

This artifact does not ratify runtime implementation, does not authorize public-credit laundering, and does not weaken authored-payload immutability.

## 2. CDL-038 state and option inventory

The governing promotion conclusions are:

- `Promotion changes visibility only by creating a successor public node plus a promotion_receipt, never by mutating the original node.`
- `The original private node remains immutable after promotion.`
- `promotion_receipt`
- `Promotion is a one-way visibility transition.`
- `No automatic public corroboration or reuse credit carry-forward is allowed.`
- `No automatic reputation carry-forward is allowed.`

The rejected directions remain:

- `in-place visibility mutation on original node`
- `successor-node plus promotion_receipt with automatic reputation carry-forward`

## 3. Successor-node model and authored-payload immutability

`Promotion changes visibility only by creating a successor public node plus a promotion_receipt, never by mutating the original node.`

`The original private node remains immutable after promotion.`

The promoted public node is therefore a new public submission with continuity by reference rather than mutation.

`A promoted public successor node starts in proposed validation_state; it does not inherit the original node's validation_state.`

## 4. promotion_receipt schema and provenance continuity

`promotion_receipt`

`promotion_receipt must carry: original node CID, public successor node CID, disclosed lineage reference, epoch of promotion.`

`promotion_receipt is a reserved field under CDL-034; reserved-field collision rules apply.`

The candidate provenance structure may additionally include disclosed audit history hashes and promotion signer references, but the minimum continuity surface is fixed by the fields above.

## 5. Carry-forward restrictions and disclosed lineage

`No automatic public corroboration or reuse credit carry-forward is allowed.`

`No automatic reputation carry-forward is allowed.`

`Disclosed lineage is required; anonymous laundering of private work into public credit is not permitted.`

`Phase 345 must not treat a successfully promoted node as having automatic reputation advantage.`

This means promotion preserves provenance continuity, not public legitimacy or reward continuity.

## 6. Evidence prelock requirements for CDL-038

Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.

Later ratification must treat the following five evidence items as authoritative:

- `successor-node model and authored-payload immutability contract`
- `promotion_receipt candidate schema`
- `carry-forward restrictions (corroboration, reuse credit)`
- `disclosed lineage and audit history rules`
- `CDL-034 reserved-field cross-reference and CDL-035 validation_state interaction`

These evidence items are the minimum ratification basis for `CDL-038`.

## 7. Carry-forward constraints for later node-schema lanes

`No runtime implementation of promotion logic is ratified in Phase 344.`

Later phases may not:

- treat promotion as an in-place visibility edit,
- bypass `CDL-034` reserved-field and collision rules,
- inherit private-node `validation_state` into the public successor,
- turn private corroboration or local reuse into automatic public credit.

## 8. Non-goals and canonical anchors

Non-goals:

- no ratification of `CDL-038`,
- no runtime implementation of promotion logic,
- no automatic public corroboration inheritance,
- no automatic public reuse-credit or reputation carry-forward.

Canonical anchors:

- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md`
- `docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_evidence_prelock_343_v0.1.md`
- `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`
- `docs/specs/ilc_node_schema_concretization_proposals_v0.1.md`
- `docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md`
