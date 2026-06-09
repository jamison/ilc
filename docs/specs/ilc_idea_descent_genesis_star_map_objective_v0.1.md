# Idea-Descent Objective: Genesis Star-Map Candidate Refinement

PUBLIC_RC_EXCLUDE: idea_descent_genesis_star_map_objective_support_only
PUBLIC_RC_EXCLUDE_REASON: Local evaluator objective for private Genesis candidate
graph rehearsal. This document does not authorize signing, publication, graph
mutation, or public RC activation.

## Objective

Use the protocol-governed iterative refinement sidecar to evaluate proposed
Genesis star-map candidate artifacts against the current v0.2/v0.3 Genesis node
manifest lineage.

The current acceptance target is `out/genesis_core_star_map_v0.3_candidate.json`,
which is the Phase 1446 signed candidate star map referenced by
`ilc_core/rc/signing_ceremony_status.py`.

## Required Invariants

- Candidate JSON must be a deterministic object with `metadata`, `nodes`, and
  `edges`.
- The seven Genesis truth primitives must appear both as required nodes and as
  the canonical `metadata.transition_basis`.
- Genesis Agent 1 and its authority artifacts must remain present:
  `genesis_agent:01`, `artifact:genesis_agent1_pubkey_record_838a`,
  `ceremony:genesis_agent1_keygen_838a`,
  `artifact:genesis_authority_assertion_schema`, and
  `artifact:genesis_intent_attestation_init_authority_map`.
- Required Genesis nodes must remain signed, Genesis-attested, and attested by
  `genesis_agent:01`.
- Every edge endpoint must resolve to a candidate node.
- Every edge must carry a decomposition recipe grounded in truth primitives.
- The v0.3 candidate must retain the high-authority core bootstrap projection
  scope and the Phase 1387e expansion lineage unless a later signed successor
  manifest explicitly supersedes it.

## Non-Goals

This objective does not sign a new manifest, mutate any Genesis artifact, write
to the graph, allocate ECU, mint ILC, open or mutate a CDL/ADR, publish public
RC artifacts, or authorize public serving. It is an internal evaluator loop for
finding and repairing candidate graph-shape defects before any separate
authorized signing or launch step.
