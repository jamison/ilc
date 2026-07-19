# ILC Phase 1576 Slice Materializer v0.1

**Phase:** `1576-slice-materializer`  
**Validator-safe label:** `1576-Fix6`  
**Date:** 2026-07-19  
**Sensitivity:** NON-SENSITIVE

## 1. Purpose

This phase implements the local-only Atlas signed-slice materializer. The materializer consumes native signed-slice records and portable witnesses only after the read-only verifier accepts them, then verifies local blob bytes against witness SHA-384 commitments before emitting a status-only materialization receipt.

The materializer does not fetch over a production network, write LMDB, write public graph state, grant verifier roles, clear economic guards, sign records, mint, settle, write wallets, activate CCSS delivery, activate public P2P, or transition epochs.

## 2. Runtime

Runtime:

`ilc_core/bundle/atlas_slice_materializer.py`

CLI:

`ilc atlas materialize-signed-slice`

The runtime calls `verify_native_signed_slice_record()` and, when supplied, `verify_portable_manifest_witness()` before any blob path is resolved. A verifier failure raises `AtlasSliceMaterializerError` and aborts before blob fetch.

## 3. Blob Resolution and Digest Verification

Supported source root:

`--local-source-root`

The phase supports local paths only. There is no URL, VPS, object store, IPFS, or public P2P fetch path.

For each commitment, the materializer derives a stable ID and SHA-384 digest from the already verified witness:

- `node_commitments`: `node_id` + `record_sha384`
- `edge_commitments`: `edge_id` + `record_sha384`
- `content_commitments`: exactly one of `content_id`, `content_cid`, or `table_key` + `sha384`

Candidate local paths are resolved under the source root. Any resolved path outside the source root is rejected with `atlas_slice_materializer_path_traversal`. A blob is accepted only after its SHA-384 digest exactly matches the commitment digest.

## 4. Bounds

The materializer enforces:

- Maximum individual blob size: 128 MiB.
- Maximum total materialized bytes per call: 1 GiB.

The size checks run before blob bytes are read into the digest stream.

## 5. Receipts

Receipt schema:

`atlas_slice_materializer_1576.v0.1`

Receipt IDs use:

`atlas_slice_materialization_receipt:<sha384>`

The receipt records:

- `blobs_verified`
- `blobs_missing`
- `total_bytes_materialized`
- `verifier_eligibility_evidence`
- `materialized_baseline_verified`
- `materialized_baseline_verified_reason`
- `verified_blobs`
- `missing_blobs`
- native verifier summary
- optional witness verifier summary
- non-claims
- output tokens
- canonical `receipt_body_sha384`

`verifier_eligibility_evidence` is status-only evidence. It is not a verifier role grant or guard clearance.

## 6. Rehearsal Mode

The CLI supports `--allow-missing-blobs` for schema examples and dry rehearsals. In that mode, missing blobs are recorded in `missing_blobs`; they are not counted as verified, and `verifier_eligibility_evidence` remains false.

Strict mode is the default and raises on any missing blob.

## 7. Local Results

Schema-example rehearsal:

- Receipt: `out/atlas_slice_materializer_1576/local_materialization_receipt.json`
- Receipt ID: `atlas_slice_materialization_receipt:e3cb67ca11e630b54eb8c1bba88cf334f3646b59a5d6ee8118e454f9bcfcb2920eedced49e1328c64a80441542d70bc7`
- `blobs_verified`: 0
- `blobs_missing`: 4
- `materialized_baseline_verified`: false
- Reason: `no_real_blobs_in_schema_examples`
- `verifier_eligibility_evidence`: false

Generated local baseline witness over signed release package JSON blobs:

- Native record: `out/atlas_slice_materializer_1576/baseline_native_record.json`
- Portable witness: `out/atlas_slice_materializer_1576/baseline_portable_witness.json`
- Receipt: `out/atlas_slice_materializer_1576/baseline_materialization_receipt.json`
- Receipt ID: `atlas_slice_materialization_receipt:f04a59383f2a07876d86722397abce41c8d6b9e7df2859633bd19f729dba2dfeca802d11dbcd593161c331c97b8caf53`
- Core Slice 0 package SHA-384: `eac5d3c18945fd3a7b9c5d5c54c2145819f50eaf185d64c158b43b4e80ef3d2177e6650d5deb0685b324b6233e411545`
- Public-RC Baseline Slice 1 package SHA-384: `af7a9063ca1315cbd264f8a5474bb0b2f1cdcaf2288d772ce3582b442a44caa71c41d1f4a4cd287492d75e942d203777`
- `blobs_verified`: 2
- `blobs_missing`: 0
- `total_bytes_materialized`: 8790649
- `materialized_baseline_verified`: true
- Reason: `core_slice_0_and_public_rc_baseline_slice_1_verified`
- `verifier_eligibility_evidence`: true

## 8. Non-Claims

This phase does not:

- Activate CCSS delivery.
- Credit ECU.
- Transition epochs.
- Clear guards.
- Write LMDB.
- Settle ILC.
- Publish manifests.
- Mint ILC.
- Fetch over a production network.
- Sign production records.
- Write public graph state.
- Activate public P2P.
- Grant verifier roles.
- Write wallets.

