# ILC Cluster A Replay Proof Package v0.1

## Overview
The **Cluster A Replay Proof Package** is a deterministic, portable artifact that bundles an Acceptance Evidence artifact with its minimal replay context. This allows any independent party to verify that the evidence is mathematically consistent with the claimed execution results and input record, without needing access to the original runtime environment or policy history.

## Schema
- **JSON Schema**: [ilc_cluster_a_replay_proof_package_v0.1.json](ilc_cluster_a_replay_proof_package_v0.1.json)
- **Version**: `v0.1`

### Structure
```json
{
  "package_version": "v0.1",
  "record_hash_sha256": "<hex>",
  "evidence_contract_hash_sha256": "<hex>",
  "package_hash_sha256": "<hex>",
  "evidence": { ... },
  "replay_contract": {
      "governance_record": { ... },
      "apply_result": { ... },
      "conformance_result": { ... }
  }
}
```

### Fields
- `record_hash_sha256`: Must match `evidence.record_hash_sha256` and the digest of `replay_contract.governance_record`.
- `evidence_contract_hash_sha256`: Must match the canonical digest of the `evidence` object.
- `package_hash_sha256`: The canonical digest of the package (excluding this field).
- `evidence`: The full Acceptance Evidence artifact (Phase 141).
- `replay_contract`: The subset of inputs required to deterministically replay the attestation check.
  - `governance_record`: The original input record (signatures optional/ignored for hash check).
  - `apply_result`: The output of `apply_governance_record`.
  - `conformance_result`: The output of `evaluate_cluster_a_conformance`.

## Canonicalization
To compute `package_hash_sha256`:
1. Construct the package object with `package_hash_sha256` set to `""` (empty string) or excluded.
2. Sort all keys recursively.
3. Use strict JSON serialization (no whitespace, `separators=(",", ":")`).
4. Encode to UTF-8.
5. Compute SHA-256.

## Verification Process
A verifier MUST:
1. Validate the JSON schema.
2. Recompute `package_hash_sha256` and verify it matches the field.
3. Validate `evidence` schema.
4. Verify `evidence.record_hash_sha256` matches `record_hash_sha256`.
5. Verify `evidence_contract_hash_sha256` matches the digest of `evidence`.
6. Run `attest_cluster_a_replay` using `evidence` and `replay_contract` contents.
   - This re-verifies that the evidence fields match the `replay_contract` results.
   - It re-verifies that `governance_record` hash matches `record_hash_sha256`.

## Security Notes
- This package proves **consistency**, not **correctness of execution**. It proves that *if* the execution results were X, the evidence Y is valid. It does not prove that X was the correct result of applying the record to a specific chain state, as state history is not included.
- For full chain-state verification, a verifier would need the full ledger history.
