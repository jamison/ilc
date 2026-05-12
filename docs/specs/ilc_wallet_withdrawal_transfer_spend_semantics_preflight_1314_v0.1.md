# ILC Wallet-Facing Value-Action Semantics Preflight 1314 v0.1

Status: implemented / preflight-only / no wallet-facing value-action activation
Date: 2026-05-11
Phase: 1314
Owner lane: G8 graph-native sidecars / Gap 13 value-path user-action boundary

Required tokens:

```text
wallet_withdrawal_transfer_spend_semantics_preflight_phase_1314.v0.1
wallet_withdrawal_transfer_spend_not_activated_phase_1314
wallet_signing_ledger_write_not_authorized_phase_1314
public_claimability_user_action_boundary_recorded_phase_1314
phase_1315_ecu_minting_ilc_settlement_boundary_preflight_next
public_rc_remains_blocked_after_phase_1314
```

Boundary token:

```text
wallet_provider_agnostic_not_ledger_truth_agnostic_phase_1314
```

Phase 1314 was executed after explicit human authorization:

```text
GO Phase 1314
```

This phase records a deterministic wallet-facing value-action semantics
preflight at `ilc_core/sidecars/wallet_action_semantics_preflight.py`. It does
not authorize wallet-facing withdrawal requests, wallet-facing transfer
requests, wallet-facing spend requests, wallet-provider signing requests,
wallet-provider ledger-write requests, public claimability activation, public
claim endpoint serving, ECU minting, ILC settlement, withdrawal runtime, source export, package
publication, release artifacts, release keys, release envelopes, signing, CDL
mutation, Genesis Atlas mutation/signing, or v0.2 signing.

## 0. Discovery Discipline

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | The six Phase 1314 required tokens existed only in the executable prompt before implementation. They are now carried into code, tests, this spec, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.53, Roadmap v1.1, network/value planning, and graph-native sidecar architecture. |
| Section 0b Concept-discovery search | Searched wallet-facing withdrawal/transfer/spend requests, wallet-provider signing, wallet-provider ledger-write, public claim endpoint, claimability, ECU minting, ILC settlement, withdrawal runtime, and historical public-wallet/lifecycle terms across current docs, code, tests, and MemPalace advisory results. |
| Section 0c Contradiction and non-claim search | Confirmed current canon keeps wallet query surfaces read-only and explicitly blocks wallet-facing withdrawal/transfer/spend requests, wallet-provider signing, wallet-provider ledger-write, public claim endpoint, ECU minting, ILC settlement, and withdrawal runtime activation. |
| Section 0d Source expansion and newly discovered tokens | Direct-read PLANNING_INDEX, Capsule v5.53, STATUS tail, Window 1303-1316 lock/guidance, Phase 576 wallet boundary, Phase 615 lifecycle contract, Phase 617 public wallet surface, Phase 1294 package allowlist rehearsal, Phase 1291 public claimability verifier contract, public wallet/lifecycle/verifier runtime files, and graph-native sidecar registry code. |

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

## 1. Claim Verification

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1314 is sensitive and requires explicit human GO | `docs/antigravity_tasks/antigravity_prompt__phase_1314_g8_wallet_withdrawal_transfer_spend_semantics_preflight.md` | confirmed |
| Phase 1314 required tokens are the wallet-facing value-action preflight tokens | Phase 1314 prompt | confirmed |
| Window 1303-1316 locks Phase 1314 as preflight-only wallet-facing semantics work | `docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md` and `docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md` | confirmed |
| Phase 576 keeps wallet visibility/accounting read-only and defers spend/transfer/withdrawal/signing | `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md` | confirmed |
| Phase 617 permitted wallet operations are exactly status/history/export/summary | `docs/specs/ilc_public_wallet_surface_contract_spec_617_v0.1.md` and `ilc_core/protocol/public_wallet_runtime.py` | confirmed |
| Current public wallet runtime has no withdrawal, transfer, spend, signing, or ledger-write method | `PublicWalletRuntime` method table and source read | confirmed |
| Local verifier flags keep wallet-facing withdrawal/transfer/spend requests, ECU mint, and ILC settlement false | `ilc_core/sidecars/claimability_receipt_verifier.py` | confirmed |
| Phase 1315 is the next sensitive ECU minting and ILC settlement boundary preflight | Phase 1314 prompt and Window 1303-1316 guidance | confirmed |

## 2. Implemented Preflight Packet

The new module provides:

- `wallet_action_semantics_preflight_required_tokens()`
- `wallet_action_semantics_preflight_manifest()`
- `build_wallet_action_semantics_preflight_packet()`
- `validate_wallet_action_semantics_preflight_packet()`
- `wallet_action_semantics_preflight_ref()`
- `export_wallet_action_semantics_preflight_json()`

The packet is deterministic and canonical:

- JSON export uses `json.dumps(..., sort_keys=True, allow_nan=False)`.
- Floats, cycles, non-JSON values, oversized text, excessive depth, and
  excessive payload nodes are rejected.
- The packet carries a `candidate_sha256` over the canonical payload.
- Validation rejects operation-list drift, prohibited-action drift,
  source-evidence drift, user-action-boundary drift, activation-requirement
  drift, activation-flag drift, and hash drift.

## 3. User-Action Boundary

| Surface | Phase 1314 disposition |
|---------|------------------------|
| Wallet-facing read operations | Still exactly `wallet_status`, `wallet_history`, `wallet_export`, and `ledger_summary`. |
| Wallet-facing withdrawal request | Not activated; token `wallet_withdrawal_transfer_spend_not_activated_phase_1314`. |
| Wallet-facing transfer request | Not activated; token `wallet_withdrawal_transfer_spend_not_activated_phase_1314`. |
| Wallet-facing spend request | Not activated; token `wallet_withdrawal_transfer_spend_not_activated_phase_1314`. |
| Wallet-provider signing request | Not authorized; token `wallet_signing_ledger_write_not_authorized_phase_1314`. |
| Wallet-provider ledger-write request | Not authorized; token `wallet_signing_ledger_write_not_authorized_phase_1314`. |
| Public claim endpoint | Not enabled; user action boundary recorded only. |
| External chain destination collection | Not enabled. |
| ECU minting | Not authorized; routed to Phase 1315 preflight. |
| ILC settlement | Not authorized; routed to Phase 1315 preflight. |

## 4. Registry And Package Impact

The sidecar registry now includes:

```text
wallet_action_semantics_preflight
```

with authority gate:

```text
phase_1314_preflight_only_wallet_actions_blocked
```

and implementation status:

```text
preflight_recorded_phase_1314_no_wallet_action_activation
```

The OpenClaw/NemoClaw claimable local bridge now requires this preflight
sidecar alongside the offline claimability verifier. The package profile now
records `wallet_action_semantics_preflight_sidecar` in the claimable and full
node public-P2P profiles. This is package/profile metadata and local preflight
logic only; it is not a wallet-facing action implementation.

## 5. Wallet Provider And Ledger Truth Boundary

Phase 1314 preserves the core boundary:

```text
wallet_provider_agnostic_not_ledger_truth_agnostic_phase_1314
```

ILC remains wallet-provider agnostic: local keyfiles, hardware wallets, HSMs,
external wallet SDK callbacks, or later provider adapters may act as signing
providers if they satisfy the signing-provider contract and explicit authority
gates. That does not make ILC ledger-truth agnostic. The authoritative objects
remain the ledger state, graph state, receipts, settled roots, wallet-root
bindings, claimability proofs, and deterministic sidecar manifests.

Terminology rule for future work: avoid shorthand such as "wallet transfer"
when the intended object is the ILC ledger-truth value transition. Use
"wallet-facing transfer request" for an adapter/provider request, and use
"ledger-truth value transition" for the authoritative state change that would
require later explicit authority.

In plain terms: a wallet is an adapter or sidecar around ILC truth, not the
source of truth. A provider can help hold keys, sign payloads, or present user
actions, but it must not be treated as the ledger, the graph, or the authority
that makes a claim spendable or settled.

## 6. Future ILC Wallet Recipe Lane

A future ILC wallet should be planned as a recipe of graph-native sidecars, not
as a monolithic wallet embedded inside the core ledger substrate. Candidate
recipe pieces are:

- wallet-provider adapter sidecar for local keyfile, hardware wallet, HSM, or
  external SDK callback integration;
- signing-intent and payload-binding sidecar that proves exactly what a user is
  being asked to authorize;
- ledger-truth value-action sidecar that validates withdrawal/transfer/spend
  requests against claimability proofs, wallet-root bindings, replay/nullifier
  policy, and settlement gates;
- receipt and user-visible history sidecar that derives presentation from
  immutable ledger/graph records rather than inventing wallet-local truth;
- recovery/export sidecar that keeps user custody portable without granting
  public activation by default.

This lane should be routed after the Phase 1315 ECU/ILC settlement boundary and
before any Phase 1338-style activation decision if the project chooses to ship
an ILC-native wallet profile. It is not a Phase 1314 deliverable and is not a
public-RC blocker unless a later sequence lock explicitly selects it.

## 7. Non-Claims

Phase 1314 does not authorize:

- public RC claim or public launch claim;
- source export, source publication, package publication, release artifact production, release keys, release envelopes, or signing;
- public claimability/API activation, public verifier service, or public claim endpoint;
- public P2P, public fetch serving, public sidecar/projection serving, non-loopback bind, public listener, or peer discovery;
- helper promotion, marker removal, helper stripping, or public export stripping;
- Genesis Atlas mutation/signing, v0.2 signing, CDL mutation, or CDL-088 opening;
- wallet-facing withdrawal requests, wallet-facing transfer requests, wallet-facing spend requests, wallet-provider signing requests, wallet-provider ledger-write requests, withdrawal runtime, wallet-provider custody integration, ECU minting, or ILC settlement;
- public confidential messaging or public confidential coordination serving.

## 8. Next Gate

Phase 1315 is sensitive and requires explicit `GO Phase 1315`.

```text
phase_1315_ecu_minting_ilc_settlement_boundary_preflight_next
```
