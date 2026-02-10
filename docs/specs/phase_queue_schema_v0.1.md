# Phase Queue Schema v0.1

## Purpose
Define a stable queue contract for automated phase execution loops.

## Top-level object

| Field | Type | Required | Notes |
|---|---|---|---|
| `queue_version` | `string` | Yes | Fixed to `v0.1`. |
| `updated_at` | `string` | Yes | ISO-8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`). |
| `items` | `array` | Yes | Ordered phase jobs. |

## Item object

| Field | Type | Required | Notes |
|---|---|---|---|
| `phase_id` | `string` | Yes | Example: `phase_139_g8_constitution_cluster_a_acceptance_integrity_hardening_fix1`. |
| `phase_number` | `integer` | Yes | Numeric sort key (`139`). |
| `prompt_path` | `string` | Yes | Repository-relative prompt path. |
| `status` | `string` | Yes | One of: `pending`, `running`, `done`, `failed`. |
| `started_at` | `string|null` | No | Set on transition to `running`. |
| `finished_at` | `string|null` | No | Set on terminal state. |
| `walkthrough_path` | `string|null` | No | Filled after run if known. |
| `commit` | `string|null` | No | Commit hash when done. |
| `failure_reason` | `string|null` | No | Short failure summary. |

## State transitions
1. `pending -> running`
2. `running -> done`
3. `running -> failed`

No direct transition from `done` or `failed` to other states without explicit reset.

## Determinism requirements
1. `items` are sorted by `phase_number` at write-time.
2. `updated_at` is always refreshed on mutation.
3. No duplicate `phase_id` values.
4. Unknown statuses are invalid.

