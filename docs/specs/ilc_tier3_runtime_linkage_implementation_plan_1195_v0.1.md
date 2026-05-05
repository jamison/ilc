# Tier-3 Runtime Linkage Implementation Plan 1195 v0.1

**Phase:** 1195
**Date:** 2026-05-05
**Status:** scope committed — no runtime mutation

`tier3_runtime_linkage_scope_committed_phase_1195`

---

## 1. Purpose

This phase advances the Tier-3 runtime linkage lane after the governance prerequisites
were satisfied by ADR-0020 acceptance. The scope-first rule remains in force: implement a
runtime first tranche only if inspection shows a small, unambiguous, testable path with no
protocol ambiguity.

Inspection result: the implementation path is not small enough for a safe Phase 1195 code
mutation. This phase therefore publishes the implementation plan only.

---

## 2. ADR-0020 Runtime Implications

ADR-0020 establishes the Knowledge-Node-First Design Principle:

- governed information, policy, parameters, and durable documentation should first be
  considered as graph-native knowledge nodes;
- genesis-layer membership should be minimized to surfaces that cannot be wrong without
  catastrophic failure;
- governance constants and stable documentation should receive migration classifications;
- no knowledge node may be required before the graph can accept knowledge nodes.

Tier-3 runtime linkage is the concrete runtime lane for this principle. It must make
`schema:*` and `runtime:*` surfaces addressable, versioned, and linkable to the signed
Genesis/star-map reference chain without moving bootstrap-critical state into the graph
before the graph can accept it.

---

## 3. Existing Runtime Surfaces

Inspection found these adjacent surfaces:

| Surface | Current state |
|---------|---------------|
| `ilc_core/node/node_schema_core_runtime_360.py` | CDL-034 / CDL-073 node schema core runtime exists for authored payload normalization and primitive type validation |
| `ilc_core/node/executable_descriptor_runtime_363.py` | CDL-037 executable descriptor runtime exists with sandboxed runtime-binding validation |
| `ilc_core/network/star_map/star_map_route_index_runtime.py` | Star-map route index runtime exists as L3 routing support |
| ADR-0033 | Published star-map navigation results can become first-class `star_map` nodes |
| Genesis star-map artifacts | v0.1 and v0.2 candidate carry `candidate_id`, `category`, `canonicality_tier`, `decision_log_refs`, `graph_projection`, and attestation metadata, but not explicit `schema:*` / `runtime:*` node classes |

Current gap:

- No single runtime module currently owns `schema:*` / `runtime:*` node-class binding.
- Existing node schema validation admits primitive types like `knowledge_claim`,
  `execution_descriptor`, and `governance_proposal`, but does not define Tier-3
  schema/runtime node classes.
- Executable descriptor runtime validates sandboxed runtime bindings, but that is not the
  same as graph-native runtime node linkage.

---

## 4. Proposed Tier-3 Model

Tier-3 should introduce two graph-native node families:

### `schema:*`

Purpose: durable schema contracts that agents and tooling can reference.

Minimum fields:

- `schema_id`
- `schema_version`
- `schema_digest`
- `schema_artifact_ref`
- `authority_ref`
- `lineage_ref`
- `status` (`draft`, `accepted`, `ratified`, `superseded`)

### `runtime:*`

Purpose: durable runtime binding records that link implementation artifacts to ratified
schema, CDL, and ADR surfaces.

Minimum fields:

- `runtime_id`
- `runtime_version`
- `implementation_ref`
- `schema_refs`
- `cdl_dependency_refs`
- `adr_dependency_refs`
- `test_evidence_refs`
- `lineage_ref`
- `status` (`planned`, `active`, `superseded`)

The two families must be linkable:

`schema:* -> runtime:* -> signed Genesis/star-map lineage`

---

## 5. Signed Star-Map Binding

Tier-3 records should bind to the signed reference chain without mutating signed Genesis
v0.1:

1. Read signed Genesis v0.1 as immutable authority baseline.
2. Reference v0.2 candidate only as unsigned candidate until signing authorization occurs.
3. Bind Tier-3 node records to signed or candidate star-map artifacts by digest/reference,
   not by regenerating them.
4. Preserve the immutable diagnostic SHA:
   `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`.

---

## 6. Implementation Sequence

Recommended sequence:

1. Add a planning-only schema document defining `schema:*` and `runtime:*` node contracts.
2. Add pure validation helpers in a new module, likely
   `ilc_core/node/tier3_runtime_linkage_runtime.py`.
3. Use deterministic JSON normalization (`sort_keys=True`, compact separators,
   `allow_nan=False`) for any machine-verifiable record.
4. Add tests for:
   - schema node required fields;
   - runtime node required fields;
   - lineage reference required;
   - version token required;
   - no signed Genesis v0.1 mutation.
5. Only after validation runtime exists, bind selected ratified artifacts as initial
   `schema:*` / `runtime:*` candidate records.

---

## 7. Runtime Version Token

If implemented in a future phase, use a runtime token in this form:

```text
tier3_runtime_linkage_runtime_NNNN.v0.1
```

For example:

```text
tier3_runtime_linkage_runtime_120x.v0.1
```

No such token is introduced in Phase 1195.

---

## 8. Test Strategy

Phase 1195 planning tests should verify:

- this plan exists;
- the scope token exists;
- ADR-0020 is referenced;
- `schema:*` and `runtime:*` families are named;
- no runtime token is introduced;
- signed Genesis v0.1 mutation is out of scope.

Future implementation tests should be added only when the runtime module is created.

---

## 9. Non-Claims

This phase does not:

- implement Tier-3 runtime linkage;
- mutate `ilc_core/`;
- introduce a runtime version token;
- mutate signed Genesis v0.1;
- sign v0.2;
- open or ratify a CDL.
