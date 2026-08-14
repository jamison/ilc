# ILC Sidecar Execution Receipt Schema — GAP-HARNESS-SIDECAR-05

**Status:** committed
**Phase:** GAP-HARNESS-SIDECAR-05
**Date:** 2026-08-14
**Sensitivity:** NON-SENSITIVE
**Runtime module:** `ilc_core/sidecars/execution_receipt.py`

## 1. Purpose and Scope

`SidecarExecutionReceipt` is a local advisory record for completed sidecar tool actions. It lets an operator or digital agent later inspect whether a local sidecar action completed, failed, or partially completed, and lets the local graph query layer look up receipt records by token.

This schema is intentionally not a consensus receipt, not a BLS attestation, not a CDL-governed finality record, and not a public-serving API.

## 2. Field Table

| Field | Type | Constraint | Rule |
|-------|------|------------|------|
| `schema_version` | string | Exactly `sidecar_execution_receipt_GAP_HARNESS_SIDECAR_05.v0.1` | Included in stored JSON and checked on decode |
| `receipt_token` | string | 64 lowercase hex chars | SHA-256 of canonical JSON over all fields except `receipt_token` and `schema_version` |
| `tool_id` | string | Non-empty, max 128 chars | Local sidecar tool identifier |
| `action_type` | string | One of `ilc_transfer`, `ecu_transfer`, `attribution_batch`, `graph_submit`, `query`, `unknown` | Advisory classification only |
| `epoch` | integer | Non-negative int, bool rejected | Protocol epoch supplied by caller; never wall-clock-derived |
| `agent_id_hex` | string | 96 lowercase hex chars | Acting AgentID in canonical hex form |
| `inputs_hash` | string | 64 lowercase hex chars | SHA-256 of canonical JSON input arguments |
| `outputs_hash` | string | 64 lowercase hex chars | SHA-256 of canonical JSON output/result payload |
| `status` | string | One of `success`, `failure`, `partial` | Local execution outcome |
| `error_token` | string | Empty unless `status == "failure"`; max 128 chars | Required for failure receipts |

## 3. Receipt Token Derivation

The runtime computes `receipt_token` last from the canonical JSON encoding of:

```json
{
  "action_type": "...",
  "agent_id_hex": "...",
  "epoch": 0,
  "error_token": "",
  "inputs_hash": "...",
  "outputs_hash": "...",
  "status": "success",
  "tool_id": "..."
}
```

Serialization is:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

The token is:

```python
hashlib.sha256(encoded_payload).hexdigest()
```

`schema_version` is validated on stored JSON decode, but it is not part of the receipt-token preimage. This keeps the token scoped to action semantics rather than storage envelope versioning.

## 4. LMDB Layout

`SidecarExecutionReceiptStore` uses two named LMDB sub-databases:

| Sub-database | Name | Key | Value |
|--------------|------|-----|-------|
| Receipts | `b"receipts"` | `epoch.to_bytes(8, "big") + ordinal.to_bytes(4, "big")` | Canonical JSON receipt bytes |
| Token index | `b"token_index"` | `receipt_token.encode("utf-8")` | 12-byte receipt key from the receipts database |

Append semantics:

- `append_receipt()` writes the receipt and token index in one LMDB write transaction.
- Duplicate `receipt_token` values fail closed with `sidecar_execution_receipt_token_duplicate`.
- Per-epoch ordinal assignment is derived under the write transaction.
- `read_receipts_for_epoch()` returns receipts in ordinal order.
- `lookup_by_token()` resolves the token index and fails closed on malformed index pointers or missing target records.

## 5. Non-Claims

This phase does not integrate receipts into existing sidecar tools, expose a public receipt API, create a network listener, create a consensus-layer receipt, add signing or BLS attestation, mutate the graph, mutate settlement state, mint ECU, activate ILC transfer, clear any guard, perform CDL mutation, activate public RC, activate mainnet, or push a public mirror.
