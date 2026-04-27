# ILC Phase 855 — Truth Primitive Wire Format Specification v0.1

Status: locked
Date: 2026-04-27
Phase: 855
Owner lane: Window 853–862 — HB-001/003 prerequisite

`phase_855_truth_primitive_wire_format_spec`
`new_seven_wire_format_locked`
`assert_truth_required_fields_locked`
`truth_primitive_dag_cbor_canonical_form_locked`
`truth_primitive_cose_sign1_scope_locked`
`truth_primitive_edge_generation_locked`

---

## 1. Purpose

This document locks the wire format for the seven ILC truth primitives described
in ADM-001 §4.0.1: `assert.truth`, `validate.claim`, `contradict.assert`,
`refute.claim`, `revise.assert`, `link.claim`, `commit.epoch`.

The wire format specified here is the Layer 0 canonical definition. It is the
prerequisite for:

- **HB-001** — Genesis-authority assertion schema (Phase 856): applies
  `assert.truth` to the genesis authority domain.
- **HB-003** — Layer 0 bundle schema section (Phase 859): embeds these schema
  definitions in the distributable Layer 0 bundle.

This document does NOT authorize deployment of these primitives to the live
epistemic graph or extension of `ALLOWED_PRIMITIVE_TYPES` (CDL-034). Both
require a separate CDL. The HB-001/003 CDL (Phase 857) will decide whether
to fold that authorization in or defer it.

---

## 2. Relationship to Existing Infrastructure

### 2.1 Existing event_log.py event kinds

The runtime `ilc_core/protocol/event_log.py` uses event kinds including
`"claim"`, `"refutation"`, `"commit.epoch"`. These are **not** the New Seven;
they are an existing operational log layer that predates this specification.
The two systems are orthogonal. The New Seven are the canonical protocol
submission primitives; the event_log kinds are runtime instrumentation.

When the New Seven are deployed to the live epistemic graph, a separate
migration decision will determine how (or whether) the existing event_log
primitives are remapped. This window does not make that decision.

### 2.2 CDL-034 primitive_type taxonomy

CDL-034's `ALLOWED_PRIMITIVE_TYPES` (`citation`, `execution_descriptor`,
`governance_proposal`, `knowledge_claim`, `observation`) classify nodes **in
the graph** — what type of knowledge claim a node represents.

The New Seven classify **submission operations** — the verb used to create or
act on a node. A single `assert.truth` submission may produce a node whose
`primitive_type` is `knowledge_claim`. The two taxonomies are orthogonal (see
Phase 854 §3.1).

---

## 3. Submission Envelope (common to all seven)

Every truth primitive submission shares a common outer envelope before the
primitive-specific payload. The envelope uses DAG-CBOR encoding (see §6).

```
TruthPrimitiveSubmission = {
    "v"           : 1,               # protocol version (uint, locked at 1 for this spec)
    "primitive"   : <string>,        # one of the seven primitive identifiers
    "shard_id"    : <CIDv1 string>,  # target shard; omitted for system-scope primitives
    "agent_id"    : <string>,        # submitting agent's canonical agent_id
    "epoch"       : <uint>,          # current epoch at submission time
    "payload"     : <map>,           # primitive-specific fields (see §4)
    "sig"         : <bstr>,          # COSE Sign1 over protected envelope (see §5)
}
```

**Required fields for all primitives:** `v`, `primitive`, `agent_id`, `epoch`,
`payload`, `sig`. `shard_id` is required for graph-scoped primitives (see per-
primitive notes); omitted for `commit.epoch` (system scope).

**Canonical identifier strings:**
```
assert.truth
validate.claim
contradict.assert
refute.claim
revise.assert
link.claim
commit.epoch
```

---

## 4. Per-Primitive Specification

### 4.1 assert.truth

**Semantic:** An agent asserts a new truth claim into the graph. Creates a new
node and one or more provenance edges.

**Required payload fields:**

| Field | Type | Constraint |
|-------|------|-----------|
| `content` | map | Assertion content — primitive_type, text or structured body, epistemic_type |
| `primitive_type` | string | Must be a value from `ALLOWED_PRIMITIVE_TYPES` (CDL-034) or an extension ratified by CDL |
| `epistemic_type` | string | One of `{objective, subjective, normative, creative_speculative}` (CDL-034) |
| `refutation_criterion` | map | CDL-052 refutation criterion object (required for `knowledge_claim`; optional for others) |
| `parent_node_ids` | array[CIDv1] | Zero or more CIDv1 node identifiers this assertion builds upon |

**Optional payload fields:** `version`, `language`, `shard_tags`, `expiry_epoch`

**Graph output:**
- Creates one new node: `{node_id: CIDv1(payload), primitive_type, creator_agent_id, epoch_created, …}`
- Creates one `asserted_by` edge: `{source: node_id, target: agent_id, epoch_created}`
- For each `parent_node_id`: creates one `extends` edge: `{source: node_id, target: parent_id, epoch_created}`

**Edge types produced:** `asserted_by`, `extends`

---

### 4.2 validate.claim

**Semantic:** An agent validates (endorses as coherent and admissible) an
existing node. Does not create a new node; creates a validation edge.

**Required payload fields:**

| Field | Type | Constraint |
|-------|------|-----------|
| `target_node_id` | CIDv1 | The node being validated |
| `confidence` | string | Decimal string, 0 < confidence ≤ 1.0 |
| `evidence_summary` | string | Brief machine-legible rationale (max 1024 bytes UTF-8) |

**Optional payload fields:** `validation_epoch`, `panel_seat` (outsider seat marker)

**Graph output:**
- Creates one `validated_by` edge: `{source: target_node_id, target: agent_id, weight: confidence, epoch_created}`

**Edge types produced:** `validated_by`

**Constraint:** A single agent may not issue more than one `validate.claim`
per node per epoch. Duplicate submissions are rejected.

---

### 4.3 contradict.assert

**Semantic:** An agent asserts that two nodes make mutually contradictory claims,
signalling a contradiction in the graph. Does not itself resolve the contradiction.

**Required payload fields:**

| Field | Type | Constraint |
|-------|------|-----------|
| `node_a_id` | CIDv1 | First contradicting node |
| `node_b_id` | CIDv1 | Second contradicting node; must differ from `node_a_id` |
| `contradiction_scope` | string | One of `{logical, empirical, definitional}` |
| `rationale` | string | Machine-legible contradiction claim (max 2048 bytes UTF-8) |

**Optional payload fields:** `resolution_proposal_id` (links to a `revise.assert` proposal)

**Graph output:**
- Creates one `contradicts` edge: `{source: node_a_id, target: node_b_id, epoch_created, submitter: agent_id}`
- Duplicate symmetric edge not created (no `contradicts` from node_b → node_a).

**Edge types produced:** `contradicts`

---

### 4.4 refute.claim

**Semantic:** An agent formally refutes an existing claim using a structured
refutation criterion. More specific than `contradict.assert`: this targets one
node with a CDL-052-compliant refutation.

**Required payload fields:**

| Field | Type | Constraint |
|-------|------|-----------|
| `target_node_id` | CIDv1 | The node being refuted |
| `refutation_criterion` | map | CDL-052 refutation criterion (claim, evidence_type, scope_boundary, claim_form, has_falsifiable_test) |
| `evidence_node_ids` | array[CIDv1] | Zero or more supporting evidence nodes |

**Optional payload fields:** `confidence` (refutation confidence, decimal string 0–1)

**Graph output:**
- Creates one `refuted_by` edge: `{source: target_node_id, target: agent_id, epoch_created}`
- For each `evidence_node_id`: creates one `supported_by` edge from the refutation context

**Edge types produced:** `refuted_by`, `supported_by`

**Constraint:** `has_falsifiable_test` must be `true` for the submission to
pass CDL-052 gate. Submissions with `has_falsifiable_test: false` are rejected
at the submission layer.

---

### 4.5 revise.assert

**Semantic:** An agent proposes a revision of an existing node. The original node
is not deleted; both coexist. The revision is a new node with a `revision_of` edge.

**Required payload fields:**

| Field | Type | Constraint |
|-------|------|-----------|
| `source_node_id` | CIDv1 | The node being revised |
| `revised_content` | map | Full replacement content (same structure as `assert.truth` payload `content`) |
| `revision_rationale` | string | Machine-legible reason for the revision (max 2048 bytes UTF-8) |

**Optional payload fields:** `preserves_fields` (array of field names unchanged from source)

**Graph output:**
- Creates one new node (the revision): same schema as `assert.truth` node output
- Creates one `revision_of` edge: `{source: new_node_id, target: source_node_id, epoch_created}`
- Creates one `revised_by` edge: `{source: source_node_id, target: new_node_id, epoch_created}`

**Edge types produced:** `revision_of`, `revised_by`, plus `asserted_by` for the new node

---

### 4.6 link.claim

**Semantic:** An agent asserts a typed relationship between two existing nodes
without claiming contradiction or validation. Creates a semantic edge.

**Required payload fields:**

| Field | Type | Constraint |
|-------|------|-----------|
| `source_node_id` | CIDv1 | Source node |
| `target_node_id` | CIDv1 | Target node; must differ from source |
| `link_type` | string | One of `{cites, elaborates, contrasts, instantiates, generalizes}` |
| `link_rationale` | string | Machine-legible reason (max 1024 bytes UTF-8) |

**Optional payload fields:** `weight` (decimal string 0–1, defaults to 0.5)

**Graph output:**
- Creates one edge of type `link_type`: `{source: source_node_id, target: target_node_id, weight, epoch_created, creator_agent_id}`

**Edge types produced:** `cites`, `elaborates`, `contrasts`, `instantiates`, `generalizes`

---

### 4.7 commit.epoch

**Semantic:** The system-level primitive that finalizes an epoch. Issued by the
consensus layer, not by individual agents. Creates an immutable epoch record node.

**Required payload fields:**

| Field | Type | Constraint |
|-------|------|-----------|
| `epoch_id` | uint | The epoch being committed |
| `previous_epoch_hash` | bstr | Hash of previous `commit.epoch` node CID |
| `participating_agents` | array[string] | Agent IDs active in this epoch |
| `scoring_results` | map | Per-agent scoring outcomes |
| `reward_distribution` | map | Per-agent reward amounts (canonical decimal strings) |
| `finalization_hash` | bstr | Consensus-agreed hash of epoch state |

**Optional payload fields:** `quorum_record_ids` (CIDv1 array of this epoch's quorum records)

**Authorization:** Only the consensus layer may issue `commit.epoch`. Agent-submitted
`commit.epoch` submissions are rejected at ingestion.

**Graph output:**
- Creates one epoch record node: `{node_id: CIDv1(payload), primitive_type: "epoch_record", epoch_created: epoch_id}`
- Creates `finalizes` edge: `{source: epoch_record_node_id, target: previous_epoch_hash, epoch_created}`

**Edge types produced:** `finalizes`

---

## 5. COSE Sign1 Requirements

All seven primitives use COSE_Sign1 (RFC 9052) with Ed25519 (-8) for agent-issued
primitives. The consensus layer uses the validator key (ML-DSA-65, CDL-069) for
`commit.epoch`.

### 5.1 Sig_structure

```
Sig_structure = [
    "Signature1",
    protected_bstr,          # DAG-CBOR-encoded protected header
    h'',                     # zero-length external_aad
    payload_bstr,            # DAG-CBOR-encoded payload map
]
```

### 5.2 Protected header

```
{
    1: -8,                   # alg: EdDSA (Ed25519)
    4: <agent_id_bytes>,     # kid: agent's canonical agent_id as UTF-8 bytes
}
```

For `commit.epoch`, `alg` is the validator key algorithm per CDL-069.

### 5.3 Signed scope

The signature covers `protected_bstr || payload_bstr` through the COSE
Sig_structure above. The `epoch` field is included in payload and therefore
signed. The outer envelope `v`, `primitive`, `shard_id` fields are NOT
separately signed — they are derived from the payload or are routing metadata.

**Signature length:** Ed25519 signatures must be exactly 64 bytes (L-6 audit
finding, enforced in `cose_sign1.py`).

---

## 6. DAG-CBOR Canonical Form

All submission envelopes and payload maps must use DAG-CBOR (deterministic CBOR
subset). Canonical rules:

1. **Map key ordering:** Sort by (encoded_key_byte_length, encoded_key_bytes)
   lexicographically. Tiebreak: encoded bytes ascending.
2. **String encoding:** All string keys and string values use CBOR text string
   (major type 3), not byte string.
3. **Decimal amounts:** All decimal amounts (ECU values, confidence, weight)
   encoded as CBOR text string using `decimal_to_canonical_string()` from
   `ilc_core/ledger/exact_numeric.py`.
4. **CIDv1 references:** Encoded as CBOR byte string (CIDv1 bytes), not as
   text string.
5. **No undefined/null:** Omit optional fields rather than encoding null.
6. **No float:** All numeric values that represent amounts use canonical decimal
   string encoding. Integer counters (epoch, version) use CBOR uint.

---

## 7. Edge Type Registry

Complete set of edge types produced by the New Seven:

| Edge type | Produced by | Source | Target |
|-----------|-------------|--------|--------|
| `asserted_by` | assert.truth, revise.assert | node_id | agent_id |
| `extends` | assert.truth | new_node_id | parent_node_id |
| `validated_by` | validate.claim | target_node_id | agent_id |
| `contradicts` | contradict.assert | node_a_id | node_b_id |
| `refuted_by` | refute.claim | target_node_id | agent_id |
| `supported_by` | refute.claim | refutation_context | evidence_node_id |
| `revision_of` | revise.assert | new_node_id | source_node_id |
| `revised_by` | revise.assert | source_node_id | new_node_id |
| `cites` | link.claim | source_node_id | target_node_id |
| `elaborates` | link.claim | source_node_id | target_node_id |
| `contrasts` | link.claim | source_node_id | target_node_id |
| `instantiates` | link.claim | source_node_id | target_node_id |
| `generalizes` | link.claim | source_node_id | target_node_id |
| `finalizes` | commit.epoch | epoch_record_node_id | previous_epoch_hash |

---

## 8. Forbidden Interpretations

The following interpretations are forbidden by this specification:

- Using `assert.truth` as authorization to bypass CDL-034 `primitive_type`
  validation in the live graph.
- Using `validate.claim` as a substitute for CDL-017 consensus validator
  endorsement.
- Treating `contradict.assert` as a refutation (it signals conflict, not
  evidence-backed falsification).
- Treating `commit.epoch` as agent-issuable (consensus-only).
- Using floating-point for any numeric amount field.
- Emitting null/undefined for optional fields instead of omitting them.

---

## 9. Relationship to Genesis Assertion Schema (Phase 856)

Phase 856 applies `assert.truth` to the genesis authority domain. The genesis
assertion schema will specify:

- Which `content` structure a genesis-authority `assert.truth` object carries
- How the genesis authority key (ML-DSA-65, CDL-069 / Phase 838a) is embedded
- How the node produced by genesis `assert.truth` is anchored to genesis lineage
- Whether a new `primitive_type` value (`genesis_authority_assertion`) is needed

This document (Phase 855) provides the wire format foundation; Phase 856
provides the domain-specific schema on top of it.

---

## 10. Dependency Acknowledgment

This phase carries the mandatory dependency bundle from
`docs/specs/ilc_phase_853_862_sequence_lock_v0.1.md`.

---

## 11. Tokens

```
phase_855_truth_primitive_wire_format_spec_locked
new_seven_wire_format_locked_phase_855
assert_truth_required_fields_locked
validate_claim_required_fields_locked
contradict_assert_required_fields_locked
refute_claim_required_fields_locked
revise_assert_required_fields_locked
link_claim_required_fields_locked
commit_epoch_required_fields_locked
truth_primitive_dag_cbor_canonical_form_locked
truth_primitive_cose_sign1_scope_locked
truth_primitive_edge_type_registry_locked
phase_856_genesis_assertion_schema_prerequisite_cleared
phase_859_layer_0_bundle_schema_section_prerequisite_cleared
```
