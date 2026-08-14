# ILC Agent Onboarding Guide GAP-HARNESS-SIDECAR-02 v0.1

**Phase:** GAP-HARNESS-SIDECAR-02
**Date:** 2026-08-14
**Status:** committed guide
**Sensitivity:** NON-SENSITIVE

```text
agent_onboarding_guide_committed_GAP_HARNESS_SIDECAR_02
```

## 1. Scope

This guide gives the current low-friction local onboarding path for a new ILC
agent or operator using the real CLI surfaces confirmed by
GAP-HARNESS-SIDECAR-01. It does not activate private harness modules, public
sidecar serving, public graph mutation, public RC, mainnet, external withdrawal,
or any guard-controlled transfer path.

The installed console command is shown as `ilc`. In a source checkout, the
equivalent module command is:

```bash
python -m ilc_core.cli <args>
```

`python -m ilc_core <args>` is not currently a registered module entrypoint
because `ilc_core/__main__.py` is absent.

## 2. Prerequisites

- A Python environment with `ilc-core` installed or a source checkout with the
  project virtual environment active.
- A local graph-state JSON path for identity and local query/verify commands.
- A root AgentID or lineage context for protocol identity. The hotkey generated
  below does not create or change the root AgentID.
- A writable private key directory that is not checked into git.
- Optional local graph persistence via `ILC_TRUTH_GRAPH_STORE_PATH` if the
  operator wants a durable local truth-submission record.

Example setup:

```bash
mkdir -p ./.ilc-local/keys ./.ilc-local/state
printf '{"schema_version":"local-onboarding.v0.1","nodes":[],"epochs":[]}\n' > ./.ilc-local/state/graph.json
```

## 3. Identity Initialization

Initialize local identity state:

```bash
ilc --graph-state ./.ilc-local/state/graph.json identity init --lineage-id lineage-local --key-ref key-local-0
```

Expected JSON envelope:

```json
{
  "command": "identity",
  "data": {
    "action": "init",
    "state": {
      "key_ref": "key-local-0",
      "lineage_id": "lineage-local",
      "rotation_count": 0,
      "status": "active",
      "updated_at": "<runtime timestamp>"
    },
    "state_path": "<path>"
  },
  "ok": true,
  "schema_version": "254.v0.1",
  "ts_utc": "<runtime timestamp>"
}
```

Invite-aware identity initialization exists behind explicit invite flags, but it
is not the basic onboarding path in this guide.

## 4. Hotkey Generation

Generate an Ed25519 action-signing hotkey:

```bash
ilc agent keygen --output ./.ilc-local/keys/agent-hotkey.pem
```

Expected JSON fields:

```json
{
  "key_path": "<absolute path>",
  "key_uri": "file:///<absolute path>",
  "public_key_fingerprint": "<sha256 over raw 32-byte Ed25519 public key>",
  "public_key_hex": "<raw 32-byte Ed25519 public key as hex>",
  "subcommand": "keygen"
}
```

Custody boundary:

- The generated hotkey is for local action signing.
- It is not the ML-DSA-65 root AgentID key.
- Rotating or losing this hotkey does not change the root AgentID.
- The CLI writes the key with owner-only permissions.
- Do not place the PEM in git, graph payloads, transcripts, or logs.

## 5. Identity State Check

Show local identity state:

```bash
ilc --graph-state ./.ilc-local/state/graph.json identity show
```

Export a sanitized local identity snapshot:

```bash
ilc --graph-state ./.ilc-local/state/graph.json identity export
```

These commands read the local identity state beside the configured graph-state
file and emit JSON. They do not prove network admission by themselves.

## 6. Balance Check

Prototype compatibility balance:

```bash
ilc balance
```

This emits `report_mode: "prototype_compat"` and is **NOT YET AVAILABLE FOR
AGENT USE** as a full settled-balance claim.

Per-agent local state balance:

```bash
ilc balance --agent-id <agent-id> --state-json ./.ilc-local/state/balances.json
```

This is only as authoritative as the local state file supplied. Public RC
settlement readback must use the activated settlement/readback surfaces, not the
prototype compatibility command alone.

## 7. First Truth Submission

The active value-action graph submission surface is `ilc submit`; there is no
separate value-action top-level command.

Unsigned local JSON-shape submission:

```bash
ilc --graph-state ./.ilc-local/state/graph.json submit --primitive assert.truth --payload-json '{"content":{"body":"hello from a new ILC agent"},"epistemic_type":"objective","parent_node_ids":[],"primitive_type":"observation"}' --agent-id <agent-id> --epoch 0
```

Signed local submission using the hotkey:

```bash
ilc --graph-state ./.ilc-local/state/graph.json submit --primitive assert.truth --payload-json '{"content":{"body":"hello from a new ILC agent"},"epistemic_type":"objective","parent_node_ids":[],"primitive_type":"observation"}' --agent-id <agent-id> --epoch 0 --signing-key file:///absolute/path/to/agent-hotkey.pem
```

Expected output fields include:

```json
{
  "subcommand": "submit",
  "primitive": "assert.truth",
  "creates_node": true,
  "node_primitive_type": "observation",
  "graph_persistence": "<runtime status>"
}
```

If `ILC_TRUTH_GRAPH_STORE_PATH` is not configured, graph persistence remains a
deferred/local status and the command should be treated as a validation and JSON
contract check, not as a durable public graph write.

## 8. Receipt Verification

Current direct verification surface:

```bash
ilc --graph-state ./.ilc-local/state/graph.json verify node --node-id <node-id>
```

This verifies a node already present in the local graph-state fixture/store. It
does not fetch missing network content and it does not prove public graph
admission by itself.

Durable signed submission receipt verification is **NOT YET AVAILABLE FOR AGENT
USE** as a single polished onboarding command. The operator must retain the
submission JSON, configured graph store path, signature metadata, and any later
admission/readback receipt until the sidecar receipt lane promotes a higher
level command.

## 9. Limitations And Blockers

| Surface | Current state | Operator interpretation |
|---|---|---|
| `python -m ilc_core` | Not registered | Use installed `ilc` or `python -m ilc_core.cli` |
| `ilc balance` with no `--agent-id` | Prototype compatibility | NOT YET AVAILABLE FOR AGENT USE as settled balance |
| `ilc submit` without `ILC_TRUTH_GRAPH_STORE_PATH` | Validation/contract result; persistence deferred | Not a durable public graph write |
| Hotkey signature | Proves the local Ed25519 key signed the payload | Does not by itself prove the hotkey is authorized for an AgentID |
| `ilc_core/harness/` modules | Private `PUBLIC_RC_EXCLUDE` scaffolds | Not public RC runtime surfaces |
| Public sidecar serving | Not activated by this guide | Requires later sensitive gates |

## 10. Non-Claims

This guide does not claim public RC activation, public graph serving, public P2P
serving, private harness promotion, generalized ECU money transfer, external
withdrawal, mainnet activation, or epoch 0 to 1 launch execution.
