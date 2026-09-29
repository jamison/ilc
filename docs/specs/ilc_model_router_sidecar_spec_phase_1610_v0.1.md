# ILC Model Router Sidecar Spec - Phase 1610

**Status:** committed by Phase 1610  
**Date:** 2026-09-29  
**Sensitivity:** NON-SENSITIVE  
**Output token:** `model_router_spec_complete_phase_1610`

## 1. Overview

The Model Router is the future `ilc-model-router` sidecar package: an OpenRouter-compatible routing layer that turns local inference calls into signed, attributable, local-first sidecar receipts. It is designed to converge with the existing HARNESS-SIDECAR-05 execution receipt runtime in `ilc_core/sidecars/execution_receipt.py`, while keeping router-specific provider metadata outside the core receipt schema.

The router is not part of the `ilc-core` package in this phase. Phase 1610 is a spec-only decision phase. It does not implement router code, modify `ilc_core/`, open CDL-116, or authorize graph promotion.

## 2. Live Pre-Read Findings

`ACTION_TYPES` in `ilc_core/sidecars/execution_receipt.py` currently contains:

```text
attribution_batch
ecu_transfer
graph_submit
ilc_transfer
query
unknown
```

`"model_inference"` is absent. `_RECEIPT_PAYLOAD_KEYS` contains exactly ten fields:

```text
action_type
agent_id_hex
epoch
error_token
inputs_hash
outputs_hash
receipt_token
schema_version
status
tool_id
```

The existing HARNESS-SIDECAR-05 LMDB layout has two sub-databases: `b"receipts"` and `b"token_index"`. `SidecarExecutionReceiptStore.append_receipt()` writes the receipt and token index in one LMDB write transaction. `_next_epoch_ordinal()` scans existing epoch records under that transaction and enforces `MAX_SIDECAR_EXECUTION_RECEIPTS_PER_EPOCH = 10_000`.

No `ilc_core/model_router/` or `ilc_core/sidecars/model_router/` package exists. CDL-116 is assigned/reserved to Model Router in the Window 1596-1616 planning document, but there is no CDL-116 row in the constitutional decision log yet.

## Decision 1 - `action_type` Extension

Phase 1610 locks Option (a): add `"model_inference"` to the existing HARNESS-SIDECAR-05 `ACTION_TYPES` frozenset in a separate Phase 1611 compatibility patch.

Do not route model inference receipts through `action_type="unknown"`. That would obscure receipt indexing and weaken later Werner and CapProof evidence selection. Do not create a router-local action-type registry. That would create a second type system beside the existing sidecar receipt schema.

Phase 1611 is therefore `GAP-HARNESS-SIDECAR-05-FIX1`: a non-sensitive `ilc-core` compatibility patch that adds `"model_inference"` to `ACTION_TYPES`, updates the schema document, and adds regression tests for encode/decode/token stability.

This is a sidecar receipt `action_type`, not a graph primitive type. `ilc_core/protocol/primitive_type_registry.py` remains unchanged. The router does not add `"model_inference"` to `ALLOWED_PRIMITIVE_TYPES`.

## Decision 2 - Companion Record Storage

Router-specific metadata is stored in a separate LMDB companion sub-database keyed by `receipt_token`.

Core HARNESS-SIDECAR-05 receipt fields remain unchanged:

| Field | Rule |
|---|---|
| `action_type` | Must be `"model_inference"` after Phase 1611. |
| `agent_id_hex` | 96 lowercase hex AgentID. |
| `epoch` | Non-negative integer supplied by caller. |
| `error_token` | Empty for success, required for failure or partial status. |
| `inputs_hash` | SHA-256 commitment to canonical request content. |
| `outputs_hash` | SHA-256 commitment to canonical response or partial response content. |
| `receipt_token` | Existing HARNESS-SIDECAR-05 token derivation. |
| `schema_version` | Existing HARNESS-SIDECAR-05 schema version. |
| `status` | `success`, `failure`, or `partial`. |
| `tool_id` | `ilc-model-router-v1`. |

Companion record fields:

| Field | Rule |
|---|---|
| `schema_version` | `ilc_model_router_companion_meta_phase_1610.v0.1`. |
| `receipt_token` | 64 lowercase hex key matching the core receipt. |
| `model_id` | Non-empty provider model identifier. |
| `provider` | Non-empty provider identifier. |
| `token_counts_input` | Non-negative integer. |
| `token_counts_output` | Non-negative integer. |
| `capability_class` | String or null; advisory until CDL-116. |
| `consent_status` | `local_only`, `promotion_pending`, or `promoted`. |

Companion fields must not be added to `_RECEIPT_PAYLOAD_KEYS`.

## Decision 3 - LMDB Architecture

The router store extends the local sidecar LMDB environment with four logical sub-databases:

| Sub-database | Key | Value |
|---|---|---|
| `b"receipts"` | Existing epoch+ordinal key | Core `SidecarExecutionReceipt` JSON. |
| `b"token_index"` | Existing `receipt_token` bytes | Existing epoch+ordinal key. |
| `b"companion_meta"` | `receipt_token` bytes | Router companion record JSON. |
| `b"nullifiers"` | 32-byte nullifier | `receipt_token` bytes. |

The core receipt write and companion/nullifier write must be atomic at the router acceptance boundary. Phase 1612 must either use one LMDB write transaction across the relevant sub-databases or implement an equivalent production-grade atomic primitive before shipping receipt persistence.

The current `DEFAULT_SIDECAR_EXECUTION_RECEIPT_MAP_SIZE_BYTES = 64 * 1024 * 1024` is the HARNESS-SIDECAR-05 baseline. Phase 1612 may expose a router store map-size parameter, but the default must be explicit and finite. The current `MAX_SIDECAR_EXECUTION_RECEIPTS_PER_EPOCH = 10_000` is retained for Phase 1612. It is acceptable for local RC-scale routing but must be measured before any high-throughput public-router claim. The current `MAX_SIDECAR_EXECUTION_RECEIPT_BYTES = 64 * 1024` remains a hard cap for core receipt bytes; companion records must define their own bounded byte cap.

## Decision 4 - Provider Adapter Interface

Provider adapters expose:

```text
route(request) -> RouterReceipt
```

The adapter must always produce a receipt-shaped result for an attempted route:

| Outcome | Receipt rule |
|---|---|
| Success | `status="success"`, empty `error_token`, output commitment over canonical response. |
| Provider timeout | `status="failure"`, `error_token="provider_timeout"`. |
| Provider error | `status="failure"`, stable `provider_error_<code>` token. |
| Partial response | `status="partial"`, `error_token` naming the partial condition, output commitment over partial output. |

Adapters must enforce a hard network timeout. Timeout values must be finite (`math.isfinite(timeout)`) and positive before any HTTP call. Redirect-following must be disabled for any request that transmits authentication material, nullifiers, AgentIDs, or signed request payloads. Response bodies must be read with a bounded byte cap before parsing.

Raw prompts and raw completions must not be stored in core receipts, companion records, or default logs. The router records commitments (`inputs_hash`, `outputs_hash`) and bounded metadata only.

## Decision 5 - Nullifier Schema

The router nullifier is a 32-byte SHA-256 digest over canonical JSON containing:

```json
{
  "agent_id_hex": "<96 lowercase hex>",
  "epoch": 0,
  "request_nonce": "<caller-generated nonce>",
  "schema_version": "ilc_model_router_nullifier_phase_1610.v0.1"
}
```

Serialization must use `sort_keys=True`, compact separators, and `allow_nan=False`.

The nullifier sub-database key is the raw 32-byte digest. The value is the `receipt_token` bytes. Before routing, the router checks this sub-database and raises `model_router_nullifier_collision` if the nullifier already exists. Nullifiers include `epoch` to prevent cross-epoch replay ambiguity. Prior-epoch nullifiers are archived, not silently deleted.

## Decision 6 - Publication Consent UX

Receipts are local-only by default. Publication requires explicit user action:

```text
ilc sidecar model-router promote-receipt <receipt_token>
```

Before CDL-116, promotion is a local stub only. It may write a local preview artifact but must not mutate Atlas, submit a graph node, claim ECU attribution, or create public network state.

Discovery commands follow the ILC CLI hierarchy:

```text
ilc sidecar model-router list-receipts
ilc sidecar model-router promote-receipt <receipt_token>
ilc sidecar model-router route ...
```

The consent status is recorded in companion metadata. `consent_status="promoted"` is only valid after the promotion code path has completed whatever CDL-116 later authorizes.

## 3. Router Receipt Schema Summary

Core receipt example after Phase 1611:

```json
{
  "action_type": "model_inference",
  "agent_id_hex": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "epoch": 0,
  "error_token": "",
  "inputs_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "outputs_hash": "1111111111111111111111111111111111111111111111111111111111111111",
  "receipt_token": "<computed by HARNESS-SIDECAR-05>",
  "schema_version": "sidecar_execution_receipt_GAP_HARNESS_SIDECAR_05.v0.1",
  "status": "success",
  "tool_id": "ilc-model-router-v1"
}
```

Companion metadata example:

```json
{
  "capability_class": null,
  "consent_status": "local_only",
  "model_id": "example-model",
  "provider": "example-provider",
  "receipt_token": "<64 lowercase hex>",
  "schema_version": "ilc_model_router_companion_meta_phase_1610.v0.1",
  "token_counts_input": 0,
  "token_counts_output": 0
}
```

## 4. CDL-116 Scope Preview

CDL-116 will govern Model Router Sidecar Protocol v1. This preview is advisory and not a governance decision.

CDL-116 should cover:

- Graph promotion authority for router receipts.
- Consent semantics for who may promote a receipt and what is published.
- Werner evidence lane treatment for `token_counts_input` and `token_counts_output`.
- CapProof `capability_class` attestation linkage.
- Canonical status of `action_type="model_inference"` after Phase 1611.
- Privacy boundary: commitments by default, raw prompt/output only if a later CDL explicitly authorizes a specific publication class.

Phase 1610 does not open CDL-116. Phase 1615 is the sensitive CDL opening slot.

## 5. Phase Sequence

The locked sequence is:

| Phase | Role | Token |
|---|---|---|
| 1611 | HARNESS-SIDECAR-05-FIX1 action-type compatibility patch | `sidecar_execution_receipt_model_inference_action_type_committed_phase_1611` |
| 1612 | Model Router receipt schema and local LMDB persistence | `model_router_receipts_committed_phase_1612` |
| 1613 | Router auth wiring plus provider adapters and failure receipt contract | `model_router_adapters_complete_phase_1613` |
| 1614 | CLI smoke for route/list/promote-stub | `model_router_cli_smoke_pass_phase_1614` |
| 1615 | CDL-116 opening | `cdl_116_model_router_v1_opened_phase_1615` |

Phase 1611 is HARNESS-SIDECAR-05-FIX1 rather than Router Auth because live pre-read confirmed that `"model_inference"` is absent from `ACTION_TYPES`.
Router auth is therefore not lost: it is sequenced into Phase 1613 with provider adapters, matching the current Phase 1613 prompt. Phase 1613 must implement request signing/nullifier construction under DST `ilc-model-router-request-v1`, duplicate-detection fail-closed behavior, and adapter dispatch without graph promotion.

## 6. Non-Claims

Phase 1610 does not:

- Modify `ilc_core/`.
- Create an `ilc-model-router` package.
- Add `"model_inference"` to `ACTION_TYPES`.
- Add `"model_inference"` to `ALLOWED_PRIMITIVE_TYPES`.
- Open, ratify, or mutate CDL-116.
- Authorize graph promotion.
- Publish raw prompts or raw completions.
- Mint, transfer, or settle ECU or ILC.
- Write LMDB or Atlas state.
- Activate Werner, CapProof, validator, or public RC runtime behavior.
- Push a public mirror.
