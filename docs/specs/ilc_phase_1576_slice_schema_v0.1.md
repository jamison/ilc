# ILC Phase 1576 Slice Schema v0.1

**Phase:** `1576-slice-schema`  
**Validator-safe label:** `1576-Fix4`  
**Date:** 2026-07-19  
**Sensitivity:** NON-SENSITIVE

## 1. Purpose

This phase ratifies the Window 1576 production schema boundary for signed graph slices.

The schema separates two surfaces:

- **Native authority commitment:** a future LMDB `__signed_slices__` record scoped to a deterministic named projection.
- **Portable distribution witness:** an `AtlasSliceManifest` JSON object derived from the native record and independently verifiable by recipients before content fetch or materialization.

The two surfaces are related but not interchangeable. The native record is the canonical authority commitment. The portable witness is the package truth a recipient can carry, inspect, and verify outside the originating LMDB.

## 2. Compatibility With Fix3 / Fix3a

The Genesis v0.5 Core Slice 0 and Public-RC Baseline Slice 1 packages signed in `1575c-Fix3` remain valid public-RC bridge artifacts. They are JSON extraction packages with detached operator signatures, not native `__signed_slices__` records.

This phase does not invalidate, resign, mutate, or supersede those artifacts. It defines the production-native schema for future signing lanes.

## 3. Native Signed Slice Record

Future signing ceremonies write a record to:

`__signed_slices__`

Required native record fields:

- `authority_proof_path`
- `native_record_kind = atlas_signed_slice_record`
- `native_table = __signed_slices__`
- `preimage`
- `preimage_sha384`
- `schema_version = atlas_slice_schema_1576.v0.1`
- `signature`
- `signature_status`
- `signer_authority_class`
- `signer_key_ref`

The signed preimage commits to:

- `slice_id`
- `schema_version`
- `projection_query_id`
- `projection_parameters`
- `included_tables`
- `privacy_class`
- `authority_root`
- `epoch_or_version`
- `canonicalization_version`
- `merkle_root`
- `preimage_domain`

The `__signed_slices__` table is excluded from normal projection signing. A later higher-order registry slice may sign the signed-slice registry only if explicitly authorized; ordinary projection slices must not include their own signature table.

## 4. Named Projection Rule

A named projection is not a loose row list. It is a deterministic query definition:

- `projection_query_id`
- `projection_parameters`
- `included_tables`
- `privacy_class`
- `schema_version`
- `canonicalization_version`

For Genesis public signing, `projection_query_id` is limited to:

- `genesis_core_star_map`
- `public_protocol_graph`
- `support_candidate_graph`

Genesis must not sign `excluded_private_material` as a public slice.

## 5. Merkle Recipe

Hash algorithm:

`SHA-384`

Domain separators:

- Leaf: `ILC_ATLAS_SLICE_LEAF_V1`
- Internal node: `ILC_ATLAS_SLICE_NODE_V1`
- Empty tree: `ILC_ATLAS_SLICE_EMPTY_V1`
- Signed preimage: `ILC_ATLAS_SLICE_SIGNED_PREIMAGE_V1`
- Portable witness: `ILC_ATLAS_SLICE_PORTABLE_WITNESS_V1`

Leaf hash:

```text
leaf = SHA384(domain_leaf || len(table) || table || len(key) || key || len(canonical_value) || canonical_value)
```

Internal node hash:

```text
node = SHA384(domain_node || left_hash_bytes || right_hash_bytes)
```

Sort order:

```text
(table, key, leaf_hash)
```

Odd-leaf rule:

```text
duplicate the final hash at that level
```

Empty root:

```text
SHA384(domain_empty)
```

Canonical value serialization uses deterministic JSON with sorted keys, compact separators, UTF-8 bytes, no NaN, and no floats.

## 6. Portable Manifest Witness

Required portable witness fields:

- `authority_proof_path`
- `authority_root`
- `availability`
- `canonicalization_version`
- `content_commitments`
- `derived_from_native_record_sha384`
- `edge_commitments`
- `epoch_or_version`
- `excluded_tables`
- `manifest_domain`
- `manifest_sha384`
- `merkle_root`
- `node_commitments`
- `permission_policy`
- `privacy_class`
- `projection_parameters`
- `projection_query_id`
- `required_tests`
- `schema_version`
- `semantic_loss_annotations`
- `signer_authority_class`
- `slice_id`

The witness must include `excluded_tables = ["__signed_slices__"]` unless a later registry-slice authority explicitly changes that rule.

## 7. Executable Example

The focused schema test fixture produced:

- Example Merkle root: `5f8e78aa2b4ac18dd664ec121ea4d994636aca1e9a8238d56fa6681e5e0d1722eb99ca67292e3d2a8c4213e22b22093a`
- Example native preimage SHA-384: `822530c362f650478cab7417ad6d36bec7cf7d6439ccf1065657feb4da21dcb919716de67568315f5257dab9a80b56c0`
- Example portable witness SHA-384: `82a2a54487c5bc30cfa051ef933766b0dd5f25468d1a9f4208f95dc5eab0ab6227b074cc300c5c004bc668a2f52a74b7`

## 8. Runtime Helper

Runtime schema helper:

`ilc_core/bundle/atlas_slice_schema.py`

The helper is intentionally pure. It does not import LMDB writer code, mutate stores, sign payloads, fetch blobs, or materialize packages.

## 9. Non-Claims

This phase does not:

- Write LMDB.
- Create a `__signed_slices__` table.
- Produce a production signature.
- Publish a manifest.
- Materialize a slice.
- Fetch content blobs.
- Grant verifier roles.
- Credit ECU.
- Mint ILC.
- Settle ILC.
- Write wallets.
- Clear runtime guards.
- Activate public P2P.
- Activate CCSS delivery.
- Transition epoch 0 to epoch 1.

## 10. Tokens

- `atlas_slice_schema_committed_phase_1576`
- `atlas_slice_native_signed_record_schema_committed_phase_1576`
- `atlas_slice_manifest_portable_witness_schema_committed_phase_1576`
- `atlas_slice_merkle_recipe_committed_phase_1576`
- `atlas_slice_no_lmdb_write_no_signing_phase_1576`

## 11. Next Work

Next phase: `1576-slice-verifier`.

The verifier should validate native preimages and portable witnesses before any fetch or materialization. It should include negative tests for changed projection parameters, changed Merkle roots, forbidden private projections, recursive signed-slice table inclusion, invalid authority classes, and float-containing payloads.
