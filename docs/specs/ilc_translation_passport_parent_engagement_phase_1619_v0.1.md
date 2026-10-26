# TranslationPassport And Parent Engagement Spec - Phase 1619

**Phase:** 1619
**Status:** Provisional specification complete; graph materialization unresolved
**Date:** 2026-10-21
**Authority class:** NON-SENSITIVE spec-only research

## §1 - Non-Load-Bearing Preamble

Every field and semantic in this document is **provisional unless and until
adopted under the applicable authority**. This specification defines a local
application record and a research contract. It does not open CDL territory,
register a graph type, authorize submission, or invalidate any record
network-wide.

The direct runtime audit found no accepted type or payload contract that makes a
`TranslationPassport` graph object valid today. The local record described here
is usable for bounded application workflows, but its graph-node status remains
unresolved.

## §2 - `revise.assert` Foundation

The current implementation in
`ilc_core/epistemic/truth_primitive_submission_runtime.py` accepts an outer
envelope with protocol version, primitive, 96-character lowercase-hex
`agent_id`, nonnegative integer epoch, map payload, and native signature object.
Binary floating-point values in the payload are rejected.

For `primitive="revise.assert"`, the payload contract validates:

| Field | Runtime rule |
|---|---|
| `source_node_id` | Required nonempty string. |
| `revised_content` | Required map. |
| `revised_content.primitive_type` | Required nonempty string in the runtime's known primitive-type set. |
| `revision_rationale` | Required string, at most 2,048 UTF-8 bytes. |

The result creates a new graph node and declares exactly these edges:

```text
asserted_by: new_node_id -> agent_id
revision_of: new_node_id -> source_node_id
revised_by: source_node_id -> new_node_id
```

The native envelope verifier binds `key_ref` to `agent_id`, verifies the BLS
signature over canonical envelope bytes under the declared network domain, and
checks the payload digest. This authenticates the envelope and signer identity;
it does not, by itself, establish target-specific authority to publish a
TranslationPassport.

The attribution bridge maps accepted `revise.assert` events to artifact type
`revision_chain`. That is an ECU attribution-routing classification. It neither
defines `TranslationPassport` semantics nor proves that a revision edge is a
valid CDL-084 explicit nearest-first provenance-chain payload. Any economic use
must independently satisfy CDL-084/CDL-108 rules and avoid double attribution.

## §3 - Orthogonal Translation Semantics

A `TranslationContract` separates three dimensions that must not be inferred
from one another.

### Preservation criterion

| Kind | Required contract |
|---|---|
| `exact` | Named domain and observable boundary; source and target behavior must be equal for every admitted input under the declared relation. |
| `approximate` | Named metric/relation, units, exact decimal tolerance, direction of inequality, composition rule, and allowed error propagation. |

The criterion determines domain closure and error-propagation obligations. A
parent operation requiring an input omitted by the child representation cannot
borrow the child's admission guarantee. It must refine the representation,
provide the input independently, or decline the shortcut.

### Evidence class

Allowed provisional values are `formal_proof`,
`finite_exhaustive_verification`, `sampled_evidence`,
`verified_counterexample`, and `unresolved`. Evidence strength does not change
the preservation obligation. An exact claim can have only sampled support; an
approximate claim can have a formal proof.

### Numerical and execution profile

The profile separately binds determinism class, numeric representation,
precision, rounding, overflow behavior, resource bounds, applicable law/policy
refs, execution substrate constraints, and effect contract. Exact integers or
decimal strings are required for boundary values; no bare float is permitted in
an identity or authority preimage.

Examples:

| Preservation | Evidence | Profile | Correct interpretation |
|---|---|---|---|
| Exact equality | Sampled evidence | Deterministic Decimal profile | Exact behavior is claimed, but support is empirical and incomplete. |
| Approximation within Decimal `0.001` under a named metric | Formal proof | Deterministic rational/Decimal profile | The weaker approximation obligation has stronger support. |
| Exact equality | Verified counterexample | Any profile matching the claim | The exact claim is refuted in the declared domain; this says nothing about a narrower revised claim. |

## §4 - `TranslationContract` Field Schema

Provisional discriminator: `translation_contract_v0`.

| Field | Provisional type | Semantics | Provisional note |
|---|---|---|---|
| `schema_version` | fixed string | Exactly `translation_contract_v0`. | Not a registered protocol version. |
| `parent_claim_ref` | CID | Exact `SufficiencyMathematicalClaimV0` parent. | Does not import current eligibility. |
| `source_representation_ref` | CID | Representation accepted by the parent claim. | Must match the parent contract. |
| `target_representation_ref` | CID | Child/refined representation. | May add distinctions; cannot silently remove required ones. |
| `source_domain_ref` | CID | Parent input/state/action domain. | Immutable. |
| `target_domain_ref` | CID | Child domain. | Inclusion or translation relation must be explicit. |
| `translation_operation_ref` | CID | Pure transformation or typed relation. | Executable authority is separate. |
| `preservation_criterion` | structured tagged object | Exact or approximate obligation from §3. | Includes observation/effect boundaries. |
| `evidence_class` | enum | Support class from §3. | Orthogonal to criterion. |
| `evidence_refs` | bounded ordered array of CIDs | Proof, test, sample, or counterexample records. | Empty requires `unresolved`. |
| `numerical_execution_profile` | structured object | Determinism, precision, rounding, substrate, bounds, laws, effects. | No bare floats. |
| `admission_contract_ref` | CID | Typed admitted/rejected/unresolved semantics. | Child admission cannot be generalized to omitted parent inputs. |
| `authority_scope_ref` | CID | Scope required to apply or publish the translation. | Authentication does not imply this authority. |
| `source_view_ref` | CID | Observer-local view in which the source contract was resolved. | Not a global latest-state claim. |
| `target_view_ref` | CID | Observer-local view for the target. | May differ only under an explicit compatibility policy. |
| `freshness_rule_ref` | CID | Rule for source/target policy and evidence freshness. | Historical permission never supplies missing present authority. |
| `failure_outcomes` | bounded enum map | `not_applicable`, `insufficient_evidence`, `mismatch`, `unauthorized`, `stale_view`, `resource_limit`. | Total typed outcomes are preferred over exceptions. |
| `provenance_edge_plan` | fixed structured object | Proposed `revision_of`/`revised_by` mapping if later authorized. | A plan, not proof of materialization. |
| `created_at` | canonical UTC timestamp | Historical creation time. | Not current permission. |
| `author_ref` | identity ref | Local record author. | Not automatic submit authority. |
| `supersedes_contract_ref` | null or CID | Backward pointer to prior contract. | No mutable forward supersession. |

A stale source or target view never silently changes either contract. The
resolver returns a typed stale/unresolved outcome unless a named policy permits
that exact historical view and all required authority remains valid.

## §5 - Missing-Evidence And Stale-View Decisions

| Condition | Outcome | Required record |
|---|---|---|
| Shortcut evidence unavailable, while direct computation is independently authorized and ready | Use an existing authorized reference result or perform direct computation; do not block solely on the shortcut | Missing shortcut refs, independent execution authority, operation/version, inputs, and resulting receipt. |
| Required authority or freshness evidence unavailable | `unresolved_pending_evidence`; do not use the translation | Missing evidence set, authority/policy ref, view/checkpoint, freshness rule, and retry condition. |
| Evidence present but operation, domain, scope, or version mismatches | Reject this proposed use; do not infer that the source claim itself is false | Exact mismatch dimensions, compared identities, and rejection receipt. |
| Historical view explicitly permitted under a named policy | Evaluate only within that policy's declared scope and time boundary | Policy ref/version, historical checkpoint, permitted purpose/effects, and current authority evidence. Historical permission cannot replace missing required authority. |
| Direct computation is not independently authorized | Do not recompute merely because shortcut evidence is absent | Separate authority verdict and reason code. |
| Counterexample is malformed or unauthenticated | Reject the evidence object; leave the underlying claim unresolved unless other evidence decides it | Structural/authentication failure distinct from mathematical verdict. |

## §6 - `TranslationPassport` Local Record And Type Audit

The local application object has provisional discriminator
`translation_passport_local_v0` and contains:

| Field | Meaning |
|---|---|
| `translation_contract_ref` | Exact contract from §4. |
| `parent_claim_ref` | Exact immutable parent claim. |
| `source_node_ref` | Existing source node or local source object. |
| `child_representation_ref` | Refined child representation. |
| `eligibility_assessment_ref` | Historical use-time assessment; may be unresolved. |
| `authority_evidence_refs` | Evidence considered for the proposed use. |
| `availability_evidence_refs` | Readiness observations, separate from permission. |
| `local_record_id` | Local content hash derived from the canonical record body under the preimage rule below. |
| `created_at` and `author_ref` | Historical authorship. |
| `supersedes_passport_ref` | Optional backward pointer. |

This record may be stored in an application-local content-addressed store. That
store is not a central registry, protocol graph, or source of network authority.

The identifier does not participate in its own preimage. Define
`local_record_body` as the canonical encoding of every governed field above
except `local_record_id`, then compute:

```text
local_record_id = hash(
  "ilc:translation-passport-local:v0" || canonical(local_record_body)
)
```

The domain separator is literal UTF-8. The selected hash algorithm and
canonical encoding must be named by any later implementation before two
independent implementations can claim matching identifiers. This local
content hash is neither a protocol CID nor graph-materialization authority.

### Five-gate audit

| Gate | Direct source result | Phase 1619 disposition |
|---|---|---|
| 1. Operation acceptance | `_HANDLERS` accepts `revise.assert`. | **Pass for generic lineage revision**, not for a new primitive named TranslationPassport. |
| 2. Revised-content primitive type | Runtime knows agent types `citation`, `execution_descriptor`, `governance_proposal`, `knowledge_claim`, and `observation`. `_KNOWN_PRIMITIVE_TYPES` also unions system-scope types even though the registry documents them as consensus/genesis-only and not agent-issuable. No TranslationPassport type or governed equivalent mapping exists. | **Unresolved.** `knowledge_claim` is a possible research candidate, but no authority or validated mapping permits this spec to select it. The `revise_assert_system_scope_primitive_type_admission_gap` must be reconciled before any materialization claim. |
| 3. Payload validity | `_validate_revise_assert` checks a map, known `primitive_type`, source ID, and bounded rationale. It does not validate TranslationContract/Passport fields. | **Unresolved/insufficient.** Structural acceptance of arbitrary extra map fields is not a passport schema contract. |
| 4. Envelope authentication | Native ingress requires a BLS envelope bound to agent ID, network domain, digest, and canonical bytes. | **Not assessed for a concrete record.** This spec creates no signed envelope. |
| 5. Policy authorization | Inspected validation/persistence paths authenticate the signer but expose no TranslationPassport-specific target/scope authorization decision. | **Unresolved.** Absence of a policy check cannot be interpreted as permission. |

Because all five gates do not pass, graph materialization is **unresolved**. No
graph-node submission pattern is asserted in this phase.

## §7 - Lineage-Refinement Pattern, Local Only

The current permitted pattern is local and non-authoritative:

1. Resolve the exact parent claim, operation version, domain, observation
   boundary, and historical eligibility assessment from the observer's local
   evidence view.
2. Build a canonical `TranslationContract` with separate preservation,
   evidence, and numerical/execution dimensions.
3. Evaluate the missing-evidence/stale-view table and record a typed outcome.
4. Build a `translation_passport_local_v0` record and content-address it in a
   local application store.
5. If evidence later changes, create a successor record with a backward pointer;
   never mutate the old record or a global "current" entry.

Before graph submission could be specified, later work must establish:

- Gate 2: a recognized existing primitive/payload mapping or properly governed
  type extension, plus resolution of
  `revise_assert_system_scope_primitive_type_admission_gap` so system-only types
  cannot be borrowed as agent authority;
- Gate 3: a bounded validator for every passport field and cross-field invariant;
- Gate 4: a concrete authenticated envelope and replay-safe acceptance receipt;
- Gate 5: applicable target, scope, effect, and submitter authorization from an
  identified authority.

Only after those gates pass could a caller consider a `revise.assert` envelope
whose `source_node_id` is the parent/source node and whose revised content is a
valid accepted payload. The runtime's `revision_of` and `revised_by` edges would
then preserve graph lineage. They would still not, without separate evidence,
prove computational sufficiency or economic eligibility.

## §8 - Scoped-Validity Table

| Prior use or claim | Classification | Reason or missing evidence |
|---|---|---|
| TranslationPassport as a local research/application record | `scoped-valid` | Local immutable packaging needs no claim of protocol authority. |
| TranslationContract as a mathematical relation in calculus/recipes | `scoped-valid` | Nonbinding research use remains valid with the three dimensions separated. |
| TranslationPassport as an already accepted graph node type | `requires-reevaluation` | No such registered type or equivalent governed mapping was found. |
| Generic lineage revision through `revise.assert` | `scoped-valid` | Existing operation and edge contract are implemented, subject to native envelope requirements. |
| TranslationPassport payload through `revise.assert` | `undecidable-with-present-evidence` | Gates 2, 3, 4, and 5 are not established for a concrete passport. |
| Claim that revision edges alone satisfy CDL-084 attribution traversal | `requires-reevaluation` | CDL-084 uses an explicit nearest-first chain payload and economic constraints; graph lineage alone is insufficient. |
| Historical-view use under a named bounded policy | `undecidable-with-present-evidence` | Requires exact policy, checkpoint, scope, present authority, and freshness evidence. |
| Network-wide invalidation of earlier research terms | `requires-reevaluation` | This phase has no authority to invalidate records globally; each use is scoped. |

## §9 - Open Questions For Phase 1620

1. How does an executable recipe reference local TranslationPassports without
   implying that they are graph nodes?
2. Which ordered role, ordinal, multiplicity, and effect bindings govern each
   recipe edge?
3. How are prepared execution structure, completed historical execution, and
   present use-time readiness kept separate?
4. How are authority-view identity, policy version, checkpoint, delivery,
   freshness, and conflict resolution represented locally and content-addressed?
5. Which fallbacks independently satisfy the original request's authority,
   scope, effects, and readiness constraints?
6. What total typed outcome is returned when translation is inapplicable,
   insufficiently evidenced, stale, unauthorized, or resource-bounded?
7. What future accepted-type mapping, if any, is justified for recipe/capsule
   objects after the actual registry and payload-contract audit?

## §10 - Non-Claims

No CDL is opened or numbered. No field is binding. No TranslationPassport graph
type or submission path is authorized, and no network-wide invalidation occurs.
`revise.assert` semantics are unchanged. No `ilc_core/` code, LMDB, graph,
attribution bridge, ECU, ILC, wallet, settlement, minting, validator, jury,
network, epoch, public-RC, or mainnet state changes. Authentication is not
treated as authorization, and revision lineage is not treated as automatic
CDL-084/CDL-108 credit eligibility.
