# ILC Graph Linkage and Dependency Contract Candidate v0.1

Status: Non-normative planning artifact — docs-only contract candidate
Date: 2026-03-18
Owner: GPT-5 Codex
Purpose: Provide a single docs-only contract candidate for Graph Node linkage semantics and
dependency classification so future schema and economics work can converge on one auditable
baseline.

## 1. Scope boundary

This document is not ratified law, not a final schema, and not authorization for runtime changes.

It is a consolidation candidate built from the current research stack:
- `docs/research/ilc_graph_linkage_contract_draft_v0.1.md`
- `docs/research/ilc_primitive_to_link_template_matrix_v0.1.md`
- `docs/research/ilc_dependency_closure_preservation_architecture_memo_v0.1.md`
- `docs/research/ilc_host_admission_and_dependency_serviceability_memo_v0.1.md`

Its purpose is narrow:
- define the minimum linkage contract the project likely needs,
- make required-vs-reference dependency semantics explicit,
- and provide a stable docs-only target for later schema work.

## 2. Why this candidate now

The repo already contains enough signal to justify a single candidate contract:
- content-addressed Graph Nodes are already canonical architecture,
- dependency-closure preservation now depends on explicit linkage semantics,
- host serviceability depends on knowing which links imply closure obligations,
- and later economics will need a way to distinguish productive dependencies from ornamental
  references.

Without a single docs-only candidate, later work is likely to drift into:
- multiple near-synonymous link vocabularies,
- host logic guessing what counts as a required ancestor,
- reward logic being attached to arbitrary citations,
- and duplicate/equivalence handling becoming inconsistent across lanes.

## 3. Core contract principles

### 3.1 Graph Node truth remains identity-and-linkage only

The base Graph Node contract should define:
- node identity,
- authorship/signature,
- deterministic encoding,
- and graph linkage.

It should not encode reward logic, routing hints, or mutable host locations.

### 3.2 Required dependencies must be first-class

The contract must distinguish:
- dependencies required for serviceability and economic eligibility,
from:
- references that are merely contextual or explanatory.

This distinction is the foundation for:
- dependency-closure preservation,
- host admission/serviceability,
- and later challenge logic.

### 3.3 Link types should be few, stable, and machine-usable

The contract should prefer a small linkage vocabulary over a large expressive thesaurus.

The goal is:
- enough expressiveness for automation,
- not maximum linguistic richness.

### 3.4 Duplicate and revision semantics must not be left implicit

The linkage contract should leave room to distinguish:
- exact duplicate,
- semantic equivalent,
- prior version,
- superseded node,
- revived stewardship of existing canonical content.

That boundary is critical for founder/steward economics later.

## 4. Candidate linkage object

The exact eventual schema encoding may vary, but the candidate linkage object should minimally carry:

- `target_node_id`
  - canonical node identity of the linked node

- `link_type`
  - one of the canonical linkage enum values

- `dependency_class`
  - `required` or `reference`

- `justification`
  - optional explanatory note or semantic context

- `scope_class`
  - optional field for later narrowing/weighting semantics if needed

This is enough to support:
- primitive-specific legal link templates,
- dependency-closure reasoning,
- host-side dependency scans,
- and future payout traceability.

## 5. Candidate canonical link-type enum

Recommended baseline set:

- `depends_on`
  - the node materially depends on the target for validity or productive use

- `derived_from`
  - the node is substantively built from or transformed from the target

- `refutes`
  - the node contradicts or contests the target

- `confirms`
  - the node supports or validates the target

- `reframes`
  - the node reorganizes or reformulates the target while preserving lineage

- `previous_version_ref`
  - the node continues, updates, or supersedes a prior version lineage

Possible later additions, but not recommended for the first contract freeze:
- `refers_to`
- `amplifies`
- `is_subset_of`

The reason to keep the initial set small is straightforward:
- every extra link type multiplies later schema, host, accounting, and challenge complexity.

## 6. Required-vs-reference semantics

### 6.1 `required`

Meaning:
- the linked node must be available and part of valid dependency closure for the dependent node to
  count as serviceable or economically eligible.

Consequences:
- host admission logic must resolve it,
- host serviceability audits can challenge it,
- later upstream allocation logic may flow across it.

### 6.2 `reference`

Meaning:
- the linked node is contextual, explanatory, comparative, or supplementary, but not mandatory for
  serviceability or baseline economic eligibility.

Consequences:
- hosts need not resolve it to claim full dependency-complete serviceability,
- later reward logic should not treat it like a productive dependency by default.

This distinction should be treated as mandatory in future contract work.

## 7. Candidate primitive-to-link templates

This candidate follows the current working primitive family as a design aid only.

### 7.1 Assert

Likely legal links:
- `depends_on`
- `derived_from`
- `previous_version_ref`
- later, possibly `refers_to`

Typical required use:
- when the assertion materially depends on prior canon or evidence

### 7.2 Observe

Likely legal links:
- `depends_on`
- `derived_from`

Typical required use:
- source/provenance/instrumentation dependencies

### 7.3 Model

Likely legal links:
- `depends_on`
- `derived_from`
- `previous_version_ref`
- optionally `reframes`

Typical required use:
- strongest dependency-closure case in the current matrix

### 7.4 Refute

Likely legal links:
- `refutes`
- `depends_on`

Typical required use:
- explicit target relation plus supporting counter-evidence where needed

### 7.5 Confirm

Likely legal links:
- `confirms`
- `depends_on`

Typical required use:
- explicit target relation plus supporting confirmatory evidence

### 7.6 Reframe

Likely legal links:
- `reframes`
- `derived_from`
- `previous_version_ref`

Typical required use:
- preserve lineage while allowing substantive reorganization

## 8. Duplicate and revision guidance

The contract candidate assumes the following future-compatible distinctions:

### Exact duplicate

- same payload
- same canonical node identity
- no fresh founder surface

### Semantic equivalent

- not byte-identical
- may require future alias/equivalence treatment
- should not automatically imply fresh founder economics

### Superseded node

- remains in history
- may lose visibility or current weight
- still contributes to lineage

### Revived stewardship

- old canonical content becomes actively available again
- may justify stewardship/availability value
- should not normally recreate founder rights

## 9. Host-serviceability implications

This contract candidate is intentionally compatible with the host-serviceability model:
- nodes declare canonical dependencies,
- hosts resolve required closure,
- audits target host resolvability claims,
- not node truth itself.

That means:
- host routing/location data should remain outside the node,
- serviceability obligations are layered above node identity and linkage,
- and later challenge logic should target host claims against required closure.

## 10. Accounting implications

This contract candidate is also intentionally compatible with the current accounting direction:
- node-level usefulness should key off canonical IDs and accepted dependency structure,
- host-level service should key off host/service receipts,
- upstream allocation should flow over `required` dependency paths, not arbitrary references.

This is the cleanest path to keeping:
- node importance,
- host service quality,
- and dependency-closure economics

from collapsing into one noisy metric.

## 11. Recommended next use of this candidate

This candidate should be used as:
- a docs-only baseline for future schema discussion,
- a review target for terminology normalization,
- and an anti-refactor anchor for future economics and host-serviceability work.

It should not be used as:
- runtime authorization,
- proof that the primitive family is fully ratified,
- or a substitute for a later actual schema artifact.

## 12. Bottom line

The project is now at the point where a docs-only linkage contract candidate is justified.

The minimum viable candidate is:
- one small canonical link vocabulary,
- one mandatory required-vs-reference distinction,
- one clean linkage object shape,
- and one primitive-facing interpretation layer.

That is enough to make later schema/economics work more auditable and less likely to drift.
