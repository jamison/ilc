# ILC ADR-0019 Governance Compilation Boundary Disposition 708 v0.1

Status: disposition artifact
Date: 2026-04-17
Phase: 708
Related source: `docs/adr/ADR_0019_Graph_Native_Governance_Compilation_Boundary.md`

`adr_0019_disposition_published`
`adr_0019_explanatory_boundary_preserved`
`bounded_graph_compilation_surfaces_remain_preferred_direction`
`compiled_artifacts_not_raw_nodes_feed_runtime`
`governance_compilation_boundary_remains_explicit`

## 1. Inherited ADR statement

ADR-0019 remains the correct long-horizon architectural direction:

- keep a small audited kernel code-resident
- allow bounded declarative governance surfaces to become graph-compilable over
  time
- force every governed surface to be classified explicitly
- require compiled artifacts, not raw graph nodes, to feed runtime decisions

This disposition does not replace ADR-0019. It states what part of ADR-0019 is
still explanatory framing and what part is now a live planning / spec boundary.

## 2. Explanatory framing that remains explanatory

The following ADR-0019 content remains explanatory direction rather than current
binding law:

- the long-horizon ambition that more governance surfaces eventually become
  graph-compilable
- any future self-same genesis or canonical governance-node sourcing
- any implied future where the consensus kernel itself becomes graph-defined

These ideas may guide design discussion, but they are not executable law merely
because ADR-0019 described them.

## 3. Surfaces promoted to active planning / spec boundary

The following ADR-0019 content is now an active live-planning boundary:

- every new governable surface must be classifiable as `kernel_resident`,
  `graph_compiled`, `runtime_derived`, or `operator_local`
- bounded declarative surfaces remain the preferred candidate set for future
  graph-native compilation
- runtime decisions must consume compiled artifacts rather than raw governance
  nodes directly
- provenance and admissibility remain mandatory parts of the compile boundary

This is the spec-level meaning of ADR-0019 in the current frontier.

## 4. Boundary preserved in current window

The explicit governance-compilation boundary remains:

- kernel-resident:
  - cryptographic primitives
  - compiler / loader semantics
  - transport and security-critical runtime internals
  - storage internals
  - consensus execution kernel internals
- graph-compilation candidates:
  - governance constants
  - policy thresholds
  - bounded decision tables
  - declarative protocol rules
  - schema and validation profiles
  - activation flags and sunset rules

Window `707-712` preserves this boundary; it does not widen it.

## 5. Explicit non-goals

This disposition does not authorize:

- unrestricted executable code loaded from governance nodes
- graph-defined replacement of security-critical kernel internals
- automatic runtime self-modification
- silent conversion of ADR-0019 into a blanket mandate that “more graph-native”
  is always better

The preserved boundary is the point. Overreach is still prohibited.
