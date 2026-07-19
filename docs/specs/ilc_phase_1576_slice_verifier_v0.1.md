# ILC Phase 1576 Slice Verifier v0.1

**Phase:** `1576-slice-verifier`  
**Validator-safe label:** `1576-Fix5`  
**Date:** 2026-07-19  
**Sensitivity:** NON-SENSITIVE

## 1. Purpose

This phase implements the read-only verifier for the native signed-slice record and portable manifest witness schema ratified in `1576-slice-schema`.

The verifier consumes untrusted JSON and replays the canonical commitments before any future content fetch or materialization step. It is not a materializer and does not write graph state.

## 2. Code Audit Findings

The implementation audit found that `ilc_core/bundle/atlas_slice_schema.py` correctly defines deterministic builders, SHA-384 Merkle roots, recursive `__signed_slices__` exclusion, and float rejection. The missing load-bearing surface was an independent verifier for already-built or received records.

Without this phase, a caller could construct valid objects through the builder path, but there was no strict read-only validator for unknown fields, tampered hashes, mismatched native/witness linkage, malformed commitments, or signature-status policy before install/materialization work.

## 3. Native Record Verification

Runtime:

`ilc_core/bundle/atlas_slice_verifier.py`

Function:

`verify_native_signed_slice_record(record, require_signature_status=False)`

The verifier enforces:

- Exact native record field set.
- `native_record_kind = atlas_signed_slice_record`.
- `native_table = __signed_slices__`.
- `schema_version = atlas_slice_schema_1576.v0.1`.
- Exact signed preimage field set.
- `preimage_domain = ILC_ATLAS_SLICE_SIGNED_PREIMAGE_V1`.
- `canonicalization_version = atlas_slice_canonical_json_sha384_1576.v0.1`.
- SHA-384 shape for `preimage_sha384` and `merkle_root`.
- `preimage_sha384 == SHA384(canonical_preimage)`.
- Canonical sorted `included_tables`.
- Canonical sorted `projection_parameters`.
- Recursive exclusion of `__signed_slices__`.
- Allowed privacy classes.
- Allowed signer authority classes.
- Genesis signer projection whitelist.
- Signature-status policy.
- Float rejection anywhere in the record or preimage.

`--require-signature-status` makes `signature_status=signature_verified` mandatory, but this phase does not itself cryptographically verify a production ML-DSA signature.

## 4. Portable Witness Verification

Function:

`verify_portable_manifest_witness(witness, native_record=None, require_signature_status=False)`

The verifier enforces:

- Exact witness field set.
- `manifest_domain = ILC_ATLAS_SLICE_PORTABLE_WITNESS_V1`.
- Schema and canonicalization constants.
- `excluded_tables = ["__signed_slices__"]`.
- `manifest_sha384 == SHA384(canonical_witness_without_manifest_sha384)`.
- SHA-384 shape for `derived_from_native_record_sha384` and `merkle_root`.
- Allowed privacy classes.
- Permission policy privacy class matches witness privacy class.
- Bounded commitment lists.
- Each commitment has a stable ID and at least one SHA-384 digest field.
- Commitment list ordering is canonical.
- Float rejection anywhere in the witness.

When a native record is supplied, the verifier also enforces:

- `derived_from_native_record_sha384 == SHA384(canonical_native_record)`.
- Authority root, epoch/version, Merkle root, privacy class, projection parameters, projection ID, slice ID, authority proof path, and signer authority class match the native record.

## 5. CLI

Command:

```bash
ilc atlas verify-signed-slice \
  --native-record out/atlas_slice_verifier_1576/native_record_example.json \
  --portable-witness out/atlas_slice_verifier_1576/portable_witness_example.json \
  --json-out out/atlas_slice_verifier_1576/local_verification_receipt.json \
  --generated-at-utc 2026-07-19T00:00:00Z \
  --source-label genesis-local-current
```

CLI result:

- Native record SHA-384: `efd39cac1e69d569e4c20a946ae8c78abfc4ddcfb7fe25e4a1692d34e0ec305a34a12837d0699616943d011ec11937b8`
- Witness manifest SHA-384: `dcf6b007f0145bd33b3ee759d03dc0116d67a467d4cbf430e4dab7018be14983a1cdbccdfc03c2f191ca3357979d63da`
- Receipt ID: `atlas_slice_verification_receipt:02b23cf217e376bcf8a3cf783970a7a90e2b03cec102f5a62cf9e661bf73e5677bf465b3dce4ba243faf9eef20bc54b5`

The local receipt is ignored under `out/` and is not a graph write.

## 6. Negative Test Coverage

Focused tests cover:

- Unknown native record field.
- Bad native preimage hash.
- Recursive `__signed_slices__` inclusion.
- Genesis signing a private projection.
- Native/witness Merkle mismatch after witness rehash.
- Witness manifest hash mismatch.
- Invalid witness signer authority class.
- Bad commitment digest after witness rehash.
- Float rejection.
- Strict signature-status gate on unsigned schema records.
- CLI receipt output.

## 7. Non-Claims

This phase does not:

- Write LMDB.
- Create a `__signed_slices__` table.
- Produce a production signature.
- Cryptographically verify a production ML-DSA signature.
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

## 8. Tokens

- `atlas_slice_verifier_committed_phase_1576`
- `atlas_slice_native_record_verification_committed_phase_1576`
- `atlas_slice_portable_witness_linkage_verification_committed_phase_1576`
- `atlas_slice_verifier_negative_tests_committed_phase_1576`
- `atlas_slice_verifier_no_lmdb_no_materialization_phase_1576`

## 9. Next Work

Next phase: `1576-slice-materializer`.

The materializer should consume only verifier-passing records/witnesses and should remain bounded: fetch only committed blobs, verify each blob digest before use, then write a local install/materialization receipt. It must not grant verifier roles, mint, settle, or transition epochs.
