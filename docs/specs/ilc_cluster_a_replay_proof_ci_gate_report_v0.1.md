# ILC Cluster A Replay Proof CI Gate Report v0.1

**Version:** v0.1
**Status:** Draft

## Overview
This specification defines the JSON schema for the automated CI/CD gate report produced by the `ilc-canon-cluster-a-replay-proof ci-gate` command.

## Schema
See `ilc_cluster_a_replay_proof_ci_gate_report_v0.1.json` for formal schema.

## Strictness and Determinism
- **Serialization:** Must be deterministic (sorted keys, no whitespace separators by default, stable floating point).
- **Paths:** Reports MUST NOT contain absolute host paths. Relative paths are permitted if portable.
- **Error Tokens:** Errors MUST be reported via stable `error_token` strings, never free-form exception text.

## Semantics
- `ok`: True if and only if all checks passed AND validation logic succeeded (`fail_count == 0` AND `exit_code == 0`).
- `exit_code`:
    - `0`: Success (Gate Passed).
    - `1`: Check Failure (Gate Failed, but execution completed).
    - `2`: Runtime/Input Error (Gate Aborted).
- `checks`: List of executed checks. Order should be deterministic (e.g., by check_id or execution order if stable).

## Check Item
Each check result contains:
- `check_id`: Stable identifier (e.g., `check_package_verify_valid`).
- `ok`: Boolean outcome.
- `expected`: Description of expected state (e.g., `ok=true`).
- `actual`: Description of actual state (e.g., `ok=false`).
- `error_token`: Nullable stable error identifier if applicable.

## Baseline Enforcement (Phase 150)

When the `ci-gate` command is invoked with `--baseline <path>`, the gate loads a previously saved baseline report and compares it structurally against the current gate output.

### Baseline Compare Contract
The `baseline_compare` field in the gate report is `null` when no baseline is provided, or an object with:
- `compare_version`: `"v0.1"`
- `ok`: `true` if current report matches baseline exactly, `false` otherwise.
- `mismatch_count`: Number of structural mismatches found.
- `mismatches`: Deterministically sorted list of mismatch items.

Each mismatch item contains:
- `path`: JSON Pointer to the differing field.
- `reason`: One of `value_mismatch`, `missing_left`, `missing_right`, `schema_invalid_current`, `schema_invalid_baseline`.
- `left`: Value from the current report (null if missing).
- `right`: Value from the baseline report (null if missing).
- `detail`: Nullable detail string (used for schema validation errors).

### Drift Enforcement
When `--enforce-baseline` is set and the compare detects mismatches:
- `exit_code` is set to `1` (verification failure).
- `error_token` is set to `baseline_drift_detected`.
- The `baseline_compare` object is included in the report output.

### Baseline Error Tokens
Baseline-related runtime errors use `exit_code=2` with stable tokens:
- `baseline_not_found`: Baseline file does not exist.
- `baseline_invalid_json`: Baseline file is not valid JSON.
- `baseline_schema_invalid`: Baseline file fails schema validation.
- `baseline_compare_runtime_error`: Unexpected error during compare execution.
