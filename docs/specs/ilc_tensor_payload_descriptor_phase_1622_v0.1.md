# TensorPayloadDescriptor Spec - Phase 1622

**Phase:** 1622
**Status:** Provisional specification complete; local application descriptor only
**Date:** 2026-10-21
**Authority class:** NON-SENSITIVE spec-only research

## §1 - Non-Load-Bearing Preamble

Every field, value set, validation rule, and semantic in this document is
**provisional unless and until adopted under the applicable authority**. The
present classification is a local application descriptor. It is not a ratified
graph type, accepted `content_type`, type-definition instance, protocol bundle
schema, or authority to publish tensor bytes.

The four records below remain separate:

1. the tensor descriptor says which bytes and layout are described;
2. the operation contract says what numerical behavior a use requires;
3. the invocation decision says whether one requested execution is authorized;
4. availability evidence says what an identified observer could locate, access,
   retrieve, integrity-check, and retain for a bounded use.

**Security property:** signed metadata authenticates the signed descriptor
fields only. It never grants permission to load arbitrary code, execute a
locator target, fetch an unbounded object, use an artifact outside scope, or
perform an effect. Code authorization is evaluated independently under the
invocation's applicable authority and sandbox/effect contract.

## §2 - Tensor Descriptor Layer (Primary Identity)

Provisional schema name: `TensorPayloadDescriptorV0`.

### Descriptor-body fields

| Field | Provisional type | Required | Contract |
|---|---|---:|---|
| `schema_version` | fixed string | yes | Exactly `tensor_payload_descriptor_v0`. |
| `encoding_version` | fixed string | yes | Exactly `raw_contiguous_v0` in the first profile. Compression is not implied. |
| `implementation_profile_ref` | content-addressed ref | yes | Identifies finite rank/dimension/element/byte limits and validator version. |
| `dtype` | bounded enum | yes | Logical scalar type. The profile maps it to exact item size and encoding. |
| `itemsize_bytes` | positive integer | yes | Must equal the profile's value for `dtype`; Boolean is not an integer here. |
| `shape` | bounded integer array | yes | Rank and each nonnegative dimension obey the profile. Empty array means a scalar; a zero dimension means an empty tensor. |
| `element_count` | nonnegative integer | yes | Checked product of `shape`; scalar count is one. Overflow is rejected before allocation. |
| `byte_order` | enum | yes | `little`, `big`, or `not_applicable`; one-byte dtypes require `not_applicable`. |
| `layout` | fixed string | yes | `contiguous` in the first profile. |
| `major_order` | enum | yes | `row_major` or `column_major`; determines canonical contiguous strides. |
| `strides_bytes` | bounded integer array | yes | Exact canonical contiguous strides for shape, item size, and major order. Negative or overlapping strides are not in v0. |
| `byte_length` | nonnegative integer | yes | Exactly `element_count * itemsize_bytes`, using checked integer arithmetic, and no greater than the profile cap. |
| `payload_integrity` | object | yes | `algorithm="sha256"`, 64 lowercase hex digest, `hashed_byte_length`, and domain label `ilc.tensor.raw-bytes.v0`. It commits to the exact logical tensor byte range, not a locator. |
| `view` | object or null | yes | Null for a standalone tensor. A view binds base object identity, base payload digest, base byte length, nonnegative byte offset, visible length, and exact bounds proof. |
| `semantic_labels` | bounded map or null | yes | Optional names/axes only. They grant no operation semantics or authority. |
| `created_at` | canonical UTC timestamp | yes | Historical metadata; never a freshness or permission signal. |
| `author_ref` | identity ref | yes | Authenticates authorship only. |
| `supersedes_descriptor_ref` | CID or null | yes | Immutable backward pointer. No mutable `superseded_by` field exists. |

### Derived descriptor identity

`canonical_descriptor_cid` is a derived wrapper/index value, not a member of its
own preimage. It is CIDv1 over canonical DAG-CBOR encoding of the descriptor
body above. A verifier recomputes it; self-reference is forbidden. A local
application may compute this CID-compatible identity for deterministic
comparison, but doing so does not materialize a graph node or confer graph
authority.

Three identity spaces are independent:

| Identity | Algorithm/encoding | Meaning |
|---|---|---|
| Canonical descriptor CID | CIDv1 over descriptor DAG-CBOR | Identity of the descriptor body. |
| Payload integrity digest | SHA-256 over exact raw tensor bytes | Integrity fingerprint for the described payload range. It is not a CIDv1 or AgentID. |
| Agent/key identity | Applicable identity/key profile | Operator or signer identity; never tensor identity. Genesis-forward AgentID derivation uses the CDL-069 SHA-384 identity-seed rule. A BLS public key is separate key material. CDL-118's public-RC native-submit profile exceptionally binds `key_ref == agent_id` and encodes a compressed G1 key as 96 lowercase hex characters; that profile-specific equality does not merge general AgentID derivation with BLS key encoding. |

SHA-384 identity, invite, relay, or other protocol commitment domains do not
replace the SHA-256 tensor-payload integrity domain defined here.

### Contiguous bounded profile

The first profile accepts only dense contiguous byte layouts. Its referenced
profile must contain finite exact-integer values for `max_rank`,
`max_dimension`, `max_elements`, and `max_bytes`. Validation proceeds before
allocation:

1. reject Boolean, negative, non-integer, over-rank, and over-cap values;
2. compute element count with checked multiplication;
3. validate item size and exact byte length;
4. recompute canonical strides;
5. validate view offset plus visible length without overflow;
6. hash exactly the bounded payload range and compare the digest.

Sparse indices, tiled/chunked storage, compression, negative strides,
overlapping views, device pointers, and arbitrary foreign-memory handles are
not v0 encodings. A future profile may represent them only under an identified
numerical and safety contract; it is a different implementation profile, not a
silent interpretation of this descriptor.

## §3 - Operation Contract Layer

Provisional schema name: `TensorOperationContractV0`. It is a separate
content-addressed record referenced by an invocation. It is not embedded as
mutable descriptor state.

| Field | Purpose |
|---|---|
| `operation_id` and `operation_version` | Identify exact semantics; incompatible versions cannot share results. |
| `input_descriptor_refs` and ordered roles | Bind descriptors, role names, ordinals, multiplicity, and expected types. |
| `numerical_profile_ref` | Defines dtype promotion, accumulation precision, rounding, overflow, NaN/Inf/subnormal handling, and backend tolerances. |
| `determinism_class` | One of exact deterministic, profile-deterministic, bounded approximation, or stochastic with explicit seed/distribution contract. |
| `observation_boundary_ref` | Names admission, output, successor, and effect components that must be preserved. |
| `implementation_profile_ref` | Identifies admissible implementation/backend constraints. |
| `law_refs` | References only laws whose premises apply; Phase 1620 candidate laws remain nonbinding. |
| `effect_contract_ref` | Lists permitted effects. Omitted effects are not authorized. |
| `resource_limits` | Finite memory, bytes, operations, time, nesting, and external-call limits. |

Stochastic semantics belong to the generating/consuming operation contract,
not to tensor bytes. A payload digest proves byte equality, not equal numerical
behavior across different dtype, backend, operation, or policy profiles.

The Phase 1621 result is the controlling lesson: retained summaries may be
valid for one operation and refuted for another. Therefore descriptor identity
alone never establishes operation-relative sufficiency.

## §4 - Invocation Decision (Separate Referenced Record)

Provisional schema name: `TensorInvocationDecisionV0`. This pre-execution
record binds:

| Field | Contract |
|---|---|
| `invocation_id` | Identity of this intentional request, including nonce/intention where applicable. |
| `operation_contract_ref` | Exact operation and version requested. |
| `code_identity_ref` | Exact executable/implementation identity. It is not tensor bytes or a descriptor CID. |
| `descriptor_refs` | Ordered bounded input descriptor CIDs. |
| `input_refs` | Exact bounded invocation inputs or commitments. |
| `scope` and `requested_effects` | Network, purpose, authority, effects, and resource boundary. |
| `policy_ref` and `authority_view_ref` | Identified policy and observer-local checkpoint/view. No global-latest assertion. |
| `authority_evidence_refs` | Authentication, delegation, permission, withdrawal, and conflict evidence. |
| `decision` and `reason_codes` | `authorized`, `rejected`, or `unresolved_pending_evidence`, with typed reasons. |
| `decided_at` and `fresh_until` | Historical decision time and bounded freshness. Null expiry never means permanent permission. |

Code identity says what may run; descriptor identity says what tensor metadata
was bound; authority evidence says whether this invocation may occur. Signing
one of these does not substitute for the others. The invocation decision has no
`output_digest`, because no output exists yet.

## §4b - Execution Receipt And Output Record

Provisional schema name: `TensorExecutionReceiptV0`. It is created only after an
attempt and is immutable. It records `invocation_id`, operation/code/descriptor
refs, actual dependency reads, execution outcome, typed error/rejection reasons,
resource use, effects attempted/applied, output descriptor refs,
`output_digest` with algorithm/domain/byte length, execution timestamp or epoch
sequence, and the authority view under which execution was attempted.

An output digest says what bytes were produced. It does not retroactively alter
the invocation decision, grant present reuse eligibility, prove availability,
or make an execution mathematically sufficient for another operation.

## §5 - Availability Evidence (Separate Referenced Record)

Availability is measured evidence, not permission. Provisional schema name:
`TensorAvailabilityObservationV0`.

Each record binds:

- observer identity and observing component identity;
- descriptor CID and payload SHA-256/byte length;
- network, operation/use scope, and invocation when invocation-specific;
- observation time and authoritative checkpoint/context;
- locator class, without making the locator authoritative;
- integrity result and exact bytes checked;
- access condition and access decision;
- custody state through consumption or a required recheck rule;
- finite freshness rule and `valid_until`;
- attestation identity/authority when evidence comes from another component.

The four facts remain independent:

| Fact | Example outcome | Does not imply |
|---|---|---|
| `bytes_available` | retrieved and integrity-checked locally | permission to use or future retention |
| `locator_exists` | a bounded locator was observed | bytes exist, are authentic, or are accessible |
| `access_permitted` | applicable access policy is affirmative | bytes are present or valid |
| `retention_advertised` | provider promises retention until a bound | successful retrieval, local custody, or guaranteed future availability |

Required outcomes include `available_verified`, `missing`, `corrupted`,
`access_denied`, `retention_expired`, `evicted`, and
`unresolved_pending_evidence`. A successful old observation does not establish
readiness after eviction. The consumer pins checked bytes through the
invocation or re-retrieves and rechecks them at consumption.

Locators and provider advertisements remain outside the descriptor's immutable
payload identity so transport changes do not mutate tensor identity. A remote
"availability certificate" is not required merely to prove that bytes already
exist in authenticated local custody.

## §6 - Layer Boundary Classification

### Decision tree

| Question | Direct authority finding | Phase 1622 answer |
|---|---|---|
| 1. Distribution placement | ADR-0009 governs protocol-native distribution. Layer 0 carries schemas/rules, Layer 2 carries graph-state snapshots, and Layer 3 carries live operations/references. | No current canonical placement is authorized. If later adopted, the descriptor schema belongs in Layer 0, graph instances may appear in Layer 2 snapshots, and submissions/retrieval references use Layer 3. Raw tensor bytes are not automatically bundled into any layer; they remain separately content-bound payloads. |
| 2. Graph content typing | ADR-0030 lists accepted content-routing tokens; current `Node` has generic dict content, and CDL-097 adds only `type_definition`. | No accepted `tensor_payload_descriptor` content token or tensor payload validator exists. Generic `content`, `task_result`, and `genesis.blob` do not provide a compatible general tensor semantic contract. Outcome (b) is not established. |
| 3. Governed type-definition authority | ADR-0035 defines the homoiconic type architecture. CDL-097 ratifies type-definition schema authority, but no initial tensor definition instance and no registry activation; `ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED=True`. | Binding graph semantics would require a governed definition/content-type extension or other expressly recognized authority, plus activation. Existing authority supplies a path, not an already-authorized tensor type. |
| 4. Local application/runtime representation | Local bounded data structures need no claim of canonical graph status. | The descriptor in §§2-5 is valid as a local application contract now. It may use deterministic encoding/CID-compatible identity without claiming graph publication. |

### Verdict

**Present classification: outcome (a), local application descriptor.** No valid
mapping to an existing accepted payload contract was found. Outcome (c) is not
already granted merely because ADR-0030/ADR-0035/CDL-097 are adjacent. A future
canonical graph type would follow outcome (d), a governed authority extension
and activation, unless a later audit demonstrates a genuinely compatible
existing payload contract.

CDL-076 governs truth-primitive announcement gossip. CDL-080 governs the
`star.map` N-gram route index as an L3 routing layer. Neither governs general
node-type classification, tensor semantics, or authority to load payloads.

The Phase 1621 SIM adds no tensor-placement authority. It demonstrates why
descriptor identity, operation contract, invocation authority, and readiness
must remain separate: equal retained metadata can be sufficient for one
operation and refuted for another.

## §7 - Werner Field Disambiguation

CDL-116 `token_counts_input` and `token_counts_output` are bounded Model Router
receipt metadata for future Werner evidence calibration. They count model
tokens. They do not encode tensor dtype, shape, layout, strides, payload bytes,
payload integrity, numerical profile, invocation permission, or availability.

`TensorPayloadDescriptor` does not amend CDL-116, the Werner formula, Model
Router consent, graph promotion, or settlement. Tensor element counts must not
be relabeled as Werner token counts, and Werner token counts must not be used as
tensor shape or byte-length evidence.

## §8 - Authority Requirements For Future Adoption

Future binding adoption must identify the exact authority mechanism and settle,
at minimum:

1. canonical descriptor and referenced-record encodings, size caps, and error
   tokens;
2. accepted graph `Node.type` and `content_type`, or an expressly compatible
   existing payload contract;
3. ADR-0035 decomposition, role schema, membership requirements,
   non/attribution policy, dispute paths, effective boundary, and immutable
   supersession semantics;
4. Layer 0 schema distribution and Layer 2/3 instance/reference handling under
   ADR-0009;
5. payload retrieval, integrity, authentication, access, freshness, and local
   custody contracts;
6. executable code authority, sandbox/effect limits, and prohibition on signed
   metadata becoming code-loading permission;
7. current-policy and withdrawal resolution without a central latest-state
   registry;
8. conformance vectors for integer overflow, malformed dimensions, huge
   allocations, view escapes, digest mismatch, locator confusion, dtype/layout
   mismatch, and profile downgrade;
9. whether descriptors are attributable content or non-attributable
   infrastructure; and
10. a separate SENSITIVE activation decision for any default-off registry or
    public graph path.

No CDL number is pre-allocated. CDL-097 is existing type-definition authority,
not automatic ratification of this type. This spec does not decide that a new
CDL is inevitable; a later direct audit may find an authorized compatible path,
but it must demonstrate the payload contract rather than rely on a generic
node container.

## §9 - Non-Claims

No CDL is opened, numbered, amended, or ratified. No field, dtype, profile,
digest rule, content token, node kind, operation contract, availability record,
or classification becomes protocol binding. No tensor, model weight, KV cache,
activation, code artifact, or locator is loaded, executed, published, or stored
by `ilc_core/`.

No `ilc_core/`, LMDB, graph, type-registry guard, protocol bundle, routing,
announcement, fetch, Model Router, Werner, wallet, ECU, ILC, settlement,
minting, validator, jury, network, epoch, public-RC, or mainnet state changes.
The contiguous profile does not imply sparse/tiled support. Descriptor signing
does not authorize code loading or payload use. Local deterministic identity
does not imply canonical graph materialization.
