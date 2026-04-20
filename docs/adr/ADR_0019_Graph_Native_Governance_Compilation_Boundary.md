# ADR-0019: Graph-Native Governance Compilation Boundary

**Status:** Accepted
**Date:** 2026-03-18
**Author:** GPT-5 Codex, in collaboration with Jamie (project lead)
**Source:** Window 441+ planning discussion, 2026-03-18
**Dependencies:** ADR-0007, ADR-0009, ADR-0011, ADM-003 v0.2, Window 434-440 handoff

---

## Context

ILC increasingly benefits from moving hard-coded governance values and bounded declarative policy surfaces into traceable, governable knowledge artifacts. The long-term design goal is not a runtime whose imperative core is freely authored by graph nodes, but a system where governable values and bounded rule surfaces are derived from historically anchored, auditable graph-native sources.

In the longer term, this may include self-same genesis or canonical knowledge-node sources for governable values, but only after the epistemic graph and distribution layer are stable enough to support them safely.

The risk is overreach. If the project tries to make the entire imperative runtime graph-defined too early, it creates bootstrap circularity, weakens auditability, and increases the attack surface for malformed or adversarial knowledge content.

What is needed is a clean boundary between a small audited kernel and the graph-native surfaces that kernel is allowed to compile and consume.

## Decision

Adopt the following architectural boundary as the preferred long-horizon direction.

### 1. Small audited kernel remains code-resident

The following remain kernel-resident by default:
- compiler / loader semantics,
- cryptographic primitives and verification routines,
- transport and security-critical runtime internals,
- storage engine internals,
- core consensus execution kernel until a later explicit governance decision says otherwise.

### 2. Bounded declarative governance surfaces are graph-compilable

The following are preferred candidates for graph-native compilation over time:
- governance constants,
- policy thresholds,
- bounded decision tables,
- declarative protocol rules,
- schema and validation profiles,
- activation flags and sunset rules.

### 3. Every governed surface must be explicitly classified

New rule/value surfaces should be classified as one of:
- `kernel_resident`,
- `graph_compiled`,
- `runtime_derived`,
- `operator_local`.

This classification exists to prevent policy sprawl, provenance loss, and ad hoc constants.

### 4. Compiled outputs, not raw graph nodes, feed runtime decisions

The runtime should consume validated compiled artifacts, not raw governance nodes directly.

The compilation pipeline should be:
- source-node selection,
- admissibility checks,
- deterministic compile step,
- signed or otherwise provenance-bound compiled output,
- runtime consumption of the compiled artifact.

### 5. Graph-native compilation is not self-modifying runtime by default

This ADR does not authorize:
- unrestricted executable logic loaded from governance nodes,
- node-defined cryptographic or compiler semantics,
- graph-defined replacement of security-critical kernel internals,
- unconstrained self-modifying runtime behavior.

## Consequences

Positive:
- reduces scattered hard-coded governance constants,
- improves provenance for future governance changes,
- aligns long-term architecture with graph-native protocol identity,
- creates a cleaner path for future governance-controlled compile surfaces.

Tradeoffs:
- requires a stricter source taxonomy,
- introduces a compiler/loader boundary that must itself remain small and well-audited,
- slows down any attempt to over-generalize graph-native behavior into imperative runtime too early.

## Sooner-rather-than-later implications

To avoid future refactoring churn, near-term windows should:
- tag new rule/value surfaces with provenance classes,
- avoid baking prototype defaults into runtime without traceability,
- keep measurement outputs distinct from ratified law,
- define graph-native compilation as a future lane now, even if implementation is deferred.

## Alternatives considered

### 1. Keep all governance values hard-coded in runtime

Rejected as the long-term direction because it creates traceability and governance-friction problems.

### 2. Make as much of the entire program graph-defined as possible

Rejected as an early or default strategy because it weakens auditability, increases bootstrap complexity, and risks an unsafe meta-circular system.

### 3. Externalize values only into operator-local config files

Rejected as insufficient because it lacks graph-native provenance and does not reflect constitutional/governance history in a first-class way.
