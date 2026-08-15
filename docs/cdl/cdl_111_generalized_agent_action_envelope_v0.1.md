# CDL-111 Generalized AgentActionEnvelope Scope Opening v0.1

Status: opened
Phase: GAP-HARNESS-SIDECAR-03
Date: 2026-08-15
Output token: `generalized_agent_action_envelope_cdl_opened_GAP_HARNESS_SIDECAR_03`

## Scope

CDL-111 opens the governance lane for extending `AgentActionEnvelope` beyond the
currently implemented `ILC_TRANSFER` action type.

The current runtime surface is intentionally narrow:

- `ilc_core/value_action/ilc_transfer_intent.py` defines `ActionType` with only
  `ILC_TRANSFER`.
- `validate_envelope()` accepts only `ActionType.ILC_TRANSFER`.
- No generalized dispatcher exists for ECU transfer, graph submission,
  attribution batch submission, task commissioning, or sidecar actions.

CDL-111 governs the future procedure for adding additional action types to this
envelope family. It does not itself ratify those action types.

## Current State

The live value-action lane has already ratified and activated a bounded
`ILC_TRANSFER` path. That path is not reopened here.

Current implementation state:

- `AgentActionEnvelope` exists as a dataclass in
  `ilc_core/value_action/ilc_transfer_intent.py`.
- `ActionType.ILC_TRANSFER` is the only runtime action discriminator.
- Local Ed25519 signing support signs the current transfer envelope payload.
- Ledger settlement and nonce enforcement are bound to the `ILC_TRANSFER` path.
- Graph submission signing remains a separate truth-write-path hardening
  surface and is not an `AgentActionEnvelope` action type.

This phase records the mismatch between the agent-harness goal of generalized
actions and the present runtime's single-action implementation.

## Governance Framework

Future `AgentActionEnvelope` action types require a separate governance action
before implementation or activation.

Minimum requirements for each future action type:

- A named action discriminator in canonical uppercase snake case.
- A stable payload schema with deterministic serialization rules.
- A dispatch guard named `<ACTION_TYPE>_ENVELOPE_DISPATCH_NOT_ACTIVATED`.
- Exact validation failure tokens for malformed, unauthorized, or inactive
  payloads.
- A signer-authority rule that binds signing key material to the source
  `AgentID` without relying on a central registry.
- Replay protection through nonce, epoch, object-version, or equivalent
  deterministic state binding.
- Clear separation between schema admission and value-moving or graph-mutating
  activation.
- Focused tests showing that unknown or inactive action types fail closed.

An action type is not considered active merely because it appears in this CDL,
the companion spec, an advisory envelope, a research note, or a planning queue.

## Dispatch Semantics

The future dispatcher must fail closed.

Required baseline behavior:

- Unknown action types must raise
  `ValueError("unknown_envelope_action_type:<type>")`.
- Known but inactive action types must raise their dedicated guard token.
- Dispatch must never silently route an unrecognized action to `ILC_TRANSFER`.
- Dispatch must never treat a signed payload as authorized unless the signer is
  authorized for the source `AgentID` and the specific action scope.
- Dispatch must validate the complete action payload before any LMDB write,
  consensus submit, economic transfer, sidecar execution, or graph mutation.

The current `validate_envelope()` token
`ValueError("invalid_envelope_action_type")` remains valid for the current
single-action runtime. CDL-111's `unknown_envelope_action_type:<type>` token is
the forward contract for a future generalized dispatcher.

## Ordered Next-Action-Type Queue

The following queue is advisory and non-activating. Each item requires its own
future ratification or explicitly authorized implementation phase.

| Order | Candidate action type | Candidate scope | Required guard |
|---|---|---|---|
| 1 | `GRAPH_SUBMIT` | Signed graph/truth primitive submission through the hardened write path | `GRAPH_SUBMIT_ENVELOPE_DISPATCH_NOT_ACTIVATED` |
| 2 | `ECU_TRANSFER` | Bounded graph-contextual ECU fast-path transfer | `ECU_TRANSFER_ENVELOPE_DISPATCH_NOT_ACTIVATED` |
| 3 | `ATTRIBUTION_BATCH` | Agent-authored attribution batch proposal or audit handoff | `ATTRIBUTION_BATCH_ENVELOPE_DISPATCH_NOT_ACTIVATED` |
| 4 | `TASK_COMMISSION` | Task-offer, acceptance, result, and receipt lifecycle coordination | `TASK_COMMISSION_ENVELOPE_DISPATCH_NOT_ACTIVATED` |

The order is intended to minimize refactoring: graph submission and ECU transfer
already have adjacent runtime surfaces, while attribution and task coordination
need tighter authority and receipt boundaries before they should share a common
dispatcher.

## Non-Claims

This CDL opening does NOT activate any new `AgentActionEnvelope` action type.

This phase does not:

- Ratify CDL-111.
- Modify `ilc_core/value_action/ilc_transfer_intent.py`.
- Add `ECU_TRANSFER`, `GRAPH_SUBMIT`, `ATTRIBUTION_BATCH`, or
  `TASK_COMMISSION` to `ActionType`.
- Create a generalized runtime dispatcher.
- Authorize public graph mutation.
- Authorize generalized ECU money transfer.
- Authorize external withdrawal.
- Authorize public RC, mainnet, minting, or public mirror push.

The only immediate effect is opening the governance record for future
`AgentActionEnvelope` scope extension.
