# ILC Generalized AgentActionEnvelope Spec GAP-HARNESS-SIDECAR-03 v0.1

Status: companion specification
Phase: GAP-HARNESS-SIDECAR-03
Authority: CDL-111 opening document
Date: 2026-08-15

## Purpose

This specification records the engineering contract for future generalized
`AgentActionEnvelope` dispatch. It is intentionally non-activating.

The current implementation remains `ILC_TRANSFER` only. The companion CDL-111
opening exists so future action types can be added without treating an enum
extension as a merely local code change.

## Runtime Baseline

Current source state:

- `AgentActionEnvelope` is defined in
  `ilc_core/value_action/ilc_transfer_intent.py`.
- `ActionType` contains exactly one value: `ILC_TRANSFER`.
- `validate_envelope()` rejects any non-`ILC_TRANSFER` action in the current
  transfer-specific runtime.
- Signing uses the current transfer payload shape through
  `LocalEd25519SigningProvider`.

No runtime file is modified by this phase.

## Dispatch Contract

A future generalized dispatcher must use explicit action routing:

1. Parse the action discriminator as a string.
2. Reject unknown actions with
   `ValueError("unknown_envelope_action_type:<type>")`.
3. Reject known but inactive actions with their dedicated guard token.
4. Validate payload shape and byte-size bounds before routing.
5. Verify signer authorization for the specific `AgentID` and action scope.
6. Consume or reserve replay protection before any durable write.
7. Execute the action through the action-specific adapter.
8. Emit a deterministic receipt or error token.

The dispatcher must not infer authorization from a public-key fingerprint alone.
Self-contained signed records may carry raw public key bytes plus fingerprint for
verification, but AgentID authority must be proven through graph-native binding
records or an equivalent locally verifiable authority chain.

## Guard Naming

Each future action type requires a default-off guard:

| Action type | Guard |
|---|---|
| `GRAPH_SUBMIT` | `GRAPH_SUBMIT_ENVELOPE_DISPATCH_NOT_ACTIVATED` |
| `ECU_TRANSFER` | `ECU_TRANSFER_ENVELOPE_DISPATCH_NOT_ACTIVATED` |
| `ATTRIBUTION_BATCH` | `ATTRIBUTION_BATCH_ENVELOPE_DISPATCH_NOT_ACTIVATED` |
| `TASK_COMMISSION` | `TASK_COMMISSION_ENVELOPE_DISPATCH_NOT_ACTIVATED` |

The guard must be checked before side effects.

## Serialization Requirements

Any future JSON representation used for hashing, signing, receipts, or protocol
artifacts must use deterministic serialization:

- `sort_keys=True`
- `allow_nan=False`
- stable separators where byte identity is required
- no floats for economic values
- finite `Decimal` validation for amounts

Binary canonical payloads should keep using the existing ILC DAG-CBOR helpers
where applicable.

## Compatibility

The existing `ILC_TRANSFER` runtime is preserved. Future code must not:

- Rename the current `ILC_TRANSFER` discriminator.
- Change existing transfer-ledger record IDs.
- Change existing nonce-store semantics.
- Convert graph submission advisory envelopes into active generalized dispatch
  without a separate activation phase.

## Non-Claims

This specification does NOT activate generalized action dispatch.

It does not add runtime action types, modify transfer settlement, authorize
public graph writes, authorize external withdrawals, authorize generalized ECU
money transfer, mutate any CDL beyond opening CDL-111, launch public RC, or push
the public mirror.
