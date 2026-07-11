# ILC Fix86 Content-Layer Edge Type Recipe Annotation v0.1

Status: support candidate, unsigned Atlas LMDB annotation

Phase: 1545p-Fix86

Date: 2026-07-11

## Purpose

This document records the graph-output contracts and irreducibility attestation
for the content-layer edge types produced by the six agent-issuable truth
primitives in `ilc_core/epistemic/truth_primitive_submission_runtime.py`.

Runtime preflight found 13 live content-layer output edge types, not 12. The
additional edge type is `supported_by`, produced by `refute.claim` for each
evidence node in `evidence_node_ids`. Because the runtime is the authoritative
source for this phase, Fix86 annotates all 13 live output edge types.

Content-layer edge types are not compositions of other truth primitives. They
are the output layer of truth primitive invocation. Governance edge types
compose primitives; content-layer edge types ARE the primitive outputs.

## Runtime Anchor

Authoritative runtime:

`ilc_core/epistemic/truth_primitive_submission_runtime.py`

Runtime version:

`truth_primitive_submission_runtime_868.v0.1`

Agent-issuable primitives:

| Primitive | Creates node | Output edge types |
| --- | ---: | --- |
| `assert.truth` | yes | `asserted_by`, `extends` |
| `validate.claim` | no | `validated_by` |
| `contradict.assert` | no | `contradicts` |
| `refute.claim` | no | `refuted_by`, `supported_by` |
| `link.claim` | no | `cites`, `elaborates`, `contrasts`, `instantiates`, `generalizes` |
| `revise.assert` | yes | `asserted_by`, `revision_of`, `revised_by` |

## Content-Layer Edge Type Table

| Edge type | Produced by primitive | Creates node | Source label | Target label | Semantic scope |
| --- | --- | ---: | --- | --- | --- |
| `asserted_by` | `assert.truth`, `revise.assert` | yes | `new_node_id` | `agent_id` | Agent attribution for an asserted or revised node. |
| `extends` | `assert.truth` | yes | `new_node_id` | `parent_node_id` | Lineage derivation from prior parent nodes. |
| `validated_by` | `validate.claim` | no | `target_node_id` | `agent_id` | Agent endorsement of an existing node. |
| `contradicts` | `contradict.assert` | no | `node_a_id` | `node_b_id` | Logical, empirical, or definitional conflict registration. |
| `refuted_by` | `refute.claim` | no | `target_node_id` | `agent_id` | Popperian falsification attribution. |
| `supported_by` | `refute.claim` | no | `refutation_context` | `evidence_node_id` | Evidence support context for a refutation. |
| `cites` | `link.claim` | no | `source_node_id` | `target_node_id` | Reference from source to target. |
| `elaborates` | `link.claim` | no | `source_node_id` | `target_node_id` | Added detail or context. |
| `contrasts` | `link.claim` | no | `source_node_id` | `target_node_id` | Material comparison or contrast. |
| `instantiates` | `link.claim` | no | `source_node_id` | `target_node_id` | Specific instance of an abstract target. |
| `generalizes` | `link.claim` | no | `source_node_id` | `target_node_id` | General form encompassing the target. |
| `revision_of` | `revise.assert` | yes | `new_node_id` | `source_node_id` | Forward supersession from new node to source node. |
| `revised_by` | `revise.assert` | yes | `source_node_id` | `new_node_id` | Backward pointer from source node to revised node. |

## Irreducibility Attestation

Each listed content-layer edge type is annotated as:

`decomposition_recipe = irreducible_primitive`

This means the edge type is an atomic graph-output contract of the named truth
primitive invocation. It is not produced by composing other truth primitives.

Incorrect statement:

`asserted_by = assert.truth composed with link.claim`

Correct statement:

`asserted_by` is produced by `assert.truth`; it is one of the output edges of
that primitive invocation.

## Relationship To Phase 1387h

Phase 1387h records that selected governance edge types reduce to truth
primitive compositions, such as `assert.truth` followed by `link.claim` or
`validate.claim` followed by `link.claim`.

Fix86 records the complementary fact: the content-layer edge types are the
irreducible outputs of truth primitive invocation. The two-level relationship is:

1. Governance edge type reduces to a truth primitive composition.
2. Truth primitive invocation emits content-layer edge types.
3. Content-layer edge types do not reduce further.

## LMDB Annotation Scope

Fix86 writes 13 support-candidate invariant nodes:

`invariant:fix86_content_layer_edge_type_irreducible_{edge_type}`

Each invariant node records:

- `edge_type`
- `produced_by_primitive`
- `creates_node`
- `source_label`
- `target_label`
- `semantic_scope`
- `decomposition_recipe`
- `runtime_version_anchor`
- `gap_register_row`
- token `content_layer_edge_type_irreducible_{edge_type}_invariant_fix86`

The `SOURCE_TREE_MEMBER` edge uses the existing source-tree manifest anchor:

`artifact:genesis_source_tree_manifest_candidate_1545p_fix38`

The prompt's earlier `genesis:genesis_root_v0.4` target was not present in the
current LMDB and was corrected before mutation.

## Non-Claims

This annotation does not activate the ADR-0035 type registry runtime.

This annotation does not open, amend, or ratify CDL-097, CDL-099, CDL-100, or
any other CDL.

This annotation does not create CDL-097 definition-node instances for these
edge types. That remains Gap G3 and belongs to Window 1577+.

This annotation does not annotate `finalizes`, which is produced by
`commit.epoch` and is consensus-layer only.

This annotation does not mutate `ilc_core/`, change runtime behavior, clear any
default-off guard, sign any Genesis artifact, publish any public mirror, activate
public RC, mint ECU, settle ILC, or transition epochs.
