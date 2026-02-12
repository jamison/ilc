# ILC Cluster A Replay Proof Batch Ops Contract v0.1

**Version:** `v0.1`
**Status:** Draft

## Overview

This contract defines the output structure of the `verify-and-compare` operational command. This command composes batch verification and report comparison into a single atomic operation, providing a strict interface for CI/CD gates and operator verification.

## Goals

1.  **Atomicity**: Combine verify and compare steps.
2.  **Determinism**: Output MUST be byte-for-byte reproducible for identical inputs.
3.  **Strictness**: Explicit `ok` status and `exit_code` mapping.

## Schema

### Fields

-   **`ops_contract_version`** (string, required): Must be `"v0.1"`.
-   **`ok`** (boolean, required): `true` if AND ONLY IF batch verification succeeded AND comparison matched expected report.
-   **`batch_report_path`** (string | null, required): Absolute path to the generated batch report file, if persisted.
-   **`compare_report_path`** (string | null, required): Absolute path to the generated compare report file, if persisted.
-   **`batch_ok`** (boolean, required): `true` if batch verification produced a valid report (regardless of payload content).
-   **`compare_ok`** (boolean, required): `true` if comparison found no mismatches.
-   **`exit_code`** (integer, required):
    -   `0`: Success (`ok=true`).
    -   `1`: Mismatch (`batch_ok=true`, `compare_ok=false`).
    -   `2`: Error (Schema, IO, or internal failure).
-   **`error_token`** (string | null, required): Stable error token if `exit_code` is `2`.

## Example

```json
{
  "ops_contract_version": "v0.1",
  "ok": false,
  "batch_report_path": "/tmp/batch_report.json",
  "compare_report_path": null,
  "batch_ok": true,
  "compare_ok": false,
  "exit_code": 1,
  "error_token": null
}
```
