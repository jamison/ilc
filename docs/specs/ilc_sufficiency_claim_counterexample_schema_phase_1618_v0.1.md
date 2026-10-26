# SufficiencyClaim and Counterexample Schema - Phase 1618

**Phase:** 1618
**Status:** Provisional specification complete
**Date:** 2026-10-21
**Authority class:** NON-SENSITIVE spec-only research

## §1 - Non-Load-Bearing Preamble

Every field, value set, constraint, and semantic in this document is
**provisional unless and until adopted under the applicable authority**. This
document is a research schema contract for later evaluation. It does not open
CDL territory, create a protocol type, authorize graph materialization, or make
the names below binding.

The schema separates three facts that must never collapse into one `valid`
flag:

1. an immutable mathematical proposition about operation-relative behavior;
2. an immutable historical assessment of whether a particular observer could
   use that proposition under an identified evidence and authority view; and
3. invocation-local readiness, including whether required bytes remain in
   verified custody when the operation actually runs.

Records are content-addressed canonical objects. Implementations must use
bounded structured encoding, exact integers or decimal strings where numeric
boundaries are needed, and no binary floating-point value in an identity or
authority preimage.

## §2 - `SufficiencyClaim` Schema

`SufficiencyClaim` is a provisional container that references one mathematical
claim and zero or more historical eligibility assessments. Adding an assessment
does not change the mathematical claim's identity. A current view selects among
immutable assessments; it never edits them.

### §2a - Mathematical Claim Sub-Schema

Provisional object name: `SufficiencyMathematicalClaimV0`.

| Field | Provisional type | Required | Meaning and invariant |
|---|---|---:|---|
| `schema_version` | fixed string | yes | Exactly `sufficiency_mathematical_claim_v0`. |
| `claim_subject_refs` | bounded nonempty ordered array of CIDs | yes | Content-addressed representation or representation family being claimed sufficient. Order and multiplicity are explicit. |
| `representation_contract_ref` | CID | yes | Descriptor defining retained distinctions and its encoding. |
| `operation_id` | bounded string | yes | Stable operation family identifier; not a human label alone. |
| `operation_version` | bounded string | yes | Immutable operation-semantic version. Different incompatible versions cannot share results accidentally. |
| `domain_contract_ref` | CID | yes | Finite or otherwise checkable input/state/action domain and membership rules. |
| `observation_boundary_ref` | CID | yes | Declares which output, admission, rejection, and effect components are observable. Incidental timestamps or observer identities are excluded unless explicitly named. |
| `admission_semantics_ref` | CID | yes | Total typed outcome contract for admitted, rejected, and unresolved inputs. |
| `successor_semantics_ref` | CID | yes | State-transition or result relation used by the claim. |
| `effect_semantics_ref` | CID | yes | Declared effects that equivalence must preserve; cannot silently omit economic or capability effects. |
| `assumption_refs` | bounded ordered array of CIDs | yes | Explicit premises, including determinism, approximation, or stochastic assumptions. Empty is permitted only when the checker confirms no extra premise. |
| `claim_kind` | enum | yes | `exact_behavioral_equivalence`, `bounded_approximation`, or `stochastic_equivalence`. Each kind requires its own checker contract. |
| `tolerance_contract` | null or object of decimal strings | yes | Must be null for exact claims. Approximate claims bind named metrics, units, inequalities, and exact decimal bounds. |
| `verification_method` | enum | yes | `exhaustive_domain`, `formal_derivation`, `bounded_model_check`, `statistical_test`, or `composed_evidence`. |
| `evidence_commitment` | null or object | yes | Null means evidence absent. Otherwise binds `hash_algorithm`, `digest`, `media_type`, `byte_length`, and optional evidence CID. |
| `created_at` | canonical UTC timestamp | yes | Historical creation time; never a present-eligibility signal. |
| `author_ref` | content-addressed identity ref | yes | Identifies the proposer, not an automatic authority grant. |
| `supersedes_claim_ref` | null or CID | yes | Optional backward pointer to an older mathematical claim. No mutable forward `superseded_by` field exists. |

The mathematical claim identity is the CID of its canonical encoding. Mutable
`status`, current permission, latest policy, current availability, and current
withdrawal state are forbidden from that identity. A proposition may exist with
`evidence_commitment=null`; it is then an unevidenced claim, not a verified
claim. Attaching evidence produces a distinct immutable claim identity because
the evidence commitment is part of this provisional mathematical record.

The exact proposition is:

```text
Within `domain_contract_ref` and under `assumption_refs`, for every domain-valid
action `a` and states `s1` and `s2` represented as equivalent by
`representation_contract_ref`, compare `(s1, a)` and `(s2, a)`. If both states
admit that same action, they preserve the output, successor representation, and
declared effects named by `observation_boundary_ref` for
`operation_id@operation_version`. If admission differs, that difference is a
separating behavior. Rejection reasons and effects are compared only when the
observation boundary declares them observable.
```

For `divergence_component=admission`, both states must belong to the declared
domain, but both need not admit the action: the admission difference is the
observation being established.

### §2a.1 - Finite Fixture Verification Notes

A representation that is injective over a finite domain places no two distinct
states in one equivalence class. Phase 1621 fixture E2b therefore performs 125
reflexive state/action checks: 25 singleton classes times five actions. The
checks establish correctness over the declared domain, not compression.

Verification methods remain distinct. Formal symbolic arguments such as E5 use
`formal_derivation`; finite exhaustive enumeration uses `exhaustive_domain`;
finite separating-counterexample checks use `bounded_model_check`.

### §2b - Use-Time Eligibility Record Sub-Schema

Provisional object name: `SufficiencyEligibilityAssessmentV0`.

| Field | Provisional type | Required | Meaning and invariant |
|---|---|---:|---|
| `schema_version` | fixed string | yes | Exactly `sufficiency_eligibility_assessment_v0`. |
| `mathematical_claim_ref` | CID | yes | Exact claim assessed; no family-name substitution. |
| `proposition` | structured object | yes | The specific use proposition being assessed, separate from evidence and outcome. |
| `observer_id` | content-addressed identity ref | yes | Observer whose bounded evidence view is evaluated. |
| `use_scope` | structured bounded object | yes | Network, operation, purpose, effects, resource limits, and requested authority scope. |
| `input_refs` | bounded ordered array of CIDs | yes | Exact invocation inputs or immutable input commitments. |
| `policy_ref` | CID | yes | Identified policy version applicable to this assessment. |
| `checker_ref` | CID | yes | Checker implementation/specification identity and version. |
| `evidence_view_ref` | CID | yes | Observer-local snapshot/authority-view manifest. No global latest-state claim is implied. |
| `authoritative_checkpoint_ref` | CID | yes | Epoch, snapshot, or other authority checkpoint used by the view. |
| `view_observed_at` | canonical UTC timestamp | yes | Time at which the identified view was observed. |
| `freshness_rule_ref` | CID | yes | Rule determining whether evidence is fresh for this use. |
| `fresh_until` | canonical UTC timestamp or null | yes | Derived bounded expiry where the rule defines one; null means freshness is not established, not infinite validity. |
| `completeness_basis` | structured object | yes | Names the required evidence set, obtained set, omitted set, and closure method. |
| `authority_evidence_refs` | bounded ordered array of CIDs | yes | Authentication, delegation, policy, and withdrawal evidence considered. Empty does not mean authorized. |
| `availability_evidence_refs` | bounded ordered array of CIDs | yes | Availability observations considered. These inform readiness but do not grant permission. |
| `available_evidence_refs` | bounded ordered array of CIDs | yes | Evidence actually available to the observer for the proposition. |
| `assessment_outcome` | enum | yes | `affirmative`, `negative`, `unresolved_pending_evidence`, `contradictory_evidence`, or `not_applicable`. |
| `reason_codes` | bounded nonempty ordered array of enums | yes | Typed reasons supporting the outcome. Free text alone is insufficient. |
| `assessment_receipt_ref` | CID | yes | Deterministic receipt binding checker inputs, method, output, and resource use. |
| `assessed_at` | canonical UTC timestamp | yes | Historical assessment time. |
| `supersedes_assessment_ref` | null or CID | yes | Optional backward pointer to a prior assessment. It does not alter the prior record. |

`proposition`, `available_evidence_refs`, and `assessment_outcome` are always
separate. A view resolver may select a later assessment for current use, but it
must identify the selection policy and checkpoint. It must not erase older
assessments or treat "latest seen" as universal authority.

An affirmative eligibility assessment is not invocation readiness. Before use,
the caller separately verifies that required objects remain present in local
custody or retrieves and checks them again. A valid sufficiency claim also does
not prohibit direct computation when direct computation is independently
authorized.

### §2c - Provisional Container

| Field | Provisional type | Required | Meaning |
|---|---|---:|---|
| `schema_version` | fixed string | yes | Exactly `sufficiency_claim_container_v0`. |
| `mathematical_claim_ref` | CID | yes | Stable proposition. |
| `eligibility_assessment_refs` | bounded ordered array of CIDs | yes | Historical assessments known to this container; may be empty. |
| `counterexample_refs` | bounded ordered array of CIDs | yes | Paired falsifying evidence known to this container; may be empty. |
| `container_created_at` | canonical UTC timestamp | yes | Historical packaging time only. |

The container is a packaging view, not a mutable registry. A new package may
reference more evidence without mutating an older package or declaring itself
globally current.

## §3 - Availability Descriptors And Evidence Binding

Provisional object name: `AvailabilityEvidenceV0`.

### Descriptor fields

| Field | Provisional type | Meaning |
|---|---|---|
| `bytes_available` | `yes`, `no`, or `unknown` | Whether the identified bytes were locally present at observation time. |
| `locator_exists` | `yes`, `no`, or `unknown` | Whether a locator was known; it says nothing about successful retrieval. |
| `access_permitted` | `yes`, `no`, or `unknown` | Whether the identified policy permits the observer to access the object. |
| `retention_advertised` | `yes`, `no`, or `unknown` | What a provider claimed about retention. It is not retrieval evidence. |
| `observed_at_time` | canonical UTC timestamp | Time of the bounded observation. |
| `observed_retrieval` | `succeeded`, `failed`, or `not_attempted` | Whether retrieval actually occurred and its outcome. |

### Mandatory evidence bindings

| Field | Provisional type | Meaning and invariant |
|---|---|---|
| `observer_id` | content-addressed identity ref | Observer for whom the observation is valid. |
| `observing_component_id` | content-addressed component/key ref | Component that performed or attested the observation; its authentication policy is explicit. |
| `scope` | bounded object/CID set | Exact object bytes or object set checked, plus network and invocation scope. |
| `authoritative_checkpoint_ref` | CID | Policy/snapshot grounding any access or freshness claim. |
| `observation_context_ref` | CID | Invocation, storage, and retrieval context. |
| `observation_time` | canonical UTC timestamp | When the evidence was produced. |
| `integrity_result` | structured enum object | Hash, size, encoding, and content checks; each is `pass`, `fail`, or `not_checked`. |
| `access_condition` | structured object | Applicable policy, observer, purpose, and expiration. |
| `freshness_rule_ref` | CID | Rule requiring re-observation or custody through invocation. |
| `valid_until` | canonical UTC timestamp or null | Bounded result of the freshness rule; null never means permanent. |
| `attestation_ref` | CID or null | Required for remote/component-supplied evidence; local retrieval may bind a local authenticated receipt instead of a remote certificate. |

`retention_advertised` is not `observed_retrieval`, and neither is guaranteed
future availability. An unexpired retrieval observation also does not prove
readiness after eviction. The required-object set comes from the operation/use
contract, and readiness requires verified local custody through the invocation
or a fresh retrieval immediately before consumption. Availability evidence is
readiness evidence, never permission or mathematical proof.

### Three evidence-state examples

| Proposition | Available evidence | Assessment outcome | Explanation |
|---|---|---|---|
| Representation preserves the declared observable contract | none; `evidence_commitment=null` | `unresolved_pending_evidence` | The proposition exists, but absence of support is not affirmation. |
| Representation preserves admission result | separating witness shows admitted versus rejected states share the representation | `contradictory_evidence` | Present evidence negates the proposition. Schema rejection of malformed evidence would instead leave the proposition unresolved. |
| Required closure includes a checkpoint-listed withdrawal record | closure manifest proves that record is omitted | `unresolved_pending_evidence` or `negative`, according to the declared policy | The omission is evidence because the required set was explicitly committed. Mere failure to find an unrequired object would not prove absence. |

## §4 - Counterexample Schema

Provisional object name: `SufficiencyCounterexampleV0`.

| Field | Provisional type | Required | Meaning and invariant |
|---|---|---:|---|
| `schema_version` | fixed string | yes | Exactly `sufficiency_counterexample_v0`. |
| `claim_ref` | CID | yes | Exact mathematical claim challenged. |
| `operation_id` and `operation_version` | bounded strings | yes | Must equal the claim's operation binding. |
| `domain_contract_ref` | CID | yes | Must equal or validly specialize the claim domain. |
| `left_witness_ref` and `right_witness_ref` | CIDs | yes | Two admissible witness states/configurations. |
| `representation_left` and `representation_right` | canonical byte commitments | yes | Must be equal under the challenged representation for a separating witness. |
| `observable_left` and `observable_right` | typed commitments | yes | Must differ in at least one observation-boundary component. |
| `divergence_component` | bounded enum/path | yes | Identifies admission, successor/result, or declared effect difference. |
| `checker_ref` | CID | yes | Checker/spec identity used to validate the witness. |
| `checker_receipt_ref` | CID | yes | Deterministic receipt showing domain membership, equal representation, and divergent behavior. |
| `evidence_refs` | bounded ordered array of CIDs | yes | Supporting objects. |
| `author_ref` | identity ref | yes | Submitter identity, not automatic governing authority. |
| `created_at` | canonical UTC timestamp | yes | Historical time. |
| `supersedes_counterexample_ref` | null or CID | yes | Optional backward pointer; no mutable forward link. |

A malformed or unauthenticated counterexample is rejected as evidence; that
rejection does not prove the claim true. A verified separating witness refutes
the exact mathematical proposition in its declared domain. It does not by
itself invoke CDL-083, allocate ECU, convene a panel, or produce a governance
verdict.

CDL-083 governs caller-filtered, upheld `REFUTATION` economic events with panel
quorum and an explicit refuting-agent payout path. This provisional
counterexample is mathematical evidence only. A future governed bridge would
have to authenticate the record, obtain the applicable verdict, satisfy
CDL-083, and prevent replay before any economic use.

## §5 - Claim-Counterexample Evidence Pairing Semantics

Pairing is a typed immutable edge or packaging reference from a counterexample
to one exact `claim_ref`. The verifier must establish all of the following:

1. the claim and counterexample encodings are structurally valid and bounded;
2. the counterexample references the claim's exact operation version, domain,
   representation, and observation boundary;
3. both witnesses are members of the declared domain and meet admission
   preconditions;
4. their retained representations are equal;
5. at least one required observable differs;
6. the checker receipt binds the same objects and method; and
7. evidence authentication/authority is evaluated separately from mathematical
   validity.

One claim may have many counterexamples. A counterexample may be repackaged in
many observer views but its mathematical identity is immutable. Pairing does
not mutate a claim, select a global active view, settle value, open a challenge,
or authorize public propagation. A later revised claim points backward to the
old claim and may refine its representation or scope; it does not erase the
counterexample against the older proposition.

Assessment aggregation keeps each result visible. A conclusive applicable
prohibition or failed mathematical contract yields `negative`; absent or
indeterminate required evidence yields `unresolved_pending_evidence`. Invalid
evidence is not silently converted into a negative mathematical verdict.

## §6 - Open Questions For Phase 1619

1. Can a `TranslationPassport` be represented through an existing accepted
   truth-primitive content type and its validated payload contract, or must
   graph materialization remain unresolved?
2. Does `revise.assert` accept the intended operation envelope, content type,
   and payload shape independently, and what submitter authority is required?
3. Should translation be a partial function or a total typed result with
   explicit `not_applicable`, `insufficient_evidence`, and `rejected` outcomes?
4. Which fields bind parent operation/version, child representation, source and
   target domains, refinement witness, authority/effect scope, and backward
   lineage?
5. How does the passport reference an eligibility assessment without making
   historical use permission permanent?
6. How are availability observations passed without introducing a circular
   remote availability-certificate dependency?

**FE-12 coverage:** identified observer, use scope, evidence view,
completeness basis, freshness rule, authoritative checkpoint, authority
evidence, and typed outcome are explicit in §2b.

**FE-13 coverage:** §3 separates local byte presence, locator knowledge, access
permission, provider retention advertising, actual retrieval, integrity, and
invocation-local custody. Availability is a measured dependency, not authority.

Open classification: this document does not decide whether any provisional
object is a local descriptor, payload of an existing accepted primitive, or a
new governed type. That determination remains subject to direct type-registry
and authority analysis.

## §7 - Non-Claims

No CDL is opened or assigned. No field is binding; every field is provisional
unless and until adopted under the applicable authority. No schema is
registered, no graph object is materialized, and no central registry, central
checker, global latest-state oracle, or permanent permission cache is created.
No `ilc_core/` code, LMDB, truth-primitive runtime, `revise.assert`, CDL-083
panel, ECU, ILC, wallet, settlement, minting, validator, jury, network, epoch,
public-RC, or mainnet surface changes.
