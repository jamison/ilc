# ExecutableStarMap And ExecutionCapsule Spec - Phase 1620

**Phase:** 1620
**Status:** Provisional specification complete
**Date:** 2026-10-21
**Authority class:** NON-SENSITIVE spec-only research

## §1 - Non-Load-Bearing Preamble

Every field and semantic here is **provisional unless and until adopted under
the applicable authority**. `ExecutableStarMap` and `ExecutionCapsule` are
research structures, not registered protocol types. The selected research
encoding and golden vectors are not canonical wire formats, hash preimages, or
node types.

The design is local-first and content-addressed. Agents resolve bounded evidence
from their own accepted views and exchange immutable objects or receipts. This
spec creates no central registry, global checker, global active-view pointer, or
permanent permission cache.

## §2 - `ExecutableStarMap` Versus ILC `star_map`

The names are similar; the governed surfaces are not.

### ILC `star_map`-specific protocol authorities

| Authority | Source-specific scope |
|---|---|
| CDL-076 | Lightweight truth-primitive announcement gossip after persistence; not general star-map governance. |
| CDL-077 | Generic CID-addressed WANT-HAVE/WANT-BLOCK pull-fetch. |
| CDL-079 | Bootstrap `star.map` distribution. |
| CDL-080 | N-gram route index as advisory L3 routing between announcement and authoritative L2 fetch. |
| ADR-0033 | Published navigation results become first-class `star_map` epistemic nodes at publication/reliance boundaries. |

### Adjacent transport and type architecture

| Authority | Separate scope |
|---|---|
| ADR-0030 | Node embedding substrate and content typing. |
| ADR-0035 | Homoiconic type-definition architecture. |
| CDL-097 | Ratified type-definition authority and type-registry boundary. |

This spec's `ExecutableStarMap` is a directed typed computation recipe. It does
not amend any authority above. The undirected membership Laplacian can support
discovery and spectral analysis, but it cannot establish operand order, role
identity, multiplicity, effects, authorization, or computational sufficiency.

## §3 - `ExecutableStarMap` Schema

Research discriminator: `recipe_definition_v0`. Research encoding is UTF-8
JSON with sorted keys, no insignificant whitespace, integers only for integral
values, and canonical decimal strings for nonintegral numeric boundaries. This
choice is reproducibility scaffolding only.

| Field | Research type | Contract |
|---|---|---|
| `encoding_version` | fixed string | `recipe_definition_v0`; version participates in recipe identity. |
| `boundary_ports` | bounded ordered array | Typed inputs/outputs visible at recipe boundary. |
| `steps` | bounded ordered array | Finite step definitions; nested recipe refs have explicit depth and total-step caps. |
| `dependency_refs` | bounded ordered CID array | Implementation, schema, law/policy, and data dependencies. |
| `declared_outputs` | bounded ordered array | Named output roles, types, and multiplicities. |
| `outcome_contract` | typed enum map | Accepted, rejected, deferred, unresolved, and resource-exhausted outcomes. |
| `effect_contract_ref` | CID | Permitted and prohibited effects; omitted effects are not authorized. |
| `budget_contract` | bounded object | Time, memory, bytes, steps, depth, and external-call caps. |
| `fallback_policy_ref` | CID or null | Authority-preserving fallback rules; null means no fallback. |
| `created_at` and `author_ref` | timestamp and identity ref | Historical authorship, not execution permission. |

Each step contains `step_id`, `operation_ref`, `operation_version`, ordered
`input_bindings`, ordered `output_bindings`, optional nested recipe ref,
dependency refs, effect subset, and budget subset. `step_id` is unique only
inside one recipe. The same label may appear in another recipe.

Input bindings are `(role, ordinal, value_ref, expected_type)`. Ordinals are
**zero-based**, matching recipes v0.4. `(role, ordinal)` is unique within a
step; `value_ref` may repeat, so `multiply(x,x)` retains both operand positions.
Sufficiency-claim or TranslationPassport refs are optional and appear only when
they justify reuse/substitution. Direct execution requires no sufficiency claim.

## §4 - Identity Separation

| Identity | Research preimage | Purpose |
|---|---|---|
| Recipe identity | Encoding version plus canonical recipe definition | Says what computation is specified. |
| Invocation identity | Recipe CID, ordered input commitments, implementation ref, budget, requested effects, scope, authority-view checkpoint, caller nonce/intention ID | Identifies this intentional run. A fresh nonce permits a deliberate repeat and prevents cache identity from becoming replay suppression. |
| Output digest | Hash algorithm/domain plus exact produced bytes or canonical typed output | Says what was produced; never substitutes for invocation or recipe identity. |

Execution occurrence identity is a fully qualified path. It contains the root
`invocation_id`, followed by one frame for every nested recipe call. Each parent
frame binds `(recipe_id, call_site_step_id, call_site_occurrence_index,
child_binding_ordinal)`, and the leaf binds
`(recipe_id, step_id, occurrence_index)`. Occurrence indexes and child-binding
ordinals are zero-based and derived from the deterministic execution order of
their parent frame. No global mutable counter participates in identity.

## §5 - Ordered Role Binding And Structural Closure

Role names/cardinalities alone are insufficient. Every `(parent_type, role)`
has permitted child types, cardinality, order, and bounds.

| Parent type and role | Permitted target types | Cardinality/ordering |
|---|---|---|
| Recipe `step` | StepDefinition | 1..bounded N, recipe order |
| Step `operation` | OperationDescriptor | exactly 1 |
| Step `input` | BoundaryInput, PriorStepOutput, ImmutableArtifact | 0..bounded N, `(role, ordinal)` order |
| Step `output` | OutputDescriptor | 1..bounded N, ordinal order |
| Step `dependency` | SchemaDescriptor, ImplementationDescriptor, PolicyObject, LawEvidenceRecord, ImmutableArtifact | bounded set with canonical CID order |
| Invocation `recipe` | RecipeDefinition | exactly 1 |
| Invocation `input` | ImmutableArtifact or canonical scalar descriptor | matches recipe boundary exactly |
| Invocation `implementation` | ImplementationDescriptor | one per executable operation/recipe binding |
| Invocation `authority_view` | AuthorityViewCheckpoint | exactly 1 for governed use |
| Capsule `invocation` | Invocation | exactly 1 |
| Capsule `receipt` | ExecutionReceipt | zero when prepared; exactly 1 when completed |
| Receipt `output` | ImmutableArtifact or canonical scalar descriptor | matches declared outputs |
| Receipt `trace` | ExecutionTrace | exactly 1 |

Wrong target type is `contradictory`, not missing. It counts against retrieval
budgets and blocks semantic evaluation. A reference is resolved only when its
object is fetched/locally present, CID/integrity checked, structurally validated,
and accepted under the observer's bounded view. Structural closure values are
`complete`, `missing`, `contradictory`, and `resource_exhausted`.

A capsule is structurally self-contained when every required selected-path role
is resolved under its declared domain, access, view, and resource bounds.
Optional provenance not consumed by the selected operation is not a required
object. Structural self-containment does not require execution or completion.

## §6 - `ExecutionCapsule` Schema And Lifecycle

An `ExecutionCapsule` is a packaging view over immutable references, not a copy
or closed snapshot.

| Field | Research type | Meaning |
|---|---|---|
| `capsule_version` | fixed string | `execution_capsule_v0`. |
| `recipe_ref` | CID | Recipe identity. |
| `invocation_ref` | CID | Specific invocation identity. |
| `scope_ref` | CID | Domain, network, purpose, requested effects, and policy scope. |
| `dependency_manifest_ref` | CID | Role/type/cardinality/bound contract and required-object set. |
| `prepared_receipt_ref` | CID | Structure/identity/dependency/scope checks; no output implied. |
| `execution_receipt_ref` | CID or null | Null when no historical execution is recorded. |
| `authority_view_checkpoint_ref` | CID | Exact accepted authority view for the assessed action. |
| `availability_evidence_refs` | bounded CID array | Readiness observations; never permission. |
| `sufficiency_claim_refs` | bounded CID array | Optional reuse/substitution evidence. |
| `created_at` and `author_ref` | timestamp and identity | Historical packaging. |

### Three independent concepts

- **Prepared:** invocation structure, identities, dependency contract, scope,
  and bounds were checked. No execution result exists yet.
- **Completed:** a historical execution outcome and receipt/output refs exist.
  Completion remains true even if bytes disappear or policy later changes.
- **Use-time readiness:** selected-path required bytes are locally retained or
  technically retrievable, integrity-checked, and held through consumption (or
  fetched and rechecked at consumption). Readiness says nothing about whether
  the observer is permitted to perform the requested use; current observer
  permission is the separate substantive assessment below.

Action-relative state:

| Action | Required lifecycle fact |
|---|---|
| Execute prepared invocation | Prepared; completion not required. |
| Reuse prior result | Completed plus current affirmative assessments and readiness. |
| Inspect historical execution | Completed; payload may be unavailable. |
| Resolve/fetch dependencies | Prepared or completed according to request. |

Transition to completed requires complete structure, affirmative execution
authority for the attempted action, ready selected-path dependencies, execution
under the bound implementation/budget/effects, and an immutable receipt plus
trace. Rejection/deferment creates trace evidence but not a completed successful
result unless the outcome contract explicitly defines that historical outcome
as the completion being recorded.

### Six separate assessments and aggregate rule

| Assessment | Values |
|---|---|
| Structural closure | `complete`, `missing`, `contradictory`, `resource_exhausted` |
| Computational contract | `affirmative`, `negative`, `unresolved` |
| Historical production authority | `affirmative`, `negative`, `unresolved` |
| Present artifact eligibility | `affirmative`, `negative`, `unresolved` |
| Current observer permission | `affirmative`, `negative`, `unresolved` |
| Use-time readiness | `ready`, `not_ready`, `unresolved` |

Deterministic aggregate:

1. non-complete structure returns `unresolved_pending_evidence` without semantic
   evaluation;
2. any applicable conclusive negative substantive verdict returns
   `rejected_use`;
3. otherwise any unresolved substantive verdict returns
   `unresolved_pending_evidence`;
4. all substantive verdicts affirmative but readiness not ready returns
   `unresolved_pending_evidence`;
5. all substantive verdicts affirmative and readiness ready returns
   `authorized_reuse`.

Malformed evidence is a structural failure, not automatic refutation.

### Invocation-local custody and evidence classes

Required objects are determined by the selected operation/use contract. A local
successful retrieval observation binds invocation, observer, observing
component, exact CID, integrity, network/use scope, checkpoint/context, time,
freshness, and custody through consumption. Safe execution pins checked bytes or
rechecks retrieval/integrity at consumption. An unexpired observation cannot
prove that evicted bytes remain available.

Evidence classes remain separate: local successful retrieval; provider
retention advertisement; third-party availability attestation with explicit
issuer authority/scope/freshness; and storage/replication promise. Only direct
fetch/check proves local possession, without a circular requirement to fetch a
second certificate for bytes already held.

### Authority-view contract

1. **Identity:** exact CIDs of governing policy and eligibility records.
2. **Authentication evidence:** issuer/deliverer, scope, lineage, signature or
   equivalent evidence; sequence alone proves neither authenticity nor freshness.
3. **Acceptance policy:** observer-local rules for accept/update/reject/conflict.

An `authority_view_checkpoint` binds observer, network, use scope, lineage,
policy CID, eligibility CID, validity interval, and freshness evidence. It is
distinct from historical production checkpoints. Rollback/replay/equivocation
are resolved per lineage and scope; conflict remains unresolved without an
authorized resolution. The local accepted-view pointer is not presumed to be a
graph node or canonical type.

### Authority-preserving fallback

| Selected fallback condition | Decision |
|---|---|
| Applicable fallback authority, scope/effects, fresh view, and selected-path dependencies all satisfied | Fallback may execute; record its own invocation and receipt. |
| Fallback authority absent | `unresolved_pending_evidence`; capsule signature grants no permission. |
| Some original-path objects unavailable but fallback-path objects ready and fallback independently authorized | Fallback may execute; original objects are not artificial requirements. |
| Fallback-path object missing/evicted | Not ready; retrieve/check or remain unresolved. |
| Fallback changes requested effect or scope | Re-authorize under the changed request; no borrowed permission. |

## §7 - Accepted-State History Versus Execution Trace

Accepted-state history is an immutable record of events/transitions accepted
under the applicable policy. Acceptance does not establish mathematical or
factual truth. Execution trace records the current run, including rejected,
deferred, unresolved, and resource-exhausted attempts.

A rejected attempted transition leaves protected application state unchanged.
A separately authorized audit append may record the rejection. Trace entries
bind invocation/occurrence identity, input commitments, operation/version,
outcome code, reasons, effects attempted/applied, resource use, and evidence
view. History includes only the accepted transition record authorized by its
policy; trace preserves the attempt regardless.

## §8 - Candidate Composition Laws And Research Vectors

| Candidate law | Premises | Proof status | Tests | Runtime status | Governance status |
|---|---|---|---|---|---|
| Sequential exact composition | Total typed operations; matching domains; exact preserved observables/effects | Written finite argument in research | Phase 1621 bounded fixtures | Not implemented | Nonbinding |
| Approximation composition | Named metrics; compatible units; explicit Lipschitz/error rules | Conditional derivation | Future numeric vectors | Not implemented | Nonbinding |
| Guarded substitution | Guard true; claim exact scope/version; current authority/readiness | Conditional argument | Phase 1621 negative cases | Not implemented | Nonbinding |
| Deterministic-check reuse | Same checker/version/input/view and immutable evidence | Conditional argument | Future cache invalidation cases | Not implemented | Nonbinding |
| Parallel commutativity | Disjoint or proven-commuting effects and deterministic operations | Unproved generally | Counterexample required before use | Not implemented | Nonbinding |

No general edge-commutativity claim is made.

### Four-property table and golden vectors

| Property | Separate definition | Positive vector | Negative vector |
|---|---|---|---|
| Contract determinacy | One canonical meaning for roles, domains, outputs, effects, and outcomes | `multiply` with `left@0`, `right@1`, integer domain, exact output/effect-free contract | Same inputs without ordinal/role distinction; must reject as ambiguous |
| Execution determinism | Same bound implementation/input/profile yields same typed outcome | Exact integer `add(2,3)=5` under pinned implementation | Unpinned implementation or unspecified rounding; must be unresolved/rejected |
| Checker determinism | Same claim/evidence/checker/view yields same verdict/reason | Exhaustive finite parity fixture with pinned checker CID | Checker version absent or unordered evidence consumption; must reject |
| Reproducibility | Independent run can reconstruct artifacts and method from recorded identities/environment | Recipe, fixture, checker, command, environment, and result hashes all present | Seed-only stochastic receipt without backend/environment; not reproducible |

These vectors are concrete research fixtures for Phase 1621. Their JSON-like
representation follows `recipe_definition_v0`; it is not a protocol encoding.

## §9 - Open Questions For Phase 1621

1. E1 and E2b must exhaustively establish expected-valid claims; E2a, E3, E4,
   and E5 must produce independently checked separating counterexamples.
2. The six records must pin fixture IDs, domains, expected/actual verdicts,
   evidence types, typed receipts, checker identity, and deterministic hashes.
3. Structural failures, wrong role target types, missing fields, bound failures,
   and resource exhaustion must prevent semantic evaluation.
4. Tests must keep rejection reason/effects in the observation contract only
   when declared observable.
5. Revision tests must use a genuine old-equivalence/new-divergence witness, not
   an arithmetic tautology.
6. The SIM must test the aggregate six-assessment rule, prepared/completed/
   readiness separation, invocation replay distinction, stale views, and
   authority-preserving fallback without claiming production security.

### Routed implementation obligations

- **Row 35a** owns interpreter lifecycle mechanics: derivation of the fully
  qualified occurrence path, prepared/completed state transitions, bounded
  dependency traversal, deterministic execution order, invocation replay,
  authority-preserving fallback, and trace/receipt production. It may not
  collapse invocation, occurrence, recipe, or output identity.
- **Row 35c** owns observer-local use decisions: authority-view acceptance,
  stale/replayed/conflicting evidence handling, current permission, technical
  readiness and custody, aggregate decisions, and cache/result invalidation. It
  must preserve the separation between historical completion, present
  permission, and readiness.
- **Phase 1621-Fix1** owns only finite evidence-object validation and
  mathematical verification. It does not implement either downstream runtime.

## §10 - Non-Claims

No CDL is opened or numbered. No field, type, encoding, law, vector, authority
view, or capsule is binding or canonical. No `ilc_core/`, LMDB, graph,
`star_map`, routing, announcement, fetch, type registry, wallet, ECU, ILC,
settlement, minting, validator, jury, network, epoch, public-RC, or mainnet state
changes. CDL-076/077/079/080 and ADR-0033 remain unchanged. ADR-0033's
publication/reliance boundary is preserved. Candidate laws are not claimed
proved beyond their stated assumptions.
