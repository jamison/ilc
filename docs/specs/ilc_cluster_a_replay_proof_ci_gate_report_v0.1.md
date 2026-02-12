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
