# ILC Phase 856 — Genesis Assertion Schema Design v0.1

Status: locked
Date: 2026-04-27
Phase: 856
Owner lane: Window 853–862 — HB-001 prerequisite

`phase_856_genesis_assertion_schema_design`
`genesis_authority_assertion_primitive_type_defined`
`genesis_assert_truth_content_schema_locked`
`genesis_authority_key_embedding_locked`
`genesis_lineage_anchor_locked`

---

## 1. Purpose

Phase 856 applies the `assert.truth` wire format (Phase 855) to the genesis
authority domain. It produces a locked schema for genesis-authority
`assert.truth` objects — the machine-legible, signed artifacts that any agent
can receive, verify, and use to reconstruct genesis bootstrap state.

This design is the direct prerequisite for:
- **HB-001 implementation** (Phase 858): `ilc_core/genesis/assertion_schema.py`
- **HB-001/003 CDL** (Phase 857): scope uses this design as the ratification target

---

## 2. Problem Statement

Current state: genesis authority is encoded in `genesis.json`, a plain JSON
file loaded by the Rust binary at startup using `serde` deserialization. This
file is:

- Not self-describing (no schema or kind field)
- Not signed by the genesis authority key
- Not verifiable using protocol-native machinery
- Readable only by code that knows the `RawGenesis` struct shape

ADR-0027 §4 requires that genesis bootstrap artifacts be the "recursive
self-anchor" of canonical lineage — signed, self-describing, machine-legible.
HB-001 closes this gap.

---

## 3. Genesis Assertion Object: Field Schema

A genesis-authority assertion is an `assert.truth` submission (Phase 855)
where the payload content carries the genesis domain schema defined below.

### 3.1 New primitive_type value

```
"genesis_authority_assertion"
```

This value is added to `ALLOWED_PRIMITIVE_TYPES` by the HB-001/003 CDL
(Phase 857). Until the CDL is ratified, this primitive_type value is
reserved and rejected at the live graph ingestion layer.

### 3.2 assert.truth payload.content for genesis authority

```
GenesisAssertionContent = {
    # --- Identity and kind ---
    "kind"               : "genesis_authority_assertion",  # matches primitive_type
    "schema_version"     : 1,                              # uint, locked at 1 for this spec

    # --- Network identity ---
    "network_id"         : <string>,   # canonical network identifier
                                        # e.g. "ilc-mysticeti-testnet-m009" (testnet)
                                        # or "ilc-genesis-v1" (public launch)
    "is_testnet"         : <bool>,     # true for testnet, false for mainnet
    "real_ecu"           : <bool>,     # true when ECU has real economic weight

    # --- Epoch anchor ---
    "genesis_epoch"      : 0,          # always 0; genesis is by definition epoch zero

    # --- Authority key ---
    "genesis_authority_key" : {
        "algorithm"      : "ML-DSA-65",     # CDL-069 genesis authority algorithm
        "public_key_hex" : <string>,         # hex-encoded ML-DSA-65 public key bytes
                                             # from Phase 838a key ceremony
        "key_id"         : <string>,         # stable identifier (hash prefix of pubkey)
    },

    # --- Validator set ---
    "validators" : [
        {
            "validator_id"    : <uint>,     # sequential ID starting at 1
            "agent_id"        : <string>,   # canonical agent_id (96-char hex, 48 bytes)
            "validator_key"   : <string>,   # BLS12-381 G1 compressed pubkey (96-char hex)
            "stake_micro_ecu" : <string>,   # canonical decimal string (exact_numeric)
            "role"            : <string>,   # "genesis_validator" | "bootstrap_validator"
        },
        # ... one entry per genesis validator
    ],

    # --- BFT parameters ---
    "f"                  : <uint>,     # max faulty validators tolerated at genesis
                                        # quorum = 2f + 1

    # --- Lineage ---
    "predecessor_genesis_cid" : null,  # always null at genesis; non-null for upgrades
}
```

### 3.3 Full assert.truth submission structure for genesis

```
GenesisAssertTruth = {
    "v"         : 1,
    "primitive" : "assert.truth",
    # shard_id omitted — genesis assertions are system-scope
    "agent_id"  : <genesis_authority_agent_id>,  # the genesis authority agent
    "epoch"     : 0,                             # genesis epoch
    "payload"   : {
        "content"      : GenesisAssertionContent,  # (§3.2)
        "primitive_type": "genesis_authority_assertion",
        "epistemic_type": "objective",
        "refutation_criterion": null,              # not refutable (system primitive)
        "parent_node_ids": [],                     # no predecessors at genesis
    },
    "sig"       : <bstr>,  # COSE Sign1 with genesis authority ML-DSA-65 key (see §4)
}
```

### 3.4 Resulting node schema

The graph node produced by a genesis `assert.truth` submission:

```
GenesisAssertionNode = {
    "node_id"              : <CIDv1>,                    # DAG-CBOR hash of payload
    "primitive_type"       : "genesis_authority_assertion",
    "creator_agent_id"     : <genesis_authority_agent_id>,
    "epoch_created"        : 0,
    "content"              : GenesisAssertionContent,    # (§3.2)
    "sig"                  : <bstr>,                     # same sig as submission
    "genesis_anchor"       : true,                       # marks this as genesis root
}
```

---

## 4. Signature Scope for Genesis Assertion

Genesis authority assertions use a specialized COSE Sign1 configuration because
the genesis authority key is ML-DSA-65 (CDL-069), not Ed25519.

### 4.1 Algorithm identifier

COSE algorithm: ML-DSA-65 uses a private-use label. Per CDL-069 §3, the
algorithm identifier is `-65` (private use range, CDL-069 registered).

```
protected header = {
    1: -65,                           # alg: ML-DSA-65 (CDL-069 §3)
    4: <genesis_authority_key_id>,   # kid: from genesis_authority_key.key_id
}
```

### 4.2 Payload scope

The COSE Sign1 Sig_structure covers the `payload` map (DAG-CBOR encoded),
including the full `GenesisAssertionContent`. The outer envelope fields
(`v`, `primitive`, `agent_id`, `epoch`) are NOT separately signed — they
are derived from or included in the payload.

### 4.3 Verification path for any agent

An agent verifying a genesis assertion:
1. Receives a `GenesisAssertTruth` object.
2. Extracts `payload.content.genesis_authority_key.public_key_hex`.
3. Decodes and verifies the COSE Sign1 `sig` against the ML-DSA-65 public key.
4. Confirms `payload.content.network_id` matches the expected network.
5. Confirms `payload.content.genesis_epoch == 0`.
6. Trusts the `validators` list as the authoritative genesis validator set.

This path requires no code repository and no out-of-band operator knowledge — 
only the genesis assertion object itself and the CDL-069 ML-DSA-65 verification
library. This is the homoiconic bootstrap property HB-001 targets.

---

## 5. Relationship to genesis.json (Rust Binary)

The Rust binary (`ilc_consensus/src/config.rs`) will continue to load
`genesis.json` for the current testnet (M-009). The genesis assertion object is
a parallel canonical representation, not a replacement for the Rust boot path.

At public launch (`network_id = "ilc-genesis-v1"`, `real_ecu = true`), the
genesis assertion object becomes the canonical authority source. The Rust binary
may derive its `ValidatorSet` by verifying and parsing the genesis assertion
object rather than the raw JSON. That migration is a Phase 863+ item; it is
explicitly excluded from this window (see sequence lock §6).

---

## 6. primitive_type Extension Decision

The HB-001/003 CDL (Phase 857) will formally authorize the new
`"genesis_authority_assertion"` primitive_type value. This CDL mutates
`ALLOWED_PRIMITIVE_TYPES` in `node_schema_core_runtime_360.py` by amendment.

If the CDL scoping review at Phase 857 finds that this mutation entangles
too many existing tests or creates scope risk, the alternative is:
- Genesis assertion nodes exist outside the `ALLOWED_PRIMITIVE_TYPES` guard
  (system-primitive exempt list), similar to `commit.epoch` which is
  consensus-only.
- The exempt list would be a separate frozen set: `SYSTEM_PRIMITIVE_TYPES`.

Phase 857 decides. Both paths are constitutionally acceptable.

---

## 7. Non-Goals

This design does NOT:
- Redefine how the Rust binary loads genesis on M-009 today.
- Replace genesis.json with assertion objects on the live network.
- Assert that multiple genesis assertions are valid (one genesis root only).
- Authorize any agent other than the genesis authority to issue
  `genesis_authority_assertion` objects.
- Specify how genesis assertions are gossiped to peers (HB-002, RC2+).

---

## 8. Dependency Acknowledgment

This phase carries the mandatory dependency bundle from
`docs/specs/ilc_phase_853_862_sequence_lock_v0.1.md` and additionally:

- `docs/specs/ilc_phase_855_truth_primitive_wire_format_spec_v0.1.md`
- `docs/specs/ilc_phase_838b_sphincs_shamir_split_closure_v0.1.md` (genesis authority key)
- `docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_ratification_evidence_838j_v0.1.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`

---

## 9. Tokens

```
phase_856_genesis_assertion_schema_design_locked
genesis_authority_assertion_primitive_type_defined
genesis_assert_truth_content_schema_locked
genesis_authority_key_ml_dsa_65_embedding_locked
genesis_lineage_predecessor_null_at_genesis
genesis_assertion_verification_path_without_code_repo_locked
genesis_json_rust_binary_not_replaced_in_window_853_862
hb_001_cdl_opening_prerequisite_cleared
```
