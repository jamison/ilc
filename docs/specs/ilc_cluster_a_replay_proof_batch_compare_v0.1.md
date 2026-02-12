# ILC Cluster A Replay Proof Batch Compare Report v0.1

## Metadata
- **Version:** v0.1
- **Type:** Specification
- **Phase:** 147

## Purpose
Defines the structure of the comparison report generated when comparing two Cluster A replay proof batch reports. This report is used to verify deterministic reproducibility of batch verification runs.

## Schema
See [ilc_cluster_a_replay_proof_batch_compare_v0.1.json](./ilc_cluster_a_replay_proof_batch_compare_v0.1.json).

## Semantics

### Root Object
- `compare_version`: Must be "v0.1".
- `ok`: boolean. True if and only if valid inputs are structurally identical.
- `left_report_version`: version string from left report, or null if invalid.
- `right_report_version`: version string from right report, or null if invalid.
- `mismatch_count`: Total number of mismatches found.
- `mismatches`: List of mismatch objects, sorted deterministically by `path` then `reason`.

### Mismatch Object
- `path`: JSON pointer-like string indicating the location of mismatch.
  - Root is `/`.
  - Keys are escaped: `~` -> `~0`, `/` -> `~1`.
- `reason`: One of:
  - `value_mismatch`: Values at path differ.
  - `missing_left`: Key exists in right but not left.
  - `missing_right`: Key exists in left but not right.
  - `schema_invalid_left`: Left input failed schema validation (comparison aborted).
  - `schema_invalid_right`: Right input failed schema validation (comparison aborted).
- `left`: The value present in the left report (or null if missing).
- `right`: The value present in the right report (or null if missing).
- `detail`: Optional string. Populated only for schema invalidation reasons to provide context.

## Determinism
- Mismatches must be sorted lexicographically by `path`.
- If paths are identical (e.g. multiple reasons at same path - theoretical), sort by `reason`.
