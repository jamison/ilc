# ILC Cluster A Acceptance Evidence v0.1

**Phase**: 141
**Module**: `ilc_core.protocol.ilc_cluster_a_acceptance_evidence`

## Overview
The **Acceptance Evidence** artifact is a deterministic, portable record of a Cluster A governance decision. It captures the input identity, the full set of constitutional checks, and the final acceptance outcome.

## Schema
### Artifact Kind
- `artifact_kind`: "cluster_a_acceptance_evidence"
- `artifact_version`: "v0.1"

### Identity
- `record_uid`: (string) The `gov_record_id` of the evaluated record.
- `record_hash_sha256`: (hex string) The SHA-256 digest of the canonical governance payload bytes (excluding signatures).
- `transcript_hash_sha256`: (hex string | null) The digest of the transcript context, if applicable.
- `generated_at`: (ISO-8601 string) Strict UTC timestamp of evidence generation.

### Outcome
- `accepted`: (boolean) True if and only if both application and conformance checks succeeded.
- `conformance_ok`: (boolean) True if conformance checks passed.
- `acceptance_errors`: (list[string]) Sorted unique list of all error codes from application and conformance.
- `acceptance_warnings`: (list[string]) Sorted unique list of all warnings.

### Constitution Checks
- `constitution_checks`: (list[object]) Deterministic list of constitution check results, sorted by `check_id`.
  - `check_id`: (string) e.g., "CONST-001"
  - `status`: (string) "pass" | "fail" | "not_applicable"
  - `error_code`: (string | null)
  - `details`: (object | null)

### State Delta
- `policy_state_delta`: (object | null) The deterministic state change derived from the record application (e.g., proposal state updates, known record updates).

## Determinism Rules
1. All list fields (errors, warnings, checks) must be sorted.
2. `record_hash_sha256` must be derived using the canonical ingest serialization.
3. Timestamps must be strict ISO-8601 UTC strings ending in 'Z' (e.g., `2025-10-25T12:00:00.123456Z`).

## Replay Attestation
The `ilc_cluster_a_replay_attestation` module verifies this artifact against a re-execution of the logic.
- Any semantic mismatch results in `ok=False` and specific context violation errors.
- Any schema violation (invalid types, missing fields) results in `ok=False` and schema violation errors (fail-safe behavior).
