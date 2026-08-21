# ILC REFUTES Edge Usage Discipline v0.1

Status: pre-public-RC schema discipline note
Phase: GAP-SCHEMA-PREREQS-00
Date: 2026-08-21

## 1. Purpose

This note locks the usage boundary for the Atlas `REFUTES` edge type before
public RC. The goal is to prevent refutation semantics from being represented
only as generic links after public graph data begins accumulating.

## 2. Required Use

`REFUTES` MUST be used when a graph record explicitly contests a named prior
node. This includes:

- `assert.refutation` records that identify the prior node being contested.
- `assert.revision` records whose rationale explicitly says the prior node is
  false, invalid, superseded because of error, or no longer supportable.
- Runtime or Atlas annotations that encode a concrete refutation relationship
  between a new assertion and an existing node.

The source of the `REFUTES` edge is the contesting node or assertion record.
The target is the specific prior node being contested.

## 3. Non-Required Use

`REFUTES` MUST NOT be used for:

- General disagreement with no named target node.
- Ordinary `link.claim` contrast, comparison, citation, elaboration, or
  instantiation.
- Revision history that corrects wording without contesting the truth of the
  prior node.
- `refute.claim` evidence support edges that already use the runtime
  `refuted_by` and `supported_by` graph-output contract.

## 4. Relationship To Existing Truth Primitive Runtime

CDL-074 runtime primitives currently emit lower-case operational edge labels
such as `refuted_by`, `supported_by`, `revision_of`, and `revised_by`.
This note does not mutate those runtime labels. It defines when the Atlas
semantic edge type `REFUTES` is required in graph classification,
annotation, or future public graph projection layers.

## 5. Non-Claims

This note does not add a new truth primitive, mutate CDL-074, change ECU
weighting, authorize public graph writes, or activate public P2P/fetch serving.
