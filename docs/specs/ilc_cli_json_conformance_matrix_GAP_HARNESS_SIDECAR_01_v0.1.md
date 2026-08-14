# ILC CLI/JSON Conformance Matrix GAP-HARNESS-SIDECAR-01 v0.1

**Phase:** GAP-HARNESS-SIDECAR-01
**Date:** 2026-08-14
**Status:** committed conformance matrix
**Sensitivity:** NON-SENSITIVE

```text
cli_json_conformance_matrix_committed_GAP_HARNESS_SIDECAR_01
```

## 1. Scope

This matrix records the JSON shape of the seven primary ILC CLI surfaces by
direct read of `ilc_core/cli/main.py` and focused subprocess tests. It does not
change `ilc_core/`, activate serving, mutate graph state, clear guards, mutate
CDLs, push a mirror, or execute public RC.

The actual module entrypoint used by tests is:

```text
python -m ilc_core.cli
```

Deviation recorded: `python -m ilc_core` is not registered because
`ilc_core/__main__.py` does not exist. This is a packaging/entrypoint
conformance deviation, not a JSON-schema failure of the command surfaces.

## 2. Controlling JSON Envelopes

### 2.1 Primary envelope

Used by `identity`, `epoch`, `balance`, and `submit`.

| Field | Type | Notes |
|---|---|---|
| `schema_version` | string | `254.v0.1` |
| `command` | string | Top-level command token |
| `ok` | boolean | `true` on success |
| `ts_utc` | string | Runtime-generated UTC timestamp |
| `data` | object | Command-specific payload |

### 2.2 Query envelope

Used by `query`.

| Field | Type | Notes |
|---|---|---|
| `ok` | boolean | `true` on success |
| `data` | object | Query result |
| `meta.command` | string | `query <subcommand>` |
| `meta.schema_version` | string | `299.v0.1` |
| `meta.generated_at` | string | Runtime-generated UTC timestamp |

### 2.3 Verify envelope

Used by `verify`.

| Field | Type | Notes |
|---|---|---|
| `ok` | boolean | `true` on success |
| `data` | object | Verification result |
| `meta.command` | string | `verify <subcommand>` |
| `meta.schema_version` | string | `301.v0.1` |
| `meta.generated_at` | string | Runtime-generated UTC timestamp |

### 2.4 Bundle envelope

Used by `bundle`.

| Field | Type | Notes |
|---|---|---|
| `ok` | boolean | `true` on success |
| `data` | object | Bundle result |
| `meta.command` | string | `bundle <subcommand>` |
| `meta.schema_version` | string | `303.v0.1` |
| `meta.generated_at` | string | Runtime-generated UTC timestamp |

## 3. Command Surface Matrix

| Surface | Actual command tested | Required arguments / fixture | Data fields asserted | Verdict |
|---|---|---|---|---|
| Identity | `ilc identity init`; `ilc identity show`; `ilc identity export` | `--graph-state <fixture>` global option; no invite required while invite enforcement guard remains default-off | `action`, `state_path`, `state`; export adds `export` | PASS |
| Query | `ilc query node --node-id node-1` | JSON graph fixture containing `nodes` | `query`, `node_id`, `node` | PASS |
| Verify | `ilc verify node --node-id node-1` | Same JSON graph fixture | `subject`, `verdict`, `checks` | PASS |
| Bundle | `ilc bundle inspect --bundle-cid bundle-1` | `ILC_BUNDLE_STATE_PATH=<fixture>` | `subject`, `result`, `checks` | PASS |
| Epoch | `ilc epoch` | No fixture | `epoch_id`, `state`, `finalization_hash` | PROTOTYPE |
| Balance | `ilc balance` | No fixture | `account_id`, `balance_ilc`, `pending_balance_ilc`, `report_mode` | PROTOTYPE |
| Value-action / submit | `ilc submit --primitive assert.truth ...` | CDL-073 `assert.truth` fixture with `content`, `primitive_type`, `epistemic_type`, `parent_node_ids` | `subcommand`, `primitive`, `creates_node`, `node_primitive_type`, `graph_persistence` | PASS |

## 4. Registered Command Inventory

Direct read of `ilc_core/cli/main.py` shows the target surfaces are registered as
top-level argparse subparsers:

```text
identity
query
verify
bundle
epoch
balance
submit
```

The value-action / envelope submission surface is not a literal
`ilc value-action` command. The active command is `ilc submit`, backed by
`ilc_core.cli.d2e_submit_cli.handle_submit()`. It accepts an optional
`--signing-key file://...` hotkey argument from GAP-GRAPH-SIGN-00.

## 5. Deviations And Gaps

| Deviation | Impact | Disposition |
|---|---|---|
| `python -m ilc_core` fails because `ilc_core/__main__.py` is absent | Prompt-level invocation wording is not the actual module entrypoint | Tests use `python -m ilc_core.cli`; package entrypoint may be fixed in a future install/CLI packaging phase |
| `epoch` returns prototype data | Not suitable as a full agent-facing epoch-status readback claim by itself | Labelled PROTOTYPE |
| Bare `balance` returns prototype compatibility data | Full per-agent balance requires `--agent-id` and suitable local balance state | Labelled PROTOTYPE |

## 6. Non-Claims

This matrix does not claim:

- public sidecar serving;
- public graph mutation;
- public P2P activation;
- wallet write, transfer, spend, withdrawal, or external-address handling;
- ECU minting or generalized ECU money transfer;
- ILC settlement activation beyond already authorized lanes;
- signing-provider runtime beyond existing submit hotkey support;
- public mirror push;
- public RC activation;
- mainnet activation;
- epoch transition.
