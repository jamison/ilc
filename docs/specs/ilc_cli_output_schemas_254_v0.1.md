# ILC CLI Output Schemas 254 v0.1

Status: Phase-254 specification artifact (non-ratifying)
Date: 2026-02-21
Lane: D2e-02 CLI output schema specification
Depends on:
- `docs/specs/ilc_cli_command_surface_lock_253_v0.1.md`
- `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md`

## 1. Purpose and scope

This artifact defines JSON output schemas for the full Phase-253 CLI command surface:
- seven protocol primitive commands,
- eight operational commands,
- shared success envelope,
- shared error envelope,
- normative exit-code semantics.

This artifact is specification-only. It does not implement CLI runtime behavior and does not mutate CDL status.

## 2. Shared schema conventions

All command responses MUST include:
- `schema_version`: `"254.v0.1"`,
- `command`: command name,
- `ok`: boolean success indicator,
- `ts_utc`: RFC3339 UTC timestamp string.

Success payload shape:

```json
{
  "schema_version": "254.v0.1",
  "command": "<command>",
  "ok": true,
  "ts_utc": "2026-02-21T00:00:00Z",
  "data": {}
}
```

Error payload shape (shared for all commands):

```json
{
  "schema_version": "254.v0.1",
  "command": "<command>",
  "ok": false,
  "error": true,
  "code": "<exit_code>",
  "message": "<stable error message>",
  "details": {}
}
```

## 3. Exit-code semantics

- `0`: success
- `1`: protocol/runtime error
- `2`: usage/argument error
- `3`: network/transport error

## 4. Primitive command schemas (normative)

### 4.1 `assert`
Success data fields:
- `claim_cid` (string, CIDv1)
- `epoch_id` (string)
- `lineage_id` (string)

Success example:

```json
{
  "schema_version": "254.v0.1",
  "command": "assert",
  "ok": true,
  "ts_utc": "2026-02-21T00:00:00Z",
  "data": {
    "claim_cid": "bafy...",
    "epoch_id": "epoch-0421",
    "lineage_id": "lineage-001"
  }
}
```

Error example:

```json
{
  "schema_version": "254.v0.1",
  "command": "assert",
  "ok": false,
  "error": true,
  "code": "2",
  "message": "missing required claim payload",
  "details": {
    "missing": ["claim"]
  }
}
```

### 4.2 `validate`
Success data fields:
- `target_cid` (string)
- `validation_cid` (string)
- `accepted` (boolean)

Success example:

```json
{
  "schema_version": "254.v0.1",
  "command": "validate",
  "ok": true,
  "ts_utc": "2026-02-21T00:00:00Z",
  "data": {
    "target_cid": "bafy-target",
    "validation_cid": "bafy-validation",
    "accepted": true
  }
}
```

Error example:

```json
{
  "schema_version": "254.v0.1",
  "command": "validate",
  "ok": false,
  "error": true,
  "code": "1",
  "message": "validation rejected by protocol rules",
  "details": {
    "reason": "invalid evidence envelope"
  }
}
```

### 4.3 `contradict`
Success data fields:
- `target_cid` (string)
- `contradiction_cid` (string)
- `accepted` (boolean)

Success example:

```json
{
  "schema_version": "254.v0.1",
  "command": "contradict",
  "ok": true,
  "ts_utc": "2026-02-21T00:00:00Z",
  "data": {
    "target_cid": "bafy-target",
    "contradiction_cid": "bafy-contradiction",
    "accepted": true
  }
}
```

Error example:

```json
{
  "schema_version": "254.v0.1",
  "command": "contradict",
  "ok": false,
  "error": true,
  "code": "1",
  "message": "contradiction submission failed",
  "details": {
    "reason": "evidence hash mismatch"
  }
}
```

### 4.4 `refute`
Success data fields:
- `target_cid` (string)
- `refutation_cid` (string)
- `accepted` (boolean)

Success example:

```json
{
  "schema_version": "254.v0.1",
  "command": "refute",
  "ok": true,
  "ts_utc": "2026-02-21T00:00:00Z",
  "data": {
    "target_cid": "bafy-target",
    "refutation_cid": "bafy-refutation",
    "accepted": true
  }
}
```

Error example:

```json
{
  "schema_version": "254.v0.1",
  "command": "refute",
  "ok": false,
  "error": true,
  "code": "1",
  "message": "refutation rejected",
  "details": {
    "reason": "proof does not satisfy contract"
  }
}
```

### 4.5 `revise`
Success data fields:
- `target_cid` (string)
- `revision_cid` (string)
- `supersedes` (string)

Success example:

```json
{
  "schema_version": "254.v0.1",
  "command": "revise",
  "ok": true,
  "ts_utc": "2026-02-21T00:00:00Z",
  "data": {
    "target_cid": "bafy-original",
    "revision_cid": "bafy-revision",
    "supersedes": "bafy-original"
  }
}
```

Error example:

```json
{
  "schema_version": "254.v0.1",
  "command": "revise",
  "ok": false,
  "error": true,
  "code": "2",
  "message": "missing supersedes field",
  "details": {
    "missing": ["supersedes"]
  }
}
```

### 4.6 `link`
Success data fields:
- `source_cid` (string)
- `target_cid` (string)
- `edge_type` (string)
- `edge_cid` (string)

Success example:

```json
{
  "schema_version": "254.v0.1",
  "command": "link",
  "ok": true,
  "ts_utc": "2026-02-21T00:00:00Z",
  "data": {
    "source_cid": "bafy-source",
    "target_cid": "bafy-target",
    "edge_type": "supports",
    "edge_cid": "bafy-edge"
  }
}
```

Error example:

```json
{
  "schema_version": "254.v0.1",
  "command": "link",
  "ok": false,
  "error": true,
  "code": "2",
  "message": "edge_type must be provided",
  "details": {
    "missing": ["edge_type"]
  }
}
```

### 4.7 `epoch`
Success data fields:
- `epoch_id` (string)
- `state` (string)
- `finalization_hash` (string)

Success example:

```json
{
  "schema_version": "254.v0.1",
  "command": "epoch",
  "ok": true,
  "ts_utc": "2026-02-21T00:00:00Z",
  "data": {
    "epoch_id": "epoch-0421",
    "state": "open",
    "finalization_hash": "sha256:..."
  }
}
```

Error example:

```json
{
  "schema_version": "254.v0.1",
  "command": "epoch",
  "ok": false,
  "error": true,
  "code": "3",
  "message": "unable to reach epoch endpoint",
  "details": {
    "endpoint": "https://example.invalid"
  }
}
```

## 5. Operational command schemas (normative)

Operational commands use the same shared success/error envelopes.

| Command | Success data contract |
| --- | --- |
| `query` | `query`, `results` (array), `count` (integer) |
| `verify` | `subject`, `verified` (boolean), `verification_type` |
| `balance` | `account_id`, `ecu_balance`, `pending_balance` |
| `identity` | `lineage_id`, `status`, `export_ref` |
| `bundle` | `bundle_cid`, `valid` (boolean), `manifest_ref` |
| `shard` | `shard_id`, `assignment`, `routing_status` |
| `capproof` | `probe_set`, `overall_pass` (boolean), `probe_results` |
| `config` | `profile`, `changed_keys` (array), `effective_config_ref` |

## 6. Non-goals

This phase does not:
- implement command handlers,
- alter the Phase-253 command surface lock,
- alter exit-code semantics,
- introduce runtime behavior changes in `ilc_core/`.

## 7. Canonical anchors

- `docs/specs/ilc_cli_command_surface_lock_253_v0.1.md`
- `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md`
