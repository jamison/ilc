# ILC ECU Minting And ILC Settlement Boundary Preflight 1315 v0.1

Status: implemented / preflight-only / no value-path activation
Date: 2026-05-11
Phase: 1315
Owner lane: G8 graph-native sidecars / Gap 12-13 ECU/ILC value-path boundary

Required tokens:

```text
ecu_minting_ilc_settlement_boundary_preflight_phase_1315.v0.1
ecu_minting_not_authorized_phase_1315
ilc_settlement_not_authorized_phase_1315
value_path_activation_boundary_recorded_phase_1315
phase_1316_window_1303_1316_closure_audit_next
public_rc_remains_blocked_after_phase_1315
```

Phase 1315 was executed after explicit human authorization:

```text
GO Phase 1315
```

This phase records a deterministic ECU/ILC value-path activation boundary at
`ilc_core/sidecars/value_path_activation_boundary_preflight.py`. It does not
authorize ECU minting, ECU creation, ILC settlement, ILC transfer, settlement
root publication, withdrawal runtime, wallet-facing withdrawal request,
wallet-facing transfer request, wallet-facing spend request, wallet-provider
signing request, wallet-provider ledger-write request, public claimability
activation, public claim endpoint serving, public verifier service, external
chain bridge, release artifact production, release key material, CDL-088,
Genesis Atlas mutation/signing, or v0.2 signing.

## 0. Discovery Discipline

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | The six Phase 1315 required tokens existed in the executable prompt before implementation, with one prior Phase 1314 requirement token carrying the Phase 1315 topic without the `.v0.1` suffix. They are now carried into code, tests, this spec, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.53, Roadmap v1.1, network/value planning, graph-native sidecar architecture, and the sidecar registry spec. |
| Section 0b Concept-discovery search | Searched ECU minting, ECU creation, ILC settlement, withdrawal runtime, conversion, sweeper, claimability, wallet write, value path, settlement root, public launch, wallet provider, and ledger-truth terms across current docs, code, tests, and MemPalace advisory results. |
| Section 0c Contradiction and non-claim search | Confirmed current canon blocks ECU minting, ILC settlement, withdrawal runtime, wallet writes, public claimability activation, public claim endpoint serving, source export, release materialization, CDL-088 opening, public RC, and v0.2 signing. |
| Section 0d Source expansion and newly discovered tokens | Direct-read PLANNING_INDEX, Capsule v5.53, STATUS tail, Window 1303-1316 lock/guidance, Phase 615 lifecycle contract, Phase 617 public wallet surface, Phase 1291 public claimability contract, Phase 1314 wallet-action packet, claimability verifier, public wallet runtime, ECU/ILC lifecycle runtime, package profile contracts, and graph-native sidecar registry code. |

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

## 1. Claim Verification

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1315 is sensitive and requires explicit human GO | `docs/antigravity_tasks/antigravity_prompt__phase_1315_g8_ecu_minting_ilc_settlement_boundary_preflight.md` | confirmed |
| Phase 1315 required tokens are the ECU/ILC value-path preflight tokens | Phase 1315 prompt | confirmed |
| Window 1303-1316 locks Phase 1315 as ECU minting and ILC settlement boundary preflight | `docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md` and `docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md` | confirmed |
| Phase 1314 records wallet-facing actions as blocked and routes ECU/ILC boundary to Phase 1315 | `ilc_core/sidecars/wallet_action_semantics_preflight.py` and Phase 1314 walkthrough | confirmed |
| Current public wallet runtime remains read-only | `ilc_core/protocol/public_wallet_runtime.py` | confirmed |
| Current ECU/ILC lifecycle runtime contains an existing `commit_settled_epoch` local lifecycle method, but Phase 1315 does not call or activate it | `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py` and `ilc_core/sidecars/value_path_activation_boundary_preflight.py` | confirmed |
| Current claimability verifier keeps ECU minting and ILC settlement activation false | `ilc_core/sidecars/claimability_receipt_verifier.py` | confirmed |
| Phase 1316 is the next closure/audit gate | Phase 1315 prompt and Window 1303-1316 guidance | confirmed |
| CDL mutation is not authorized by Phase 1315 | Phase 1315 prompt and `docs/specs/ilc_constitutional_decision_log_v0.1.md` diff check | confirmed by no intended mutation |

## 2. Implemented Preflight Packet

The new module provides:

- `value_path_activation_boundary_preflight_required_tokens()`
- `value_path_activation_boundary_preflight_manifest()`
- `build_value_path_activation_boundary_preflight_packet()`
- `validate_value_path_activation_boundary_preflight_packet()`
- `value_path_activation_boundary_preflight_ref()`
- `export_value_path_activation_boundary_preflight_json()`

The packet is deterministic and canonical:

- JSON export uses `json.dumps(..., sort_keys=True, allow_nan=False)`.
- Floats, cycles, non-JSON values, oversized text, excessive depth, and
  excessive payload nodes are rejected.
- The packet carries a `candidate_sha256` over the canonical payload.
- Validation rejects authorization-flag drift, permitted-substrate drift,
  prohibited-action drift, source-evidence drift, ledger-truth-boundary drift,
  activation-requirement drift, and hash drift.

## 3. Value-Path Boundary

| Surface | Phase 1315 disposition |
|---------|------------------------|
| ECU active layer read | Permitted as local read substrate only. |
| ECU/ILC lifecycle status | Permitted as local read substrate only. |
| Wallet query surface | Still exactly `wallet_status`, `wallet_history`, `wallet_export`, and `ledger_summary`. |
| ECU minting | Not authorized; token `ecu_minting_not_authorized_phase_1315`. |
| ECU creation | Not authorized; token `ecu_minting_not_authorized_phase_1315`. |
| ECU supply policy mutation | Not authorized; token `ecu_minting_not_authorized_phase_1315`. |
| ILC settlement | Not authorized; token `ilc_settlement_not_authorized_phase_1315`. |
| ILC transfer | Not authorized; token `ilc_settlement_not_authorized_phase_1315`. |
| Settlement root publication | Not authorized; token `ilc_settlement_not_authorized_phase_1315`. |
| Withdrawal runtime | Not enabled; token `ilc_settlement_not_authorized_phase_1315`. |
| Wallet-provider signing request | Not authorized; generic value-path activation authority remains blocked. |
| Wallet-provider ledger-write request | Not authorized; generic value-path activation authority remains blocked. |
| Public claim endpoint | Not enabled; public claimability activation remains blocked. |
| External chain bridge | Not enabled. |
| Release materialization | Not authorized. |
| CDL-088 | Not opened. |

## 4. Ledger-Truth Interpretation

Phase 1315 preserves the Phase 1314 boundary:

```text
wallet_provider_agnostic_not_ledger_truth_agnostic_phase_1314
```

ILC remains wallet-provider agnostic but not ledger-truth agnostic. In plain
terms, any wallet is an adapter or sidecar. The authoritative objects remain
the ledger state, graph state, receipts, settled roots, wallet-root bindings,
claimability proofs, and deterministic sidecar manifests.

This phase is the bridge from "wallet-facing action request" to "ledger-truth
value transition." A wallet provider may eventually ask for a withdrawal,
transfer, spend, or signing action, but the provider does not create the truth.
The later activation gate must prove the request against ILC truth objects and
must fail closed on replay, duplicate claim, invalid root, invalid receipt, or
missing authority.

## 5. Registry And Package Impact

The sidecar registry now includes:

```text
value_path_activation_boundary_preflight
```

with authority gate:

```text
phase_1315_preflight_only_value_path_activation_blocked
```

and implementation status:

```text
preflight_recorded_phase_1315_no_ecu_mint_or_ilc_settlement_activation
```

The OpenClaw/NemoClaw claimable local bridge now requires this preflight sidecar
alongside the offline claimability verifier and wallet-action semantics
preflight. The package profile now records
`value_path_activation_boundary_preflight_sidecar` in the claimable and full
node public-P2P profiles. This is package/profile metadata and local preflight
logic only; it is not ECU minting, ILC settlement, withdrawal runtime, wallet
write, public claimability, or public serving implementation.

## 6. Non-Claims

Phase 1315 does not authorize:

- public RC claim or public launch claim;
- source export, source publication, package publication, release artifact production, release keys, release envelopes, or signing;
- public claimability/API activation, public verifier service, or public claim endpoint;
- public P2P, public fetch serving, public sidecar/projection serving, non-loopback bind, public listener, or peer discovery;
- helper promotion, marker removal, helper stripping, or public export stripping;
- Genesis Atlas mutation/signing, v0.2 signing, CDL mutation, or CDL-088 opening;
- no wallet-facing withdrawal request, no wallet-facing transfer request, no wallet-facing spend request, no wallet-provider signing request, no wallet-provider ledger-write request, no wallet write, no withdrawal runtime, no ECU minting, no ILC settlement, and no value-path activation;
- public confidential messaging or public confidential coordination serving.

## 7. Remaining Activation Requirements

Before any later Phase 1338-style value-path activation gate can execute, the
project still needs:

- explicit value-path activation authority;
- ECU mint policy and supply invariant;
- ILC settlement authority and replay policy;
- settlement root namespace and binding contract;
- withdrawal runtime contract;
- wallet-provider signing payload contract;
- wallet ledger-write authority and replay policy;
- public claimability API or local claim endpoint authority;
- replay/nullifier duplicate-claim registry policy;
- TransportPrincipal public-path authority if anything leaves loopback/private harness scope;
- release materialization and package-profile authority if a public RC claim is made;
- separate human authorization after Phase 1315.

## 8. Next Gate

Phase 1316 is sensitive and requires explicit `GO Phase 1316`.

```text
phase_1316_window_1303_1316_closure_audit_next
```
